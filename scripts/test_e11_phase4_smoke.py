"""E11 Phase 4 smoke (docs/BADGES_AND_CELEBRATIONS_PLAN.md 4.2 to 4.4, 2.1, 2.2 and section 12): progress around the site.
Run: python scripts/test_e11_phase4_smoke.py

Checks:
  * Quick Tests are marked (is_quicktest, old rows back-filled from their answers) and never count for the Full marks line; a
    perfect Quick Test gets its own "Full marks" card;
  * the mastery path's next step for every state, and the path of a real topic;
  * the results strip right after a lesson quiz (the level bar from before to after, the chips, the next step), and only then;
  * Close to a badge: one or two steps from the Next up badge, once a day, never beside a new badge;
  * Your week: last week's days, questions right and best moment; offered on a page until its flag is saved, never twice;
  * the Today numbers on the Practice and Profile pages; the lesson page's path data and the quiz bar line;
  * the client (moments.js, lesson-progress.js), the copy lint, the restored quiz bar selector, versions and caps.
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
from models import progress_bits as pb  # noqa: E402
from models import social  # noqa: E402
from models import zorp_voice as voice  # noqa: E402
from models.user_data import record_quiz_attempt  # noqa: E402

HDR = {'Accept': 'application/json'}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def new_pupil(prefix='p4'):
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


def iso(d, hour=10):
    return f'{d.isoformat()}T{hour:02d}:00:00+00:00'


def moments_of(html):
    m = re.search(r'id="pb-new-moments">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else []


def set_guide(uid, rewards, origin=True):
    with get_db() as conn:
        raw = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()
        merged = social.merge_guide_json(raw['guide_json'] if raw else None, {'origin': origin, 'tours': {'app': True}, 'rewards': rewards})
        conn.execute('UPDATE user_profile_settings SET guide_json = ? WHERE user_id = ?', (merged, uid))
        conn.commit()


# ---- Quick Tests and the Full marks line ------------------------------------------------------------------------------
def test_quick_tests_are_not_lesson_quizzes():
    _, uid = new_pupil()
    with get_db() as conn:
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 5, 5, [{'user_answer': 'A', 'correct': True}] * 5, [], is_quicktest=True)
        assert conn.execute('SELECT is_quicktest FROM quiz_attempts WHERE user_id = ?', (uid,)).fetchone()['is_quicktest'] == 1
        assert 'perfect_1' not in gam.evaluate_milestones(conn, uid), 'a perfect Quick Test is not Full marks'
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 10, 10, ['A'] * 10, [])
        assert 'perfect_1' in gam.evaluate_milestones(conn, uid), 'a perfect lesson quiz is'
    src = read('app.py')
    assert "conn.execute(\"UPDATE quiz_attempts SET is_quicktest = 1 WHERE answers_json LIKE '[{%'\")" in src
    assert "is_quicktest=True," in src and "kind='quicktest_perfect' if done else 'quicktest_done'" in src
    assert gam._PERFECT_QUIZ_WHERE.startswith('is_retry = 0 AND is_quicktest = 0')
    # the back-fill rule tells them apart by the shape of the answers
    with get_db() as conn:
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 3, 3, '[{\"user_answer\": \"A\"}]', ?, 0)", (uid, iso(datetime.now(timezone.utc).date())))
        conn.execute("UPDATE quiz_attempts SET is_quicktest = 1 WHERE user_id = ? AND answers_json LIKE '[{%'", (uid,))
        rows = conn.execute('SELECT answers_json, is_quicktest FROM quiz_attempts WHERE user_id = ?', (uid,)).fetchall()
        assert all((r['answers_json'].startswith('[{')) == bool(r['is_quicktest']) for r in rows)


def test_quick_test_full_marks_card():
    from flask import g
    from flask_login import login_user
    import app as appmod
    _, uid = new_pupil()
    user = appmod.load_user(uid)
    for score, kind in ((12, 'quicktest_perfect'), (9, 'quicktest_done')):
        with app.test_request_context('/quicktest/results'):
            login_user(user)
            appmod._note_quiz_finished(uid, 'gcse', 'maths', 'bidmas', score, 12, 900 + score, wrong=12 - score, kind='quicktest')
            noted = getattr(g, 'pb_new_moments', [])
            assert [m['kind'] for m in noted] == [kind], noted
            assert not [m for m in noted if m['type'] == 'perfect'], 'never the lesson quiz full screen'


def test_quick_tests_make_no_ninja():
    """2026-11-12, David's decision (plan section 12): a Quick Test neither makes a ninja or a master nor breaks a run of 10/10s.
    A topic badge already earned that way is kept, and the mastery path counts it."""
    from models.topic_status import topic_status_map
    _, uid = new_pupil()
    with get_db() as conn:
        conn.execute("INSERT INTO lesson_progress (user_id, level, subject, topic, section_key, section_label, updated_at, "
                     "completed_keys_json, step_total) VALUES (?, 'gcse', 'maths', 'bidmas', 'step-1', '', ?, ?, 2)",
                     (uid, iso(datetime.now(timezone.utc).date()), json.dumps(['step-1', 'step-2'])))
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 10, 10, [{'user_answer': 'A'}] * 10, [], is_quicktest=True)
        st = topic_status_map(conn, uid)[('gcse', 'maths', 'bidmas')]
        assert st['lesson_complete'] and not st['ninja'], 'a perfect Quick Test is not a ninja'
        assert 'topic_ninja:gcse:maths:bidmas' not in gam.evaluate_milestones(conn, uid)
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 10, 10, ['A'] * 10, [])
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 4, 10, [{'user_answer': 'A'}] * 10, [], is_quicktest=True)
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 10, 10, ['A'] * 10, [])
        st = topic_status_map(conn, uid)[('gcse', 'maths', 'bidmas')]
        assert st['ninja'] and st['master_ever'], 'a Quick Test between two 10/10s does not break the run'
        got = gam.evaluate_milestones(conn, uid)
        assert {'topic_ninja:gcse:maths:bidmas', 'topic_master:gcse:maths:bidmas'} <= set(got), got
    # a ninja earned through a Quick Test before the change: the badge stays and the path shows it
    _, uid2 = new_pupil()
    with get_db() as conn:
        conn.execute("INSERT INTO lesson_progress (user_id, level, subject, topic, section_key, section_label, updated_at, "
                     "completed_keys_json, step_total) VALUES (?, 'gcse', 'maths', 'bidmas', 'step-1', '', ?, ?, 2)",
                     (uid2, iso(datetime.now(timezone.utc).date()), json.dumps(['step-1', 'step-2'])))
        record_quiz_attempt(conn, uid2, 'gcse', 'maths', 'bidmas', 10, 10, [{'user_answer': 'A'}] * 10, [], is_quicktest=True)
        conn.execute("INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'topic_ninja:gcse:maths:bidmas', ?)",
                     (uid2, iso(datetime.now(timezone.utc).date())))
        conn.commit()
        p = pb.path(conn, uid2, 'gcse', 'maths', 'bidmas')
        assert [s['done'] for s in p['steps']] == [True, True, False] and p['next'] == pb.NEXT['master_two'], p
    assert "not_quick = ' AND is_quicktest = 0' if 'is_quicktest' in quiz_cols else ''" in read('models/topic_status.py')


# ---- the mastery path -------------------------------------------------------------------------------------------------
def test_next_step_for_every_state():
    ns = pb.next_step
    assert ns(None) == pb.NEXT['lesson'] and ns({'has_perfect': True}) == pb.NEXT['lesson_ninja']
    assert ns({'lesson_complete': True}) == 'A 10/10 on the quiz makes you a ninja on this topic.'
    assert ns({'lesson_complete': True, 'ninja': True, 'perfect_run': 0}) == pb.NEXT['master_two']
    assert ns({'lesson_complete': True, 'ninja': True, 'perfect_run': 1}) == 'One more 10/10 in a row for Master.'
    keep = ns({'lesson_complete': True, 'ninja': True, 'master_ever': True, 'master_active': True, 'master_expires_at': '2027-02-12T09:00:00+00:00'})
    assert keep == 'You are a master here. A 10/10 by 12 February keeps it.', keep
    assert ns({'lesson_complete': True, 'ninja': True, 'master_ever': True}) == pb.NEXT['master_again']


def test_path_of_a_topic():
    _, uid = new_pupil()
    with get_db() as conn:
        p = pb.path(conn, uid, 'gcse', 'maths', 'bidmas')
        assert [s['id'] for s in p['steps']] == ['lesson', 'ninja', 'master'] and not any(s['done'] for s in p['steps'])
        assert p['bar'] == 'Lesson done. A 10/10 on the quiz makes you a ninja on this topic.' and p['label'] == 'Mastery path'
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 10, 10, ['A'] * 10, [])
        p = pb.path(conn, uid, 'gcse', 'maths', 'bidmas')
        assert p['next'] == "Finish the lesson's quick checks for Ninja." and p['bar'].startswith('Lesson done. One more 10/10 in a row')


# ---- the results strip and Close to a badge ---------------------------------------------------------------------------
def test_results_strip_and_near_card():
    c, uid = new_pupil()
    set_guide(uid, {})
    with get_db() as conn:
        for _ in range(3):
            record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 6, 10, ['A'] * 10, [])
        gam.evaluate_milestones(conn, uid)
        aid = record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 7, 10, ['A'] * 10, [{'question': 'q'}] * 10)
    with c.session_transaction() as sess:
        sess['pb_qxp'] = [aid, 20]
        sess['pb_own'] = uid
    html = c.get(f'/quiz-attempts/{aid}').get_data(as_text=True)
    strip = re.search(r'<section class="results-earned".*?</section>', html, re.S)
    assert strip, 'the strip right after submitting'
    s = strip.group(0)
    assert 'Level 1' in s and 'XP to level 2' in s and 'class="results-level-fill" style="--from: ' in s
    assert s.count('<li class="mastery-chip') == 3 and 'Finish every lesson step for Lesson complete.' in s
    near = [m for m in moments_of(html) if m.get('kind') == 'near_badge']
    assert near and near[0]['title'] == 'Quiz fan' and near[0]['line'] == 'Finish one more quiz.', moments_of(html)
    assert re.fullmatch(r'near:\d{8}', near[0]['id']), near[0]['id']
    again = c.get(f'/quiz-attempts/{aid}').get_data(as_text=True)
    assert 'class="results-earned"' not in again, 'only on the page a pupil lands on after submitting'
    # once shown today (the client saves the flag), never again that day
    set_guide(uid, {near[0]['id']: True})
    with c.session_transaction() as sess:
        sess['pb_qxp'] = [aid, 20]
        sess['pb_own'] = uid
    html = c.get(f'/quiz-attempts/{aid}').get_data(as_text=True)
    assert not [m for m in moments_of(html) if m.get('kind') == 'near_badge']


def test_level_bar():
    bar = pb.level_bar(150, 170, gam.xp_level_progress)
    assert bar['from'] == 0.75 and bar['to'] == 0.85 and not bar['up'] and bar['to_next'] == '30 XP to level 2'
    up = pb.level_bar(190, 210, gam.xp_level_progress)
    assert up['up'] and up['from'] == 0.0 and up['level'] == 2


# ---- Your week --------------------------------------------------------------------------------------------------------
def test_your_week():
    c, uid = new_pupil()
    mon, sun, key = pb.last_week()
    assert re.fullmatch(r'wk:\d{4}w\d{2}', key) and mon.weekday() == 0 and (sun - mon).days == 6
    with get_db() as conn:
        assert pb.week_moment(conn, uid) is None, 'no study day last week: nothing'
        for d in (0, 2, 3):
            conn.execute('INSERT INTO user_study_days (user_id, study_date) VALUES (?, ?)', (uid, (mon + timedelta(days=d)).isoformat()))
        conn.executemany("INSERT INTO generator_mcq_attempts (user_id, level, subject, topic, mode, difficulty, user_answer, correct_answer, "
                         "correct, created_at, part_index) VALUES (?, 'gcse', 'maths', 'pythagoras', 'mcq', 'foundational', 'A', 'A', ?, ?, ?)",
                         [(uid, 1, iso(mon), None)] * 5 + [(uid, 0, iso(mon), None)] * 2 + [(uid, 1, iso(mon), 0)] * 3)
        conn.commit()
        w = pb.week_moment(conn, uid)
        assert w['id'] == key and w['days'] == 3 and w['dots'] == '1011000' and w['count'] == 5 and w['best'] == 'topic', w
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 7, 10, '[]', ?, 0)", (uid, iso(mon + timedelta(days=2))))
        conn.commit()
        w = pb.week_moment(conn, uid)
        assert w['best'] == 'quiz' and w['score'] == 7 and w['count'] == 12, w
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', 'bidmas', 10, 10, '[]', ?, 0)", (uid, iso(mon + timedelta(days=3))))
        conn.commit()
        assert pb.week_moment(conn, uid)['best'] == 'perfect'
        conn.execute('INSERT INTO user_milestones (user_id, milestone_key, earned_at, quiet) VALUES (?, ?, ?, 0)', (uid, 'quizzes_5', iso(mon)))
        conn.execute('INSERT INTO user_milestones (user_id, milestone_key, earned_at, quiet) VALUES (?, ?, ?, 0)', (uid, 'first_quiz', iso(mon)))
        conn.commit()
        w = pb.week_moment(conn, uid)
        assert w['best'] == 'badge' and w['title'] == 'Quiz fan', 'the highest tier'
    # offered on a page until its flag is saved
    set_guide(uid, {})
    week = [m for m in moments_of(c.get('/topics').get_data(as_text=True)) if m.get('type') == 'week']
    assert len(week) == 1 and week[0]['id'] == key
    set_guide(uid, {key: True})
    assert not [m for m in moments_of(c.get('/topics').get_data(as_text=True)) if m.get('type') == 'week']
    assert 'wk:' in social._GUIDE_VOLATILE_PREFIXES and 'near:' in social._GUIDE_VOLATILE_PREFIXES
    with get_db() as conn:
        g = json.loads(conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()['guide_json'])
    assert key in g['recent'], 'kept in the ring (safe to forget)'


# ---- Today ------------------------------------------------------------------------------------------------------------
def test_today():
    c, uid = new_pupil()
    today = datetime.now(timezone.utc).date()
    with get_db() as conn:
        conn.executemany("INSERT INTO generator_mcq_attempts (user_id, level, subject, topic, mode, difficulty, user_answer, correct_answer, "
                         "correct, created_at, part_index) VALUES (?, 'gcse', 'maths', 'bidmas', 'mcq', 'foundational', 'A', 'A', ?, ?, NULL)",
                         [(uid, 1, iso(today))] * 3 + [(uid, 1, iso(today - timedelta(days=1)))] * 4)
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 6, 10, ['A'] * 10, [])
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 4, 4, [{'user_answer': 'A'}] * 4, [], is_quicktest=True)
        record_quiz_attempt(conn, uid, 'gcse', 'maths', 'bidmas', 2, 2, ['A'] * 2, [], is_retry=True)
        conn.commit()
        t = pb.today(conn, uid)
    assert t['right'] == 9 and t['right_label'] == '9 right' and t['title'] == 'Today', t
    practice = c.get('/').get_data(as_text=True)
    strip = re.search(r'<section class="today-strip".*?</section>', practice, re.S).group(0)
    assert '9 right' in strip and 'XP' in strip and strip.count('<li class="today-dot') == 7 and 'aria-hidden="true"' in strip
    profile = c.get('/profile').get_data(as_text=True)
    assert re.search(r'<p class="streak-today"><strong>Today</strong> <span>9 right</span>', profile)
    assert 'today-strip' not in app.test_client().get('/').get_data(as_text=True), 'signed out: no strip'


# ---- lesson pages -----------------------------------------------------------------------------------------------------
def test_lesson_page_path():
    c, uid = new_pupil()
    html = c.get('/topic/gcse/maths/bidmas').get_data(as_text=True)
    m = re.search(r"data-lesson-path='([^']*)'", html)
    assert m, 'signed in: the path rides on the lesson wrapper'
    data = json.loads(m.group(1).replace('&#34;', '"').replace('&quot;', '"'))
    assert data['bar'].startswith('Lesson done.') and len(data['steps']) == 3
    assert "data-lesson-path" not in app.test_client().get('/topic/gcse/maths/bidmas').get_data(as_text=True)
    js = read('static/js/lesson-progress.js')
    for needle in ("JSON.parse(wrapper.dataset.lessonPath || 'null')", 'function initPath(root)', 'function pathLessonDone()',
                   "note.className = 'lesson-quiz-cta-note';", "    pathLessonDone();\n", 'initPath(contentRoot);'):
        assert needle in js, needle
    css = read('static/css/components.css')
    assert '}\n/* 2026-11-11 (E11 Phase 4): this selector line was missing' in css and '.lesson-quiz-cta-bar {\n    text-align: center;' in css
    assert '.mastery-chip.is-done' in css and '.lesson-quiz-cta-note' in css


# ---- the client, the copy, versions -----------------------------------------------------------------------------------
def test_client_copy_versions():
    js = read('static/js/moments.js')
    for needle in ("if (m.type === 'week') return !!g && !g.rewardSeen(m.id);", "if (m.type === 'week' && g.markReward) g.markReward(m.id);",
                   "(m.type === 'week' && m.part === 'days')) spend();", "['days', 'right', 'best'].forEach(function (part) {",
                   "if (stages.some(function (m) { return m.type !== 'week'; }) || badges.length) stages = stages.filter(",
                   "else if (m.type === 'week') { t.kind = 'week_card'; t.days = m.days; }",
                   "if (m.kind === 'near_badge' && G() && G().markReward) G().markReward(m.id);",
                   "if (k === 'quicktest_perfect') return fill(UI.quicktestPerfect, m);", 'function weekBox(box, m) {'):
        assert needle in js, needle
    for kind in ('quicktest_perfect', 'near_badge', 'week_card'):
        assert re.search(rf'\b{kind}: \'', js), kind
    for fn in (voice.extract_progress_copy, voice.extract_moment_copy):
        items, errors = fn()
        assert not errors and not [v for v in voice.lint(items) if v.level == 'error'], fn.__name__
    assert "js/moments.js') ~ '?v=7'" in read('templates/partials/guide.html')   # 2026-11-12: v6, the 10/10 redrawn; 2026-11-13: v7, its sounds
    assert "js/lesson-progress.js') }}?v=28" in read('templates/base.html') and "css/components.css') }}?v=36" in read('templates/base.html')
    for f in (ROOT / 'templates').rglob('*.html'):
        assert "around.css') }}?v=1" not in f.read_text(encoding='utf-8'), f
    assert "CACHE_VERSION = 'pb-v129'" in read('static/js/sw.js')   # 2026-11-13: the celebration sounds; 2026-11-12: the 10/10 redrawn


def main():
    tests = [test_quick_tests_are_not_lesson_quizzes, test_quick_test_full_marks_card, test_quick_tests_make_no_ninja, test_next_step_for_every_state, test_path_of_a_topic, test_results_strip_and_near_card,
             test_level_bar, test_your_week, test_today, test_lesson_page_path, test_client_copy_versions]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('E11 Phase 4 smoke passed.')


if __name__ == '__main__':
    main()
