from typing import Annotated

from mcp.server.fastmcp import Context
from pydantic import Field

from app.services.fhir_loader import load_patient_data
from app.services.context_builder import build_context_slice


async def build_patient_context(
    patient_id: Annotated[
        str,
        Field(description="The patient ID whose FHIR data should be loaded and normalized into a runtime context slice."),
    ],
    ctx: Context = None,
) -> dict:
    """Transforms fragmented FHIR patient records into normalized runtime clinical context for downstream safety evaluation. Loads and structures patient allergies, active medications, recent observations, recent procedures, and conditions into a deterministic runtime context abstraction layer used by CROSS safety workflows. Designed for reusable context propagation across healthcare AI systems and MCP agents."""
    fhir_data = load_patient_data(patient_id)
    context = build_context_slice(fhir_data)
    return {"context_type": "runtime_clinical_context", **context}
