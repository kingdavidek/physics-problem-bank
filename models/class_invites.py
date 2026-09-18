"""Handle invites into a class (G8 Phase 5). Still opt-in — never a silent add."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from models.class_audit import log_class_event, user_handle
from models.classes import (
    CLASS_ACTIVE_MEMBER_CAP,
    JOIN_DISCLOSURE,
    MEMBER_ACTIVE,
    activate_membership,
    get_class,
    get_class_for_teacher,
    get_membership,
    teacher_owns_class,
)
from models.moderation import is_blocked
from models.user import utc_now_iso

INVITE_PENDING = 'pending'
INVITE_ACCEPTED = 'accepted'
INVITE_DECLINED = 'declined'
INVITE_CANCELLED = 'cancelled'

MAX_PENDING_INVITES_PER_CLASS = 40
INVITE_EXPIRE_DAYS = 14


def _table_exists(conn, name):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return bool(row)


def _invite_cutoff_iso():
    return (datetime.now(timezone.utc) - timedelta(days=INVITE_EXPIRE_DAYS)).isoformat()


def _invite_is_expired(created_at):
    if not created_at:
        return True
    try:
        stamp = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
    except ValueError:
        return True
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp < datetime.now(timezone.utc) - timedelta(days=INVITE_EXPIRE_DAYS)


def _pending_count(conn, class_id):
    row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM class_invites
        WHERE class_id = ? AND status = ? AND created_at >= ?
        ''',
        (class_id, INVITE_PENDING, _invite_cutoff_iso()),
    ).fetchone()
    return int(row['n'] if row else 0)


def _claim_invite(conn, invite_id, new_status):
    cursor = conn.execute(
        '''
        UPDATE class_invites
        SET status = ?, responded_at = ?
        WHERE id = ? AND status = ?
        ''',
        (new_status, utc_now_iso(), invite_id, INVITE_PENDING),
    )
    return cursor.rowcount == 1


def get_invite(conn, invite_id):
    if not _table_exists(conn, 'class_invites'):
        return None
    row = conn.execute(
        '''
        SELECT i.*, c.name AS class_name, c.archived_at,
               t.handle AS teacher_handle, s.handle AS student_handle
        FROM class_invites i
        JOIN classes c ON c.id = i.class_id
        JOIN users t ON t.id = i.teacher_id
        JOIN users s ON s.id = i.student_id
        WHERE i.id = ?
        ''',
        (invite_id,),
    ).fetchone()
    return dict(row) if row else None


def get_invite_for_pair(conn, class_id, student_id):
    if not _table_exists(conn, 'class_invites'):
        return None
    row = conn.execute(
        '''
        SELECT * FROM class_invites
        WHERE class_id = ? AND student_id = ?
        ''',
        (class_id, student_id),
    ).fetchone()
    return dict(row) if row else None


def invite_student(conn, teacher_id, class_id, student_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    klass = get_class_for_teacher(conn, teacher_id, class_id)
    if not klass:
        raise ValueError('not_found')
    if klass.get('archived_at'):
        raise ValueError('class_archived')
    student_id = int(student_id)
    teacher_id = int(teacher_id)
    if student_id == teacher_id:
        raise ValueError('self_invite')
    if is_blocked(conn, teacher_id, student_id):
        raise ValueError('blocked')
    membership = get_membership(conn, class_id, student_id)
    if membership and membership.get('status') == MEMBER_ACTIVE:
        raise ValueError('already_member')

    existing = get_invite_for_pair(conn, class_id, student_id)
    now = utc_now_iso()
    if (
        existing
        and existing.get('status') == INVITE_PENDING
        and not _invite_is_expired(existing.get('created_at'))
    ):
        raise ValueError('already_invited')
    if _pending_count(conn, class_id) >= MAX_PENDING_INVITES_PER_CLASS:
        raise ValueError('invite_limit')
    if existing:
        conn.execute(
            '''
            UPDATE class_invites
            SET teacher_id = ?, status = ?, created_at = ?, responded_at = NULL
            WHERE id = ?
            ''',
            (teacher_id, INVITE_PENDING, now, existing['id']),
        )
        invite_id = existing['id']
    else:
        cursor = conn.execute(
            '''
            INSERT INTO class_invites (
                class_id, teacher_id, student_id, status, created_at, responded_at
            ) VALUES (?, ?, ?, ?, ?, NULL)
            ''',
            (class_id, teacher_id, student_id, INVITE_PENDING, now),
        )
        invite_id = cursor.lastrowid
    conn.commit()
    handle = user_handle(conn, student_id)
    log_class_event(
        conn, class_id, teacher_id, 'invite_sent',
        subject_handle=handle,
        meta={'invite_id': invite_id},
    )
    return get_invite(conn, invite_id)


def list_pending_invites_for_class(conn, teacher_id, class_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    if not _table_exists(conn, 'class_invites'):
        return []
    rows = conn.execute(
        '''
        SELECT i.*, c.name AS class_name, s.handle AS student_handle,
               t.handle AS teacher_handle
        FROM class_invites i
        JOIN classes c ON c.id = i.class_id
        JOIN users s ON s.id = i.student_id
        JOIN users t ON t.id = i.teacher_id
        WHERE i.class_id = ? AND i.status = ? AND i.created_at >= ?
        ORDER BY i.created_at DESC, i.id DESC
        ''',
        (class_id, INVITE_PENDING, _invite_cutoff_iso()),
    ).fetchall()
    return [dict(row) for row in rows]


def list_pending_invites_for_student(conn, student_id):
    if not _table_exists(conn, 'class_invites'):
        return []
    rows = conn.execute(
        '''
        SELECT i.*, c.name AS class_name, c.archived_at,
               t.handle AS teacher_handle, s.handle AS student_handle
        FROM class_invites i
        JOIN classes c ON c.id = i.class_id
        JOIN users t ON t.id = i.teacher_id
        JOIN users s ON s.id = i.student_id
        WHERE i.student_id = ? AND i.status = ? AND c.archived_at IS NULL
          AND i.created_at >= ?
        ORDER BY i.created_at DESC, i.id DESC
        ''',
        (student_id, INVITE_PENDING, _invite_cutoff_iso()),
    ).fetchall()
    return [dict(row) for row in rows]


def accept_invite(conn, student_id, invite_id, *, disclosed):
    if not disclosed:
        raise ValueError('join_disclosure_required')
    invite = get_invite(conn, invite_id)
    if not invite or int(invite['student_id']) != int(student_id):
        raise ValueError('not_found')
    if invite.get('status') != INVITE_PENDING or _invite_is_expired(invite.get('created_at')):
        raise ValueError('invite_not_pending')
    klass = get_class(conn, invite['class_id'])
    if not klass or klass.get('archived_at'):
        raise ValueError('class_archived')
    if is_blocked(conn, student_id, invite['teacher_id']):
        raise ValueError('blocked')
    if not _claim_invite(conn, invite_id, INVITE_ACCEPTED):
        raise ValueError('invite_not_pending')
    try:
        membership = activate_membership(conn, klass, student_id)
    except ValueError as exc:
        if str(exc) == 'already_member':
            conn.commit()
        raise
    conn.commit()
    handle = user_handle(conn, student_id)
    log_class_event(
        conn, klass['id'], student_id, 'invite_accepted',
        subject_handle=handle,
        meta={'invite_id': invite_id, 'via': 'invite'},
    )
    log_class_event(
        conn, klass['id'], student_id, 'student_joined',
        subject_handle=handle,
        meta={'via': 'invite'},
    )
    return membership


def decline_invite(conn, student_id, invite_id):
    invite = get_invite(conn, invite_id)
    if not invite or int(invite['student_id']) != int(student_id):
        raise ValueError('not_found')
    if invite.get('status') != INVITE_PENDING or _invite_is_expired(invite.get('created_at')):
        raise ValueError('invite_not_pending')
    if not _claim_invite(conn, invite_id, INVITE_DECLINED):
        raise ValueError('invite_not_pending')
    conn.commit()
    handle = user_handle(conn, student_id)
    log_class_event(
        conn, invite['class_id'], student_id, 'invite_declined',
        subject_handle=handle,
        meta={'invite_id': invite_id},
    )
    return True


def cancel_invite(conn, teacher_id, class_id, invite_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    invite = get_invite(conn, invite_id)
    if not invite or int(invite['class_id']) != int(class_id):
        raise ValueError('not_found')
    if invite.get('status') != INVITE_PENDING or _invite_is_expired(invite.get('created_at')):
        raise ValueError('invite_not_pending')
    if not _claim_invite(conn, invite_id, INVITE_CANCELLED):
        raise ValueError('invite_not_pending')
    conn.commit()
    log_class_event(
        conn, class_id, teacher_id, 'invite_cancelled',
        subject_handle=invite.get('student_handle'),
        meta={'invite_id': invite_id},
    )
    return True


def serialize_invite(row, *, for_student=False):
    if not row:
        return None
    payload = {
        'id': row['id'],
        'class_id': row['class_id'],
        'class_name': row.get('class_name'),
        'status': row['status'],
        'created_at': row.get('created_at'),
        'can_leave': False,
    }
    if for_student:
        payload['teacher_handle'] = row.get('teacher_handle')
        payload['disclosure'] = JOIN_DISCLOSURE
        payload['active_member_cap'] = CLASS_ACTIVE_MEMBER_CAP
    else:
        payload['student_handle'] = row.get('student_handle')
    return payload
