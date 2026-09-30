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
MOTION_CSS_BUDGET_BYTES = 12_000  # E8 Phase 1: raised from 8_000 (docs/ZORP_EXPRESSIVENESS.md 2.1); measured 7_895 after Phase 3

BANNED_STRINGS = ('lottie', 'jsdelivr', 'unpkg')

RUNTIME_JS = JS_DIR / 'zorp-motion.js'
BUDDY_PARTIAL = ROOT / 'templates' / 'partials' / 'buddy.html'
BASE_HTML = ROOT / 'templates' / 'base.html'
API_NAMES = ('bind', 'play', 'idle', 'setFace', 'setExpression', 'hasExpression', 'valenceOf', 'allowedIn', 'motionLevel', 'react', 'turn')
PHASE1_CLIPS = ('idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake')
PHASE2_CLIPS = PHASE1_CLIPS + ('hop',)
PHASE4_CLIPS = PHASE2_CLIPS + ('peek', 'sleep')
CELEBRATE_JS = JS_DIR / 'celebrate.js'
SOUND_JS = JS_DIR / 'sound.js'
QUIZ_RUNNER_JS = JS_DIR / 'quiz-runner.js'
PRACTICE_CSS = CSS_DIR / 'practice.css'
RIG_CLASSES = ('buddy-root', 'buddy-shadow', 'buddy-arm--l', 'buddy-arm--r', 'buddy-body',
               'buddy-head', 'buddy-antenna--l', 'buddy-antenna--r',
               'buddy-foot--l', 'buddy-foot--r')   # buddy-pupil now lives in partials/zorp_parts.html (E8)


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


def _strip_css_comments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def _media_block_text(css, query):
    """Text inside every `@media (<query>) { ... }` block (braces matched), joined."""
    out = []
    for marker in re.finditer(r'@media\s*\(' + re.escape(query) + r'\)\s*\{', css):
        depth, i = 1, marker.end()
        while i < len(css) and depth:
            depth += {'{': 1, '}': -1}.get(css[i], 0)
            i += 1
        out.append(css[marker.end():i - 1])
    return '\n'.join(out)


def test_motion_css_keyframes_pair_with_reduced_motion():
    # Phase 1 created motion.css, so this is no longer a skeleton check that can
    # be skipped-but-reported: a missing file here is a real regression.
    assert MOTION_CSS.exists(), 'motion.css missing (Phase 1)'
    raw = MOTION_CSS.read_text(encoding='utf-8')
    size = len(raw.encode('utf-8'))
    assert size <= MOTION_CSS_BUDGET_BYTES, (
        f'motion.css is {size} bytes, exceeds the {MOTION_CSS_BUDGET_BYTES} byte cap '
        '(E7 §2 #8/§2 #11, E8 §2 #7 — raise deliberately, in the same commit, with a recorded reason)'
    )
    # E8 Phase 2 review fix: comments never count. A keyframe that is only *mentioned* in a
    # comment inside the reduced block used to pass this test.
    css = _strip_css_comments(raw)
    keyframe_names = re.findall(r'@keyframes\s+([\w-]+)', css)
    assert keyframe_names, 'motion.css exists but defines no @keyframes'
    reduced_block = _media_block_text(css, 'prefers-reduced-motion: reduce')
    enabled_block = _media_block_text(css, 'prefers-reduced-motion: no-preference')
    for name in keyframe_names:
        uses = re.findall(r'[^{}]*\{[^{}]*animation:\s*' + re.escape(name) + r'\b[^{}]*\}', css)
        assert uses, f'@keyframes {name} is never used by an animation: declaration'
        in_reduced = name in reduced_block  # e.g. zorp-pulse: the reduced fallback itself
        # otherwise every use must be switched on only under no-preference (so reduced motion
        # never runs it) and must be switched off by an `animation: none` rule in the reduced block
        gated = all(use.strip() in enabled_block or use.strip() in reduced_block for use in uses)
        assert in_reduced or (gated and 'animation: none' in reduced_block), (
            f'@keyframes {name} in motion.css has no matching reduced-motion variant '
            '(E7 §2 #3 — every clip needs a reduced-motion fallback)'
        )


def test_runtime_exposes_api():
    js = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'window.pbZorp' in js
    for name in API_NAMES:
        assert re.search(r'\b' + name + r'\s*:', js), f'pbZorp.{name} missing'
    for clip in PHASE2_CLIPS:
        assert f"'{clip}'" in js, f'clip {clip} missing from CLIP_NAMES'
    assert '.animate(' in js                          # WAAPI (§2 #2)
    assert 'prefers-reduced-motion' in js             # §2 #3
    assert 'visibilitychange' in js                   # idle pauses when hidden
    assert 'onclick' not in js.lower()


def test_rig_markup():
    buddy = BUDDY_PARTIAL.read_text(encoding='utf-8')
    for cls in RIG_CLASSES:
        assert cls in buddy, cls
    # E8 Phase 1: the seven hard-coded faces (11 pupil groups) are gone; pupils come from the
    # eye parts, so the default render has exactly two and buddy.html itself has none.
    assert 'class="buddy-pupil"' not in buddy
    parts = (ROOT / 'templates' / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    assert 'class="buddy-pupil"' in parts
    from app import app  # noqa: E402
    with app.app_context():
        default_svg = str(app.jinja_env.get_template('partials/buddy.html').module.buddy_mascot())
    assert default_svg.count('class="buddy-pupil"') == 2
    assert 'class="zorp-face"' in buddy and 'zorp-slot--mouth' in buddy
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
    # E8 Phase 3: the arms left the fill-box list on purpose. They are pivot groups now: the shoulder
    # is the group origin (transform-box: view-box; transform-origin: 0 0), so the clip angles stay
    # exactly as they were. .zorp-plate joined (the plate is scaled by the views).
    for sel in ('.buddy-antenna--l', '.buddy-antenna--r', '.buddy-foot--l', '.buddy-foot--r',
                '.zorp-plate', '.buddy-pupil', '.buddy-root'):
        assert sel in m.group(1), f'{sel} lacks transform-box: fill-box (Phase 1.5 depends on it)'
    assert '.buddy-arm--l' not in m.group(1) and '.buddy-arm--r' not in m.group(1)
    arm = re.search(r'\.buddy-arm\s*\{([^}]*)\}', css)
    assert arm and 'transform-box:view-box' in arm.group(1).replace(' ', '') and 'transform-origin:0 0' in arm.group(1).replace(': ', ':'), \
        'arm pivot groups need transform-box: view-box; transform-origin: 0 0'
    flip = re.search(r'\.zorp-flip\s*\{([^}]*)\}', css)
    assert flip and 'view-box' in flip.group(1) and '32px 0' in flip.group(1), 'the flip wrapper pivots at x = 32'
    assert re.search(r'\.buddy-arm--l-front,\s*\.buddy-arm--r-front\s*\{\s*display:\s*none', css), 'front-layer arms are hidden in the front view'
    for name in ('pb-zorp-wink', 'pb-zorp-nod', 'pb-zorp-shake', 'pb-zorp-tap'):
        assert name not in css   # E6 keyframes stay in chrome.css only


def test_arm_pivot_groups():
    # E8 Phase 3: each arm is <g transform="translate(shoulder)"><g class="buddy-arm ..."><path d="M0 0..."/></g></g>
    # (twice: back layer and front layer), so the clip rotates about the shoulder with no fill-box maths.
    from app import app  # noqa: E402
    with app.app_context():
        svg = str(app.jinja_env.get_template('partials/buddy.html').module.buddy_mascot())
    for cls, x in (('buddy-arm--l', '15.6'), ('buddy-arm--r', '48.4'), ('buddy-arm--l-front', '15.6'), ('buddy-arm--r-front', '48.4')):
        m = re.search(r'<g transform="translate\(' + re.escape(x) + r' 40\)"><g class="buddy-arm ' + cls + r'"[^>]*><path d="(M[^"]*)"', svg)
        assert m, f'{cls}: no pivot group at translate({x} 40)'
        assert m.group(1).startswith('M0 0'), f'{cls}: arm path must be re-based to M0 0'
    # the front layer is painted after the feet, the back layer before the head
    assert svg.index('buddy-arm--l"') < svg.index('buddy-head') < svg.index('buddy-foot--r') < svg.index('buddy-arm--l-front')


def test_ambient_fx_outside_flip():
    # E8 Phase 3: the mirror wrapper never contains the ambient slot (? ! zzz and the thought bubble never mirror).
    from app import app  # noqa: E402
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        for kwargs in ({}, {'view': 'side', 'facing': 'l'}, {'view': 'back', 'facing': 'l'}, {'view': 'three-quarter', 'facing': 'l'}):
            svg = str(module.buddy_mascot(face='thinking', **kwargs))
            flip_open = svg.index('class="zorp-flip"')
            fx = svg.index('zorp-slot--fx"')
            assert svg.count('class="zorp-flip"') == 1
            assert flip_open < svg.index('buddy-head') < svg.index('buddy-foot--r') < fx, kwargs
            # nothing after the flip wrapper's own closing tag but the ambient slot and the root closes
            tail = svg[fx:]
            assert tail.count('<g') >= 1 and 'zorp-flip' not in tail and 'buddy-foot' not in tail
    # flip depth: walk the tags and check the ambient slot is at the depth of the flip, not inside it
    with app.app_context():
        svg = str(app.jinja_env.get_template('partials/buddy.html').module.buddy_mascot(face='thinking', view='side', facing='l'))
    depth, stack = 0, []
    for tag in re.finditer(r'<(/?)g\b[^>]*>', svg):
        if tag.group(1):
            stack.pop()
        else:
            stack.append(tag.group(0))
            if 'zorp-slot--fx"' in tag.group(0):
                assert not any('zorp-flip' in t for t in stack[:-1]), 'ambient fx is inside the flip'
                assert any('buddy-root' in t for t in stack[:-1])


def test_existing_arm_clips_unchanged():
    # E8 Phase 3 structural guard: the arm pivots moved, the clip angles did not. Every rotate() literal of the
    # Phase 2 runtime is still present, the same number of times (measured from the committed 06e72f1 runtime).
    js = RUNTIME_JS.read_text(encoding='utf-8')
    expected = {
        '-1.5': 1, '-100': 1, '-105': 1, '-10': 2, '-115': 1, '-14': 1, '-25': 2, '-35': 2, '-4': 2, '-5': 1,
        '-6': 2, '-80': 4, '-8': 2, '-95': 2, '0': 38, '100': 1, '115': 1, '12': 2, '14': 1, '3': 3, '4': 2,
        '6': 5, '80': 2,
    }
    for deg, count in expected.items():
        found = js.count(f"rotate({deg}deg)")
        assert found >= count, f'rotate({deg}deg): {found} < {count} (an existing clip angle changed)'


def test_base_loads_motion_assets():
    base = BASE_HTML.read_text(encoding='utf-8')
    assert base.index('css/chrome.css') < base.index('css/motion.css') < base.index('css/practice.css')
    assert base.index('js/zorp-motion.js') < base.index('js/study-buddy.js')


def test_buddy_face_persists_without_hidden_root():
    # Buddy quiet fix (2026-09-27): the corner Zorp face must stay visible (and thus
    # reactTarget()-eligible) even when there is nothing for the bubble to say, so a
    # logged-in user with no prompt still gets a rendered, non-hidden aside -- only the
    # card starts hidden.
    from app import app  # noqa: E402
    from models.user import User  # noqa: E402

    with app.test_client() as client:
        r = client.get('/register')
        m = re.search(r'name="csrf_token" value="([^"]+)"', r.data.decode())
        assert m
        suffix = os.urandom(4).hex()
        client.post(
            '/register',
            data={
                'csrf_token': m.group(1),
                'email': f'zmp_face_{suffix}@example.com',
                'handle': f'zmpface_{suffix}',
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        r = client.get('/profile')
        assert r.status_code == 200
        html = r.data.decode()
        aside_m = re.search(r'<aside id="study-buddy"[^>]*>', html)
        assert aside_m, 'expected the study-buddy aside on the profile page'
        aside_tag = aside_m.group(0)
        assert ' hidden' not in aside_tag, aside_tag
        assert 'data-buddy-state="face"' in aside_tag
        card_m = re.search(r'<div class="study-buddy-card"[^>]*>', html)
        assert card_m and 'hidden' in card_m.group(0)
        # The face element sits outside the card, so it stays rendered (and thus
        # findable by reactTarget()'s getClientRects() check) regardless of the
        # card's hidden state.
        face_m = re.search(r'<span class="study-buddy-face"[^>]*>', html)
        assert face_m and not re.search(r'(?<!aria-)\bhidden\b', face_m.group(0))


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
        for clip in PHASE2_CLIPS:
            assert f'data-zorp-clip="{clip}"' in html, (path, clip)
        assert 'onclick=' not in html.lower()
    r = client.get('/styleguide')
    styleguide_html = r.data.decode()
    for kind in ('correct', 'wrong', 'streak', 'milestone', 'lesson_complete', 'first_correct'):
        assert f'data-zorp-react="{kind}"' in styleguide_html, kind


def test_cosmetic_css():
    from models.zorp_kit import LOOK_ANTENNAE, LOOK_COLOURS, LOOK_FEET, LOOK_MOUTHS

    css = MOTION_CSS.read_text(encoding='utf-8')
    for prop in ('--zorp-body', '--zorp-accent', '--zorp-limb'):
        assert prop in css, f'{prop} missing from motion.css'
    for colour in LOOK_COLOURS:
        assert f'data-zorp-colour="{colour}"' in css, colour
    for antenna in LOOK_ANTENNAE:
        assert f'data-zorp-antenna="{antenna}"' in css, antenna
    for feet in LOOK_FEET:
        assert f'data-zorp-feet="{feet}"' in css, feet
    # E8 Phase 1: the look's mouth is chosen server-side (zorp_rig.parts_for), not by CSS.
    from models import zorp_rig
    for mouth in LOOK_MOUTHS:
        assert mouth in zorp_rig.CHANNELS['mouth'], mouth
    assert 'buddy-mouth' not in css
    assert not re.search(r'--brand-\d+\s*:', css), (
        'motion.css must never redefine --brand-*, only read it as a var() fallback'
    )
    for attr in ('data-zorp-antenna', 'data-zorp-feet'):
        m = re.search(re.escape(attr) + r'="[^"]+"\][^{]*\{([^}]*)\}', css)
        assert m and 'scale:' in m.group(1) and 'transform:' not in m.group(1), (
            f'{attr} rule must use the `scale` property, not `transform`'
        )
    keyframe_m = re.search(r'@keyframes\s+zorp-pulse\s*\{([^}]*\{[^}]*\}[^}]*)\}', css, re.S)
    assert keyframe_m, 'zorp-pulse keyframe missing'
    body = keyframe_m.group(1)
    assert '--zorp-body' in body and '--zorp-accent' in body, (
        'zorp-pulse must read --zorp-body/--zorp-accent so a recoloured Zorp keeps its colour on the reduced-motion cheer'
    )


def test_cosmetic_markup():
    buddy = BUDDY_PARTIAL.read_text(encoding='utf-8')
    for bare in ('var(--brand-400)"', 'var(--brand-500)"', 'var(--brand-700)"'):
        assert bare not in buddy, f'bare {bare} should be var(--zorp-X, {bare}'
    # E8 Phase 1: the smile/grin/cat swap is a mouth variant drawn by zorp_parts.html.
    assert 'data-mouth=' in buddy
    assert "buddy_mascot(look=none, face='nudge', view='front', facing='r')" in buddy   # E8 Phase 3 signature
    parts = (ROOT / 'templates' / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    for name in ('smile', 'grin', 'cat'):
        assert f"n == '{name}'" in parts, name
    from app import app  # noqa: E402
    from models import zorp_kit
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        plain = str(module.buddy_mascot())
        grin = str(module.buddy_mascot(zorp_kit.live_look('jump')))
        cat = str(module.buddy_mascot(zorp_kit.live_look('wave')))
        sleepy = str(module.buddy_mascot(zorp_kit.live_look('jump'), face='sleep'))
    assert 'q6.5 5.4 13 0' in grin and 'q6.5 5.4 13 0' not in plain
    assert 'M26 44.6q3-2.6 6-.4' in cat
    assert 'q6.5 5.4 13 0' not in sleepy, 'a look mouth replaces the resting (nudge) mouth only'


def test_default_render_has_no_look():
    from app import app  # noqa: E402
    from models import zorp_kit

    default_svg = '<svg class="buddy-mascot" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        for look in (None, {}, zorp_kit.live_look('idle'), zorp_kit.live_look('not-a-real-pose')):
            rendered = str(module.buddy_mascot(look))
            assert rendered.startswith(default_svg), rendered[:120]
            assert 'data-zorp-' not in rendered.split('>', 1)[0] + '>'
            assert 'data-mouth' not in rendered.split('>', 1)[0] + '>'
            assert 'zorp-hat' not in rendered
            assert 'zorp-shoe' not in rendered
        rendered = str(module.buddy_mascot(zorp_kit.live_look('jump')))
        assert 'data-zorp-colour="sunny"' in rendered
        assert 'data-zorp-antenna="long"' in rendered
        assert 'data-zorp-feet="big"' in rendered
        assert 'data-mouth="grin"' in rendered
        # E7 Phase 1.6
        assert rendered.count('zorp-shoe--sneakers') == 2
        rendered = str(module.buddy_mascot(zorp_kit.live_look('scholar')))
        assert 'zorp-hat--mortarboard' in rendered


def test_overlay_rig_wiring():
    # E7 Phase 1.6: hat is the last thing inside the head group; shoes are
    # painted after the head closes, one per foot, left-then-right.
    buddy = BUDDY_PARTIAL.read_text(encoding='utf-8')
    last_face_idx = buddy.index('class="zorp-face"')
    hat_call_idx = buddy.index('zorp_hat(look.hat')
    head_close_idx = buddy.index('{# /buddy-head #}')
    assert last_face_idx < hat_call_idx < head_close_idx

    foot_l_idx = buddy.index('buddy-foot--l')
    foot_r_idx = buddy.index('buddy-foot--r')
    shoe_l_idx = buddy.index('zorp_shoe(look.shoes, 24')
    shoe_r_idx = buddy.index('zorp_shoe(look.shoes, 40')
    assert head_close_idx < foot_l_idx < shoe_l_idx < foot_r_idx < shoe_r_idx

    assert '{% if look.hat %}' in buddy
    assert '{% if look.shoes %}' in buddy

    motion_css = MOTION_CSS.read_text(encoding='utf-8')
    assert 'zorp-hat' not in motion_css
    assert 'zorp-shoe' not in motion_css


def _extract_function_span(js, fn_name):
    """Return (start, end) character offsets covering `function fn_name(...) { ... }`
    in `js`, matched by brace depth rather than assuming it is the last function."""
    m = re.search(r'function\s+' + re.escape(fn_name) + r'\s*\([^)]*\)\s*\{', js)
    assert m, f'function {fn_name} not found'
    start = m.start()
    depth = 1
    i = m.end()
    while i < len(js) and depth:
        if js[i] == '{':
            depth += 1
        elif js[i] == '}':
            depth -= 1
        i += 1
    return start, i


def test_react_api_gating_and_hop_clip():
    js = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'REACT_GAP_MS = 900' in js or 'REACT_GAP_MS=900' in js
    m = re.search(r"CORRECT_VARIANTS\s*=\s*\[([^\]]*)\]", js)
    assert m, 'CORRECT_VARIANTS missing'
    variants = [v.strip().strip("'\"") for v in m.group(1).split(',')]
    assert variants == ['cheer', 'wave', 'hop'], variants
    m = re.search(r"REACT_CLIP\s*=\s*\{([^}]*)\}", js, re.S)
    assert m, 'REACT_CLIP missing'
    assert re.search(r"wrong\s*:\s*'wobble'", m.group(1)), 'wrong must map to wobble, never shake'

    # 'shake' must never appear anywhere in the react-gating machinery: REACT_CLIP,
    # REACT_FACE, CORRECT_VARIANTS, or the body of react() itself.
    react_start, react_end = _extract_function_span(js, 'react')
    react_clip_start = re.search(r'REACT_CLIP\s*=\s*\{', js).start()
    react_clip_end = js.index('};', react_clip_start) + 2
    react_face_start = re.search(r'REACT_FACE\s*=\s*\{', js).start()
    react_face_end = js.index('};', react_face_start) + 2
    variants_start = re.search(r'CORRECT_VARIANTS\s*=\s*\[', js).start()
    variants_end = js.index('];', variants_start) + 2
    for start, end, label in (
        (react_clip_start, react_clip_end, 'REACT_CLIP'),
        (react_face_start, react_face_end, 'REACT_FACE'),
        (variants_start, variants_end, 'CORRECT_VARIANTS'),
        (react_start, react_end, 'react()'),
    ):
        assert 'shake' not in js[start:end], (
            f'{label} must never reference shake — wrong answers must never head-shake the mascot'
        )

    assert "data-guide-root" in js[react_start:react_end] or 'inGuide' in js[react_start:react_end]
    assert 'guide-open' in js[react_start:react_end]
    assert "motionLevel() === 'off'" in js

    # A rare reaction (milestone/lesson_complete/first_correct) must not be cancellable by an
    # ordinary correct/wrong/streak reaction landing immediately after it starts.
    assert 'rareProtectUntil' in js[react_start:react_end], (
        'react() must protect an in-flight rare reaction from being cut short by a gated one'
    )
    assert 'hop' in js
    assert re.search(r"hop\s*:\s*\{", js), 'hop clip missing from CLIPS table'

    # ifIdle handled in play()
    play_start, play_end = _extract_function_span(js, 'play')
    assert 'ifIdle' in js[play_start:play_end]

    # REACT_RARE is only for genuinely rare events — correct/wrong/streak must always
    # respect the 900ms gate, never bypass it.
    react_rare_start = re.search(r'REACT_RARE\s*=\s*\{', js).start()
    react_rare_end = js.index('};', react_rare_start) + 2
    react_rare_body = js[react_rare_start:react_rare_end]
    for gated_kind in ('correct', 'wrong', 'streak'):
        assert re.search(r"\b" + gated_kind + r"\s*:", react_rare_body) is None, (
            f'{gated_kind} must stay gated by REACT_GAP_MS — it must not appear in REACT_RARE'
        )

    # The wrong-answer thought bubble is JS-created only — it must never be baked into
    # buddy.html's static markup or motion.css's stylesheet (both stay untouched this phase).
    buddy_html = BUDDY_PARTIAL.read_text(encoding='utf-8')
    motion_css = MOTION_CSS.read_text(encoding='utf-8')
    assert 'buddy-thought' not in buddy_html, (
        'buddy.html must not gain a thought-bubble element — it is created purely at runtime'
    )
    assert 'buddy-thought' not in motion_css, (
        'motion.css must not gain thought-bubble rules — it is styled inline via WAAPI/attrs'
    )

    # Thought-bubble creation/cleanup wired into stop(); reduced-motion branch never touches it.
    assert 'function showThought' in js
    assert 'function clearThought' in js
    stop_start, stop_end = _extract_function_span(js, 'stop')
    assert 'clearThought' in js[stop_start:stop_end]
    clips_lookup = js.index('var c = CLIPS[name];', play_start)
    reduced_marker = js.index('if (reduced) {', clips_lookup)
    reduced_end = js.index('return delay(inst, hold)', reduced_marker)   # E8 Phase 3: the hold is reducedMs || dur, / spd
    assert 'showThought' not in js[reduced_marker:reduced_end], (
        'reduced-motion branch of play() must never create a thought bubble'
    )
    full_marker = js.index('try {', reduced_end)
    assert 'showThought' in js[full_marker:play_end], (
        'full-motion branch of play() must be able to show the thought bubble'
    )


def test_celebrate_pbzorp_isolation():
    js = CELEBRATE_JS.read_text(encoding='utf-8')
    start, end = _extract_function_span(js, 'reactMascot')
    body = js[start:end]
    assert 'pbZorp' in body, 'reactMascot must reference window.pbZorp'
    outside = js[:start] + js[end:]
    assert 'pbZorp' not in outside, (
        'every pbZorp reference in celebrate.js must live inside reactMascot() — '
        'this is what proves celebrate.js degrades gracefully with zorp-motion.js absent'
    )
    assert "reactMascot('wrong')" in js
    assert "reactMascot('milestone')" in js
    assert "reactMascot('streak')" in js
    assert "reactMascot('lesson_complete')" in js
    assert "reactMascot(openedFirst ? 'first_correct' : (isStreak ? 'streak' : 'correct'));" in js, (
        'celebrateCorrect must route first_correct/streak/correct through a single reactMascot call '
        'that actually branches on openedFirst/isStreak — not just mention the strings separately'
    )
    assert "reactMascot('shake'" not in js
    assert "target.classList.add('is-shake')" in js
    assert 'pbSound.ding' in js or 'pbSound && window.pbSound.ding' in js
    assert 'pbSound.soft' in js or 'pbSound && window.pbSound.soft' in js
    assert 'points !== 0' in js


def test_sound_ding_and_soft():
    js = SOUND_JS.read_text(encoding='utf-8')
    assert 'ding: playDing' in js
    assert 'soft: playSoft' in js
    assert 'function playDing' in js
    assert 'function playSoft' in js
    # Both route through playSequence, the same helper every other tone uses.
    ding_start, ding_end = _extract_function_span(js, 'playDing')
    soft_start, soft_end = _extract_function_span(js, 'playSoft')
    assert 'playSequence(' in js[ding_start:ding_end]
    assert 'playSequence(' in js[soft_start:soft_end]
    wrong_start, wrong_end = _extract_function_span(js, 'playWrong')
    wrong_gain = max(float(g) for g in re.findall(r'gain:\s*([\d.]+)', js[wrong_start:wrong_end]))
    soft_gain = max(float(g) for g in re.findall(r'gain:\s*([\d.]+)', js[soft_start:soft_end]))
    assert soft_gain < wrong_gain, (soft_gain, wrong_gain)
    for ext in ('.mp3', '.wav', '.ogg'):
        assert ext not in js
    assert 'new Audio(' not in js


def test_quiz_runner_scope():
    js = QUIZ_RUNNER_JS.read_text(encoding='utf-8')
    lesson_start, lesson_end = _extract_function_span(js, 'initLessonQuizRunner')
    quick_start, quick_end = _extract_function_span(js, 'initQuicktestRunner')
    assert 'pbCelebrate' in js[lesson_start:lesson_end]
    assert 'pbCelebrate' not in js[quick_start:quick_end], (
        'the quick-test runner must never reference pbCelebrate — it already gets '
        'celebration via site.js, and adding it here would double-fire ticks/tones'
    )


def _extract_media_block(css, media_query):
    marker = re.search(re.escape(media_query) + r'\s*\{', css)
    assert marker, f'{media_query} block missing'
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


def test_phase4_new_clips():
    # E7 Phase 4: 'peek' and 'sleep' were speculated in the Phase 1 clip table but never
    # implemented until now. Additive only — CLIP_NAMES/CLIPS both gain entries, nothing
    # existing is touched.
    js = RUNTIME_JS.read_text(encoding='utf-8')
    for clip in ('peek', 'sleep'):
        assert f"'{clip}'" in js, f'clip {clip} missing from CLIP_NAMES'
        assert re.search(re.escape(clip) + r"\s*:\s*\{", js), f'{clip} clip missing from CLIPS table'
    for clip in PHASE4_CLIPS:
        assert f"'{clip}'" in js, f'clip {clip} missing from CLIP_NAMES'
    # 'peek' has no reducedFace — the existing play() reduced-motion branch already resolves
    # `false` for any clip lacking one, so it must never gain a special-cased reduced check.
    m = re.search(r"peek\s*:\s*\{", js)
    assert m, 'peek clip missing from CLIPS table'
    depth = 1
    i = m.end()
    while i < len(js) and depth:
        if js[i] == '{':
            depth += 1
        elif js[i] == '}':
            depth -= 1
        i += 1
    assert 'reducedFace' not in js[m.end():i]


def test_phase4_react_target_skips_decorative_mascots():
    # E7 Phase 4 post-review fix: zorp-triggers.js's data-zorp-autoplay mascots (empty states,
    # streak-ring peek) bind into `instances` before study-buddy.js binds/unhides the corner
    # buddy (base.html script order), so reactTarget()'s "first rendered instance" scan must
    # explicitly skip any instance whose host is one of these one-off decorative mascots —
    # otherwise a milestone/streak/correct celebration on /profile or an empty-state page could
    # animate the small decorative mascot instead of the intended buddy.
    js = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'data-zorp-autoplay' in js, 'reactTarget() must know about the autoplay marker attribute'
    react_target_start, react_target_end = _extract_function_span(js, 'reactTarget')
    assert 'isDecorative' in js[react_target_start:react_target_end], (
        'reactTarget() must exclude decorative (data-zorp-autoplay) mascots from its scan'
    )


def test_practice_css_quiz_runner_option_animations():
    css = PRACTICE_CSS.read_text(encoding='utf-8')
    block = _extract_media_block(css, '@media (prefers-reduced-motion: no-preference)')
    assert '.quiz-runner-option.is-pop' in block
    assert '.quiz-runner-option.is-shake' in block
    assert '.quiz-runner-option.is-reveal' in block
    assert '.mcq-btn.is-pop' in block and '.btn.is-pop' in block   # unchanged
    assert '.mcq-btn.is-shake' in block and '.btn.is-shake' in block


def test_phase5_motionlevel_reads_data_motion():
    js = RUNTIME_JS.read_text(encoding='utf-8')
    level_start, level_end = _extract_function_span(js, 'motionLevel')
    body = js[level_start:level_end]
    assert 'document.documentElement.getAttribute' in body and "'data-motion'" in body, (
        'motionLevel() must read data-motion from document.documentElement'
    )
    assert "'off'" in body and "'reduced'" in body


def test_phase5_css_motion_preference_mirrors():
    base_css = (CSS_DIR / 'base.css').read_text(encoding='utf-8')
    motion_css = MOTION_CSS.read_text(encoding='utf-8')
    chrome_css = (CSS_DIR / 'chrome.css').read_text(encoding='utf-8')
    practice_css = PRACTICE_CSS.read_text(encoding='utf-8')
    assert 'html[data-motion="reduced"]' in base_css and 'html[data-motion="off"]' in base_css
    assert 'html[data-motion="reduced"]' in motion_css and 'html[data-motion="off"]' in motion_css
    assert 'html[data-motion="reduced"]' in chrome_css and 'html[data-motion="off"]' in chrome_css
    assert 'html[data-motion="reduced"]' in practice_css and 'html[data-motion="off"]' in practice_css
    # The universal data-motion catch-all is what actually delivers "less motion"
    # site-wide; the mirror blocks alone (e.g. the view-transition one) also contain
    # these selector strings, so pin the catch-all's declaration too, not just the
    # selector text, so deleting the catch-all itself would fail this test.
    catchall_idx = base_css.index(
        'html[data-motion="reduced"] *, html[data-motion="reduced"] *::before'
    )
    catchall_tail = base_css[catchall_idx:catchall_idx + 400]
    assert 'animation-duration: 0.01ms !important' in catchall_tail
    assert 'transition-duration: 0.01ms !important' in catchall_tail


def test_phase5_motion_preference_persists():
    # Mirrors the settings-persistence pattern in scripts/test_social_smoke.py.
    import uuid

    from app import app  # noqa: E402

    def csrf_from(html):
        m = re.search(r'name="csrf_token" value="([^"]+)"', html)
        assert m, 'csrf token not found'
        return m.group(1)

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.get('/register')
        r = client.post(
            '/register',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'zorp_motion_{suffix}@example.com',
                'handle': f'zmp_{suffix}',
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200

        r = client.get('/profile/settings')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'name="motion_preference"' in html
        for value in ('system', 'reduced', 'off'):
            assert f'value="{value}"' in html

        # Cycle through non-default values before returning to the default, so the
        # first save is never a no-op that would pass even if persistence were broken.
        for value in ('reduced', 'off', 'system'):
            r = client.get('/profile/settings')
            token = csrf_from(r.data.decode())
            r = client.post(
                '/profile/settings',
                data={
                    'csrf_token': token,
                    'profile_visibility': 'followers_only',
                    'default_share_visibility': 'followers_only',
                    'motion_preference': value,
                },
                follow_redirects=True,
            )
            assert r.status_code == 200
            assert b'Settings saved' in r.data

            r = client.get('/profile/settings')
            assert r.status_code == 200
            html = r.data.decode()
            checked_input = re.search(
                r'<input type="radio" name="motion_preference" value="([a-z]+)"\s*\n?\s*checked>',
                html,
            )
            assert checked_input, 'no motion_preference radio marked checked'
            assert checked_input.group(1) == value, (
                f'expected motion_preference={value} to persist, got {checked_input.group(1)}'
            )

            # The rendered <html> tag itself must carry the new value.
            home = client.get('/')
            assert home.status_code == 200
            home_html = home.data.decode()
            assert re.search(r'<html[^>]*data-motion="%s"' % value, home_html), (
                f'<html> did not render data-motion="{value}" after saving it'
            )


def test_phase5_patch_motion_preference():
    import json
    import uuid

    from app import app  # noqa: E402

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.get('/register')
        m = re.search(r'name="csrf_token" value="([^"]+)"', r.data.decode())
        assert m, 'csrf token not found'
        r = client.post(
            '/register',
            data={
                'csrf_token': m.group(1),
                'email': f'zorp_motion_patch_{suffix}@example.com',
                'handle': f'zmpp_{suffix}',
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200

        r = client.patch(
            '/api/v1/me/settings',
            data=json.dumps({'motion_preference': 'bogus'}),
            content_type='application/json',
        )
        assert r.status_code == 400, f'expected 400 for an invalid motion_preference, got {r.status_code}'

        r = client.patch(
            '/api/v1/me/settings',
            data=json.dumps({'motion_preference': 'off'}),
            content_type='application/json',
        )
        assert r.status_code == 200, f'expected 200 for a valid motion_preference, got {r.status_code}'
        body = json.loads(r.data.decode())
        settings = body.get('settings', body)
        assert settings.get('motion_preference') == 'off', (
            f'PATCH did not persist motion_preference=off, got {settings!r}'
        )


def main():
    test_no_third_party_animation_library()
    test_motion_css_keyframes_pair_with_reduced_motion()
    test_runtime_exposes_api()
    test_rig_markup()
    test_motion_css_rig_pivots()
    test_arm_pivot_groups()
    test_ambient_fx_outside_flip()
    test_existing_arm_clips_unchanged()
    test_base_loads_motion_assets()
    test_buddy_face_persists_without_hidden_root()
    test_dev_motion_sections()
    test_cosmetic_css()
    test_cosmetic_markup()
    test_default_render_has_no_look()
    test_overlay_rig_wiring()
    test_react_api_gating_and_hop_clip()
    test_celebrate_pbzorp_isolation()
    test_sound_ding_and_soft()
    test_quiz_runner_scope()
    test_practice_css_quiz_runner_option_animations()
    test_phase4_new_clips()
    test_phase4_react_target_skips_decorative_mascots()
    test_phase5_motionlevel_reads_data_motion()
    test_phase5_css_motion_preference_mirrors()
    test_phase5_motion_preference_persists()
    test_phase5_patch_motion_preference()
    print('Zorp motion smoke passed.')


if __name__ == '__main__':
    main()
