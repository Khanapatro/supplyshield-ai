"""
SupplyShield AI - Phase 1 FalkorDB Verification Script
Tests database connectivity, graph node/relationship creation, and Cypher querying.
"""

import sys
from falkordb import FalkorDB

def verify_falkordb(host: str = "127.0.0.1", port: int = 6379):
    print(f"[*] Connecting to FalkorDB at {host}:{port}...")
    try:
        db = FalkorDB(host=host, port=port)
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        sys.exit(1)

    graph_name = "test_supplyshield"
    graph = db.select_graph(graph_name)
    print(f"[+] Connected successfully! Using graph: '{graph_name}'")

    # Step 1: Clean test graph
    print("[*] Resetting test graph...")
    try:
        graph.delete()
        # Re-select after delete
        graph = db.select_graph(graph_name)
    except Exception:
        pass

    # Step 2: Create test nodes and relationship
    print("[*] Creating test nodes and relationship (:Supplier)-[:SUPPLIES]->(:Component)...")
    create_query = """
    CREATE (s:Supplier {id: 'SUP-001', name: 'Apex Semiconductors', location: 'Taiwan', capacity: 10000})
    CREATE (c:Component {id: 'CMP-101', name: 'Automotive Microcontroller MCU-v2', unit_cost: 45.50})
    CREATE (s)-[r:SUPPLIES {lead_time_days: 14, min_order_qty: 500}]->(c)
    """
    res_create = graph.query(create_query)
    print(f"[+] Created {res_create.nodes_created} nodes, {res_create.relationships_created} relationships in {res_create.run_time_ms:.2f} ms")

    # Step 3: Query back using Cypher
    print("[*] Querying relationship from FalkorDB using Cypher...")
    match_query = """
    MATCH (s:Supplier)-[r:SUPPLIES]->(c:Component)
    RETURN s.id AS supplier_id,
           s.name AS supplier_name,
           s.location AS location,
           type(r) AS rel_type,
           r.lead_time_days AS lead_time_days,
           c.id AS component_id,
           c.name AS component_name
    """
    res_match = graph.query(match_query)

    print("\n--- QUERY RESULTS FROM FALKORDB ---")
    headers = ["Supplier ID", "Supplier Name", "Location", "Relation", "Lead Time (days)", "Component ID", "Component Name"]
    print(f"{headers[0]:<14} | {headers[1]:<22} | {headers[2]:<10} | {headers[3]:<10} | {headers[4]:<16} | {headers[5]:<14} | {headers[6]}")
    print("-" * 115)
    for row in res_match.result_set:
        print(f"{str(row[0]):<14} | {str(row[1]):<22} | {str(row[2]):<10} | {str(row[3]):<10} | {str(row[4]):<16} | {str(row[5]):<14} | {str(row[6])}")

    print("\n[+] Verification successful! FalkorDB is active, responsive, and processing Cypher queries properly.")

if __name__ == "__main__":
    verify_falkordb()
