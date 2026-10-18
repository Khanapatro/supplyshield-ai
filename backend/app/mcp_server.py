"""
SupplyShield AI - Model Context Protocol (MCP) Server
Exposes FalkorDB graph reasoning, disruption analysis, and action execution as MCP Tools.
Conforms to Hackathon Track 01 criteria: 'Tool selection through MCP'.
"""

import json
import sys
from typing import Any, Dict, List
from app.graph.queries import (
    query_supply_chain_overview,
    query_all_suppliers,
    record_recovery_action,
    query_action_history
)
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.supplier_evaluator import SupplierEvaluator
from app.services.recovery_planner import RecoveryPlanner

MCP_TOOLS = [
    {
        "name": "get_supply_chain_overview",
        "description": "Returns counts of all suppliers, components, factories, products, orders, shipments, and risk events in the FalkorDB supply chain graph.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "analyze_disruption",
        "description": "Performs multi-hop graph traversal to find all affected components, vehicle products, factories, and customer orders when a supplier experiences a disruption.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "supplier_id": {
                    "type": "string",
                    "description": "Unique business ID of the disrupted supplier, e.g. 'SUP-001'"
                }
            },
            "required": ["supplier_id"]
        }
    },
    {
        "name": "find_compatible_alternatives",
        "description": "Discovers alternative suppliers for a component, evaluates compatibility, capacity, lead time, and risk, and returns deterministically ranked options.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "disrupted_supplier_id": {
                    "type": "string",
                    "description": "ID of supplier to exclude"
                },
                "component_id": {
                    "type": "string",
                    "description": "ID of required component, e.g. 'CMP-101'"
                }
            },
            "required": ["disrupted_supplier_id", "component_id"]
        }
    },
    {
        "name": "recommend_recovery_plan",
        "description": "Synthesizes downstream impact and ranked alternatives into an explainable recovery recommendation with traceable graph paths.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "supplier_id": {
                    "type": "string",
                    "description": "ID of the disrupted supplier"
                }
            },
            "required": ["supplier_id"]
        }
    },
    {
        "name": "execute_recovery_action",
        "description": "Acts on graph analysis by recording the contracted recovery action into FalkorDB graph memory across sessions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "disrupted_supplier_id": {"type": "string"},
                "selected_alternative_id": {"type": "string"},
                "component_id": {"type": "string"},
                "justification": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["disrupted_supplier_id", "selected_alternative_id", "component_id", "justification"]
        }
    },
    {
        "name": "get_agent_decision_history",
        "description": "Retrieves persistent agent decisions and recovery actions recorded across sessions in FalkorDB graph memory.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Executes the requested graph tool."""
    if tool_name == "get_supply_chain_overview":
        return query_supply_chain_overview()

    elif tool_name == "analyze_disruption":
        return ImpactAnalyzer.analyze_supplier_disruption(arguments["supplier_id"])

    elif tool_name == "find_compatible_alternatives":
        return SupplierEvaluator.evaluate_alternatives(
            arguments["disrupted_supplier_id"],
            arguments["component_id"]
        )

    elif tool_name == "recommend_recovery_plan":
        return RecoveryPlanner.plan_recovery(arguments["supplier_id"])

    elif tool_name == "execute_recovery_action":
        return record_recovery_action(
            disrupted_supplier_id=arguments["disrupted_supplier_id"],
            selected_alternative_id=arguments["selected_alternative_id"],
            component_id=arguments["component_id"],
            justification=arguments["justification"],
            score=arguments.get("score", 90.0)
        )

    elif tool_name == "get_agent_decision_history":
        return query_action_history()

    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def main():
    """Stdio-based JSON-RPC MCP server loop."""
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")

            if method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": MCP_TOOLS}
                }
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                result = handle_tool_call(name, args)
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2)}
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"}
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32000, "message": str(e)}
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
