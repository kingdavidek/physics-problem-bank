"""Lesson-complete / ninja / master status and related badge keys."""
from calendar import monthrange
from datetime import datetime, timezone
import json

from models.lesson_steps import lesson_step_total
from topic_registry import TOPICS, iter_topics

QUIZ_LENGTH = 10
MASTER_MONTHS = 3
STATUS_TIERS = (5, 10, 20)

_SUBJECT_LABELS = {
    'maths': 'Maths',
    'physics': 'Physics',
    'cs': 'Computer Science',
    'chemistry': 'Chemistry',
    'science': 'Integrated Science',
}
_LEVEL_LABELS = {
    'gcse': 'GCSE',
    'alevel': 'A-Level',
    'myp': 'MYP',
    'eursc': 'European School',
}
_KIND_EMOJI = {
    'completed': '📘',
    'ninja': '🥷',
    'master': '👑',
}
_KIND_TIER = {
    'completed': 'bronze',
    'ninja': 'silver',
    'master': 'gold',
}
_TIER_EMOJI = {5: '🌱', 10: '🌳', 20: '🌟'}
_TIER_TIER = {5: 'bronze', 10: 'silver', 20: 'gold'}


def _parse_iso(value):
    if not value:
        return None
    text = str(value).replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _add_months(dt, months=MASTER_MONTHS):
    month_index = dt.month - 1 + months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def is_perfect_quiz(score, total):
    total = int(total or 0)
    score = int(score or 0)
    return total >= QUIZ_LENGTH and score == total


def topic_badge_key(kind, level, subject, topic):
    return f'topic_{kind}:{level}:{subject}:{topic}'


def aggregate_badge_key(kind, count):
    return f'topics_{kind}_{count}'


def subject_badge_key(kind, level, subject):
    return f'subject_{kind}:{level}:{subject}'


def _topic_name(level, subject, topic):
    cfg = ((TOPICS.get(level) or {}).get(subject) or {}).get(topic) or {}
    return cfg.get('name') or str(topic).replace('_', ' ').title()


def _subject_title(level, subject):
    return (
        f"{_LEVEL_LABELS.get(level, str(level).title())} "
        f"{_SUBJECT_LABELS.get(subject, str(subject).title())}"
    )


def topic_badge_meta(key):
    """Display metadata for per-topic / aggregate keys not in the static catalog."""
    if not key:
        return None
    if key.startswith('topic_'):
        try:
            kind, level, subject, topic = key.split(':', 3)
        except ValueError:
            return None
        kind = kind[len('topic_'):]
        name = _topic_name(level, subject, topic)
        titles = {
            'completed': f'{name} lesson complete',
            'ninja': f'{name} ninja',
            'master': f'{name} master',
        }
        descriptions = {
            'completed': f'Finish every lesson checkpoint on {name}',
            'ninja': f'Complete the {name} lesson and score 10/10 on its quiz',
            'master': f'Reach {name} ninja, then two consecutive 10/10 quizzes',
        }
        if kind not in titles:
            return None
        return {
            'title': titles[kind],
            'description': descriptions[kind],
            'emoji': _KIND_EMOJI.get(kind, '★'),
            'tier': _KIND_TIER.get(kind, 'bronze'),
        }
    if key.startswith('subject_'):
        try:
            kind, level, subject = key.split(':', 2)
        except ValueError:
            return None
        kind = kind[len('subject_'):]
        title = _subject_title(level, subject)
        titles = {
            'completed': f'{title} complete',
            'ninja': f'{title} ninja',
            'master': f'{title} master',
        }
        if kind not in titles:
            return None
        return {
            'title': titles[kind],
            'description': f'Reach {kind} on every {title} topic',
            'emoji': '🎓',
            'tier': 'gold',
        }
    return None


def catalog_extra_entries():
    """Global 5/10/20 and per-subject badges (not per-topic)."""
    entries = {}
    labels = {
        'completed': 'lessons complete',
        'ninja': 'topic ninjas',
        'master': 'topic masters',
    }
    for kind, label in labels.items():
        for count in STATUS_TIERS:
            entries[aggregate_badge_key(kind, count)] = {
                'title': f'{count} {label}',
                'description': f'Reach {kind} status on {count} topics',
                'emoji': _TIER_EMOJI.get(count, '★'),
                'tier': _TIER_TIER.get(count, 'bronze'),
            }
    for level, subjects in TOPICS.items():
        if not isinstance(subjects, dict):
            continue
        for subject, topics in subjects.items():
            slugs = [slug for slug, _cfg in iter_topics(topics)]
            if not slugs:
                continue
            title = _subject_title(level, subject)
            for kind in ('completed', 'ninja', 'master'):
                entries[subject_badge_key(kind, level, subject)] = {
                    'title': f'{title} {kind}' if kind != 'completed' else f'{title} complete',
                    'description': f'Reach {kind} on every {title} topic',
                    'emoji': '🎓',
                    'tier': 'gold',
                }
    return entries


def resolve_step_total(level, subject, topic, step_total, completed_keys=None):
    """Use stored step_total when set; otherwise fall back to the lesson template."""
    stored = int(step_total or 0)
    if stored > 0:
        return stored
    canonical = lesson_step_total(level, subject, topic)
    if canonical > 0:
        return canonical
    return 0


def compute_topic_status(completed_keys, step_total, quizzes, now=None):
    """Return status flags for one topic.

    Lesson complete = every lesson checkpoint done (step_total > 0).
    Ninja = lesson complete and at least one 10/10 quiz.
    Master = ninja plus two consecutive 10-question perfects; active for
    3 months after the qualifying quiz, extended by later 10/10s in-window.
    """
    now = now or datetime.now(timezone.utc)
    keys = [k for k in (completed_keys or []) if k]
    total_steps = int(step_total or 0)
    lesson_complete = total_steps > 0 and len(keys) >= total_steps
    progress = 0.0
    if total_steps > 0:
        progress = min(1.0, len(keys) / float(total_steps))

    qualifying = []
    for quiz in quizzes or []:
        q_total = int(quiz.get('total') or 0)
        if q_total < QUIZ_LENGTH:
            continue
        dt = _parse_iso(quiz.get('created_at'))
        if dt is None:
            continue
        qualifying.append((dt, is_perfect_quiz(quiz.get('score'), q_total)))

    has_perfect = any(perfect for _dt, perfect in qualifying)
    ninja = bool(lesson_complete and has_perfect)

    master_expires = None
    master_ever = False
    streak = 0
    for dt, perfect in qualifying:
        in_window = master_expires is not None and dt <= master_expires
        if in_window:
            if perfect:
                master_expires = _add_months(dt, MASTER_MONTHS)
            streak = 1 if perfect else 0
            continue
        if perfect:
            streak += 1
        else:
            streak = 0
        if streak >= 2:
            master_ever = True
            master_expires = _add_months(dt, MASTER_MONTHS)

    master_active = bool(
        ninja
        and master_expires is not None
        and now <= master_expires
    )
    if not ninja:
        master_active = False

    if master_active:
        mastery = 1.0
    elif ninja:
        mastery = 0.67
    elif lesson_complete:
        mastery = 0.34
    else:
        mastery = round(0.34 * progress, 3)

    return {
        'lesson_complete': lesson_complete,
        'ninja': ninja,
        'master_ever': bool(ninja and master_ever),
        'master_active': master_active,
        'master_expires_at': master_expires.isoformat() if master_expires and master_active else None,
        'mastery': mastery,
        'step_total': total_steps,
        'completed_count': len(keys),
    }


def topic_status_map(conn, user_id, now=None):
    """(level, subject, topic) → status dict for topics with lesson or quiz data."""
    now = now or datetime.now(timezone.utc)
    lessons = {}
    lesson_cols = {
        row[1] for row in conn.execute('PRAGMA table_info(lesson_progress)').fetchall()
    }
    step_select = ', step_total' if 'step_total' in lesson_cols else ''
    rows = conn.execute(
        f'''
        SELECT level, subject, topic, completed_keys_json{step_select}
        FROM lesson_progress
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchall()
    for row in rows:
        raw = row['completed_keys_json'] or '[]'
        try:
            keys = json.loads(raw)
        except (TypeError, ValueError):
            keys = []
        if not isinstance(keys, list):
            keys = []
        step_total = 0
        if 'step_total' in row.keys():
            step_total = int(row['step_total'] or 0)
        level = row['level']
        subject = row['subject']
        topic = row['topic']
        cleaned_keys = [k for k in keys if isinstance(k, str) and k.strip()]
        lessons[(level, subject, topic)] = {
            'completed_keys': cleaned_keys,
            'step_total': resolve_step_total(
                level,
                subject,
                topic,
                step_total,
                cleaned_keys,
            ),
        }

    quizzes = {}
    quiz_rows = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY created_at ASC, id ASC
        ''',
        (user_id,),
    ).fetchall()
    for row in quiz_rows:
        key = (row['level'], row['subject'], row['topic'])
        quizzes.setdefault(key, []).append({
            'score': row['score'],
            'total': row['total'],
            'created_at': row['created_at'],
        })

    out = {}
    for key in set(lessons) | set(quizzes):
        lesson = lessons.get(key) or {}
        out[key] = compute_topic_status(
            lesson.get('completed_keys') or [],
            lesson.get('step_total') or 0,
            quizzes.get(key) or [],
            now=now,
        )
    return out


def subject_slugs_for_badges():
    subjects = []
    for level, subjects_map in TOPICS.items():
        if not isinstance(subjects_map, dict):
            continue
        for subject, topics in subjects_map.items():
            slugs = [slug for slug, _cfg in iter_topics(topics)]
            if slugs:
                subjects.append((level, subject, slugs))
    return subjects


def gcse_subject_slugs():
    """Backward-compatible alias for GCSE subject badge groups."""
    return [
        item for item in subject_slugs_for_badges()
        if item[0] == 'gcse'
    ]


def milestone_keys_for_statuses(statuses):
    """Badge keys that should be awarded for the given status map."""
    keys = []
    counts = {'completed': 0, 'ninja': 0, 'master': 0}
    for (level, subject, topic), status in statuses.items():
        if status.get('lesson_complete'):
            counts['completed'] += 1
            keys.append(topic_badge_key('completed', level, subject, topic))
        if status.get('ninja'):
            counts['ninja'] += 1
            keys.append(topic_badge_key('ninja', level, subject, topic))
        if status.get('master_ever'):
            counts['master'] += 1
            keys.append(topic_badge_key('master', level, subject, topic))
    for kind, n in counts.items():
        for threshold in STATUS_TIERS:
            if n >= threshold:
                keys.append(aggregate_badge_key(kind, threshold))
    for level, subject, slugs in subject_slugs_for_badges():
        if slugs and all(
            statuses.get((level, subject, slug), {}).get('lesson_complete')
            for slug in slugs
        ):
            keys.append(subject_badge_key('completed', level, subject))
        if slugs and all(
            statuses.get((level, subject, slug), {}).get('ninja')
            for slug in slugs
        ):
            keys.append(subject_badge_key('ninja', level, subject))
        if slugs and all(
            statuses.get((level, subject, slug), {}).get('master_ever')
            for slug in slugs
        ):
            keys.append(subject_badge_key('master', level, subject))
    return keys


def evaluate_topic_milestones(conn, user_id, award_fn, now=None):
    """Award newly earned topic-status badges. ``award_fn`` is ``_award_milestone``."""
    statuses = topic_status_map(conn, user_id, now=now)
    earned = []
    for key in milestone_keys_for_statuses(statuses):
        if award_fn(conn, user_id, key):
            earned.append(key)
    return earned
