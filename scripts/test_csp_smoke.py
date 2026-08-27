"""CSP / S2 hardening smoke — run: python scripts/test_csp_smoke.py"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-csp-smoke')

from app import app  # noqa: E402

INLINE_SCRIPT = re.compile(r'<script(?![^>]*\bsrc=)([^>]*)>', re.I)
SCRIPT_SRC = re.compile(r"script-src ([^;]+)")


def _script_src(csp: str) -> str:
    match = SCRIPT_SRC.search(csp or '')
    assert match, csp
    return match.group(1)


def main():
    templates = ROOT / 'templates'
    for path in templates.rglob('*.html'):
        src = path.read_text(encoding='utf-8')
        assert 'onclick=' not in src.lower(), path.name
        assert 'oninput=' not in src.lower(), path.name
        assert 'onchange=' not in src.lower(), path.name
        assert 'pythonanywhere.com' not in src, path.name
        assert 'cdn.jsdelivr.net' not in src, path.name

    with app.test_client() as client:
        r = client.get('/')
        assert r.status_code == 200
        csp = r.headers.get('Content-Security-Policy') or ''
        script_src = _script_src(csp)
        assert "'unsafe-inline'" not in script_src, script_src
        assert "'nonce-" in script_src
        assert 'cdn.jsdelivr.net' not in csp
        assert "'unsafe-eval'" in script_src
        assert "'wasm-unsafe-eval'" in script_src
        html = r.data.decode()
        for tag in INLINE_SCRIPT.findall(html):
            assert 'application/json' in tag.lower(), tag
        assert 'cdn.jsdelivr.net' not in html
        assert 'vendor/mathjax/tex-svg.js' in html

        r = client.get('/topic/gcse/cs/python_programming')
        assert r.status_code == 200, r.data[:300]
        html = r.data.decode()
        assert 'python-programming-lesson.js' in html
        assert 'onclick=' not in html.lower()
        assert 'cdn.jsdelivr.net' not in html
        assert 'pythonanywhere.com' not in html

    print('CSP smoke tests passed.')


if __name__ == '__main__':
    main()
