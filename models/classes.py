"""Teacher profiles and classes (G8 Phase 1–5). Frozen set-work lives in class_assignments."""
from __future__ import annotations

import re
import sqlite3
import secrets

from models.moderation import is_blocked
from models.user import utc_now_iso
from topic_registry import TOPICS

CLASS_ACTIVE_MEMBER_CAP = 40
MAX_CLASSES_PER_TEACHER = 40
CLASS_NAME_MAX = 80
JOIN_CODE_LEN = 8
MEMBER_ACTIVE = 'active'
MEMBER_REMOVED = 'removed'
JOIN_DISCLOSURE = (
    'If you join, this teacher can see your class and named study progress, '
    'including skill-gap labels, and can set questions for you. '
    'Private reflection notes stay yours. Only the teacher can take you off the class — '
    'there is no Leave button. If you want to leave, ask the teacher.'
)
# Easy to read/type: no 0/O/1/I/L.
_JOIN_ALPHABET = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'
_JOIN_TRIES = 12


def teacher_is_enabled(conn, user_id):
    row = conn.execute(
        'SELECT 1 FROM teacher_profiles WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    return bool(row)


def get_teacher_profile(conn, user_id):
    row = conn.execute(
        'SELECT user_id, enabled_at FROM teacher_profiles WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    return dict(row) if row else None


def enable_teacher(conn, user_id):
    """Idempotent soft enable. One login; the student app stays."""
    existing = get_teacher_profile(conn, user_id)
    if existing:
        return existing
    now = utc_now_iso()
    conn.execute(
        'INSERT INTO teacher_profiles (user_id, enabled_at) VALUES (?, ?)',
        (user_id, now),
    )
    conn.commit()
    return {'user_id': user_id, 'enabled_at': now}


def teacher_owns_class(conn, teacher_id, class_id):
    row = conn.execute(
        'SELECT 1 FROM classes WHERE id = ? AND teacher_id = ?',
        (class_id, teacher_id),
    ).fetchone()
    return bool(row)


def teacher_can_view(conn, teacher_id, student_id):
    """True when student is an active member of a live class owned by teacher."""
    if int(teacher_id) == int(student_id):
        return False
    if not teacher_is_enabled(conn, teacher_id):
        return False
    if not _table_exists(conn, 'class_memberships'):
        return False
    row = conn.execute(
        '''
        SELECT 1
        FROM class_memberships m
        JOIN classes c ON c.id = m.class_id
        WHERE c.teacher_id = ?
          AND m.student_id = ?
          AND m.status = 'active'
          AND c.archived_at IS NULL
        LIMIT 1
        ''',
        (teacher_id, student_id),
    ).fetchone()
    return bool(row)


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def _new_join_code():
    return ''.join(secrets.choice(_JOIN_ALPHABET) for _ in range(JOIN_CODE_LEN))


def _validate_class_name(name):
    cleaned = ' '.join((name or '').split())
    if not cleaned:
        raise ValueError('name_required')
    if len(cleaned) > CLASS_NAME_MAX:
        raise ValueError('name_too_long')
    return cleaned


def _validate_level_subject(level, subject):
    level = (level or '').strip().lower() or None
    subject = (subject or '').strip().lower() or None
    if not level and not subject:
        return None, None
    if not level or not subject:
        raise ValueError('level_subject_pair')
    try:
        TOPICS[level][subject]
    except KeyError:
        raise ValueError('invalid_topic') from None
    return level, subject


def _active_class_count(conn, teacher_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM classes WHERE teacher_id = ? AND archived_at IS NULL',
        (teacher_id,),
    ).fetchone()
    return int(row['n'] if row else 0)


def create_class(conn, teacher_id, name, level=None, subject=None):
    if not teacher_is_enabled(conn, teacher_id):
        raise ValueError('teacher_required')
    if _active_class_count(conn, teacher_id) >= MAX_CLASSES_PER_TEACHER:
        raise ValueError('class_limit')
    cleaned = _validate_class_name(name)
    level, subject = _validate_level_subject(level, subject)
    now = utc_now_iso()
    last_error = None
    for _ in range(_JOIN_TRIES):
        code = _new_join_code()
        try:
            cursor = conn.execute(
                '''
                INSERT INTO classes (
                    teacher_id, name, level, subject, org_id,
                    join_code, join_code_rotated_at, created_at, archived_at
                ) VALUES (?, ?, ?, ?, NULL, ?, ?, ?, NULL)
                ''',
                (teacher_id, cleaned, level, subject, code, now, now),
            )
            conn.commit()
            created = get_class(conn, cursor.lastrowid)
            _audit_class(
                conn, created['id'], teacher_id, 'class_created',
                meta={'name': cleaned},
            )
            return created
        except sqlite3.IntegrityError as exc:
            last_error = exc
            continue
    raise RuntimeError('join_code_collision') from last_error


def get_class(conn, class_id):
    row = conn.execute(
        '''
        SELECT c.*, (
            SELECT COUNT(*) FROM class_memberships m
            WHERE m.class_id = c.id AND m.status = ?
        ) AS active_member_count
        FROM classes c
        WHERE c.id = ?
        ''',
        (MEMBER_ACTIVE, class_id),
    ).fetchone()
    return dict(row) if row else None


def get_class_for_teacher(conn, teacher_id, class_id):
    row = conn.execute(
        '''
        SELECT c.*, (
            SELECT COUNT(*) FROM class_memberships m
            WHERE m.class_id = c.id AND m.status = ?
        ) AS active_member_count
        FROM classes c
        WHERE c.id = ? AND c.teacher_id = ?
        ''',
        (MEMBER_ACTIVE, class_id, teacher_id),
    ).fetchone()
    return dict(row) if row else None


def list_classes_for_teacher(conn, teacher_id, *, include_archived=True):
    sql = '''
        SELECT c.*, (
            SELECT COUNT(*) FROM class_memberships m
            WHERE m.class_id = c.id AND m.status = ?
        ) AS active_member_count
        FROM classes c
        WHERE c.teacher_id = ?
    '''
    params = [MEMBER_ACTIVE, teacher_id]
    if not include_archived:
        sql += ' AND c.archived_at IS NULL'
    sql += ' ORDER BY c.archived_at IS NOT NULL, c.created_at DESC, c.id DESC'
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def archive_class(conn, teacher_id, class_id):
    row = get_class_for_teacher(conn, teacher_id, class_id)
    if not row:
        raise ValueError('not_found')
    if row.get('archived_at'):
        return row
    now = utc_now_iso()
    conn.execute(
        'UPDATE classes SET archived_at = ? WHERE id = ? AND teacher_id = ?',
        (now, class_id, teacher_id),
    )
    if _table_exists(conn, 'class_invites'):
        conn.execute(
            '''
            UPDATE class_invites
            SET status = 'cancelled', responded_at = ?
            WHERE class_id = ? AND status = 'pending'
            ''',
            (now, class_id),
        )
    conn.commit()
    _audit_class(conn, class_id, teacher_id, 'class_archived')
    return get_class_for_teacher(conn, teacher_id, class_id)


def rotate_join_code(conn, teacher_id, class_id):
    row = get_class_for_teacher(conn, teacher_id, class_id)
    if not row:
        raise ValueError('not_found')
    if row.get('archived_at'):
        raise ValueError('class_archived')
    now = utc_now_iso()
    last_error = None
    for _ in range(_JOIN_TRIES):
        code = _new_join_code()
        try:
            conn.execute(
                '''
                UPDATE classes
                SET join_code = ?, join_code_rotated_at = ?
                WHERE id = ? AND teacher_id = ?
                ''',
                (code, now, class_id, teacher_id),
            )
            conn.commit()
            updated = get_class_for_teacher(conn, teacher_id, class_id)
            _audit_class(conn, class_id, teacher_id, 'join_code_rotated')
            return updated
        except sqlite3.IntegrityError as exc:
            last_error = exc
            continue
    raise RuntimeError('join_code_collision') from last_error


def serialize_class(row, *, include_join_code=True):
    if not row:
        return None
    payload = {
        'id': row['id'],
        'name': row['name'],
        'level': row.get('level'),
        'subject': row.get('subject'),
        'org_id': row.get('org_id'),
        'created_at': row.get('created_at'),
        'archived_at': row.get('archived_at'),
        'join_code_rotated_at': row.get('join_code_rotated_at'),
        'active_member_cap': CLASS_ACTIVE_MEMBER_CAP,
        'active_member_count': int(row.get('active_member_count') or 0),
    }
    if include_join_code:
        payload['join_code'] = row.get('join_code')
    return payload


def serialize_teacher_status(conn, user_id):
    profile = get_teacher_profile(conn, user_id)
    classes = list_classes_for_teacher(conn, user_id) if profile else []
    return {
        'enabled': bool(profile),
        'enabled_at': profile['enabled_at'] if profile else None,
        'class_count': len([item for item in classes if not item.get('archived_at')]),
        'active_member_cap': CLASS_ACTIVE_MEMBER_CAP,
    }


def _normalize_join_code(code):
    return re.sub(r'[^A-Z0-9]', '', (code or '').upper())


def _active_member_count(conn, class_id):
    row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM class_memberships
        WHERE class_id = ? AND status = ?
        ''',
        (class_id, MEMBER_ACTIVE),
    ).fetchone()
    return int(row['n'] if row else 0)


def get_class_by_join_code(conn, code):
    normalized = _normalize_join_code(code)
    if len(normalized) != JOIN_CODE_LEN:
        return None
    row = conn.execute(
        'SELECT * FROM classes WHERE join_code = ?',
        (normalized,),
    ).fetchone()
    return dict(row) if row else None


def get_membership(conn, class_id, student_id):
    row = conn.execute(
        'SELECT * FROM class_memberships WHERE class_id = ? AND student_id = ?',
        (class_id, student_id),
    ).fetchone()
    return dict(row) if row else None


def _audit_class(conn, class_id, actor_id, action, *, subject_handle=None, meta=None):
    from models.class_audit import log_class_event

    log_class_event(
        conn, class_id, actor_id, action,
        subject_handle=subject_handle, meta=meta,
    )


def _user_handle(conn, user_id):
    from models.class_audit import user_handle

    return user_handle(conn, user_id)


def activate_membership(conn, klass, student_id):
    """Add or re-activate a student. Does not commit. Never a silent add — callers must require disclosure."""
    if not klass:
        raise ValueError('not_found')
    if klass.get('archived_at'):
        raise ValueError('class_archived')
    class_id = klass['id']
    if int(klass['teacher_id']) == int(student_id):
        raise ValueError('self_join')
    if is_blocked(conn, student_id, klass['teacher_id']):
        raise ValueError('blocked')
    existing = get_membership(conn, class_id, student_id)
    if existing and existing.get('status') == MEMBER_ACTIVE:
        raise ValueError('already_member')
    if _active_member_count(conn, class_id) >= CLASS_ACTIVE_MEMBER_CAP:
        raise ValueError('class_full')
    now = utc_now_iso()
    if existing:
        conn.execute(
            '''
            UPDATE class_memberships
            SET status = ?, joined_at = ?, removed_at = NULL, removed_by_teacher_id = NULL
            WHERE class_id = ? AND student_id = ?
            ''',
            (MEMBER_ACTIVE, now, class_id, student_id),
        )
    else:
        try:
            conn.execute(
                '''
                INSERT INTO class_memberships (
                    class_id, student_id, status, joined_at,
                    removed_at, removed_by_teacher_id
                ) VALUES (?, ?, ?, ?, NULL, NULL)
                ''',
                (class_id, student_id, MEMBER_ACTIVE, now),
            )
        except sqlite3.IntegrityError:
            raise ValueError('already_member') from None
    if _active_member_count(conn, class_id) > CLASS_ACTIVE_MEMBER_CAP:
        conn.rollback()
        raise ValueError('class_full')
    if _table_exists(conn, 'class_invites'):
        conn.execute(
            '''
            UPDATE class_invites
            SET status = 'accepted', responded_at = ?
            WHERE class_id = ? AND student_id = ? AND status = 'pending'
            ''',
            (now, class_id, student_id),
        )
    return get_membership(conn, class_id, student_id)


def join_class(conn, student_id, code, *, disclosed):
    if not disclosed:
        raise ValueError('join_disclosure_required')
    klass = get_class_by_join_code(conn, code)
    if not klass or klass.get('archived_at'):
        raise ValueError('invalid_join_code')
    try:
        membership = activate_membership(conn, klass, student_id)
    except ValueError as exc:
        if str(exc) in ('blocked', 'class_archived'):
            raise ValueError('invalid_join_code') from exc
        raise
    conn.commit()
    handle = _user_handle(conn, student_id)
    _audit_class(
        conn, klass['id'], student_id, 'student_joined',
        subject_handle=handle,
        meta={'via': 'code'},
    )
    return membership


def list_classes_for_student(conn, student_id, *, include_removed=False):
    sql = '''
        SELECT c.id, c.name, c.level, c.subject, c.archived_at, c.teacher_id,
               u.handle AS teacher_handle,
               m.status, m.joined_at, m.removed_at
        FROM class_memberships m
        JOIN classes c ON c.id = m.class_id
        JOIN users u ON u.id = c.teacher_id
        WHERE m.student_id = ?
    '''
    params = [student_id]
    if not include_removed:
        sql += ' AND m.status = ?'
        params.append(MEMBER_ACTIVE)
    sql += ' ORDER BY m.joined_at DESC, c.id DESC'
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def list_roster(conn, teacher_id, class_id, *, include_removed=False):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    sql = '''
        SELECT m.student_id, u.handle, m.status, m.joined_at, m.removed_at
        FROM class_memberships m
        JOIN users u ON u.id = m.student_id
        WHERE m.class_id = ?
    '''
    params = [class_id]
    if not include_removed:
        sql += ' AND m.status = ?'
        params.append(MEMBER_ACTIVE)
    sql += ' ORDER BY m.joined_at ASC, u.handle COLLATE NOCASE ASC'
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def remove_student(conn, teacher_id, class_id, student_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    existing = get_membership(conn, class_id, student_id)
    if not existing:
        raise ValueError('not_found')
    if existing.get('status') == MEMBER_REMOVED:
        return existing
    handle = _user_handle(conn, student_id)
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE class_memberships
        SET status = ?, removed_at = ?, removed_by_teacher_id = ?
        WHERE class_id = ? AND student_id = ?
        ''',
        (MEMBER_REMOVED, now, teacher_id, class_id, student_id),
    )
    conn.commit()
    _audit_class(
        conn, class_id, teacher_id, 'student_removed',
        subject_handle=handle,
    )
    return get_membership(conn, class_id, student_id)


def serialize_student_class(row):
    if not row:
        return None
    return {
        'id': row['id'],
        'name': row['name'],
        'level': row.get('level'),
        'subject': row.get('subject'),
        'teacher_handle': row.get('teacher_handle'),
        'joined_at': row.get('joined_at'),
        'archived_at': row.get('archived_at'),
        'can_leave': False,
    }


def serialize_roster_member(row):
    if not row:
        return None
    payload = {
        'student_id': row['student_id'],
        'handle': row['handle'],
        'status': row['status'],
        'joined_at': row.get('joined_at'),
        'removed_at': row.get('removed_at'),
    }
    if 'last_active' in row:
        payload['last_active'] = row.get('last_active')
    if 'quiz_count_7d' in row:
        payload['quiz_count_7d'] = int(row.get('quiz_count_7d') or 0)
    return payload


def disclosure_payload():
    return {
        'disclosure': JOIN_DISCLOSURE,
        'can_leave': False,
        'active_member_cap': CLASS_ACTIVE_MEMBER_CAP,
    }
