"""Zorp's wardrobe (E10 phase 6b, docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md section 11, owner's answer 8).

Badges unlock cosmetics the live rig already draws (models/zorp_kit.py LOOK_FIELDS: colours, antennae, feet, smiles, hats,
shoes); the pupil chooses what Zorp wears. This module owns the catalogue, the unlock rules, the server-side validation and
the storage format. Nothing here adds art: every value must be in zorp_kit.LOOK_FIELDS (scripts/test_wardrobe_smoke.py checks).

Storage: user_profile_settings.zorp_outfit_json. '' means the pupil never chose (Zorp keeps the automatic look that follows
the latest pose badge, zorp_kit.live_look). Otherwise {"v": 1, "<slot>": "<value>", ...} with only the non-default slots; an
outfit with no slots is a deliberate plain Zorp. The client is never trusted: validate_outfit() runs on every write, and
outfit_look() drops anything not unlocked again on every read.
"""
import json

from models import zorp_kit

STORAGE_VERSION = 1
MAX_JSON_BYTES = 400

# slot -> pupil-facing label. The order is the order on the page.
SLOTS = (
    ('colour', 'Colour'),
    ('antenna', 'Antennae'),
    ('feet', 'Feet'),
    ('mouth', 'Smile'),
    ('hat', 'Hat'),
    ('shoes', 'Shoes'),
)
SLOT_KEYS = tuple(k for k, _ in SLOTS)

# (slot, value, name, noun, unlock)
#   value '' is the slot's default (always available, the "Zorp as he comes" choice).
#   noun is what the badge stage says: "New in your wardrobe: <noun>."
#   unlock: None (always), ('badge', milestone_key) or ('family', family_key, label) for "any badge of that family".
_RAW = (
    ('colour', '', 'Zorp blue', 'the Zorp blue colour', None),
    ('colour', 'sunny', 'Sunny', 'the sunny colour', ('badge', 'qotd_first')),
    ('colour', 'mint', 'Mint', 'the mint colour', ('badge', 'topics_master_5')),
    ('colour', 'violet', 'Violet', 'the violet colour', ('badge', 'accuracy_top_friend')),
    ('antenna', '', 'Standard', 'the standard antennae', None),
    ('antenna', 'long', 'Long', 'the long antennae', ('badge', 'topics_10')),
    ('antenna', 'short', 'Short', 'the short antennae', ('family', 'subject', 'a subject badge')),
    ('feet', '', 'Standard', 'the standard feet', None),
    ('feet', 'big', 'Big', 'the big feet', ('badge', 'topics_completed_5')),
    ('mouth', '', 'Usual smile', 'the usual smile', None),
    ('mouth', 'grin', 'Wide grin', 'the wide grin', ('badge', 'questions_25')),
    ('mouth', 'cat', 'Cat smile', 'the cat smile', ('badge', 'topics_ninja_5')),
    ('hat', '', 'No hat', 'no hat', None),
    ('hat', 'mortarboard', 'Mortarboard', 'the mortarboard', ('badge', 'first_lesson_step')),
    ('hat', 'beanie', 'Beanie', 'the beanie', ('badge', 'app_tour')),
    ('shoes', '', 'No shoes', 'no shoes', None),
    ('shoes', 'sneakers', 'Sneakers', 'the sneakers', ('badge', 'streak_7')),
)


def _build():
    items = []
    for slot, value, name, noun, unlock in _RAW:
        items.append({
            'id': f'{slot}.{value or "default"}',
            'slot': slot,
            'value': value,
            'name': name,
            'noun': noun,
            'unlock': unlock,
        })
    return tuple(items)


ITEMS = _build()
BY_ID = {i['id']: i for i in ITEMS}
BY_SLOT_VALUE = {(i['slot'], i['value']): i for i in ITEMS}


def is_default(item):
    return item['value'] == ''


def _meta(key):
    from models.gamification import milestone_meta
    return milestone_meta(key)


def unlock_label(item):
    """What the pupil must earn, as words for 'Earn <this> to unlock'. '' for an always-available item."""
    rule = item['unlock']
    if not rule:
        return ''
    if rule[0] == 'badge':
        return _meta(rule[1]).get('title') or rule[1]
    return rule[2]


def unlock_badge_key(item):
    """The milestone key to open on the badge sheet for a locked item (None for a family rule or an open item)."""
    rule = item['unlock']
    return rule[1] if rule and rule[0] == 'badge' else None


def _earned_keys(conn, user_id):
    rows = conn.execute('SELECT milestone_key FROM user_milestones WHERE user_id = ?', (user_id,)).fetchall()
    return {r['milestone_key'] for r in rows}


def _satisfied_by(item, keys):
    """The subset of `keys` that unlocks `item` ('' rule -> all of them is not meaningful; callers skip open items)."""
    rule = item['unlock']
    if not rule:
        return set()
    if rule[0] == 'badge':
        return {rule[1]} & set(keys)
    return {k for k in keys if (_meta(k).get('family') or '') == rule[1]}


def unlocked_ids(conn, user_id):
    """Ids of the items this pupil may wear now."""
    keys = _earned_keys(conn, user_id)
    return {i['id'] for i in ITEMS if not i['unlock'] or _satisfied_by(i, keys)}


def items_unlocked_by(conn, user_id, milestone_key):
    """Items that `milestone_key` newly opens for this pupil (it is the only earned badge that satisfies the rule)."""
    keys = _earned_keys(conn, user_id)
    out = []
    for item in ITEMS:
        sat = _satisfied_by(item, keys)
        if sat == {milestone_key}:
            out.append(item)
    return out


def wardrobe_payload(conn, user_id, milestone_key):
    """What the badge stage needs for one badge: {'id', 'name', 'noun'} of the first item it opens, else None."""
    items = items_unlocked_by(conn, user_id, milestone_key)
    if not items:
        return None
    first = items[0]
    return {'id': first['id'], 'name': first['name'], 'noun': first['noun']}


# ---- storage -------------------------------------------------------------------------------------------------------

def parse_outfit(raw):
    """Stored text -> dict of non-default slot -> value, or None when the pupil never chose. Junk is treated as never chose."""
    if raw is None or not str(raw).strip():
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    out = {}
    for slot in SLOT_KEYS:
        value = data.get(slot)
        item = BY_SLOT_VALUE.get((slot, value)) if isinstance(value, str) else None
        if item and not is_default(item):
            out[slot] = value
    return out


def outfit_to_json(outfit):
    """Dict (already validated) -> stored text; None -> '' (never chose)."""
    if outfit is None:
        return ''
    body = {'v': STORAGE_VERSION}
    for slot in SLOT_KEYS:
        if outfit.get(slot):
            body[slot] = outfit[slot]
    return json.dumps(body, separators=(',', ':'))


def validate_outfit(conn, user_id, raw):
    """Check a client outfit against the catalogue and this pupil's badges.

    `raw` is a dict slot -> value ('' or missing = default). Returns (outfit, error): outfit is the cleaned dict of
    non-default slots, error is None or a (message, code) pair. Unknown slots, unknown values, non-strings and locked items
    are all refused and nothing is saved by the caller.
    """
    if not isinstance(raw, dict):
        return None, ('zorp_outfit must be an object or null', 'invalid_outfit')
    unknown = set(raw) - set(SLOT_KEYS)
    if unknown:
        return None, (f'Unknown outfit slot(s): {", ".join(sorted(str(k) for k in unknown))}', 'invalid_outfit')
    allowed = unlocked_ids(conn, user_id)
    out = {}
    for slot in SLOT_KEYS:
        value = raw.get(slot, '')
        if value is None:
            value = ''
        if not isinstance(value, str):
            return None, (f'{slot} must be text', 'invalid_outfit')
        item = BY_SLOT_VALUE.get((slot, value))
        if not item:
            return None, (f'Unknown {slot} item', 'invalid_outfit')
        if item['id'] not in allowed:
            return None, (f'{item["name"]} is not unlocked yet', 'locked_item')
        if not is_default(item):
            out[slot] = value
    return out, None


def save_outfit(conn, user_id, outfit):
    """Write an already validated outfit (dict) or None (back to the automatic look). Touches only this column."""
    conn.execute(
        'INSERT OR IGNORE INTO user_profile_settings (user_id) VALUES (?)', (user_id,),
    )
    conn.execute(
        'UPDATE user_profile_settings SET zorp_outfit_json = ? WHERE user_id = ?',
        (outfit_to_json(outfit), user_id),
    )
    conn.commit()


def outfit_look(conn, user_id, stored):
    """The look dict for buddy_mascot(look=...): the stored outfit minus anything no longer unlocked, or None when the pupil
    never chose (the caller then keeps the automatic look). Only values in zorp_kit.LOOK_FIELDS leave this function."""
    outfit = parse_outfit(stored)
    if outfit is None:
        return None
    if outfit:
        allowed = unlocked_ids(conn, user_id)
        outfit = {s: v for s, v in outfit.items() if BY_SLOT_VALUE[(s, v)]['id'] in allowed}
    return {s: v for s, v in outfit.items() if v in zorp_kit.LOOK_FIELDS.get(s, ())}


# ---- the page ------------------------------------------------------------------------------------------------------

def page_model(conn, user_id, stored, try_id=None):
    """Everything profile.html needs to draw the wardrobe panel: slots with items (locked state and reason), the saved outfit
    and the draft the panel opens with (the saved outfit, plus an unlocked `try_id` put on for a try-on that is not saved)."""
    allowed = unlocked_ids(conn, user_id)
    saved = outfit_look(conn, user_id, stored)
    draft = dict(saved or {})
    tried = BY_ID.get(try_id) if try_id else None
    if tried and tried['id'] in allowed:
        if is_default(tried):
            draft.pop(tried['slot'], None)
        else:
            draft[tried['slot']] = tried['value']
    slots = []
    for slot, label in SLOTS:
        rows = []
        for item in ITEMS:
            if item['slot'] != slot:
                continue
            locked = item['id'] not in allowed
            rows.append({
                'id': item['id'],
                'value': item['value'],
                'name': item['name'],
                'locked': locked,
                'reason': unlock_label(item) if locked else '',
                'badge': unlock_badge_key(item) if locked else None,
                'checked': (draft.get(slot, '') == item['value']),
            })
        slots.append({'key': slot, 'label': label, 'choices': rows})
    return {
        'slots': slots,
        'chose': saved is not None,
        'saved': saved or {},
        'draft': draft,
        'tried': tried['id'] if tried and tried['id'] in allowed else '',
    }
