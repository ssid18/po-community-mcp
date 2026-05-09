from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from app.models import ClinicalActionInput
from app.services.decision_service import validate_action


async def validate_clinical_action(
    action: Annotated[
        dict,
        Field(
            description=(
                "The clinical action to validate. "
                "Keys: type (one of: prescribe, order_test, discharge) and payload (dict)."
            )
        ),
    ],
    sharp_context: Annotated[
        dict,
        Field(
            description=(
                "The SHARP patient context. "
                "Keys: patient_id (str) and encounter_id (str)."
            )
        ),
    ],
    ctx: Context = None,
) -> dict:
    """Primary CROSS runtime enforcement tool. Deterministically validates proposed clinical actions against structured FHIR runtime context before execution. Evaluates prescriptions, diagnostic orders, and discharge actions using reusable safety rules grounded in patient allergies, medications, procedures, observations, and conditions. Returns structured GO/NO_GO safety decisions with evidence references, decision traces, impact summaries, and follow-up awareness."""
    input_data = ClinicalActionInput(action=action, sharp_context=sharp_context)
    result = validate_action(input_data)
    return result.model_dump()
