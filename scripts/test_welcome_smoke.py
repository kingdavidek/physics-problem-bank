"""E7 Phase 3 — mobile welcome flow smoke.

Run: python scripts/test_welcome_smoke.py

Covers docs/MASCOT_MOTION_AND_ONBOARDING.md §3.4 / Phase 3: the `/welcome`
route, `welcome.html` / `welcome.js`, the `guide_json` welcome keys, the
register() redirect, the profile_settings() Replay welcome branch, and the
nested-<form> fix in profile_settings.html.
"""
import os
import random
import re
import string
import sys
import tempfile
import uuid
from pathlib import Path

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('SECRET_KEY', 'pb-testing')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db, GENERATOR_LAUNCH_PATHS  # noqa: E402
from models.account_deletion import delete_user_account, remaining_user_rows  # noqa: E402
from models.user import User  # noqa: E402
import topic_registry as tr  # noqa: E402

WELCOME_HTML = ROOT / 'templates' / 'welcome.html'
WELCOME_JS = ROOT / 'static' / 'js' / 'welcome.js'
SW_JS = ROOT / 'static' / 'js' / 'sw.js'
ZORP_MOTION_JS = ROOT / 'static' / 'js' / 'zorp-motion.js'
GUIDE_JS = ROOT / 'static' / 'js' / 'guide.js'
PROFILE_SETTINGS_HTML = ROOT / 'templates' / 'profile_settings.html'
PWA_SMOKE = ROOT / 'scripts' / 'test_pwa_smoke.py'

BANNED_STRINGS = ('lottie', 'jsdelivr', 'unpkg', 'innerhtml')
BANNED_NUDGE_RE = re.compile(
    r"friends are|behind|hurry|don['’]t lose|everyone else", re.IGNORECASE
)


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def logout(client):
    html = client.get('/').data.decode()
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        client.post('/logout', data={'csrf_token': m.group(1)})


def register(client, email, handle):
    logout(client)
    r = client.get('/register')
    assert r.status_code == 200
    token = csrf_from(r.data.decode())
    r = client.post(
        '/register',
        data={
            'csrf_token': token,
            'email': email,
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
    )
    return r


def guide_json_for(handle):
    with get_db() as conn:
        row = conn.execute(
            '''
            SELECT guide_json FROM user_profile_settings
            WHERE user_id = (SELECT id FROM users WHERE handle = ?)
            ''',
            (handle,),
        ).fetchone()
        return row['guide_json'] if row else None


def form_tag_max_depth(html: str) -> int:
    depth = 0
    maxd = 0
    for m in re.finditer(r'</?form\b', html):
        if m.group().startswith('</'):
            depth -= 1
        else:
            depth += 1
            maxd = max(maxd, depth)
    return maxd


# --- static-file checks (1-4, 6, 8) --------------------------------------

def test_files_exist_and_clean():
    assert WELCOME_HTML.is_file()
    assert WELCOME_JS.is_file()

    for path in (WELCOME_HTML, WELCOME_JS):
        text = path.read_text(encoding='utf-8')
        lower = text.lower()
        assert 'onclick=' not in lower
        assert 'oninput=' not in lower
        assert 'onchange=' not in lower

    js = WELCOME_JS.read_text(encoding='utf-8')
    for banned in BANNED_STRINGS:
        assert banned not in js.lower(), f'welcome.js contains banned string {banned!r}'
    assert 'localStorage' not in js
    assert 'fetch(' not in js

    # every play()/idle() call passes {el: ...} explicitly, and only uses
    # clip names that exist in zorp-motion.js's CLIP_NAMES.
    motion_js = ZORP_MOTION_JS.read_text(encoding='utf-8')
    m = re.search(r"CLIP_NAMES\s*=\s*\[([^\]]+)\]", motion_js)
    assert m, 'CLIP_NAMES not found in zorp-motion.js'
    clip_names = {c.strip().strip("'\"") for c in m.group(1).split(',')}

    play_calls = re.findall(r"\.play\(\s*'([a-z_]+)'\s*,\s*(\{[^)]*?\})\s*\)", js)
    assert play_calls, 'no pbZorp.play() calls found in welcome.js'
    for name, opts in play_calls:
        assert name in clip_names, f'welcome.js plays unknown clip {name!r}'
        assert 'el:' in opts or 'el :' in opts, f'welcome.js play({name!r}, ...) missing explicit el'

    idle_calls = re.findall(r"\.idle\(([^)]*)\)", js)
    assert idle_calls, 'no pbZorp.idle() calls found in welcome.js'
    for args in idle_calls:
        assert 'hero' in args, f'welcome.js idle({args}) does not pass the hero element'

    assert form_tag_max_depth(PROFILE_SETTINGS_HTML.read_text(encoding='utf-8')) <= 1


def test_sw_precache_excludes_welcome():
    sw = SW_JS.read_text(encoding='utf-8')
    m = re.search(r'PRECACHE_URLS\s*=\s*\[(.*?)\]', sw, re.S)
    assert m, 'PRECACHE_URLS not found'
    precache = m.group(1)
    assert '/welcome' not in precache
    assert 'welcome.js' not in precache

    version_m = re.search(r"CACHE_VERSION\s*=\s*'([^']+)'", sw)
    assert version_m, 'CACHE_VERSION not found'
    version = version_m.group(1)
    pinned = PWA_SMOKE.read_text(encoding='utf-8')
    assert version in pinned, f'{version!r} not pinned in test_pwa_smoke.py'


def test_guide_never_tour_includes_welcome():
    guide_js = GUIDE_JS.read_text(encoding='utf-8')
    m = re.search(r'NEVER_TOUR\s*=\s*\{(.*?)\};', guide_js, re.S)
    assert m, 'NEVER_TOUR not found in guide.js'
    assert re.search(r'\bwelcome\s*:\s*1\b', m.group(1)), 'welcome missing from NEVER_TOUR'


def test_registry_tracks_match_live_catalogue():
    with app.app_context():
        from app import _welcome_tracks, WELCOME_SURPRISE, _WELCOME_LEVEL_ORDER

    tracks = _welcome_tracks()
    assert tracks, 'no welcome tracks computed'
    for t in tracks:
        assert (t['level'], t['subject']) in GENERATOR_LAUNCH_PATHS
        assert not t['level'].startswith('alevel')
        assert not t['level'].startswith('myp')

    # Completeness, not just soundness: every subject actually launched under a
    # welcome-eligible level must be offered — a newly-launched subject (e.g. a
    # future GCSE Physics) must never be silently missing from /welcome without a
    # code change here failing this assertion first.
    offered = {(t['level'], t['subject']) for t in tracks}
    for level, subject in GENERATOR_LAUNCH_PATHS:
        if level in _WELCOME_LEVEL_ORDER:
            assert (level, subject) in offered, (
                f'{level}/{subject} is launched but not offered on /welcome — '
                '_welcome_level_subjects() dropped it'
            )

    # No real registry topic slug anywhere may equal WELCOME_SURPRISE (#11).
    for subjects in tr.TOPICS.values():
        for topics in subjects.values():
            assert WELCOME_SURPRISE not in topics


def main():
    test_files_exist_and_clean()
    test_sw_precache_excludes_welcome()
    test_guide_never_tour_includes_welcome()
    test_registry_tracks_match_live_catalogue()

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        email = f'welcome_{suffix}@example.com'
        handle = f'welcome_{suffix}'

        # --- logged-out access (22) -----------------------------------
        with app.test_client() as anon:
            r = anon.get('/welcome')
            assert r.status_code == 302 and '/login' in r.headers['Location']
            r = anon.post('/welcome/step', data={'step': 'skip'})
            assert r.status_code == 302 and '/login' in r.headers['Location']

        # --- fresh-user flow (12) --------------------------------------
        r = register(client, email, handle)
        assert r.status_code == 302, r.data[:300]
        assert r.headers['Location'] == '/welcome'

        r = client.get(r.headers['Location'], follow_redirects=True)
        assert r.status_code == 200
        html = r.data.decode()
        assert 'data-step="hello"' in html
        assert 'id="welcome"' in html
        assert f'@{handle}' in html
        assert 'data-welcome-hero' in html
        assert 'welcome.js?v=' in html
        assert 'id="study-buddy"' not in html
        assert f'data-guide-endpoint="welcome"' in html

        # copy / banned-nudge check (7) on the rendered hello screen and
        # on the source files themselves.
        for text in (html, WELCOME_HTML.read_text(encoding='utf-8'), WELCOME_JS.read_text(encoding='utf-8')):
            assert not BANNED_NUDGE_RE.search(text), text[:200]

        assert 'id="welcome-skip"' in html

        # --- step-through (13) ------------------------------------------
        token = csrf_from(html)
        r = client.post('/welcome/step', data={'csrf_token': token, 'step': 'hello'})
        assert r.status_code == 302 and r.headers['Location'] == '/welcome?step=level'

        r = client.get('/welcome?step=level')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'data-step="level"' in html
        assert 'What do you want to practise?' in html
        assert 'id="welcome-skip"' in html
        assert not BANNED_NUDGE_RE.search(html)

        with app.app_context():
            from app import _welcome_tracks
        tracks = _welcome_tracks()
        # every offered level value matches _welcome_tracks() (#9)
        for t in tracks:
            assert f'value="{t["key"]}"' in html

        token = csrf_from(html)
        r = client.post(
            '/welcome/step',
            data={'csrf_token': token, 'step': 'level', 'level': 'eursc_s1'},
        )
        assert r.status_code == 302 and r.headers['Location'] == '/welcome?step=topic'

        r = client.get('/welcome?step=topic')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'data-step="topic"' in html
        assert 'Pick a first topic' in html
        assert not BANNED_NUDGE_RE.search(html)

        with app.app_context():
            from app import _welcome_track, _welcome_topics, WELCOME_SURPRISE
        track = _welcome_track('eursc_s1')
        real_topics = {t['slug'] for t in _welcome_topics(track)}
        assert 'es0_fixture' not in real_topics

        offered = set(re.findall(r'name="topic" value="([a-z0-9_]+)"', html))
        assert WELCOME_SURPRISE in offered
        for slug in offered - {WELCOME_SURPRISE}:
            assert slug in real_topics, f'{slug} offered but not a real topic for this track'
            assert slug != 'es0_fixture'

        token = csrf_from(html)
        r = client.post(
            '/welcome/step',
            data={'csrf_token': token, 'step': 'topic', 'topic': 'measurement'},
        )
        assert r.status_code == 302 and r.headers['Location'] == '/welcome?step=ready'

        r = client.get('/welcome?step=ready')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'data-step="ready"' in html
        assert 'When you get one right, I’ll do a little dance.' in html
        assert not BANNED_NUDGE_RE.search(html)

        # ready form has the fields that actually start a question at / (13, 15)
        assert 'id="welcome-ready-form"' in html
        m = re.search(r'<form[^>]*id="welcome-ready-form"[^>]*>(.*?)</form>', html, re.S)
        assert m, 'welcome-ready-form not found'
        ready_form = m.group(1)
        ready_fields = dict(re.findall(r'name="([a-z_]+)" value="([^"]*)"', ready_form))
        assert ready_fields.get('level') == 'eursc'
        assert ready_fields.get('subject') == 'science'
        assert ready_fields.get('topic') == 'measurement'
        assert ready_fields.get('action') == 'start'

        # --- stored guide_json shape (14) --------------------------------
        raw = guide_json_for(handle)
        assert raw is not None
        assert '"level":"eursc_s1"' in raw
        assert '"topic":"measurement"' in raw
        assert '"welcome_done":true' in raw

        # --- posting the Ready form to / actually returns a question (15) --
        token = csrf_from(html)
        r = client.post(
            '/',
            data={
                'csrf_token': token,
                'level': ready_fields['level'],
                'subject': ready_fields['subject'],
                'topic': ready_fields['topic'],
                'mode': 'standard',
                'difficulty': 'foundational',
                'action': 'start',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert 'problem-card-inner' in r.data.decode()

        # --- guide state shape unaffected (16) ---------------------------
        r = client.get('/api/v1/me/settings')
        settings = r.get_json()['settings']
        assert set(settings['guide'].keys()) == {'v', 'origin', 'tours', 'rewards'}
        assert 'welcome_done' not in settings
        assert 'level' not in settings
        assert 'topic' not in settings

        r = client.get('/')
        home = r.data.decode()
        gm = re.search(
            r'<script type="application/json" id="pb-guide-state"([^>]*)>(.*?)</script>',
            home, re.S,
        )
        assert gm
        assert 'data-guide-persisted="1"' not in gm.group(1)

        # --- PATCH cannot write welcome keys (17) ------------------------
        before = guide_json_for(handle)
        r = client.patch(
            '/api/v1/me/settings',
            json={'guide': {'welcome_done': True, 'level': 'hacked', 'topic': 'hacked'}},
        )
        assert r.status_code == 200
        after = guide_json_for(handle)
        assert '"level":"hacked"' not in after
        assert '"topic":"hacked"' not in after
        assert '"level":"eursc_s1"' in after
        assert '"topic":"measurement"' in after

        # --- done users are redirected (18) ------------------------------
        for step in (None, 'hello', 'level', 'topic'):
            path = '/welcome' if step is None else f'/welcome?step={step}'
            r = client.get(path)
            assert r.status_code == 302 and r.headers['Location'] == '/', (step, r.headers.get('Location'))
        r = client.get('/welcome?step=ready')
        assert r.status_code == 200

        # --- replay (20): settings has the control, works, and does not
        # reset an unrelated setting ---------------------------------------
        r = client.patch('/api/v1/me/settings', json={'sound_enabled': True})
        assert r.status_code == 200

        r = client.get('/profile/settings')
        settings_html = r.data.decode()
        assert 'id="guide-replay-welcome"' in settings_html
        assert 'replay_welcome' in settings_html
        assert form_tag_max_depth(settings_html) <= 1

        token = csrf_from(settings_html)
        r = client.post(
            '/profile/settings',
            data={'csrf_token': token, 'action': 'replay_welcome'},
        )
        assert r.status_code == 302 and r.headers['Location'] == '/welcome'
        raw = guide_json_for(handle)
        assert '"welcome_done":false' in raw
        assert '"level":"eursc_s1"' in raw  # level/topic kept as-is

        r = client.get('/api/v1/me/settings')
        assert r.get_json()['settings']['sound_enabled'] is True  # untouched by replay

        # --- validation / tampering never 500s and never writes (21) ------
        before = guide_json_for(handle)
        html = client.get('/welcome?step=level').data.decode()
        token = csrf_from(html)
        for bad in ('../../../etc/passwd', '<script>alert(1)</script>', 'alevel_a1', '', 'x' * 200):
            r = client.post(
                '/welcome/step',
                data={'csrf_token': token, 'step': 'level', 'level': bad},
            )
            assert r.status_code != 500
            assert r.status_code == 302
        after = guide_json_for(handle)
        assert after == before

        html = client.get('/welcome?step=topic').data.decode()
        token = csrf_from(html)
        for bad_topic in ('bidmas', 'es0_fixture', '<script>', '../../etc/passwd', ''):
            r = client.post(
                '/welcome/step',
                data={'csrf_token': token, 'step': 'topic', 'topic': bad_topic},
            )
            assert r.status_code != 500
            assert r.status_code == 302
        after = guide_json_for(handle)
        assert after == before, 'a wrong-course/fixture/garbage topic must not be written'

        r = client.post('/welcome/step', data={'csrf_token': token, 'step': 'not_a_real_step'})
        assert r.status_code == 302
        assert guide_json_for(handle) == before

        # topic POST with no stored course at all
        with get_db() as conn:
            uid = User.get_by_handle(conn, handle).id
            conn.execute(
                "UPDATE user_profile_settings SET guide_json = '{}' WHERE user_id = ?",
                (uid,),
            )
            conn.commit()
        html = client.get('/welcome?step=level').data.decode()
        token = csrf_from(html)
        r = client.post(
            '/welcome/step',
            data={'csrf_token': token, 'step': 'topic', 'topic': 'measurement'},
        )
        assert r.status_code == 302
        assert r.headers['Location'] == '/welcome?step=level'
        assert guide_json_for(handle) == '{}'

        # --- CSRF genuinely enforced (23) ---------------------------------
        html = client.get('/welcome?step=level').data.decode()
        good_token = csrf_from(html)
        before = guide_json_for(handle)
        # Pin PB_DB_PATH to whatever _db_path() is *actually* already resolving to
        # (while PB_TESTING is still '1', so this picks up the sticky PB_TEST_DB_PATH
        # this run has been using all along) — never point the app at a fresh,
        # unrelated database. Flipping PB_TESTING off must not also swap databases,
        # or every query after this point 500s against an empty schema.
        import app as app_module
        current_db_path = app_module._db_path()
        saved_db_path = os.environ.get('PB_DB_PATH')
        saved_testing = os.environ.get('PB_TESTING')
        os.environ['PB_DB_PATH'] = current_db_path
        os.environ['PB_TESTING'] = '0'
        try:
            r = client.post(
                '/welcome/step',
                data={'csrf_token': 'not-the-real-token', 'step': 'level', 'level': 'gcse_maths'},
            )
            assert r.status_code == 302
            assert guide_json_for(handle) == before, 'bad CSRF token must not write'

            r = client.post(
                '/welcome/step',
                data={'csrf_token': good_token, 'step': 'level', 'level': 'gcse_maths'},
            )
            assert r.status_code == 302
            assert '"level":"gcse_maths"' in guide_json_for(handle), 'a real CSRF token must be accepted'
        finally:
            if saved_testing is None:
                os.environ.pop('PB_TESTING', None)
            else:
                os.environ['PB_TESTING'] = saved_testing
            if saved_db_path is None:
                os.environ.pop('PB_DB_PATH', None)
            else:
                os.environ['PB_DB_PATH'] = saved_db_path

        # --- skip from every screen (19) -----------------------------------
        for i in range(4):
            skip_suffix = ''.join(random.choices(string.ascii_lowercase, k=8))
            skip_email = f'welcome_skip_{skip_suffix}@example.com'
            skip_handle = f'wskip_{skip_suffix}'
            r = register(client, skip_email, skip_handle)
            assert r.status_code == 302 and r.headers['Location'] == '/welcome'
            step_names = ['hello', 'level', 'topic', 'ready']
            step_name = step_names[i]
            # walk to the target step first (server won't render `ready`/`topic`
            # without prior choices, so make the minimal choices needed)
            # Setting the level (or level+topic) marks intermediate progress; the
            # topic step also flips welcome_done, so only do that when the
            # target screen to test Skip from is 'ready' (which renders fine
            # even once done, per welcome()'s own-track-and-topic exception).
            if i >= 2:
                html = client.get('/welcome?step=level').data.decode()
                token = csrf_from(html)
                client.post('/welcome/step', data={'csrf_token': token, 'step': 'level', 'level': 'gcse_cs'})
            if i >= 3:
                html = client.get('/welcome?step=topic').data.decode()
                token = csrf_from(html)
                client.post('/welcome/step', data={'csrf_token': token, 'step': 'topic', 'topic': 'ethical'})
            path = '/welcome' if step_name == 'hello' else f'/welcome?step={step_name}'
            html = client.get(path).data.decode()
            assert 'id="welcome-skip"' in html
            token = csrf_from(html)
            r = client.post('/welcome/step', data={'csrf_token': token, 'step': 'skip'})
            assert r.status_code == 302 and r.headers['Location'] == '/'
            raw = guide_json_for(skip_handle)
            assert '"welcome_done":true' in raw

            with get_db() as conn:
                uid = User.get_by_handle(conn, skip_handle).id
                delete_user_account(conn, uid)
                leftover = remaining_user_rows(conn, uid)
                assert not {t: n for t, n in leftover.items() if n}

        # --- cleanup -------------------------------------------------------
        with get_db() as conn:
            uid = User.get_by_handle(conn, handle).id
            delete_user_account(conn, uid)
            leftover = remaining_user_rows(conn, uid)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero

    print('Welcome flow smoke tests passed.')


if __name__ == '__main__':
    main()
