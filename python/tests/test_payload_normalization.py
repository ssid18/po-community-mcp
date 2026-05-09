"""Verification: prescribe payload accepts both 'drug' and 'medication' keys."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.rule_engine import evaluate_action

_CONTEXT_WITH_PENICILLIN_ALLERGY = {
    "allergies": [{"id": "123", "value": "penicillin", "display": "Penicillin"}],
    "active_medications": [],
    "recent_observations": [],
    "recent_procedures": [],
    "conditions": [],
}


def test_prescribe_drug_key_triggers_allergy_rule():
    """Existing behavior: payload['drug'] = 'penicillin' → NO_GO / allergy."""
    action = {"type": "prescribe", "payload": {"drug": "penicillin"}}
    result = evaluate_action(action, _CONTEXT_WITH_PENICILLIN_ALLERGY)
    assert result["decision"] == "NO_GO"
    assert result["rule_triggered"] == "allergy"
    assert result["severity"] == "high"


def test_prescribe_medication_key_triggers_allergy_rule():
    """New case: payload['medication'] = 'Penicillin' → NO_GO / allergy (case-insensitive)."""
    action = {"type": "prescribe", "payload": {"medication": "Penicillin"}}
    result = evaluate_action(action, _CONTEXT_WITH_PENICILLIN_ALLERGY)
    assert result["decision"] == "NO_GO"
    assert result["rule_triggered"] == "allergy"
    assert result["severity"] == "high"


def test_prescribe_drug_key_takes_precedence_over_medication_key():
    """'drug' wins when both keys are present."""
    action = {"type": "prescribe", "payload": {"drug": "penicillin", "medication": "aspirin"}}
    result = evaluate_action(action, _CONTEXT_WITH_PENICILLIN_ALLERGY)
    assert result["decision"] == "NO_GO"
    assert result["rule_triggered"] == "allergy"


def test_prescribe_safe_drug_returns_go():
    """Safe drug via 'medication' key → GO."""
    action = {"type": "prescribe", "payload": {"medication": "aspirin"}}
    result = evaluate_action(action, _CONTEXT_WITH_PENICILLIN_ALLERGY)
    assert result["decision"] == "GO"
    assert result["rule_triggered"] == "none"


def test_prescribe_empty_payload_returns_go():
    """Empty payload → GO (no drug to evaluate)."""
    action = {"type": "prescribe", "payload": {}}
    result = evaluate_action(action, _CONTEXT_WITH_PENICILLIN_ALLERGY)
    assert result["decision"] == "GO"
