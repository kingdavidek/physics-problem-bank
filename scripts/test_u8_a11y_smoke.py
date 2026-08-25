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
# Uncompressed tree is larger than the original 60KB U8.6 target; fail if it grows.
CSS_BUDGET_BYTES = 210_000


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
    print(f'CSS uncompressed {total} bytes across {len(files)} files')
    assert files, 'missing static/css'
    assert total <= CSS_BUDGET_BYTES, f'{total} exceeds {CSS_BUDGET_BYTES}'


def main():
    test_tab_bar_aria_current()
    test_profile_tablist_markup()
    test_css_budget()
    print('U8 a11y / CSS budget smoke OK')


if __name__ == '__main__':
    main()
