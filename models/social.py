import json

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
ACTIVITY_QUIZ_COMPLETED = 'quiz_completed'


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
               show_last_activity, show_lesson_progress, show_quiz_stats
        FROM user_profile_settings
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    return dict(row) if row else {}


def update_profile_settings(conn, user_id, settings):
    ensure_user_profile(conn, user_id)
    visibility = settings.get('profile_visibility', VISIBILITY_PUBLIC)
    if visibility not in VISIBILITY_CHOICES:
        visibility = VISIBILITY_PUBLIC
    conn.execute(
        '''
        UPDATE user_profile_settings
        SET profile_visibility = ?,
            show_member_since = ?,
            show_last_topic = ?,
            show_last_activity = ?,
            show_lesson_progress = ?,
            show_quiz_stats = ?
        WHERE user_id = ?
        ''',
        (
            visibility,
            _bool_int(settings.get('show_member_since', True)),
            _bool_int(settings.get('show_last_topic', True)),
            _bool_int(settings.get('show_last_activity', True)),
            _bool_int(settings.get('show_lesson_progress', True)),
            _bool_int(settings.get('show_quiz_stats', True)),
            user_id,
        ),
    )
    conn.commit()


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
    visibility = settings.get('profile_visibility', VISIBILITY_PUBLIC)
    if visibility == VISIBILITY_PRIVATE:
        return False
    if visibility == VISIBILITY_FOLLOWERS:
        return is_following(conn, viewer_id, target_user_id)
    return True


def get_user_by_handle(conn, handle):
    return User.get_by_handle(conn, handle)


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
