# run_agent.py

from testguardian.agent import TestGuardianAgent

agent = TestGuardianAgent("config.yaml")
results = agent.run()

for r in results:
    print("\n----------------------------------")
    print("Test              :", r["test"])
    print("Language          :", r["language"])
    print("Prediction        :", r["prediction"])
    print("Confidence        :", r["confidence"])
    print("Recommended Action:", r["recommended_action"])
    print("Status            :", r["status"])
    if "open_bugs" in r:
        print("Open Bugs         :", ", ".join(r["open_bugs"]))
    print("Reasons:")
    for k, v in r["reasons"].items():
        print(f"  - {k}: {v}")# run_agent.py
