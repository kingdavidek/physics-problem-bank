"""Question of the day — one shared MCQ with a friend mini leaderboard."""
import hashlib
from datetime import date

from generators.shared.lesson_quiz import build_lesson_mcq_quiz, topic_supports_lesson_mcq
from models.user import utc_now_iso
from topic_registry import TOPICS


def current_day_key(today=None):
    return (today or date.today()).isoformat()


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
    level, subject, topic, cfg = paths[seed % len(paths)]
    quiz_seed = _day_seed(f'{day_key}-{level}-{subject}-{topic}')
    problems = build_lesson_mcq_quiz(level, subject, topic, cfg, seed=quiz_seed)
    problem = problems[0]
    return {
        'day_key': day_key,
        'level': level,
        'subject': subject,
        'topic': topic,
        'topic_name': cfg.get('name', topic.replace('_', ' ').title()),
        'problem': problem,
        'seed': quiz_seed,
    }


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


def friend_qotd_leaderboard(conn, viewer_id, day_key=None):
    day_key = day_key or current_day_key()
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
