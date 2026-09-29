"""E8 Phase 0 — Zorp expressions: budget ledger baseline, gallery skeleton, decisions.

Run: python scripts/test_zorp_expression_smoke.py

Phase 0 of docs/ZORP_EXPRESSIVENESS.md is scaffolding only (templates, scripts, docs).
This file records the §2.1 budget ledger at its measured baseline and guards the new
`/styleguide#zorp-gallery` section, the dev-only snapshot tool and the recorded
decisions (§7.1). The size asserts are deliberately loose (a disaster guard, not a cap):
Phase 1 lowers each constant to the cap named in its trailing comment and removes
PHASE0_SLACK.
"""
import os

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('PB_STYLEGUIDE', '1')

import argparse
import ast
import fnmatch
import gzip
import importlib.util
import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS_DIR = ROOT / 'static' / 'js'
CSS_DIR = ROOT / 'static' / 'css'
MOTION_CSS = CSS_DIR / 'motion.css'
RUNTIME_JS = JS_DIR / 'zorp-motion.js'
TEMPLATES = ROOT / 'templates'
DOC = ROOT / 'docs' / 'ZORP_EXPRESSIVENESS.md'
SNAPSHOT_TOOL = ROOT / 'scripts' / 'zorp_gallery_snapshot.py'

# §2.1 ledger: Phase 0 baseline, measured 2026-09-29 @4db62e2; Phase 1 lowers each to the
# cap in the trailing comment.
INSTANCE_DEFAULT_MAX_BYTES = 7_249  # Phase 1 target 4_500
INSTANCE_MAX_ELEMENTS = 98  # Phase 1 target 70
INSTANCE_LOOK_MAX_BYTES = 8_344  # Phase 1 target 5_800
PAGE_MASCOT_MAX_BYTES = 21_747  # Phase 1 target 36_000 incl. library + island
PAGE_MASCOT_MAX_GZIP = 1_425  # Phase 1 target 6_000
RUNTIME_JS_MAX_BYTES = 48_000  # new cap; baseline 26_602
PARTS_LIBRARY_MAX_BYTES = 16_000  # not present at baseline
RIG_JSON_MAX_BYTES = 6_000  # not present at baseline
PHASE0_SLACK = 1.25  # disaster guard; delete in Phase 1
MOTION_CSS_BASELINE_BYTES = 4_844  # cap stays at test_zorp_motion_smoke.py:33

GALLERY_FACES = ('nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk',
                 'weak_topic', 'friend_challenge', 'sleep')
BANNED_STRINGS = ('lottie', 'jsdelivr', 'unpkg', 'gsap')
DEFAULT_SVG_START = '<svg class="buddy-mascot" viewBox="0 0 64 64"'


def _elements(svg):
    return len(re.findall(r'<[a-zA-Z]', svg))


def _gz(text):
    return len(gzip.compress(text.encode('utf-8')))


def _fullest_look():
    """Largest buddy_mascot() render over every combination of look fields."""
    from app import app  # noqa: E402
    from models import zorp_kit  # noqa: E402

    names = list(zorp_kit.LOOK_FIELDS)
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        best = ''
        for combo in itertools.product(*(zorp_kit.LOOK_FIELDS[n] for n in names)):
            svg = str(module.buddy_mascot(dict(zip(names, combo))))
            if len(svg.encode('utf-8')) > len(best.encode('utf-8')):
                best = svg
    return best


def _register(client):
    r = client.get('/register')
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.data.decode())
    assert m, 'register page has no csrf token'
    suffix = os.urandom(4).hex()
    client.post(
        '/register',
        data={
            'csrf_token': m.group(1),
            'email': f'zexp_{suffix}@example.com',
            'handle': f'zexp_{suffix}',
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )


def test_no_animation_libraries():
    for directory in (JS_DIR, CSS_DIR):
        for path in sorted(directory.rglob('*')):
            if not path.is_file():
                continue
            text = path.read_text(encoding='utf-8', errors='ignore').lower()
            for banned in BANNED_STRINGS:
                assert banned not in text, (
                    f'{path.relative_to(ROOT)} contains banned string {banned!r} '
                    '(E8 §2 #2: hand-built SVG + WAAPI/CSS only)'
                )
    for name in ('partials/buddy.html', 'partials/zorp_overlays.html'):
        html = (TEMPLATES / name).read_text(encoding='utf-8')
        assert '<animate' not in html, f'{name} uses SMIL <animate> (banned by E8 §2 #2)'


def test_instance_bytes_measured():
    from app import app  # noqa: E402

    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        default_svg = str(module.buddy_mascot())
    look_svg = _fullest_look()
    d_bytes = len(default_svg.encode('utf-8'))
    l_bytes = len(look_svg.encode('utf-8'))
    d_elements = _elements(default_svg)
    print(f'  default instance: {d_bytes} B, {_gz(default_svg)} B gzip, {d_elements} elements')
    print(f'  fullest look:     {l_bytes} B, {_gz(look_svg)} B gzip, {_elements(look_svg)} elements')
    assert default_svg.startswith(DEFAULT_SVG_START), default_svg[:120]
    assert d_bytes <= INSTANCE_DEFAULT_MAX_BYTES * PHASE0_SLACK
    assert d_elements <= INSTANCE_MAX_ELEMENTS * PHASE0_SLACK
    assert l_bytes <= INSTANCE_LOOK_MAX_BYTES * PHASE0_SLACK


def test_page_mascot_bytes_measured():
    from app import app  # noqa: E402

    with app.test_client() as client:
        _register(client)
        r = client.get('/')
        assert r.status_code == 200
        html = r.data.decode()
    found = re.findall(r'<svg class="buddy-mascot".*?</svg>', html, re.S)
    joined = ''.join(found)
    size = len(joined.encode('utf-8'))
    print(f'  logged-in /: {len(found)} mascots, {size} B, {_gz(joined)} B gzip')
    assert 2 <= len(found) <= 4, len(found)
    assert size <= PAGE_MASCOT_MAX_BYTES * PHASE0_SLACK


def test_runtime_sizes_measured():
    css = MOTION_CSS.stat().st_size
    js = RUNTIME_JS.stat().st_size
    print(f'  motion.css: {css} B (baseline {MOTION_CSS_BASELINE_BYTES}); zorp-motion.js: {js} B')
    assert js <= RUNTIME_JS_MAX_BYTES, f'zorp-motion.js {js} B exceeds {RUNTIME_JS_MAX_BYTES}'


def test_gallery_section():
    from app import app  # noqa: E402

    r = app.test_client().get('/styleguide')
    assert r.status_code == 200
    html = r.data.decode()
    for needle in ('id="zorp-gallery"', 'id="sg-zorp-gallery-56"', 'id="sg-zorp-gallery-128"'):
        assert needle in html, needle
    pill_motion = html.index('href="#zorp-motion"')
    pill_gallery = html.index('href="#zorp-gallery"')
    pill_diagrams = html.index('href="#diagrams"')
    assert pill_motion < pill_gallery < pill_diagrams, 'gallery pill must sit between Zorp motion and Diagrams'
    for face in GALLERY_FACES:
        assert html.count(f'data-gallery-face="{face}"') == 2, face
    start = html.index('id="zorp-gallery"')
    section = html[start:html.index('</section>', start)]
    assert 'data-zorp-demo' not in section, 'gallery faces must stay unbound to pbZorp'
    assert 'data-zorp-autoplay' not in section, 'gallery faces must not autoplay'


def test_snapshot_tool_is_dev_only():
    assert SNAPSHOT_TOOL.is_file(), 'scripts/zorp_gallery_snapshot.py is missing'
    assert not fnmatch.fnmatch(SNAPSHOT_TOOL.name, 'test_*_smoke.py'), (
        'the snapshot tool must not be picked up by run_smoke_tests.py'
    )
    ignore = (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()
    assert 'data/zorp_gallery/' in [line.strip() for line in ignore], '.gitignore lacks data/zorp_gallery/'
    reqs = (ROOT / 'requirements.txt').read_text(encoding='utf-8').lower()
    assert 'playwright' not in reqs and 'pillow' not in reqs, 'dev-only deps must stay out of requirements.txt'
    # Top-level statements only: Playwright/Pillow imports must be lazy (inside functions)
    # so the tool still exits 0 in an interpreter that lacks them.
    tree = ast.parse(SNAPSHOT_TOOL.read_text(encoding='utf-8'))
    for node in tree.body:
        if isinstance(node, ast.Import):
            mods = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            mods = [node.module or '']
        else:
            continue
        assert not any(m.split('.')[0] in ('playwright', 'PIL') for m in mods), (
            'Playwright/Pillow must be imported lazily so the tool exits 0 without them'
        )


def test_snapshot_label_guard():
    # The tool deletes the output directory it writes to, so a label must never be able to
    # resolve to data/, data/zorp_gallery or anywhere outside data/zorp_gallery/<label>.
    spec = importlib.util.spec_from_file_location('zorp_gallery_snapshot', SNAPSHOT_TOOL)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    for bad in ('.', '..', '...', '../x', 'a/b', 'a\\b', '', '-x', '.hidden', 'x' * 41):
        try:
            tool._label(bad)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError(f'label {bad!r} should have been rejected')
    for good in ('baseline', 'phase1', 'v1.2-rc_3'):
        assert tool._label(good) == good
        out = tool._out_dir(good)
        assert out.parent == tool.OUT_ROOT.resolve()
    for bad in ('..', '.', '../x'):
        try:
            tool._out_dir(bad)
        except SystemExit:
            continue
        raise AssertionError(f'_out_dir({bad!r}) should refuse to resolve outside OUT_ROOT')


def test_decisions_recorded():
    lines = DOC.read_text(encoding='utf-8').splitlines()
    text = '\n'.join(lines)
    assert '### 7.1 Decisions confirmed 2026-09-29' in text
    assert 'Q4 profile/rank/nudge: **yes**' in text
    assert 'Proposed' not in lines[2], 'status line still says Proposed'


def main():
    test_no_animation_libraries()
    test_instance_bytes_measured()
    test_page_mascot_bytes_measured()
    test_runtime_sizes_measured()
    test_gallery_section()
    test_snapshot_tool_is_dev_only()
    test_snapshot_label_guard()
    test_decisions_recorded()
    print('Zorp expression smoke (E8 Phase 0) passed.')


if __name__ == '__main__':
    main()
