import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

MODEL_PATH = "models/testguardian_model.pkl"

def retrain_model():

    test_df  = pd.read_csv("data/training_data.csv")

    X = test_df[["file_size", "last_modified_days", "commit_frequency"]]
    y = test_df["label"]

    model = RandomForestClassifier()
    model.fit(X, y)

    import os
    os.makedirs("models", exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("Model retrained and saved")
