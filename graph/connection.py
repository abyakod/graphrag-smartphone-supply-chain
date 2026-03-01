"""
PhoneGraph: Memgraph Connection Manager

Provides singleton connection to Memgraph database with health checking,
retry logic, and both gqlalchemy and LangChain connection interfaces.
"""

import os
import logging
from typing import Optional

from gqlalchemy import Memgraph
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


def get_memgraph_host() -> str:
    """Get Memgraph host from environment variable or default."""
    return os.getenv("MEMGRAPH_HOST", "localhost")


def get_memgraph_port() -> int:
    """Get Memgraph port from environment variable or default."""
    return int(os.getenv("MEMGRAPH_PORT", "7687"))


class MemgraphConnection:
    """
    Singleton connection manager for Memgraph database.
    
    Provides both raw gqlalchemy connection for direct Cypher queries
    and LangChain-compatible connection for GraphRAG chains.
    """
    
    _instance: Optional["MemgraphConnection"] = None
    _memgraph: Optional[Memgraph] = None
    
    def __new__(cls) -> "MemgraphConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._memgraph is None:
            self._connect()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    def _connect(self) -> None:
        """Establish connection to Memgraph with retry logic."""
        host = get_memgraph_host()
        port = get_memgraph_port()
        logger.info(f"Connecting to Memgraph at {host}:{port}...")
        
        try:
            self._memgraph = Memgraph(host=host, port=port)
            # Test connection
            result = list(self._memgraph.execute_and_fetch("RETURN 1 AS alive"))
            if result and result[0]["alive"] == 1:
                logger.info("✅ Successfully connected to Memgraph")
            else:
                raise ConnectionError("Memgraph connection test failed")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Memgraph: {e}")
            self._memgraph = None
            raise
    
    @property
    def db(self) -> Memgraph:
        """Get the raw Memgraph gqlalchemy connection."""
        if self._memgraph is None:
            self._connect()
        return self._memgraph
    
    def execute(self, query: str) -> None:
        """Execute a Cypher query without returning results."""
        self.db.execute(query)
    
    def execute_and_fetch(self, query: str) -> list:
        """Execute a Cypher query and return all results as a list."""
        return list(self.db.execute_and_fetch(query))
    
    def health_check(self) -> dict:
        """
        Perform a comprehensive health check on the Memgraph connection.
        
        Returns:
            dict with keys: status, node_count, edge_count, memory_usage
        """
        try:
            # Basic connectivity
            result = self.execute_and_fetch("RETURN 1 AS alive")
            if not result:
                return {"status": "unhealthy", "error": "No response from Memgraph"}
            
            # Node count
            node_result = self.execute_and_fetch("MATCH (n) RETURN count(n) AS count")
            node_count = node_result[0]["count"] if node_result else 0
            
            # Edge count
            edge_result = self.execute_and_fetch(
                "MATCH ()-[r]->() RETURN count(r) AS count"
            )
            edge_count = edge_result[0]["count"] if edge_result else 0
            
            # Storage info
            try:
                storage = self.execute_and_fetch("SHOW STORAGE INFO")
                memory_info = {item["storage info"]: item["value"] for item in storage} if storage else {}
            except Exception:
                memory_info = {}
            
            return {
                "status": "healthy",
                "node_count": node_count,
                "edge_count": edge_count,
                "memory_info": memory_info,
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def clear_database(self) -> None:
        """Drop all nodes and relationships from the database."""
        logger.warning("🗑️ Clearing entire Memgraph database...")
        self.execute("MATCH (n) DETACH DELETE n")
        logger.info("✅ Database cleared")
    
    def get_schema_info(self) -> dict:
        """Get current schema information from Memgraph."""
        try:
            node_labels = self.execute_and_fetch(
                "MATCH (n) RETURN DISTINCT labels(n) AS labels, count(n) AS count"
            )
            edge_types = self.execute_and_fetch(
                "MATCH ()-[r]->() RETURN DISTINCT type(r) AS type, count(r) AS count"
            )
            return {
                "node_labels": [
                    {"labels": r["labels"], "count": r["count"]} for r in node_labels
                ],
                "edge_types": [
                    {"type": r["type"], "count": r["count"]} for r in edge_types
                ],
            }
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {"node_labels": [], "edge_types": []}


def get_langchain_graph():
    """
    Get a LangChain-compatible Memgraph graph instance.
    
    Used by MemgraphQAChain and other LangChain components.
    
    Returns:
        MemgraphLangChain instance
    """
    from langchain_memgraph.graphs.memgraph_graph import MemgraphGraph
    
    host = get_memgraph_host()
    port = get_memgraph_port()
    url = f"bolt://{host}:{port}"
    
    logger.info(f"Creating LangChain Memgraph connection at {url}")
    
    graph = MemgraphGraph(
        url=url,
        username="",
        password="",
        refresh_schema=True,
    )
    
    return graph


# Module-level convenience functions
def get_connection() -> MemgraphConnection:
    """Get the singleton Memgraph connection instance."""
    return MemgraphConnection()


def get_db() -> Memgraph:
    """Get the raw Memgraph gqlalchemy database instance."""
    return get_connection().db
