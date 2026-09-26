"""Smoke checks for S2 Unit 2.3 Senses advanced Practice cells (Batch 3.3).

Safeguarding gate: every stem is a third-person fictional case, textbook/public
table or supplied aggregate; ``DISCLOSE_RE`` and the senses-specific patterns
below must stay clean; the uneven matrix (smell / interoception MS, foundational
SMS for touch / taste / proprioception_balance, foundational MS for the I/D-only
slugs) stays fail-closed; lesson and standard pools are unchanged.
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
from generators.eursc import s2_senses as senses_mod  # noqa: E402
from generators.eursc.s2_senses import (  # noqa: E402
    eursc_science_hearing,
    eursc_science_hearing_variants,
    eursc_science_interoception,
    eursc_science_interoception_variants,
    eursc_science_nonhuman_senses,
    eursc_science_nonhuman_senses_variants,
    eursc_science_proprioception_balance,
    eursc_science_proprioception_balance_variants,
    eursc_science_smell,
    eursc_science_smell_variants,
    eursc_science_taste,
    eursc_science_taste_variants,
    eursc_science_touch,
    eursc_science_touch_variants,
    eursc_science_vision,
    eursc_science_vision_variants,
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
SENSES_SLUGS = (
    "vision",
    "hearing",
    "touch",
    "smell",
    "taste",
    "proprioception_balance",
    "interoception",
    "nonhuman_senses",
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

# Batch 3.3 gate: no second-person sensory tests, body-part prompts, glasses /
# hearing-aid / dizziness / hunger / heartbeat / mood questions, no classmate
# testing or ranking, and no live internal-state survey.
SENSES_DISCLOSE_RE = re.compile(
    r"\b(your (eyes?|ears?|nose|tongue|skin|hearing|eyesight|sight|vision|"
    r"glasses|hearing aid|balance|heartbeat|pulse|hunger|mood|feelings|"
    r"prescription|fingertips?)|"
    r"can you (see|hear|smell|taste|feel|balance)|"
    r"(close|cover|test|check) your|touch (your|each other|a classmate)|"
    r"spin (yourself|around|a classmate|each other)|"
    r"test (each other|a classmate|classmates)|"
    r"rank (your|the) (class|classmates|pupils))\b",
    re.I,
)

STANDARD_SNAPSHOT = {
    "vision": senses_mod._VI_STANDARD,
    "hearing": senses_mod._HE_STANDARD,
    "touch": senses_mod._TO_STANDARD,
    "smell": senses_mod._SM_STANDARD,
    "taste": senses_mod._TA_STANDARD,
    "proprioception_balance": senses_mod._PR_STANDARD,
    "interoception": senses_mod._IN_STANDARD,
    "nonhuman_senses": senses_mod._NH_STANDARD,
}

LESSON_COUNT_SNAPSHOT = {
    slug: {"foundational": 10, "intermediate": 10, "difficult": 10}
    for slug in SENSES_SLUGS
}

# Matrix (docs/EURSC_ADVANCED_QUESTIONS.md): supported tiers per mode.
MS_TIERS = {
    "vision": ("intermediate", "difficult"),
    "hearing": ("intermediate", "difficult"),
    "touch": ("intermediate", "difficult"),
    "smell": (),
    "taste": ("intermediate", "difficult"),
    "proprioception_balance": ("intermediate", "difficult"),
    "interoception": (),
    "nonhuman_senses": DIFFS,
}
SMS_TIERS = {
    "vision": DIFFS,
    "hearing": DIFFS,
    "touch": ("intermediate", "difficult"),
    "smell": ("intermediate", "difficult"),
    "taste": ("intermediate", "difficult"),
    "proprioception_balance": ("intermediate", "difficult"),
    "interoception": ("intermediate", "difficult"),
    "nonhuman_senses": DIFFS,
}
MS_ONLY_EXCLUDED = ("smell", "interoception")

GENERATORS = {
    "vision": (eursc_science_vision, eursc_science_vision_variants),
    "hearing": (eursc_science_hearing, eursc_science_hearing_variants),
    "touch": (eursc_science_touch, eursc_science_touch_variants),
    "smell": (eursc_science_smell, eursc_science_smell_variants),
    "taste": (eursc_science_taste, eursc_science_taste_variants),
    "proprioception_balance": (
        eursc_science_proprioception_balance,
        eursc_science_proprioception_balance_variants,
    ),
    "interoception": (eursc_science_interoception, eursc_science_interoception_variants),
    "nonhuman_senses": (eursc_science_nonhuman_senses, eursc_science_nonhuman_senses_variants),
}

PINNED = (
    (eursc_science_vision, SITUATIONAL_MULTI_STEP_MODE, "foundational",
     "vision_foundational_sms_exhibit_parts_then_lens_mcq"),
    (eursc_science_hearing, MULTI_STEP_MODE, "intermediate",
     "hearing_intermediate_ms_table_loudest_then_medium_mcq"),
    (eursc_science_touch, MULTI_STEP_MODE, "difficult",
     "touch_difficult_ms_ratio_then_density_order_then_word"),
    (eursc_science_smell, SITUATIONAL_MULTI_STEP_MODE, "difficult",
     "smell_difficult_sms_dog_pct_then_caution_pick_then_verdict"),
    (eursc_science_taste, SITUATIONAL_MULTI_STEP_MODE, "intermediate",
     "taste_intermediate_sms_panel_colour_pick_then_order"),
    (eursc_science_proprioception_balance, MULTI_STEP_MODE, "difficult",
     "proprioception_balance_difficult_ms_model_rate_then_lag_mcq_then_word"),
    (eursc_science_interoception, SITUATIONAL_MULTI_STEP_MODE, "difficult",
     "interoception_difficult_sms_ambiguous_count_then_order_then_word"),
    (eursc_science_nonhuman_senses, MULTI_STEP_MODE, "difficult",
     "nonhuman_senses_difficult_ms_echo_distance_then_mcq_then_word"),
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


def test_unit23_registers_supported_modes():
    for slug in SENSES_SLUGS:
        key = ("eursc", "science", slug)
        expected = ["standard"]
        if MS_TIERS[slug]:
            expected.append(MULTI_STEP_MODE)
        if SMS_TIERS[slug]:
            expected.append(SITUATIONAL_MULTI_STEP_MODE)
        assert topic_mode_capabilities(*key) == tuple(expected), (slug, topic_mode_capabilities(*key))


def test_excluded_cells_stay_empty():
    for slug in SENSES_SLUGS:
        generate, vf = GENERATORS[slug]
        key = ("eursc", "science", slug)
        for mode, tiers in ((MULTI_STEP_MODE, MS_TIERS[slug]), (SITUATIONAL_MULTI_STEP_MODE, SMS_TIERS[slug])):
            for difficulty in DIFFS:
                if difficulty in tiers:
                    assert len(vf(difficulty, mode)) >= 3, (slug, mode, difficulty)
                    assert _normalize_generator_mode(*key, mode, difficulty=difficulty) == mode
                    continue
                assert vf(difficulty, mode) == [], (slug, mode, difficulty)
                assert _normalize_generator_mode(*key, mode, difficulty=difficulty) == "standard", (slug, mode, difficulty)
                try:
                    generate(difficulty, mode)
                except ValueError as exc:
                    assert f"No {mode} variants" in str(exc), (slug, mode, difficulty, exc)
                else:
                    raise AssertionError(f"{slug} {difficulty} {mode} leaked")
    for slug in MS_ONLY_EXCLUDED:
        assert _normalize_generator_mode("eursc", "science", slug, MULTI_STEP_MODE) == "standard", slug


def test_unit23_cells_are_grader_ready():
    saw_order_or_pick = False
    saw_three_part = False
    for slug in SENSES_SLUGS:
        generate, variants = GENERATORS[slug]
        for mode, tiers in (
            (MULTI_STEP_MODE, MS_TIERS[slug]),
            (SITUATIONAL_MULTI_STEP_MODE, SMS_TIERS[slug]),
        ):
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            for difficulty in tiers:
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
                        assert not SENSES_DISCLOSE_RE.search(blob), (fn.__name__, blob[:180])
                        assert "fictional" in blob.lower(), fn.__name__
                        assert "(ii)" in problem["question"], fn.__name__
                    via_generate = generate(
                        difficulty, mode, variant_name=fn.__name__
                    )
                    assert via_generate.get("answer_type") == "number_fields", fn.__name__
    assert saw_order_or_pick
    assert saw_three_part


def test_unit23_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit23_packs_randomise_once():
    """Every part derives from one chosen pack: the echo distance matches the stem."""
    random.seed(11)
    for _ in range(12):
        problem = eursc_science_hearing(
            "difficult",
            SITUATIONAL_MULTI_STEP_MODE,
            variant_name="hearing_difficult_sms_echo_distance_then_order_then_word",
        )
        m = re.search(r"echo (\d+) s\s+after a clap; sound travels at (\d+) m/s", problem["question"])
        assert m, problem["question"][:240]
        t, v = int(m.group(1)), int(m.group(2))
        raw_d = problem["correct_answer_raw"].split("\x1e")[0]
        assert int(float(raw_d)) == v * t // 2, (raw_d, t, v)


def test_unit23_lesson_and_standard_isolated():
    for slug in SENSES_SLUGS:
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


def test_unit23_api_generate():
    with app.test_client() as client:
        cases = (
            ("vision", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("vision", MULTI_STEP_MODE, "intermediate"),
            ("hearing", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("touch", MULTI_STEP_MODE, "intermediate"),
            ("smell", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("taste", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("proprioception_balance", MULTI_STEP_MODE, "intermediate"),
            ("interoception", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("nonhuman_senses", MULTI_STEP_MODE, "foundational"),
            ("nonhuman_senses", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
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

        empties = (
            ("vision", MULTI_STEP_MODE, "foundational"),
            ("touch", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("smell", MULTI_STEP_MODE, "intermediate"),
            ("taste", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("proprioception_balance", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("interoception", MULTI_STEP_MODE, "intermediate"),
        )
        for topic, mode, difficulty in empties:
            empty = client.post(
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
            assert empty.status_code == 200, empty.data[:400]
            problem = empty.get_json()["problem"]
            assert problem["mode"] == "standard", (topic, mode, difficulty)
            variant = (empty.get_json().get("selection") or {}).get("variant_name") or ""
            assert "_ms_" not in variant and "_sms_" not in variant, (topic, variant)


def main():
    test_unit23_registers_supported_modes()
    test_excluded_cells_stay_empty()
    test_unit23_cells_are_grader_ready()
    test_unit23_same_variant_is_pinned()
    test_unit23_packs_randomise_once()
    test_unit23_lesson_and_standard_isolated()
    test_unit23_api_generate()
    print("S2 Unit 2.3 Senses advanced checks passed.")


if __name__ == "__main__":
    main()
