import os
import secrets
from datetime import date, timedelta
import urllib.error
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines from a .env file (does not override existing env vars)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key, value)


_load_env_file(_ROOT / ".env")

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash, g, send_from_directory, Response
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from jinja2.exceptions import TemplateNotFound
from markupsafe import Markup
import sqlite3
import json
import uuid
from topics_data import TOPIC_CONTENT
from topic_registry import TOPICS
from generators.shared.lesson_quiz import (
    build_lesson_mcq_quiz,
    topic_supports_lesson_mcq,
)
from generators.alevel.magnetism import (
    aqa_mag_faradays_law,
    aqa_mag_flux_linkage,
    aqa_mag_motor_effect,
    aqa_mag_particle_path,
    aqa_mag_transformers,
)
from generators.alevel.photoelectric import (
    aqa_pe_basic,
    aqa_pe_debroglie,
    aqa_pe_photoelectric_equation,
    aqa_pe_stopping_potential,
    aqa_pe_threshold_frequency,
)
from generators.shared.utils import format_light_markdown
from generators.shared.lesson_assist import (
    daily_limit_ip,
    daily_limit_session,
    generate_explanation,
    is_enabled as lesson_assist_enabled,
    user_facing_error,
    validate_payload,
)
from generators.shared.variant_utils import (
    normalize_mode,
    resolve_variant_callable,
    variant_is_randomizable,
)
from models.user import (
    User,
    can_access_difficulty,
    normalize_email,
    normalize_handle,
    validate_email,
    validate_handle,
    validate_password,
)
from models.social import (
    VISIBILITY_CHOICES,
    VISIBILITY_FOLLOWERS,
    VISIBILITY_PUBLIC,
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_MCQ_ANSWERED,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUESTION_SHARED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_SUGGESTION_SENT,
    ACTIVITY_TOPIC_OPENED,
    can_view_profile,
    ensure_user_profile,
    follow_user,
    follower_count,
    following_count,
    get_activity_summary,
    get_profile_settings,
    get_user_by_handle,
    is_following,
    lesson_progress_summary,
    list_activity_events,
    list_followers,
    list_following,
    list_followed_feed,
    normalize_feed_filter,
    FEED_FILTER_ALL,
    FEED_FILTER_LESSONS,
    FEED_FILTER_QUIZZES,
    FEED_FILTER_SHARES,
    quiz_stats_summary,
    record_activity_event,
    record_mcq_answered,
    record_question_generated,
    record_quiz_completed,
    record_topic_opened,
    search_users_by_handle,
    unfollow_user,
    update_profile_settings,
)
from models.sharing import (
    SUGGESTION_DISMISSED,
    SUGGESTION_OPENED,
    SUGGESTION_PENDING,
    can_view_share,
    count_pending_suggestions,
    create_shared_question,
    create_suggestion,
    dismiss_suggestion,
    get_shared_question,
    get_suggestion,
    list_suggestions_inbox,
    mark_suggestion_opened,
)
from models.notifications import (
    NOTIFICATION_FOLLOW,
    NOTIFICATION_SUGGESTION,
    count_unread_notifications,
    create_notification,
    list_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    mark_suggestion_notifications_read,
)
from models.user_data import (
    clear_lesson_progress,
    delete_saved_problem,
    enrich_quiz_attempt_problems,
    get_lesson_progress,
    get_quiz_attempt,
    get_saved_problem,
    get_practice_streak,
    list_generator_mcq_attempts,
    list_lesson_progress,
    list_quiz_attempts,
    list_saved_problems,
    record_generator_mcq_attempt,
    record_quiz_attempt,
    save_problem,
    update_saved_problem,
    upsert_lesson_progress,
)
from models.gamification import (
    evaluate_milestones,
    friend_effort_leaderboard,
    get_study_streak,
    get_weekly_recap,
    list_user_milestones,
    record_study_day,
)
from models.problem_queue import (
    clear_problem_queue as clear_db_problem_queue,
    get_problem_queue as get_db_problem_queue,
    save_problem_queue as save_db_problem_queue,
)
from models.moderation import (
    REPORT_TYPES,
    block_user,
    create_report,
    is_blocked,
    list_blocked_users,
    unblock_user,
)
from models.rate_limit import check_and_increment_rate_limit

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-for-local-testing')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

login_manager = LoginManager()

def _csrf_token():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_hex(32)
        session['_csrf_token'] = token
        session.modified = True
    return token


def _validate_csrf(form_token):
    expected = session.get('_csrf_token', '')
    if not form_token or not expected:
        return False
    return secrets.compare_digest(form_token, expected)


def _wants_json_response():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json'


def _render_problem_field(text):
    if not text:
        return ''
    text = str(text)
    if any(marker in text.lower() for marker in _BLOCK_HTML_MARKERS):
        return text
    return str(format_question_html(text))


def _problem_client_payload(problem):
    payload = {
        'question_html': _render_problem_field(problem.get('question')),
        'solution_html': _render_problem_field(problem.get('solution')),
        'hint_html': _render_problem_field(problem.get('hint')),
        'marks': problem.get('marks'),
        'options': problem.get('options') or [],
        'correct_answer': problem.get('correct_answer'),
        'variant_name': problem.get('variant_name'),
    }
    return payload

_BLOCK_HTML_MARKERS = ('<svg', '<div', '<table', '<pre', '<figure')


@app.template_filter('format_question_html')
def format_question_html(value):
    """Format question/solution HTML: newlines, **bold**, leave diagrams intact."""
    if not value:
        return ''
    text = str(value)
    if any(marker in text.lower() for marker in _BLOCK_HTML_MARKERS):
        return Markup(text)
    text = text.replace('\n', '<br>\n')
    return Markup(format_light_markdown(text))


@app.context_processor
def inject_nav():
    lesson_meta = None
    view_args = request.view_args or {}

    if request.endpoint == 'topic_page':
        lesson_meta = _lesson_meta_for_topic(
            view_args.get('level'),
            view_args.get('subject'),
            view_args.get('topic'),
        )
    elif request.endpoint in ('lesson_mcq_results', 'lesson_mcq_quiz'):
        lesson_meta = _lesson_meta_for_topic(
            view_args.get('level'),
            view_args.get('subject'),
            view_args.get('topic'),
            quiz_review=request.endpoint == 'lesson_mcq_results',
        )
    elif request.endpoint == 'view_quiz_attempt':
        lesson_meta = getattr(g, 'lesson_meta', None)

    assist_on = lesson_assist_enabled() and lesson_meta is not None
    lesson_progress_on = assist_on and not (lesson_meta or {}).get('quizReview')
    unread_notifications = 0
    if current_user.is_authenticated:
        with get_db() as conn:
            unread_notifications = count_unread_notifications(conn, current_user.id)
    return {
        'nav_endpoint': request.endpoint,
        'lesson_meta': lesson_meta,
        'lesson_assist_enabled': assist_on,
        'lesson_progress_enabled': lesson_progress_on,
        'csrf_token': _csrf_token,
        'unread_notifications': unread_notifications,
    }


def _is_python_lesson_page():
    view_args = request.view_args or {}
    return (
        request.endpoint == 'topic_page'
        and view_args.get('level') == 'gcse'
        and view_args.get('subject') == 'cs'
        and view_args.get('topic') == 'python_programming'
    )


@app.after_request
def apply_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        # 'unsafe-inline' allows <script> blocks and onclick= handlers in templates.
        # 'unsafe-eval' is required by MathJax; 'wasm-unsafe-eval' is required by Pyodide.
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
        # Pyodide fetches pyodide.wasm and the Python stdlib zip from the CDN at runtime.
        "connect-src 'self' https://cdn.jsdelivr.net; "
        # Pyodide uses blob: workers internally for async execution; SW is same-origin.
        "worker-src 'self' blob:; "
        "manifest-src 'self'; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
    if _is_python_lesson_page():
        # SharedArrayBuffer (blocking stdin in the Pyodide worker) needs cross-origin isolation.
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Embedder-Policy'] = 'credentialless'
    return response


## Database functions:

def get_db():
    db_path = os.path.join(app.root_path, 'data', 'quicktest.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quicktest_sessions (
            session_id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_assist_usage (
            day TEXT NOT NULL,
            client_key TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (day, client_key)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            handle TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login_at TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            mode TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            problem_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_saved_problems_user
        ON saved_problems (user_id, created_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            user_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            section_key TEXT NOT NULL,
            section_label TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            PRIMARY KEY (user_id, level, subject, topic),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_lesson_progress_user
        ON lesson_progress (user_id, updated_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            answers_json TEXT NOT NULL,
            problems_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_quiz_attempts_user
        ON quiz_attempts (user_id, created_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS generator_mcq_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            mode TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            correct INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_generator_mcq_attempts_user
        ON generator_mcq_attempts (user_id, created_at DESC)
    """)
    quiz_cols = {
        row[1] for row in conn.execute('PRAGMA table_info(quiz_attempts)').fetchall()
    }
    if 'problems_json' not in quiz_cols:
        conn.execute('ALTER TABLE quiz_attempts ADD COLUMN problems_json TEXT')
    lesson_cols = {
        row[1] for row in conn.execute('PRAGMA table_info(lesson_progress)').fetchall()
    }
    if 'completed_keys_json' not in lesson_cols:
        conn.execute(
            'ALTER TABLE lesson_progress ADD COLUMN completed_keys_json TEXT NOT NULL DEFAULT \'[]\''
        )
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profile_settings (
            user_id INTEGER PRIMARY KEY,
            profile_visibility TEXT NOT NULL DEFAULT 'public',
            show_member_since INTEGER NOT NULL DEFAULT 1,
            show_last_topic INTEGER NOT NULL DEFAULT 1,
            show_last_activity INTEGER NOT NULL DEFAULT 1,
            show_lesson_progress INTEGER NOT NULL DEFAULT 1,
            show_quiz_stats INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_summary (
            user_id INTEGER PRIMARY KEY,
            last_topic_level TEXT,
            last_topic_subject TEXT,
            last_topic_topic TEXT,
            last_topic_label TEXT,
            last_topic_at TEXT,
            last_activity_type TEXT,
            last_activity_level TEXT,
            last_activity_subject TEXT,
            last_activity_topic TEXT,
            last_activity_label TEXT,
            last_activity_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            follower_id INTEGER NOT NULL,
            following_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (follower_id, following_id),
            FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (following_id) REFERENCES users(id) ON DELETE CASCADE,
            CHECK (follower_id != following_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_follows_following
        ON follows (following_id)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_activity_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            visibility TEXT NOT NULL DEFAULT 'followers_only',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_activity_events_user_created
        ON user_activity_events (user_id, created_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shared_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            mode TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            problem_json TEXT NOT NULL,
            visibility TEXT NOT NULL DEFAULT 'followers_only',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_shared_questions_user
        ON shared_questions (user_id, created_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS question_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            level TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            mode TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            problem_json TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            read_at TEXT,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_suggestions_recipient
        ON question_suggestions (recipient_id, status, created_at DESC)
    """)
    profile_cols = {
        row[1] for row in conn.execute('PRAGMA table_info(user_profile_settings)').fetchall()
    }
    for col, ddl in (
        ('show_shared_questions', 'INTEGER NOT NULL DEFAULT 1'),
        ('auto_share_quiz', 'INTEGER NOT NULL DEFAULT 0'),
        ('auto_share_lesson', 'INTEGER NOT NULL DEFAULT 0'),
        ('default_share_visibility', "TEXT NOT NULL DEFAULT 'followers_only'"),
        ('show_study_streak', 'INTEGER NOT NULL DEFAULT 0'),
        ('show_milestones', 'INTEGER NOT NULL DEFAULT 0'),
    ):
        if col not in profile_cols:
            conn.execute(f'ALTER TABLE user_profile_settings ADD COLUMN {col} {ddl}')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER NOT NULL DEFAULT 0,
            longest_streak INTEGER NOT NULL DEFAULT 0,
            last_active_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_study_days (
            user_id INTEGER NOT NULL,
            study_date TEXT NOT NULL,
            PRIMARY KEY (user_id, study_date),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_milestones (
            user_id INTEGER NOT NULL,
            milestone_key TEXT NOT NULL,
            earned_at TEXT NOT NULL,
            PRIMARY KEY (user_id, milestone_key),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            read_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_user_created
        ON user_notifications (user_id, created_at DESC)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_problem_queues (
            user_id INTEGER NOT NULL,
            queue_key TEXT NOT NULL,
            queue_json TEXT NOT NULL DEFAULT '[]',
            queue_index INTEGER NOT NULL DEFAULT 0,
            variant_name TEXT,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (user_id, queue_key),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_blocks (
            blocker_id INTEGER NOT NULL,
            blocked_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (blocker_id, blocked_id),
            FOREIGN KEY (blocker_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (blocked_id) REFERENCES users(id) ON DELETE CASCADE,
            CHECK (blocker_id != blocked_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_blocks_blocked
        ON user_blocks (blocked_id)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reporter_id INTEGER NOT NULL,
            reported_user_id INTEGER,
            report_type TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            context_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rate_limit_buckets (
            bucket_key TEXT NOT NULL,
            window_start TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT,
            PRIMARY KEY (bucket_key, window_start)
        )
    """)
    conn.commit()

login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access that page.'
login_manager.login_message_category = 'error'


@login_manager.unauthorized_handler
def _unauthorized():
    if request.path.startswith('/api/'):
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    return redirect(url_for('login', next=request.path))


@login_manager.user_loader
def load_user(user_id):
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return None
    with get_db() as conn:
        return User.get_by_id(conn, uid)


def _save_qt(data):
    qt_id = session.get('qt_id', str(uuid.uuid4()))
    session['qt_id'] = qt_id
    session.modified = True

    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO quicktest_sessions (session_id, data) VALUES (?, ?)",
            (qt_id, json.dumps(data))
        )
        conn.commit()
    return qt_id

def _load_qt():
    qt_id = session.get('qt_id')
    if not qt_id:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT data FROM quicktest_sessions WHERE session_id = ?",
            (qt_id,)
        ).fetchone()
        if row:
            return json.loads(row['data'])
    return None


def _save_lq(data):
    lq_id = session.get('lq_id', str(uuid.uuid4()))
    session['lq_id'] = lq_id
    session.modified = True
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO quicktest_sessions (session_id, data) VALUES (?, ?)",
            (f"lq_{lq_id}", json.dumps(data)),
        )
        conn.commit()
    return lq_id


def _load_lq():
    lq_id = session.get('lq_id')
    if not lq_id:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT data FROM quicktest_sessions WHERE session_id = ?",
            (f"lq_{lq_id}",),
        ).fetchone()
        if row:
            return json.loads(row['data'])
    return None


def _option_letter(opt):
    if not opt:
        return ''
    return str(opt).strip()[:1].upper()


def _quiz_explanation(problem):
    return problem.get('explanation') or problem.get('solution') or problem.get('hint') or ''


def _quiz_assist_item(problem, user_answer, question_number):
    correct = problem.get('correct_answer', '')
    user = (user_answer or '').strip().upper()[:1]
    return {
        'question': problem.get('question', ''),
        'options': problem.get('options') or [],
        'correctAnswer': correct,
        'userAnswer': user,
        'modelExplanation': _quiz_explanation(problem),
        'questionNumber': question_number,
        'wasCorrect': bool(user and user == correct),
    }


def _render_quiz_results(
    problems,
    score,
    total,
    topic_name,
    lesson_url,
    level,
    subject,
    topic,
    *,
    attempt_date=None,
    back_url=None,
    back_label=None,
    show_wrong_explanations_only=True,
    quiz_attempt_id=None,
):
    return render_template(
        'lesson_mcq_results.html',
        problems=problems,
        score=score,
        total=total,
        topic_name=topic_name,
        lesson_url=lesson_url,
        level=level,
        subject=subject,
        topic=topic,
        option_letter=_option_letter,
        quiz_explanation=_quiz_explanation,
        quiz_assist_item=_quiz_assist_item,
        attempt_date=attempt_date,
        back_url=back_url or lesson_url,
        back_label=back_label or '← Back to lesson',
        show_wrong_explanations_only=show_wrong_explanations_only,
        quiz_attempt_id=quiz_attempt_id,
    )


def _lesson_quiz_available(level, subject, topic):
    try:
        topic_config = TOPICS[level][subject][topic]
    except KeyError:
        return False
    if level != "gcse" or subject not in ("maths", "cs"):
        return False
    return topic_supports_lesson_mcq(topic_config)

## Problems functionality:

def lesson_problem(fn):
    q, s, hint, marks = fn()
    return {"question": q, "solution": s}

def get_topic_content(level, subject, topic):
    return TOPIC_CONTENT.get((level, subject, topic))

def _selection_key(level, subject, topic, mode, difficulty):
    return f"{level}|{subject}|{topic}|{mode}|{difficulty}"


def _clear_problem_queue(user_id=None, queue_key=None):
    for key in (
        'problem_queue_key',
        'problem_queue',
        'problem_index',
        'problem_variant_name',
    ):
        session.pop(key, None)
    if user_id:
        with get_db() as conn:
            clear_db_problem_queue(conn, user_id, queue_key)


def _build_problem_queue(topic_config, level, subject, topic, mode, difficulty):
    variants_builder = topic_config.get('variants_func')
    if not variants_builder:
        return None

    queue = variants_builder(difficulty, normalize_mode(mode))
    if not queue:
        return None

    return [variant.__name__ for variant in queue]


def _load_queue_state(user_id, queue_key):
    """Return (queue, index, variant_name) from DB or session."""
    if user_id:
        with get_db() as conn:
            stored = get_db_problem_queue(conn, user_id, queue_key)
        if stored and stored.get('queue'):
            return stored['queue'], stored['index'], stored.get('variant_name')
        return None, -1, None
    if session.get('problem_queue_key') != queue_key:
        return None, -1, None
    return (
        session.get('problem_queue'),
        session.get('problem_index', -1),
        session.get('problem_variant_name'),
    )


def _persist_queue_state(user_id, queue_key, queue, index, variant_name):
    if user_id:
        with get_db() as conn:
            save_db_problem_queue(conn, user_id, queue_key, queue, index, variant_name)
    session['problem_queue_key'] = queue_key
    session['problem_queue'] = queue
    session['problem_index'] = index
    session['problem_variant_name'] = variant_name
    session.modified = True


def _get_problem_from_queue(
    topic_config, level, subject, topic, mode, difficulty, action, user_id=None
):
    """Advance or start the variant queue. Returns problem dict."""
    problem, _meta = _generate_queued_problem(
        topic_config, level, subject, topic, mode, difficulty, action, user_id=user_id
    )
    return problem


def _generate_queued_problem(
    topic_config, level, subject, topic, mode, difficulty, action, user_id=None
):
    """
    Generate a problem from the variant queue.

    action:
      - start: rebuild queue and return first item (API) OR start if empty (web)
      - next: advance to next variant
    Returns (problem_dict, meta_dict).
    """
    generator = topic_config['func']
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    queue, idx, _variant = _load_queue_state(user_id, queue_key)

    rebuild = False
    if action == 'start':
        if user_id is not None:
            rebuild = True
        else:
            rebuild = not queue
    elif not queue:
        rebuild = True

    if rebuild:
        queue = _build_problem_queue(topic_config, level, subject, topic, mode, difficulty)
        if not queue:
            problem = generator(difficulty, mode)
            return problem, {
                'variant_name': None,
                'queue_position': 0,
                'queue_length': 0,
                'can_reroll': False,
            }
        idx = 0
    else:
        idx += 1
        if idx >= len(queue):
            queue = _build_problem_queue(topic_config, level, subject, topic, mode, difficulty)
            if not queue:
                problem = generator(difficulty, mode)
                return problem, {
                    'variant_name': None,
                    'queue_position': 0,
                    'queue_length': 0,
                    'can_reroll': False,
                }
            idx = 0

    variant_name = queue[idx]
    _persist_queue_state(user_id, queue_key, queue, idx, variant_name)
    problem = generator(difficulty, mode, variant_name=variant_name)
    meta = {
        'variant_name': variant_name,
        'queue_position': idx + 1,
        'queue_length': len(queue),
        'can_reroll': _can_reroll_variant(topic_config, mode, difficulty, variant_name),
    }
    return problem, meta


def _reroll_variant_problem(topic_config, mode, difficulty, variant_name):
    """Regenerate a named variant with fresh random values."""
    if not variant_name or not topic_config.get('variants_func'):
        return None
    generator = topic_config['func']
    return generator(difficulty, mode, variant_name=variant_name)


def _can_reroll_variant(topic_config, mode, difficulty, variant_name):
    if not variant_name or not topic_config.get('variants_func'):
        return False
    variant_fn = resolve_variant_callable(
        topic_config['variants_func'],
        difficulty,
        mode,
        variant_name,
    )
    return variant_is_randomizable(variant_fn)


def _reroll_current_problem(topic_config, level, subject, topic, mode, difficulty, user_id=None):
    """Regenerate the current queue variant without advancing the queue index."""
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    _queue, _idx, variant_name = _load_queue_state(user_id, queue_key)
    if not variant_name or not topic_config.get('variants_func'):
        return None
    return _reroll_variant_problem(topic_config, mode, difficulty, variant_name)


def _can_reroll_current_variant(topic_config, level, subject, topic, mode, difficulty, user_id=None):
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    _queue, _idx, variant_name = _load_queue_state(user_id, queue_key)
    if not variant_name or not topic_config.get('variants_func'):
        return False
    return _can_reroll_variant(topic_config, mode, difficulty, variant_name)


_TOPIC_ALIASES = {
    ('gcse', 'cs', 'binary'): 'data_rep',
}


def _resolve_topic_slug(level, subject, topic):
    return _TOPIC_ALIASES.get((level, subject, topic), topic)


## ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'anon_count' not in session:
        session['anon_count'] = 0

    problem = None
    error = None
    limit_hit = False
    ANON_DAILY_LIMIT = 999

    if request.method == 'POST':
        selected_level = request.form.get('level', 'gcse')
        selected_subject = request.form.get('subject', 'physics')
        selected_topic = _resolve_topic_slug(
            selected_level, selected_subject, request.form.get('topic', 'forces')
        )
        raw_mode = request.form.get('mode', 'standard')
        selected_diff = request.form.get('difficulty', 'foundational')
        action = request.form.get('action', 'start')
    else:
        selected_level = request.args.get('level', 'gcse')
        selected_subject = request.args.get('subject', 'physics')
        selected_topic = _resolve_topic_slug(
            selected_level, selected_subject, request.args.get('topic', 'forces')
        )
        raw_mode = request.args.get('mode', 'standard')
        selected_diff = request.args.get('difficulty', 'foundational')
        action = 'start'
    selected_mode = normalize_mode(raw_mode)


    if request.method == 'POST':
        if not can_access_difficulty(current_user, selected_diff):
            error = (
                'Difficult questions require a free account. '
                'Sign up or log in to continue.'
            )
        elif session['anon_count'] >= ANON_DAILY_LIMIT:
            limit_hit = True
        else:
            try:
                topic_config = TOPICS[selected_level][selected_subject][selected_topic]
                generator = topic_config['func']

                if action == 'reroll':
                    problem = _reroll_current_problem(
                        topic_config,
                        selected_level,
                        selected_subject,
                        selected_topic,
                        selected_mode,
                        selected_diff,
                    )
                    if problem is None:
                        error = 'Could not refresh this question. Generate a new one instead.'
                elif action == 'next' and topic_config.get('variants_func'):
                    problem = _get_problem_from_queue(
                        topic_config,
                        selected_level,
                        selected_subject,
                        selected_topic,
                        selected_mode,
                        selected_diff,
                        action='next'
                    )
                elif topic_config.get('variants_func'):
                    problem = _get_problem_from_queue(
                        topic_config,
                        selected_level,
                        selected_subject,
                        selected_topic,
                        selected_mode,
                        selected_diff,
                        action='start'
                    )
                else:
                    _clear_problem_queue()
                    problem = generator(selected_diff, selected_mode)

                if problem is not None:
                    session['anon_count'] += 1
                    session['last_problem_payload'] = {
                        'level': selected_level,
                        'subject': selected_subject,
                        'topic': selected_topic,
                        'mode': selected_mode,
                        'difficulty': selected_diff,
                        'variant_name': session.get('problem_variant_name'),
                        'problem': problem,
                    }
                    session.modified = True
                    _track_question_generated(
                        selected_level,
                        selected_subject,
                        selected_topic,
                        selected_diff,
                    )
            except KeyError:
                _clear_problem_queue()
                error = 'Invalid combination. Please try again.'

    can_reroll_variant = False
    if problem and not error:
        try:
            topic_config = TOPICS[selected_level][selected_subject][selected_topic]
            can_reroll_variant = _can_reroll_current_variant(
                topic_config,
                selected_level,
                selected_subject,
                selected_topic,
                selected_mode,
                selected_diff,
            )
        except KeyError:
            can_reroll_variant = False

    return render_template(
        'index.html',
        problem=problem,
        error=error,
        limit_hit=limit_hit,
        selected_level=selected_level,
        selected_subject=selected_subject,
        selected_topic=selected_topic,
        selected_mode=selected_mode,
        selected_diff=selected_diff,
        queue_active=bool(session.get('problem_queue')),
        can_reroll_variant=can_reroll_variant,
    )



@app.route("/topic/<level>/<subject>/<topic>")
def topic_page(level, subject, topic):
    try:
        topic_data = TOPICS[level][subject][topic]
    except KeyError:
        return "Topic not found", 404

    _track_topic_opened(level, subject, topic)

    if level == "alevel" and subject == "physics" and topic == "photoelectric":
        p1 = lesson_problem(aqa_pe_basic)
        p2 = lesson_problem(aqa_pe_threshold_frequency)
        p3 = lesson_problem(aqa_pe_photoelectric_equation)
        p4 = lesson_problem(aqa_pe_stopping_potential)
        p5 = lesson_problem(aqa_pe_debroglie)

        return render_template(
            "alevel_physics_photoelectric_lesson.html",
            p1=p1,
            p2=p2,
            p3=p3,
            p4=p4,
            p5=p5,
        )

    if level == "alevel" and subject == "physics" and topic == "magnetism":
        p1 = aqa_mag_motor_effect()
        p2 = aqa_mag_particle_path()
        p3 = aqa_mag_flux_linkage()
        p4 = aqa_mag_faradays_law()
        p5 = aqa_mag_transformers()

        return render_template(
            "alevel_physics_magnetism_lesson.html",
            p1=p1, p2=p2, p3=p3, p4=p4, p5=p5
        )

    custom = f"{level}_{subject}_{topic}_lesson.html"
    try:
        return render_template(custom)
    except TemplateNotFound:
        content = get_topic_content(level, subject, topic)
        if not content:
            return "Topic not found", 404
        return render_template(
            "topic.html",
            content=content,
            level=level,
            subject=subject,
            topic=topic,
            supports_lesson_quiz=_lesson_quiz_available(level, subject, topic),
        )



LEVEL_LABELS = {
    'gcse': 'GCSE',
    'alevel': 'A-Level',
    'myp': 'IB MYP',
}
SUBJECT_LABELS = {
    'maths': 'Mathematics',
    'physics': 'Physics',
    'cs': 'Computer Science',
    'chemistry': 'Chemistry',
}
PROFILE_VISIBILITY_LABELS = {
    'public': 'Public',
    'followers_only': 'Followers only',
    'private': 'Private',
}
SHARE_VISIBILITY_LABELS = PROFILE_VISIBILITY_LABELS


def _topic_label(level, subject, topic):
    try:
        return TOPICS[level][subject][topic].get('name', topic.replace('_', ' ').title())
    except KeyError:
        return topic.replace('_', ' ').title()


def _track_topic_opened(level, subject, topic):
    if not current_user.is_authenticated:
        return
    label = _topic_label(level, subject, topic)
    with get_db() as conn:
        record_topic_opened(conn, current_user.id, level, subject, topic, label)
        record_activity_event(
            conn,
            current_user.id,
            ACTIVITY_TOPIC_OPENED,
            {
                'level': level,
                'subject': subject,
                'topic': topic,
                'topic_label': label,
            },
            VISIBILITY_FOLLOWERS,
        )
    _record_study_activity(current_user.id)


def _track_question_generated(level, subject, topic, difficulty):
    if not current_user.is_authenticated:
        return
    label = _topic_label(level, subject, topic)
    with get_db() as conn:
        record_question_generated(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            label,
            difficulty,
        )
        record_activity_event(
            conn,
            current_user.id,
            ACTIVITY_QUESTION_GENERATED,
            {
                'level': level,
                'subject': subject,
                'topic': topic,
                'topic_label': label,
                'difficulty': difficulty,
            },
            VISIBILITY_FOLLOWERS,
        )
    _record_study_activity(current_user.id)


def _track_mcq_answered(level, subject, topic, difficulty, user_answer, correct_answer, correct):
    if not current_user.is_authenticated:
        return
    label = _topic_label(level, subject, topic)
    with get_db() as conn:
        record_generator_mcq_attempt(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            'mcq',
            difficulty,
            user_answer,
            correct_answer,
            correct,
        )
        record_mcq_answered(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            label,
            correct,
        )
        record_activity_event(
            conn,
            current_user.id,
            ACTIVITY_MCQ_ANSWERED,
            {
                'level': level,
                'subject': subject,
                'topic': topic,
                'topic_label': label,
                'difficulty': difficulty,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'correct': bool(correct),
            },
            VISIBILITY_FOLLOWERS,
        )


def _track_quiz_completed(level, subject, topic, score, total):
    if not current_user.is_authenticated:
        return
    label = _topic_label(level, subject, topic)
    with get_db() as conn:
        settings = get_profile_settings(conn, current_user.id)
        visibility = VISIBILITY_FOLLOWERS
        if settings.get('auto_share_quiz'):
            visibility = _normalize_share_visibility(settings.get('default_share_visibility'))
        record_quiz_completed(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            label,
            score,
            total,
        )
        record_activity_event(
            conn,
            current_user.id,
            ACTIVITY_QUIZ_COMPLETED,
            {
                'level': level,
                'subject': subject,
                'topic': topic,
                'topic_label': label,
                'score': score,
                'total': total,
                'auto_shared': bool(settings.get('auto_share_quiz')),
            },
            visibility,
        )
    _record_study_activity(current_user.id)


def _public_profile_url(handle):
    return url_for('public_profile', handle=handle)


def _build_public_profile_context(target_user, viewer_id=None):
    with get_db() as conn:
        settings = get_profile_settings(conn, target_user.id)
        if not can_view_profile(conn, viewer_id, target_user.id, settings):
            return None
        activity = get_activity_summary(conn, target_user.id)
        followers = follower_count(conn, target_user.id)
        following = following_count(conn, target_user.id)
        is_own = viewer_id == target_user.id
        viewer_follows = (
            is_following(conn, viewer_id, target_user.id) if viewer_id else False
        )
        lesson_rows = []
        quiz_rows = []
        if settings.get('show_lesson_progress'):
            lesson_rows = lesson_progress_summary(conn, target_user.id, limit=8)
        if settings.get('show_quiz_stats'):
            quiz_rows = quiz_stats_summary(conn, target_user.id, limit=5)
        study_streak = None
        milestones = []
        if is_own or settings.get('show_study_streak'):
            study_streak = get_study_streak(conn, target_user.id)
        if is_own or settings.get('show_milestones'):
            milestones = list_user_milestones(conn, target_user.id)

    for item in lesson_rows:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
        item['lesson_url'] = url_for(
            'topic_page',
            level=item['level'],
            subject=item['subject'],
            topic=item['topic'],
        )
    for item in quiz_rows:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])

    last_topic_url = None
    if activity.get('last_topic_level') and activity.get('last_topic_topic'):
        last_topic_url = url_for(
            'topic_page',
            level=activity['last_topic_level'],
            subject=activity['last_topic_subject'],
            topic=activity['last_topic_topic'],
        )

    last_activity_url = None
    if activity.get('last_activity_level') and activity.get('last_activity_topic'):
        last_activity_url = url_for(
            'topic_page',
            level=activity['last_activity_level'],
            subject=activity['last_activity_subject'],
            topic=activity['last_activity_topic'],
        )

    return {
        'profile_user': target_user,
        'settings': settings,
        'activity': activity,
        'followers_count': followers,
        'following_count': following,
        'is_own_profile': is_own,
        'viewer_follows': viewer_follows,
        'lesson_progress': lesson_rows,
        'quiz_attempts': quiz_rows,
        'last_topic_url': last_topic_url,
        'last_activity_url': last_activity_url,
        'study_streak': study_streak,
        'milestones': milestones,
    }


def _api_error(message, status=400, code=None):
    payload = {'ok': False, 'error': message}
    if code:
        payload['code'] = code
    return jsonify(payload), status


def _notify_suggestion_received(conn, recipient_id, sender_handle, suggestion_id, topic_label):
    create_notification(
        conn,
        recipient_id,
        NOTIFICATION_SUGGESTION,
        {
            'suggestion_id': suggestion_id,
            'sender_handle': sender_handle,
            'topic_label': topic_label,
        },
    )


def _notify_new_follower(conn, following_id, follower_handle):
    create_notification(
        conn,
        following_id,
        NOTIFICATION_FOLLOW,
        {'follower_handle': follower_handle},
    )


def _serialize_notification_item(item):
    payload = item.get('payload') or {}
    ntype = item.get('notification_type', '')
    if ntype == NOTIFICATION_SUGGESTION:
        handle = payload.get('sender_handle', 'someone')
        topic = payload.get('topic_label', 'a topic')
        message = f'@{handle} sent you a question on {topic}'
        url = url_for('view_suggestion', suggestion_id=payload.get('suggestion_id'))
    elif ntype == NOTIFICATION_FOLLOW:
        handle = payload.get('follower_handle', 'someone')
        message = f'@{handle} started following you'
        url = url_for('public_profile', handle=handle)
    else:
        message = 'New notification'
        url = url_for('profile')
    return {
        'id': item['id'],
        'type': ntype,
        'message': message,
        'url': url,
        'read': item.get('read_at') is not None,
        'created_at': item.get('created_at'),
    }


def _serialize_feed_item(item):
    payload = item.get('payload') or {}
    event_type = item.get('event_type', '')
    handle = item.get('actor_handle', 'someone')
    topic_label = payload.get('topic_label') or 'a topic'
    actor_url = url_for('public_profile', handle=handle)

    if event_type == ACTIVITY_QUIZ_COMPLETED:
        score = payload.get('score')
        total = payload.get('total')
        score_text = f'{score}/{total}' if score is not None and total else 'a quiz'
        message = f'@{handle} scored {score_text} on {topic_label}'
        url = _topic_page_url(
            payload.get('level'),
            payload.get('subject'),
            payload.get('topic'),
        ) or actor_url
        card_type = 'quiz'
        card_label = 'Quiz'
    elif event_type == ACTIVITY_LESSON_STEP_COMPLETED:
        section = payload.get('section_label') or 'a lesson step'
        message = f'@{handle} completed {section} on {topic_label}'
        url = _topic_page_url(
            payload.get('level'),
            payload.get('subject'),
            payload.get('topic'),
        ) or actor_url
        card_type = 'lesson'
        card_label = 'Lesson'
    elif event_type == ACTIVITY_QUESTION_SHARED:
        message = f'@{handle} shared a question on {topic_label}'
        share_id = payload.get('share_id')
        url = (
            url_for('view_shared_question', share_id=share_id)
            if share_id
            else actor_url
        )
        card_type = 'share'
        card_label = 'Share'
    elif event_type == ACTIVITY_TOPIC_OPENED:
        message = f'@{handle} opened {topic_label}'
        url = _topic_page_url(
            payload.get('level'),
            payload.get('subject'),
            payload.get('topic'),
        ) or actor_url
        card_type = 'topic'
        card_label = 'Topic'
    else:
        message = f'@{handle} was active on Problem Bank'
        url = actor_url
        card_type = 'activity'
        card_label = 'Activity'

    return {
        'id': item['id'],
        'type': event_type,
        'card_type': card_type,
        'card_label': card_label,
        'actor_handle': handle,
        'actor_url': actor_url,
        'message': message,
        'url': url,
        'created_at': item.get('created_at'),
    }


def _feed_items_for_viewer(viewer_id, filter_name=FEED_FILTER_ALL, limit=50, before_id=None):
    with get_db() as conn:
        raw_items = list_followed_feed(
            conn, viewer_id, filter_name, limit=limit, before_id=before_id
        )
        items = []
        for item in raw_items:
            if item.get('event_type') == ACTIVITY_QUESTION_SHARED:
                payload = item.get('payload') or {}
                share_id = payload.get('share_id')
                if not share_id:
                    continue
                share = get_shared_question(conn, share_id)
                if not share:
                    continue
                if not can_view_share(
                    conn,
                    viewer_id,
                    item.get('user_id'),
                    item.get('visibility'),
                ):
                    continue
            items.append(_serialize_feed_item(item))
        return items


def _settings_to_json(settings):
    return {
        'profile_visibility': settings.get('profile_visibility', VISIBILITY_PUBLIC),
        'show_member_since': bool(settings.get('show_member_since', True)),
        'show_last_topic': bool(settings.get('show_last_topic', True)),
        'show_last_activity': bool(settings.get('show_last_activity', True)),
        'show_lesson_progress': bool(settings.get('show_lesson_progress', True)),
        'show_quiz_stats': bool(settings.get('show_quiz_stats', True)),
        'show_shared_questions': bool(settings.get('show_shared_questions', True)),
        'auto_share_quiz': bool(settings.get('auto_share_quiz', False)),
        'auto_share_lesson': bool(settings.get('auto_share_lesson', False)),
        'default_share_visibility': settings.get('default_share_visibility', VISIBILITY_FOLLOWERS),
        'show_study_streak': bool(settings.get('show_study_streak', False)),
        'show_milestones': bool(settings.get('show_milestones', False)),
    }


def _normalize_share_visibility(value):
    if value in VISIBILITY_CHOICES:
        return value
    return VISIBILITY_FOLLOWERS


def _problem_from_session_payload():
    payload = session.get('last_problem_payload')
    if not payload or not isinstance(payload.get('problem'), dict):
        return None
    level = payload['level']
    subject = payload['subject']
    topic = payload['topic']
    mode = normalize_mode(payload.get('mode', 'standard'))
    difficulty = payload.get('difficulty', 'foundational')
    problem = dict(payload['problem'])
    variant_name = payload.get('variant_name') or problem.get('variant_name')
    if variant_name:
        problem['variant_name'] = variant_name
    if not _topic_path_valid(level, subject, topic) or not problem.get('question'):
        return None
    return {
        'level': level,
        'subject': subject,
        'topic': topic,
        'mode': mode,
        'difficulty': difficulty,
        'problem': problem,
    }


def _record_user_activity(user_id, event_type, payload, visibility=VISIBILITY_FOLLOWERS):
    with get_db() as conn:
        record_activity_event(conn, user_id, event_type, payload, visibility)


def _record_study_activity(user_id):
    if not user_id:
        return
    with get_db() as conn:
        record_study_day(conn, user_id)
        evaluate_milestones(conn, user_id)


def _topic_page_url(level, subject, topic):
    if level and subject and topic:
        return url_for('topic_page', level=level, subject=subject, topic=topic)
    return None


def _activity_field(activity, prefix, show):
    if not show:
        return None
    label = activity.get(f'{prefix}_label')
    if not label:
        return None
    return {
        'label': label,
        'url': _topic_page_url(
            activity.get(f'{prefix}_level'),
            activity.get(f'{prefix}_subject'),
            activity.get(f'{prefix}_topic'),
        ),
        'at': activity.get(f'{prefix}_at'),
    }


def _build_public_profile_json(target_user, viewer_id=None):
    context = _build_public_profile_context(target_user, viewer_id)
    if context is None:
        return None

    settings = context['settings']
    activity = context['activity']
    profile = {
        'handle': target_user.handle,
        'followers_count': context['followers_count'],
        'following_count': context['following_count'],
        'is_own_profile': context['is_own_profile'],
        'viewer_follows': context['viewer_follows'],
    }
    if settings.get('show_member_since'):
        created = target_user.created_at or ''
        profile['member_since'] = created[:10] if created else None
    if settings.get('show_last_topic') or settings.get('show_last_activity'):
        profile['activity'] = {
            'last_topic': _activity_field(activity, 'last_topic', settings.get('show_last_topic')),
            'last_activity': _activity_field(
                activity,
                'last_activity',
                settings.get('show_last_activity'),
            ),
        }
    if settings.get('show_lesson_progress'):
        profile['lesson_progress'] = [
            {
                'level': item['level'],
                'subject': item['subject'],
                'topic': item['topic'],
                'topic_label': item['topic_label'],
                'lesson_url': item['lesson_url'],
                'section_key': item.get('section_key'),
                'section_label': item.get('section_label'),
                'completed_count': item.get('completed_count', 0),
                'updated_at': item.get('updated_at'),
            }
            for item in context['lesson_progress']
        ]
    if settings.get('show_quiz_stats'):
        profile['quiz_attempts'] = [
            {
                'level': item['level'],
                'subject': item['subject'],
                'topic': item['topic'],
                'topic_label': item['topic_label'],
                'score': item['score'],
                'total': item['total'],
                'created_at': item['created_at'],
            }
            for item in context['quiz_attempts']
        ]
    if context.get('study_streak') is not None and (
        context['is_own_profile'] or settings.get('show_study_streak')
    ):
        profile['study_streak'] = context['study_streak']
    if context.get('milestones') and (
        context['is_own_profile'] or settings.get('show_milestones')
    ):
        profile['milestones'] = context['milestones']
    return profile


def _resolve_active_user_by_handle(handle):
    with get_db() as conn:
        target = get_user_by_handle(conn, normalize_handle(handle))
    if not target or not target.is_active:
        return None
    return target


def _serialize_user_search_results(rows):
    serialized = []
    for item in rows:
        entry = {
            'handle': item['handle'],
            'profile_url': _public_profile_url(item['handle']),
            'profile_accessible': item['profile_accessible'],
        }
        if item.get('member_since'):
            entry['member_since'] = item['member_since']
        if 'viewer_follows' in item:
            entry['viewer_follows'] = item['viewer_follows']
        serialized.append(entry)
    return serialized


def _unified_search(query, viewer_id=None, limit_topics=8, limit_users=8):
    normalized = (query or '').strip()
    if len(normalized) < 2:
        return normalized.lower(), [], [], 'Enter at least 2 characters to search.'

    topics = _search_topics(normalized, limit=limit_topics) if limit_topics > 0 else []
    with get_db() as conn:
        users = search_users_by_handle(
            conn,
            normalized,
            viewer_id=viewer_id,
            limit=limit_users,
            exclude_user_id=viewer_id,
        )
    return normalized.lower(), topics, users, None


def _lesson_meta_for_topic(level, subject, topic, *, quiz_review=False):
    if not level or not subject or not topic:
        return None
    try:
        topic_data = TOPICS[level][subject][topic]
    except KeyError:
        return None
    meta = {
        'level': level,
        'subject': subject,
        'topic': topic,
        'topicTitle': topic_data.get('name', topic),
    }
    if quiz_review:
        meta['quizReview'] = True
    return meta


def _topic_path_valid(level, subject, topic):
    try:
        TOPICS[level][subject][topic]
        return True
    except KeyError:
        return False


_TOPIC_LEVEL_ORDER = ('gcse', 'alevel', 'myp')
_TOPIC_SUBJECT_ORDER = {
    'gcse': ('maths', 'physics', 'cs'),
    'alevel': ('physics',),
    'myp': ('chemistry',),
}


def _build_topic_groups():
    groups = []
    for level in _TOPIC_LEVEL_ORDER:
        subjects = TOPICS.get(level)
        if not subjects:
            continue
        for subject in _TOPIC_SUBJECT_ORDER.get(level, tuple(subjects.keys())):
            topics = subjects.get(subject)
            if not topics:
                continue
            items = [
                {
                    'slug': slug,
                    'name': cfg['name'],
                    'url': f'/topic/{level}/{subject}/{slug}',
                }
                for slug, cfg in sorted(topics.items(), key=lambda x: x[1]['name'].lower())
            ]
            groups.append({
                'title': f"{LEVEL_LABELS.get(level, level.title())} {SUBJECT_LABELS.get(subject, subject.title())}",
                'topics': items,
            })
    return groups


_TOPIC_INDEX = None


def _get_topic_index():
    global _TOPIC_INDEX
    if _TOPIC_INDEX is not None:
        return _TOPIC_INDEX

    items = []
    for level in _TOPIC_LEVEL_ORDER:
        subjects = TOPICS.get(level)
        if not subjects:
            continue
        for subject in _TOPIC_SUBJECT_ORDER.get(level, tuple(subjects.keys())):
            topics = subjects.get(subject)
            if not topics:
                continue
            group = (
                f"{LEVEL_LABELS.get(level, level.title())} "
                f"{SUBJECT_LABELS.get(subject, subject.title())}"
            )
            for slug, cfg in sorted(topics.items(), key=lambda x: x[1]['name'].lower()):
                items.append({
                    'name': cfg['name'],
                    'slug': slug,
                    'url': f'/topic/{level}/{subject}/{slug}',
                    'group': group,
                })
    _TOPIC_INDEX = items
    return _TOPIC_INDEX


def _search_topics(query, limit=8):
    query = (query or '').strip().lower()
    if len(query) < 2:
        return []

    tokens = query.split()
    matches = []
    for item in _get_topic_index():
        haystack = ' '.join([
            item['name'].lower(),
            item['slug'].replace('_', ' '),
            item['group'].lower(),
        ])
        if all(token in haystack for token in tokens):
            matches.append(item)

    matches.sort(key=lambda item: (
        0 if item['name'].lower().startswith(query) else 1,
        item['name'].lower(),
    ))
    return matches[:limit]


@app.route('/topics')
def topics_index():
    return render_template('topics.html', topic_groups=_build_topic_groups())


@app.route('/about')
def about():
    return render_template('about.html')


@app.get('/offline')
def offline():
    return render_template('offline.html')


@app.get('/sw.js')
def service_worker():
    """Serve the service worker from the site root so it can control the whole origin."""
    path = _ROOT / 'static' / 'js' / 'sw.js'
    response = Response(path.read_text(encoding='utf-8'), mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.get('/manifest.webmanifest')
def web_manifest():
    return send_from_directory(
        _ROOT / 'static',
        'manifest.webmanifest',
        mimetype='application/manifest+json',
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    errors = {}
    form = {
        'email': '',
        'handle': '',
    }

    if request.method == 'POST':
        if not _validate_csrf(request.form.get('csrf_token')):
            errors['form'] = 'Your session expired. Please try again.'
        else:
            form['email'] = request.form.get('email', '')
            form['handle'] = request.form.get('handle', '')
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            age_ok = request.form.get('age_confirm') == '1'

            for field, validator, value in (
                ('email', validate_email, form['email']),
                ('handle', validate_handle, form['handle']),
                ('password', validate_password, password),
            ):
                msg = validator(value)
                if msg:
                    errors[field] = msg

            if not age_ok:
                errors['age_confirm'] = 'You must confirm you are 13 or older to create an account.'

            if password and confirm and password != confirm:
                errors['confirm_password'] = 'Passwords do not match.'

            if not errors:
                email = normalize_email(form['email'])
                handle = normalize_handle(form['handle'])
                with get_db() as conn:
                    if User.get_by_email(conn, email):
                        errors['email'] = 'An account with that email already exists.'
                    elif User.get_by_handle(conn, handle):
                        errors['handle'] = 'That handle is already taken.'
                    else:
                        user = User.create(conn, email, handle, password)
                        ensure_user_profile(conn, user.id)
                        login_user(user, remember=True)
                        user.touch_login(conn)
                        flash('Welcome to Problem Bank!', 'success')
                        return redirect(url_for('profile'))

    return render_template('register.html', errors=errors, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    error = None
    email_value = ''

    if request.method == 'POST':
        if not _validate_csrf(request.form.get('csrf_token')):
            error = 'Your session expired. Please try again.'
        else:
            email_value = request.form.get('email', '')
            password = request.form.get('password', '')
            remember = request.form.get('remember') == '1'

            with get_db() as conn:
                user = User.get_by_email(conn, normalize_email(email_value))

            if user and user.is_active and user.check_password(password):
                login_user(user, remember=remember)
                with get_db() as conn:
                    user.touch_login(conn)
                next_url = request.args.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect(url_for('profile'))

            error = 'Invalid email or password.'

    return render_template('login.html', error=error, email_value=email_value)


@app.post('/logout')
def logout():
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(url_for('index'))
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    with get_db() as conn:
        ensure_user_profile(conn, current_user.id)
        saved = list_saved_problems(conn, current_user.id, limit=10)
        progress = list_lesson_progress(conn, current_user.id, limit=10)
        quizzes = list_quiz_attempts(conn, current_user.id, limit=10)
        mcq_attempts = list_generator_mcq_attempts(conn, current_user.id, limit=10)
        practice_streak = get_practice_streak(conn, current_user.id)
        study_streak = get_study_streak(conn, current_user.id)
        milestones = list_user_milestones(conn, current_user.id)
        weekly_recap = get_weekly_recap(conn, current_user.id)
        leaderboard = friend_effort_leaderboard(conn, current_user.id, days=7)
        pending_suggestions = count_pending_suggestions(conn, current_user.id)
    for item in saved:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
    for item in progress:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
        item['lesson_url'] = url_for(
            'topic_page',
            level=item['level'],
            subject=item['subject'],
            topic=item['topic'],
        )
    for item in quizzes:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
    for item in mcq_attempts:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
        item['correct'] = bool(item.get('correct'))
    if weekly_recap.get('best_quiz'):
        bq = weekly_recap['best_quiz']
        bq['topic_label'] = _topic_label(bq['level'], bq['subject'], bq['topic'])
    for item in leaderboard:
        item['profile_url'] = url_for('public_profile', handle=item['handle'])
    return render_template(
        'profile.html',
        saved_problems=saved,
        lesson_progress=progress,
        quiz_attempts=quizzes,
        mcq_attempts=mcq_attempts,
        practice_streak=practice_streak,
        study_streak=study_streak,
        milestones=milestones,
        weekly_recap=weekly_recap,
        friend_leaderboard=leaderboard[:5],
        pending_suggestions=pending_suggestions,
        public_profile_url=_public_profile_url(current_user.handle),
    )


@app.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def profile_settings():
    errors = {}
    with get_db() as conn:
        settings = get_profile_settings(conn, current_user.id)

    if request.method == 'POST':
        if not _validate_csrf(request.form.get('csrf_token')):
            errors['form'] = 'Your session expired. Please try again.'
        else:
            updated = {
                'profile_visibility': request.form.get('profile_visibility', 'public'),
                'show_member_since': request.form.get('show_member_since') == '1',
                'show_last_topic': request.form.get('show_last_topic') == '1',
                'show_last_activity': request.form.get('show_last_activity') == '1',
                'show_lesson_progress': request.form.get('show_lesson_progress') == '1',
                'show_quiz_stats': request.form.get('show_quiz_stats') == '1',
                'show_shared_questions': request.form.get('show_shared_questions') == '1',
                'auto_share_quiz': request.form.get('auto_share_quiz') == '1',
                'auto_share_lesson': request.form.get('auto_share_lesson') == '1',
                'default_share_visibility': request.form.get(
                    'default_share_visibility',
                    VISIBILITY_FOLLOWERS,
                ),
                'show_study_streak': request.form.get('show_study_streak') == '1',
                'show_milestones': request.form.get('show_milestones') == '1',
            }
            with get_db() as conn:
                update_profile_settings(conn, current_user.id, updated)
                settings = get_profile_settings(conn, current_user.id)
            flash('Settings saved.', 'success')
            return redirect(url_for('profile_settings'))

    return render_template(
        'profile_settings.html',
        settings=settings,
        visibility_choices=VISIBILITY_CHOICES,
        profile_visibility_label=PROFILE_VISIBILITY_LABELS.get(
            settings.get('profile_visibility', VISIBILITY_PUBLIC),
            'Public',
        ),
        errors=errors,
        public_profile_url=_public_profile_url(current_user.handle),
    )


@app.route('/u/<handle>')
def public_profile(handle):
    with get_db() as conn:
        target = get_user_by_handle(conn, handle)
    if not target or not target.is_active:
        return 'User not found', 404

    viewer_id = current_user.id if current_user.is_authenticated else None
    context = _build_public_profile_context(target, viewer_id)
    if context is None:
        return render_template(
            'public_profile_private.html',
            profile_user=target,
        )

    return render_template('public_profile.html', **context)


@app.route('/u/<handle>/followers')
def public_profile_followers(handle):
    with get_db() as conn:
        target = get_user_by_handle(conn, handle)
        if not target or not target.is_active:
            return 'User not found', 404
        settings = get_profile_settings(conn, target.id)
        viewer_id = current_user.id if current_user.is_authenticated else None
        if not can_view_profile(conn, viewer_id, target.id, settings):
            return render_template('public_profile_private.html', profile_user=target)
        users = list_followers(conn, target.id, limit=100)

    for item in users:
        item['profile_url'] = _public_profile_url(item['handle'])
    return render_template(
        'follow_list.html',
        profile_user=target,
        list_title='Followers',
        users=users,
    )


@app.route('/u/<handle>/following')
def public_profile_following(handle):
    with get_db() as conn:
        target = get_user_by_handle(conn, handle)
        if not target or not target.is_active:
            return 'User not found', 404
        settings = get_profile_settings(conn, target.id)
        viewer_id = current_user.id if current_user.is_authenticated else None
        if not can_view_profile(conn, viewer_id, target.id, settings):
            return render_template('public_profile_private.html', profile_user=target)
        users = list_following(conn, target.id, limit=100)

    for item in users:
        item['profile_url'] = _public_profile_url(item['handle'])
    return render_template(
        'follow_list.html',
        profile_user=target,
        list_title='Following',
        users=users,
    )


@app.post('/u/<handle>/follow')
@login_required
def follow_user_route(handle):
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(request.referrer or url_for('index'))

    with get_db() as conn:
        target = get_user_by_handle(conn, handle)
        if not target or not target.is_active:
            flash('User not found.', 'error')
            return redirect(url_for('index'))
        if target.id == current_user.id:
            return redirect(_public_profile_url(handle))
        followed = follow_user(conn, current_user.id, target.id)
        if followed:
            _notify_new_follower(conn, target.id, current_user.handle)

    flash(f'You are now following @{target.handle}.', 'success')
    return redirect(_public_profile_url(handle))


@app.post('/u/<handle>/unfollow')
@login_required
def unfollow_user_route(handle):
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(request.referrer or url_for('index'))

    with get_db() as conn:
        target = get_user_by_handle(conn, handle)
        if not target:
            flash('User not found.', 'error')
            return redirect(url_for('index'))
        unfollow_user(conn, current_user.id, target.id)

    flash(f'You unfollowed @{target.handle}.', 'success')
    return redirect(_public_profile_url(handle))


@app.route('/search')
def site_search():
    query = (request.args.get('q') or '').strip()
    topics = []
    users = []
    error = None
    if query:
        viewer_id = current_user.id if current_user.is_authenticated else None
        _, topics, user_rows, error = _unified_search(query, viewer_id=viewer_id)
        users = _serialize_user_search_results(user_rows)

    return render_template(
        'search.html',
        query=query,
        topics=topics,
        users=users,
        error=error,
    )


@app.route('/users/search')
def user_search_redirect():
    return redirect(url_for('site_search', q=request.args.get('q', '')))


@app.get('/api/v1/search')
def api_v1_search():
    query = (request.args.get('q') or '').strip()
    try:
        limit = int(request.args.get('limit', 8))
    except (TypeError, ValueError):
        limit = 8
    limit = min(max(limit, 1), 20)

    viewer_id = current_user.id if current_user.is_authenticated else None
    normalized, topics, user_rows, error = _unified_search(
        query,
        viewer_id=viewer_id,
        limit_topics=limit,
        limit_users=limit,
    )
    if error:
        return _api_error(error, 400, 'query_too_short')

    return jsonify({
        'ok': True,
        'query': normalized,
        'topics': topics,
        'users': _serialize_user_search_results(user_rows),
    })


@app.get('/api/v1/users/search')
def api_v1_search_users():
    query = (request.args.get('q') or '').strip()
    try:
        limit = int(request.args.get('limit', 20))
    except (TypeError, ValueError):
        limit = 20

    viewer_id = current_user.id if current_user.is_authenticated else None
    normalized, _, user_rows, error = _unified_search(
        query,
        viewer_id=viewer_id,
        limit_topics=0,
        limit_users=limit,
    )
    if error:
        return _api_error(error, 400, 'query_too_short')

    return jsonify({
        'ok': True,
        'query': normalize_handle(query),
        'users': _serialize_user_search_results(user_rows),
    })


@app.get('/api/v1/users/<handle>/profile')
def api_v1_user_profile(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')

    viewer_id = current_user.id if current_user.is_authenticated else None
    profile = _build_public_profile_json(target, viewer_id)
    if profile is None:
        return jsonify({
            'ok': False,
            'error': 'Profile is not accessible',
            'code': 'profile_private',
            'profile': {'handle': target.handle},
        }), 403

    return jsonify({'ok': True, 'profile': profile})


@app.post('/api/v1/users/<handle>/follow')
@login_required
def api_v1_follow_user(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')
    if target.id == current_user.id:
        return _api_error('You cannot follow yourself', 400, 'self_follow')

    with get_db() as conn:
        if is_blocked(conn, current_user.id, target.id):
            return _api_error('Cannot follow a blocked user', 403, 'blocked')
        if is_following(conn, current_user.id, target.id):
            unfollow_user(conn, current_user.id, target.id)
            following = False
        else:
            followed = follow_user(conn, current_user.id, target.id)
            following = True
            if followed:
                _notify_new_follower(conn, target.id, current_user.handle)
        followers_count = follower_count(conn, target.id)

    return jsonify({
        'ok': True,
        'handle': target.handle,
        'following': following,
        'followers_count': followers_count,
    })


@app.delete('/api/v1/users/<handle>/follow')
@login_required
def api_v1_unfollow_user(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')
    if target.id == current_user.id:
        return _api_error('You cannot unfollow yourself', 400, 'self_follow')

    with get_db() as conn:
        unfollow_user(conn, current_user.id, target.id)
        followers_count = follower_count(conn, target.id)

    return jsonify({
        'ok': True,
        'handle': target.handle,
        'following': False,
        'followers_count': followers_count,
    })


@app.post('/api/v1/generator/mcq-answer')
@login_required
def api_v1_generator_mcq_answer():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _api_error('JSON body required', 400, 'invalid_payload')

    level = (payload.get('level') or '').strip()
    subject = (payload.get('subject') or '').strip()
    topic = (payload.get('topic') or '').strip()
    difficulty = (payload.get('difficulty') or 'foundational').strip()
    user_answer = (payload.get('user_answer') or '').strip()
    correct_answer = (payload.get('correct_answer') or '').strip()
    correct = payload.get('correct')

    if not level or not subject or not topic:
        return _api_error('level, subject, and topic are required', 400, 'missing_fields')
    if not user_answer or not correct_answer:
        return _api_error('user_answer and correct_answer are required', 400, 'missing_fields')
    if correct not in (True, False):
        return _api_error('correct must be a boolean', 400, 'invalid_correct')

    try:
        TOPICS[level][subject][topic]
    except KeyError:
        return _api_error('Invalid topic', 400, 'invalid_topic')

    _track_mcq_answered(
        level,
        subject,
        topic,
        difficulty,
        user_answer,
        correct_answer,
        correct,
    )
    with get_db() as conn:
        streak = get_practice_streak(conn, current_user.id)

    return jsonify({'ok': True, 'practice_streak': streak})


@app.get('/api/v1/me/settings')
@login_required
def api_v1_get_settings():
    with get_db() as conn:
        settings = get_profile_settings(conn, current_user.id)
    return jsonify({'ok': True, 'settings': _settings_to_json(settings)})


@app.patch('/api/v1/me/settings')
@login_required
def api_v1_patch_settings():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _api_error('Request body must be a JSON object', 400, 'invalid_json')

    allowed_keys = {
        'profile_visibility',
        'show_member_since',
        'show_last_topic',
        'show_last_activity',
        'show_lesson_progress',
        'show_quiz_stats',
        'show_shared_questions',
        'auto_share_quiz',
        'auto_share_lesson',
        'default_share_visibility',
        'show_study_streak',
        'show_milestones',
    }
    unknown = set(payload.keys()) - allowed_keys
    if unknown:
        return _api_error(
            f'Unknown field(s): {", ".join(sorted(unknown))}',
            400,
            'invalid_field',
        )

    if 'profile_visibility' in payload:
        visibility = payload['profile_visibility']
        if visibility not in VISIBILITY_CHOICES:
            return _api_error(
                f'profile_visibility must be one of: {", ".join(VISIBILITY_CHOICES)}',
                400,
                'invalid_visibility',
            )

    if 'default_share_visibility' in payload:
        share_visibility = payload['default_share_visibility']
        if share_visibility not in VISIBILITY_CHOICES:
            return _api_error(
                f'default_share_visibility must be one of: {", ".join(VISIBILITY_CHOICES)}',
                400,
                'invalid_visibility',
            )

    bool_fields = (
        'show_member_since',
        'show_last_topic',
        'show_last_activity',
        'show_lesson_progress',
        'show_quiz_stats',
        'show_shared_questions',
        'auto_share_quiz',
        'auto_share_lesson',
        'show_study_streak',
        'show_milestones',
    )
    for field in bool_fields:
        if field in payload and not isinstance(payload[field], bool):
            return _api_error(f'{field} must be a boolean', 400, 'invalid_field')

    with get_db() as conn:
        current = _settings_to_json(get_profile_settings(conn, current_user.id))
        current.update(payload)
        update_profile_settings(conn, current_user.id, current)
        settings = _settings_to_json(get_profile_settings(conn, current_user.id))

    return jsonify({'ok': True, 'settings': settings})


@app.get('/api/v1/me/notifications')
@login_required
def api_v1_list_notifications():
    try:
        limit = min(max(int(request.args.get('limit', 20)), 1), 50)
    except (TypeError, ValueError):
        limit = 20
    before_id = request.args.get('before_id', type=int)
    with get_db() as conn:
        items = list_notifications(
            conn, current_user.id, limit=limit, before_id=before_id
        )
        unread = count_unread_notifications(conn, current_user.id)
    return jsonify({
        'ok': True,
        'unread_count': unread,
        'notifications': [_serialize_notification_item(item) for item in items],
        'next_before_id': items[-1]['id'] if items else None,
    })


@app.post('/api/v1/me/notifications/read')
@login_required
def api_v1_mark_notifications_read():
    payload = request.get_json(silent=True) or {}
    mark_all = bool(payload.get('all'))
    notification_id = payload.get('id')

    with get_db() as conn:
        if mark_all:
            mark_all_notifications_read(conn, current_user.id)
        elif notification_id is not None:
            if not mark_notification_read(conn, current_user.id, int(notification_id)):
                return _api_error('Notification not found', 404, 'not_found')
        else:
            return _api_error('Provide id or all: true', 400, 'invalid_payload')
        unread = count_unread_notifications(conn, current_user.id)

    return jsonify({'ok': True, 'unread_count': unread})


@app.get('/feed')
@login_required
def activity_feed():
    filter_name = normalize_feed_filter(request.args.get('filter', FEED_FILTER_ALL))
    items = _feed_items_for_viewer(current_user.id, filter_name)
    return render_template(
        'feed.html',
        filter=filter_name,
        items=items,
        feed_filters=(
            (FEED_FILTER_ALL, 'All'),
            (FEED_FILTER_LESSONS, 'Lessons'),
            (FEED_FILTER_QUIZZES, 'Quizzes'),
            (FEED_FILTER_SHARES, 'Shares'),
        ),
    )


@app.get('/api/v1/feed')
@login_required
def api_v1_feed():
    filter_name = normalize_feed_filter(request.args.get('filter', FEED_FILTER_ALL))
    try:
        limit = min(max(int(request.args.get('limit', 50)), 1), 100)
    except (TypeError, ValueError):
        limit = 50
    before_id = request.args.get('before_id', type=int)
    items = _feed_items_for_viewer(
        current_user.id, filter_name, limit=limit, before_id=before_id
    )
    return jsonify({
        'ok': True,
        'filter': filter_name,
        'items': items,
        'next_before_id': items[-1]['id'] if items else None,
    })


@app.get('/leaderboard/friends')
@login_required
def friend_leaderboard_page():
    with get_db() as conn:
        leaderboard = friend_effort_leaderboard(conn, current_user.id, days=7)
    for item in leaderboard:
        item['profile_url'] = url_for('public_profile', handle=item['handle'])
    return render_template(
        'leaderboard_friends.html',
        leaderboard=leaderboard,
        period_days=7,
    )


@app.get('/api/v1/me/gamification')
@login_required
def api_v1_me_gamification():
    with get_db() as conn:
        streak = get_study_streak(conn, current_user.id)
        milestones = list_user_milestones(conn, current_user.id)
        recap = get_weekly_recap(conn, current_user.id)
        leaderboard = friend_effort_leaderboard(conn, current_user.id, days=7)
    if recap.get('best_quiz'):
        bq = recap['best_quiz']
        bq['topic_label'] = _topic_label(bq['level'], bq['subject'], bq['topic'])
    return jsonify({
        'ok': True,
        'study_streak': streak,
        'milestones': milestones,
        'weekly_recap': recap,
        'friend_leaderboard': [
            {
                'rank': item['rank'],
                'handle': item['handle'],
                'score': item['score'],
                'is_viewer': item['is_viewer'],
            }
            for item in leaderboard
        ],
    })


GENERATE_DAILY_LIMIT = 200
REPORT_DAILY_LIMIT = 20
DIFFICULTIES = ('foundational', 'intermediate', 'difficult')


def _client_ip():
    forwarded = (request.headers.get('X-Forwarded-For') or '').split(',')[0].strip()
    return forwarded or (request.remote_addr or 'unknown')


def _api_rate_limit(action, limit):
    """Return (allowed, remaining) or abort with JSON error via tuple (False, 0)."""
    if current_user.is_authenticated:
        bucket = f'{action}:user:{current_user.id}'
    else:
        bucket = f'{action}:ip:{_client_ip()}'
    with get_db() as conn:
        allowed, remaining, _count = check_and_increment_rate_limit(conn, bucket, limit)
    return allowed, remaining


def _build_topics_catalog():
    levels = []
    for level in _TOPIC_LEVEL_ORDER:
        subjects_map = TOPICS.get(level) or {}
        subjects = []
        for subject in _TOPIC_SUBJECT_ORDER.get(level, tuple(subjects_map.keys())):
            topics_map = subjects_map.get(subject) or {}
            topics = []
            for slug, cfg in sorted(topics_map.items(), key=lambda x: x[1]['name'].lower()):
                has_variants = bool(cfg.get('variants_func'))
                modes = ['standard']
                if has_variants:
                    modes.append('mcq')
                if _lesson_quiz_available(level, subject, slug):
                    modes.append('lesson')
                topics.append({
                    'slug': slug,
                    'name': cfg['name'],
                    'url': f'/topic/{level}/{subject}/{slug}',
                    'has_variants': has_variants,
                    'supports_lesson_mcq': topic_supports_lesson_mcq(cfg),
                    'modes': modes,
                    'difficulties': list(DIFFICULTIES),
                })
            subjects.append({
                'id': subject,
                'label': SUBJECT_LABELS.get(subject, subject.title()),
                'topics': topics,
            })
        levels.append({
            'id': level,
            'label': LEVEL_LABELS.get(level, level.title()),
            'subjects': subjects,
        })
    return levels


@app.get('/api/v1/topics')
def api_v1_topics_catalog():
    return jsonify({'ok': True, 'levels': _build_topics_catalog()})


@app.post('/api/v1/problems/generate')
def api_v1_generate_problem():
    payload = request.get_json(silent=True) or {}
    level = (payload.get('level') or 'gcse').strip()
    subject = (payload.get('subject') or 'maths').strip()
    topic = _resolve_topic_slug(level, subject, (payload.get('topic') or '').strip())
    mode = normalize_mode(payload.get('mode') or 'standard')
    difficulty = (payload.get('difficulty') or 'foundational').strip()
    action = (payload.get('action') or 'start').strip().lower()

    if action not in ('start', 'next', 'reroll'):
        return _api_error('action must be start, next, or reroll', 400, 'invalid_action')
    if difficulty not in DIFFICULTIES:
        return _api_error(
            f'difficulty must be one of: {", ".join(DIFFICULTIES)}',
            400,
            'invalid_difficulty',
        )
    if not _topic_path_valid(level, subject, topic):
        return _api_error('Topic not found', 404, 'topic_not_found')
    if not can_access_difficulty(current_user, difficulty):
        return _api_error(
            'Difficult questions require a free account',
            403,
            'difficulty_locked',
        )

    allowed, remaining = _api_rate_limit('generate', GENERATE_DAILY_LIMIT)
    if not allowed:
        return _api_error('Daily generate limit reached', 429, 'rate_limited')

    topic_config = TOPICS[level][subject][topic]
    user_id = current_user.id if current_user.is_authenticated else None
    meta = {
        'variant_name': None,
        'queue_position': 0,
        'queue_length': 0,
        'can_reroll': False,
    }

    try:
        if action == 'reroll':
            if not user_id and not session.get('problem_variant_name'):
                return _api_error('Nothing to reroll — generate a problem first', 400, 'no_variant')
            problem = _reroll_current_problem(
                topic_config, level, subject, topic, mode, difficulty, user_id=user_id
            )
            if problem is None:
                return _api_error('Could not reroll this question', 400, 'reroll_failed')
            queue_key = _selection_key(level, subject, topic, mode, difficulty)
            _queue, idx, variant_name = _load_queue_state(user_id, queue_key)
            meta = {
                'variant_name': variant_name,
                'queue_position': (idx + 1) if _queue else 0,
                'queue_length': len(_queue) if _queue else 0,
                'can_reroll': _can_reroll_variant(
                    topic_config, mode, difficulty, variant_name
                ),
            }
        elif topic_config.get('variants_func'):
            problem, meta = _generate_queued_problem(
                topic_config,
                level,
                subject,
                topic,
                mode,
                difficulty,
                action,
                user_id=user_id,
            )
        else:
            problem = topic_config['func'](difficulty, mode)
    except Exception:
        return _api_error('Could not generate problem', 500, 'generate_failed')

    if problem is None:
        return _api_error('Could not generate problem', 500, 'generate_failed')

    if user_id:
        session['last_problem_payload'] = {
            'level': level,
            'subject': subject,
            'topic': topic,
            'mode': mode,
            'difficulty': difficulty,
            'variant_name': meta.get('variant_name') or problem.get('variant_name'),
            'problem': problem,
        }
        session.modified = True
        _track_question_generated(level, subject, topic, difficulty)

    client = _problem_client_payload(problem)
    client['difficulty'] = difficulty
    client['level'] = level
    client['subject'] = subject
    client['topic'] = topic
    client['mode'] = mode
    client['topic_label'] = _topic_label(level, subject, topic)

    return jsonify({
        'ok': True,
        'problem': client,
        'selection': meta,
        'rate_limit_remaining': remaining,
    })


@app.get('/api/v1/me/saved-problems')
@login_required
def api_v1_list_saved_problems():
    try:
        limit = min(max(int(request.args.get('limit', 50)), 1), 100)
    except (TypeError, ValueError):
        limit = 50
    with get_db() as conn:
        saved = list_saved_problems(conn, current_user.id, limit=limit)
    items = []
    for item in saved:
        items.append({
            'id': item['id'],
            'level': item['level'],
            'subject': item['subject'],
            'topic': item['topic'],
            'topic_label': _topic_label(item['level'], item['subject'], item['topic']),
            'mode': item['mode'],
            'difficulty': item['difficulty'],
            'created_at': item['created_at'],
            'problem': _problem_client_payload(item['problem']),
        })
    return jsonify({'ok': True, 'saved_problems': items})


@app.get('/api/v1/me/saved-problems/<int:saved_id>')
@login_required
def api_v1_get_saved_problem(saved_id):
    with get_db() as conn:
        saved = get_saved_problem(conn, current_user.id, saved_id)
    if not saved:
        return _api_error('Saved question not found', 404, 'not_found')
    return jsonify({
        'ok': True,
        'saved_problem': {
            'id': saved['id'],
            'level': saved['level'],
            'subject': saved['subject'],
            'topic': saved['topic'],
            'topic_label': _topic_label(saved['level'], saved['subject'], saved['topic']),
            'mode': saved['mode'],
            'difficulty': saved['difficulty'],
            'created_at': saved['created_at'],
            'problem': _problem_client_payload(saved['problem']),
        },
    })


@app.post('/api/v1/me/saved-problems')
@login_required
def api_v1_save_problem():
    payload = request.get_json(silent=True) or {}
    data = _problem_from_session_payload()
    if not data and isinstance(payload.get('problem'), dict):
        level = payload.get('level')
        subject = payload.get('subject')
        topic = payload.get('topic')
        if not _topic_path_valid(level, subject, topic):
            return _api_error('Topic not found', 404, 'topic_not_found')
        data = {
            'level': level,
            'subject': subject,
            'topic': topic,
            'mode': normalize_mode(payload.get('mode', 'standard')),
            'difficulty': payload.get('difficulty', 'foundational'),
            'problem': payload['problem'],
        }
    if not data:
        return _api_error('Generate a question first, then save it', 400, 'no_problem')

    try:
        with get_db() as conn:
            saved_id = save_problem(
                conn,
                current_user.id,
                data['level'],
                data['subject'],
                data['topic'],
                data['mode'],
                data['difficulty'],
                data['problem'],
            )
    except ValueError:
        return _api_error('Saved question limit reached (200)', 400, 'saved_limit')

    return jsonify({
        'ok': True,
        'saved_id': saved_id,
        'url': url_for('view_saved_problem', saved_id=saved_id),
    })


@app.delete('/api/v1/me/saved-problems/<int:saved_id>')
@login_required
def api_v1_delete_saved_problem(saved_id):
    with get_db() as conn:
        deleted = delete_saved_problem(conn, current_user.id, saved_id)
    if not deleted:
        return _api_error('Saved question not found', 404, 'not_found')
    return jsonify({'ok': True})


@app.post('/api/v1/users/<handle>/block')
@login_required
def api_v1_block_user(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')
    if target.id == current_user.id:
        return _api_error('You cannot block yourself', 400, 'self_block')
    with get_db() as conn:
        block_user(conn, current_user.id, target.id)
    return jsonify({'ok': True, 'handle': target.handle, 'blocked': True})


@app.delete('/api/v1/users/<handle>/block')
@login_required
def api_v1_unblock_user(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')
    with get_db() as conn:
        unblock_user(conn, current_user.id, target.id)
    return jsonify({'ok': True, 'handle': target.handle, 'blocked': False})


@app.get('/api/v1/me/blocks')
@login_required
def api_v1_list_blocks():
    with get_db() as conn:
        blocked = list_blocked_users(conn, current_user.id)
    return jsonify({
        'ok': True,
        'blocked': [
            {'handle': item['handle'], 'blocked_at': item['blocked_at']}
            for item in blocked
        ],
    })


@app.post('/api/v1/users/<handle>/report')
@login_required
def api_v1_report_user(handle):
    target = _resolve_active_user_by_handle(handle)
    if not target:
        return _api_error('User not found', 404, 'user_not_found')
    if target.id == current_user.id:
        return _api_error('You cannot report yourself', 400, 'self_report')

    allowed, remaining = _api_rate_limit('report', REPORT_DAILY_LIMIT)
    if not allowed:
        return _api_error('Daily report limit reached', 429, 'rate_limited')

    payload = request.get_json(silent=True) or {}
    report_type = (payload.get('report_type') or 'other').strip().lower()
    if report_type not in REPORT_TYPES:
        return _api_error(
            f'report_type must be one of: {", ".join(sorted(REPORT_TYPES))}',
            400,
            'invalid_report_type',
        )
    note = (payload.get('note') or '').strip()
    context = payload.get('context') if isinstance(payload.get('context'), dict) else {}

    with get_db() as conn:
        report_id = create_report(
            conn,
            current_user.id,
            reported_user_id=target.id,
            report_type=report_type,
            note=note,
            context=context,
        )
    return jsonify({
        'ok': True,
        'report_id': report_id,
        'rate_limit_remaining': remaining,
    })


@app.route('/saved-problems')
@login_required
def saved_problems_index():
    with get_db() as conn:
        saved = list_saved_problems(conn, current_user.id, limit=100)
    for item in saved:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
    return render_template('saved_problems.html', saved_problems=saved)


@app.route('/saved-problems/<int:saved_id>')
@login_required
def view_saved_problem(saved_id):
    with get_db() as conn:
        saved = get_saved_problem(conn, current_user.id, saved_id)
    if not saved:
        return 'Saved question not found', 404
    problem = saved['problem']
    can_reroll_variant = False
    try:
        topic_config = TOPICS[saved['level']][saved['subject']][saved['topic']]
        can_reroll_variant = _can_reroll_variant(
            topic_config,
            normalize_mode(saved['mode']),
            saved['difficulty'],
            problem.get('variant_name'),
        )
    except KeyError:
        can_reroll_variant = False
    return render_template(
        'saved_problem.html',
        saved=saved,
        problem=problem,
        topic_label=_topic_label(saved['level'], saved['subject'], saved['topic']),
        can_reroll_variant=can_reroll_variant,
    )


@app.post('/saved-problems/save')
@login_required
def save_problem_route():
    wants_json = _wants_json_response()

    if not _validate_csrf(request.form.get('csrf_token')):
        message = 'Your session expired. Please try again.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 403
        flash(message, 'error')
        return redirect(url_for('index'))

    payload = session.get('last_problem_payload')
    if not payload or not isinstance(payload.get('problem'), dict):
        message = 'Generate a question first, then save it.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    level = payload['level']
    subject = payload['subject']
    topic = payload['topic']
    mode = normalize_mode(payload.get('mode', 'standard'))
    difficulty = payload.get('difficulty', 'foundational')
    problem = dict(payload['problem'])
    variant_name = payload.get('variant_name') or problem.get('variant_name')
    if variant_name:
        problem['variant_name'] = variant_name

    if not _topic_path_valid(level, subject, topic):
        message = 'Could not save that question.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    if not problem.get('question'):
        message = 'Could not save that question.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    try:
        with get_db() as conn:
            saved_id = save_problem(
                conn,
                current_user.id,
                level,
                subject,
                topic,
                mode,
                difficulty,
                problem,
            )
    except ValueError:
        message = 'You have reached the saved question limit (200). Delete some to save more.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('index'))

    message = 'Question saved to your profile.'
    if wants_json:
        return jsonify({
            'ok': True,
            'message': message,
            'saved_id': saved_id,
            'saved_url': url_for('view_saved_problem', saved_id=saved_id),
        })

    flash(message, 'success')
    return redirect(url_for('index'))


@app.post('/saved-problems/<int:saved_id>/reroll')
@login_required
def reroll_saved_problem_route(saved_id):
    wants_json = _wants_json_response()

    if not _validate_csrf(request.form.get('csrf_token')):
        message = 'Your session expired. Please try again.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 403
        flash(message, 'error')
        return redirect(url_for('view_saved_problem', saved_id=saved_id))

    with get_db() as conn:
        saved = get_saved_problem(conn, current_user.id, saved_id)
    if not saved:
        message = 'Saved question not found.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 404
        flash(message, 'error')
        return redirect(url_for('saved_problems_index'))

    problem = saved['problem']
    variant_name = problem.get('variant_name')
    mode = normalize_mode(saved['mode'])
    level = saved['level']
    subject = saved['subject']
    topic = saved['topic']
    difficulty = saved['difficulty']

    try:
        topic_config = TOPICS[level][subject][topic]
    except KeyError:
        message = 'Could not refresh this question.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('view_saved_problem', saved_id=saved_id))

    if not _can_reroll_variant(topic_config, mode, difficulty, variant_name):
        message = 'This saved question cannot be refreshed with new numbers.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(url_for('view_saved_problem', saved_id=saved_id))

    try:
        new_problem = _reroll_variant_problem(topic_config, mode, difficulty, variant_name)
    except Exception:
        new_problem = None

    if not new_problem or not new_problem.get('question'):
        message = 'Could not refresh this question. Try again later.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 500
        flash(message, 'error')
        return redirect(url_for('view_saved_problem', saved_id=saved_id))

    new_problem = dict(new_problem)
    new_problem['variant_name'] = variant_name

    with get_db() as conn:
        updated = update_saved_problem(conn, current_user.id, saved_id, new_problem)
    if not updated:
        message = 'Saved question not found.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 404
        flash(message, 'error')
        return redirect(url_for('saved_problems_index'))

    message = 'New numbers generated for this saved question.'
    if wants_json:
        return jsonify({
            'ok': True,
            'message': message,
            'problem': _problem_client_payload(new_problem),
            'can_reroll_variant': True,
        })

    flash(message, 'success')
    return redirect(url_for('view_saved_problem', saved_id=saved_id))


@app.post('/saved-problems/<int:saved_id>/delete')
@login_required
def delete_saved_problem_route(saved_id):
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(url_for('profile'))

    with get_db() as conn:
        deleted = delete_saved_problem(conn, current_user.id, saved_id)
    if deleted:
        flash('Saved question removed.', 'success')
    else:
        flash('Saved question not found.', 'error')
    next_url = request.form.get('next') or url_for('profile')
    if not next_url.startswith('/'):
        next_url = url_for('profile')
    return redirect(next_url)


def _share_problem_from_data(user_id, data, visibility, note=''):
    share_id = None
    with get_db() as conn:
        share_id = create_shared_question(
            conn,
            user_id,
            data['level'],
            data['subject'],
            data['topic'],
            data['mode'],
            data['difficulty'],
            data['problem'],
            visibility=visibility,
            note=note,
        )
        record_activity_event(
            conn,
            user_id,
            ACTIVITY_QUESTION_SHARED,
            {
                'share_id': share_id,
                'level': data['level'],
                'subject': data['subject'],
                'topic': data['topic'],
                'topic_label': _topic_label(data['level'], data['subject'], data['topic']),
                'note': note,
            },
            visibility,
        )
    return share_id


@app.post('/shared-questions/share')
@login_required
def share_question_route():
    wants_json = _wants_json_response()
    if not _validate_csrf(request.form.get('csrf_token')):
        message = 'Your session expired. Please try again.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 403
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    visibility = _normalize_share_visibility(
        request.form.get('visibility') or VISIBILITY_FOLLOWERS
    )
    note = (request.form.get('note') or '').strip()[:200]
    saved_id = request.form.get('saved_id', type=int)

    if saved_id:
        with get_db() as conn:
            saved = get_saved_problem(conn, current_user.id, saved_id)
        if not saved:
            message = 'Saved question not found.'
            if wants_json:
                return jsonify({'ok': False, 'error': message}), 404
            flash(message, 'error')
            return redirect(url_for('profile'))
        data = {
            'level': saved['level'],
            'subject': saved['subject'],
            'topic': saved['topic'],
            'mode': normalize_mode(saved['mode']),
            'difficulty': saved['difficulty'],
            'problem': saved['problem'],
        }
    else:
        data = _problem_from_session_payload()
        if not data:
            message = 'Generate a question first, then share it.'
            if wants_json:
                return jsonify({'ok': False, 'error': message}), 400
            flash(message, 'error')
            return redirect(url_for('index'))

    try:
        share_id = _share_problem_from_data(current_user.id, data, visibility, note)
    except ValueError:
        message = 'You have reached the shared question limit (200).'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    share_url = url_for('view_shared_question', share_id=share_id)
    message = 'Question shared.'
    if wants_json:
        return jsonify({'ok': True, 'message': message, 'share_id': share_id, 'share_url': share_url})
    flash(message, 'success')
    return redirect(share_url)


@app.get('/shared/<int:share_id>')
def view_shared_question(share_id):
    with get_db() as conn:
        shared = get_shared_question(conn, share_id)
    if not shared:
        return 'Shared question not found', 404

    viewer_id = current_user.id if current_user.is_authenticated else None
    with get_db() as conn:
        if not can_view_share(conn, viewer_id, shared['user_id'], shared['visibility']):
            return render_template(
                'shared_question_private.html',
                owner_handle=shared.get('owner_handle'),
            )

    topic_label = _topic_label(shared['level'], shared['subject'], shared['topic'])
    return render_template(
        'shared_question.html',
        shared=shared,
        problem=shared['problem'],
        topic_label=topic_label,
        owner_handle=shared.get('owner_handle'),
    )


@app.route('/suggestions')
@login_required
def suggestions_inbox():
    status = request.args.get('status', SUGGESTION_PENDING)
    if status not in (SUGGESTION_PENDING, SUGGESTION_OPENED, SUGGESTION_DISMISSED, 'all'):
        status = SUGGESTION_PENDING
    with get_db() as conn:
        if status == 'all':
            items = list_suggestions_inbox(conn, current_user.id, limit=100)
        else:
            items = list_suggestions_inbox(conn, current_user.id, status=status, limit=100)
    for item in items:
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
    return render_template(
        'suggestions.html',
        suggestions=items,
        filter_status=status,
    )


@app.post('/suggestions')
@login_required
def create_suggestion_route():
    wants_json = _wants_json_response()
    if not _validate_csrf(request.form.get('csrf_token')):
        message = 'Your session expired. Please try again.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 403
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    recipient_handle = normalize_handle(request.form.get('recipient_handle', ''))
    note = (request.form.get('note') or '').strip()[:200]
    saved_id = request.form.get('saved_id', type=int)

    if not recipient_handle:
        message = 'Enter a recipient handle.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    with get_db() as conn:
        recipient = get_user_by_handle(conn, recipient_handle)
    if not recipient or not recipient.is_active:
        message = 'User not found.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 404
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    if saved_id:
        with get_db() as conn:
            saved = get_saved_problem(conn, current_user.id, saved_id)
        if not saved:
            message = 'Saved question not found.'
            if wants_json:
                return jsonify({'ok': False, 'error': message}), 404
            flash(message, 'error')
            return redirect(url_for('profile'))
        data = {
            'level': saved['level'],
            'subject': saved['subject'],
            'topic': saved['topic'],
            'mode': normalize_mode(saved['mode']),
            'difficulty': saved['difficulty'],
            'problem': saved['problem'],
        }
    else:
        data = _problem_from_session_payload()
        if not data:
            message = 'Generate a question first, then suggest it.'
            if wants_json:
                return jsonify({'ok': False, 'error': message}), 400
            flash(message, 'error')
            return redirect(url_for('index'))

    try:
        with get_db() as conn:
            suggestion_id = create_suggestion(
                conn,
                current_user.id,
                recipient.id,
                data['level'],
                data['subject'],
                data['topic'],
                data['mode'],
                data['difficulty'],
                data['problem'],
                note=note,
            )
            record_activity_event(
                conn,
                current_user.id,
                ACTIVITY_SUGGESTION_SENT,
                {
                    'suggestion_id': suggestion_id,
                    'recipient_handle': recipient.handle,
                    'level': data['level'],
                    'subject': data['subject'],
                    'topic': data['topic'],
                    'topic_label': _topic_label(data['level'], data['subject'], data['topic']),
                },
                VISIBILITY_FOLLOWERS,
            )
            topic_label = _topic_label(data['level'], data['subject'], data['topic'])
            _notify_suggestion_received(
                conn,
                recipient.id,
                current_user.handle,
                suggestion_id,
                topic_label,
            )
    except ValueError as exc:
        if str(exc) == 'self_suggest':
            message = 'You cannot suggest a question to yourself.'
        else:
            message = 'That user has too many pending suggestions.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 400
        flash(message, 'error')
        return redirect(request.referrer or url_for('index'))

    message = f'Question sent to @{recipient.handle}.'
    if wants_json:
        return jsonify({'ok': True, 'message': message, 'suggestion_id': suggestion_id})
    flash(message, 'success')
    return redirect(url_for('suggestions_inbox'))


@app.get('/suggestions/<int:suggestion_id>')
@login_required
def view_suggestion(suggestion_id):
    with get_db() as conn:
        item = get_suggestion(conn, suggestion_id, recipient_id=current_user.id)
        if item:
            mark_suggestion_opened(conn, suggestion_id, current_user.id)
            mark_suggestion_notifications_read(conn, current_user.id, suggestion_id)
    if not item:
        return 'Suggestion not found', 404
    topic_label = _topic_label(item['level'], item['subject'], item['topic'])
    return render_template(
        'suggestion_view.html',
        suggestion=item,
        problem=item['problem'],
        topic_label=topic_label,
    )


@app.post('/suggestions/<int:suggestion_id>/dismiss')
@login_required
def dismiss_suggestion_route(suggestion_id):
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(url_for('suggestions_inbox'))
    with get_db() as conn:
        dismissed = dismiss_suggestion(conn, suggestion_id, current_user.id)
    if dismissed:
        flash('Suggestion dismissed.', 'success')
    else:
        flash('Suggestion not found.', 'error')
    return redirect(url_for('suggestions_inbox'))


@app.post('/quiz-attempts/<int:attempt_id>/share')
@login_required
def share_quiz_attempt_route(attempt_id):
    wants_json = _wants_json_response()
    if not _validate_csrf(request.form.get('csrf_token')):
        message = 'Your session expired. Please try again.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 403
        flash(message, 'error')
        return redirect(url_for('profile'))

    visibility = _normalize_share_visibility(
        request.form.get('visibility') or VISIBILITY_FOLLOWERS
    )
    with get_db() as conn:
        attempt = get_quiz_attempt(conn, current_user.id, attempt_id)
    if not attempt:
        message = 'Quiz attempt not found.'
        if wants_json:
            return jsonify({'ok': False, 'error': message}), 404
        flash(message, 'error')
        return redirect(url_for('profile'))

    _record_user_activity(
        current_user.id,
        ACTIVITY_QUIZ_COMPLETED,
        {
            'level': attempt['level'],
            'subject': attempt['subject'],
            'topic': attempt['topic'],
            'topic_label': _topic_label(attempt['level'], attempt['subject'], attempt['topic']),
            'score': attempt['score'],
            'total': attempt['total'],
            'attempt_id': attempt_id,
            'shared': True,
        },
        visibility,
    )
    message = 'Quiz score shared to your activity feed.'
    if wants_json:
        return jsonify({'ok': True, 'message': message})
    flash(message, 'success')
    return redirect(url_for('view_quiz_attempt', attempt_id=attempt_id))


@app.post('/api/v1/shared-questions')
@login_required
def api_v1_create_share():
    payload = request.get_json(silent=True) or {}
    visibility = _normalize_share_visibility(
        payload.get('visibility') or VISIBILITY_FOLLOWERS
    )
    note = (payload.get('note') or '').strip()[:200]
    saved_id = payload.get('saved_id')

    if saved_id:
        with get_db() as conn:
            saved = get_saved_problem(conn, current_user.id, int(saved_id))
        if not saved:
            return _api_error('Saved question not found', 404, 'not_found')
        data = {
            'level': saved['level'],
            'subject': saved['subject'],
            'topic': saved['topic'],
            'mode': normalize_mode(saved['mode']),
            'difficulty': saved['difficulty'],
            'problem': saved['problem'],
        }
    else:
        data = _problem_from_session_payload()
        if not data:
            return _api_error('Generate a question first', 400, 'no_problem')

    try:
        share_id = _share_problem_from_data(current_user.id, data, visibility, note)
    except ValueError:
        return _api_error('Shared question limit reached', 400, 'share_limit')

    return jsonify({
        'ok': True,
        'share_id': share_id,
        'share_url': url_for('view_shared_question', share_id=share_id),
    })


@app.get('/api/v1/shared-questions/<int:share_id>')
def api_v1_get_share(share_id):
    with get_db() as conn:
        shared = get_shared_question(conn, share_id)
    if not shared:
        return _api_error('Shared question not found', 404, 'not_found')

    viewer_id = current_user.id if current_user.is_authenticated else None
    with get_db() as conn:
        if not can_view_share(conn, viewer_id, shared['user_id'], shared['visibility']):
            return _api_error('Shared question is not accessible', 403, 'not_accessible')

    return jsonify({
        'ok': True,
        'share': {
            'id': shared['id'],
            'owner_handle': shared.get('owner_handle'),
            'level': shared['level'],
            'subject': shared['subject'],
            'topic': shared['topic'],
            'topic_label': _topic_label(shared['level'], shared['subject'], shared['topic']),
            'mode': shared['mode'],
            'difficulty': shared['difficulty'],
            'note': shared.get('note') or '',
            'created_at': shared['created_at'],
            'problem': _problem_client_payload(shared['problem']),
        },
    })


@app.get('/api/v1/me/suggestions')
@login_required
def api_v1_list_suggestions():
    status = request.args.get('status', SUGGESTION_PENDING)
    with get_db() as conn:
        if status == 'all':
            items = list_suggestions_inbox(conn, current_user.id, limit=50)
        elif status in (SUGGESTION_PENDING, SUGGESTION_OPENED, SUGGESTION_DISMISSED):
            items = list_suggestions_inbox(conn, current_user.id, status=status, limit=50)
        else:
            return _api_error('Invalid status', 400, 'invalid_status')
    out = []
    for item in items:
        out.append({
            'id': item['id'],
            'sender_handle': item['sender_handle'],
            'status': item['status'],
            'note': item.get('note') or '',
            'topic_label': _topic_label(item['level'], item['subject'], item['topic']),
            'created_at': item['created_at'],
            'url': url_for('view_suggestion', suggestion_id=item['id']),
        })
    return jsonify({'ok': True, 'suggestions': out})


@app.post('/api/v1/suggestions')
@login_required
def api_v1_create_suggestion():
    payload = request.get_json(silent=True) or {}
    recipient_handle = normalize_handle(payload.get('recipient_handle', ''))
    note = (payload.get('note') or '').strip()[:200]
    saved_id = payload.get('saved_id')

    if not recipient_handle:
        return _api_error('recipient_handle is required', 400, 'invalid_field')

    with get_db() as conn:
        recipient = get_user_by_handle(conn, recipient_handle)
    if not recipient or not recipient.is_active:
        return _api_error('User not found', 404, 'user_not_found')

    if saved_id:
        with get_db() as conn:
            saved = get_saved_problem(conn, current_user.id, int(saved_id))
        if not saved:
            return _api_error('Saved question not found', 404, 'not_found')
        data = {
            'level': saved['level'],
            'subject': saved['subject'],
            'topic': saved['topic'],
            'mode': normalize_mode(saved['mode']),
            'difficulty': saved['difficulty'],
            'problem': saved['problem'],
        }
    else:
        data = _problem_from_session_payload()
        if not data:
            return _api_error('Generate a question first', 400, 'no_problem')

    try:
        with get_db() as conn:
            suggestion_id = create_suggestion(
                conn,
                current_user.id,
                recipient.id,
                data['level'],
                data['subject'],
                data['topic'],
                data['mode'],
                data['difficulty'],
                data['problem'],
                note=note,
            )
            record_activity_event(
                conn,
                current_user.id,
                ACTIVITY_SUGGESTION_SENT,
                {
                    'suggestion_id': suggestion_id,
                    'recipient_handle': recipient.handle,
                    'level': data['level'],
                    'subject': data['subject'],
                    'topic': data['topic'],
                    'topic_label': _topic_label(data['level'], data['subject'], data['topic']),
                },
                VISIBILITY_FOLLOWERS,
            )
            topic_label = _topic_label(data['level'], data['subject'], data['topic'])
            _notify_suggestion_received(
                conn,
                recipient.id,
                current_user.handle,
                suggestion_id,
                topic_label,
            )
    except ValueError as exc:
        code = 'self_suggest' if str(exc) == 'self_suggest' else 'inbox_limit'
        message = (
            'You cannot suggest a question to yourself'
            if code == 'self_suggest'
            else 'That user has too many pending suggestions'
        )
        return _api_error(message, 400, code)

    return jsonify({
        'ok': True,
        'suggestion_id': suggestion_id,
        'url': url_for('view_suggestion', suggestion_id=suggestion_id),
    })


@app.post('/api/v1/suggestions/<int:suggestion_id>/dismiss')
@login_required
def api_v1_dismiss_suggestion(suggestion_id):
    with get_db() as conn:
        dismissed = dismiss_suggestion(conn, suggestion_id, current_user.id)
    if not dismissed:
        return _api_error('Suggestion not found', 404, 'not_found')
    return jsonify({'ok': True})


@app.get('/api/lesson-progress/<level>/<subject>/<topic>')
@login_required
def api_get_lesson_progress(level, subject, topic):
    if not _topic_path_valid(level, subject, topic):
        return jsonify({'error': 'Topic not found'}), 404
    with get_db() as conn:
        progress = get_lesson_progress(conn, current_user.id, level, subject, topic)
    if not progress:
        return jsonify({'progress': None})
    return jsonify({'progress': progress})


@app.post('/api/lesson-progress')
@login_required
def api_save_lesson_progress():
    payload = request.get_json(silent=True) or {}
    if not _validate_csrf(payload.get('csrf_token')):
        return jsonify({'error': 'Invalid session'}), 403

    level = payload.get('level', '')
    subject = payload.get('subject', '')
    topic = payload.get('topic', '')
    section_key = (payload.get('section_key') or '').strip()
    section_label = (payload.get('section_label') or '').strip()[:200]
    completed_keys = payload.get('completed_keys')
    if completed_keys is not None:
        if not isinstance(completed_keys, list):
            return jsonify({'error': 'Invalid completed steps'}), 400
        completed_keys = [
            str(key).strip()[:80]
            for key in completed_keys
            if str(key).strip()
        ]

    if not _topic_path_valid(level, subject, topic):
        return jsonify({'error': 'Topic not found'}), 404
    if not section_key or len(section_key) > 80:
        return jsonify({'error': 'Invalid section'}), 400

    with get_db() as conn:
        upsert_lesson_progress(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            section_key,
            section_label,
            completed_keys=completed_keys,
        )
        progress = get_lesson_progress(conn, current_user.id, level, subject, topic)
        settings = get_profile_settings(conn, current_user.id)
    completed_count = len((progress or {}).get('completed_keys') or [])
    visibility = VISIBILITY_FOLLOWERS
    if settings.get('auto_share_lesson'):
        visibility = _normalize_share_visibility(settings.get('default_share_visibility'))
    _record_user_activity(
        current_user.id,
        ACTIVITY_LESSON_STEP_COMPLETED,
        {
            'level': level,
            'subject': subject,
            'topic': topic,
            'topic_label': _topic_label(level, subject, topic),
            'section_key': section_key,
            'section_label': section_label,
            'completed_count': completed_count,
            'auto_shared': bool(settings.get('auto_share_lesson')),
        },
        visibility,
    )
    if completed_count > 0:
        _record_study_activity(current_user.id)
    return jsonify({'ok': True})


@app.post('/lesson-progress/<level>/<subject>/<topic>/clear')
@login_required
def clear_lesson_progress_route(level, subject, topic):
    if not _validate_csrf(request.form.get('csrf_token')):
        flash('Your session expired. Please try again.', 'error')
        return redirect(url_for('profile'))

    with get_db() as conn:
        clear_lesson_progress(conn, current_user.id, level, subject, topic)
    flash('Lesson bookmark cleared.', 'success')
    return redirect(url_for('profile'))


@app.route('/quiz-attempts/<int:attempt_id>')
@login_required
def view_quiz_attempt(attempt_id):
    with get_db() as conn:
        attempt = get_quiz_attempt(conn, current_user.id, attempt_id)
    if not attempt:
        return 'Quiz attempt not found', 404
    if not attempt.get('problems'):
        flash(
            'Full review is not available for this older attempt. Try a new quiz on the same topic.',
            'error',
        )
        return redirect(url_for('profile'))

    topic_name = _topic_label(attempt['level'], attempt['subject'], attempt['topic'])
    g.lesson_meta = _lesson_meta_for_topic(
        attempt['level'],
        attempt['subject'],
        attempt['topic'],
        quiz_review=True,
    )
    lesson_url = url_for(
        'topic_page',
        level=attempt['level'],
        subject=attempt['subject'],
        topic=attempt['topic'],
    )
    problems = enrich_quiz_attempt_problems(attempt['problems'], attempt['answers'])
    return _render_quiz_results(
        problems,
        attempt['score'],
        attempt['total'],
        topic_name,
        lesson_url,
        attempt['level'],
        attempt['subject'],
        attempt['topic'],
        attempt_date=attempt['created_at'][:10] if attempt.get('created_at') else None,
        back_url=url_for('profile'),
        back_label='← Back to profile',
        show_wrong_explanations_only=True,
        quiz_attempt_id=attempt_id,
    )


def _lesson_assist_client_ip():
    forwarded = request.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _lesson_assist_session_key():
    sid = session.get('lesson_assist_sid')
    if not sid:
        sid = str(uuid.uuid4())
        session['lesson_assist_sid'] = sid
        session.modified = True
    return sid


def _lesson_assist_usage_count(day, client_key):
    with get_db() as conn:
        row = conn.execute(
            "SELECT count FROM lesson_assist_usage WHERE day = ? AND client_key = ?",
            (day, client_key),
        ).fetchone()
    return int(row['count']) if row else 0


def _lesson_assist_increment(day, client_key):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO lesson_assist_usage (day, client_key, count)
            VALUES (?, ?, 1)
            ON CONFLICT(day, client_key) DO UPDATE SET count = count + 1
            """,
            (day, client_key),
        )
        conn.commit()


def _lesson_assist_rate_limit():
    """Return (allowed, remaining, error_code)."""
    if not lesson_assist_enabled():
        return False, 0, 'assistant_unavailable'

    day = date.today().isoformat()
    ip_key = f"ip:{_lesson_assist_client_ip()}"
    session_key = f"session:{_lesson_assist_session_key()}"

    ip_count = _lesson_assist_usage_count(day, ip_key)
    session_count = _lesson_assist_usage_count(day, session_key)
    ip_max = daily_limit_ip()
    session_max = daily_limit_session()

    if ip_count >= ip_max or session_count >= session_max:
        return False, 0, 'rate_limited'

    remaining = min(ip_max - ip_count, session_max - session_count)
    return True, remaining, None


def _lesson_assist_record_usage():
    day = date.today().isoformat()
    _lesson_assist_increment(day, f"ip:{_lesson_assist_client_ip()}")
    _lesson_assist_increment(day, f"session:{_lesson_assist_session_key()}")


def _lesson_assist_error(status, code, message, retry_after_sec=None):
    payload = {
        'ok': False,
        'error': {
            'code': code,
            'message': message,
        },
    }
    if retry_after_sec is not None:
        payload['error']['retryAfterSec'] = retry_after_sec
    return jsonify(payload), status


@app.route('/api/lesson/explain', methods=['POST'])
def lesson_explain():
    if not lesson_assist_enabled():
        return _lesson_assist_error(
            503,
            'assistant_unavailable',
            'The lesson assistant is not configured on this server.',
        )

    allowed, remaining, limit_code = _lesson_assist_rate_limit()
    if not allowed:
        if limit_code == 'rate_limited':
            return _lesson_assist_error(
                429,
                'rate_limited',
                "You've used today's explanation limit. Try again tomorrow.",
                retry_after_sec=86400,
            )
        return _lesson_assist_error(
            503,
            'assistant_unavailable',
            'The lesson assistant is not available right now.',
        )

    payload = request.get_json(silent=True)
    normalized, validation_error = validate_payload(payload)
    if validation_error:
        return _lesson_assist_error(
            400,
            validation_error['code'],
            validation_error['message'],
        )

    ctx = normalized['context']
    try:
        TOPICS[ctx['level']][ctx['subject']][ctx['topic']]
    except KeyError:
        return _lesson_assist_error(400, 'invalid_context', 'Unknown lesson topic.')

    try:
        result = generate_explanation(normalized)
    except RuntimeError as exc:
        app.logger.warning('Lesson assist provider error: %s', exc)
        return _lesson_assist_error(
            503,
            'assistant_unavailable',
            user_facing_error(exc),
        )
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        app.logger.warning('Lesson assist error: %s', exc)
        return _lesson_assist_error(
            503,
            'assistant_unavailable',
            user_facing_error(exc),
        )

    _lesson_assist_record_usage()
    _, remaining_after, _ = _lesson_assist_rate_limit()

    meta = result.get('meta') or {}
    meta['remainingToday'] = remaining_after

    return jsonify({
        'ok': True,
        'explanation': result['explanation'],
        'meta': meta,
    })


@app.route('/quicktest/start', methods=['POST'])
def quicktest_start():
    level = request.form.get('level', 'gcse')
    subject = request.form.get('subject', 'physics')
    topic = _resolve_topic_slug(level, subject, request.form.get('topic', 'forces'))
    mode = normalize_mode(request.form.get('mode', 'standard'))
    difficulty = request.form.get('difficulty', 'foundational')

    try:
        topic_config = TOPICS[level][subject][topic]
        generator = topic_config['func']
        variants_func = topic_config.get('variants_func')
    except KeyError:
        return 'Invalid topic', 400

    problems = []
    if variants_func:
        variant_list = variants_func(difficulty, mode)
        for variant_fn in variant_list:
            p = generator(difficulty, mode, variant_name=variant_fn.__name__)
            problems.append(p)
    else:
        for _ in range(10):
            p = generator(difficulty, mode, variant_name=None)
            problems.append(p)

    data = {
        'problems': problems,
        'index': 0,
        'topic_name': topic_config.get('name', topic),
        'level': level,
        'subject': subject,
        'topic': topic,
        'difficulty': difficulty,
        'mode': mode,
    }
    _save_qt(data)                       # <-- stores in SQLite, not in session
    return redirect(url_for('quicktest_question'))

@app.route('/quicktest', methods=['GET'])
def quicktest_question():
    data = _load_qt()
    if not data:
        return redirect(url_for('index'))
    idx = data['index']
    if idx >= len(data['problems']):
        return redirect(url_for('quicktest_results'))
    return render_template(
        'quicktest_question.html',
        problem=data['problems'][idx],
        current=idx + 1,
        total=len(data['problems']),
        topic_name=data['topic_name'],
        qt_level=data.get('level', 'gcse'),
        qt_subject=data.get('subject', 'physics'),
        qt_topic=data.get('topic', 'forces'),
        qt_mode=data.get('mode', 'standard'),
        qt_difficulty=data.get('difficulty', 'foundational'),
    )

@app.route('/quicktest/next', methods=['POST'])
def quicktest_next():
    data = _load_qt()
    if not data:
        return redirect(url_for('index'))
    data['index'] += 1
    _save_qt(data)
    if data['index'] >= len(data['problems']):
        return redirect(url_for('quicktest_results'))
    return redirect(url_for('quicktest_question'))

@app.route('/lesson-quiz/<level>/<subject>/<topic>')
def lesson_mcq_quiz(level, subject, topic):
    if not _lesson_quiz_available(level, subject, topic):
        return 'Lesson quiz not available for this topic', 404

    try:
        topic_config = TOPICS[level][subject][topic]
    except KeyError:
        return 'Topic not found', 404

    try:
        problems = build_lesson_mcq_quiz(level, subject, topic, topic_config)
    except ValueError:
        return 'Lesson quiz not available for this topic', 404
    data = {
        'problems': problems,
        'topic_name': topic_config.get('name', topic),
        'level': level,
        'subject': subject,
        'topic': topic,
        'lesson_url': url_for('topic_page', level=level, subject=subject, topic=topic),
        'total': len(problems),
    }
    _save_lq(data)
    return render_template(
        'lesson_mcq_quiz.html',
        problems=problems,
        topic_name=data['topic_name'],
        lesson_url=data['lesson_url'],
        level=level,
        subject=subject,
        topic=topic,
        total=len(problems),
    )


@app.route('/lesson-quiz/<level>/<subject>/<topic>/submit', methods=['POST'])
def lesson_mcq_submit(level, subject, topic):
    if not _lesson_quiz_available(level, subject, topic):
        return 'Lesson quiz not available for this topic', 404

    data = _load_lq()
    if not data or data.get('topic') != topic:
        return redirect(url_for('lesson_mcq_quiz', level=level, subject=subject, topic=topic))

    answers = []
    score = 0
    for i, problem in enumerate(data['problems']):
        letter = (request.form.get(f'answer_{i}', '') or '').strip().upper()[:1]
        answers.append(letter)
        if letter and letter == problem.get('correct_answer'):
            score += 1

    data['answers'] = answers
    data['score'] = score
    _save_lq(data)

    if current_user.is_authenticated:
        with get_db() as conn:
            attempt_id = record_quiz_attempt(
                conn,
                current_user.id,
                level,
                subject,
                topic,
                score,
                data.get('total', len(data['problems'])),
                answers,
                data['problems'],
            )
        _track_quiz_completed(
            level,
            subject,
            topic,
            score,
            data.get('total', len(data['problems'])),
        )
        return redirect(url_for('view_quiz_attempt', attempt_id=attempt_id))

    return redirect(url_for('lesson_mcq_results', level=level, subject=subject, topic=topic))


@app.route('/lesson-quiz/<level>/<subject>/<topic>/results')
def lesson_mcq_results(level, subject, topic):
    if not _lesson_quiz_available(level, subject, topic):
        return 'Lesson quiz not available for this topic', 404

    data = _load_lq()
    if not data or data.get('topic') != topic or 'answers' not in data:
        return redirect(url_for('lesson_mcq_quiz', level=level, subject=subject, topic=topic))

    enriched = []
    for i, problem in enumerate(data['problems']):
        p = dict(problem)
        p['user_answer'] = data['answers'][i] if i < len(data['answers']) else ''
        enriched.append(p)

    return _render_quiz_results(
        enriched,
        data['score'],
        data.get('total', len(enriched)),
        data['topic_name'],
        data['lesson_url'],
        level,
        subject,
        topic,
        show_wrong_explanations_only=False,
    )


@app.route('/quicktest/results', methods=['GET'])
def quicktest_results():
    data = _load_qt()
    if not data:
        return redirect(url_for('index'))
    problems = data['problems']
    total_marks = sum(p['marks'] for p in problems)
    return render_template(
        'quicktest_results.html',
        problems=problems,
        topic_name=data['topic_name'],
        total_marks=total_marks,
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)