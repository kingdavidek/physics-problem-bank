"""ES Stage 6 — five practice slots per eursc/science topic per difficulty.

Run: python scripts/test_es_practice_slots_smoke.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from generators.eursc.science_shared import EURSC_PRACTICE_SLOT_COUNT  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

DIFFS = ("foundational", "intermediate", "difficult")


def test_practice_slot_count():
    science = TOPICS["eursc"]["science"]
    for slug, cfg in science.items():
        if slug == "es0_fixture":
            continue
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            lesson = vf(difficulty, "lesson")
            practice = vf(difficulty, "standard")
            mcq = vf(difficulty, "mcq")
            assert len(lesson) >= EURSC_PRACTICE_SLOT_COUNT, (slug, difficulty, len(lesson))
            assert len(practice) == min(EURSC_PRACTICE_SLOT_COUNT, len(lesson)), (
                slug,
                difficulty,
                len(practice),
                len(lesson),
            )
            assert len(mcq) >= 1, (slug, difficulty)
            practice_names = {fn.__name__ for fn in practice}
            assert len(practice_names) == len(practice), (slug, difficulty, "duplicate practice slots")
            for fn in practice:
                assert fn in lesson, (slug, difficulty, fn.__name__)


def test_practice_slots_are_stable():
    """Same pool should yield the same five practice names (kind-mix curation)."""
    cfg = TOPICS["eursc"]["science"]["energy"]
    vf = cfg["variants_func"]
    first = [fn.__name__ for fn in vf("intermediate", "standard")]
    second = [fn.__name__ for fn in vf("intermediate", "standard")]
    assert first == second
    assert len(first) == EURSC_PRACTICE_SLOT_COUNT


def main():
    test_practice_slot_count()
    test_practice_slots_are_stable()
    print("ES practice-slot smoke tests passed.")


if __name__ == "__main__":
    main()
