"""EURSC questions must be direct: no course/model meta-phrases.

Pupils aged 11-15 should read a question as having one answer, not as a
statement that is only true "in this model" or "at S2 level". This smoke
scans every EURSC science topic across lesson, standard and advanced modes
(stem, options, solution, hint, and pick/order option banks) and fails on
phrases that hedge the answer with references to the lesson, model, course
or syllabus, or with "of the order of".

Safeguarding wording about "this quiz" / "the app" (what the page will not
collect) is deliberately not covered here.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from generators.eursc.science_shared import SYLLABUS_MODULES  # noqa: E402
from generators.shared.variant_utils import ADVANCED_MODES  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
MODES = ("lesson", "standard") + tuple(ADVANCED_MODES)

META_RE = re.compile(
    r"\bof the order of\b"
    r"|\b(in|for|at|under|by) (this|the|our|a simple) (S[1-7] )?"
    r"(lesson|model|course|syllabus|teaching (model|set|figure)|classroom model)\b"
    r"|\bof (this|the) (S[1-7] )?(lesson|course|syllabus)\b"
    r"|\b(this|the) (lesson|syllabus|course|S[1-7] model|S[1-7] position|S[1-7] teaching model)"
    r"('s| says| names| treats| uses| quotes| lists| calls| position| model| response| approach| reading| next step)\b"
    r"|\bat S[1-7] level\b"
    r"|\bin the S[1-7] (model|course|syllabus)\b"
    r"|\bteaching (set|count|figure|model)\b"
    r"|\bclassroom (model|figure)\b",
    re.I,
)


def _blob(problem):
    parts = [
        str(problem.get("question") or ""),
        str(problem.get("solution") or ""),
        str(problem.get("hint") or ""),
        " ".join(str(o) for o in (problem.get("options") or [])),
    ]
    for key in ("answer_field_labels", "answer_field_options"):
        val = problem.get(key)
        if isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, (list, tuple)):
                    parts.extend(str(x) for x in item)
                else:
                    parts.append(str(item))
    return " ".join(parts)


def _objectives():
    for module in SYLLABUS_MODULES.values():
        if not isinstance(module, dict):
            continue
        for obj in module.get("objectives") or ():
            yield module.get("slug"), str(obj)


def main():
    checked = 0
    for slug, cfg in SCIENCE.items():
        if slug == "es0_fixture":
            continue
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            for mode in MODES:
                for fn in vf(difficulty, mode):
                    for _ in range(2):
                        blob = _blob(fn())
                        hit = META_RE.search(blob)
                        assert not hit, (slug, difficulty, mode, fn.__name__, hit.group(0), blob[:200])
                        checked += 1
    for slug, obj in _objectives():
        hit = META_RE.search(obj)
        assert not hit, (slug, obj, hit.group(0))
    print(f"EURSC direct-wording smoke passed: {checked} renders across {len(SCIENCE) - 1} topics.")


if __name__ == "__main__":
    main()
