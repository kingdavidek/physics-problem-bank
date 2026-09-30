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
        'look-side', 'side',
    ),
    'brows': ('none', 'soft', 'raised', 'raised-l', 'worried', 'determined', 'skeptical', 'knit',
              'side', 'side-up', 'side-w'),
    'mouth': (
        'smile', 'smile-w', 'smile-wide', 'smile-big', 'grin', 'grin-tongue', 'laugh', 'cat',
        'smirk', 'tiny', 'o', 'wow', 'flat', 'wavy', 'wobble-smile', 'sleepy', 'blep', 'frown-soft',
        'side-smile', 'side-grin', 'side-o',
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

# models/buddy.py prompt types -> preset. D4 (streak_risk -> heads-up) switches in Phase 5, so
# the legacy streak_risk name still maps to itself here.
PROMPT_FACES = {
    'nudge': 'nudge',
    'milestone': 'milestone',
    'celebrate': 'celebrate',
    'qotd_nudge': 'qotd_nudge',
    'streak_risk': 'streak_risk',
    'weak_topic': 'weak_topic',
    'friend_challenge': 'friend_challenge',
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
    'react.streak': ('joy', 'proud', 'heads-up'),
    'react.milestone': ('proud', 'wow', 'aww'),
    'react.lesson_complete': ('love', 'happy'),
    'react.first_correct': ('wow', 'joy'),
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
GUIDE_LORE_STEPS = ()  # step ids in static/js/guide-catalog.js that may use a negative face (Phase 5 copy)
# Contexts where a negative preset is never allowed (docs/ZORP_EXPRESSIVENESS.md §5).
BANNED_CONTEXTS_FOR_NEGATIVE = ('prompt.', 'react.', 'dismiss', 'idle', 'autoplay.', 'notification')
NEGATIVE_ALLOWED = ('guide.lore', 'guide.reward.big', 'clip.dance.trip', 'clip.dizzy', 'styleguide')


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
    'side': _view(
        plate=(8, 0, .5, 1), eyeL=_HIDE, eyeR=(6.5, 0, 1, 1), brows=(6.5, 0, 1, 1), mouth=(10, 0, 1, 1),
        cheeks=(0, 0, 1, 1), fxFace=(7, 0, 1, 1), antL=(7, 0, 1, 1), antR=(3, 0, 1, 1), hl=(2, 0, 1, 1),
        footL=(4, 0, 1, 1), footR=(-2, 0, 1, 1), armL=_HIDE, armR=_HIDE, armRf=(-20, 2, 1, 1), armLf=_HIDE,
    ),
    'back': _view(plate=_HIDE, eyeL=_HIDE, eyeR=_HIDE, brows=_HIDE, mouth=_HIDE, cheeks=_HIDE, fxFace=_HIDE,
                  hl=(20, 0, 1, 1)),
    'back-glance': _view(
        plate=(-11, 0, .4, 1), eyeL=(-8, 0, -1, 1), eyeR=_HIDE, brows=_HIDE, mouth=_HIDE, cheeks=_HIDE,
        fxFace=_HIDE, hl=(20, 0, 1, 1),
    ),
}
# Parts a side view draws with dedicated art instead of the front variant (channel -> {id: id}).
# Unlisted ids keep their front art, moved by the row's translate. Ids listed here must exist.
_SIDE_EYES = dict.fromkeys(('open', 'open-lift', 'open-big', 'open-off', 'curious', 'curious-r', 'low', 'low-r',
                            'look-up', 'look-side'), 'side')
_SIDE_MOUTH = {
    'smile': 'side-smile', 'smile-w': 'side-smile', 'smile-wide': 'side-smile', 'smile-big': 'side-smile',
    'smirk': 'side-smile', 'tiny': 'side-smile', 'cat': 'side-smile', 'wobble-smile': 'side-smile',
    'grin': 'side-grin', 'grin-tongue': 'side-grin', 'laugh': 'side-grin', 'blep': 'side-grin',
    'o': 'side-o', 'wow': 'side-o', 'sleepy': 'side-o',
}
_SIDE_BROWS = {
    'soft': 'side', 'determined': 'side', 'knit': 'side', 'raised': 'side-up', 'skeptical': 'side-up',
    'raised-l': 'none', 'worried': 'side-w',
}
_SIDE_CHEEKS = {'rosy': 'side-rosy', 'glow': 'side-glow', 'blush': 'side-blush'}
_SIDE_MAP = {'eyes': _SIDE_EYES, 'mouth': _SIDE_MOUTH, 'brows': _SIDE_BROWS, 'cheeks': _SIDE_CHEEKS}
VIEW_VARIANTS = {
    'side': _SIDE_MAP,
    # over-the-shoulder look: one edge eye only (the mouth, brows and cheeks are hidden)
    'back-glance': {'eyes': _SIDE_EYES},
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


def view_styles(view, facing=None):
    """Inline style text per VIEW_PARTS key, plus 'flip', for a static render of `view`.
    Empty for the default (front, right) so the default markup carries no style attributes."""
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
    return styles


def map_variant(view, channel, vid):
    """The variant id a view draws for a channel variant (front art unless the view remaps it)."""
    return VIEW_VARIANTS.get(view, {}).get(channel, {}).get(vid, vid)

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
        'c': {'guide': list(CONTEXT_MAP['guide']), 'guide.lore': list(CONTEXT_MAP['guide.lore'])},
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
    text = PARTS_TEMPLATE.read_text(encoding='utf-8')
    for channel, ids in CHANNELS.items():
        assert len(set(ids)) == len(ids), f'duplicate variant in {channel}'
        for vid in ids:
            if vid == 'none':
                continue  # 'none' is deliberately empty art
            assert f"'{vid}'" in text, f'zorp_parts.html has no {channel}:{vid}'
    return True
