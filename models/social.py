import json

from models.avatar import avatar_to_json, parse_avatar
from models.user import User, normalize_handle, utc_now_iso

VISIBILITY_PUBLIC = 'public'
VISIBILITY_FOLLOWERS = 'followers_only'
VISIBILITY_PRIVATE = 'private'
VISIBILITY_CHOICES = (
    VISIBILITY_PUBLIC,
    VISIBILITY_FOLLOWERS,
    VISIBILITY_PRIVATE,
)

ACTIVITY_TOPIC_OPENED = 'topic_opened'
ACTIVITY_QUESTION_GENERATED = 'question_generated'
ACTIVITY_MCQ_ANSWERED = 'mcq_answered'
ACTIVITY_QUIZ_COMPLETED = 'quiz_completed'
ACTIVITY_QUESTION_SHARED = 'question_shared'
ACTIVITY_SUGGESTION_SENT = 'suggestion_sent'
ACTIVITY_LESSON_STEP_COMPLETED = 'lesson_step_completed'

FEED_FILTER_ALL = 'all'
FEED_FILTER_LESSONS = 'lessons'
FEED_FILTER_QUIZZES = 'quizzes'
FEED_FILTER_SHARES = 'shares'
FEED_FILTER_CHOICES = (
    FEED_FILTER_ALL,
    FEED_FILTER_LESSONS,
    FEED_FILTER_QUIZZES,
    FEED_FILTER_SHARES,
)

FEED_EVENT_TYPES = {
    FEED_FILTER_ALL: (
        ACTIVITY_QUIZ_COMPLETED,
        ACTIVITY_LESSON_STEP_COMPLETED,
        ACTIVITY_QUESTION_SHARED,
        ACTIVITY_TOPIC_OPENED,
    ),
    FEED_FILTER_LESSONS: (ACTIVITY_LESSON_STEP_COMPLETED,),
    FEED_FILTER_QUIZZES: (ACTIVITY_QUIZ_COMPLETED,),
    FEED_FILTER_SHARES: (ACTIVITY_QUESTION_SHARED,),
}

FEED_DEFAULT_LIMIT = 50
FEED_MAX_LIMIT = 100
SEARCH_MAX_LIMIT = 50
SEARCH_DEFAULT_LIMIT = 20
SEARCH_MIN_QUERY_LEN = 2


def _like_escape(value):
    return (
        (value or '')
        .replace('\\', '\\\\')
        .replace('%', '\\%')
        .replace('_', '\\_')
    )


def _bool_int(value):
    return 1 if value else 0


def ensure_user_profile(conn, user_id):
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_profile_settings (user_id)
        VALUES (?)
        ''',
        (user_id,),
    )
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_activity_summary (user_id)
        VALUES (?)
        ''',
        (user_id,),
    )
    conn.commit()


def get_profile_settings(conn, user_id):
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        '''
        SELECT profile_visibility, show_member_since, show_last_topic,
               show_last_activity, show_lesson_progress, show_quiz_stats,
               show_shared_questions, auto_share_quiz, auto_share_lesson,
               default_share_visibility, show_study_streak, show_milestones,
               email_weekly_digest, avatar_json, show_accuracy_leaderboard
        FROM user_profile_settings
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    data = dict(row) if row else {}
    data['avatar'] = parse_avatar(data.get('avatar_json'))
    return data


def update_profile_settings(conn, user_id, settings):
    ensure_user_profile(conn, user_id)

    visibility = settings.get('profile_visibility', VISIBILITY_PUBLIC)
    if visibility not in VISIBILITY_CHOICES:
        visibility = VISIBILITY_PUBLIC
    share_visibility = settings.get('default_share_visibility', VISIBILITY_FOLLOWERS)
    if share_visibility not in VISIBILITY_CHOICES:
        share_visibility = VISIBILITY_FOLLOWERS
    if 'avatar' in settings or settings.get('avatar_json'):
        avatar_json = avatar_to_json(
            settings.get('avatar') or parse_avatar(settings.get('avatar_json'))
        )
    else:
        existing = conn.execute(
            'SELECT avatar_json FROM user_profile_settings WHERE user_id = ?',
            (user_id,),
        ).fetchone()
        avatar_json = (existing['avatar_json'] if existing else '') or avatar_to_json({})
    conn.execute(
        '''
        UPDATE user_profile_settings
        SET profile_visibility = ?,
            show_member_since = ?,
            show_last_topic = ?,
            show_last_activity = ?,
            show_lesson_progress = ?,
            show_quiz_stats = ?,
            show_shared_questions = ?,
            auto_share_quiz = ?,
            auto_share_lesson = ?,
            default_share_visibility = ?,
            show_study_streak = ?,
            show_milestones = ?,
            email_weekly_digest = ?,
            avatar_json = ?,
            show_accuracy_leaderboard = ?
        WHERE user_id = ?
        ''',
        (
            visibility,
            _bool_int(settings.get('show_member_since', True)),
            _bool_int(settings.get('show_last_topic', True)),
            _bool_int(settings.get('show_last_activity', True)),
            _bool_int(settings.get('show_lesson_progress', True)),
            _bool_int(settings.get('show_quiz_stats', True)),
            _bool_int(settings.get('show_shared_questions', True)),
            _bool_int(settings.get('auto_share_quiz', False)),
            _bool_int(settings.get('auto_share_lesson', False)),
            share_visibility,
            _bool_int(settings.get('show_study_streak', False)),
            _bool_int(settings.get('show_milestones', False)),
            _bool_int(settings.get('email_weekly_digest', False)),
            avatar_json,
            _bool_int(settings.get('show_accuracy_leaderboard', True)),
            user_id,
        ),
    )
    conn.commit()


def record_activity_event(conn, user_id, event_type, payload, visibility=VISIBILITY_FOLLOWERS):
    if visibility not in VISIBILITY_CHOICES:
        visibility = VISIBILITY_FOLLOWERS
    now = utc_now_iso()
    conn.execute(
        '''
        INSERT INTO user_activity_events (
            user_id, event_type, payload_json, visibility, created_at
        ) VALUES (?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            event_type,
            json.dumps(payload or {}),
            visibility,
            now,
        ),
    )
    conn.commit()


def list_activity_events(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT id, event_type, payload_json, visibility, created_at
        FROM user_activity_events
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('payload_json', None) or '{}'
        try:
            data['payload'] = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data['payload'] = {}
        out.append(data)
    return out


RECENT_PRACTISED_LIMIT = 8
RECENT_PRACTISED_SCAN = 80
RECENT_PRACTISED_EVENTS = (
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_TOPIC_OPENED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_MCQ_ANSWERED,
)


def list_recent_practised_topics(conn, user_id, *, limit=RECENT_PRACTISED_LIMIT, scan=RECENT_PRACTISED_SCAN):
    """Distinct topics the user practised, newest first (for the home chip strip)."""
    rows = conn.execute(
        '''
        SELECT payload_json, created_at
        FROM user_activity_events
        WHERE user_id = ?
          AND event_type IN (?, ?, ?, ?, ?)
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        (user_id, *RECENT_PRACTISED_EVENTS, scan),
    ).fetchall()
    out = []
    seen = set()
    for row in rows:
        try:
            payload = json.loads(row['payload_json'] or '{}')
        except (TypeError, ValueError, json.JSONDecodeError):
            payload = {}
        level = payload.get('level')
        subject = payload.get('subject')
        topic = payload.get('topic')
        if not topic:
            continue
        key = (level, subject, topic)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            'level': level,
            'subject': subject,
            'topic': topic,
            'topic_label': payload.get('topic_label') or '',
            'difficulty': payload.get('difficulty') or '',
            'last_at': row['created_at'],
        })
        if len(out) >= limit:
            break
    return out


def normalize_feed_filter(value):
    if value in FEED_FILTER_CHOICES:
        return value
    return FEED_FILTER_ALL


def list_followed_feed(
    conn,
    viewer_id,
    filter_name=FEED_FILTER_ALL,
    limit=FEED_DEFAULT_LIMIT,
    before_id=None,
):
    """Activity events from users the viewer follows (feed timeline)."""
    filter_name = normalize_feed_filter(filter_name)
    limit = min(max(int(limit), 1), FEED_MAX_LIMIT)
    event_types = FEED_EVENT_TYPES[filter_name]
    placeholders = ','.join('?' * len(event_types))
    before_clause = ''
    params = [viewer_id, viewer_id, viewer_id, VISIBILITY_PRIVATE, *event_types]
    if before_id is not None:
        before_clause = 'AND e.id < ?'
        params.append(int(before_id))
    params.append(limit)
    rows = conn.execute(
        f'''
        SELECT e.id, e.user_id, e.event_type, e.payload_json, e.visibility, e.created_at,
               u.handle AS actor_handle, ups.avatar_json AS actor_avatar_json
        FROM user_activity_events e
        JOIN users u ON u.id = e.user_id
        LEFT JOIN user_profile_settings ups ON ups.user_id = e.user_id
        WHERE e.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
        )
          AND e.user_id NOT IN (
            SELECT blocked_id FROM user_blocks WHERE blocker_id = ?
            UNION
            SELECT blocker_id FROM user_blocks WHERE blocked_id = ?
          )
          AND e.visibility != ?
          AND e.event_type IN ({placeholders})
          {before_clause}
        ORDER BY e.id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('payload_json', None) or '{}'
        try:
            data['payload'] = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data['payload'] = {}
        data['avatar'] = parse_avatar(data.pop('actor_avatar_json', None))
        out.append(data)
    return out


def get_activity_summary(conn, user_id):
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        '''
        SELECT last_topic_level, last_topic_subject, last_topic_topic,
               last_topic_label, last_topic_at,
               last_activity_type, last_activity_level, last_activity_subject,
               last_activity_topic, last_activity_label, last_activity_at
        FROM user_activity_summary
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    return dict(row) if row else {}


def record_topic_opened(conn, user_id, level, subject, topic, topic_label):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_topic_level = ?,
            last_topic_subject = ?,
            last_topic_topic = ?,
            last_topic_label = ?,
            last_topic_at = ?
        WHERE user_id = ?
        ''',
        (level, subject, topic, topic_label or '', now, user_id),
    )
    conn.commit()


def record_question_generated(conn, user_id, level, subject, topic, topic_label, difficulty):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    if difficulty:
        label = f'{label} ({difficulty})'
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_QUESTION_GENERATED,
            level,
            subject,
            topic,
            f'Practised: {label}',
            now,
            user_id,
        ),
    )
    conn.commit()


def record_mcq_answered(conn, user_id, level, subject, topic, topic_label, correct, *,
                        score=None, score_total=None):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    if score_total is not None and score is not None and not correct:
        outcome = f'{score}/{score_total}'
    else:
        outcome = 'Correct' if correct else 'Incorrect'
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_MCQ_ANSWERED,
            level,
            subject,
            topic,
            f'MCQ: {label} — {outcome}',
            now,
            user_id,
        ),
    )
    conn.commit()


def record_quiz_completed(conn, user_id, level, subject, topic, topic_label, score, total):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_QUIZ_COMPLETED,
            level,
            subject,
            topic,
            f'Quiz: {label} — {score}/{total}',
            now,
            user_id,
        ),
    )
    conn.commit()


def is_following(conn, follower_id, following_id):
    if not follower_id or not following_id:
        return False
    row = conn.execute(
        '''
        SELECT 1 FROM follows
        WHERE follower_id = ? AND following_id = ?
        ''',
        (follower_id, following_id),
    ).fetchone()
    return row is not None


def follow_user(conn, follower_id, following_id):
    if follower_id == following_id:
        return False
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT OR IGNORE INTO follows (follower_id, following_id, created_at)
        VALUES (?, ?, ?)
        ''',
        (follower_id, following_id, now),
    )
    conn.commit()
    return cursor.rowcount > 0


def unfollow_user(conn, follower_id, following_id):
    cursor = conn.execute(
        '''
        DELETE FROM follows
        WHERE follower_id = ? AND following_id = ?
        ''',
        (follower_id, following_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def follower_count(conn, user_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM follows WHERE following_id = ?',
        (user_id,),
    ).fetchone()
    return row['n'] if row else 0


def following_count(conn, user_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM follows WHERE follower_id = ?',
        (user_id,),
    ).fetchone()
    return row['n'] if row else 0


def list_followers(conn, user_id, limit=50):
    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at, f.created_at AS followed_at
        FROM follows f
        JOIN users u ON u.id = f.follower_id
        WHERE f.following_id = ?
        ORDER BY f.created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def list_following(conn, user_id, limit=50):
    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at, f.created_at AS followed_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY f.created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def can_view_profile(conn, viewer_id, target_user_id, settings):
    if viewer_id and viewer_id == target_user_id:
        return True
    from models.moderation import is_blocked
    if is_blocked(conn, viewer_id, target_user_id):
        return False
    visibility = settings.get('profile_visibility', VISIBILITY_PUBLIC)
    if visibility == VISIBILITY_PRIVATE:
        return False
    if visibility == VISIBILITY_FOLLOWERS:
        return is_following(conn, viewer_id, target_user_id)
    return True


def get_user_by_handle(conn, handle):
    return User.get_by_handle(conn, handle)


def search_users_by_handle(
    conn,
    query,
    *,
    viewer_id=None,
    limit=SEARCH_DEFAULT_LIMIT,
    exclude_user_id=None,
):
    query = normalize_handle(query)
    if len(query) < SEARCH_MIN_QUERY_LEN:
        return []

    limit = min(max(int(limit), 1), SEARCH_MAX_LIMIT)
    pattern = f'%{_like_escape(query)}%'
    prefix_pattern = f'{_like_escape(query)}%'

    sql = '''
        SELECT id, handle, created_at
        FROM users
        WHERE is_active = 1
          AND handle LIKE ? ESCAPE '\\'
    '''
    params = [pattern]
    if exclude_user_id is not None:
        sql += ' AND id != ?'
        params.append(exclude_user_id)
    sql += " AND handle != 'problem_bot' COLLATE NOCASE"
    sql += '''
        ORDER BY
            CASE
                WHEN handle = ? COLLATE NOCASE THEN 0
                WHEN handle LIKE ? ESCAPE '\\' COLLATE NOCASE THEN 1
                ELSE 2
            END,
            handle COLLATE NOCASE
        LIMIT ?
    '''
    params.extend([query, prefix_pattern, limit])

    rows = conn.execute(sql, params).fetchall()
    results = []
    for row in rows:
        settings = get_profile_settings(conn, row['id'])
        accessible = can_view_profile(conn, viewer_id, row['id'], settings)
        item = {
            'handle': row['handle'],
            'profile_accessible': accessible,
            'avatar': settings.get('avatar') or parse_avatar(None),
        }
        if accessible and settings.get('show_member_since'):
            created = row['created_at'] or ''
            item['member_since'] = created[:10] if created else None
        if viewer_id is not None and viewer_id != row['id']:
            item['viewer_follows'] = is_following(conn, viewer_id, row['id'])
        results.append(item)
    return results


def search_following_by_handle(conn, follower_id, query, *, limit=8):
    """Handles among people the viewer follows (for suggest-to-friend autocomplete)."""
    query = normalize_handle(query)
    if not query:
        return []

    limit = min(max(int(limit), 1), SEARCH_MAX_LIMIT)
    pattern = f'%{_like_escape(query)}%'
    prefix_pattern = f'{_like_escape(query)}%'

    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
          AND u.is_active = 1
          AND u.handle LIKE ? ESCAPE '\\'
        ORDER BY
            CASE
                WHEN u.handle = ? COLLATE NOCASE THEN 0
                WHEN u.handle LIKE ? ESCAPE '\\' COLLATE NOCASE THEN 1
                ELSE 2
            END,
            u.handle COLLATE NOCASE
        LIMIT ?
        ''',
        (follower_id, pattern, query, prefix_pattern, limit),
    ).fetchall()

    results = []
    for row in rows:
        settings = get_profile_settings(conn, row['id'])
        item = {
            'handle': row['handle'],
            'profile_accessible': True,
            'avatar': settings.get('avatar') or parse_avatar(None),
            'viewer_follows': True,
        }
        if settings.get('show_member_since'):
            created = row['created_at'] or ''
            item['member_since'] = created[:10] if created else None
        results.append(item)
    return results


def lesson_progress_summary(conn, user_id, limit=8):
    rows = conn.execute(
        '''
        SELECT level, subject, topic, section_key, section_label,
               completed_keys_json, updated_at
        FROM lesson_progress
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('completed_keys_json', None) or '[]'
        try:
            keys = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            keys = []
        if not isinstance(keys, list):
            keys = []
        data['completed_count'] = len([k for k in keys if isinstance(k, str) and k.strip()])
        out.append(data)
    return out


def quiz_stats_summary(conn, user_id, limit=5):
    rows = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]
