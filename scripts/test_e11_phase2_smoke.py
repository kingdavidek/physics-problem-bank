"""E11 Phase 2 smoke (docs/BADGES_AND_CELEBRATIONS_PLAN.md sections 3 and 10): the new badges.
Run: python scripts/test_e11_phase2_smoke.py

Checks:
  * the catalogue: every new badge, its family, its copy and the next step of every line;
  * the rules against seeded history (quizzes, perfect quizzes, a cleared retry, questions answered right, streaks, the daily
    question, topics, set work);
  * the Recovery line through the real check routes: a right answer after a wrong try, and after the bigger hint, once per
    question; an MCQ retry after "Try again" is checked but never recorded as an attempt; Quick Test and lesson quizzes are out;
  * the quiet back-fill of everything history earns, with one corner card;
  * the two new families and hats (crown, sprout) on the badge stage, the live rig and the wardrobe;
  * set-work badges on the shelf only for pupils in a class; the client wiring.
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
from models import zorp_kit, zorp_wardrobe as ward  # noqa: E402

HDR = {'Accept': 'application/json'}
NEW = ('quizzes_5', 'quizzes_25', 'perfect_5', 'perfect_20', 'bounce_1', 'bounce_25', 'hint_1', 'hint_25', 'retry_fixed',
       'questions_250', 'streak_3', 'streak_100', 'qotd_30', 'topics_3', 'topics_25', 'setwork_1', 'setwork_10')


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def new_pupil(prefix='p2'):
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'{prefix}_{s}@example.com', 'handle': f'{prefix}_{s}',
                                              'password': 'password123', 'age_confirm': True}, headers=HDR)
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def keys(uid):
    with get_db() as conn:
        return {r['milestone_key']: r['quiet'] for r in conn.execute('SELECT milestone_key, quiet FROM user_milestones WHERE user_id = ?', (uid,))}


def events(uid, kind):
    with get_db() as conn:
        return conn.execute('SELECT COUNT(*) AS n FROM user_activity_events WHERE user_id = ? AND event_type = ?', (uid, kind)).fetchone()['n']


def now(days=0):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


# ---- the catalogue ----
def test_catalogue():
    cat = gam.MILESTONE_CATALOG
    for k in NEW:
        m = cat[k]
        assert m['family'] in gam.BADGE_FAMILIES and len(m['blurb']) <= 80 and len(m['how']) <= 80, k
    assert 'habit' not in json.dumps([cat[k]['title'] for k in cat]).lower(), 'no habit framing (voice rules)'
    lines = [('first_quiz', 'quizzes_5', 'quizzes_25'), ('perfect_1', 'perfect_5', 'perfect_20'), ('bounce_1', 'bounce_25'),
             ('hint_1', 'hint_25'), ('questions_25', 'questions_50', 'questions_250'), ('streak_3', 'streak_7', 'streak_30', 'streak_100'),
             ('qotd_first', 'qotd_7', 'qotd_30'), ('topics_3', 'topics_10', 'topics_25'), ('setwork_1', 'setwork_10'),
             ('first_lesson_step', 'topics_completed_5')]
    for line in lines:
        for a, b in zip(line, line[1:]):
            assert cat[a]['next'] == b, (a, cat[a]['next'], b)
        assert cat[line[-1]]['next'] in (None, 'topics_completed_10'), line[-1]
    assert cat['perfect_1']['family'] == cat['perfect_5']['family'] == 'perfect' and cat['bounce_1']['family'] == 'growth'
    assert cat['questions_50']['how'] == 'Get 100 practice questions right.', 'answered right now (David, answer 4)'
    assert cat['setwork_1'].get('class_only') and cat['setwork_10'].get('class_only')
    assert len(cat) == 56


# ---- the rules ----
def test_rules_from_history():
    _, uid = new_pupil()
    with get_db() as conn:
        conn.execute('PRAGMA foreign_keys = OFF')
        q = ("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
             "VALUES (?, 'gcse', 'maths', 'bidmas', ?, 10, '[]', ?, ?)")
        for i in range(4):
            conn.execute(q, (uid, 7, now(), 0))
        conn.commit()
        assert 'quizzes_5' not in gam.evaluate_milestones(conn, uid)
        conn.execute(q, (uid, 10, now(), 0))
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 3, 3, '[]', ?, 1)", (uid, now()))
        conn.commit()
        got = gam.evaluate_milestones(conn, uid)
        assert {'quizzes_5', 'perfect_1', 'retry_fixed'} <= set(got) and 'perfect_5' not in got, got
        for _ in range(4):
            conn.execute(q, (uid, 10, now(), 0))
        conn.commit()
        assert 'perfect_5' in gam.evaluate_milestones(conn, uid)
        a = ("INSERT INTO generator_mcq_attempts (user_id, level, subject, topic, mode, difficulty, user_answer, correct_answer, "
             "correct, created_at, part_index) VALUES (?, 'gcse', 'maths', 'bidmas', 'mcq', 'foundational', 'A', 'A', ?, ?, ?)")
        conn.executemany(a, [(uid, 1, now(), 0)] * 30)       # parts of multi-part questions do not count one by one
        conn.executemany(a, [(uid, 0, now(), None)] * 30)    # wrong answers do not count
        conn.commit()
        assert 'questions_25' not in gam.evaluate_milestones(conn, uid)
        conn.executemany(a, [(uid, 1, now(), None)] * 250)
        conn.commit()
        assert {'questions_25', 'questions_50', 'questions_250'} <= set(gam.evaluate_milestones(conn, uid))
        conn.execute('INSERT OR REPLACE INTO user_streaks (user_id, current_streak, longest_streak, last_active_date, freeze_available) '
                     'VALUES (?, 3, 100, ?, 0)', (uid, now()[:10]))
        for d in range(30):
            conn.execute("INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at) VALUES (?, ?, 1, 'A', ?)",
                         (uid, (datetime.now(timezone.utc).date() - timedelta(days=d)).isoformat(), now()))
        for i in range(25):
            conn.execute("INSERT INTO user_activity_events (user_id, event_type, payload_json, visibility, created_at) "
                         "VALUES (?, 'topic_opened', ?, 'private', ?)",
                         (uid, json.dumps({'level': 'gcse', 'subject': 'maths', 'topic': f't{i}'}), now()))
        for i in range(10):
            conn.execute("INSERT INTO class_assignment_recipients (assignment_id, student_id, status, completed_at) "
                         "VALUES (?, ?, 'complete', ?)", (900000 + i, uid, now()))
        conn.commit()
        got = set(gam.evaluate_milestones(conn, uid))
        assert {'streak_3', 'streak_7', 'streak_30', 'streak_100', 'qotd_30', 'topics_3', 'topics_10', 'topics_25',
                'setwork_1', 'setwork_10'} <= got, got
        assert gam.evaluate_milestones(conn, uid) == [], 'each badge once'


# ---- the Recovery line through the real routes ----
STRAIGHT = {'question': 'Two angles lie on a straight line. One angle is 41°. Find the other angle.',
            'correct_answer_raw': '139', 'answer_type': 'number', 'solution': '180 − 41 = <strong>139</strong>°',
            'hint': 'Angles on a straight line add up to 180°.', 'marks': 1}


def bind(c, problem, topic='geometry_angles', mode='standard', source=None):
    with c.session_transaction() as sess:
        p = {'level': 'gcse', 'subject': 'maths', 'topic': topic, 'mode': mode, 'difficulty': 'foundational', 'problem': dict(problem)}
        if source:
            p['source'] = source
        sess['last_problem_payload'] = p


def check(c, answer, **extra):
    return c.post('/api/v1/problems/check', json=dict({'user_answer': answer, 'hint_ladder': True}, **extra), headers=HDR).get_json()


def test_recovery_typed():
    c, uid = new_pupil()
    bind(c, STRAIGHT)
    assert check(c, '139')['correct'] and events(uid, 'retry_correct') == 0, 'right first time is not a recovery'
    bind(c, STRAIGHT)
    wrong = check(c, '41')
    assert not wrong['correct'] and (wrong.get('hint') or {}).get('rung') == 1, wrong
    right = check(c, '139', bigger_hint=True)
    assert right['correct'] and events(uid, 'retry_correct') == 1 and events(uid, 'hint_correct') == 1
    got = [m['key'] for m in right.get('new_milestones') or []]
    assert {'bounce_1', 'hint_1'} <= set(got), got
    lines = [m.get('wardrobe') for m in right['new_milestones'] if m['key'] in ('bounce_1', 'hint_1')]
    assert [w['id'] for w in lines if w] == ['hat.sprout'], ('one of the pair opens the sprout, once', lines)
    check(c, '139', bigger_hint=True)
    assert events(uid, 'retry_correct') == 1 and events(uid, 'hint_correct') == 1, 'once per question'
    # a wrong try then right without opening the bigger hint: Bounce back only
    bind(c, STRAIGHT)
    check(c, '41')
    check(c, '139')
    assert events(uid, 'retry_correct') == 2 and events(uid, 'hint_correct') == 1
    # Show answer opened (the page says answer_seen): the question earns nothing, even with a wrong try and the bigger hint before
    bind(c, STRAIGHT)
    check(c, '41')
    check(c, '139', bigger_hint=True, answer_seen=True)
    check(c, '139', bigger_hint=True)
    assert events(uid, 'retry_correct') == 2 and events(uid, 'hint_correct') == 1, 'an answer seen closes the question'
    # the bigger hint claimed on a question the server sent no hint for counts for nothing
    plain = dict(STRAIGHT, hint='')
    bind(c, plain, topic='bidmas', mode='standard')
    c.post('/api/v1/problems/check', json={'user_answer': '1'}, headers=HDR)   # no ladder asked: no hint sent
    check(c, '139', bigger_hint=True)
    assert events(uid, 'hint_correct') == 1
    with get_db() as conn:
        ev = conn.execute("SELECT payload_json, visibility FROM user_activity_events WHERE user_id = ? AND event_type = 'retry_correct'", (uid,)).fetchall()
    assert all(r['visibility'] == 'private' for r in ev), 'private, never in a feed'
    assert all(set(json.loads(r['payload_json'])) == {'level', 'subject', 'topic'} for r in ev)
    n_before = events(uid, 'retry_correct')
    for kw in ({'source': 'quicktest'}, {'mode': 'lesson'}):
        bind(c, STRAIGHT, **kw)
        check(c, '41')
        check(c, '139', bigger_hint=True)
    assert events(uid, 'retry_correct') == n_before and events(uid, 'hint_correct') == 1, 'Quick Test and lesson quizzes never count'


def test_recovery_mcq_retry():
    c, uid = new_pupil()
    mcq = {'question': 'Pick B.', 'options': ['A) 1', 'B) 2', 'C) 3', 'D) 4'], 'correct_answer': 'B'}
    bind(c, mcq, topic='bidmas')
    with get_db() as conn:
        before = conn.execute('SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ?', (uid,)).fetchone()['n']
    body = {'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas', 'user_answer': 'A'}
    assert c.post('/api/v1/generator/mcq-answer', json=body, headers=HDR).get_json()['correct'] is False
    r = c.post('/api/v1/generator/mcq-answer', json=dict(body, user_answer='B', retry=True), headers=HDR).get_json()
    assert r['correct'] is True and 'attempt_id' not in r, r
    with get_db() as conn:
        after = conn.execute('SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ?', (uid,)).fetchone()['n']
    assert after == before + 1, 'the retry is checked but never recorded as an attempt (the first answer stays in the stats)'
    assert events(uid, 'retry_correct') == 1 and 'bounce_1' in keys(uid)
    bind(c, mcq, topic='bidmas')
    c.post('/api/v1/generator/mcq-answer', json=body, headers=HDR)
    c.post('/api/v1/generator/mcq-answer', json=dict(body, user_answer='B', retry=True, answer_seen=True), headers=HDR)
    assert events(uid, 'retry_correct') == 1, 'Show answer opened before the retry: nothing'


# ---- the quiet back-fill ----
def test_backfill_phase2():
    c, uid = new_pupil()
    with get_db() as conn:
        for i in range(6):
            conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                         "VALUES (?, 'gcse', 'maths', 'bidmas', 6, 10, '[]', ?, 0)", (uid, now(5)))
        conn.execute('INSERT OR REPLACE INTO user_streaks (user_id, current_streak, longest_streak, last_active_date, freeze_available) '
                     'VALUES (?, 0, 4, ?, 0)', (uid, now(5)[:10]))
        conn.commit()
        n = gam.backfill_quiet_badges(conn, gam.PHASE2_BACKFILL_KEYS)
        conn.commit()
        assert n >= 2
    k = keys(uid)
    assert k.get('quizzes_5') == 1 and k.get('streak_3') == 1 and 'quizzes_25' not in k and 'bounce_1' not in k, k
    cards = [m for m in json.loads(re.search(r'id="pb-new-moments">(.*?)</script>', c.get('/topics').get_data(as_text=True), re.S).group(1))
             if m.get('kind') == 'backfill']
    assert len(cards) == 1 and cards[0]['count'] == 2, cards
    assert "'e11_backfill_phase2' not in migrated" in read('app.py') and 'backfill_quiet_badges(conn, PHASE2_BACKFILL_KEYS)' in read('app.py')
    assert set(gam.PHASE2_BACKFILL_KEYS) == set(NEW) - {'bounce_1', 'bounce_25', 'hint_1', 'hint_25'} | {'questions_25', 'questions_50'}


# ---- families, hats, wardrobe ----
def test_families_and_hats():
    bs = read('static/js/badge-stage.js')
    block = bs.split('// BEGIN FAMILIES')[1].split('// END FAMILIES')[0]
    assert '    perfect: {' in block and '    growth: {' in block and "fx: 'sprout'" in block
    assert 'var DRAW = {' in bs and "part(fam.prop) || (DRAW[fam.fx] ? DRAW[fam.fx]() : null)" in bs
    assert "if (key === 'streak_100') card.ids.push('streak:100');" in bs
    assert {'crown', 'sprout'} <= set(zorp_kit.LOOK_HATS) and 'toque' not in zorp_kit.LOOK_HATS
    with app.app_context():
        mod = app.jinja_env.get_template('partials/zorp_overlays.html').module
        for name in ('crown', 'sprout'):
            out = str(mod.zorp_hat(name, 32, 14.5))
            assert out.startswith(f'<g class="zorp-hat zorp-hat--{name}"') and out.count('<g') == 1, out[:80]
    items = {i['value']: i for i in ward.ITEMS if i['slot'] == 'hat'}
    assert items['crown']['unlock'] == ('family', 'perfect', 'a full marks badge')
    assert items['sprout']['unlock'] == ('family', 'growth', 'a recovery badge')


# ---- the shelf ----
def test_class_only_on_the_shelf():
    _, uid = new_pupil()
    with get_db() as conn:
        shelf = {i['key'] for i in gam.list_milestone_shelf(conn, uid)}
        assert 'setwork_1' not in shelf and 'quizzes_5' in shelf, 'not in a class: no set-work badges'
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.execute("INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'setwork_1', ?)", (uid, now()))
        conn.commit()
        shelf = {i['key'] for i in gam.list_milestone_shelf(conn, uid)}
        assert 'setwork_1' in shelf and 'setwork_10' not in shelf, 'an earned one always shows'


# ---- the client ----
def test_client_wiring():
    js = read('static/js/site.js')
    assert js.count("if (block.dataset.hintRung === '2') body.bigger_hint = true;") == 3
    assert "user_answer: letter, retry: true, answer_seen: answerSeen() || undefined" in js
    assert js.count("      if (answerSeen()) body.answer_seen = true;\n") == 3
    assert "if (details.open) details.setAttribute('data-seen', '1');" in js
    mo = read('static/js/moments.js')
    assert "if (key === 'streak_100') g.markReward('streak:100');" in mo


def test_no_shadowed_functions():
    """2026-11-11: E11 Phase 1 added a second `function part` to badge-stage.js; the later declaration replaced part(id), so every
    badge stage played with no medal and no prop. No script may declare one name twice in its top scope."""
    for rel in ('static/js/badge-stage.js', 'static/js/moments.js', 'static/js/guide.js', 'static/js/celebrate.js',
                'static/js/zorp-stage.js', 'static/js/story-chapters.js', 'static/js/zorp-tour.js', 'static/js/zorp-coach.js',
                'static/js/site.js'):
        names = re.findall(r'^  function (\w+)\s*\(', read(rel), re.M)
        dupes = sorted({n for n in names if names.count(n) > 1})
        assert not dupes, (rel, dupes)
    bs = read('static/js/badge-stage.js')
    assert 'function cardsPart(specs)' in bs and 'part: cardsPart' in bs and bs.count('function part(') == 1


def main():
    tests = [test_catalogue, test_rules_from_history, test_recovery_typed, test_recovery_mcq_retry, test_backfill_phase2,
             test_families_and_hats, test_class_only_on_the_shelf, test_client_wiring, test_no_shadowed_functions]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('E11 Phase 2 smoke passed.')


if __name__ == '__main__':
    main()
