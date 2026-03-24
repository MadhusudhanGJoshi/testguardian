"""
build_training_data.py
----------------------
Builds a real labelled training dataset from expert feedback.
Merges expert corrections with their feature vectors extracted
at prediction time, producing a new training_data.csv.

Run this when enough feedback has accumulated (recommended: 50+ entries)
then retrain the model:
    PYTHONPATH=. python scripts/build_training_data.py
    PYTHONPATH=. python scripts/retrain_model.py

The resulting training_data.csv replaces the synthetic dataset
with real labelled data from your test suite.
"""

import json
import os
import sys
import pandas as pd
from datetime import datetime

FEEDBACK_FILE      = "data/expert_feedback.json"
TRAINING_DATA_FILE = "data/training_data.csv"
BACKUP_DIR         = "data/backups"

FEATURE_COLUMNS = [
    "file_size",
    "lines_of_code",
    "last_modified_days",
    "commit_frequency",
    "pass_rate",
    "fail_streak",
    "result_flips",
    "total_runs",
]

MIN_FEEDBACK_ENTRIES = 10


def build_training_data():

    # --- Load feedback ---
    if not os.path.exists(FEEDBACK_FILE):
        print(f"[ERROR] No feedback file found at '{FEEDBACK_FILE}'. "
              f"Run the agent and add expert feedback first.")
        sys.exit(1)

    with open(FEEDBACK_FILE, "r") as f:
        feedback = json.load(f)

    if not feedback:
        print(f"[ERROR] Feedback file is empty. Add expert feedback first via add_feedback.py.")
        sys.exit(1)

    if len(feedback) < MIN_FEEDBACK_ENTRIES:
        print(f"[WARNING] Only {len(feedback)} feedback entries found. "
              f"Recommended minimum is {MIN_FEEDBACK_ENTRIES} for reliable training. "
              f"Proceeding anyway...")

    # --- Build rows from feedback entries ---
    rows = []
    skipped = 0

    for entry in feedback:
        features = entry.get("features", {})

        # Skip entries with no feature data
        if not features:
            print(f"[WARNING] Skipping '{entry.get('test_name')}' — no feature data. "
                  f"Re-run the agent and re-add feedback to capture features.")
            skipped += 1
            continue

        row = {col: features.get(col, 0) for col in FEATURE_COLUMNS}
        row["label"] = entry["actual_label"]
        rows.append(row)

    if not rows:
        print(f"[ERROR] No usable feedback entries found with feature data. "
              f"Ensure the agent has run and predictions are saved before adding feedback.")
        sys.exit(1)

    df = pd.DataFrame(rows)

    # --- Label distribution check ---
    label_counts = df["label"].value_counts()
    print(f"\nLabel distribution in feedback:")
    for label, count in label_counts.items():
        print(f"  {label:<10} : {count} entries")

    missing_labels = set(["stable", "flaky", "obsolete", "unused"]) - set(label_counts.index)
    if missing_labels:
        print(f"\n[WARNING] Missing labels in feedback: {missing_labels}. "
              f"Model may not predict these classes well. "
              f"Consider adding more feedback for these labels.")

    # --- Backup existing training data ---
    if os.path.exists(TRAINING_DATA_FILE):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"training_data_{timestamp}.csv")
        pd.read_csv(TRAINING_DATA_FILE).to_csv(backup_path, index=False)
        print(f"\n[INFO] Existing training data backed up to '{backup_path}'")

    # --- Save new training data ---
    cols = FEATURE_COLUMNS + ["label"]
    df[cols].to_csv(TRAINING_DATA_FILE, index=False)

    print(f"\n[INFO] New training_data.csv saved with {len(df)} labelled rows.")
    print(f"[INFO] Skipped {skipped} entries with missing feature data.")
    print(f"\nNext step: run 'python scripts/retrain_model.py' to retrain the model.")


if __name__ == "__main__":
    build_training_data()
