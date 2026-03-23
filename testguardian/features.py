import os
import time
 
 
def extract_features(test_path, history_stats=None):
    """
    Extract features from a test file path and optional execution history.
 
    Parameters:
        test_path     : str  — path to the test file
        history_stats : dict — normalised stats from historyreader.read_history()
                               If None or empty, history features default to 0.
 
    Returns:
        dict of all features ready for the predictor.
 
    Raises:
        FileNotFoundError : if test_path does not exist
        PermissionError   : if test_path is not readable
    """
    if not test_path:
        raise ValueError("test_path must not be empty.")
 
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test file not found: '{test_path}'")
 
    if not os.access(test_path, os.R_OK):
        raise PermissionError(f"Test file is not readable: '{test_path}'")
 
    features = {}
 
    # --- File metadata features ---
    features["file_size"] = os.path.getsize(test_path)
 
    try:
        with open(test_path, "r", encoding="utf-8", errors="ignore") as f:
            features["lines_of_code"] = len(f.readlines())
    except Exception as e:
        print(f"[WARNING] Could not read lines from '{test_path}': {e}. Defaulting to 0.")
        features["lines_of_code"] = 0
 
    last_modified = os.path.getmtime(test_path)
    days_old = (time.time() - last_modified) / (60 * 60 * 24)
    features["last_modified_days"] = int(days_old)
 
    # Placeholder for future git integration
    features["commit_frequency"] = 0
 
    # --- Execution history features ---
    h = history_stats or {}
 
    def _safe_get(key, default):
        val = h.get(key, default)
        try:
            return type(default)(val)
        except (TypeError, ValueError):
            print(f"[WARNING] Invalid value for history feature '{key}': {val!r}. "
                  f"Defaulting to {default}.")
            return default
 
    features["pass_rate"]    = _safe_get("pass_rate",    0.0)
    features["fail_streak"]  = _safe_get("fail_streak",  0)
    features["result_flips"] = _safe_get("result_flips", 0)
    features["total_runs"]   = _safe_get("total_runs",   0)
 
    return features
 
