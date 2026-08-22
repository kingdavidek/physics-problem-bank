"""Topic lesson-complete / ninja / master status and 10-question quizzes.

Run: python scripts/test_topic_status_smoke.py
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.gamification import evaluate_milestones, list_user_milestones  # noqa: E402
from models.quicktest import QUICKTEST_LENGTH, build_quicktest_problems  # noqa: E402
from models.topic_status import (  # noqa: E402
    aggregate_badge_key,
    compute_topic_status,
    topic_badge_key,
)
from models.user import utc_now_iso  # noqa: E402
from topic_registry import TOPICS  # noqa: E402


def _dt(days_ago=0, now=None):
    now = now or datetime.now(timezone.utc)
    return (now - timedelta(days=days_ago)).replace(microsecond=0).isoformat()


def _quiz(score, total=10, days_ago=0, now=None):
    return {'score': score, 'total': total, 'created_at': _dt(days_ago, now)}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'ts_{suffix}@example.com',
            'handle': f'ts_{suffix}'[:20],
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    body = r.get_json()
    return body['token'], body['user']['id']


def insert_lesson(conn, user_id, topic, keys, step_total, subject='maths'):
    conn.execute(
        '''
        INSERT INTO lesson_progress (
            user_id, level, subject, topic, section_key, section_label,
            completed_keys_json, step_total, updated_at
        ) VALUES (?, 'gcse', ?, ?, ?, '', ?, ?, ?)
        ''',
        (
            user_id,
            subject,
            topic,
            keys[-1] if keys else '',
            json.dumps(keys),
            step_total,
            utc_now_iso(),
        ),
    )


def insert_quiz(conn, user_id, topic, score, total, created_at, subject='maths'):
    conn.execute(
        '''
        INSERT INTO quiz_attempts (
            user_id, level, subject, topic, score, total,
            answers_json, created_at
        ) VALUES (?, 'gcse', ?, ?, ?, ?, '[]', ?)
        ''',
        (user_id, subject, topic, score, total, created_at),
    )


def main():
    now = datetime(2026, 8, 22, 12, 0, tzinfo=timezone.utc)
    keys = ['step-0', 'step-1', 'step-2']

    empty = compute_topic_status([], 3, [], now=now)
    assert empty['lesson_complete'] is False
    assert empty['ninja'] is False
    assert empty['master_active'] is False

    done = compute_topic_status(keys, 3, [], now=now)
    assert done['lesson_complete'] is True
    assert done['ninja'] is False
    assert done['mastery'] == 0.34

    ninja = compute_topic_status(keys, 3, [_quiz(10, now=now)], now=now)
    assert ninja['ninja'] is True
    assert ninja['master_active'] is False
    assert ninja['master_ever'] is False

    almost = compute_topic_status(
        keys, 3, [_quiz(10, days_ago=2, now=now), _quiz(7, days_ago=1, now=now)], now=now
    )
    assert almost['ninja'] is True
    assert almost['master_active'] is False

    master = compute_topic_status(
        keys,
        3,
        [_quiz(10, days_ago=2, now=now), _quiz(10, days_ago=1, now=now)],
        now=now,
    )
    assert master['ninja'] is True
    assert master['master_ever'] is True
    assert master['master_active'] is True
    assert master['mastery'] == 1.0

    expired = compute_topic_status(
        keys,
        3,
        [_quiz(10, days_ago=120, now=now), _quiz(10, days_ago=119, now=now)],
        now=now,
    )
    assert expired['ninja'] is True
    assert expired['master_ever'] is True
    assert expired['master_active'] is False

    extended = compute_topic_status(
        keys,
        3,
        [
            _quiz(10, days_ago=100, now=now),
            _quiz(10, days_ago=99, now=now),
            _quiz(10, days_ago=10, now=now),
        ],
        now=now,
    )
    assert extended['master_active'] is True

    short_quiz = compute_topic_status(keys, 3, [_quiz(7, total=7, now=now)], now=now)
    assert short_quiz['ninja'] is False

    problems, _cfg = build_quicktest_problems(
        'gcse', 'maths', 'bidmas', 'standard', 'foundational', TOPICS
    )
    assert len(problems) == QUICKTEST_LENGTH == 10

    with app.app_context():
        with app.test_client() as client:
            token, user_id = register(client, 'stat1')
            with get_db() as conn:
                insert_lesson(conn, user_id, 'bidmas', keys, 3)
                conn.commit()
                earned = evaluate_milestones(conn, user_id)
                assert topic_badge_key('completed', 'gcse', 'maths', 'bidmas') in earned
                assert topic_badge_key('ninja', 'gcse', 'maths', 'bidmas') not in earned

                insert_quiz(conn, user_id, 'bidmas', 10, 10, _dt(2, now))
                conn.commit()
                earned = evaluate_milestones(conn, user_id)
                assert topic_badge_key('ninja', 'gcse', 'maths', 'bidmas') in earned
                assert topic_badge_key('master', 'gcse', 'maths', 'bidmas') not in earned

                insert_quiz(conn, user_id, 'bidmas', 10, 10, _dt(1, now))
                conn.commit()
                earned = evaluate_milestones(conn, user_id)
                assert topic_badge_key('master', 'gcse', 'maths', 'bidmas') in earned

                listed = {item['key']: item for item in list_user_milestones(conn, user_id)}
                assert listed[topic_badge_key('completed', 'gcse', 'maths', 'bidmas')]['title']
                assert 'ninja' in listed[topic_badge_key('ninja', 'gcse', 'maths', 'bidmas')]['title'].lower()

            token2, user_id2 = register(client, 'stat2')
            with get_db() as conn:
                for index in range(5):
                    slug = f'topic{index}'
                    insert_lesson(
                        conn, user_id2, slug, ['step-0'], 1, subject='maths'
                    )
                conn.commit()
                earned = evaluate_milestones(conn, user_id2)
                assert aggregate_badge_key('completed', 5) in earned
                assert aggregate_badge_key('completed', 10) not in earned

            r = client.get('/topics')
            assert r.status_code == 200
            body = r.data.decode()
            assert 'lessons' in body
            assert 'ninja' in body

    print('Topic status + 10-question quiz smoke tests passed.')


if __name__ == '__main__':
    main()
