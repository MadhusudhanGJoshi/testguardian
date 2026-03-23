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
    ".robot": lambda f: True,
    ".mtr":   lambda f: True,
    ".test":  lambda f: True,
}


def _normalise_filter(filter_param) -> set:
    """
    Normalise the filter param from config into a set of lowercase extensions.
    Accepts a single string or a list of strings.
    Returns empty set if no filter specified (means scan all).

    Examples:
        ".mtr"              -> {".mtr"}
        "mtr"               -> {".mtr"}
        [".java", ".xml"]   -> {".java", ".xml"}
        None                -> set()
    """
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
            print(f"[WARNING] Filter extension '{ext}' is not a recognised test type. "
                  f"Supported: {list(SUPPORTED_EXTENSIONS.keys())}. It will be ignored.")
        else:
            normalised.add(ext)

    return normalised


def is_test_file(filename, allowed_extensions=None):
    """
    Returns True if filename is a recognised test file.
    If allowed_extensions is provided (non-empty set), only those extensions pass.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        return False

    if allowed_extensions and ext not in allowed_extensions:
        return False

    matcher = TEST_PATTERNS.get(ext)
    return matcher(filename) if matcher else False


class FileSystemSource(TestSource):
    def __init__(self, path, filter=None):
        """
        Parameters:
            path   : str            — directory to scan
            filter : str or list    — file extension(s) to include
                                      e.g. ".mtr", [".java", ".xml"]
                                      If omitted, all supported types are scanned.
        """
        if not path:
            raise ValueError("'source.params.path' must not be empty in config.yaml.")

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Test source path not found: '{path}'. "
                f"Check 'source.params.path' in config.yaml."
            )

        if not os.path.isdir(path):
            raise NotADirectoryError(
                f"Test source path is not a directory: '{path}'."
            )

        self.path = path
        self.allowed_extensions = _normalise_filter(filter)

        if self.allowed_extensions:
            labels = [SUPPORTED_EXTENSIONS[e] for e in self.allowed_extensions]
            print(f"[INFO] Scanning for: {', '.join(labels)} "
                  f"({', '.join(self.allowed_extensions)}) in '{self.path}'")
        else:
            print(f"[INFO] Scanning all supported test types in '{self.path}'")

    def scan(self):
        tests = []

        for root, _, files in os.walk(self.path):
            for file in files:
                if is_test_file(file, self.allowed_extensions):
                    ext = os.path.splitext(file)[1].lower()
                    tests.append({
                        "name": file,
                        "source": "filesystem",
                        "path": os.path.join(root, file),
                        "language": SUPPORTED_EXTENSIONS.get(ext, "unknown"),
                    })

        if not tests:
            exts = (', '.join(self.allowed_extensions)
                    if self.allowed_extensions
                    else "any supported type")
            print(f"[WARNING] No test files found in '{self.path}' "
                  f"matching filter: {exts}.")

        return tests
