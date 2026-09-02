"""Smoke checks for movement multi-step pilot content."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _generator_topic_options, _normalize_generator_mode, app  # noqa: E402
from generators.eursc.s1_sports import (  # noqa: E402
    eursc_science_movement,
    eursc_science_movement_variants,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
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


def test_movement_registers_advanced_modes():
    key = ("eursc", "science", "movement")
    assert MULTI_STEP_MODE in topic_mode_capabilities(*key)
    assert SITUATIONAL_MULTI_STEP_MODE in topic_mode_capabilities(*key)
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
    assert row["modes"] == ("standard", MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)


def test_movement_multi_step_variants_are_grader_ready():
    for difficulty in DIFFS:
        variants = eursc_science_movement_variants(difficulty, MULTI_STEP_MODE)
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
            via_generate = eursc_science_movement(
                difficulty, MULTI_STEP_MODE, variant_name=fn.__name__
            )
            assert via_generate.get("answer_type") == "number_fields", fn.__name__


def test_movement_multi_step_solutions_link_parts():
    problem = eursc_science_movement(
        "intermediate",
        MULTI_STEP_MODE,
        variant_name="movement_intermediate_ms_minute_run",
    )
    solution = problem.get("solution") or ""
    assert "(i)" in solution and "(ii)" in solution and "(iii)" in solution


def test_movement_multi_step_randomization():
    fn = next(
        f
        for f in eursc_science_movement_variants("foundational", MULTI_STEP_MODE)
        if f.__name__ == "movement_foundational_ms_speed_extrapolate"
    )
    random.seed(1)
    first = fn()["question"]
    random.seed(2)
    second = fn()["question"]
    assert first != second


def test_movement_same_variant_is_pinned():
    name = "movement_foundational_ms_speed_extrapolate"
    random.seed(7)
    first = eursc_science_movement(
        "foundational", MULTI_STEP_MODE, variant_name=name
    )
    random.seed(7)
    second = eursc_science_movement(
        "foundational", MULTI_STEP_MODE, variant_name=name
    )
    assert first["question"] == second["question"]
    assert first["correct_answer_raw"] == second["correct_answer_raw"]


def test_movement_standard_matrix_unchanged():
    cfg = SCIENCE["movement"]
    vf = cfg["variants_func"]
    for difficulty in DIFFS:
        standard = vf(difficulty, "standard")
        assert len(standard) == 5, difficulty
        lesson = vf(difficulty, "lesson")
        practice_names = {fn.__name__ for fn in standard}
        assert all(fn.__name__ in practice_names for fn in standard)
        assert len(lesson) > len(standard)


def test_movement_multi_step_api_generate():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "movement",
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
    assert problem["topic"] == "movement"
    assert problem.get("answer_type") == "number_fields"


def main():
    test_movement_registers_advanced_modes()
    test_movement_multi_step_variants_are_grader_ready()
    test_movement_multi_step_solutions_link_parts()
    test_movement_multi_step_randomization()
    test_movement_same_variant_is_pinned()
    test_movement_standard_matrix_unchanged()
    test_movement_multi_step_api_generate()
    print("Movement multi-step pilot checks passed.")


if __name__ == "__main__":
    main()
