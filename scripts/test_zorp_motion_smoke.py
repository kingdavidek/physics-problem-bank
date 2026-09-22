"""E7 Phase 0 — Zorp motion package skeleton smoke.

Run: python scripts/test_zorp_motion_smoke.py

This is the Phase 0 "spec freeze + gate" smoke from docs/MASCOT_MOTION_AND_ONBOARDING.md
§5. It pins the constraints frozen in §2 before any motion code exists:

* no third-party animation library or CDN anywhere in static/js or static/css
  (E6 §2 #3/#10, E7 §2 #12 — Lottie/GSAP/Rive/jsdelivr/unpkg stay banned);
* once static/css/motion.css exists (Phase 1), every @keyframes block in it has
  a matching rule inside a reduced-motion block, and the file stays <= 8 KB
  (E7 §2 #8/§5 Phase 0).

The motion.css checks are skipped-but-reported until Phase 1 adds the file —
this is the "skeleton" Phase 0 asks for, not a false pass. Do not relax the
banned-library check to make this file "pass early"; it should already pass
today because nothing in the repo uses these libraries.
"""
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
    if not MOTION_CSS.exists():
        print('motion.css does not exist yet (Phase 1) — skeleton check skipped, not failed.')
        return
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


def main():
    test_no_third_party_animation_library()
    test_motion_css_keyframes_pair_with_reduced_motion()
    print('Zorp motion Phase 0 skeleton smoke passed.')


if __name__ == '__main__':
    main()
