"""E9 Phase 4: Zorp's sounds, off by default (docs/ZORP_CHARM.md 3.4, 6 Phase 4, decision D6 = B).

Run: python scripts/test_zorp_sound_smoke.py

Two halves.
* The cues and their gate: scripts/zorp_sound_harness.js runs the real static/js/sound.js (and celebrate.js) in Node
  against a fake AudioContext and a virtual clock (silent by default, no context on load, the tap rule, quiz, hidden tab,
  the 400 ms arbiter, one sequence per 7 s, gains and durations against the table, blips, confetti silent when cues are on).
  Static checks pin where force, the blips and the cue calls may appear.
* The zorp_sound setting end to end (the Flask test client): default off for new and existing users, the form and the PATCH
  validator (chatter and junk rejected), the mirror on <html>, nothing leaking to other viewers, the privacy documents, and
  the known settings-switch persistence bug of docs/AI_HANDOFF.md (checked here, not assumed).
Skips the Node half cleanly when `node` is not on PATH.
"""
import os

os.environ['PB_TESTING'] = '1'

import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

JS_DIR = ROOT / 'static' / 'js'
TEMPLATES = ROOT / 'templates'
HARNESS = ROOT / 'scripts' / 'zorp_sound_harness.js'


def _read(path):
    return Path(path).read_text(encoding='utf-8')


def _csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def _register(client, tag):
    suffix = uuid.uuid4().hex[:8]
    handle = f'zs{tag}_{suffix}'
    r = client.get('/register')
    r = client.post(
        '/register',
        data={
            'csrf_token': _csrf(r.data.decode()),
            'email': f'{handle}@example.com',
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    return handle


def _save(client, **fields):
    token = _csrf(client.get('/profile/settings').data.decode())
    data = {'csrf_token': token, 'profile_visibility': 'followers_only', 'default_share_visibility': 'followers_only'}
    data.update(fields)
    r = client.post('/profile/settings', data=data, follow_redirects=True)
    assert r.status_code == 200 and b'Settings saved' in r.data
    return r


def _checked(html, name):
    m = re.search(r'<input type="radio" name="%s" value="([a-z]+)"\s*\n?\s*checked>' % name, html)
    return m.group(1) if m else None


def _patch(client, payload):
    return client.patch('/api/v1/me/settings', data=json.dumps(payload), content_type='application/json')


# ---------------------------------------------------------------------------------------------
# The cues and their gate (Node)
# ---------------------------------------------------------------------------------------------

def test_cue_gate_harness():
    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping the sound harness.')
        return
    result = subprocess.run([node, str(HARNESS), str(JS_DIR / 'sound.js'), str(JS_DIR / 'celebrate.js')],
                            cwd=str(ROOT), check=False, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, 'zorp sound harness FAILED (see node output above)'


def test_force_and_blips_only_from_styleguide():
    """3.4.7: only styleguide.js may pass force, turn the D7 blips on or arm the tap listeners; D7 blips are not wired to pupils."""
    hits = {'force': [], 'blips': [], 'arm': []}
    for path in sorted(JS_DIR.glob('*.js')) + sorted(TEMPLATES.rglob('*.html')):
        text = _read(path)
        if re.search(r'\bforce\s*:\s*true\b', text):
            hits['force'].append(path.name)
        if re.search(r'\bblips\s*:\s*true\b', text):
            hits['blips'].append(path.name)
        if re.search(r'pbSound\.arm\(|\bs\.arm\(', text):
            hits['arm'].append(path.name)
    assert hits == {'force': ['styleguide.js'], 'blips': ['styleguide.js'], 'arm': ['styleguide.js']}, hits
    talk = _read(JS_DIR / 'zorp-talk.js')
    assert 'o.blips' in talk and 'force: o.force' in talk and 'force: true' not in talk, 'talk passes the styleguide options through, never its own'
    for name in ('guide.js', 'study-buddy.js', 'welcome.js', 'celebrate.js', 'zorp-poses.js'):
        text = _read(JS_DIR / name)
        assert not re.search(r'\bblips\b|\bforce\s*:', text), f'{name} must not touch blips or pass force'


def test_sound_js_stays_synthesised_and_loaded_everywhere():
    sound = _read(JS_DIR / 'sound.js')
    for banned in ('fetch(', 'decodeAudioData', 'XMLHttpRequest', 'new Audio', 'createMediaElementSource', '.mp3', '.ogg', '.wav'):
        assert banned not in sound, banned
    assert 'createOscillator' in sound and 'new AC()' in sound
    # nothing runs on load except binding the listeners: no context is created at the top level
    top = sound[sound.index('  bindUnlock();'):]
    assert 'ensureCtx' not in top and 'ctxReady' not in top
    base = _read(TEMPLATES / 'base.html')
    assert "js/sound.js') }}?v=4" in base


def test_guide_welcome_and_react_pass_cue_true():
    guide = _read(JS_DIR / 'guide.js')
    assert "playGesture(step.gesture, null, step.mode === 'reward')" in guide and 'cue: !!cue' in guide
    assert "pbZorp.play(name, { el: el, cue: !!cue })" in guide.replace('window.', '')
    welcome = _read(JS_DIR / 'welcome.js')
    assert "{ el: hero, cue: true }" in welcome
    core = _read(JS_DIR / 'zorp-motion.js')
    assert 'cue: !!(plan && plan.cue)' in core and 'view: vw, cue: opts.cue' in core
    poses = _read(JS_DIR / 'zorp-poses.js')
    assert 'CUED = { first_correct: 1, milestone: 1, lesson_complete: 1 }' in poses, 'streak, correct and wrong never sound a cue'
    assert 'cue: !!CUED[kind]' in poses
    celebrate = _read(JS_DIR / 'celebrate.js')
    assert 'ps.cuesActive()' in celebrate and 'ps.cued(' in celebrate


# ---------------------------------------------------------------------------------------------
# The zorp_sound setting
# ---------------------------------------------------------------------------------------------

def test_constants_and_normaliser():
    from models.social import (
        ZORP_SOUND_CELEBRATIONS, ZORP_SOUND_CHATTER, ZORP_SOUND_CHOICES, ZORP_SOUND_DEFINED, ZORP_SOUND_OFF,
        normalize_zorp_sound,
    )

    assert ZORP_SOUND_CHOICES == ('off', 'celebrations')
    assert ZORP_SOUND_DEFINED == ('off', 'celebrations', 'chatter') and ZORP_SOUND_CHATTER == 'chatter'
    assert normalize_zorp_sound('celebrations') == ZORP_SOUND_CELEBRATIONS
    for junk in ('chatter', 'CELEBRATIONS', '', None, 1, ['celebrations'], 'on', True):
        assert normalize_zorp_sound(junk) == ZORP_SOUND_OFF, junk


def test_default_off_for_new_users_and_mirrored_to_html():
    from app import app

    with app.test_client() as client:
        anon = client.get('/login').data.decode()
        assert re.search(r'<html[^>]*data-zorp-sound="off"', anon), 'logged-out pages mirror off'
        _register(client, 'new')
        r = client.get('/profile/settings')
        html = r.data.decode()
        assert _checked(html, 'zorp_sound') == 'off', 'a new account has Zorp silent'
        assert re.search(r'<html[^>]*data-zorp-sound="off"', html)
        home = client.get('/').data.decode()
        assert re.search(r'<html[^>]*data-zorp-sound="off"', home)
        got = client.get('/api/v1/me/settings').get_json()
        assert got['settings']['zorp_sound'] == 'off'


def test_form_round_trip_and_junk():
    from app import app

    with app.test_client() as client:
        _register(client, 'rt')
        # cycle through the non-default value first, so a save that did nothing would fail
        for value in ('celebrations', 'off', 'celebrations'):
            _save(client, zorp_sound=value)
            html = client.get('/profile/settings').data.decode()
            assert _checked(html, 'zorp_sound') == value, f'{value} did not persist'
            assert re.search(r'<html[^>]*data-zorp-sound="%s"' % value, client.get('/').data.decode()), 'html mirror'
        # chatter and junk on the form are stored as off, never as themselves
        for junk in ('chatter', 'bogus', '<script>', 'CELEBRATIONS'):
            _save(client, zorp_sound='celebrations')
            _save(client, zorp_sound=junk)
            got = client.get('/api/v1/me/settings').get_json()['settings']['zorp_sound']
            assert got == 'off', f'{junk!r} stored as {got!r}'
        # a form that leaves the field out (an old cached page) falls back to off, like motion_preference
        _save(client, zorp_sound='celebrations')
        _save(client)
        assert client.get('/api/v1/me/settings').get_json()['settings']['zorp_sound'] == 'off'


def test_other_saves_keep_zorp_sound():
    """Every route that rewrites the settings row goes through _settings_to_json, which carries zorp_sound."""
    from app import app

    with app.test_client() as client:
        _register(client, 'keep')
        _save(client, zorp_sound='celebrations')
        # PATCH of another field
        r = _patch(client, {'sound_enabled': True})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_sound'] == 'celebrations'
        r = _patch(client, {'theme_preference': 'dark', 'motion_preference': 'reduced'})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_sound'] == 'celebrations'
        r = _patch(client, {'guide': {'origin': True}})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_sound'] == 'celebrations'
        # the Replay intro button rewrites the row too
        token = _csrf(client.get('/profile/settings').data.decode())
        client.post('/profile/settings', data={'csrf_token': token, 'action': 'replay_guide_intro'}, follow_redirects=True)
        assert client.get('/api/v1/me/settings').get_json()['settings']['zorp_sound'] == 'celebrations'
        html = client.get('/profile/settings').data.decode()
        assert _checked(html, 'zorp_sound') == 'celebrations'
        # and the answer-tone switch is independent of it: turning it off leaves Zorp's setting alone
        r = _patch(client, {'sound_enabled': False})
        assert r.get_json()['settings']['sound_enabled'] is False and r.get_json()['settings']['zorp_sound'] == 'celebrations'


def test_patch_validation_rejects_chatter_and_junk():
    from app import app

    with app.test_client() as client:
        _register(client, 'pv')
        for bad in ('chatter', 'bogus', '', 'Celebrations', 1, True, None, ['off'], {'a': 1}):
            r = _patch(client, {'zorp_sound': bad})
            assert r.status_code == 400, f'{bad!r} gave {r.status_code}'
            body = r.get_json()
            assert body['code'] == 'invalid_zorp_sound' and 'off, celebrations' in body['error'], body
        assert client.get('/api/v1/me/settings').get_json()['settings']['zorp_sound'] == 'off', 'a rejected value stores nothing'
        for good in ('celebrations', 'off'):
            r = _patch(client, {'zorp_sound': good})
            assert r.status_code == 200 and r.get_json()['settings']['zorp_sound'] == good
        # an unknown sibling field is still refused, and a bad zorp_sound beside a good field changes neither
        r = _patch(client, {'zorp_sound': 'celebrations'})
        assert r.status_code == 200
        r = _patch(client, {'zorp_sound': 'chatter', 'theme_preference': 'dark'})
        assert r.status_code == 400
        got = client.get('/api/v1/me/settings').get_json()['settings']
        assert got['zorp_sound'] == 'celebrations' and got['theme_preference'] != 'dark'


def test_existing_users_migrate_to_off():
    """A database from before Phase 4 has no zorp_sound column: the startup migration adds it, with 'off' for every existing row."""
    from app import app, get_db

    with app.test_client() as client:
        handle = _register(client, 'old')
    with get_db() as conn:
        uid = conn.execute('SELECT id FROM users WHERE handle = ?', (handle,)).fetchone()['id']
        conn.execute('ALTER TABLE user_profile_settings DROP COLUMN zorp_sound')
        conn.commit()
        cols = [r[1] for r in conn.execute('PRAGMA table_info(user_profile_settings)').fetchall()]
        assert 'zorp_sound' not in cols
    code = (
        "import os, sys\n"
        "sys.path.insert(0, %r)\n"
        "import app as a\n"
        "from models.social import get_profile_settings\n"
        "with a.get_db() as conn:\n"
        "    cols = {r[1]: r for r in conn.execute('PRAGMA table_info(user_profile_settings)').fetchall()}\n"
        "    assert 'zorp_sound' in cols, cols.keys()\n"
        "    assert cols['zorp_sound'][4] == \"'off'\", cols['zorp_sound']\n"
        "    assert get_profile_settings(conn, %d)['zorp_sound'] == 'off'\n"
        "print('migrated')\n"
    ) % (str(ROOT), uid)
    result = subprocess.run([sys.executable, '-c', code], cwd=str(ROOT), env=dict(os.environ), check=False,
                            capture_output=True, text=True)
    assert result.returncode == 0 and 'migrated' in result.stdout, result.stdout + result.stderr


def test_not_visible_to_other_viewers():
    """Gate Q2: zorp_sound is never shown to anyone else (public profile, the other viewer's own mirror, the settings API)."""
    from app import app, get_db

    a_client, b_client = app.test_client(), app.test_client()   # not `with`: a preserved request context would leak A's login into B
    a_handle = _register(a_client, 'va')
    _register(b_client, 'vb')
    _save(a_client, zorp_sound='celebrations', profile_visibility='public')
    page = b_client.get(f'/u/{a_handle}')
    assert page.status_code == 200
    html = page.data.decode()
    assert 'zorp_sound' not in html and 'celebrations' not in html.lower()
    assert re.search(r'<html[^>]*data-zorp-sound="off"', html), "B's page mirrors B's own setting, never A's"
    assert app.test_client().get('/api/v1/me/settings').status_code in (401, 302), 'the settings API is own-account only'
    with get_db() as conn:
        assert 'zorp_sound' in [r[1] for r in conn.execute('PRAGMA table_info(user_profile_settings)').fetchall()]
    app_src = _read(ROOT / 'app.py')
    start = app_src.index('def _build_public_profile_context')
    assert 'zorp_sound' not in app_src[start:start + 6000], 'the public profile context never reads it'


def test_settings_page_markup_and_copy():
    from app import app

    with app.test_client() as client:
        _register(client, 'ui')
        html = client.get('/profile/settings').data.decode()
    head = html.index('id="zorp-sound-label"')
    section = html[head:html.index('</section>', head)]
    assert 'role="radiogroup"' in section and 'aria-labelledby="zorp-sound-label"' in section
    assert '>Zorp’s sounds</div>' in section
    assert 'Short, quiet sounds when Zorp celebrates. Best with headphones. They play only with full motion.' in section
    # Final audit B4: the option labels use colons (no dash), and the intro says cues need full motion
    assert '<strong>Off</strong>: Zorp is silent' in section and '<strong>Celebrations</strong>: a short sound when Zorp celebrates' in section
    assert '—' not in section and '–' not in section
    values = re.findall(r'<input type="radio" name="zorp_sound" value="([a-z]+)"', section)
    assert values == ['off', 'celebrations'], f'chatter is never offered: {values}'
    assert 'chatter' not in html.lower()
    # its own panel straight after the sound switch's, which keeps covering the answer tones only
    assert html.index('name="sound_enabled"') < html.index('name="zorp_sound"') < html.index('id="guide-replay-intro"')
    assert 'Play sound effects for correct and incorrect answers' in html
    # system voice, marked so the copy lint covers it
    assert section.count('data-zorp-voice="system:system_settings"') >= 3
    # the page is well formed around it (an unbalanced tag once slipped in while editing)
    for tag in ('section', 'div', 'fieldset', 'form'):
        assert html.count(f'<{tag}') == html.count(f'</{tag}>'), tag


def test_sound_switch_persists():
    """The known bug of docs/AI_HANDOFF.md 1.1: the sound switch UI did not persist after Save. Checked here, not assumed:
    the macro is a native checkbox in a label with an in-flow 44 x 26 track and no absolutely positioned overlay, and Save persists
    sound_enabled on, off and on again (non-default value first). The browser-level check (a real click) is in the phase report."""
    from app import app

    macro = _read(TEMPLATES / 'partials' / 'settings_switch.html')
    assert '<label class="switch-row">' in macro and 'type="checkbox"' in macro and 'name="{{ name }}" value="1"' in macro
    css = _read(ROOT / 'static' / 'css' / 'pages.css')
    track = css[css.index('\n.switch {'):css.index('}', css.index('\n.switch {'))]
    assert 'width: 44px' in track and 'height: 26px' in track and 'position: relative' in track
    assert 'inset' not in track and 'position: absolute' not in track, 'AI_HANDOFF 1.1: no overlay on the track'
    with app.test_client() as client:
        _register(client, 'sw')
        for want in (True, False, True):
            fields = {'sound_enabled': '1'} if want else {}
            _save(client, **fields)
            html = client.get('/profile/settings').data.decode()
            m = re.search(r'<input type="checkbox" class="switch-input" name="sound_enabled" value="1"( checked)?>', html)
            assert m and bool(m.group(1)) is want, f'sound_enabled={want} did not persist'
            assert client.get('/api/v1/me/settings').get_json()['settings']['sound_enabled'] is want
            body = client.get('/').data.decode()
            assert ('data-sound-enabled="1"' in body) is want


# ---------------------------------------------------------------------------------------------
# Privacy documents (same change as the setting)
# ---------------------------------------------------------------------------------------------

def test_privacy_documents_name_zorp_sound():
    ropa = _read(ROOT / 'docs' / 'ROPA.md')
    row1 = [line for line in ropa.splitlines() if line.startswith('| 1 |')][0]
    assert 'zorp_sound' in row1 and 'theme_preference' in row1 and 'motion_preference' in row1
    full = _read(TEMPLATES / 'legal_privacy.html')
    assert 'Zorp' in full[full.index('<strong>Settings:</strong>'):full.index('<strong>Security:</strong>')]
    simple = _read(TEMPLATES / 'legal_privacy_simple.html')
    assert 'Zorp' in simple and 'sound' in simple.lower()
    dpia = _read(ROOT / 'docs' / 'DPIA.md')
    log = [line for line in dpia.splitlines() if line.startswith('| 2026-10-0') and 'zorp_sound' in line]
    assert log, 'a dated DPIA review-log row names zorp_sound'
    assert 'off by default' in log[0] and 'ROPA' in log[0] and 'privacy notice' in log[0].lower()
    sg = _read(ROOT / 'docs' / 'SECURITY_AND_GDPR.md')
    assert 'zorp_sound' in sg


def main():
    test_cue_gate_harness()
    test_force_and_blips_only_from_styleguide()
    test_sound_js_stays_synthesised_and_loaded_everywhere()
    test_guide_welcome_and_react_pass_cue_true()
    test_constants_and_normaliser()
    test_default_off_for_new_users_and_mirrored_to_html()
    test_form_round_trip_and_junk()
    test_other_saves_keep_zorp_sound()
    test_patch_validation_rejects_chatter_and_junk()
    test_existing_users_migrate_to_off()
    test_not_visible_to_other_viewers()
    test_settings_page_markup_and_copy()
    test_sound_switch_persists()
    test_privacy_documents_name_zorp_sound()
    print('Zorp sound smoke (E9 Phase 4) passed.')


if __name__ == '__main__':
    main()
