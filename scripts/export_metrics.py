"""
export_metrics.py
-----------------
Reads predictions.json and expert_feedback.json and exports
a structured metrics.json file suitable for dashboards.

Outputs:
    data/metrics.json  — current run metrics (Grafana-ready)

Run after each agent run:
    PYTHONPATH=. python scripts/export_metrics.py
"""

import json
import os
import sys
from datetime import datetime
from collections import Counter

PREDICTIONS_FILE = "data/predictions.json"
FEEDBACK_FILE    = "data/expert_feedback.json"
METRICS_FILE     = "data/metrics.json"


def export_metrics():

    # --- Load predictions ---
    if not os.path.exists(PREDICTIONS_FILE):
        print(f"[ERROR] No predictions file found at '{PREDICTIONS_FILE}'. "
              f"Run the agent first.")
        sys.exit(1)

    with open(PREDICTIONS_FILE, "r") as f:
        all_runs = json.load(f)

    if not all_runs:
        print(f"[ERROR] Predictions file is empty.")
        sys.exit(1)

    if not isinstance(all_runs, list):
        all_runs = [all_runs]

    # --- Load feedback ---
    feedback = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r") as f:
                feedback = json.load(f)
        except Exception:
            feedback = []

    # --- Build per-run metrics ---
    runs_metrics = []

    for run in all_runs:
        predictions = run.get("predictions", [])
        if not predictions:
            continue

        prediction_dist = Counter(p["prediction"] for p in predictions)
        action_dist     = Counter(p["recommended_action"] for p in predictions)
        confidences     = [p["confidence"] for p in predictions]
        pending         = sum(1 for p in predictions if p["status"] == "pending_expert_review")

        run_metrics = {
            "run_id":                  run.get("run_id", "unknown"),
            "run_timestamp":           run.get("run_timestamp", "unknown"),
            "total_tests":             len(predictions),
            "prediction_distribution": dict(prediction_dist),
            "action_distribution":     dict(action_dist),
            "avg_confidence":          round(sum(confidences) / len(confidences), 3),
            "min_confidence":          round(min(confidences), 3),
            "max_confidence":          round(max(confidences), 3),
            "pending_expert_review":   pending,
        }
        runs_metrics.append(run_metrics)

    # --- Latest run metrics ---
    latest = runs_metrics[-1]

    # --- Feedback metrics ---
    feedback_count = len(feedback)
    correct = sum(
        1 for f in feedback
        if f.get("actual_label") == f.get("original_prediction")
        and f.get("original_prediction") != "unknown"
    )
    total_with_prediction = sum(
        1 for f in feedback
        if f.get("original_prediction") != "unknown"
    )
    model_accuracy = (
        round(correct / total_with_prediction, 3)
        if total_with_prediction > 0 else None
    )

    label_corrections = Counter(f["actual_label"] for f in feedback)

    # --- Compose final metrics ---
    metrics = {
        "exported_at":          datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "latest_run":           latest,
        "all_runs":             runs_metrics,
        "feedback": {
            "total_entries":        feedback_count,
            "model_accuracy":       model_accuracy,
            "correct_predictions":  correct,
            "total_reviewed":       total_with_prediction,
            "label_corrections":    dict(label_corrections),
        },
        "summary": {
            "total_runs_recorded":  len(runs_metrics),
            "tests_to_remove":      latest["action_distribution"].get("remove", 0),
            "tests_to_keep":        latest["action_distribution"].get("keep", 0),
            "tests_to_investigate": latest["action_distribution"].get("investigate", 0),
        }
    }

    os.makedirs("data", exist_ok=True)
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[INFO] Metrics exported to '{METRICS_FILE}'")
    print(f"\n--- Latest Run Summary ---")
    print(f"  Run ID          : {latest['run_id']}")
    print(f"  Total tests     : {latest['total_tests']}")
    print(f"  Avg confidence  : {latest['avg_confidence']}")
    print(f"  Pending review  : {latest['pending_expert_review']}")
    print(f"  Predictions     : {latest['prediction_distribution']}")
    print(f"  Actions         : {latest['action_distribution']}")
    if model_accuracy is not None:
        print(f"\n--- Feedback Loop ---")
        print(f"  Feedback entries: {feedback_count}")
        print(f"  Model accuracy  : {model_accuracy * 100:.1f}% ({correct}/{total_with_prediction} correct)")


if __name__ == "__main__":
    export_metrics()
