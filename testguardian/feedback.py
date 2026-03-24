"""
feedback.py
-----------
Manages expert feedback on agent predictions.
Feedback entries are saved to data/expert_feedback.json and
accumulate over time to build a real labelled training dataset.
"""

import json
import os
from datetime import datetime

FEEDBACK_FILE    = "data/expert_feedback.json"
PREDICTIONS_FILE = "data/predictions.json"


def load_feedback() -> list:
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"[WARNING] Could not read feedback file: {e}. Returning empty list.")
        return []


def load_latest_prediction(test_name: str) -> dict:
    """
    Look up the most recent prediction for a given test name
    from data/predictions.json. Returns empty dict if not found.
    """
    if not os.path.exists(PREDICTIONS_FILE):
        return {}
    try:
        with open(PREDICTIONS_FILE, "r") as f:
            all_runs = json.load(f)
        if not isinstance(all_runs, list):
            all_runs = [all_runs]
        # Search from most recent run backwards
        for run in reversed(all_runs):
            for pred in run.get("predictions", []):
                if pred.get("test") == test_name:
                    return pred
    except Exception as e:
        print(f"[WARNING] Could not read predictions file: {e}.")
    return {}


def save_feedback(test_name: str, actual_label: str) -> dict:
    """
    Save an expert correction for a given test.
    Enriches the entry with the original prediction context if available.

    Parameters:
        test_name    : filename of the test (e.g. "test_login.py")
        actual_label : expert's correct label ("stable","flaky","obsolete","unused")

    Returns:
        The saved feedback entry.
    """
    valid_labels = {"stable", "flaky", "obsolete", "unused"}
    if actual_label not in valid_labels:
        raise ValueError(
            f"Invalid label '{actual_label}'. Must be one of: {valid_labels}"
        )

    # Look up original prediction for context
    prediction = load_latest_prediction(test_name)

    entry = {
        "test_name":          test_name,
        "actual_label":       actual_label,
        "feedback_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "original_prediction": prediction.get("prediction", "unknown"),
        "original_confidence": prediction.get("confidence", None),
        "features":            prediction.get("reasons", {}).get("features", {}),
    }

    feedback = load_feedback()
    feedback.append(entry)

    os.makedirs("data", exist_ok=True)
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=2)

    return entry
