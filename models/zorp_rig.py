"""Zorp expression data (E8 Phase 1, docs/ZORP_EXPRESSIVENESS.md §4.3).

The live rig (templates/partials/buddy.html) draws one face from channels: eyes (left and
right), brows, mouth, cheeks and fx. A preset is a named combination of those channel
variants. This module is the single source of truth for the data; the art for every variant
lives in templates/partials/zorp_parts.html, and static/js/zorp-motion.js reads the same
presets from the JSON data island built by rig_json().

Rules that hold for every phase:
* the eight legacy face names stay valid forever;
* unknown names fail closed to 'nudge' (resolve_preset);
* every preset carries a valence, and negative presets are kept out of prompt, reaction,
  dismissal and idle contexts (docs/ZORP_EXPRESSIVENESS.md §5). Phase 1 ships none.
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
        'closed', 'closed-r',
    ),
    'brows': ('none', 'soft', 'raised', 'raised-l', 'worried', 'determined', 'skeptical'),
    'mouth': (
        'smile', 'smile-w', 'smile-wide', 'smile-big', 'grin', 'grin-tongue', 'laugh', 'cat',
        'smirk', 'tiny', 'o', 'wow', 'flat', 'wavy', 'wobble-smile', 'sleepy',
    ),
    'cheeks': ('none', 'rosy', 'blush'),
    'fx': ('none', 'stars', 'flame', 'zzz', 'sparkles'),
}
# Order used by the JSON island arrays: [eyeL, eyeR, brows, mouth, cheeks, fx, valence].
SLOTS = ('eyeL', 'eyeR', 'brows', 'mouth', 'cheeks', 'fx')

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
    'wow': _p('wide', 'raised', 'wow'),
    'aww': _p('goo', 'worried', 'wobble-smile', 'rosy'),
    'bashful': _p('smile-arc', 'worried', 'tiny', 'blush'),
    'determined': _p('open', 'determined', 'smile'),
    'heads-up': dict(_HEADS_UP),
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
# Contexts where a negative preset is never allowed (docs/ZORP_EXPRESSIVENESS.md §5).
BANNED_CONTEXTS_FOR_NEGATIVE = ('prompt.', 'react.', 'dismiss', 'idle', 'autoplay.', 'notification')
NEGATIVE_ALLOWED = ('guide.lore', 'clip.dance.trip', 'clip.dizzy', 'styleguide')

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


def parts_for(name, mouth_override=None):
    """(eyeL, eyeR, brows, mouth, cheeks, fx) ids the server draws for a preset."""
    ch = preset(name)
    if mouth_override and resolve_preset(name) == LOOK_MOUTH_FACE and mouth_override in CHANNELS['mouth']:
        ch['mouth'] = mouth_override
    return ch


def rig_json():
    """Compact JSON for the #pb-zorp-rig data island (read once by zorp-motion.js)."""
    presets = {}
    for name, ch in PRESETS.items():
        presets[name] = [ch[s] for s in SLOTS] + [_VAL_CODE[VALENCE[name]]]
    return json.dumps({'v': 1, 'p': presets}, separators=(',', ':'), ensure_ascii=True)


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
    for kind, face in PROMPT_FACES.items():
        assert face in PRESETS, f'prompt type {kind} maps to unknown preset {face}'
    text = PARTS_TEMPLATE.read_text(encoding='utf-8')
    for channel, ids in CHANNELS.items():
        assert len(set(ids)) == len(ids), f'duplicate variant in {channel}'
        for vid in ids:
            if vid == 'none':
                continue  # 'none' is deliberately empty art
            assert f"'{vid}'" in text, f'zorp_parts.html has no {channel}:{vid}'
    return True
