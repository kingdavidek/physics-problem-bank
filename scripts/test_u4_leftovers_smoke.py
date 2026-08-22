"""U4 leftovers — recent practised strip + challenge quiz-runner / H2H.

Run: python scripts/test_u4_leftovers_smoke.py
"""
import os
import re
import sys
import uuid
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.challenges import (  # noqa: E402
    CHALLENGE_COMPLETE,
    build_head_to_head,
    create_challenge,
    get_challenge,
    submit_challenge_attempt,
)
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
    r = client.get('/')
    client.post(
        '/logout',
        data={'csrf_token': csrf_from(r.data.decode())},
        follow_redirects=True,
    )


def login(client, email):
    r = client.get('/login')
    client.post(
        '/login',
        data={
            'csrf_token': csrf_from(r.data.decode()),
            'email': email,
            'password': 'password123',
        },
        follow_redirects=True,
    )


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user
        return user.id


def chip_topics(html: str):
    return re.findall(
        r'class="recent-practised-chip-form">.*?name="topic" value="([^"]+)"',
        html,
        flags=re.S,
    )


def generate(client, topic, csrf):
    r = client.post(
        '/',
        data={
            'csrf_token': csrf,
            'level': 'gcse',
            'subject': 'maths',
            'topic': topic,
            'mode': 'standard',
            'difficulty': 'foundational',
            'action': 'start',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200
    return r


def fake_problems():
    return [
        {
            'question': 'What is 2+2?',
            'options': ['A 3', 'B 4', 'C 5', 'D 6'],
            'correct_answer': 'B',
        },
        {
            'question': 'What is 3+3?',
            'options': ['A 5', 'B 6', 'C 7', 'D 8'],
            'correct_answer': 'B',
        },
    ]


def main():
    with app.test_client() as client:
        r = client.get('/')
        assert r.status_code == 200
        assert b'recent-practised' not in r.data

        suffix = uuid.uuid4().hex[:8]
        handle_b = f'u4b_{suffix}'
        handle_a = f'u4a_{suffix}'
        email_b = f'u4b_{suffix}@example.com'
        email_a = f'u4a_{suffix}@example.com'

        register(client, email_b, handle_b)
        logout(client)
        register(client, email_a, handle_a)

        r = client.get('/')
        assert r.status_code == 200
        assert b'recent-practised' not in r.data
        csrf = csrf_from(r.data.decode())

        generate(client, 'algebra', csrf)
        r = client.get('/')
        assert b'recent-practised' in r.data
        assert chip_topics(r.data.decode()) == ['algebra']

        generate(client, 'bidmas', csrf)
        r = client.get('/')
        topics = chip_topics(r.data.decode())
        assert topics[0] == 'bidmas'
        assert 'algebra' in topics

        uid_a = user_id_for(handle_a)
        uid_b = user_id_for(handle_b)
        problems = fake_problems()
        with get_db() as conn:
            challenge_id = create_challenge(
                conn, uid_a, uid_b, 'gcse', 'maths', 'algebra', problems, seed=42,
            )

        r = client.get(f'/challenges/{challenge_id}')
        assert r.status_code == 200
        body = r.data.decode()
        assert 'data-quiz-runner' in body
        assert 'data-submit-label="Submit challenge"' in body
        assert 'quiz-runner-step' in body
        assert 'quiz-runner-active' in body
        assert 'What is 2+2?' in body

        r = client.post(
            f'/challenges/{challenge_id}',
            data={
                'csrf_token': csrf,
                'action': 'submit',
                'answer_0': 'B',
                'answer_1': 'B',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        assert b'Waiting for @' in r.data
        assert handle_b.encode() in r.data

        with get_db() as conn:
            challenge = get_challenge(conn, challenge_id)
            assert challenge['creator_answers'] == ['B', 'B']
            assert challenge['creator_score'] == 2
            assert challenge['status'] != CHALLENGE_COMPLETE

        logout(client)
        login(client, email_b)
        r = client.get(f'/challenges/{challenge_id}')
        assert b'data-quiz-runner' in r.data
        assert b'Decline challenge' in r.data

        r = client.post(
            f'/challenges/{challenge_id}',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'action': 'submit',
                'answer_0': 'B',
                'answer_1': 'A',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        body = r.data.decode()
        assert 'challenge-h2h' in body
        assert f'@{handle_a} wins' in body
        assert f'@{handle_a}: B' in body
        assert f'@{handle_b}: A' in body
        assert 'What is 3+3?' in body

        with get_db() as conn:
            challenge = get_challenge(conn, challenge_id)
            assert challenge['status'] == CHALLENGE_COMPLETE
            assert challenge['opponent_answers'] == ['B', 'A']
            assert challenge['opponent_score'] == 1
            comparison = build_head_to_head(challenge)
            assert comparison['winner'] == 'creator'
            assert comparison['questions'][0]['creator_correct'] is True
            assert comparison['questions'][1]['opponent_correct'] is False
            assert comparison['has_answers'] is True

    print('u4 leftovers smoke ok')


if __name__ == '__main__':
    main()
