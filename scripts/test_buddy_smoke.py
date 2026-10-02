"""E3 buddy + friend accuracy leaderboard smoke — run: python scripts/test_buddy_smoke.py"""
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.buddy import (  # noqa: E402
    BUDDY_CELEBRATE,
    BUDDY_FRIEND_CHALLENGE,
    BUDDY_STREAK_RISK,
    BUDDY_WEAK_TOPIC,
    buddy_task_mark,
)
from models.gamification import ensure_user_streak  # noqa: E402
from models.notifications import NOTIFICATION_MILESTONE  # noqa: E402
from models.social import follow_user  # noqa: E402
from models.user import User  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle):
    r = client.get('/register')
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
        follow_redirects=True,
    )
    assert r.status_code == 200


def logout(client):
    r = client.get('/profile')
    client.post(
        '/logout',
        data={'csrf_token': csrf_from(r.data.decode())},
        follow_redirects=True,
    )


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user
        return user.id


def insert_quiz(user_id, score, total, *, created_at=None, topic='algebra'):
    created_at = created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    with get_db() as conn:
        conn.execute(
            '''
            INSERT INTO quiz_attempts (
                user_id, level, subject, topic, score, total, answers_json, problems_json, created_at
            ) VALUES (?, 'gcse', 'maths', ?, ?, ?, '[]', '[]', ?)
            ''',
            (user_id, topic, score, total, created_at),
        )
        conn.commit()


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'e3a_{suffix}'
        handle_b = f'e3b_{suffix}'
        email_a = f'e3a_{suffix}@example.com'
        email_b = f'e3b_{suffix}@example.com'

        r = client.get('/api/v1/build-info')
        assert r.status_code == 200
        assert r.get_json()['buddy_embed'] == 'v6'
        assert r.get_json()['study_buddy_js'] == 'v11'

        r = client.get('/')
        assert r.status_code == 200
        assert b'data-buddy-root' not in r.data
        assert b'buddy.js' not in r.data
        assert b'study-buddy.js' not in r.data
        assert b'zorp-motion.js' not in r.data and b'zorp-poses.js' not in r.data

        r = client.get('/api/v1/me/buddy')
        assert r.status_code in (401, 403)

        register(client, email_a, handle_a)
        uid_a = user_id_for(handle_a)

        r = client.get('/profile')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'study-buddy' in html
        assert 'study-buddy.js' in html
        assert 'data-buddy-face' in html
        assert 'buddy-mascot' in html
        assert 'data-face=' in html
        assert 'zorp-motion.js?v=11' in html
        assert 'zorp-poses.js?v=4' in html and html.index('zorp-motion.js') < html.index('zorp-poses.js')
        assert 'css/motion.css?v=8' in html
        assert 'buddy-arm--l' in html
        assert 'buddy-pupil' in html
        # Fresh user, no milestones earned yet -> default Zorp (E7 Phase 1.5).
        assert 'data-zorp-colour' not in html
        assert 'data-mouth=' not in html

        # Fresh user: nothing applies -> the buddy is None, not a permanent nudge.
        r = client.get('/api/v1/me/buddy')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['buddy'] is None

        # A fresh user renders no bubble server-side, but the aside is still present as
        # a face-only corner Zorp (so answer reactions/idle motion keep working) -- the
        # root carries no `hidden` attribute, the card starts hidden, and the JSON
        # island is always rendered (as `null` here) so the client skips its initial
        # fetch rather than firing one right away.
        assert 'data-buddy-root' in html
        assert 'id="pb-buddy-prompt"' in html
        assert 'id="pb-buddy-prompt">null</script>' in html
        m = re.search(r'<aside id="study-buddy"[^>]*>', html)
        assert m, 'expected the study-buddy aside on the profile page'
        aside_tag = m.group(0)
        assert ' hidden' not in aside_tag, aside_tag
        assert 'data-buddy-state="face"' in aside_tag
        card_m = re.search(r'<div class="study-buddy-card"[^>]*>', html)
        assert card_m, 'expected the study-buddy-card div'
        assert 'hidden' in card_m.group(0)

        insert_quiz(uid_a, 8, 10)
        r = client.get('/api/v1/me/buddy')
        celebrate = r.get_json()['buddy']
        assert celebrate['type'] == BUDDY_CELEBRATE
        assert celebrate['face'] == '😄'
        assert '8/10' in celebrate['message']
        assert celebrate['task_mark']

        # task_mark is stable across two calls with no new activity...
        mark_1 = celebrate['task_mark']
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['task_mark'] == mark_1
        with get_db() as conn:
            mark_direct = buddy_task_mark(conn, uid_a, datetime.now(timezone.utc))
        assert mark_direct == mark_1
        assert datetime.now(timezone.utc).date().isoformat() in mark_1
        # ...changes after another quiz attempt row is inserted...
        insert_quiz(uid_a, 5, 10, topic='functions')
        r = client.get('/api/v1/me/buddy')
        mark_2 = r.get_json()['buddy']['task_mark']
        assert mark_2 != mark_1
        # ...and changes after 5 MCQ attempts (a fresh "task" every 5 answers).
        now_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with get_db() as conn:
            for _ in range(5):
                conn.execute(
                    '''
                    INSERT INTO generator_mcq_attempts (
                        user_id, level, subject, topic, mode, difficulty,
                        user_answer, correct_answer, correct, created_at
                    ) VALUES (?, 'gcse', 'maths', 'algebra', 'mcq', 'foundational', 'A', 'B', 0, ?)
                    ''',
                    (uid_a, now_iso),
                )
            conn.commit()
        r = client.get('/api/v1/me/buddy')
        mark_3 = r.get_json()['buddy']['task_mark']
        assert mark_3 != mark_2

        # Milestones no longer surface as a buddy bubble -- they generate a
        # 'milestone_earned' notification and a #pb-new-milestone JSON island
        # instead. evaluate_milestones() is the single place that awards them.
        with get_db() as conn:
            conn.execute('DELETE FROM user_milestones WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM user_notifications WHERE user_id = ?', (uid_a,))
            conn.commit()
        from models.gamification import evaluate_milestones  # noqa: E402
        with get_db() as conn:
            earned = evaluate_milestones(conn, uid_a)
            assert 'first_quiz' in earned
            rows = conn.execute(
                'SELECT notification_type, payload_json FROM user_notifications WHERE user_id = ?',
                (uid_a,),
            ).fetchall()
            milestone_rows = [row for row in rows if row['notification_type'] == NOTIFICATION_MILESTONE]
            assert len(milestone_rows) == 1
            assert 'first_quiz' in milestone_rows[0]['payload_json']
            # Re-running adds no duplicate notification for an already-earned badge.
            again = evaluate_milestones(conn, uid_a)
            assert 'first_quiz' not in again
            rows_after = conn.execute(
                'SELECT COUNT(*) AS n FROM user_notifications WHERE user_id = ? AND notification_type = ?',
                (uid_a, NOTIFICATION_MILESTONE),
            ).fetchone()
            assert rows_after['n'] == 1

        r = client.get('/api/v1/me/notifications')
        assert r.status_code == 200
        notif = r.get_json()
        milestone_items = [n for n in notif['notifications'] if n['type'] == NOTIFICATION_MILESTONE]
        assert len(milestone_items) == 1
        assert 'New badge' in milestone_items[0]['message']
        assert '#milestones' in milestone_items[0]['url']

        r = client.get('/profile')
        assert r.status_code == 200
        profile_html = r.data.decode()
        # No more milestone bubble/attribute on the corner buddy.
        assert 'data-buddy-milestone-key' not in profile_html
        # But the badge celebration island fires once via #pb-new-milestone.
        assert 'id="pb-new-milestone"' in profile_html
        assert 'first_quiz' in profile_html

        # The recent-milestone celebration island clears once earned_at falls
        # outside the 24h window (studied via direct DB manipulation, since the
        # smoke suite can't wait a day).
        with get_db() as conn:
            old_at = (datetime.now(timezone.utc) - timedelta(hours=25)).replace(microsecond=0).isoformat()
            conn.execute(
                'UPDATE user_milestones SET earned_at = ? WHERE user_id = ?',
                (old_at, uid_a),
            )
            conn.commit()
        r = client.get('/profile')
        assert 'id="pb-new-milestone"' not in r.data.decode()

        with get_db() as conn:
            conn.execute('DELETE FROM user_milestones WHERE user_id = ?', (uid_a,))
            conn.commit()

        today_iso = datetime.now(timezone.utc).date().isoformat()
        with get_db() as conn:
            conn.execute('DELETE FROM quiz_attempts WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM generator_mcq_attempts WHERE user_id = ?', (uid_a,))
            conn.execute(
                'UPDATE user_streaks SET current_streak = 0, last_active_date = NULL WHERE user_id = ?',
                (uid_a,),
            )
            conn.execute(
                'INSERT OR IGNORE INTO user_study_days (user_id, study_date) VALUES (?, ?)',
                (uid_a, today_iso),
            )
            conn.execute('DELETE FROM qotd_attempts WHERE user_id = ?', (uid_a,))
            conn.commit()
        # qotd_nudge and the bare 'nudge' fallback are gone -- with none of the
        # remaining triggers true, the buddy is None.
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy'] is None

        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(days=3)).replace(microsecond=0).isoformat()
        with get_db() as conn:
            conn.execute('DELETE FROM quiz_attempts WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM user_study_days WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM qotd_attempts WHERE user_id = ?', (uid_a,))
            ensure_user_streak(conn, uid_a)
            conn.execute(
                '''
                UPDATE user_streaks
                SET current_streak = 4, longest_streak = 4, last_active_date = ?,
                    freeze_available = 0
                WHERE user_id = ?
                ''',
                (yesterday, uid_a),
            )
            conn.commit()
        # streak_risk still shows a bubble -- David explicitly chose to keep it.
        r = client.get('/api/v1/me/buddy')
        streak = r.get_json()['buddy']
        assert streak['type'] == BUDDY_STREAK_RISK
        assert streak['face'] == '🔥'
        assert 'streak' in streak['message'].lower()
        assert streak['task_mark']
        # E8 Phase 5 (Children's Code std 13): upbeat copy, no loss framing
        assert streak['message'] == 'Keep your 4-day streak going with one quick question.', streak['message']
        assert 'risk' not in streak['message'].lower() and 'lose' not in streak['message'].lower()
        # the corner buddy's first paint is the upbeat heads-up look, never a frown
        page = client.get('/').data.decode()
        assert 'data-face="heads-up"' in page, 'streak_risk prompt must draw the heads-up preset'
        assert 'frown' not in page.split('id="study-buddy"', 1)[1].split('data-buddy-card', 1)[0]
        with get_db() as conn:
            conn.execute('UPDATE user_streaks SET freeze_available = 1 WHERE user_id = ?', (uid_a,))
            conn.commit()
        freeze_msg = client.get('/api/v1/me/buddy').get_json()['buddy']['message']
        assert 'honest' not in freeze_msg and 'risk' not in freeze_msg.lower()
        assert freeze_msg == 'You have a skip in hand this week, and one quick question still keeps your streak going.'
        with get_db() as conn:
            conn.execute('UPDATE user_streaks SET freeze_available = 0 WHERE user_id = ?', (uid_a,))
            conn.commit()

        with get_db() as conn:
            conn.execute(
                '''
                UPDATE user_streaks
                SET current_streak = 0, last_active_date = NULL
                WHERE user_id = ?
                ''',
                (uid_a,),
            )
            conn.commit()
        today_iso = datetime.now(timezone.utc).date().isoformat()
        with get_db() as conn:
            conn.execute(
                '''
                INSERT OR IGNORE INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
                VALUES (?, ?, 1, 'A', ?)
                ''',
                (uid_a, today_iso, datetime.now(timezone.utc).replace(microsecond=0).isoformat()),
            )
            conn.commit()
        insert_quiz(uid_a, 1, 10, created_at=old, topic='algebra')
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_WEAK_TOPIC
        assert r.get_json()['buddy']['action_url']
        off_page = r.get_json()['buddy']
        assert off_page['type'] == BUDDY_WEAK_TOPIC
        assert off_page['face'] == '🤔'
        assert off_page['action_label'] == 'Practise this'
        assert '/topic/' in off_page['action_url']
        stay_off = [item for item in off_page.get('actions') or [] if item.get('kind') == 'stay']
        assert stay_off == []

        r = client.get('/api/v1/me/buddy?level=gcse&subject=maths&topic=algebra')
        on_page = r.get_json()['buddy']
        assert on_page['type'] == BUDDY_WEAK_TOPIC
        labels = [item['label'] for item in on_page['actions']]
        assert 'Practise MCQ' in labels
        assert 'Take a quiz' in labels
        assert any(item.get('kind') == 'stay' and 'Keep learning' in item.get('label', '') for item in on_page['actions'])
        assert 'algebra' in on_page['actions'][0]['url'] or 'mode=mcq' in on_page['actions'][0]['url']
        assert on_page['actions'][0]['label'] == 'Practise MCQ'
        assert 'mode=mcq' in on_page['action_url']
        assert '/lesson-quiz/' in next(item['url'] for item in on_page['actions'] if item['label'] == 'Take a quiz')
        assert 'Keep learning' in on_page['actions'][-1]['label']

        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with get_db() as conn:
            conn.execute(
                '''
                INSERT INTO generator_mcq_attempts (
                    user_id, level, subject, topic, mode, difficulty,
                    user_answer, correct_answer, correct, created_at
                ) VALUES (?, 'gcse', 'maths', 'algebra', 'mcq', 'foundational', 'A', 'B', 0, ?)
                ''',
                (uid_a, now),
            )
            conn.commit()
        r = client.get('/api/v1/me/buddy?level=gcse&subject=maths&topic=algebra')
        after_mcq = r.get_json()['buddy']
        assert after_mcq['actions'][0]['label'] == 'Take a quiz'
        assert 'quiz' in after_mcq['message'].lower()

        old_milestone_at = (datetime.now(timezone.utc) - timedelta(days=2)).replace(microsecond=0).isoformat()
        with get_db() as conn:
            conn.execute('DELETE FROM user_milestones WHERE user_id = ?', (uid_a,))
            for key in ('first_quiz', 'qotd_first'):
                conn.execute(
                    '''
                    INSERT INTO user_milestones (user_id, milestone_key, earned_at)
                    VALUES (?, ?, ?)
                    ''',
                    (uid_a, key, old_milestone_at),
                )
            conn.commit()

        # qotd_first carries pose 'wave' (E7 Phase 1.5) and is the only pose-bearing
        # milestone earned here, so it drives the automatic look on /profile.
        r = client.get('/profile')
        assert r.status_code == 200
        profile_with_look = r.data.decode()
        assert 'data-zorp-colour="mint"' in profile_with_look
        assert 'data-mouth="cat"' in profile_with_look
        # Earned > 24h ago -> no celebration island this load.
        assert 'id="pb-new-milestone"' not in profile_with_look

        r = client.get('/topic/gcse/maths/algebra')
        assert r.status_code == 200
        assert b'data-buddy-actions' in r.data
        assert b'study-buddy.js' in r.data
        html_lesson = r.data.decode()
        assert 'data-buddy-level="gcse"' in html_lesson
        assert 'data-buddy-subject="maths"' in html_lesson
        assert 'data-buddy-topic="algebra"' in html_lesson
        assert 'study-buddy.js?v=28' in html_lesson
        assert 'Problem Bank build: buddy-embed-v6' in html_lesson
        assert 'pb-buddy-embed-v6' in html_lesson
        assert 'id="pb-buddy-page"' in html_lesson
        assert 'id="pb-buddy-prompt"' in html_lesson
        assert 'Practise MCQ' in html_lesson
        assert 'Keep learning' in html_lesson
        assert '"topic": "algebra"' in html_lesson or '"topic":"algebra"' in html_lesson

        r = client.get('/topic/gcse/maths/functions')
        assert r.status_code == 200
        html_fn = r.data.decode()
        assert 'data-buddy-topic="functions"' in html_fn
        assert 'id="pb-buddy-prompt"' in html_fn

        r = client.get(
            '/api/v1/me/buddy',
            headers={'Referer': 'http://localhost/topic/gcse/maths/algebra'},
        )
        via_ref = r.get_json()['buddy']
        assert via_ref['type'] == BUDDY_WEAK_TOPIC
        assert any(item.get('kind') == 'stay' for item in via_ref['actions'])
        assert 'Practise this' not in [item.get('label') for item in via_ref['actions']]

        r = client.get('/api/v1/me/buddy?level=gcse&topic=algebra')
        via_infer = r.get_json()['buddy']
        assert any(item.get('kind') == 'stay' for item in via_infer['actions'])

        r = client.get(
            '/api/v1/me/buddy',
            headers={'X-PB-Buddy-Path': '/topic/gcse/maths/algebra'},
        )
        via_header = r.get_json()['buddy']
        assert any(item.get('kind') == 'stay' for item in via_header['actions'])
        buddy_js = client.get('/static/js/study-buddy.js').data.decode()
        assert 'pb-buddy-storage' in buddy_js
        assert 'pb-buddy-quiet' in buddy_js
        # The old bypass that showed a server-rendered "stay" bubble unconditionally
        # (before every suppression key) is gone -- everything now goes through the
        # single maybeShow()/shouldShow() gate.
        assert "data-buddy-server" not in buddy_js
        assert 'shouldShow' in buddy_js

        # quiz_runner_mode pages must omit the aside entirely, not just hide it.
        r = client.get('/lesson-quiz/gcse/maths/algebra')
        assert r.status_code == 200
        quiz_html = r.data.decode()
        assert 'data-buddy-root' not in quiz_html

        logout(client)
        register(client, email_b, handle_b)
        uid_b = user_id_for(handle_b)
        logout(client)
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': email_a,
                'password': 'password123',
            },
            follow_redirects=True,
        )
        with get_db() as conn:
            follow_user(conn, uid_a, uid_b)
            conn.execute('DELETE FROM quiz_attempts WHERE user_id IN (?, ?)', (uid_a, uid_b))
            conn.execute(
                'DELETE FROM generator_mcq_attempts WHERE user_id IN (?, ?)',
                (uid_a, uid_b),
            )
            conn.execute('DELETE FROM quiz_challenges WHERE creator_id = ?', (uid_a,))
            conn.execute('DELETE FROM user_milestones WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM user_study_days WHERE user_id = ?', (uid_a,))
            conn.execute('DELETE FROM qotd_attempts WHERE user_id = ?', (uid_a,))
            conn.execute(
                '''
                UPDATE user_streaks
                SET current_streak = 0, last_active_date = NULL
                WHERE user_id = ?
                ''',
                (uid_a,),
            )
            conn.commit()

        r = client.get('/api/v1/me/buddy')
        friend = r.get_json()['buddy']
        assert friend['type'] == BUDDY_FRIEND_CHALLENGE
        assert friend['face'] == '🤝'
        assert f'@{handle_b}' in friend['message']
        assert friend['friend_handle'] == handle_b
        assert handle_b in friend['action_url']
        assert friend['action_label'] == 'Send challenge'

        recent_challenge_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with get_db() as conn:
            conn.execute(
                '''
                INSERT INTO quiz_challenges (
                    creator_id, opponent_id, level, subject, topic, seed,
                    problems_json, status, created_at
                ) VALUES (?, ?, 'gcse', 'maths', 'algebra', 1, '[]', 'pending', ?)
                ''',
                (uid_a, uid_b, recent_challenge_at),
            )
            conn.commit()
        # Nothing left to trigger -> None, not a nudge fallback.
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy'] is None

        with get_db() as conn:
            conn.execute('DELETE FROM quiz_challenges WHERE creator_id = ?', (uid_a,))
            conn.commit()
        insert_quiz(uid_a, 1, 10, created_at=old, topic='algebra')
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_WEAK_TOPIC

        with get_db() as conn:
            conn.execute('DELETE FROM quiz_attempts WHERE user_id = ?', (uid_a,))
            milestone_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            conn.execute(
                '''
                INSERT INTO user_milestones (user_id, milestone_key, earned_at)
                VALUES (?, 'first_quiz', ?)
                ''',
                (uid_a, milestone_at),
            )
            conn.commit()
        # A milestone earned in the last 24h no longer becomes a buddy bubble at
        # all (it's a notification instead), so the next-highest-priority trigger
        # shows through -- here, friend_challenge (uid_a follows uid_b, no recent
        # challenge sent).
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_FRIEND_CHALLENGE

        logout(client)
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': email_b,
                'password': 'password123',
            },
            follow_redirects=True,
        )
        with get_db() as conn:
            follow_user(conn, uid_b, uid_a)
            conn.execute('DELETE FROM quiz_attempts WHERE user_id IN (?, ?)', (uid_a, uid_b))
            conn.execute(
                'DELETE FROM generator_mcq_attempts WHERE user_id IN (?, ?)',
                (uid_a, uid_b),
            )
            conn.commit()

        insert_quiz(uid_b, 9, 10)
        insert_quiz(uid_a, 2, 10)

        r = client.get('/leaderboard/friends?board=accuracy')
        assert r.status_code == 200
        body = r.data.decode()
        assert 'Friend accuracy leaderboard' in body
        assert 'Quiz accuracy' in body
        assert handle_a in body
        assert handle_b in body

        r = client.get('/api/v1/me/gamification')
        assert r.status_code == 200
        board = r.get_json()['friend_accuracy_leaderboard']
        handles = [item['handle'] for item in board]
        assert handle_b in handles
        assert handle_a in handles
        by_handle = {item['handle']: item for item in board}
        assert by_handle[handle_b]['accuracy_pct'] == 90.0
        assert by_handle[handle_a]['accuracy_pct'] == 20.0
        assert by_handle[handle_b]['rank'] < by_handle[handle_a]['rank']

        r = client.patch(
            '/api/v1/me/settings',
            json={'show_accuracy_leaderboard': False},
        )
        assert r.status_code == 200
        assert r.get_json()['settings']['show_accuracy_leaderboard'] is False

        logout(client)
        # Log back in as A (who follows nobody) — follow B from A
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': email_a,
                'password': 'password123',
            },
            follow_redirects=True,
        )
        with get_db() as conn:
            follow_user(conn, uid_a, uid_b)

        r = client.get('/api/v1/me/gamification')
        board = r.get_json()['friend_accuracy_leaderboard']
        handles = [item['handle'] for item in board]
        assert handle_b not in handles
        assert handle_a in handles

        r = client.get('/leaderboard/friends')
        assert r.status_code == 200
        assert b'Friend effort leaderboard' in r.data

    print('Buddy and accuracy-leaderboard smoke tests passed.')


if __name__ == '__main__':
    main()
