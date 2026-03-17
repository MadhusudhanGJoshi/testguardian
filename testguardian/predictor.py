#import joblib
#import os
#import pandas as pd

#MODEL_PATH = "models/test_model.pkl"

## Load model once
#model = None

#def load_model():
#    global model
#    if model is None:
#        if not os.path.exists(MODEL_PATH):
#            raise Exception("Model not found. Run retrain_model.py first.")
#        model = joblib.load(MODEL_PATH)
#    return model


#def predict_test(features):

#    model = load_model()

##    X = [[
##        features["file_size"],
##        features["last_modified_days"],
##        features["commit_frequency"]
##    ]]

##    prediction = model.predict([features])[0]

#    X = pd.DataFrame([features])

#    prediction = model.predict(X)[0]
#    confidence = model.predict_proba(X).max()
#    probabilities = model.predict_proba(X)[0]
#   # confidence = max(probabilities)

#    return prediction, confidence


import joblib
import pandas as pd

MODEL_PATH = "models/testguardian_model.pkl"

FEATURE_COLUMNS = [
    "file_size",
    "last_modified_days",
    "commit_frequency"
]

def load_model():
    return joblib.load(MODEL_PATH)


def predict_test(model, features):

    model = joblib.load(MODEL_PATH)

    # Ensure consistent feature ordering
    ordered_features = {k: features.get(k, 0) for k in FEATURE_COLUMNS}

    X = pd.DataFrame([ordered_features])

    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X).max()

    return prediction, confidence
