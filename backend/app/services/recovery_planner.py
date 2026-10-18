"""
SupplyShield AI - Recovery Planner Service
Synthesizes disruption impact and alternative supplier evaluations into an actionable, evidence-backed recovery plan.
"""

from typing import Dict, Any
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.supplier_evaluator import SupplierEvaluator

class RecoveryPlanner:
    """Generates holistic recovery recommendations from graph data."""

    @staticmethod
    def plan_recovery(supplier_id: str, graph_name: str | None = None) -> Dict[str, Any]:
        """Synthesizes disruption impact with ranked alternative recovery options."""
        # 1. Analyze impact
        impact = ImpactAnalyzer.analyze_supplier_disruption(supplier_id, graph_name)

        # 2. For each affected component, evaluate alternatives
        recovery_options = []
        for comp in impact["affected_components"]:
            comp_id = comp["id"]
            evaluated = SupplierEvaluator.evaluate_alternatives(supplier_id, comp_id, graph_name)
            recovery_options.append({
                "component_id": comp_id,
                "component_name": comp["name"],
                "component_criticality": comp["criticality"],
                "ranked_alternatives": evaluated
            })

        # 3. Determine best recovery path
        primary_alternatives = []
        for opt in recovery_options:
            feasible = [a for a in opt["ranked_alternatives"] if a["is_feasible"]]
            if feasible:
                primary_alternatives.append(feasible[0])

        estimated_lead_days = max([a["metrics"]["lead_time_days"] for a in primary_alternatives], default=0)

        # 4. Generate structured advisory summary
        summary_text = (
            f"Disruption at {supplier_id} impacts {impact['metrics']['affected_orders_count']} customer orders "
            f"across {impact['metrics']['affected_products_count']} product lines, representing "
            f"${impact['total_revenue_at_risk']:,.2f} in at-risk revenue. "
        )
        if primary_alternatives:
            top_sup = primary_alternatives[0]
            summary_text += (
                f"Recommended recovery: Switch component sourcing to {top_sup['supplier_name']} ({top_sup['supplier_id']}), "
                f"scoring {top_sup['total_score']}/100 with estimated turnaround lead time of {estimated_lead_days} days."
            )
        else:
            summary_text += "Caution: No verified feasible alternatives meeting capacity and compatibility standards found."

        return {
            "disrupted_supplier_id": supplier_id,
            "disruption_summary": summary_text,
            "impact_assessment": impact,
            "component_recovery_options": recovery_options,
            "recommended_primary_alternatives": primary_alternatives,
            "estimated_recovery_lead_time_days": estimated_lead_days,
            "traceable_graph_paths": impact["evidence_paths"],
            "limitations_and_caveats": [
                "Recommendations are advisory; manual procurement approval required.",
                "Lead times are estimated from recorded contract baselines and transit conditions.",
                "Assumes alternative supplier capacity is not simultaneously booked by third-party buyers."
            ]
        }
