import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
 
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
 
TRAINING_DATA_PATH = "data/training_data.csv"
 
 
def retrain_model():
    """
    Retrain the Random Forest model from training_data.csv.
 
    Raises:
        FileNotFoundError : if training data file is missing
        ValueError        : if training data is missing required columns or has no rows
        RuntimeError      : if model training or saving fails
    """
    if not os.path.exists(TRAINING_DATA_PATH):
        raise FileNotFoundError(
            f"Training data not found at '{TRAINING_DATA_PATH}'. "
            f"Ensure the file exists before retraining."
        )
 
    try:
        test_df = pd.read_csv(TRAINING_DATA_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to read training data from '{TRAINING_DATA_PATH}': {e}")
 
    if test_df.empty:
        raise ValueError(f"Training data file '{TRAINING_DATA_PATH}' is empty.")
 
    missing_cols = [c for c in FEATURE_COLUMNS + ["label"] if c not in test_df.columns]
    if missing_cols:
        raise ValueError(
            f"Training data is missing required columns: {missing_cols}. "
            f"Found columns: {list(test_df.columns)}"
        )
 
    X = test_df[FEATURE_COLUMNS]
    y = test_df["label"]
 
    if len(X) < 10:
        print(f"[WARNING] Only {len(X)} training rows found. "
              f"Model accuracy may be low. Consider expanding training data.")
 
    try:
        model = RandomForestClassifier()
        model.fit(X, y)
    except Exception as e:
        raise RuntimeError(f"Model training failed: {e}")
 
    try:
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, MODEL_PATH)
    except Exception as e:
        raise RuntimeError(f"Failed to save model to '{MODEL_PATH}': {e}")
 
    print(f"Model retrained on {len(X)} rows and saved to '{MODEL_PATH}'")
 
