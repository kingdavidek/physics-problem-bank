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
    BUDDY_NUDGE,
    BUDDY_STREAK_RISK,
    BUDDY_WEAK_TOPIC,
)
from models.gamification import ensure_user_streak  # noqa: E402
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
        assert r.get_json()['buddy_embed'] == 'v3'

        r = client.get('/')
        assert r.status_code == 200
        assert b'data-buddy-root' not in r.data
        assert b'buddy.js' not in r.data
        assert b'study-buddy.js' not in r.data

        r = client.get('/api/v1/me/buddy')
        assert r.status_code in (401, 403)

        register(client, email_a, handle_a)
        uid_a = user_id_for(handle_a)

        r = client.get('/profile')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'study-buddy' in html
        assert 'study-buddy.js' in html
        assert '👾' in html

        r = client.get('/api/v1/me/buddy')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['buddy']['type'] == BUDDY_NUDGE
        assert data['buddy']['message']
        assert data['buddy']['action_url']
        assert data['buddy']['action_label']

        insert_quiz(uid_a, 8, 10)
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_CELEBRATE
        assert '8/10' in r.get_json()['buddy']['message']

        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(days=3)).replace(microsecond=0).isoformat()
        with get_db() as conn:
            conn.execute('DELETE FROM quiz_attempts WHERE user_id = ?', (uid_a,))
            ensure_user_streak(conn, uid_a)
            conn.execute(
                '''
                UPDATE user_streaks
                SET current_streak = 4, longest_streak = 4, last_active_date = ?
                WHERE user_id = ?
                ''',
                (yesterday, uid_a),
            )
            conn.commit()
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_STREAK_RISK
        assert 'streak' in r.get_json()['buddy']['message'].lower()

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
        insert_quiz(uid_a, 1, 10, created_at=old, topic='algebra')
        r = client.get('/api/v1/me/buddy')
        assert r.get_json()['buddy']['type'] == BUDDY_WEAK_TOPIC
        assert r.get_json()['buddy']['action_url']
        off_page = r.get_json()['buddy']
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

        r = client.get('/topic/gcse/maths/algebra')
        assert r.status_code == 200
        assert b'data-buddy-actions' in r.data
        assert b'study-buddy.js' in r.data
        html_lesson = r.data.decode()
        assert 'data-buddy-level="gcse"' in html_lesson
        assert 'data-buddy-subject="maths"' in html_lesson
        assert 'data-buddy-topic="algebra"' in html_lesson
        assert 'study-buddy.js?v=3' in html_lesson
        assert 'Problem Bank build: buddy-embed-v3' in html_lesson
        assert 'pb-buddy-embed-v3' in html_lesson
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
        assert 'pb-buddy-storage' in html_lesson

        logout(client)
        register(client, email_b, handle_b)
        uid_b = user_id_for(handle_b)
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
