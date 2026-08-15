"""Emoji + colour avatars (engagement E2.2). No image uploads."""
from __future__ import annotations

import json

AVATAR_FACES = ('🙂', '😎', '🤓', '😺', '🦊', '🐸', '🐼', '🌙')
AVATAR_EXTRAS = ('', '🎓', '🎧', '⭐')
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
