
def explain(features, prediction):
    """
    Provide a simple explanation for prediction
    """

    explanation = {}

    if prediction == "HIGH_RISK":
        explanation["reason"] = "High code complexity or high test churn detected"
    elif prediction == "MEDIUM_RISK":
        explanation["reason"] = "Moderate feature volatility"
    else:
        explanation["reason"] = "Low complexity and stable code"

    explanation["features"] = features

    return explanation
