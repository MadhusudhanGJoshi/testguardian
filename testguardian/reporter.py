"""
reporter.py
-----------
Generates console and JSON reports from agent prediction results.
"""

import json
import os
from datetime import datetime


REPORT_DIR = "reports"


def _console_report(results: list, source: str, test_type: str, has_history: bool):
    """Print a formatted console summary table."""

    print("\n" + "=" * 70)
    print(f"  TestGuardian Report")
    print(f"  Source  : {source}")
    print(f"  Type    : {test_type}")
    print(f"  History : {'provided' if has_history else 'not provided — using file metadata only'}")
    print(f"  Run at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Summary counts
    pred_counts   = {}
    action_counts = {}
    for r in results:
        pred_counts[r["prediction"]]         = pred_counts.get(r["prediction"], 0) + 1
        action_counts[r["recommended_action"]] = action_counts.get(r["recommended_action"], 0) + 1

    print(f"\n  Total tests scanned : {len(results)}")
    print(f"  Predictions         : " +
          " | ".join(f"{k}: {v}" for k, v in sorted(pred_counts.items())))
    print(f"  Actions             : " +
          " | ".join(f"{k}: {v}" for k, v in sorted(action_counts.items())))
    print()

    # Per-test table
    col_w = [40, 12, 10, 10, 8, 20]
    header = (
        f"{'Test':<{col_w[0]}}"
        f"{'Language':<{col_w[1]}}"
        f"{'Prediction':<{col_w[2]}}"
        f"{'Confidence':<{col_w[3]}}"
        f"{'Suite':<{col_w[4]}}"
        f"{'Action':<{col_w[5]}}"
    )
    print("  " + header)
    print("  " + "-" * sum(col_w))

    for r in results:
        suite = r.get("suite", "—")
        conf  = f"{r['confidence'] * 100:.0f}%"
        print(
            f"  {r['test']:<{col_w[0]}}"
            f"{r['language']:<{col_w[1]}}"
            f"{r['prediction']:<{col_w[2]}}"
            f"{conf:<{col_w[3]}}"
            f"{suite:<{col_w[4]}}"
            f"{r['recommended_action']:<{col_w[5]}}"
        )

    print()
    pending = sum(1 for r in results if r["status"] == "pending_expert_review")
    print(f"  {pending} test(s) flagged as pending_expert_review")
    print("=" * 70 + "\n")


def _json_report(results: list, source: str, test_type: str,
                 has_history: bool, output_dir: str) -> str:
    """Save a structured JSON report and return the file path."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename   = f"testguardian_report_{timestamp}.json"
    filepath   = os.path.join(output_dir, filename)

    pred_counts   = {}
    action_counts = {}
    for r in results:
        pred_counts[r["prediction"]]           = pred_counts.get(r["prediction"], 0) + 1
        action_counts[r["recommended_action"]] = action_counts.get(r["recommended_action"], 0) + 1

    report = {
        "run_timestamp":           datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source":                  source,
        "test_type":               test_type,
        "history_provided":        has_history,
        "total_tests":             len(results),
        "prediction_distribution": pred_counts,
        "action_distribution":     action_counts,
        "pending_expert_review":   sum(1 for r in results if r["status"] == "pending_expert_review"),
        "results":                 results,
    }

    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)

    return filepath


def generate_report(results: list, source: str, test_type: str,
                    has_history: bool, output_dir: str = REPORT_DIR,
                    fmt: str = "both") -> str:
    """
    Generate report in requested format.

    Parameters:
        results    : list of prediction dicts from agent.run()
        source     : test source path
        test_type  : file extension filter used
        has_history: whether execution history was provided
        output_dir : directory to save JSON report
        fmt        : "console", "json", or "both"

    Returns:
        path to saved JSON report (or empty string if console only)
    """
    filepath = ""

    if fmt in ("console", "both"):
        _console_report(results, source, test_type, has_history)

    if fmt in ("json", "both"):
        filepath = _json_report(results, source, test_type, has_history, output_dir)
        print(f"[INFO] Report saved to '{filepath}'")

    return filepath
