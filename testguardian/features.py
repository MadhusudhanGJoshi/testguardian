import os
import time


def extract_features(test_path):

    features = {}

    # file size in bytes
    features["file_size"] = os.path.getsize(test_path)

    # number of lines
    with open(test_path, "r", encoding="utf-8", errors="ignore") as f:
        features["lines_of_code"] = len(f.readlines())

    # last modified time
    last_modified = os.path.getmtime(test_path)

    days_old = (time.time() - last_modified) / (60 * 60 * 24)

    features["last_modified_days"] = int(days_old)

    # placeholder for future git integration
    features["commit_frequency"] = 0

    return features
