# Reproducibility Package Guide

## Goal
Ensure paper/demo claims are reproducible with fixed data, fixed code revision, and repeatable commands.

## Package Contents
1. Code revision metadata
- git commit hash
- branch
- timestamp

2. Environment metadata
- OS
- Python version
- Node version
- package lock files

3. Dataset metadata
- dataset filenames
- row counts
- checksum hashes

4. Experiment metadata
- profile inputs used for generation
- model settings and thresholds
- output artifacts and summary metrics

## Recommended Folder Structure
- `docs/reproducibility/manifest.json`
- `docs/reproducibility/inputs/*.json`
- `docs/reproducibility/outputs/*.json`
- `docs/reproducibility/charts/*.png`

## Minimal Command Protocol
1. Backend Python syntax validation:
- `python -m py_compile backend-python/server.py`

2. Node contract QA:
- `cd backend-node && npm test`

3. Frontend quality gate:
- `cd frontend && npm test`

4. Python contract tests:
- `python -m unittest discover -s backend-python/tests -p "test_*.py"`

## Reporting Template
- Baseline date and environment
- command list used
- generated outputs with hashes
- observed KPI values
- deviations from expected values

## Sign-off Checklist
- [ ] Commands executed without critical errors
- [ ] Artifacts saved with timestamp
- [ ] Input profiles archived
- [ ] Output files checksummed
- [ ] Reviewer verification complete
