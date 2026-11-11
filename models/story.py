"""Zorp's story chapters (E10 phase 8, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A6 and section 11.13).

Six short chapters continue the arrival film. Which ones a pupil may watch is worked out here, on the server, from the badges the
pupil has earned (the count, or one specific kind of badge). Nothing is stored for it: the unlock is derived every time.

The only state is the "watched" and "offered" flags in the protected `tours` region of guide_json (`story_w<n>`, `story_o<n>`;
models/social.py never evicts that region), written by the client through the ordinary guide PATCH. The chapter scenes and
every word Zorp says are static/js/story-chapters.js; this file holds only what the server needs: number, id, title and the
unlock rule. scripts/test_story_chapters_smoke.py pins the two to each other.
"""

# Chapter 0 is the arrival film itself (always available; the shelf lists it first).
# `badges`: the number of badges that unlocks a chapter. `any_prefix` (optional): earning any badge whose key starts with this
# opens it too, whichever comes first. `alt` is the sentence the shelf shows for that second way in.
# 2026-11-10 (E11 Phase 2, David's answer 7): the counts went from 3, 5, 8, 10, 15, 20 to 3, 6, 10, 15, 22, 30, because the
# catalogue grew from 39 to 56 badges and the chapters would otherwise open too quickly.
CHAPTERS = (
    {'n': 1, 'id': 'belt', 'title': 'The maths belt', 'badges': 3},
    {'n': 2, 'id': 'crew', 'title': 'Meet the crew', 'badges': 6},
    {'n': 3, 'id': 'doors', 'title': 'Puzzle doors', 'badges': 10,
     'any_prefix': 'topic_master:', 'alt': 'Or earn a topic master badge.'},
    {'n': 4, 'id': 'home', 'title': 'Home', 'badges': 15},
    {'n': 5, 'id': 'logbook', 'title': 'The logbook', 'badges': 22},
    {'n': 6, 'id': 'postcard', 'title': 'A postcard from Novara', 'badges': 30,
     'any_prefix': 'subject_completed:', 'alt': 'Or earn a subject complete badge.'},
)

ARRIVAL_TITLE = 'Arrival'
FLAG_WATCHED = 'story_w'
FLAG_OFFERED = 'story_o'
OFFER_MOMENT_KIND = 'story_offer'


def unlock_label(chapter):
    return f"Unlocks at {chapter['badges']} badges"


def is_unlocked(chapter, earned_keys):
    """True when the earned badge keys open this chapter: enough badges, or one badge of the named kind."""
    earned = list(earned_keys or ())
    if len(earned) >= chapter['badges']:
        return True
    prefix = chapter.get('any_prefix')
    return bool(prefix) and any(str(k).startswith(prefix) for k in earned)


def unlocked_numbers(earned_keys):
    return [c['n'] for c in CHAPTERS if is_unlocked(c, earned_keys)]


def newly_unlocked(earned_now, new_keys):
    """Chapter numbers that these badges just opened: unlocked with them and not without them."""
    now = list(dict.fromkeys(earned_now or ()))
    new = set(new_keys or ())
    opened_before = set(unlocked_numbers([k for k in now if k not in new]))
    return [n for n in unlocked_numbers(now) if n not in opened_before]


def earned_keys(conn, user_id):
    rows = conn.execute('SELECT milestone_key FROM user_milestones WHERE user_id = ?', (user_id,)).fetchall()
    return [row['milestone_key'] for row in rows]


def offer_moment(n):
    """The toast moment that offers chapter n ("Zorp has a new story for you", Watch and Later). Never auto-plays."""
    return {'type': 'toast', 'kind': OFFER_MOMENT_KIND, 'id': f'story:{int(n)}', 'chapter': int(n)}


def _tours(guide_state):
    tours = (guide_state or {}).get('tours')
    return tours if isinstance(tours, dict) else {}


def watched(guide_state, n):
    return bool(_tours(guide_state).get(f'{FLAG_WATCHED}{n}'))


def any_story_flag(guide_state):
    """True once the pupil has been offered or has watched any chapter (the catch-up offer is then never made)."""
    return any(isinstance(k, str) and k.startswith('story_') and v for k, v in _tours(guide_state).items())


def catchup_chapter(earned, guide_state):
    """For a pupil who already had enough badges before chapters existed: the first unlocked chapter, once. None when the pupil
    has been offered or has watched anything (so Later is final until a new badge opens a new chapter) or has none unlocked."""
    if any_story_flag(guide_state):
        return None
    opened = unlocked_numbers(earned)
    return opened[0] if opened else None


def shelf(earned, guide_state):
    """Rows for the profile shelf: chapter 0 first, then the chapters in order. Every row: n, title, unlocked, watched, and for a
    locked chapter the `unlock` sentence and the optional `alt` sentence."""
    rows = [{'n': 0, 'title': ARRIVAL_TITLE, 'unlocked': True, 'watched': True, 'unlock': '', 'alt': ''}]
    for chapter in CHAPTERS:
        opened = is_unlocked(chapter, earned)
        rows.append({
            'n': chapter['n'],
            'title': chapter['title'],
            'unlocked': opened,
            'watched': opened and watched(guide_state, chapter['n']),
            'unlock': '' if opened else unlock_label(chapter),
            'alt': '' if opened else chapter.get('alt', ''),
        })
    return rows
