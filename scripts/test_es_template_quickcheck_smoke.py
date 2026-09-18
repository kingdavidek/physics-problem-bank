"""EURSC lesson pages: direct prose and plausible Quick Check distractors.

Scans every ``templates/eursc_science_*.html`` and checks:

* no course/model meta-phrases in the page text ("in this lesson",
  "in this S2 model", "of the order of", "teaching set", ...);
* every inline Quick Check (``.mcq-inline``) has four distinct, non-empty
  options, a ``data-correct`` letter that matches one of them, no retired
  filler option, and no length give-away;
* within a page the correct letter is spread over A-D rather than always B.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEMPLATES = sorted((ROOT / "templates").glob("eursc_science_*.html"))

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

RETIRED_FILLER = {
    "a class vote", "a class rank", "a class league", "a stored diet",
    "a stored diet file", "a diet file", "a diet", "a food group", "a menu",
    "a light-year", "only a light-year", "a vaccine", "a vaccination",
    "a magnet pole", "a joint map", "a shock survey", "a shock story",
    "a shock file", "a glasses file", "a handle", "a brand", "a pupil name",
    "a rumour", "a joke", "a spell", "sand", "a private confession",
    "a household rank", "a tongue rank", "a canal rank", "rank classmates",
    "ranks classmates", "rank the class", "ranks the class", "rank alex",
    "rank sam", "rank jordan", "ranking alex", "ranks pupils",
    "a pupil ranking", "inspect homes", "forced spinning", "store files",
    "eighty", "fourteen", "a unit of time", "an advert", "a stored diary",
    "a private diary", "a prescription", "a prescription file",
    "a medical file", "a stored clinical file", "a stored map",
    "a plate survey", "a fridge photo", "a carbon diary", "a stored menu",
    "a hearing test", "a geocentric vote", "a friction force",
    "a pulse of 80", "iron nails", "plastic", "an si unit", "si units fail",
    "a virus chain only", "must be photographed", "must be uploaded",
    "uploads a prescription", "eight planets", "fourteen days",
    "fourteen minutes",
}

BLOCK_RE = re.compile(
    r'<div class="mcq-inline"[^>]*data-correct="([A-D])"[^>]*>(.*?)</div>', re.S
)
BTN_RE = re.compile(r'<button class="btn mcq-btn" data-letter="([A-D])">(.*?)</button>', re.S)


def _text(html):
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    html = re.sub(r"{%.*?%}", " ", html, flags=re.S)
    return html


def main():
    blocks_checked = 0
    for path in TEMPLATES:
        src = path.read_text(encoding="utf-8")
        name = path.name
        hit = META_RE.search(_text(src))
        assert not hit, (name, hit.group(0), _text(src)[max(0, hit.start() - 60): hit.end() + 60])
        letters = Counter()
        for m in BLOCK_RE.finditer(src):
            correct, body = m.group(1), m.group(2)
            buttons = BTN_RE.findall(body)
            assert [b[0] for b in buttons] == ["A", "B", "C", "D"], (name, buttons)
            bodies = [re.sub(r"\s+", " ", b[1]).strip() for b in buttons]
            assert all(bodies), (name, bodies)
            lowered = [b.lower() for b in bodies]
            assert len(set(lowered)) == 4, (name, bodies)
            for b in lowered:
                assert b not in RETIRED_FILLER, (name, b)
            correct_body = bodies["ABCD".index(correct)]
            if not (bodies[0] in ("A", "B", "C") or correct_body in ("A", "B", "C")):
                longest_wrong = max(len(b) for b in bodies if b != correct_body)
                assert not (
                    len(correct_body) > 2.5 * longest_wrong
                    and len(correct_body) - longest_wrong > 25
                ), (name, correct_body, bodies)
            letters[correct] += 1
            blocks_checked += 1
        total = sum(letters.values())
        if total >= 4:
            assert max(letters.values()) <= max(2, round(0.5 * total)), (name, dict(letters))
            assert len(letters) >= 3, (name, dict(letters))
    print(f"EURSC template quick-check smoke passed: {len(TEMPLATES)} pages, {blocks_checked} quick checks.")


if __name__ == "__main__":
    main()
