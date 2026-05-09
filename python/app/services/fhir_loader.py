import json
import os


def load_patient_data(patient_id: str) -> dict:
    """Load mock FHIR data from JSON file. Returns empty dict on failure."""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", f"{patient_id}.json")
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
