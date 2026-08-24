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
        if path.name == RADIOACTIVITY:
            continue
        src = path.read_text(encoding='utf-8')
        assert 'class="lesson-shell"' in src, path.name
        assert src.count('class="mcq-inline"') == src.count('data-correct='), path.name


def test_every_lesson_route_is_ok():
    client = app.test_client()
    for path in sorted((ROOT / 'templates').glob('*_lesson.html')):
        if path.name == RADIOACTIVITY:
            continue
        match = FILENAME_RE.match(path.name)
        assert match, path.name
        level, subject, topic = match.groups()
        url = f'/topic/{level}/{subject}/{topic}'
        response = client.get(url)
        assert response.status_code == 200, f'{url} -> {response.status_code}'
        html = response.data.decode()
        src = path.read_text(encoding='utf-8')
        if path.name != RADIOACTIVITY:
            assert 'lesson-shell' in html, url
        assert html.count('mcq-inline') == src.count('class="mcq-inline"'), url


if __name__ == '__main__':
    test_mensuration_template_has_no_inline_style()
    test_mensuration_route()
    test_migrated_lessons_have_shell_and_keep_mcqs()
    test_every_lesson_route_is_ok()
    print('Lesson unify smoke OK')
