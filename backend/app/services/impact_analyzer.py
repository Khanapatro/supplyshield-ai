"""
SupplyShield AI - Disruption Impact Analysis Service
Calculates multi-hop downstream impact across components, products, factories, and customer orders.
"""

from typing import Dict, Any, List
from app.graph.queries import query_downstream_supplier_impact, query_all_risk_events

class ImpactAnalyzer:
    """Analyzes supply chain disruption impacts using graph traversal results."""

    @staticmethod
    def analyze_supplier_disruption(supplier_id: str, graph_name: str | None = None) -> Dict[str, Any]:
        """
        Calculates scope, severity, affected entities, and graph evidence paths
        resulting from a supplier disruption.
        """
        raw_impact = query_downstream_supplier_impact(supplier_id, graph_name)

        affected_components = raw_impact["affected_components"]
        affected_products = raw_impact["affected_products"]
        affected_orders = raw_impact["affected_orders"]
        total_rev = raw_impact["total_revenue_at_risk"]
        evidence_paths = raw_impact["evidence_paths"]

        # Calculate severity metrics
        critical_orders = [o for o in affected_orders if o["priority"] == "CRITICAL"]
        high_orders = [o for o in affected_orders if o["priority"] == "HIGH"]

        # Component stock health
        component_criticality_flag = any(c.get("criticality") == "CRITICAL" for c in affected_components)

        # Impact Severity Score Formula:
        # Base on revenue at risk + order priorities + criticality
        # 0.0 to 1.0 scale
        priority_weight = (len(critical_orders) * 0.25) + (len(high_orders) * 0.15)
        criticality_weight = 0.3 if component_criticality_flag else 0.1
        revenue_weight = min(total_rev / 50000000.0, 0.4) # Normalized to $50M

        severity_score = min(round(priority_weight + criticality_weight + revenue_weight, 2), 1.0)

        if severity_score >= 0.75:
            severity_tier = "CRITICAL"
        elif severity_score >= 0.45:
            severity_tier = "HIGH"
        else:
            severity_tier = "MODERATE"

        return {
            "disrupted_entity_id": supplier_id,
            "disrupted_entity_type": "Supplier",
            "severity_tier": severity_tier,
            "severity_score": severity_score,
            "total_revenue_at_risk": total_rev,
            "metrics": {
                "affected_components_count": len(affected_components),
                "affected_products_count": len(affected_products),
                "affected_orders_count": len(affected_orders),
                "critical_orders_count": len(critical_orders),
                "high_priority_orders_count": len(high_orders)
            },
            "affected_components": affected_components,
            "affected_products": affected_products,
            "affected_orders": affected_orders,
            "evidence_paths": evidence_paths
        }

    @staticmethod
    def analyze_event_disruption(event_id: str, graph_name: str | None = None) -> List[Dict[str, Any]]:
        """Analyzes impact for all suppliers affected by a specific risk event."""
        events = query_all_risk_events(graph_name)
        target_event = next((e for e in events if e["id"] == event_id), None)
        if not target_event:
            raise ValueError(f"Risk event '{event_id}' not found.")

        results = []
        for sup_id in target_event.get("affected_suppliers", []):
            sup_impact = ImpactAnalyzer.analyze_supplier_disruption(sup_id, graph_name)
            sup_impact["originating_risk_event"] = target_event
            results.append(sup_impact)

        return results
