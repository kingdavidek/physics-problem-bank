"""Persistent problem variant queues for logged-in API clients."""
import json

from models.user import utc_now_iso


def get_problem_queue(conn, user_id, queue_key):
    row = conn.execute(
        '''
        SELECT queue_json, queue_index, variant_name, updated_at
        FROM user_problem_queues
        WHERE user_id = ? AND queue_key = ?
        ''',
        (user_id, queue_key),
    ).fetchone()
    if not row:
        return None
    try:
        queue = json.loads(row['queue_json'] or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        queue = []
    if not isinstance(queue, list):
        queue = []
    return {
        'queue': [str(name) for name in queue],
        'index': int(row['queue_index'] or 0),
        'variant_name': row['variant_name'],
        'updated_at': row['updated_at'],
    }


def save_problem_queue(conn, user_id, queue_key, queue, index, variant_name):
    now = utc_now_iso()
    conn.execute(
        '''
        INSERT INTO user_problem_queues (
            user_id, queue_key, queue_json, queue_index, variant_name, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, queue_key) DO UPDATE SET
            queue_json = excluded.queue_json,
            queue_index = excluded.queue_index,
            variant_name = excluded.variant_name,
            updated_at = excluded.updated_at
        ''',
        (
            user_id,
            queue_key,
            json.dumps(list(queue or [])),
            int(index),
            variant_name,
            now,
        ),
    )
    conn.commit()


def clear_problem_queue(conn, user_id, queue_key=None):
    if queue_key:
        conn.execute(
            'DELETE FROM user_problem_queues WHERE user_id = ? AND queue_key = ?',
            (user_id, queue_key),
        )
    else:
        conn.execute(
            'DELETE FROM user_problem_queues WHERE user_id = ?',
            (user_id,),
        )
    conn.commit()
