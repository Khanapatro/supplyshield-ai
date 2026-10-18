"""
Tests for SupplyShield AI FastAPI Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Verifies GET /health returns 200 and healthy FalkorDB status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["graph_name"] == "supplyshield"

def test_overview_endpoint():
    """Verifies GET /api/overview returns non-zero counts for entities."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["suppliers"] >= 5
    assert data["components"] >= 6
    assert data["products"] >= 5
    assert data["customer_orders"] >= 8

def test_suppliers_endpoint():
    """Verifies GET /api/suppliers returns list of suppliers with details."""
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    suppliers = response.json()["data"]
    assert len(suppliers) >= 5
    sup_ids = [s["id"] for s in suppliers]
    assert "SUP-001" in sup_ids
    assert "SUP-002" in sup_ids

def test_disruption_analysis_endpoint():
    """Verifies POST /api/disruptions/analyze calculates impact for SUP-001."""
    payload = {"supplier_id": "SUP-001"}
    response = client.post("/api/disruptions/analyze", json=payload)
    assert response.status_code == 200
    res = response.json()["data"]
    assert res["disrupted_entity_id"] == "SUP-001"
    assert res["metrics"]["affected_orders_count"] == 7
    assert res["metrics"]["affected_products_count"] == 3
    assert len(res["evidence_paths"]) == 7

def test_recovery_recommendation_endpoint():
    """Verifies POST /api/recovery/recommend returns ranked alternatives."""
    payload = {"supplier_id": "SUP-001"}
    response = client.post("/api/recovery/recommend", json=payload)
    assert response.status_code == 200
    res = response.json()["data"]
    assert res["disrupted_supplier_id"] == "SUP-001"
    assert "Nexus" in res["disruption_summary"]
    primary_alts = res["recommended_primary_alternatives"]
    assert len(primary_alts) >= 1
    assert primary_alts[0]["supplier_id"] == "SUP-002"
    assert primary_alts[0]["decision"] == "RECOMMENDED"
    assert primary_alts[0]["total_score"] >= 80.0

def test_execute_recovery_action_and_memory():
    """Verifies that the agent acts on graph data, stores decision in FalkorDB, and remembers across sessions."""
    action_payload = {
        "disrupted_supplier_id": "SUP-001",
        "selected_alternative_id": "SUP-002",
        "component_id": "CMP-101",
        "justification": "Nexus Microelectronics verified drop-in pin compatible with AEC-Q100 rating and 12,000 units capacity.",
        "score": 94.2
    }
    response = client.post("/api/recovery/execute", json=action_payload)
    assert response.status_code == 200
    res = response.json()["data"]
    assert res["status"] == "EXECUTED"
    assert res["selected_alternative"] == "SUP-002"

    # Query history to verify memory persistence in FalkorDB
    hist_response = client.get("/api/agent/history")
    assert hist_response.status_code == 200
    history = hist_response.json()["data"]
    assert len(history) >= 1
    assert any("Nexus" in h["alternative_contracted"] for h in history)

