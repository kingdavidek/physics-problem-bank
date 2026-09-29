"""E8 Zorp expressions: budgets, presets, parts library, safeguarding (docs/ZORP_EXPRESSIVENESS.md).

Run: python scripts/test_zorp_expression_smoke.py

Phase 0 recorded the section 2.1 ledger at its baseline. Phase 1 (2026-09-29) built the
expression engine (models/zorp_rig.py, templates/partials/zorp_parts.html and
zorp_library.html, the slot-based buddy.html) and flips every ledger constant to its cap; the
measured value is in each constant's comment. Later phases extend this file.
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
TEMPLATES = ROOT / 'templates'
DOC = ROOT / 'docs' / 'ZORP_EXPRESSIVENESS.md'
SNAPSHOT_TOOL = ROOT / 'scripts' / 'zorp_gallery_snapshot.py'

# §2.1 ledger caps (Phase 1, measured 2026-09-29).
INSTANCE_DEFAULT_MAX_BYTES = 4_500  # measured 2,454 B (baseline 7,249)
INSTANCE_MAX_ELEMENTS = 70  # measured 39 (baseline 98)
INSTANCE_LOOK_MAX_BYTES = 5_800  # measured 3,624 B (baseline 8,344)
PAGE_MASCOT_MAX_BYTES = 36_000  # 3 instances + library + island; see test_page_mascot_budget output
PAGE_MASCOT_MAX_GZIP = 6_000
RUNTIME_JS_MAX_BYTES = 48_000  # baseline 26_602; Phase 1 measured in test_runtime_js_budget output
PARTS_LIBRARY_MAX_BYTES = 16_000  # <template> only; measured in test_library_and_island_budget output
RIG_JSON_MAX_BYTES = 6_000  # island; measured 1,359 B with tags (1,301 B JSON)
MOTION_CSS_MAX_BYTES = 12_000  # mirrors test_zorp_motion_smoke.py; baseline 4_844, Phase 1 6_445

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
    for name in ('soft-smile', 'grin', 'happy', 'joy', 'laugh', 'smug', 'wow', 'aww', 'bashful', 'determined'):
        assert name in zorp_rig.PRESETS, name
    assert len(zorp_rig.NEW_PRESETS) >= 10
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
    # every mouth/eye a face may use is listed once; no part id is a frown yet (Phase 2 adds it)
    assert not any('frown' in vid for ids in zorp_rig.CHANNELS.values() for vid in ids)


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
    assert zorp_rig.face_for_prompt('streak_risk') == 'streak_risk'  # Phase 5 switches this to heads-up
    for kind in ('milestone', 'celebrate', 'qotd_nudge', 'weak_topic', 'friend_challenge', 'nudge'):
        assert zorp_rig.face_for_prompt(kind) == kind
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
    # Phase 1 ships no negative preset at all
    assert 'negative' not in zorp_rig.VALENCE.values()


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
    assert 'data-zorp-slow' in html and 'id="pb-zorp-parts"' in html and 'styleguide.js?v=5' in html


def test_fx_motion_mirrors():
    css = MOTION_CSS.read_text(encoding='utf-8')
    for name in ('zorp-twinkle', 'zorp-zzz'):
        assert f'@keyframes {name}' in css
    assert css.count('animation: none') >= 3
    assert 'html[data-motion="reduced"] .buddy-mascot .zorp-sp' in css
    assert 'html[data-motion="off"] .buddy-mascot .zorp-z' in css
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
    assert 'data-gallery-phase="1"' in html
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
    test_picker_and_gallery_markup()
    test_fx_motion_mirrors()
    test_runtime_js_budget()
    test_gallery_section()
    test_snapshot_tool_is_dev_only()
    test_snapshot_label_guard()
    test_decisions_recorded()
    print('Zorp expression smoke (E8 Phase 1) passed.')


if __name__ == '__main__':
    main()
