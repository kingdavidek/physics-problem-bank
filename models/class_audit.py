"""Class activity log (G8 Phase 5). Handles only — never emails, T3, or answer keys."""
from __future__ import annotations

import json

from models.user import utc_now_iso

MAX_AUDIT_EVENTS_PER_CLASS = 200

ALLOWED_META_KEYS = frozenset({
    'name',
    'via',
    'topic',
    'question_count',
    'recipient_count',
    'assignment_id',
    'invite_id',
})

DELETED_ACTOR_LABEL = 'a deleted account'


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def user_handle(conn, user_id):
    if user_id is None:
        return None
    row = conn.execute(
        'SELECT handle FROM users WHERE id = ?',
        (user_id,),
    ).fetchone()
    return row['handle'] if row else None


def _looks_like_email(value):
    if not isinstance(value, str):
        return False
    if '@' not in value or '.' not in value:
        return False
    local, _, domain = value.partition('@')
    return bool(local) and '.' in domain and ' ' not in value.strip()


def _safe_meta(meta):
    if not isinstance(meta, dict):
        return {}
    out = {}
    for key, value in meta.items():
        if key not in ALLOWED_META_KEYS:
            continue
        if isinstance(value, bool) or value is None:
            out[key] = value
        elif isinstance(value, int) and not isinstance(value, bool):
            out[key] = value
        elif isinstance(value, float):
            out[key] = value
        elif isinstance(value, str):
            if _looks_like_email(value):
                continue
            out[key] = value[:120]
    return out


def _trim_audit(conn, class_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM class_audit_events WHERE class_id = ?',
        (class_id,),
    ).fetchone()
    extra = int(row['n'] or 0) - MAX_AUDIT_EVENTS_PER_CLASS
    if extra <= 0:
        return
    conn.execute(
        '''
        DELETE FROM class_audit_events
        WHERE id IN (
            SELECT id FROM class_audit_events
            WHERE class_id = ?
            ORDER BY id ASC
            LIMIT ?
        )
        ''',
        (class_id, extra),
    )


def log_class_event(conn, class_id, actor_id, action, *, subject_handle=None, meta=None):
    if not _table_exists(conn, 'class_audit_events'):
        return None
    action = (action or '').strip()[:64]
    if not action:
        return None
    handle = (subject_handle or '').strip()[:64] or None
    if handle and _looks_like_email(handle):
        handle = None
    payload = json.dumps(_safe_meta(meta), default=str)
    cursor = conn.execute(
        '''
        INSERT INTO class_audit_events (
            class_id, actor_id, action, subject_handle, meta_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (class_id, actor_id, action, handle, payload, utc_now_iso()),
    )
    _trim_audit(conn, class_id)
    conn.commit()
    return cursor.lastrowid


def list_class_audit(conn, teacher_id, class_id, *, limit=MAX_AUDIT_EVENTS_PER_CLASS):
    from models.classes import teacher_owns_class

    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    if not _table_exists(conn, 'class_audit_events'):
        return []
    limit = min(max(int(limit), 1), MAX_AUDIT_EVENTS_PER_CLASS)
    rows = conn.execute(
        '''
        SELECT e.id, e.class_id, e.actor_id, e.action, e.subject_handle,
               e.meta_json, e.created_at, u.handle AS actor_handle
        FROM class_audit_events e
        LEFT JOIN users u ON u.id = e.actor_id
        WHERE e.class_id = ?
        ORDER BY e.id DESC
        LIMIT ?
        ''',
        (class_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def serialize_audit_event(row):
    if not row:
        return None
    try:
        meta = json.loads(row.get('meta_json') or '{}')
    except (TypeError, ValueError, json.JSONDecodeError):
        meta = {}
    if not isinstance(meta, dict):
        meta = {}
    actor = row.get('actor_handle') or DELETED_ACTOR_LABEL
    return {
        'id': row['id'],
        'action': row['action'],
        'actor_handle': actor,
        'subject_handle': row.get('subject_handle'),
        'meta': _safe_meta(meta),
        'created_at': row.get('created_at'),
    }
