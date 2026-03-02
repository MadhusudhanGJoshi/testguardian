import os
import pandas as pd


def extract_features(repo_path: str) -> pd.DataFrame:
    """
    Extract structured features from test repository.
    Each row represents a test file.
    """
    data = []

    tests_dir = os.path.join(repo_path, "tests")

    for root, _, files in os.walk(tests_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                file_path = os.path.join(root, file)

                with open(file_path, "r") as f:
                    content = f.readlines()

                feature_row = {
                    "test_name": file,
                    "lines_of_code": len(content),
                    "assert_count": sum(1 for line in content if "assert" in line),
                }

                data.append(feature_row)

    return pd.DataFrame(data)
