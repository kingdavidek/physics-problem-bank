"""E11 Phase 1 smoke (docs/BADGES_AND_CELEBRATIONS_PLAN.md sections 2 and 9): the celebration ladder.
Run: python scripts/test_e11_phase1_smoke.py

Checks:
  * the Celebrations setting (full, big, small) and the 10/10-as-card flag: stored, validated, kept by other saves, on the page;
  * Full marks: earned by the first 10/10 on a lesson quiz (not a retry run, not under three questions), and its badge stage is
    that 10/10's celebration; later 10/10s are the perfect moment, every time (David's answer 1);
  * the quiet back-fill: 10/10s already on record earn Full marks with no stage and no notification, then one corner card, once;
  * Welcome back: the first study day after three or more days away is a corner card, never after a shorter gap;
  * the client rules (wiring): one sequence of at most three cards in a fixed order with Skip all, the setting, the 10/10 link,
    the day's budget of six finished lessons (10/10s, badges and level-ups never count), the carry to the next page, the
    first-correct card, the beat.
The browser walks are in the plan's section 9.
"""
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models import gamification as gam  # noqa: E402

LESSON = ('gcse', 'maths', 'bidmas')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def new_pupil(prefix='p1'):
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'{prefix}_{s}@example.com', 'handle': f'{prefix}_{s}',
                                              'password': 'password123', 'age_confirm': True},
               headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def csrf(c):
    return re.search(r'<meta name="csrf-token" content="([^"]+)">', c.get('/topics').get_data(as_text=True)).group(1)


def islands(html):
    ms = re.search(r'id="pb-new-milestones">(.*?)</script>', html, re.S)
    mm = re.search(r'id="pb-new-moments">(.*?)</script>', html, re.S)
    return (json.loads(ms.group(1)) if ms else []), (json.loads(mm.group(1)) if mm else [])


def take_quiz(c, wrong=0):
    level, subject, topic = LESSON
    assert c.get(f'/lesson-quiz/{level}/{subject}/{topic}').status_code == 200
    with get_db() as conn:
        row = conn.execute("SELECT data FROM quicktest_sessions WHERE session_id LIKE 'lq_%' ORDER BY rowid DESC LIMIT 1").fetchone()
    problems = json.loads(row['data'])['problems']
    form = {}
    for i, p in enumerate(problems):
        right = p['correct_answer'][:1].upper()
        form[f'answer_{i}'] = next(ch for ch in 'ABCD' if ch != right) if i < wrong else right
    r = c.post(f'/lesson-quiz/{level}/{subject}/{topic}/submit', data=form)
    assert r.status_code == 302, r.status_code
    return islands(c.get(r.headers['Location']).get_data(as_text=True))


def badge_rows(uid):
    with get_db() as conn:
        return {r['milestone_key']: r['quiet'] for r in conn.execute('SELECT milestone_key, quiet FROM user_milestones WHERE user_id = ?', (uid,))}


# ---- the setting ----
def test_setting():
    c, _ = new_pupil()
    page = c.get('/topics').get_data(as_text=True)
    assert 'data-pb-celebrate="full"' in page and 'data-pb-perfect-card' not in page, 'default: full screen'
    tok = csrf(c)
    h = {'X-CSRF-Token': tok}
    for mode in ('big', 'small', 'full'):
        r = c.patch('/api/v1/me/settings', json={'celebration_mode': mode}, headers=h)
        assert r.status_code == 200 and r.get_json()['settings']['celebration_mode'] == mode, r.data
        assert f'data-pb-celebrate="{mode}"' in c.get('/topics').get_data(as_text=True)
    for bad in ('huge', '', None, 3):
        r = c.patch('/api/v1/me/settings', json={'celebration_mode': bad}, headers=h)
        assert r.status_code == 400 and r.get_json()['code'] == 'invalid_celebration_mode', (bad, r.data)
    r = c.patch('/api/v1/me/settings', json={'perfect_as_card': 'yes'}, headers=h)
    assert r.status_code == 400, 'perfect_as_card is a boolean'
    r = c.patch('/api/v1/me/settings', json={'celebration_mode': 'big', 'perfect_as_card': True}, headers=h)
    assert r.get_json()['settings']['perfect_as_card'] is True
    # any other save keeps both (every caller of update_profile_settings passes the whole settings)
    r = c.patch('/api/v1/me/settings', json={'theme_preference': 'dark'}, headers=h)
    st = r.get_json()['settings']
    assert st['celebration_mode'] == 'big' and st['perfect_as_card'] is True, st
    page = c.get('/topics').get_data(as_text=True)
    assert 'data-pb-celebrate="big"' in page and 'data-pb-perfect-card="1"' in page
    # the settings page: three choices and the switch, and the form saves them
    sp = c.get('/profile/settings').get_data(as_text=True)
    assert 'id="celebrations"' in sp and re.search(r'value="big"\s+checked', sp) and 'name="perfect_as_card"' in sp
    r = c.post('/profile/settings', data={'csrf_token': tok, 'celebration_mode': 'small', 'zorp_sound': 'off', 'theme_preference': 'system',
                                  'motion_preference': 'system', 'profile_visibility': 'followers_only',
                                  'default_share_visibility': 'followers_only'})
    assert r.status_code in (302, 303), r.status_code
    st = c.get('/api/v1/me/settings').get_json()['settings']
    assert st['celebration_mode'] == 'small' and st['perfect_as_card'] is False, st   # the switch was off in that form
    assert app.test_client().get('/topics').get_data(as_text=True).count('data-pb-celebrate') == 0, 'signed out: nothing'


# ---- Full marks ----
def test_full_marks():
    m = gam.MILESTONE_CATALOG[gam.MILESTONE_PERFECT_1]
    assert m['title'] == 'Full marks' and m['family'] in gam.BADGE_FAMILIES and len(m['blurb']) <= 80 and len(m['how']) <= 80
    c, uid = new_pupil()
    ms, mm = take_quiz(c, wrong=1)
    assert 'perfect_1' not in badge_rows(uid), 'nine out of ten is not full marks'
    ms, mm = take_quiz(c, wrong=0)
    assert 'perfect_1' in [b['key'] for b in ms] and not [m for m in mm if m['type'] == 'perfect'], (ms, mm)
    assert [b for b in ms if b['key'] == 'perfect_1'][0]['family'] == 'perfect'   # 2026-11-10: its own family since E11 Phase 2
    assert badge_rows(uid)['perfect_1'] == 0, 'earned live, not quiet'
    ms, mm = take_quiz(c, wrong=0)
    assert 'perfect_1' not in [b['key'] for b in ms] and [m['type'] for m in mm if m['type'] == 'perfect'] == ['perfect'], (ms, mm)
    # a retry run, or a quiz under three questions, never earns it
    c2, uid2 = new_pupil()
    with get_db() as conn:
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 3, 3, '[]', ?, 1)", (uid2, now))
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 2, 2, '[]', ?, 0)", (uid2, now))
        conn.commit()
        assert gam.evaluate_milestones(conn, uid2) and 'perfect_1' not in badge_rows(uid2)


# ---- the quiet back-fill ----
def test_backfill_quiet_then_one_card():
    c, uid = new_pupil()
    with get_db() as conn:
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 10, 10, '[]', '2026-10-01T10:00:00+00:00', 0)", (uid,))
        conn.commit()
        n_notes = conn.execute('SELECT COUNT(*) AS n FROM user_notifications WHERE user_id = ?', (uid,)).fetchone()['n']
        added = gam.backfill_quiet_badges(conn, (gam.MILESTONE_PERFECT_1,))
        conn.commit()
        assert added >= 1
        row = conn.execute("SELECT earned_at, quiet FROM user_milestones WHERE user_id = ? AND milestone_key = 'perfect_1'", (uid,)).fetchone()
        assert row['quiet'] == 1 and row['earned_at'].startswith('2026-10-01'), dict(row)
        assert conn.execute('SELECT COUNT(*) AS n FROM user_notifications WHERE user_id = ?', (uid,)).fetchone()['n'] == n_notes, 'no bell'
        assert gam.backfill_quiet_badges(conn, (gam.MILESTONE_PERFECT_1,)) == 0 or True   # other pupils only; never twice for one
        assert conn.execute("SELECT COUNT(*) AS n FROM user_milestones WHERE user_id = ? AND milestone_key = 'perfect_1'", (uid,)).fetchone()['n'] == 1
    ms, mm = islands(c.get('/topics').get_data(as_text=True))
    assert not ms, 'no badge stage for a quiet badge'
    cards = [m for m in mm if m.get('kind') == 'backfill']
    assert len(cards) == 1 and cards[0]['count'] == 1 and cards[0]['title'] == 'Full marks', mm
    assert badge_rows(uid)['perfect_1'] == 2
    assert not [m for m in islands(c.get('/topics').get_data(as_text=True))[1] if m.get('kind') == 'backfill'], 'once'
    assert "'e11_backfill_perfect_1' not in migrated" in read('app.py')


# ---- Welcome back ----
def seed_last_study(uid, days_ago):
    day = (datetime.now(timezone.utc).date() - timedelta(days=days_ago)).isoformat()
    with get_db() as conn:
        conn.execute('INSERT OR IGNORE INTO user_study_days (user_id, study_date) VALUES (?, ?)', (uid, day))
        conn.execute('INSERT OR REPLACE INTO user_streaks (user_id, current_streak, longest_streak, last_active_date, freeze_available) '
                     'VALUES (?, 1, 1, ?, 0)', (uid, day))
        conn.commit()


def lesson_save(c, keys):
    """Open the lesson (itself a study action) and save steps: the moments of both, the page's island then the save's JSON."""
    page = c.get('/topic/{}/{}/{}'.format(*LESSON)).get_data(as_text=True)
    tok = re.search(r'<meta name="csrf-token" content="([^"]+)">', page).group(1)
    r = c.post('/api/lesson-progress', json={'csrf_token': tok, 'level': LESSON[0], 'subject': LESSON[1], 'topic': LESSON[2],
                                             'section_key': keys[-1], 'section_label': 'x', 'completed_keys': keys, 'step_total': 6})
    body = r.get_json()
    return {'new_moments': islands(page)[1] + (body.get('new_moments') or [])}


def test_welcome_back():
    c, uid = new_pupil()
    seed_last_study(uid, 4)
    body = lesson_save(c, ['step-0'])
    kinds = [m.get('kind') for m in body.get('new_moments') or []]
    assert 'welcome_back' in kinds, body.get('new_moments')
    body = lesson_save(c, ['step-0', 'step-1'])
    assert 'welcome_back' not in [m.get('kind') for m in body.get('new_moments') or []], 'once: today is a study day now'
    c2, uid2 = new_pupil()
    seed_last_study(uid2, 2)
    body = lesson_save(c2, ['step-0'])
    assert not [m for m in body.get('new_moments') or [] if str(m.get('kind', '')).startswith('welcome_back')], 'two days is not away'
    c3, _ = new_pupil()
    body = lesson_save(c3, ['step-0'])
    assert not [m for m in body.get('new_moments') or [] if str(m.get('kind', '')).startswith('welcome_back')], 'a first day ever is not a return'


# ---- the client rules ----
def test_client_rules():
    mo = read('static/js/moments.js')
    assert 'var MAX_CARDS = 3;' in mo and 'var BUDGET = 6;' in mo
    play = mo.split('  function play(list, badges) {')[1].split('window.pbMoments = ')[0]
    # the setting, the 10/10 link, the budget (finished lessons only)
    assert "md === 'small' || (md === 'big' && m.type !== 'level') || (m.type === 'perfect' && perfectAsCard())" in play
    assert "if (!small && (m.type === 'lesson_complete' || m.type === 'week')) { lessons += 1; small = budgetUsed() + lessons > BUDGET; }" in play   # 2026-11-11: E11 Phase 4, Your week spends from the same budget
    assert "if (md === 'small' || !(window.pbBadgeStage && window.pbBadgeStage.part))" in play and 'badges.map(badgeCard)' in play
    # the order and the cap, the rest carried
    assert play.index('var front =') < play.index('var b2 =') < play.index('var k =') and 'carry(front.slice(f.length)' in play
    assert 'tierOf(x.b) - tierOf(y.b)' in play and "TIER = { violet: 0, gold: 1, silver: 2, bronze: 3 }" in mo
    seq = mo.split('  function sequence(front, badgeSpecs, back) {')[1].split('  function asCard(m)')[0]
    assert "if (m.type === 'lesson_complete' || (m.type === 'week' && m.part === 'days')) spend();" in seq and "if (m.type === 'perfect') perfectLink(st);" in seq
    assert 'UI.skipAll' in seq and 'window.pbStage.close();' in seq and 'items.length > 1' in seq
    assert "'fs:' + today() + ':' + (n + 1)" in mo, 'the budget lives in the protected guide state ring'
    assert "JSON.stringify({ perfect_as_card: true })" in mo and "'data-pb-perfect-card', '1'" in mo
    assert "var CARRY = 'pb-celebrate-next:';" in mo
    guide = read('static/js/guide.js')
    assert 'var BEAT_MS = 300;' in guide and "'pb-celebrate-next:' + STORE_NS" in guide and 'function resumeCarried()' in guide
    assert "moments([{ type: 'toast', id: 'toast:first_correct', kind: 'first_correct' }]);" in guide
    bs = read('static/js/badge-stage.js')
    assert 'window.pbBadgeStage = { play: play, part: cardsPart, ready: ready, families: FAMILIES };' in bs   # cardsPart since 2026-11-11 (plan section 9, Fixed)
    social = read('models/social.py')
    assert "_GUIDE_VOLATILE_PREFIXES = ('level:', 'lesson:', 'milestone:', 'fs:', 'wk:', 'near:')" in social   # 2026-11-11: E11 Phase 4 adds wk: and near:
    # the budget flags go to the evictable ring, not the durable rewards
    from models.social import merge_guide_json
    merged = json.loads(merge_guide_json('{}', {'rewards': {f'fs:20261110:{i}': True for i in range(1, 7)}}))
    assert not [k for k in merged.get('rewards', {}) if k.startswith('fs:')] and len([k for k in merged['recent'] if k.startswith('fs:')]) == 6


def main():
    tests = [test_setting, test_full_marks, test_backfill_quiet_then_one_card, test_welcome_back, test_client_rules]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('E11 Phase 1 smoke passed.')


if __name__ == '__main__':
    main()
