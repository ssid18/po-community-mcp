from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from app.models import ClinicalActionInput
from app.services.decision_service import validate_action


async def simulate_clinical_action(
    action: Annotated[
        dict,
        Field(
            description=(
                "The clinical action to simulate. "
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
    """Performs stateless pre-execution simulation of proposed clinical actions using CROSS deterministic safety rules. Allows healthcare AI agents to evaluate potential runtime safety outcomes before execution without persisting state or modifying patient data. Reuses the same FHIR-backed validation substrate as runtime enforcement to provide predicted decisions, triggered safety rules, risk scoring, and operational impact summaries."""
    input_data = ClinicalActionInput(action=action, sharp_context=sharp_context)
    result = validate_action(input_data)

    recommended_next_step = (
        "Modify clinical action before execution"
        if result.decision == "NO_GO"
        else "Safe to proceed"
    )

    return {
        "simulation": True,
        "simulation_mode": "pre_execution",
        "predicted_decision": result.decision,
        "triggered_rule": result.rule_triggered,
        "risk_score": result.risk_score,
        "impact": result.impact,
        "recommended_next_step": recommended_next_step,
    }
