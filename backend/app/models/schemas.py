"""
SupplyShield AI - Pydantic Request & Response Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    database: str
    graph_name: str
    version: str

class DisruptionAnalysisRequest(BaseModel):
    supplier_id: str = Field(..., description="ID of the disrupted supplier (e.g., 'SUP-001')")
    graph_name: Optional[str] = None

class RecoveryRequest(BaseModel):
    supplier_id: str = Field(..., description="ID of the supplier to recover from (e.g., 'SUP-001')")
    graph_name: Optional[str] = None

class SeedRequest(BaseModel):
    clear_existing: bool = Field(default=False, description="Whether to clear graph before seeding")
    graph_name: Optional[str] = None

class ExecuteActionRequest(BaseModel):
    disrupted_supplier_id: str = Field(..., description="ID of disrupted supplier")
    selected_alternative_id: str = Field(..., description="ID of alternative supplier to contract")
    component_id: str = Field(..., description="ID of component being rerouted")
    justification: str = Field(..., description="Explainable reason for selection")
    score: float = Field(default=90.0, description="Deterministic decision score")
    graph_name: Optional[str] = None

