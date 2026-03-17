import os
from .base import TestSource


# Maps file extension to test framework label
SUPPORTED_EXTENSIONS = {
    ".py":    "pytest/unittest",
    ".java":  "JUnit",
    ".js":    "Jest/Mocha",
    ".ts":    "Jest/Mocha (TypeScript)",
    ".robot": "Robot Framework",
    ".mtr":   "MTR (MySQL Test Run)",
    ".test":  "MTR (MySQL Test Run)",
}

# Per-extension naming conventions that identify a file as a test
TEST_PATTERNS = {
    ".py":    lambda f: f.startswith("test_") or f.startswith("test-"),
    ".java":  lambda f: f.startswith("Test") or f.endswith("Test.java") or f.endswith("Tests.java"),
    ".js":    lambda f: "test" in f.lower() or "spec" in f.lower(),
    ".ts":    lambda f: "test" in f.lower() or "spec" in f.lower(),
    ".robot": lambda f: True,   # all .robot files are tests
    ".mtr":   lambda f: True,   # all .mtr files are MTR tests
    ".test":  lambda f: True,   # all .test files are MTR tests
}


def is_test_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False
    matcher = TEST_PATTERNS.get(ext)
    return matcher(filename) if matcher else False


class FileSystemSource(TestSource):
    def __init__(self, path):
        self.path = path

    def scan(self):
        tests = []

        for root, _, files in os.walk(self.path):
            for file in files:
                if is_test_file(file):
                    ext = os.path.splitext(file)[1].lower()
                    tests.append({
                        "name": file,
                        "source": "filesystem",
                        "path": os.path.join(root, file),
                        "language": SUPPORTED_EXTENSIONS.get(ext, "unknown"),
                    })

        return tests
