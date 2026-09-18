"""EURSC MCQ distractors must be plausible, on-topic misconceptions.

Before the 2026-09 distractor pass, wrong answers were often nonsense
("a class vote", "a stored diet file", "rank classmates") that
tested nothing. This smoke renders every EURSC MCQ (lesson, standard and
advanced modes, including MCQ fields inside number_fields problems) and
checks that:

* the four options are distinct and non-empty;
* no option is one of the retired filler phrases;
* the correct option is not conspicuously longer than every wrong option
  (a length give-away).

Safeguarding items that are *about* this quiz / the app keep their
meaning; the retired-filler list only covers phrases that were used as
off-topic wrong answers in ordinary science items.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from generators.shared.variant_utils import ADVANCED_MODES  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

SCIENCE = TOPICS["eursc"]["science"]
DIFFS = ("foundational", "intermediate", "difficult")
MODES = ("lesson", "standard") + tuple(ADVANCED_MODES)

RETIRED_FILLER = {
    "a class vote", "a class rank", "a class league", "a stored diet",
    "a stored diet file", "a diet file", "a diet", "a food group", "a menu",
    "a light-year", "only a light-year", "a vaccine", "a vaccination",
    "a magnet pole", "a joint map", "a shock survey",
    "a shock story", "a shock file", "a glasses file", "a handle", "a brand",
    "a pupil name", "a rumour", "a joke", "a spell", "sand",
    "a private confession", "a household rank", "a tongue rank",
    "a canal rank", "rank classmates", "ranks classmates", "rank the class",
    "ranks the class", "rank alex", "rank sam", "rank jordan",
    "ranking alex", "ranks pupils", "a pupil ranking", "inspect homes",
    "forced spinning", "store files", "eighty", "fourteen", "a unit of time",
    "an advert", "a stored diary",
    "a private diary", "a prescription", "a prescription file",
    "a medical file", "a stored clinical file", "a stored map",
    "a plate survey", "a fridge photo", "a carbon diary", "a stored menu",
    "a hearing test", "a geocentric vote", "a friction force",
    "a pulse of 80", "iron nails", "plastic", "an si unit",
    "si units fail", "a virus chain only",
    "must be photographed", "must be uploaded", "uploads a prescription",
    }


def _option_body(option):
    text = str(option or "")
    if len(text) >= 3 and text[0] in "ABCD" and text[1:3] == "  ":
        return text[3:].strip()
    return text.strip()


def _check_set(name, bodies, correct_body):
    assert len(bodies) == 4, (name, bodies)
    assert all(bodies), (name, bodies)
    lowered = [b.lower() for b in bodies]
    assert len(set(lowered)) == 4, (name, bodies)
    for body in lowered:
        assert body not in RETIRED_FILLER, (name, body)
    if correct_body:
        wrong = [len(b) for b in bodies if b != correct_body]
        assert wrong, (name, bodies)
        # The correct option must not be more than 2.5x the longest wrong
        # option AND more than 25 characters longer than it.
        longest_wrong = max(wrong)
        assert not (
            len(correct_body) > 2.5 * longest_wrong
            and len(correct_body) - longest_wrong > 25
        ), (name, correct_body, bodies)


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
                        problem = fn()
                        options = problem.get("options")
                        if options and problem.get("correct_answer"):
                            letter = str(problem["correct_answer"])[:1]
                            bodies = [_option_body(o) for o in options]
                            correct = ""
                            for option in options:
                                if str(option)[:1] == letter:
                                    correct = _option_body(option)
                            if bodies and bodies[0] in ("A", "B", "C"):
                                # letter-of-diagram items: only distinctness applies
                                assert len(set(bodies)) == len(bodies), (fn.__name__, bodies)
                            else:
                                _check_set(fn.__name__, bodies, correct)
                            checked += 1
                        field_types = problem.get("answer_field_types") or []
                        field_options = problem.get("answer_field_options") or []
                        raw = str(problem.get("correct_answer_raw") or "")
                        sep = "\x1e" if "\x1e" in raw else "|"
                        raw_parts = raw.split(sep)
                        for i, ftype in enumerate(field_types):
                            if ftype != "mcq" or i >= len(field_options):
                                continue
                            opts = [str(o) for o in (field_options[i] or [])]
                            if not opts:
                                continue
                            bodies = [_option_body(o) for o in opts]
                            correct = ""
                            if i < len(raw_parts) and re.fullmatch(r"[A-D]", raw_parts[i]):
                                idx = "ABCD".index(raw_parts[i])
                                if idx < len(bodies):
                                    correct = bodies[idx]
                            if bodies and bodies[0] in ("A", "B", "C"):
                                assert len(set(bodies)) == len(bodies), (fn.__name__, bodies)
                            else:
                                _check_set(fn.__name__, bodies, correct)
                            checked += 1
    print(f"EURSC distractor-quality smoke passed: {checked} MCQ option sets checked.")


if __name__ == "__main__":
    main()
