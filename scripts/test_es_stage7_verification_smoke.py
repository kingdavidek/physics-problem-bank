"""ES Stage 7 — verification smoke (mobile, dark, print, sensitive sample).

Automates the manual sample from docs/EURSC_LESSON_IMPROVEMENT_HANDOFF.md.
Run: python scripts/test_es_stage7_verification_smoke.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import GENERATOR_LAUNCH_GCSE_MATHS_CS, app  # noqa: E402
from generators.eursc.science_shared import EURSC_PRACTICE_SLOT_COUNT, SYLLABUS_MODULES  # noqa: E402
from generators.shared.lesson_quiz import build_lesson_quiz  # noqa: E402
from models.qotd import list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

TEMPLATES = ROOT / "templates"
LESSON_CSS = (ROOT / "static" / "css" / "lesson-pages.css").read_text(encoding="utf-8")

# Representative sample: S1 figures, S1 sensitive, S2 sensitive, S3 cycles.
SAMPLE_SLUGS = (
    "measurement",
    "reproductive_anatomy",
    "dependence_addiction",
    "ecosystems_cycles",
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


def _lesson_html(client, slug):
    r = client.get(f"/topic/eursc/science/{slug}")
    assert r.status_code == 200, (slug, r.data[:300])
    return r.data.decode()


def test_print_and_mobile_css_contract():
    assert "@media print" in LESSON_CSS
    assert "@media (max-width: 700px)" in LESSON_CSS
    assert "@media (max-width: 900px)" in LESSON_CSS
    assert ".lesson-table-wrap" in LESSON_CSS
    assert ".lesson-shell" in LESSON_CSS
    assert "max-width: 100%" in LESSON_CSS


def test_sample_lessons_mobile_and_light():
    with app.test_client() as client:
        for slug in SAMPLE_SLUGS:
            html = _lesson_html(client, slug)
            assert 'name="viewport" content="width=device-width' in html, slug
            assert 'data-lesson-subject="science"' in html, slug
            assert "lesson-pages.css" in html, slug
            assert 'class="lesson-shell"' in html, slug
            assert "theme.js" in html, slug
            assert 'style="' not in (
                TEMPLATES / f"eursc_science_{slug}_lesson.html"
            ).read_text(encoding="utf-8"), slug
            assert not DISCLOSE_RE.search(html), slug
            ref = next(r for r, m in SYLLABUS_MODULES.items() if m["slug"] == slug)
            module = SYLLABUS_MODULES[ref]
            assert html.count('class="mcq-inline"') == module["checkpoints"], slug
            assert f"/lesson-quiz/eursc/science/{slug}" in html, slug


def test_dark_mode_contract():
    tokens = (ROOT / "static" / "css" / "tokens.css").read_text(encoding="utf-8")
    theme_js = (ROOT / "static" / "js" / "theme.js").read_text(encoding="utf-8")
    assert ':root[data-theme="dark"]' in tokens
    assert ':root:not([data-theme="light"])' in tokens
    assert "prefers-color-scheme: dark" in tokens
    assert "pb_theme" in theme_js
    assert "data-theme" in theme_js
    # Lesson SVG fills remap for dark surfaces (Stage 1–5 science figures).
    assert "var(--surface)" in LESSON_CSS
    assert "var(--diagram-paper)" in LESSON_CSS


def test_sensitive_templates_third_person():
    for slug in ("reproductive_anatomy", "dependence_addiction"):
        src = (TEMPLATES / f"eursc_science_{slug}_lesson.html").read_text(encoding="utf-8")
        assert not DISCLOSE_RE.search(src), slug
        assert "lesson-gloss" in src or "clinical" in src.lower() or "fictional" in src.lower()


def test_practice_home_and_slots_unchanged():
    assert GENERATOR_LAUNCH_GCSE_MATHS_CS is True
    assert all(level != "eursc" for level, *_rest in list_mcq_topic_paths())

    science = TOPICS["eursc"]["science"]
    for slug in SAMPLE_SLUGS:
        cfg = science[slug]
        vf = cfg["variants_func"]
        for difficulty in ("foundational", "intermediate", "difficult"):
            lesson = vf(difficulty, "lesson")
            practice = vf(difficulty, "standard")
            assert len(lesson) >= EURSC_PRACTICE_SLOT_COUNT, (slug, difficulty)
            assert len(practice) == min(EURSC_PRACTICE_SLOT_COUNT, len(lesson)), (
                slug,
                difficulty,
            )
        quiz = build_lesson_quiz("eursc", "science", slug, cfg, seed=17)
        assert len(quiz) == 10, slug


def test_practice_generator_rejects_eursc_post():
    with app.test_client() as client:
        home = client.get("/")
        assert home.status_code == 200
        html = home.data.decode()
        assert 'data-launch-gcse-only="1"' in html
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
        posted = client.post(
            "/",
            data={
                "csrf_token": csrf,
                "level": "eursc",
                "subject": "science",
                "topic": "measurement",
                "mode": "standard",
                "difficulty": "foundational",
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        assert 'value="gcse"' in body or 'id="level-select" value="gcse"' in body


def main():
    test_print_and_mobile_css_contract()
    test_sample_lessons_mobile_and_light()
    test_dark_mode_contract()
    test_sensitive_templates_third_person()
    test_practice_home_and_slots_unchanged()
    test_practice_generator_rejects_eursc_post()
    print("ES Stage 7 verification smoke tests passed.")


if __name__ == "__main__":
    main()
