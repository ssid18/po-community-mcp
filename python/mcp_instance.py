from mcp.server.fastmcp import FastMCP
from tools.patient_age_tool import get_patient_age
from tools.patient_allergies_tool import get_patient_allergies
from tools.patient_id_tool import find_patient_id
from tools.validate_clinical_action_tool import validate_clinical_action
from tools.build_patient_context_tool import build_patient_context
from tools.simulate_clinical_action_tool import simulate_clinical_action

mcp = FastMCP("Python Template", stateless_http=True, host="0.0.0.0")

_original_get_capabilities = mcp._mcp_server.get_capabilities

def _patched_get_capabilities(notification_options, experimental_capabilities):
    caps = _original_get_capabilities(notification_options, experimental_capabilities)
    caps.model_extra["extensions"] = {
        "ai.promptopinion/fhir-context": {
            "scopes": [
                {"name": "patient/Patient.rs", "required": True},
                {"name": "patient/Observation.rs"},
                {"name": "patient/MedicationStatement.rs"},
                {"name": "patient/Condition.rs"},
            ]
        }
    }
    return caps

mcp._mcp_server.get_capabilities = _patched_get_capabilities



mcp.tool(name="GetPatientAge", description="Gets the age of a patient.")(get_patient_age)
mcp.tool(name="GetPatientAllergies", description="Gets the known allergies of a patient.")(get_patient_allergies)
mcp.tool(name="FindPatientId", description="Finds a patient id given a first name and last name")(find_patient_id)
mcp.tool(name="validate_clinical_action", description="Primary CROSS runtime enforcement tool. Deterministically validates proposed clinical actions against structured FHIR runtime context before execution. Evaluates prescriptions, diagnostic orders, and discharge actions using reusable safety rules grounded in patient allergies, medications, procedures, observations, and conditions. Returns structured GO/NO_GO safety decisions with evidence references, decision traces, impact summaries, and follow-up awareness.")(validate_clinical_action)
mcp.tool(name="build_patient_context", description="Transforms fragmented FHIR patient records into normalized runtime clinical context for downstream safety evaluation. Loads and structures patient allergies, active medications, recent observations, recent procedures, and conditions into a deterministic runtime context abstraction layer used by CROSS safety workflows. Designed for reusable context propagation across healthcare AI systems and MCP agents.")(build_patient_context)
mcp.tool(name="simulate_clinical_action", description="Performs stateless pre-execution simulation of proposed clinical actions using CROSS deterministic safety rules. Allows healthcare AI agents to evaluate potential runtime safety outcomes before execution without persisting state or modifying patient data. Reuses the same FHIR-backed validation substrate as runtime enforcement to provide predicted decisions, triggered safety rules, risk scoring, and operational impact summaries.")(simulate_clinical_action)
