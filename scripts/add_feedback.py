"""
add_feedback.py
---------------
CLI tool for experts to correct agent predictions.
Corrections are saved to data/expert_feedback.json and
accumulate to build a real labelled training dataset.

Usage:
    PYTHONPATH=. python scripts/add_feedback.py --test test_login.py --label stable
    PYTHONPATH=. python scripts/add_feedback.py --test test_legacy_feature.py --label obsolete

Valid labels: stable, flaky, obsolete, unused
"""

import argparse
import sys
from testguardian.feedback import save_feedback

parser = argparse.ArgumentParser(
    description="Add expert feedback to correct a TestGuardian prediction."
)
parser.add_argument(
    "--test",
    required=True,
    help="Test filename to correct (e.g. test_login.py)"
)
parser.add_argument(
    "--label",
    required=True,
    choices=["stable", "flaky", "obsolete", "unused"],
    help="Correct label for this test"
)

args = parser.parse_args()

try:
    entry = save_feedback(args.test, args.label)
    print(f"\nFeedback saved:")
    print(f"  Test              : {entry['test_name']}")
    print(f"  Correct label     : {entry['actual_label']}")
    print(f"  Original prediction: {entry['original_prediction']}")
    print(f"  Timestamp         : {entry['feedback_timestamp']}")
    if entry.get("original_prediction") != "unknown":
        if entry["actual_label"] == entry["original_prediction"]:
            print(f"  Agreement         : Model was CORRECT")
        else:
            print(f"  Agreement         : Model was WRONG — correction recorded")
except ValueError as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to save feedback: {e}")
    sys.exit(1)
