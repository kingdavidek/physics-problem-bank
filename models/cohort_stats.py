"""Anonymous cohort stats for individual practice questions (Phase G5).

Aggregates how often students get the *same* generated question wrong.
Stats are keyed by a stable hash of the question stem + mark-scheme payload,
never expose individual users, and only surface once a minimum sample size is
reached.
"""
import hashlib
import re
from html import unescape

from models.user import utc_now_iso

MIN_SAMPLE_SIZE = 20


def _strip_html(text):
    text = re.sub(r'<[^>]+>', ' ', text or '')
    text = unescape(text)
    return re.sub(r'\s+', ' ', text).strip().lower()


def _mcq_correct_option_text(problem):
    letter = str(problem.get('correct_answer') or '').strip()[:1].upper()
    if not letter:
        return ''
    for opt in problem.get('options') or []:
        opt_s = str(opt or '').strip()
        if not opt_s:
            continue
        opt_letter = opt_s[:1].upper()
        if opt_letter == letter:
            body = opt_s[1:].lstrip('.) \u2013-\u2014:')
            return _strip_html(body or opt_s)
    return ''


def compute_problem_key(problem, *, level, subject, topic, variant_name=None, field_correct_raw=None):
    """Build a stable anonymous key for one gradable question instance."""
    if not isinstance(problem, dict):
        return None
    level = (level or '').strip()
    subject = (subject or '').strip()
    topic = (topic or '').strip()
    if not (level and subject and topic):
        return None

    question = _strip_html(problem.get('question') or '')
    if not question:
        return None

    parts = [level, subject, topic]
    variant = (variant_name or problem.get('variant_name') or '').strip()
    if variant:
        parts.append(variant)
    parts.append(question)

    if field_correct_raw is not None:
        parts.append('field')
        parts.append(str(field_correct_raw))
    elif problem.get('correct_answer_raw') is not None:
        parts.append(str(problem.get('answer_type') or 'number'))
        parts.append(str(problem['correct_answer_raw']))
    elif problem.get('options') and problem.get('correct_answer'):
        option_text = _mcq_correct_option_text(problem)
        if not option_text:
            return None
        parts.append('mcq')
        parts.append(option_text)
    else:
        return None

    digest = hashlib.sha256('\x1e'.join(parts).encode('utf-8')).hexdigest()
    return digest[:32]


def record_cohort_sample(conn, problem_key, level, subject, topic, correct):
    """Increment anonymous counters for one answered question."""
    if not problem_key:
        return
    now = utc_now_iso()
    wrong_inc = 0 if correct else 1
    conn.execute(
        '''
        INSERT INTO problem_cohort_stats (
            problem_key, level, subject, topic,
            total_attempts, wrong_attempts, updated_at
        ) VALUES (?, ?, ?, ?, 1, ?, ?)
        ON CONFLICT(problem_key) DO UPDATE SET
            total_attempts = total_attempts + 1,
            wrong_attempts = wrong_attempts + excluded.wrong_attempts,
            updated_at = excluded.updated_at
        ''',
        (problem_key, level, subject, topic, wrong_inc, now),
    )
    conn.commit()


def get_cohort_stats(conn, problem_key):
    row = conn.execute(
        '''
        SELECT problem_key, level, subject, topic,
               total_attempts, wrong_attempts, updated_at
        FROM problem_cohort_stats
        WHERE problem_key = ?
        ''',
        (problem_key,),
    ).fetchone()
    if not row:
        return None
    return dict(row)


def serialize_cohort_stats(stats, *, min_sample_size=MIN_SAMPLE_SIZE):
    if not stats:
        return None
    total = int(stats.get('total_attempts') or 0)
    wrong = int(stats.get('wrong_attempts') or 0)
    if total < min_sample_size:
        return None
    wrong_pct = round(100.0 * wrong / total, 1) if total else None
    return {
        'wrong_pct': wrong_pct,
        'sample_size': total,
        'min_sample_size': min_sample_size,
    }


def record_and_get_cohort(
    conn,
    problem,
    *,
    level,
    subject,
    topic,
    variant_name=None,
    correct,
    field_correct_raw=None,
    min_sample_size=MIN_SAMPLE_SIZE,
):
    """Record one anonymous sample and return public stats when eligible."""
    problem_key = compute_problem_key(
        problem,
        level=level,
        subject=subject,
        topic=topic,
        variant_name=variant_name,
        field_correct_raw=field_correct_raw,
    )
    if not problem_key:
        return None
    record_cohort_sample(conn, problem_key, level, subject, topic, correct)
    stats = get_cohort_stats(conn, problem_key)
    return serialize_cohort_stats(stats, min_sample_size=min_sample_size)
