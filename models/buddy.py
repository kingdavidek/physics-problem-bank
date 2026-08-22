"""Alien buddy prompt (engagement E3.1 / E5.1). Message types plus a fallback nudge."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from generators.shared.lesson_quiz import topic_supports_lesson_mcq
from models.gamification import get_study_streak, milestone_meta
from models.moderation import is_blocked
from models.qotd import get_daily_question
from models.social import list_following
from models.weak_topics import analyze_weak_topics
from topic_registry import TOPICS

BUDDY_MILESTONE = 'milestone'
BUDDY_CELEBRATE = 'celebrate'
BUDDY_QOTD_NUDGE = 'qotd_nudge'
BUDDY_STREAK_RISK = 'streak_risk'
BUDDY_WEAK_TOPIC = 'weak_topic'
BUDDY_FRIEND_CHALLENGE = 'friend_challenge'
BUDDY_NUDGE = 'nudge'

BUDDY_TYPES = (
    BUDDY_MILESTONE,
    BUDDY_CELEBRATE,
    BUDDY_QOTD_NUDGE,
    BUDDY_STREAK_RISK,
    BUDDY_WEAK_TOPIC,
    BUDDY_FRIEND_CHALLENGE,
    BUDDY_NUDGE,
)

BUDDY_FACES = {
    BUDDY_MILESTONE: '🎉',
    BUDDY_CELEBRATE: '😄',
    BUDDY_QOTD_NUDGE: '❓',
    BUDDY_STREAK_RISK: '🔥',
    BUDDY_WEAK_TOPIC: '🤔',
    BUDDY_FRIEND_CHALLENGE: '🤝',
    BUDDY_NUDGE: '👾',
}


def _utc_now():
    return datetime.now(timezone.utc)


def _finish(prompt):
    buddy_type = prompt.get('type', BUDDY_NUDGE)
    prompt['face'] = BUDDY_FACES.get(buddy_type, '👾')
    return prompt


def _recent_milestone(conn, user_id, now):
    cutoff = (now - timedelta(hours=24)).replace(microsecond=0).isoformat()
    row = conn.execute(
        '''
        SELECT milestone_key, earned_at
        FROM user_milestones
        WHERE user_id = ? AND earned_at >= ?
        ORDER BY earned_at DESC
        LIMIT 1
        ''',
        (user_id, cutoff),
    ).fetchone()
    if not row:
        return None
    key = row['milestone_key']
    meta = milestone_meta(key)
    return {
        'key': key,
        'title': meta.get('title', key.replace('_', ' ').title()),
        'emoji': meta.get('emoji', '🏅'),
        'earned_at': row['earned_at'],
    }


def _has_qotd_today(conn, user_id, day_key):
    row = conn.execute(
        'SELECT 1 FROM qotd_attempts WHERE user_id = ? AND day_key = ? LIMIT 1',
        (user_id, day_key),
    ).fetchone()
    return row is not None


def _has_activity_today(conn, user_id, today_iso):
    row = conn.execute(
        'SELECT 1 FROM user_study_days WHERE user_id = ? AND study_date = ? LIMIT 1',
        (user_id, today_iso),
    ).fetchone()
    if row:
        return True
    if _latest_quiz_today(conn, user_id, today_iso):
        return True
    row = conn.execute(
        '''
        SELECT 1 FROM generator_mcq_attempts
        WHERE user_id = ? AND created_at >= ?
        LIMIT 1
        ''',
        (user_id, f'{today_iso}T00:00:00'),
    ).fetchone()
    return row is not None


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


def _mcq_count_today(conn, user_id, today_iso, level, subject, topic):
    row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM generator_mcq_attempts
        WHERE user_id = ?
          AND level = ? AND subject = ? AND topic = ?
          AND created_at >= ?
        ''',
        (user_id, level, subject, topic, f'{today_iso}T00:00:00'),
    ).fetchone()
    return int(row['n'] or 0) if row else 0


def _same_topic(level, subject, topic, other_level, other_subject, other_topic):
    if not (level and topic and other_level and other_topic):
        return False
    if str(level).lower() != str(other_level).lower():
        return False
    if str(topic).lower() != str(other_topic).lower():
        return False
    left = str(subject or '').lower()
    right = str(other_subject or '').lower()
    if left and right and left != right:
        return False
    return True


def _quiz_available(level, subject, topic):
    if level != 'gcse' or subject not in ('maths', 'cs'):
        return False
    try:
        return topic_supports_lesson_mcq(TOPICS[level][subject][topic])
    except KeyError:
        return False


def _sent_challenge_recently(conn, user_id, now, *, days=7):
    cutoff = (now - timedelta(days=days)).replace(microsecond=0).isoformat()
    row = conn.execute(
        '''
        SELECT 1 FROM quiz_challenges
        WHERE creator_id = ? AND created_at >= ?
        LIMIT 1
        ''',
        (user_id, cutoff),
    ).fetchone()
    return row is not None


def _friend_challenge_target(conn, user_id):
    for friend in list_following(conn, user_id, limit=50):
        friend_id = friend.get('id')
        handle = friend.get('handle')
        if not friend_id or not handle:
            continue
        if is_blocked(conn, user_id, friend_id):
            continue
        return handle
    return None


def _friend_challenge_prompt(conn, user_id, now):
    if _sent_challenge_recently(conn, user_id, now):
        return None
    handle = _friend_challenge_target(conn, user_id)
    if not handle:
        return None
    try:
        qotd = get_daily_question(day_key=now.date().isoformat())
    except ValueError:
        return None
    return _finish({
        'type': BUDDY_FRIEND_CHALLENGE,
        'message': f"Challenge @{handle} to today's topic?",
        'detail': 'Friend challenge',
        'action_kind': 'challenge',
        'friend_handle': handle,
        'action_label': 'Send challenge',
        'level': qotd.get('level'),
        'subject': qotd.get('subject'),
        'topic': qotd.get('topic'),
    })


def _weak_topic_prompt(item, topic_label, *, on_topic, practised_mcq_today):
    level = item['level']
    subject = item['subject']
    topic = item['topic']
    quiz_ok = _quiz_available(level, subject, topic)

    if not on_topic:
        return _finish({
            'type': BUDDY_WEAK_TOPIC,
            'message': f'{topic_label} looks shaky. A short practice set will help.',
            'detail': 'Weak topic',
            'action_kind': 'topic',
            'level': level,
            'subject': subject,
            'topic': topic,
            'action_label': 'Practise this',
            'actions': [
                {
                    'kind': 'link',
                    'action_kind': 'topic',
                    'label': 'Practise this',
                    'level': level,
                    'subject': subject,
                    'topic': topic,
                },
            ],
        })

    if practised_mcq_today:
        message = (
            f'Nice — want a quiz on {topic_label} to check it sticks?'
            if quiz_ok
            else f'Nice work on {topic_label}. A few more questions will help it stick.'
        )
    else:
        message = (
            f'Try a few questions on {topic_label}, or take a quiz to check it sticks.'
            if quiz_ok
            else f'Try a few practice questions on {topic_label}.'
        )

    actions = []
    mcq_action = {
        'kind': 'link',
        'action_kind': 'generate_mcq',
        'label': 'Practise MCQ',
        'level': level,
        'subject': subject,
        'topic': topic,
    }
    quiz_action = {
        'kind': 'link',
        'action_kind': 'lesson_quiz',
        'label': 'Take a quiz',
        'level': level,
        'subject': subject,
        'topic': topic,
    }
    if practised_mcq_today and quiz_ok:
        actions.append(quiz_action)
        actions.append(mcq_action)
    else:
        actions.append(mcq_action)
        if quiz_ok:
            actions.append(quiz_action)
    actions.append({
        'kind': 'stay',
        'label': f'Keep learning {topic_label}',
    })

    primary = next((action for action in actions if action.get('kind') == 'link'), actions[0])
    return _finish({
        'type': BUDDY_WEAK_TOPIC,
        'message': message,
        'detail': 'Weak topic',
        'action_kind': primary.get('action_kind', 'topic'),
        'level': level,
        'subject': subject,
        'topic': topic,
        'action_label': primary.get('label', 'Practise this'),
        'actions': actions,
    })


def build_buddy_prompt(
    conn,
    user_id,
    *,
    now=None,
    topic_label_fn=None,
    current_level=None,
    current_subject=None,
    current_topic=None,
):
    """Pick one short encouragement for the corner widget. Never raises."""
    now = now or _utc_now()
    today = now.date()
    today_iso = today.isoformat()
    label_fn = topic_label_fn or (lambda _level, _subject, topic: str(topic).replace('_', ' '))

    milestone = _recent_milestone(conn, user_id, now)
    if milestone:
        title = milestone['title']
        emoji = milestone['emoji']
        return _finish({
            'type': BUDDY_MILESTONE,
            'message': f'New badge: {title} {emoji}',
            'detail': 'New badge',
            'action_kind': 'milestone',
            'action_label': 'View badges',
            'milestone_key': milestone['key'],
        })

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
        return _finish({
            'type': BUDDY_CELEBRATE,
            'message': message,
            'detail': 'Today’s quiz',
            'action_kind': 'topic',
            'level': quiz['level'],
            'subject': quiz['subject'],
            'topic': quiz['topic'],
            'action_label': 'Practise again',
        })

    if (
        not _has_qotd_today(conn, user_id, today_iso)
        and _has_activity_today(conn, user_id, today_iso)
    ):
        return _finish({
            'type': BUDDY_QOTD_NUDGE,
            'message': 'Today’s question is still open.',
            'detail': 'Daily question',
            'action_kind': 'qotd',
            'action_label': 'Today’s question',
        })

    streak = get_study_streak(conn, user_id)
    last_active = streak.get('last_active_date')
    if streak.get('current', 0) >= 1 and last_active:
        last_day = last_active[:10]
        yesterday = (today - timedelta(days=1)).isoformat()
        if last_day == yesterday:
            days = int(streak['current'])
            if streak.get('freeze_available'):
                message = (
                    'You have one skip left this week — but a question now keeps the run honest.'
                )
            else:
                message = f'Your {days}-day streak is at risk. Open a topic today to keep it.'
            return _finish({
                'type': BUDDY_STREAK_RISK,
                'message': message,
                'detail': 'Streak reminder',
                'action_kind': 'topics',
                'action_label': 'Browse topics',
            })

    weak = analyze_weak_topics(conn, user_id, limit=1)
    if weak:
        item = weak[0]
        topic_label = label_fn(item['level'], item['subject'], item['topic'])
        on_topic = _same_topic(
            item['level'],
            item['subject'],
            item['topic'],
            current_level,
            current_subject,
            current_topic,
        )
        practised_mcq = False
        if on_topic:
            practised_mcq = _mcq_count_today(
                conn,
                user_id,
                today_iso,
                item['level'],
                item['subject'],
                item['topic'],
            ) >= 1
        return _weak_topic_prompt(
            item,
            topic_label,
            on_topic=on_topic,
            practised_mcq_today=practised_mcq,
        )

    friend_challenge = _friend_challenge_prompt(conn, user_id, now)
    if friend_challenge:
        return friend_challenge

    return _finish({
        'type': BUDDY_NUDGE,
        'message': 'Ready when you are. Try today’s question or pick a topic.',
        'detail': 'Practice nudge',
        'action_kind': 'qotd',
        'action_label': 'Today’s question',
    })
