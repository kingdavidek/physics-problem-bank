"""E5.2 milestone badges smoke — run: python scripts/test_milestones_smoke.py"""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.gamification import (  # noqa: E402
    MILESTONE_ACCURACY_TOP_FRIEND,
    MILESTONE_QOTD_7,
    MILESTONE_QOTD_FIRST,
    MILESTONE_QUESTIONS_25,
    MILESTONE_QUESTIONS_50,
    evaluate_milestones,
    list_user_milestones,
)
from models.social import ACTIVITY_QUESTION_GENERATED, follow_user  # noqa: E402
from models.user import utc_now_iso  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'ms_{suffix}@example.com',
            'handle': f'ms_{suffix}',
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    body = r.get_json()
    return body['token'], body['user']['id']


def milestone_keys(conn, user_id):
    return [item['key'] for item in list_user_milestones(conn, user_id)]


def insert_qotd_days(conn, user_id, n):
    today = datetime.now(timezone.utc).date()
    now = utc_now_iso()
    for i in range(n):
        day_key = (today - timedelta(days=i)).isoformat()
        conn.execute(
            '''
            INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
            VALUES (?, ?, 1, 'A', ?)
            ''',
            (user_id, day_key, now),
        )
    conn.commit()


def insert_question_events(conn, user_id, n):
    now = utc_now_iso()
    conn.executemany(
        '''
        INSERT INTO user_activity_events (
            user_id, event_type, payload_json, visibility, created_at
        ) VALUES (?, ?, '{}', 'followers_only', ?)
        ''',
        [(user_id, ACTIVITY_QUESTION_GENERATED, now)] * n,
    )
    conn.commit()


def insert_quiz(conn, user_id, score, total):
    conn.execute(
        '''
        INSERT INTO quiz_attempts (
            user_id, level, subject, topic, score, total, answers_json, problems_json, created_at
        ) VALUES (?, 'gcse', 'maths', 'algebra', ?, ?, '[]', '[]', ?)
        ''',
        (user_id, score, total, utc_now_iso()),
    )
    conn.commit()


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_a, uid_a = register(client, f'a_{suffix}')
        token_b, uid_b = register(client, f'b_{suffix}')
        token_c, uid_c = register(client, f'c_{suffix}')

        with get_db() as conn:
            insert_qotd_days(conn, uid_a, 1)
            first = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QOTD_FIRST in first
            assert MILESTONE_QOTD_7 not in first
            listed = list_user_milestones(conn, uid_a)
            by_key = {item['key']: item for item in listed}
            assert by_key[MILESTONE_QOTD_FIRST]['title'] == 'Daily starter'
            assert by_key[MILESTONE_QOTD_FIRST]['emoji'] == '☀️'
            again = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QOTD_FIRST not in again
            assert milestone_keys(conn, uid_a).count(MILESTONE_QOTD_FIRST) == 1

            today = datetime.now(timezone.utc).date()
            now = utc_now_iso()
            for i in range(1, 6):
                conn.execute(
                    '''
                    INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
                    VALUES (?, ?, 1, 'A', ?)
                    ''',
                    (uid_a, (today - timedelta(days=i)).isoformat(), now),
                )
            conn.commit()
            six = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QOTD_7 not in six
            conn.execute(
                '''
                INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
                VALUES (?, ?, 1, 'A', ?)
                ''',
                (uid_a, (today - timedelta(days=6)).isoformat(), now),
            )
            conn.commit()
            seven = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QOTD_7 in seven
            assert evaluate_milestones(conn, uid_a) == []
            assert milestone_keys(conn, uid_a).count(MILESTONE_QOTD_7) == 1

            insert_question_events(conn, uid_a, 49)
            forty_nine = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QUESTIONS_25 in forty_nine
            assert MILESTONE_QUESTIONS_50 not in forty_nine
            insert_question_events(conn, uid_a, 1)
            fifty = evaluate_milestones(conn, uid_a)
            assert MILESTONE_QUESTIONS_50 in fifty
            listed = list_user_milestones(conn, uid_a)
            by_key = {item['key']: item for item in listed}
            assert by_key[MILESTONE_QUESTIONS_50]['title'] == 'Practice veteran'
            assert by_key[MILESTONE_QUESTIONS_50]['emoji'] == '🏅'
            assert evaluate_milestones(conn, uid_a) == []
            assert milestone_keys(conn, uid_a).count(MILESTONE_QUESTIONS_50) == 1

            follow_user(conn, uid_a, uid_b)
            follow_user(conn, uid_b, uid_a)
            insert_quiz(conn, uid_a, 10, 10)
            insert_quiz(conn, uid_b, 8, 10)
            a_earned = evaluate_milestones(conn, uid_a)
            b_earned = evaluate_milestones(conn, uid_b)
            assert MILESTONE_ACCURACY_TOP_FRIEND in a_earned
            assert MILESTONE_ACCURACY_TOP_FRIEND not in b_earned
            assert MILESTONE_ACCURACY_TOP_FRIEND in milestone_keys(conn, uid_a)
            assert MILESTONE_ACCURACY_TOP_FRIEND not in milestone_keys(conn, uid_b)
            assert evaluate_milestones(conn, uid_a) == []
            assert milestone_keys(conn, uid_a).count(MILESTONE_ACCURACY_TOP_FRIEND) == 1

            insert_quiz(conn, uid_c, 10, 10)
            c_earned = evaluate_milestones(conn, uid_c)
            assert MILESTONE_ACCURACY_TOP_FRIEND not in c_earned
            assert MILESTONE_ACCURACY_TOP_FRIEND not in milestone_keys(conn, uid_c)

        r = client.get('/api/v1/me/gamification', headers=bearer(token_a))
        assert r.status_code == 200, r.data
        body = r.get_json()
        api_keys = [item['key'] for item in body['milestones']]
        assert MILESTONE_QOTD_FIRST in api_keys
        assert MILESTONE_QOTD_7 in api_keys
        assert MILESTONE_QUESTIONS_50 in api_keys
        assert MILESTONE_ACCURACY_TOP_FRIEND in api_keys
        top = next(item for item in body['milestones'] if item['key'] == MILESTONE_ACCURACY_TOP_FRIEND)
        assert top['emoji'] == '🥇'
        assert top['title'] == 'Top of the class'

        r = client.get('/profile', headers=bearer(token_a))
        assert r.status_code == 200
        html = r.data.decode()
        assert 'id="milestones"' in html
        assert 'Daily starter' in html
        assert '☀️' in html
        assert 'Practice veteran' in html
        assert 'Top of the class' in html

        r = client.get('/api/v1/me/gamification', headers=bearer(token_c))
        assert r.status_code == 200
        c_keys = [item['key'] for item in r.get_json()['milestones']]
        assert MILESTONE_ACCURACY_TOP_FRIEND not in c_keys

    print('Milestone (E5.2) smoke tests passed.')


if __name__ == '__main__':
    main()
