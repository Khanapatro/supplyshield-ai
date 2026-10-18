"""
Tests for Graph Seeding and Multi-Hop Integrity in FalkorDB
"""

import pytest
from app.graph.connection import get_graph
from app.graph.seed import seed_database, inspect_graph_counts

TEST_GRAPH = "test_supplyshield_pytest"

@pytest.fixture(scope="module")
def setup_test_graph():
    """Seeds a dedicated test graph before tests run and cleans up afterwards."""
    summary = seed_database(clear_existing=True, graph_name=TEST_GRAPH)
    yield summary
    # Teardown
    try:
        g = get_graph(TEST_GRAPH)
        g.delete()
    except Exception:
        pass

def test_graph_seed_counts(setup_test_graph):
    """Verifies that all expected nodes and relationships are seeded correctly."""
    counts = inspect_graph_counts(TEST_GRAPH)

    # Check minimum required entities from Master Prompt
    assert counts["nodes"]["Supplier"] >= 5, "At least 5 suppliers required"
    assert counts["nodes"]["Component"] >= 6, "At least 6 components required"
    assert counts["nodes"]["Factory"] >= 3, "At least 3 factories required"
    assert counts["nodes"]["Product"] >= 5, "At least 5 products required"
    assert counts["nodes"]["CustomerOrder"] >= 8, "At least 8 customer orders required"
    assert counts["nodes"]["Shipment"] >= 4, "At least 4 shipments required"
    assert counts["nodes"]["RiskEvent"] >= 2, "At least 2 risk events required"
    assert counts["nodes"]["Location"] >= 5, "Locations required"

    assert counts["relationships"]["SUPPLIES"] >= 6
    assert counts["relationships"]["USED_IN"] >= 10
    assert counts["relationships"]["ORDERS"] >= 8
    assert counts["relationships"]["ALTERNATIVE_TO"] >= 2

def test_seed_idempotency(setup_test_graph):
    """Running seed again must not duplicate any nodes or relationships."""
    initial_counts = inspect_graph_counts(TEST_GRAPH)

    # Run seed again without clearing
    seed_database(clear_existing=False, graph_name=TEST_GRAPH)

    after_counts = inspect_graph_counts(TEST_GRAPH)

    assert initial_counts["nodes"] == after_counts["nodes"], "Node counts should remain identical"
    assert initial_counts["relationships"] == after_counts["relationships"], "Relationship counts should remain identical"

def test_downstream_impact_traversal(setup_test_graph):
    """Traces Supplier -> Component -> Product -> CustomerOrder multi-hop path."""
    g = get_graph(TEST_GRAPH)

    query = """
    MATCH (s:Supplier {id: 'SUP-001'})-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product)<-[:ORDERS]-(o:CustomerOrder)
    RETURN count(DISTINCT p) AS affected_products, count(DISTINCT o) AS affected_orders
    """
    res = g.query(query)
    assert len(res.result_set) == 1
    affected_products, affected_orders = res.result_set[0]

    # SUP-001 supplies CMP-101 which is used in 3 products and affects 7 orders
    assert affected_products == 3, f"Expected 3 affected products, got {affected_products}"
    assert affected_orders == 7, f"Expected 7 affected orders, got {affected_orders}"

def test_alternative_supplier_relationship(setup_test_graph):
    """Verifies verified alternative supplier links exist for the disrupted supplier."""
    g = get_graph(TEST_GRAPH)

    query = """
    MATCH (alt:Supplier)-[r:ALTERNATIVE_TO]->(disrupted:Supplier {id: 'SUP-001'})
    RETURN alt.id AS alt_id, alt.name AS alt_name, r.compatibility_score AS compatibility, r.verified AS verified
    ORDER BY compatibility DESC
    """
    res = g.query(query)
    assert len(res.result_set) >= 1

    top_alt = res.result_set[0]
    assert top_alt[0] == "SUP-002", "Expected SUP-002 (Nexus) to be the top alternative"
    assert top_alt[3] is True, "Alternative must be marked verified"
    assert top_alt[2] >= 0.95, "Compatibility score must be >= 0.95"
