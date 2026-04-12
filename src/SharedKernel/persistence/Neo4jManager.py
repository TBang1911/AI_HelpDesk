from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver
from SharedKernel.utils.yamlenv import load_env_yaml

config = load_env_yaml()

class Neo4jManager:
    _instance: Optional["Neo4jManager"] = None
    _driver: Optional[Driver] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._driver is None:
            self._initialize_driver()

    def _initialize_driver(self):
        neo4j_config = getattr(config, "neo4j", None)
        if not neo4j_config:
            raise ValueError("Neo4j configuration not found in config.yaml")

        self._driver = GraphDatabase.driver(
            neo4j_config.uri,
            auth=(neo4j_config.user, neo4j_config.password),
            max_connection_pool_size=50,
            connection_acquisition_timeout=60,
            max_transaction_retry_time=30,
        )

    def get_driver(self) -> Driver:
        if self._driver is None:
            self._initialize_driver()
        return self._driver

    def verify_connectivity(self) -> bool:
        if self._driver is None:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    def execute_query(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        driver = self.get_driver()
        with driver.session(database=database) as session:
            result = session.run(cypher, parameters or {})
            return [record.data() for record in result]

    def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> Dict[str, Any]:
        driver = self.get_driver()
        with driver.session(database=database) as session:
            result = session.run(query, parameters or {})
            return {
                "counters": result.consume().counters,
                "last_bookmark": session.last_bookmark(),
            }

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def refresh_connection(self):
        self.close()
        self._initialize_driver()


def get_neo4j_manager() -> Neo4jManager:
    return Neo4jManager()
