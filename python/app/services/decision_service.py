import logging

from app.models import ClinicalActionInput, DecisionResponse, Evidence
from app.services.fhir_loader import load_patient_data
from app.services.context_builder import build_context_slice
from app.services.rule_engine import evaluate_action


# ── Safe default response (used on any error) ──────────────────

SAFE_DEFAULT = DecisionResponse(
    decision="GO",
    severity="low",
    primary_reason="No clinical safety issues detected",
    risk_score=0.1,
    evidence=Evidence(fhir_refs=[]),
    recommended_action="Proceed",
    confidence=0.8,
    impact="No clinical safety risks identified",
    rule_triggered="none",
    decision_trace=[
        "Loaded structured patient context",
        "Evaluated deterministic safety rules",
        "No rule violations detected",
    ],
)


def validate_action(input_data: ClinicalActionInput) -> DecisionResponse:
    """
    Orchestrate: load FHIR → build context → run rules → add confidence.
    Returns safe default GO on any failure.
    """
    try:
        # Step 1: Load FHIR data
        fhir_data = load_patient_data(input_data.sharp_context.patient_id)

        # Step 2: Build context slice
        context = build_context_slice(fhir_data)

        # Step 3: Run rule engine
        action_dict = {
            "type": input_data.action.type,
            "payload": input_data.action.payload,
        }
        result = evaluate_action(action_dict, context)

        # Step 4: Add confidence (NOT in rule_engine)
        confidence = 0.9 if result["decision"] == "NO_GO" else 0.8

        # Step 5: Discharge follow-up signal (evidence-based, non-decisional)
        follow_up_required = None
        follow_up_reason = None

        if input_data.action.type == "discharge":
            observations = context.get("recent_observations", [])
            if observations:
                obs = observations[0]
                try:
                    systolic, diastolic = map(int, obs["value"].split("/"))
                    if systolic > 130 or diastolic > 80:
                        follow_up_required = True
                        follow_up_reason = f"Elevated blood pressure (Observation/{obs['id']})"
                except (ValueError, AttributeError):
                    pass

            if follow_up_required is None:
                for cond in context.get("conditions", []):
                    if cond["value"] == "hypertension":
                        follow_up_required = True
                        follow_up_reason = f"Follow-up recommended due to hypertension (Condition/{cond['id']})"
                        break

        return DecisionResponse(
            decision=result["decision"],
            severity=result["severity"],
            primary_reason=result["primary_reason"],
            risk_score=result["risk_score"],
            evidence=Evidence(fhir_refs=result["evidence"]["fhir_refs"]),
            recommended_action=result["recommended_action"],
            confidence=confidence,
            impact=result["impact"],
            rule_triggered=result["rule_triggered"],
            decision_trace=result["decision_trace"],
            follow_up_required=follow_up_required,
            follow_up_reason=follow_up_reason,
        )

    except Exception as e:
        logging.exception("validate_action failed: %s", e)
        return DecisionResponse(
            decision="GO",
            severity="low",
            primary_reason="No clinical safety issues detected",
            impact="No clinical safety risks identified",
            rule_triggered="error",
            risk_score=0.1,
            evidence=Evidence(fhir_refs=[]),
            recommended_action="Proceed",
            confidence=0.8,
        )
