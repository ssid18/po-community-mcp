from pydantic import BaseModel, model_serializer
from typing import Literal, Optional


# ── Request Models ──────────────────────────────────────────────

class ActionDetail(BaseModel):
    type: Literal["prescribe", "order_test", "discharge"]
    payload: dict = {}


class SharpContext(BaseModel):
    patient_id: str
    encounter_id: str


class ClinicalActionInput(BaseModel):
    action: ActionDetail
    sharp_context: SharpContext


# ── Response Models ─────────────────────────────────────────────

class Evidence(BaseModel):
    fhir_refs: list[str] = []


class DecisionResponse(BaseModel):
    decision: Literal["GO", "NO_GO"]
    severity: Literal["low", "medium", "high"]
    primary_reason: str
    risk_score: float
    evidence: Evidence
    recommended_action: str
    confidence: float
    impact: str
    rule_triggered: str
    decision_trace: list[str] = []
    follow_up_required: Optional[bool] = None
    follow_up_reason: Optional[str] = None

    @model_serializer(mode="wrap")
    def _exclude_none(self, handler) -> dict:
        return {k: v for k, v in handler(self).items() if v is not None}
