import yaml
from testguardian.sources.registry import get_source


class TestGuardianAgent:
    def __init__(self, config_path, model=None):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        source_type = self.config["source"]["type"]
        params = self.config["source"]["params"]

        self.source = get_source(source_type, **params)
        self.model = model

    def run(self):
        raw_tests = self.source.scan()
        return raw_tests
