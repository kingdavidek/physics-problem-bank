"""Phase G3 (revision queue) smoke test — run: python scripts/test_phase_g3_smoke.py"""
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models.revision_queue import (  # noqa: E402
    complete_revision_item,
    dismiss_revision_item,
    list_revision_queue,
    sync_revision_queue,
)
from models.user_data import record_generator_mcq_attempt, record_quiz_attempt  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def _past_iso(days_ago=1):
    return (datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=days_ago)).isoformat()


def _force_due_now(conn, user_id, topic):
    """Simulate time passing: push a queue row's due_at into the past so it
    shows up in the due-only view, without waiting on the real due-date
    scheduling rules."""
    conn.execute(
        'UPDATE user_revision_queue SET due_at = ? WHERE user_id = ? AND topic = ?',
        (_past_iso(), user_id, topic),
    )
    conn.commit()


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        r = client.post(
            '/api/v1/auth/register',
            json={
                'email': f'pg3_{suffix}@example.com',
                'handle': f'pg3_{suffix}',
                'password': 'password123',
                'age_confirm': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        body = r.get_json()
        token = body['token']
        user_id = body['user']['id']
        auth = bearer(token)

        with get_db() as conn:
            # Severely weak (quiz average well under 60%) -> flagged weak and
            # queued with a due date, though still a few days out initially.
            record_quiz_attempt(
                conn, user_id, 'gcse', 'maths', 'bidmas', 2, 10,
                ['A'] * 10, [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            # Moderately weak (quiz average between 60-70%) -> also weak, but
            # a longer initial due interval than the severe topic.
            record_quiz_attempt(
                conn, user_id, 'gcse', 'maths', 'algebra', 13, 20,
                ['A'] * 20, [{'question': 'Q', 'correct_answer': 'B'}] * 20,
            )
            # Not weak at all -> should never enter the queue.
            record_quiz_attempt(
                conn, user_id, 'gcse', 'maths', 'surds', 10, 10,
                ['A'] * 10, [{'question': 'Q', 'correct_answer': 'A'}] * 10,
            )

            sync_revision_queue(conn, user_id)
            all_items = list_revision_queue(conn, user_id, limit=10, due_only=False)
            topics = {i['topic'] for i in all_items}
            assert 'bidmas' in topics
            assert 'algebra' in topics
            assert 'surds' not in topics

            # Brand-new items are scheduled a few days out (not nagging the
            # student the instant a topic looks weak), so nothing is due yet.
            assert list_revision_queue(conn, user_id, limit=10, due_only=True) == []

            # bidmas (severe) should have an earlier/equal due date and a
            # higher priority than algebra (moderate).
            by_topic = {i['topic']: i for i in all_items}
            assert by_topic['bidmas']['due_at'] <= by_topic['algebra']['due_at']
            assert by_topic['bidmas']['priority'] >= by_topic['algebra']['priority']

            # Simulate time passing so both are now due, and confirm a
            # re-sync (e.g. from a later page load) does not reset the due
            # date back out into the future.
            _force_due_now(conn, user_id, 'bidmas')
            _force_due_now(conn, user_id, 'algebra')
            sync_revision_queue(conn, user_id)
            due_items = list_revision_queue(conn, user_id, limit=10, due_only=True)
            assert {i['topic'] for i in due_items} == {'bidmas', 'algebra'}

        # GET the due-today queue via API.
        r = client.get('/api/v1/me/revision-queue?limit=10', headers=auth)
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert len(data['revision_queue']) == 2
        top = data['revision_queue'][0]
        assert top['topic'] in ('bidmas', 'algebra')
        assert top['topic_label']
        assert top['topic_url']
        assert 'due_date' in top

        # limit is clamped between 1 and 20.
        r = client.get('/api/v1/me/revision-queue?limit=1', headers=auth)
        assert len(r.get_json()['revision_queue']) == 1

        # Profile page renders the "Due today" widget with a due item.
        r = client.get('/profile', headers=auth)
        assert r.status_code == 200
        assert b'Due today' in r.data

        # Dismiss ("not now") snoozes the item a few days -> disappears from
        # the due-only view.
        r = client.post(
            '/api/v1/me/revision-queue/dismiss',
            json={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['ok'] is True

        r = client.get('/api/v1/me/revision-queue?due_only=1&limit=10', headers=auth)
        due_topics = {i['topic'] for i in r.get_json()['revision_queue']}
        assert due_topics == {'algebra'}

        # Complete ("done") snoozes further out and records last_completed_at.
        r = client.post(
            '/api/v1/me/revision-queue/complete',
            json={'level': 'gcse', 'subject': 'maths', 'topic': 'algebra'},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        with get_db() as conn:
            row = conn.execute(
                'SELECT last_completed_at, due_at FROM user_revision_queue '
                'WHERE user_id = ? AND topic = ?',
                (user_id, 'algebra'),
            ).fetchone()
            assert row['last_completed_at'] is not None
            assert row['due_at'] > _past_iso(days_ago=0)

        # Nothing left due today now.
        r = client.get('/api/v1/me/revision-queue?due_only=1', headers=auth)
        assert r.get_json()['revision_queue'] == []

        # Acting on a topic not currently in the queue -> 404.
        r = client.post(
            '/api/v1/me/revision-queue/dismiss',
            json={'level': 'gcse', 'subject': 'maths', 'topic': 'nonexistent_topic'},
            headers=auth,
        )
        assert r.status_code == 404, r.data
        assert r.get_json()['ok'] is False

        # Missing fields -> 400.
        r = client.post('/api/v1/me/revision-queue/dismiss', json={'level': 'gcse'}, headers=auth)
        assert r.status_code == 400, r.data

        # Direct model-level dismiss/complete on a missing row returns False.
        with get_db() as conn:
            assert dismiss_revision_item(conn, user_id, 'gcse', 'maths', 'nope') is False
            assert complete_revision_item(conn, user_id, 'gcse', 'maths', 'nope') is False

        # Unauthenticated requests are rejected.
        r = client.get('/api/v1/me/revision-queue', headers={'Accept': 'application/json'})
        assert r.status_code in (401, 403), r.data

    print('Phase G3 smoke tests passed.')


if __name__ == '__main__':
    main()
