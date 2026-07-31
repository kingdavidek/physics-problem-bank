"""Wrong-answer reflection storage (Phase G4).

Optional student notes after a wrong Check or MCQ answer. Reflections can
link to a generator_mcq_attempts row when the client received attempt_id
from the check / mcq-answer APIs.
"""
from models.user import utc_now_iso

DEFAULT_LIMIT = 20
MAX_LIMIT = 100
MAX_REFLECTION_TEXT = 500

PROMPT_TYPES = frozenset({
    'calculation_error',
    'misread_question',
    'forgot_formula',
    'guessed',
    'other',
})

SOURCES = frozenset({'check', 'mcq'})


def _normalize_prompt_type(value):
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text not in PROMPT_TYPES:
        return None
    return text


def _reflection_row(row):
    item = dict(row)
    item['attempt_id'] = item.get('attempt_id')
    return item


def save_reflection(
    conn,
    user_id,
    level,
    subject,
    topic,
    *,
    source,
    difficulty='foundational',
    prompt_type=None,
    reflection_text='',
    attempt_id=None,
):
    """Persist one wrong-answer reflection. Returns the new row id."""
    level = (level or '').strip()
    subject = (subject or '').strip()
    topic = (topic or '').strip()
    source = (source or '').strip().lower()
    difficulty = (difficulty or 'foundational').strip() or 'foundational'
    prompt_type = _normalize_prompt_type(prompt_type)
    text = (reflection_text or '').strip()
    if len(text) > MAX_REFLECTION_TEXT:
        raise ValueError('reflection_too_long')
    if source not in SOURCES:
        raise ValueError('invalid_source')
    if not (level and subject and topic):
        raise ValueError('missing_topic')
    if not prompt_type and not text:
        raise ValueError('empty_reflection')

    if attempt_id is not None:
        attempt_id = int(attempt_id)
        row = conn.execute(
            '''
            SELECT id FROM generator_mcq_attempts
            WHERE id = ? AND user_id = ?
            ''',
            (attempt_id, user_id),
        ).fetchone()
        if not row:
            raise ValueError('invalid_attempt_id')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO user_wrong_answer_reflections (
            user_id, level, subject, topic, difficulty, source,
            attempt_id, prompt_type, reflection_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            difficulty,
            source,
            attempt_id,
            prompt_type,
            text,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_reflection(conn, user_id, reflection_id):
    row = conn.execute(
        '''
        SELECT id, user_id, level, subject, topic, difficulty, source,
               attempt_id, prompt_type, reflection_text, created_at
        FROM user_wrong_answer_reflections
        WHERE id = ? AND user_id = ?
        ''',
        (reflection_id, user_id),
    ).fetchone()
    if not row:
        return None
    return _reflection_row(row)


def list_reflections(conn, user_id, *, limit=DEFAULT_LIMIT, before_id=None, topic=None):
    params = [user_id]
    clauses = ['user_id = ?']
    if before_id is not None:
        clauses.append('id < ?')
        params.append(int(before_id))
    if topic:
        clauses.append('topic = ?')
        params.append(topic.strip())
    params.append(min(max(int(limit), 1), MAX_LIMIT))
    rows = conn.execute(
        f'''
        SELECT id, user_id, level, subject, topic, difficulty, source,
               attempt_id, prompt_type, reflection_text, created_at
        FROM user_wrong_answer_reflections
        WHERE {' AND '.join(clauses)}
        ORDER BY id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    return [_reflection_row(row) for row in rows]
