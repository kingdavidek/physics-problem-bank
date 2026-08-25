"""U6.2 — mensuration lesson unification smoke.

Run: python scripts/test_lesson_unify_smoke.py
"""
import os
import re
import sys
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402

LESSON = ROOT / 'templates' / 'gcse_maths_mensuration_lesson.html'


def test_all_lesson_templates_have_no_inline_style():
    """U6 definition of done — no inline style= in lesson teaching copy."""
    import re as _re
    pat = _re.compile(r'\sstyle="')
    offenders = []
    for path in sorted((ROOT / 'templates').glob('*_lesson.html')):
        n = len(pat.findall(path.read_text(encoding='utf-8')))
        if n:
            offenders.append(f'{path.name} ({n})')
    assert offenders == [], 'inline style= remains: ' + ', '.join(offenders)


def test_mensuration_template_has_no_inline_style():
    src = LESSON.read_text(encoding='utf-8')
    assert 'style="' not in src
    assert 'class="lesson-shell"' in src
    assert len(re.findall(r'<details[^>]*class="lesson-section"', src)) == 8
    assert src.count('class="mcq-inline"') == 7
    assert src.count('data-correct=') == 7
    assert 'lesson-quickcheck' in src
    assert 'lesson-hero' in src
    assert 'Start Practice Quiz' in src


def test_mensuration_route():
    client = app.test_client()
    r = client.get('/topic/gcse/maths/mensuration')
    assert r.status_code == 200, r.data[:500]
    html = r.data.decode()
    assert 'lesson-shell' in html
    assert html.count('mcq-inline') == 7
    assert 'data-lesson-content' in html
    assert '/lesson-quiz/gcse/maths/mensuration' in html


FILENAME_RE = re.compile(
    r'^(gcse|alevel|myp)_([a-z]+)_([a-z0-9_]+)_lesson\.html$'
)
RADIOACTIVITY = 'gcse_physics_radioactivity_lesson.html'


def test_migrated_lessons_have_shell_and_keep_mcqs():
    for path in sorted((ROOT / 'templates').glob('*_lesson.html')):
        src = path.read_text(encoding='utf-8')
        assert 'class="lesson-shell"' in src, path.name
        assert src.count('class="mcq-inline"') == src.count('data-correct='), path.name


def test_every_lesson_route_is_ok():
    client = app.test_client()
    for path in sorted((ROOT / 'templates').glob('*_lesson.html')):
        match = FILENAME_RE.match(path.name)
        assert match, path.name
        level, subject, topic = match.groups()
        url = f'/topic/{level}/{subject}/{topic}'
        response = client.get(url)
        assert response.status_code == 200, f'{url} -> {response.status_code}'
        html = response.data.decode()
        src = path.read_text(encoding='utf-8')
        assert 'lesson-shell' in html, url
        assert html.count('mcq-inline') == src.count('class="mcq-inline"'), url


def test_radioactivity_uses_base_tokens():
    src = (ROOT / 'templates' / RADIOACTIVITY).read_text(encoding='utf-8')
    assert '{% extends "base.html" %}' in src
    assert 'class="lesson-shell"' in src
    assert ':root' not in src
    assert '<style>' not in src
    assert 'pythonanywhere.com' not in src
    assert src.count('class="lesson-section"') == 8
    assert 'style="' not in src
    client = app.test_client()
    response = client.get('/topic/gcse/physics/radioactivity')
    assert response.status_code == 200, response.data[:500]
    html = response.data.decode()
    assert 'lesson-shell' in html
    assert 'relative charge' in html
    assert 'Generate a question' in html
    assert 'pythonanywhere.com' not in html


def test_no_maxwidth_attribute_selectors():
    css_dir = ROOT / 'static' / 'css'
    needle = 'style*="max-width:860px"'
    for path in css_dir.glob('*.css'):
        text = path.read_text(encoding='utf-8')
        assert needle not in text, path.name
        assert "style*='max-width:860px'" not in text, path.name
    js = (ROOT / 'static' / 'js' / 'lesson-progress.js').read_text(encoding='utf-8')
    assert 'max-width:860px' not in js
    assert 'max-width: 860px' not in js
    for path in (ROOT / 'templates').glob('*_lesson.html'):
        src = path.read_text(encoding='utf-8')
        assert 'max-width:860px' not in src, path.name
        assert 'max-width: 860px' not in src, path.name


LEGACY_STUBS = (
    'gcse_maths_surds.html',
    'gcse_maths_fdp.html',
    'gcse_maths_decimals.html',
    'gcse_maths_bidmas.html',
    'gcse_combined_physics_radioactivity.html',
)
LIVE_AFTER_STUBS = (
    'gcse_maths_surds_lesson.html',
    'gcse_maths_fdp_lesson.html',
    'gcse_maths_decimals_lesson.html',
    'gcse_maths_bidmas_lesson.html',
    'gcse_physics_radioactivity_lesson.html',
)


def test_legacy_unrouted_stubs_are_gone():
    templates = ROOT / 'templates'
    for name in LEGACY_STUBS:
        assert not (templates / name).exists(), name
    for name in LIVE_AFTER_STUBS:
        assert (templates / name).exists(), name
    client = app.test_client()
    for url in (
        '/topic/gcse/maths/surds',
        '/topic/gcse/maths/fdp',
        '/topic/gcse/maths/decimals',
        '/topic/gcse/maths/bidmas',
        '/topic/gcse/physics/radioactivity',
    ):
        response = client.get(url)
        assert response.status_code == 200, f'{url} -> {response.status_code}'
        assert 'lesson-shell' in response.data.decode()


def test_no_python_in_templates():
    py_files = sorted(p.name for p in (ROOT / 'templates').glob('*.py'))
    assert py_files == []
    legacy = ROOT / 'scripts' / 'legacy'
    assert (legacy / 'gcse_number_generator_additions.py').is_file()
    assert (legacy / 'gcse_three_topics_generator_additions.py').is_file()


def test_lesson_quiz_page_skips_lesson_progress_chrome():
    client = app.test_client()
    lesson = client.get('/topic/gcse/maths/geometry_angles')
    lesson_html = lesson.data.decode()
    assert 'data-lesson-content' in lesson_html

    quiz = client.get('/lesson-quiz/gcse/maths/geometry_angles')
    assert quiz.status_code == 200
    quiz_html = quiz.data.decode()
    assert 'data-lesson-content' not in quiz_html
    assert 'data-quiz-runner' in quiz_html
    assert 'quiz-runner-active' in quiz_html


if __name__ == '__main__':
    test_all_lesson_templates_have_no_inline_style()
    test_mensuration_template_has_no_inline_style()
    test_mensuration_route()
    test_migrated_lessons_have_shell_and_keep_mcqs()
    test_every_lesson_route_is_ok()
    test_radioactivity_uses_base_tokens()
    test_no_maxwidth_attribute_selectors()
    test_legacy_unrouted_stubs_are_gone()
    test_no_python_in_templates()
    test_lesson_quiz_page_skips_lesson_progress_chrome()
    print('Lesson unify smoke OK')
