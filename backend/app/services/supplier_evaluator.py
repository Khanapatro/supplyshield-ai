"""
SupplyShield AI - Alternative Supplier Evaluation & Deterministic Scoring
Applies transparent mathematical scoring and hard constraint disqualifications.
"""

from typing import List, Dict, Any
from app.graph.queries import query_alternative_suppliers

# Documented Scoring Weights (Must sum to 1.0)
WEIGHT_COMPATIBILITY = 0.40
WEIGHT_CAPACITY = 0.30
WEIGHT_LEAD_TIME = 0.20
WEIGHT_RISK = 0.10

# Hard Constraint Thresholds
MIN_COMPATIBILITY_THRESHOLD = 0.80
MIN_CAPACITY_THRESHOLD = 2000 # Minimum operational batch threshold

class SupplierEvaluator:
    """Evaluates and ranks alternative suppliers deterministically."""

    @staticmethod
    def evaluate_alternatives(
        disrupted_supplier_id: str,
        component_id: str,
        graph_name: str | None = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves alternative candidates from FalkorDB, checks hard constraints,
        and computes deterministic scores for feasible suppliers.
        """
        candidates = query_alternative_suppliers(disrupted_supplier_id, component_id, graph_name)
        evaluated = []

        for cand in candidates:
            sup_id = cand["supplier_id"]
            name = cand["supplier_name"]
            capacity = cand["capacity"]
            lead_time = cand["lead_time_days"]
            risk = cand["risk_score"]
            compatibility = cand["compatibility_score"]
            is_verified = cand["is_verified"]
            notes = cand["verification_notes"]

            # 1. Check Hard Constraints
            disqualified = False
            rejection_reasons = []

            # Hard Constraint A: Compatibility
            if compatibility < MIN_COMPATIBILITY_THRESHOLD:
                disqualified = True
                rejection_reasons.append(
                    f"Incompatible component specification (score: {compatibility:.2f} < threshold: {MIN_COMPATIBILITY_THRESHOLD:.2f})."
                )

            # Hard Constraint B: Minimum Batch Capacity
            if capacity < MIN_CAPACITY_THRESHOLD:
                disqualified = True
                rejection_reasons.append(
                    f"Insufficient manufacturing capacity ({capacity:,} units < minimum required: {MIN_CAPACITY_THRESHOLD:,})."
                )

            # 2. Deterministic Scoring (0 to 100 scale)
            if not disqualified:
                # Sub-score 1: Compatibility (0 to 1) -> 40 pts
                compat_pts = compatibility * WEIGHT_COMPATIBILITY * 100

                # Sub-score 2: Capacity normalized to 15,000 units -> 30 pts
                norm_capacity = min(capacity / 15000.0, 1.0)
                capacity_pts = norm_capacity * WEIGHT_CAPACITY * 100

                # Sub-score 3: Lead time (lower is better, 5 to 40 days scale) -> 20 pts
                lead_factor = max(0.0, min((40 - lead_time) / (40 - 5), 1.0))
                lead_pts = lead_factor * WEIGHT_LEAD_TIME * 100

                # Sub-score 4: Risk score (lower is better: 1 - risk) -> 10 pts
                risk_pts = (1.0 - risk) * WEIGHT_RISK * 100

                total_score = round(compat_pts + capacity_pts + lead_pts + risk_pts, 1)
                decision = "RECOMMENDED" if total_score >= 80 else "FEASIBLE_BACKUP"
            else:
                total_score = 0.0
                decision = "REJECTED"

            evaluated.append({
                "supplier_id": sup_id,
                "supplier_name": name,
                "status": cand["status"],
                "decision": decision,
                "total_score": total_score,
                "is_feasible": not disqualified,
                "metrics": {
                    "compatibility_score": round(compatibility, 2),
                    "capacity_units": capacity,
                    "lead_time_days": lead_time,
                    "risk_score": round(risk, 2),
                    "is_verified_alternative": is_verified
                },
                "score_breakdown": {
                    "compatibility_points": round(compat_pts, 1) if not disqualified else 0.0,
                    "capacity_points": round(capacity_pts, 1) if not disqualified else 0.0,
                    "lead_time_points": round(lead_pts, 1) if not disqualified else 0.0,
                    "risk_points": round(risk_pts, 1) if not disqualified else 0.0,
                    "weights_applied": {
                        "compatibility": f"{int(WEIGHT_COMPATIBILITY*100)}%",
                        "capacity": f"{int(WEIGHT_CAPACITY*100)}%",
                        "lead_time": f"{int(WEIGHT_LEAD_TIME*100)}%",
                        "risk": f"{int(WEIGHT_RISK*100)}%"
                    }
                },
                "rejection_reasons": rejection_reasons,
                "verification_evidence": notes,
                "supplied_component_name": cand["supplied_component_name"] or "Unknown"
            })

        # Sort: Feasible options first by score descending, rejected last
        evaluated.sort(key=lambda x: (x["is_feasible"], x["total_score"]), reverse=True)
        return evaluated
