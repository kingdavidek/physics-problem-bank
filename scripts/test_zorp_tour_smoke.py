"""E10 phase 6: the app tour and the just-in-time spotlights (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A3, A4, section 10, 11.9).

Run: python scripts/test_zorp_tour_smoke.py

* Files and caps: static/js/zorp-tour.js and static/css/tour.css are new, on demand, with their own byte caps; no library, no CDN,
  no innerHTML, no inline handlers; script animation is opacity and transform only.
* The catalog: about fourteen stops of one to three steps, in the plan's order, faces from CONTEXT_MAP['tour'], clips from the
  autoplay list, the page maps match the Flask endpoints, the voice rules on every line and label.
* Lazy loading: no page carries the tour's files; the island is on pages with the guide (inClass says if there is a Classes stop).
* guide.js wiring: the tour starts on pb-coach-ended, is offered once to accounts that predate it, suppresses the per-tab tours
  once taken, and is replayable from Settings (which sets run and clears tours.app).
* The badge: Pathfinder, family tour, distinct from topics_10 "Broad explorer"; awarded once, only after the tour was taken.
* Spotlights: nine, each with a seen flag in the protected tours region.
The browser walk (Playwright, desktop and phone, light, dark and reduced motion) is in the plan's Progress section 11.9.
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
TOUR_JS = JS / 'zorp-tour.js'
TOUR_CSS = CSS / 'tour.css'

# Own caps for the on-demand files (2026-11-08, E10 phase 6).
TOUR_JS_MAX_BYTES = 35_200  # 2026-11-10: +600 for the lesson-quiz spotlight fix (waits for the end-of-lesson quiz bar; closes if its target goes); 2026-11-10 E11 Phase 0: +600, a spotlight steps aside while a stage or dialog is on screen (measured 34,858 B)
TOUR_CSS_MAX_BYTES = 2_800

STOP_ORDER = ['picker', 'hints', 'save', 'quicktest', 'learn', 'lessonquiz', 'today', 'week', 'friends', 'challenges',
              'streak', 'progress', 'history', 'classes', 'settings', 'replay']
PAGE_ORDER = ['practice', 'learn', 'daily', 'compete', 'profile', 'classes', 'settings']
SPOT_IDS = ('hint', 'bigger', 'lessonquiz', 'quicktest', 'aiexplain', 'setwork', 'challenge', 'revision', 'saved')


def _read(path):
    return Path(path).read_text(encoding='utf-8')


def _csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html) or re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def _register(client, tag='tr'):
    handle = f'{tag}_{uuid.uuid4().hex[:8]}'
    r = client.get('/register')
    r = client.post('/register', data={
        'csrf_token': _csrf(r.data.decode()), 'email': f'{handle}@example.com', 'handle': handle,
        'password': 'password123', 'confirm_password': 'password123', 'age_confirm': '1',
    })
    assert r.status_code == 302, r.status_code
    return handle


def _guide_json(handle):
    from app import get_db

    with get_db() as conn:
        row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = (SELECT id FROM users WHERE handle = ?)',
                           (handle,)).fetchone()
    return json.loads(row[0]) if row and row[0] else {}


def _user_id(handle):
    from app import get_db

    with get_db() as conn:
        return conn.execute('SELECT id FROM users WHERE handle = ?', (handle,)).fetchone()[0]


def _steps():
    src = _read(TOUR_JS)
    block = src[src.index('var STEPS = ['):src.index('var END = {')]
    out = []
    for chunk in re.split(r'\n    \{\n', block)[1:]:
        def one(key):
            m = re.search(rf"\b{key}: '((?:[^'\\]|\\.)*)'", chunk)
            return m.group(1) if m else None
        lines = re.findall(r"'((?:[^'\\]|\\.)*)'", re.search(r'lines: \[(.*?)\]', chunk, re.S).group(1))
        out.append({'id': one('id'), 'stop': one('stop'), 'page': one('page'), 'heading': one('heading'), 'face': one('face'),
                    'clip': one('clip'), 'class_only': 'classOnly' in chunk, 'lines': lines, 'target': one('target')})
    return out


def _spots():
    src = _read(TOUR_JS)
    block = src[src.index('var SPOTS = {'):src.index('// END COPY')]
    out = {}
    for m in re.finditer(r"\n    (\w+): \{\n      id: '([\w.]+)',\n      lines: \[(.*?)\],\n      face: '([\w-]+)',\n      clip: '([\w-]+)',", block, re.S):
        out[m.group(1)] = {'id': m.group(2), 'lines': re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(3)), 'face': m.group(4), 'clip': m.group(5)}
    return out


def test_files_and_caps():
    js, css = _read(TOUR_JS), _read(TOUR_CSS)
    assert len(js.encode('utf-8')) <= TOUR_JS_MAX_BYTES, len(js.encode('utf-8'))
    assert len(css.encode('utf-8')) <= TOUR_CSS_MAX_BYTES, len(css.encode('utf-8'))
    for name, text in (('zorp-tour.js', js), ('tour.css', css)):
        assert not re.search(r'https?://|cdn|jquery|lottie|gsap|import\s*\(', text, re.I), f'{name}: no library or CDN'
    assert 'innerHTML' not in js and 'insertAdjacentHTML' not in js and 'eval(' not in js, 'nodes and textContent only'
    assert not re.search(r'\son\w+\s*=', js), 'no inline handlers'
    assert '@keyframes' not in css and 'transition' not in css, 'the tour animates in script (opacity, transform)'
    assert not re.search(r'#[0-9a-fA-F]{3,8}\b', css), 'colours come from tokens, so light and dark follow the page'
    for m in re.finditer(r'animate\((.*?)\{ duration', js, re.S):
        props = set(re.findall(r'(\w+):', m.group(1)))
        assert props <= {'opacity', 'transform', 'offset'}, props
    assert 'Escape' in js and "'polite'" in js and 'aria-live' in js, 'Esc skips; announcements are polite'
    assert 'pb-tour-on' in css and 'pb-tour-target' in css


def test_catalog_shape_faces_and_clips():
    from models import zorp_rig as rig

    steps = _steps()
    assert len(steps) == 19, len(steps)
    stops = []
    for s in steps:
        if s['stop'] not in stops:
            stops.append(s['stop'])
    assert stops == STOP_ORDER, stops
    pages = []
    for s in steps:
        if s['page'] not in pages:
            pages.append(s['page'])
    assert pages == PAGE_ORDER, pages
    for s in steps:
        assert 1 <= len(s['lines']) <= 2 and s['id'].startswith(s['page'] + '.'), s
        assert s['face'] in rig.CONTEXT_MAP['tour'] and rig.VALENCE[s['face']] != rig.NEGATIVE, s
        assert s['clip'] in rig.AUTOPLAY_CLIPS, s
        assert s['target'], s
    assert [s['page'] for s in steps if s['class_only']] == ['classes']
    assert rig.CONTEXT_MAP['tour'] == rig.CONTEXT_MAP['guide']
    spots = _spots()
    assert tuple(spots) == SPOT_IDS, list(spots)
    for key, sp in spots.items():
        assert sp['id'] == 'sp.' + key and 1 <= len(sp['lines']) <= 2
        assert sp['face'] in rig.CONTEXT_MAP['tour'] and rig.VALENCE[sp['face']] != rig.NEGATIVE, sp
        assert sp['clip'] in rig.AUTOPLAY_CLIPS, sp
    src = _read(TOUR_JS)
    assert "clip: 'bow'" not in src and "play: 'bow'" in src and "end: 'proud'" in src


def test_page_maps_match_flask():
    from app import app

    src = _read(TOUR_JS)
    page_of = dict(re.findall(r"(\w+): '(\w+)'", re.search(r'var PAGE_OF = \{(.*?)\};', src).group(1)))
    url_of = dict(re.findall(r"(\w+): '(/[^']*)'", re.search(r'var URL_OF = \{(.*?)\};', src).group(1)))
    assert list(page_of.values()) == PAGE_ORDER and list(url_of) == PAGE_ORDER
    with app.test_request_context():
        from flask import url_for
        for endpoint, page in page_of.items():
            assert url_for(endpoint) == url_of[page], (endpoint, url_of[page])
    rules = {r.endpoint for r in app.url_map.iter_rules()}
    guide = _read(JS / 'guide.js')
    spot_page = re.search(r"var SPOT_PAGE = \{(.*?)\n  \};", guide, re.S).group(1)
    names = re.findall(r'(\w+): \[', spot_page)
    assert len(names) >= 9, names
    for name in names:
        assert name in rules, name


def test_voice_rules_on_every_line():
    from models import zorp_voice as voice

    items, errors = voice.extract_tour_catalog()
    assert not errors, errors
    lines = [i for i in items if i.kind == 'line']
    expected = [t for s in _steps() for t in s['lines']] + [t for sp in _spots().values() for t in sp['lines']]
    got = [i.text for i in lines]
    for text in expected:
        assert text in got, text
    labels = {i.text for i in items if i.kind == 'label'}
    assert {'Next', 'Skip tour', 'Continue'} <= labels, labels
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
    text = ' '.join(expected)
    assert not re.search(r'[\U0001F300-\U0001FAFF☀-➿]', text), 'no emoji'
    assert text.count('!') <= 1
    # the offer line and its labels are in the guide catalog
    cat = _read(JS / 'guide-catalog.js')
    assert "appoffer" in cat and "'Show me around'" in cat and "'Not now'" in cat


def test_lazy_loading_and_island():
    from app import app

    base = _read(ROOT / 'templates' / 'base.html')
    for name in ('zorp-tour', 'tour.css'):
        assert name not in base, f'base.html must not mention {name}'
    sw = _read(JS / 'sw.js')
    for name in ('zorp-tour', 'tour.css'):
        assert name not in sw, f'{name} is not precached'
    partial = _read(ROOT / 'templates' / 'partials' / 'guide.html')
    assert partial.count('id="pb-tour-assets"') == 1
    guide = _read(JS / 'guide.js')
    assert "getElementById('pb-tour-assets')" in guide

    def assert_lazy(html, where):
        assert not re.search(r'<script[^>]+src="[^"]*zorp-tour\.js', html), where
        assert not re.search(r'<link[^>]+href="[^"]*/tour\.css', html), where

    with app.test_client() as client:
        _register(client)
        for path in ('/', '/profile', '/topics'):
            html = client.get(path).data.decode()
            assert_lazy(html, path)
            m = re.search(r'<script type="application/json" id="pb-tour-assets">(.*?)</script>', html, re.S)
            assert m, path
            assets = json.loads(m.group(1))
            assert set(assets) == {'js', 'css', 'inClass'} and '?v=' in assets['js'] and '?v=' in assets['css'], assets
            assert assets['inClass'] is False
        for url in ('/static/js/zorp-tour.js', '/static/css/tour.css'):
            assert client.get(url).status_code == 200, url


def test_in_class_pupil_gets_the_classes_stop():
    from app import app, get_db
    from models.classes import create_class, enable_teacher, join_class

    with app.test_client() as teacher_client:
        teacher = _register(teacher_client, 'tt')
    with get_db() as conn:
        tid = _user_id(teacher)
        enable_teacher(conn, tid)
        code = create_class(conn, tid, 'Tour class', 'gcse', 'maths')['join_code']
        conn.commit()
    with app.test_client() as pupil_client:
        pupil = _register(pupil_client, 'tp')
        with get_db() as conn:
            join_class(conn, _user_id(pupil), code, disclosed=True)
            conn.commit()
        html = pupil_client.get('/').data.decode()
        assets = json.loads(re.search(r'id="pb-tour-assets">(.*?)</script>', html, re.S).group(1))
        assert assets['inClass'] is True, assets


def test_guide_js_wiring():
    guide = _read(JS / 'guide.js')
    m = re.search(r"addEventListener\('pb-coach-ended', function \(e\) \{(.*?)\n  \}\);", guide, re.S)
    assert m, 'pb-coach-ended handler'
    body = m.group(1)
    assert "how !== 'leave'" in body and "!seen('app')" in body and 'beginAppTour(true)' in body
    assert "seen('appoffer')" in guide and "seen('origin')" in guide, 'accounts that predate the tour get one offer'
    assert "seen('app') ? ''" in guide, 'once taken, the per-tab tours stay quiet'
    assert 'pb-tour-on' in guide and 'keepalive' in guide
    cat = _read(JS / 'guide-catalog.js')
    assert "appoffer" in cat


def test_replay_from_settings():
    from app import app

    with app.test_client() as client:
        handle = _register(client)
        token = _csrf(client.get('/profile/settings').data.decode())
        html = client.get('/profile/settings').data.decode()
        assert 'id="guide-replay-tour"' in html and 'Replay the tour' in html and 'Replay the arrival' in html
        r = client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'origin': True, 'tours': {'app': True, 'practice': True}, 'rewards': {}}},
                         headers={'X-CSRF-Token': token})
        assert r.status_code == 200, r.data[:200]
        r = client.post('/profile/settings', data={'csrf_token': token, 'action': 'replay_tour'})
        assert r.status_code == 302 and r.headers['Location'].rstrip('/').endswith(('', '/')) and r.headers['Location'] in ('/', 'http://localhost/'), r.headers['Location']
        state = _guide_json(handle)
        assert state['tours'].get('app') is False and state['run'] == {'id': 'app', 'step': 0}, state
        assert state['tours'].get('practice') is True, 'other flags are kept'


def test_the_badge():
    from app import app
    from models import gamification as g

    meta = g.MILESTONE_CATALOG[g.MILESTONE_TOUR]
    other = g.MILESTONE_CATALOG[g.MILESTONE_TOPICS_10]
    assert meta['title'] == 'Pathfinder' and meta['family'] == 'tour' and 'tour' in g.BADGE_FAMILIES
    assert meta['title'] != other['title'] and meta['family'] != other['family'], 'distinct from Broad explorer / explorer'
    assert 'Take Zorp' in meta['how'] and len(meta['blurb']) <= 80 and len(meta['how']) <= 80
    badge = _read(JS / 'badge-stage.js')
    assert "tour:" in badge and 'bp-sign' in badge
    assert 'id="bp-sign"' in _read(ROOT / 'static' / 'images' / 'badge-props.svg')

    with app.test_client() as client:
        handle = _register(client)
        token = _csrf(client.get('/profile').data.decode())
        hdr = {'X-CSRF-Token': token}
        r = client.post('/api/v1/me/tour/complete', json={}, headers=hdr)
        assert r.status_code == 200 and r.get_json() == {'ok': True, 'awarded': False}, r.get_json()
        # 2026-11-08 (E10 review fix 8): "Not now" sets tours.app; that alone must never earn the badge
        r = client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'origin': True, 'tours': {'app': True}, 'rewards': {}}}, headers=hdr)
        assert r.status_code == 200
        r = client.post('/api/v1/me/tour/complete', json={}, headers=hdr)
        assert r.get_json() == {'ok': True, 'awarded': False}, 'declining the tour earns nothing'
        # the end cannot be claimed from an early step, or by a pupil whose tour is not running
        r = client.post('/api/v1/me/tour/reached-end', json={}, headers=hdr)
        assert r.get_json() == {'ok': True, 'recorded': False}
        client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'run': {'id': 'app', 'step': 3}}}, headers=hdr)
        r = client.post('/api/v1/me/tour/reached-end', json={}, headers=hdr)
        assert r.get_json()['recorded'] is False, 'step 3 is not the end'
        assert client.post('/api/v1/me/tour/complete', json={}, headers=hdr).get_json()['awarded'] is False
        assert 'tour_finished' not in json.dumps(_guide_json(handle)), 'nothing recorded yet'
        # the marker cannot be written through the guide PATCH either
        client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'tour_finished': True}}, headers=hdr)
        assert client.post('/api/v1/me/tour/complete', json={}, headers=hdr).get_json()['awarded'] is False
        # the last page of the tour: the client saves the run, then says so; the server records it, and only then the badge comes
        client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'run': {'id': 'app', 'step': 18}}}, headers=hdr)
        r = client.post('/api/v1/me/tour/reached-end', json={}, headers=hdr)
        assert r.get_json() == {'ok': True, 'recorded': True}, r.get_json()
        r = client.post('/api/v1/me/tour/complete', json={}, headers=hdr)
        data = r.get_json()
        assert data['awarded'] is True, data
        assert any(k.get('key') == g.MILESTONE_TOUR or k == g.MILESTONE_TOUR for k in (data.get('new_milestones') or [])), data
        r = client.post('/api/v1/me/tour/complete', json={}, headers=hdr)
        assert r.get_json()['awarded'] is False, 'once'
        # a replay must reach the end again: starting the tour clears the marker
        from app import get_db
        from models import social as social_models
        with get_db() as conn:
            uid = conn.execute('SELECT id FROM users WHERE handle = ?', (handle,)).fetchone()[0]
            assert social_models.guide_tour_finished(conn, uid) is True
            social_models.start_app_tour(conn, uid)
            assert social_models.guide_tour_finished(conn, uid) is False
        assert 'tour_finished' not in json.dumps(_guide_json(handle))
    src = _read(TOUR_JS)
    assert "/api/v1/me/tour/reached-end" in src and src.index('tellEnd()') < src.index("'/api/v1/me/tour/complete'")
    assert 'told.then(go, go)' in src, 'the run is cleared (end) only after the server has the end recorded'
    anon = app.test_client()
    assert anon.post('/api/v1/me/tour/complete', json={}).status_code in (302, 401, 403)


def test_spotlight_flags_are_protected_seen_state():
    from app import app
    from models import social

    for key in SPOT_IDS:
        assert f"sp_{key}" in _read(TOUR_JS) or "'sp_' +" in _read(TOUR_JS)
    assert "'sp_'" in _read(TOUR_JS) or '"sp_' in _read(TOUR_JS) or 'sp_' in _read(TOUR_JS)
    with app.test_client() as client:
        handle = _register(client)
        token = _csrf(client.get('/profile').data.decode())
        tours = {'app': True, 'coach': True}
        tours.update({f'sp_{k}': True for k in SPOT_IDS})
        r = client.patch('/api/v1/me/settings', json={'guide': {'v': 1, 'origin': True, 'tours': tours, 'rewards': {}}}, headers={'X-CSRF-Token': token})
        assert r.status_code == 200, r.data[:200]
        got = _guide_json(handle)['tours']
        assert all(got.get(f'sp_{k}') is True for k in SPOT_IDS) and got.get('app') and got.get('coach'), got
    guide = _read(JS / 'guide.js')
    for ev in ('pb-hint-shown', 'pb-hint-bigger'):
        assert ev in guide
    assert 'coachOn' in guide or 'coach' in guide


TESTS = (
    test_files_and_caps,
    test_catalog_shape_faces_and_clips,
    test_page_maps_match_flask,
    test_voice_rules_on_every_line,
    test_lazy_loading_and_island,
    test_in_class_pupil_gets_the_classes_stop,
    test_guide_js_wiring,
    test_replay_from_settings,
    test_the_badge,
    test_spotlight_flags_are_protected_seen_state,
)


def main():
    for fn in TESTS:
        fn()
        print(f'  ok {fn.__name__}')
    print('Zorp tour smoke (E10 phase 6) passed.')


if __name__ == '__main__':
    main()
