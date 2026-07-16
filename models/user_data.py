import json
from datetime import date, timedelta

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
        ans = answers[i] if i < len(answers) else ''
        if isinstance(ans, dict):
            item['user_answer'] = ans.get('user_answer')
            item['answered_correctly'] = ans.get('correct')
            item['was_checked'] = ans.get('checked')
        else:
            item['user_answer'] = ans
        enriched.append(item)
    return enriched


def list_quiz_attempts(conn, user_id, limit=20, before_id=None):
    params = [user_id]
    before_clause = ''
    if before_id is not None:
        before_clause = 'AND id < ?'
        params.append(int(before_id))
    params.append(limit)
    rows = conn.execute(
        f'''
        SELECT id, level, subject, topic, score, total, created_at,
               CASE WHEN problems_json IS NOT NULL AND problems_json != '' THEN 1 ELSE 0 END AS has_review
        FROM quiz_attempts
        WHERE user_id = ?
        {before_clause}
        ORDER BY id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    return [dict(row) for row in rows]


def record_generator_mcq_attempt(
    conn,
    user_id,
    level,
    subject,
    topic,
    mode,
    difficulty,
    user_answer,
    correct_answer,
    correct,
    *,
    attempt_group_id=None,
    part_index=None,
    part_total=None,
):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO generator_mcq_attempts (
            user_id, level, subject, topic, mode, difficulty,
            user_answer, correct_answer, correct, created_at,
            attempt_group_id, part_index, part_total
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            user_answer,
            correct_answer,
            1 if correct else 0,
            now,
            attempt_group_id,
            part_index,
            part_total,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def list_generator_mcq_attempts(conn, user_id, limit=10, before_id=None):
    params = [user_id]
    before_clause = ''
    if before_id is not None:
        before_clause = 'AND id < ?'
        params.append(int(before_id))
    params.append(limit)
    rows = conn.execute(
        f'''
        SELECT id, level, subject, topic, mode, difficulty,
               user_answer, correct_answer, correct, created_at,
               attempt_group_id, part_index, part_total
        FROM generator_mcq_attempts
        WHERE user_id = ?
        {before_clause}
        ORDER BY id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    return [dict(row) for row in rows]


def get_generator_mcq_attempt(conn, user_id, attempt_id):
    row = conn.execute(
        '''
        SELECT id, level, subject, topic, mode, difficulty,
               user_answer, correct_answer, correct, created_at,
               attempt_group_id, part_index, part_total
        FROM generator_mcq_attempts
        WHERE user_id = ? AND id = ?
        ''',
        (user_id, attempt_id),
    ).fetchone()
    return dict(row) if row else None


def group_mcq_attempts_for_display(attempts):
    """Collapse multipart practice rows that share an attempt_group_id."""
    if not attempts:
        return []

    by_group = {}
    ungrouped = []
    for item in attempts:
        gid = item.get('attempt_group_id')
        if gid:
            by_group.setdefault(gid, []).append(item)
        else:
            ungrouped.append({**item, 'is_multipart': False})

    grouped = []
    for rows in by_group.values():
        latest_by_part = {}
        part_total = None
        for row in rows:
            if row.get('part_total') is not None:
                part_total = row['part_total']
            part_index = row.get('part_index')
            if part_index is None:
                continue
            previous = latest_by_part.get(part_index)
            if previous is None or row['id'] > previous['id']:
                latest_by_part[part_index] = row

        if not latest_by_part:
            for row in rows:
                ungrouped.append({**row, 'is_multipart': False})
            continue

        total = part_total if part_total is not None else len(latest_by_part)
        score = sum(1 for row in latest_by_part.values() if row.get('correct'))
        base = max(rows, key=lambda row: row['id'])
        grouped.append({
            **base,
            'is_multipart': True,
            'score': score,
            'total': total,
            'correct': score == total,
            'created_at': max(row['created_at'] for row in rows),
        })

    combined = grouped + ungrouped
    combined.sort(key=lambda row: (row.get('created_at') or '', row.get('id') or 0), reverse=True)
    return combined


def list_generator_mcq_attempts_for_display(
    conn, user_id, limit=10, before_id=None, *, raw_limit=200
):
    """Fetch raw attempts and return grouped rows for profile/history UI."""
    raw_limit = max(int(limit), min(int(raw_limit), 500))
    attempts = list_generator_mcq_attempts(
        conn, user_id, limit=raw_limit, before_id=before_id
    )
    return group_mcq_attempts_for_display(attempts)[:limit]


def get_practice_streak(conn, user_id):
    rows = conn.execute(
        '''
        SELECT DISTINCT substr(created_at, 1, 10) AS day
        FROM generator_mcq_attempts
        WHERE user_id = ?
        ORDER BY day DESC
        ''',
        (user_id,),
    ).fetchall()
    if not rows:
        return 0
    days = {row['day'] for row in rows}
    today = date.today()
    yesterday = today - timedelta(days=1)
    if today.isoformat() in days:
        anchor = today
    elif yesterday.isoformat() in days:
        anchor = yesterday
    else:
        return 0
    streak = 0
    expected = anchor
    while expected.isoformat() in days:
        streak += 1
        expected -= timedelta(days=1)
    return streak


def _saved_row(row):
    if row is None:
        return None
    data = dict(row)
    data['problem'] = json.loads(data.pop('problem_json'))
    return data
