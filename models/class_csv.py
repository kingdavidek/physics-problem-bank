"""Teacher CSV downloads (G8 Phase 5). Handles only — never emails or answer keys."""
from __future__ import annotations

import csv
from io import StringIO

from models.class_assignments import list_assignments_for_teacher, list_recipients
from models.class_progress import enrich_roster
from models.classes import list_roster, teacher_owns_class


def _csv_cell(value):
    if value is None:
        return ''
    text = str(value)
    if text[:1] in ('=', '+', '-', '@'):
        return "'" + text
    return text


def _csv_body(header, rows):
    buf = StringIO()
    writer = csv.writer(buf, lineterminator='\n')
    writer.writerow(header)
    for row in rows:
        writer.writerow([_csv_cell(cell) for cell in row])
    return buf.getvalue()


def _safe_filename(class_id, kind):
    return f'class-{int(class_id)}-{kind}.csv'


def roster_csv(conn, teacher_id, class_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    members = enrich_roster(conn, list_roster(conn, teacher_id, class_id))
    rows = [
        (
            member.get('handle'),
            member.get('joined_at'),
            member.get('last_active'),
            int(member.get('quiz_count_7d') or 0),
            member.get('status'),
        )
        for member in members
    ]
    body = _csv_body(
        ('handle', 'joined_at', 'last_active', 'quiz_count_7d', 'status'),
        rows,
    )
    return _safe_filename(class_id, 'roster'), body


def assignments_csv(conn, teacher_id, class_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    summaries = list_assignments_for_teacher(conn, teacher_id, class_id)
    rows = []
    for summary in summaries:
        for rec in list_recipients(conn, summary['id']):
            rows.append((
                summary['id'],
                summary.get('topic'),
                summary.get('level'),
                summary.get('subject'),
                summary.get('created_at'),
                rec.get('handle'),
                rec.get('status'),
                int(rec.get('answered_count') or 0),
                int(rec.get('question_count') or 0),
                int(rec.get('score') or 0),
                rec.get('completed_at'),
            ))
    body = _csv_body(
        (
            'assignment_id',
            'topic',
            'level',
            'subject',
            'created_at',
            'handle',
            'status',
            'answered_count',
            'question_count',
            'score',
            'completed_at',
        ),
        rows,
    )
    return _safe_filename(class_id, 'assignments'), body
