"""
recommender.py
--------------
Maps ML prediction + bug system check to a recommended action and status.

Logic:
    "flaky" or "obsolete":
        if open bugs exist against this test → "investigate" (active tracking, do not remove)
        if no open bugs                      → "remove" + "pending_expert_review"

    "unused":
        → "remove" + "pending_expert_review" (no bug check needed)

    "stable":
        → "keep" + "active"
"""


def recommend_action(prediction, open_bugs=None):
    """
    Parameters:
        prediction : str  — ML model label ("stable", "flaky", "obsolete", "unused")
        open_bugs  : list — open bug identifiers from bug system, or None/empty list

    Returns:
        (action, status) tuple
    """
    open_bugs = open_bugs or []

    if prediction in ("flaky", "obsolete"):
        if open_bugs:
            # Active bugs tracked against this test — do not remove
            return "investigate", "active"
        else:
            # No open bugs, consistently problematic — recommend removal
            return "remove", "pending_expert_review"

    if prediction == "unused":
        return "remove", "pending_expert_review"

    if prediction == "stable":
        return "keep", "active"

    # Fallback for any unknown prediction
    return "review", "pending_expert_review"
