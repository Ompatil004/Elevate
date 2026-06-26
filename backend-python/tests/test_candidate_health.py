"""
test_candidate_health.py
Phase 4 -- Regression Gate for Candidate Generation Health.

Reads logs/candidate_generation_metrics.jsonl and asserts that key health
metrics have not regressed below acceptable thresholds.

Run this after any change to candidate_generator.py or nutrition_rules.yaml:

    pytest backend-python/tests/test_candidate_health.py -v

If any assertion fails, the change likely reintroduced the lunch-starvation
issue. Review the JSONL file to identify the top rejection reason.
"""

import json
import pathlib
import statistics

import pytest

# Path is relative to the project root (backend-python/).
_BACKEND_ROOT = pathlib.Path(__file__).parent.parent
METRICS_FILE  = _BACKEND_ROOT / "logs" / "candidate_generation_metrics.jsonl"

THRESHOLDS = {
    "lunch_acceptance_rate_min": 0.10,
    "fallback_usage_max":        0.05,
    "generation_time_ms_max":    500,
}


def _load_metrics() -> list:
    if not METRICS_FILE.exists():
        pytest.skip(
            f"Metrics file not found: {METRICS_FILE}\n"
            "Run the nutrition engine first to generate metrics."
        )
    records = []
    with open(METRICS_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if not records:
        pytest.skip("Metrics file is empty -- no data to assert against.")
    return records


def test_lunch_acceptance_rate():
    records = [r for r in _load_metrics() if r.get("meal_type") == "lunch"]
    if not records:
        pytest.skip("No lunch records in metrics file yet.")
    rates = [r["acceptance_rate"] for r in records]
    avg   = statistics.mean(rates)
    med   = statistics.median(rates)
    threshold = THRESHOLDS["lunch_acceptance_rate_min"]
    assert avg >= threshold, (
        f"Lunch acceptance rate avg={avg:.2%} is below threshold {threshold:.0%}.\n"
        f"  Median: {med:.2%}\n"
        f"  Worst:  {min(rates):.2%}\n"
        f"  n={len(rates)} records\n"
        f"  Hint: check logs/candidate_generation_metrics.jsonl for top rejection causes."
    )


def test_fallback_usage_rate():
    records    = _load_metrics()
    fallback_n = sum(1 for r in records if r.get("used_fallback"))
    total      = len(records)
    rate       = fallback_n / max(total, 1)
    threshold  = THRESHOLDS["fallback_usage_max"]
    assert rate <= threshold, (
        f"Fallback usage {rate:.2%} ({fallback_n}/{total} meals) exceeds threshold {threshold:.0%}.\n"
        "Hint: check template-driven generation and composition rules."
    )


def test_generation_time():
    records   = _load_metrics()
    times     = [r.get("generation_time_ms", 0) for r in records]
    worst     = max(times) if times else 0
    threshold = THRESHOLDS["generation_time_ms_max"]
    assert worst <= threshold, (
        f"Worst generation time {worst} ms exceeds threshold {threshold} ms.\n"
        f"  Average: {statistics.mean(times):.0f} ms\n"
        "  Hint: check _get_dynamic_candidates for O(n^2) loops."
    )


def test_metrics_file_has_recent_records():
    records = _load_metrics()
    assert len(records) >= 4, (
        f"Only {len(records)} records found -- run a full day of meal generation first."
    )


def test_all_meal_types_represented():
    records     = _load_metrics()
    found_types = {r.get("meal_type") for r in records}
    expected    = {"breakfast", "lunch", "dinner", "snack"}
    missing     = expected - found_types
    assert not missing, (
        f"Missing records for meal types: {missing}\n"
        "Ensure a full day of meal generation was run."
    )
