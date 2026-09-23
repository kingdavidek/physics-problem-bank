"""E7 Phase 1 — Zorp rig + motion runtime + idle smoke.

Run: python scripts/test_zorp_motion_smoke.py

Phase 0 froze the constraints in docs/MASCOT_MOTION_AND_ONBOARDING.md §2/§5:

* no third-party animation library or CDN anywhere in static/js or static/css
  (E6 §2 #3/#10, E7 §2 #12 — Lottie/GSAP/Rive/jsdelivr/unpkg stay banned);
* every @keyframes block in motion.css has a matching rule inside a
  reduced-motion block, and the file stays <= 8 KB (E7 §2 #8/§2 #11).

Phase 1 adds the rig groups in templates/partials/buddy.html, the pivots and
CSS idle loop in static/css/motion.css, and the window.pbZorp runtime in
static/js/zorp-motion.js. This file keeps the Phase 0 checks (which now
actually run, rather than being skipped-but-reported) and adds the Phase 1
checks below.
"""
import os

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('PB_STYLEGUIDE', '1')

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS_DIR = ROOT / 'static' / 'js'
CSS_DIR = ROOT / 'static' / 'css'
MOTION_CSS = CSS_DIR / 'motion.css'
MOTION_CSS_BUDGET_BYTES = 8_000

BANNED_STRINGS = ('lottie', 'jsdelivr', 'unpkg')

RUNTIME_JS = JS_DIR / 'zorp-motion.js'
BUDDY_PARTIAL = ROOT / 'templates' / 'partials' / 'buddy.html'
BASE_HTML = ROOT / 'templates' / 'base.html'
API_NAMES = ('bind', 'play', 'idle', 'setFace', 'motionLevel')
PHASE1_CLIPS = ('idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake')
RIG_CLASSES = ('buddy-root', 'buddy-shadow', 'buddy-arm--l', 'buddy-arm--r', 'buddy-body',
               'buddy-head', 'buddy-antenna--l', 'buddy-antenna--r', 'buddy-pupil',
               'buddy-foot--l', 'buddy-foot--r')


def test_no_third_party_animation_library():
    for directory in (JS_DIR, CSS_DIR):
        for path in sorted(directory.rglob('*')):
            if not path.is_file():
                continue
            text = path.read_text(encoding='utf-8', errors='ignore').lower()
            for banned in BANNED_STRINGS:
                assert banned not in text, (
                    f'{path.relative_to(ROOT)} contains banned string {banned!r} '
                    '(E6 §2 #3/#10, E7 §2 #12 ban Lottie/GSAP/Rive/CDN loads)'
                )


def _extract_reduced_motion_block(css):
    """Return the text inside `@media (prefers-reduced-motion: reduce) { ... }`,
    matching braces properly rather than assuming the block is last in the file
    (motion.css is also expected to hold transform-box rules per E7 §3.1, which
    may come after the reduced-motion block)."""
    marker = re.search(r'@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{', css)
    if not marker:
        return ''
    start = marker.end()
    depth = 1
    i = start
    while i < len(css) and depth:
        if css[i] == '{':
            depth += 1
        elif css[i] == '}':
            depth -= 1
        i += 1
    return css[start:i - 1]


def test_motion_css_keyframes_pair_with_reduced_motion():
    # Phase 1 created motion.css, so this is no longer a skeleton check that can
    # be skipped-but-reported: a missing file here is a real regression.
    assert MOTION_CSS.exists(), 'motion.css missing (Phase 1)'
    css = MOTION_CSS.read_text(encoding='utf-8')
    size = len(css.encode('utf-8'))
    assert size <= MOTION_CSS_BUDGET_BYTES, (
        f'motion.css is {size} bytes, exceeds the {MOTION_CSS_BUDGET_BYTES} byte cap '
        '(E7 §2 #8/§2 #11 — raise deliberately, in the same commit, with a recorded reason)'
    )
    keyframe_names = re.findall(r'@keyframes\s+([\w-]+)', css)
    assert keyframe_names, 'motion.css exists but defines no @keyframes'
    reduced_block = _extract_reduced_motion_block(css)
    for name in keyframe_names:
        assert name in reduced_block or f'{name}-reduced' in css, (
            f'@keyframes {name} in motion.css has no matching reduced-motion variant '
            '(E7 §2 #3 — every clip needs a reduced-motion fallback)'
        )


def test_runtime_exposes_api():
    js = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'window.pbZorp' in js
    for name in API_NAMES:
        assert re.search(r'\b' + name + r'\s*:', js), f'pbZorp.{name} missing'
    for clip in PHASE1_CLIPS:
        assert f"'{clip}'" in js, f'clip {clip} missing from CLIP_NAMES'
    assert '.animate(' in js                          # WAAPI (§2 #2)
    assert 'prefers-reduced-motion' in js             # §2 #3
    assert 'visibilitychange' in js                   # idle pauses when hidden
    assert 'onclick' not in js.lower()


def test_rig_markup():
    buddy = BUDDY_PARTIAL.read_text(encoding='utf-8')
    for cls in RIG_CLASSES:
        assert cls in buddy, cls
    assert buddy.count('class="buddy-pupil"') == 11
    root = buddy.index('class="buddy-root"')
    arm = buddy.index('buddy-arm--l')
    head = buddy.index('<g class="buddy-head">')
    foot = buddy.index('buddy-foot--l')
    assert root < arm < head < foot   # arms behind body, feet painted over it
    assert 'aria-hidden="true"' in buddy
    body = buddy.index('class="buddy-body"')
    head_close = buddy.index('{# /buddy-head #}')
    assert head < body < head_close   # body nested inside head (D5 #1)
    assert head_close < foot          # feet painted after the head closes


def test_motion_css_rig_pivots():
    if not MOTION_CSS.exists():
        raise AssertionError('motion.css missing (Phase 1)')
    css = MOTION_CSS.read_text(encoding='utf-8')
    m = re.search(r'([^{}]+)\{\s*transform-box:\s*fill-box;\s*\}', css)
    assert m, 'motion.css needs a transform-box: fill-box rule'
    for sel in ('.buddy-antenna--l', '.buddy-antenna--r', '.buddy-foot--l', '.buddy-foot--r',
                '.buddy-arm--l', '.buddy-arm--r', '.buddy-pupil', '.buddy-root'):
        assert sel in m.group(1), f'{sel} lacks transform-box: fill-box (Phase 1.5 depends on it)'
    for name in ('pb-zorp-wink', 'pb-zorp-nod', 'pb-zorp-shake', 'pb-zorp-tap'):
        assert name not in css   # E6 keyframes stay in chrome.css only


def test_base_loads_motion_assets():
    base = BASE_HTML.read_text(encoding='utf-8')
    assert base.index('css/chrome.css') < base.index('css/motion.css') < base.index('css/practice.css')
    assert base.index('js/zorp-motion.js') < base.index('js/study-buddy.js')


def test_dev_motion_sections():
    from app import app  # noqa: E402
    client = app.test_client()
    for path, demo_id in (('/styleguide', 'sg-zorp-motion'), ('/guide-preview', 'guide-preview-motion')):
        r = client.get(path)
        assert r.status_code == 200, path
        html = r.data.decode()
        assert f'id="{demo_id}"' in html
        assert 'zorp-motion.js' in html
        assert 'css/motion.css' in html
        assert 'buddy-arm--l' in html and 'buddy-pupil' in html
        for clip in PHASE1_CLIPS:
            assert f'data-zorp-clip="{clip}"' in html, (path, clip)
        assert 'onclick=' not in html.lower()


def main():
    test_no_third_party_animation_library()
    test_motion_css_keyframes_pair_with_reduced_motion()
    test_runtime_exposes_api()
    test_rig_markup()
    test_motion_css_rig_pivots()
    test_base_loads_motion_assets()
    test_dev_motion_sections()
    print('Zorp motion Phase 1 smoke passed.')


if __name__ == '__main__':
    main()
