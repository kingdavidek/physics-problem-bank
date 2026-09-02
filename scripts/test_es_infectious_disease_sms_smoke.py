"""Smoke checks for infectious_disease situational multi-step pilot content."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _generator_topic_options, _normalize_generator_mode, app  # noqa: E402
from generators.eursc.s2_health import (  # noqa: E402
    eursc_science_infectious_disease,
    eursc_science_infectious_disease_variants,
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


def test_infectious_disease_registers_situational_mode():
    key = ("eursc", "science", "infectious_disease")
    assert topic_mode_capabilities(*key) == (
        "standard",
        SITUATIONAL_MULTI_STEP_MODE,
    )
    assert (
        _normalize_generator_mode(*key, SITUATIONAL_MULTI_STEP_MODE)
        == SITUATIONAL_MULTI_STEP_MODE
    )
    assert _normalize_generator_mode(*key, MULTI_STEP_MODE) == "standard"
    row = next(
        item
        for item in _generator_topic_options()
        if (item["level"], item["subject"], item["slug"]) == key
    )
    assert row["modes"] == ("standard", SITUATIONAL_MULTI_STEP_MODE)


def test_infectious_disease_sms_variants_are_grader_ready():
    saw_order_or_pick = False
    for difficulty in DIFFS:
        variants = eursc_science_infectious_disease_variants(
            difficulty, SITUATIONAL_MULTI_STEP_MODE
        )
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
            types = problem.get("answer_field_types") or []
            if any(kind in types for kind in ("order", "pick")):
                saw_order_or_pick = True
            blob = _blob(problem)
            assert not DISCLOSE_RE.search(blob), (fn.__name__, blob[:180])
            assert "fictional" in blob.lower(), fn.__name__
            via_generate = eursc_science_infectious_disease(
                difficulty, SITUATIONAL_MULTI_STEP_MODE, variant_name=fn.__name__
            )
            assert via_generate.get("answer_type") == "number_fields", fn.__name__
    assert saw_order_or_pick


def test_infectious_disease_sms_solutions_link_parts():
    problem = eursc_science_infectious_disease(
        "intermediate",
        SITUATIONAL_MULTI_STEP_MODE,
        variant_name="infectious_disease_intermediate_sms_outbreak_next_hygiene",
    )
    solution = problem.get("solution") or ""
    assert "(i)" in solution and "(ii)" in solution and "(iii)" in solution
    assert problem.get("answer_field_types") == ["number", "number", "pick"]


def test_infectious_disease_sms_randomization():
    fn = next(
        f
        for f in eursc_science_infectious_disease_variants(
            "foundational", SITUATIONAL_MULTI_STEP_MODE
        )
        if f.__name__ == "infectious_disease_foundational_sms_token_double_safeguard"
    )
    stems = set()
    for seed in range(20):
        random.seed(seed)
        stems.add(fn()["question"])
    assert len(stems) > 1


def test_infectious_disease_same_variant_is_pinned():
    name = "infectious_disease_foundational_sms_token_double_safeguard"
    random.seed(7)
    first = eursc_science_infectious_disease(
        "foundational", SITUATIONAL_MULTI_STEP_MODE, variant_name=name
    )
    random.seed(7)
    second = eursc_science_infectious_disease(
        "foundational", SITUATIONAL_MULTI_STEP_MODE, variant_name=name
    )
    assert first["question"] == second["question"]
    assert first["correct_answer_raw"] == second["correct_answer_raw"]


def test_infectious_disease_standard_matrix_unchanged():
    cfg = SCIENCE["infectious_disease"]
    vf = cfg["variants_func"]
    for difficulty in DIFFS:
        standard = vf(difficulty, "standard")
        assert len(standard) == 5, difficulty
        lesson = vf(difficulty, "lesson")
        practice_names = {fn.__name__ for fn in standard}
        assert all(fn.__name__ in practice_names for fn in standard)
        assert len(lesson) > len(standard)
        advanced_names = {
            fn.__name__ for fn in vf(difficulty, SITUATIONAL_MULTI_STEP_MODE)
        }
        assert practice_names.isdisjoint(advanced_names), difficulty
        assert vf(difficulty, MULTI_STEP_MODE) == []


def test_infectious_disease_sms_api_generate():
    with app.test_client() as client:
        response = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "infectious_disease",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
    assert response.status_code == 200, response.data[:400]
    payload = response.get_json()
    assert payload["ok"] is True
    problem = payload["problem"]
    assert problem["mode"] == SITUATIONAL_MULTI_STEP_MODE
    assert problem["topic"] == "infectious_disease"
    assert problem.get("answer_type") == "number_fields"


def main():
    test_infectious_disease_registers_situational_mode()
    test_infectious_disease_sms_variants_are_grader_ready()
    test_infectious_disease_sms_solutions_link_parts()
    test_infectious_disease_sms_randomization()
    test_infectious_disease_same_variant_is_pinned()
    test_infectious_disease_standard_matrix_unchanged()
    test_infectious_disease_sms_api_generate()
    print("Infectious-disease situational multi-step pilot checks passed.")


if __name__ == "__main__":
    main()
