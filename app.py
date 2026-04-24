import os
from flask import Flask, render_template, request, session, redirect, url_for
from jinja2.exceptions import TemplateNotFound
import sqlite3
import json
import uuid
from topics_data import TOPIC_CONTENT
from topic_registry import TOPICS
from generators.alevel.physics import (aqa_mag_motor_effect,aqa_mag_particle_path,aqa_mag_flux_linkage,aqa_mag_faradays_law,aqa_mag_transformers,)
from generators.alevel.physics import (aqa_pe_basic,aqa_pe_threshold_frequency,aqa_pe_photoelectric_equation,aqa_pe_stopping_potential,aqa_pe_debroglie,)

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

@app.after_request
def apply_csp(response):
    # Allow scripts from the MathJax CDN and enable 'unsafe-eval' for them
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'"
    )
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
    conn.commit()

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

    queue = variants_builder(difficulty, mode)
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

## ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'anon_count' not in session:
        session['anon_count'] = 0

    problem = None
    error = None
    limit_hit = False
    ANON_DAILY_LIMIT = 999

    selected_level = request.form.get('level', 'gcse') if request.method == 'POST' else 'gcse'
    selected_subject = request.form.get('subject', 'physics') if request.method == 'POST' else 'physics'
    selected_topic = request.form.get('topic', 'forces') if request.method == 'POST' else 'forces'
    selected_mode = request.form.get('mode', 'revision') if request.method == 'POST' else 'revision'
    selected_diff = request.form.get('difficulty', 'foundational') if request.method == 'POST' else 'foundational'
    action = request.form.get('action', 'start') if request.method == 'POST' else 'start'


    if request.method == 'POST':
        if session['anon_count'] >= ANON_DAILY_LIMIT:
            limit_hit = True
        else:
            try:
                topic_config = TOPICS[selected_level][selected_subject][selected_topic]
                generator = topic_config['func']

                if action == 'next' and topic_config.get('variants_func'):
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

                session['anon_count'] += 1
                session.modified = True
            except KeyError:
                _clear_problem_queue()
                error = 'Invalid combination. Please try again.'

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
    )



@app.route("/topic/<level>/<subject>/<topic>")
def topic_page(level, subject, topic):
    try:
        topic_data = TOPICS[level][subject][topic]
    except KeyError:
        return "Topic not found", 404

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
        return render_template("topic.html", content=content)



@app.route('/topics')
def topics_index():
    return render_template('topics.html')


@app.route('/quicktest/start', methods=['POST'])
def quicktest_start():
    level = request.form.get('level', 'gcse')
    subject = request.form.get('subject', 'physics')
    topic = request.form.get('topic', 'forces')
    mode = request.form.get('mode', 'revision')
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