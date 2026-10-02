"""E8 Zorp expressions: budgets, presets, parts library, safeguarding (docs/ZORP_EXPRESSIVENESS.md).

Run: python scripts/test_zorp_expression_smoke.py

Phase 0 recorded the section 2.1 ledger at its baseline. Phase 1 (2026-09-29) built the
expression engine (models/zorp_rig.py, templates/partials/zorp_parts.html and
zorp_library.html, the slot-based buddy.html) and flips every ledger constant to its cap; the
measured value is in each constant's comment. Phase 2 (2026-09-29) adds the full vocabulary,
the fx layer, animated swaps and the safeguarding tests (valence, CONTEXT_MAP, guide catalog).
Phase 3 (2026-09-29) adds the views (side, three-quarter, back, back-glance), the flip wrapper and the
pinch-turn; the constants below carry the Phase 3 measurements.
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
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS_DIR = ROOT / 'static' / 'js'
CSS_DIR = ROOT / 'static' / 'css'
MOTION_CSS = CSS_DIR / 'motion.css'
RUNTIME_JS = JS_DIR / 'zorp-motion.js'
POSES_JS = JS_DIR / 'zorp-poses.js'
TEMPLATES = ROOT / 'templates'
DOC = ROOT / 'docs' / 'ZORP_EXPRESSIVENESS.md'
SNAPSHOT_TOOL = ROOT / 'scripts' / 'zorp_gallery_snapshot.py'

# §2.1 ledger caps (Phase 1, measured 2026-09-29; Phase 2 re-measured, see docs ledger).
INSTANCE_DEFAULT_MAX_BYTES = 4_500  # measured 2,454 B Phase 1, 2,493 B Phase 2, 3,036 B Phase 3 (baseline 7,249)
INSTANCE_MAX_ELEMENTS = 70  # measured 39 Phase 1, 40 Phase 2, 50 Phase 3 (baseline 98)
INSTANCE_LOOK_MAX_BYTES = 5_800  # measured 3,624 B Phase 1, 3,663 B Phase 2, 4,206 B Phase 3 (baseline 8,344)
PAGE_MASCOT_MAX_BYTES = 36_000  # 3 instances + library + island; see test_page_mascot_budget output
PAGE_MASCOT_MAX_GZIP = 6_000
RUNTIME_JS_MAX_BYTES = 56_000  # baseline 26_602; 47_868 after Phase 3; Phase 4 first trimmed it to 43_084, then added the register hook (45_370; 45_509 after the review fixes); 47_962 after Phase 5; RAISED 48_000 -> 56_000 on 2026-10-01 (E8 Phase 7, David: "raise the cap by however much you need"): idle life (blink, glance, antenna twitch, look-around clip, IntersectionObserver and typing pauses) measured at 53_081 B, see docs/ZORP_EXPRESSIVENESS.md 2.1 and test_runtime_js_budget output
POSES_JS_MAX_BYTES = 26_000  # Phase 7 (2026-10-01): measured 25_662 B, no raise needed; E8 Phase 4 (new file, 2026-09-30): poses table, beat engine and the new clips, 24,000 B at first; raised to 26,000 B in Phase 5 (2026-09-30, ledger note) for the react() plan; measured in test_poses_js_budget output
PARTS_LIBRARY_MAX_BYTES = 16_000  # <template> only; measured 6,959 B Phase 1, 12,169 B Phase 2, 13,432 B Phase 3
RIG_JSON_MAX_BYTES = 6_000  # island; measured 1,359 B Phase 1, 2,802 B Phase 2, 4,503 B Phase 3 (with tags)
MOTION_CSS_MAX_BYTES = 12_000  # mirrors test_zorp_motion_smoke.py; baseline 4_844, Phase 1 6_445, Phase 2 7_466, Phase 3 7_895

NEGATIVE_NAMES = ('sad', 'aww-teary', 'embarrassed', 'dizzy')  # reserved preset names (the 'worried' brow variant is not a preset)
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


def _render(fn):
    from app import app  # noqa: E402

    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        return fn(module)


def _library_html():
    from app import app  # noqa: E402

    with app.app_context():
        return app.jinja_env.get_template('partials/zorp_library.html').render()


def _split_library(html):
    tpl = re.search(r'<template id="pb-zorp-parts">.*?</template>', html, re.S)
    island = re.search(r'<script type="application/json" id="pb-zorp-rig">.*?</script>', html, re.S)
    assert tpl and island, 'library must hold the template and the island'
    return tpl.group(0), island.group(0)


def test_presets_complete():
    from models import zorp_rig

    assert zorp_rig.validate()
    for name in ('nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk', 'weak_topic',
                 'friend_challenge', 'sleep'):
        assert name in zorp_rig.PRESETS and name in zorp_rig.LEGACY_FACES, name
    for name in ('soft-smile', 'grin', 'happy', 'joy', 'laugh', 'smug', 'wow', 'aww', 'bashful', 'determined',
                 'proud', 'love', 'curious', 'thinking', 'confused', 'oops', 'embarrassed', 'aww-teary',
                 'sad', 'dizzy', 'sleepy', 'wink', 'heads-up'):
        assert name in zorp_rig.PRESETS, name
    assert len(zorp_rig.NEW_PRESETS) >= 22
    tpl, _ = _split_library(_library_html())
    for channel, ids in zorp_rig.CHANNELS.items():
        for vid in ids:
            assert f'data-part="{channel}:{vid}"' in tpl, (channel, vid)
    for name, ch in zorp_rig.PRESETS.items():
        for key, channel in (('eyeL', 'eyes'), ('eyeR', 'eyes'), ('brows', 'brows'), ('mouth', 'mouth'),
                             ('cheeks', 'cheeks'), ('fx', 'fx')):
            assert f'data-part="{channel}:{ch[key]}"' in tpl, (name, key, ch[key])
    # D4: streak_risk keeps its name but is upbeat (no frown, no sad eyes).
    streak = zorp_rig.PRESETS['streak_risk']
    assert streak == zorp_rig.PRESETS['heads-up']
    assert streak['brows'] == 'raised' and streak['mouth'] == 'smile' and streak['fx'] == 'flame'
    # the only frown in the vocabulary belongs to the negative 'sad' preset and nothing else
    frowns = [n for n, ch in zorp_rig.PRESETS.items() if 'frown' in ch['mouth']]
    assert frowns == ['sad'], frowns
    sad = zorp_rig.PRESETS['sad']
    assert sad['eyeL'] == 'goo-shine' and sad['fx'] == 'tear-shine' and sad['brows'] == 'worried'
    assert zorp_rig.PRESETS['determined']['eyeL'] == 'squint' and zorp_rig.PRESETS['wow']['fx'] == 'exclaim'
    assert zorp_rig.PRESETS['aww']['cheeks'] == 'glow' and zorp_rig.PRESETS['bashful']['fx'] == 'blush-steam'
    assert zorp_rig.PRESETS['wink']['eyeL'] == 'open' and zorp_rig.PRESETS['wink']['eyeR'] == 'wink-line'
    assert zorp_rig.PRESETS['thinking']['fx'] == 'thought' and zorp_rig.PRESETS['confused']['eyeL'] == 'look-side'


def test_js_fallback_table_matches_rig():
    # zorp-motion.js carries a built-in copy of the legacy presets for pages without the island.
    from models import zorp_rig

    js = RUNTIME_JS.read_text(encoding='utf-8')
    block = js[js.index('var LEGACY_PRESETS = {'):]
    block = block[:block.index('};')]
    rows = dict(re.findall(r"(\w+): \[([^\]]*)\]", block))
    assert set(rows) == set(zorp_rig.LEGACY_FACES), sorted(rows)
    code = {'positive': '+', 'neutral': '0', 'negative': '-'}
    for name in zorp_rig.LEGACY_FACES:
        want = [zorp_rig.PRESETS[name][k] for k in zorp_rig.SLOTS] + [code[zorp_rig.VALENCE[name]]]
        have = [v.strip().strip("'") for v in rows[name].split(',')]
        assert have == want, (name, have, want)


def test_default_render_budget():
    default_svg = _render(lambda m: str(m.buddy_mascot()))
    d_bytes = len(default_svg.encode('utf-8'))
    d_elements = _elements(default_svg)
    print(f'  default instance: {d_bytes} B, {_gz(default_svg)} B gzip, {d_elements} elements')
    assert default_svg.startswith(DEFAULT_SVG_START), default_svg[:120]
    assert default_svg.split('>', 1)[0] == '<svg class="buddy-mascot" viewBox="0 0 64 64" aria-hidden="true" focusable="false"'
    assert d_bytes <= INSTANCE_DEFAULT_MAX_BYTES, d_bytes
    assert d_elements <= INSTANCE_MAX_ELEMENTS, d_elements
    assert default_svg.count('class="buddy-pupil"') == 2
    # exactly one face: one plate, one mouth slot, no hidden alternatives
    assert default_svg.count('class="zorp-face"') == 1 and 'display="none"' not in default_svg
    for face in _all_presets():
        svg = _render(lambda m, face=face: str(m.buddy_mascot(face=face)))
        assert len(svg.encode('utf-8')) <= INSTANCE_DEFAULT_MAX_BYTES, face
        assert _elements(svg) <= INSTANCE_MAX_ELEMENTS, face


def _all_presets():
    from models import zorp_rig

    return list(zorp_rig.PRESETS)


def test_full_look_budget():
    look_svg = _fullest_look()
    l_bytes = len(look_svg.encode('utf-8'))
    print(f'  fullest look:     {l_bytes} B, {_gz(look_svg)} B gzip, {_elements(look_svg)} elements')
    assert l_bytes <= INSTANCE_LOOK_MAX_BYTES, l_bytes
    # the fullest look also with the heaviest preset (joy: tongue, sparkles, brows, cheeks)
    from models import zorp_kit

    names = list(zorp_kit.LOOK_FIELDS)
    look = {n: zorp_kit.LOOK_FIELDS[n][0] for n in names}
    joy = _render(lambda m: str(m.buddy_mascot(look, face='joy')))
    assert len(joy.encode('utf-8')) <= INSTANCE_LOOK_MAX_BYTES


def test_library_and_island_budget():
    from models import zorp_rig

    tpl, island = _split_library(_library_html())
    print(f'  library <template>: {len(tpl.encode())} B; island: {len(island.encode())} B')
    assert len(tpl.encode('utf-8')) <= PARTS_LIBRARY_MAX_BYTES
    assert len(island.encode('utf-8')) <= RIG_JSON_MAX_BYTES
    data = json.loads(re.search(r'>(.*)</script>', island, re.S).group(1))
    assert data['v'] == 1 and set(data['p']) == set(zorp_rig.PRESETS)
    for name, row in data['p'].items():
        assert len(row) == 7 and row[6] in '+0-', name
    # inert: nothing runnable inside the template
    assert '<script' not in tpl and 'onload' not in tpl and '<animate' not in tpl


def test_page_mascot_budget():
    from app import app  # noqa: E402

    with app.test_client() as client:
        _register(client)
        r = client.get('/')
        assert r.status_code == 200
        html = r.data.decode()
    found = re.findall(r'<svg class="buddy-mascot".*?</svg>', html, re.S)
    tpl, island = _split_library(html)
    assert html.count('id="pb-zorp-parts"') == 1 and html.count('id="pb-zorp-rig"') == 1
    joined = ''.join(found) + tpl + island
    size = len(joined.encode('utf-8'))
    gz = _gz(joined)
    print(f'  logged-in /: {len(found)} mascots + library + island = {size} B, {gz} B gzip')
    assert 2 <= len(found) <= 4, len(found)
    assert size <= PAGE_MASCOT_MAX_BYTES, size
    assert gz <= PAGE_MASCOT_MAX_GZIP, gz
    assert html.index('id="pb-zorp-parts"') < html.index('id="pb-buddy-prompt"') or 'id="pb-buddy-prompt"' not in html
    # anonymous pages have no runtime, so no library either
    anon = app.test_client().get('/login').data.decode()
    assert 'zorp-motion.js' not in anon and 'pb-zorp-parts' not in anon and 'pb-zorp-rig' not in anon


def test_unknown_face_fails_closed():
    from models import zorp_rig

    for bad in ('bogus', '', None, 5, ['nudge'], 'NUDGE', 'nudge ', '__proto__', 'streak-risk'):
        assert zorp_rig.resolve_preset(bad) == 'nudge', bad
        assert zorp_rig.face_for_prompt(bad) == 'nudge', bad
    # E8 Phase 5 (D4): the prompt types map to upbeat presets; streak_risk is the heads-up look
    assert zorp_rig.face_for_prompt('streak_risk') == 'heads-up'
    want = {'milestone': 'proud', 'celebrate': 'happy', 'qotd_nudge': 'wink', 'weak_topic': 'determined',
            'friend_challenge': 'wink', 'nudge': 'nudge'}
    for kind, face in want.items():
        assert zorp_rig.face_for_prompt(kind) == face, kind
    plain = _render(lambda m: str(m.buddy_mascot()))
    assert _render(lambda m: str(m.buddy_mascot(face='bogus'))) == plain
    assert _render(lambda m: str(m.buddy_mascot(face='<script>'))) == plain
    happy = _render(lambda m: str(m.buddy_mascot(face='happy')))
    assert ' data-expr="happy"' in happy and 'data-expr' not in plain


def test_offline_sleep_draws_eyes():
    from app import app  # noqa: E402

    html = app.test_client().get('/offline').data.decode()
    m = re.search(r'<span class="study-buddy-face pb-zorp-small" id="offline-zorp".*?</span>', html, re.S)
    assert m, 'offline mascot missing'
    span = m.group(0)
    assert 'data-face="sleep"' in span and 'data-expr="sleep"' in span
    assert span.count('M-3-.4q3 3.4 6 0') == 2, 'both closed eyes must be drawn'
    assert 'zorp-zzz' in span and 'zorp-slot--mouth' in span
    assert 'class="buddy-pupil"' not in span, 'a sleeping face has no open pupils'


def test_valence_classified():
    from models import zorp_rig

    assert set(zorp_rig.VALENCE) == set(zorp_rig.PRESETS)
    assert set(zorp_rig.VALENCE.values()) <= {'positive', 'neutral', 'negative'}
    assert zorp_rig.valence('bogus') == zorp_rig.valence('nudge')
    negative = {n for n, v in zorp_rig.VALENCE.items() if v == 'negative'}
    assert negative == set(NEGATIVE_NAMES), negative


def test_no_negative_in_prompt_faces():
    from models import buddy, zorp_rig

    negative = {n for n, v in zorp_rig.VALENCE.items() if v == 'negative'} | set(NEGATIVE_NAMES)
    for kind in buddy.BUDDY_TYPES:
        face = zorp_rig.face_for_prompt(kind)
        assert face in zorp_rig.PRESETS and zorp_rig.VALENCE[face] != 'negative', (kind, face)
    for context, faces in zorp_rig.CONTEXT_MAP.items():
        if context.startswith(zorp_rig.BANNED_CONTEXTS_FOR_NEGATIVE):
            for face in faces:
                assert face not in negative, (context, face)
    # the streak prompt never draws a frown or sad eyes (D4)
    streak = zorp_rig.preset(zorp_rig.face_for_prompt('streak_risk'))
    assert 'frown' not in streak['mouth'] and streak['eyeL'] != 'goo-shine'
    # literals in the consumers that react to pupils or draw prompts
    for path in (JS_DIR / 'celebrate.js', JS_DIR / 'study-buddy.js', JS_DIR / 'zorp-triggers.js', RUNTIME_JS,
                 *sorted(TEMPLATES.rglob('*.html'))):
        text = path.read_text(encoding='utf-8')
        for name in negative:
            for quote in ("'", '"'):
                assert f'{quote}{name}{quote}' not in text, f'{path.relative_to(ROOT)} uses negative preset {name!r}'


def _react_faces():
    from models import zorp_rig

    return {face for context, faces in zorp_rig.CONTEXT_MAP.items() if context.startswith('react.') for face in faces}


def test_blush_never_on_react():
    """Blush and sweat are Zorp's own bashfulness: never in a react.* context (plan section 2 #6)."""
    from models import zorp_rig

    own = {n for n, ch in zorp_rig.PRESETS.items()
           if ch['cheeks'] == 'blush' or ch['fx'] in ('blush-steam', 'sweat')}
    assert {'bashful', 'embarrassed'} <= own
    react = _react_faces()
    assert react and not (react & own), react & own
    # the runtime's reaction tables (react() faces) must not name them either
    js = RUNTIME_JS.read_text(encoding='utf-8')
    m = re.search(r"REACT_FACE\s*=\s*\{([^}]*)\}", js)
    for name in own:
        assert f"'{name}'" not in m.group(1), name
    assert 'bashful' not in '\n'.join(
        line for line in js.splitlines() if 'REACT_' in line or 'CORRECT_VARIANTS' in line)


def _catalog_steps():
    """(step id, face, lore, resolve, big) for every object with a face: in guide-catalog.js."""
    text = (JS_DIR / 'guide-catalog.js').read_text(encoding='utf-8')
    steps = []
    for m in re.finditer(r"face:\s*'([\w-]+)'", text):
        depth, i = 0, m.start()
        while i > 0:  # walk back to the opening brace of the enclosing object
            i -= 1
            if text[i] == '}':
                depth += 1
            elif text[i] == '{':
                if depth == 0:
                    break
                depth -= 1
        depth, j = 1, i + 1
        while depth and j < len(text):
            depth += {'{': 1, '}': -1}.get(text[j], 0)
            j += 1
        obj = text[i:j]
        ident = re.search(r"\bid:\s*'([^']+)'", obj)
        resolve = re.search(r"\bresolve:\s*'([\w-]+)'", obj)
        steps.append((ident.group(1) if ident else None, m.group(1),
                      bool(re.search(r'\blore:\s*true', obj)), resolve.group(1) if resolve else None,
                      bool(re.search(r'\bbig:\s*true', obj))))
    return steps


def test_negative_presets_restricted():
    """Plan section 5: negative presets stay out of prompt/react/dismiss/idle/autoplay/notification
    contexts, appear only in NEGATIVE_ALLOWED contexts, and the guide catalog only uses presets
    from CONTEXT_MAP['guide'] (negative ones only in allowlisted lore steps that resolve positively)."""
    from models import zorp_rig

    zorp_rig.validate()
    negative = {n for n, v in zorp_rig.VALENCE.items() if v == 'negative'}
    assert negative == set(NEGATIVE_NAMES)
    for context, faces in zorp_rig.CONTEXT_MAP.items():
        for face in faces:
            assert face in zorp_rig.PRESETS, (context, face)
            if face in negative:
                assert context.startswith(zorp_rig.NEGATIVE_ALLOWED), f'{context} may not use {face}'
                assert not context.startswith(zorp_rig.BANNED_CONTEXTS_FOR_NEGATIVE), (context, face)
    # the banned prefixes are all still there (nobody quietly shortened the list)
    for prefix in ('prompt.', 'react.', 'dismiss', 'idle', 'autoplay.', 'notification'):
        assert prefix in zorp_rig.BANNED_CONTEXTS_FOR_NEGATIVE, prefix
    assert not set(zorp_rig.NEGATIVE_ALLOWED) & set(zorp_rig.BANNED_CONTEXTS_FOR_NEGATIVE)
    # 'sad' exists only for guide lore (plus the styleguide review list)
    homes = {c for c, faces in zorp_rig.CONTEXT_MAP.items() if 'sad' in faces}
    assert homes == {'guide.lore', 'styleguide'}, homes
    assert 'sad' not in zorp_rig.CONTEXT_MAP['guide']
    # every react context resolves to a positive or neutral face (a wrong answer never ends sad)
    for context, faces in zorp_rig.CONTEXT_MAP.items():
        if context.startswith('react.'):
            assert all(zorp_rig.VALENCE[f] != 'negative' for f in faces), context
    # guide catalog
    steps = _catalog_steps()
    assert len(steps) >= 20, len(steps)
    for step_id, face, lore, resolve, big in steps:
        assert face in zorp_rig.PRESETS, (step_id, face)
        if zorp_rig.VALENCE[face] == 'negative' and big:
            # Phase 5: the one big reward (100-day streak, happy tears) may open on aww-teary, and resolves positively
            assert face in zorp_rig.CONTEXT_MAP['guide.reward.big'], (step_id, face)
            assert resolve in zorp_rig.CONTEXT_MAP['guide'] and zorp_rig.VALENCE[resolve] == 'positive', 'a big reward must resolve positively'
        elif zorp_rig.VALENCE[face] == 'negative':
            assert lore and step_id in zorp_rig.GUIDE_LORE_STEPS, f'{step_id}: negative {face} outside an allowlisted lore step'
            assert face in zorp_rig.CONTEXT_MAP['guide.lore']
            assert resolve and zorp_rig.VALENCE[resolve] == 'positive', f'{step_id}: lore step must resolve positively'
        else:
            assert face in zorp_rig.CONTEXT_MAP['guide'], (step_id, face)
    for step_id in zorp_rig.GUIDE_LORE_STEPS:
        assert any(s[0] == step_id for s in steps), f'allowlisted lore step {step_id} not in the catalog'
    # prompt types never resolve to a negative preset, whatever the emoji says
    for kind in zorp_rig.PROMPT_FACES:
        assert zorp_rig.valence(zorp_rig.face_for_prompt(kind)) != 'negative'


def test_consumers_filter_by_valence():
    """study-buddy.js refuses negative presets (island valence and its fallback table); guide.js
    accepts a preset only inside the guide allowlist and lore steps show step.resolve last."""
    sb = (JS_DIR / 'study-buddy.js').read_text(encoding='utf-8')
    assert 'valenceOf' in sb and "!== 'negative'" in sb
    m = re.search(r'var FACE_OK = \{(.*?)\};', sb, re.S)
    assert m and 'negative' not in m.group(1)
    for value in re.findall(r"\w+:\s*'(\w+)'", m.group(1)):
        assert value in ('positive', 'neutral'), value
    guide = (JS_DIR / 'guide.js').read_text(encoding='utf-8')
    assert 'allowedIn' in guide and "'guide.lore'" in guide and 'step.resolve' in guide
    # the last line of a lore step is checked against the plain guide list (no negative face can
    # stay on screen even when step.resolve is missing or negative; review 2026-09-29)
    assert "step.big ? 'guide.reward.big' : (step.lore ? 'guide.lore' : 'guide')" in guide and "lineIndex < lines.length ?" in guide
    assert 'hasExpression' not in guide.split('function setFace', 1)[1].split('function setMedal', 1)[0], (
        'guide.js must ask allowedIn (the allowlist), not just hasExpression'
    )


def test_data_expr_kept_in_sync():
    js = RUNTIME_JS.read_text(encoding='utf-8')
    assert "'custom'" in js and 'function markExpr' in js
    draw = js[js.index('function drawChannels'):]
    draw = draw[:draw.index('\n  }\n')]
    assert 'markExpr(inst, hint)' in draw
    assert 'drawChannels(inst, back, swap.prev' in js and 'drawChannels(inst, ch, face)' in js


def test_rig_json_escapes_lt():
    from models import zorp_rig

    text = zorp_rig.rig_json()
    assert '<' not in text and '</script' not in text.lower()
    assert json.loads(text)['ff'] == list(zorp_rig.FX_FACE)
    # a preset name carrying a closing tag would come out escaped, and still parse back
    saved = dict(zorp_rig.PRESETS['nudge'])
    try:
        zorp_rig.PRESETS['</script><b>'] = saved
        zorp_rig.VALENCE['</script><b>'] = 'neutral'
        out = zorp_rig.rig_json()
        assert '<' not in out and '\\u003c/script>' in out
        assert '</script><b>' in json.loads(out)['p']
    finally:
        zorp_rig.PRESETS.pop('</script><b>', None)
        zorp_rig.VALENCE.pop('</script><b>', None)


def test_face_fx_slot_markup():
    from models import zorp_rig

    for name, ch in zorp_rig.PRESETS.items():
        svg = _render(lambda m, name=name: str(m.buddy_mascot(face=name)))
        face_part = svg.split('class="zorp-slot--fx-face">', 1)[1].split('</g>', 1)[0] if ch['fx'] in zorp_rig.FX_FACE else ''
        assert (face_part != '') == (ch['fx'] in zorp_rig.FX_FACE), name
        ambient = svg.split('class="zorp-slot--fx">', 1)[1]
        if ch['fx'] in zorp_rig.FX_FACE:
            assert ambient.startswith('</g>'), f'{name}: face-attached fx leaked into the ambient slot'
        head = svg.split('class="zorp-face"', 1)[1].split('class="buddy-foot', 1)[0]
        assert 'zorp-slot--fx-face' in head, 'the face-attached slot must sit inside the face group (and so the head)'
        assert 'zorp-slot--fx"' not in head


def test_snapshot_compare_is_mascot_box_only():
    text = SNAPSHOT_TOOL.read_text(encoding='utf-8')
    for needle in ('def _mascot_bbox', 'def _mascot_pct', "'box'", 'fx-filmstrips.png', 'matrix.png', 'PARITY_EXEMPT'):
        assert needle in text, needle
    assert "'streak_risk'" in text and "'sleep'" in text
    m = re.search(r'OVER_PCT = ([\d.]+)', text)
    assert m and float(m.group(1)) <= 0.2, 'legacy faces must be ~0 changed pixels inside the mascot box'


def test_picker_and_gallery_markup():
    from app import app  # noqa: E402
    from models import zorp_rig

    html = app.test_client().get('/styleguide').data.decode()
    for name in zorp_rig.PRESETS:
        assert f'data-zorp-expr="{name}"' in html, name
        assert html.count(f'data-gallery-face="{name}"') == 2, name
    for slot in zorp_rig.SLOTS:
        assert f'data-zorp-channel="{slot}"' in html, slot
    for level in ('system', 'reduced', 'off'):
        assert f'data-zorp-set-motion="{level}"' in html, level
    assert 'data-zorp-slow' in html and 'id="pb-zorp-parts"' in html and 'styleguide.js?v=8' in html
    assert 'id="sg-zorp-matrix"' in html and 'data-eyes="open open-big' in html


def _strip_comments(css):
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def _media_text(css, query):
    out = []
    for marker in re.finditer(r'@media\s*\(' + re.escape(query) + r'\)\s*\{', css):
        depth, i = 1, marker.end()
        while i < len(css) and depth:
            depth += {'{': 1, '}': -1}.get(css[i], 0)
            i += 1
        out.append(css[marker.end():i - 1])
    return '\n'.join(out)


FX_KEYFRAMES = ('zorp-twinkle', 'zorp-zzz', 'zorp-drop', 'zorp-pop', 'zorp-orbit')
FX_WILDCARD = '.buddy-mascot [class*="zorp-slot--fx"] *'


def test_fx_motion_mirrors():
    css = _strip_comments(MOTION_CSS.read_text(encoding='utf-8'))
    for name in FX_KEYFRAMES:
        assert f'@keyframes {name}' in css, name
    assert not re.search(r'--(wrong|correct)-\d+', css), 'face colours must never be grading colours'
    parts = (TEMPLATES / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    assert not re.search(r'--(wrong|correct)-', parts)
    # .zk/.zf are CSS rules, which beat presentation attributes: a colour attribute on a .zk
    # (stroke) or .zf (fill) element would be silently painted ink instead (review 2026-09-29).
    for tag in re.findall(r'<[a-z]+ [^>]*class="[^"]*\bzk\b[^"]*"[^>]*>', parts):
        assert ' stroke="' not in tag and ' fill="' not in tag, tag
    for tag in re.findall(r'<[a-z]+ [^>]*class="[^"]*\bzf\b[^"]*"[^>]*>', parts):
        assert ' fill="' not in tag, tag
    assert MOTION_CSS.stat().st_size <= MOTION_CSS_MAX_BYTES


def test_fx_keyframes_have_reduced_mirrors():
    """Every fx keyframe runs only under no-preference and is switched off (a) by the OS
    reduced-motion media query and (b) by both html[data-motion] mirrors (reduced and off),
    for every element inside the two fx slots. Comments never count."""
    css = _strip_comments(MOTION_CSS.read_text(encoding='utf-8'))
    enabled = _media_text(css, 'prefers-reduced-motion: no-preference')
    reduced = _media_text(css, 'prefers-reduced-motion: reduce')
    for name in FX_KEYFRAMES:
        uses = re.findall(r'[^{}]*\{[^{}]*animation:\s*' + name + r'\b[^{}]*\}', css)
        assert uses, f'{name} is never used'
        for use in uses:
            assert use.strip() in enabled, f'{name} must only run under prefers-reduced-motion: no-preference: {use.strip()}'
    assert re.search(re.escape(FX_WILDCARD) + r'\s*\{\s*animation:\s*none', reduced), 'OS reduced-motion mirror missing'
    for level in ('reduced', 'off'):
        assert re.search(r'html\[data-motion="' + level + r'"\]\s+' + re.escape(FX_WILDCARD) + r'[^{]*\{\s*animation:\s*none', css), level
    # every animated fx element sits inside one of the two fx slots, so the wildcard reaches it
    parts = (TEMPLATES / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    animated = re.findall(r'class="(zorp-(?:sp|z|h|gl|dr|pp|orb))"', parts)
    assert set(animated) == {'zorp-sp', 'zorp-z', 'zorp-h', 'zorp-gl', 'zorp-dr', 'zorp-pp', 'zorp-orb'}, set(animated)
    buddy = (TEMPLATES / 'partials' / 'buddy.html').read_text(encoding='utf-8')
    assert 'class="zorp-slot--fx"' in buddy and 'class="zorp-slot--fx-face"' in buddy


def test_twinkle_rate():
    """WCAG 2.3.1 / plan section 3.6: every keyframe that toggles opacity has duration / toggles
    of at least 333 ms (i.e. no more than 3 changes a second), for every declaration using it."""
    css = _strip_comments(MOTION_CSS.read_text(encoding='utf-8'))
    checked = 0
    for name, body in re.findall(r'@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)\s*\}', css):
        # Expand grouped selectors ("0%, 100%") into one stop each and sort by offset, so a
        # 1 -> 0.4 -> 1 twinkle counts as two toggles, not one (review 2026-09-29).
        stops = []
        for sel, decl in re.findall(r'([^{}]+)\{([^{}]*)\}', body):
            m = re.search(r'opacity:\s*([\d.]+)', decl)
            if not m:
                continue
            for key in sel.split(','):
                key = key.strip()
                pct = {'from': 0.0, 'to': 100.0}.get(key)
                stops.append((pct if pct is not None else float(key.rstrip('%')), float(m.group(1))))
        opacities = [v for _, v in sorted(stops)]
        toggles = sum(1 for a, b in zip(opacities, opacities[1:]) if a != b)
        if not toggles:
            continue
        uses = re.findall(r'animation:\s*' + re.escape(name) + r'\s+([\d.]+)(ms|s)\b', css)
        assert uses, f'{name} toggles opacity but no rule uses it'
        for value, unit in uses:
            ms = float(value) * (1000 if unit == 's' else 1)
            assert ms / toggles >= 333, f'{name}: {ms} ms / {toggles} toggles = {ms / toggles:.0f} ms (< 333)'
            checked += 1
    assert checked >= 3, 'expected the twinkle/zzz uses to be checked'



def test_side_arms_clear_the_face():
    """Side view (2026-09-30): the near arm hangs from behind the profile plate, so a front-view raise would sweep
    across the face. side_rot() lifts it over the top instead. For EVERY front angle and every arm shape the drawn
    arm (a segment from the shoulder to the hand, plus its stroke) stays clear of the profile eye, brow and mouth, a
    raise ends up in the upper half, and the tween from the hanging arm swings backwards (positive angle for the
    right arm), never forward through the face. The JS copy (sideRot) is compared in zorp_poses_harness.js."""
    import math

    from models import zorp_rig

    side = zorp_rig.VIEWS['side']
    sx, sy = 48.4 + side['armRf'][0], 40 + side['armRf'][1]          # the near shoulder in profile
    eye = (37.8 + side['eyeR'][0], 35.2 + side['eyeR'][1], 3.6)      # centre and largest eye radius
    mouth = (32 + side['mouth'][0], 44 + side['mouth'][1], 3.4)       # anchor and half width of the side mouths
    brow = (37.8 + side['brows'][0], 30, 3.2)                         # the side brows (x 35-40.6, y about 30)
    # hand point and hand radius per drawn art, in the arm's own frame (hanging down); see zorp_parts.html arm()
    reach = {'straight': ((0, 13.2), 2), 'fist': ((0, 29.6), 4.6), 'side-rest': ((1.4, 9.6), 2.6), 'side-bent': ((9.5, 8), 2.6)}

    def clear(rot, art):
        (hx, hy), hr = reach[art]
        t = math.radians(rot)
        px, py = sx + hx * math.cos(t) - hy * math.sin(t), sy + hx * math.sin(t) + hy * math.cos(t)
        for cx, cy, r in (eye, brow, mouth):
            ux, uy = px - sx, py - sy
            k = max(0, min(1, ((cx - sx) * ux + (cy - sy) * uy) / (ux * ux + uy * uy)))
            d = math.hypot(sx + k * ux - cx, sy + k * uy - cy)
            if d < r + (hr if k == 1 else 1.7):
                return False
        return True

    assert zorp_rig.pose_arms('think-chin', 'side') == ('side-rest', 'side-bent')
    assert zorp_rig.pose_arms('flex', 'side') == ('side-rest', 'fist') and zorp_rig.pose_arms('flex') == ('rest', 'bent-fist')
    for shape in zorp_rig.ARM_SHAPES:
        art = zorp_rig.SIDE_ARMS.get(shape, shape)
        if art == 'bent':
            continue  # never drawn in profile
        for front in range(-180, 181):
            rot = zorp_rig.side_rot(front, shape)
            assert rot == -zorp_rig.side_rot(-front, shape), 'the left arm mirrors the right'
            assert clear(rot, art), f'{shape} at {front} deg draws at {rot} deg across the profile face'
            if abs(front) >= 70 and art != 'side-bent':
                assert 180 <= abs(rot) <= 225 and (rot > 0) == (front < 0), f'{front}: a raise lifts over the top, backwards'
    # the poses keep their front-view angles; the side view remaps them (static render and runtime alike)
    for name, row in zorp_rig.POSES.items():
        assert zorp_rig.pose_transform('armR', row['armR'], 'r', 'side') == (
            f"rotate({zorp_rig._n(zorp_rig.side_rot(row['armR'][1], row['armR'][0]))}deg)" if row['armR'][1] else '')
        if row['armR'][1]:
            assert zorp_rig.pose_transform('armR', row['armR']) == f"rotate({zorp_rig._n(row['armR'][1])}deg)", 'front view unchanged'


def _check_side_profile(zorp_rig, parts):
    """Side view redesign (2026-09-30): every preset draws profile art for the eye and a mouth that sits on the
    wide profile plate, in both facings; one near arm only; the look-up and look-side eyes keep their direction."""
    from app import app

    side = zorp_rig.VIEWS['side']
    assert side['armL'] is None and side['armR'] is None and side['armLf'] is None and side['armRf'] is not None
    dx, _, sx, _ = side['plate']
    assert .6 <= sx <= .72, 'the profile plate is a wide shape, not a sliver'
    left, right = 32 + dx - 15.5 * sx, 32 + dx + 15.5 * sx
    assert right <= 32 + 21, 'the plate stays inside the body silhouette'
    assert zorp_rig.map_variant('side', 'eyes', 'look-up') == 'side-up'
    assert zorp_rig.map_variant('side', 'eyes', 'look-side') == 'side-fwd'
    for mouth in zorp_rig.CHANNELS['mouth']:
        variant = zorp_rig.map_variant('side', 'mouth', mouth)
        assert variant.startswith('side-'), f'{mouth} has no profile mouth'
        match = re.search(r"n == '%s' -%%\}\s*<[a-z]+[^>]*?(?:d=\"M([\d.]+)|cx=\"([\d.]+)\")" % re.escape(variant), parts)
        assert match, variant
        x0 = float(match.group(1) or match.group(2)) + side['mouth'][0]
        assert left + 4 <= x0 <= right - 2, f'{variant} starts at x {x0}, off the profile plate {left}-{right}'
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        assert zorp_rig.pose_arms('bow', 'side') == (zorp_rig.SIDE_ARM, zorp_rig.SIDE_ARM) and zorp_rig.pose_arms('bow') == ('rest', 'rest')
        assert zorp_rig.pose_arms('wave', 'side') == (zorp_rig.SIDE_ARM, 'straight')
        for face in zorp_rig.PRESETS:
            drawn = {}
            for facing in ('r', 'l'):
                svg = str(module.buddy_mascot(face=face, view='side', facing=facing))
                slot = re.search(r'class="zorp-slot--mouth"[^>]*>(.*?)</g>', svg, re.S).group(1).strip()
                assert slot and ('class="zk"' in slot or 'class="zf"' in slot), f'{face} facing {facing}: no mouth drawn in side view'
                assert ('scale:-1 1' in svg) == (facing == 'l')
                assert svg.count('class="buddy-arm buddy-arm--r-front" style="display:inline') == 1 and svg.count('display:inline') == 1, 'exactly one arm is drawn in side view'
                drawn[facing] = re.sub(r' style="scale:-1 1"', '', svg)
                assert 'data-facing="l"' in svg or facing == 'r'
                assert svg.count('class="zn zsa"') == 4, 'the profile paddle arm is drawn in side view (both arms, both layers)'
                assert zorp_rig.map_variant('back-glance', 'mouth', 'smile') == 'side-smile'
                glance = str(module.buddy_mascot(face=face, view='back-glance', facing=facing))
                assert re.search(r'class="zorp-slot--mouth"[^>]*>\s*<[a-z]', glance), f'{face}: back-glance draws a hint of smile'
                assert 'zsa' not in glance and 'zsa' not in str(module.buddy_mascot(face=face)), 'rest arms elsewhere'
            assert drawn['l'].replace(' data-facing="l"', '') == drawn['r'], f'{face}: facing left is the same art as facing right'

def test_views_complete():
    """E8 Phase 3: every view names every part (front-hidden arms aside), the hidden parts are explicit,
    the side variants exist as art and in the island, and each view renders within the element budget."""
    from app import app  # noqa: E402
    from models import zorp_rig

    zorp_rig.validate()
    assert zorp_rig.VIEW_NAMES == ('front', 'three-quarter', 'side', 'back', 'back-glance')
    assert set(zorp_rig.VIEWS) == set(zorp_rig.VIEW_NAMES)
    for name in zorp_rig.VIEW_NAMES:
        row = zorp_rig.VIEWS[name]
        assert set(row) == set(zorp_rig.VIEW_PARTS), (name, set(zorp_rig.VIEW_PARTS) ^ set(row))
        for part, entry in row.items():
            assert entry is None or len(entry) == 4, (name, part)
    for part in zorp_rig.FRONT_HIDDEN:
        assert zorp_rig.VIEWS['front'][part] is None, part
    # side: one eye, the far arm hidden, the front-layer arm shown; back: no face at all
    side = zorp_rig.VIEWS['side']
    assert side['eyeL'] is None and side['eyeR'] is not None and side['armRf'] is not None and side['armLf'] is None
    for part in ('eyeL', 'eyeR', 'mouth', 'brows', 'cheeks', 'plate'):
        assert zorp_rig.VIEWS['back'][part] is None, part
    assert zorp_rig.VIEWS['back']['hl'] is not None
    # side variants are real art, real channel values, and in the island
    parts = (TEMPLATES / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    for channel, variants in (('eyes', ('side', 'side-up', 'side-fwd')),
                              ('mouth', ('side-smile', 'side-o', 'side-flat', 'side-wavy', 'side-frown')),
                              ('brows', ('side',)), ('cheeks', ('side-rosy',))):
        for variant in variants:
            assert variant in zorp_rig.CHANNELS[channel], (channel, variant)
            assert f"'{variant}'" in parts, f'no art for {channel} {variant}'
    data = json.loads(zorp_rig.rig_json())
    assert 'w' in data and 'm' in data
    _check_side_profile(zorp_rig, parts)
    module = None
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        for view in zorp_rig.VIEW_NAMES:
            for facing in ('r', 'l'):
                for face in ('nudge', 'joy', 'thinking'):
                    svg = str(module.buddy_mascot(face=face, view=view, facing=facing))
                    assert _elements(svg) <= INSTANCE_MAX_ELEMENTS, (view, facing, face)
                    assert len(svg.encode('utf-8')) <= INSTANCE_DEFAULT_MAX_BYTES + 1_500, (view, facing, face)
                    assert svg.count('class="zorp-flip"') == 1
                    assert ('data-view=' in svg) == (view != 'front'), view
        # the default render is unchanged: no view attributes, no inline styles
        default = str(module.buddy_mascot())
        assert default.startswith(DEFAULT_SVG_START) and 'style="' not in default and 'data-view' not in default
        # unknown view or facing fails closed to the front view
        assert str(module.buddy_mascot(view='nope', facing='x')) == default


def test_guide_slapstick_lore_only():
    """Phase 2 review item: confused and bashful are slapstick/lore faces (plan section 5), so they may be
    used by guide.lore and guide.thanks style contexts, never the plain guide list."""
    from models import zorp_rig

    for face in zorp_rig.SLAPSTICK_LORE_ONLY:
        assert face not in zorp_rig.CONTEXT_MAP['guide'], face
        assert face in zorp_rig.CONTEXT_MAP['guide.lore'], face
    assert set(zorp_rig.SLAPSTICK_LORE_ONLY) == {'confused', 'bashful'}
    for step_id, face, lore, resolve, big in _catalog_steps():
        if face in zorp_rig.SLAPSTICK_LORE_ONLY:
            assert lore or step_id in zorp_rig.GUIDE_LORE_STEPS or face in zorp_rig.CONTEXT_MAP.get('guide.thanks', ()), (
                f'{step_id}: {face} outside a slapstick/lore step'
            )


def test_react_wrong_and_autoplay_empty_contexts():
    """Phase 2 review items: react.wrong never ends on oops (the oops beat is its own first-beat context),
    and autoplay.empty no longer offers sleepy."""
    from models import zorp_rig

    assert 'oops' not in zorp_rig.CONTEXT_MAP['react.wrong']
    assert zorp_rig.CONTEXT_MAP['react.wrong.first'] == ('oops',)
    assert 'sleepy' not in zorp_rig.CONTEXT_MAP['autoplay.empty']
    assert zorp_rig.valence('oops') != 'negative'


def test_prompt_faces_positive_and_match_client():
    """Phase 5: every prompt type draws an upbeat preset (the resting 'nudge' default aside), streak_risk is
    heads-up with no frown, and study-buddy.js keeps the identical table for its client-side render."""
    from models import buddy, zorp_rig

    assert set(zorp_rig.PROMPT_FACES) == set(buddy.BUDDY_TYPES), 'every buddy prompt type has a face'
    for kind, face in zorp_rig.PROMPT_FACES.items():
        if kind == 'nudge':
            assert zorp_rig.VALENCE[face] == 'neutral'  # the resting default: no prompt of this type is ever shown
        else:
            assert zorp_rig.VALENCE[face] == 'positive', (kind, face)
        assert f'prompt.{kind}' in zorp_rig.CONTEXT_MAP and zorp_rig.CONTEXT_MAP[f'prompt.{kind}'] == (face,)
    assert zorp_rig.PROMPT_FACES['streak_risk'] == 'heads-up'
    heads_up = zorp_rig.preset('heads-up')
    assert heads_up['mouth'] == 'smile' and heads_up['brows'] == 'raised' and heads_up['fx'] == 'flame'
    assert zorp_rig.preset('streak_risk') == heads_up
    sb = (JS_DIR / 'study-buddy.js').read_text(encoding='utf-8')
    m = re.search(r'var PROMPT_FACE = \{(.*?)\};', sb, re.S)
    assert m, 'study-buddy.js lost its PROMPT_FACE table'
    client = dict(re.findall(r"(\w+):\s*'([\w-]+)'", m.group(1)))
    assert client == zorp_rig.PROMPT_FACES, 'study-buddy.js PROMPT_FACE differs from zorp_rig.PROMPT_FACES'
    # the server renders the same face on the corner buddy's first paint
    base = (TEMPLATES / 'base.html').read_text(encoding='utf-8')
    assert 'zorp_rig.face_for_prompt(' in base


def test_streak_copy_is_upbeat_and_not_shaming():
    """Phase 5 (Children's Code std 13): no streak-loss framing in the buddy copy (the live prompt is asserted
    in test_buddy_smoke.py)."""
    src = (ROOT / 'models' / 'buddy.py').read_text(encoding='utf-8')
    messages = re.findall(r"message = (?:f)?'([^']*)'", src)
    assert any(m == 'Keep your {days}-day streak going with one quick question.' for m in messages), messages
    for line in messages:
        for banned in ('lose', 'lost', 'risk', 'break', 'broke', 'miss out', 'disappoint', "don't let", 'honest', 'guilt'):
            assert banned not in line.lower(), (banned, line)


def test_react_contexts_phase5():
    """Phase 5: a wrong answer is oops (the first beat only) then determined or soft-smile, and every react
    list is positive or neutral, without blush, sweat or sad eyes."""
    from models import zorp_rig

    assert zorp_rig.CONTEXT_MAP['react.wrong'] == ('determined', 'soft-smile')
    assert zorp_rig.CONTEXT_MAP['react.wrong.first'] == ('oops',)
    assert [c for c, faces in zorp_rig.CONTEXT_MAP.items() if c.startswith(('react.', 'prompt.', 'dismiss')) and 'oops' in faces] == ['react.wrong.first']
    banned = set(NEGATIVE_NAMES) | {'bashful', 'confused', 'embarrassed'}
    for context, faces in zorp_rig.CONTEXT_MAP.items():
        if context.startswith('react.'):
            assert not banned & set(faces), (context, banned & set(faces))
            for face in faces:
                ch = zorp_rig.PRESETS[face]
                assert ch['cheeks'] != 'blush' and ch['fx'] not in ('sweat', 'blush-steam', 'tear-shine'), (context, face)
    # the reaction runtime reads these lists from the island, so they must ship
    island = json.loads(zorp_rig.rig_json())['c']
    for context in ('react.correct', 'react.wrong', 'react.streak', 'react.milestone', 'react.lesson_complete',
                    'react.first_correct', 'guide.reward.big'):
        assert island[context] == list(zorp_rig.CONTEXT_MAP[context]), context
    assert set(zorp_rig.REACT_CLIPS) == {'correct', 'wrong', 'streak', 'first_correct', 'milestone', 'lesson_complete'}


def test_react_mapping_uses_context_map():
    """zorp-motion.js does not hard-code reaction faces any more: the plan in zorp-poses.js asks
    pbZorp.allowedIn('react.<kind>', preset) (CONTEXT_MAP via the island) and filters on positive valence."""
    poses = POSES_JS.read_text(encoding='utf-8')
    assert "pb.allowedIn('react.' + kind, n)" in poses and "pb.valenceOf(n) === 'positive'" in poses
    motion = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'reactHook' in motion and 'plan.big' in motion
    # the wrong-answer oops is a beat of oops-encourage, at most 300 ms, and the clip resolves on soft-smile
    m = re.search(r"add\('oops-encourage'.*?\]\s*\}\)\);", poses, re.S)
    assert m
    beats = re.findall(r"\{ pose: '(\w+)'(?:, expr: '([\w-]+)')?[^}]*?ms: (\d+)(?:, hold: (\d+))?", m.group(0))
    assert beats[0][1] == 'oops' and int(beats[0][2]) + int(beats[0][3] or 0) <= 300, beats[0]
    assert [b[1] for b in beats if b[1]][-1] == 'soft-smile'
    assert [b[1] for b in beats].count('oops') == 1, 'oops only ever as the first beat'


def test_guide_lore_and_big_reward_phase5():
    """Phase 5: origin.home is the one sad lore step (resolves to aww on its last line), the 100-day streak
    is the one big reward (aww-teary to proud), nothing else in the catalog is negative."""
    from models import zorp_rig

    text = (JS_DIR / 'guide-catalog.js').read_text(encoding='utf-8')
    steps = _catalog_steps()
    negative = [(i, f, lore, r, big) for i, f, lore, r, big in steps if zorp_rig.VALENCE[f] == 'negative']
    assert sorted((f, r) for _, f, _, r, _ in negative) == [('aww-teary', 'proud'), ('sad', 'aww')], negative
    assert zorp_rig.GUIDE_LORE_STEPS == ('origin.home',)
    home = [s for s in steps if s[0] == 'origin.home'][0]
    assert home[1] == 'sad' and home[2] and home[3] == 'aww'
    assert 'origin.home' in text.split("id: 'origin.nudge'")[0], 'the lore step sits before origin.nudge'
    # the lore copy is two lines: sad first, resolved on the last
    block = text[text.index("id: 'origin.home'"):text.index("id: 'origin.nudge'")]
    assert len(re.findall(r"^\s{10}'.*',$", block, re.M)) == 2
    assert 'lonely' not in text.lower() and 'miss you' not in text.lower() and 'come back' not in text.lower()
    # only steps with an id in GUIDE_LORE_STEPS may be lore; a lore step never resolves to a negative preset
    for step_id, face, lore, resolve, big in steps:
        if lore:
            assert step_id in zorp_rig.GUIDE_LORE_STEPS, step_id
            assert resolve and zorp_rig.VALENCE[resolve] == 'positive'
    guide = (JS_DIR / 'guide.js').read_text(encoding='utf-8')
    assert "big: !!template.big" in guide and "resolve: template.resolve || null" in guide
    assert "(step.lore || step.big) && lastLine && step.resolve" in guide
    # a multi-line big reward: the tap that follows line one reads 'Continue', not 'Close'
    big_block = text[text.index("'streak:100'"):text.index('first_correct: {')]
    assert "primary: 'Continue'" in big_block and big_block.count("'") >= 6 and "lines: ['100-day streak. Extraordinary.'," in big_block
    # every preset the catalog names exists
    for step_id, face, lore, resolve, big in steps:
        assert face in zorp_rig.PRESETS and (not resolve or resolve in zorp_rig.PRESETS)


def test_guide_gestures_phase5():
    """guide.js plays the new clips; the catalog uses only names the runtime has (core list or zorp-poses.js)."""
    guide = (JS_DIR / 'guide.js').read_text(encoding='utf-8')
    m = re.search(r'ZORP_GESTURES\s*=\s*\{([^}]*)\}', guide)
    names = set(re.findall(r"'?([\w-]+)'?\s*:\s*1", m.group(1)))
    assert {'side-point', 'fist-pump', 'victory', 'flex', 'shrug', 'think-chin', 'bow', 'dance', 'float'} <= names
    core = set(re.findall(r"'([\w-]+)'", re.search(r'CLIP_NAMES\s*=\s*\[([^\]]*)\]', RUNTIME_JS.read_text(encoding='utf-8')).group(1)))
    added = set(re.findall(r"\badd\('([\w-]+)'", POSES_JS.read_text(encoding='utf-8')))
    catalog = set(re.findall(r"gesture:\s*'([\w-]+)'", (JS_DIR / 'guide-catalog.js').read_text(encoding='utf-8')))
    assert catalog <= names and catalog <= core | added, catalog - (core | added)
    assert {'side-point', 'fist-pump', 'victory', 'flex', 'dance'} <= catalog, 'the Phase 5 refresh uses the new clips'


def test_welcome_and_empty_states_phase5():
    from models import zorp_rig

    welcome = (JS_DIR / 'welcome.js').read_text(encoding='utf-8')
    for needle in ("zorp.turn('front', 'r', { el: hero, required: true })", "zorp.play('wave'", "clipOr('side-point', 'point')",
                   "target: 'down'", "clipOr('think-chin', 'think')", "clipOr('fist-pump', 'cheer')", 'Promise.race', 'setTimeout(resolve, 450)'):
        assert needle in welcome, needle
    assert "play('cheer'" not in welcome.replace("clipOr('fist-pump', 'cheer')", '')
    tpl = (TEMPLATES / 'welcome.html').read_text(encoding='utf-8')
    assert "view='side'" not in tpl  # server draws the hero front-facing
    assert "zorp.turn('side', 'r', { el: hero, instant: true })" in welcome
    # empty states use the new calm clips, all allowlisted
    for name, clip in (('saved_problems.html', 'think-chin'), ('qotd.html', 'think-chin'), ('leaderboard_friends.html', 'think-chin'), ('follow_list.html', 'shrug')):
        assert f'data-zorp-autoplay="{clip}"' in (TEMPLATES / name).read_text(encoding='utf-8'), name
        assert clip in zorp_rig.AUTOPLAY_CLIPS
    # offline stays a static sleep; the PWA banner is a static soft smile (server drawn, no runtime needed)
    base = (TEMPLATES / 'base.html').read_text(encoding='utf-8')
    assert "buddy_mascot(face='soft-smile')" in base
    assert "buddy_mascot(face='sleep')" in (TEMPLATES / 'offline.html').read_text(encoding='utf-8')


def test_welcome_hello_hero_is_front_on_the_server():
    from app import app  # noqa: E402

    text = (TEMPLATES / 'welcome.html').read_text(encoding='utf-8')
    hero = re.search(r'<span class="study-buddy-face welcome-hero".*?</span>', text, re.S).group(0)
    assert 'view=' not in hero  # no-JS or a failed runtime shows him facing the pupil
    # the macro draws a profile only when asked: the default hero stays the front view
    with app.app_context():
        buddy = app.jinja_env.get_template('partials/buddy.html').module
        assert 'data-view="side"' in str(buddy.buddy_mascot(view='side'))
        assert 'data-view' not in str(buddy.buddy_mascot(view=None))


def test_runtime_js_budget():
    css = MOTION_CSS.stat().st_size
    js = RUNTIME_JS.stat().st_size
    print(f'  motion.css: {css} B; zorp-motion.js: {js} B')
    assert js <= RUNTIME_JS_MAX_BYTES, f'zorp-motion.js {js} B exceeds {RUNTIME_JS_MAX_BYTES}'
    text = RUNTIME_JS.read_text(encoding='utf-8')
    for name in ('setExpression', 'hasExpression', 'expressions', 'pb-zorp-rig', 'pb-zorp-parts', '.zorp-face .buddy-pupil'):
        assert name in text, name
    assert 'innerHTML' not in text, 'parts are cloned, never built from strings (E8 section 5)'


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
    assert 'data-gallery-phase="5"' in html
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


POSE_NAMES_REQUIRED = ('stand', 'wave', 'point-l', 'point-r', 'point-down', 'fist-up', 'victory', 'flex', 'think-chin',
                       'shrug', 'bow', 'peek', 'crouch', 'dance-a', 'dance-b', 'sit', 'float', 'sleep')
NEW_CLIPS = ('fist-pump', 'victory', 'flex', 'shrug', 'bow', 'think-chin', 'dance', 'float', 'oops-encourage', 'turn')
OLD_CLIPS = ('idle', 'blink', 'cheer', 'wobble', 'think', 'wave', 'point', 'nod', 'wink', 'tap', 'shake', 'hop', 'peek',
             'sleep', 'side-point')


def test_poses_complete():
    """E8 Phase 4: every pose defines every part, arm shapes exist as art and in the library, and a static
    pose= render stays inside the instance budget while the default render carries no pose markup."""
    from app import app  # noqa: E402
    from models import zorp_rig

    zorp_rig.validate()
    assert set(POSE_NAMES_REQUIRED) <= set(zorp_rig.POSES), set(POSE_NAMES_REQUIRED) - set(zorp_rig.POSES)
    assert zorp_rig.ARM_SHAPES == ('rest', 'straight', 'fist', 'bent', 'bent-fist')
    for name, row in zorp_rig.POSES.items():
        assert set(row) == set(zorp_rig.POSE_PARTS) | {'view', 'expr'}, name
    parts = (TEMPLATES / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    tpl, _island = _split_library(_library_html())
    for shape in zorp_rig.ARM_SHAPES:
        for side in ('l', 'r'):
            assert f'data-part="arm:{shape}-{side}"' in tpl, (shape, side)
    assert 'macro arm(' in parts
    # arm shapes are tiny: every one under 200 B in the library
    for m in re.finditer(r'<g data-part="arm:[a-z-]+">(.*?)</g>', tpl):
        assert len(m.group(1).encode()) <= 200, m.group(0)
    with app.app_context():
        module = app.jinja_env.get_template('partials/buddy.html').module
        default = str(module.buddy_mascot())
        assert 'data-pose' not in default and 'style="' not in default
        assert str(module.buddy_mascot(pose='stand')) == default.replace('<svg class="buddy-mascot"', '<svg class="buddy-mascot"', 1), 'stand is the default'
        assert str(module.buddy_mascot(pose='nope')) == str(module.buddy_mascot(pose='stand'))
        for name in zorp_rig.POSE_NAMES:
            svg = str(module.buddy_mascot(face=zorp_rig.POSES[name]['expr'] or 'nudge', pose=name))
            assert _elements(svg) <= INSTANCE_MAX_ELEMENTS, name
            assert len(svg.encode('utf-8')) <= INSTANCE_DEFAULT_MAX_BYTES, (name, len(svg.encode()))
            assert ('data-pose=' in svg) == (name != 'stand'), name
            for shape in set(zorp_rig.pose_arms(name)):
                if shape != 'rest':
                    assert 'class="zl"' in svg, (name, shape)
        # think-chin shows the front-layer twin over the body and hides the one behind it
        chin = str(module.buddy_mascot(pose='think-chin'))
        assert re.search(r'buddy-arm--r" style="display:none"', chin) and re.search(r'buddy-arm--r-front" style="display:inline"', chin)
        # raised arms (W4) are drawn in the front layer so the fist shows above the body, at every size
        for name, sides in (('fist-up', 'r'), ('victory', 'lr'), ('flex', 'r')):
            svg = str(module.buddy_mascot(pose=name))
            for side in sides:
                assert re.search(rf'buddy-arm--{side}" style="display:none"', svg), (name, side)
                assert re.search(rf'buddy-arm--{side}-front" style="display:inline;transform:rotate\(-?1?\d+deg\)"', svg), (name, side)
        # the shadow stays on the ground: float and crouch counter-translate the root's dy
        assert 'translate(0,8px) scale(.7,1)' in str(module.buddy_mascot(pose='float')), 'float shadow'
        assert 'translate(0,-3px) scale(1,1)' in str(module.buddy_mascot(pose='crouch')), 'crouch shadow'
        # a pose with a default view draws it unless a view is given; facing left mirrors the root
        assert 'data-view="side"' in str(module.buddy_mascot(pose='bow'))
        assert 'data-view' not in str(module.buddy_mascot(pose='bow', view='front'))
        assert 'rotate(18deg)' in str(module.buddy_mascot(pose='bow', facing='r'))
        assert 'rotate(-18deg)' in str(module.buddy_mascot(pose='bow', facing='l'))
        # the shadow keeps its own opacity
        assert 'opacity:.6' in str(module.buddy_mascot(pose='float'))


def test_poses_js_budget():
    js = POSES_JS.stat().st_size
    core = RUNTIME_JS.stat().st_size
    print(f'  zorp-motion.js: {core} B; zorp-poses.js: {js} B')
    assert js <= POSES_JS_MAX_BYTES, js
    assert core <= RUNTIME_JS_MAX_BYTES, core
    text = POSES_JS.read_text(encoding='utf-8')
    for name in ('pb.register(', 'compileBeats', 'clipInfo', "'fist-pump'", 'pb.pose = pose'):
        assert name in text, name
    assert 'innerHTML' not in text
    # the core exposes the hook and reports the new names as absent when the file does not load
    core_text = RUNTIME_JS.read_text(encoding='utf-8')
    for name in ('register: function', 'hasClip:', 'hasPose:', 'pose: function'):
        assert name in core_text, name
    # W6: hop and cheer keep the shadow on the ground (it counters the root's lift)
    assert "translate(0,9px) scale(0.75,1)" in core_text and "translate(0,8px) scale(0.7,1)" in core_text
    base = (TEMPLATES / 'base.html').read_text(encoding='utf-8')
    assert base.index('js/zorp-motion.js') < base.index('js/zorp-poses.js') < base.index('js/zorp-triggers.js')
    assert 'zorp-poses.js\') }}?v=3' in base
    sw = (JS_DIR / 'sw.js').read_text(encoding='utf-8')
    assert '/static/js/zorp-poses.js' in sw and '/static/js/zorp-motion.js' in sw


def _poses_js_beats():
    text = POSES_JS.read_text(encoding='utf-8')
    return text[text.index('var CL = rt.clips;'):]


def test_beats_reference_known_names():
    from models import zorp_rig

    text = _poses_js_beats()
    poses = set(re.findall(r"\bpose:\s*'([a-z-]+)'", text))
    exprs = set(re.findall(r"\bexpr:\s*'([a-z_-]+)'", text))
    fxs = set(re.findall(r"\bfx:\s*'([a-z-]+)'", text))
    views = set(re.findall(r"\bview:\s*'([a-z-]+)'", text))
    reduced = set(re.findall(r"\breduced:\s*'([a-z_-]+)'", text))
    assert poses and exprs and fxs
    assert poses <= set(zorp_rig.POSES), poses - set(zorp_rig.POSES)
    assert exprs <= set(zorp_rig.PRESETS), exprs - set(zorp_rig.PRESETS)
    assert reduced <= set(zorp_rig.PRESETS), reduced
    assert fxs <= set(zorp_rig.CHANNELS['fx']), fxs - set(zorp_rig.CHANNELS['fx'])
    assert views <= set(zorp_rig.VIEW_NAMES), views
    assert 'thought' in fxs and 'sparkles' in {zorp_rig.PRESETS['joy']['fx']}
    easings = set(re.findall(r"\b(?:ease|aease):\s*'([a-z]+)'", text))
    assert easings <= {'out', 'in', 'overshoot', 'io'}, easings
    # the named easing table carries the docs 3.10 curves
    table = re.search(r"var EASE = \{(.*?)\};", POSES_JS.read_text(encoding='utf-8')).group(1)
    for curve in ('cubic-bezier(.2,.8,.2,1)', 'cubic-bezier(.6,0,.9,.4)', 'cubic-bezier(.34,1.56,.64,1)'):
        assert curve in table, curve


def test_stretch_within_limits():
    """docs 3.10: squash and stretch stays within STRETCH_MAX per axis and roughly keeps volume."""
    from models import zorp_rig

    text = _poses_js_beats()
    pairs = [(float(a), float(b)) for a, b in re.findall(r"\bs:\s*\[([\d.]+),\s*([\d.]+)\]", text)]
    assert len(pairs) >= 5, pairs
    for sx, sy in pairs:
        assert abs(sx - 1) <= zorp_rig.STRETCH_MAX + 1e-9 and abs(sy - 1) <= zorp_rig.STRETCH_MAX + 1e-9, (sx, sy)
        assert abs(sx * sy - 1) <= 0.12, (sx, sy)
    for name, row in zorp_rig.POSES.items():
        sx, sy = row['root'][3], row['root'][4]
        assert abs(sx - 1) <= zorp_rig.STRETCH_MAX and abs(sy - 1) <= zorp_rig.STRETCH_MAX and abs(sx * sy - 1) <= 0.12, name


def test_every_new_clip_has_reduced_and_names_are_kept():
    text = _poses_js_beats()
    adds = re.findall(r"add\('([a-z-]+)', beatClip\(\{ reduced: '([a-z_-]+)'", text)
    assert {n for n, _ in adds} == set(NEW_CLIPS) - {'turn'}, adds
    assert "add('turn'," in text   # instant or nothing: pbZorp.turn's reduced rule
    core = RUNTIME_JS.read_text(encoding='utf-8')
    m = re.search(r"CLIP_NAMES = \[([^\]]+)\]", core)
    have = {c.strip().strip("'") for c in m.group(1).split(',')}
    assert set(OLD_CLIPS) <= have, set(OLD_CLIPS) - have
    from models import zorp_rig
    for _name, face in adds:
        assert zorp_rig.VALENCE[face] != zorp_rig.NEGATIVE, face


def test_clips_end_non_negative():
    """Data level: the last expression of every clip is a positive preset (the node harness checks the compiled
    beats and the 1.2 s rule; this reads the source literals)."""
    from models import zorp_rig

    text = _poses_js_beats()
    for name, body in re.findall(r"add\('([a-z-]+)', beatClip\((.*?)\)\);\n", text, re.S):
        exprs = re.findall(r"\bexpr:\s*'([a-z_-]+)'", body)
        if 'trip:' in body:
            main_part = body.split('trip:')[0]
            trip_part = body.split('trip:')[1]
            assert zorp_rig.VALENCE[re.findall(r"\bexpr:\s*'([a-z_-]+)'", main_part)[-1]] == zorp_rig.POSITIVE, name
            assert zorp_rig.VALENCE[re.findall(r"\bexpr:\s*'([a-z_-]+)'", trip_part)[-1]] == zorp_rig.POSITIVE, name
            for e in re.findall(r"\bexpr:\s*'([a-z_-]+)'", main_part):
                assert zorp_rig.VALENCE[e] != zorp_rig.NEGATIVE, (name, e)
            trip_neg = {e for e in re.findall(r"\bexpr:\s*'([a-z_-]+)'", trip_part) if zorp_rig.VALENCE[e] == zorp_rig.NEGATIVE}
            assert trip_neg == {'embarrassed'}, (name, trip_neg)   # the trip's only negative face is Zorp's own
            assert 'embarrassed' in zorp_rig.CONTEXT_MAP['clip.dance.trip']
            continue
        assert exprs, name
        assert zorp_rig.VALENCE[exprs[-1]] == zorp_rig.POSITIVE, f'{name} ends on {exprs[-1]}'
        for e in exprs:
            assert zorp_rig.VALENCE[e] != zorp_rig.NEGATIVE, (name, e)


def test_pose_gallery_markup():
    from app import app  # noqa: E402
    from models import zorp_rig

    html = app.test_client().get('/styleguide').data.decode()
    start = html.index('id="zorp-poselib"')
    section = html[start:html.index('</section>', start)]
    assert 'href="#zorp-poselib"' in html and 'data-poses-phase="4"' in html
    for name in zorp_rig.POSE_NAMES:
        for size in (56, 160):
            assert section.count(f'data-pose-name="{name}" data-pose-view=') >= 2, name
            assert f'data-pose-size="{size}"' in section
        assert f'data-zorp-pose="{name}"' in section, name
    for clip in NEW_CLIPS:
        assert f'data-zorp-clip="{clip}"' in section, clip
    for name in ('bow', 'sit'):   # poses with a default view also show the front
        assert f'data-pose-name="{name}" data-pose-view="front"' in section and f'data-pose-name="{name}" data-pose-view="side"' in section
    # server-drawn, not bound: only the live pair is data-zorp-demo
    assert section.count('data-zorp-demo') == 2
    assert 'zorp-poses.js' in html and 'styleguide.js?v=8' in html


def _idle_block():
    text = RUNTIME_JS.read_text(encoding='utf-8')
    start = text.index('// ---- Idle life (E8 Phase 7')
    end = text.index("document.addEventListener('visibilitychange'")
    return text[start:end]


def test_idle_life_rules():
    """Phase 7: idle life is WAAPI one-shots on timers, never a frame loop, and only under the section 5 conditions."""
    block = _idle_block()
    for name in ('requestAnimationFrame', 'setInterval', 'cancelAnimationFrame'):
        assert name not in RUNTIME_JS.read_text(encoding='utf-8'), f'zorp-motion.js must not use {name}'
        assert name not in POSES_JS.read_text(encoding='utf-8'), f'zorp-poses.js must not use {name}'
    # the gates: full motion, visible tab, on screen, quiet (typing / just pressed), nothing running, front view
    for needle in ("motionLevel() === 'full'", '!document.hidden', 'inst.vis', 'IntersectionObserver', 'typing()', 'lastInput',
                   '!inst.busy', "inst.view === 'front'", 'guide-open', 'data-motion', 'LOOK_GAP_MS = 45000', "lifeLoop(inst, 'a', 6000, 14000, act)"):
        assert needle in block, needle
    text = RUNTIME_JS.read_text(encoding='utf-8')
    assert "visibilitychange" in text and 'refreshIdle' in text
    # idle never touches the expression
    assert 'setExpression' not in block and 'tempFace' not in block and 'setFace' not in block
    # the look-around is a clip with no face and no reducedFace (reduced motion skips it)
    clip = text[text.index("CLIPS['look-around']"):text.index('function play(')]
    assert "view: 'three-quarter'" in clip and 'face:' not in clip.replace('reducedFace', '')
    assert "'look-around'" in text[:text.index('var SLOT_KEYS')]
    # decorative autoplay never starts it (not in zorp-triggers' allowlist) and the Guide never calls idle
    assert 'look-around' not in (JS_DIR / 'zorp-triggers.js').read_text(encoding='utf-8')
    assert 'pbZorp.idle' not in (JS_DIR / 'guide.js').read_text(encoding='utf-8')


def test_phase7_polish():
    parts = (TEMPLATES / 'partials' / 'zorp_parts.html').read_text(encoding='utf-8')
    css = MOTION_CSS.read_text(encoding='utf-8')
    # glow cheeks: dark themes get a rose glow instead of olive gold at half opacity
    assert parts.count('--zorp-glow') >= 3
    assert css.count('--zorp-glow:') == 2 and 'prefers-color-scheme: dark' in css and ':root[data-theme="dark"] .buddy-mascot' in css
    # the sparkle eye's star is large enough to read at 56 px (arms of about 2.5 units either way, plus a second catch-light)
    sparkle = re.search(r"n == 'sparkle' -%}\n(.*?)\n\{%- elif", parts, re.S).group(1)
    assert 'q.4 2.3 2.3 2.6' in sparkle and 'r=".55"' in sparkle
    # the thinking brows are soft arcs with inner ends level, not lowered towards each other
    knit = re.search(r"n == 'knit' -%}\n(.*?)\n\{%- elif", parts, re.S).group(1)
    assert 'M23.4 29.4q2.9-1.5 5.8 0' in knit
    # sweat in profile sits on the temple behind the eye
    assert '.zorp-dr { translate: -15px -1px; }' in css
    base = (TEMPLATES / 'base.html').read_text(encoding='utf-8')
    assert 'Study streak at risk' not in base and 'keeps your streak going' in base
    sw = (JS_DIR / 'sw.js').read_text(encoding='utf-8')
    assert "pb-v99" in sw and 'ignoreSearch: true' in sw


def test_phase7_runtime_fixes_static():
    text = RUNTIME_JS.read_text(encoding='utf-8')
    assert 'return !missing;' in text and 'return drawn;' in text      # setFace is false without the parts library
    assert 'function tidy(inst)' in text and 'tidy(inst);' in text      # no translate/scale residue after turning back
    assert "fxFace.style.display = 'none'" in text                      # a thought never shares the spot with sweat
    assert 'once(inst, slot, frames' in text                            # part-swap squeezes are tracked by stop()
    poses = POSES_JS.read_text(encoding='utf-8')
    assert 'shapeOf' not in poses and 'function (kind, now, keep)' in poses
    for dead in ('api: window.pbZorp', 'canAnimate: canAnimate', 'kf: kf'):
        assert dead not in text, dead


def main():
    test_no_animation_libraries()
    test_presets_complete()
    test_js_fallback_table_matches_rig()
    test_default_render_budget()
    test_full_look_budget()
    test_library_and_island_budget()
    test_page_mascot_budget()
    test_unknown_face_fails_closed()
    test_offline_sleep_draws_eyes()
    test_valence_classified()
    test_no_negative_in_prompt_faces()
    test_negative_presets_restricted()
    test_blush_never_on_react()
    test_consumers_filter_by_valence()
    test_data_expr_kept_in_sync()
    test_rig_json_escapes_lt()
    test_face_fx_slot_markup()
    test_picker_and_gallery_markup()
    test_fx_motion_mirrors()
    test_fx_keyframes_have_reduced_mirrors()
    test_twinkle_rate()
    test_runtime_js_budget()
    test_views_complete()
    test_side_arms_clear_the_face()
    test_guide_slapstick_lore_only()
    test_react_wrong_and_autoplay_empty_contexts()
    test_prompt_faces_positive_and_match_client()
    test_streak_copy_is_upbeat_and_not_shaming()
    test_react_contexts_phase5()
    test_react_mapping_uses_context_map()
    test_guide_lore_and_big_reward_phase5()
    test_guide_gestures_phase5()
    test_welcome_and_empty_states_phase5()
    test_welcome_hello_hero_is_front_on_the_server()
    test_gallery_section()
    test_snapshot_tool_is_dev_only()
    test_snapshot_label_guard()
    test_snapshot_compare_is_mascot_box_only()
    test_poses_complete()
    test_poses_js_budget()
    test_beats_reference_known_names()
    test_stretch_within_limits()
    test_every_new_clip_has_reduced_and_names_are_kept()
    test_clips_end_non_negative()
    test_pose_gallery_markup()
    test_idle_life_rules()
    test_phase7_polish()
    test_phase7_runtime_fixes_static()
    test_decisions_recorded()
    print('Zorp expression smoke (E8 Phase 7) passed.')


if __name__ == '__main__':
    main()
