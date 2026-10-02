"""Zorp expression data (E8 Phase 1-3, docs/ZORP_EXPRESSIVENESS.md §4.3).

The live rig (templates/partials/buddy.html) draws one face from channels: eyes (left and
right), brows, mouth, cheeks and fx. A preset is a named combination of those channel
variants. This module is the single source of truth for the data; the art for every variant
lives in templates/partials/zorp_parts.html, and static/js/zorp-motion.js reads the same
presets from the JSON data island built by rig_json().

Rules that hold for every phase:
* the eight legacy face names stay valid forever;
* unknown names fail closed to 'nudge' (resolve_preset);
* every preset carries a valence, and negative presets are kept out of prompt, reaction,
  dismissal and idle contexts (docs/ZORP_EXPRESSIVENESS.md §5). Phase 2 ships four of them
  (sad, aww-teary, embarrassed, dizzy), all kept to CONTEXT_MAP contexts in NEGATIVE_ALLOWED.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS_TEMPLATE = ROOT / 'templates' / 'partials' / 'zorp_parts.html'

# Variant ids per channel. A right-eye sibling is the same id plus "-r" (drawn mirrored or
# offset for the right side); it is listed here so it gets a part in the library too.
CHANNELS = {
    'eyes': (
        'open', 'open-lift', 'open-big', 'open-off', 'curious', 'curious-r', 'low', 'low-r',
        'wink-line', 'happy-arc', 'smile-arc', 'laugh', 'laugh-r', 'wide', 'goo', 'half',
        'closed', 'closed-r', 'goo-shine', 'squint', 'sparkle', 'heart', 'spiral', 'look-up',
        'look-side', 'side', 'side-up', 'side-fwd',
    ),
    'brows': ('none', 'soft', 'raised', 'raised-l', 'worried', 'determined', 'skeptical', 'knit',
              'side', 'side-up', 'side-w'),
    'mouth': (
        'smile', 'smile-w', 'smile-wide', 'smile-big', 'grin', 'grin-tongue', 'laugh', 'cat',
        'smirk', 'tiny', 'o', 'wow', 'flat', 'wavy', 'wobble-smile', 'sleepy', 'blep', 'frown-soft',
        'side-smile', 'side-grin', 'side-o', 'side-flat', 'side-wavy', 'side-frown',
    ),
    'cheeks': ('none', 'rosy', 'blush', 'glow', 'side-rosy', 'side-glow', 'side-blush'),
    'fx': (
        'none', 'stars', 'flame', 'zzz', 'sparkles', 'sweat', 'tear-shine', 'blush-steam', 'hearts',
        'exclaim', 'question', 'dizzy-orbit', 'notes', 'bulb', 'thought',
    ),
}
# Channel-matrix review view (styleguide): the main eye and mouth variants; asymmetric legacy
# eye offsets (open-lift, open-off, curious, low) are left out.
MATRIX_EYES = ('open', 'open-big', 'goo', 'goo-shine', 'happy-arc', 'smile-arc', 'laugh', 'wink-line',
               'wide', 'half', 'closed', 'squint', 'sparkle', 'heart', 'spiral', 'look-up', 'look-side')
MATRIX_MOUTHS = ('smile', 'smile-wide', 'grin', 'grin-tongue', 'laugh', 'cat', 'smirk', 'tiny', 'o', 'wow',
                 'flat', 'wavy', 'wobble-smile', 'sleepy', 'blep', 'frown-soft')
# fx that are drawn inside the face group (they move with the head); every other fx sits in the
# ambient slot outside the head. Shipped to the runtime in the island ("ff").
FX_FACE = ('sweat', 'tear-shine', 'blush-steam')
# Order used by the JSON island arrays: [eyeL, eyeR, brows, mouth, cheeks, fx, valence].
SLOTS = ('eyeL', 'eyeR', 'brows', 'mouth', 'cheeks', 'fx')
SLOT_CHANNEL = {'eyeL': 'eyes', 'eyeR': 'eyes', 'brows': 'brows', 'mouth': 'mouth', 'cheeks': 'cheeks', 'fx': 'fx'}

POSITIVE, NEUTRAL, NEGATIVE = 'positive', 'neutral', 'negative'
_VAL_CODE = {POSITIVE: '+', NEUTRAL: '0', NEGATIVE: '-'}


def _p(eyes, brows='none', mouth='smile', cheeks='none', fx='none', eye_r=None):
    """One preset. `eyes` is the left eye; the right eye is `eye_r`, else `eyes`-r when that
    sibling exists, else the same variant."""
    right = eye_r or (eyes + '-r' if eyes + '-r' in CHANNELS['eyes'] else eyes)
    return {'eyeL': eyes, 'eyeR': right, 'brows': brows, 'mouth': mouth, 'cheeks': cheeks, 'fx': fx}


_HEADS_UP = _p('open-big', 'raised', 'smile', 'none', 'flame')

PRESETS = {
    # Legacy names (E6/E7 face allowlist plus the E7 Phase 4 sleep face).
    'nudge': _p('open'),
    'milestone': _p('open-lift', 'none', 'smile-wide', 'none', 'stars'),
    'celebrate': _p('happy-arc', 'none', 'smile-big', 'rosy'),
    'qotd_nudge': _p('curious', 'raised-l', 'o'),
    # D4: the frown is gone; the legacy name now draws the upbeat heads-up look.
    'streak_risk': dict(_HEADS_UP),
    'weak_topic': _p('low', 'skeptical', 'flat'),
    'friend_challenge': _p('wink-line', 'none', 'smile-w', eye_r='open-off'),
    'sleep': _p('closed', 'none', 'sleepy', 'none', 'zzz'),
    # New in Phase 1.
    'soft-smile': _p('open', 'soft', 'smile'),
    'grin': _p('open-big', 'none', 'grin'),
    'happy': _p('smile-arc', 'soft', 'smile-wide', 'rosy'),
    'joy': _p('happy-arc', 'raised', 'grin-tongue', 'rosy', 'sparkles'),
    'laugh': _p('laugh', 'raised', 'laugh', 'rosy'),
    'smug': _p('half', 'skeptical', 'smirk'),
    'wow': _p('wide', 'raised', 'wow', 'none', 'exclaim'),
    'aww': _p('goo', 'worried', 'wobble-smile', 'glow'),
    'bashful': _p('smile-arc', 'worried', 'tiny', 'blush', 'blush-steam'),
    'determined': _p('squint', 'determined', 'smile'),
    'heads-up': dict(_HEADS_UP),
    # Phase 2.
    'proud': _p('sparkle', 'soft', 'smile-wide', 'glow', 'sparkles'),
    'love': _p('heart', 'soft', 'smile-wide', 'glow', 'hearts'),
    'curious': _p('open', 'raised', 'o', 'none', 'question'),
    'thinking': _p('look-up', 'knit', 'flat', 'none', 'thought'),
    'confused': _p('look-side', 'skeptical', 'wavy', 'none', 'question'),
    'oops': _p('wide', 'worried', 'wavy'),
    'embarrassed': _p('half', 'worried', 'wavy', 'blush', 'sweat'),
    'aww-teary': _p('goo-shine', 'worried', 'wobble-smile', 'rosy', 'tear-shine'),
    'sad': _p('goo-shine', 'worried', 'frown-soft', 'none', 'tear-shine'),
    'dizzy': _p('spiral', 'none', 'wavy', 'none', 'dizzy-orbit'),
    'sleepy': _p('half', 'none', 'sleepy'),
    'wink': _p('open', 'soft', 'smirk', eye_r='wink-line'),
}

LEGACY_FACES = (
    'nudge', 'milestone', 'celebrate', 'qotd_nudge', 'streak_risk', 'weak_topic',
    'friend_challenge', 'sleep',
)
NEW_PRESETS = tuple(name for name in PRESETS if name not in LEGACY_FACES)

VALENCE = {
    'nudge': NEUTRAL, 'milestone': POSITIVE, 'celebrate': POSITIVE, 'qotd_nudge': NEUTRAL,
    'streak_risk': POSITIVE, 'weak_topic': NEUTRAL, 'friend_challenge': POSITIVE, 'sleep': NEUTRAL,
    'soft-smile': POSITIVE, 'grin': POSITIVE, 'happy': POSITIVE, 'joy': POSITIVE,
    'laugh': POSITIVE, 'smug': POSITIVE, 'wow': POSITIVE, 'aww': POSITIVE, 'bashful': POSITIVE,
    'determined': POSITIVE, 'heads-up': POSITIVE,
    'proud': POSITIVE, 'love': POSITIVE, 'curious': NEUTRAL, 'thinking': NEUTRAL,
    'confused': NEUTRAL, 'oops': NEUTRAL, 'embarrassed': NEGATIVE, 'aww-teary': NEGATIVE,
    'sad': NEGATIVE, 'dizzy': NEGATIVE, 'sleepy': NEUTRAL, 'wink': POSITIVE,
}

# models/buddy.py prompt types -> preset (E8 Phase 5). Every prompt face is upbeat: D4 moves streak_risk to
# the heads-up look (raised brows, soft smile, flame), and no prompt ever draws a negative preset. 'nudge' is
# the neutral resting default (the buddy shows nothing when no real trigger applies). study-buddy.js keeps a
# copy of this table (PROMPT_FACE) for the client-side render; test_prompt_faces_match_client pins the two.
PROMPT_FACES = {
    'nudge': 'nudge',
    'milestone': 'proud',
    'celebrate': 'happy',
    'qotd_nudge': 'wink',
    'streak_risk': 'heads-up',
    'weak_topic': 'determined',
    'friend_challenge': 'wink',   # review 2026-09-30: not smug (half lids + skeptical brow read as taunting a friend)
}
CONTEXT_MAP = {'prompt.' + kind: (face,) for kind, face in PROMPT_FACES.items()}
# Where each preset may appear (docs/ZORP_EXPRESSIVENESS.md §3.7, §4.3). react.* rotates
# positives only; blush and sweat are Zorp's own bashfulness and never appear there.
CONTEXT_MAP.update({
    'react.correct': ('grin', 'joy', 'happy', 'smug'),
    # A wrong answer may END only on these two. 'oops' is the first beat (at most 300 ms, neutral)
    # and has its own context below, so no react.wrong resolution can stop on it (review 2026-09-29).
    'react.wrong': ('determined', 'soft-smile'),
    'react.wrong.first': ('oops',),
    # Phase 5: each list covers every preset the kind's clips draw (test_react_clips_use_context_map).
    'react.streak': ('determined', 'joy', 'grin', 'proud'),
    'react.milestone': ('proud', 'aww', 'happy', 'wow', 'grin'),
    'react.lesson_complete': ('love', 'happy'),
    'react.first_correct': ('determined', 'wow', 'joy', 'happy'),
    'dismiss': ('soft-smile', 'nudge'),
    'autoplay.empty': ('thinking', 'curious', 'nudge'),
    'clip.dance.trip': ('embarrassed', 'laugh'),
    'clip.dizzy': ('dizzy', 'laugh'),
    'guide.reward.big': ('aww-teary', 'aww', 'happy'),
})
# Guide steps: any non-negative preset except the slapstick/lore ones below; lore steps
# (allowlisted ids, GUIDE_LORE_STEPS) may also open on those and on 'sad', and must resolve to a
# positive preset on their last line (step.resolve).
# Zorp's own slapstick and lore faces (docs/ZORP_EXPRESSIVENESS.md section 5): kept out of plain
# guide steps, allowed in lore steps, and 'bashful' also when Zorp is thanked or praised.
SLAPSTICK_LORE_ONLY = ('confused', 'bashful')
CONTEXT_MAP['guide'] = tuple(n for n in PRESETS if VALENCE[n] != NEGATIVE and n not in SLAPSTICK_LORE_ONLY)
CONTEXT_MAP['guide.lore'] = CONTEXT_MAP['guide'] + SLAPSTICK_LORE_ONLY + ('sad',)
CONTEXT_MAP['guide.thanks'] = ('bashful', 'happy', 'aww')
CONTEXT_MAP['styleguide'] = tuple(PRESETS)
GUIDE_LORE_STEPS = ('origin.home',)  # step ids in static/js/guide-catalog.js that may use a negative face (Phase 5 copy, for David's review)
# Contexts where a negative preset is never allowed (docs/ZORP_EXPRESSIVENESS.md §5).
BANNED_CONTEXTS_FOR_NEGATIVE = ('prompt.', 'react.', 'dismiss', 'idle', 'autoplay.', 'notification')
NEGATIVE_ALLOWED = ('guide.lore', 'guide.reward.big', 'clip.dance.trip', 'clip.dizzy', 'styleguide')

# Phase 5: which clips answer each react() kind (the runtime table in zorp-poses.js is pinned to this by
# test_react_plan_matches_runtime; faces come from CONTEXT_MAP['react.<kind>']). Correct answers rotate the
# small clips; only the rarer big moments get a big clip, and BIG_CLIPS never start within BIG_GAP_MS of each
# other (a second one inside the window becomes a small 'cheer'). 'wrong' is the sympathetic oops-encourage.
REACT_CLIPS = {
    'correct': ('cheer', 'hop', 'wave'),
    'wrong': ('oops-encourage',),
    'streak': ('fist-pump',),
    'first_correct': ('victory',),
    'milestone': ('flex', 'wave'),
    'lesson_complete': ('dance',),
}
BIG_CLIPS = ('fist-pump', 'victory', 'flex', 'dance')
BIG_GAP_MS = 7000
REACT_FACES = {'lesson_complete': 'love'}   # the dance shows love (hearts) where its beats say laugh; never a trip
# Positive or neutral clips a server-rendered element may start with data-zorp-autoplay (zorp-triggers.js
# keeps the same list; test_autoplay_allowlist_matches_runtime). No wobble, no oops, no dance trip, no sleep.
AUTOPLAY_CLIPS = ('think', 'think-chin', 'shrug', 'peek', 'wave', 'nod', 'wink', 'float', 'hop', 'cheer', 'flex', 'side-point')


# ---------------------------------------------------------------------------------------------
# Views (E8 Phase 3, docs/ZORP_EXPRESSIVENESS.md section 3.8). A view is a per-part resting
# transform plus visibility, written as the CSS individual transform properties `translate` and
# `scale` (they compose with the `transform` that clips and E6 gestures animate, so no clip ever
# loses its view). Values are for a Zorp facing RIGHT; facing LEFT is the same art mirrored by
# `g.zorp-flip` (scale -1 1 around x = 32). Ambient fx sit outside the flip and never mirror.
# ---------------------------------------------------------------------------------------------
VIEW_PARTS = (
    'plate', 'eyeL', 'eyeR', 'brows', 'mouth', 'cheeks', 'fxFace',
    'antL', 'antR', 'hl', 'footL', 'footR',
    'armL', 'armR', 'armLf', 'armRf',   # back-layer arms, then the front-layer twins (after the feet)
)
FRONT_HIDDEN = ('armLf', 'armRf')  # hidden by motion.css in the front view; a view shows them with display:inline
VIEW_NAMES = ('front', 'three-quarter', 'side', 'back', 'back-glance')
FACINGS = ('r', 'l')
_ID = (0, 0, 1, 1)  # visible, no change: (dx, dy, sx, sy)
_HIDE = None


def _view(**parts):
    row = {k: _ID for k in VIEW_PARTS}
    for k in FRONT_HIDDEN:
        row[k] = _HIDE
    row.update(parts)
    return row


VIEWS = {
    'front': _view(),
    'three-quarter': _view(
        plate=(3.5, 0, .85, 1), eyeL=(4.5, 0, .82, 1), eyeR=(3, 0, 1, 1), brows=(3.5, 0, .85, 1),
        mouth=(3.5, 0, .85, 1), cheeks=(3.5, 0, .85, 1), fxFace=(3.5, 0, 1, 1),
        antL=(4, 0, 1, 1), hl=(-2, 0, 1, 1), footL=(3, -.5, 1, 1), armL=(2, 0, 1, 1),
    ),
    # Side (E8 Phase 4 revision, 2026-09-30): a wide profile plate (about two thirds of the front plate,
    # its outer edge just inside the silhouette), the near eye and mouth forward on it, cheeks behind the
    # mouth, ONE arm (armRf, the near arm, front layer: the side-rest paddle) hanging from just behind the plate and
    # pointing a little forward, the far arm hidden, the feet overlapping with the near one forward, the antennae
    # drawn together and back. Face fx are placed by motion.css ([data-view="side"]), not by a row.
    'side': _view(
        plate=(7.6, 0, .66, 1), eyeL=_HIDE, eyeR=(6.5, 0, 1, 1), brows=(6.5, 0, 1, 1), mouth=(11, 0, 1, 1),
        cheeks=(-4, 0, 1, 1), antL=(3.5, 0, 1, 1), antR=(-4, 0, 1, 1), hl=(2, 0, 1, 1),
        footL=(6, 0, 1, 1), footR=(-1, 0, 1, 1), armL=_HIDE, armR=_HIDE, armRf=(-19.4, 2, 1, 1), armLf=_HIDE,
    ),
    'back': _view(plate=_HIDE, eyeL=_HIDE, eyeR=_HIDE, brows=_HIDE, mouth=_HIDE, cheeks=_HIDE, fxFace=_HIDE,
                  hl=(20, 0, 1, 1)),
    # Over-the-shoulder look (2026-09-30): a rounded partial plate, inset 3.5 px from the silhouette, holding the
    # mirrored profile eye and a hint of smile near its outer edge.
    'back-glance': _view(
        plate=(-9.8, 0, .56, 1), eyeL=(-6.5, 0, -1, 1), eyeR=_HIDE, brows=_HIDE, mouth=(-12.5, 0, -1, 1),
        cheeks=_HIDE, fxFace=_HIDE, hl=(20, 0, 1, 1),
    ),
}
# Parts a side view draws with dedicated art instead of the front variant (channel -> {id: id}).
# Unlisted ids keep their front art, moved by the row's translate. Ids listed here must exist.
_SIDE_EYES = dict.fromkeys(('open', 'open-lift', 'open-big', 'open-off', 'curious', 'curious-r', 'low', 'low-r'), 'side')
_SIDE_EYES.update({'look-up': 'side-up', 'look-side': 'side-fwd'})
_SIDE_MOUTH = {
    'smile': 'side-smile', 'smile-w': 'side-smile', 'smile-wide': 'side-smile', 'smile-big': 'side-smile',
    'smirk': 'side-smile', 'tiny': 'side-smile', 'cat': 'side-smile', 'wobble-smile': 'side-smile',
    'grin': 'side-grin', 'grin-tongue': 'side-grin', 'laugh': 'side-grin', 'blep': 'side-grin',
    'o': 'side-o', 'wow': 'side-o', 'sleepy': 'side-o',
    'flat': 'side-flat', 'wavy': 'side-wavy', 'frown-soft': 'side-frown',
}
_SIDE_BROWS = {
    'soft': 'side', 'determined': 'side', 'knit': 'side', 'raised': 'side-up', 'skeptical': 'side-up',
    'raised-l': 'none', 'worried': 'side-w',
}
_SIDE_CHEEKS = {'rosy': 'side-rosy', 'glow': 'side-glow', 'blush': 'side-blush'}
_SIDE_MAP = {'eyes': _SIDE_EYES, 'mouth': _SIDE_MOUTH, 'brows': _SIDE_BROWS, 'cheeks': _SIDE_CHEEKS}
VIEW_VARIANTS = {
    'side': _SIDE_MAP,
    # over-the-shoulder look: the profile eye and mouth (brows and cheeks are hidden)
    'back-glance': {'eyes': _SIDE_EYES, 'mouth': _SIDE_MOUTH},
}
DEFAULT_VIEW, DEFAULT_FACING = 'front', 'r'


def resolve_view(view, facing=None):
    """(view, facing) for any input; unknown views fall back to front, unknown facings to right.
    The front view has no facing (always right): a mirrored front would swap its highlight."""
    view = view if isinstance(view, str) and view in VIEWS else DEFAULT_VIEW
    facing = 'l' if facing == 'l' else DEFAULT_FACING
    return view, (DEFAULT_FACING if view == DEFAULT_VIEW else facing)


def _n(value):
    text = f'{value:g}'
    return text[1:] if text.startswith('0.') else ('-' + text[2:] if text.startswith('-0.') else text)


def rest_css(entry):
    """CSS declarations for one VIEWS entry (None = hidden)."""
    if entry is None:
        return 'display:none'
    dx, dy, sx, sy = entry
    out = []
    if (dx, dy) != (0, 0):
        out.append(f'translate:{_n(dx)}px {_n(dy)}px')
    if (sx, sy) != (1, 1):
        out.append(f'scale:{_n(sx)} {_n(sy)}')
    return ';'.join(out)


def view_styles(view, facing=None, pose=None):
    """Inline style text per VIEW_PARTS key, plus 'flip' and the pose keys root, head and shadow, for a
    static render of `view` (and of `pose` when given). Empty for the default (front, right, no
    pose) so the default markup carries no style attributes."""
    view, facing = resolve_view(view, facing)
    row = VIEWS[view]
    styles = {}
    for key in VIEW_PARTS:
        entry = row[key]
        if entry is None:
            styles[key] = '' if key in FRONT_HIDDEN else 'display:none'
        elif key in FRONT_HIDDEN:
            styles[key] = ';'.join(filter(None, ['display:inline', rest_css(entry)]))
        else:
            styles[key] = rest_css(entry)
    styles['flip'] = 'scale:-1 1' if facing == 'l' else ''
    styles.update(root='', head='', shadow='')
    if pose is not None:
        _add_pose(styles, row, resolve_pose(pose), facing, view)
    return styles


def _add_pose(styles, view_row, pose, facing, view):
    """Merge a pose's inline styles into a view's (see view_styles)."""
    ps = pose_styles(pose, facing, view)
    for key in ('root', 'head', 'shadow'):
        styles[key] = ps[key]
    for key in ('footL', 'footR'):
        styles[key] = ';'.join(filter(None, [styles[key], ps[key]]))
    for side in 'LR':
        back, front = f'arm{side}', f'arm{side}f'
        if POSES[pose][back][2] and view_row[back] is not None:
            # front-layer arm: the twin in front of the body is drawn, the one behind it is not
            styles[back] = 'display:none'
            styles[front] = ';'.join(filter(None, ['display:inline', ps[front]]))
        else:
            styles[back] = ';'.join(filter(None, [styles[back], ps[back]]))
            styles[front] = ';'.join(filter(None, [styles[front], ps[front]]))


def map_variant(view, channel, vid):
    """The variant id a view draws for a channel variant (front art unless the view remaps it)."""
    return VIEW_VARIANTS.get(view, {}).get(channel, {}).get(vid, vid)

# ---------------------------------------------------------------------------------------------
# Poses (E8 Phase 4, docs/ZORP_EXPRESSIVENESS.md sections 3.9 and 3.10). A pose is a resting
# transform per rig part plus an arm shape per arm, an optional default view and a preset hint.
# Rows are written in degrees and pixels for a Zorp facing RIGHT; the root sits outside the mirror
# wrapper, so a static render or the runtime flips its dx and rotation for facing LEFT. The pose
# table ships to the browser inside static/js/zorp-poses.js (poses_json() is the source of that
# embedded copy; scripts/test_zorp_poses_smoke.py fails when the two differ). Only `transform` is
# used for poses; views use the individual `translate`/`scale` properties, so the two compose.
#   root   (dx, dy, rot, sx, sy)   pivot: feet (transform-origin 50% 90%)
#   head   (dx, dy, rot)           armL / armR (shape, rot, front)   front = 1: draw the front-layer twin
#   footL / footR (dx, dy, rot)    shadow (sx, opacity)
# ---------------------------------------------------------------------------------------------
ARM_SHAPES = ('rest', 'straight', 'fist', 'bent', 'bent-fist', 'reach', 'palm')
SIDE_ARM = 'side-rest'   # the profile paddle: drawn instead of 'rest' in the side view, put back on any other view
# Shapes the side view draws with other art: the paddle for a resting arm, a profile 'bent' whose hand comes forward
# to the chin (think-chin) instead of reaching back behind the body, and the flex as a raised fist (a bent arm seen
# from the side would fold across the face).
SIDE_ARMS = {'rest': SIDE_ARM, 'bent': 'side-bent', 'bent-fist': 'fist', 'palm': 'straight'}   # palm (the open shrug hand) has no profile art: a straight arm
LIBRARY_ARM_SHAPES = ARM_SHAPES + (SIDE_ARM, 'side-bent')
POSE_PARTS = ('root', 'head', 'armL', 'armR', 'footL', 'footR', 'shadow')
STRETCH_MAX = .12  # squash and stretch: no axis deforms more than 12% (docs 3.10)
_R0, _H0, _F0, _S0, _A0 = (0, 0, 0, 1, 1), (0, 0, 0), (0, 0, 0), (1, 1), ('rest', 0, 0)


def _pose(root=_R0, head=_H0, armL=_A0, armR=_A0, footL=_F0, footR=_F0, shadow=_S0, view='', expr=''):
    return {'root': root, 'head': head, 'armL': armL, 'armR': armR, 'footL': footL, 'footR': footR,
            'shadow': shadow, 'view': view, 'expr': expr}


POSES = {
    'stand': _pose(view='front', expr='nudge'),
    'wave': _pose(head=(0, 0, 3), armR=('straight', -100, 0), expr='milestone'),
    # wave clip (readability pass 2026-10-02): the long arm raised beside the head, swinging between these two angles
    'wave-lo': _pose(root=(0, 0, 3, 1, 1), head=(0, 0, 4), armR=('reach', -120, 1), expr='milestone'),
    'wave-hi': _pose(root=(0, 0, 3, 1, 1), head=(0, 0, 4), armR=('reach', -176, 1), expr='milestone'),
    'point-l': _pose(head=(0, 0, -4), armL=('straight', 82, 0), expr='qotd_nudge'),
    'point-r': _pose(head=(0, 0, 4), armR=('straight', -82, 0), expr='qotd_nudge'),
    'point-down': _pose(head=(0, 0, 6), armR=('straight', -35, 0), expr='qotd_nudge'),
    'fist-up': _pose(root=(0, 0, 4, 1, 1), armR=('fist', -165, 1), expr='grin'),
    'victory': _pose(root=(0, 0, 0, 1, 1.02), armL=('fist', 160, 1), armR=('fist', -160, 1), expr='joy'),
    'flex': _pose(root=(0, 0, 0, 1, 1.03), armR=('bent-fist', -90, 1), armL=('bent-fist', 90, 1), expr='proud'),
    'flex-pump': _pose(root=(0, 0, -2, 1, 1.03), head=(0, 0, -3), armR=('bent-fist', -112, 1), armL=('bent-fist', 112, 1), expr='proud'),
    'think-chin': _pose(head=(0, 0, -6), armR=('bent', 0, 1), expr='thinking'),
    'shrug': _pose(root=(0, 0, 0, 1.03, .97), head=(0, 1.5, 6), armL=('palm', 14, 1), armR=('palm', -14, 1), expr='soft-smile'),
    'shrug-hi': _pose(root=(0, -1, 0, 1.03, .97), head=(0, 2.5, 8), armL=('palm', 30, 1), armR=('palm', -30, 1), expr='soft-smile'),
    'bow': _pose(root=(0, 0, 18, 1, 1), view='side', expr='bashful'),
    'peek': _pose(root=(-8, 0, 0, 1, 1), head=(0, 0, -10), expr='nudge'),
    'crouch': _pose(root=(0, 3, 0, 1.11, .89), armL=('rest', 14, 0), armR=('rest', -14, 0), expr='determined'),
    'dance-a': _pose(root=(0, 0, 9, 1, 1), head=(0, 0, -3), armL=('reach', 148, 1), armR=('rest', -16, 0), footR=(0, -4, 0), expr='laugh'),
    'dance-b': _pose(root=(0, 0, -9, 1, 1), head=(0, 0, 3), armL=('rest', 16, 0), armR=('reach', -148, 1), footL=(0, -4, 0), expr='laugh'),
    'dance-up': _pose(root=(0, 0, 0, 1, 1), armL=('reach', 160, 1), armR=('reach', -160, 1), footL=(0, -3, 0), footR=(0, -3, 0), expr='laugh'),
    'sit': _pose(root=(0, 3, 0, 1, .95), footL=(3, -1, 0), footR=(3, -1, 0), view='side', expr='happy'),
    'float': _pose(root=(0, -10, 0, 1, 1), armL=('rest', 26, 0), armR=('rest', -26, 0), footL=(0, 0, -8), footR=(0, 0, 8), shadow=(.7, .6), expr='happy'),
    'sleep': _pose(root=(0, 1.5, 0, 1, .98), head=(0, 0, 12), expr='sleep'),
}
POSE_NAMES = tuple(POSES)


def resolve_pose(name):
    """A known pose name, or 'stand' (fail closed)."""
    return name if isinstance(name, str) and name in POSES else 'stand'


def pose_view(name):
    """The pose's default view ('' = leave the view alone)."""
    return POSES[resolve_pose(name)]['view']


def static_view(view, pose):
    """The view a static render draws: an explicit `view` wins (front included); with none given a
    pose draws its own default view (bow and sit: side), and anything else the front."""
    if isinstance(view, str) and view in VIEWS:
        return view
    return (pose_view(pose) or DEFAULT_VIEW) if pose else DEFAULT_VIEW


def pose_arms(name, view=DEFAULT_VIEW):
    """(left shape, right shape) drawn for a pose in a view: the side view draws SIDE_ARMS art where it has some."""
    row = POSES[resolve_pose(name)]
    shapes = row['armL'][0], row['armR'][0]
    return tuple(SIDE_ARMS.get(s, s) if view == 'side' else s for s in shapes)


def side_rot(rot, shape='rest'):
    """The arm angle the side view draws for a pose or clip angle written for the front view (the same rule as
    sideRot in zorp-motion.js). The near arm hangs from behind the profile plate, so a raise that goes out to the
    side in the front view would sweep across the face in profile. Low angles (up to 40 deg) are kept, 40 to 70
    deg is held at 40 (down and forward, under the mouth), and a raise of 70 deg or more becomes an arm lifted
    over the top, 135 deg (up and forward, clear of the eye and brows) at 70 up to 179 deg at 180. It is written
    as the backward angle (360 - lift) so a tween from the hanging arm swings back and over the head, never
    through the face. A long arm (fist, reach, and bent-fist, which the side view draws as a fist) is held within
    10 deg of vertical so it clears the brows. The profile bent arm (side-bent) is drawn reaching the chin and is
    not turned. The left arm mirrors the right."""
    if shape == 'bent':
        return 0
    a = min(abs(rot), 180)
    if a < 70:
        return rot if a <= 40 else (-40 if rot < 0 else 40)
    out = round(225 - (a - 70) * .4, 2)
    if shape in ('fist', 'bent-fist', 'reach'):
        out = min(out, 190)
    return out if rot < 0 else -out


def _t(*vals):
    return ','.join(_n(v) for v in vals)


def pose_transform(part, row, facing='r', view=DEFAULT_VIEW):
    """The canonical CSS `transform` text for one part of a pose row; '' when it is the identity.
    The runtime builds the very same strings (zorp-poses.js). Arm angles go through side_rot() in the side view."""
    if part == 'root':
        dx, dy, rot, sx, sy = row
        if facing == 'l':
            dx, rot = -dx, -rot
        out = f'translate({_n(dx)}px,{_n(dy)}px) rotate({_n(rot)}deg) scale({_t(sx, sy)})'
        return '' if (dx, dy, rot, sx, sy) == _R0 else out
    if part in ('head', 'footL', 'footR'):
        dx, dy, rot = row
        return '' if (dx, dy, rot) == _H0 else f'translate({_n(dx)}px,{_n(dy)}px) rotate({_n(rot)}deg)'
    if part in ('armL', 'armR'):
        rot = side_rot(row[1], row[0]) if view == 'side' else row[1]
        return '' if rot == 0 else f'rotate({_n(rot)}deg)'
    sx, _, dy = row   # shadow (sx, opacity, dy): dy counters the root's lift so the shadow stays on the ground
    return '' if (sx, dy) == (1, 0) else f'translate(0,{_n(dy)}px) scale({_n(sx)},1)'


def pose_styles(name, facing='r', view=DEFAULT_VIEW):
    """Inline style text per rig key for a static render of a pose: root, head, footL, footR,
    shadow, armL, armR (armLf/armRf, the front-layer twins, carry the same arm transform)."""
    row = POSES[resolve_pose(name)]
    styles = {}
    for part in POSE_PARTS:
        css = pose_transform(part, tuple(row[part]) + ((-row['root'][1],) if part == 'shadow' else ()), facing, view)
        css = f'transform:{css}' if css else ''
        if part == 'shadow' and row[part][1] != 1:
            css = ';'.join(filter(None, [css, f'opacity:{_n(row[part][1])}']))
        styles[part] = css
    for side in 'LR':
        styles[f'arm{side}f'] = styles[f'arm{side}']
    return styles


def poses_json():
    """Compact JSON of the pose table, embedded in static/js/zorp-poses.js between its markers."""
    data = {}
    for name, row in POSES.items():
        data[name] = {
            'r': list(row['root']), 'h': list(row['head']), 'L': list(row['armL']), 'R': list(row['armR']),
            'fl': list(row['footL']), 'fr': list(row['footR']), 's': list(row['shadow']),
            'v': row['view'], 'e': row['expr'],
        }
    return json.dumps(data, separators=(',', ':'), ensure_ascii=True)


# Mouth swaps chosen by the automatic live look (models/zorp_kit.py LOOK_MOUTHS) replace the
# resting mouth of the 'nudge' face only.
LOOK_MOUTH_FACE = 'nudge'


def resolve_preset(name):
    """Return a known preset name, or 'nudge' (fail closed)."""
    if isinstance(name, str) and name in PRESETS:
        return name
    return 'nudge'


def preset(name):
    """Channel dict for a preset name (unknown -> nudge). Returns a fresh copy."""
    return dict(PRESETS[resolve_preset(name)])


def face_for_prompt(buddy_type):
    """Map a models/buddy.py prompt type to its preset name (unknown or empty -> nudge)."""
    if isinstance(buddy_type, str):
        return resolve_preset(PROMPT_FACES.get(buddy_type, 'nudge'))
    return 'nudge'


def valence(name):
    return VALENCE.get(resolve_preset(name), NEUTRAL)


def parts_for(name, mouth_override=None, view=DEFAULT_VIEW):
    """(eyeL, eyeR, brows, mouth, cheeks, fx) ids the server draws for a preset in a view."""
    ch = preset(name)
    if mouth_override and resolve_preset(name) == LOOK_MOUTH_FACE and mouth_override in CHANNELS['mouth']:
        ch['mouth'] = mouth_override
    view = resolve_view(view)[0]
    if view != DEFAULT_VIEW:
        for slot in ('eyeL', 'eyeR', 'brows', 'mouth', 'cheeks'):
            ch[slot] = map_variant(view, SLOT_CHANNEL[slot], ch[slot])
    return ch


def rig_json():
    """Compact JSON for the #pb-zorp-rig data island (read once by zorp-motion.js)."""
    presets = {}
    for name, ch in PRESETS.items():
        presets[name] = [ch[s] for s in SLOTS] + [_VAL_CODE[VALENCE[name]]]
    data = {
        'v': 1,
        'p': presets,
        # 'c': the guide allowlists guide.js and pbZorp.allowedIn() read; 'ff': face-attached fx.
        # Phase 5 adds the react.* lists (pbZorp.allowedIn for the reaction faces) and the big-reward list.
        'c': {k: list(v) for k, v in CONTEXT_MAP.items()
              if k in ('guide', 'guide.lore', 'guide.reward.big') or k.startswith('react.')},
        'ff': list(FX_FACE),
        # Phase 3: 'w' per-view rows, sparse (a part that is visible and unchanged is left out;
        # 0 = hidden, [dx, dy, sx, sy] = resting translate and scale), 'm' the side variant maps.
        'w': {v: {k: (0 if e is None else [e[0], e[1], e[2], e[3]])
                  for k, e in VIEWS[v].items() if e is None or tuple(e) != _ID}
              for v in VIEW_NAMES},
        'm': VIEW_VARIANTS,
    }
    # '<' is escaped so nothing in the island can ever close its <script> element early.
    return json.dumps(data, separators=(',', ':'), ensure_ascii=True).replace('<', '\\u003c')


def validate_poses():
    """Every pose defines every part with sane values (docs 3.9, 3.10)."""
    assert POSE_NAMES[0] == 'stand' and POSES['stand'] == _pose(view='front', expr='nudge')
    lens = {'root': 5, 'head': 3, 'footL': 3, 'footR': 3, 'shadow': 2, 'armL': 3, 'armR': 3}
    for name, row in POSES.items():
        assert set(row) == set(POSE_PARTS) | {'view', 'expr'}, f'pose {name}: keys {sorted(row)}'
        for part, size in lens.items():
            assert len(row[part]) == size, f'pose {name}.{part}'
        for side in ('armL', 'armR'):
            shape, rot, front = row[side]
            assert shape in ARM_SHAPES and front in (0, 1) and -190 <= rot <= 190, f'pose {name}.{side}'
        dx, dy, rot, sx, sy = row['root']
        assert abs(dx) <= 14 and abs(dy) <= 14 and abs(rot) <= 30, f'pose {name}.root'
        assert abs(sx - 1) <= STRETCH_MAX and abs(sy - 1) <= STRETCH_MAX, f'pose {name}: stretch beyond {STRETCH_MAX}'
        assert row['view'] in ('',) + VIEW_NAMES, f'pose {name}.view'
        assert row['expr'] == '' or (row['expr'] in PRESETS and VALENCE[row['expr']] != NEGATIVE), f'pose {name}.expr'
        assert 0 < row['shadow'][0] <= 1.2 and 0 <= row['shadow'][1] <= 1
    return True


def validate():
    """Consistency checks used by the smoke suite. Raises AssertionError on the first problem."""
    assert set(PRESETS) == set(VALENCE), 'every preset needs exactly one valence'
    for name in LEGACY_FACES:
        assert name in PRESETS, f'legacy face {name} missing'
    for name, ch in PRESETS.items():
        assert set(ch) == set(SLOTS), f'{name}: channels {sorted(ch)}'
        assert ch['eyeL'] in CHANNELS['eyes'] and ch['eyeR'] in CHANNELS['eyes'], name
        for key in ('brows', 'mouth', 'cheeks', 'fx'):
            assert ch[key] in CHANNELS[key], f'{name}: unknown {key} {ch[key]!r}'
        assert VALENCE[name] in _VAL_CODE, name
    for context, faces in CONTEXT_MAP.items():
        for face in faces:
            assert face in PRESETS, f'{context}: unknown preset {face}'
            if VALENCE[face] == NEGATIVE:
                assert context.startswith(NEGATIVE_ALLOWED), f'{context} may not use negative {face}'
            if context.startswith(BANNED_CONTEXTS_FOR_NEGATIVE):
                assert VALENCE[face] != NEGATIVE, f'{context} uses negative {face}'
    assert set(MATRIX_EYES) <= set(CHANNELS['eyes']) and set(MATRIX_MOUTHS) <= set(CHANNELS['mouth'])
    for fx_id in FX_FACE:
        assert fx_id in CHANNELS['fx'], fx_id
    for kind, face in PROMPT_FACES.items():
        assert face in PRESETS, f'prompt type {kind} maps to unknown preset {face}'
    # Phase 3: views are complete, sane and only remap to variants that exist.
    assert tuple(VIEWS) == VIEW_NAMES and VIEW_NAMES[0] == DEFAULT_VIEW
    for view, row in VIEWS.items():
        assert set(row) == set(VIEW_PARTS), f'view {view} parts {sorted(set(row) ^ set(VIEW_PARTS))}'
        for key, entry in row.items():
            assert entry is None or (len(entry) == 4 and all(isinstance(v, (int, float)) for v in entry)), (view, key)
            assert entry is None or (-40 <= entry[0] <= 40 and -40 <= entry[1] <= 40 and -2 <= entry[2] <= 2 and -2 <= entry[3] <= 2), (view, key)
    assert all(VIEWS[DEFAULT_VIEW][k] == _ID for k in VIEW_PARTS if k not in FRONT_HIDDEN)
    assert all(VIEWS[DEFAULT_VIEW][k] is None for k in FRONT_HIDDEN), 'front arms are hidden in the front view'
    for view, chans in VIEW_VARIANTS.items():
        assert view in VIEWS and view != DEFAULT_VIEW, view
        for channel, mapping in chans.items():
            for src, dst in mapping.items():
                assert src in CHANNELS[channel] and dst in CHANNELS[channel], (view, channel, src, dst)
    # Every mouth has profile art, so the side view always draws one (a front mouth moved by the row's
    # translate could run off the narrow profile plate).
    side_mouths = {map_variant('side', 'mouth', m) for m in CHANNELS['mouth']}
    assert all(m.startswith('side-') for m in side_mouths), sorted(side_mouths)
    validate_poses()
    text = PARTS_TEMPLATE.read_text(encoding='utf-8')
    for shape in LIBRARY_ARM_SHAPES[1:]:  # 'rest' is the macro's default branch
        assert f"'{shape}'" in text, f'zorp_parts.html has no arm:{shape}'
    for channel, ids in CHANNELS.items():
        assert len(set(ids)) == len(ids), f'duplicate variant in {channel}'
        for vid in ids:
            if vid == 'none':
                continue  # 'none' is deliberately empty art
            assert f"'{vid}'" in text, f'zorp_parts.html has no {channel}:{vid}'
    return True
