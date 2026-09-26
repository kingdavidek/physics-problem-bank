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
API_NAMES = ('bind', 'play', 'idle', 'setFace', 'motionLevel', 'react')
PHASE1_CLIPS = ('idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake')
PHASE2_CLIPS = PHASE1_CLIPS + ('hop',)
PHASE4_CLIPS = PHASE2_CLIPS + ('peek', 'sleep')
CELEBRATE_JS = JS_DIR / 'celebrate.js'
SOUND_JS = JS_DIR / 'sound.js'
QUIZ_RUNNER_JS = JS_DIR / 'quiz-runner.js'
PRACTICE_CSS = CSS_DIR / 'practice.css'
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
    for mouth in LOOK_MOUTHS:
        assert f'data-mouth="{mouth}"' in css, mouth
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
    for cls in ('buddy-mouth--smile', 'buddy-mouth--grin', 'buddy-mouth--cat'):
        assert buddy.count(cls) == 1, f'{cls} should appear exactly once'
    nudge_start = buddy.index('buddy-face--nudge')
    nudge_end = buddy.index('buddy-face--milestone')
    for cls in ('buddy-mouth--smile', 'buddy-mouth--grin', 'buddy-mouth--cat'):
        idx = buddy.index(cls)
        assert nudge_start < idx < nudge_end, f'{cls} must sit inside buddy-face--nudge'
    smile_line = buddy[buddy.index('buddy-mouth--smile'):buddy.index('buddy-mouth--smile') + 200]
    grin_line = buddy[buddy.index('buddy-mouth--grin'):buddy.index('buddy-mouth--grin') + 200]
    cat_line = buddy[buddy.index('buddy-mouth--cat'):buddy.index('buddy-mouth--cat') + 200]
    assert 'display="none"' not in smile_line.split('/>')[0]
    assert 'display="none"' in grin_line.split('/>')[0]
    assert 'display="none"' in cat_line.split('/>')[0]
    assert 'data-mouth=' in buddy
    assert 'buddy_mascot(look=none)' in buddy or 'buddy_mascot(look=None)' in buddy


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
    last_face_idx = buddy.rindex('buddy-face--friend-challenge')
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
    reduced_end = js.index('return delay(inst, c.dur)', reduced_marker)
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


def main():
    test_no_third_party_animation_library()
    test_motion_css_keyframes_pair_with_reduced_motion()
    test_runtime_exposes_api()
    test_rig_markup()
    test_motion_css_rig_pivots()
    test_base_loads_motion_assets()
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
    print('Zorp motion Phase 1-2 smoke passed.')


if __name__ == '__main__':
    main()
