from fastapi import APIRouter
from app.models import ClinicalActionInput, DecisionResponse
from app.services.decision_service import validate_action

router = APIRouter()


@router.post("/tools/validate_clinical_action", response_model=DecisionResponse)
def validate_clinical_action(input_data: ClinicalActionInput):
    """MCP tool: Validate a clinical action against FHIR patient context."""
    return validate_action(input_data)
