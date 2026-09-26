"""Smoke checks for S2 Unit 2.1 Astronomy advanced Practice cells (Batch 3.1)."""
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _normalize_generator_mode, app  # noqa: E402
from generators.eursc import s2_universe as universe_mod  # noqa: E402
from generators.eursc.s2_universe import (  # noqa: E402
    eursc_science_atoms_molecules,
    eursc_science_atoms_molecules_variants,
    eursc_science_life_earth_elsewhere,
    eursc_science_life_earth_elsewhere_variants,
    eursc_science_light_telescopes,
    eursc_science_light_telescopes_variants,
    eursc_science_solar_system,
    eursc_science_solar_system_variants,
)
from generators.shared.variant_utils import (  # noqa: E402
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
BOTH_ADVANCED = (MULTI_STEP_MODE, SITUATIONAL_MULTI_STEP_MODE)
ASTRONOMY_SLUGS = (
    "solar_system",
    "light_telescopes",
    "life_earth_elsewhere",
    "atoms_molecules",
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
    "solar_system": universe_mod._SS_STANDARD,
    "light_telescopes": universe_mod._LT_STANDARD,
    "life_earth_elsewhere": universe_mod._LF_STANDARD,
    "atoms_molecules": universe_mod._AM_STANDARD,
}

LESSON_COUNT_SNAPSHOT = {
    slug: {"foundational": 10, "intermediate": 10, "difficult": 10}
    for slug in ASTRONOMY_SLUGS
}

MS_PARTIAL = {
    "life_earth_elsewhere": ("intermediate", "difficult"),
}

GENERATORS = {
    "solar_system": (eursc_science_solar_system, eursc_science_solar_system_variants),
    "light_telescopes": (
        eursc_science_light_telescopes,
        eursc_science_light_telescopes_variants,
    ),
    "life_earth_elsewhere": (
        eursc_science_life_earth_elsewhere,
        eursc_science_life_earth_elsewhere_variants,
    ),
    "atoms_molecules": (
        eursc_science_atoms_molecules,
        eursc_science_atoms_molecules_variants,
    ),
}

PINNED = (
    (
        eursc_science_solar_system,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "solar_system_foundational_sms_dome_spin_then_revolve_mcq",
    ),
    (
        eursc_science_solar_system,
        MULTI_STEP_MODE,
        "foundational",
        "solar_system_foundational_ms_planets_then_rotate_mcq",
    ),
    (
        eursc_science_light_telescopes,
        MULTI_STEP_MODE,
        "intermediate",
        "light_telescopes_intermediate_ms_two_sec_light_then_phase_mcq",
    ),
    (
        eursc_science_life_earth_elsewhere,
        SITUATIONAL_MULTI_STEP_MODE,
        "foundational",
        "life_earth_elsewhere_foundational_sms_needs_three_then_water_mcq",
    ),
    (
        eursc_science_atoms_molecules,
        MULTI_STEP_MODE,
        "difficult",
        "atoms_molecules_difficult_ms_co2_rearrange_then_fe_keyword",
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


def test_unit21_registers_supported_modes():
    both = ("standard",) + BOTH_ADVANCED
    for slug in ASTRONOMY_SLUGS:
        key = ("eursc", "science", slug)
        assert topic_mode_capabilities(*key) == both, slug


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


def test_unit21_cells_are_grader_ready():
    saw_order_or_pick = False
    for slug in ASTRONOMY_SLUGS:
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


def test_unit21_same_variant_is_pinned():
    for generate, mode, difficulty, name in PINNED:
        random.seed(7)
        first = generate(difficulty, mode, variant_name=name)
        random.seed(7)
        second = generate(difficulty, mode, variant_name=name)
        assert first["correct_answer_raw"] == second["correct_answer_raw"], name
        stem_a = re.sub(r"sk-[a-z]+-\d+", "sk-id", first["question"])
        stem_b = re.sub(r"sk-[a-z]+-\d+", "sk-id", second["question"])
        assert stem_a == stem_b, name


def test_unit21_lesson_and_standard_isolated():
    for slug in ASTRONOMY_SLUGS:
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


def test_unit21_api_generate():
    with app.test_client() as client:
        cases = (
            ("solar_system", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("solar_system", MULTI_STEP_MODE, "foundational"),
            ("light_telescopes", MULTI_STEP_MODE, "foundational"),
            ("light_telescopes", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
            ("life_earth_elsewhere", SITUATIONAL_MULTI_STEP_MODE, "foundational"),
            ("life_earth_elsewhere", MULTI_STEP_MODE, "intermediate"),
            ("atoms_molecules", MULTI_STEP_MODE, "foundational"),
            ("atoms_molecules", SITUATIONAL_MULTI_STEP_MODE, "intermediate"),
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
                "topic": "life_earth_elsewhere",
                "mode": MULTI_STEP_MODE,
                "difficulty": "foundational",
                "action": "start",
            },
            headers={"Accept": "application/json"},
        )
        assert empty.status_code == 200, empty.data[:400]
        problem = empty.get_json()["problem"]
        assert problem["mode"] == "standard"
        variant = (empty.get_json().get("selection") or {}).get("variant_name") or ""
        assert "_ms_" not in variant and "_sms_" not in variant, variant


def main():
    test_unit21_registers_supported_modes()
    test_partial_ms_foundational_stays_empty()
    test_unit21_cells_are_grader_ready()
    test_unit21_same_variant_is_pinned()
    test_unit21_lesson_and_standard_isolated()
    test_unit21_api_generate()
    print("S2 Unit 2.1 Astronomy advanced checks passed.")


if __name__ == "__main__":
    main()
