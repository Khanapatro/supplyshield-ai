"""
SupplyShield AI - FastAPI Main Application
Exposes graph analysis, alternative supplier evaluation, and recovery planning APIs.
"""

import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.graph.connection import get_falkordb_client, get_graph, GraphConnectionError
from app.graph.queries import (
    query_supply_chain_overview,
    query_all_suppliers,
    query_all_risk_events,
    query_visual_graph,
    record_recovery_action,
    query_action_history
)
from app.graph.seed import seed_database
from app.services.impact_analyzer import ImpactAnalyzer
from app.services.supplier_evaluator import SupplierEvaluator
from app.services.recovery_planner import RecoveryPlanner
from app.models.schemas import (
    HealthResponse,
    DisruptionAnalysisRequest,
    RecoveryRequest,
    SeedRequest,
    ExecuteActionRequest
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("supplyshield.api")

app = FastAPI(
    title="SupplyShield AI API",
    description="FalkorDB Graph-Powered Supply Chain Disruption & Recovery Engine",
    version=settings.APP_VERSION
)

# Enable CORS for frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Verifies that the backend API and FalkorDB graph database are both healthy."""
    try:
        client = get_falkordb_client()
        ping_ok = client.connection.ping()
        db_status = "connected" if ping_ok else "unreachable"
    except Exception as e:
        logger.error(f"Health check failed connecting to FalkorDB: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"FalkorDB connection failed: {e}"
        )

    return {
        "status": "healthy",
        "database": db_status,
        "graph_name": settings.FALKORDB_GRAPH_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/api/overview")
def get_supply_chain_overview():
    """Returns high-level statistics of seeded supply chain entities."""
    try:
        stats = query_supply_chain_overview()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/suppliers")
def get_suppliers():
    """Lists all suppliers in the graph with their operational and risk status."""
    try:
        suppliers = query_all_suppliers()
        return {"status": "success", "data": suppliers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-events")
def get_risk_events():
    """Lists all active and monitored risk events in the network."""
    try:
        events = query_all_risk_events()
        return {"status": "success", "data": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/graph/visual")
def get_visual_graph():
    """Returns all nodes and edges formatted for visual graph explorers."""
    try:
        graph_data = query_visual_graph()
        return {"status": "success", "data": graph_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/disruptions/analyze")
def analyze_disruption(payload: DisruptionAnalysisRequest):
    """
    Analyzes downstream impact of a disrupted supplier across components, products,
    factories, and customer orders using multi-hop graph traversal.
    """
    try:
        impact = ImpactAnalyzer.analyze_supplier_disruption(payload.supplier_id, payload.graph_name)
        return {"status": "success", "data": impact}
    except Exception as e:
        logger.error(f"Error analyzing disruption for {payload.supplier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/components/{component_id}/alternatives")
def get_component_alternatives(component_id: str, excluded_supplier_id: str = "SUP-001"):
    """
    Discovers and deterministically scores alternative suppliers for a specific component.
    """
    try:
        alternatives = SupplierEvaluator.evaluate_alternatives(excluded_supplier_id, component_id)
        return {"status": "success", "data": alternatives}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recovery/recommend")
def recommend_recovery_plan(payload: RecoveryRequest):
    """
    Generates a full, explainable recovery plan combining impact scope and ranked
    alternative suppliers with transparent scoring and graph evidence paths.
    """
    try:
        plan = RecoveryPlanner.plan_recovery(payload.supplier_id, payload.graph_name)
        return {"status": "success", "data": plan}
    except Exception as e:
        logger.error(f"Error generating recovery plan for {payload.supplier_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/demo/seed")
def reseed_demo_data(payload: SeedRequest):
    """
    Seeds the FalkorDB graph idempotently. Can be triggered from UI to reset demo state.
    """
    try:
        summary = seed_database(clear_existing=payload.clear_existing, graph_name=payload.graph_name)
        return {"status": "success", "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recovery/execute")
def execute_recovery_action(payload: ExecuteActionRequest):
    """
    Executes and records the recovery action into FalkorDB graph memory.
    Implements 'Actions based on what the graph shows' and 'Remember across sessions'.
    """
    try:
        res = record_recovery_action(
            disrupted_supplier_id=payload.disrupted_supplier_id,
            selected_alternative_id=payload.selected_alternative_id,
            component_id=payload.component_id,
            justification=payload.justification,
            score=payload.score,
            graph_name=payload.graph_name
        )
        return {"status": "success", "data": res}
    except Exception as e:
        logger.error(f"Error executing recovery action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/history")
def get_agent_history(graph_name: str | None = None):
    """
    Retrieves all past agent decisions and actions stored across sessions in FalkorDB graph memory.
    """
    try:
        history = query_action_history(graph_name)
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

