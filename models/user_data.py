import json

from models.user import utc_now_iso

MAX_SAVED_PROBLEMS = 200


def save_problem(conn, user_id, level, subject, topic, mode, difficulty, problem):
    count = conn.execute(
        'SELECT COUNT(*) AS n FROM saved_problems WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if count >= MAX_SAVED_PROBLEMS:
        raise ValueError('saved_limit')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO saved_problems (
            user_id, level, subject, topic, mode, difficulty, problem_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            json.dumps(problem),
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def list_saved_problems(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT id, level, subject, topic, mode, difficulty, problem_json, created_at
        FROM saved_problems
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [_saved_row(row) for row in rows]


def get_saved_problem(conn, user_id, saved_id):
    row = conn.execute(
        '''
        SELECT id, level, subject, topic, mode, difficulty, problem_json, created_at
        FROM saved_problems
        WHERE user_id = ? AND id = ?
        ''',
        (user_id, saved_id),
    ).fetchone()
    return _saved_row(row) if row else None


def delete_saved_problem(conn, user_id, saved_id):
    cursor = conn.execute(
        'DELETE FROM saved_problems WHERE user_id = ? AND id = ?',
        (user_id, saved_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def update_saved_problem(conn, user_id, saved_id, problem):
    cursor = conn.execute(
        '''
        UPDATE saved_problems
        SET problem_json = ?
        WHERE user_id = ? AND id = ?
        ''',
        (json.dumps(problem), user_id, saved_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def upsert_lesson_progress(
    conn,
    user_id,
    level,
    subject,
    topic,
    section_key,
    section_label,
    completed_keys=None,
):
    now = utc_now_iso()
    existing = get_lesson_progress(conn, user_id, level, subject, topic)
    merged = set(existing.get('completed_keys') or []) if existing else set()
    if completed_keys:
        merged.update(completed_keys)
    if section_key:
        merged.add(section_key)
    completed_list = sorted(
        merged,
        key=lambda key: int(key.rsplit('-', 1)[-1]) if key.rsplit('-', 1)[-1].isdigit() else 0,
    )
    completed_json = json.dumps(completed_list)
    conn.execute(
        '''
        INSERT INTO lesson_progress (
            user_id, level, subject, topic, section_key, section_label,
            completed_keys_json, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, level, subject, topic) DO UPDATE SET
            section_key = excluded.section_key,
            section_label = excluded.section_label,
            completed_keys_json = excluded.completed_keys_json,
            updated_at = excluded.updated_at
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            section_key or '',
            section_label or '',
            completed_json,
            now,
        ),
    )
    conn.commit()


def get_lesson_progress(conn, user_id, level, subject, topic):
    row = conn.execute(
        '''
        SELECT section_key, section_label, completed_keys_json, updated_at
        FROM lesson_progress
        WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
        ''',
        (user_id, level, subject, topic),
    ).fetchone()
    if not row:
        return None
    data = dict(row)
    raw_keys = data.pop('completed_keys_json', None) or '[]'
    try:
        keys = json.loads(raw_keys)
    except (TypeError, ValueError, json.JSONDecodeError):
        keys = []
    if not isinstance(keys, list):
        keys = []
    data['completed_keys'] = [k for k in keys if isinstance(k, str) and k.strip()]
    if not data['completed_keys'] and data.get('section_key'):
        legacy = data['section_key']
        if legacy.startswith('section-'):
            legacy = 'step-' + legacy[len('section-'):]
        data['completed_keys'] = [legacy]
    return data


def list_lesson_progress(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT level, subject, topic, section_key, section_label, updated_at
        FROM lesson_progress
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def clear_lesson_progress(conn, user_id, level, subject, topic):
    cursor = conn.execute(
        '''
        DELETE FROM lesson_progress
        WHERE user_id = ? AND level = ? AND subject = ? AND topic = ?
        ''',
        (user_id, level, subject, topic),
    )
    conn.commit()
    return cursor.rowcount > 0


def record_quiz_attempt(conn, user_id, level, subject, topic, score, total, answers, problems):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO quiz_attempts (
            user_id, level, subject, topic, score, total, answers_json, problems_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            score,
            total,
            json.dumps(answers),
            json.dumps(problems),
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_quiz_attempt(conn, user_id, attempt_id):
    row = conn.execute(
        '''
        SELECT id, level, subject, topic, score, total, answers_json, problems_json, created_at
        FROM quiz_attempts
        WHERE user_id = ? AND id = ?
        ''',
        (user_id, attempt_id),
    ).fetchone()
    if not row:
        return None
    data = dict(row)
    data['answers'] = json.loads(data['answers_json'])
    if data.get('problems_json'):
        data['problems'] = json.loads(data['problems_json'])
    else:
        data['problems'] = None
    return data


def enrich_quiz_attempt_problems(problems, answers):
    enriched = []
    for i, problem in enumerate(problems):
        item = dict(problem)
        item['user_answer'] = answers[i] if i < len(answers) else ''
        enriched.append(item)
    return enriched


def list_quiz_attempts(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT id, level, subject, topic, score, total, created_at,
               CASE WHEN problems_json IS NOT NULL AND problems_json != '' THEN 1 ELSE 0 END AS has_review
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def _saved_row(row):
    if row is None:
        return None
    data = dict(row)
    data['problem'] = json.loads(data.pop('problem_json'))
    return data
