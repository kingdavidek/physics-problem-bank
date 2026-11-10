"""E10 phase 3: the coach, the guided first question (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A2, section 10, 11.6).

Run: python scripts/test_zorp_coach_smoke.py

* Files and caps: static/js/zorp-coach.js and static/css/coach.css are new, on demand, with their own byte caps; no library, no
  CDN, no innerHTML, no inline handlers; the CSS has no animation of its own and no fixed position (nothing can cover the page).
* The catalog (the steps in zorp-coach.js): shape, faces from models/zorp_rig.py CONTEXT_MAP['coach'] (positive or neutral),
  clips from the positive autoplay list, the wrong-answer order names real steps, the voice rules on every line and label.
* site.js dispatches the four events the coach waits for; every event the coach listens to is dispatched somewhere.
* Lazy loading: no page carries a <script> or <link> for the coach; the island is on pages that have the guide; not precached.
* Which page is coached: only the question that Start on /welcome asks for (the hidden coach field), and only when a question
  was made; the Practice tour cannot open on that page while the coach loads or runs; both are marked seen when it ends.
The browser walk (Playwright, phone and desktop, light, dark and reduced motion) is in the plan's Progress section 11.6.
"""
import json
import os
import re
import sys
import uuid
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS = ROOT / 'static' / 'js'
CSS = ROOT / 'static' / 'css'
COACH_JS = JS / 'zorp-coach.js'
COACH_CSS = CSS / 'coach.css'

# Own caps for the on-demand files (2026-11-08, E10 phase 3).
COACH_JS_MAX_BYTES = 14_000
COACH_CSS_MAX_BYTES = 3_000

EVENTS = ('pb-answer-checked', 'pb-answer-unlocked', 'pb-hint-shown', 'pb-hint-bigger')
STEP_IDS = ('answer', 'pick', 'hint', 'bigger', 'reveal', 'note', 'close')


def _read(path):
    return Path(path).read_text(encoding='utf-8')


def _csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html) or re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def _register(client, tag='co'):
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
    return json.loads(row[0]) if row and row[0] else {}


def _steps():
    """The step objects of zorp-coach.js, read by a small scan (id, lines, face, clip, per step)."""
    src = _read(COACH_JS)
    block = src[src.index('steps: ['):]
    out = []
    for m in re.finditer(r"\{\s*id: '(\w+)',\s*lines: \[((?:'(?:[^'\\]|\\.)*',?\s*)+)\],\s*face: '([\w-]+)',\s*clip: '([\w-]+)',\s*\}", block):
        lines = re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(2))
        out.append({'id': m.group(1), 'lines': lines, 'face': m.group(3), 'clip': m.group(4)})
    return out


# ---------------------------------------------------------------------------------------------

def test_files_and_caps():
    js, css = _read(COACH_JS), _read(COACH_CSS)
    assert len(js.encode('utf-8')) <= COACH_JS_MAX_BYTES, len(js.encode('utf-8'))
    assert len(css.encode('utf-8')) <= COACH_CSS_MAX_BYTES, len(css.encode('utf-8'))
    for name, text in (('zorp-coach.js', js), ('coach.css', css)):
        assert not re.search(r'https?://|cdn|jquery|lottie|gsap|import\s*\(', text, re.I), f'{name}: no library or CDN'
    assert 'innerHTML' not in js and 'insertAdjacentHTML' not in js and 'eval(' not in js, 'nodes and textContent only'
    assert not re.search(r'\son\w+\s*=', js), 'no inline handlers'
    assert '@keyframes' not in css and 'transition' not in css and 'animation' not in css, 'the coach animates in script (opacity, transform)'
    assert 'position: fixed' not in css and 'z-index' not in css and 'backdrop' not in css, 'in the page flow: no backdrop, nothing fixed'
    assert not re.search(r'#[0-9a-fA-F]{3,8}\b', css), 'colours come from tokens, so light and dark follow the page'
    # animation in script is limited to opacity and transform
    for m in re.finditer(r'animate\((.*?)\{ duration', js, re.S):
        props = set(re.findall(r'(\w+):', m.group(1)))
        assert props <= {'opacity', 'transform'}, props
    assert 'z.play(step.clip' in js and "level() === 'full'" in js, 'limbs (clips) only at full motion'
    assert "'off'" in js, 'motion off shows the callout with no fade'


def test_catalog_shape_faces_and_clips():
    from models import zorp_rig as rig

    steps = _steps()
    assert [s['id'] for s in steps] == list(STEP_IDS), [s['id'] for s in steps]
    allowed = set(rig.CONTEXT_MAP['coach'])
    for s in steps:
        assert len(s['lines']) == 1, s
        assert s['face'] in allowed and rig.VALENCE[s['face']] != rig.NEGATIVE, s
        assert s['clip'] in rig.AUTOPLAY_CLIPS, s
    src = _read(COACH_JS)
    order = re.search(r"wrong: \[((?:'\w+',?\s*)+)\]", src)
    assert order, 'the wrong-answer order'
    ids = re.findall(r"'(\w+)'", order.group(1))
    assert ids == ['hint', 'bigger', 'reveal', 'note', 'close'], ids
    assert set(ids) <= set(STEP_IDS)
    # plan A2 step 3's targets are on the pages the coach points at
    index = _read(ROOT / 'templates' / 'index.html') + _read(ROOT / 'templates' / 'partials' / 'free_response_inline.html')
    for sel in ('free-response-hint', 'hint-card', 'free-response-hint-more', 'answer-reveal', 'mcq-options', 'mcq-hint-slot', 'free-response-row'):
        assert sel in index, sel
    assert 'wrong-answer-reflection-toggle' in _read(JS / 'site.js')


def test_voice_rules_on_every_line():
    from models import zorp_voice as voice

    items, errors = voice.extract_coach_catalog()
    assert not errors, errors
    lines = [i for i in items if i.kind == 'line']
    assert [i.text for i in lines] == [s['lines'][0] for s in _steps()], 'the lint reads the same lines the runtime shows'
    labels = {i.text for i in items if i.kind == 'label'}
    assert labels == {'Got it', 'Skip for now'}, labels
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
    text = ' '.join(i.text for i in lines)
    assert not re.search(r'[\U0001F300-\U0001FAFF☀-➿]', text), 'no emoji'
    assert 'That’s the loop: try, hint, try again.' in text and 'Pick an answer.' in text
    # the plan's draft lines, as the owner approved them in A2
    assert 'I only show them after you try' in text and 'This shows the first step' in text and 'whenever you want it' in text


def test_site_js_dispatches_the_events():
    site = _read(JS / 'site.js')
    coach = _read(COACH_JS)
    for ev in EVENTS:
        assert f"'{ev}'" in site, f'site.js must dispatch {ev}'
        assert f"'{ev}'" in coach, f'the coach must wait for {ev}'
    assert site.count("pbEv('pb-answer-checked', { correct: !!ok })") == 1
    # one place for every typed and multiple choice check: celebrateResult
    m = re.search(r'function celebrateResult\(ok, target, revealTarget\) \{(.*?)\n  \}', site, re.S)
    assert m and 'pb-answer-checked' in m.group(1), 'pb-answer-checked comes from celebrateResult'
    m = re.search(r'function unlockAnswer\(\) \{(.*?)\n  \}', site, re.S)
    assert m and 'pb-answer-unlocked' in m.group(1) and m.group(1).index("removeAttribute('data-locked')") < m.group(1).index('pb-answer-unlocked')
    m = re.search(r'function onHintMore\(event\) \{(.*?)\n  \}', site, re.S)
    assert m and 'pb-hint-bigger' in m.group(1)
    m = re.search(r'function showHintLadder\(block, data\) \{(.*?)\n  \}', site, re.S)
    assert m and 'pb-hint-shown' in m.group(1)
    assert "pbEv('pb-hint-shown');" in site.split('function fetchOptionNote')[1].split('function showMcqRetry')[0], 'MCQ option note'
    # the coach never reaches into the page's own state beyond reading it and listening
    for forbidden in ('.focus(', 'dataset.hintRung =', 'localStorage', 'sessionStorage', 'fetch('):
        assert forbidden not in coach, f'the coach must not use {forbidden}'
    assert 'aria-live' in coach and "'polite'" in coach and 'Escape' in coach and 'pagehide' in coach


def test_lazy_loading_and_island():
    from app import app

    base = _read(ROOT / 'templates' / 'base.html')
    for name in ('zorp-coach', 'coach.css'):
        assert name not in base, f'base.html must not mention {name}'
    partial = _read(ROOT / 'templates' / 'partials' / 'guide.html')
    assert partial.count('id="pb-coach-assets"') == 1
    sw = _read(JS / 'sw.js')
    for name in ('zorp-coach', 'coach.css'):
        assert name not in sw, f'{name} is not precached'
    guide = _read(JS / 'guide.js')
    assert "getElementById('pb-coach-assets')" in guide and "addAsset('script', { src: a.js })" in guide

    def assert_lazy(html, where):
        assert not re.search(r'<script[^>]+src="[^"]*zorp-coach\.js', html), where
        assert not re.search(r'<link[^>]+href="[^"]*/coach\.css', html), where

    with app.test_client() as guest:
        html = guest.get('/').data.decode()
        assert_lazy(html, 'guest /')
        assert 'data-guide-coach' not in html
    with app.test_client() as client:
        _register(client)
        for path in ('/', '/profile', '/welcome', '/topics'):
            r = client.get(path)
            assert r.status_code == 200, path
            html = r.data.decode()
            assert_lazy(html, path)
            assert 'data-guide-coach' not in html, path
            m = re.search(r'<script type="application/json" id="pb-coach-assets">(.*?)</script>', html, re.S)
            assert m, path
            assets = json.loads(m.group(1))
            assert set(assets) == {'js', 'css'} and all('?v=' in v for v in assets.values()), assets
        for url in ('/static/js/zorp-coach.js', '/static/css/coach.css'):
            assert client.get(url).status_code == 200, url


def _ready_form_fields(html):
    form = re.search(r'<form[^>]*id="welcome-ready-form".*?</form>', html, re.S).group(0)
    return dict(re.findall(r'<input type="hidden" name="(\w+)" value="([^"]*)"', form))


def test_only_the_arrivals_first_question_is_coached():
    from app import app

    tpl = _read(ROOT / 'templates' / 'welcome.html')
    assert '<input type="hidden" name="coach" value="1">' in tpl
    with app.test_client() as client:
        _register(client)
        client.post('/welcome/step', data={'csrf_token': _csrf(client.get('/welcome').data.decode()), 'step': 'level', 'level': 'gcse_maths'})
        topic = client.get('/welcome?step=topic').data.decode()
        slug = re.search(r'name="topic" value="([a-z0-9_]+)" class="welcome-card"', topic).group(1)
        client.post('/welcome/step', data={'csrf_token': _csrf(topic), 'step': 'topic', 'topic': slug})
        ready = client.get('/welcome?step=ready').data.decode()
        fields = _ready_form_fields(ready)
        assert fields.get('coach') == '1' and fields.get('action') == 'start', fields
        # Start: the question comes with the coach flag
        r = client.post('/', data=fields)
        html = r.data.decode()
        assert r.status_code == 200 and 'data-guide-coach="1"' in html
        assert 'free-response-inline' in html or 'id="mcq-options"' in html, 'a question was made'
        assert re.search(r'<body[^>]*data-guide-endpoint="index"[^>]*data-guide-coach="1"', html)
        # a question from the picker, the new-question button or a reload of the page is not coached
        plain = {k: v for k, v in fields.items() if k != 'coach'}
        assert 'data-guide-coach' not in client.post('/', data=plain).data.decode()
        assert 'data-guide-coach' not in client.get('/').data.decode()
        # no question made (the form is refused without its token), no coach
    app_src = _read(ROOT / 'app.py')
    assert "coach_first=bool(problem and not error and request.method == 'POST' and request.form.get('coach') == '1')" in app_src


def test_guide_js_keeps_the_practice_tour_away_and_marks_both_seen():
    guide = _read(JS / 'guide.js')
    m = re.search(r'function maybePlayTour\(\) \{(.*?)\n  \}', guide, re.S)
    assert m
    body = m.group(1)
    # the coach is decided before any tour is chosen, and while it loads or runs no tour opens
    assert body.index("coachState === 'loading'") < body.index('coachDue()') < body.index('tourFor(endpoint)')
    assert "coachState === 'active'" in body and 'startCoach();' in body
    due = re.search(r'function coachDue\(\) \{(.*?)\n  \}', guide, re.S).group(1)
    assert "data-guide-coach') === '1'" in due and "!seen('coach')" in due and '!coachState' in due and 'coachAssets()' in due
    ended = guide.split("addEventListener('pb-coach-ended'")[1].split('});')[0]
    assert "markTourSeen('coach')" in ended and "markTourSeen('practice')" in ended and 'flushPersist()' in ended
    # no question to coach: fall back to the normal tour
    start = re.search(r'function startCoach\(\) \{(.*?)\n  \}', guide, re.S).group(1)
    assert 'pbCoach.start()' in start and 'maybePlayTour()' in start and 'skipTourThisLoad = false' in start
    # the coach ends in every way the pupil can leave: done, skip (link, Esc), leave (pagehide), and says so once
    coach = _read(COACH_JS)
    for how in ("'done'", "'skip'", "'leave'"):
        assert f'finish({how})' in coach, how
    assert coach.count("new CustomEvent('pb-coach-ended'") == 1
    # a stage or reward overlay open: the coach waits (never two things at once)
    assert "getElementById('guide-root')" in coach and 'pbStage.isOpen' in coach and 'blocked()' in coach


def test_seen_state_is_the_existing_guide_state():
    from app import app

    with app.test_client() as client:
        handle = _register(client)
        token = _csrf(client.get('/profile').data.decode())
        # the keys the coach writes are ordinary tour flags: accepted, stored, returned (guide.js PATCHes /api/v1/me/settings)
        r = client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'origin': True, 'tours': {'coach': True, 'practice': True}, 'rewards': {}}},
                         headers={'X-CSRF-Token': token})
        assert r.status_code == 200, (r.status_code, r.data[:200])
        state = _guide_json(handle)
        assert state['tours'].get('coach') is True and state['tours'].get('practice') is True, state
        # a later patch for another flag keeps them (the guide state merges)
        r = client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'origin': True, 'tours': {'profile': True}, 'rewards': {}}},
                         headers={'X-CSRF-Token': token})
        assert r.status_code == 200
        assert _guide_json(handle)['tours'].get('coach') is True


TESTS = (
    test_files_and_caps,
    test_catalog_shape_faces_and_clips,
    test_voice_rules_on_every_line,
    test_site_js_dispatches_the_events,
    test_lazy_loading_and_island,
    test_only_the_arrivals_first_question_is_coached,
    test_guide_js_keeps_the_practice_tour_away_and_marks_both_seen,
    test_seen_state_is_the_existing_guide_state,
)


def main():
    for fn in TESTS:
        fn()
        print(f'  ok {fn.__name__}')
    print('Zorp coach smoke (E10 phase 3) passed.')


if __name__ == '__main__':
    main()
