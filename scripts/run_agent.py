# run_agent.py

from testguardian.agent import TestGuardianAgent

agent = TestGuardianAgent("config.yaml")
results = agent.run()

print(results)
