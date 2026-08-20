"""Lesson progress must stay per-user — run: python scripts/test_lesson_progress_smoke.py"""
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


def logout(client):
    r = client.get('/profile')
    client.post(
        '/logout',
        data={'csrf_token': csrf_from(r.data.decode())},
        follow_redirects=True,
    )


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user
        return user.id


def main():
    js = (ROOT / 'static' / 'js' / 'lesson-progress.js').read_text(encoding='utf-8')
    assert "dataset.userId" in js
    assert 'lesson-progress:u' in js
    assert 'dropSharedGuestProgress' in js
    assert "removeItem(guestStorageKey)" in js

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'lpa_{suffix}'
        handle_b = f'lpb_{suffix}'
        register(client, f'{handle_a}@example.com', handle_a)
        uid_a = user_id_for(handle_a)

        r = client.get('/topic/gcse/maths/functions')
        assert r.status_code == 200
        html_a = r.data.decode()
        assert f'data-user-id="{uid_a}"' in html_a
        assert 'lesson-progress.js?v=8' in html_a

        r = client.post(
            '/api/lesson-progress',
            json={
                'csrf_token': csrf_from(html_a),
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'section_key': 'step-3',
                'section_label': 'Inverse functions',
                'completed_keys': ['step-1', 'step-2', 'step-3'],
            },
        )
        assert r.get_json()['ok'] is True
        saved = client.get('/api/lesson-progress/gcse/maths/functions').get_json()
        assert saved['progress']['completed_keys'] == ['step-1', 'step-2', 'step-3']

        logout(client)
        register(client, f'{handle_b}@example.com', handle_b)
        uid_b = user_id_for(handle_b)
        assert uid_b != uid_a

        r = client.get('/api/lesson-progress/gcse/maths/functions')
        assert r.status_code == 200
        assert r.get_json()['progress'] is None

        r = client.get('/topic/gcse/maths/functions')
        assert r.status_code == 200
        html_b = r.data.decode()
        assert f'data-user-id="{uid_b}"' in html_b
        assert f'data-user-id="{uid_a}"' not in html_b

    print('Lesson progress per-user smoke tests passed.')


if __name__ == '__main__':
    main()
