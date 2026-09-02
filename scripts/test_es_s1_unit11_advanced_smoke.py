"""Smoke checks for S1 Unit 1.1 advanced Practice cells (Batch 2.1)."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _normalize_generator_mode, app  # noqa: E402
from generators.eursc.s1_science_lab import (  # noqa: E402
    eursc_science_measurement,
    eursc_science_measurement_variants,
    eursc_science_science_lab,
    eursc_science_science_lab_variants,
    eursc_science_what_is_science,
    eursc_science_what_is_science_variants,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
BOTH_ADVANCED = (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)

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

STANDARD_SNAPSHOT = {
    "what_is_science": {
        "foundational": (
            "what_is_science_foundational_mcq_authority",
            "what_is_science_foundational_keyword_evidence_word",
            "what_is_science_foundational_number_mean_len",
            "what_is_science_foundational_order_share_steps",
            "what_is_science_foundational_pick_not_science",
        ),
        "intermediate": (
            "what_is_science_intermediate_mcq_book",
            "what_is_science_intermediate_keyword_reproducible",
            "what_is_science_intermediate_number_mean_time",
            "what_is_science_intermediate_order_enquiry",
            "what_is_science_intermediate_pick_public",
        ),
        "difficult": (
            "what_is_science_difficult_mcq_anecdote",
            "what_is_science_difficult_keyword_hypothesis_word",
            "what_is_science_difficult_number_groups",
            "what_is_science_difficult_order_check_chain",
            "what_is_science_difficult_pick_method_keep",
        ),
    },
    "science_lab": {
        "foundational": (
            "science_lab_foundational_mcq_bench_thermo",
            "science_lab_foundational_keyword_independent_word",
            "science_lab_foundational_number_mean_temp",
            "science_lab_foundational_order_plan_order",
            "science_lab_foundational_pick_safety_two",
        ),
        "intermediate": (
            "science_lab_intermediate_mcq_bench_heat",
            "science_lab_intermediate_keyword_dependent_word",
            "science_lab_intermediate_number_mean_time",
            "science_lab_intermediate_order_draw_order",
            "science_lab_intermediate_pick_reduce_error",
        ),
        "difficult": (
            "science_lab_difficult_mcq_control_list",
            "science_lab_difficult_keyword_control_word",
            "science_lab_difficult_number_range_lab",
            "science_lab_difficult_order_full_plan",
            "science_lab_difficult_pick_three_vars",
        ),
    },
}

LESSON_COUNT_SNAPSHOT = {
    "what_is_science": {"foundational": 11, "intermediate": 11, "difficult": 10},
    "science_lab": {"foundational": 11, "intermediate": 11, "difficult": 10},
}

CELLS = (
    (
        "measurement",
        SITUATIONAL_MULTI_STEP_MODE,
        DIFFS,
        eursc_science_measurement,
        eursc_science_measurement_variants,
    ),
    (
        "what_is_science",
        MULTI_STEP_MODE,
        ("intermediate", "difficult"),
        eursc_science_what_is_science,
        eursc_science_what_is_science_variants,
    ),
    (
        "what_is_science",
        SITUATIONAL_MULTI_STEP_MODE,
        DIFFS,
        eursc_science_what_is_science,
        eursc_science_what_is_science_variants,
    ),
    (
        "science_lab",
        MULTI_STEP_MODE,
        DIFFS,
        eursc_science_science_lab,
        eursc_science_science_lab_variants,
    ),
    (
        "science_lab",
        SITUATIONAL_MULTI_STEP_MODE,
        DIFFS,
        eursc_science_science_lab,
        eursc_science_science_lab_variants,
    ),
)

PINNED = (
    (
        eursc_science_measurement,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "measurement_foundational_sms_harbour_km_compare",
    ),
    (
        eursc_science_what_is_science,
        MULTI_STEP_MODE,
        "intermediate",
        "what_is_science_intermediate_ms_count_evidence_then_reproduce",
    ),
    (
        eursc_science_what_is_science,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "what_is_science_foundational_sms_club_claim_then_test",
    ),
    (
        eursc_science_science_lab,
        MULTI_STEP_MODE,
        "foundational",
        "science_lab_foundational_ms_temps_mean_then_instrument",
    ),
    (
        eursc_science_science_lab,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "science_lab_foundational_sms_heat_water_mean_then_thermo",
    ),
)


def _blob(problem):
    return " ".join(
        [
            str(problem.get("question") or ""),
            str(problem.get("solution") or ""),
            str(problem.get("hint") or ""),
        ]
    )


def test_unit11_registers_supported_modes():
    both = ("standard",) + BOTH_ADVANCED
    for slug in ("measurement", "what_is_science", "science_lab"):
        key = ("eursc", "science", slug)
        assert topic_mode_capabilities(*key) == both, slug
        assert _normalize_generator_mode(*key, MULTI_STEP_MODE) == MULTI_STEP_MODE
        assert (
            _normalize_generator_mode(*key, SITUATIONAL_MULTI_STEP_MODE)
            == SITUATIONAL_MULTI_STEP_MODE
        )


def test_what_is_science_foundational_ms_stays_empty():
    vf = eursc_science_what_is_science_variants
    assert vf("foundational", MULTI_STEP_MODE) == []
    try:
        eursc_science_what_is_science("foundational", MULTI_STEP_MODE)
    except ValueError as exc:
        assert "No multi_step variants" in str(exc)
    else:
        raise AssertionError("foundational what_is_science multi_step leaked")
    key = ("eursc", "science", "what_is_science")
    assert (
        _normalize_generator_mode(
            *key, MULTI_STEP_MODE, difficulty="foundational"
        )
        == "standard"
    )
    assert (
        _normalize_generator_mode(
            *key, MULTI_STEP_MODE, difficulty="intermediate"
        )
        == MULTI_STEP_MODE
    )


def test_unit11_cells_are_grader_ready():
    saw_order_or_pick = False
    for slug, mode, diffs, generate, variants in CELLS:
        for difficulty in diffs:
            pool = variants(difficulty, mode)
            assert len(pool) >= 3, (slug, mode, difficulty, len(pool))
            names = [fn.__name__ for fn in pool]
            assert len(set(names)) == len(names), (slug, mode, difficulty, names)
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            for fn in pool:
                assert tag in fn.__name__, fn.__name__
                assert getattr(fn, "_kind", "") == "number_fields", fn.__name__
                assert getattr(fn, "_randomizable", False) is True, fn.__name__
                problem = fn()
                assert problem.get("answer_type") == "number_fields", fn.__name__
                assert problem.get("correct_answer_raw"), fn.__name__
                assert int(problem.get("marks") or 0) >= 2, fn.__name__
                types = problem.get("answer_field_types") or []
                assert 2 <= len(types) <= 4, (fn.__name__, types)
                if any(kind in types for kind in ("order", "pick")):
                    saw_order_or_pick = True
                blob = _blob(problem)
                assert not DISCLOSE_RE.search(blob), (fn.__name__, blob[:180])
                assert "fictional" in blob.lower(), fn.__name__
                via_generate = generate(
                    difficulty, mode, variant_name=fn.__name__
                )
                assert via_generate.get("answer_type") == "number_fields", fn.__name__
    assert saw_order_or_pick


def test_unit11_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit11_randomization():
    fn = next(
        f
        for f in eursc_science_science_lab_variants(
            "foundational", SITUATIONAL_MULTI_STEP_MODE
        )
        if f.__name__ == "science_lab_foundational_sms_heat_water_mean_then_thermo"
    )
    stems = set()
    for seed in range(20):
        random.seed(seed)
        stems.add(fn()["question"])
    assert len(stems) > 1


def test_unit11_lesson_and_standard_isolated():
    for slug, expected in STANDARD_SNAPSHOT.items():
        vf = SCIENCE[slug]["variants_func"]
        for difficulty in DIFFS:
            standard_names = tuple(fn.__name__ for fn in vf(difficulty, "standard"))
            assert standard_names == expected[difficulty], (slug, difficulty, standard_names)
            lesson_names = [fn.__name__ for fn in vf(difficulty, "lesson")]
            assert len(lesson_names) == LESSON_COUNT_SNAPSHOT[slug][difficulty], (
                slug,
                difficulty,
                len(lesson_names),
            )
            assert all("_ms_" not in name and "_sms_" not in name for name in lesson_names)
            advanced = []
            for mode in BOTH_ADVANCED:
                advanced.extend(fn.__name__ for fn in vf(difficulty, mode))
            assert set(standard_names).isdisjoint(advanced), (slug, difficulty)
            assert set(lesson_names).isdisjoint(advanced), (slug, difficulty)


def test_unit11_api_generate():
    with app.test_client() as client:
        cases = (
            ("measurement", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("science_lab", MULTI_STEP_MODE, "foundational"),
            ("science_lab", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("what_is_science", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("what_is_science", MULTI_STEP_MODE, "intermediate"),
        )
        for topic, mode, difficulty in cases:
            response = client.post(
                "/api/v1/problems/generate",
                json={
                    "level": "eursc",
                    "subject": "science",
                    "topic": topic,
                    "mode": mode,
                    "difficulty": difficulty,
                    "action": "start",
                },
                headers={"Accept": "application/json"},
            )
            assert response.status_code == 200, (topic, mode, response.data[:400])
            payload = response.get_json()
            problem = payload["problem"]
            assert problem["mode"] == mode, (topic, mode, problem["mode"])
            assert problem.get("answer_type") == "number_fields", topic
            variant = (payload.get("selection") or {}).get("variant_name") or ""
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            assert tag in variant, (topic, variant)

        empty = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "what_is_science",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
        assert empty.status_code == 200, empty.data[:400]
        payload = empty.get_json()
        problem = payload["problem"]
        assert problem["mode"] == "standard"
        variant = (payload.get("selection") or {}).get("variant_name") or ""
        assert "_ms_" not in variant and "_sms_" not in variant, variant


def main():
    test_unit11_registers_supported_modes()
    test_what_is_science_foundational_ms_stays_empty()
    test_unit11_cells_are_grader_ready()
    test_unit11_same_variant_is_pinned()
    test_unit11_randomization()
    test_unit11_lesson_and_standard_isolated()
    test_unit11_api_generate()
    print("S1 Unit 1.1 advanced checks passed.")


if __name__ == "__main__":
    main()
