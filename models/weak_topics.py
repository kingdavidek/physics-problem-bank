"""Identify topics where the user is struggling from quiz and MCQ history."""
from datetime import date, timedelta

MIN_MCQ_ATTEMPTS = 3
MIN_QUIZ_ATTEMPTS = 1
WEAK_QUIZ_PCT = 70.0
WEAK_MCQ_PCT = 70.0
RECENT_QUIZ_PCT = 60.0
RECENT_DAYS = 14
DEFAULT_LIMIT = 8


def _topic_key(level, subject, topic):
    return (level, subject, topic)


def _empty_topic_stats():
    return {
        'quiz_count': 0,
        'quiz_score_sum': 0,
        'quiz_total_sum': 0,
        'quiz_last_at': None,
        'quiz_last_score': None,
        'quiz_last_total': None,
        'quiz_best_pct': None,
        'mcq_count': 0,
        'mcq_correct': 0,
        'mcq_last_at': None,
        'last_practised': None,
    }


def _aggregate_topic_stats(conn, user_id, *, lookback_days=None):
    since_iso = None
    if lookback_days is not None:
        since_day = (date.today() - timedelta(days=lookback_days - 1)).isoformat()
        since_iso = f'{since_day}T00:00:00'

    topics = {}

    quiz_sql = '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ?
    '''
    quiz_params = [user_id]
    if since_iso:
        quiz_sql += ' AND created_at >= ?'
        quiz_params.append(since_iso)

    for row in conn.execute(quiz_sql, quiz_params).fetchall():
        key = _topic_key(row['level'], row['subject'], row['topic'])
        stats = topics.setdefault(key, _empty_topic_stats())
        score = row['score'] or 0
        total = row['total'] or 0
        stats['quiz_count'] += 1
        stats['quiz_score_sum'] += score
        stats['quiz_total_sum'] += total
        pct = (100.0 * score / total) if total else 0.0
        if stats['quiz_best_pct'] is None or pct > stats['quiz_best_pct']:
            stats['quiz_best_pct'] = pct
        created_at = row['created_at']
        if not stats['quiz_last_at'] or created_at > stats['quiz_last_at']:
            stats['quiz_last_at'] = created_at
            stats['quiz_last_score'] = score
            stats['quiz_last_total'] = total
        if not stats['last_practised'] or created_at > stats['last_practised']:
            stats['last_practised'] = created_at

    mcq_sql = '''
        SELECT level, subject, topic, correct, created_at
        FROM generator_mcq_attempts
        WHERE user_id = ?
    '''
    mcq_params = [user_id]
    if since_iso:
        mcq_sql += ' AND created_at >= ?'
        mcq_params.append(since_iso)

    for row in conn.execute(mcq_sql, mcq_params).fetchall():
        key = _topic_key(row['level'], row['subject'], row['topic'])
        stats = topics.setdefault(key, _empty_topic_stats())
        stats['mcq_count'] += 1
        stats['mcq_correct'] += int(row['correct'] or 0)
        created_at = row['created_at']
        if not stats['mcq_last_at'] or created_at > stats['mcq_last_at']:
            stats['mcq_last_at'] = created_at
        if not stats['last_practised'] or created_at > stats['last_practised']:
            stats['last_practised'] = created_at

    return topics


def _compute_weakness(stats):
    """Return (weakness_score, reasons) or None if topic is not weak enough."""
    reasons = []
    weakness_score = 0.0
    quiz_avg_pct = None
    mcq_accuracy_pct = None

    if stats['quiz_count'] >= MIN_QUIZ_ATTEMPTS and stats['quiz_total_sum']:
        quiz_avg_pct = 100.0 * stats['quiz_score_sum'] / stats['quiz_total_sum']
        if quiz_avg_pct < WEAK_QUIZ_PCT:
            weakness_score += (WEAK_QUIZ_PCT - quiz_avg_pct) * 1.5
            label = 'attempt' if stats['quiz_count'] == 1 else 'attempts'
            reasons.append(
                f'Quiz average {quiz_avg_pct:.0f}% ({stats["quiz_count"]} {label})'
            )

        last_at = stats.get('quiz_last_at') or ''
        if (
            stats['quiz_last_total']
            and last_at[:10] >= (date.today() - timedelta(days=RECENT_DAYS - 1)).isoformat()
        ):
            last_pct = 100.0 * stats['quiz_last_score'] / stats['quiz_last_total']
            if last_pct < RECENT_QUIZ_PCT:
                weakness_score += max(0.0, RECENT_QUIZ_PCT - last_pct) * 0.5
                recent = (
                    f'Recent quiz {stats["quiz_last_score"]}/'
                    f'{stats["quiz_last_total"]}'
                )
                if recent not in reasons:
                    reasons.append(recent)

    if stats['mcq_count'] >= MIN_MCQ_ATTEMPTS:
        mcq_accuracy_pct = 100.0 * stats['mcq_correct'] / stats['mcq_count']
        if mcq_accuracy_pct < WEAK_MCQ_PCT:
            weakness_score += (WEAK_MCQ_PCT - mcq_accuracy_pct) * 1.0
            wrong = stats['mcq_count'] - stats['mcq_correct']
            reasons.append(
                f'MCQ accuracy {mcq_accuracy_pct:.0f}% ({wrong} wrong of {stats["mcq_count"]})'
            )

    if not reasons:
        return None

    return {
        'weakness_score': round(weakness_score, 1),
        'reasons': reasons,
        'quiz_average_pct': round(quiz_avg_pct, 1) if quiz_avg_pct is not None else None,
        'mcq_accuracy_pct': round(mcq_accuracy_pct, 1) if mcq_accuracy_pct is not None else None,
    }


def analyze_weak_topics(conn, user_id, *, limit=DEFAULT_LIMIT, lookback_days=None):
    """
    Rank topics the user should revisit based on quiz and generator MCQ history.
    Returns list sorted by weakness_score descending.
    """
    aggregated = _aggregate_topic_stats(conn, user_id, lookback_days=lookback_days)
    ranked = []

    for (level, subject, topic), stats in aggregated.items():
        weakness = _compute_weakness(stats)
        if not weakness:
            continue
        best_quiz = None
        if stats['quiz_best_pct'] is not None and stats['quiz_count']:
            best_quiz = f'{stats["quiz_best_pct"]:.0f}% best'
        ranked.append({
            'level': level,
            'subject': subject,
            'topic': topic,
            'weakness_score': weakness['weakness_score'],
            'reasons': weakness['reasons'],
            'quiz_average_pct': weakness['quiz_average_pct'],
            'mcq_accuracy_pct': weakness['mcq_accuracy_pct'],
            'quiz_attempts': stats['quiz_count'],
            'mcq_attempts': stats['mcq_count'],
            'best_quiz_pct': round(stats['quiz_best_pct'], 1) if stats['quiz_best_pct'] is not None else None,
            'best_quiz_label': best_quiz,
            'last_practised': stats['last_practised'],
            'last_practised_date': (stats['last_practised'] or '')[:10] or None,
        })

    ranked.sort(
        key=lambda item: (
            -item['weakness_score'],
            item['last_practised'] or '',
        ),
    )
    return ranked[:limit]


def serialize_weak_topic(item, *, topic_label=None, topic_url=None, lesson_quiz_url=None):
    """JSON/API shape for one weak topic row."""
    out = {
        'level': item['level'],
        'subject': item['subject'],
        'topic': item['topic'],
        'topic_label': topic_label or item['topic'],
        'weakness_score': item['weakness_score'],
        'reasons': item['reasons'],
        'quiz_average_pct': item['quiz_average_pct'],
        'mcq_accuracy_pct': item['mcq_accuracy_pct'],
        'quiz_attempts': item['quiz_attempts'],
        'mcq_attempts': item['mcq_attempts'],
        'best_quiz_pct': item['best_quiz_pct'],
        'last_practised': item['last_practised'],
        'last_practised_date': item['last_practised_date'],
    }
    if topic_url:
        out['topic_url'] = topic_url
    if lesson_quiz_url:
        out['lesson_quiz_url'] = lesson_quiz_url
    return out
