#!/usr/bin/env python3
"""
testguardian.py
---------------
CLI entry point for TestGuardian.

Usage:
    python testguardian.py --source <path> --type <ext> [options]

Examples:
    # Scan pytest tests with no history
    python testguardian.py --source ./tests --type .py

    # Scan MTR tests with execution history
    python testguardian.py --source mysql-test/suite/ --type .test \\
        --suite-dir t --history data/reports/mtr/

    # Scan JUnit tests, save report to custom directory
    python testguardian.py --source ./src/test --type .java \\
        --history data/reports/junit/ --output ./reports/ --format both

    # All supported types, no history
    python testguardian.py --source ./tests
"""

import sys
import argparse
from testguardian.agent import TestGuardianAgent
from testguardian.reporter import generate_report


import json
import os
from datetime import datetime


SUPPORTED_TYPES = [".py", ".java", ".js", ".ts", ".robot", ".mtr", ".test"]


def parse_args():
    parser = argparse.ArgumentParser(
        prog="testguardian",
        description="TestGuardian — AI-powered test suite governance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python testguardian.py --source ./tests --type .py
  python testguardian.py --source mysql-test/suite/ --type .test --suite-dir t
  python testguardian.py --source ./tests --type .java --history data/reports/junit/
        """
    )

    # Required
    parser.add_argument(
        "--source",
        required=True,
        help="Path to the test base directory to scan"
    )

    # Optional
    parser.add_argument(
        "--type",
        choices=SUPPORTED_TYPES,
        default=None,
        help="Test file type to scan (e.g. .py, .java, .test). "
             "Omit to scan all supported types."
    )
    parser.add_argument(
        "--history",
        default="",
        help="Path to execution history directory or file "
             "(JUnit XML, Robot XML, MTR .result, CSV). "
             "Omit to run without history."
    )
    parser.add_argument(
        "--suite-dir",
        default=None,
        dest="suite_dir",
        help="Only scan tests inside subdirectories with this name "
             "(e.g. 't' for MySQL suite/*/t/*.test structure)"
    )
    parser.add_argument(
        "--output",
        default="reports/",
        help="Directory to save the JSON report (default: reports/)"
    )
    parser.add_argument(
        "--format",
        choices=["console", "json", "both"],
        default="both",
        help="Report output format (default: both)"
    )
    parser.add_argument(
        "--bugsystem",
        choices=["none"],
        default="none",
        help="Bug system integration (default: none)"
    )

    return parser.parse_args()


def build_cli_config(args) -> dict:
    """Build the agent config dict from CLI arguments."""
    return {
        "source": {
            "type": "filesystem",
            "params": {
                "path":      args.source,
                "filter":    args.type,
                "suite_dir": args.suite_dir,
            }
        },
        "history": {
            "path": args.history or ""
        },
        "bugsystem": {
            "type":   args.bugsystem,
            "params": {}
        },
        "model": {
            "threshold": 0.7
        }
    }


def _export_metrics_safe():
    try:
        import subprocess, sys
        subprocess.run([sys.executable, 'scripts/export_metrics.py'], check=False)
    except Exception:
        pass


def save_predictions(results: list, output_dir: str):
    """Append this run's predictions to data/predictions.json."""
    predictions_file = "data/predictions.json"
    run_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    run_id        = "run_" + datetime.now().strftime("%Y%m%d_%H%M%S")

    for r in results:
        r["timestamp"] = run_timestamp

    payload = {
        "run_timestamp": run_timestamp,
        "run_id":        run_id,
        "total_tests":   len(results),
        "predictions":   results
    }

    os.makedirs("data", exist_ok=True)
    all_runs = []
    if os.path.exists(predictions_file):
        try:
            with open(predictions_file, "r") as f:
                all_runs = json.load(f)
            if not isinstance(all_runs, list):
                all_runs = [all_runs]
        except Exception:
            all_runs = []

    all_runs.append(payload)
    with open(predictions_file, "w") as f:
        json.dump(all_runs, f, indent=2)


def main():
    args = parse_args()

    print("\n  TestGuardian — AI-powered test suite governance")
    print("  " + "─" * 48)

    # Build config from CLI args
    config = build_cli_config(args)

    # Run agent
    try:
        agent   = TestGuardianAgent(cli_config=config)
        results = agent.run()
    except (FileNotFoundError, RuntimeError, ValueError) as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

    if not results:
        print("[WARNING] No results to report.")
        sys.exit(0)

    # Generate report
    generate_report(
        results    = results,
        source     = args.source,
        test_type  = args.type or "all",
        has_history= bool(args.history),
        output_dir = args.output,
        fmt        = args.format,
    )

    # Save predictions and export metrics
    save_predictions(results, args.output)
    _export_metrics_safe()


if __name__ == "__main__":
    main()
