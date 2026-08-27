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
    POSE_TOKENS,
    pose,
    resolve_pose,
)
from models.gamification import (  # noqa: E402
    MILESTONE_CATALOG,
    MILESTONE_FIRST_LESSON,
    MILESTONE_QOTD_FIRST,
    MILESTONE_STREAK_7,
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


def main():
    test_tokens_and_resolve()
    test_pose_markup()
    test_no_licensed_names()
    test_live_mascot_unchanged()
    test_proof_badges()
    test_styleguide_gallery()
    test_templates_use_kit()
    print('Zorp pose kit smoke OK')


if __name__ == '__main__':
    main()
