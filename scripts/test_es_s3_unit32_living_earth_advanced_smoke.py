"""Smoke checks for S3 Unit 3.2 Living Earth advanced Practice cells (Batch 4.2).

Safeguarding gate: environmental scenarios use supplied public/aggregate data,
fictional reserves, farms and field stations only — never a pupil's household,
diet, bin, garden, address or travel, and nothing ranks homes or families
(``LIVING_EARTH_DISCLOSE_RE`` over stems, solutions, hints AND every option
bank). Field-project items grade planning, records, analysis and reflection
only. Full matrix for all five slugs; lesson and standard pools unchanged.
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
from generators.eursc import s3_living_earth as living_mod  # noqa: E402
from generators.eursc.s3_living_earth import (  # noqa: E402
    eursc_science_classification_biodiversity,
    eursc_science_classification_biodiversity_variants,
    eursc_science_ecology_field_project,
    eursc_science_ecology_field_project_variants,
    eursc_science_ecosystem_characteristics,
    eursc_science_ecosystem_characteristics_variants,
    eursc_science_ecosystems_cycles,
    eursc_science_ecosystems_cycles_variants,
    eursc_science_food_environment,
    eursc_science_food_environment_variants,
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
LIVING_EARTH_SLUGS = (
    "food_environment",
    "ecosystems_cycles",
    "ecosystem_characteristics",
    "classification_biodiversity",
    "ecology_field_project",
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

# Batch 4.2 gate: no household / diet / garden / address prompts, no ranking of
# homes or families, no private uploads or location-linked samples.
LIVING_EARTH_DISCLOSE_RE = re.compile(
    r"\b(your (home|house|household|family|families|diet|meals?|plate|bin|"
    r"garden|backyard|lawn|address|postcode|street|carbon footprint|"
    r"shopping|car|holiday|flights?)|"
    r"where you live|what you (eat|ate|buy|bought)|"
    r"(photograph|upload|map) your|"
    r"rank (your|the) (class|classmates|pupils|families|households|homes|gardens))\b",
    re.I,
)

STANDARD_SNAPSHOT = {
    "food_environment": living_mod._FE_STANDARD,
    "ecosystems_cycles": living_mod._ECY_STANDARD,
    "ecosystem_characteristics": living_mod._CH_STANDARD,
    "classification_biodiversity": living_mod._CL_STANDARD,
    "ecology_field_project": living_mod._FP_STANDARD,
}

LESSON_COUNT_SNAPSHOT = {
    slug: {"foundational": 10, "intermediate": 10, "difficult": 10}
    for slug in LIVING_EARTH_SLUGS
}

# Matrix (docs/EURSC_ADVANCED_QUESTIONS.md): supported tiers per mode.
MS_TIERS = {slug: DIFFS for slug in LIVING_EARTH_SLUGS}
SMS_TIERS = {slug: DIFFS for slug in LIVING_EARTH_SLUGS}
MS_ONLY_EXCLUDED = ()

GENERATORS = {
    "food_environment": (eursc_science_food_environment, eursc_science_food_environment_variants),
    "ecosystems_cycles": (eursc_science_ecosystems_cycles, eursc_science_ecosystems_cycles_variants),
    "ecosystem_characteristics": (
        eursc_science_ecosystem_characteristics,
        eursc_science_ecosystem_characteristics_variants,
    ),
    "classification_biodiversity": (
        eursc_science_classification_biodiversity,
        eursc_science_classification_biodiversity_variants,
    ),
    "ecology_field_project": (eursc_science_ecology_field_project, eursc_science_ecology_field_project_variants),
}

PINNED = (
    (eursc_science_food_environment, MULTI_STEP_MODE, "intermediate",
     "food_environment_intermediate_ms_compare_ratio_then_choice_mcq"),
    (eursc_science_food_environment, SITUATIONAL_MULTI_STEP_MODE, "difficult",
     "food_environment_difficult_sms_trial_gap_then_caution_pick_then_verdict"),
    (eursc_science_ecosystems_cycles, MULTI_STEP_MODE, "difficult",
     "ecosystems_cycles_difficult_ms_carbon_balance_then_mcq_then_pick"),
    (eursc_science_ecosystem_characteristics, SITUATIONAL_MULTI_STEP_MODE, "intermediate",
     "ecosystem_characteristics_intermediate_sms_river_ratio_then_mcq_then_word"),
    (eursc_science_classification_biodiversity, MULTI_STEP_MODE, "difficult",
     "classification_biodiversity_difficult_ms_descent_pct_then_mcq_then_word"),
    (eursc_science_ecology_field_project, SITUATIONAL_MULTI_STEP_MODE, "intermediate",
     "ecology_field_project_intermediate_sms_woodlice_mean_then_mcq_then_word"),
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
    parts = [
        str(problem.get("question") or ""),
        str(problem.get("solution") or ""),
        str(problem.get("hint") or ""),
    ]
    for bank in problem.get("answer_field_options") or []:
        for item in bank or []:
            parts.append(item["text"] if isinstance(item, dict) else str(item))
    return " ".join(parts)


def test_unit32_registers_supported_modes():
    for slug in LIVING_EARTH_SLUGS:
        key = ("eursc", "science", slug)
        expected = ["standard"]
        if MS_TIERS[slug]:
            expected.append(MULTI_STEP_MODE)
        if SMS_TIERS[slug]:
            expected.append(SITUATIONAL_MULTI_STEP_MODE)
        assert topic_mode_capabilities(*key) == tuple(expected), (slug, topic_mode_capabilities(*key))


def test_excluded_cells_stay_empty():
    for slug in LIVING_EARTH_SLUGS:
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


def test_unit32_cells_are_grader_ready():
    saw_order_or_pick = False
    saw_three_part = False
    for slug in LIVING_EARTH_SLUGS:
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
                        hit = LIVING_EARTH_DISCLOSE_RE.search(blob)
                        assert not hit, (fn.__name__, hit and hit.group(0))
                        assert "fictional" in blob.lower(), fn.__name__
                        assert "(ii)" in problem["question"], fn.__name__
                    via_generate = generate(
                        difficulty, mode, variant_name=fn.__name__
                    )
                    assert via_generate.get("answer_type") == "number_fields", fn.__name__
    assert saw_order_or_pick
    assert saw_three_part


def test_unit32_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit32_packs_randomise_once():
    """Every part derives from one chosen pack: the woodlice mean matches the stem."""
    random.seed(11)
    for _ in range(12):
        problem = eursc_science_ecology_field_project(
            "intermediate",
            SITUATIONAL_MULTI_STEP_MODE,
            variant_name="ecology_field_project_intermediate_sms_woodlice_mean_then_mcq_then_word",
        )
        m = re.search(r"under logs (\d+), (\d+), (\d+);", problem["question"])
        assert m, problem["question"][:240]
        logs = [int(g) for g in m.groups()]
        raw_mean = problem["correct_answer_raw"].split("\x1e")[0]
        assert int(float(raw_mean)) == sum(logs) // 3, (raw_mean, logs)


def test_unit32_lesson_and_standard_isolated():
    for slug in LIVING_EARTH_SLUGS:
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


def test_unit32_api_generate():
    with app.test_client() as client:
        cases = (
            ("food_environment", MULTI_STEP_MODE, "foundational"),
            ("food_environment", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("ecosystems_cycles", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("ecosystems_cycles", MULTI_STEP_MODE, "intermediate"),
            ("ecosystem_characteristics", MULTI_STEP_MODE, "foundational"),
            ("ecosystem_characteristics", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("classification_biodiversity", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("classification_biodiversity", MULTI_STEP_MODE, "intermediate"),
            ("ecology_field_project", MULTI_STEP_MODE, "foundational"),
            ("ecology_field_project", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
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

        # No Unit 3.2 cell is excluded; the permanent exclusions elsewhere still clamp.
        empties = (
            ("smell", MULTI_STEP_MODE, "intermediate"),
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
    test_unit32_registers_supported_modes()
    test_excluded_cells_stay_empty()
    test_unit32_cells_are_grader_ready()
    test_unit32_same_variant_is_pinned()
    test_unit32_packs_randomise_once()
    test_unit32_lesson_and_standard_isolated()
    test_unit32_api_generate()
    print("S3 Unit 3.2 Living Earth advanced checks passed.")


if __name__ == "__main__":
    main()
