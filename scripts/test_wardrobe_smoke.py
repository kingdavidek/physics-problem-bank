"""E10 phase 6b wardrobe smoke: catalogue, unlocks, server validation, where the outfit renders, the badge stage tie-in, lazy loading,
caps, export and erase, voice. Run: python scripts/test_wardrobe_smoke.py"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from flask import jsonify, request  # noqa: E402
from flask_login import current_user, login_required  # noqa: E402

import app as appmod  # noqa: E402
from app import app, get_db  # noqa: E402
from models import gamification as gam  # noqa: E402
from models import zorp_kit, zorp_voice  # noqa: E402
from models import zorp_wardrobe as ward  # noqa: E402
from models.account_deletion import delete_user_account  # noqa: E402
from models.data_export import build_user_export  # noqa: E402

# Own caps (bytes). 2026-11-08: E10 phase 6b, lazy files that load only on the profile page.
CAPS = {
    'static/js/wardrobe.js': 6500,
    'static/css/wardrobe.css': 2800,
}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


@app.get('/_t/ward-earn')
@login_required
def _t_ward_earn():
    """Award a badge row and note it for delivery in this answer (the test stands in for the real award paths)."""
    key = request.args['key']
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, datetime('now'))",
                     (current_user.id, key))
        conn.commit()
    appmod._note_new_milestones(current_user.id, [key])
    return jsonify({'ok': True})


def register(client):
    s = uuid.uuid4().hex[:8]
    r = client.post('/api/v1/auth/register', json={'email': f'wd_{s}@example.com', 'handle': f'wd_{s}',
                                                   'password': 'password123', 'age_confirm': True},
                    headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    b = r.get_json()
    return b['token'], b['user']['id'], f'wd_{s}'


def session_login(client, uid):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True


def earn(uid, key):
    with app.app_context():
        with get_db() as conn:
            conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, datetime('now'))", (uid, key))
            conn.commit()


def patch(client, tok, body):
    return client.patch('/api/v1/me/settings', json=body, headers={'Authorization': f'Bearer {tok}', 'Accept': 'application/json'})


def test_catalogue_shape():
    ids = [i['id'] for i in ward.ITEMS]
    assert len(ids) == len(set(ids)), 'duplicate item ids'
    for slot, label in ward.SLOTS:
        rows = [i for i in ward.ITEMS if i['slot'] == slot]
        assert label and len(rows) >= 2, slot
        assert sum(1 for i in rows if ward.is_default(i)) == 1, f'{slot}: exactly one always-available default'
        assert all((i['unlock'] is None) == ward.is_default(i) for i in rows), f'{slot}: only the default is open'
    assert set(ward.SLOT_KEYS) == set(zorp_kit.LOOK_FIELDS), 'every live-rig slot is covered, no extra slot'
    for i in ward.ITEMS:
        if ward.is_default(i):
            continue
        assert i['value'] in zorp_kit.LOOK_FIELDS[i['slot']], f'{i["id"]} is not live-approved art (kit-only items stay out)'
        rule = i['unlock']
        if rule[0] == 'badge':
            assert rule[1] in gam.MILESTONE_CATALOG, rule
        else:
            assert rule[1] in gam.BADGE_FAMILIES and rule[2], rule
        assert len(i['name']) <= 22, i['name']
        assert len(zorp_voice_line(i)) <= 80, i
    # no kit-only hats sneak in
    assert not ({'toque', 'quiff'} & {i['value'] for i in ward.ITEMS})


def zorp_voice_line(item):
    return 'New in your wardrobe: ' + item['noun'] + '.'


def test_every_badge_family_unlocks_something():
    covered = set()
    for i in ward.ITEMS:
        rule = i['unlock']
        if not rule:
            continue
        covered.add(rule[1] if rule[0] == 'family' else gam.MILESTONE_CATALOG[rule[1]]['family'])
    missing = set(gam.BADGE_FAMILIES) - covered
    assert not missing, f'badge families that unlock nothing: {sorted(missing)}'
    # one badge opens at most one item, so the badge stage line is unambiguous
    per_key = {}
    for i in ward.ITEMS:
        if i['unlock'] and i['unlock'][0] == 'badge':
            per_key[i['unlock'][1]] = per_key.get(i['unlock'][1], 0) + 1
    assert max(per_key.values()) == 1, per_key


def test_server_validation_and_storage():
    with app.test_client() as c:
        tok, uid, _h = register(c)
        r = c.get('/api/v1/me/settings', headers={'Authorization': f'Bearer {tok}'})
        assert r.get_json()['settings']['zorp_outfit'] is None, 'never chose -> null'
        # locked, unknown, malformed: refused, nothing stored
        for body, code in (
            ({'zorp_outfit': {'hat': 'mortarboard'}}, 'locked_item'),
            ({'zorp_outfit': {'colour': 'sunny'}}, 'locked_item'),
            ({'zorp_outfit': {'hat': 'toque'}}, 'invalid_outfit'),
            ({'zorp_outfit': {'cape': 'red'}}, 'invalid_outfit'),
            ({'zorp_outfit': {'hat': 5}}, 'invalid_outfit'),
            ({'zorp_outfit': ['hat']}, 'invalid_outfit'),
            ({'zorp_outfit': 'beanie'}, 'invalid_outfit'),
        ):
            r = patch(c, tok, body)
            assert r.status_code == 400 and r.get_json()['code'] == code, (body, r.status_code, r.data)
        with app.app_context(), get_db() as conn:
            assert conn.execute('SELECT zorp_outfit_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()[0] == ''
        # a refused outfit refuses the whole PATCH
        before = c.get('/api/v1/me/settings', headers={'Authorization': f'Bearer {tok}'}).get_json()['settings']['sound_enabled']
        r = patch(c, tok, {'sound_enabled': not before, 'zorp_outfit': {'hat': 'beanie'}})
        assert r.status_code == 400
        assert c.get('/api/v1/me/settings', headers={'Authorization': f'Bearer {tok}'}).get_json()['settings']['sound_enabled'] is before
        # defaults are always allowed; an explicit plain Zorp is stored as chosen
        r = patch(c, tok, {'zorp_outfit': {}})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_outfit'] == {}, r.data
        earn(uid, 'first_lesson_step')
        r = patch(c, tok, {'zorp_outfit': {'hat': 'mortarboard', 'colour': ''}})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_outfit'] == {'hat': 'mortarboard'}, r.data
        # other settings PATCHes leave the outfit alone
        r = patch(c, tok, {'sound_enabled': True})
        assert r.get_json()['settings']['zorp_outfit'] == {'hat': 'mortarboard'}
        # a family rule: any subject badge opens the short antennae
        assert patch(c, tok, {'zorp_outfit': {'antenna': 'short'}}).status_code == 400
        earn(uid, 'subject_completed:gcse:maths')
        assert patch(c, tok, {'zorp_outfit': {'antenna': 'short'}}).status_code == 200
        # reset: back to the automatic look
        r = patch(c, tok, {'zorp_outfit': None})
        assert r.status_code == 200 and r.get_json()['settings']['zorp_outfit'] is None
        with app.app_context(), get_db() as conn:
            assert conn.execute('SELECT zorp_outfit_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()[0] == ''


def test_outfit_renders_and_automatic_look_stays():
    with app.test_client() as c:
        tok, uid, _h = register(c)
        session_login(c, uid)
        earn(uid, 'first_lesson_step')   # latest pose badge 'scholar': violet, long antennae, mortarboard (the automatic look)
        html = c.get('/profile').get_data(as_text=True)
        corner = html.split('<aside id="study-buddy"')[1].split('data-buddy-card')[0]
        assert 'data-zorp-colour="violet"' in corner and 'zorp-hat--mortarboard' in corner, 'never chose: automatic look kept'
        # chosen: only the chosen items, not the automatic ones
        earn(uid, 'app_tour')
        assert patch(c, tok, {'zorp_outfit': {'hat': 'beanie'}}).status_code == 200
        html = c.get('/profile').get_data(as_text=True)
        corner = html.split('<aside id="study-buddy"')[1].split('data-buddy-card')[0]
        guide = html.split('data-guide-face')[1].split('</svg>')[0]
        for part in (corner, guide):
            assert 'zorp-hat--beanie' in part and 'zorp-hat--mortarboard' not in part, 'the outfit renders in the corner buddy and the guide rig'
            assert 'data-zorp-colour' not in part and 'data-zorp-antenna' not in part
        # an item that is stored but no longer unlocked is dropped on read (never trust storage either)
        with app.app_context(), get_db() as conn:
            conn.execute('UPDATE user_profile_settings SET zorp_outfit_json = ? WHERE user_id = ?',
                         ('{"v":1,"colour":"sunny","hat":"beanie","cape":"x"}', uid))
            conn.commit()
        corner = c.get('/profile').get_data(as_text=True).split('<aside id="study-buddy"')[1].split('data-buddy-card')[0]
        assert 'data-zorp-colour' not in corner and 'zorp-hat--beanie' in corner
        # junk storage reads as never chose
        assert ward.parse_outfit('not json') is None and ward.parse_outfit('[1]') is None and ward.parse_outfit('') is None


def test_panel_on_profile():
    with app.test_client() as c:
        tok, uid, _h = register(c)
        session_login(c, uid)
        html = c.get('/profile').get_data(as_text=True)
        assert 'id="wardrobe"' in html and 'Zorp’s wardrobe' in html
        panel = html.split('id="wardrobe"')[1].split('data-wd-art')[0]
        assert panel.count('<fieldset') == len(ward.SLOTS) and panel.count('<legend>') == len(ward.SLOTS)
        # a new pupil: only the defaults can be worn, the rest are disabled with the reason as visible text
        radios = re.findall(r'<input type="radio"[^>]*>', panel)
        assert len(radios) == len(ward.ITEMS)
        enabled = [r for r in radios if ' disabled' not in r]
        assert len(enabled) == len(ward.SLOTS) and all('value=""' in r and ' checked' in r for r in enabled), enabled
        assert 'Earn Lesson learner to unlock' in panel and 'data-badge-open="first_lesson_step"' in panel
        assert 'Earn a subject badge to unlock' in panel
        # ?try= puts an unlocked item on in the preview, unsaved; a locked or junk id is ignored
        earn(uid, 'first_lesson_step')
        tried = c.get('/profile?try=hat.mortarboard').get_data(as_text=True).split('id="wardrobe"')[1].split('data-wd-art')[0]
        assert 'zorp-hat--mortarboard' in tried.split('wd-slots')[0] and 'data-wd-id="hat.mortarboard" checked' in tried
        for bad in ('hat.beanie', 'nope', '<script>'):
            part = c.get('/profile?try=' + bad).get_data(as_text=True).split('id="wardrobe"')[1].split('data-wd-art')[0]
            assert 'zorp-hat--' not in part.split('wd-slots')[0], bad
        with app.app_context(), get_db() as conn:
            assert conn.execute('SELECT zorp_outfit_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()[0] == '', 'a try-on stores nothing'


def test_badge_stage_tie_in():
    with app.test_client() as c:
        tok, uid, _h = register(c)
        h = {'Authorization': f'Bearer {tok}', 'Accept': 'application/json'}
        body = c.get('/_t/ward-earn?key=first_lesson_step', headers=h).get_json()
        got = body['new_milestones'][0]
        assert got['key'] == 'first_lesson_step' and got['wardrobe'] == {'id': 'hat.mortarboard', 'name': 'Mortarboard', 'noun': 'the mortarboard'}, got
        # a badge that opens nothing carries no wardrobe field; a second subject badge opens nothing new
        body = c.get('/_t/ward-earn?key=first_quiz', headers=h).get_json()
        assert 'wardrobe' not in body['new_milestones'][0]
        body = c.get('/_t/ward-earn?key=subject_completed:gcse:maths', headers=h).get_json()
        assert body['new_milestones'][0]['wardrobe']['id'] == 'antenna.short'
        body = c.get('/_t/ward-earn?key=subject_ninja:gcse:maths', headers=h).get_json()
        assert 'wardrobe' not in body['new_milestones'][0], 'only the badge that newly opens the item says so'
    js = read('static/js/badge-stage.js')
    assert "wardrobe: 'New in your wardrobe: {item}.'" in js and "tryOn: 'Try it on'" in js
    assert '?try=' in js and '#wardrobe' in js
    assert 'innerHTML' not in js
    line = ward.BY_ID['hat.beanie']['noun']
    assert len('New in your wardrobe: ' + line + '.') <= 80
    assert 'hat.beanie' in ward.BY_ID and len('Try it on') <= 22


def test_lazy_loading_and_wiring():
    for rel in CAPS:
        name = Path(rel).name
        for shared in ('templates/base.html', 'templates/partials/guide.html', 'static/js/sw.js', 'static/js/site.js'):
            assert name not in read(shared), f'{name} is lazy: not in {shared}'
        assert name in read('templates/profile.html'), name
    profile = read('templates/profile.html')
    assert 'partials/wardrobe.html' in profile
    assert re.search(r'wardrobe\.js\'\) }}\?v=\d+" defer', profile)
    assert 'wardrobe' in read('static/js/u4.js'), 'the profile tab script opens the Progress tab for #wardrobe'


def test_caps_and_rules():
    for rel, cap in CAPS.items():
        n = (ROOT / rel).stat().st_size
        assert n <= cap, f'{rel} is {n} bytes, cap {cap}'
    js = read('static/js/wardrobe.js')
    for banned in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'eval(', 'document.write'):
        assert banned not in js, banned
    css = read('static/css/wardrobe.css')
    assert '@keyframes' not in css and 'transition' not in css, 'no animation in the wardrobe style: the preview clip is the rig\'s'
    panel = read('templates/partials/wardrobe.html')
    assert not re.search(r'\son[a-z]+=', panel) and '<script' not in panel and 'style="' not in panel, 'CSP: no inline handlers, scripts or styles'
    assert 'role="status"' in panel and 'aria-live="polite"' in panel


def test_export_and_erase():
    with app.test_client() as c:
        tok, uid, _h = register(c)
        earn(uid, 'first_lesson_step')
        assert patch(c, tok, {'zorp_outfit': {'hat': 'mortarboard'}}).status_code == 200
        with app.app_context(), get_db() as conn:
            payload = build_user_export(conn, uid)
            assert '"hat":"mortarboard"' in payload['settings']['zorp_outfit_json'], 'the account export carries the outfit'
            delete_user_account(conn, uid)
            assert conn.execute('SELECT COUNT(*) FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()[0] == 0, 'erase removes the row, outfit with it'


def test_not_visible_to_others():
    # beanie: no pose badge A has earned draws it, so any beanie on a page can only come from the outfit
    a, b = app.test_client(), app.test_client()   # not context-managed: two preserved contexts would share flask-login's cached user
    tok, uid, handle = register(a)
    earn(uid, 'app_tour')
    session_login(a, uid)
    assert patch(a, tok, {'zorp_outfit': {'hat': 'beanie'}}).status_code == 200
    assert 'zorp-hat--beanie' in a.get('/profile').get_data(as_text=True).split('<aside id="study-buddy"')[1].split('data-buddy-card')[0]
    tok_b, uid_b, _hb = register(b)
    session_login(b, uid_b)
    for url in (f'/u/{handle}', f'/api/v1/users/{handle}'):
        text = b.get(url).get_data(as_text=True)
        assert 'zorp_outfit' not in text and 'zorp-hat--beanie' not in text, url
    mine = b.get('/profile').get_data(as_text=True).split('<aside id="study-buddy"')[1].split('data-buddy-card')[0]
    assert 'zorp-hat--' not in mine, "another pupil's Zorp is not dressed in A's outfit"
    assert 'zorp_outfit' not in read('models/avatar.py'), 'the outfit is not part of the avatar that other pupils see'


def test_voice_items_present():
    items, errors = zorp_voice.extract()
    assert not errors, errors
    paths = {i.path for i in items}
    assert {'static/js/wardrobe.js', 'templates/partials/wardrobe.html', 'models/zorp_wardrobe.py'} <= paths


def main():
    tests = [test_catalogue_shape, test_every_badge_family_unlocks_something, test_server_validation_and_storage,
             test_outfit_renders_and_automatic_look_stays, test_panel_on_profile, test_badge_stage_tie_in,
             test_lazy_loading_and_wiring, test_caps_and_rules, test_export_and_erase, test_not_visible_to_others,
             test_voice_items_present]
    for t in tests:
        t()
    print('Wardrobe smoke (E10 phase 6b) passed.')


if __name__ == '__main__':
    main()
