"""Study streaks, milestones, weekly recap, and friend effort leaderboard."""
from datetime import date, timedelta

from models.social import (
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_TOPIC_OPENED,
)
from models.user import utc_now_iso

MILESTONE_FIRST_QUIZ = 'first_quiz'
MILESTONE_FIRST_LESSON = 'first_lesson_step'
MILESTONE_TOPICS_10 = 'topics_10'
MILESTONE_STREAK_7 = 'streak_7'
MILESTONE_STREAK_30 = 'streak_30'
MILESTONE_QUESTIONS_25 = 'questions_25'

MILESTONE_CATALOG = {
    MILESTONE_FIRST_QUIZ: {
        'title': 'First quiz',
        'description': 'Complete your first lesson quiz',
    },
    MILESTONE_FIRST_LESSON: {
        'title': 'Lesson learner',
        'description': 'Complete a lesson quick check',
    },
    MILESTONE_TOPICS_10: {
        'title': 'Broad explorer',
        'description': 'Practise 10 different topics',
    },
    MILESTONE_STREAK_7: {
        'title': 'Week warrior',
        'description': 'Reach a 7-day study streak',
    },
    MILESTONE_STREAK_30: {
        'title': 'Dedicated',
        'description': 'Reach a 30-day study streak',
    },
    MILESTONE_QUESTIONS_25: {
        'title': 'Practice regular',
        'description': 'Generate 25 practice questions',
    },
}

EFFORT_EVENT_TYPES = (
    ACTIVITY_TOPIC_OPENED,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_LESSON_STEP_COMPLETED,
)

EFFORT_WEIGHTS = {
    ACTIVITY_TOPIC_OPENED: 1,
    ACTIVITY_QUESTION_GENERATED: 1,
    ACTIVITY_QUIZ_COMPLETED: 3,
    ACTIVITY_LESSON_STEP_COMPLETED: 2,
}


def ensure_user_streak(conn, user_id):
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_streaks (user_id, current_streak, longest_streak, last_active_date)
        VALUES (?, 0, 0, NULL)
        ''',
        (user_id,),
    )


def record_study_day(conn, user_id, on_date=None):
    """Mark a calendar day as active and update streak counters."""
    ensure_user_streak(conn, user_id)
    day = (on_date or date.today()).isoformat()
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_study_days (user_id, study_date)
        VALUES (?, ?)
        ''',
        (user_id, day),
    )

    row = conn.execute(
        '''
        SELECT current_streak, longest_streak, last_active_date
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    last_active = row['last_active_date']
    current = row['current_streak'] or 0
    longest = row['longest_streak'] or 0

    if last_active == day:
        conn.commit()
        return get_study_streak(conn, user_id)

    if last_active:
        previous = date.fromisoformat(last_active)
        today = date.fromisoformat(day)
        if (today - previous).days == 1:
            current += 1
        else:
            current = 1
    else:
        current = 1

    longest = max(longest, current)
    conn.execute(
        '''
        UPDATE user_streaks
        SET current_streak = ?, longest_streak = ?, last_active_date = ?
        WHERE user_id = ?
        ''',
        (current, longest, day, user_id),
    )
    conn.commit()
    return get_study_streak(conn, user_id)


def get_study_streak(conn, user_id):
    ensure_user_streak(conn, user_id)
    row = conn.execute(
        '''
        SELECT current_streak, longest_streak, last_active_date
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not row:
        return {'current': 0, 'longest': 0, 'last_active_date': None}

    current = row['current_streak'] or 0
    last_active = row['last_active_date']
    if last_active:
        last_day = date.fromisoformat(last_active)
        gap = (date.today() - last_day).days
        if gap > 1:
            current = 0

    return {
        'current': current,
        'longest': row['longest_streak'] or 0,
        'last_active_date': last_active,
    }


def _has_milestone(conn, user_id, milestone_key):
    row = conn.execute(
        '''
        SELECT 1 FROM user_milestones
        WHERE user_id = ? AND milestone_key = ?
        ''',
        (user_id, milestone_key),
    ).fetchone()
    return row is not None


def _award_milestone(conn, user_id, milestone_key):
    if _has_milestone(conn, user_id, milestone_key):
        return False
    conn.execute(
        '''
        INSERT INTO user_milestones (user_id, milestone_key, earned_at)
        VALUES (?, ?, ?)
        ''',
        (user_id, milestone_key, utc_now_iso()),
    )
    return True


def _distinct_topics_count(conn, user_id):
    row = conn.execute(
        '''
        SELECT COUNT(DISTINCT
            json_extract(payload_json, '$.level') || '|' ||
            json_extract(payload_json, '$.subject') || '|' ||
            json_extract(payload_json, '$.topic')
        ) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND event_type IN (?, ?, ?, ?)
          AND json_extract(payload_json, '$.topic') IS NOT NULL
        ''',
        (
            user_id,
            ACTIVITY_TOPIC_OPENED,
            ACTIVITY_QUESTION_GENERATED,
            ACTIVITY_QUIZ_COMPLETED,
            ACTIVITY_LESSON_STEP_COMPLETED,
        ),
    ).fetchone()
    return row['n'] if row else 0


def evaluate_milestones(conn, user_id):
    """Award any newly earned milestones; returns list of newly earned keys."""
    streak = get_study_streak(conn, user_id)
    earned = []

    quiz_count = conn.execute(
        'SELECT COUNT(*) AS n FROM quiz_attempts WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if quiz_count >= 1 and _award_milestone(conn, user_id, MILESTONE_FIRST_QUIZ):
        earned.append(MILESTONE_FIRST_QUIZ)

    lesson_count = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM lesson_progress
        WHERE user_id = ?
          AND completed_keys_json IS NOT NULL
          AND completed_keys_json != '[]'
        ''',
        (user_id,),
    ).fetchone()['n']
    if lesson_count >= 1 and _award_milestone(conn, user_id, MILESTONE_FIRST_LESSON):
        earned.append(MILESTONE_FIRST_LESSON)

    if _distinct_topics_count(conn, user_id) >= 10:
        if _award_milestone(conn, user_id, MILESTONE_TOPICS_10):
            earned.append(MILESTONE_TOPICS_10)

    question_count = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM user_activity_events
        WHERE user_id = ? AND event_type = ?
        ''',
        (user_id, ACTIVITY_QUESTION_GENERATED),
    ).fetchone()['n']
    if question_count >= 25 and _award_milestone(conn, user_id, MILESTONE_QUESTIONS_25):
        earned.append(MILESTONE_QUESTIONS_25)

    if streak['longest'] >= 7 and _award_milestone(conn, user_id, MILESTONE_STREAK_7):
        earned.append(MILESTONE_STREAK_7)
    if streak['longest'] >= 30 and _award_milestone(conn, user_id, MILESTONE_STREAK_30):
        earned.append(MILESTONE_STREAK_30)

    if earned:
        conn.commit()
    return earned


def list_user_milestones(conn, user_id):
    rows = conn.execute(
        '''
        SELECT milestone_key, earned_at
        FROM user_milestones
        WHERE user_id = ?
        ORDER BY earned_at ASC
        ''',
        (user_id,),
    ).fetchall()
    out = []
    for row in rows:
        key = row['milestone_key']
        meta = MILESTONE_CATALOG.get(key, {})
        out.append({
            'key': key,
            'title': meta.get('title', key),
            'description': meta.get('description', ''),
            'earned_at': row['earned_at'],
        })
    return out


def get_weekly_recap(conn, user_id, days=7):
    """In-app weekly summary for the last `days` calendar days (inclusive)."""
    start_day = (date.today() - timedelta(days=days - 1)).isoformat()

    active_days = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM user_study_days
        WHERE user_id = ? AND study_date >= ?
        ''',
        (user_id, start_day),
    ).fetchone()['n']

    topics = conn.execute(
        '''
        SELECT COUNT(DISTINCT
            json_extract(payload_json, '$.level') || '|' ||
            json_extract(payload_json, '$.subject') || '|' ||
            json_extract(payload_json, '$.topic')
        ) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN (?, ?, ?, ?)
          AND json_extract(payload_json, '$.topic') IS NOT NULL
        ''',
        (
            user_id,
            start_day,
            ACTIVITY_TOPIC_OPENED,
            ACTIVITY_QUESTION_GENERATED,
            ACTIVITY_QUIZ_COMPLETED,
            ACTIVITY_LESSON_STEP_COMPLETED,
        ),
    ).fetchone()['n']

    best_quiz = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ? AND created_at >= ?
        ORDER BY (1.0 * score / total) DESC, score DESC, created_at DESC
        LIMIT 1
        ''',
        (user_id, start_day),
    ).fetchone()

    activity_total = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN (?, ?, ?, ?)
        ''',
        (
            user_id,
            start_day,
            *EFFORT_EVENT_TYPES,
        ),
    ).fetchone()['n']

    recap = {
        'days': days,
        'active_days': active_days,
        'topics_practised': topics,
        'activity_count': activity_total,
        'best_quiz': None,
    }
    if best_quiz:
        recap['best_quiz'] = {
            'level': best_quiz['level'],
            'subject': best_quiz['subject'],
            'topic': best_quiz['topic'],
            'score': best_quiz['score'],
            'total': best_quiz['total'],
            'created_at': best_quiz['created_at'],
        }
    return recap


def _effort_score_since(conn, user_id, since_iso):
    placeholders = ','.join('?' * len(EFFORT_EVENT_TYPES))
    rows = conn.execute(
        f'''
        SELECT event_type, COUNT(*) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN ({placeholders})
        GROUP BY event_type
        ''',
        (user_id, since_iso, *EFFORT_EVENT_TYPES),
    ).fetchall()
    score = 0
    for row in rows:
        score += EFFORT_WEIGHTS.get(row['event_type'], 1) * row['n']
    return score


def friend_effort_leaderboard(conn, viewer_id, days=7):
    """Effort-based ranking for people the viewer follows, plus the viewer."""
    since_day = (date.today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'

    following = conn.execute(
        '''
        SELECT u.id, u.handle
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY u.handle COLLATE NOCASE
        ''',
        (viewer_id,),
    ).fetchall()

    viewer = conn.execute(
        'SELECT id, handle FROM users WHERE id = ?',
        (viewer_id,),
    ).fetchone()

    participants = {row['id']: row['handle'] for row in following}
    if viewer:
        participants[viewer['id']] = viewer['handle']

    ranked = []
    for user_id, handle in participants.items():
        ranked.append({
            'user_id': user_id,
            'handle': handle,
            'score': _effort_score_since(conn, user_id, since_iso),
            'is_viewer': user_id == viewer_id,
        })

    ranked.sort(key=lambda item: (-item['score'], item['handle'].lower()))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
    return ranked
