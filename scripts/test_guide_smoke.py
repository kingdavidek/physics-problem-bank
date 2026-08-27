"""E6 / A1 Guide overlay smoke — run: python scripts/test_guide_smoke.py"""
import os
import json
import re
import sys
import uuid
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.account_deletion import delete_user_account, remaining_user_rows  # noqa: E402
from models.data_export import build_user_export  # noqa: E402
from models.user import User  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def guide_state_from(html: str):
    m = re.search(
        r'<script type="application/json" id="pb-guide-state"([^>]*)>(.*?)</script>',
        html,
        re.S,
    )
    assert m, 'pb-guide-state missing'
    attrs, raw = m.group(1), m.group(2)
    return json.loads(raw), 'data-guide-persisted="1"' in attrs


def register(client, email, handle):
    r = client.get('/register')
    token = csrf_from(r.data.decode())
    r = client.post(
        '/register',
        data={
            'csrf_token': token,
            'email': email,
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200, r.data[:400]


def main():
    partial = (ROOT / 'templates' / 'partials' / 'guide.html').read_text(encoding='utf-8')
    assert 'onclick=' not in partial.lower()
    assert 'oninput=' not in partial.lower()
    assert 'data-guide-bubble' in partial
    assert 'data-guide-primary' in partial
    chrome = (ROOT / 'static' / 'css' / 'chrome.css').read_text(encoding='utf-8')
    assert 'data-guide-mode="reward"' in chrome
    assert 'data-guide-mode="tour"' in chrome
    assert '.guide-spot' in chrome
    assert '.guide-actions .btn[hidden]' in chrome
    assert 'pb-streak-fire' in chrome
    assert '.nav-streak.is-flame' in chrome
    assert 'prefers-reduced-motion' in chrome
    assert 'lottie' not in chrome.lower()
    js_src = (ROOT / 'static' / 'js' / 'guide.js').read_text(encoding='utf-8')
    assert 'playStreakFlame' in js_src
    assert "rewardType === 'streak'" in js_src
    assert 'is-flame' in js_src
    assert 'lottie' not in js_src.lower()
    assert 'jsdelivr' not in js_src.lower()
    assert 'data-guide-spot' in partial
    assert 'data-guide-medal' in partial
    assert 'buddy_mascot()' in partial
    assert 'role="dialog"' in partial
    assert 'aria-modal="true"' in partial

    with app.test_client() as client:
        r = client.get('/')
        assert r.status_code == 200
        guest = r.data.decode()
        assert 'data-guide-root' not in guest
        assert 'guide.js' not in guest
        assert 'guide-catalog.js' not in guest
        assert 'pb-guide-state' not in guest
        assert 'data-guide-endpoint=' in guest

        r = client.get('/static/js/guide.js')
        assert r.status_code == 200, r.data[:200]
        guide_js = r.data.decode()
        assert 'pb-guide-v1' in guide_js
        assert 'textContent' in guide_js
        assert 'innerHTML' not in guide_js
        assert "play: play" in guide_js or 'play: play,' in guide_js
        assert 'prefers-reduced-motion' in guide_js
        assert 'profile_settings' in guide_js
        assert 'login' in guide_js
        assert 'data-guide-preview' in guide_js
        assert 'isPreview' in guide_js
        assert 'function reward' in guide_js
        assert 'copyFlags' in guide_js
        assert "type === 'milestone'" in guide_js
        assert "type === 'streak'" in guide_js
        assert "type === 'first_correct'" in guide_js
        assert "type === 'lesson_complete'" in guide_js
        assert 'pb-buddy-milestone-' in guide_js
        assert 'ENDPOINT_TOUR' in guide_js
        assert 'topics_index' in guide_js
        assert 'friend_leaderboard_page' in guide_js
        assert 'challenge_detail' in guide_js
        assert 'function tourFor' in guide_js
        assert 'function firstMatch' in guide_js
        assert 'data-guide-spot' in guide_js
        assert 'guide-tour-open' in guide_js
        assert 'skipTourThisLoad' in guide_js
        assert 'pb-guide-state' in guide_js
        assert '/api/v1/me/settings' in guide_js
        assert 'function persistNow' in guide_js
        assert 'pagehide' in guide_js
        assert 'data-guide-persisted' in guide_js

        r = client.get('/static/js/celebrate.js')
        assert r.status_code == 200
        celebrate_js = r.data.decode()
        assert 'pbGuide' in celebrate_js
        assert "type: 'milestone'" in celebrate_js
        assert "type: 'streak'" in celebrate_js
        assert "type: 'first_correct'" in celebrate_js
        assert "type: 'lesson_complete'" in celebrate_js

        r = client.get('/static/js/guide-catalog.js')
        assert r.status_code == 200, r.data[:200]
        catalog = r.data.decode()
        origin_ids = re.findall(r"id:\s*'origin\.[^']+'", catalog)
        assert len(origin_ids) >= 4, origin_ids
        assert 'Novara sent helpers' in catalog or 'Novara' in catalog
        assert 'Zorp' in catalog
        assert "mode: 'story'" in catalog
        assert 'Skip intro' in catalog
        assert 'origin.ready' in catalog
        assert 'Let’s go' in catalog or "Let's go" in catalog or 'go' in catalog.lower()
        assert "'streak:7'" in catalog
        assert "'streak:30'" in catalog
        assert "'streak:100'" in catalog
        assert 'You earned this.' in catalog
        assert 'first_correct:' in catalog
        assert 'lesson_complete:' in catalog
        assert 'First correct' in catalog
        assert 'Lesson complete' in catalog
        assert 'practice:' in catalog or "practice:" in catalog
        assert "id: 'practice.picker'" in catalog
        assert "id: 'profile.streak'" in catalog
        assert "id: 'daily.today'" in catalog
        assert "id: 'learn.grid'" in catalog
        assert "id: 'compete.board'" in catalog
        assert 'Not now' in catalog
        assert 'profile_settings' not in catalog
        assert 'friend_leaderboard_page' not in catalog
        assert 'topics_index' not in catalog
        assert '#main-form' in catalog
        assert '#milestones' in catalog
        assert '.qotd-daily-card' in catalog
        assert '#topics-grid' in catalog
        assert '#leaderboard-board-tabs' in catalog
        assert 'friends only' in catalog.lower()
        assert 'No DMs.' in catalog

        suffix = uuid.uuid4().hex[:8]
        handle = f'gda1_{suffix}'
        email = f'gda1_{suffix}@example.com'
        register(client, email, handle)

        r = client.get('/')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'data-guide-root' in html
        assert 'data-guide-bubble' in html
        assert 'data-guide-primary' in html
        assert 'data-guide-skip' in html
        assert 'guide.js' in html
        assert 'guide-catalog.js' in html
        assert 'guide.js?v=' in html
        assert 'buddy-mascot' in html
        assert 'data-guide-medal' in html
        assert 'pb-milestone-catalog' in html
        assert 'first_quiz' in html
        assert 'data-guide-endpoint="index"' in html
        assert 'onclick=' not in html.lower()
        assert 'id="main-form"' in html
        assert 'id="app-tab-bar"' in html
        assert 'id="mode-select"' in html
        assert 'data-guide-spot' in html

        state, persisted = guide_state_from(html)
        assert persisted is False
        assert state.get('origin') is False

        r = client.get('/api/v1/me/settings')
        assert r.status_code == 200
        api_guide = r.get_json()['settings']['guide']
        assert api_guide['origin'] is False
        assert api_guide['tours'] == {}
        assert api_guide['rewards'] == {}

        r = client.patch(
            '/api/v1/me/settings',
            json={'guide': {'origin': True, 'tours': {'practice': True}}},
        )
        assert r.status_code == 200, r.data[:400]
        guide = r.get_json()['settings']['guide']
        assert guide['origin'] is True
        assert guide['tours']['practice'] is True

        r = client.patch(
            '/api/v1/me/settings',
            json={'guide': {'rewards': {'first_correct': True}}},
        )
        assert r.status_code == 200
        guide = r.get_json()['settings']['guide']
        assert guide['origin'] is True
        assert guide['tours']['practice'] is True
        assert guide['rewards']['first_correct'] is True

        r = client.patch('/api/v1/me/settings', json={'theme_preference': 'dark'})
        assert r.status_code == 200
        assert r.get_json()['settings']['guide']['origin'] is True

        r = client.patch('/api/v1/me/settings', json={'guide': 'nope'})
        assert r.status_code == 400
        r = client.patch('/api/v1/me/settings', json={'guide': {'origin': 'yes'}})
        assert r.status_code == 400

        r = client.get('/')
        html = r.data.decode()
        state, persisted = guide_state_from(html)
        assert persisted is True
        assert state['origin'] is True

        r = client.get('/profile/settings')
        settings = r.data.decode()
        assert 'id="guide-replay-intro"' in settings
        assert 'replay_guide_intro' in settings
        assert 'onclick=' not in settings.lower()
        r = client.post(
            '/profile/settings',
            data={
                'csrf_token': csrf_from(settings),
                'action': 'replay_guide_intro',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        home = r.data.decode()
        state, persisted = guide_state_from(home)
        assert persisted is True
        assert state['origin'] is False
        assert state['tours'].get('practice') is True

        with get_db() as conn:
            user = User.get_by_handle(conn, handle)
            exported = build_user_export(conn, user.id)
            assert 'guide_json' in exported['settings']
            assert 'origin' in exported['settings']['guide_json']

        r = client.get('/profile')
        assert r.status_code == 200
        profile = r.data.decode()
        assert 'data-guide-endpoint="profile"' in profile
        assert 'id="milestones"' in profile
        assert 'id="revision-plan"' in profile
        assert 'id="guide-replay-intro"' not in profile

        r = client.get('/qotd')
        assert r.status_code == 200
        qotd = r.data.decode()
        assert 'data-guide-endpoint="qotd_page"' in qotd
        assert 'qotd-daily-card' in qotd
        assert 'id="qotd-board"' in qotd

        r = client.get('/topics')
        assert r.status_code == 200
        topics = r.data.decode()
        assert 'data-guide-endpoint="topics_index"' in topics
        assert 'id="topics-grid"' in topics
        assert 'topics-level-bar' in topics

        r = client.get('/leaderboard/friends')
        assert r.status_code == 200
        compete = r.data.decode()
        assert 'data-guide-endpoint="friend_leaderboard_page"' in compete
        assert 'id="leaderboard-board-tabs"' in compete
        assert 'id="compete-challenges"' in compete
        assert 'No DMs' in compete

        r = client.get('/profile/settings')
        assert r.status_code == 200
        settings = r.data.decode()
        assert 'data-guide-endpoint="profile_settings"' in settings
        assert 'guide.js' in settings
        assert 'id="guide-replay-intro"' in settings

        r = client.get('/privacy')
        assert r.status_code == 200
        privacy = r.data.decode()
        assert 'data-guide-endpoint="legal_privacy"' in privacy
        assert 'Guide intro' in privacy

        r = client.get('/privacy/simple')
        assert r.status_code == 200
        assert 'intro' in r.data.decode().lower()

        r = client.get('/guide-preview')
        assert r.status_code == 200, r.data[:300]
        preview = r.data.decode()
        assert 'data-guide-root' in preview
        assert 'data-guide-preview="1"' in preview
        assert 'guide.js' in preview
        assert 'guide-preview.js' in preview
        assert 'guide-preview-play' in preview
        assert 'guide-preview-badge' in preview
        assert 'guide-preview-streak' in preview
        assert 'id="guide-preview-nav-streak"' in preview
        assert 'class="nav-streak"' in preview
        assert 'guide-preview-first' in preview
        assert 'guide-preview-lesson' in preview
        assert 'guide-preview-practice' in preview
        assert 'guide-preview-profile' in preview
        assert 'guide-preview-daily' in preview
        assert 'guide-preview-learn' in preview
        assert 'guide-preview-compete' in preview
        assert 'data-guide-endpoint="guide_preview"' in preview
        assert 'onclick=' not in preview.lower()

        r = client.get('/api/v1/build-info')
        assert r.status_code == 200
        assert r.get_json().get('guide_preview') == '/guide-preview'

        with get_db() as conn:
            user = User.get_by_handle(conn, handle)
            uid = user.id
            delete_user_account(conn, uid)
            leftover = remaining_user_rows(conn, uid)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero

    print('Guide smoke tests passed.')


if __name__ == '__main__':
    main()
