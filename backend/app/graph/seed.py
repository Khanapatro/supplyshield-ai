"""
SupplyShield AI - Repeatable Graph Seeder
Loads synthetic supply chain data into FalkorDB idempotently using MERGE queries.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

from app.config import settings
from app.graph.connection import get_graph
from app.graph.schema import ensure_schema

logger = logging.getLogger(__name__)

def load_dataset(file_path: Path | None = None) -> Dict[str, Any]:
    """Loads the synthetic supply chain dataset from JSON."""
    path = file_path or settings.DATA_FILE
    if not path.exists():
        # Fallback to check relative to root
        alt_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / "synthetic_supply_chain.json"
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(f"Synthetic supply chain data file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def seed_database(clear_existing: bool = False, graph_name: str | None = None) -> Dict[str, Any]:
    """
    Seeds FalkorDB with synthetic supply chain data.
    Ensures idempotency using MERGE so running multiple times produces no duplicate nodes or relationships.
    """
    start_time = time.time()
    graph = get_graph(graph_name)

    if clear_existing:
        logger.info("Clearing existing graph data...")
        try:
            graph.delete()
            graph = get_graph(graph_name)
        except Exception as e:
            logger.warning(f"Note on graph reset: {e}")

    # Ensure indexes exist
    ensure_schema(graph_name)

    data = load_dataset()

    # 1. Seed Locations
    for loc in data.get("locations", []):
        query = """
        MERGE (l:Location {id: $id})
        ON CREATE SET l.name = $name, l.country = $country, l.region = $region, l.is_synthetic = true
        ON MATCH SET l.name = $name, l.country = $country, l.region = $region
        """
        graph.query(query, loc)

    # 2. Seed Suppliers & Location edges
    for sup in data.get("suppliers", []):
        query = """
        MERGE (s:Supplier {id: $id})
        ON CREATE SET s.name = $name, s.status = $status, s.capacity = $capacity,
                      s.lead_time_days = $lead_time_days, s.risk_score = $risk_score,
                      s.description = $description, s.is_synthetic = true
        ON MATCH SET s.name = $name, s.status = $status, s.capacity = $capacity,
                     s.lead_time_days = $lead_time_days, s.risk_score = $risk_score,
                     s.description = $description
        WITH s
        MATCH (l:Location {id: $location_id})
        MERGE (s)-[:LOCATED_IN]->(l)
        """
        graph.query(query, sup)

    # 3. Seed Components
    for comp in data.get("components", []):
        query = """
        MERGE (c:Component {id: $id})
        ON CREATE SET c.name = $name, c.category = $category, c.criticality = $criticality,
                      c.unit_cost = $unit_cost, c.stock_quantity = $stock_quantity,
                      c.safety_stock = $safety_stock, c.qualification_standard = $qualification_standard,
                      c.is_synthetic = true
        ON MATCH SET c.name = $name, c.category = $category, c.criticality = $criticality,
                     c.unit_cost = $unit_cost, c.stock_quantity = $stock_quantity,
                     c.safety_stock = $safety_stock, c.qualification_standard = $qualification_standard
        """
        graph.query(query, comp)

    # 4. Seed Factories & Location edges
    for fac in data.get("factories", []):
        query = """
        MERGE (f:Factory {id: $id})
        ON CREATE SET f.name = $name, f.capacity_utilization = $capacity_utilization,
                      f.monthly_vehicle_capacity = $monthly_vehicle_capacity, f.is_synthetic = true
        ON MATCH SET f.name = $name, f.capacity_utilization = $capacity_utilization,
                     f.monthly_vehicle_capacity = $monthly_vehicle_capacity
        WITH f
        MATCH (l:Location {id: $location_id})
        MERGE (f)-[:LOCATED_IN]->(l)
        """
        graph.query(query, fac)

    # 5. Seed Products
    for prd in data.get("products", []):
        query = """
        MERGE (p:Product {id: $id})
        ON CREATE SET p.name = $name, p.category = $category, p.priority = $priority,
                      p.unit_price = $unit_price, p.is_synthetic = true
        ON MATCH SET p.name = $name, p.category = $category, p.priority = $priority,
                     p.unit_price = $unit_price
        """
        graph.query(query, prd)

    # 6. Seed CustomerOrders & Product edges
    for ord_item in data.get("customer_orders", []):
        query = """
        MERGE (o:CustomerOrder {id: $id})
        ON CREATE SET o.order_number = $order_number, o.customer_name = $customer_name,
                      o.quantity = $quantity, o.priority = $priority, o.status = $status,
                      o.days_until_due = $days_until_due, o.revenue = $revenue, o.is_synthetic = true
        ON MATCH SET o.order_number = $order_number, o.customer_name = $customer_name,
                     o.quantity = $quantity, o.priority = $priority, o.status = $status,
                     o.days_until_due = $days_until_due, o.revenue = $revenue
        WITH o
        MATCH (p:Product {id: $product_id})
        MERGE (o)-[:ORDERS]->(p)
        """
        graph.query(query, ord_item)

    # 7. Seed Shipments & Edges
    for shp in data.get("shipments", []):
        query = """
        MERGE (sh:Shipment {id: $id})
        ON CREATE SET sh.tracking_number = $tracking_number, sh.quantity = $quantity,
                      sh.status = $status, sh.eta_days = $eta_days,
                      sh.original_eta_days = $original_eta_days, sh.is_synthetic = true
        ON MATCH SET sh.tracking_number = $tracking_number, sh.quantity = $quantity,
                     sh.status = $status, sh.eta_days = $eta_days,
                     sh.original_eta_days = $original_eta_days
        WITH sh
        MATCH (s:Supplier {id: $supplier_id})
        MERGE (sh)-[:FROM_SUPPLIER]->(s)
        WITH sh
        MATCH (c:Component {id: $component_id})
        MERGE (sh)-[r:CARRIES]->(c)
        ON CREATE SET r.quantity = $quantity
        ON MATCH SET r.quantity = $quantity
        """
        graph.query(query, shp)

    # 8. Seed RiskEvents & Affected edges
    for evt in data.get("risk_events", []):
        query = """
        MERGE (r:RiskEvent {id: $id})
        ON CREATE SET r.event_type = $event_type, r.severity = $severity,
                      r.severity_score = $severity_score, r.status = $status,
                      r.description = $description, r.is_synthetic = true
        ON MATCH SET r.event_type = $event_type, r.severity = $severity,
                     r.severity_score = $severity_score, r.status = $status,
                     r.description = $description
        """
        graph.query(query, evt)

        # Connect affected suppliers
        for sup_id in evt.get("affected_supplier_ids", []):
            edge_q = """
            MATCH (r:RiskEvent {id: $evt_id}), (s:Supplier {id: $sup_id})
            MERGE (r)-[:AFFECTS]->(s)
            """
            graph.query(edge_q, {"evt_id": evt["id"], "sup_id": sup_id})

        # Connect affected shipments
        for shp_id in evt.get("affected_shipment_ids", []):
            edge_q = """
            MATCH (r:RiskEvent {id: $evt_id}), (sh:Shipment {id: $shp_id})
            MERGE (r)-[:AFFECTS]->(sh)
            """
            graph.query(edge_q, {"evt_id": evt["id"], "shp_id": shp_id})

    # 9. Seed Relationships from JSON
    rels = data.get("relationships", {})

    # SUPPLIES
    for rel in rels.get("supplies", []):
        query = """
        MATCH (s:Supplier {id: $supplier_id}), (c:Component {id: $component_id})
        MERGE (s)-[r:SUPPLIES]->(c)
        ON CREATE SET r.lead_time_days = $lead_time_days, r.daily_capacity = $daily_capacity,
                      r.unit_cost = $unit_cost, r.is_primary = $is_primary
        ON MATCH SET r.lead_time_days = $lead_time_days, r.daily_capacity = $daily_capacity,
                     r.unit_cost = $unit_cost, r.is_primary = $is_primary
        """
        graph.query(query, rel)

    # USED_IN
    for rel in rels.get("used_in", []):
        query = """
        MATCH (c:Component {id: $component_id}), (p:Product {id: $product_id})
        MERGE (c)-[r:USED_IN]->(p)
        ON CREATE SET r.quantity_per_unit = $quantity_per_unit
        ON MATCH SET r.quantity_per_unit = $quantity_per_unit
        """
        graph.query(query, rel)

    # PRODUCES
    for rel in rels.get("produces", []):
        query = """
        MATCH (f:Factory {id: $factory_id}), (p:Product {id: $product_id})
        MERGE (f)-[:PRODUCES]->(p)
        """
        graph.query(query, rel)

    # ALTERNATIVE_TO (Verified alternative relationships)
    for rel in rels.get("alternative_to", []):
        query = """
        MATCH (s1:Supplier {id: $from_supplier_id}), (s2:Supplier {id: $to_supplier_id})
        MERGE (s1)-[r:ALTERNATIVE_TO]->(s2)
        ON CREATE SET r.compatibility_score = $compatibility_score,
                      r.verified = $verified,
                      r.verification_notes = $verification_notes,
                      r.component_id = $component_id,
                      r.target_component_id = $target_component_id
        ON MATCH SET r.compatibility_score = $compatibility_score,
                     r.verified = $verified,
                     r.verification_notes = $verification_notes,
                     r.component_id = $component_id,
                     r.target_component_id = $target_component_id
        """
        graph.query(query, rel)

    elapsed = (time.time() - start_time) * 1000

    # Collect graph statistics
    counts = inspect_graph_counts(graph_name)

    return {
        "status": "success",
        "graph_name": graph_name or settings.FALKORDB_GRAPH_NAME,
        "execution_time_ms": round(elapsed, 2),
        "node_counts": counts["nodes"],
        "relationship_counts": counts["relationships"],
        "total_nodes": sum(counts["nodes"].values()),
        "total_relationships": sum(counts["relationships"].values())
    }

def inspect_graph_counts(graph_name: str | None = None) -> Dict[str, Any]:
    """Queries total counts for all node labels and relationship types."""
    graph = get_graph(graph_name)

    labels = ["Supplier", "Component", "Factory", "Product", "Shipment", "CustomerOrder", "Location", "RiskEvent"]
    node_counts = {}
    for lbl in labels:
        try:
            res = graph.query(f"MATCH (n:{lbl}) RETURN count(n)")
            node_counts[lbl] = res.result_set[0][0] if res.result_set else 0
        except Exception:
            node_counts[lbl] = 0

    rel_types = ["SUPPLIES", "USED_IN", "PRODUCES", "CARRIES", "FROM_SUPPLIER", "ORDERS", "LOCATED_IN", "AFFECTS", "ALTERNATIVE_TO"]
    rel_counts = {}
    for r in rel_types:
        try:
            res = graph.query(f"MATCH ()-[rel:{r}]->() RETURN count(rel)")
            rel_counts[r] = res.result_set[0][0] if res.result_set else 0
        except Exception:
            rel_counts[r] = 0

    return {
        "nodes": node_counts,
        "relationships": rel_counts
    }

if __name__ == "__main__":
    print("[*] Starting repeatable FalkorDB seeding...")
    summary = seed_database(clear_existing=True)
    print("\n--- SEEDING COMPLETED ---")
    print(f"Graph: {summary['graph_name']}")
    print(f"Execution time: {summary['execution_time_ms']} ms")
    print("\nNode Counts:")
    for lbl, cnt in summary['node_counts'].items():
        print(f"  - {lbl:<15}: {cnt}")
    print(f"  TOTAL NODES: {summary['total_nodes']}")

    print("\nRelationship Counts:")
    for r, cnt in summary['relationship_counts'].items():
        print(f"  - {r:<15}: {cnt}")
    print(f"  TOTAL RELATIONSHIPS: {summary['total_relationships']}")
