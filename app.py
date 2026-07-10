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

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash, g
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
    list_followers,
    list_following,
    quiz_stats_summary,
    record_question_generated,
    record_quiz_completed,
    record_topic_opened,
    unfollow_user,
    update_profile_settings,
)
from models.user_data import (
    clear_lesson_progress,
    delete_saved_problem,
    enrich_quiz_attempt_problems,
    get_lesson_progress,
    get_quiz_attempt,
    get_saved_problem,
    list_lesson_progress,
    list_quiz_attempts,
    list_saved_problems,
    record_quiz_attempt,
    save_problem,
    update_saved_problem,
    upsert_lesson_progress,
)

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
    return {
        'nav_endpoint': request.endpoint,
        'lesson_meta': lesson_meta,
        'lesson_assist_enabled': assist_on,
        'lesson_progress_enabled': lesson_progress_on,
        'csrf_token': _csrf_token,
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
        # Pyodide uses blob: workers internally for async execution.
        "worker-src 'self' blob:; "
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
    conn.commit()

login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access that page.'
login_manager.login_message_category = 'error'


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


def _clear_problem_queue():
    for key in (
        'problem_queue_key',
        'problem_queue',
        'problem_index',
        'problem_variant_name',
    ):
        session.pop(key, None)


def _build_problem_queue(topic_config, level, subject, topic, mode, difficulty):
    variants_builder = topic_config.get('variants_func')
    if not variants_builder:
        return None

    queue = variants_builder(difficulty, normalize_mode(mode))
    if not queue:
        return None

    return [variant.__name__ for variant in queue]


def _get_problem_from_queue(topic_config, level, subject, topic, mode, difficulty, action):
    generator = topic_config['func']
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    current_key = session.get('problem_queue_key')
    queue = session.get('problem_queue')
    idx = session.get('problem_index', -1)

    needs_new_queue = (
        action == 'start' or
        current_key != queue_key or
        not queue
    )

    if needs_new_queue:
        queue = _build_problem_queue(topic_config, level, subject, topic, mode, difficulty)
        if not queue:
            return generator(difficulty, mode)
        idx = 0
    else:
        idx += 1
        if idx >= len(queue):
            queue = _build_problem_queue(topic_config, level, subject, topic, mode, difficulty)
            idx = 0

    variant_name = queue[idx]
    session['problem_queue_key'] = queue_key
    session['problem_queue'] = queue
    session['problem_index'] = idx
    session['problem_variant_name'] = variant_name
    session.modified = True

    return generator(difficulty, mode, variant_name=variant_name)


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


def _reroll_current_problem(topic_config, level, subject, topic, mode, difficulty):
    """Regenerate the current queue variant without advancing the queue index."""
    variant_name = session.get('problem_variant_name')
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    if (
        not variant_name
        or session.get('problem_queue_key') != queue_key
        or not topic_config.get('variants_func')
    ):
        return None

    return _reroll_variant_problem(topic_config, mode, difficulty, variant_name)


def _can_reroll_current_variant(topic_config, level, subject, topic, mode, difficulty):
    variant_name = session.get('problem_variant_name')
    queue_key = _selection_key(level, subject, topic, mode, difficulty)
    if (
        not variant_name
        or session.get('problem_queue_key') != queue_key
        or not topic_config.get('variants_func')
    ):
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


def _topic_label(level, subject, topic):
    try:
        return TOPICS[level][subject][topic].get('name', topic.replace('_', ' ').title())
    except KeyError:
        return topic.replace('_', ' ').title()


def _track_topic_opened(level, subject, topic):
    if not current_user.is_authenticated:
        return
    with get_db() as conn:
        record_topic_opened(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            _topic_label(level, subject, topic),
        )


def _track_question_generated(level, subject, topic, difficulty):
    if not current_user.is_authenticated:
        return
    with get_db() as conn:
        record_question_generated(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            _topic_label(level, subject, topic),
            difficulty,
        )


def _track_quiz_completed(level, subject, topic, score, total):
    if not current_user.is_authenticated:
        return
    with get_db() as conn:
        record_quiz_completed(
            conn,
            current_user.id,
            level,
            subject,
            topic,
            _topic_label(level, subject, topic),
            score,
            total,
        )


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
    }


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


@app.route('/topics')
def topics_index():
    return render_template('topics.html', topic_groups=_build_topic_groups())


@app.route('/about')
def about():
    return render_template('about.html')


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
    return render_template(
        'profile.html',
        saved_problems=saved,
        lesson_progress=progress,
        quiz_attempts=quizzes,
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
            }
            with get_db() as conn:
                update_profile_settings(conn, current_user.id, updated)
                settings = get_profile_settings(conn, current_user.id)
            flash('Privacy settings saved.', 'success')
            return redirect(url_for('profile_settings'))

    return render_template(
        'profile_settings.html',
        settings=settings,
        visibility_choices=VISIBILITY_CHOICES,
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
        follow_user(conn, current_user.id, target.id)

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