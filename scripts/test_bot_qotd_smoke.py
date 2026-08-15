"""E1.2 daily bot QOTD challenge smoke — run: python scripts/test_bot_qotd_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.bot import BOT_HANDLE, BOT_PROMPT, ensure_system_bot, is_bot_handle  # noqa: E402
from models.user import User, validate_handle  # noqa: E402


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
    assert r.status_code == 200


def main():
    assert is_bot_handle(BOT_HANDLE)
    assert is_bot_handle('@Problem_Bot')
    assert validate_handle(BOT_HANDLE)

    with app.test_client() as client:
        with get_db() as conn:
            bot = ensure_system_bot(conn)
            assert bot.handle == BOT_HANDLE
            again = ensure_system_bot(conn)
            assert again.id == bot.id

        suffix = uuid.uuid4().hex[:8]
        email = f'botq_{suffix}@example.com'
        handle = f'botq_{suffix}'
        register(client, email, handle)

        r = client.get('/feed')
        assert r.status_code == 200
        html = r.data.decode()
        assert BOT_PROMPT in html
        assert 'A Problem Bank bot' in html
        assert '/qotd' in html
        assert 'feed-card--bot' in html

        r = client.get('/api/v1/feed?filter=all&limit=20')
        assert r.status_code == 200
        data = r.get_json()
        challenge = data.get('qotd_challenge')
        assert challenge, data
        assert challenge['is_bot'] is True
        assert challenge['actor_handle'] == BOT_HANDLE
        assert challenge['url'] == '/qotd'
        assert challenge['answered'] is False
        assert challenge['message'] == BOT_PROMPT

        r = client.get('/api/v1/feed?filter=all&limit=20&before_id=1')
        assert r.status_code == 200
        assert r.get_json().get('qotd_challenge') is None

        r = client.get('/api/v1/feed?filter=quizzes')
        assert r.status_code == 200
        assert r.get_json().get('qotd_challenge') is None

        r = client.get(f'/u/{BOT_HANDLE}')
        assert r.status_code == 200
        profile = r.data.decode()
        assert 'not a person' in profile.lower() or 'bot' in profile.lower()
        assert 'Study buddy invite' not in profile
        assert 'Challenge to quiz' not in profile

        client.post(
            '/logout',
            data={'csrf_token': csrf_from(client.get('/profile').data.decode())},
            follow_redirects=True,
        )

        r = client.get('/register')
        token = csrf_from(r.data.decode())
        r = client.post(
            '/register',
            data={
                'csrf_token': token,
                'email': f'botsteal_{suffix}@example.com',
                'handle': BOT_HANDLE,
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        body = r.data.lower()
        assert b'reserved' in body or b'already' in body or b'taken' in body

        r = client.post(
            '/login',
            data={
                'csrf_token': csrf_from(client.get('/login').data.decode()),
                'email': 'problem_bot@internal.problembank',
                'password': 'password123',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        r = client.get('/api/v1/auth/me')
        assert r.status_code == 401
        with get_db() as conn:
            still = User.get_by_email(conn, email)
        assert still is not None
        assert still.handle != BOT_HANDLE

    print('Bot QOTD smoke tests passed.')


if __name__ == '__main__':
    main()
