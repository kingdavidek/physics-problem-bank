"""Frozen class set-work (G8 Phase 4). Graded from stored JSON, never client keys."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from models.classes import (
    MEMBER_ACTIVE,
    get_membership,
    list_roster,
    teacher_owns_class,
)
from models.user import utc_now_iso

STATUS_ASSIGNED = 'assigned'
STATUS_COMPLETE = 'complete'

MIN_ASSIGNMENT_QUESTIONS = 1
MAX_ASSIGNMENT_QUESTIONS = 20
MAX_ASSIGNMENTS_PER_CLASS = 40
PREVIEW_TTL_HOURS = 2
MAX_PREVIEWS_PER_TEACHER = 8

_STRIP_KEYS = (
    'correct_answer',
    'correct_answer_raw',
    'solution',
    'solution_html',
    'hint',
    'hint_html',
    'answer_tests',
)


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def _parse_json_list(raw):
    try:
        parsed = json.loads(raw or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return parsed


def _dump_json(value):
    return json.dumps(value, default=str)


def strip_problem_keys(problem, *, reveal=False):
    if not isinstance(problem, dict):
        return {}
    out = dict(problem)
    if reveal:
        return out
    for key in _STRIP_KEYS:
        out.pop(key, None)
    return out


def _letter(value):
    return (value or '').strip().upper()[:1]


def _answers_slots(raw, question_count):
    parsed = _parse_json_list(raw)
    slots = [None] * question_count
    for i in range(question_count):
        if i >= len(parsed) or parsed[i] is None:
            continue
        item = parsed[i]
        if not isinstance(item, dict):
            continue
        slots[i] = {
            'user_answer': item.get('user_answer'),
            'correct': bool(item.get('correct')),
        }
    return slots


def _answered_count(slots):
    return sum(1 for item in slots if item is not None)


def _score_count(slots):
    return sum(1 for item in slots if item and item.get('correct'))


def grade_frozen_answer(problem, user_answer):
    """Grade from the stored problem only. Ignore any client-supplied keys."""
    from generators.shared.answer_checkers import (
        MAX_USER_ANSWER_LEN,
        check_answer,
        check_number_fields,
    )

    if user_answer is None or str(user_answer).strip() == '':
        raise ValueError('missing_answer')
    text = str(user_answer)
    if len(text) > MAX_USER_ANSWER_LEN:
        raise ValueError('answer_too_long')

    options = problem.get('options') or []
    if options:
        letter = _letter(text)
        correct = _letter(problem.get('correct_answer'))
        return letter, bool(letter and correct and letter == correct)

    raw = problem.get('correct_answer_raw')
    if raw is not None:
        answer_type = problem.get('answer_type') or 'number'
        try:
            if answer_type == 'number_fields':
                result = check_number_fields(
                    str(raw),
                    text,
                    field_types=problem.get('answer_field_types'),
                )
            else:
                result = check_answer(answer_type, str(raw), text)
        except (TypeError, ValueError):
            return text.strip(), False
        return text.strip(), bool(result.get('correct'))

    letter = _letter(text)
    correct = _letter(problem.get('correct_answer'))
    if correct:
        return letter, bool(letter and letter == correct)
    raise ValueError('not_gradable')


def _owned_class(conn, teacher_id, class_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    row = conn.execute(
        'SELECT * FROM classes WHERE id = ? AND teacher_id = ?',
        (class_id, teacher_id),
    ).fetchone()
    if not row:
        raise ValueError('not_found')
    return dict(row)


def _require_live_class(conn, teacher_id, class_id):
    klass = _owned_class(conn, teacher_id, class_id)
    if klass.get('archived_at'):
        raise ValueError('class_archived')
    return klass


def resolve_recipients(conn, teacher_id, class_id, *, assign_all, student_ids):
    roster = list_roster(conn, teacher_id, class_id)
    active_ids = [int(row['student_id']) for row in roster]
    if assign_all:
        if not active_ids:
            raise ValueError('no_recipients')
        return active_ids
    wanted = []
    seen = set()
    for raw in student_ids or []:
        try:
            sid = int(raw)
        except (TypeError, ValueError):
            raise ValueError('invalid_student')
        if sid in seen:
            continue
        seen.add(sid)
        wanted.append(sid)
    if not wanted:
        raise ValueError('no_recipients')
    active_set = set(active_ids)
    for sid in wanted:
        if sid not in active_set:
            raise ValueError('not_in_class')
    return wanted


def _preview_cutoff_iso():
    return (
        datetime.now(timezone.utc).replace(microsecond=0)
        - timedelta(hours=PREVIEW_TTL_HOURS)
    ).isoformat()


def prune_previews(conn, teacher_id):
    if not _table_exists(conn, 'class_assignment_previews'):
        return
    conn.execute(
        'DELETE FROM class_assignment_previews WHERE created_at < ?',
        (_preview_cutoff_iso(),),
    )
    rows = conn.execute(
        '''
        SELECT id FROM class_assignment_previews
        WHERE teacher_id = ?
        ORDER BY created_at DESC, id DESC
        ''',
        (teacher_id,),
    ).fetchall()
    extra = [row['id'] for row in rows[MAX_PREVIEWS_PER_TEACHER:]]
    if extra:
        placeholders = ','.join('?' * len(extra))
        conn.execute(
            f'DELETE FROM class_assignment_previews WHERE id IN ({placeholders})',
            extra,
        )


def save_preview(conn, teacher_id, class_id, *, level, subject, topic, mode, difficulty, problems):
    _require_live_class(conn, teacher_id, class_id)
    if not problems:
        raise ValueError('generate_failed')
    prune_previews(conn, teacher_id)
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO class_assignment_previews (
            teacher_id, class_id, level, subject, topic, mode, difficulty,
            problems_json, question_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            teacher_id,
            class_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            _dump_json(problems),
            len(problems),
            now,
        ),
    )
    conn.commit()
    return get_preview(conn, teacher_id, class_id, cursor.lastrowid)


def get_preview(conn, teacher_id, class_id, preview_id):
    if not _table_exists(conn, 'class_assignment_previews'):
        raise ValueError('not_found')
    row = conn.execute(
        '''
        SELECT * FROM class_assignment_previews
        WHERE id = ? AND teacher_id = ? AND class_id = ?
        ''',
        (preview_id, teacher_id, class_id),
    ).fetchone()
    if not row:
        raise ValueError('not_found')
    data = dict(row)
    if (data.get('created_at') or '') < _preview_cutoff_iso():
        raise ValueError('not_found')
    data['problems'] = _parse_json_list(data.pop('problems_json', None))
    return data


def consume_preview(conn, teacher_id, class_id, preview_id):
    preview = get_preview(conn, teacher_id, class_id, preview_id)
    conn.execute(
        'DELETE FROM class_assignment_previews WHERE id = ?',
        (preview_id,),
    )
    return preview


def _assignment_count(conn, class_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM class_assignments WHERE class_id = ?',
        (class_id,),
    ).fetchone()
    return int(row['n'] if row else 0)


def create_assignment(
    conn,
    teacher_id,
    class_id,
    *,
    level,
    subject,
    topic,
    mode,
    difficulty,
    problems,
    student_ids,
):
    _require_live_class(conn, teacher_id, class_id)
    if not problems:
        raise ValueError('generate_failed')
    count = len(problems)
    if count < MIN_ASSIGNMENT_QUESTIONS or count > MAX_ASSIGNMENT_QUESTIONS:
        raise ValueError('invalid_count')
    if _assignment_count(conn, class_id) >= MAX_ASSIGNMENTS_PER_CLASS:
        raise ValueError('assignment_limit')
    if not student_ids:
        raise ValueError('no_recipients')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO class_assignments (
            class_id, teacher_id, level, subject, topic, mode, difficulty,
            problems_json, question_count, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            class_id,
            teacher_id,
            level,
            subject,
            topic,
            mode,
            difficulty,
            _dump_json(problems),
            count,
            now,
        ),
    )
    assignment_id = cursor.lastrowid
    empty_answers = _dump_json([None] * count)
    for student_id in student_ids:
        conn.execute(
            '''
            INSERT INTO class_assignment_recipients (
                assignment_id, student_id, status, answers_json, score, completed_at
            ) VALUES (?, ?, ?, ?, NULL, NULL)
            ''',
            (assignment_id, student_id, STATUS_ASSIGNED, empty_answers),
        )
    conn.commit()
    from models.class_audit import log_class_event

    log_class_event(
        conn,
        class_id,
        teacher_id,
        'assignment_created',
        meta={
            'assignment_id': assignment_id,
            'topic': topic,
            'question_count': count,
            'recipient_count': len(student_ids),
        },
    )
    return get_assignment_for_teacher(conn, teacher_id, class_id, assignment_id)


def _load_assignment_row(conn, assignment_id):
    row = conn.execute(
        'SELECT * FROM class_assignments WHERE id = ?',
        (assignment_id,),
    ).fetchone()
    if not row:
        return None
    data = dict(row)
    data['problems'] = _parse_json_list(data.pop('problems_json', None))
    return data


def list_assignments_for_teacher(conn, teacher_id, class_id):
    _owned_class(conn, teacher_id, class_id)
    rows = conn.execute(
        '''
        SELECT a.id, a.class_id, a.teacher_id, a.level, a.subject, a.topic,
               a.mode, a.difficulty, a.question_count, a.created_at,
               COUNT(r.student_id) AS recipient_count,
               SUM(CASE WHEN r.status = ? THEN 1 ELSE 0 END) AS complete_count
        FROM class_assignments a
        LEFT JOIN class_assignment_recipients r ON r.assignment_id = a.id
        WHERE a.class_id = ? AND a.teacher_id = ?
        GROUP BY a.id
        ORDER BY a.created_at DESC, a.id DESC
        ''',
        (STATUS_COMPLETE, class_id, teacher_id),
    ).fetchall()
    return [dict(row) for row in rows]


def list_recipients(conn, assignment_id):
    rows = conn.execute(
        '''
        SELECT r.assignment_id, r.student_id, r.status, r.answers_json,
               r.score, r.completed_at, u.handle,
               a.question_count
        FROM class_assignment_recipients r
        JOIN users u ON u.id = r.student_id
        JOIN class_assignments a ON a.id = r.assignment_id
        WHERE r.assignment_id = ?
        ORDER BY u.handle COLLATE NOCASE ASC
        ''',
        (assignment_id,),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        slots = _answers_slots(item.pop('answers_json', None), item['question_count'])
        item['answered_count'] = _answered_count(slots)
        item['score'] = _score_count(slots)
        out.append(item)
    return out


def get_assignment_for_teacher(conn, teacher_id, class_id, assignment_id):
    _owned_class(conn, teacher_id, class_id)
    data = _load_assignment_row(conn, assignment_id)
    if not data or int(data['class_id']) != int(class_id) or int(data['teacher_id']) != int(teacher_id):
        raise ValueError('not_found')
    data['recipients'] = list_recipients(conn, assignment_id)
    return data


def serialize_recipient(row):
    if not row:
        return None
    return {
        'student_id': row['student_id'],
        'handle': row.get('handle'),
        'status': row['status'],
        'answered_count': int(row.get('answered_count') or 0),
        'question_count': int(row.get('question_count') or 0),
        'score': int(row.get('score') or 0),
        'completed_at': row.get('completed_at'),
    }


def serialize_assignment_summary(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'class_id': row['class_id'],
        'level': row['level'],
        'subject': row['subject'],
        'topic': row['topic'],
        'mode': row['mode'],
        'difficulty': row['difficulty'],
        'question_count': int(row['question_count']),
        'created_at': row.get('created_at'),
        'recipient_count': int(row.get('recipient_count') or 0),
        'complete_count': int(row.get('complete_count') or 0),
        'can_reroll': False,
    }


def serialize_preview(preview):
    problems = [strip_problem_keys(item, reveal=False) for item in preview.get('problems') or []]
    return {
        'preview_id': preview['id'],
        'class_id': preview['class_id'],
        'level': preview['level'],
        'subject': preview['subject'],
        'topic': preview['topic'],
        'mode': preview['mode'],
        'difficulty': preview['difficulty'],
        'question_count': int(preview['question_count']),
        'created_at': preview.get('created_at'),
        'problems': problems,
        'can_reroll': False,
    }


def serialize_teacher_assignment(data, *, include_problems=True):
    payload = {
        'id': data['id'],
        'class_id': data['class_id'],
        'level': data['level'],
        'subject': data['subject'],
        'topic': data['topic'],
        'mode': data['mode'],
        'difficulty': data['difficulty'],
        'question_count': int(data['question_count']),
        'created_at': data.get('created_at'),
        'can_reroll': False,
        'recipients': [serialize_recipient(row) for row in data.get('recipients') or []],
    }
    if include_problems:
        payload['problems'] = [
            strip_problem_keys(item, reveal=False) for item in data.get('problems') or []
        ]
    return payload


def class_set_work_summary(conn, class_id):
    if not _table_exists(conn, 'class_assignment_recipients'):
        return {'available': False}
    row = conn.execute(
        '''
        SELECT COUNT(*) AS assigned,
               SUM(CASE WHEN r.status = ? THEN 1 ELSE 0 END) AS complete
        FROM class_assignment_recipients r
        JOIN class_assignments a ON a.id = r.assignment_id
        WHERE a.class_id = ?
        ''',
        (STATUS_COMPLETE, class_id),
    ).fetchone()
    assigned = int(row['assigned'] or 0) if row else 0
    complete = int(row['complete'] or 0) if row else 0
    return {
        'available': assigned > 0,
        'assigned': assigned,
        'complete': complete,
    }


def student_set_work_for_class(conn, class_id, student_id):
    if not _table_exists(conn, 'class_assignment_recipients'):
        return []
    rows = conn.execute(
        '''
        SELECT a.id, a.topic, a.level, a.subject, a.question_count,
               a.created_at, r.status, r.answers_json, r.score, r.completed_at
        FROM class_assignment_recipients r
        JOIN class_assignments a ON a.id = r.assignment_id
        WHERE a.class_id = ? AND r.student_id = ?
        ORDER BY a.created_at DESC, a.id DESC
        ''',
        (class_id, student_id),
    ).fetchall()
    out = []
    for row in rows:
        slots = _answers_slots(row['answers_json'], row['question_count'])
        out.append({
            'assignment_id': row['id'],
            'topic': row['topic'],
            'level': row['level'],
            'subject': row['subject'],
            'question_count': int(row['question_count']),
            'answered_count': _answered_count(slots),
            'score': _score_count(slots),
            'status': row['status'],
            'created_at': row['created_at'],
            'completed_at': row['completed_at'],
        })
    return out


def list_class_work_for_student(conn, student_id):
    if not _table_exists(conn, 'class_assignment_recipients'):
        return []
    rows = conn.execute(
        '''
        SELECT a.id, a.class_id, a.level, a.subject, a.topic, a.mode, a.difficulty,
               a.question_count, a.created_at, c.name AS class_name,
               r.status, r.answers_json, r.score, r.completed_at
        FROM class_assignment_recipients r
        JOIN class_assignments a ON a.id = r.assignment_id
        JOIN classes c ON c.id = a.class_id
        JOIN class_memberships m
          ON m.class_id = a.class_id AND m.student_id = r.student_id
        WHERE r.student_id = ? AND m.status = ?
        ORDER BY a.created_at DESC, a.id DESC
        ''',
        (student_id, MEMBER_ACTIVE),
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        slots = _answers_slots(item.pop('answers_json', None), item['question_count'])
        item['answered_count'] = _answered_count(slots)
        item['score'] = _score_count(slots)
        out.append(item)
    return out


def get_class_work_for_student(conn, student_id, assignment_id):
    row = conn.execute(
        '''
        SELECT a.*, c.name AS class_name,
               r.status AS recipient_status, r.answers_json, r.score AS recipient_score,
               r.completed_at
        FROM class_assignment_recipients r
        JOIN class_assignments a ON a.id = r.assignment_id
        JOIN classes c ON c.id = a.class_id
        WHERE r.assignment_id = ? AND r.student_id = ?
        ''',
        (assignment_id, student_id),
    ).fetchone()
    if not row:
        raise ValueError('not_found')
    data = dict(row)
    membership = get_membership(conn, data['class_id'], student_id)
    if not membership or membership.get('status') != MEMBER_ACTIVE:
        raise ValueError('not_found')
    data['problems'] = _parse_json_list(data.pop('problems_json', None))
    slots = _answers_slots(data.pop('answers_json', None), data['question_count'])
    data['answers'] = slots
    data['answered_count'] = _answered_count(slots)
    data['score'] = _score_count(slots)
    data['status'] = data.pop('recipient_status')
    data.pop('recipient_score', None)
    return data


def serialize_student_work_list_item(row):
    return {
        'assignment_id': row['id'],
        'class_id': row['class_id'],
        'class_name': row.get('class_name'),
        'level': row['level'],
        'subject': row['subject'],
        'topic': row['topic'],
        'mode': row['mode'],
        'difficulty': row['difficulty'],
        'question_count': int(row['question_count']),
        'answered_count': int(row.get('answered_count') or 0),
        'score': int(row.get('score') or 0),
        'status': row['status'],
        'created_at': row.get('created_at'),
        'completed_at': row.get('completed_at'),
        'can_reroll': False,
        'can_leave': False,
    }


def serialize_student_work(data):
    problems_out = []
    answers = data.get('answers') or []
    for i, problem in enumerate(data.get('problems') or []):
        answered = i < len(answers) and answers[i] is not None
        payload = strip_problem_keys(problem, reveal=answered)
        payload['index'] = i
        payload['answered'] = answered
        if answered:
            payload['user_answer'] = answers[i].get('user_answer')
            payload['correct'] = bool(answers[i].get('correct'))
        problems_out.append(payload)
    return {
        'assignment_id': data['id'],
        'class_id': data['class_id'],
        'class_name': data.get('class_name'),
        'level': data['level'],
        'subject': data['subject'],
        'topic': data['topic'],
        'mode': data['mode'],
        'difficulty': data['difficulty'],
        'question_count': int(data['question_count']),
        'answered_count': int(data.get('answered_count') or 0),
        'score': int(data.get('score') or 0),
        'status': data['status'],
        'created_at': data.get('created_at'),
        'completed_at': data.get('completed_at'),
        'can_reroll': False,
        'can_leave': False,
        'problems': problems_out,
    }


def submit_student_answer(conn, student_id, assignment_id, index, user_answer):
    data = get_class_work_for_student(conn, student_id, assignment_id)
    membership = get_membership(conn, data['class_id'], student_id)
    if not membership or membership.get('status') != MEMBER_ACTIVE:
        raise ValueError('not_found')
    if data['status'] == STATUS_COMPLETE:
        raise ValueError('already_complete')
    try:
        index = int(index)
    except (TypeError, ValueError):
        raise ValueError('invalid_index')
    problems = data.get('problems') or []
    if index < 0 or index >= len(problems):
        raise ValueError('invalid_index')
    answers = list(data.get('answers') or [None] * len(problems))
    while len(answers) < len(problems):
        answers.append(None)
    if answers[index] is not None:
        raise ValueError('already_answered')
    stored_answer, correct = grade_frozen_answer(problems[index], user_answer)
    answers[index] = {'user_answer': stored_answer, 'correct': correct}
    answered = _answered_count(answers)
    score = _score_count(answers)
    complete = answered >= len(problems)
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE class_assignment_recipients
        SET answers_json = ?, score = ?, status = ?, completed_at = ?
        WHERE assignment_id = ? AND student_id = ?
        ''',
        (
            _dump_json(answers),
            score,
            STATUS_COMPLETE if complete else STATUS_ASSIGNED,
            now if complete else None,
            assignment_id,
            student_id,
        ),
    )
    conn.commit()
    return get_class_work_for_student(conn, student_id, assignment_id)
