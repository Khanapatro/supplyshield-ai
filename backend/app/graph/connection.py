"""Graph connection module for FalkorDB"""

import logging
from falkordb import FalkorDB, Graph
from app.config import settings

logger = logging.getLogger(__name__)

class GraphConnectionError(Exception):
    """Raised when FalkorDB is unreachable."""
    pass

def get_falkordb_client() -> FalkorDB:
    """Instantiate FalkorDB client using configured settings."""
    try:
        client = FalkorDB(host=settings.FALKORDB_HOST, port=settings.FALKORDB_PORT)
        # Perform quick connection check
        client.connection.ping()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to FalkorDB at {settings.FALKORDB_HOST}:{settings.FALKORDB_PORT} - {e}")
        raise GraphConnectionError(
            f"FalkorDB is unreachable at {settings.FALKORDB_HOST}:{settings.FALKORDB_PORT}. "
            "Ensure the Docker container 'supplyshield-db' is running."
        ) from e

def get_graph(graph_name: str | None = None) -> Graph:
    """Retrieve the selected FalkorDB graph instance."""
    client = get_falkordb_client()
    target_graph = graph_name or settings.FALKORDB_GRAPH_NAME
    return client.select_graph(target_graph)
