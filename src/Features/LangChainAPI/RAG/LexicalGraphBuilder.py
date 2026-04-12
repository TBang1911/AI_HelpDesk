import logging
from typing import Any, Dict, List
from langchain_core.documents import Document
from SharedKernel.utils.yamlenv import load_env_yaml

log = logging.getLogger(__name__)
config = load_env_yaml()

class LexicalGraphBuilder:
    def __init__(self, process, embedding_model, llm_provider, neo4j_store):
        self.process = process
        self.embedding_model = embedding_model
        self.llm_provider = llm_provider
        self.neo4j_store = neo4j_store

    @property
    def section_size(self):
        return (
            getattr(config, "lexical_graph", None).section_size
            if hasattr(config, "lexical_graph")
            else 10
        )

    @property
    def separators(self):
        return (
            getattr(config, "lexical_graph", None).separators
            if hasattr(config, "lexical_graph")
            else None
        )

    @property
    def entity_types(self):
        return (
            getattr(config, "lexical_graph", None).entity_types
            if hasattr(config, "lexical_graph")
            else None
        )

    def get_separators(self, file_type: str = "generic") -> List[str]:
        if self.separators:
            file_specific = getattr(self.separators, file_type, None)
            generic = getattr(self.separators, "generic", ["\n\n", "\n"])
            return file_specific if file_specific else generic
        return ["\n\n", "\n"]

    def get_entity_types(self, file_type: str = "generic") -> List[str]:
        if self.entity_types:
            universal = getattr(self.entity_types, "universal", [])
            file_specific = getattr(self.entity_types, file_type, [])
            return universal + file_specific if file_type != "generic" else universal
        return ["PERSON", "ORGANIZATION", "LOCATION", "CONCEPT"]

    async def build_graph(self, documents: List[Document], source: str):
        log.info(f"Starting build graph for source: {source}")

        chunks = self.process.split_PaC(documents)
        child_chunks = chunks.get("children", [])
        log.info(f"Split into {len(child_chunks)} chunks")

        embeddings = await self._batch_embed_chunks(child_chunks)
        log.info(f"Generated {len(embeddings)} embeddings")

        sections = self._group_into_sections(
            child_chunks, section_size=self.section_size
        )
        log.info(f"Grouped into {len(sections)} sections")

        entities = await self._batch_extract_entities(sections)
        log.info(f"Extracted {len(entities)} entities")

        nodes, edges = self._build_hierarchical_structure(
            chunks, sections, entities, embeddings
        )
        log.info(f"Built {len(nodes)} nodes, {len(edges)} edges")

        await self.neo4j_store.add_graph(nodes, edges)

        return {
            "sections": len(sections),
            "chunks": len(child_chunks),
            "entities": len(entities),
            "nodes": len(nodes),
            "edges": len(edges),
        }

    async def _batch_embed_chunks(self, chunks: List[Document]) -> List[List[float]]:
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_model.embed_documents(texts)
        return embeddings

    def _group_into_sections(
        self, chunks: List[Document], section_size: int = 10
    ) -> List[Dict[str, Any]]:
        sections = []
        for i in range(0, len(chunks), section_size):
            section_chunks = chunks[i : i + section_size]
            section_content = "\n".join([c.page_content for c in section_chunks])
            sections.append(
                {
                    "section_id": f"section_{i // section_size}",
                    "chunks": section_chunks,
                    "content": section_content,
                    "chunk_indices": list(range(i, min(i + section_size, len(chunks)))),
                }
            )
        return sections

    async def _batch_extract_entities(self, sections: List[Dict]) -> List[Dict]:
        entities = []
        for section in sections:
            section_entities = await self._extract_section_entities(section)
            entities.extend(section_entities)
        return entities

    async def _extract_section_entities(self, section: Dict) -> List[Dict]:
        entity_types = self.get_entity_types()
        entity_types_str = ", ".join(entity_types)

        prompt = f"""
            Extract entities from the following section text.

            Section:
            {section["content"]}

            Extract entities ({entity_types_str}) with their types.
            Return as JSON list: [{{"name": "...", "type": "..."}}]
        """
        try:
            response = self.llm_provider.invoke(prompt)
            entities = self._parse_llm_entities(response)
            for e in entities:
                e["section_id"] = section["section_id"]
            return entities
        except Exception as e:
            log.error(f"Entity extraction failed: {e}")
            return []

    def _parse_llm_entities(self, response) -> List[Dict]:
        import json

        try:
            return json.loads(response.content)
        except:
            return []

    def _build_hierarchical_structure(
        self,
        chunks: Dict,
        sections: List[Dict],
        entities: List[Dict],
        embeddings: List[List[float]],
    ) -> tuple:
        nodes = []
        edges = []

        child_chunks = chunks.get("children", [])
        for i, chunk in enumerate(child_chunks):
            node_id = f"chunk_{i}"
            nodes.append(
                {
                    "id": node_id,
                    "type": "Chunk",
                    "content": chunk.page_content,
                    "embedding": embeddings[i] if i < len(embeddings) else None,
                    "metadata": chunk.metadata,
                }
            )

        for section in sections:
            section_node_id = section["section_id"]
            nodes.append(
                {
                    "id": section_node_id,
                    "type": "Section",
                    "content": section["content"],
                    "summary": "",
                    "metadata": {"chunk_indices": section["chunk_indices"]},
                }
            )

            chunk_indices = section["chunk_indices"]
            for idx in chunk_indices:
                edges.append(
                    {
                        "source": section_node_id,
                        "target": f"chunk_{idx}",
                        "type": "CONTAINS",
                    }
                )

        for entity in entities:
            entity_id = f"entity_{entity['name']}_{entity['type']}"
            nodes.append(
                {
                    "id": entity_id,
                    "type": "Entity",
                    "name": entity["name"],
                    "entity_type": entity["type"],
                    "metadata": {"section_id": entity.get("section_id")},
                }
            )

            if entity.get("section_id"):
                edges.append(
                    {
                        "source": entity["section_id"],
                        "target": entity_id,
                        "type": "SUMMARIZES",
                    }
                )

        return nodes, edges
