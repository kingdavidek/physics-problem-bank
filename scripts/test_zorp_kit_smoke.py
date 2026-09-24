"""Zorp pose kit smoke — stills, unknown→idle, no licensed names.

Run: python scripts/test_zorp_kit_smoke.py
"""
import os
import re
import sys
from pathlib import Path

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('PB_STYLEGUIDE', '1')

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models.zorp_kit import (  # noqa: E402
    ACTION_TOKENS,
    COSTUME_TOKENS,
    LIVE_LOOKS,
    LOOK_FIELDS,
    POSE_TOKENS,
    live_look,
    pose,
    resolve_pose,
)
from models.gamification import (  # noqa: E402
    MILESTONE_CATALOG,
    MILESTONE_FIRST_LESSON,
    MILESTONE_QOTD_FIRST,
    MILESTONE_STREAK_7,
    _pose_from_meta,
    latest_pose_milestone,
)
from app import app  # noqa: E402


BANNED = ('mickey', 'elvis', 'disney', 'steamboat')


def _kit_sources():
    paths = [
        ROOT / 'models' / 'zorp_kit.py',
        ROOT / 'templates' / 'partials' / 'zorp_kit.html',
        ROOT / 'templates' / 'partials' / 'zorp_badge.html',
        ROOT / 'templates' / 'styleguide.html',
        ROOT / 'docs' / 'ENGAGEMENT_VISUAL.md',
        ROOT / 'docs' / 'AI_HANDOFF.md',
    ]
    return '\n'.join(path.read_text(encoding='utf-8').lower() for path in paths)


def test_tokens_and_resolve():
    assert len(POSE_TOKENS) == 11
    assert ACTION_TOKENS == (
        'idle', 'run', 'jump', 'sing', 'eat', 'wave', 'think',
    )
    assert COSTUME_TOKENS == ('showman', 'scholar', 'explorer', 'chef')
    assert resolve_pose('JUMP') == 'jump'
    assert resolve_pose('nope') == 'idle'
    assert resolve_pose(None) == 'idle'
    assert resolve_pose('mickey') == 'idle'


def test_pose_markup():
    for token in POSE_TOKENS:
        markup = str(pose(token, size=64))
        assert markup.startswith('<svg ')
        assert f'zorp-pose--{token}' in markup
        assert 'viewBox="0 0 80 80"' in markup
        assert 'aria-hidden="true"' in markup
        assert '<ellipse' in markup or '<path' in markup
        assert '&lt;' not in markup
    labelled = str(pose('jump', size=28, title='Week warrior'))
    assert 'role="img"' in labelled
    assert 'aria-label="Week warrior"' in labelled
    assert 'aria-hidden' not in labelled
    unknown = str(pose('not-a-pose'))
    assert 'zorp-pose--idle' in unknown


def test_no_licensed_names():
    blob = _kit_sources()
    for word in BANNED:
        assert word not in blob, word


def test_live_mascot_unchanged():
    buddy = (ROOT / 'templates' / 'partials' / 'buddy.html').read_text(encoding='utf-8')
    faces = re.findall(r'buddy-face--([a-z0-9-]+)', buddy)
    assert faces == [
        'nudge',
        'milestone',
        'celebrate',
        'qotd-nudge',
        'streak-risk',
        'weak-topic',
        'friend-challenge',
    ]
    assert 'pose_run' not in buddy
    assert 'zorp-pose' not in buddy


def test_proof_badges():
    assert MILESTONE_CATALOG[MILESTONE_STREAK_7]['pose'] == 'jump'
    assert MILESTONE_CATALOG[MILESTONE_FIRST_LESSON]['pose'] == 'scholar'
    assert MILESTONE_CATALOG[MILESTONE_QOTD_FIRST]['pose'] == 'wave'
    assert 'pose' not in MILESTONE_CATALOG['first_quiz']


def test_live_looks():
    assert set(LIVE_LOOKS.keys()) <= set(POSE_TOKENS)
    for name, look in LIVE_LOOKS.items():
        for field, value in look.items():
            assert field in LOOK_FIELDS, (name, field)
            assert value in LOOK_FIELDS[field], (name, field, value)
    # resolve_pose is case-insensitive / dash-normalising, so live_look is too.
    assert live_look('JUMP') == live_look('jump')
    assert live_look('streak') == {}  # sanity: not a pose token, so idle -> {}
    assert live_look(None) == {}
    assert live_look('idle') == {}
    assert live_look('not-a-real-pose') == {}
    a = live_look('jump')
    b = live_look('jump')
    assert a == b
    assert a is not b
    assert a is not LIVE_LOOKS['jump']
    for key, meta in MILESTONE_CATALOG.items():
        pose_token = _pose_from_meta(meta)
        if pose_token:
            assert live_look(pose_token), (key, pose_token)


def test_latest_pose_milestone():
    import sqlite3

    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute(
        '''
        CREATE TABLE user_milestones (
            user_id INTEGER NOT NULL,
            milestone_key TEXT NOT NULL,
            earned_at TEXT NOT NULL,
            PRIMARY KEY (user_id, milestone_key)
        )
        '''
    )
    rows = [
        (1, 'first_quiz', '2026-01-01T00:00:00+00:00'),        # no pose
        (1, MILESTONE_FIRST_LESSON, '2026-01-02T00:00:00+00:00'),  # scholar
        (1, MILESTONE_STREAK_7, '2026-01-03T00:00:00+00:00'),      # jump, latest for user 1
        (2, MILESTONE_QOTD_FIRST, '2026-01-01T00:00:00+00:00'),    # wave, only pose milestone for user 2
        (2, 'first_quiz', '2026-01-05T00:00:00+00:00'),            # no pose, later but irrelevant
    ]
    conn.executemany(
        'INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, ?)',
        rows,
    )
    conn.commit()
    assert latest_pose_milestone(conn, 1) == 'jump'
    assert latest_pose_milestone(conn, 2) == 'wave'
    assert latest_pose_milestone(conn, 3) is None
    conn.close()


def test_styleguide_looks():
    client = app.test_client()
    response = client.get('/styleguide')
    assert response.status_code == 200
    html = response.data.decode()
    assert 'id="sg-zorp-looks"' in html
    for name, look in LIVE_LOOKS.items():
        if look.get('colour'):
            assert f'data-zorp-colour="{look["colour"]}"' in html, name
        if look.get('antenna'):
            assert f'data-zorp-antenna="{look["antenna"]}"' in html, name
        if look.get('feet'):
            assert f'data-zorp-feet="{look["feet"]}"' in html, name
        if look.get('mouth'):
            assert f'data-mouth="{look["mouth"]}"' in html, name


def test_base_passes_look():
    base = (ROOT / 'templates' / 'base.html').read_text(encoding='utf-8')
    guide = (ROOT / 'templates' / 'partials' / 'guide.html').read_text(encoding='utf-8')
    assert 'buddy_mascot(look=buddy_look)' in base
    assert 'buddy_mascot(look=buddy_look)' in guide


def test_styleguide_gallery():
    client = app.test_client()
    response = client.get('/styleguide')
    assert response.status_code == 200, response.data[:400]
    html = response.data.decode()
    assert 'id="sg-zorp-poses"' in html
    assert 'id="sg-zorp-costumes"' in html
    for token in POSE_TOKENS:
        assert f'zorp-pose--{token}' in html
        assert f'<code>{token}</code>' in html
    assert html.count('buddy-face--nudge') >= 1
    assert 'data-buddy-face' in html


def test_templates_use_kit():
    profile = (ROOT / 'templates' / 'profile.html').read_text(encoding='utf-8')
    public = (ROOT / 'templates' / 'public_profile.html').read_text(encoding='utf-8')
    assert 'zorp_badge_face' in profile
    assert 'zorp_badge_face' in public
    base = (ROOT / 'templates' / 'base.html').read_text(encoding='utf-8')
    assert 'zorp_kit.pose' not in base
    assert "partials/zorp_kit.html" not in base


def test_styleguide_localhost_without_env_flag():
    old_styleguide = os.environ.pop('PB_STYLEGUIDE', None)
    old_testing = os.environ.pop('PB_TESTING', None)
    try:
        client = app.test_client()
        response = client.get('/styleguide', headers={'Host': 'localhost:5001'})
        assert response.status_code == 200, response.status_code
    finally:
        if old_styleguide is not None:
            os.environ['PB_STYLEGUIDE'] = old_styleguide
        if old_testing is not None:
            os.environ['PB_TESTING'] = old_testing


def main():
    test_tokens_and_resolve()
    test_pose_markup()
    test_no_licensed_names()
    test_live_mascot_unchanged()
    test_proof_badges()
    test_live_looks()
    test_latest_pose_milestone()
    test_styleguide_looks()
    test_base_passes_look()
    test_styleguide_gallery()
    test_styleguide_localhost_without_env_flag()
    test_templates_use_kit()
    print('Zorp pose kit smoke OK')


if __name__ == '__main__':
    main()
