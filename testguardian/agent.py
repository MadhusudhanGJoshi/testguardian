import os
import yaml
from testguardian.registry import get_source, get_bugsystem
from testguardian.features import extract_features
from testguardian.predictor import load_model, predict_test
from testguardian.explainer import explain
from testguardian.recommender import recommend_action
from testguardian.historyreader import read_history
 
 
class TestGuardianAgent:
    def __init__(self, config_path, model=None):
        # --- Config loading ---
        if not config_path or not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Config file not found: '{config_path}'. "
                f"Ensure config.yaml exists in the project root."
            )
 
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Malformed config file '{config_path}': {e}")
 
        if not self.config:
            raise ValueError(f"Config file '{config_path}' is empty or invalid.")
 
        # --- Source initialisation ---
        try:
            source_cfg = self.config.get("source", {})
            source_type = source_cfg.get("type")
            params = source_cfg.get("params", {})
            if not source_type:
                raise ValueError("'source.type' is missing from config.yaml.")
            self.source = get_source(source_type, **params)
        except Exception as e:
            raise RuntimeError(f"Failed to initialise test source: {e}")
 
        # --- Model loading ---
        try:
            self.model = load_model()
        except FileNotFoundError as e:
            raise FileNotFoundError(str(e))
        except RuntimeError as e:
            raise RuntimeError(str(e))
 
        # --- History loading (optional — warn but don't crash) ---
        history_path = self.config.get("history", {}).get("path", "")
        self.history = read_history(history_path)
 
        # --- Bug system initialisation (optional — warn but don't crash) ---
        try:
            bugsystem_config = self.config.get("bugsystem", {})
            bugsystem_type = bugsystem_config.get("type", "none")
            bugsystem_params = bugsystem_config.get("params", {})
            self.bugsystem = get_bugsystem(bugsystem_type, **bugsystem_params)
        except Exception as e:
            print(f"[WARNING] Failed to initialise bug system: {e}. Continuing without it.")
            from testguardian.bugsystems.null_bugsystem import NullBugSystem
            self.bugsystem = NullBugSystem()
 
    def run(self):
        """
        Scan, predict, and recommend for all discovered tests.
        Per-test errors are caught and logged — a single bad file
        will not stop the entire run.
        """
        try:
            raw_tests = self.source.scan()
        except Exception as e:
            raise RuntimeError(f"Failed to scan test sources: {e}")
 
        if not raw_tests:
            print("[WARNING] No test files found. Check 'source.params.path' in config.yaml.")
            return []
 
        results = []
 
        for each_test in raw_tests:
            try:
                # Look up history stats — exact match first,
                # then suffix match to handle classname.testname format
                # e.g. "tests.test_login.py" matches "test_login.py"
                test_name = each_test["name"]
                test_history = self.history.get(test_name)
                if test_history is None:
                    for key in self.history:
                        if key.endswith("." + test_name) or key.endswith("/" + test_name):
                            test_history = self.history[key]
                            break
 
                features = extract_features(each_test["path"], history_stats=test_history)
 
                prediction, confidence = predict_test(self.model, features)
 
                reasons = explain(features, prediction)
 
                try:
                    open_bugs = self.bugsystem.get_open_bugs(each_test["name"])
                except Exception as e:
                    print(f"[WARNING] Bug system query failed for '{each_test['name']}': {e}. "
                          f"Proceeding without bug data.")
                    open_bugs = []
 
                action, status = recommend_action(prediction, open_bugs=open_bugs)
 
                result = {
                    "test":               each_test["name"],
                    "language":           each_test.get("language", "unknown"),
                    "source":             each_test["source"],
                    "prediction":         prediction,
                    "confidence":         round(confidence, 2),
                    "reasons":            reasons,
                    "recommended_action": action,
                    "status":             status,
                }
 
                if test_history:
                    result["history"] = {
                        "total_runs":   test_history["total_runs"],
                        "pass_rate":    f"{test_history['pass_rate'] * 100:.1f}%",
                        "fail_streak":  test_history["fail_streak"],
                        "result_flips": test_history["result_flips"],
                    }
 
                if open_bugs:
                    result["open_bugs"] = open_bugs
 
                results.append(result)
 
            except Exception as e:
                print(f"[ERROR] Skipping test '{each_test.get('name', 'unknown')}': {e}")
                continue
 
        return results
 
