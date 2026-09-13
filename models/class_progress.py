"""T0–T2 class progress for teachers (G8 Phase 3). No T3 free-text."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from models.class_assignments import class_set_work_summary, student_set_work_for_class
from models.classes import (
    MEMBER_ACTIVE,
    get_membership,
    list_roster,
    teacher_owns_class,
)
from models.revision_queue import list_revision_queue, sync_revision_queue
from models.skill_gaps import analyze_skill_gaps
from models.social import lesson_progress_summary
from models.weak_topics import analyze_weak_topics, serialize_weak_topic
from topic_registry import TOPICS

ACTIVITY_DAYS = 7
T0_WEAK_TOPIC_LIMIT = 5
T1_WEAK_LIMIT = 8
T1_QUIZ_LIMIT = 5
T1_LESSON_LIMIT = 8
T2_GAP_LIMIT = 6


def _topic_label(level, subject, topic):
    try:
        return TOPICS[level][subject][topic].get('name', topic.replace('_', ' ').title())
    except (KeyError, TypeError, AttributeError):
        return (topic or '').replace('_', ' ').title()


def _since_iso(days):
    since_day = (datetime.now(timezone.utc).date() - timedelta(days=days - 1)).isoformat()
    return f'{since_day}T00:00:00'


def teacher_can_view_member(conn, teacher_id, class_id, student_id):
    """True when the student is an active member of this teacher-owned class."""
    if int(teacher_id) == int(student_id):
        return False
    if not teacher_owns_class(conn, teacher_id, class_id):
        return False
    existing = get_membership(conn, class_id, student_id)
    return bool(existing and existing.get('status') == MEMBER_ACTIVE)


def student_activity_snippet(conn, student_id):
    since = _since_iso(ACTIVITY_DAYS)
    last_row = conn.execute(
        '''
        SELECT MAX(ts) AS last_active FROM (
            SELECT MAX(created_at) AS ts FROM quiz_attempts WHERE user_id = ?
            UNION ALL
            SELECT MAX(created_at) AS ts FROM generator_mcq_attempts WHERE user_id = ?
            UNION ALL
            SELECT MAX(updated_at) AS ts FROM lesson_progress WHERE user_id = ?
        )
        ''',
        (student_id, student_id, student_id),
    ).fetchone()
    quiz_row = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM quiz_attempts
        WHERE user_id = ? AND created_at >= ?
        ''',
        (student_id, since),
    ).fetchone()
    return {
        'last_active': last_row['last_active'] if last_row else None,
        'quiz_count_7d': int(quiz_row['n'] if quiz_row else 0),
    }


def enrich_roster(conn, members):
    return [
        {**dict(member), **student_activity_snippet(conn, member['student_id'])}
        for member in members
    ]


def class_aggregates(conn, teacher_id, class_id):
    if not teacher_owns_class(conn, teacher_id, class_id):
        raise ValueError('not_found')
    roster = list_roster(conn, teacher_id, class_id)
    ids = [row['student_id'] for row in roster]
    since = _since_iso(ACTIVITY_DAYS)
    avg_quiz_pct = None
    students_with_quizzes = 0
    quiz_attempts_7d = 0
    mcq_attempts_7d = 0
    if ids:
        placeholders = ','.join('?' * len(ids))
        pooled = conn.execute(
            f'''
            SELECT SUM(score) AS s, SUM(total) AS t,
                   COUNT(DISTINCT user_id) AS n
            FROM quiz_attempts
            WHERE user_id IN ({placeholders})
            ''',
            ids,
        ).fetchone()
        total = int(pooled['t'] or 0) if pooled else 0
        if total:
            avg_quiz_pct = round(100.0 * int(pooled['s'] or 0) / total, 1)
        students_with_quizzes = int(pooled['n'] or 0) if pooled else 0
        quiz_attempts_7d = int(conn.execute(
            f'''
            SELECT COUNT(*) AS n FROM quiz_attempts
            WHERE user_id IN ({placeholders}) AND created_at >= ?
            ''',
            [*ids, since],
        ).fetchone()['n'])
        mcq_attempts_7d = int(conn.execute(
            f'''
            SELECT COUNT(*) AS n FROM generator_mcq_attempts
            WHERE user_id IN ({placeholders}) AND created_at >= ?
            ''',
            [*ids, since],
        ).fetchone()['n'])

    weak_counts = Counter()
    for member in roster:
        for item in analyze_weak_topics(conn, member['student_id'], limit=T1_WEAK_LIMIT):
            key = (item['level'], item['subject'], item['topic'])
            weak_counts[key] += 1

    top_weak = []
    for (level, subject, topic), count in weak_counts.most_common(T0_WEAK_TOPIC_LIMIT):
        top_weak.append({
            'level': level,
            'subject': subject,
            'topic': topic,
            'topic_label': _topic_label(level, subject, topic),
            'student_count': count,
        })

    return {
        'student_count': len(roster),
        'avg_quiz_pct': avg_quiz_pct,
        'students_with_quizzes': students_with_quizzes,
        'quiz_attempts_7d': quiz_attempts_7d,
        'mcq_attempts_7d': mcq_attempts_7d,
        'top_weak_topics': top_weak,
        'set_work': class_set_work_summary(conn, class_id),
    }


def student_progress(conn, teacher_id, class_id, student_id):
    if not teacher_can_view_member(conn, teacher_id, class_id, student_id):
        raise ValueError('not_found')
    handle_row = conn.execute(
        'SELECT handle FROM users WHERE id = ?',
        (student_id,),
    ).fetchone()
    handle = handle_row['handle'] if handle_row else None

    weak_raw = analyze_weak_topics(conn, student_id, limit=T1_WEAK_LIMIT)
    weak_keys = {
        (item['level'], item['subject'], item['topic']) for item in weak_raw
    }
    weak_topics = [
        serialize_weak_topic(
            item,
            topic_label=_topic_label(item['level'], item['subject'], item['topic']),
        )
        for item in weak_raw
    ]

    quizzes = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (student_id, T1_QUIZ_LIMIT),
    ).fetchall()
    recent_quizzes = []
    for row in quizzes:
        item = dict(row)
        item['topic_label'] = _topic_label(item['level'], item['subject'], item['topic'])
        recent_quizzes.append(item)

    lessons = []
    for row in lesson_progress_summary(conn, student_id, limit=T1_LESSON_LIMIT):
        lessons.append({
            'level': row['level'],
            'subject': row['subject'],
            'topic': row['topic'],
            'topic_label': _topic_label(row['level'], row['subject'], row['topic']),
            'completed_count': row.get('completed_count') or 0,
            'updated_at': row.get('updated_at'),
        })

    sync_revision_queue(conn, student_id)
    due_today_count = len(list_revision_queue(conn, student_id, limit=50, due_only=True))

    skill_gaps = []
    for gap in analyze_skill_gaps(conn, student_id, limit=T2_GAP_LIMIT):
        topics_out = []
        overlaps_weak = False
        for topic_item in gap.get('topics') or []:
            key = (topic_item['level'], topic_item['subject'], topic_item['topic'])
            if key in weak_keys:
                overlaps_weak = True
            topics_out.append({
                'level': topic_item['level'],
                'subject': topic_item['subject'],
                'topic': topic_item['topic'],
                'topic_label': _topic_label(*key),
                'is_weak_topic': key in weak_keys,
            })
        skill_gaps.append({
            'prompt_type': gap['prompt_type'],
            'label': gap['label'],
            'reflection_count': gap['reflection_count'],
            'topic_count': gap['topic_count'],
            'last_reflected_at': gap.get('last_reflected_at'),
            'topics': topics_out,
            'overlaps_weak_topic': overlaps_weak,
        })

    return {
        'student_id': student_id,
        'handle': handle,
        'weak_topics': weak_topics,
        'recent_quizzes': recent_quizzes,
        'lessons': lessons,
        'due_today_count': due_today_count,
        'skill_gaps': skill_gaps,
        'set_work': student_set_work_for_class(conn, class_id, student_id),
    }
