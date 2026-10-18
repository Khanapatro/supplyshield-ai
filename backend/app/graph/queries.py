"""
SupplyShield AI - Cypher Query Repository for FalkorDB
Contains parameterized graph queries for impact analysis, multi-hop path tracing, and alternative discovery.
"""

from typing import List, Dict, Any
from app.graph.connection import get_graph

def query_supply_chain_overview(graph_name: str | None = None) -> Dict[str, Any]:
    """Retrieves high-level summary of the supply chain entities."""
    g = get_graph(graph_name)

    labels = ["Supplier", "Component", "Factory", "Product", "CustomerOrder", "Shipment", "RiskEvent"]
    counts = {}
    for lbl in labels:
        try:
            res = g.query(f"MATCH (n:{lbl}) RETURN count(n)")
            counts[lbl] = res.result_set[0][0] if res.result_set else 0
        except Exception:
            counts[lbl] = 0

    return {
        "suppliers": counts.get("Supplier", 0),
        "components": counts.get("Component", 0),
        "factories": counts.get("Factory", 0),
        "products": counts.get("Product", 0),
        "customer_orders": counts.get("CustomerOrder", 0),
        "shipments": counts.get("Shipment", 0),
        "risk_events": counts.get("RiskEvent", 0)
    }

def query_all_suppliers(graph_name: str | None = None) -> List[Dict[str, Any]]:
    """Retrieves all suppliers with location and risk profile."""
    g = get_graph(graph_name)
    q = """
    MATCH (s:Supplier)
    OPTIONAL MATCH (s)-[:LOCATED_IN]->(l:Location)
    RETURN s.id AS id, s.name AS name, s.status AS status, s.capacity AS capacity,
           s.lead_time_days AS lead_time_days, s.risk_score AS risk_score,
           s.description AS description, l.name AS location_name, l.country AS country
    ORDER BY s.id
    """
    res = g.query(q)
    suppliers = []
    for r in res.result_set:
        suppliers.append({
            "id": r[0],
            "name": r[1],
            "status": r[2],
            "capacity": r[3],
            "lead_time_days": r[4],
            "risk_score": r[5],
            "description": r[6],
            "location": f"{r[7]}, {r[8]}" if r[7] else "Unknown"
        })
    return suppliers

def query_all_risk_events(graph_name: str | None = None) -> List[Dict[str, Any]]:
    """Retrieves active risk events."""
    g = get_graph(graph_name)
    q = """
    MATCH (r:RiskEvent)
    OPTIONAL MATCH (r)-[:AFFECTS]->(s:Supplier)
    OPTIONAL MATCH (r)-[:AFFECTS]->(sh:Shipment)
    RETURN r.id AS id, r.event_type AS event_type, r.severity AS severity,
           r.severity_score AS severity_score, r.status AS status, r.description AS description,
           collect(DISTINCT s.id) AS affected_suppliers,
           collect(DISTINCT sh.id) AS affected_shipments
    ORDER BY r.severity_score DESC
    """
    res = g.query(q)
    events = []
    for r in res.result_set:
        events.append({
            "id": r[0],
            "event_type": r[1],
            "severity": r[2],
            "severity_score": r[3],
            "status": r[4],
            "description": r[5],
            "affected_suppliers": [x for x in r[6] if x],
            "affected_shipments": [x for x in r[7] if x]
        })
    return events

def query_downstream_supplier_impact(supplier_id: str, graph_name: str | None = None) -> Dict[str, Any]:
    """
    Traces downstream impact from a supplier:
    Supplier -> Component -> Product -> CustomerOrder
    Also traces affected Factories producing those products.
    """
    g = get_graph(graph_name)

    # 1. Affected Components
    comp_q = """
    MATCH (s:Supplier {id: $sup_id})-[r:SUPPLIES]->(c:Component)
    RETURN c.id AS id, c.name AS name, c.criticality AS criticality,
           c.stock_quantity AS stock_quantity, c.unit_cost AS unit_cost,
           r.lead_time_days AS lead_time_days, r.is_primary AS is_primary
    """
    comp_res = g.query(comp_q, {"sup_id": supplier_id})
    components = []
    for r in comp_res.result_set:
        components.append({
            "id": r[0], "name": r[1], "criticality": r[2],
            "stock_quantity": r[3], "unit_cost": r[4],
            "lead_time_days": r[5], "is_primary": r[6]
        })

    # 2. Affected Products and Factories
    prod_q = """
    MATCH (s:Supplier {id: $sup_id})-[:SUPPLIES]->(c:Component)-[u:USED_IN]->(p:Product)
    OPTIONAL MATCH (f:Factory)-[:PRODUCES]->(p)
    RETURN p.id AS id, p.name AS name, p.category AS category, p.priority AS priority,
           p.unit_price AS unit_price, u.quantity_per_unit AS qty_per_unit,
           collect(DISTINCT f.name) AS factories
    """
    prod_res = g.query(prod_q, {"sup_id": supplier_id})
    products = []
    for r in prod_res.result_set:
        products.append({
            "id": r[0], "name": r[1], "category": r[2], "priority": r[3],
            "unit_price": r[4], "qty_per_unit": r[5], "factories": r[6]
        })

    # 3. Affected Customer Orders
    order_q = """
    MATCH (s:Supplier {id: $sup_id})-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product)<-[:ORDERS]-(o:CustomerOrder)
    RETURN o.id AS id, o.order_number AS order_number, o.customer_name AS customer_name,
           o.quantity AS quantity, o.priority AS priority, o.status AS status,
           o.days_until_due AS days_until_due, o.revenue AS revenue,
           p.name AS product_name, p.id AS product_id
    ORDER BY o.days_until_due ASC
    """
    order_res = g.query(order_q, {"sup_id": supplier_id})
    orders = []
    total_revenue_at_risk = 0.0
    for r in order_res.result_set:
        rev = float(r[7] or 0.0)
        total_revenue_at_risk += rev
        orders.append({
            "id": r[0], "order_number": r[1], "customer_name": r[2],
            "quantity": r[3], "priority": r[4], "status": r[5],
            "days_until_due": r[6], "revenue": rev,
            "product_name": r[8], "product_id": r[9]
        })

    # 4. Evidence Paths (Complete multi-hop paths)
    paths_q = """
    MATCH path = (s:Supplier {id: $sup_id})-[:SUPPLIES]->(c:Component)-[:USED_IN]->(p:Product)<-[:ORDERS]-(o:CustomerOrder)
    RETURN s.name AS supplier, c.name AS component, p.name AS product, o.order_number AS order_num, o.customer_name AS customer
    """
    paths_res = g.query(paths_q, {"sup_id": supplier_id})
    evidence_paths = []
    for r in paths_res.result_set:
        evidence_paths.append({
            "path_string": f"[{r[0]}] -> SUPPLIES -> [{r[1]}] -> USED_IN -> [{r[2]}] -> ORDERS -> [{r[3]}] ({r[4]})",
            "supplier": r[0],
            "component": r[1],
            "product": r[2],
            "order": r[3],
            "customer": r[4]
        })

    return {
        "supplier_id": supplier_id,
        "affected_components": components,
        "affected_products": products,
        "affected_orders": orders,
        "total_revenue_at_risk": total_revenue_at_risk,
        "evidence_paths": evidence_paths
    }

def query_alternative_suppliers(disrupted_supplier_id: str, component_id: str, graph_name: str | None = None) -> List[Dict[str, Any]]:
    """
    Queries all potential alternative suppliers for a component,
    excluding the disrupted supplier. Looks for:
    1. Direct verified ALTERNATIVE_TO relationships.
    2. Suppliers who supply compatible components.
    """
    g = get_graph(graph_name)

    # Cypher query searching both direct alternative edges and compatible supply edges
    q = """
    MATCH (alt:Supplier)
    WHERE alt.id <> $disrupted_id
    OPTIONAL MATCH (alt)-[alt_rel:ALTERNATIVE_TO]->(s_orig:Supplier {id: $disrupted_id})
    OPTIONAL MATCH (alt)-[sup_rel:SUPPLIES]->(c_alt:Component)
    WHERE c_alt.id = $comp_id OR c_alt.id = alt_rel.component_id
    RETURN DISTINCT
        alt.id AS supplier_id,
        alt.name AS supplier_name,
        alt.status AS status,
        alt.capacity AS capacity,
        alt.lead_time_days AS lead_time_days,
        alt.risk_score AS risk_score,
        c_alt.id AS supplied_component_id,
        c_alt.name AS supplied_component_name,
        c_alt.qualification_standard AS qualification,
        alt_rel.compatibility_score AS compatibility_score,
        alt_rel.verified AS is_verified,
        alt_rel.verification_notes AS notes
    """
    res = g.query(q, {"disrupted_id": disrupted_supplier_id, "comp_id": component_id})
    candidates = []
    seen = set()

    for r in res.result_set:
        sup_id = r[0]
        if sup_id in seen:
            continue
        seen.add(sup_id)

        candidates.append({
            "supplier_id": r[0],
            "supplier_name": r[1],
            "status": r[2],
            "capacity": r[3] or 0,
            "lead_time_days": r[4] or 999,
            "risk_score": r[5] or 1.0,
            "supplied_component_id": r[6],
            "supplied_component_name": r[7],
            "qualification": r[8],
            "compatibility_score": r[9] if r[9] is not None else 0.5,
            "is_verified": bool(r[10]),
            "verification_notes": r[11] or "No direct compatibility verification recorded."
        })

    return candidates

def query_visual_graph(graph_name: str | None = None) -> Dict[str, Any]:
    """Retrieves full nodes and relationships for visual graph renderers."""
    g = get_graph(graph_name)

    nodes_q = """
    MATCH (n)
    RETURN id(n) AS internal_id, labels(n)[0] AS label, n.id AS business_id,
           COALESCE(n.name, n.order_number, n.tracking_number, n.event_type) AS display_name,
           n.status AS status, n.priority AS priority, n.severity AS severity
    """
    nodes_res = g.query(nodes_q)
    nodes = []
    for r in nodes_res.result_set:
        nodes.append({
            "id": r[2] or f"node_{r[0]}",
            "internal_id": r[0],
            "label": r[1],
            "name": r[3] or "Unknown",
            "status": r[4],
            "priority": r[5],
            "severity": r[6]
        })

    edges_q = """
    MATCH (a)-[r]->(b)
    RETURN a.id AS source, b.id AS target, type(r) AS rel_type
    """
    edges_res = g.query(edges_q)
    edges = []
    for r in edges_res.result_set:
        if r[0] and r[1]:
            edges.append({
                "source": r[0],
                "target": r[1],
                "label": r[2]
            })

    return {"nodes": nodes, "edges": edges}

def record_recovery_action(
    disrupted_supplier_id: str,
    selected_alternative_id: str,
    component_id: str,
    justification: str,
    score: float,
    agent_name: str = "SupplyShield AI Agent",
    graph_name: str | None = None
) -> Dict[str, Any]:
    """
    Acts on graph findings and persists agent decision memory in FalkorDB:
    Creates (:RecoveryAction) node connected to Disrupted Supplier and Chosen Alternative.
    Satisfies 'Actions based on what graph shows' & 'Remember across sessions'.
    """
    g = get_graph(graph_name)
    import time
    action_id = f"ACT-{int(time.time())}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    q = """
    MATCH (disrupted:Supplier {id: $disrupted_id})
    MATCH (alt:Supplier {id: $alt_id})
    CREATE (act:RecoveryAction {
        id: $action_id,
        action_type: 'REROUTE_SUPPLY',
        status: 'EXECUTED',
        component_id: $comp_id,
        justification: $justification,
        decision_score: $score,
        agent_name: $agent_name,
        timestamp: $timestamp
    })
    CREATE (act)-[:REPLACES]->(disrupted)
    CREATE (act)-[:CONTRACTS_TO]->(alt)
    RETURN act.id, act.status, act.timestamp
    """
    res = g.query(q, {
        "disrupted_id": disrupted_supplier_id,
        "alt_id": selected_alternative_id,
        "action_id": action_id,
        "comp_id": component_id,
        "justification": justification,
        "score": score,
        "agent_name": agent_name,
        "timestamp": timestamp
    })
    row = res.result_set[0] if res.result_set else [action_id, "EXECUTED", timestamp]
    return {
        "action_id": row[0],
        "status": row[1],
        "timestamp": row[2],
        "disrupted_supplier": disrupted_supplier_id,
        "selected_alternative": selected_alternative_id,
        "component_id": component_id,
        "decision_score": score
    }

def query_action_history(graph_name: str | None = None) -> List[Dict[str, Any]]:
    """Retrieves past agent decisions and actions stored in FalkorDB graph memory."""
    g = get_graph(graph_name)
    q = """
    MATCH (act:RecoveryAction)-[:REPLACES]->(disrupted:Supplier)
    MATCH (act)-[:CONTRACTS_TO]->(alt:Supplier)
    RETURN act.id AS action_id, act.timestamp AS timestamp, act.action_type AS action_type,
           act.status AS status, act.decision_score AS score, act.justification AS justification,
           disrupted.id AS disrupted_id, disrupted.name AS disrupted_name,
           alt.id AS alt_id, alt.name AS alt_name
    ORDER BY act.timestamp DESC
    """
    res = g.query(q)
    history = []
    for r in res.result_set:
        history.append({
            "action_id": r[0],
            "timestamp": r[1],
            "action_type": r[2],
            "status": r[3],
            "decision_score": r[4],
            "justification": r[5],
            "disrupted_supplier": f"{r[7]} ({r[6]})",
            "alternative_contracted": f"{r[9]} ({r[8]})"
        })
    return history

