"""Cross-topic skill gaps from wrong-answer reflections (Phase G6).

Rolls up reflection chip tags (e.g. misread_question) across topics so the
student can see recurring mistake patterns, not just per-topic weak scores.
"""
from collections import defaultdict
from datetime import date, timedelta

from models.reflections import PROMPT_TYPE_LABELS, PROMPT_TYPES

DEFAULT_LIMIT = 6
TOPICS_PER_GAP = 5
MIN_REFLECTIONS = 2
DEFAULT_LOOKBACK_DAYS = 90


def prompt_type_label(prompt_type):
    if not prompt_type:
        return 'Note'
    return PROMPT_TYPE_LABELS.get(prompt_type, prompt_type.replace('_', ' ').title())


def analyze_skill_gaps(conn, user_id, *, limit=DEFAULT_LIMIT, lookback_days=DEFAULT_LOOKBACK_DAYS):
    """Rank recurring reflection tags by frequency and recency."""
    params = [user_id]
    sql = '''
        SELECT prompt_type, level, subject, topic, created_at
        FROM user_wrong_answer_reflections
        WHERE user_id = ? AND prompt_type IS NOT NULL
    '''
    if lookback_days is not None:
        since_day = (date.today() - timedelta(days=lookback_days - 1)).isoformat()
        sql += ' AND created_at >= ?'
        params.append(f'{since_day}T00:00:00')

    grouped = defaultdict(lambda: {
        'reflection_count': 0,
        'topics': defaultdict(lambda: {'count': 0, 'last_reflected_at': None}),
        'last_reflected_at': None,
    })

    for row in conn.execute(sql, params).fetchall():
        prompt_type = row['prompt_type']
        if prompt_type not in PROMPT_TYPES:
            continue
        bucket = grouped[prompt_type]
        bucket['reflection_count'] += 1
        topic_key = (row['level'], row['subject'], row['topic'])
        topic_stats = bucket['topics'][topic_key]
        topic_stats['count'] += 1
        created_at = row['created_at']
        if not topic_stats['last_reflected_at'] or created_at > topic_stats['last_reflected_at']:
            topic_stats['last_reflected_at'] = created_at
        if not bucket['last_reflected_at'] or created_at > bucket['last_reflected_at']:
            bucket['last_reflected_at'] = created_at

    ranked = []
    for prompt_type, data in grouped.items():
        if data['reflection_count'] < MIN_REFLECTIONS:
            continue
        topics = []
        for (level, subject, topic), stats in data['topics'].items():
            topics.append({
                'level': level,
                'subject': subject,
                'topic': topic,
                'reflection_count': stats['count'],
                'last_reflected_at': stats['last_reflected_at'],
            })
        topics.sort(
            key=lambda item: (-item['reflection_count'], item['last_reflected_at'] or ''),
        )
        ranked.append({
            'prompt_type': prompt_type,
            'label': prompt_type_label(prompt_type),
            'reflection_count': data['reflection_count'],
            'topic_count': len(topics),
            'topics': topics[:TOPICS_PER_GAP],
            'last_reflected_at': data['last_reflected_at'],
        })

    ranked.sort(
        key=lambda item: (
            -item['reflection_count'],
            item['last_reflected_at'] or '',
        ),
    )
    return ranked[:limit]
