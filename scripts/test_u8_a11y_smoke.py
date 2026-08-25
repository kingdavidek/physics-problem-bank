"""U8.3 / U8.6 — chrome a11y and CSS budget.

Run: python scripts/test_u8_a11y_smoke.py
"""
import os
import sys
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402

CSS_DIR = ROOT / 'static' / 'css'
LESSON_ONLY = {'lesson-pages.css', 'lesson-assist.css'}
# Uncompressed tree is larger than the original 60KB stretch; fail if it grows.
CSS_BUDGET_BYTES = 210_000
# Core sheets loaded on every page after the U8.6 lesson split.
# Measured ~184KB; leave a little room for token/component tweaks.
CSS_CORE_BUDGET_BYTES = 190_000


def test_tab_bar_aria_current():
    client = app.test_client()
    html = client.get('/').data.decode()
    assert 'id="app-tab-bar"' in html
    assert 'aria-label="Main navigation"' in html
    assert 'aria-current="page"' in html


def test_profile_tablist_markup():
    src = (ROOT / 'templates' / 'profile.html').read_text(encoding='utf-8')
    assert 'role="tablist"' in src
    assert 'aria-orientation="horizontal"' in src
    assert 'role="tab"' in src


def test_css_budget():
    files = sorted(CSS_DIR.glob('*.css'))
    total = sum(path.stat().st_size for path in files)
    core = sum(path.stat().st_size for path in files if path.name not in LESSON_ONLY)
    print(f'CSS uncompressed {total} bytes across {len(files)} files (core {core})')
    assert files, 'missing static/css'
    assert (CSS_DIR / 'lesson-pages.css').is_file()
    assert total <= CSS_BUDGET_BYTES, f'{total} exceeds {CSS_BUDGET_BYTES}'
    assert core <= CSS_CORE_BUDGET_BYTES, f'core {core} exceeds {CSS_CORE_BUDGET_BYTES}'


def test_lesson_pages_css_is_route_only():
    client = app.test_client()
    home = client.get('/').data.decode()
    assert 'lesson-pages.css' not in home
    lesson = client.get('/topic/gcse/maths/mensuration')
    assert lesson.status_code == 200
    html = lesson.data.decode()
    assert 'lesson-pages.css' in html
    assert html.index('pages.css') < html.index('lesson-pages.css')


def test_card_vocabulary_and_mcq_letter_markup():
    components = (ROOT / 'static' / 'css' / 'components.css').read_text(encoding='utf-8')
    assert '.card-raised' in components
    assert '.card-tinted' in components
    practice = (ROOT / 'static' / 'css' / 'practice.css').read_text(encoding='utf-8')
    assert '.mcq-letter' in practice
    assert '.mcq-btn[data-letter]::before' not in practice
    js = (ROOT / 'static' / 'js' / 'site.js').read_text(encoding='utf-8')
    assert 'decorateMcqButton' in js
    assert 'mcq-letter' in js
    sg = (ROOT / 'templates' / 'styleguide.html').read_text(encoding='utf-8')
    assert 'class="card card-raised"' in sg
    assert 'class="mcq-letter"' in sg


def main():
    test_tab_bar_aria_current()
    test_profile_tablist_markup()
    test_css_budget()
    test_lesson_pages_css_is_route_only()
    test_card_vocabulary_and_mcq_letter_markup()
    print('U8 a11y / CSS budget smoke OK')


if __name__ == '__main__':
    main()
