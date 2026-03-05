import json
import os

FEEDBACK_FILE = "data/expert_feedback.json"

def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    
    with open(FEEDBACK_FILE, "r") as f:
        return json.load(f)


def save_feedback(entry):
    feedback = load_feedback()
    feedback.append(entry)

    os.makedirs("data", exist_ok=True)

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(feedback, f, indent=2)
