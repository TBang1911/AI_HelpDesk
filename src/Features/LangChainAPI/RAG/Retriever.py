import logging
from collections import defaultdict
import json
from redisvl.query import TextQuery, VectorQuery
from SharedKernel.base.Metrics import Metrics
from SharedKernel.persistence.RedisConnectionManager import get_redis_manager

class HybridRetriever:
    def __init__(self, embeddings, redis_url, connection_manager=None):
        self.embeddings = embeddings
        self.redis_url = redis_url
        self._manager = connection_manager or get_redis_manager()
        self._index = None
        self._store = None

    @property
    def index(self):
        """Lazy initialization of SearchIndex"""
        if self._index is None:
            self._index = self._manager.get_search_index(self.redis_url)
        return self._index

    @property
    def store(self):
        """Lazy initialization of RedisStore"""
        if self._store is None:
            self._store = self._manager.get_store(self.redis_url)
        return self._store

    async def retriever(self, query: str, k: int = 5):
        query_embed = await self.embeddings.aembed_query(query)

        vector_query = VectorQuery(
            vector=query_embed,
            vector_field_name="embedding",
            num_results=k,
            return_fields=["text", "_metadata_json"]
        )

        bm25_query = TextQuery(
            text=query,
            text_field_name="text",
            num_results=k,
            return_fields=["text", "_metadata_json"]
        )

        vector_docs = self.index.query(vector_query)
        bm25_docs = self.index.query(bm25_query)
        
        logging.info("vector_docs len = %s", len(vector_docs))
        logging.info("bm25_docs len = %s", len(bm25_docs))

        if not vector_docs and not bm25_docs:
            vector_docs = self.index.query(
                VectorQuery(
                    vector=query_embed,
                    vector_field_name="embedding",
                    num_results=k,
                    return_fields=["text", "_metadata_json"]
                )
            )
            logging.info("Retry vector query result: %s", len(vector_docs))

        fused = self.rrf_fusion([bm25_docs, vector_docs])

        filtered_score_fused = []
        for doc_id, score in fused:
            filtered_score_fused.append((doc_id, score))

        top_docs = filtered_score_fused[:k]

        doc_map = {}
        for doc in list(vector_docs) + list(bm25_docs):
            doc_id = doc.get("id")
            if not doc_id:
                continue
            metadata = doc.get("_metadata_json", {})
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            doc_map[doc_id] = {
                "text": doc.get("text", ""),
                "metadata": metadata
            }

        parent_to_children = defaultdict(list)
        for doc_id, _ in top_docs:
            if doc_id not in doc_map:
                continue
            metadata = doc_map[doc_id]["metadata"].copy()
            parent_id = doc_map[doc_id]["metadata"].get("parent_id")
            if not parent_id:
                continue
            parent_to_children[parent_id].append({
                "id": doc_id, "metadata": metadata
            })

        parent_ids = list(parent_to_children.keys())
        
        if not parent_ids:
            return []
        
        parent_docs = self.store.mget(parent_ids)

        results = []
        for i, parent in enumerate(parent_docs):
            if not parent:
                continue

            parent_id = parent_ids[i]

            try:
                parent_json = json.loads(parent.decode())
                parent_text = parent_json.get("page_content", "")
                parent_metadata = parent_json.get("metadata", {})
            except json.JSONDecodeError:
                parent_text = parent.decode()
                parent_metadata = {}

            child_ids = parent_to_children[parent_id]

            results.append({
                "id": parent_id,
                "content": parent_text,
                "metadata": parent_metadata,
                "children": child_ids,
            })
                
        return results

    def rrf_fusion(self, rank_lists, k: int = 60):
        """Reciprocal Rank Fusion for combining search results"""

        score_map = defaultdict(float)
        for ranking in rank_lists:
            for rank, doc in enumerate(ranking, start=1):
                doc_id = doc.get("id")
                if not doc_id:
                    continue
                score_map[doc_id] += 1 / (k + rank)
        return sorted(score_map.items(), key=lambda x: x[1], reverse=True)