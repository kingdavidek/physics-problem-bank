"""Whole-matrix audit for EURSC advanced Practice modes (post-S3).

The capability matrix in ``docs/EURSC_ADVANCED_QUESTIONS.md`` is parsed and
treated as the single source of truth. For every one of the 46 manifest slugs
this smoke checks that:

* the slug appears exactly once in the matrix;
* every supported ``topic × tier × mode`` cell exposes at least three variant
  functions with unique, well-formed names, each rendering a ``number_fields``
  problem that self-grades with an existing grader;
* every excluded cell is empty and fails closed at the variants, generate and
  app-clamp layers;
* the advertised capabilities match the matrix exactly;
* no advanced variant leaks into the lesson pool, the standard five-slot pool,
  a lesson quiz, or QOTD.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import _normalize_generator_mode  # noqa: E402
from generators.eursc.science_shared import SYLLABUS_MODULES  # noqa: E402
from generators.shared.answer_checkers import (  # noqa: E402
    CHECKERS,
    _parse_proof_steps_raw,
    check_answer,
)
from generators.shared.lesson_quiz import build_lesson_quiz  # noqa: E402
from generators.shared.variant_utils import (  # noqa: E402
    ADVANCED_MODES,
    MULTI_STEP_MODE,
    SITUATIONAL_MULTI_STEP_MODE,
)
from models.qotd import get_daily_question, list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS, topic_mode_capabilities  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
TIER_LETTER = {"F": "foundational", "I": "intermediate", "D": "difficult"}
DOC = ROOT / "docs" / "EURSC_ADVANCED_QUESTIONS.md"
ALLOWED_FIELD_TYPES = {"number", "mcq", "keyword", "order", "pick"}
ROW_RE = re.compile(r"^\|\s*\d\.\d\.\d\s*\|\s*`([a-z_]+)`\s*\|\s*([^|]*)\|\s*([^|]*)\|")


def _tiers(cell):
    cell = cell.strip()
    if cell.startswith("—"):
        return ()
    letters = [tok.strip() for tok in cell.split(",")]
    assert all(tok in TIER_LETTER for tok in letters), cell
    return tuple(TIER_LETTER[tok] for tok in letters)


def parse_matrix():
    matrix = {}
    for line in DOC.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        slug, ms_cell, sms_cell = m.group(1), m.group(2), m.group(3)
        assert slug not in matrix, f"{slug} appears twice in the matrix"
        matrix[slug] = {
            MULTI_STEP_MODE: _tiers(ms_cell),
            SITUATIONAL_MULTI_STEP_MODE: _tiers(sms_cell),
        }
    return matrix


def client_user_answer(problem):
    raw = str(problem.get("correct_answer_raw") or "")
    types = problem.get("answer_field_types") or []
    sep = "\x1e" if "\x1e" in raw else "|"
    out = []
    for i, part in enumerate(raw.split(sep)):
        ft = types[i] if i < len(types) else "number"
        if ft in ("pick", "order"):
            parsed = _parse_proof_steps_raw(part)
            assert parsed, (ft, part)
            ids = parsed["correct_ids"][: parsed["pick_count"]] if parsed["mode"] == "pick" else parsed["expected_ids"]
            out.append("|".join(ids))
        else:
            out.append(part)
    return sep.join(out)


def test_matrix_covers_every_manifest_slug_once():
    matrix = parse_matrix()
    manifest = [m["slug"] for m in SYLLABUS_MODULES.values() if isinstance(m, dict) and m.get("slug")]
    assert len(manifest) == 46 and len(set(manifest)) == 46
    assert set(matrix) == set(manifest), set(matrix) ^ set(manifest)
    assert set(matrix) == {slug for slug in SCIENCE if slug != "es0_fixture"}
    return matrix


def test_capabilities_match_matrix(matrix):
    for slug, cells in matrix.items():
        expected = ["standard"]
        if cells[MULTI_STEP_MODE]:
            expected.append(MULTI_STEP_MODE)
        if cells[SITUATIONAL_MULTI_STEP_MODE]:
            expected.append(SITUATIONAL_MULTI_STEP_MODE)
        got = topic_mode_capabilities("eursc", "science", slug)
        assert got == tuple(expected), (slug, got, expected)


def test_enabled_cells_meet_minimums(matrix):
    assert "number_fields" in CHECKERS
    total = 0
    for slug, cells in matrix.items():
        vf = SCIENCE[slug]["variants_func"]
        generate = SCIENCE[slug]["func"]
        for mode, tiers in cells.items():
            tag = "_sms_" if mode == SITUATIONAL_MULTI_STEP_MODE else "_ms_"
            for difficulty in tiers:
                pool = vf(difficulty, mode)
                assert len(pool) >= 3, (slug, mode, difficulty, len(pool))
                names = [fn.__name__ for fn in pool]
                assert len(set(names)) == len(names), (slug, mode, difficulty)
                for fn in pool:
                    assert fn.__name__.startswith(f"{slug}_{difficulty}{tag}"), fn.__name__
                    problem = fn()
                    assert problem.get("answer_type") == "number_fields", fn.__name__
                    types = problem.get("answer_field_types") or []
                    assert 2 <= len(types) <= 4, (fn.__name__, types)
                    assert set(types) <= ALLOWED_FIELD_TYPES, (fn.__name__, types)
                    assert int(problem.get("marks") or 0) == len(types), fn.__name__
                    result = check_answer("number_fields", problem["correct_answer_raw"], client_user_answer(problem))
                    assert result["correct"], (fn.__name__, result)
                    via = generate(difficulty, mode, variant_name=fn.__name__)
                    assert via.get("answer_type") == "number_fields", fn.__name__
                    total += 1
    return total


def test_excluded_cells_fail_closed(matrix):
    excluded = 0
    for slug, cells in matrix.items():
        vf = SCIENCE[slug]["variants_func"]
        generate = SCIENCE[slug]["func"]
        key = ("eursc", "science", slug)
        for mode in ADVANCED_MODES:
            for difficulty in DIFFS:
                if difficulty in cells[mode]:
                    assert _normalize_generator_mode(*key, mode, difficulty=difficulty) == mode, (slug, mode, difficulty)
                    continue
                excluded += 1
                assert vf(difficulty, mode) == [], (slug, mode, difficulty)
                assert _normalize_generator_mode(*key, mode, difficulty=difficulty) == "standard", (slug, mode, difficulty)
                try:
                    generate(difficulty, mode)
                except ValueError as exc:
                    assert f"No {mode} variants" in str(exc), (slug, mode, difficulty, exc)
                else:
                    raise AssertionError(f"{slug} {difficulty} {mode} leaked")
    return excluded


def test_isolation_from_lesson_standard_quiz_and_qotd(matrix):
    assert all(level != "eursc" for level, *_rest in list_mcq_topic_paths())
    for day in ("2026-01-01", "2026-06-15", "2026-09-13"):
        assert get_daily_question(day_key=day)["level"] != "eursc"
    for slug in matrix:
        vf = SCIENCE[slug]["variants_func"]
        for difficulty in DIFFS:
            standard = [fn.__name__ for fn in vf(difficulty, "standard")]
            lesson = [fn.__name__ for fn in vf(difficulty, "lesson")]
            assert len(standard) == 5, (slug, difficulty, len(standard))
            assert len(lesson) >= 10, (slug, difficulty, len(lesson))
            for name in standard + lesson:
                assert "_ms_" not in name and "_sms_" not in name, (slug, name)
        quiz = build_lesson_quiz("eursc", "science", slug, SCIENCE[slug], seed=17)
        assert len(quiz) == 10, slug
        blob = " ".join(str(item.get("variant_name") or "") for item in quiz)
        assert "_ms_" not in blob and "_sms_" not in blob, slug


def main():
    matrix = test_matrix_covers_every_manifest_slug_once()
    test_capabilities_match_matrix(matrix)
    enabled = test_enabled_cells_meet_minimums(matrix)
    excluded = test_excluded_cells_fail_closed(matrix)
    test_isolation_from_lesson_standard_quiz_and_qotd(matrix)
    cells = sum(len(t) for c in matrix.values() for t in c.values())
    print(
        f"EURSC advanced whole-matrix audit passed: 46 slugs, {cells} enabled cells, "
        f"{enabled} variants, {excluded} cells fail closed."
    )


if __name__ == "__main__":
    main()
