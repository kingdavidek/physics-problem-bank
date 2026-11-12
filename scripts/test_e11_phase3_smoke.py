"""E11 Phase 3 smoke (docs/BADGES_AND_CELEBRATIONS_PLAN.md 4.1 and section 11): the Milestones shelf by line.
Run: python scripts/test_e11_phase3_smoke.py

Checks:
  * the lines: every catalogue badge sits in one line (or Extras, or a subject row), in threshold order, following the catalogue's
    next steps; the meter needs match the rules that award the badges (one short of a need earns nothing, the need earns it);
  * a row: the badges earned, then the next one with its meter ("3 of 5 quizzes"); a finished line says so; set work only in a class;
  * Next up: the largest share done, then the fewest to go; a line done for today (the streak, the daily question) comes last and
    has no link; a full meter is skipped; number words ("Finish two more quizzes.");
  * subjects: the welcome choice and studied subjects are shown, the rest behind Show all; topic badges ride in their subject;
  * the page: Next up with its meter and link (the latest practised topic's quiz), rows, locks, Show all, the sheet's data island
    for every badge (wardrobe links included) and Watch again; badge-sheet.js reads the island and replays through pbGuide.badges;
  * the copy is linted (models/zorp_voice.py extract_shelf_copy); shelf.css is profile only, capped and not precached.
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
from models import badge_shelf as bs  # noqa: E402
from models import gamification as gam  # noqa: E402
from models import zorp_voice as voice  # noqa: E402

HDR = {'Accept': 'application/json'}
SHELF_CSS_MAX = 3_900   # 2026-11-11: E11 Phase 3 shelf.css, 3,854 B


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def new_pupil(prefix='p3'):
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


def now(days=0):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def quizzes(conn, uid, n, score=7, topic='bidmas', retry=0):
    for _ in range(n):
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at, is_retry) "
                     "VALUES (?, 'gcse', 'maths', ?, ?, 10, '[]', ?, ?)", (uid, topic, score, now(), retry))


def answers(conn, uid, n, topic='bidmas'):
    conn.executemany("INSERT INTO generator_mcq_attempts (user_id, level, subject, topic, mode, difficulty, user_answer, correct_answer, "
                     "correct, created_at, part_index) VALUES (?, 'gcse', 'maths', ?, 'mcq', 'foundational', 'A', 'A', 1, ?, NULL)",
                     [(uid, topic, now())] * n)


def row(shelf, line_id):
    return next(r for r in shelf['lines'] + [shelf['extras']] if r['id'] == line_id)


# ---- the lines --------------------------------------------------------------------------------------------------------
def test_lines_cover_the_catalogue():
    placed = []
    for _id, _title, keys in bs.LINES + (bs.EXTRAS,):
        placed.extend(keys)
        for a, b in zip(keys, keys[1:]):
            if _id != 'extras':
                assert gam.MILESTONE_CATALOG[a]['next'] == b, (a, b)
    assert len(placed) == len(set(placed)), 'each badge in one line'
    rest = set(gam.MILESTONE_CATALOG) - set(placed)
    assert rest and all(k.startswith('subject_') for k in rest), sorted(rest)
    assert set(bs.NEED) <= set(placed) and set(bs.NEED) == set(placed) - set(bs.EXTRAS[2])
    for key, (counter, need) in bs.NEED.items():
        assert counter in bs.COPY and need >= 1, key
        assert str(need) in gam.MILESTONE_CATALOG[key]['how'] or need == 1, (key, gam.MILESTONE_CATALOG[key]['how'])


def test_meters_match_the_rules():
    """One short of each need earns nothing and the meter says so; the need earns the badge."""
    _, uid = new_pupil()
    with get_db() as conn:
        quizzes(conn, uid, 4)
        answers(conn, uid, 24)
        conn.commit()
        gam.evaluate_milestones(conn, uid)
        shelf = bs.build(conn, uid)
        q, p = row(shelf, 'quizzes'), row(shelf, 'practice')
        assert [b['key'] for b in q['badges']] == ['first_quiz'] and q['next']['key'] == 'quizzes_5', q
        assert q['meter'] == {'have': 4, 'need': 5, 'label': '4 of 5 quizzes'} and q['sentence'] == 'Finish one more quiz.'
        assert p['badges'] == [] and p['meter']['label'] == '24 of 25 questions right' and p['remaining'] == 1
        assert shelf['next_up']['key'] in ('quizzes_5', 'questions_25'), shelf['next_up']
        quizzes(conn, uid, 1)
        answers(conn, uid, 1)
        conn.commit()
        got = gam.evaluate_milestones(conn, uid)
        assert {'quizzes_5', 'questions_25'} <= set(got), got
        shelf = bs.build(conn, uid)
        q = row(shelf, 'quizzes')
        assert [b['key'] for b in q['badges']] == ['first_quiz', 'quizzes_5'] and q['next']['key'] == 'quizzes_25'
        assert q['meter']['label'] == '5 of 25 quizzes' and q['sentence'] == 'Finish 20 more quizzes.'
        p = row(shelf, 'practice')
        assert p['meter']['label'] == '25 of 100 questions right', 'Practice veteran counts 100 answers right'
        # a finished line
        conn.execute('INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, ?)', (uid, 'retry_fixed', now()))
        conn.commit()
        r = row(bs.build(conn, uid), 'retry')
        assert r['done'] and r['next'] is None and r['meter'] is None and [b['key'] for b in r['badges']] == ['retry_fixed']


def test_class_work_only_in_a_class():
    _, uid = new_pupil()
    with get_db() as conn:
        assert 'classwork' not in [r['id'] for r in bs.build(conn, uid)['lines']]
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.execute("INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'setwork_1', ?)", (uid, now()))
        conn.commit()
        r = row(bs.build(conn, uid), 'classwork')
        assert [b['key'] for b in r['badges']] == ['setwork_1'] and r['next']['key'] == 'setwork_10', 'an earned one always shows'


# ---- Next up ----------------------------------------------------------------------------------------------------------
def _r(line_id, have, need, counter='quizzes', key=None):
    remaining = need - have
    return {'id': line_id, 'next': {'key': key or line_id, 'title': line_id}, 'remaining': remaining, 'counter': counter,
            'meter': {'have': have, 'need': need, 'label': ''} if need > 1 else None, 'sentence': bs.sentence(counter, remaining),
            'link': bs.COPY[counter][3]}


def test_next_up_by_progress():
    pick = bs.pick_next_up
    assert pick([_r('a', 1, 5), _r('b', 3, 5), _r('c', 0, 1)])['key'] == 'b', 'the largest share done'
    assert pick([_r('a', 2, 4), _r('b', 10, 20)])['key'] == 'a', 'equal shares: the fewest to go'
    assert pick([_r('a', 2, 3, 'streak'), _r('b', 0, 1)], blocked={'streak'})['key'] == 'b', 'done for today comes last'
    only = pick([_r('a', 2, 3, 'streak')], blocked={'streak'})
    assert only['key'] == 'a' and only['link'] == '', 'no Study today once studied today'
    assert pick([_r('a', 5, 5), _r('b', 0, 3)])['key'] == 'b', 'a full meter is skipped (the badge comes with the next check)'
    assert pick([]) is None
    assert bs.sentence('quizzes', 2) == 'Finish two more quizzes.' and bs.sentence('right', 75) == 'Get 75 more questions right.'
    assert bs.sentence('quizzes', 1) == 'Finish one more quiz.' and bs.sentence('fixed', 1).startswith('Retry')


def test_streak_done_today_is_not_next_up():
    c, uid = new_pupil()
    with get_db() as conn:
        today = datetime.now(timezone.utc).date()
        conn.execute('INSERT OR REPLACE INTO user_streaks (user_id, current_streak, longest_streak, last_active_date, freeze_available) '
                     'VALUES (?, 2, 2, ?, 0)', (uid, today.isoformat()))
        for d in (0, 1):
            conn.execute('INSERT OR IGNORE INTO user_study_days (user_id, study_date) VALUES (?, ?)', (uid, (today - timedelta(days=d)).isoformat()))
        conn.commit()
        shelf = bs.build(conn, uid)
        assert row(shelf, 'streak')['meter']['label'] == '2 of 3 days in a row'
        assert shelf['next_up']['line'] != 'streak', shelf['next_up']


# ---- subjects ---------------------------------------------------------------------------------------------------------
def test_own_subjects_first():
    _, uid = new_pupil()
    with get_db() as conn:
        shelf = bs.build(conn, uid, own={('gcse', 'physics')})
        mine = [(r['level'], r['subject']) for r in shelf['subjects']]
        assert mine == [('gcse', 'physics')] and len(shelf['other_subjects']) >= 4, mine
        answers(conn, uid, 1, topic='bidmas')
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.execute("INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'topic_completed:gcse:cs:algorithms', ?)", (uid, now()))
        conn.commit()
        shelf = bs.build(conn, uid, own={('gcse', 'physics')})
        mine = {(r['level'], r['subject']): r for r in shelf['subjects']}
        assert {('gcse', 'physics'), ('gcse', 'maths'), ('gcse', 'cs')} <= set(mine), 'studied, chosen, or holding a topic badge'
        assert [b['key'] for b in mine[('gcse', 'cs')]['topic_badges']] == ['topic_completed:gcse:cs:algorithms']
        assert mine[('gcse', 'maths')]['topic_badges'] == []
        m = mine[('gcse', 'maths')]['meter']
        assert m['have'] == 0 and m['need'] >= 20 and m['label'].endswith('lessons'), m
        assert 'topic_completed:gcse:cs:algorithms' in shelf['sheet'], 'the sheet opens an earned topic badge'


# ---- the page ---------------------------------------------------------------------------------------------------------
def test_profile_page():
    c, uid = new_pupil()
    with get_db() as conn:
        quizzes(conn, uid, 3)
        answers(conn, uid, 2, topic='pythagoras')
        conn.commit()
        gam.evaluate_milestones(conn, uid)
    html = c.get('/profile').get_data(as_text=True)
    shelf = html[html.index('id="milestones"'):html.index('{# E10 phase 6b') if '{# E10 phase 6b' in html else html.index('id="wardrobe"')]
    assert 'class="badge-grid"' not in shelf, 'the alphabetical grid is gone'
    nu = shelf[shelf.index('class="shelf-next-up"'):shelf.index('class="shelf-lines"')]
    assert 'Next up' in nu and 'Quiz fan' in nu and 'Finish two more quizzes.' in nu and 'value="3"' in nu and 'max="5"' in nu, nu
    assert 'href="/lesson-quiz/gcse/maths/pythagoras"' in nu and '>Take a quiz</a>' in nu, 'the latest practised topic'
    order = [m for m in re.findall(r'data-line="([^"]+)"', shelf)]
    lines = [i for i in order if not i.startswith('subject:')]
    assert lines[1:] == [r[0] for r in bs.LINES if r[0] != 'classwork'] + ['extras'], lines
    assert shelf.count('class="shelf-lock"') >= 14 and '3 of 5 quizzes' in shelf
    assert '<details class="shelf-more">' in shelf and 'Show all subjects (' in shelf
    assert 'data-line="subject:gcse:maths"' in shelf.split('<details')[0], 'a studied subject is shown, not hidden'
    data = json.loads(re.search(r'id="pb-badge-data">(.*?)</script>', html, re.S).group(1))
    assert set(gam.MILESTONE_CATALOG) <= set(data) and data['first_quiz']['earned'] and not data['streak_7']['earned']
    assert set(data['first_quiz']) == {'title', 'blurb', 'how', 'family', 'emoji', 'tier', 'next_title', 'next_how', 'earned', 'date'}
    assert 'id="badge-sheet-replay" hidden>Watch again</button>' in html
    assert "css/shelf.css') }}" not in html and '/static/css/shelf.css?v=1' in html and '/static/js/badge-sheet.js?v=2' in html
    # a wardrobe "Earn ... to unlock" link names a badge the sheet can open even when it has no button on the shelf
    for key in re.findall(r'data-badge-open="([^"]+)"', html):
        assert key in data, key


def test_links():
    c, uid = new_pupil()
    with app.test_request_context(), get_db() as conn:
        from app import _shelf_links
        links = _shelf_links(conn, uid, {'welcome': {'topic': 'pythagoras'}}, {'level': 'gcse', 'subject': 'maths'})
        assert links['quiz'] == '/lesson-quiz/gcse/maths/pythagoras' and links['practice'] == '/?level=gcse&subject=maths&topic=pythagoras'
        assert links['daily'] == '/qotd' and links['lesson'] == '/topic/gcse/maths/pythagoras'
        answers(conn, uid, 1, topic='bidmas')
        conn.commit()
        assert _shelf_links(conn, uid, {'welcome': {'topic': 'pythagoras'}}, {'level': 'gcse', 'subject': 'maths'})['lesson'] == '/topic/gcse/maths/bidmas'
        none = _shelf_links(conn, -1, {}, None)
        assert none['quiz'] == none['lesson'] == '/topics'
    assert set(bs.LINKS) == {v[3] for v in bs.COPY.values()} | {'tour'}


# ---- the client, the copy, the CSS ------------------------------------------------------------------------------------
def test_client_copy_css():
    js = read('static/js/badge-sheet.js')
    assert "getElementById('pb-badge-data')" in js and 'getAttribute(\'data-title\')' not in js
    assert "window.pbGuide.badges([{ type: 'milestone', key: shown, badge: badge, replay: true }])" in js and 'replay.hidden = !(b.earned && canReplay())' in js
    bs_js = read('static/js/badge-stage.js')
    assert "again: 'Your badge'," in bs_js and 'kicker.textContent = card.replay ? UI.again : UI.kicker;' in bs_js and 'replay: spec.replay === true' in bs_js
    items, errors = voice.extract_shelf_copy()
    assert not errors and len(items) >= 70
    assert not [v for v in voice.lint(items) if v.level == 'error']
    css = ROOT / 'static/css/shelf.css'
    assert css.stat().st_size <= SHELF_CSS_MAX, css.stat().st_size
    assert 'shelf.css' not in read('static/js/sw.js'), 'profile only, not precached'
    assert '.shelf-meter::-webkit-progress-value' in read('static/css/shelf.css') and 'var(--surface-sunken)' in read('static/css/shelf.css')


def main():
    tests = [test_lines_cover_the_catalogue, test_meters_match_the_rules, test_class_work_only_in_a_class, test_next_up_by_progress,
             test_streak_done_today_is_not_next_up, test_own_subjects_first, test_profile_page, test_links, test_client_copy_css]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('E11 Phase 3 smoke passed.')


if __name__ == '__main__':
    main()
