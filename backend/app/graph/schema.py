"""
Graph schema definitions and index management for FalkorDB.
"""

import logging
from typing import List, Tuple
from app.graph.connection import get_graph

logger = logging.getLogger(__name__)

# List of (Label, Property) to index for high-performance traversals
REQUIRED_INDEXES: List[Tuple[str, str]] = [
    ("Supplier", "id"),
    ("Component", "id"),
    ("Factory", "id"),
    ("Product", "id"),
    ("Shipment", "id"),
    ("CustomerOrder", "id"),
    ("Location", "id"),
    ("RiskEvent", "id"),
]

NODE_LABELS = [
    "Supplier",
    "Component",
    "Factory",
    "Product",
    "Shipment",
    "CustomerOrder",
    "Location",
    "RiskEvent",
]

RELATIONSHIPS = [
    "SUPPLIES",
    "USED_IN",
    "PRODUCES",
    "CARRIES",
    "FROM_SUPPLIER",
    "ORDERS",
    "LOCATED_IN",
    "AFFECTS",
    "ALTERNATIVE_TO",
]

def ensure_schema(graph_name: str | None = None) -> List[str]:
    """
    Ensures all indexes are created in FalkorDB.
    Idempotent: skips or handles already-indexed properties gracefully.
    """
    graph = get_graph(graph_name)
    created_indexes = []

    for label, prop in REQUIRED_INDEXES:
        query = f"CREATE INDEX FOR (n:{label}) ON (n.{prop})"
        try:
            graph.query(query)
            logger.info(f"Created index on :{label}({prop})")
            created_indexes.append(f"{label}.{prop} (created)")
        except Exception as e:
            err_msg = str(e).lower()
            if "already indexed" in err_msg or "already exists" in err_msg:
                created_indexes.append(f"{label}.{prop} (existing)")
            else:
                logger.warning(f"Could not create index on :{label}({prop}): {e}")
                created_indexes.append(f"{label}.{prop} (error: {e})")

    return created_indexes

def get_existing_indexes(graph_name: str | None = None) -> List[dict]:
    """Retrieves list of existing indexes via db.indexes()"""
    graph = get_graph(graph_name)
    try:
        res = graph.query("CALL db.indexes()")
        indexes = []
        for row in res.result_set:
            if row and len(row) > 1:
                indexes.append({"label": row[0], "properties": row[1]})
        return indexes
    except Exception as e:
        logger.error(f"Failed to query indexes: {e}")
        return []
