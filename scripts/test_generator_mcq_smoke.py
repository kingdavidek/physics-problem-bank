"""Generator MCQ persistence smoke test — run: python scripts/test_generator_mcq_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
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
    email = f'mcq_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'mcq{uuid.uuid4().hex[:6]}'

    with app.test_client() as client:
        register(client, email, handle)

        r = client.post(
            '/api/v1/generator/mcq-answer',
            json={
                'level': 'gcse',
                'subject': 'physics',
                'topic': 'forces',
                'difficulty': 'foundational',
                'user_answer': 'A',
                'correct_answer': 'A',
                'correct': True,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert data['practice_streak'] == 1

        r = client.get('/profile')
        assert r.status_code == 200
        body = r.data.decode()
        assert 'MCQ practice' in body
        assert '1-day streak' in body
        assert '✓ Correct' in body

        r = client.post(
            '/api/v1/generator/mcq-answer',
            json={
                'level': 'gcse',
                'subject': 'physics',
                'topic': 'forces',
                'difficulty': 'foundational',
                'user_answer': 'B',
                'correct_answer': 'A',
                'correct': False,
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200

        r = client.get('/profile')
        body = r.data.decode()
        assert '✗ Incorrect' in body

    print('Generator MCQ smoke tests passed.')


if __name__ == '__main__':
    main()
