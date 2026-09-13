"""Smoke checks for S2 Unit 2.2 Health advanced Practice cells (Batch 3.2).

Safeguarding gate: every stem is a third-person fictional case, textbook or
public aggregate; ``DISCLOSE_RE`` and the extra health-specific patterns below
must stay clean; lesson and standard pools are unchanged.
"""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _normalize_generator_mode, app  # noqa: E402
from generators.eursc import s2_health as health_mod  # noqa: E402
from generators.eursc.s2_health import (  # noqa: E402
    eursc_science_dependence_addiction,
    eursc_science_dependence_addiction_variants,
    eursc_science_healthy_living,
    eursc_science_healthy_living_variants,
    eursc_science_infectious_disease,
    eursc_science_infectious_disease_variants,
    eursc_science_noninfectious_disease,
    eursc_science_noninfectious_disease_variants,
    eursc_science_tobacco,
    eursc_science_tobacco_variants,
)
from generators.shared.answer_checkers import (  # noqa: E402
    _parse_proof_steps_raw,
    check_answer,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
BOTH_ADVANCED = (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)
HEALTH_SLUGS = (
    "healthy_living",
    "infectious_disease",
    "noninfectious_disease",
    "dependence_addiction",
    "tobacco",
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

# Batch 3.2 gate: no second-person health, diet, screen, mood, use, smoking,
# vaping or family-health prompts, and no classmate ranking instructions.
HEALTH_DISCLOSE_RE = re.compile(
    r"\b(your (weight|height|bmi|meals?|snacks?|screen time|bedtime|phone|"
    r"mood|feelings|family|parents?|relatives?|habits?|gaming|gambling|"
    r"smoking|vaping|drinking|medication|diagnosis|therapy|counsell?or)|"
    r"do you (drink|game|gamble|eat|sleep|exercise|feel|take|struggle|"
    r"worry)|have you (tried|used|taken|gambled|felt)|"
    r"rank (your|the) (class|classmates|pupils))\b",
    re.I,
)

STANDARD_SNAPSHOT = {
    "healthy_living": health_mod._HL_STANDARD,
    "infectious_disease": health_mod._ID_STANDARD,
    "noninfectious_disease": health_mod._NI_STANDARD,
    "dependence_addiction": health_mod._DA_STANDARD,
    "tobacco": health_mod._TB_STANDARD,
}

LESSON_COUNT_SNAPSHOT = {
    "healthy_living": {"foundational": 10, "intermediate": 10, "difficult": 10},
    "infectious_disease": {"foundational": 10, "intermediate": 10, "difficult": 11},
    "noninfectious_disease": {"foundational": 10, "intermediate": 10, "difficult": 10},
    "dependence_addiction": {"foundational": 10, "intermediate": 10, "difficult": 10},
    "tobacco": {"foundational": 10, "intermediate": 10, "difficult": 10},
}

# Matrix: foundational MS stays — for every Unit 2.2 slug except infectious_disease.
MS_PARTIAL = {
    "healthy_living": ("intermediate", "difficult"),
    "noninfectious_disease": ("intermediate", "difficult"),
    "dependence_addiction": ("intermediate", "difficult"),
    "tobacco": ("intermediate", "difficult"),
}

GENERATORS = {
    "healthy_living": (eursc_science_healthy_living, eursc_science_healthy_living_variants),
    "infectious_disease": (
        eursc_science_infectious_disease,
        eursc_science_infectious_disease_variants,
    ),
    "noninfectious_disease": (
        eursc_science_noninfectious_disease,
        eursc_science_noninfectious_disease_variants,
    ),
    "dependence_addiction": (
        eursc_science_dependence_addiction,
        eursc_science_dependence_addiction_variants,
    ),
    "tobacco": (eursc_science_tobacco, eursc_science_tobacco_variants),
}

PINNED = (
    (
        eursc_science_healthy_living,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "healthy_living_foundational_sms_canteen_groups_then_balance_mcq",
    ),
    (
        eursc_science_healthy_living,
        MULTI_STEP_MODE,
        "difficult",
        "healthy_living_difficult_ms_claim_sample_then_flaws_pick_then_verdict",
    ),
    (
        eursc_science_infectious_disease,
        MULTI_STEP_MODE,
        "foundational",
        "infectious_disease_foundational_ms_double_count_then_chain_order",
    ),
    (
        eursc_science_noninfectious_disease,
        SITUATIONAL_MULTI_STEP_MODE,
        "difficult",
        "noninfectious_disease_difficult_sms_factory_ratio_then_control_order_then_pick",
    ),
    (
        eursc_science_dependence_addiction,
        SITUATIONAL_MULTI_STEP_MODE,
        "intermediate",
        "dependence_addiction_intermediate_sms_survey_pct_then_reading_mcq_then_word",
    ),
    (
        eursc_science_tobacco,
        MULTI_STEP_MODE,
        "difficult",
        "tobacco_difficult_ms_mortality_ratio_then_reading_mcq_then_word",
    ),
)


def client_user_answer(problem):
    """Build the answer a correct client would submit for a number_fields problem."""
    raw = str(problem.get("correct_answer_raw") or "")
    types = problem.get("answer_field_types") or []
    sep = "\x1e" if "\x1e" in raw else "|"
    out = []
    for i, part in enumerate(raw.split(sep)):
        ft = types[i] if i < len(types) else "number"
        if ft in ("pick", "order"):
            parsed = _parse_proof_steps_raw(part)
            assert parsed, (ft, part)
            if parsed["mode"] == "pick":
                ids = parsed["correct_ids"][: parsed["pick_count"]]
            else:
                ids = parsed["expected_ids"]
            out.append("|".join(ids))
        else:
            out.append(part)
    return sep.join(out)


def _blob(problem):
    return " ".join(
        [
            str(problem.get("question") or ""),
            str(problem.get("solution") or ""),
            str(problem.get("hint") or ""),
        ]
    )


def test_unit22_registers_supported_modes():
    both = ("standard",) + BOTH_ADVANCED
    for slug in HEALTH_SLUGS:
        key = ("eursc", "science", slug)
        assert topic_mode_capabilities(*key) == both, slug


def test_partial_ms_foundational_stays_empty():
    for slug in MS_PARTIAL:
        generate, vf = GENERATORS[slug]
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
        try:
            generate("foundational", MULTI_STEP_MODE)
        except ValueError as exc:
            assert "No multi_step variants" in str(exc), (slug, exc)
        else:
            raise AssertionError(f"{slug} foundational multi_step leaked")
    # infectious_disease is the one Unit 2.2 slug with foundational MS.
    assert len(eursc_science_infectious_disease_variants("foundational", MULTI_STEP_MODE)) >= 3


def test_unit22_cells_are_grader_ready():
    saw_order_or_pick = False
    saw_three_part = False
    for slug in HEALTH_SLUGS:
        generate, variants = GENERATORS[slug]
        ms_diffs = MS_PARTIAL.get(slug, DIFFS)
        for mode, diffs in (
            (MULTI_STEP_MODE, ms_diffs),
            (SITUATIONAL_MULTI_STEP_MODE, DIFFS),
        ):
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            for difficulty in diffs:
                pool = variants(difficulty, mode)
                assert len(pool) >= 3, (slug, mode, difficulty, len(pool))
                names = [fn.__name__ for fn in pool]
                assert len(set(names)) == len(names), (slug, mode, difficulty)
                for fn in pool:
                    assert fn.__name__.startswith(f"{slug}_{difficulty}{tag}"), fn.__name__
                    assert getattr(fn, "_kind", "") == "number_fields", fn.__name__
                    assert getattr(fn, "_randomizable", False) is True, fn.__name__
                    for _ in range(6):
                        problem = fn()
                        assert problem.get("answer_type") == "number_fields", fn.__name__
                        assert problem.get("correct_answer_raw"), fn.__name__
                        types = problem.get("answer_field_types") or []
                        labels = problem.get("answer_labels") or []
                        assert 2 <= len(types) <= 4, (fn.__name__, types)
                        assert len(labels) == len(types), fn.__name__
                        assert int(problem.get("marks") or 0) == len(types), fn.__name__
                        if any(kind in types for kind in ("order", "pick")):
                            saw_order_or_pick = True
                        if len(types) >= 3:
                            saw_three_part = True
                        result = check_answer(
                            "number_fields",
                            problem["correct_answer_raw"],
                            client_user_answer(problem),
                        )
                        assert result["correct"], (fn.__name__, result)
                        blob = _blob(problem)
                        assert not DISCLOSE_RE.search(blob), (fn.__name__, blob[:180])
                        assert not HEALTH_DISCLOSE_RE.search(blob), (fn.__name__, blob[:180])
                        assert "fictional" in blob.lower(), fn.__name__
                        assert "(ii)" in problem["question"], fn.__name__
                    via_generate = generate(
                        difficulty, mode, variant_name=fn.__name__
                    )
                    assert via_generate.get("answer_type") == "number_fields", fn.__name__
    assert saw_order_or_pick
    assert saw_three_part


def test_unit22_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit22_packs_randomise_once():
    """Every part is derived from one chosen pack: values in the stem match the answer."""
    random.seed(11)
    for _ in range(12):
        problem = eursc_science_infectious_disease(
            "intermediate",
            MULTI_STEP_MODE,
            variant_name="infectious_disease_intermediate_ms_coverage_pct_then_vaccine_mcq",
        )
        m = re.search(r"gives (\d+) vaccinated\s+people in a group of (\d+)", problem["question"])
        assert m, problem["question"][:200]
        vaccinated, group = int(m.group(1)), int(m.group(2))
        raw_pct = problem["correct_answer_raw"].split("\x1e")[0]
        assert int(float(raw_pct)) == round(100 * vaccinated / group), (raw_pct, vaccinated, group)


def test_unit22_lesson_and_standard_isolated():
    for slug in HEALTH_SLUGS:
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


def test_unit22_api_generate():
    with app.test_client() as client:
        cases = (
            ("healthy_living", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("healthy_living", MULTI_STEP_MODE, "intermediate"),
            ("infectious_disease", MULTI_STEP_MODE, "foundational"),
            ("infectious_disease", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("noninfectious_disease", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("noninfectious_disease", MULTI_STEP_MODE, "intermediate"),
            ("dependence_addiction", MULTI_STEP_MODE, "intermediate"),
            ("dependence_addiction", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("tobacco", MULTI_STEP_MODE, "intermediate"),
            ("tobacco", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
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

        for topic in MS_PARTIAL:
            empty = client.post(
                "/api/v1/problems/generate",
                json={
                    "level": "eursc",
                    "subject": "science",
                    "topic": topic,
                    "mode": MULTI_STEP_MODE,
                    "difficulty": "foundational",
                    "action": "start",
                },
                headers={"Accept": "application/json"},
            )
            assert empty.status_code == 200, empty.data[:400]
            problem = empty.get_json()["problem"]
            assert problem["mode"] == "standard", topic
            variant = (empty.get_json().get("selection") or {}).get("variant_name") or ""
            assert "_ms_" not in variant and "_sms_" not in variant, (topic, variant)


def main():
    test_unit22_registers_supported_modes()
    test_partial_ms_foundational_stays_empty()
    test_unit22_cells_are_grader_ready()
    test_unit22_same_variant_is_pinned()
    test_unit22_packs_randomise_once()
    test_unit22_lesson_and_standard_isolated()
    test_unit22_api_generate()
    print("S2 Unit 2.2 Health advanced checks passed.")


if __name__ == "__main__":
    main()
