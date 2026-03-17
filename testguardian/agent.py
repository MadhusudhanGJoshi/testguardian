import yaml
from testguardian.registry import get_source, get_bugsystem
from testguardian.features import extract_features
from testguardian.predictor import load_model, predict_test
from testguardian.explainer import explain
from testguardian.recommender import recommend_action


class TestGuardianAgent:
    def __init__(self, config_path, model=None):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        source_type = self.config["source"]["type"]
        params = self.config["source"]["params"]
        self.source = get_source(source_type, **params)
        self.model = load_model()

        # Initialise bug system — defaults to NullBugSystem if not configured
        bugsystem_config = self.config.get("bugsystem", {})
        bugsystem_type = bugsystem_config.get("type", "none")
        bugsystem_params = bugsystem_config.get("params", {})
        self.bugsystem = get_bugsystem(bugsystem_type, **bugsystem_params)

    def run(self):
        raw_tests = self.source.scan()

        results = []

        for each_test in raw_tests:
            features = extract_features(each_test["path"])

            prediction, confidence = predict_test(self.model, features)

            reasons = explain(features, prediction)

            # Query bug system for open bugs against this test
            open_bugs = self.bugsystem.get_open_bugs(each_test["name"])

            action, status = recommend_action(prediction, open_bugs=open_bugs)

            result = {
                "test": each_test["name"],
                "language": each_test.get("language", "unknown"),
                "source": each_test["source"],
                "prediction": prediction,
                "confidence": round(confidence, 2),
                "reasons": reasons,
                "recommended_action": action,
                "status": status,
            }

            if open_bugs:
                result["open_bugs"] = open_bugs

            results.append(result)

        return results
