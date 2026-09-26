"""Quick Test session storage and problem building."""
import json
import random
import uuid

from generators.shared.variant_utils import normalize_mode
from models.user import utc_now_iso

QUICKTEST_LENGTH = 10


def make_session_id(user_id=None):
    token = uuid.uuid4().hex
    if user_id:
        return f'qt_u{user_id}_{token}'
    return f'qt_a_{token}'


def build_quicktest_problems(level, subject, topic, mode, difficulty, topics_registry):
    """Return (problems, topic_config) or raise KeyError.

    Always builds ``QUICKTEST_LENGTH`` questions (pad by regenerating if a
    topic exposes fewer variants; sample if it exposes more).
    """
    topic_config = topics_registry[level][subject][topic]
    generator = topic_config['func']
    variants_func = topic_config.get('variants_func')
    mode = normalize_mode(mode)

    problems = []
    variant_list = []
    if variants_func:
        variant_list = list(variants_func(difficulty, mode) or [])
        if variant_list:
            if len(variant_list) >= QUICKTEST_LENGTH:
                chosen = random.sample(variant_list, QUICKTEST_LENGTH)
            else:
                chosen = list(variant_list)
            for variant_fn in chosen:
                problems.append(
                    generator(difficulty, mode, variant_name=variant_fn.__name__)
                )
            i = 0
            while len(problems) < QUICKTEST_LENGTH:
                variant_fn = variant_list[i % len(variant_list)]
                problems.append(
                    generator(difficulty, mode, variant_name=variant_fn.__name__)
                )
                i += 1
                if i > QUICKTEST_LENGTH * 8:
                    break
    while len(problems) < QUICKTEST_LENGTH:
        try:
            problems.append(generator(difficulty, mode, variant_name=None))
        except TypeError:
            if not (variants_func and variant_list):
                problems.append(generator(difficulty, mode))
            else:
                variant_fn = variant_list[len(problems) % len(variant_list)]
                problems.append(
                    generator(difficulty, mode, variant_name=variant_fn.__name__)
                )
    return problems[:QUICKTEST_LENGTH], topic_config


def save_quicktest_session(conn, session_id, data):
    now = utc_now_iso()
    payload = dict(data)
    payload['updated_at'] = now
    conn.execute(
        '''
        INSERT INTO quicktest_sessions (session_id, data)
        VALUES (?, ?)
        ON CONFLICT(session_id) DO UPDATE SET data = excluded.data
        ''',
        (session_id, json.dumps(payload)),
    )
    conn.commit()


def load_quicktest_session(conn, session_id):
    row = conn.execute(
        'SELECT data FROM quicktest_sessions WHERE session_id = ?',
        (session_id,),
    ).fetchone()
    if not row:
        return None
    return json.loads(row['data'])


def delete_quicktest_session(conn, session_id):
    conn.execute(
        'DELETE FROM quicktest_sessions WHERE session_id = ?',
        (session_id,),
    )
    conn.commit()


def session_owner_user_id(session_id):
    if session_id.startswith('qt_u') and session_id.count('_') >= 2:
        middle = session_id[4:]
        user_part = middle.split('_', 1)[0]
        if user_part.isdigit():
            return int(user_part)
    return None


def can_access_quicktest(data, session_id, viewer_user_id):
    owner = data.get('owner_user_id')
    if owner is None:
        owner = session_owner_user_id(session_id)
    if owner is not None:
        return viewer_user_id == owner
    return True
