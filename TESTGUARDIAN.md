# TestGuardian

An automated ML pipeline that helps software teams govern and maintain their growing test base — identifying tests that are flaky, obsolete, unused or stable.

---

## The Problem

As software products grow, test suites accumulate debt silently:

- **Flaky tests** intermittently fail, eroding CI/CD confidence and wasting engineer time
- **Obsolete tests** haven't caught a bug in months but still run every night
- **Unused tests** are dead code — large, untouched, contributing nothing
- **Stable tests** are the ones worth keeping — actively catching real issues

Most teams know this problem exists. Few have the time or tooling to act on it systematically.

---

## How It Works

```
Test Source + Execution History → Agent → Feature Extraction → Random Forest → Predict → Recommend → SME Feedback ↻
```

TestGuardian scans your test base, reads your execution history, extracts signals from each test file, and runs them through a Random Forest classifier to predict the health of every test. Each prediction comes with a concrete recommendation — **keep**, **remove**, or **investigate** — ready for expert review.

The feedback loop means the model gets smarter over time as your team corrects its predictions.

---

## Supported Frameworks

TestGuardian works out of the box with:

| Framework | Extension |
|---|---|
| pytest / unittest | `.py` |
| JUnit | `.java` |
| Jest / Mocha | `.js`, `.ts` |
| Robot Framework | `.robot` |
| MTR (MySQL Test Run) | `.mtr`, `.test` |

> Customisable to any test type — provided there is a reasonable amount of test execution history for the Random Forest classifier to make meaningful predictions.

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/MadhusudhanGJoshi/testguardian.git
cd testguardian

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the model
PYTHONPATH=. python scripts/retrain_model.py

# 4. Run against your test base
PYTHONPATH=. python testguardian.py \
  --source ./your-tests/ \
  --type .py \
  --history ./your-reports/
```

### Example output

```
======================================================================
  TestGuardian Report
  Source  : ./sample_tests
  Type    : .py
  History : provided
======================================================================

  Total tests scanned : 5
  Predictions         : flaky: 3 | stable: 1 | obsolete: 1
  Actions             : remove: 3 | keep: 1 | investigate: 1

  Test                        Language    Prediction  Confidence  Action
  --------------------------------------------------------------------
  test_login.py               pytest      flaky       80%         remove
  test_legacy_feature.py      pytest      obsolete    91%         remove
  test_db_connection.py       pytest      flaky       74%         remove
  test_innodb_basic.py        pytest      stable      88%         keep
  test_user_checkout.py       pytest      flaky       69%         investigate

  3 test(s) flagged as pending_expert_review
======================================================================
```

---

## CLI Reference

```bash
PYTHONPATH=. python testguardian.py [options]

  --source      Path to your test base directory          (required)
  --type        File extension to scan (.py .java .mtr …) (optional — all types if omitted)
  --history     Path to execution history reports          (optional)
  --suite-dir   Subdirectory name for suite structure      (optional — e.g. 't' for MySQL MTR)
  --output      Directory to save JSON report              (default: reports/)
  --format      Output format: console | json | both       (default: both)
```

### MySQL MTR example

```bash
PYTHONPATH=. python testguardian.py \
  --source mysql-test/suite/ \
  --type .test \
  --suite-dir t \
  --history data/reports/mtr/ \
  --format both
```

---

## Execution History Formats

TestGuardian auto-detects the format of your execution history:

| Format | Source |
|---|---|
| JUnit XML | pytest, JUnit, surefire |
| Robot Framework XML | Robot Framework output.xml |
| MTR `.result` / `.summary` | MySQL Test Run |
| CSV | normalised fallback |

Point `--history` at a **directory of multiple run reports** and TestGuardian aggregates results across all runs before computing predictions.

---

## Expert Feedback Loop

```bash
# Correct a prediction
PYTHONPATH=. python scripts/add_feedback.py --test test_login.py --label stable

# When enough feedback accumulates — rebuild training data
PYTHONPATH=. python scripts/build_training_data.py

# Retrain the model on real labelled data
PYTHONPATH=. python scripts/retrain_model.py
```

---

## ⚠️ Pilot Notice

**This is a pilot release.**

Extensive testing is currently in progress across multiple test frameworks and at-scale test suites. Scalability improvements and additional features are planned for future releases.

Not recommended for production use yet. Feedback and contributions are very welcome.

→ **Pilot release:** https://github.com/MadhusudhanGJoshi/testguardian/releases/tag/v0.1-pilot

---

## What's Coming Next

- Extensive test coverage (unit, integration, negative, scale)
- Real labelled training data pipeline from expert feedback
- Grafana dashboard integration
- Git integration for commit frequency signals
- Multithreading for large test suites

---

## Author

**Madhusudhan G Joshi**
→ https://www.linkedin.com/in/madhusudhan-joshi
