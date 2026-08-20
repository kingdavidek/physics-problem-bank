"""Question of the day — one shared difficult MCQ with a friend mini leaderboard."""
import hashlib
import random
import sqlite3
from datetime import date, datetime, timedelta, timezone

from generators.shared.lesson_quiz import build_single_mcq, topic_supports_lesson_mcq
from models.user import utc_now_iso
from topic_registry import TOPICS

QOTD_DIFFICULTY = 'difficult'


def current_day_key(today=None):
    if today is None:
        today = datetime.now(timezone.utc).date()
    elif isinstance(today, str):
        today = date.fromisoformat(today)
    return today.isoformat()


def qotd_window_day_keys(*, days=7, end_day=None):
    """UTC day_key strings for the last ``days`` days ending on ``end_day`` (inclusive)."""
    if end_day is None:
        end = datetime.now(timezone.utc).date()
    elif isinstance(end_day, str):
        end = date.fromisoformat(end_day)
    else:
        end = end_day
    count = max(1, int(days))
    return [(end - timedelta(days=offset)).isoformat() for offset in range(count - 1, -1, -1)]


def _day_seed(day_key):
    digest = hashlib.sha256(f'qotd-{day_key}'.encode('utf-8')).hexdigest()
    return int(digest[:8], 16)


def list_mcq_topic_paths():
    paths = []
    for level, subjects in TOPICS.items():
        for subject, topics in subjects.items():
            for slug, cfg in topics.items():
                if topic_supports_lesson_mcq(cfg):
                    paths.append((level, subject, slug, cfg))
    paths.sort()
    return paths


def get_daily_question(*, day_key=None):
    day_key = day_key or current_day_key()
    paths = list_mcq_topic_paths()
    if not paths:
        raise ValueError('no_mcq_topics')
    seed = _day_seed(day_key)
    rng_state = random.getstate()
    try:
        random.seed(seed)
        start = seed % len(paths)
        for offset in range(len(paths)):
            level, subject, topic, cfg = paths[(start + offset) % len(paths)]
            problem = build_single_mcq(
                level,
                subject,
                topic,
                cfg,
                difficulty=QOTD_DIFFICULTY,
                rng=random,
            )
            if problem and problem.get('options') and problem.get('correct_answer'):
                return {
                    'day_key': day_key,
                    'level': level,
                    'subject': subject,
                    'topic': topic,
                    'topic_name': cfg.get('name', topic.replace('_', ' ').title()),
                    'problem': problem,
                    'seed': seed,
                }
        raise ValueError('no_mcq_topics')
    finally:
        random.setstate(rng_state)


def get_user_attempt(conn, user_id, day_key):
    row = conn.execute(
        '''
        SELECT user_id, day_key, correct, answer, answered_at
        FROM qotd_attempts
        WHERE user_id = ? AND day_key = ?
        ''',
        (user_id, day_key),
    ).fetchone()
    return dict(row) if row else None


def record_qotd_answer(conn, user_id, day_key, answer, correct):
    existing = get_user_attempt(conn, user_id, day_key)
    if existing:
        raise ValueError('already_answered')
    conn.execute(
        '''
        INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (user_id, day_key, 1 if correct else 0, (answer or '').strip().upper()[:1], utc_now_iso()),
    )
    conn.commit()


def _qotd_participants(conn, viewer_id):
    viewer = conn.execute(
        'SELECT id, handle FROM users WHERE id = ?',
        (viewer_id,),
    ).fetchone()
    following = conn.execute(
        '''
        SELECT u.id, u.handle
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ''',
        (viewer_id,),
    ).fetchall()
    participants = {viewer['id']: viewer['handle']} if viewer else {}
    for row in following:
        participants[row['id']] = row['handle']
    return participants


def _qotd_visible_participant_ids(conn, viewer_id, participants):
    ids = list(participants.keys())
    if not ids:
        return []
    opted_in = {uid: True for uid in ids}
    placeholders = ','.join('?' * len(ids))
    try:
        rows = conn.execute(
            f'''
            SELECT user_id, show_accuracy_leaderboard
            FROM user_profile_settings
            WHERE user_id IN ({placeholders})
            ''',
            ids,
        ).fetchall()
        for row in rows:
            opted_in[row['user_id']] = bool(row['show_accuracy_leaderboard'])
    except sqlite3.OperationalError:
        pass
    return [uid for uid in ids if uid == viewer_id or opted_in.get(uid, True)]


def friend_qotd_leaderboard(conn, viewer_id, day_key=None):
    day_key = day_key or current_day_key()
    participants = _qotd_participants(conn, viewer_id)
    if not participants:
        return []

    placeholders = ','.join('?' * len(participants))
    rows = conn.execute(
        f'''
        SELECT u.id AS user_id, u.handle, a.correct, a.answered_at
        FROM qotd_attempts a
        JOIN users u ON u.id = a.user_id
        WHERE a.day_key = ? AND a.user_id IN ({placeholders})
        ORDER BY a.correct DESC, a.answered_at ASC, u.handle COLLATE NOCASE ASC
        ''',
        (day_key, *participants.keys()),
    ).fetchall()

    ranked = []
    for index, row in enumerate(rows, start=1):
        ranked.append({
            'rank': index,
            'user_id': row['user_id'],
            'handle': row['handle'],
            'correct': bool(row['correct']),
            'answered_at': row['answered_at'],
            'is_viewer': row['user_id'] == viewer_id,
        })
    return ranked


def friend_qotd_week_leaderboard(conn, viewer_id, *, days=7, end_day=None):
    """Viewer + follows ranked by correct QOTD answers over the last ``days`` UTC days."""
    day_keys = qotd_window_day_keys(days=days, end_day=end_day)
    participants = _qotd_participants(conn, viewer_id)
    if not participants:
        return []

    visible_ids = _qotd_visible_participant_ids(conn, viewer_id, participants)
    if not visible_ids:
        return []

    day_placeholders = ','.join('?' * len(day_keys))
    user_placeholders = ','.join('?' * len(visible_ids))
    rows = conn.execute(
        f'''
        SELECT user_id, day_key, correct, answered_at
        FROM qotd_attempts
        WHERE day_key IN ({day_placeholders}) AND user_id IN ({user_placeholders})
        ''',
        (*day_keys, *visible_ids),
    ).fetchall()

    stats = {
        user_id: {
            'correct_days': 0,
            'answered_days': 0,
            'earliest_answered_at': None,
        }
        for user_id in visible_ids
    }
    for row in rows:
        user_id = row['user_id']
        if user_id not in stats:
            continue
        stats[user_id]['answered_days'] += 1
        if row['correct']:
            stats[user_id]['correct_days'] += 1
        answered_at = row['answered_at']
        if answered_at:
            prev = stats[user_id]['earliest_answered_at']
            if prev is None or answered_at < prev:
                stats[user_id]['earliest_answered_at'] = answered_at

    ranked = []
    days_in_window = len(day_keys)
    for user_id in visible_ids:
        item = stats[user_id]
        ranked.append({
            'user_id': user_id,
            'handle': participants[user_id],
            'correct_days': item['correct_days'],
            'answered_days': item['answered_days'],
            'days_in_window': days_in_window,
            'is_viewer': user_id == viewer_id,
            '_earliest': item['earliest_answered_at'] or '9999',
        })

    ranked.sort(key=lambda item: (
        -item['correct_days'],
        -item['answered_days'],
        item['_earliest'],
        item['handle'].lower(),
    ))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
        del item['_earliest']
    return ranked
