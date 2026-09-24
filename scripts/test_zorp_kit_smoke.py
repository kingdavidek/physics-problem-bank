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
    LOOK_HATS,
    LOOK_SHOES,
    OVERLAY_HATS,
    OVERLAY_SHOES,
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
        ROOT / 'templates' / 'partials' / 'zorp_overlays.html',
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
    # E7 Phase 1.6: the live rig shares overlay art with the pose kit via
    # zorp_overlays.html, but never imports the pose-kit template itself,
    # and the shared overlay file never leaks either character's own
    # drawing code — it stays genuinely overlay-only.
    assert 'partials/zorp_kit.html' not in buddy
    assert "import zorp_hat, zorp_shoe" in buddy or (
        'import zorp_hat' in buddy and 'import zorp_shoe' in buddy
    )
    assert 'partials/zorp_overlays.html' in buddy
    overlays = (ROOT / 'templates' / 'partials' / 'zorp_overlays.html').read_text(encoding='utf-8')
    for leaked in ('buddy-', 'zorp-pose', '_standing_body', '_nudge_face', 'pose_'):
        assert leaked not in overlays, leaked


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
    # E7 Phase 1.6: hat/shoes overlays, deliberately a subset of the full
    # overlay art catalogue (toque/quiff stay kit-only).
    assert LOOK_FIELDS['hat'] == LOOK_HATS
    assert LOOK_FIELDS['shoes'] == LOOK_SHOES
    assert set(LOOK_HATS) <= set(OVERLAY_HATS)
    assert set(LOOK_SHOES) <= set(OVERLAY_SHOES)
    # E7 Phase 1.6: toque/quiff are kit-only, not yet approved for the live rig -- pin
    # that LOOK_HATS/LOOK_SHOES stay a strict subset of OVERLAY_HATS/OVERLAY_SHOES,
    # not silently widened to include them.
    assert 'toque' not in LOOK_HATS and 'quiff' not in LOOK_HATS
    assert set(LOOK_HATS) < set(OVERLAY_HATS)
    assert live_look('scholar')['hat'] == 'mortarboard'
    assert live_look('wave')['hat'] == 'beanie'
    assert live_look('jump')['shoes'] == 'sneakers'


def test_overlay_macros():
    with app.app_context():
        module = app.jinja_env.get_template('partials/zorp_overlays.html').module
        for name in OVERLAY_HATS:
            rendered = str(module.zorp_hat(name, 5, 7))
            assert rendered.startswith(f'<g class="zorp-hat zorp-hat--{name}" transform="translate(5 7)">'), rendered
            assert rendered.count('<g') == 1
            assert rendered.endswith('</g>')
        for name in OVERLAY_SHOES:
            rendered = str(module.zorp_shoe(name, 5, 7))
            assert rendered.startswith(f'<g class="zorp-shoe zorp-shoe--{name}" transform="translate(5 7)">'), rendered
            assert rendered.count('<g') == 1
            assert rendered.endswith('</g>')
        for bad in (None, '', 'not-a-hat', 'mickey'):
            assert str(module.zorp_hat(bad, 5, 7)) == ''
            assert str(module.zorp_shoe(bad, 5, 7)) == ''


def test_kit_headwear_regression():
    # Pre-Phase-1.6 inline headwear markup for showman/scholar/chef, translated
    # by the shared anchor (40, 22.5) into the local frame the overlay macros
    # now use. Captured from the working tree before this phase's edits.
    expected = {
        'showman': '<g class="zorp-hat zorp-hat--quiff" transform="translate(40 22.5)">'
                    '<path d="M-12 -4.5q4 -10 12 -8q2 6 -2 10z" fill="var(--ink-800)"/></g>',
        'scholar': '<g class="zorp-hat zorp-hat--mortarboard" transform="translate(40 22.5)">'
                   '<rect x="-14" y="-14.5" width="28" height="5.5" rx="1" fill="var(--ink-800)"/>\n'
                   '<polygon points="0,-18.5 14,-9.5 0,-0.5 -14,-9.5" fill="var(--ink-800)"/>\n'
                   '<line x1="14" y1="-9.5" x2="14" y2="1.5" stroke="var(--gold-500)" stroke-width="1.6"/>\n'
                   '<circle cx="14" cy="3.5" r="2.1" fill="var(--gold-500)"/></g>',
        'chef': '<g class="zorp-hat zorp-hat--toque" transform="translate(40 22.5)">'
                '<ellipse cx="0" cy="-12.5" rx="11" ry="7.5" fill="var(--brand-50)" stroke="var(--ink-400)" stroke-width="1.2"/>\n'
                '<rect x="-7" y="-8.5" width="14" height="8" fill="var(--brand-50)" stroke="var(--ink-400)" stroke-width="1.2"/></g>',
    }
    for name, hat_markup in expected.items():
        markup = str(pose(name, size=80))
        assert hat_markup in markup, name
        # Paint order preserved, matching each pose's original order exactly.
        hat_idx = markup.index(hat_markup)
        body_idx = markup.index('<ellipse cx="40" cy="46"')  # face plate, part of _standing_body()
        assert body_idx < hat_idx
        if name == 'showman':
            # Original order: body, quiff, sparkles, face, feet — hat renders
            # before the sparkles and before the feet.
            sparkle_idx = markup.index('<circle cx="28" cy="36"')
            feet_idx = markup.rindex('var(--brand-700)"/>')
            assert hat_idx < sparkle_idx < feet_idx
        elif name == 'scholar':
            # Original order: body, face, feet, mortarboard — hat renders
            # after the feet (last thing in the pose).
            feet_idx = markup.rindex('var(--brand-700)"/>', 0, hat_idx)
            assert feet_idx < hat_idx
            assert hat_idx == markup.rindex(hat_markup)
        elif name == 'chef':
            # Original order: body, face, feet, toque, spoon — hat renders
            # after the feet, before the spoon prop.
            feet_idx = markup.rindex('var(--brand-700)"/>', 0, hat_idx)
            spoon_idx = markup.index('<g transform="translate(62 46) rotate(30)">')
            assert feet_idx < hat_idx < spoon_idx
    # explorer and all 7 action tokens carry no overlay gear at all.
    for name in ('explorer',) + ACTION_TOKENS:
        markup = str(pose(name, size=80))
        assert 'zorp-hat' not in markup, name
        assert 'zorp-shoe' not in markup, name


def test_live_overlay_matches_kit():
    from models import zorp_kit

    with app.app_context():
        buddy_module = app.jinja_env.get_template('partials/buddy.html').module
        rendered = str(buddy_module.buddy_mascot(zorp_kit.live_look('scholar')))
        last_face_idx = rendered.rindex('buddy-face--friend-challenge')
        hat_idx = rendered.index('zorp-hat--mortarboard')
        foot_idx = rendered.index('buddy-foot--l')  # feet are painted after the head closes
        assert last_face_idx < hat_idx < foot_idx
        assert 'translate(32 14.5)' in rendered

        jump_rendered = str(buddy_module.buddy_mascot(zorp_kit.live_look('jump')))
        assert jump_rendered.count('zorp-shoe--sneakers') == 2
        assert 'zorp-hat' not in jump_rendered
        left_foot_idx = jump_rendered.index('buddy-foot--l')
        right_foot_idx = jump_rendered.index('buddy-foot--r')
        left_shoe_idx = jump_rendered.index('translate(24 56.5)')
        right_shoe_idx = jump_rendered.index('translate(40 56.5)')
        assert left_foot_idx < left_shoe_idx < right_foot_idx < right_shoe_idx

        wave_rendered = str(buddy_module.buddy_mascot(zorp_kit.live_look('wave')))
        assert 'zorp-hat--beanie' in wave_rendered
        assert 'zorp-shoe' not in wave_rendered

        # Same shared macro, same art: the mortarboard's inner content (minus
        # the wrapping <g>'s own translate anchor) must match between the
        # live rig and the pose-kit scholar still exactly.
        kit_markup = str(pose('scholar', size=80))
        live_inner = rendered[rendered.index('zorp-hat--mortarboard'):]
        live_inner = live_inner[live_inner.index('>') + 1:live_inner.index('</g>')]
        kit_inner = kit_markup[kit_markup.index('zorp-hat--mortarboard'):]
        kit_inner = kit_inner[kit_inner.index('>') + 1:kit_inner.index('</g>')]
        assert live_inner == kit_inner


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
        if look.get('hat'):
            assert f'zorp-hat--{look["hat"]}' in html, name
        if look.get('shoes'):
            assert f'zorp-shoe--{look["shoes"]}' in html, name
    assert html.count('id="sg-zorp-overlays"') >= 1
    assert html.count('sg-zorp-hero') >= 2


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
    test_overlay_macros()
    test_kit_headwear_regression()
    test_live_overlay_matches_kit()
    test_latest_pose_milestone()
    test_styleguide_looks()
    test_base_passes_look()
    test_styleguide_gallery()
    test_styleguide_localhost_without_env_flag()
    test_templates_use_kit()
    print('Zorp pose kit smoke OK')


if __name__ == '__main__':
    main()
