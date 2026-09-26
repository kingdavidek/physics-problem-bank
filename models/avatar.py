"""Emoji + colour avatars (engagement E2.2 / E5.5). No image uploads."""
from __future__ import annotations

import json

AVATAR_FACES = ('🙂', '😎', '🤓', '😺', '🦊', '🐸', '🐼', '🌙')
AVATAR_EXTRAS = ('', '🎓', '🎧', '⭐')
AVATAR_EXTRA_REQUIREMENTS = {
    '🎓': 'topics_10',
    '🎧': 'questions_25',
    '⭐': 'streak_7',
}
AVATAR_BACKGROUNDS = (
    '#eef6fc',
    '#e8f4fd',
    '#eef7ee',
    '#fff8e6',
    '#fdf0f7',
    '#f4f6f9',
    '#dceaf4',
    '#edf7ef',
)
DEFAULT_AVATAR = {
    'face': '🙂',
    'bg': '#eef6fc',
    'extra': '',
}
BOT_AVATAR = {
    'face': '🤓',
    'bg': '#e8f4fd',
    'extra': '⭐',
}


def parse_avatar(raw):
    """Return a safe avatar dict from JSON text, a dict, or junk."""
    data = raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            data = None
    if not isinstance(data, dict):
        return dict(DEFAULT_AVATAR)
    face = data.get('face') if data.get('face') in AVATAR_FACES else DEFAULT_AVATAR['face']
    bg = data.get('bg') if data.get('bg') in AVATAR_BACKGROUNDS else DEFAULT_AVATAR['bg']
    extra = data.get('extra') if data.get('extra') in AVATAR_EXTRAS else ''
    return {'face': face, 'bg': bg, 'extra': extra}


def _user_has_milestone(conn, user_id, milestone_key):
    row = conn.execute(
        '''
        SELECT 1 FROM user_milestones
        WHERE user_id = ? AND milestone_key = ?
        LIMIT 1
        ''',
        (user_id, milestone_key),
    ).fetchone()
    return row is not None


def unlocked_extras(conn, user_id):
    """Extras the user may newly select (always includes empty)."""
    allowed = ['']
    for extra, milestone_key in AVATAR_EXTRA_REQUIREMENTS.items():
        if _user_has_milestone(conn, user_id, milestone_key):
            allowed.append(extra)
    return tuple(allowed)


def extra_unlock_title(extra):
    milestone_key = AVATAR_EXTRA_REQUIREMENTS.get(extra)
    if not milestone_key:
        return None
    from models.gamification import milestone_meta

    return milestone_meta(milestone_key).get(
        'title',
        milestone_key.replace('_', ' ').title(),
    )


def avatar_extra_options(conn, user_id, current_avatar):
    """Settings-page metadata for each gated extra."""
    current = parse_avatar(current_avatar)
    wearing = current.get('extra') or ''
    unlocked = set(unlocked_extras(conn, user_id))
    options = []
    for extra in AVATAR_EXTRAS:
        if not extra:
            continue
        title = extra_unlock_title(extra)
        may_select = extra in unlocked or extra == wearing
        options.append({
            'extra': extra,
            'disabled': not may_select,
            'unlock_title': title,
        })
    return options


def apply_avatar_extra_policy(conn, user_id, avatar, *, previous=None):
    """Reject newly selected locked extras; grandfather existing wearers."""
    parsed = parse_avatar(avatar)
    previous = parse_avatar(previous)
    extra = parsed.get('extra') or ''
    if not extra:
        return parsed
    if extra in unlocked_extras(conn, user_id):
        return parsed
    if extra == (previous.get('extra') or ''):
        return parsed
    parsed['extra'] = previous.get('extra') or ''
    return parsed


def avatar_to_json(avatar):
    return json.dumps(parse_avatar(avatar), ensure_ascii=False, separators=(',', ':'))


def avatars_for_user_ids(conn, user_ids):
    ids = [int(uid) for uid in user_ids if uid is not None]
    if not ids:
        return {}
    placeholders = ','.join('?' * len(ids))
    rows = conn.execute(
        f'''
        SELECT user_id, avatar_json
        FROM user_profile_settings
        WHERE user_id IN ({placeholders})
        ''',
        ids,
    ).fetchall()
    found = {row['user_id']: parse_avatar(row['avatar_json']) for row in rows}
    return {uid: found.get(uid, dict(DEFAULT_AVATAR)) for uid in ids}


def attach_avatars(conn, items, id_key='user_id'):
    mapping = avatars_for_user_ids(conn, [item.get(id_key) for item in items])
    for item in items:
        uid = item.get(id_key)
        item['avatar'] = mapping.get(uid, dict(DEFAULT_AVATAR))
    return items
