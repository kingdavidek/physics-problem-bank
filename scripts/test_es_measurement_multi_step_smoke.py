"""Smoke checks for measurement multi-step pilot content."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _generator_topic_options, _normalize_generator_mode, app  # noqa: E402
from generators.eursc.s1_science_lab import (  # noqa: E402
    eursc_science_measurement,
    eursc_science_measurement_variants,
)
from generators.shared.variant_utils import MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE  # noqa: E402
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]

DISCLOSE_RE = re.compile(
    r"\b(your diet|have you ever|tell us about your|describe your eating|"
    r"are you allergic|what are you allergic|your body|when did you|"
    r"have you started|are you attracted|your period|have you had sex|"
    r"do you use contraception|your partner|are you gay|your sexuality|"
    r"have you been pregnant|are you pregnant|describe your body|"
    r"do you smoke|have you smoked|do you vape|are you addicted|"
    r"what do you use|list your medication|are you depressed|"
    r"how many hours do you sleep|describe your mood|"
    r"who in your family is ill|have you been ill|"
    r"how do you feel|describe your hunger|are you dizzy|"
    r"map your body|your heartbeat|do you wear glasses)\b",
    re.I,
)

DIFFS = ("foundational", "intermediate", "difficult")


def _blob(problem):
    return " ".join(
        [
            str(problem.get("question") or ""),
            str(problem.get("solution") or ""),
            str(problem.get("hint") or ""),
        ]
    )


def test_measurement_registers_multi_step_mode():
    key = ("eursc", "science", "measurement")
    assert topic_mode_capabilities(*key) == (
        "standard",
        MULTI_STEP_MODE,
        SITUATIONAL_MULTI_STEP_MODE,
    )
    assert _normalize_generator_mode(*key, MULTI_STEP_MODE) == MULTI_STEP_MODE
    assert (
        _normalize_generator_mode(*key, SITUATIONAL_MULTI_STEP_MODE)
        == SITUATIONAL_MULTI_STEP_MODE
    )
    row = next(
        item
        for item in _generator_topic_options()
        if (item["level"], item["subject"], item["slug"]) == key
    )
    assert row["modes"] == (
        "standard",
        MULTI_STEP_MODE,
        SITUATIONAL_MULTI_STEP_MODE,
    )


def test_measurement_multi_step_variants_are_grader_ready():
    for difficulty in DIFFS:
        variants = eursc_science_measurement_variants(difficulty, MULTI_STEP_MODE)
        assert len(variants) >= 3, (difficulty, len(variants))
        names = [fn.__name__ for fn in variants]
        assert len(set(names)) == len(names), (difficulty, names)
        for fn in variants:
            assert getattr(fn, "_kind", "") == "number_fields", fn.__name__
            assert getattr(fn, "_randomizable", False) is True, fn.__name__
            problem = fn()
            assert problem.get("answer_type") == "number_fields", fn.__name__
            assert problem.get("correct_answer_raw"), fn.__name__
            assert int(problem.get("marks") or 0) >= 2, fn.__name__
            blob = _blob(problem)
            assert not DISCLOSE_RE.search(blob), fn.__name__
            assert "fictional" in blob.lower(), fn.__name__
            via_generate = eursc_science_measurement(
                difficulty, MULTI_STEP_MODE, variant_name=fn.__name__
            )
            assert via_generate.get("answer_type") == "number_fields", fn.__name__


def test_measurement_multi_step_solutions_link_parts():
    problem = eursc_science_measurement(
        "intermediate",
        MULTI_STEP_MODE,
        variant_name="measurement_intermediate_ms_scale_convert_compare",
    )
    solution = problem.get("solution") or ""
    assert "(i)" in solution and "(ii)" in solution and "(iii)" in solution
    types = problem.get("answer_field_types") or []
    assert types == ["number", "number", "number"] or not types


def test_measurement_difficult_diagnose_uses_existing_mcq_field():
    problem = eursc_science_measurement(
        "difficult",
        MULTI_STEP_MODE,
        variant_name="measurement_difficult_ms_precision_summary",
    )
    assert problem.get("answer_field_types") == ["number", "number", "mcq"]
    options = problem.get("answer_field_options")
    assert options and options[2]
    assert "precise but not accurate" in options[2]


def test_measurement_multi_step_randomization():
    fn = next(
        f
        for f in eursc_science_measurement_variants("foundational", MULTI_STEP_MODE)
        if f.__name__ == "measurement_foundational_ms_kilo_convert_compare"
    )
    stems = set()
    for seed in range(20):
        random.seed(seed)
        stems.add(fn()["question"])
    assert len(stems) > 1


def test_measurement_same_variant_is_pinned():
    name = "measurement_foundational_ms_kilo_convert_compare"
    random.seed(7)
    first = eursc_science_measurement(
        "foundational", MULTI_STEP_MODE, variant_name=name
    )
    random.seed(7)
    second = eursc_science_measurement(
        "foundational", MULTI_STEP_MODE, variant_name=name
    )
    assert first["question"] == second["question"]
    assert first["correct_answer_raw"] == second["correct_answer_raw"]


def test_measurement_standard_matrix_unchanged():
    cfg = SCIENCE["measurement"]
    vf = cfg["variants_func"]
    for difficulty in DIFFS:
        standard = vf(difficulty, "standard")
        assert len(standard) == 5, difficulty
        lesson = vf(difficulty, "lesson")
        practice_names = {fn.__name__ for fn in standard}
        assert all(fn.__name__ in practice_names for fn in standard)
        assert len(lesson) > len(standard)
        advanced_names = {
            fn.__name__
            for fn in vf(difficulty, MULTI_STEP_MODE)
        }
        advanced_names.update(
            fn.__name__ for fn in vf(difficulty, SITUATIONAL_MULTI_STEP_MODE)
        )
        assert practice_names.isdisjoint(advanced_names), difficulty


def test_measurement_multi_step_api_generate():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "measurement",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
    assert response.status_code == 200, response.data[:400]
    payload = response.get_json()
    assert payload["ok"] is True
    problem = payload["problem"]
    assert problem["mode"] == MULTI_STEP_MODE
    assert problem["topic"] == "measurement"
    assert problem.get("answer_type") == "number_fields"


def main():
    test_measurement_registers_multi_step_mode()
    test_measurement_multi_step_variants_are_grader_ready()
    test_measurement_multi_step_solutions_link_parts()
    test_measurement_difficult_diagnose_uses_existing_mcq_field()
    test_measurement_multi_step_randomization()
    test_measurement_same_variant_is_pinned()
    test_measurement_standard_matrix_unchanged()
    test_measurement_multi_step_api_generate()
    print("Measurement multi-step pilot checks passed.")


if __name__ == "__main__":
    main()
