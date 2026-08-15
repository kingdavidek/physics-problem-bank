"""Alien buddy prompt (engagement E3.1). Three message types plus a fallback nudge."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.gamification import get_study_streak
from models.weak_topics import analyze_weak_topics

BUDDY_CELEBRATE = 'celebrate'
BUDDY_STREAK_RISK = 'streak_risk'
BUDDY_WEAK_TOPIC = 'weak_topic'
BUDDY_NUDGE = 'nudge'

BUDDY_TYPES = (BUDDY_CELEBRATE, BUDDY_STREAK_RISK, BUDDY_WEAK_TOPIC, BUDDY_NUDGE)


def _utc_now():
    return datetime.now(timezone.utc)


def _latest_quiz_today(conn, user_id, today_iso):
    return conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ? AND created_at >= ?
        ORDER BY created_at DESC
        LIMIT 1
        ''',
        (user_id, f'{today_iso}T00:00:00'),
    ).fetchone()


def build_buddy_prompt(conn, user_id, *, now=None, topic_label_fn=None):
    """Pick one short encouragement for the corner widget. Never raises."""
    now = now or _utc_now()
    today = now.date()
    today_iso = today.isoformat()
    label_fn = topic_label_fn or (lambda _level, _subject, topic: str(topic).replace('_', ' '))

    quiz = _latest_quiz_today(conn, user_id, today_iso)
    if quiz and (quiz['total'] or 0) > 0:
        topic_label = label_fn(quiz['level'], quiz['subject'], quiz['topic'])
        score = int(quiz['score'] or 0)
        total = int(quiz['total'] or 0)
        pct = (100.0 * score / total) if total else 0.0
        if pct >= 70:
            message = f'Nice work — {score}/{total} on {topic_label}.'
        else:
            message = f'Quiz logged on {topic_label} ({score}/{total}). Another go?'
        return {
            'type': BUDDY_CELEBRATE,
            'message': message,
            'detail': 'Today’s quiz',
            'action_kind': 'topic',
            'level': quiz['level'],
            'subject': quiz['subject'],
            'topic': quiz['topic'],
            'action_label': 'Practise again',
        }

    streak = get_study_streak(conn, user_id)
    last_active = streak.get('last_active_date')
    if streak.get('current', 0) >= 1 and last_active:
        last_day = last_active[:10]
        yesterday = (today - timedelta(days=1)).isoformat()
        if last_day == yesterday:
            days = int(streak['current'])
            return {
                'type': BUDDY_STREAK_RISK,
                'message': f'Your {days}-day streak is at risk. Open a topic today to keep it.',
                'detail': 'Streak reminder',
                'action_kind': 'topics',
                'action_label': 'Browse topics',
            }

    weak = analyze_weak_topics(conn, user_id, limit=1)
    if weak:
        item = weak[0]
        topic_label = label_fn(item['level'], item['subject'], item['topic'])
        return {
            'type': BUDDY_WEAK_TOPIC,
            'message': f'{topic_label} looks shaky. A short practice set will help.',
            'detail': 'Weak topic',
            'action_kind': 'topic',
            'level': item['level'],
            'subject': item['subject'],
            'topic': item['topic'],
            'action_label': 'Practise this',
        }

    return {
        'type': BUDDY_NUDGE,
        'message': 'Ready when you are. Try today’s question or pick a topic.',
        'detail': 'Practice nudge',
        'action_kind': 'qotd',
        'action_label': 'Today’s question',
    }
