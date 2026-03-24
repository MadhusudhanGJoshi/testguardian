import os
from .base import TestSource


SUPPORTED_EXTENSIONS = {
    ".py":    "pytest/unittest",
    ".java":  "JUnit",
    ".js":    "Jest/Mocha",
    ".ts":    "Jest/Mocha (TypeScript)",
    ".robot": "Robot Framework",
    ".mtr":   "MTR (MySQL Test Run)",
    ".test":  "MTR (MySQL Test Run)",
}

TEST_PATTERNS = {
    ".py":    lambda f: f.startswith("test_") or f.startswith("test-"),
    ".java":  lambda f: f.startswith("Test") or f.endswith("Test.java") or f.endswith("Tests.java"),
    ".js":    lambda f: "test" in f.lower() or "spec" in f.lower(),
    ".ts":    lambda f: "test" in f.lower() or "spec" in f.lower(),
    ".robot": lambda f: True,
    ".mtr":   lambda f: True,
    ".test":  lambda f: True,
}


def _normalise_filter(filter_param) -> set:
    """Normalise filter param into a set of lowercase extensions."""
    if not filter_param:
        return set()
    if isinstance(filter_param, str):
        filter_param = [filter_param]
    normalised = set()
    for ext in filter_param:
        ext = ext.strip().lower()
        if not ext.startswith("."):
            ext = "." + ext
        if ext not in SUPPORTED_EXTENSIONS:
            print(f"[WARNING] Filter extension '{ext}' is not recognised. "
                  f"Supported: {list(SUPPORTED_EXTENSIONS.keys())}. Ignored.")
        else:
            normalised.add(ext)
    return normalised


def is_test_file(filename, allowed_extensions=None):
    """Returns True if filename is a recognised test file."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return False
    if allowed_extensions and ext not in allowed_extensions:
        return False
    matcher = TEST_PATTERNS.get(ext)
    return matcher(filename) if matcher else False


def _infer_suite(file_path: str, base_path: str) -> str:
    """
    Infer the suite name from the file path relative to base_path.

    For structures like:
        mysql-test/suite/innodb/t/test_basic.test
    Returns: "innodb"

    For flat structures:
        sample_tests/test_login.py
    Returns: "—"
    """
    rel = os.path.relpath(file_path, base_path)
    parts = rel.split(os.sep)
    # If path has at least 2 parts (suite/test or suite/t/test), use first part as suite
    if len(parts) >= 2:
        return parts[0]
    return "—"


class FileSystemSource(TestSource):
    def __init__(self, path, filter=None, suite_dir=None):
        """
        Parameters:
            path      : str          — root directory to scan
            filter    : str or list  — file extension(s) to include
            suite_dir : str          — only scan files inside subdirs with this name
                                       e.g. "t" for MySQL suite structure (suite/*/t/*.test)
                                       If None, scan all subdirectories
        """
        if not path:
            raise ValueError("'source.params.path' must not be empty.")

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Test source path not found: '{path}'. "
                f"Check --source argument."
            )

        if not os.path.isdir(path):
            raise NotADirectoryError(
                f"Test source path is not a directory: '{path}'."
            )

        self.path       = path
        self.suite_dir  = suite_dir
        self.allowed_extensions = _normalise_filter(filter)

        if self.allowed_extensions:
            labels = [SUPPORTED_EXTENSIONS[e] for e in self.allowed_extensions]
            print(f"[INFO] Scanning for: {', '.join(labels)} "
                  f"({', '.join(self.allowed_extensions)}) in '{self.path}'")
        else:
            print(f"[INFO] Scanning all supported test types in '{self.path}'")

        if self.suite_dir:
            print(f"[INFO] Restricting scan to '/{self.suite_dir}/' subdirectories")

    def scan(self):
        tests = []

        for root, dirs, files in os.walk(self.path):
            # If suite_dir is specified, only process files inside that subdir
            if self.suite_dir:
                current_dir = os.path.basename(root)
                if current_dir != self.suite_dir:
                    continue

            for file in sorted(files):
                if is_test_file(file, self.allowed_extensions):
                    ext        = os.path.splitext(file)[1].lower()
                    file_path  = os.path.join(root, file)
                    suite_name = _infer_suite(file_path, self.path)

                    tests.append({
                        "name":     file,
                        "suite":    suite_name,
                        "source":   "filesystem",
                        "path":     file_path,
                        "language": SUPPORTED_EXTENSIONS.get(ext, "unknown"),
                    })

        if not tests:
            exts = (', '.join(self.allowed_extensions)
                    if self.allowed_extensions else "any supported type")
            print(f"[WARNING] No test files found in '{self.path}' "
                  f"matching filter: {exts}.")

        return tests
