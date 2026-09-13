"""Smoke checks for S1 Unit 1.4 Puberty advanced Practice cells (Batch 2.4)."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _normalize_generator_mode, app  # noqa: E402
from generators.eursc import s1_puberty as puberty_mod  # noqa: E402
from generators.eursc.s1_puberty import (  # noqa: E402
    eursc_science_pregnancy_sexual_health,
    eursc_science_pregnancy_sexual_health_variants,
    eursc_science_puberty_maturity,
    eursc_science_puberty_maturity_variants,
    eursc_science_reproductive_anatomy,
    eursc_science_reproductive_anatomy_variants,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
BOTH_ADVANCED = (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)
PUBERTY_SLUGS = (
    "puberty_maturity",
    "reproductive_anatomy",
    "pregnancy_sexual_health",
)

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
    "puberty_maturity": puberty_mod._PM_STANDARD,
    "reproductive_anatomy": puberty_mod._RA_STANDARD,
    "pregnancy_sexual_health": puberty_mod._PS_STANDARD,
}

LESSON_COUNT_SNAPSHOT = {
    "puberty_maturity": {"foundational": 11, "intermediate": 10, "difficult": 10},
    "reproductive_anatomy": {"foundational": 11, "intermediate": 10, "difficult": 10},
    "pregnancy_sexual_health": {"foundational": 11, "intermediate": 10, "difficult": 10},
}

MS_PARTIAL = {
    "puberty_maturity": ("intermediate", "difficult"),
    "reproductive_anatomy": ("intermediate", "difficult"),
    "pregnancy_sexual_health": ("intermediate", "difficult"),
}

GENERATORS = {
    "puberty_maturity": (
        eursc_science_puberty_maturity,
        eursc_science_puberty_maturity_variants,
    ),
    "reproductive_anatomy": (
        eursc_science_reproductive_anatomy,
        eursc_science_reproductive_anatomy_variants,
    ),
    "pregnancy_sexual_health": (
        eursc_science_pregnancy_sexual_health,
        eursc_science_pregnancy_sexual_health_variants,
    ),
}

PINNED = (
    (
        eursc_science_puberty_maturity,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "puberty_maturity_foundational_sms_chart_not_started_then_hormone_pick",
    ),
    (
        eursc_science_puberty_maturity,
        MULTI_STEP_MODE,
        "intermediate",
        "puberty_maturity_intermediate_ms_chart_not_started_then_hormone_mcq",
    ),
    (
        eursc_science_reproductive_anatomy,
        MULTI_STEP_MODE,
        "intermediate",
        "reproductive_anatomy_intermediate_ms_cycle_order_then_period_mcq",
    ),
    (
        eursc_science_pregnancy_sexual_health,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "pregnancy_sexual_health_foundational_sms_two_agree_then_consent_mcq",
    ),
    (
        eursc_science_pregnancy_sexual_health,
        MULTI_STEP_MODE,
        "intermediate",
        "pregnancy_sexual_health_intermediate_ms_consent_two_then_no_mcq",
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


def test_unit14_registers_supported_modes():
    assert topic_mode_capabilities(
        "eursc", "science", "puberty_maturity"
    ) == ("standard", MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)
    assert topic_mode_capabilities(
        "eursc", "science", "reproductive_anatomy"
    ) == ("standard", MULTI_STEP_MODE)
    assert topic_mode_capabilities(
        "eursc", "science", "pregnancy_sexual_health"
    ) == ("standard", MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)


def test_reproductive_anatomy_sms_stays_fail_closed():
    vf = eursc_science_reproductive_anatomy_variants
    key = ("eursc", "science", "reproductive_anatomy")
    for difficulty in DIFFS:
        assert vf(difficulty, SITUATIONAL_MULTI_STEP_MODE) == [], difficulty
    assert (
        _normalize_generator_mode(*key, SITUATIONAL_MULTI_STEP_MODE) == "standard"
    )


def test_partial_ms_foundational_stays_empty():
    for slug in MS_PARTIAL:
        vf = GENERATORS[slug][1]
        assert vf("foundational", MULTI_STEP_MODE) == [], slug
        key = ("eursc", "science", slug)
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


def test_unit14_cells_are_grader_ready():
    saw_order_or_pick = False
    for slug in PUBERTY_SLUGS:
        generate, variants = GENERATORS[slug]
        ms_diffs = MS_PARTIAL.get(slug, DIFFS)
        sms_diffs = () if slug == "reproductive_anatomy" else DIFFS
        for mode, diffs in (
            (MULTI_STEP_MODE, ms_diffs),
            (SITUATIONAL_MULTI_STEP_MODE, sms_diffs),
        ):
            if not diffs:
                continue
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            for difficulty in diffs:
                pool = variants(difficulty, mode)
                assert len(pool) >= 3, (slug, mode, difficulty, len(pool))
                names = [fn.__name__ for fn in pool]
                assert len(set(names)) == len(names), (slug, mode, difficulty)
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


def test_unit14_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit14_lesson_and_standard_isolated():
    for slug in PUBERTY_SLUGS:
        vf = SCIENCE[slug]["variants_func"]
        for difficulty in DIFFS:
            standard_names = tuple(fn.__name__ for fn in vf(difficulty, "standard"))
            assert standard_names == STANDARD_SNAPSHOT[slug][difficulty], (
                slug,
                difficulty,
                standard_names,
            )
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


def test_unit14_api_generate():
    with app.test_client() as client:
        cases = (
            ("puberty_maturity", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("puberty_maturity", MULTI_STEP_MODE, "intermediate"),
            ("reproductive_anatomy", MULTI_STEP_MODE, "intermediate"),
            ("pregnancy_sexual_health", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("pregnancy_sexual_health", MULTI_STEP_MODE, "intermediate"),
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

        empty_ms = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "puberty_maturity",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
        assert empty_ms.status_code == 200, empty_ms.data[:400]
        assert empty_ms.get_json()["problem"]["mode"] == "standard"

        blocked_sms = client.post(
            "/api/v1/problems/generate",
            json={
                "level": "eursc",
                "subject": "science",
                "topic": "reproductive_anatomy",
                "mode": SITUATIONAL_MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
        assert blocked_sms.status_code == 200, blocked_sms.data[:400]
        assert blocked_sms.get_json()["problem"]["mode"] == "standard"
        variant = (blocked_sms.get_json().get("selection") or {}).get("variant_name") or ""
        assert "_sms_" not in variant and "_ms_" not in variant, variant


def main():
    test_unit14_registers_supported_modes()
    test_reproductive_anatomy_sms_stays_fail_closed()
    test_partial_ms_foundational_stays_empty()
    test_unit14_cells_are_grader_ready()
    test_unit14_same_variant_is_pinned()
    test_unit14_lesson_and_standard_isolated()
    test_unit14_api_generate()
    print("S1 Unit 1.4 Puberty advanced checks passed.")


if __name__ == "__main__":
    main()
