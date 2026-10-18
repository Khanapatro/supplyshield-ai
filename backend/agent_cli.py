"""
SupplyShield AI - Interactive Disruption Response Agent CLI
Demonstrates Graph Traversal, Multi-Hop Reasoning, Deterministic Scoring, and Graph Action Execution.
"""

import sys
import time

# Ensure Windows terminals support UTF-8 characters cleanly
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.graph.connection import get_falkordb_client, get_graph
from app.graph.queries import (
    query_supply_chain_overview,
    query_all_suppliers,
    record_recovery_action,
    query_action_history
)
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.supplier_evaluator import SupplierEvaluator
from app.services.recovery_planner import RecoveryPlanner


def print_banner():
    banner = r"""
========================================================================================
     _____                       _         _____ _     _      _     _      ___  _____ 
    /  ___|                     | |       /  ___| |   (_)    | |   | |    / _ \|_   _|
    \ `--. _   _ _ __  _ __   __| |___    \ `--.| |__  _  ___| | __| |   / /_\ \ | |  
     `--. \ | | | '_ \| '_ \ / _` / __|    `--. \ '_ \| |/ _ \ |/ _` |   |  _  | | |  
    /\__/ / |_| | |_) | |_) | (_| \__ \_  /\__/ / | | | |  __/ | (_| |_  | | | |_| |_ 
    \____/ \__,_| .__/| .__/ \__,_|___(_) \____/|_| |_|_|\___|_|\__,_(_) \_| |_/\___/ 
                | |   | |                                                               
                |_|   |_|      Autonomous Supply-Chain Graph Reasoning Agent           
========================================================================================
  Hackathon Track: Track 01 - Agents That Act on Connected Data
  Database: FalkorDB (In-Memory Graph Engine)
========================================================================================
"""
    print(banner)

def run_incident_response(supplier_id: str = "SUP-001"):
    print(f"\n[STEP 1] INGESTING DISRUPTION EVENT: Disrupted Supplier -> '{supplier_id}'")
    print("-" * 88)
    time.sleep(0.5)

    print("\n[STEP 2] FALKORDB MULTI-HOP GRAPH TRAVERSAL")
    print("  Querying: (:Supplier)-[:SUPPLIES]->(:Component)-[:USED_IN]->(:Product)<-[:ORDERS]-(:CustomerOrder)")
    impact = ImpactAnalyzer.analyze_supplier_disruption(supplier_id)
    metrics = impact["metrics"]

    print(f"\n  >> GRAPH DISRUPTION SCOPE:")
    print(f"     * Severity Tier          : {impact['severity_tier']} (Score: {impact['severity_score']}/1.0)")
    print(f"     * Affected Components    : {metrics['affected_components_count']}")
    print(f"     * Affected Vehicle Lines : {metrics['affected_products_count']}")
    print(f"     * Affected Customer Orders: {metrics['affected_orders_count']} ({metrics['critical_orders_count']} CRITICAL, {metrics['high_priority_orders_count']} HIGH)")
    print(f"     * Total Revenue at Risk  : ${impact['total_revenue_at_risk']:,.2f}")

    print("\n  >> TRACEABLE GRAPH EVIDENCE PATHS:")
    for i, path in enumerate(impact["evidence_paths"][:4], 1):
        print(f"     ({i}) {path['path_string']}")
    if len(impact["evidence_paths"]) > 4:
        print(f"     ... and {len(impact['evidence_paths']) - 4} more customer order paths confirmed in FalkorDB.")

    print("\n" + "=" * 88)
    print("[STEP 3] ALTERNATIVE SUPPLIER DISCOVERY & DETERMINISTIC SCORING")
    print("  Evaluating candidates for disrupted component 'CMP-101' (Automotive Microcontroller MCU-v2)...")

    alternatives = SupplierEvaluator.evaluate_alternatives(supplier_id, "CMP-101")

    print("\n  >> CANDIDATE EVALUATION MATRIX:")
    header = f"  {'Supplier Name':<28} | {'Decision':<14} | {'Score':<6} | {'Compat':<6} | {'Capacity':<10} | {'Lead Time':<10} | {'Risk':<5}"
    print(header)
    print("  " + "-" * 86)
    for alt in alternatives:
        m = alt["metrics"]
        print(
            f"  {alt['supplier_name']:<28} | "
            f"{alt['decision']:<14} | "
            f"{alt['total_score']:<6.1f} | "
            f"{m['compatibility_score']:<6.2f} | "
            f"{m['capacity_units']:<10,d} | "
            f"{m['lead_time_days']:<2} days    | "
            f"{m['risk_score']:<5.2f}"
        )
        if alt["rejection_reasons"]:
            for r in alt["rejection_reasons"]:
                print(f"    └── [DISQUALIFIED]: {r}")

    top_choice = alternatives[0] if alternatives and alternatives[0]["is_feasible"] else None

    if top_choice:
        print("\n" + "=" * 88)
        print("[STEP 4] AGENT ACTION EXECUTION: PERSISTING DECISION INTO FALKORDB")
        print(f"  Action: Rerouting supply of CMP-101 to {top_choice['supplier_name']} ({top_choice['supplier_id']})")
        print("  Writing (:RecoveryAction) node and relationships into graph memory...")

        act = record_recovery_action(
            disrupted_supplier_id=supplier_id,
            selected_alternative_id=top_choice["supplier_id"],
            component_id="CMP-101",
            justification=f"Selected {top_choice['supplier_name']} based on top deterministic score ({top_choice['total_score']}/100) and drop-in pin compatibility.",
            score=top_choice["total_score"]
        )

        print(f"  [+] Action Recorded Successfully in FalkorDB!")
        print(f"      - Action ID : {act['action_id']}")
        print(f"      - Status    : {act['status']}")
        print(f"      - Timestamp : {act['timestamp']}")
        print(f"      - Edge      : (:RecoveryAction)-[:CONTRACTS_TO]->(:Supplier {{id: '{top_choice['supplier_id']}'}})")

    print("\n" + "=" * 88)
    print("[STEP 5] EXPLAINABLE EXECUTIVE SUMMARY")
    plan = RecoveryPlanner.plan_recovery(supplier_id)
    print(f"\n{plan['disruption_summary']}")
    print(f"\nEstimated Recovery Lead Time: {plan['estimated_recovery_lead_time_days']} days.")
    print("=" * 88 + "\n")

def view_graph_memory():
    print("\n[AGENT GRAPH MEMORY - PAST DECISIONS ACROSS SESSIONS]")
    print("-" * 88)
    history = query_action_history()
    if not history:
        print("  No previous actions recorded yet. Run an incident response first!")
        return

    for h in history:
        print(f"  * Action ID : {h['action_id']} ({h['timestamp']})")
        print(f"    Rerouted  : {h['disrupted_supplier']} ➔ {h['alternative_contracted']}")
        print(f"    Score     : {h['decision_score']}/100 | Status: {h['status']}")
        print(f"    Evidence  : {h['justification']}")
        print("  " + "-" * 60)

def main():
    print_banner()

    # Check connection
    try:
        client = get_falkordb_client()
        stats = query_supply_chain_overview()
        print(f"[+] Connected to FalkorDB on {client.connection.connection_pool.connection_kwargs.get('host')}:{client.connection.connection_pool.connection_kwargs.get('port')}")
        print(f"[+] Supply Chain Knowledge Base: {stats['suppliers']} Suppliers, {stats['components']} Components, {stats['products']} Products, {stats['customer_orders']} Orders")
    except Exception as e:
        print(f"[!] FalkorDB is offline: {e}")
        sys.exit(1)

    print("\nSELECT AN INCIDENT WORKFLOW TO EXECUTE:")
    print("  1. Ingest Disruption: Super Typhoon hits Apex Semiconductors (SUP-001)")
    print("  2. Ingest Disruption: Geopolitical route delay at Titan Power (SUP-006)")
    print("  3. View Agent Graph Memory & Past Decisions across sessions")
    print("  4. Run Full End-to-End Autonomous Incident Response")
    print("  5. Exit")

    choice = input("\nEnter choice [1-5] (Default: 4): ").strip() or "4"

    if choice == "1" or choice == "4":
        run_incident_response("SUP-001")
    elif choice == "2":
        run_incident_response("SUP-006")
    elif choice == "3":
        view_graph_memory()
    else:
        print("Exiting.")

if __name__ == "__main__":
    main()
