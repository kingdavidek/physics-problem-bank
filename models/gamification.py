"""Study streaks, milestones, weekly recap, and friend effort/accuracy leaderboards."""
from datetime import date, datetime, timedelta, timezone
import sqlite3

from models.avatar import attach_avatars
from models.social import (
    ACTIVITY_HINT_CORRECT,
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_RETRY_CORRECT,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_SET_WORK_ANSWERED,
    ACTIVITY_TOPIC_OPENED,
)
from models.notifications import NOTIFICATION_MILESTONE, create_notification
from models.user import utc_now_iso
from models.topic_status import (
    catalog_extra_entries,
    evaluate_topic_milestones,
    topic_badge_meta,
    topic_status_map as load_topic_status_map,
)
from models.zorp_kit import POSE_TOKENS as ZORP_POSE_TOKENS


def _utc_today():
    return datetime.now(timezone.utc).date()

MILESTONE_FIRST_QUIZ = 'first_quiz'
MILESTONE_FIRST_LESSON = 'first_lesson_step'
MILESTONE_TOPICS_10 = 'topics_10'
MILESTONE_STREAK_7 = 'streak_7'
MILESTONE_STREAK_30 = 'streak_30'
MILESTONE_QUESTIONS_25 = 'questions_25'
MILESTONE_QOTD_FIRST = 'qotd_first'
MILESTONE_QOTD_7 = 'qotd_7'
MILESTONE_QUESTIONS_50 = 'questions_50'
MILESTONE_ACCURACY_TOP_FRIEND = 'accuracy_top_friend'
# E10 phase 6: finishing Zorp's tour of the site (the "Explorer" badge of the plan, section 10 answer 10). The existing badge
# topics_10 is already titled "Broad explorer" and uses the `explorer` family (a map with pins), so this one has its own title
# (Pathfinder), its own family (`tour`: a signpost, Zorp bows) and its own key. It is never computed from activity: the
# server awards it once, from POST /api/v1/me/tour/complete, after the tour has been finished (see app.py).
MILESTONE_TOUR = 'app_tour'
# E11 Phase 1 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 2.1 and 3): the first 10/10 ever on a lesson quiz. The same quizzes that
# earn the full-screen perfect moment count (not a retry run, at least PERFECT_MIN_TOTAL questions, every answer right), and
# this badge's stage then replaces that moment. Family `accuracy` for now (the target): a family of its own needs a wardrobe
# item, and every look the live Zorp can draw is already in the wardrobe (plan section 9).
MILESTONE_PERFECT_1 = 'perfect_1'
PERFECT_MIN_TOTAL = 3
# E11 Phase 2 (plan section 3, David's answer 2: all of them). Each line has a next step so "Next up" always points somewhere.
MILESTONE_QUIZZES_5 = 'quizzes_5'
MILESTONE_QUIZZES_25 = 'quizzes_25'
MILESTONE_PERFECT_5 = 'perfect_5'
MILESTONE_PERFECT_20 = 'perfect_20'
MILESTONE_BOUNCE_1 = 'bounce_1'
MILESTONE_BOUNCE_25 = 'bounce_25'
MILESTONE_HINT_1 = 'hint_1'
MILESTONE_HINT_25 = 'hint_25'
MILESTONE_RETRY_FIXED = 'retry_fixed'
MILESTONE_QUESTIONS_250 = 'questions_250'
MILESTONE_STREAK_3 = 'streak_3'
MILESTONE_STREAK_100 = 'streak_100'
MILESTONE_QOTD_30 = 'qotd_30'
MILESTONE_TOPICS_3 = 'topics_3'
MILESTONE_TOPICS_25 = 'topics_25'
MILESTONE_SETWORK_1 = 'setwork_1'
MILESTONE_SETWORK_10 = 'setwork_10'
# Practice regular and Practice veteran count questions answered right since E11 Phase 2 (David's answer 4; before, questions
# started). The keys stay questions_25 and questions_50 so pupils who hold them keep them; questions_50 now needs 100 right answers.
QUESTIONS_RIGHT_THRESHOLDS = ((MILESTONE_QUESTIONS_25, 25), (MILESTONE_QUESTIONS_50, 100), (MILESTONE_QUESTIONS_250, 250))

# E10 phase 4 (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md B3, section 10): every badge carries
#   blurb  what you did, past tense and specific (shown once earned and on the badge stage)
#   how    how to earn it (shown while locked)
#   next   the key of the next badge in the same line, if there is one
#   family which choreography the badge stage plays (BADGE_FAMILIES)
# `description` stays as the older "how" wording for API consumers. The copy is Zorp's voice (docs/ZORP_CHARM.md 3.3:
# reward lines of 80 characters at most, plain English, British spelling); scripts/test_zorp_voice_smoke.py reads it.
BADGE_FAMILIES = (
    'streak', 'daily', 'practice', 'explorer', 'learning',
    'topic_completed', 'topic_ninja', 'topic_master', 'subject', 'accuracy', 'tour',
    'perfect', 'growth',   # E11 Phase 2: the Perfect line (Full marks, Bullseye, Flawless) and the Recovery line
)

MILESTONE_CATALOG = {
    MILESTONE_FIRST_QUIZ: {
        'title': 'First quiz',
        'description': 'Finish a quiz',
        'blurb': 'You finished your first quiz.',
        'how': 'Finish a quiz.',
        'next': MILESTONE_QUIZZES_5,
        'family': 'learning',
        'emoji': '📝',
        'tier': 'bronze',
    },
    MILESTONE_PERFECT_1: {
        'title': 'Full marks',
        'description': 'Get every answer right on a lesson quiz',
        'blurb': 'You got every answer right on a quiz.',
        'how': 'Get every answer right on a lesson quiz.',
        'next': MILESTONE_PERFECT_5,
        'family': 'perfect',
        'emoji': '💯',
        'tier': 'bronze',
    },
    MILESTONE_FIRST_LESSON: {
        'title': 'Lesson learner',
        'description': 'Complete a lesson quick check',
        'blurb': 'You finished your first lesson step.',
        'how': 'Finish a lesson step, such as a quick check.',
        'next': 'topics_completed_5',
        'family': 'learning',
        'emoji': '📖',
        'tier': 'bronze',
        'pose': 'scholar',
    },
    MILESTONE_TOPICS_10: {
        'title': 'Broad explorer',
        'description': 'Practise 10 different topics',
        'blurb': 'You practised 10 different topics.',
        'how': 'Practise 10 different topics.',
        'next': MILESTONE_TOPICS_25,
        'family': 'explorer',
        'emoji': '🧭',
        'tier': 'silver',
    },
    MILESTONE_TOUR: {
        'title': 'Pathfinder',
        'description': 'Take Zorp’s tour of the site',
        'blurb': 'You took the tour and found your way around.',
        'how': 'Take Zorp’s tour of the site. You can replay it from Settings.',
        'next': None,
        'family': 'tour',
        'emoji': '🚩',
        'tier': 'bronze',
    },
    MILESTONE_STREAK_7: {
        'title': 'Week warrior',
        'description': 'Reach a 7-day study streak',
        'blurb': 'You studied on 7 days in a row.',
        'how': 'Study on 7 days in a row.',
        'next': MILESTONE_STREAK_30,
        'family': 'streak',
        'emoji': '🔥',
        'tier': 'gold',
        'pose': 'jump',
    },
    MILESTONE_STREAK_30: {
        'title': 'Dedicated',
        'description': 'Reach a 30-day study streak',
        'blurb': 'You studied on 30 days in a row.',
        'how': 'Study on 30 days in a row.',
        'next': MILESTONE_STREAK_100,
        'family': 'streak',
        'emoji': '💪',
        'tier': 'gold',
    },
    MILESTONE_QUESTIONS_25: {
        'title': 'Practice regular',
        'description': 'Get 25 practice questions right',
        'blurb': 'You got 25 practice questions right.',
        'how': 'Get 25 practice questions right.',
        'next': MILESTONE_QUESTIONS_50,
        'family': 'practice',
        'emoji': '✏️',
        'tier': 'silver',
    },
    MILESTONE_QOTD_FIRST: {
        'title': 'Daily starter',
        'description': 'Answer the question of the day',
        'blurb': 'You answered the question of the day.',
        'how': 'Answer the question of the day.',
        'next': MILESTONE_QOTD_7,
        'family': 'daily',
        'emoji': '☀️',
        'tier': 'bronze',
        'pose': 'wave',
    },
    MILESTONE_QOTD_7: {
        'title': 'Seven days of questions',
        'description': 'Answer the question of the day on 7 different days',
        'blurb': 'You answered the question of the day on 7 different days.',
        'how': 'Answer the question of the day on 7 different days.',
        'next': MILESTONE_QOTD_30,
        'family': 'daily',
        'emoji': '📅',
        'tier': 'silver',
    },
    MILESTONE_QUESTIONS_50: {
        'title': 'Practice veteran',
        'description': 'Get 100 practice questions right',
        'blurb': 'You got 100 practice questions right.',
        'how': 'Get 100 practice questions right.',
        'next': MILESTONE_QUESTIONS_250,
        'family': 'practice',
        'emoji': '🏅',
        'tier': 'gold',
    },
    # Renamed from "Top of the class" (owner's answer 9, 2026-11-08). The id is kept: stored rows use it. The award rule is
    # unchanged (rank 1 on the friends' weekly accuracy board); the words celebrate the pupil's own accuracy and the `how`
    # states the rule plainly. Nothing Zorp says about it compares.
    MILESTONE_ACCURACY_TOP_FRIEND: {
        'title': 'Sharp week',
        'description': 'Highest quiz accuracy among your friends in a week',
        'blurb': 'Your quiz answers were very accurate this week.',
        'how': 'Have the highest quiz accuracy of your friends in a week (10 answers or more).',
        'next': None,
        'family': 'accuracy',
        'emoji': '🎯',
        'tier': 'violet',
    },
    # ---- E11 Phase 2 (docs/BADGES_AND_CELEBRATIONS_PLAN.md section 3) ----
    MILESTONE_QUIZZES_5: {
        'title': 'Quiz fan',
        'description': 'Finish 5 quizzes',
        'blurb': 'You finished 5 quizzes.',
        'how': 'Finish 5 quizzes.',
        'next': MILESTONE_QUIZZES_25,
        'family': 'learning',
        'emoji': '📋',
        'tier': 'silver',
    },
    MILESTONE_QUIZZES_25: {
        'title': 'Quiz veteran',
        'description': 'Finish 25 quizzes',
        'blurb': 'You finished 25 quizzes.',
        'how': 'Finish 25 quizzes.',
        'next': None,
        'family': 'learning',
        'emoji': '🗂️',
        'tier': 'gold',
    },
    MILESTONE_PERFECT_5: {
        'title': 'Bullseye',
        'description': 'Get every answer right on 5 lesson quizzes',
        'blurb': 'You got every answer right on 5 quizzes.',
        'how': 'Get every answer right on 5 lesson quizzes.',
        'next': MILESTONE_PERFECT_20,
        'family': 'perfect',
        'emoji': '🌟',
        'tier': 'silver',
    },
    MILESTONE_PERFECT_20: {
        'title': 'Flawless',
        'description': 'Get every answer right on 20 lesson quizzes',
        'blurb': 'You got every answer right on 20 quizzes.',
        'how': 'Get every answer right on 20 lesson quizzes.',
        'next': None,
        'family': 'perfect',
        'emoji': '💎',
        'tier': 'gold',
    },
    MILESTONE_BOUNCE_1: {
        'title': 'Bounce back',
        'description': 'Get a question right on a second try',
        'blurb': 'You got a question right on your second try.',
        'how': 'Get a practice question right after a wrong try.',
        'next': MILESTONE_BOUNCE_25,
        'family': 'growth',
        'emoji': '🌱',
        'tier': 'bronze',
    },
    MILESTONE_BOUNCE_25: {
        'title': 'Keeps going',
        'description': 'Get 25 questions right after a wrong try',
        'blurb': 'You got 25 questions right after a wrong try.',
        'how': 'Get 25 practice questions right after a wrong try.',
        'next': None,
        'family': 'growth',
        'emoji': '🌿',
        'tier': 'silver',
    },
    MILESTONE_HINT_1: {
        'title': 'Learned from a hint',
        'description': 'Open the bigger hint, then get the question right',
        'blurb': 'You opened the bigger hint and then got it right.',
        'how': 'Open the bigger hint on a question, then get it right.',
        'next': MILESTONE_HINT_25,
        'family': 'growth',
        'emoji': '💡',
        'tier': 'bronze',
    },
    MILESTONE_HINT_25: {
        'title': 'Hint hero',
        'description': 'Use the bigger hint and get it right 25 times',
        'blurb': 'You used the bigger hint and got it right 25 times.',
        'how': 'Use the bigger hint and get the question right 25 times.',
        'next': None,
        'family': 'growth',
        'emoji': '🔦',
        'tier': 'silver',
    },
    MILESTONE_RETRY_FIXED: {
        'title': 'All fixed',
        'description': 'Retry the questions you missed and get them all right',
        'blurb': 'You fixed every question you missed on a quiz.',
        'how': 'Retry the ones you missed on a quiz and get them all right.',
        'next': None,
        'family': 'growth',
        'emoji': '🛠️',
        'tier': 'bronze',
    },
    MILESTONE_QUESTIONS_250: {
        'title': 'Problem solver',
        'description': 'Get 250 practice questions right',
        'blurb': 'You got 250 practice questions right.',
        'how': 'Get 250 practice questions right.',
        'next': None,
        'family': 'practice',
        'emoji': '🧩',
        'tier': 'gold',
    },
    MILESTONE_STREAK_3: {
        'title': 'Three in a row',
        'description': 'Study on 3 days in a row',
        'blurb': 'You studied on 3 days in a row.',
        'how': 'Study on 3 days in a row.',
        'next': MILESTONE_STREAK_7,
        'family': 'streak',
        'emoji': '🕯️',
        'tier': 'bronze',
    },
    MILESTONE_STREAK_100: {
        'title': 'Century',
        'description': 'Study on 100 days in a row',
        'blurb': 'You studied on 100 days in a row.',
        'how': 'Study on 100 days in a row.',
        'next': None,
        'family': 'streak',
        'emoji': '🏆',
        'tier': 'violet',
    },
    MILESTONE_QOTD_30: {
        'title': 'Daily devotee',
        'description': 'Answer the question of the day on 30 different days',
        'blurb': 'You answered the question of the day on 30 different days.',
        'how': 'Answer the question of the day on 30 different days.',
        'next': None,
        'family': 'daily',
        'emoji': '🗓️',
        'tier': 'gold',
    },
    MILESTONE_TOPICS_3: {
        'title': 'Curious',
        'description': 'Practise 3 different topics',
        'blurb': 'You practised 3 different topics.',
        'how': 'Practise 3 different topics.',
        'next': MILESTONE_TOPICS_10,
        'family': 'explorer',
        'emoji': '🔎',
        'tier': 'bronze',
    },
    MILESTONE_TOPICS_25: {
        'title': 'Globetrotter',
        'description': 'Practise 25 different topics',
        'blurb': 'You practised 25 different topics.',
        'how': 'Practise 25 different topics.',
        'next': None,
        'family': 'explorer',
        'emoji': '🌍',
        'tier': 'gold',
    },
    MILESTONE_SETWORK_1: {
        'title': 'Set work done',
        'description': 'Finish a piece of set work from your class',
        'blurb': 'You finished a piece of set work.',
        'how': 'Finish a piece of set work from your class.',
        'next': MILESTONE_SETWORK_10,
        'family': 'learning',
        'emoji': '📬',
        'tier': 'bronze',
        'class_only': True,
    },
    MILESTONE_SETWORK_10: {
        'title': 'Ten tasks done',
        'description': 'Finish 10 pieces of set work',
        'blurb': 'You finished 10 pieces of set work.',
        'how': 'Finish 10 pieces of set work from your class.',
        'next': None,
        'family': 'learning',
        'emoji': '📦',
        'tier': 'silver',
        'class_only': True,
    },
}

MILESTONE_CATALOG.update(catalog_extra_entries())

EFFORT_EVENT_TYPES = (
    ACTIVITY_TOPIC_OPENED,
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_SET_WORK_ANSWERED,
)

EFFORT_WEIGHTS = {
    ACTIVITY_TOPIC_OPENED: 1,
    ACTIVITY_QUESTION_GENERATED: 1,
    ACTIVITY_QUIZ_COMPLETED: 3,
    ACTIVITY_LESSON_STEP_COMPLETED: 2,
    ACTIVITY_SET_WORK_ANSWERED: 1,   # E10 phase 4: one point per set-work question answered for the first time
}


def _iso_week_key(day):
    year, week, _ = day.isocalendar()
    return f'{year}-W{week:02d}'


def _grant_weekly_freeze(conn, user_id, today):
    week_key = _iso_week_key(today)
    row = conn.execute(
        '''
        SELECT freeze_available, freeze_week_key
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    if not row:
        return
    if row['freeze_week_key'] != week_key:
        conn.execute(
            '''
            UPDATE user_streaks
            SET freeze_available = 1, freeze_week_key = ?
            WHERE user_id = ?
            ''',
            (week_key, user_id),
        )


def _freeze_covers(conn, user_id, freeze_date):
    row = conn.execute(
        '''
        SELECT 1 FROM user_streak_freezes
        WHERE user_id = ? AND freeze_date = ?
        LIMIT 1
        ''',
        (user_id, freeze_date),
    ).fetchone()
    return row is not None


def _consume_freeze(conn, user_id, freeze_date):
    conn.execute(
        '''
        INSERT INTO user_streak_freezes (user_id, freeze_date, used_at)
        VALUES (?, ?, ?)
        ''',
        (user_id, freeze_date, utc_now_iso()),
    )
    conn.execute(
        '''
        UPDATE user_streaks
        SET freeze_available = 0
        WHERE user_id = ?
        ''',
        (user_id,),
    )


def _freeze_used_dates(conn, user_id, *, as_of=None):
    today = as_of or _utc_today()
    since = (today - timedelta(days=6)).isoformat()
    rows = conn.execute(
        '''
        SELECT freeze_date
        FROM user_streak_freezes
        WHERE user_id = ? AND freeze_date >= ?
        ORDER BY freeze_date ASC
        ''',
        (user_id, since),
    ).fetchall()
    return [row['freeze_date'] for row in rows]


def _streak_row(conn, user_id):
    return conn.execute(
        '''
        SELECT current_streak, longest_streak, last_active_date,
               freeze_available, freeze_week_key
        FROM user_streaks
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()


def ensure_user_streak(conn, user_id, on_date=None):
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_streaks (
            user_id, current_streak, longest_streak, last_active_date,
            freeze_available, freeze_week_key
        )
        VALUES (?, 0, 0, NULL, 1, NULL)
        ''',
        (user_id,),
    )
    _grant_weekly_freeze(conn, user_id, on_date or _utc_today())


def record_study_day(conn, user_id, on_date=None):
    """Mark a calendar day as active and update streak counters."""
    today = on_date or _utc_today()
    ensure_user_streak(conn, user_id, on_date=today)
    day = today.isoformat()
    _grant_weekly_freeze(conn, user_id, today)
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_study_days (user_id, study_date)
        VALUES (?, ?)
        ''',
        (user_id, day),
    )

    row = _streak_row(conn, user_id)
    last_active = row['last_active_date']
    current = row['current_streak'] or 0
    longest = row['longest_streak'] or 0
    freeze_available = int(row['freeze_available'] or 0)

    if last_active == day:
        conn.commit()
        return get_study_streak(conn, user_id, as_of=today)

    if last_active:
        previous = date.fromisoformat(last_active)
        gap_days = (today - previous).days
        if gap_days == 1:
            current += 1
        elif gap_days == 2 and freeze_available:
            missed_day = (previous + timedelta(days=1)).isoformat()
            _consume_freeze(conn, user_id, missed_day)
            current += 1
        else:
            current = 1
    else:
        current = 1

    longest = max(longest, current)
    conn.execute(
        '''
        UPDATE user_streaks
        SET current_streak = ?, longest_streak = ?, last_active_date = ?
        WHERE user_id = ?
        ''',
        (current, longest, day, user_id),
    )
    conn.commit()
    return get_study_streak(conn, user_id, as_of=today)


def get_study_streak(conn, user_id, as_of=None):
    today = as_of or _utc_today()
    ensure_user_streak(conn, user_id, on_date=today)
    _grant_weekly_freeze(conn, user_id, today)
    row = _streak_row(conn, user_id)
    if not row:
        return {
            'current': 0,
            'longest': 0,
            'last_active_date': None,
            'freeze_available': 1,
            'freeze_used_dates': [],
        }

    current = row['current_streak'] or 0
    last_active = row['last_active_date']
    freeze_available = int(row['freeze_available'] or 0)
    if last_active:
        last_day = date.fromisoformat(last_active)
        gap_days = (today - last_day).days
        if gap_days > 1:
            missed_days = gap_days - 1
            if missed_days == 1:
                missed_day = (last_day + timedelta(days=1)).isoformat()
                if not _freeze_covers(conn, user_id, missed_day) and not freeze_available:
                    current = 0
            else:
                current = 0

    return {
        'current': current,
        'longest': row['longest_streak'] or 0,
        'last_active_date': last_active,
        'freeze_available': freeze_available,
        'freeze_used_dates': _freeze_used_dates(conn, user_id, as_of=today),
    }


def _has_milestone(conn, user_id, milestone_key):
    row = conn.execute(
        '''
        SELECT 1 FROM user_milestones
        WHERE user_id = ? AND milestone_key = ?
        ''',
        (user_id, milestone_key),
    ).fetchone()
    return row is not None


def _award_milestone(conn, user_id, milestone_key):
    if _has_milestone(conn, user_id, milestone_key):
        return False
    conn.execute(
        '''
        INSERT INTO user_milestones (user_id, milestone_key, earned_at)
        VALUES (?, ?, ?)
        ''',
        (user_id, milestone_key, utc_now_iso()),
    )
    return True


_PERFECT_QUIZ_WHERE = 'is_retry = 0 AND total >= ? AND score >= total'
_QUESTIONS_RIGHT_WHERE = 'correct = 1 AND part_index IS NULL'   # E11 Phase 2: a whole practice question right


def _has_perfect_quiz(conn, user_id):
    row = conn.execute(
        f'SELECT 1 FROM quiz_attempts WHERE user_id = ? AND {_PERFECT_QUIZ_WHERE} LIMIT 1',
        (user_id, PERFECT_MIN_TOTAL),
    ).fetchone()
    return row is not None


# E11 Phase 1 (plan 2.4 rule 6, David's answer 3): a new badge that pupils may already have earned is awarded quietly from their
# history, once, by a migration (init_db): no stage, no notification. The row is marked quiet = 1; the next page the pupil looks
# at carries one corner card ("You already earned ...") and marks it quiet = 2. Phase 2 adds its badges to this table.
# Each entry: SQL that returns (user_id, at) for every pupil who earned the badge, and its parameters.
BACKFILL_RULES = {
    MILESTONE_PERFECT_1: (
        f'SELECT user_id, MIN(created_at) AS at FROM quiz_attempts WHERE {_PERFECT_QUIZ_WHERE} GROUP BY user_id',
        (PERFECT_MIN_TOTAL,),
    ),
}

# E11 Phase 2: the new badges that history already earns (the Recovery line's two events are new, so those four start from zero).
# `at` is the latest qualifying record: on or after the day the badge was really reached.
def _count_rule(table, where, need, *, user_col='user_id', at_col='created_at', params=()):
    return (f'SELECT {user_col} AS user_id, MAX({at_col}) AS at FROM {table} WHERE {where} GROUP BY {user_col} HAVING COUNT(*) >= ?',
            tuple(params) + (need,))


BACKFILL_RULES.update({
    MILESTONE_QUIZZES_5: _count_rule('quiz_attempts', 'is_retry = 0', 5),
    MILESTONE_QUIZZES_25: _count_rule('quiz_attempts', 'is_retry = 0', 25),
    MILESTONE_PERFECT_5: _count_rule('quiz_attempts', _PERFECT_QUIZ_WHERE, 5, params=(PERFECT_MIN_TOTAL,)),
    MILESTONE_PERFECT_20: _count_rule('quiz_attempts', _PERFECT_QUIZ_WHERE, 20, params=(PERFECT_MIN_TOTAL,)),
    MILESTONE_RETRY_FIXED: _count_rule('quiz_attempts', 'is_retry = 1 AND total >= 1 AND score >= total', 1),
    MILESTONE_QUESTIONS_25: _count_rule('generator_mcq_attempts', _QUESTIONS_RIGHT_WHERE, 25),
    MILESTONE_QUESTIONS_50: _count_rule('generator_mcq_attempts', _QUESTIONS_RIGHT_WHERE, 100),
    MILESTONE_QUESTIONS_250: _count_rule('generator_mcq_attempts', _QUESTIONS_RIGHT_WHERE, 250),
    MILESTONE_STREAK_3: ('SELECT user_id, last_active_date AS at FROM user_streaks WHERE longest_streak >= ?', (3,)),
    MILESTONE_STREAK_100: ('SELECT user_id, last_active_date AS at FROM user_streaks WHERE longest_streak >= ?', (100,)),
    MILESTONE_QOTD_30: ('SELECT user_id, MAX(answered_at) AS at FROM qotd_attempts GROUP BY user_id HAVING COUNT(DISTINCT day_key) >= ?',
                        (30,)),
    MILESTONE_SETWORK_1: _count_rule('class_assignment_recipients', "status = 'complete'", 1, user_col='student_id', at_col='completed_at'),
    MILESTONE_SETWORK_10: _count_rule('class_assignment_recipients', "status = 'complete'", 10, user_col='student_id', at_col='completed_at'),
})
for _key, _need in ((MILESTONE_TOPICS_3, 3), (MILESTONE_TOPICS_25, 25)):
    BACKFILL_RULES[_key] = (
        '''SELECT user_id, MAX(created_at) AS at FROM user_activity_events
           WHERE event_type IN (?, ?, ?, ?) AND json_extract(payload_json, '$.topic') IS NOT NULL
           GROUP BY user_id
           HAVING COUNT(DISTINCT json_extract(payload_json, '$.level') || '|' || json_extract(payload_json, '$.subject') || '|' ||
                                 json_extract(payload_json, '$.topic')) >= ?''',
        (ACTIVITY_TOPIC_OPENED, ACTIVITY_QUESTION_GENERATED, ACTIVITY_QUIZ_COMPLETED, ACTIVITY_LESSON_STEP_COMPLETED, _need),
    )
PHASE2_BACKFILL_KEYS = (
    MILESTONE_QUIZZES_5, MILESTONE_QUIZZES_25, MILESTONE_PERFECT_5, MILESTONE_PERFECT_20, MILESTONE_RETRY_FIXED,
    MILESTONE_QUESTIONS_25, MILESTONE_QUESTIONS_50, MILESTONE_QUESTIONS_250, MILESTONE_STREAK_3, MILESTONE_STREAK_100,
    MILESTONE_QOTD_30, MILESTONE_TOPICS_3, MILESTONE_TOPICS_25, MILESTONE_SETWORK_1, MILESTONE_SETWORK_10,
)


def backfill_quiet_badges(conn, keys):
    """Award the given badges to every pupil whose history already earns them, quietly. Returns the number of rows added."""
    added = 0
    for key in keys:
        sql, params = BACKFILL_RULES[key]
        for row in conn.execute(sql, params).fetchall():
            cur = conn.execute(
                'INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at, quiet) VALUES (?, ?, ?, 1)',
                (row[0], key, row[1] or utc_now_iso()),
            )
            added += cur.rowcount or 0
    return added


def quiet_badges_to_announce(conn, user_id):
    """Badges awarded quietly that this pupil has not been told about yet (oldest first)."""
    rows = conn.execute(
        'SELECT milestone_key FROM user_milestones WHERE user_id = ? AND quiet = 1 ORDER BY earned_at, milestone_key',
        (user_id,),
    ).fetchall()
    return [r['milestone_key'] for r in rows]


def mark_quiet_badges_announced(conn, user_id):
    conn.execute('UPDATE user_milestones SET quiet = 2 WHERE user_id = ? AND quiet = 1', (user_id,))


def award_tour_badge(conn, user_id):
    """E10 phase 6: award the tour badge (Pathfinder) once. True only the first time."""
    awarded = _award_milestone(conn, user_id, MILESTONE_TOUR)
    conn.commit()
    return awarded


def milestone_meta(key):
    """Catalog or dynamically generated topic-status badge metadata."""
    meta = MILESTONE_CATALOG.get(key)
    if meta:
        return meta
    return topic_badge_meta(key) or {
        'title': str(key).replace('_', ' ').replace(':', ' · '),
        'description': '',
        'blurb': '',
        'how': '',
        'next': None,
        'family': 'learning',
        'emoji': '★',
        'tier': 'bronze',
    }


def badge_display(key, earned_at=None):
    """Everything a badge screen needs, as plain JSON-safe data (profile sheet, badge stage, `new_milestones`).

    `next_title` / `next_how` describe the next badge in the same line, or are empty when there is none.
    """
    meta = milestone_meta(key)
    nxt = meta.get('next')
    nxt_meta = milestone_meta(nxt) if nxt else None
    return {
        'key': key,
        'title': meta.get('title', key),
        'blurb': meta.get('blurb', ''),
        'how': meta.get('how', ''),
        'family': meta.get('family') or 'learning',
        'emoji': meta.get('emoji', '★'),
        'tier': meta.get('tier', 'bronze'),
        'next': nxt or '',
        'next_title': (nxt_meta or {}).get('title', ''),
        'next_how': (nxt_meta or {}).get('how', ''),
        'earned_at': earned_at,
    }


def _pose_from_meta(meta):
    raw = (meta or {}).get('pose')
    if not raw:
        return None
    token = str(raw).strip().lower().replace('-', '_')
    if token in ZORP_POSE_TOKENS:
        return token
    return None


# E7 Phase 1.5: catalog milestones that carry a Zorp pose (drive the automatic live-buddy look).
_POSE_MILESTONE_KEYS = tuple(k for k, m in MILESTONE_CATALOG.items() if _pose_from_meta(m))


def latest_pose_milestone(conn, user_id):
    """Pose token of the user's most recently earned catalog milestone that has one, else None.

    Derived from user_milestones only -- no stored cosmetic preference (E7 section 2 #13).
    """
    if not _POSE_MILESTONE_KEYS:
        return None
    placeholders = ','.join('?' * len(_POSE_MILESTONE_KEYS))
    row = conn.execute(
        f'''
        SELECT milestone_key FROM user_milestones
        WHERE user_id = ? AND milestone_key IN ({placeholders})
        ORDER BY earned_at DESC, milestone_key ASC
        LIMIT 1
        ''',
        (user_id, *_POSE_MILESTONE_KEYS),
    ).fetchone()
    if not row:
        return None
    return _pose_from_meta(MILESTONE_CATALOG.get(row['milestone_key']))


def _questions_right_count(conn, user_id):
    row = conn.execute(
        f'SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ? AND {_QUESTIONS_RIGHT_WHERE}', (user_id,),
    ).fetchone()
    return int(row['n'] or 0) if row else 0


def _set_work_done_count(conn, user_id):
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM class_assignment_recipients WHERE student_id = ? AND status = 'complete'", (user_id,),
        ).fetchone()
    except sqlite3.OperationalError:   # a database without the class tables (some tests)
        return 0
    return int(row['n'] or 0) if row else 0


def _in_a_class(conn, user_id):
    try:
        row = conn.execute("SELECT 1 FROM class_memberships WHERE student_id = ? AND status = 'active' LIMIT 1", (user_id,)).fetchone()
    except sqlite3.OperationalError:
        return False
    return row is not None


def _distinct_topics_count(conn, user_id):
    row = conn.execute(
        '''
        SELECT COUNT(DISTINCT
            json_extract(payload_json, '$.level') || '|' ||
            json_extract(payload_json, '$.subject') || '|' ||
            json_extract(payload_json, '$.topic')
        ) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND event_type IN (?, ?, ?, ?)
          AND json_extract(payload_json, '$.topic') IS NOT NULL
        ''',
        (
            user_id,
            ACTIVITY_TOPIC_OPENED,
            ACTIVITY_QUESTION_GENERATED,
            ACTIVITY_QUIZ_COMPLETED,
            ACTIVITY_LESSON_STEP_COMPLETED,
        ),
    ).fetchone()
    return row['n'] if row else 0


def _weekly_answered_marks(conn, user_id, days=7):
    """Quiz + generator-MCQ marks possible for this user in the last `days` UTC days."""
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'
    stats = _accuracy_stats_since(conn, [user_id], since_iso)
    item = stats.get(user_id) or {}
    return int(item.get('possible') or 0)


def _maybe_award_accuracy_top_friend(conn, user_id):
    """Award Top of the class only when cheap guards pass, then the full friend board.

    Skips the leaderboard query when the badge is already held or the user has
    fewer than 10 answered questions this week. Needs at least two participants
    with a score (friends-only; a lone user never qualifies).
    """
    if _has_milestone(conn, user_id, MILESTONE_ACCURACY_TOP_FRIEND):
        return False
    if _weekly_answered_marks(conn, user_id) < 10:
        return False
    board = friend_accuracy_leaderboard(conn, user_id, days=7)
    scored = [item for item in board if item.get('accuracy_pct') is not None]
    if len(scored) < 2:
        return False
    viewer = next((item for item in board if item.get('is_viewer')), None)
    if not viewer or viewer.get('rank') != 1:
        return False
    return _award_milestone(conn, user_id, MILESTONE_ACCURACY_TOP_FRIEND)


def evaluate_milestones(conn, user_id):
    """Award any newly earned milestones; returns list of newly earned keys."""
    streak = get_study_streak(conn, user_id)
    earned = []

    quiz_count = conn.execute(
        'SELECT COUNT(*) AS n FROM quiz_attempts WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if quiz_count >= 1 and _award_milestone(conn, user_id, MILESTONE_FIRST_QUIZ):
        earned.append(MILESTONE_FIRST_QUIZ)

    if quiz_count >= 1:
        # E11 Phase 2: lesson quizzes finished (retry runs are part of the quiz they retry), perfect quizzes, a cleared retry run
        q = conn.execute(
            f'''
            SELECT SUM(CASE WHEN is_retry = 0 THEN 1 ELSE 0 END) AS finished,
                   SUM(CASE WHEN {_PERFECT_QUIZ_WHERE} THEN 1 ELSE 0 END) AS perfect,
                   SUM(CASE WHEN is_retry = 1 AND total >= 1 AND score >= total THEN 1 ELSE 0 END) AS fixed
            FROM quiz_attempts WHERE user_id = ?
            ''',
            (PERFECT_MIN_TOTAL, user_id),
        ).fetchone()
        finished, perfect, fixed = int(q['finished'] or 0), int(q['perfect'] or 0), int(q['fixed'] or 0)
        for key, ok in ((MILESTONE_QUIZZES_5, finished >= 5), (MILESTONE_QUIZZES_25, finished >= 25),
                        (MILESTONE_PERFECT_1, perfect >= 1), (MILESTONE_PERFECT_5, perfect >= 5),
                        (MILESTONE_PERFECT_20, perfect >= 20), (MILESTONE_RETRY_FIXED, fixed >= 1)):
            if ok and _award_milestone(conn, user_id, key):
                earned.append(key)

    lesson_count = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM lesson_progress
        WHERE user_id = ?
          AND completed_keys_json IS NOT NULL
          AND completed_keys_json != '[]'
        ''',
        (user_id,),
    ).fetchone()['n']
    if lesson_count >= 1 and _award_milestone(conn, user_id, MILESTONE_FIRST_LESSON):
        earned.append(MILESTONE_FIRST_LESSON)

    topics = _distinct_topics_count(conn, user_id)
    for key, need in ((MILESTONE_TOPICS_3, 3), (MILESTONE_TOPICS_10, 10), (MILESTONE_TOPICS_25, 25)):
        if topics >= need and _award_milestone(conn, user_id, key):
            earned.append(key)

    # E11 Phase 2 (David's answer 4): practice questions answered right (whole questions; the parts of a multi-part question are
    # not counted one by one)
    right = _questions_right_count(conn, user_id)
    for key, need in QUESTIONS_RIGHT_THRESHOLDS:
        if right >= need and _award_milestone(conn, user_id, key):
            earned.append(key)

    for key, need in ((MILESTONE_STREAK_3, 3), (MILESTONE_STREAK_7, 7), (MILESTONE_STREAK_30, 30), (MILESTONE_STREAK_100, 100)):
        if streak['longest'] >= need and _award_milestone(conn, user_id, key):
            earned.append(key)

    # E11 Phase 2: the Recovery line, from the private events the practice check routes record (once per question)
    rec = conn.execute(
        'SELECT SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) AS bounce, SUM(CASE WHEN event_type = ? THEN 1 ELSE 0 END) AS hint '
        'FROM user_activity_events WHERE user_id = ? AND event_type IN (?, ?)',
        (ACTIVITY_RETRY_CORRECT, ACTIVITY_HINT_CORRECT, user_id, ACTIVITY_RETRY_CORRECT, ACTIVITY_HINT_CORRECT),
    ).fetchone()
    bounce, hint = int(rec['bounce'] or 0), int(rec['hint'] or 0)
    for key, ok in ((MILESTONE_BOUNCE_1, bounce >= 1), (MILESTONE_BOUNCE_25, bounce >= 25),
                    (MILESTONE_HINT_1, hint >= 1), (MILESTONE_HINT_25, hint >= 25)):
        if ok and _award_milestone(conn, user_id, key):
            earned.append(key)

    # E11 Phase 2: set work finished (only pupils in a class have any)
    done = _set_work_done_count(conn, user_id)
    for key, need in ((MILESTONE_SETWORK_1, 1), (MILESTONE_SETWORK_10, 10)):
        if done >= need and _award_milestone(conn, user_id, key):
            earned.append(key)

    qotd_days = conn.execute(
        'SELECT COUNT(DISTINCT day_key) AS n FROM qotd_attempts WHERE user_id = ?',
        (user_id,),
    ).fetchone()['n']
    if qotd_days >= 1 and _award_milestone(conn, user_id, MILESTONE_QOTD_FIRST):
        earned.append(MILESTONE_QOTD_FIRST)
    if qotd_days >= 7 and _award_milestone(conn, user_id, MILESTONE_QOTD_7):
        earned.append(MILESTONE_QOTD_7)
    if qotd_days >= 30 and _award_milestone(conn, user_id, MILESTONE_QOTD_30):
        earned.append(MILESTONE_QOTD_30)

    if _maybe_award_accuracy_top_friend(conn, user_id):
        earned.append(MILESTONE_ACCURACY_TOP_FRIEND)

    earned.extend(evaluate_topic_milestones(conn, user_id, _award_milestone))

    # _award_milestone's PK on (user_id, milestone_key) means it returns True only
    # once per badge, so `earned` already has no duplicates -- one notification per key.
    for key in earned:
        create_notification(
            conn,
            user_id,
            NOTIFICATION_MILESTONE,
            {'milestone_key': key},
            commit=False,
        )

    if earned:
        conn.commit()
    return earned


def list_user_milestones(conn, user_id):
    rows = conn.execute(
        '''
        SELECT milestone_key, earned_at
        FROM user_milestones
        WHERE user_id = ?
        ORDER BY earned_at ASC
        ''',
        (user_id,),
    ).fetchall()
    out = []
    for row in rows:
        key = row['milestone_key']
        meta = milestone_meta(key)
        info = badge_display(key, row['earned_at'])
        out.append({
            'key': key,
            'title': info['title'],
            'description': meta.get('description', ''),
            'blurb': info['blurb'],
            'how': info['how'],
            'family': info['family'],
            'next_title': info['next_title'],
            'next_how': info['next_how'],
            'emoji': info['emoji'],
            'tier': info['tier'],
            'pose': _pose_from_meta(meta),
            'earned_at': row['earned_at'],
        })
    return out


def list_milestone_shelf(conn, user_id):
    """Full catalog for the profile grid: earned badges plus locked silhouettes."""
    earned = {item['key']: item for item in list_user_milestones(conn, user_id)}
    shelf = []
    in_class = _in_a_class(conn, user_id)
    for key, meta in MILESTONE_CATALOG.items():
        item = earned.get(key)
        if meta.get('class_only') and item is None and not in_class:
            continue   # E11 Phase 2: set-work badges are shown to pupils in a class (an earned one always shows)
        info = badge_display(key)
        shelf.append({
            'key': key,
            'title': meta.get('title', key),
            'description': meta.get('description', ''),
            'blurb': info['blurb'],
            'how': info['how'],
            'family': info['family'],
            'next_title': info['next_title'],
            'next_how': info['next_how'],
            'emoji': meta.get('emoji', '★'),
            'tier': meta.get('tier', 'bronze'),
            'pose': _pose_from_meta(meta),
            'earned': item is not None,
            'earned_at': item['earned_at'] if item else None,
        })
    for key, item in earned.items():
        if key in MILESTONE_CATALOG:
            continue
        shelf.append({
            'key': key,
            'title': item.get('title', key),
            'description': item.get('description', ''),
            'blurb': item.get('blurb', ''),
            'how': item.get('how', ''),
            'family': item.get('family', 'learning'),
            'next_title': item.get('next_title', ''),
            'next_how': item.get('next_how', ''),
            'emoji': item.get('emoji', '★'),
            'tier': item.get('tier', 'bronze'),
            'pose': item.get('pose'),
            'earned': True,
            'earned_at': item.get('earned_at'),
        })
    shelf.sort(key=lambda row: (not row['earned'], row['title']))
    return shelf


def next_up_badge(shelf):
    """One badge to point at on the profile ("Next up"): the one that follows the newest badge earned, else the first
    badge in the catalog that is not earned yet. The shelf is the list from list_milestone_shelf(). None when all are earned."""
    by_key = {item['key']: item for item in shelf}
    earned = sorted((i for i in shelf if i.get('earned')), key=lambda i: i.get('earned_at') or '', reverse=True)
    for item in earned:
        nxt = by_key.get((milestone_meta(item['key']) or {}).get('next') or '')
        if nxt and not nxt.get('earned'):
            return nxt
    for key in MILESTONE_CATALOG:
        item = by_key.get(key)
        if item and not item.get('earned'):
            return item
    return None


def streak_week_dots(conn, user_id, as_of=None):
    """Last 7 UTC days for the streak ring: studied, frozen, or missed."""
    today = as_of or _utc_today()
    start = today - timedelta(days=6)
    rows = conn.execute(
        '''
        SELECT study_date FROM user_study_days
        WHERE user_id = ? AND study_date >= ?
        ''',
        (user_id, start.isoformat()),
    ).fetchall()
    studied = {row['study_date'] for row in rows}
    frozen = set(_freeze_used_dates(conn, user_id, as_of=today))
    dots = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        key = day.isoformat()
        if key in studied:
            state = 'studied'
        elif key in frozen:
            state = 'frozen'
        else:
            state = 'missed'
        dots.append({
            'date': key,
            'label': day.strftime('%a')[0],
            'state': state,
            'is_today': offset == 0,
        })
    return dots


def streak_calendar(conn, user_id, weeks=4, as_of=None):
    """7×N UTC day grid for profile Progress (oldest week first, Mon–Sun columns)."""
    today = as_of or _utc_today()
    weeks = max(1, int(weeks))
    days_total = weeks * 7
    start = today - timedelta(days=days_total - 1)
    studied = {
        row['study_date']
        for row in conn.execute(
            '''
            SELECT study_date FROM user_study_days
            WHERE user_id = ? AND study_date >= ?
            ''',
            (user_id, start.isoformat()),
        ).fetchall()
    }
    frozen = {
        row['freeze_date']
        for row in conn.execute(
            '''
            SELECT freeze_date FROM user_streak_freezes
            WHERE user_id = ? AND freeze_date >= ?
            ''',
            (user_id, start.isoformat()),
        ).fetchall()
    }
    rows = []
    for week_index in range(weeks):
        week_cells = []
        for col in range(7):
            day_offset = week_index * 7 + col
            day = start + timedelta(days=day_offset)
            key = day.isoformat()
            if key in studied:
                state = 'studied'
            elif key in frozen:
                state = 'frozen'
            else:
                state = 'missed'
            week_cells.append({
                'date': key,
                'label': day.strftime('%a')[0],
                'state': state,
                'is_today': day == today,
            })
        rows.append(week_cells)
    return rows


def weekly_effort_by_day(conn, user_id, days=7):
    """Effort points per UTC calendar day for the last ``days`` days (Mon→today order)."""
    today = _utc_today()
    days = max(1, int(days))
    start = today - timedelta(days=days - 1)
    since_iso = f'{start.isoformat()}T00:00:00'
    type_ph = ','.join('?' * len(EFFORT_EVENT_TYPES))
    scores = { (start + timedelta(days=i)).isoformat(): 0 for i in range(days) }
    rows = conn.execute(
        f'''
        SELECT substr(created_at, 1, 10) AS day, event_type, COUNT(*) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN ({type_ph})
        GROUP BY day, event_type
        ''',
        (user_id, since_iso, *EFFORT_EVENT_TYPES),
    ).fetchall()
    for row in rows:
        day = row['day']
        if day not in scores:
            continue
        scores[day] += EFFORT_WEIGHTS.get(row['event_type'], 1) * int(row['n'] or 0)
    out = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        key = day.isoformat()
        out.append({
            'date': key,
            'label': day.strftime('%a')[0],
            'score': scores.get(key, 0),
            'is_today': day == today,
        })
    return out


def recent_accuracy_trend(conn, user_id, limit=10):
    """Last ``limit`` quiz + generator-MCQ accuracies, oldest→newest for sparklines."""
    limit = max(1, int(limit))
    points = []
    for row in conn.execute(
        '''
        SELECT created_at, score, total
        FROM quiz_attempts
        WHERE user_id = ? AND is_retry = 0
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall():
        total = int(row['total'] or 0)
        score = int(row['score'] or 0)
        if total <= 0:
            continue
        points.append({
            'created_at': row['created_at'],
            'pct': round(100.0 * score / total, 1),
            'kind': 'quiz',
        })
    for row in conn.execute(
        '''
        SELECT created_at, score, score_total, correct
        FROM generator_mcq_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall():
        total = int(row['score_total'] or 0)
        if total > 0:
            pct = round(100.0 * int(row['score'] or 0) / total, 1)
        else:
            pct = 100.0 if int(row['correct'] or 0) else 0.0
        points.append({
            'created_at': row['created_at'],
            'pct': pct,
            'kind': 'mcq',
        })
    points.sort(key=lambda item: item['created_at'], reverse=True)
    points = points[:limit]
    points.sort(key=lambda item: item['created_at'])
    return points


def streak_ring_progress(current):
    """Progress toward the next streak milestone (7 / 30 / 100)."""
    days = max(0, int(current or 0))
    target = 7
    for candidate in (7, 30, 100):
        target = candidate
        if days < candidate:
            break
    pct = 1.0 if days >= 100 else min(1.0, days / float(target))
    return {'current': days, 'target': target, 'pct': pct}


def topic_mastery_map(conn, user_id):
    """(level, subject, topic) → 0–1 mastery from lesson-complete / ninja / master."""
    return {
        key: float(status.get('mastery') or 0)
        for key, status in load_topic_status_map(conn, user_id).items()
    }


def get_weekly_recap(conn, user_id, days=7):
    """In-app weekly summary for the last `days` calendar days (inclusive)."""
    start_day = (_utc_today() - timedelta(days=days - 1)).isoformat()

    active_days = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM user_study_days
        WHERE user_id = ? AND study_date >= ?
        ''',
        (user_id, start_day),
    ).fetchone()['n']

    topics = conn.execute(
        '''
        SELECT COUNT(DISTINCT
            json_extract(payload_json, '$.level') || '|' ||
            json_extract(payload_json, '$.subject') || '|' ||
            json_extract(payload_json, '$.topic')
        ) AS n
        FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN (?, ?, ?, ?)
          AND json_extract(payload_json, '$.topic') IS NOT NULL
        ''',
        (
            user_id,
            start_day,
            ACTIVITY_TOPIC_OPENED,
            ACTIVITY_QUESTION_GENERATED,
            ACTIVITY_QUIZ_COMPLETED,
            ACTIVITY_LESSON_STEP_COMPLETED,
        ),
    ).fetchone()['n']

    best_quiz = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ? AND created_at >= ? AND total > 0 AND is_retry = 0
        ORDER BY (1.0 * score / total) DESC, score DESC, created_at DESC
        LIMIT 1
        ''',
        (user_id, start_day),
    ).fetchone()

    activity_total = conn.execute(
        f'''
        SELECT COUNT(*) AS n FROM user_activity_events
        WHERE user_id = ?
          AND created_at >= ?
          AND event_type IN ({','.join('?' * len(EFFORT_EVENT_TYPES))})
        ''',
        (
            user_id,
            start_day,
            *EFFORT_EVENT_TYPES,
        ),
    ).fetchone()['n']

    recap = {
        'days': days,
        'active_days': active_days,
        'topics_practised': topics,
        'activity_count': activity_total,
        'best_quiz': None,
    }
    if best_quiz:
        recap['best_quiz'] = {
            'level': best_quiz['level'],
            'subject': best_quiz['subject'],
            'topic': best_quiz['topic'],
            'score': best_quiz['score'],
            'total': best_quiz['total'],
            'created_at': best_quiz['created_at'],
        }
    return recap


def _effort_score_since(conn, user_id, since_iso):
    scores = _effort_scores_since(conn, [user_id], since_iso)
    return scores.get(user_id, 0)


def weekly_effort_xp(conn, user_id, days=7):
    """Effort points (displayed as XP) for the last N UTC days."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    return _effort_score_since(conn, user_id, since)


def lifetime_effort_xp(conn, user_id):
    """All-time effort points for the level ring."""
    return _effort_score_since(conn, user_id, '1970-01-01 00:00:00')


def xp_level_from_points(xp):
    """Level curve: L1 below 200 XP, then L = floor(sqrt(xp / 50))."""
    xp = max(0, int(xp or 0))
    if xp <= 0:
        return 1
    return max(1, int((xp / 50) ** 0.5))


def xp_level_progress(xp):
    """Fill for the level ring: share of XP between this level and the next."""
    xp = max(0, int(xp or 0))
    level = xp_level_from_points(xp)
    if level <= 1:
        start, nxt = 0, 200
    else:
        start = 50 * level * level
        nxt = 50 * (level + 1) * (level + 1)
    span = max(1, nxt - start)
    pct = min(1.0, max(0.0, (xp - start) / span))
    return {
        'level': level,
        'xp': xp,
        'start': start,
        'next': nxt,
        'pct': pct,
        'remaining': max(0, nxt - xp),
    }


def effort_weight(event_type):
    """Effort points one activity event of this type records (0 for events that earn none)."""
    return EFFORT_WEIGHTS.get(event_type, 0) if event_type in EFFORT_EVENT_TYPES else 0


def level_up_between(xp_before, xp_after):
    """E10 phase 5: the level reached when effort points move from xp_before to xp_after, else None.
    The payload is what the level-up stage needs: the new level, the ring fill inside it, and the points to the next level."""
    before = xp_level_from_points(xp_before)
    after = xp_level_from_points(xp_after)
    if after <= before:
        return None
    prog = xp_level_progress(xp_after)
    return {'level': after, 'pct': round(prog['pct'], 3), 'remaining': prog['remaining']}


def personal_best_quiz(conn, user_id, level, subject, topic, score, total):
    """E10 phase 5: True when this score (as a share of the total) beats every earlier quiz attempt on the same topic.
    Compared only with the pupil's own past: it needs at least one earlier attempt, and a perfect score is not 'a best'
    (the perfect moment covers it)."""
    total = int(total or 0)
    if total <= 0 or int(score or 0) >= total:
        return False
    rows = conn.execute(
        'SELECT score, total FROM quiz_attempts WHERE user_id = ? AND level = ? AND subject = ? AND topic = ? AND total > 0 AND is_retry = 0',   # full quizzes only (E10 phase 6)
        (user_id, level, subject, topic),
    ).fetchall()
    # the attempt just saved is one of the rows: it must be the only one at its share, and others must be lower
    shares = sorted(int(r['score'] or 0) / int(r['total']) for r in rows)
    mine = int(score or 0) / total
    return len(shares) >= 2 and shares[-1] <= mine + 1e-9 and shares[-2] < mine - 1e-9


def study_streak_at_risk(conn, user_id, as_of=None):
    """True when the user has an active streak but has not studied today."""
    today = as_of or _utc_today()
    streak = get_study_streak(conn, user_id, as_of=today)
    if streak.get('current', 0) < 1:
        return False
    last_active = streak.get('last_active_date')
    if not last_active:
        return False
    last_day = last_active[:10]
    if last_day == today.isoformat():
        return False
    yesterday = (today - timedelta(days=1)).isoformat()
    return last_day == yesterday


def _effort_scores_since(conn, user_ids, since_iso):
    """Batch effort scores for many users (avoids N+1 on friend leaderboard)."""
    ids = [int(uid) for uid in user_ids if uid is not None]
    scores = {uid: 0 for uid in ids}
    if not ids:
        return scores
    type_ph = ','.join('?' * len(EFFORT_EVENT_TYPES))
    user_ph = ','.join('?' * len(ids))
    rows = conn.execute(
        f'''
        SELECT user_id, event_type, COUNT(*) AS n
        FROM user_activity_events
        WHERE user_id IN ({user_ph})
          AND created_at >= ?
          AND event_type IN ({type_ph})
        GROUP BY user_id, event_type
        ''',
        (*ids, since_iso, *EFFORT_EVENT_TYPES),
    ).fetchall()
    for row in rows:
        scores[row['user_id']] = (
            scores.get(row['user_id'], 0)
            + EFFORT_WEIGHTS.get(row['event_type'], 1) * row['n']
        )
    return scores


def friend_effort_leaderboard(conn, viewer_id, days=7):
    """Effort-based ranking for people the viewer follows, plus the viewer."""
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'

    following = conn.execute(
        '''
        SELECT u.id, u.handle
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY u.handle COLLATE NOCASE
        ''',
        (viewer_id,),
    ).fetchall()

    viewer = conn.execute(
        'SELECT id, handle FROM users WHERE id = ?',
        (viewer_id,),
    ).fetchone()

    participants = {row['id']: row['handle'] for row in following}
    if viewer:
        participants[viewer['id']] = viewer['handle']

    scores = _effort_scores_since(conn, participants.keys(), since_iso)
    ranked = []
    for user_id, handle in participants.items():
        ranked.append({
            'user_id': user_id,
            'handle': handle,
            'score': scores.get(user_id, 0),
            'is_viewer': user_id == viewer_id,
        })

    ranked.sort(key=lambda item: (-item['score'], item['handle'].lower()))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
    attach_avatars(conn, ranked)
    return ranked


def _follow_graph_participants(conn, viewer_id):
    following = conn.execute(
        '''
        SELECT u.id, u.handle
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY u.handle COLLATE NOCASE
        ''',
        (viewer_id,),
    ).fetchall()
    viewer = conn.execute(
        'SELECT id, handle FROM users WHERE id = ?',
        (viewer_id,),
    ).fetchone()
    participants = {row['id']: row['handle'] for row in following}
    if viewer:
        participants[viewer['id']] = viewer['handle']
    return participants


def _accuracy_stats_since(conn, user_ids, since_iso):
    stats = {
        uid: {'earned': 0, 'possible': 0, 'quiz_n': 0, 'mcq_n': 0}
        for uid in user_ids
    }
    if not user_ids:
        return stats
    ids = list(user_ids)
    placeholders = ','.join('?' * len(ids))
    for row in conn.execute(
        f'''
        SELECT user_id,
               COALESCE(SUM(score), 0) AS earned,
               COALESCE(SUM(total), 0) AS possible,
               COUNT(*) AS n
        FROM quiz_attempts
        WHERE user_id IN ({placeholders})
          AND created_at >= ?
          AND is_retry = 0
        GROUP BY user_id
        ''',
        (*ids, since_iso),
    ).fetchall():
        item = stats[row['user_id']]
        item['earned'] += int(row['earned'] or 0)
        item['possible'] += int(row['possible'] or 0)
        item['quiz_n'] = int(row['n'] or 0)
    for row in conn.execute(
        f'''
        SELECT user_id,
               COALESCE(SUM(
                   CASE WHEN COALESCE(score_total, 0) > 0
                        THEN COALESCE(score, 0)
                        ELSE correct END
               ), 0) AS earned,
               COALESCE(SUM(
                   CASE WHEN COALESCE(score_total, 0) > 0
                        THEN score_total
                        ELSE 1 END
               ), 0) AS possible,
               COUNT(*) AS n
        FROM generator_mcq_attempts
        WHERE user_id IN ({placeholders})
          AND created_at >= ?
        GROUP BY user_id
        ''',
        (*ids, since_iso),
    ).fetchall():
        item = stats[row['user_id']]
        item['earned'] += int(row['earned'] or 0)
        item['possible'] += int(row['possible'] or 0)
        item['mcq_n'] = int(row['n'] or 0)
    return stats


def user_accuracy_pct(conn, user_id, days=None):
    """Quiz + generator-MCQ accuracy as a 0–100 int, or None if no attempts."""
    if days:
        since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
        since_iso = f'{since_day}T00:00:00'
    else:
        since_iso = '1970-01-01T00:00:00'
    stats = _accuracy_stats_since(conn, [user_id], since_iso).get(user_id) or {}
    possible = int(stats.get('possible') or 0)
    if possible <= 0:
        return None
    return int(round(100.0 * int(stats.get('earned') or 0) / possible))


def friend_accuracy_leaderboard(conn, viewer_id, days=7):
    """Weekly quiz+MCQ accuracy among people the viewer follows, plus the viewer.

    Accuracy = (lesson-quiz marks earned + generator-MCQ marks earned)
    / (lesson-quiz marks possible + generator-MCQ marks possible) over the last
    ``days`` UTC days. Users who opted out of the accuracy board are hidden from
    everyone except themselves. No global ranking.
    """
    since_day = (_utc_today() - timedelta(days=days - 1)).isoformat()
    since_iso = f'{since_day}T00:00:00'
    participants = _follow_graph_participants(conn, viewer_id)
    if not participants:
        return []

    ids = list(participants.keys())
    placeholders = ','.join('?' * len(ids))
    opted_in = {uid: True for uid in ids}
    try:
        rows = conn.execute(
            f'''
            SELECT user_id, show_accuracy_leaderboard
            FROM user_profile_settings
            WHERE user_id IN ({placeholders})
            ''',
            ids,
        ).fetchall()
        for row in rows:
            opted_in[row['user_id']] = bool(row['show_accuracy_leaderboard'])
    except sqlite3.OperationalError:
        pass

    visible_ids = [
        uid for uid in ids
        if uid == viewer_id or opted_in.get(uid, True)
    ]
    stats = _accuracy_stats_since(conn, visible_ids, since_iso)
    ranked = []
    for user_id in visible_ids:
        item_stats = stats.get(user_id) or {'earned': 0, 'possible': 0, 'quiz_n': 0, 'mcq_n': 0}
        possible = item_stats['possible']
        accuracy = round(100.0 * item_stats['earned'] / possible, 1) if possible else None
        ranked.append({
            'user_id': user_id,
            'handle': participants[user_id],
            'accuracy_pct': accuracy,
            'earned': item_stats['earned'],
            'possible': possible,
            'quiz_attempts': item_stats['quiz_n'],
            'mcq_attempts': item_stats['mcq_n'],
            'is_viewer': user_id == viewer_id,
        })

    ranked.sort(key=lambda item: (
        item['accuracy_pct'] is None,
        -(item['accuracy_pct'] if item['accuracy_pct'] is not None else -1),
        -(item['possible'] or 0),
        item['handle'].lower(),
    ))
    for index, item in enumerate(ranked, start=1):
        item['rank'] = index
    attach_avatars(conn, ranked)
    return ranked
