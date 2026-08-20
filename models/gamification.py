"""Study streaks, milestones, weekly recap, and friend effort/accuracy leaderboards."""
from datetime import date, datetime, timedelta, timezone
import sqlite3

from models.avatar import attach_avatars
from models.social import (
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_TOPIC_OPENED,
)
from models.user import utc_now_iso


def _utc_today():
    return datetime.now(timezone.utc).date()

MILESTONE_FIRST_QUIZ = 'first_quiz'
MILESTONE_FIRST_LESSON = 'first_lesson_step'
MILESTONE_TOPICS_10 = 'topics_10'
MILESTONE_STREAK_7 = 'streak_7'
MILESTONE_STREAK_30 = 'streak_30'
MILESTONE_QUESTIONS_25 = 'questions_25'
MILESTONE_QOTD_FIRST = 'qotd_first'
MILESTONE_QOTD_7 = 'qotd_7'
MILESTONE_QUESTIONS_50 = 'questions_50'
MILESTONE_ACCURACY_TOP_FRIEND = 'accuracy_top_friend'

MILESTONE_CATALOG = {
    MILESTONE_FIRST_QUIZ: {
        'title': 'First quiz',
        'description': 'Complete your first lesson quiz',
        'emoji': '📝',
    },
    MILESTONE_FIRST_LESSON: {
        'title': 'Lesson learner',
        'description': 'Complete a lesson quick check',
        'emoji': '📖',
    },
    MILESTONE_TOPICS_10: {
        'title': 'Broad explorer',
        'description': 'Practise 10 different topics',
        'emoji': '🧭',
    },
    MILESTONE_STREAK_7: {
        'title': 'Week warrior',
        'description': 'Reach a 7-day study streak',
        'emoji': '🔥',
    },
    MILESTONE_STREAK_30: {
        'title': 'Dedicated',
        'description': 'Reach a 30-day study streak',
        'emoji': '💪',
    },
    MILESTONE_QUESTIONS_25: {
        'title': 'Practice regular',
        'description': 'Generate 25 practice questions',
        'emoji': '✏️',
    },
    MILESTONE_QOTD_FIRST: {
        'title': 'Daily starter',
        'description': 'Answer the question of the day',
        'emoji': '☀️',
    },
    MILESTONE_QOTD_7: {
        'title': 'Seven days of questions',
        'description': 'Answer the question of the day on 7 different days',
        'emoji': '📅',
    },
    MILESTONE_QUESTIONS_50: {
        'title': 'Practice veteran',
        'description': 'Generate 50 practice questions',
        'emoji': '🏅',
    },
    MILESTONE_ACCURACY_TOP_FRIEND: {
        'title': 'Top of the class',
        'description': 'Rank first among friends on weekly quiz accuracy',
        'emoji': '🥇',
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


def _iso_week_key(day):
    year, week, _ = day.isocalendar()
    return f'{year}-W{week:02d}'


def _grant_weekly_freeze(conn, user_id, today):
    week_key = _iso_week_key(today)
    row = conn.execute(
        '''
        SELECT freeze_available, freeze_week_key
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not row:
        return
    if row['freeze_week_key'] != week_key:
        conn.execute(
            '''
            UPDATE user_streaks
            SET freeze_available = 1, freeze_week_key = ?
            WHERE user_id = ?
            ''',
            (week_key, user_id),
        )


def _freeze_covers(conn, user_id, freeze_date):
    row = conn.execute(
        '''
        SELECT 1 FROM user_streak_freezes
        WHERE user_id = ? AND freeze_date = ?
        LIMIT 1
        ''',
        (user_id, freeze_date),
    ).fetchone()
    return row is not None


def _consume_freeze(conn, user_id, freeze_date):
    conn.execute(
        '''
        INSERT INTO user_streak_freezes (user_id, freeze_date, used_at)
        VALUES (?, ?, ?)
        ''',
        (user_id, freeze_date, utc_now_iso()),
    )
    conn.execute(
        '''
        UPDATE user_streaks
        SET freeze_available = 0
        WHERE user_id = ?
        ''',
        (user_id,),
    )


def _freeze_used_dates(conn, user_id, *, as_of=None):
    today = as_of or _utc_today()
    since = (today - timedelta(days=6)).isoformat()
    rows = conn.execute(
        '''
        SELECT freeze_date
        FROM user_streak_freezes
        WHERE user_id = ? AND freeze_date >= ?
        ORDER BY freeze_date ASC
        ''',
        (user_id, since),
    ).fetchall()
    return [row['freeze_date'] for row in rows]


def _streak_row(conn, user_id):
    return conn.execute(
        '''
        SELECT current_streak, longest_streak, last_active_date,
               freeze_available, freeze_week_key
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()


def ensure_user_streak(conn, user_id, on_date=None):
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_streaks (
            user_id, current_streak, longest_streak, last_active_date,
            freeze_available, freeze_week_key
        )
        VALUES (?, 0, 0, NULL, 1, NULL)
        ''',
        (user_id,),
    )
    _grant_weekly_freeze(conn, user_id, on_date or _utc_today())


def record_study_day(conn, user_id, on_date=None):
    """Mark a calendar day as active and update streak counters."""
    today = on_date or _utc_today()
    ensure_user_streak(conn, user_id, on_date=today)
    day = today.isoformat()
    _grant_weekly_freeze(conn, user_id, today)
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_study_days (user_id, study_date)
        VALUES (?, ?)
        ''',
        (user_id, day),
    )

    row = _streak_row(conn, user_id)
    last_active = row['last_active_date']
    current = row['current_streak'] or 0
    longest = row['longest_streak'] or 0
    freeze_available = int(row['freeze_available'] or 0)

    if last_active == day:
        conn.commit()
        return get_study_streak(conn, user_id, as_of=today)

    if last_active:
        previous = date.fromisoformat(last_active)
        gap_days = (today - previous).days
        if gap_days == 1:
            current += 1
        elif gap_days == 2 and freeze_available:
            missed_day = (previous + timedelta(days=1)).isoformat()
            _consume_freeze(conn, user_id, missed_day)
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
    return get_study_streak(conn, user_id, as_of=today)


def get_study_streak(conn, user_id, as_of=None):
    today = as_of or _utc_today()
    ensure_user_streak(conn, user_id, on_date=today)
    _grant_weekly_freeze(conn, user_id, today)
    row = _streak_row(conn, user_id)
    if not row:
        return {
            'current': 0,
            'longest': 0,
            'last_active_date': None,
            'freeze_available': 1,
            'freeze_used_dates': [],
        }

    current = row['current_streak'] or 0
    last_active = row['last_active_date']
    freeze_available = int(row['freeze_available'] or 0)
    if last_active:
        last_day = date.fromisoformat(last_active)
        gap_days = (today - last_day).days
        if gap_days > 1:
            missed_days = gap_days - 1
            if missed_days == 1:
                missed_day = (last_day + timedelta(days=1)).isoformat()
                if not _freeze_covers(conn, user_id, missed_day) and not freeze_available:
                    current = 0
            else:
                current = 0

    return {
        'current': current,
        'longest': row['longest_streak'] or 0,
        'last_active_date': last_active,
        'freeze_available': freeze_available,
        'freeze_used_dates': _freeze_used_dates(conn, user_id, as_of=today),
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


def _weekly_answered_marks(conn, user_id, days=7):
    """Quiz + generator-MCQ marks possible for this user in the last `days` UTC days."""
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'
    stats = _accuracy_stats_since(conn, [user_id], since_iso)
    item = stats.get(user_id) or {}
    return int(item.get('possible') or 0)


def _maybe_award_accuracy_top_friend(conn, user_id):
    """Award Top of the class only when cheap guards pass, then the full friend board.

    Skips the leaderboard query when the badge is already held or the user has
    fewer than 10 answered questions this week. Needs at least two participants
    with a score (friends-only; a lone user never qualifies).
    """
    if _has_milestone(conn, user_id, MILESTONE_ACCURACY_TOP_FRIEND):
        return False
    if _weekly_answered_marks(conn, user_id) < 10:
        return False
    board = friend_accuracy_leaderboard(conn, user_id, days=7)
    scored = [item for item in board if item.get('accuracy_pct') is not None]
    if len(scored) < 2:
        return False
    viewer = next((item for item in board if item.get('is_viewer')), None)
    if not viewer or viewer.get('rank') != 1:
        return False
    return _award_milestone(conn, user_id, MILESTONE_ACCURACY_TOP_FRIEND)


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
    if question_count >= 50 and _award_milestone(conn, user_id, MILESTONE_QUESTIONS_50):
        earned.append(MILESTONE_QUESTIONS_50)

    if streak['longest'] >= 7 and _award_milestone(conn, user_id, MILESTONE_STREAK_7):
        earned.append(MILESTONE_STREAK_7)
    if streak['longest'] >= 30 and _award_milestone(conn, user_id, MILESTONE_STREAK_30):
        earned.append(MILESTONE_STREAK_30)

    qotd_days = conn.execute(
        'SELECT COUNT(DISTINCT day_key) AS n FROM qotd_attempts WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if qotd_days >= 1 and _award_milestone(conn, user_id, MILESTONE_QOTD_FIRST):
        earned.append(MILESTONE_QOTD_FIRST)
    if qotd_days >= 7 and _award_milestone(conn, user_id, MILESTONE_QOTD_7):
        earned.append(MILESTONE_QOTD_7)

    if _maybe_award_accuracy_top_friend(conn, user_id):
        earned.append(MILESTONE_ACCURACY_TOP_FRIEND)

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
            'emoji': meta.get('emoji', '★'),
            'earned_at': row['earned_at'],
        })
    return out


def get_weekly_recap(conn, user_id, days=7):
    """In-app weekly summary for the last `days` calendar days (inclusive)."""
    start_day = (_utc_today() - timedelta(days=days - 1)).isoformat()

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
    scores = _effort_scores_since(conn, [user_id], since_iso)
    return scores.get(user_id, 0)


def weekly_effort_xp(conn, user_id, days=7):
    """Effort points (displayed as XP) for the last N UTC days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    return _effort_score_since(conn, user_id, since)


def xp_level_from_points(xp):
    """Simple level curve: L2 at 50 XP, L3 at 200, L4 at 450, …"""
    xp = max(0, int(xp or 0))
    if xp <= 0:
        return 1
    return max(1, int((xp / 50) ** 0.5))


def _effort_scores_since(conn, user_ids, since_iso):
    """Batch effort scores for many users (avoids N+1 on friend leaderboard)."""
    ids = [int(uid) for uid in user_ids if uid is not None]
    scores = {uid: 0 for uid in ids}
    if not ids:
        return scores
    type_ph = ','.join('?' * len(EFFORT_EVENT_TYPES))
    user_ph = ','.join('?' * len(ids))
    rows = conn.execute(
        f'''
        SELECT user_id, event_type, COUNT(*) AS n
        FROM user_activity_events
        WHERE user_id IN ({user_ph})
          AND created_at >= ?
          AND event_type IN ({type_ph})
        GROUP BY user_id, event_type
        ''',
        (*ids, since_iso, *EFFORT_EVENT_TYPES),
    ).fetchall()
    for row in rows:
        scores[row['user_id']] = (
            scores.get(row['user_id'], 0)
            + EFFORT_WEIGHTS.get(row['event_type'], 1) * row['n']
        )
    return scores


def friend_effort_leaderboard(conn, viewer_id, days=7):
    """Effort-based ranking for people the viewer follows, plus the viewer."""
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
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

    scores = _effort_scores_since(conn, participants.keys(), since_iso)
    ranked = []
    for user_id, handle in participants.items():
        ranked.append({
            'user_id': user_id,
            'handle': handle,
            'score': scores.get(user_id, 0),
            'is_viewer': user_id == viewer_id,
        })

    ranked.sort(key=lambda item: (-item['score'], item['handle'].lower()))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
    attach_avatars(conn, ranked)
    return ranked


def _follow_graph_participants(conn, viewer_id):
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
    return participants


def _accuracy_stats_since(conn, user_ids, since_iso):
    stats = {
        uid: {'earned': 0, 'possible': 0, 'quiz_n': 0, 'mcq_n': 0}
        for uid in user_ids
    }
    if not user_ids:
        return stats
    ids = list(user_ids)
    placeholders = ','.join('?' * len(ids))
    for row in conn.execute(
        f'''
        SELECT user_id,
               COALESCE(SUM(score), 0) AS earned,
               COALESCE(SUM(total), 0) AS possible,
               COUNT(*) AS n
        FROM quiz_attempts
        WHERE user_id IN ({placeholders})
          AND created_at >= ?
        GROUP BY user_id
        ''',
        (*ids, since_iso),
    ).fetchall():
        item = stats[row['user_id']]
        item['earned'] += int(row['earned'] or 0)
        item['possible'] += int(row['possible'] or 0)
        item['quiz_n'] = int(row['n'] or 0)
    for row in conn.execute(
        f'''
        SELECT user_id,
               COALESCE(SUM(
                   CASE WHEN COALESCE(score_total, 0) > 0
                        THEN COALESCE(score, 0)
                        ELSE correct END
               ), 0) AS earned,
               COALESCE(SUM(
                   CASE WHEN COALESCE(score_total, 0) > 0
                        THEN score_total
                        ELSE 1 END
               ), 0) AS possible,
               COUNT(*) AS n
        FROM generator_mcq_attempts
        WHERE user_id IN ({placeholders})
          AND created_at >= ?
        GROUP BY user_id
        ''',
        (*ids, since_iso),
    ).fetchall():
        item = stats[row['user_id']]
        item['earned'] += int(row['earned'] or 0)
        item['possible'] += int(row['possible'] or 0)
        item['mcq_n'] = int(row['n'] or 0)
    return stats


def friend_accuracy_leaderboard(conn, viewer_id, days=7):
    """Weekly quiz+MCQ accuracy among people the viewer follows, plus the viewer.

    Accuracy = (lesson-quiz marks earned + generator-MCQ marks earned)
    / (lesson-quiz marks possible + generator-MCQ marks possible) over the last
    ``days`` UTC days. Users who opted out of the accuracy board are hidden from
    everyone except themselves. No global ranking.
    """
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'
    participants = _follow_graph_participants(conn, viewer_id)
    if not participants:
        return []

    ids = list(participants.keys())
    placeholders = ','.join('?' * len(ids))
    opted_in = {uid: True for uid in ids}
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

    visible_ids = [
        uid for uid in ids
        if uid == viewer_id or opted_in.get(uid, True)
    ]
    stats = _accuracy_stats_since(conn, visible_ids, since_iso)
    ranked = []
    for user_id in visible_ids:
        item_stats = stats.get(user_id) or {'earned': 0, 'possible': 0, 'quiz_n': 0, 'mcq_n': 0}
        possible = item_stats['possible']
        accuracy = round(100.0 * item_stats['earned'] / possible, 1) if possible else None
        ranked.append({
            'user_id': user_id,
            'handle': participants[user_id],
            'accuracy_pct': accuracy,
            'earned': item_stats['earned'],
            'possible': possible,
            'quiz_attempts': item_stats['quiz_n'],
            'mcq_attempts': item_stats['mcq_n'],
            'is_viewer': user_id == viewer_id,
        })

    ranked.sort(key=lambda item: (
        item['accuracy_pct'] is None,
        -(item['accuracy_pct'] if item['accuracy_pct'] is not None else -1),
        -(item['possible'] or 0),
        item['handle'].lower(),
    ))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
    attach_avatars(conn, ranked)
    return ranked
