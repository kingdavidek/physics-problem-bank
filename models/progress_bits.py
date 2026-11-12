"""E11 Phase 4 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 4.2 to 4.4, 2.1 and 2.2): progress shown around the site.

* the mastery path of one topic (Lesson complete, Ninja, Master) and the next step in words, for the quiz results strip and the
  lesson page chips and quiz bar;
* the Today numbers (questions right, effort points, the streak) for the Profile and Practice pages;
* Your week: last week's days studied, questions right and best moment, offered once on the first visit of a new week;
* Close to a badge: the nearest badge when one or two steps are left, at most once a day.

The copy is system voice (the COPY block below), linted through models/zorp_voice.py `extract_progress_copy`. Nothing here writes.
"""
from datetime import datetime, timedelta

from models.gamification import _effort_score_since, _utc_today, get_study_streak
from models.topic_status import TOPICS, topic_status_map

# BEGIN PROGRESS COPY
STEPS = (('lesson', 'Lesson complete'), ('ninja', 'Ninja'), ('master', 'Master'))
NEXT = {
    'lesson': 'Finish every lesson step for Lesson complete.',
    'lesson_ninja': "Finish the lesson's quick checks for Ninja.",
    'ninja': 'A 10/10 on the quiz makes you a ninja on this topic.',
    'master_two': 'Two 10/10s in a row make you a master.',
    'master_one': 'One more 10/10 in a row for Master.',
    'master_keep': 'You are a master here. A 10/10 by {date} keeps it.',
    'master_again': 'Two 10/10s in a row make you a master again.',
}
BAR_DONE = 'Lesson done.'
LABELS = {
    'path': 'Mastery path',
    'earned': 'What you earned',
    'level': 'Level {n}',
    'to_next': '{n} XP to level {next}',
    'today': 'Today',
    'right': '{n} right',
    'right_one': '1 right',
    'xp': '{n} XP',
    'streak': '{n}-day streak',
    'no_streak': 'No streak yet',
    'done': '(done)',
}
# END PROGRESS COPY

TIER_RANK = {'violet': 0, 'gold': 1, 'silver': 2, 'bronze': 3}


# ---- the mastery path -------------------------------------------------------------------------------------------------
def _date_words(iso):
    try:
        d = datetime.fromisoformat(str(iso).replace('Z', '+00:00'))
    except (TypeError, ValueError):
        return ''
    return f'{d.day} {d.strftime("%B")}'


def next_step(status):
    """The next step on a topic's path, in words, from a models.topic_status status dict (or None for an untouched topic)."""
    st = status or {}
    if not st.get('lesson_complete'):
        return NEXT['lesson_ninja'] if st.get('has_perfect') else NEXT['lesson']
    if not st.get('ninja'):
        return NEXT['ninja']
    if st.get('master_active'):
        when = _date_words(st.get('master_expires_at'))
        return NEXT['master_keep'].replace('{date}', when) if when else NEXT['master_again']
    if st.get('master_ever'):
        return NEXT['master_again']
    return NEXT['master_one'] if int(st.get('perfect_run') or 0) >= 1 else NEXT['master_two']


def path(conn, user_id, level, subject, topic):
    """{'steps': [{id, label, done}], 'next': sentence, 'bar': the quiz bar line once the lesson is done}."""
    statuses = topic_status_map(conn, user_id)
    st = dict(statuses.get((level, subject, topic)) or {})
    # has a 10/10 already (a ninja waits only for the lesson): one quick look at the rows the status was built from
    row = conn.execute(
        'SELECT 1 FROM quiz_attempts WHERE user_id = ? AND level = ? AND subject = ? AND topic = ? AND is_retry = 0 '
        'AND is_quicktest = 0 AND total >= 10 AND score >= total LIMIT 1', (user_id, level, subject, topic),
    ).fetchone()
    st['has_perfect'] = row is not None
    # a topic badge already earned counts on the path even when today's rule would not give it (badges are never taken back; a
    # ninja earned with a Quick Test before 2026-11-12 keeps its chip)
    held = {r['milestone_key'] for r in conn.execute(
        'SELECT milestone_key FROM user_milestones WHERE user_id = ? AND milestone_key IN (?, ?)',
        (user_id, f'topic_ninja:{level}:{subject}:{topic}', f'topic_master:{level}:{subject}:{topic}'),
    )}
    if f'topic_ninja:{level}:{subject}:{topic}' in held and st.get('lesson_complete'):
        st['ninja'] = True
    if f'topic_master:{level}:{subject}:{topic}' in held and st.get('ninja'):
        st['master_ever'] = True
    done = {'lesson': bool(st.get('lesson_complete')), 'ninja': bool(st.get('ninja')),
            'master': bool(st.get('master_active') or (st.get('ninja') and st.get('master_ever')))}
    after = dict(st, lesson_complete=True, ninja=bool(st.get('ninja') or st['has_perfect']))
    return {
        'label': LABELS['path'], 'done': LABELS['done'],
        'steps': [{'id': k, 'label': label, 'done': done[k]} for k, label in STEPS],
        'next': next_step(st),
        'bar': BAR_DONE + ' ' + next_step(after),
    }


# ---- today ------------------------------------------------------------------------------------------------------------
def questions_right(conn, user_id, start, end):
    """Questions answered right from `start` to `end` (dates, inclusive, UTC): practice (whole questions), lesson quizzes (not
    retries, not Quick Tests, whose scores are marks) and the daily question."""
    a, b = start.isoformat(), end.isoformat()
    n = conn.execute(
        'SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ? AND correct = 1 AND part_index IS NULL '
        'AND substr(created_at, 1, 10) BETWEEN ? AND ?', (user_id, a, b),
    ).fetchone()['n']
    n += conn.execute(
        'SELECT COALESCE(SUM(score), 0) AS n FROM quiz_attempts WHERE user_id = ? AND is_retry = 0 AND is_quicktest = 0 '
        'AND substr(created_at, 1, 10) BETWEEN ? AND ?', (user_id, a, b),
    ).fetchone()['n']
    n += conn.execute(
        'SELECT COUNT(*) AS n FROM qotd_attempts WHERE user_id = ? AND correct = 1 AND day_key BETWEEN ? AND ?',
        (user_id, a, b),
    ).fetchone()['n']
    return int(n or 0)


def today(conn, user_id, streak=None):
    """The Today card: questions right today, effort points today and the study streak (UTC days, as the streak counts them)."""
    day = _utc_today()
    streak = streak if streak is not None else get_study_streak(conn, user_id)
    right = questions_right(conn, user_id, day, day)
    xp = _effort_score_since(conn, user_id, day.strftime('%Y-%m-%d 00:00:00'))
    cur = int(streak.get('current') or 0)
    return {
        'title': LABELS['today'], 'right': right, 'xp': int(xp or 0), 'streak': cur,
        'right_label': LABELS['right_one'] if right == 1 else LABELS['right'].replace('{n}', str(right)),
        'xp_label': LABELS['xp'].replace('{n}', str(int(xp or 0))),
        'streak_label': LABELS['streak'].replace('{n}', str(cur)) if cur else LABELS['no_streak'],
    }


def level_bar(before_xp, after_xp, progress_fn):
    """The results strip's level bar: the fill before and after this quiz (from 0 when the quiz crossed into a new level)."""
    before, after = progress_fn(max(0, before_xp)), progress_fn(after_xp)
    start = before['pct'] if before['level'] == after['level'] else 0.0
    return {
        'level': after['level'], 'from': round(start, 3), 'to': round(after['pct'], 3), 'up': after['level'] > before['level'],
        'label': LABELS['level'].replace('{n}', str(after['level'])),
        'to_next': LABELS['to_next'].replace('{n}', str(after['remaining'])).replace('{next}', str(after['level'] + 1)),
    }


# ---- your week --------------------------------------------------------------------------------------------------------
def last_week(today_=None):
    """(monday, sunday, key) of the ISO week before the one `today_` is in. key is 'wk:<year>w<week>' (a guide reward flag)."""
    d = today_ or _utc_today()
    monday = d - timedelta(days=d.weekday()) - timedelta(days=7)
    year, week, _ = monday.isocalendar()
    return monday, monday + timedelta(days=6), f'wk:{year}w{week:02d}'


def _topic_name(level, subject, topic):
    cfg = ((TOPICS.get(level) or {}).get(subject) or {}).get(topic) or {}
    return str(cfg.get('name') or str(topic).replace('_', ' ').title())[:40]


def best_moment(conn, user_id, start, end):
    """The week's best moment: a badge (highest tier, then newest), else full marks on a lesson quiz, else the best lesson quiz,
    else the topic practised most. None when the week had none of these."""
    from models.gamification import badge_display
    a, b = start.isoformat(), end.isoformat()
    rows = conn.execute(
        'SELECT milestone_key, earned_at FROM user_milestones WHERE user_id = ? AND quiet = 0 '
        'AND substr(earned_at, 1, 10) BETWEEN ? AND ? ORDER BY earned_at DESC', (user_id, a, b),
    ).fetchall()
    if rows:
        best = min(rows, key=lambda r: TIER_RANK.get(badge_display(r['milestone_key'])['tier'], 3))
        info = badge_display(best['milestone_key'])
        return {'kind': 'badge', 'title': str(info['title'])[:48]}
    q = conn.execute(
        'SELECT level, subject, topic, score, total FROM quiz_attempts WHERE user_id = ? AND is_retry = 0 AND is_quicktest = 0 '
        'AND total > 0 AND substr(created_at, 1, 10) BETWEEN ? AND ? ORDER BY (score * 1.0 / total) DESC, total DESC, created_at DESC LIMIT 1',
        (user_id, a, b),
    ).fetchone()
    if q:
        name = _topic_name(q['level'], q['subject'], q['topic'])
        if q['score'] >= q['total'] and q['total'] >= 3:
            return {'kind': 'perfect', 'title': name}
        return {'kind': 'quiz', 'title': name, 'score': int(q['score']), 'total': int(q['total'])}
    t = conn.execute(
        'SELECT level, subject, topic, COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ? '
        'AND substr(created_at, 1, 10) BETWEEN ? AND ? GROUP BY level, subject, topic ORDER BY n DESC LIMIT 1', (user_id, a, b),
    ).fetchone()
    if t:
        return {'kind': 'topic', 'title': _topic_name(t['level'], t['subject'], t['topic'])}
    return None


def week_moment(conn, user_id, today_=None):
    """The Your week moment for last week, or None when last week had no study day. Its id is the week's guide flag."""
    monday, sunday, key = last_week(today_)
    days = {r['study_date'] for r in conn.execute(
        'SELECT study_date FROM user_study_days WHERE user_id = ? AND study_date BETWEEN ? AND ?',
        (user_id, monday.isoformat(), sunday.isoformat()),
    )}
    if not days:
        return None
    dots = ''.join('1' if (monday + timedelta(days=i)).isoformat() in days else '0' for i in range(7))
    m = {'type': 'week', 'id': key, 'days': len(days), 'dots': dots, 'count': questions_right(conn, user_id, monday, sunday)}
    best = best_moment(conn, user_id, monday, sunday)
    if best:
        m['best'] = best['kind']
        m['title'] = best['title']
        if best['kind'] == 'quiz':
            m['score'], m['total'] = best['score'], best['total']
    return m


# ---- close to a badge -------------------------------------------------------------------------------------------------
NEAR_MAX = 2   # "close" is one or two steps from the next badge


def near_moment(conn, user_id, day_key):
    """The Close to a badge card (plan 2.2): the Next up badge of the shelf when one or two steps are left, else None."""
    from models import badge_shelf
    nu = badge_shelf.build(conn, user_id)['next_up']
    if not nu or not nu.get('meter'):
        return None
    left = nu['meter']['need'] - nu['meter']['have']
    if not 1 <= left <= NEAR_MAX:
        return None
    return {'type': 'toast', 'id': f'near:{day_key}', 'kind': 'near_badge', 'title': str(nu['title'])[:48], 'line': nu['sentence']}

