"""Subject-access / portability export (UK GDPR Art 15/20 / S0.5)."""
from models.user import utc_now_iso

SCHEMA_VERSION = 1

_TABLES = (
    ('saved_problems', 'user_id'),
    ('lesson_progress', 'user_id'),
    ('quiz_attempts', 'user_id'),
    ('generator_mcq_attempts', 'user_id'),
    ('user_activity_summary', 'user_id'),
    ('user_activity_events', 'user_id'),
    ('shared_questions', 'user_id'),
    ('email_digest_log', 'user_id'),
    ('user_streaks', 'user_id'),
    ('user_streak_freezes', 'user_id'),
    ('user_study_days', 'user_id'),
    ('user_milestones', 'user_id'),
    ('user_notifications', 'user_id'),
    ('user_revision_queue', 'user_id'),
    ('user_wrong_answer_reflections', 'user_id'),
    ('user_revision_plans', 'user_id'),
    ('qotd_attempts', 'user_id'),
)


def _rows(conn, sql, params=()):
    found = conn.execute(sql, params).fetchall()
    return [dict(row) for row in found]


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def build_user_export(conn, user_id):
    user = conn.execute(
        '''
        SELECT id, email, handle, created_at, last_login_at, is_active, email_verified_at
        FROM users WHERE id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not user:
        return None

    settings_row = conn.execute(
        'SELECT * FROM user_profile_settings WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    settings = dict(settings_row) if settings_row else {}

    practice = {}
    for table, column in _TABLES:
        if not _table_exists(conn, table):
            continue
        practice[table] = _rows(conn, f'SELECT * FROM {table} WHERE {column} = ?', (user_id,))

    following = _rows(
        conn,
        '''
        SELECT u.handle, f.created_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY f.created_at
        ''',
        (user_id,),
    ) if _table_exists(conn, 'follows') else []
    followers = _rows(
        conn,
        '''
        SELECT u.handle, f.created_at
        FROM follows f
        JOIN users u ON u.id = f.follower_id
        WHERE f.following_id = ?
        ORDER BY f.created_at
        ''',
        (user_id,),
    ) if _table_exists(conn, 'follows') else []

    tokens = []
    if _table_exists(conn, 'api_tokens'):
        tokens = _rows(
            conn,
            '''
            SELECT id, label, created_at, last_used_at, expires_at
            FROM api_tokens WHERE user_id = ?
            ''',
            (user_id,),
        )

    return {
        'generated_at': utc_now_iso(),
        'schema_version': SCHEMA_VERSION,
        'account': dict(user),
        'settings': settings,
        'practice': practice,
        'social': {
            'following': following,
            'followers': followers,
        },
        'notes': {
            'api_sessions': tokens,
        },
    }
