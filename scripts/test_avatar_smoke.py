"""Avatar customisation smoke — run: python scripts/test_avatar_smoke.py"""
import json
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.user import User  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle):
    r = client.get('/register')
    token = csrf_from(r.data.decode())
    client.post(
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


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user
        return user.id


def award_milestone(user_id, milestone_key):
    with get_db() as conn:
        conn.execute(
            '''
            INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at)
            VALUES (?, ?, datetime('now'))
            ''',
            (user_id, milestone_key),
        )
        conn.commit()


def set_avatar_json(user_id, avatar):
    with get_db() as conn:
        conn.execute(
            '''
            UPDATE user_profile_settings
            SET avatar_json = ?
            WHERE user_id = ?
            ''',
            (json.dumps(avatar), user_id),
        )
        conn.commit()


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle = f'ava_{suffix}'
        email = f'ava_{suffix}@example.com'
        register(client, email, handle)
        uid = user_id_for(handle)

        r = client.get('/api/v1/me/settings')
        assert r.status_code == 200
        avatar = r.get_json()['settings']['avatar']
        assert avatar['face'] == '🙂'
        assert avatar['bg'] == '#eef6fc'
        assert avatar['extra'] == ''

        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar': {'face': '🦊', 'bg': '#fff8e6', 'extra': '⭐'}},
        )
        assert r.status_code == 200
        avatar = r.get_json()['settings']['avatar']
        assert avatar == {'face': '🦊', 'bg': '#fff8e6', 'extra': ''}

        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar': {'face': '🦊', 'bg': '#fff8e6', 'extra': '🎓'}},
        )
        assert r.status_code == 200
        assert r.get_json()['settings']['avatar']['extra'] == ''

        award_milestone(uid, 'topics_10')
        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar': {'face': '🦊', 'bg': '#fff8e6', 'extra': '🎓'}},
        )
        assert r.status_code == 200
        avatar = r.get_json()['settings']['avatar']
        assert avatar == {'face': '🦊', 'bg': '#fff8e6', 'extra': '🎓'}

        r = client.patch('/api/v1/me/settings', json={'show_quiz_stats': False})
        assert r.status_code == 200
        settings = r.get_json()['settings']
        assert settings['show_quiz_stats'] is False
        assert settings['avatar']['face'] == '🦊'
        assert settings['avatar']['extra'] == '🎓'

        r = client.patch('/api/v1/me/settings', json={'avatar_face': '🐼'})
        assert r.status_code == 200
        assert r.get_json()['settings']['avatar']['face'] == '🐼'
        assert r.get_json()['settings']['avatar']['extra'] == '🎓'

        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar': {'face': '<script>', 'bg': 'red', 'extra': '💣'}},
        )
        assert r.status_code == 200
        avatar = r.get_json()['settings']['avatar']
        assert avatar['face'] == '🙂'
        assert avatar['bg'] == '#eef6fc'
        assert avatar['extra'] == ''

        r = client.get(f'/api/v1/users/{handle}/profile')
        assert r.status_code == 200
        assert r.get_json()['profile']['avatar']['face'] == '🙂'

        r = client.get(f'/u/{handle}')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'user-avatar' in html
        assert '🙂' in html

        r = client.get('/profile')
        assert r.status_code == 200
        assert 'user-avatar' in r.data.decode()

        r = client.get('/profile/settings')
        settings_html = r.data.decode()
        token = csrf_from(settings_html)
        assert 'avatar_face' in settings_html
        assert 'Earn <em>Practice regular</em> to unlock' in settings_html
        assert 'Earn <em>Week warrior</em> to unlock' in settings_html
        assert 'avatar-choice--locked' in settings_html

        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar': {'face': '🦊', 'bg': '#fff8e6', 'extra': '🎓'}},
        )
        assert r.get_json()['settings']['avatar']['extra'] == '🎓'

        client.post(
            '/profile/settings',
            data={
                'csrf_token': token,
                'profile_visibility': 'public',
                'show_member_since': '1',
                'show_last_topic': '1',
                'show_last_activity': '1',
                'show_lesson_progress': '1',
                'show_quiz_stats': '1',
                'show_shared_questions': '1',
                'avatar_face': '😎',
                'avatar_bg': '#fdf0f7',
                'avatar_extra': '⭐',
            },
            follow_redirects=True,
        )
        r = client.get('/api/v1/me/settings')
        avatar = r.get_json()['settings']['avatar']
        assert avatar['extra'] == '🎓'
        assert avatar['face'] == '😎'

        award_milestone(uid, 'streak_7')
        r = client.patch(
            '/api/v1/me/settings',
            json={'avatar_extra': '⭐'},
        )
        assert r.status_code == 200
        assert r.get_json()['settings']['avatar']['extra'] == '⭐'

        set_avatar_json(uid, {'face': '🙂', 'bg': '#eef6fc', 'extra': '⭐'})
        r = client.patch('/api/v1/me/settings', json={'avatar_face': '😺'})
        assert r.status_code == 200
        assert r.get_json()['settings']['avatar'] == {
            'face': '😺',
            'bg': '#eef6fc',
            'extra': '⭐',
        }

        r = client.get('/leaderboard/friends')
        assert r.status_code == 200
        assert 'user-avatar' in r.data.decode()

    print('Avatar smoke tests passed.')


if __name__ == '__main__':
    main()
