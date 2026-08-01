"""Exam-date revision planner (Phase G7), built on weak-topic analysis (G1).

Given an exam date and curriculum scope (level/subject), spreads weak topics
across the remaining study days before the exam — heavier/weaker topics first.
"""
from datetime import date, datetime, timedelta, timezone

from models.user import utc_now_iso
from models.weak_topics import analyze_weak_topics

MAX_TOPICS_PER_DAY = 2
MAX_WEAK_TOPICS = 24
MIN_EXAM_LEAD_DAYS = 0
MAX_EXAM_LEAD_DAYS = 180


def _parse_exam_date(value):
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        raise ValueError('missing_exam_date')
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError('invalid_exam_date') from exc


def _study_dates(exam_date):
    """Calendar dates from today (UTC) through the day before the exam."""
    today = datetime.now(timezone.utc).date()
    if exam_date < today:
        raise ValueError('exam_date_past')
    if exam_date == today:
        return [today]
    last_study = exam_date - timedelta(days=1)
    days = []
    current = today
    while current <= last_study:
        days.append(current)
        current += timedelta(days=1)
        if len(days) > MAX_EXAM_LEAD_DAYS:
            break
    return days


def get_revision_plan_settings(conn, user_id):
    row = conn.execute(
        '''
        SELECT level, subject, exam_date, created_at, updated_at
        FROM user_revision_plans
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not row:
        return None
    return dict(row)


def upsert_revision_plan_settings(conn, user_id, level, subject, exam_date):
    level = (level or '').strip()
    subject = (subject or '').strip()
    exam_day = _parse_exam_date(exam_date)
    if not (level and subject):
        raise ValueError('missing_scope')
    lead_days = (exam_day - datetime.now(timezone.utc).date()).days
    if lead_days > MAX_EXAM_LEAD_DAYS:
        raise ValueError('exam_date_too_far')

    now = utc_now_iso()
    existing = get_revision_plan_settings(conn, user_id)
    if existing:
        conn.execute(
            '''
            UPDATE user_revision_plans
            SET level = ?, subject = ?, exam_date = ?, updated_at = ?
            WHERE user_id = ?
            ''',
            (level, subject, exam_day.isoformat(), now, user_id),
        )
    else:
        conn.execute(
            '''
            INSERT INTO user_revision_plans (
                user_id, level, subject, exam_date, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (user_id, level, subject, exam_day.isoformat(), now, now),
        )
    conn.commit()
    return get_revision_plan_settings(conn, user_id)


def delete_revision_plan_settings(conn, user_id):
    cursor = conn.execute(
        'DELETE FROM user_revision_plans WHERE user_id = ?',
        (user_id,),
    )
    conn.commit()
    return cursor.rowcount > 0


def build_revision_plan(conn, user_id, *, level, subject, exam_date):
    level = (level or '').strip()
    subject = (subject or '').strip()
    exam_day = _parse_exam_date(exam_date)
    study_days = _study_dates(exam_day)

    weak_topics = analyze_weak_topics(
        conn,
        user_id,
        limit=MAX_WEAK_TOPICS,
    )
    scoped = [
        item for item in weak_topics
        if item['level'] == level and item['subject'] == subject
    ]

    sessions = [
        {'plan_date': day.isoformat(), 'topics': []}
        for day in study_days
    ]
    capacity = len(sessions) * MAX_TOPICS_PER_DAY
    if sessions:
        for index, item in enumerate(scoped[:capacity]):
            day_index = index // MAX_TOPICS_PER_DAY
            sessions[day_index]['topics'].append({
                'level': item['level'],
                'subject': item['subject'],
                'topic': item['topic'],
                'weakness_score': item['weakness_score'],
                'reasons': item['reasons'],
                'quiz_average_pct': item.get('quiz_average_pct'),
                'mcq_accuracy_pct': item.get('mcq_accuracy_pct'),
            })

    days_remaining = (exam_day - datetime.now(timezone.utc).date()).days
    return {
        'level': level,
        'subject': subject,
        'exam_date': exam_day.isoformat(),
        'days_remaining': days_remaining,
        'study_day_count': len(study_days),
        'topics_scheduled': sum(len(s['topics']) for s in sessions),
        'weak_topic_count': len(scoped),
        'sessions': sessions,
        'has_plan': bool(sessions),
    }


def revision_plan_for_user(conn, user_id):
    """Return stored settings plus a freshly computed schedule, if configured."""
    settings = get_revision_plan_settings(conn, user_id)
    if not settings:
        return None
    plan = build_revision_plan(
        conn,
        user_id,
        level=settings['level'],
        subject=settings['subject'],
        exam_date=settings['exam_date'],
    )
    plan['created_at'] = settings.get('created_at')
    plan['updated_at'] = settings.get('updated_at')
    return plan
