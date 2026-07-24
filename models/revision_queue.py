"""Rule-based spaced revision queue (Phase G3), built on top of weak-topic
analysis (G1). This is intentionally simple/rule-based rather than a full
spaced-repetition algorithm:

- New weak topics are added to the queue with a due date based on how weak
  they currently look (worse accuracy -> sooner due date).
- Existing queue rows keep their due date on sync (so a user's dismiss /
  complete snooze isn't undone the next time the queue is recomputed) but get
  a fresh priority/reason.
- Topics that are no longer weak are dropped from the queue.
"""
from datetime import datetime, timedelta, timezone

from models.weak_topics import analyze_weak_topics

DEFAULT_LIMIT = 8
DUE_TODAY_LIMIT = 3

# Rule-based due intervals (days), keyed by how weak the topic looks right now.
SEVERE_PCT = 60.0
MODERATE_PCT = 80.0
SEVERE_DUE_DAYS = 2
MODERATE_DUE_DAYS = 7
DEFAULT_DUE_DAYS = 4
DISMISS_SNOOZE_DAYS = 3
COMPLETE_SNOOZE_DAYS = 7


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def _now_iso():
    return _now().isoformat()


def _due_in_days(days):
    return (_now() + timedelta(days=days)).isoformat()


def _due_days_for_weak_topic(item):
    pct_candidates = [
        p for p in (item.get('quiz_average_pct'), item.get('mcq_accuracy_pct'))
        if p is not None
    ]
    if not pct_candidates:
        return DEFAULT_DUE_DAYS
    worst_pct = min(pct_candidates)
    if worst_pct < SEVERE_PCT:
        return SEVERE_DUE_DAYS
    if worst_pct < MODERATE_PCT:
        return MODERATE_DUE_DAYS
    return DEFAULT_DUE_DAYS


def sync_revision_queue(conn, user_id, *, limit=DEFAULT_LIMIT):
    """Reconcile the revision queue with the latest weak-topic analysis.

    Call this before reading the queue (profile page / API) — there is no
    background job, so this is a cheap compute-on-read sync instead.
    """
    weak_topics = analyze_weak_topics(conn, user_id, limit=limit)
    weak_keys = {(w['level'], w['subject'], w['topic']) for w in weak_topics}

    existing_rows = conn.execute(
        'SELECT level, subject, topic FROM user_revision_queue WHERE user_id = ?',
        (user_id,),
    ).fetchall()
    existing_keys = {(r['level'], r['subject'], r['topic']) for r in existing_rows}

    now = _now_iso()
    for item in weak_topics:
        key = (item['level'], item['subject'], item['topic'])
        reason = item['reasons'][0] if item.get('reasons') else None
        if key in existing_keys:
            conn.execute(
                '''
                UPDATE user_revision_queue
                SET priority = ?, reason = ?, last_synced_at = ?
                WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
                ''',
                (item['weakness_score'], reason, now, user_id, *key),
            )
        else:
            due_at = _due_in_days(_due_days_for_weak_topic(item))
            conn.execute(
                '''
                INSERT INTO user_revision_queue (
                    user_id, level, subject, topic, priority, reason,
                    due_at, last_synced_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (user_id, *key, item['weakness_score'], reason, due_at, now, now),
            )

    for key in existing_keys - weak_keys:
        conn.execute(
            '''
            DELETE FROM user_revision_queue
            WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
            ''',
            (user_id, *key),
        )
    conn.commit()


def list_revision_queue(conn, user_id, *, limit=DEFAULT_LIMIT, due_only=True):
    """Return revision queue rows, most urgent first.

    due_only=True (default) only returns items due today or overdue —
    this is the "Due today" widget. due_only=False returns the whole queue,
    including items snoozed into the future.
    """
    sql = '''
        SELECT level, subject, topic, priority, reason, due_at, last_completed_at
        FROM user_revision_queue
        WHERE user_id = ?
    '''
    params = [user_id]
    if due_only:
        sql += ' AND due_at <= ?'
        params.append(_now_iso())
    sql += ' ORDER BY priority DESC, due_at ASC LIMIT ?'
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [
        {
            'level': r['level'],
            'subject': r['subject'],
            'topic': r['topic'],
            'priority': r['priority'],
            'reason': r['reason'],
            'due_at': r['due_at'],
            'due_date': (r['due_at'] or '')[:10] or None,
            'last_completed_at': r['last_completed_at'],
        }
        for r in rows
    ]


def _snooze_revision_item(conn, user_id, level, subject, topic, days, *, mark_completed=False):
    row = conn.execute(
        '''
        SELECT 1 FROM user_revision_queue
        WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
        ''',
        (user_id, level, subject, topic),
    ).fetchone()
    if not row:
        return False
    due_at = _due_in_days(days)
    if mark_completed:
        conn.execute(
            '''
            UPDATE user_revision_queue
            SET due_at = ?, last_completed_at = ?
            WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
            ''',
            (due_at, _now_iso(), user_id, level, subject, topic),
        )
    else:
        conn.execute(
            '''
            UPDATE user_revision_queue
            SET due_at = ?
            WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
            ''',
            (due_at, user_id, level, subject, topic),
        )
    conn.commit()
    return True


def dismiss_revision_item(conn, user_id, level, subject, topic):
    """User said 'not now' — push the due date out a few days."""
    return _snooze_revision_item(conn, user_id, level, subject, topic, DISMISS_SNOOZE_DAYS)


def complete_revision_item(conn, user_id, level, subject, topic):
    """User practised the topic — push the due date out further and record it."""
    return _snooze_revision_item(
        conn, user_id, level, subject, topic, COMPLETE_SNOOZE_DAYS, mark_completed=True
    )


def serialize_revision_item(item, *, topic_label=None, topic_url=None, lesson_quiz_url=None):
    """JSON/API shape for one revision queue row."""
    out = {
        'level': item['level'],
        'subject': item['subject'],
        'topic': item['topic'],
        'topic_label': topic_label or item['topic'],
        'priority': item['priority'],
        'reason': item['reason'],
        'due_at': item['due_at'],
        'due_date': item['due_date'],
        'last_completed_at': item['last_completed_at'],
    }
    if topic_url:
        out['topic_url'] = topic_url
    if lesson_quiz_url:
        out['lesson_quiz_url'] = lesson_quiz_url
    return out
