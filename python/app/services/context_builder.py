def build_context_slice(fhir_data: dict) -> dict:
    """
    Build a structured context slice from raw FHIR data.
    Each item is a dict with 'id', 'value' (lowercased), and 'display' (original casing).
    """

    # ── Patient Identity ─────────────────────────────────────────
    patient_id = ""
    patient_name = ""
    gender = ""
    birth_date = ""
    patient = fhir_data.get("Patient")
    if patient:
        patient_id = patient.get("id", "")
        gender = patient.get("gender", "")
        birth_date = patient.get("birthDate", "")
        names = patient.get("name", [])
        if names:
            n = names[0]
            given = " ".join(n.get("given", []))
            family = n.get("family", "")
            patient_name = f"{given} {family}".strip()

    # ── Allergies ───────────────────────────────────────────────
    allergies = []
    for entry in fhir_data.get("AllergyIntolerance", []):
        substance = entry.get("substance", "")
        if substance:
            allergies.append({
                "id": entry.get("id", ""),
                "value": substance.lower(),
                "display": substance,
            })

    # ── Active Medications ──────────────────────────────────────
    active_medications = []
    for entry in fhir_data.get("MedicationRequest", []):
        if entry.get("status", "").lower() == "active":
            medication = entry.get("medication", "")
            if medication:
                active_medications.append({
                    "id": entry.get("id", ""),
                    "value": medication.lower(),
                    "display": medication,
                })

    # ── Recent Observations (last only) ─────────────────────────
    recent_observations = []
    observations = fhir_data.get("Observation", [])
    if observations:
        last_obs = observations[-1]
        value = last_obs.get("value", "")
        if value:
            recent_observations.append({
                "id": last_obs.get("id", ""),
                "value": str(value).lower(),
                "display": str(value),
            })

    # ── Recent Procedures (performed_days_ago <= 7) ─────────────
    recent_procedures = []
    for entry in fhir_data.get("Procedure", []):
        days_ago = entry.get("performed_days_ago", 999)
        if isinstance(days_ago, (int, float)) and days_ago <= 7:
            code = entry.get("code", "")
            if code:
                recent_procedures.append({
                    "id": entry.get("id", ""),
                    "value": code.lower(),
                    "display": code,
                })

    # ── Conditions ──────────────────────────────────────────────
    conditions = []
    for entry in fhir_data.get("Condition", []):
        name = entry.get("name", "")
        if name:
            conditions.append({
                "id": entry.get("id", ""),
                "value": name.lower(),
                "display": name,
            })

    return {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "gender": gender,
        "birth_date": birth_date,
        "allergies": allergies,
        "active_medications": active_medications,
        "recent_observations": recent_observations,
        "recent_procedures": recent_procedures,
        "conditions": conditions,
    }
