"""E10 phase 6, part 1 fixes 2 and 3.
Run: python scripts/test_lesson_points_retry_stats_smoke.py

2. Lesson points by reloading: /api/lesson-progress recorded a lesson-step effort event on every save, including the save a lesson
   page makes on load (this was so before E10; phase 5 made it matter by adding level-ups). Points are now awarded only when a save
   adds a step, and never beyond the lesson's own step total.
3. Retry runs and personal best: a "Retry wrong ones" run is saved as a small quiz attempt. It is now marked (quiz_attempts.is_retry)
   and every statistic about how well a pupil did counts full quizzes only: personal best, the accuracy trend, topic status (a retry
   of ten wrong answers could look like a perfect ten), weak topics, the weekly best quiz, the friends accuracy board and the class
   average. The history list and the activity counts still show a retry.
"""
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models import gamification as gam  # noqa: E402
from models import topic_status as ts  # noqa: E402
from models import weak_topics as wt  # noqa: E402
from models.user_data import lesson_step_total, list_quiz_attempts, record_quiz_attempt  # noqa: E402

import test_celebration_moments_smoke as mo  # noqa: E402 - its helpers drive the lesson quiz (imported first: it adds test routes)

H = {'Accept': 'application/json'}
TOPIC = ('gcse', 'maths', 'bidmas')


def make_client():
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'lp_{s}@example.com', 'handle': f'lp_{s}',
                                              'password': 'password123', 'age_confirm': True}, headers=H)
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def points(uid):
    with get_db() as conn:
        return gam.lifetime_effort_xp(conn, uid)


def lesson_events(uid):
    with get_db() as conn:
        return conn.execute("SELECT COUNT(*) AS n FROM user_activity_events WHERE user_id = ? AND event_type = 'lesson_step_completed'",
                            (uid,)).fetchone()['n']


def save(c, section, keys=None, total=None):
    body = {'level': TOPIC[0], 'subject': TOPIC[1], 'topic': TOPIC[2], 'section_key': section, 'section_label': 'Part',
            'completed_keys': keys if keys is not None else [section]}
    if total:
        body['step_total'] = total
    r = c.post('/api/lesson-progress', json=body, headers=H)
    assert r.status_code == 200, r.data[:200]
    return r.get_json()['progress']


def test_lesson_points_only_for_new_steps():
    # 2026-11-08 (E10 review fix 5): every save below sends step_total=80, the most the API accepts; the server counts against the
    # lesson's own total (bidmas has 6 Quick Checks), so the client's number buys nothing, and invented keys are not steps.
    c, uid = make_client()
    total = lesson_step_total(*TOPIC)
    assert total >= 3, total
    p0 = points(uid)
    save(c, 'step-1', total=80)
    p1 = points(uid)
    assert p1 - p0 == gam.EFFORT_WEIGHTS['lesson_step_completed'], (p0, p1)
    assert lesson_events(uid) == 1
    # a lesson page saves on load: the same save again, and again, adds nothing
    for _ in range(25):
        save(c, 'step-1', total=80)
    assert points(uid) == p1 and lesson_events(uid) == 1
    # the bookmark moving to a step that is already complete adds nothing either
    save(c, 'step-1', keys=['step-1'], total=80)
    assert points(uid) == p1
    # a new step is worth points once
    save(c, 'step-2', total=80)
    assert points(uid) - p1 == gam.EFFORT_WEIGHTS['lesson_step_completed'] and lesson_events(uid) == 2
    save(c, 'step-2', total=80)
    assert lesson_events(uid) == 2
    # a client cannot invent steps beyond the lesson's own total to farm points
    before = lesson_events(uid)
    save(c, 'step-3', keys=[f'step-{i}' for i in range(3, 400)], total=80)
    assert lesson_events(uid) - before <= 1
    done = save(c, 'step-3', keys=[f'step-{i}' for i in range(400, 800)], total=80)
    after = lesson_events(uid)
    assert after - before <= 1, 'steps past the lesson total must not record more events'
    with get_db() as conn:
        stored = conn.execute('SELECT step_total FROM lesson_progress WHERE user_id = ?', (uid,)).fetchone()['step_total']
        awarded = conn.execute('SELECT COUNT(*) AS n FROM lesson_step_awards WHERE user_id = ?', (uid,)).fetchone()['n']
    assert stored == total, 'the stored total is the lesson\'s own, never the larger number the client sent'
    assert awarded <= total, 'no more steps can earn points than the lesson has'
    assert after == lesson_events(uid)
    # and no level-up by reloading: 50 more saves, no change in points
    p = points(uid)
    for _ in range(50):
        save(c, 'step-3', keys=[f'step-{i}' for i in range(3, 400)], total=80)
    assert points(uid) == p
    # the pupil still gets today as a study day from opening a part-finished lesson (one per day, not farmable)
    with get_db() as conn:
        assert gam.get_study_streak(conn, uid)['current'] >= 1
    del done


def test_lesson_points_not_farmable_by_clearing_and_redoing():
    # 2026-11-08 (E10 review fix 5): the ledger of steps that earned points is kept apart from the bookmark
    c, uid = make_client()
    total = lesson_step_total(*TOPIC)
    for i in range(total):
        save(c, f'step-{i}', total=80)
    earned = lesson_events(uid)
    p = points(uid)
    assert earned == total and p == total * gam.EFFORT_WEIGHTS['lesson_step_completed']
    r = c.delete('/api/v1/me/lesson-progress/%s/%s/%s' % TOPIC, headers=H)
    assert r.status_code == 200
    for _ in range(3):
        for i in range(total):
            save(c, f'step-{i}', total=80)
        c.delete('/api/v1/me/lesson-progress/%s/%s/%s' % TOPIC, headers=H)
    assert lesson_events(uid) == earned and points(uid) == p, 'clearing and redoing a lesson earns nothing again'
    # the web route that clears the bookmark does not clear the ledger either
    for i in range(total):
        save(c, f'step-{i}', total=80)
    assert points(uid) == p
    # keys that are not steps of this lesson never earn: odd names, a step number past the end, a client total of 80
    c2, uid2 = make_client()
    save(c2, 'x-1', keys=['x-1', 'section-9', 'step-', 'step--1', 'step-%d' % total, 'step-999'], total=80)
    assert lesson_events(uid2) == 0 and points(uid2) == 0
    with get_db() as conn:
        assert conn.execute('SELECT COUNT(*) AS n FROM lesson_step_awards WHERE user_id = ?', (uid2,)).fetchone()['n'] == 0
    # the ledger is in the export and goes with the account
    from models import account_deletion, data_export
    assert ('lesson_step_awards', 'user_id') in data_export._TABLES and ('lesson_step_awards', 'user_id') in account_deletion.USER_SCOPED_CHECKS
    with get_db() as conn:
        out = data_export.build_user_export(conn, uid)
    assert json.dumps(out).count('step-') >= total
    # the one-time seed: steps already complete when the ledger arrived are in it, so nothing is paid twice
    c3, uid3 = make_client()
    with get_db() as conn:
        conn.execute("INSERT INTO lesson_progress (user_id, level, subject, topic, section_key, section_label, updated_at, completed_keys_json, step_total) "
                     "VALUES (?, ?, ?, ?, 'step-1', 'P', datetime('now'), '[\"step-0\",\"step-1\"]', ?)", (uid3, *TOPIC, total))
        conn.execute("DELETE FROM schema_migrations WHERE name = 'lesson_step_awards_seed'")
        conn.commit()
    import app as appmod
    with get_db() as conn:
        appmod._seed_lesson_step_awards(conn)
        keys = sorted(r['step_key'] for r in conn.execute('SELECT step_key FROM lesson_step_awards WHERE user_id = ?', (uid3,)).fetchall())
    assert keys == ['step-0', 'step-1'], keys
    save(c3, 'step-1', keys=['step-0', 'step-1'], total=80)
    assert lesson_events(uid3) == 0, 'steps done before the ledger existed are not paid again'


def test_retry_attempts_are_marked_everywhere():
    src = (ROOT / 'app.py').read_text(encoding='utf-8')
    assert src.count("is_retry=bool(data.get('retry_mode'))") == 4, 'all four record_quiz_attempt call sites pass retry_mode'
    with get_db() as conn:
        cols = {r[1] for r in conn.execute('PRAGMA table_info(quiz_attempts)').fetchall()}
    assert 'is_retry' in cols


def add_attempt(uid, score, total, retry=False, topic=TOPIC):
    with get_db() as conn:
        return record_quiz_attempt(conn, uid, *topic, score, total, ['A'] * total, [], is_retry=retry)


def test_personal_best_counts_full_quizzes_only():
    c, uid = make_client()
    add_attempt(uid, 6, 10)
    add_attempt(uid, 7, 10)            # a full quiz, the pupil's best so far
    add_attempt(uid, 3, 3, retry=True)   # the three misses fixed: 100 per cent of three questions, not a full quiz
    add_attempt(uid, 8, 10)            # a full quiz that beats every earlier full quiz
    with get_db() as conn:
        assert gam.personal_best_quiz(conn, uid, *TOPIC, 8, 10) is True, 'a retry run must not stop a later full quiz being a best'
        # the retry is still in the history list
        rows = list_quiz_attempts(conn, uid, limit=10)
        assert len(rows) == 4 and any(r['total'] == 3 for r in rows)
    # a retry never makes a "best" itself: the moment is only asked for full quizzes, and a small retry of 5/5 does not hide a 9/10
    add_attempt(uid, 5, 5, retry=True)
    add_attempt(uid, 9, 10)
    with get_db() as conn:
        assert gam.personal_best_quiz(conn, uid, *TOPIC, 9, 10) is True


def test_other_statistics_count_full_quizzes_only():
    c, uid = make_client()
    add_attempt(uid, 5, 10)
    add_attempt(uid, 10, 10, retry=True)    # ten wrong answers retried and all right: not a perfect quiz
    with get_db() as conn:
        # accuracy trend (the sparkline): the retry is not a point
        trend = gam.recent_accuracy_trend(conn, uid)
        assert [p['pct'] for p in trend if p['kind'] == 'quiz'] == [50.0], trend
        # weekly best quiz
        recap = gam.get_weekly_recap(conn, uid)
        best = (recap or {}).get('best_quiz')
        assert best is None or (best['score'], best['total']) == (5, 10), best
        # topic status: ninja asks for a 10/10 on a full quiz, and a retry of ten does not count
        stat = ts.compute_topic_status(['s1', 's2', 's3'], 3, [{'score': 10, 'total': 10, 'created_at': '2026-11-08T10:00:00+00:00'}])
        assert stat['ninja'] is True     # (the pure function is unchanged: it is fed full quizzes only)
        status_map = ts.topic_status_map(conn, uid)
        item = status_map.get(TOPIC)
        assert not item or not item.get('ninja'), item
        # weak topics: the topic's quiz average is the full quiz alone
        stats = wt._aggregate_topic_stats(conn, uid)
        topic = next(v for k, v in stats.items() if TOPIC[2] in str(k))
        assert topic['quiz_count'] == 1 and topic['quiz_score_sum'] == 5 and topic['quiz_total_sum'] == 10, topic
        # the friends accuracy board's per-user stats
        since = '2000-01-01T00:00:00'
        accuracy = gam._accuracy_stats_since(conn, [uid], since) if hasattr(gam, '_accuracy_stats_since') else None
        if accuracy is not None:
            assert accuracy[uid]['earned'] == 5 and accuracy[uid]['possible'] == 10, accuracy
    # the real routes: a Retry wrong ones run through the lesson quiz is saved as a retry
    c2, uid2 = mo.make_client()
    r = mo.take_quiz(c2, uid2, wrong=3)
    page = c2.get(r.headers['Location']).get_data(as_text=True)
    level, subject, topic_slug = mo.TOPIC
    r = c2.post(f'/lesson-quiz/{level}/{subject}/{topic_slug}/retry-wrong', data={'csrf_token': mo.csrf_of(page)})
    assert r.status_code == 302
    c2.get(f'/lesson-quiz/{level}/{subject}/{topic_slug}')
    problems = mo.quiz_problems(uid2)
    form = {f'answer_{i}': p['correct_answer'][:1].upper() for i, p in enumerate(problems)}
    c2.post(f'/lesson-quiz/{level}/{subject}/{topic_slug}/submit', data=form)
    with get_db() as conn:
        rows = conn.execute('SELECT total, is_retry FROM quiz_attempts WHERE user_id = ? ORDER BY id', (uid2,)).fetchall()
    assert [(r['total'], r['is_retry']) for r in rows] == [(10, 0), (3, 1)], [tuple(r) for r in rows]
    # an 8/10 full quiz now is a personal best even though the retry scored 3/3
    with get_db() as conn:
        add = record_quiz_attempt(conn, uid2, level, subject, topic_slug, 9, 10, ['A'] * 10, [])
        assert add
        assert gam.personal_best_quiz(conn, uid2, level, subject, topic_slug, 9, 10) is True


def main():
    for t in (test_lesson_points_only_for_new_steps, test_lesson_points_not_farmable_by_clearing_and_redoing, test_retry_attempts_are_marked_everywhere,
              test_personal_best_counts_full_quizzes_only, test_other_statistics_count_full_quizzes_only):
        t()
        print('ok', t.__name__)
    print('Lesson points and retry stats smoke (E10 phase 6) passed.')


if __name__ == '__main__':
    main()
