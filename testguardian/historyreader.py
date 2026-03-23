"""
historyreader.py
----------------
Reads test execution history from multiple report files and normalises
them into per-test stats used as ML features.

Supported formats (auto-detected by extension):
    JUnit XML   — pytest, JUnit, surefire (.xml with <testsuites>/<testsuite> root)
    Robot XML   — Robot Framework output.xml (.xml with <robot> root)
    MTR         — MySQL Test Run .result or .summary files
    CSV         — normalised fallback (columns: test_name, result)

Usage:
    Single file : read_history("data/reports/run_01.xml")
    Directory   : read_history("data/reports/")
                  Scans all supported files in the directory (sorted by name
                  to preserve run order), reads each one, and aggregates
                  results across all runs per test before computing stats.

Returns dict keyed by test_name:
    {
        "test_login.py": {
            "pass_rate":    0.85,   # fraction of passing runs
            "fail_streak":  0,      # consecutive failures at tail
            "result_flips": 2,      # pass<->fail transitions
            "total_runs":   20
        }
    }
"""

import os
import csv
import xml.etree.ElementTree as ET


SUPPORTED_EXTENSIONS = {".xml", ".csv", ".result", ".summary"}


def read_history(path: str) -> dict:
    """
    Entry point. Accepts either a single report file or a directory of reports.
    Returns normalised stats per test, or empty dict on any unrecoverable issue.
    """
    if not path or not path.strip():
        return {}

    if not os.path.exists(path):
        print(f"[WARNING] History path not found: '{path}'. Skipping history features.")
        return {}

    if not os.access(path, os.R_OK):
        print(f"[WARNING] History path not readable: '{path}'. Skipping history features.")
        return {}

    if os.path.isdir(path):
        return _read_directory(path)

    return _read_single_file(path)


def _read_directory(directory: str) -> dict:
    """
    Scan directory recursively for all supported report files.
    Files are sorted by name to preserve run chronological order.
    Results are aggregated across all files before computing stats.
    """
    report_files = []
    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            if os.path.splitext(filename)[1].lower() in SUPPORTED_EXTENSIONS:
                report_files.append(os.path.join(root, filename))

    if not report_files:
        print(f"[WARNING] No supported report files found in '{directory}'. "
              f"Supported: {SUPPORTED_EXTENSIONS}. Skipping history features.")
        return {}

    print(f"[INFO] Found {len(report_files)} report file(s) in '{directory}'. Aggregating...")

    # Accumulate raw results per test across all runs
    # { test_name: ["pass", "fail", "pass", ...] }
    aggregated = {}
    files_read = 0

    for filepath in report_files:
        try:
            raw = _read_raw(filepath)
            for test_name, results in raw.items():
                aggregated.setdefault(test_name, []).extend(results)
            files_read += 1
        except Exception as e:
            print(f"[WARNING] Skipping '{filepath}': {e}")
            continue

    if files_read == 0:
        print(f"[WARNING] No report files could be read from '{directory}'. "
              f"Skipping history features.")
        return {}

    print(f"[INFO] Successfully read {files_read}/{len(report_files)} report file(s).")

    return {name: _compute_stats(results) for name, results in aggregated.items()}


def _read_single_file(path: str) -> dict:
    """Read and parse a single report file. Returns normalised stats per test."""
    if os.path.getsize(path) == 0:
        print(f"[WARNING] Report file is empty: '{path}'. Skipping.")
        return {}
    try:
        raw = _read_raw(path)
        return {name: _compute_stats(results) for name, results in raw.items()}
    except Exception as e:
        print(f"[WARNING] Failed to parse '{path}': {e}. Skipping history features.")
        return {}


def _read_raw(path: str) -> dict:
    """
    Read a single file and return raw results per test as:
        { test_name: ["pass", "fail", ...] }
    Used by both single file and directory aggregation paths.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".xml":
        return _read_xml_raw(path)
    elif ext == ".csv":
        return _read_csv_raw(path)
    elif ext in (".result", ".summary"):
        return _read_mtr_raw(path)
    else:
        # Unknown extension — try XML first, fall back to CSV
        try:
            return _read_xml_raw(path)
        except ET.ParseError:
            return _read_csv_raw(path)


def _compute_stats(results: list) -> dict:
    """Compute normalised stats from an ordered list of 'pass'/'fail' strings."""
    total = len(results)
    if total == 0:
        return {"pass_rate": 0.0, "fail_streak": 0, "result_flips": 0, "total_runs": 0}

    passes = results.count("pass")
    pass_rate = round(passes / total, 4)

    fail_streak = 0
    for r in reversed(results):
        if r == "fail":
            fail_streak += 1
        else:
            break

    result_flips = sum(
        1 for i in range(1, total)
        if results[i] != results[i - 1]
    )

    return {
        "pass_rate":    pass_rate,
        "fail_streak":  fail_streak,
        "result_flips": result_flips,
        "total_runs":   total
    }


def _read_xml_raw(path: str) -> dict:
    """Parse JUnit or Robot Framework XML — returns raw results dict."""
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        raise ET.ParseError(f"Malformed XML in '{path}': {e}")

    root = tree.getroot()

    if root.tag == "robot":
        return _parse_robot_xml_raw(root, path)

    if root.tag in ("testsuites", "testsuite"):
        return _parse_junit_xml_raw(root, path)

    print(f"[WARNING] Unrecognised XML root tag '<{root.tag}>' in '{path}'. "
          f"Expected <robot>, <testsuite>, or <testsuites>. Skipping.")
    return {}


def _parse_junit_xml_raw(root, path: str) -> dict:
    """Parse JUnit/pytest XML — returns { test_name: ['pass'|'fail'] }."""
    raw = {}
    suites = root.findall(".//testsuite") or [root]
    for suite in suites:
        for tc in suite.findall("testcase"):
            name = (tc.get("classname", "") + "." + tc.get("name", "")).strip(".")
            if not name:
                continue
            result = "fail" if (
                tc.find("failure") is not None or tc.find("error") is not None
            ) else "pass"
            raw.setdefault(name, []).append(result)

    if not raw:
        print(f"[WARNING] No test cases found in JUnit XML '{path}'. Check report format.")
    return raw


def _parse_robot_xml_raw(root, path: str) -> dict:
    """Parse Robot Framework output.xml — returns { test_name: ['pass'|'fail'] }."""
    raw = {}
    for test in root.findall(".//test"):
        name = test.get("name", "")
        status_el = test.find("status")
        if not name or status_el is None:
            continue
        result = "pass" if status_el.get("status", "").upper() == "PASS" else "fail"
        raw.setdefault(name, []).append(result)

    if not raw:
        print(f"[WARNING] No tests found in Robot XML '{path}'. Check report format.")
    return raw


def _read_mtr_raw(path: str) -> dict:
    """Parse MTR .result/.summary — returns { test_name: ['pass'|'fail'] }."""
    raw = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            name = parts[0]
            status = parts[-1].lower()
            if status not in ("pass", "fail"):
                continue
            raw.setdefault(name, []).append(status)

    if not raw:
        print(f"[WARNING] No results found in MTR file '{path}'. Check report format.")
    return raw


def _read_csv_raw(path: str) -> dict:
    """Parse CSV (columns: test_name, result) — returns { test_name: ['pass'|'fail'] }."""
    raw = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            print(f"[WARNING] CSV '{path}' is empty or has no headers.")
            return {}

        missing = {"test_name", "result"} - {c.lower() for c in reader.fieldnames}
        if missing:
            raise ValueError(
                f"CSV '{path}' missing required columns: {missing}. "
                f"Found: {list(reader.fieldnames)}"
            )

        rows = list(reader)
        if "run_id" in {c.lower() for c in (reader.fieldnames or [])}:
            try:
                rows = sorted(rows, key=lambda r: int(r.get("run_id", 0)))
            except ValueError:
                pass

        for row in rows:
            name = row.get("test_name", "").strip()
            result = row.get("result", "").strip().lower()
            if not name or result not in ("pass", "fail"):
                continue
            raw.setdefault(name, []).append(result)

    if not raw:
        print(f"[WARNING] No valid rows in CSV '{path}'. Check column values.")
    return raw
