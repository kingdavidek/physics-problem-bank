"""E10 phases 1 and 2: the Zorp stage and the arrival film (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md 6.1, A1, section 10).

Run: python scripts/test_zorp_stage_smoke.py

* Files and caps: the new on-demand files have their own byte caps; no library, no CDN, nodes only, transform and opacity only.
* The props template (static/images/stage-props.svg) is inert: well-formed XML, no script, no links, no foreign content.
* The catalog (static/js/stage-catalog.js): shape, every beat names something the runtime has, every scene starts and ends on a
  positive or neutral face (CONTEXT_MAP['stage']), the voice rules on every line, and section 10 change 3 (no stamp promise).
* Lazy loading: ordinary pages carry only the asset island, never a <script> or <link> for the stage; not precached.
* The arrival: /welcome carries the slot nodes for scene 6; every accepted welcome step records the origin story as seen;
  finishing or skipping marks welcome done and origin seen; a refused step writes nothing.
* Settings: one "Replay the arrival" (the old actions still work); sound on for new accounts.
* Reduced and off paths, the API the later phases call, the dialog and focus rules, the dialogue-box origin fallback.
The browser walk (Playwright, phone and desktop, light, dark and reduced motion) is in the plan's Progress section.
"""
import json
import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS = ROOT / 'static' / 'js'
CSS = ROOT / 'static' / 'css'
STAGE_JS = JS / 'zorp-stage.js'
CATALOG_JS = JS / 'stage-catalog.js'
STAGE_CSS = CSS / 'stage.css'
PROPS_SVG = ROOT / 'static' / 'images' / 'stage-props.svg'

# Own caps for the on-demand files (plan 6.4 proposed 24 KB, 10 KB and 12 KB; the catalog is new).
STAGE_JS_MAX_BYTES = 27_000   # 2026-11-13 RAISED 24_000 -> 27_000: the celebration sounds button, quiet on close, the sound library loaded beside the stage (26,386 B)
STAGE_CSS_MAX_BYTES = 12_200   # 2026-11-13 E10 Phase 9 review RAISED 11_000 -> 12_200: a phone on its side shows the picture beside the panel (11,587 B); 2026-11-13 RAISED 10_000 -> 11_000: the celebration sounds button (10,564 B)
PROPS_MAX_BYTES = 12_000
CATALOG_MAX_BYTES = 8_000

LAYOUTS = {'centre', 'left', 'choose'}
PROPS = {'planet', 'ship', 'logbook', 'card'}
BEAT_KEYS = {'prop', 'zorp', 'play', 'turn', 'face', 'crew', 'burst', 'talk', 'wait'}
BEAT_EXTRA = {'set', 'async', 'target', 'facing'}


def _read(path):
    return Path(path).read_text(encoding='utf-8')


# ---- a tiny reader for the catalog's JavaScript object literal (single-quoted strings, bare keys, trailing commas) ----
def js_literal(src):
    out = []
    i = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c == "'":
            j = i + 1
            buf = []
            while src[j] != "'":
                if src[j] == '\\':
                    buf.append(src[j + 1])
                    j += 2
                    continue
                buf.append(src[j])
                j += 1
            out.append(json.dumps(''.join(buf)))
            i = j + 1
        elif src.startswith('//', i):
            i = src.index('\n', i)
        elif c.isalpha() or c == '_':
            m = re.match(r'[A-Za-z_]\w*', src[i:])
            word = m.group(0)
            i += len(word)
            if re.match(r'\s*:', src[i:]):
                out.append(json.dumps(word))
            elif word in ('true', 'false', 'null'):
                out.append(word)
            else:
                raise ValueError(f'unexpected identifier {word!r}')
        else:
            out.append(c)
            i += 1
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', ''.join(out)))


def catalog():
    src = _read(CATALOG_JS)
    start = src.index('window.pbStageCatalog = ') + len('window.pbStageCatalog = ')
    depth = 0
    k = start
    while k < len(src):
        ch = src[k]
        if ch == "'":   # skip a string, escapes included
            k += 1
            while src[k] != "'":
                k += 2 if src[k] == '\\' else 1
        elif src.startswith('//', k):   # a line comment may hold an apostrophe
            k = src.index('\n', k)
            continue
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return js_literal(src[start:k + 1])
        k += 1
    raise AssertionError('catalog literal not closed')


def runtime_clips():
    core = _read(JS / 'zorp-motion.js')
    names = set(re.findall(r"'([\w-]+)'", re.search(r'CLIP_NAMES\s*=\s*\[([^\]]*)\]', core).group(1)))
    names |= set(re.findall(r"\badd\('([\w-]+)'", _read(JS / 'zorp-poses.js')))
    names |= set(re.findall(r"\badd\('([\w-]+)'", _read(STAGE_JS)))
    names |= {'nod', 'wink', 'tap', 'shake'}   # the E6 CSS gestures play() also takes
    return names


def _csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html) or re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def _register(client, tag='st'):
    handle = f'{tag}_{uuid.uuid4().hex[:8]}'
    r = client.get('/register')
    r = client.post('/register', data={
        'csrf_token': _csrf(r.data.decode()), 'email': f'{handle}@example.com', 'handle': handle,
        'password': 'password123', 'confirm_password': 'password123', 'age_confirm': '1',
    })
    assert r.status_code == 302 and r.headers['Location'] == '/welcome', r.headers.get('Location')
    return handle


def _guide_json(handle):
    from app import get_db

    with get_db() as conn:
        row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = (SELECT id FROM users WHERE handle = ?)',
                           (handle,)).fetchone()
        return json.loads(row['guide_json'] or '{}')


# ---------------------------------------------------------------------------------------------
# Files, caps, hygiene
# ---------------------------------------------------------------------------------------------

def test_files_and_caps():
    for path, cap in ((STAGE_JS, STAGE_JS_MAX_BYTES), (STAGE_CSS, STAGE_CSS_MAX_BYTES), (PROPS_SVG, PROPS_MAX_BYTES),
                      (CATALOG_JS, CATALOG_MAX_BYTES)):
        size = path.stat().st_size
        print(f'  {path.relative_to(ROOT)}: {size:,} of {cap:,} (headroom {cap - size:,})')
        assert size <= cap, f'{path.name} {size} B exceeds its cap {cap}'
    for path in (STAGE_JS, CATALOG_JS):
        text = _read(path)
        for banned in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval(', 'new Function', 'setInterval',
                       'requestAnimationFrame', 'localStorage', 'http://', 'https://'):
            assert banned not in text, f'{path.name} uses {banned}'
    for path in (STAGE_JS, CATALOG_JS, STAGE_CSS, PROPS_SVG):
        low = _read(path).lower()
        for lib in ('lottie', 'gsap', 'rive', 'anime.js', 'cdn', 'jsdelivr', 'unpkg'):
            assert not re.search(r'(?<![\w-])' + re.escape(lib) + r'(?![\w-])', low), f'{path.name} mentions {lib}'
    # zorp-poses.js keeps its budget: the stage's composite clips are registered from zorp-stage.js
    assert (JS / 'zorp-poses.js').stat().st_size <= 36_500
    stage = _read(STAGE_JS)
    assert 'z.register(function (rt)' in stage and "add('stage-arrive'" in stage and "add('stage-gaze'" in stage
    assert 'stage-' not in _read(JS / 'zorp-poses.js')


def test_css_animates_transform_and_opacity_only():
    css = _read(STAGE_CSS)
    for m in re.finditer(r'@keyframes\s+([\w-]+)\s*\{(.*?)\}\s*\}', css, re.S):
        props = set(re.findall(r'([a-z-]+)\s*:', m.group(2)))
        assert props <= {'transform', 'opacity'}, f'@keyframes {m.group(1)} animates {props}'
    for m in re.finditer(r'transition\s*:\s*([^;]+);', css):
        for part in re.split(r',(?![^()]*\))', m.group(1)):   # commas inside cubic-bezier() are not separators
            assert part.split()[0] in ('transform', 'opacity'), f'transition on {part.strip()!r}'
    assert 'transition-property' not in css
    js = _read(STAGE_JS)
    # every WAAPI keyframe in the runtime moves transform or opacity only
    for frames in re.findall(r'\[\{ (?:transform|opacity)[^\]]*\]', js):
        keys = set(re.findall(r'\b([a-zA-Z]+):', frames)) - {'offset'}
        assert keys <= {'transform', 'opacity'}, frames
    assert 'left:' not in js and '.style.left' not in js and '.style.top' not in js


def test_props_template_is_inert():
    root = ET.parse(PROPS_SVG).getroot()   # well-formed XML (a "--" in a comment once broke the parse)
    ns = '{http://www.w3.org/2000/svg}'
    ids = {}
    for el in root.iter():
        tag = el.tag.replace(ns, '')
        assert tag not in ('script', 'foreignObject', 'a', 'image', 'use', 'iframe', 'style'), f'props template has <{tag}>'
        for attr, value in el.attrib.items():
            name = attr.split('}')[-1]
            assert not name.lower().startswith('on'), f'event attribute {name}'
            assert name != 'href', 'no links in the props template'
            assert 'javascript' not in value.lower()
        if 'id' in el.attrib:
            ids[el.attrib['id']] = el
    for need in ('st-planet', 'st-ship', 'st-ship-rim', 'st-logbook', 'st-card'):
        assert need in ids and ids[need].tag == ns + 'svg', need
    # a clip-path reference must resolve inside the same prop, because each prop is cloned alone
    for pid in ('st-planet', 'st-ship', 'st-ship-rim', 'st-logbook', 'st-card'):
        own = {el.attrib['id'] for el in ids[pid].iter() if 'id' in el.attrib}
        for el in ids[pid].iter():
            for value in el.attrib.values():
                for ref in re.findall(r'url\(#([\w-]+)\)', value):
                    assert ref in own, f'{pid} refers to #{ref} outside itself'
    text = _read(PROPS_SVG)
    assert 'var(--' not in text, 'prop colours are literal: the stage is night sky in both themes'
    # every state class the CSS styles exists in the props, and every data-set state the catalog uses has CSS
    css = _read(STAGE_CSS)
    for cls in set(re.findall(r'\.(st-[\w-]+)', css)):
        assert f'"{cls}"' in text or f' {cls}"' in text or f'"{cls} ' in text, f'CSS styles .{cls} that no prop has'


# ---------------------------------------------------------------------------------------------
# The catalog
# ---------------------------------------------------------------------------------------------

def test_catalog_shape_and_beats():
    from models import zorp_rig

    cat = catalog()
    scenes = {s['id']: s for s in cat['scenes']}
    assert len(scenes) == len(cat['scenes']), 'scene ids are unique'
    assert cat['arrival'] == ['arrival.land', 'arrival.novara', 'arrival.mission', 'arrival.crew', 'arrival.help'], cat['arrival']
    assert scenes['arrival.choose'].get('slot') is True, 'scene 6 shows the page\'s real forms'
    clips = runtime_clips()
    css = _read(STAGE_CSS)
    states = set(re.findall(r'\[data-set~=(\w+)\]', css))
    for sid, sc in scenes.items():
        assert sc.get('heading'), sid
        assert sc.get('layout') in LAYOUTS, (sid, sc.get('layout'))
        assert set(sc.get('props', [])) <= PROPS, sid
        lines = sc.get('lines', [])
        if sc.get('slot'):
            assert not lines and len(sc['beats']) == 1, sid
        else:
            assert 1 <= len(lines) <= 2 and len(sc['beats']) == len(lines), f'{sid}: one beat list per line'
            assert sc.get('primary') and sc.get('skipLabel') == 'Skip intro', sid
        for beats in sc['beats']:
            for b in beats:
                acts = set(b) & BEAT_KEYS
                assert len(acts) == 1 and set(b) <= BEAT_KEYS | BEAT_EXTRA, (sid, b)
                if 'play' in b or 'crew' in b:
                    assert b.get('play', b.get('crew')) in clips, (sid, b)
                if 'turn' in b:
                    assert b['turn'] in zorp_rig.VIEW_NAMES, (sid, b)
                if 'prop' in b:
                    assert b['prop'] in PROPS | {'streak'}, (sid, b)
                    if 'set' in b:
                        assert b['set'] in states, f'{sid}: no CSS for data-set state {b["set"]!r}'
                        assert b['prop'] in sc.get('props', []), f'{sid}: sets {b["prop"]} without listing it'
                if 'zorp' in b:
                    assert b['zorp'] == 'arrive', (sid, b)
                if 'wait' in b:
                    assert 0 < b['wait'] <= 1200, (sid, b)
    # the crew scene shows the crew (a crew beat), scene 1 lands, scene 2 looks up, scene 5 shows the hint card
    flat = {sid: [b for beats in sc['beats'] for b in beats] for sid, sc in scenes.items()}
    assert any(b.get('crew') == 'wave' for b in flat['arrival.crew'])
    assert any(b.get('turn') == 'back-glance' for b in flat['arrival.crew'])
    assert any(b.get('zorp') == 'arrive' for b in flat['arrival.land']) and any(b.get('play') == 'wave' for b in flat['arrival.land'])
    assert any(b.get('play') == 'stage-gaze' for b in flat['arrival.novara']) and any(b.get('play') == 'think-chin' for b in flat['arrival.novara'])
    assert any(b.get('set') == 'hint' for b in flat['arrival.help'])
    assert any(b.get('play') == 'think-chin' for b in flat['arrival.choose'])
    # timing stays calm: no scene line carries more than about 8 s of beats, and nothing advances by itself
    stage = _read(STAGE_JS)
    assert 'goScene(S.i + 1)' in stage and stage.count('goScene(') <= 6
    assert not re.search(r'setTimeout\(\s*onNext', stage) and 'autoplay' not in stage.lower()


def test_every_scene_starts_and_ends_positive_or_neutral():
    from models import zorp_rig

    assert 'stage' in zorp_rig.CONTEXT_MAP
    allowed = zorp_rig.CONTEXT_MAP['stage']
    assert all(zorp_rig.VALENCE[f] != 'negative' for f in allowed)
    for sc in catalog()['scenes']:
        for key in ('face', 'end'):
            face = sc[key]
            assert face in allowed and zorp_rig.VALENCE[face] in ('positive', 'neutral'), (sc['id'], key, face)
        for beats in sc['beats']:
            for b in beats:
                if 'face' in b:
                    assert b['face'] in allowed, (sc['id'], b)
    # the stage's own clips use only non-negative presets, and the runtime refuses a negative one as its own guard
    stage = _read(STAGE_JS)
    for face in re.findall(r"\bexpr: '([\w-]+)'", stage) + re.findall(r"\), '([\w-]+)'\)\);", stage):
        assert zorp_rig.VALENCE[face] != 'negative', face
    assert "z.valenceOf(name) !== 'negative'" in stage
    negative = {n for n, v in zorp_rig.VALENCE.items() if v == 'negative'}
    for path in (STAGE_JS, CATALOG_JS):
        text = _read(path)
        for name in negative:
            assert f"'{name}'" not in text, f'{path.name} names negative preset {name}'


def test_voice_rules_on_every_line():
    from models import zorp_voice as voice

    items, errors = voice.extract_stage_catalog()
    assert not errors, errors
    lines = [i for i in items if i.kind == 'line']
    assert len(lines) == 8, [i.text for i in lines]
    found = [v for v in voice.lint(items) if v.level in ('error', 'warn') and v.item.path != '(inventory)']
    assert not found, '\n'.join(f'{v.item.ref} {v.rule}: {v.detail} | {v.item.text}' for v in found)
    for it in items:
        assert it.voice == 'zorp'
        if it.surface == 'guide_line':
            assert len(it.text) <= 100 and it.text.count('!') <= 1, it.text
            assert not re.search(r'[–—]|\s-\s', it.text), it.text
        if it.surface == 'button_label':
            assert len(it.text) <= 22, it.text
        if it.dismiss:
            assert it.text in voice.DISMISS_APPROVED, it.text
    text = ' '.join(i.text.lower() for i in lines)
    # section 10 change 3: the logbook is a story device, no stamp promise; Zorp cheers when they reach something new
    assert 'stamp' not in text and 'badge' not in text and 'logbook' in text and 'something new' in text and 'cheer' in text
    # the homesick line moved to a later chapter (A1); the bot line is there
    assert 'home' not in text and 'miss' not in text and "i’m a bot, not a person" in text
    # scene 6's words are the page's own (welcome.html), marked for the lint
    welcome = _read(ROOT / 'templates' / 'welcome.html')
    for line in ('What do you want to practise?', 'Good choice. Your first question is ready.'):
        assert f'data-zorp-voice="zorp:welcome_line">{line}<' in welcome, line


# ---------------------------------------------------------------------------------------------
# Lazy loading
# ---------------------------------------------------------------------------------------------

def test_lazy_loading():
    from app import app

    base = _read(ROOT / 'templates' / 'base.html')
    for name in ('zorp-stage.js', 'stage.css', 'stage-catalog.js', 'stage-props'):
        assert name not in base, f'base.html must not mention {name}'
    partial = _read(ROOT / 'templates' / 'partials' / 'guide.html')
    assert 'id="pb-stage-assets"' in partial and partial.count('?v=') == 4 + 2 + 3 + 3 + 2 + 3   # 2026-11-08: E10 phase 8 adds the story island's three files (js, css, props); 2026-11-08: E10 phase 6 adds the tour island's two files (js, css); phase 5 adds the moments island's three (js, css, props); 2026-11-08: phase 3 adds the coach island's two files; phase 4 the badge island's three (js, css, props)
    sw = _read(JS / 'sw.js')
    for name in ('zorp-stage.js', 'stage.css', 'stage-catalog.js', 'stage-props.svg'):
        assert name not in sw, f'{name} is not precached (plan 6.4)'
    guide = _read(JS / 'guide.js')
    assert 'function loadStage()' in guide and "getElementById('pb-stage-assets')" in guide
    assert "addAsset('script', { src: a.js })" in guide and "addAsset('link', { rel: 'stylesheet', href: a.css })" in guide

    def assert_lazy(html, where):
        assert not re.search(r'<script[^>]+src="[^"]*(?:zorp-stage|stage-catalog)\.js', html), where
        assert not re.search(r'<link[^>]+href="[^"]*/stage\.css', html), where

    with app.test_client() as guest:
        html = guest.get('/').data.decode()
        assert_lazy(html, 'guest /')
        assert 'pb-stage-assets' not in html, 'no stage for guests'
    with app.test_client() as client:
        _register(client)
        for path in ('/', '/profile', '/welcome', '/topics'):
            r = client.get(path)
            assert r.status_code == 200, path
            html = r.data.decode()
            assert_lazy(html, path)
            m = re.search(r'<script type="application/json" id="pb-stage-assets">(.*?)</script>', html, re.S)
            assert m, path
            assets = json.loads(m.group(1))
            assert set(assets) == {'js', 'css', 'catalog', 'props'} and all('?v=' in v for v in assets.values()), assets
        for url in ('/static/js/zorp-stage.js', '/static/css/stage.css', '/static/js/stage-catalog.js', '/static/images/stage-props.svg'):
            r = client.get(url)
            assert r.status_code == 200, url


# ---------------------------------------------------------------------------------------------
# The arrival on /welcome
# ---------------------------------------------------------------------------------------------

def test_welcome_page_hands_its_forms_to_scene_6():
    from app import app

    tpl = _read(ROOT / 'templates' / 'welcome.html')
    assert "welcome.js') }}?v=6" in tpl
    with app.test_client() as client:
        _register(client)
        hello = client.get('/welcome').data.decode()
        # the level choice is on the hello page, hidden, for scene 6 (no navigation between scene 5 and 6)
        m = re.search(r'<div class="welcome-screen" id="welcome-screen-level" data-arrival-slot="1" hidden>', hello)
        assert m, 'hidden level screen on the hello step'
        assert re.search(r'<form[^>]*id="welcome-skip-form-hello" data-arrival-slot="3"', hello)
        assert 'name="level" value=' in hello and 'id="welcome-screen-hello"' in hello
        token = _csrf(hello)
        client.post('/welcome/step', data={'csrf_token': token, 'step': 'level', 'level': 'gcse_maths'})
        topic = client.get('/welcome?step=topic').data.decode()
        assert 'id="welcome-screen-topic" data-arrival-slot="1"' in topic and 'data-arrival-slot="3"' in topic
        client.post('/welcome/step', data={'csrf_token': _csrf(topic), 'step': 'topic', 'topic': 'surprise'})
        ready = client.get('/welcome?step=ready').data.decode()
        for marker in ('id="welcome-screen-ready" data-arrival-slot="1"', 'id="welcome-ready-form" data-arrival-slot="2"',
                       'id="welcome-ready-bar" data-arrival-slot="3"', 'id="welcome-skip-form-ready" data-arrival-slot="4"'):
            assert marker in ready, marker
    js = _read(JS / 'welcome.js')
    assert "guide.loadStage()" in js and "concat('arrival.choose')" in js and 'skipTo: choose' in js
    assert "start: step === 'hello' ? 0 : choose" in js and "guide.markSeen('origin')" in js
    assert "cue('cheer')" in js and "cue('fist-pump')" in js and 'plainScreens(step)' in js


def test_arrival_marks_welcome_done_and_origin_seen():
    from app import app

    with app.test_client() as client:
        handle = _register(client, 'arr')
        g = _guide_json(handle)
        assert g.get('origin') in (None, False) and not g.get('welcome_done')
        html = client.get('/welcome?step=level').data.decode()
        token = _csrf(html)
        # a refused step writes nothing
        before = _guide_json(handle)
        r = client.post('/welcome/step', data={'csrf_token': token, 'step': 'level', 'level': 'not_a_track'})
        assert r.status_code == 302 and _guide_json(handle) == before
        # (a bad CSRF token writes nothing too; scripts/test_welcome_smoke.py checks that with PB_TESTING off)
        # a choice in scene 6 records the story as seen
        client.post('/welcome/step', data={'csrf_token': token, 'step': 'level', 'level': 'gcse_maths'})
        g = _guide_json(handle)
        assert g['origin'] is True and not g.get('welcome_done')
        client.post('/welcome/step', data={'csrf_token': token, 'step': 'topic', 'topic': 'surprise'})
        g = _guide_json(handle)
        assert g['origin'] is True and g['welcome_done'] is True
        settings = client.get('/api/v1/me/settings').get_json()['settings']
        assert settings['guide']['origin'] is True
        # the old origin story will not autoplay: the page says the server holds origin = true
        home = client.get('/').data.decode()
        m = re.search(r'<script type="application/json" id="pb-guide-state"([^>]*)>(.*?)</script>', home, re.S)
        assert 'data-guide-persisted="1"' in m.group(1) and json.loads(m.group(2))['origin'] is True
    # Skip for now from the first screen: welcome done, origin seen, lands on Practice
    with app.test_client() as client:
        handle = _register(client, 'arrskip')
        token = _csrf(client.get('/welcome').data.decode())
        r = client.post('/welcome/step', data={'csrf_token': token, 'step': 'skip'})
        assert r.status_code == 302 and r.headers['Location'] == '/'
        g = _guide_json(handle)
        assert g['welcome_done'] is True and g['origin'] is True
    # the no-JS "Let's go" on the hello screen counts too
    with app.test_client() as client:
        handle = _register(client, 'arrhello')
        token = _csrf(client.get('/welcome').data.decode())
        client.post('/welcome/step', data={'csrf_token': token, 'step': 'hello'})
        assert _guide_json(handle)['origin'] is True


def test_replay_the_arrival():
    from app import app

    with app.test_client() as client:
        handle = _register(client, 'rep')
        token = _csrf(client.get('/welcome').data.decode())
        client.post('/welcome/step', data={'csrf_token': token, 'step': 'skip'})
        html = client.get('/profile/settings').data.decode()
        assert html.count('value="replay_arrival"') == 1 and 'id="guide-replay-arrival"' in html and '>Replay the arrival<' in html
        assert 'value="replay_guide_intro"' not in html and 'value="replay_welcome"' not in html
        r = client.post('/profile/settings', data={'csrf_token': _csrf(html), 'action': 'replay_arrival'})
        assert r.status_code == 302 and r.headers['Location'] == '/welcome'
        g = _guide_json(handle)
        assert g['welcome_done'] is False and g['origin'] is True
        page = client.get('/welcome')
        assert page.status_code == 200 and 'data-step="hello"' in page.data.decode(), 'the film plays again from scene 1'
        # the E6/E7 actions still work (a cached settings page)
        r = client.post('/profile/settings', data={'csrf_token': _csrf(html), 'action': 'replay_guide_intro'})
        assert r.status_code == 302 and _guide_json(handle)['origin'] is False
        r = client.post('/profile/settings', data={'csrf_token': _csrf(html), 'action': 'replay_welcome'})
        assert r.status_code == 302 and r.headers['Location'] == '/welcome'


def test_sound_on_for_new_accounts():
    from app import app

    with app.test_client() as client:
        _register(client, 'snd')
        s = client.get('/api/v1/me/settings').get_json()['settings']
        assert s['sound_enabled'] is True and s['zorp_sound'] == 'celebrations'
        html = client.get('/profile/settings').data.decode()
        assert 'On for new accounts; switch them off here' in html
        # Settings still switches both off
        data = {'csrf_token': _csrf(html), 'profile_visibility': 'followers_only', 'default_share_visibility': 'followers_only',
                'zorp_sound': 'off'}
        r = client.post('/profile/settings', data=data, follow_redirects=True)
        assert r.status_code == 200
        s = client.get('/api/v1/me/settings').get_json()['settings']
        assert s['sound_enabled'] is False and s['zorp_sound'] == 'off'


# ---------------------------------------------------------------------------------------------
# Runtime contracts (static): reduced and off, the API, the dialog, the fallback
# ---------------------------------------------------------------------------------------------

def test_reduced_and_off_paths():
    stage = _read(STAGE_JS)
    # full motion plays the beats; anything else shows the still frame (every prop and state, the end face)
    assert "function full() { return level() === 'full'; }" in stage
    assert 'if (!full()) {' in stage and 'still frame' in stage and 'face(full() ? sc.face : sc.end)' in stage
    assert "if (level() === 'reduced' && !(first && S.opts.resume)) anim(R.set, [{ opacity: 0 }, { opacity: 1 }]" in stage
    assert "if (level() === 'off') done();" in stage, 'off closes with no fade'
    assert "if (!job.opts.resume && level() !== 'off')" in stage, 'off opens with no fade'
    assert "if (b.wait) return full() ? wait(b.wait) : null;" in stage
    # lines: one at a time at full motion, all at once otherwise (fewer taps, no reveal)
    assert 'var from = still ? 0 : li;' in stage


def test_api_queue_and_dialog():
    stage = _read(STAGE_JS)
    for name in ('play: play', 'ready: ready', 'isOpen:', 'close:', 'cue:', 'zorp:', 'scenes: expand'):
        assert name in stage, name
    assert 'var queue = [];' in stage and 'queue.push(' in stage and 'if (S || !queue.length) return;' in stage, 'stages queue'
    assert "new CustomEvent('pb-stage-closed'" in stage
    for attr in ("'role', 'dialog'", "'aria-modal', 'true'", "'aria-labelledby', 'pb-stage-h'", "'aria-describedby', 'pb-stage-lines'",
                 "'aria-live', 'polite'"):
        assert attr in stage, attr
    assert "e.key === 'Escape'" in stage and "e.key !== 'Tab'" in stage, 'Esc and the focus trap'
    assert 's.back.focus' in stage and 'n.inert = true' in stage and 'n.inert = false' in stage, 'focus comes back; the page is inert'
    assert "r.next.type = r.skip.type = 'button'" in stage
    guide = _read(JS / 'guide.js')
    assert "document.addEventListener('pb-stage-closed'" in guide
    assert 'if (stageBusy()) return;' in guide, 'rewards wait for an open stage'
    assert "stage.play('arrival', { story: true })" in guide, 'the origin story is the film for an account that never saw it'
    assert "startQueue(steps, 'origin')" in guide, 'the dialogue-box origin stays as the fallback'
    assert 'markSeen: markSeen' in guide and 'loadStage: loadStage' in guide
    assert 'innerHTML' not in guide


def test_preview_route():
    from app import app

    with app.test_client() as client:
        html = client.get('/guide-preview').data.decode()
    assert 'id="guide-preview-stage"' in html and 'data-stage-demo' in html and "guide-preview.js?v=10" in html
    ids = [s['id'] for s in catalog()['scenes']]
    for sid in ids:
        assert f'data-stage-play="{sid}"' in html, sid
    assert 'data-stage-play="arrival"' in html and 'data-stage-play="story"' in html
    js = _read(JS / 'guide-preview.js')
    assert ".get('stage')" in js and '/^[a-z.]{1,40}$/' in js


TESTS = (
    test_files_and_caps,
    test_css_animates_transform_and_opacity_only,
    test_props_template_is_inert,
    test_catalog_shape_and_beats,
    test_every_scene_starts_and_ends_positive_or_neutral,
    test_voice_rules_on_every_line,
    test_lazy_loading,
    test_welcome_page_hands_its_forms_to_scene_6,
    test_arrival_marks_welcome_done_and_origin_seen,
    test_replay_the_arrival,
    test_sound_on_for_new_accounts,
    test_reduced_and_off_paths,
    test_api_queue_and_dialog,
    test_preview_route,
)


def main():
    for fn in TESTS:
        fn()
        print(f'  ok {fn.__name__}')
    print('Zorp stage smoke (E10 phases 1 and 2) passed.')


if __name__ == '__main__':
    main()
