import os
import joblib
import pandas as pd
 
MODEL_PATH = "models/testguardian_model.pkl"
 
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
 
 
def load_model():
    """
    Load the trained Random Forest model from disk.
 
    Raises:
        FileNotFoundError : if model file does not exist
        RuntimeError      : if model file is corrupt or unloadable
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at '{MODEL_PATH}'. "
            f"Run 'python scripts/retrain_model.py' to train the model first."
        )
    try:
        return joblib.load(MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to load model from '{MODEL_PATH}': {e}")
 
 
def predict_test(model, features):
    """
    Run prediction for a single test using extracted features.
 
    Raises:
        ValueError  : if features dict is missing required columns
        RuntimeError: if model prediction fails
    """
    if not features:
        raise ValueError("Features dict is empty. Cannot run prediction.")
 
    missing = [col for col in FEATURE_COLUMNS if col not in features]
    if missing:
        raise ValueError(
            f"Features dict is missing required columns: {missing}. "
            f"Ensure extract_features() is returning all expected keys."
        )
 
    try:
        ordered_features = {k: features.get(k, 0) for k in FEATURE_COLUMNS}
        X = pd.DataFrame([ordered_features])
        prediction = model.predict(X)[0]
        confidence = model.predict_proba(X).max()
        return prediction, confidence
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}")
 
