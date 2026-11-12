"""E11 Phase 3 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 4.1): the Milestones shelf as rows by line.

Each line is a chain of badges in threshold order. A row shows the badges earned, then the next one with a progress meter
("3 of 5 quizzes"). The progress numbers come from the same records `evaluate_milestones` awards from, so a full meter means the
badge arrives with the next check. "Next up" is the line closest to its next badge by progress (a line that cannot move again
today, the streak or the daily question once done today, comes last). Subject lines show the pupil's own subjects (studied, or
chosen at welcome); the rest sit behind "Show all". Nothing here awards a badge.

The copy (row titles, meter units, the Next up sentences and link labels) is system voice and is linted by
scripts/test_zorp_voice_smoke.py through models/zorp_voice.py `extract_shelf_copy`.
"""
from datetime import datetime, timedelta, timezone

from models.gamification import (
    ACTIVITY_HINT_CORRECT,
    ACTIVITY_RETRY_CORRECT,
    MILESTONE_CATALOG,
    PERFECT_MIN_TOTAL,
    _PERFECT_QUIZ_WHERE,
    _distinct_topics_count,
    _in_a_class,
    _pose_from_meta,
    _questions_right_count,
    _set_work_done_count,
    _utc_today,
    badge_display,
    get_study_streak,
    list_user_milestones,
    milestone_meta,
)
from models.topic_status import subject_badge_key, subject_slugs_for_badges, topic_status_map

# ---- the lines --------------------------------------------------------------------------------------------------------
# (id, row title, badge keys in threshold order). Order on the shelf is this order.
LINES = (
    ('lessons', 'Lessons', ('first_lesson_step', 'topics_completed_5', 'topics_completed_10', 'topics_completed_20')),
    ('quizzes', 'Quizzes', ('first_quiz', 'quizzes_5', 'quizzes_25')),
    ('perfect', 'Full marks', ('perfect_1', 'perfect_5', 'perfect_20')),
    ('practice', 'Practice', ('questions_25', 'questions_50', 'questions_250')),
    ('bounce', 'Second tries', ('bounce_1', 'bounce_25')),
    ('hint', 'Hints', ('hint_1', 'hint_25')),
    ('retry', 'Retries', ('retry_fixed',)),
    ('streak', 'Streaks', ('streak_3', 'streak_7', 'streak_30', 'streak_100')),
    ('daily', 'Daily question', ('qotd_first', 'qotd_7', 'qotd_30')),
    ('explorer', 'Explorer', ('topics_3', 'topics_10', 'topics_25')),
    ('ninja', 'Topic ninjas', ('topics_ninja_5', 'topics_ninja_10', 'topics_ninja_20')),
    ('master', 'Topic masters', ('topics_master_5', 'topics_master_10', 'topics_master_20')),
    ('classwork', 'Class work', ('setwork_1', 'setwork_10')),
)
# Single badges with no count behind them; one row, no meter.
EXTRAS = ('extras', 'Extras', ('app_tour', 'accuracy_top_friend'))
SUBJECT_KINDS = ('completed', 'ninja', 'master')

# key -> (counter, need). A badge with no entry has no meter (Pathfinder, Sharp week).
NEED = {
    'first_lesson_step': ('lesson_steps', 1),
    'first_quiz': ('quiz_any', 1),
    'quizzes_5': ('quizzes', 5), 'quizzes_25': ('quizzes', 25),
    'perfect_1': ('perfect', 1), 'perfect_5': ('perfect', 5), 'perfect_20': ('perfect', 20),
    'questions_25': ('right', 25), 'questions_50': ('right', 100), 'questions_250': ('right', 250),
    'bounce_1': ('bounce', 1), 'bounce_25': ('bounce', 25),
    'hint_1': ('hint', 1), 'hint_25': ('hint', 25),
    'retry_fixed': ('fixed', 1),
    'streak_3': ('streak', 3), 'streak_7': ('streak', 7), 'streak_30': ('streak', 30), 'streak_100': ('streak', 100),
    'qotd_first': ('qotd', 1), 'qotd_7': ('qotd', 7), 'qotd_30': ('qotd', 30),
    'topics_3': ('topics', 3), 'topics_10': ('topics', 10), 'topics_25': ('topics', 25),
    'setwork_1': ('setwork', 1), 'setwork_10': ('setwork', 10),
}
for _kind, _counter in (('completed', 'lessons_done'), ('ninja', 'ninja'), ('master', 'master')):
    for _n in (5, 10, 20):
        NEED[f'topics_{_kind}_{_n}'] = (_counter, _n)

# BEGIN SHELF COPY (system voice; models/zorp_voice.py extract_shelf_copy reads this block)
# counter -> (meter unit, one more, n more, link). The meter reads "3 of 5 quizzes"; Next up reads the sentence.
COPY = {
    'lesson_steps': ('lesson steps', 'Finish a lesson step, such as a quick check.', 'Finish {n} more lesson steps.', 'lesson'),
    'lessons_done': ('lessons', 'Finish one more lesson.', 'Finish {n} more lessons.', 'lesson'),
    'ninja': ('topics at ninja', 'Reach ninja on one more topic.', 'Reach ninja on {n} more topics.', 'quiz'),
    'master': ('topics at master', 'Reach master on one more topic.', 'Reach master on {n} more topics.', 'quiz'),
    'quiz_any': ('quizzes', 'Finish a quiz.', 'Finish {n} more quizzes.', 'quiz'),
    'quizzes': ('quizzes', 'Finish one more quiz.', 'Finish {n} more quizzes.', 'quiz'),
    'perfect': ('quizzes with full marks', 'Get full marks on one more quiz.', 'Get full marks on {n} more quizzes.', 'quiz'),
    'fixed': ('retries', 'Retry the ones you missed on a quiz and get them all right.', '', 'quiz'),
    'right': ('questions right', 'Get one more question right.', 'Get {n} more questions right.', 'practice'),
    'bounce': ('right after a wrong try', 'Get one more right after a wrong try.', 'Get {n} more right after a wrong try.', 'practice'),
    'hint': ('right after the bigger hint', 'Get one more right after the bigger hint.', 'Get {n} more right after the bigger hint.', 'practice'),
    'streak': ('days in a row', 'Study one more day in a row.', 'Study {n} more days in a row.', 'study'),
    'qotd': ('days', 'Answer the daily question on one more day.', 'Answer the daily question on {n} more days.', 'daily'),
    'topics': ('topics', 'Practise one more topic.', 'Practise {n} more topics.', 'topics'),
    'setwork': ('pieces of set work', 'Finish one more piece of set work.', 'Finish {n} more pieces of set work.', 'classwork'),
}
LINKS = {
    'lesson': 'Open a lesson',
    'quiz': 'Take a quiz',
    'practice': 'Try a question',
    'study': 'Study today',
    'daily': "Today's question",
    'topics': 'Try a new topic',
    'classwork': 'Open class work',
    'tour': 'Take the tour',
}
UI = {
    'next_up': 'Next up',
    'all_done': 'All earned',
    'show_all': 'Show all subjects',
    'subjects': 'Your subjects',
    'topic_badges': 'Topic badges',
    'of': '{have} of {need} {unit}',
}
# END SHELF COPY

_WORDS = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten')
NEW_DAYS = 7   # E10 phase 7: a badge earned in the last 7 days wears the "New" ribbon


def number_word(n):
    return _WORDS[n] if 0 <= n < len(_WORDS) else str(n)


def sentence(counter, remaining):
    """The Next up sentence for `remaining` more of `counter` ("Finish two more quizzes.")."""
    _unit, one, many, _link = COPY[counter]
    if remaining <= 1 or not many:
        return one
    return many.replace('{n}', number_word(remaining))


# ---- counts -----------------------------------------------------------------------------------------------------------
def counts(conn, user_id, statuses=None):
    """Every counter the lines need, from the records evaluate_milestones awards from."""
    out = {}
    out['lesson_steps'] = conn.execute(
        "SELECT COUNT(*) AS n FROM lesson_progress WHERE user_id = ? AND completed_keys_json IS NOT NULL AND completed_keys_json != '[]'",
        (user_id,),
    ).fetchone()['n']
    q = conn.execute(
        f'''SELECT COUNT(*) AS n, SUM(CASE WHEN is_retry = 0 THEN 1 ELSE 0 END) AS finished,
                   SUM(CASE WHEN {_PERFECT_QUIZ_WHERE} THEN 1 ELSE 0 END) AS perfect,
                   SUM(CASE WHEN is_retry = 1 AND total >= 1 AND score >= total THEN 1 ELSE 0 END) AS fixed
            FROM quiz_attempts WHERE user_id = ?''',
        (PERFECT_MIN_TOTAL, user_id),
    ).fetchone()
    out['quiz_any'] = int(q['n'] or 0)
    out['quizzes'], out['perfect'], out['fixed'] = int(q['finished'] or 0), int(q['perfect'] or 0), int(q['fixed'] or 0)
    out['right'] = _questions_right_count(conn, user_id)
    rec = conn.execute(
        'SELECT SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) AS bounce, SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) AS hint '
        'FROM user_activity_events WHERE user_id = ? AND event_type IN (?, ?)',
        (ACTIVITY_RETRY_CORRECT, ACTIVITY_HINT_CORRECT, user_id, ACTIVITY_RETRY_CORRECT, ACTIVITY_HINT_CORRECT),
    ).fetchone()
    out['bounce'], out['hint'] = int(rec['bounce'] or 0), int(rec['hint'] or 0)
    # a streak badge is earned when the run reaches the count, so progress is the run going now (the longest run is history)
    out['streak'] = int(get_study_streak(conn, user_id)['current'] or 0)
    out['qotd'] = conn.execute('SELECT COUNT(DISTINCT day_key) AS n FROM qotd_attempts WHERE user_id = ?', (user_id,)).fetchone()['n']
    out['topics'] = _distinct_topics_count(conn, user_id)
    out['setwork'] = _set_work_done_count(conn, user_id)
    statuses = topic_status_map(conn, user_id) if statuses is None else statuses
    out['lessons_done'] = sum(1 for s in statuses.values() if s.get('lesson_complete'))
    out['ninja'] = sum(1 for s in statuses.values() if s.get('ninja'))
    out['master'] = sum(1 for s in statuses.values() if s.get('master_ever'))
    return out


def blocked_today(conn, user_id):
    """Counters that cannot move again today: the streak once studied today, the daily question once answered today."""
    from models.qotd import current_day_key
    out = set()
    today = _utc_today().isoformat()
    if conn.execute('SELECT 1 FROM user_study_days WHERE user_id = ? AND study_date = ?', (user_id, today)).fetchone():
        out.add('streak')
    if conn.execute('SELECT 1 FROM qotd_attempts WHERE user_id = ? AND day_key = ?', (user_id, current_day_key())).fetchone():
        out.add('qotd')
    return out


def studied_subjects(conn, user_id):
    """(level, subject) pairs the pupil has lesson, quiz or practice records in."""
    pairs = set()
    for table in ('lesson_progress', 'quiz_attempts', 'generator_mcq_attempts'):
        for row in conn.execute(f'SELECT DISTINCT level, subject FROM {table} WHERE user_id = ?', (user_id,)):
            if row['level'] and row['subject']:
                pairs.add((row['level'], row['subject']))
    return pairs


# ---- the shelf --------------------------------------------------------------------------------------------------------
def _item(key, earned_row, cutoff):
    meta = milestone_meta(key)
    info = badge_display(key, earned_row['earned_at'] if earned_row else None)
    earned = earned_row is not None
    return {
        'key': key, 'title': info['title'], 'blurb': info['blurb'], 'how': info['how'], 'family': info['family'],
        'emoji': info['emoji'], 'tier': info['tier'], 'next_title': info['next_title'], 'next_how': info['next_how'],
        'pose': _pose_from_meta(meta), 'earned': earned, 'earned_at': info['earned_at'],
        'is_new': bool(earned and (info['earned_at'] or '') >= cutoff),
    }


def _row(line_id, title, keys, earned, cutoff, have):
    """earned badges in threshold order, then the next one with its meter. `have` is counter -> count."""
    got = [_item(k, earned[k], cutoff) for k in keys if k in earned]
    nxt_key = next((k for k in keys if k not in earned), None)
    row = {'id': line_id, 'title': title, 'badges': got, 'next': None, 'meter': None, 'done': nxt_key is None,
           'remaining': None, 'sentence': '', 'link': '', 'counter': ''}
    if nxt_key is None:
        return row
    row['next'] = _item(nxt_key, None, cutoff)
    rule = NEED.get(nxt_key)
    if rule:
        counter, need = rule
        n = min(int(have.get(counter, 0) or 0), need)
        row.update(counter=counter, remaining=need - n, link=COPY[counter][3], sentence=sentence(counter, need - n))
        if need > 1:
            row['meter'] = {'have': n, 'need': need, 'label': UI['of'].format(have=n, need=need, unit=COPY[counter][0])}
    elif nxt_key == 'app_tour':
        row.update(link='tour', sentence=row['next']['how'])
    return row


def _subject_rows(statuses, earned, cutoff):
    """One row per (level, subject) with lessons: complete, ninja, master; the topic badges earned in it ride along."""
    rows = []
    for level, subject, slugs in subject_slugs_for_badges():
        total = len(slugs)
        done = {'completed': 0, 'ninja': 0, 'master': 0}
        for slug in slugs:
            st = statuses.get((level, subject, slug)) or {}
            done['completed'] += bool(st.get('lesson_complete'))
            done['ninja'] += bool(st.get('ninja'))
            done['master'] += bool(st.get('master_ever'))
        keys = [subject_badge_key(k, level, subject) for k in SUBJECT_KINDS]
        title = milestone_meta(keys[0]).get('title', '').replace(' complete', '')
        row = _row(f'subject:{level}:{subject}', title, keys, earned, cutoff, {})
        nxt = row['next']
        if nxt:
            kind = nxt['key'].split(':')[0].replace('subject_', '')
            counter = {'completed': 'lessons_done', 'ninja': 'ninja', 'master': 'master'}[kind]
            n = min(done[kind], total)
            row.update(counter=counter, remaining=total - n, link=COPY[counter][3], sentence=sentence(counter, total - n),
                       meter={'have': n, 'need': total, 'label': UI['of'].format(have=n, need=total, unit=COPY[counter][0])})
        row['topic_badges'] = [_item(k, earned[k], cutoff) for k in earned
                               if k.startswith(('topic_completed:', 'topic_ninja:', 'topic_master:')) and k.split(':')[1:3] == [level, subject]]
        row['level'], row['subject'] = level, subject
        rows.append(row)
    return rows


def build(conn, user_id, own=(), now=None):
    """The whole shelf. `own` is the (level, subject) pairs chosen at welcome; studied ones are added here."""
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=NEW_DAYS)).replace(microsecond=0).isoformat()
    earned = {row['key']: row for row in list_user_milestones(conn, user_id)}
    statuses = topic_status_map(conn, user_id)
    have = counts(conn, user_id, statuses)
    in_class = _in_a_class(conn, user_id)

    lines = []
    for line_id, title, keys in LINES:
        if line_id == 'classwork' and not in_class and not any(k in earned for k in keys):
            continue   # E11 Phase 2: set work is for pupils in a class (an earned one always shows)
        lines.append(_row(line_id, title, keys, earned, cutoff, have))
    extras = _row(*EXTRAS, earned, cutoff, have)
    extras['locked'] = [_item(k, None, cutoff) for k in EXTRAS[2] if k not in earned]

    mine = set(own) | studied_subjects(conn, user_id)
    subjects, others = [], []
    for row in _subject_rows(statuses, earned, cutoff):
        pair = (row['level'], row['subject'])
        (subjects if pair in mine or row['badges'] or row['topic_badges'] else others).append(row)

    blocked = blocked_today(conn, user_id)
    next_up = pick_next_up(lines + subjects + [extras], blocked)

    # the sheet opens any badge by key (a row, Next up, or a wardrobe "Earn ... to unlock" link): only what it shows
    sheet = {}
    for key in list(MILESTONE_CATALOG) + [k for k in earned if k not in MILESTONE_CATALOG]:
        it = _item(key, earned.get(key), cutoff)
        sheet[key] = {f: it[f] for f in ('title', 'blurb', 'how', 'family', 'emoji', 'tier', 'next_title', 'next_how', 'earned')}
        sheet[key]['date'] = (it['earned_at'] or '')[:10]
    return {
        'lines': lines, 'extras': extras, 'subjects': subjects, 'other_subjects': others, 'next_up': next_up,
        'earned_count': len(earned), 'earned_keys': list(earned), 'sheet': sheet, 'ui': UI, 'link_labels': LINKS,
    }


def pick_next_up(rows, blocked=frozenset()):
    """The row closest to its next badge: the largest share done, then the fewest to go, then the shelf order. Rows whose
    counter cannot move again today come after the rest. A row whose meter is already full is skipped (the badge arrives
    with the next check). None when nothing is left."""
    best = None
    for order, row in enumerate(rows):
        if not row.get('next') or row.get('remaining') is None and row.get('link') != 'tour':
            continue
        remaining = row['remaining'] if row.get('remaining') is not None else 1
        if remaining <= 0:
            continue
        need = (row['meter'] or {}).get('need') or remaining
        share = 1 - remaining / need if need else 0
        key = (row.get('counter') in blocked, -share, remaining, order)
        if best is None or key < best[0]:
            best = (key, row)
    if not best:
        return None
    row = best[1]
    link = '' if row.get('counter') in blocked else row['link']   # done for today: no "Study today" once studied
    return {'key': row['next']['key'], 'title': row['next']['title'], 'item': row['next'], 'sentence': row['sentence'],
            'meter': row['meter'], 'link': link, 'line': row['id']}
