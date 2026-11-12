import json
import re
from datetime import date, timedelta

from models.user import utc_now_iso
from generators.shared.answer_record import public_problem, public_problems
from models.lesson_steps import lesson_step_total

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
            json.dumps(public_problem(problem)),
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
        (json.dumps(public_problem(problem)), user_id, saved_id),
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
    step_total=None,
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
    existing_total = int((existing or {}).get('step_total') or 0)
    if step_total is None:
        stored_total = existing_total
    else:
        stored_total = max(existing_total, int(step_total))
    canonical = lesson_step_total(level, subject, topic)
    if canonical > 0:
        # 2026-11-08 (E10 review fix 5): the server's own count wins; a larger client-sent total is never stored
        stored_total = canonical
    conn.execute(
        '''
        INSERT INTO lesson_progress (
            user_id, level, subject, topic, section_key, section_label,
            completed_keys_json, step_total, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, level, subject, topic) DO UPDATE SET
            section_key = excluded.section_key,
            section_label = excluded.section_label,
            completed_keys_json = excluded.completed_keys_json,
            step_total = excluded.step_total,
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
            stored_total,
            now,
        ),
    )
    conn.commit()


_STEP_KEY_RE = re.compile(r'^step-(\d+)$')


def valid_lesson_step_keys(level, subject, topic, keys, fallback_total=0):
    """The keys that name a real step of the lesson. 2026-11-08 (E10 review fix 5): only `step-N` with N below the lesson's own
    step total (the server's count of its Quick Checks) is real. A lesson with no known count falls back to the stored total
    (at most 80); with no total at all nothing is real, so a client cannot invent steps."""
    limit = lesson_step_total(level, subject, topic)
    if limit <= 0:
        limit = max(0, int(fallback_total or 0))
    found = []
    for key in keys or []:
        match = _STEP_KEY_RE.match(key) if isinstance(key, str) else None
        if match and int(match.group(1)) < limit and key not in found:
            found.append(key)
    return found


def award_new_lesson_steps(conn, user_id, level, subject, topic, completed_keys, fallback_total=0):
    """Remember which steps of a lesson have earned effort points, and return how many are newly earned by this save.
    A step earns points once, ever: clearing the bookmark and redoing the lesson earns nothing (the ledger is not cleared with
    the progress), and a key that is not a real step of the lesson never counts."""
    now = utc_now_iso()
    new = 0
    for key in valid_lesson_step_keys(level, subject, topic, completed_keys, fallback_total):
        cursor = conn.execute(
            '''
            INSERT OR IGNORE INTO lesson_step_awards (user_id, level, subject, topic, step_key, awarded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (user_id, level, subject, topic, key, now),
        )
        new += cursor.rowcount
    conn.commit()
    return new


def get_lesson_progress(conn, user_id, level, subject, topic):
    row = conn.execute(
        '''
        SELECT section_key, section_label, completed_keys_json, updated_at, step_total
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
    data['step_total'] = int(data.get('step_total') or 0)
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


def record_quiz_attempt(conn, user_id, level, subject, topic, score, total, answers, problems, is_retry=False, is_quicktest=False):
    # 2026-11-08 (E10 phase 6): is_retry marks a Retry wrong ones run (a small attempt made of questions the pupil missed). Every
    # statistic about how well a pupil did (personal best, accuracy trend, topic status, weak topics, accuracy boards, class averages)
    # counts full quizzes only (is_retry = 0); the history list and activity counts still show the retry.
    # 2026-11-11 (E11 Phase 4): is_quicktest marks a Quick Test (its score is marks); the Full marks line counts lesson quizzes only.
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO quiz_attempts (
            user_id, level, subject, topic, score, total, answers_json, problems_json, created_at, is_retry, is_quicktest
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            level,
            subject,
            topic,
            score,
            total,
            json.dumps(answers),
            json.dumps(public_problems(problems)),
            now,
            1 if is_retry else 0,
            1 if is_quicktest else 0,
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
    """The stored problems with each pupil answer and whether it was right.

    A Quick Test row stores ``{'user_answer', 'correct', ...}``; a lesson quiz row stores the answer alone, so it is
    graded again here, exactly as the quiz graded it (``grade_lesson_quiz_problem``). Without this the review page had
    no verdict for a lesson quiz and showed every question as wrong (2026-11-07).
    """
    from generators.shared.lesson_quiz import grade_lesson_quiz_problem

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
            try:
                item['answered_correctly'] = bool(ans) and grade_lesson_quiz_problem(problem, ans)['correct']
            except Exception:  # noqa: BLE001 - an old row the grader cannot read keeps the letter comparison
                item['answered_correctly'] = None
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
    score=None,
    score_total=None,
):
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO generator_mcq_attempts (
            user_id, level, subject, topic, mode, difficulty,
            user_answer, correct_answer, correct, created_at,
            attempt_group_id, part_index, part_total, score, score_total
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            score,
            score_total,
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
               attempt_group_id, part_index, part_total, score, score_total
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
               attempt_group_id, part_index, part_total, score, score_total
        FROM generator_mcq_attempts
        WHERE user_id = ? AND id = ?
        ''',
        (user_id, attempt_id),
    ).fetchone()
    return dict(row) if row else None


def _mcq_attempt_display_row(item):
    """Normalize a single practice attempt row for profile/history UI."""
    row = {**item, 'is_multipart': False}
    score_total = item.get('score_total')
    if score_total is not None and int(score_total) > 0:
        row['score'] = int(item.get('score') or 0)
        row['total'] = int(score_total)
    return row


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
            ungrouped.append(_mcq_attempt_display_row(item))

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
                ungrouped.append(_mcq_attempt_display_row(row))
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
    from datetime import datetime, timezone, timedelta

    rows = conn.execute(
        '''
        SELECT DISTINCT substr(created_at, 1, 10) AS day
        FROM generator_mcq_attempts
        WHERE user_id = ?
        ORDER BY day DESC
        LIMIT 400
        ''',
        (user_id,),
    ).fetchall()
    if not rows:
        return 0
    days = {row['day'] for row in rows}
    today = datetime.now(timezone.utc).date()
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
