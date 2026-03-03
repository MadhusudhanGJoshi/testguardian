import os
from .base import TestSource


class FileSystemSource(TestSource):
    def __init__(self, path):
        self.path = path

    def scan(self):
        tests = []

        for root, _, files in os.walk(self.path):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    tests.append({
                        "name": file,
                        "source": "filesystem",
                        "path": os.path.join(root, file)
                    })

        return tests
