# ── Default safe GO response ────────────────────────────────────

DEFAULT_GO = {
    "decision": "GO",
    "severity": "low",
    "primary_reason": "No clinical safety issues detected",
    "risk_score": 0.1,
    "evidence": {"fhir_refs": []},
    "recommended_action": "Proceed",
    "impact": "No clinical safety risks identified",
    "rule_triggered": "none",
    "decision_trace": [
        "Loaded structured patient context",
        "Evaluated deterministic safety rules",
        "No rule violations detected",
    ],
}


def evaluate_action(action: dict, context: dict) -> dict:
    """
    Apply deterministic safety rules. First match wins (early return).
    Returns structured dict WITHOUT confidence.
    """
    action_type = action.get("type", "")

    # ── PRESCRIBE rules ─────────────────────────────────────────
    if action_type == "prescribe":
        _payload = action.get("payload", {})
        drug = (_payload.get("drug") or _payload.get("medication") or "").lower()

        if not drug:
            return {**DEFAULT_GO}

        # Rule 1: Allergy check
        for allergy in context.get("allergies", []):
            if drug == allergy["value"]:
                ref = f"AllergyIntolerance/{allergy['id']}"
                return {
                    "decision": "NO_GO",
                    "severity": "high",
                    "primary_reason": f"Patient has documented allergy to {allergy['display']}",
                    "risk_score": 0.95,
                    "evidence": {"fhir_refs": [ref]},
                    "recommended_action": "Use alternative medication",
                    "impact": "Prevents potential allergic reaction",
                    "rule_triggered": "allergy",
                    "decision_trace": [
                        f"Loaded {ref}",
                        "Matched prescribed drug with allergy",
                        "Triggered allergy safety rule",
                    ],
                }

        # Rule 2: Drug conflict check
        for med in context.get("active_medications", []):
            if drug == med["value"]:
                ref = f"MedicationRequest/{med['id']}"
                return {
                    "decision": "NO_GO",
                    "severity": "medium",
                    "primary_reason": f"Patient is already on {med['display']}",
                    "risk_score": 0.8,
                    "evidence": {"fhir_refs": [ref]},
                    "recommended_action": "Review current medications before prescribing",
                    "impact": "Prevents harmful drug interaction",
                    "rule_triggered": "drug_conflict",
                    "decision_trace": [
                        f"Loaded {ref}",
                        "Matched prescribed drug with active medication",
                        "Triggered drug conflict safety rule",
                    ],
                }

    # ── ORDER_TEST rule ─────────────────────────────────────────
    elif action_type == "order_test":
        test = str(action.get("payload", {}).get("test", "")).lower()

        if not test:
            return {**DEFAULT_GO}

        # Rule 3: Duplicate procedure check
        for proc in context.get("recent_procedures", []):
            if test == proc["value"]:
                ref = f"Procedure/{proc['id']}"
                return {
                    "decision": "NO_GO",
                    "severity": "medium",
                    "primary_reason": f"{proc['display']} was recently performed",
                    "risk_score": 0.7,
                    "evidence": {"fhir_refs": [ref]},
                    "recommended_action": "Review recent procedures before ordering",
                    "impact": "Prevents unnecessary repeat procedure",
                    "rule_triggered": "duplicate_procedure",
                    "decision_trace": [
                        f"Loaded {ref}",
                        "Matched ordered test with recent procedure",
                        "Triggered duplicate procedure safety rule",
                    ],
                }

    # ── DISCHARGE rule ──────────────────────────────────────────
    elif action_type == "discharge":
        observations = context.get("recent_observations", [])

        if not observations:
            return DEFAULT_GO

        # Rule 4: Unsafe discharge — check blood pressure
        for obs in observations:
            bp = obs["value"]
            try:
                systolic, diastolic = map(int, bp.split("/"))
                if systolic > 140 or diastolic > 90:
                    ref = f"Observation/{obs['id']}"
                    return {
                        "decision": "NO_GO",
                        "severity": "high",
                        "primary_reason": f"Patient has elevated blood pressure ({obs['display']})",
                        "risk_score": 0.9,
                        "evidence": {"fhir_refs": [ref]},
                        "recommended_action": "Stabilize vitals before discharge",
                        "impact": "Prevents unsafe patient discharge",
                        "rule_triggered": "unsafe_discharge",
                        "decision_trace": [
                            f"Loaded {ref}",
                            f"Parsed BP as {systolic}/{diastolic}",
                            "Triggered unsafe discharge safety rule",
                        ],
                    }
            except (ValueError, AttributeError):
                continue

    # ── No rule triggered ───────────────────────────────────────
    return {**DEFAULT_GO}
