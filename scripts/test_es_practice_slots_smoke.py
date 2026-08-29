"""ES Practice generator Phase 2 — five-family standard slots.

Run: python scripts/test_es_practice_slots_smoke.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from generators.eursc.science_shared import (  # noqa: E402
    EURSC_PRACTICE_SLOT_COUNT,
    bind_eursc_topic,
    eursc_slot_family,
)
from generators.shared.lesson_quiz import build_lesson_quiz  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

DIFFS = ("foundational", "intermediate", "difficult")
SCIENCE = TOPICS["eursc"]["science"]


def _syllabus_topics():
    return {slug: cfg for slug, cfg in SCIENCE.items() if slug != "es0_fixture"}


def test_practice_slot_count():
    for slug, cfg in _syllabus_topics().items():
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            lesson = vf(difficulty, "lesson")
            practice = vf(difficulty, "standard")
            mcq = vf(difficulty, "mcq")
            assert len(lesson) >= EURSC_PRACTICE_SLOT_COUNT, (slug, difficulty, len(lesson))
            assert len(practice) == EURSC_PRACTICE_SLOT_COUNT, (
                slug,
                difficulty,
                len(practice),
            )
            assert len(mcq) >= 1, (slug, difficulty)
            practice_names = [fn.__name__ for fn in practice]
            assert len(set(practice_names)) == len(practice_names), (
                slug,
                difficulty,
                "duplicate practice slots",
            )
            for fn in practice:
                assert fn in lesson, (slug, difficulty, fn.__name__)


def test_practice_slots_are_explicit_and_stable():
    cfg = SCIENCE["energy"]
    vf = cfg["variants_func"]
    first = [fn.__name__ for fn in vf("intermediate", "standard")]
    second = [fn.__name__ for fn in vf("intermediate", "standard")]
    assert first == second
    assert len(first) == EURSC_PRACTICE_SLOT_COUNT
    src = (ROOT / "generators" / "eursc" / "s3_machines.py").read_text(encoding="utf-8")
    assert "_EN_STANDARD" in src
    for name in first:
        assert name in src, name


def test_standard_generate_does_not_leak_lesson_items():
    cfg = SCIENCE["energy"]
    vf = cfg["variants_func"]
    gen = cfg["func"]
    lesson = vf("intermediate", "lesson")
    practice = vf("intermediate", "standard")
    practice_names = {fn.__name__ for fn in practice}
    hidden = [fn for fn in lesson if fn.__name__ not in practice_names]
    assert hidden, "energy intermediate should keep extra lesson items"
    payload = gen("intermediate", "standard")
    # Generated problem comes from one of the five named slots.
    named = gen("intermediate", "standard", variant_name=practice[0].__name__)
    assert named.get("question")
    try:
        gen("intermediate", "standard", variant_name=hidden[0].__name__)
    except ValueError as err:
        assert "Unknown standard variant" in str(err)
    else:
        raise AssertionError("standard generate leaked a lesson-only variant")


def test_empty_standard_pool_does_not_fallback_to_lesson():
    def _mcq():
        return {"question": "lesson-only"}

    _mcq.__name__ = "dummy_mcq"
    _mcq._kind = "mcq"
    generate, variants = bind_eursc_topic(
        "dummy",
        {"foundational": [_mcq]},
        {"foundational": ()},
    )
    assert variants("foundational", "lesson") == [_mcq]
    assert variants("foundational", "standard") == []
    try:
        generate("foundational", "standard")
    except ValueError as err:
        assert "No standard variants" in str(err)
    else:
        raise AssertionError("empty standard pool fell back to lesson")


def test_lesson_quiz_still_uses_full_bank():
    cfg = SCIENCE["measurement"]
    lesson_len = len(cfg["variants_func"]("foundational", "lesson"))
    assert lesson_len > EURSC_PRACTICE_SLOT_COUNT
    quiz = build_lesson_quiz("eursc", "science", "measurement", cfg, seed=17)
    assert len(quiz) == 10


def test_standard_recipe_order():
    """Every named standard tier is MCQ, keyword, data, ordered, pick — in that order."""
    want = ("mcq", "keyword", "data", "order", "pick")
    for slug, cfg in _syllabus_topics().items():
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            practice = vf(difficulty, "standard")
            fams = tuple(eursc_slot_family(getattr(fn, "_kind", "")) for fn in practice)
            assert fams == want, (slug, difficulty, fams)


def test_movement_standard_is_kinematics():
    """1.3.1 is v=d/t and distance–time graphs, not the canvas joint/muscle row."""
    cfg = SCIENCE["movement"]
    vf = cfg["variants_func"]
    for difficulty in DIFFS:
        for fn in vf(difficulty, "standard"):
            problem = fn()
            blob = " ".join(
                [
                    fn.__name__,
                    str(problem.get("question") or ""),
                    str(problem.get("solution") or ""),
                ]
            ).lower()
            assert "antagonistic" not in blob, (difficulty, fn.__name__)
            assert any(
                token in blob
                for token in ("speed", "distance", "metre", "graph", "time", "second")
            ), (difficulty, fn.__name__, blob[:120])


def main():
    test_practice_slot_count()
    test_practice_slots_are_explicit_and_stable()
    test_standard_generate_does_not_leak_lesson_items()
    test_empty_standard_pool_does_not_fallback_to_lesson()
    test_lesson_quiz_still_uses_full_bank()
    test_standard_recipe_order()
    test_movement_standard_is_kinematics()
    print("ES practice-slot smoke tests passed.")


if __name__ == "__main__":
    main()
