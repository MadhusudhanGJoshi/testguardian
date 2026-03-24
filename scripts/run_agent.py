import json
import os
from datetime import datetime
from testguardian.agent import TestGuardianAgent

PREDICTIONS_FILE = "data/predictions.json"

agent = TestGuardianAgent("config.yaml")
results = agent.run()

# --- Console output ---
for r in results:
    print("\n----------------------------------")
    print("Test              :", r["test"])
    print("Language          :", r["language"])
    print("Prediction        :", r["prediction"])
    print("Confidence        :", r["confidence"])
    print("Recommended Action:", r["recommended_action"])
    print("Status            :", r["status"])
    if "history" in r:
        h = r["history"]
        print(f"History           : {h['total_runs']} runs | "
              f"Pass rate: {h['pass_rate']} | "
              f"Fail streak: {h['fail_streak']} | "
              f"Flips: {h['result_flips']}")
    if "open_bugs" in r:
        print("Open Bugs         :", ", ".join(r["open_bugs"]))
    print("Reasons:")
    for k, v in r["reasons"].items():
        print(f"  - {k}: {v}")

# --- Save predictions to JSON ---
run_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
run_id = "run_" + datetime.now().strftime("%Y%m%d_%H%M%S")

# Attach timestamp to each prediction entry
for r in results:
    r["timestamp"] = run_timestamp

payload = {
    "run_timestamp": run_timestamp,
    "run_id":        run_id,
    "total_tests":   len(results),
    "predictions":   results
}

# Load existing predictions and append this run
os.makedirs("data", exist_ok=True)
all_runs = []
if os.path.exists(PREDICTIONS_FILE):
    try:
        with open(PREDICTIONS_FILE, "r") as f:
            all_runs = json.load(f)
        if not isinstance(all_runs, list):
            all_runs = [all_runs]
    except (json.JSONDecodeError, Exception) as e:
        print(f"[WARNING] Could not read existing predictions file: {e}. Starting fresh.")
        all_runs = []

all_runs.append(payload)

with open(PREDICTIONS_FILE, "w") as f:
    json.dump(all_runs, f, indent=2)

print(f"\n[INFO] Predictions saved to '{PREDICTIONS_FILE}' (run_id: {run_id})")
