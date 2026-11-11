import json
import re

from models.avatar import avatar_to_json, parse_avatar
from models.user import User, normalize_handle, utc_now_iso

VISIBILITY_PUBLIC = 'public'
VISIBILITY_FOLLOWERS = 'followers_only'
VISIBILITY_PRIVATE = 'private'
VISIBILITY_CHOICES = (
    VISIBILITY_PUBLIC,
    VISIBILITY_FOLLOWERS,
    VISIBILITY_PRIVATE,
)

THEME_SYSTEM = 'system'
THEME_LIGHT = 'light'
THEME_DARK = 'dark'
THEME_CHOICES = (THEME_SYSTEM, THEME_LIGHT, THEME_DARK)

MOTION_SYSTEM = 'system'
MOTION_REDUCED = 'reduced'
MOTION_OFF = 'off'
MOTION_CHOICES = (MOTION_SYSTEM, MOTION_REDUCED, MOTION_OFF)

# E9 Phase 4 (D6 = B, docs/ZORP_CHARM.md 6): Zorp's celebration sounds, a display preference like the two above.
# `chatter` (voice blips, D7) is defined so the page and the sound code know the name, but it is never accepted from a
# pupil until D7 is revisited after the evaluation: ZORP_SOUND_CHOICES is what the form, the PATCH validator and storage accept.
ZORP_SOUND_OFF = 'off'
ZORP_SOUND_CELEBRATIONS = 'celebrations'
ZORP_SOUND_CHATTER = 'chatter'
ZORP_SOUND_CHOICES = (ZORP_SOUND_OFF, ZORP_SOUND_CELEBRATIONS)
ZORP_SOUND_DEFINED = ZORP_SOUND_CHOICES + (ZORP_SOUND_CHATTER,)

# E11 Phase 1 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 2.4 rule 5, David's answer 11): how big celebrations are.
#   full   every stage full screen (the default)
#   big    badges and level-ups full screen; everything else (a finished lesson, a 10/10) as a corner card
#   small  every stage as a corner card (badges still show their card, and nothing is lost from Milestones)
# perfect_as_card (the quiet link on the 10/10 screen) turns only the 10/10 stage into a card, in full mode.
CELEBRATION_FULL = 'full'
CELEBRATION_BIG = 'big'
CELEBRATION_SMALL = 'small'
CELEBRATION_MODES = (CELEBRATION_FULL, CELEBRATION_BIG, CELEBRATION_SMALL)

GUIDE_JSON_MAX = 4096
_GUIDE_TOUR_KEY = re.compile(r'^[a-z][a-z0-9_]{0,31}$')
_GUIDE_REWARD_KEY = re.compile(r'^[a-z0-9_:]{1,64}$')
_GUIDE_FLAG_LIMIT = 40
_GUIDE_OWN_KEYS = ('v', 'origin', 'tours', 'rewards', 'run', 'recent')

# 2026-11-08 (E10 phase 6, fixing the phase 5 "seen-state overflow"). The guide state is one 4,096 byte blob, and phase 4 and 5
# put one flag per badge, level and lesson into it, so an active pupil could fill it, an over-large merge was refused, and the
# tour, coach and spotlight flags stopped saving. It is now split into regions, each with its own byte budget, so one kind of
# flag can never crowd out another:
#   tours     (tours, coach, app tour, spotlights)     <= GUIDE_TOURS_BYTES, never evicted
#   rewards   (streak:*, first_correct, lesson_complete) <= GUIDE_REWARDS_BYTES, a handful of flags in all
#   recent    (level:*, lesson:*, milestone:*)         a ring, oldest evicted first, <= GUIDE_RECENT_BYTES and GUIDE_RECENT_MAX entries
#   run       the tour in progress {id, step}
# The ring is safe to forget: badges, levels and perfect quizzes are emitted once by the server when they happen, so the
# flag only guards against showing one twice in a page view; a forgotten lesson flag can at worst replay the small finished
# lesson scene. The client still sees one `rewards` dict (durable flags, then the ring in order), so guide.js is unchanged
# for them. The total (about 4,000 bytes at the very most, a few hundred for a real pupil) is always under GUIDE_JSON_MAX.
GUIDE_TOURS_BYTES = 1400
GUIDE_REWARDS_BYTES = 800
GUIDE_RECENT_BYTES = 1400
GUIDE_RECENT_MAX = 80
GUIDE_INCOMING_MAX = 16384      # transport limit for one PATCH; the stored state is always trimmed to the budgets above
# 'fs:<day>:<n>' (E11 Phase 1): the full screens spent from the day's budget; old days fall out of the ring by themselves
_GUIDE_VOLATILE_PREFIXES = ('level:', 'lesson:', 'milestone:', 'fs:')
_GUIDE_INCOMING_TOURS = 80
_GUIDE_INCOMING_REWARDS = 400
GUIDE_RUN_MAX_STEP = 60

# E7 Phase 3: welcome state lives in the same guide_json blob (§2 of
# docs/MASCOT_MOTION_AND_ONBOARDING.md) but is a distinct namespace from the
# Guide's own v/origin/tours/rewards keys.
_WELCOME_TOKEN_RE = re.compile(r'^[a-z0-9_]{1,40}$')


def empty_guide_state():
    return {'v': 1, 'origin': False, 'tours': {}, 'rewards': {}, 'run': None}


def guide_json_is_stored(raw):
    """True only when the stored JSON actually holds Guide state (not just welcome keys).

    A brand-new user whose only guide_json content is E7 welcome keys must not flip
    ``data-guide-persisted`` to true — that flag tells guide.js the server is
    authoritative, which would make it drop local-only Guide flags.
    """
    text = (raw or '').strip()
    if not text or text in ('{}', 'null'):
        return False
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    return any(key in data for key in _GUIDE_OWN_KEYS)


def welcome_state(raw_or_dict):
    """Shape-validated welcome onboarding state parsed the same way as public_guide_state."""
    if isinstance(raw_or_dict, dict):
        data = raw_or_dict
    else:
        try:
            data = json.loads(raw_or_dict or '{}')
        except (TypeError, ValueError):
            data = {}
    if not isinstance(data, dict):
        data = {}
    level = data.get('level')
    if not isinstance(level, str) or not _WELCOME_TOKEN_RE.match(level):
        level = None
    topic = data.get('topic')
    if not isinstance(topic, str) or not _WELCOME_TOKEN_RE.match(topic):
        topic = None
    return {
        'done': data.get('welcome_done') is True,
        'level': level,
        'topic': topic,
    }


_UNSET = object()


def set_welcome_state(conn, user_id, *, done=_UNSET, level=_UNSET, topic=_UNSET):
    """Targeted update of only the welcome_done/level/topic keys in guide_json.

    Never touches the Guide's own v/origin/tours/rewards keys, and never rewrites
    the rest of user_profile_settings (unlike update_profile_settings).
    """
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        'SELECT guide_json FROM user_profile_settings WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    try:
        base = json.loads((row['guide_json'] if row else '') or '{}')
    except (TypeError, ValueError):
        base = {}
    if not isinstance(base, dict):
        base = {}

    if done is not _UNSET:
        base['welcome_done'] = bool(done)
    if level is not _UNSET:
        if level is None:
            base.pop('level', None)
        else:
            base['level'] = level
    if topic is not _UNSET:
        if topic is None:
            base.pop('topic', None)
        else:
            base['topic'] = topic

    dumped = json.dumps(base, separators=(',', ':'))
    if len(dumped) > GUIDE_JSON_MAX:
        raise ValueError('guide_json too large')

    conn.execute(
        'UPDATE user_profile_settings SET guide_json = ? WHERE user_id = ?',
        (dumped, user_id),
    )
    conn.commit()


def set_guide_origin(conn, user_id, seen=True):
    """E10: record the Guide origin story as seen (or not) in guide_json, keeping every other key.

    The arrival film on /welcome tells the origin story, so any welcome_step POST (a choice, Skip intro then a
    choice, or Skip for now) means the pupil has seen or skipped it: the old origin story must not play afterwards.
    """
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        'SELECT guide_json FROM user_profile_settings WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    dumped = merge_guide_json(row['guide_json'] if row else '', {'origin': bool(seen)})
    conn.execute(
        'UPDATE user_profile_settings SET guide_json = ? WHERE user_id = ?',
        (dumped, user_id),
    )
    conn.commit()


def start_app_tour(conn, user_id):
    """E10 phase 6: "Replay the tour" (Settings). The app tour is due again from its first step; the badge stays earned once."""
    ensure_user_profile(conn, user_id)
    row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (user_id,)).fetchone()
    dumped = merge_guide_json(
        row['guide_json'] if row else '',
        {'tours': {'app': False}, 'run': {'id': 'app', 'step': 0}},
    )
    # 2026-11-08 (E10 review fix 8): a replay must reach the end again; the server-only marker is cleared
    try:
        stored = json.loads(dumped)
        if isinstance(stored, dict) and stored.pop(TOUR_FINISHED_KEY, None) is not None:
            dumped = _guide_dump(stored)
    except (TypeError, ValueError):
        pass
    conn.execute('UPDATE user_profile_settings SET guide_json = ? WHERE user_id = ?', (dumped, user_id))
    conn.commit()


def guide_tour_taken(conn, user_id):
    """True when the app tour is running or has been finished or skipped."""
    row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (user_id,)).fetchone()
    state = public_guide_state(row['guide_json'] if row else '')
    run = state.get('run') or {}
    return bool((state.get('tours') or {}).get('app')) or run.get('id') == 'app'


# 2026-11-08 (E10 review fix 8). Declining the tour ("Not now") sets tours.app, which any pupil can also PATCH, so that flag
# cannot prove the tour was walked. The Pathfinder badge now asks for a server-only marker, `tour_finished`, kept in guide_json
# beside the welcome keys. It is written only by mark_tour_finished, never by the guide PATCH (merge_guide_json reads known keys
# only), and only when the stored run says the pupil is on the last page of the tour (the settings page: step 16 or later; the
# 19 steps run 0..18, or 0..17 without the Classes stop, and the settings page starts at 17 or 16).
TOUR_FINISHED_KEY = 'tour_finished'
TOUR_END_MIN_STEP = 16


def mark_tour_finished(conn, user_id):
    """Record that the app tour reached its end. True only when the stored run is the app tour at its last page."""
    row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (user_id,)).fetchone()
    if not row:
        return False
    try:
        base = json.loads(row['guide_json'] or '{}')
    except (TypeError, ValueError):
        return False
    if not isinstance(base, dict):
        return False
    run = _guide_run(base.get('run')) or {}
    if run.get('id') != 'app' or run.get('step', -1) < TOUR_END_MIN_STEP:
        return False
    base[TOUR_FINISHED_KEY] = True
    conn.execute('UPDATE user_profile_settings SET guide_json = ? WHERE user_id = ?', (_guide_dump(base), user_id))
    conn.commit()
    return True


def guide_tour_finished(conn, user_id):
    """True when mark_tour_finished recorded the end of the app tour (the Pathfinder badge asks for this)."""
    row = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (user_id,)).fetchone()
    try:
        base = json.loads((row['guide_json'] if row else '') or '{}')
    except (TypeError, ValueError):
        return False
    return isinstance(base, dict) and base.get(TOUR_FINISHED_KEY) is True


# E10 (answer 7 of docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md section 10): a NEW account starts with both sounds on, the
# answer tones and Zorp's celebration cues; Settings still switches either off. Existing accounts keep what they have:
# the stored values (sound_enabled 0/1, zorp_sound off/celebrations) cannot tell "never chose" from "chose off", so
# nothing is migrated, and the column defaults stay 0 / 'off'. The browser rules still decide when a sound may play
# (a tap in the last 5 s, a visible page, not in a quiz; Zorp's cues only at full motion).
NEW_ACCOUNT_SOUND_ENABLED = True
NEW_ACCOUNT_ZORP_SOUND = ZORP_SOUND_CELEBRATIONS


def apply_new_account_defaults(conn, user_id):
    """Defaults that apply to a brand-new account only (called right after the account is created)."""
    ensure_user_profile(conn, user_id)
    conn.execute(
        'UPDATE user_profile_settings SET sound_enabled = ?, zorp_sound = ? WHERE user_id = ?',
        (_bool_int(NEW_ACCOUNT_SOUND_ENABLED), normalize_zorp_sound(NEW_ACCOUNT_ZORP_SOUND), user_id),
    )
    conn.commit()


def _guide_bool_flags(src, key_re, limit=_GUIDE_FLAG_LIMIT, keep_last=False):
    """The valid boolean flags of `src`, at most `limit`: the first ones, or with keep_last the newest (the end of the dict)."""
    out = {}
    if not isinstance(src, dict):
        return out
    items = list(src.items())
    if keep_last and len(items) > limit:
        items = items[-limit:]
    for key, value in items:
        if len(out) >= limit:
            break
        if not isinstance(key, str) or not key_re.match(key):
            continue
        if isinstance(value, bool):
            out[key] = value
    return out


def public_guide_state(raw_or_dict):
    if isinstance(raw_or_dict, dict):
        data = raw_or_dict
    else:
        try:
            data = json.loads(raw_or_dict or '{}')
        except (TypeError, ValueError):
            data = {}
    if not isinstance(data, dict):
        data = {}
    state = empty_guide_state()
    if 'origin' in data:
        state['origin'] = bool(data['origin'])
    state['tours'] = _guide_bool_flags(data.get('tours'), _GUIDE_TOUR_KEY, _GUIDE_INCOMING_TOURS)
    rewards = _guide_bool_flags(data.get('rewards'), _GUIDE_REWARD_KEY, _GUIDE_INCOMING_REWARDS)
    # the client sees one rewards dict: the durable flags, then the ring of recent celebration flags (oldest first)
    recent = data.get('recent')
    if isinstance(recent, list):
        for key in recent:
            if isinstance(key, str) and _GUIDE_REWARD_KEY.match(key):
                rewards[key] = True
    state['rewards'] = rewards
    state['run'] = _guide_run(data.get('run'))
    return state


def _guide_run(value):
    """The tour in progress {id, step}, or None. Shape-checked: a tour id and a small step number."""
    if not isinstance(value, dict):
        return None
    tour_id = value.get('id')
    step = value.get('step')
    if not isinstance(tour_id, str) or not _GUIDE_TOUR_KEY.match(tour_id):
        return None
    if isinstance(step, bool) or not isinstance(step, int) or step < 0 or step > GUIDE_RUN_MAX_STEP:
        return None
    return {'id': tour_id, 'step': step}


def _guide_dump(value):
    return json.dumps(value, separators=(',', ':'))


def _fit_guide_flags(flags, budget):
    """Keep flags in order while they fit the byte budget (a flag past the budget is dropped)."""
    out = {}
    for key, value in flags.items():
        out[key] = value
        if len(_guide_dump(out)) > budget:
            out.pop(key)
    return out


def _fit_guide_recent(keys):
    keys = list(keys)[-GUIDE_RECENT_MAX:]
    while keys and len(_guide_dump(keys)) > GUIDE_RECENT_BYTES:
        keys.pop(0)
    return keys


def _settle_guide(base):
    """Bring a stored guide dict inside the regional budgets, moving older volatile reward flags into the ring."""
    recent = [k for k in (base.get('recent') or []) if isinstance(k, str) and _GUIDE_REWARD_KEY.match(k)] \
        if isinstance(base.get('recent'), list) else []
    rewards = base.get('rewards') if isinstance(base.get('rewards'), dict) else {}
    durable = {}
    for key, value in rewards.items():
        if not isinstance(key, str) or not _GUIDE_REWARD_KEY.match(key) or not isinstance(value, bool):
            continue
        if key.startswith(_GUIDE_VOLATILE_PREFIXES):
            if value and key not in recent:
                recent.append(key)
        else:
            durable[key] = value
    tours = base.get('tours') if isinstance(base.get('tours'), dict) else {}
    tours = {k: v for k, v in tours.items() if isinstance(k, str) and _GUIDE_TOUR_KEY.match(k) and isinstance(v, bool)}
    base['tours'] = _fit_guide_flags(tours, GUIDE_TOURS_BYTES)
    base['rewards'] = _fit_guide_flags(durable, GUIDE_REWARDS_BYTES)
    base['recent'] = _fit_guide_recent(recent)
    run = _guide_run(base.get('run'))
    if run:
        base['run'] = run
    else:
        base.pop('run', None)
    return base


def validate_guide_patch(data):
    if not isinstance(data, dict):
        return None, 'guide must be an object'
    if 'origin' in data and not isinstance(data['origin'], bool):
        return None, 'guide.origin must be a boolean'
    if 'tours' in data and not isinstance(data['tours'], dict):
        return None, 'guide.tours must be an object'
    if 'rewards' in data and not isinstance(data['rewards'], dict):
        return None, 'guide.rewards must be an object'
    if 'run' in data and data['run'] is not None and _guide_run(data['run']) is None:
        return None, 'guide.run must be null or {id, step}'
    dumped = json.dumps(data, separators=(',', ':'))
    if len(dumped) > GUIDE_INCOMING_MAX:
        return None, 'guide is too large'
    return data, None


def merge_guide_json(existing_raw, incoming):
    try:
        base = json.loads(existing_raw or '{}')
    except (TypeError, ValueError):
        base = {}
    if not isinstance(base, dict):
        base = {}
    _settle_guide(base)
    if isinstance(incoming, dict):
        if 'origin' in incoming:
            base['origin'] = bool(incoming['origin'])
        if 'tours' in incoming and isinstance(incoming['tours'], dict):
            tours = base.get('tours') if isinstance(base.get('tours'), dict) else {}
            tours.update(_guide_bool_flags(incoming['tours'], _GUIDE_TOUR_KEY, _GUIDE_INCOMING_TOURS))
            base['tours'] = _fit_guide_flags(tours, GUIDE_TOURS_BYTES)
        if 'rewards' in incoming and isinstance(incoming['rewards'], dict):
            rewards = base.get('rewards') if isinstance(base.get('rewards'), dict) else {}
            recent = list(base.get('recent') or [])
            # the durable flags first (a handful), then the ring's candidates: only the newest of a very long list are looked at
            valid = _guide_bool_flags(incoming['rewards'], _GUIDE_REWARD_KEY, 1 << 20)
            durable_in = [kv for kv in valid.items() if not kv[0].startswith(_GUIDE_VOLATILE_PREFIXES)][:_GUIDE_INCOMING_REWARDS]
            volatile_in = [kv for kv in valid.items() if kv[0].startswith(_GUIDE_VOLATILE_PREFIXES)][-_GUIDE_INCOMING_REWARDS:]
            for key, value in durable_in + volatile_in:
                if key.startswith(_GUIDE_VOLATILE_PREFIXES):
                    if value and key not in recent:
                        recent.append(key)
                    elif not value and key in recent:
                        recent.remove(key)
                else:
                    rewards[key] = value
            base['rewards'] = _fit_guide_flags(rewards, GUIDE_REWARDS_BYTES)
            base['recent'] = _fit_guide_recent(recent)
        if 'run' in incoming:
            run = _guide_run(incoming['run'])
            if run:
                base['run'] = run
            else:
                base.pop('run', None)
    base['v'] = 1
    dumped = _guide_dump(base)
    if len(dumped) > GUIDE_JSON_MAX:
        raise ValueError('guide_json too large')
    return dumped


def normalize_theme_preference(value):
    if value in THEME_CHOICES:
        return value
    return THEME_SYSTEM


def normalize_motion_preference(value):
    if value in MOTION_CHOICES:
        return value
    return MOTION_SYSTEM


def normalize_celebration_mode(value):
    if value in CELEBRATION_MODES:
        return value
    return CELEBRATION_FULL


def normalize_zorp_sound(value):
    # Anything else, including the not-yet-offered `chatter`, is stored and rendered as off.
    if value in ZORP_SOUND_CHOICES:
        return value
    return ZORP_SOUND_OFF

ACTIVITY_TOPIC_OPENED = 'topic_opened'
ACTIVITY_QUESTION_GENERATED = 'question_generated'
ACTIVITY_MCQ_ANSWERED = 'mcq_answered'
ACTIVITY_QUIZ_COMPLETED = 'quiz_completed'
ACTIVITY_QUESTION_SHARED = 'question_shared'
ACTIVITY_SUGGESTION_SENT = 'suggestion_sent'
ACTIVITY_LESSON_STEP_COMPLETED = 'lesson_step_completed'
# E10 phase 4 (2026-11-08): a set-work question answered for the first time. Always private (never in a feed); it only adds one
# effort point and a study day. The payload is the assignment id and nothing else.
ACTIVITY_SET_WORK_ANSWERED = 'set_work_answered'
# E11 Phase 2 (docs/BADGES_AND_CELEBRATIONS_PLAN.md section 3, the Recovery line): a practice question got right after a wrong try on
# the same question, and one got right after opening its bigger hint. Always private (never in a feed: FEED_EVENT_TYPES lists what
# feeds show), no effort points, payload level, subject and topic only. Recorded once per question by the check routes in app.py.
ACTIVITY_RETRY_CORRECT = 'retry_correct'
ACTIVITY_HINT_CORRECT = 'hint_correct'

FEED_FILTER_ALL = 'all'
FEED_FILTER_LESSONS = 'lessons'
FEED_FILTER_QUIZZES = 'quizzes'
FEED_FILTER_SHARES = 'shares'
FEED_FILTER_CHOICES = (
    FEED_FILTER_ALL,
    FEED_FILTER_LESSONS,
    FEED_FILTER_QUIZZES,
    FEED_FILTER_SHARES,
)

FEED_EVENT_TYPES = {
    FEED_FILTER_ALL: (
        ACTIVITY_QUIZ_COMPLETED,
        ACTIVITY_LESSON_STEP_COMPLETED,
        ACTIVITY_QUESTION_SHARED,
        ACTIVITY_TOPIC_OPENED,
    ),
    FEED_FILTER_LESSONS: (ACTIVITY_LESSON_STEP_COMPLETED,),
    FEED_FILTER_QUIZZES: (ACTIVITY_QUIZ_COMPLETED,),
    FEED_FILTER_SHARES: (ACTIVITY_QUESTION_SHARED,),
}

FEED_DEFAULT_LIMIT = 50
FEED_MAX_LIMIT = 100
SEARCH_MAX_LIMIT = 50
SEARCH_DEFAULT_LIMIT = 20
SEARCH_MIN_QUERY_LEN = 2


def _like_escape(value):
    return (
        (value or '')
        .replace('\\', '\\\\')
        .replace('%', '\\%')
        .replace('_', '\\_')
    )


def _bool_int(value):
    return 1 if value else 0


def ensure_user_profile(conn, user_id):
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_profile_settings (user_id)
        VALUES (?)
        ''',
        (user_id,),
    )
    conn.execute(
        '''
        INSERT OR IGNORE INTO user_activity_summary (user_id)
        VALUES (?)
        ''',
        (user_id,),
    )
    conn.commit()


def get_profile_settings(conn, user_id):
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        '''
        SELECT profile_visibility, show_member_since, show_last_topic,
               show_last_activity, show_lesson_progress, show_quiz_stats,
               show_shared_questions, auto_share_quiz, auto_share_lesson,
               default_share_visibility, show_study_streak, show_milestones,
               email_weekly_digest, avatar_json, show_accuracy_leaderboard,
               sound_enabled, theme_preference, motion_preference, zorp_sound,
               guide_json, zorp_outfit_json, celebration_mode, perfect_as_card
        FROM user_profile_settings
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    data = dict(row) if row else {}
    data['avatar'] = parse_avatar(data.get('avatar_json'))
    data['celebration_mode'] = normalize_celebration_mode(data.get('celebration_mode'))
    data['perfect_as_card'] = bool(data.get('perfect_as_card'))
    data['guide'] = public_guide_state(data.get('guide_json'))
    data['guide_json_persisted'] = guide_json_is_stored(data.get('guide_json'))
    data['welcome'] = welcome_state(data.get('guide_json'))
    return data


def update_profile_settings(conn, user_id, settings):
    ensure_user_profile(conn, user_id)

    visibility = settings.get('profile_visibility', VISIBILITY_FOLLOWERS)
    if visibility not in VISIBILITY_CHOICES:
        visibility = VISIBILITY_FOLLOWERS
    share_visibility = settings.get('default_share_visibility', VISIBILITY_FOLLOWERS)
    if share_visibility not in VISIBILITY_CHOICES:
        share_visibility = VISIBILITY_FOLLOWERS
    theme_preference = normalize_theme_preference(settings.get('theme_preference', THEME_SYSTEM))
    motion_preference = normalize_motion_preference(settings.get('motion_preference', MOTION_SYSTEM))
    zorp_sound = normalize_zorp_sound(settings.get('zorp_sound', ZORP_SOUND_OFF))
    celebration_mode = normalize_celebration_mode(settings.get('celebration_mode', CELEBRATION_FULL))
    existing = conn.execute(
        'SELECT avatar_json, guide_json FROM user_profile_settings WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    if 'avatar' in settings or settings.get('avatar_json'):
        avatar_json = avatar_to_json(
            settings.get('avatar') or parse_avatar(settings.get('avatar_json'))
        )
    else:
        avatar_json = (existing['avatar_json'] if existing else '') or avatar_to_json({})
    if 'guide' in settings:
        guide_json = merge_guide_json(
            existing['guide_json'] if existing else '',
            settings.get('guide'),
        )
    else:
        guide_json = (existing['guide_json'] if existing else '') or '{}'
    conn.execute(
        '''
        UPDATE user_profile_settings
        SET profile_visibility = ?,
            show_member_since = ?,
            show_last_topic = ?,
            show_last_activity = ?,
            show_lesson_progress = ?,
            show_quiz_stats = ?,
            show_shared_questions = ?,
            auto_share_quiz = ?,
            auto_share_lesson = ?,
            default_share_visibility = ?,
            show_study_streak = ?,
            show_milestones = ?,
            email_weekly_digest = ?,
            avatar_json = ?,
            show_accuracy_leaderboard = ?,
            sound_enabled = ?,
            theme_preference = ?,
            motion_preference = ?,
            zorp_sound = ?,
            guide_json = ?,
            celebration_mode = ?,
            perfect_as_card = ?
        WHERE user_id = ?
        ''',
        (
            visibility,
            _bool_int(settings.get('show_member_since', True)),
            _bool_int(settings.get('show_last_topic', False)),
            _bool_int(settings.get('show_last_activity', False)),
            _bool_int(settings.get('show_lesson_progress', False)),
            _bool_int(settings.get('show_quiz_stats', False)),
            _bool_int(settings.get('show_shared_questions', True)),
            _bool_int(settings.get('auto_share_quiz', False)),
            _bool_int(settings.get('auto_share_lesson', False)),
            share_visibility,
            _bool_int(settings.get('show_study_streak', False)),
            _bool_int(settings.get('show_milestones', False)),
            _bool_int(settings.get('email_weekly_digest', False)),
            avatar_json,
            _bool_int(settings.get('show_accuracy_leaderboard', True)),
            _bool_int(settings.get('sound_enabled', False)),
            theme_preference,
            motion_preference,
            zorp_sound,
            guide_json,
            celebration_mode,
            _bool_int(settings.get('perfect_as_card', False)),
            user_id,
        ),
    )
    conn.commit()


def record_activity_event(conn, user_id, event_type, payload, visibility=VISIBILITY_FOLLOWERS):
    if visibility not in VISIBILITY_CHOICES:
        visibility = VISIBILITY_FOLLOWERS
    now = utc_now_iso()
    conn.execute(
        '''
        INSERT INTO user_activity_events (
            user_id, event_type, payload_json, visibility, created_at
        ) VALUES (?, ?, ?, ?, ?)
        ''',
        (
            user_id,
            event_type,
            json.dumps(payload or {}),
            visibility,
            now,
        ),
    )
    conn.commit()


def list_activity_events(conn, user_id, limit=20):
    rows = conn.execute(
        '''
        SELECT id, event_type, payload_json, visibility, created_at
        FROM user_activity_events
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('payload_json', None) or '{}'
        try:
            data['payload'] = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data['payload'] = {}
        out.append(data)
    return out


RECENT_PRACTISED_LIMIT = 8
RECENT_PRACTISED_SCAN = 80
RECENT_PRACTISED_EVENTS = (
    ACTIVITY_QUESTION_GENERATED,
    ACTIVITY_TOPIC_OPENED,
    ACTIVITY_QUIZ_COMPLETED,
    ACTIVITY_LESSON_STEP_COMPLETED,
    ACTIVITY_MCQ_ANSWERED,
)


def list_recent_practised_topics(conn, user_id, *, limit=RECENT_PRACTISED_LIMIT, scan=RECENT_PRACTISED_SCAN):
    """Distinct topics the user practised, newest first (for the home chip strip)."""
    rows = conn.execute(
        '''
        SELECT payload_json, created_at
        FROM user_activity_events
        WHERE user_id = ?
          AND event_type IN (?, ?, ?, ?, ?)
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        ''',
        (user_id, *RECENT_PRACTISED_EVENTS, scan),
    ).fetchall()
    out = []
    seen = set()
    for row in rows:
        try:
            payload = json.loads(row['payload_json'] or '{}')
        except (TypeError, ValueError, json.JSONDecodeError):
            payload = {}
        level = payload.get('level')
        subject = payload.get('subject')
        topic = payload.get('topic')
        if not topic:
            continue
        key = (level, subject, topic)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            'level': level,
            'subject': subject,
            'topic': topic,
            'topic_label': payload.get('topic_label') or '',
            'difficulty': payload.get('difficulty') or '',
            'last_at': row['created_at'],
        })
        if len(out) >= limit:
            break
    return out


def normalize_feed_filter(value):
    if value in FEED_FILTER_CHOICES:
        return value
    return FEED_FILTER_ALL


def list_followed_feed(
    conn,
    viewer_id,
    filter_name=FEED_FILTER_ALL,
    limit=FEED_DEFAULT_LIMIT,
    before_id=None,
):
    """Activity events from users the viewer follows (feed timeline)."""
    filter_name = normalize_feed_filter(filter_name)
    limit = min(max(int(limit), 1), FEED_MAX_LIMIT)
    event_types = FEED_EVENT_TYPES[filter_name]
    placeholders = ','.join('?' * len(event_types))
    before_clause = ''
    params = [viewer_id, viewer_id, viewer_id, VISIBILITY_PRIVATE, *event_types]
    if before_id is not None:
        before_clause = 'AND e.id < ?'
        params.append(int(before_id))
    params.append(limit)
    rows = conn.execute(
        f'''
        SELECT e.id, e.user_id, e.event_type, e.payload_json, e.visibility, e.created_at,
               u.handle AS actor_handle, ups.avatar_json AS actor_avatar_json
        FROM user_activity_events e
        JOIN users u ON u.id = e.user_id
        LEFT JOIN user_profile_settings ups ON ups.user_id = e.user_id
        WHERE e.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
        )
          AND e.user_id NOT IN (
            SELECT blocked_id FROM user_blocks WHERE blocker_id = ?
            UNION
            SELECT blocker_id FROM user_blocks WHERE blocked_id = ?
          )
          AND e.visibility != ?
          AND e.event_type IN ({placeholders})
          {before_clause}
        ORDER BY e.id DESC
        LIMIT ?
        ''',
        params,
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('payload_json', None) or '{}'
        try:
            data['payload'] = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data['payload'] = {}
        data['avatar'] = parse_avatar(data.pop('actor_avatar_json', None))
        out.append(data)
    return out


def get_activity_summary(conn, user_id):
    ensure_user_profile(conn, user_id)
    row = conn.execute(
        '''
        SELECT last_topic_level, last_topic_subject, last_topic_topic,
               last_topic_label, last_topic_at,
               last_activity_type, last_activity_level, last_activity_subject,
               last_activity_topic, last_activity_label, last_activity_at
        FROM user_activity_summary
        WHERE user_id = ?
        ''',
        (user_id,),
    ).fetchone()
    return dict(row) if row else {}


def record_topic_opened(conn, user_id, level, subject, topic, topic_label):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_topic_level = ?,
            last_topic_subject = ?,
            last_topic_topic = ?,
            last_topic_label = ?,
            last_topic_at = ?
        WHERE user_id = ?
        ''',
        (level, subject, topic, topic_label or '', now, user_id),
    )
    conn.commit()


def record_question_generated(conn, user_id, level, subject, topic, topic_label, difficulty):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    if difficulty:
        label = f'{label} ({difficulty})'
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_QUESTION_GENERATED,
            level,
            subject,
            topic,
            f'Practised: {label}',
            now,
            user_id,
        ),
    )
    conn.commit()


def record_mcq_answered(conn, user_id, level, subject, topic, topic_label, correct, *,
                        score=None, score_total=None):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    if score_total is not None and score is not None and not correct:
        outcome = f'{score}/{score_total}'
    else:
        outcome = 'Correct' if correct else 'Incorrect'
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_MCQ_ANSWERED,
            level,
            subject,
            topic,
            f'MCQ: {label} — {outcome}',
            now,
            user_id,
        ),
    )
    conn.commit()


def record_quiz_completed(conn, user_id, level, subject, topic, topic_label, score, total):
    ensure_user_profile(conn, user_id)
    now = utc_now_iso()
    label = topic_label or topic.replace('_', ' ').title()
    conn.execute(
        '''
        UPDATE user_activity_summary
        SET last_activity_type = ?,
            last_activity_level = ?,
            last_activity_subject = ?,
            last_activity_topic = ?,
            last_activity_label = ?,
            last_activity_at = ?
        WHERE user_id = ?
        ''',
        (
            ACTIVITY_QUIZ_COMPLETED,
            level,
            subject,
            topic,
            f'Quiz: {label} — {score}/{total}',
            now,
            user_id,
        ),
    )
    conn.commit()


def is_following(conn, follower_id, following_id):
    if not follower_id or not following_id:
        return False
    row = conn.execute(
        '''
        SELECT 1 FROM follows
        WHERE follower_id = ? AND following_id = ?
        ''',
        (follower_id, following_id),
    ).fetchone()
    return row is not None


def follow_user(conn, follower_id, following_id):
    if follower_id == following_id:
        return False
    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT OR IGNORE INTO follows (follower_id, following_id, created_at)
        VALUES (?, ?, ?)
        ''',
        (follower_id, following_id, now),
    )
    conn.commit()
    return cursor.rowcount > 0


def unfollow_user(conn, follower_id, following_id):
    cursor = conn.execute(
        '''
        DELETE FROM follows
        WHERE follower_id = ? AND following_id = ?
        ''',
        (follower_id, following_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def follower_count(conn, user_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM follows WHERE following_id = ?',
        (user_id,),
    ).fetchone()
    return row['n'] if row else 0


def following_count(conn, user_id):
    row = conn.execute(
        'SELECT COUNT(*) AS n FROM follows WHERE follower_id = ?',
        (user_id,),
    ).fetchone()
    return row['n'] if row else 0


def list_followers(conn, user_id, limit=50):
    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at, f.created_at AS followed_at
        FROM follows f
        JOIN users u ON u.id = f.follower_id
        WHERE f.following_id = ?
        ORDER BY f.created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def list_following(conn, user_id, limit=50):
    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at, f.created_at AS followed_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
        ORDER BY f.created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def can_view_profile(conn, viewer_id, target_user_id, settings):
    if viewer_id and viewer_id == target_user_id:
        return True
    from models.moderation import is_blocked
    if is_blocked(conn, viewer_id, target_user_id):
        return False
    visibility = settings.get('profile_visibility', VISIBILITY_FOLLOWERS)
    if visibility == VISIBILITY_PRIVATE:
        return False
    if visibility == VISIBILITY_FOLLOWERS:
        return is_following(conn, viewer_id, target_user_id)
    return True


def get_user_by_handle(conn, handle):
    return User.get_by_handle(conn, handle)


def search_users_by_handle(
    conn,
    query,
    *,
    viewer_id=None,
    limit=SEARCH_DEFAULT_LIMIT,
    exclude_user_id=None,
):
    query = normalize_handle(query)
    if len(query) < SEARCH_MIN_QUERY_LEN:
        return []

    limit = min(max(int(limit), 1), SEARCH_MAX_LIMIT)
    pattern = f'%{_like_escape(query)}%'
    prefix_pattern = f'{_like_escape(query)}%'

    sql = '''
        SELECT id, handle, created_at
        FROM users
        WHERE is_active = 1
          AND handle LIKE ? ESCAPE '\\'
    '''
    params = [pattern]
    if exclude_user_id is not None:
        sql += ' AND id != ?'
        params.append(exclude_user_id)
    sql += " AND handle != 'problem_bot' COLLATE NOCASE"
    sql += '''
        ORDER BY
            CASE
                WHEN handle = ? COLLATE NOCASE THEN 0
                WHEN handle LIKE ? ESCAPE '\\' COLLATE NOCASE THEN 1
                ELSE 2
            END,
            handle COLLATE NOCASE
        LIMIT ?
    '''
    params.extend([query, prefix_pattern, limit])

    rows = conn.execute(sql, params).fetchall()
    results = []
    for row in rows:
        settings = get_profile_settings(conn, row['id'])
        accessible = can_view_profile(conn, viewer_id, row['id'], settings)
        item = {
            'handle': row['handle'],
            'profile_accessible': accessible,
            'avatar': settings.get('avatar') or parse_avatar(None),
        }
        if accessible and settings.get('show_member_since'):
            created = row['created_at'] or ''
            item['member_since'] = created[:10] if created else None
        if viewer_id is not None and viewer_id != row['id']:
            item['viewer_follows'] = is_following(conn, viewer_id, row['id'])
        results.append(item)
    return results


def search_following_by_handle(conn, follower_id, query, *, limit=8):
    """Handles among people the viewer follows (for suggest-to-friend autocomplete)."""
    query = normalize_handle(query)
    if not query:
        return []

    limit = min(max(int(limit), 1), SEARCH_MAX_LIMIT)
    pattern = f'%{_like_escape(query)}%'
    prefix_pattern = f'{_like_escape(query)}%'

    rows = conn.execute(
        '''
        SELECT u.id, u.handle, u.created_at
        FROM follows f
        JOIN users u ON u.id = f.following_id
        WHERE f.follower_id = ?
          AND u.is_active = 1
          AND u.handle LIKE ? ESCAPE '\\'
        ORDER BY
            CASE
                WHEN u.handle = ? COLLATE NOCASE THEN 0
                WHEN u.handle LIKE ? ESCAPE '\\' COLLATE NOCASE THEN 1
                ELSE 2
            END,
            u.handle COLLATE NOCASE
        LIMIT ?
        ''',
        (follower_id, pattern, query, prefix_pattern, limit),
    ).fetchall()

    results = []
    for row in rows:
        settings = get_profile_settings(conn, row['id'])
        item = {
            'handle': row['handle'],
            'profile_accessible': True,
            'avatar': settings.get('avatar') or parse_avatar(None),
            'viewer_follows': True,
        }
        if settings.get('show_member_since'):
            created = row['created_at'] or ''
            item['member_since'] = created[:10] if created else None
        results.append(item)
    return results


def lesson_progress_summary(conn, user_id, limit=8):
    rows = conn.execute(
        '''
        SELECT level, subject, topic, section_key, section_label,
               completed_keys_json, updated_at
        FROM lesson_progress
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    out = []
    for row in rows:
        data = dict(row)
        raw = data.pop('completed_keys_json', None) or '[]'
        try:
            keys = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            keys = []
        if not isinstance(keys, list):
            keys = []
        data['completed_count'] = len([k for k in keys if isinstance(k, str) and k.strip()])
        out.append(data)
    return out


def quiz_stats_summary(conn, user_id, limit=5):
    rows = conn.execute(
        '''
        SELECT level, subject, topic, score, total, created_at
        FROM quiz_attempts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''',
        (user_id, limit),
    ).fetchall()
    return [dict(row) for row in rows]
