"""Phase E smoke test — run: python scripts/test_phase_e_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'pe_{suffix}@example.com',
            'handle': f'pe_{suffix}',
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    body = r.get_json()
    return body['token'], body['user']['id']


def main():
    with app.test_client() as client:
        suffix_a = uuid.uuid4().hex[:8]
        suffix_b = uuid.uuid4().hex[:8]
        token_a, _ = register(client, f'a_{suffix_a}')
        token_b, _ = register(client, f'b_{suffix_b}')
        auth_a = bearer(token_a)
        auth_b = bearer(token_b)
        handle_b = f'pe_b_{suffix_b}'

        # Study pair invite + accept
        r = client.post('/api/v1/study-pairs/invite', json={'handle': handle_b}, headers=auth_a)
        assert r.status_code == 201, r.data
        pair_id = r.get_json()['pair_id']

        r = client.get('/api/v1/me/study-pair', headers=auth_b)
        assert r.status_code == 200
        assert len(r.get_json()['pending_invites']) == 1

        r = client.post(f'/api/v1/study-pairs/{pair_id}/accept', headers=auth_b)
        assert r.status_code == 200
        assert r.get_json()['study_pair']['status'] == 'active'

        r = client.get('/api/v1/me/study-pair', headers=auth_a)
        assert r.get_json()['study_pair']['buddy_handle'] == handle_b
        assert r.get_json()['buddy_recap'] is not None

        # End pair for challenge isolation (optional — challenges don't require pair)
        r = client.delete('/api/v1/me/study-pair', headers=auth_a)
        assert r.status_code == 200

        # Challenge create
        r = client.post(
            '/api/v1/challenges',
            json={
                'opponent_handle': handle_b,
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
            },
            headers=auth_a,
        )
        assert r.status_code == 201, r.data
        challenge_id = r.get_json()['challenge']['id']

        r = client.get(f'/api/v1/challenges/{challenge_id}', headers=auth_b)
        assert r.status_code == 200
        ch = r.get_json()['challenge']
        assert ch['total'] == 10
        assert len(ch['problems']) == 10

        # Same problems for both players
        r2 = client.get(f'/api/v1/challenges/{challenge_id}', headers=auth_a)
        assert r2.get_json()['challenge']['problems'][0]['question_html'] == ch['problems'][0]['question_html']

        answers = ['A'] * 10
        r = client.post(
            f'/api/v1/challenges/{challenge_id}/submit',
            json={'answers': answers},
            headers=auth_a,
        )
        assert r.status_code == 200, r.data
        assert 'score' in r.get_json()

        r = client.post(
            f'/api/v1/challenges/{challenge_id}/submit',
            json={'answers': answers},
            headers=auth_b,
        )
        assert r.status_code == 200
        assert r.get_json()['challenge']['status'] == 'complete'

        # QOTD
        r = client.get('/api/v1/qotd/today', headers=auth_a)
        assert r.status_code == 200
        qotd = r.get_json()
        assert qotd['question_html']
        assert qotd['options']

        r = client.post('/api/v1/qotd/today/answer', json={'answer': 'A'}, headers=auth_a)
        assert r.status_code == 200
        assert 'correct' in r.get_json()

        r = client.post('/api/v1/qotd/today/answer', json={'answer': 'B'}, headers=auth_a)
        assert r.status_code == 409

        # Follow for leaderboard
        client.post(f'/api/v1/users/{handle_b}/follow', headers=auth_a)
        r = client.post('/api/v1/qotd/today/answer', json={'answer': 'A'}, headers=auth_b)
        assert r.status_code == 200

        r = client.get('/api/v1/qotd/today/leaderboard', headers=auth_a)
        assert r.status_code == 200
        board = r.get_json()['leaderboard']
        assert len(board) >= 2

        r = client.get('/api/v1/challenges', headers=auth_a)
        assert r.status_code == 200
        assert any(c['id'] == challenge_id for c in r.get_json()['challenges'])

    print('Phase E smoke tests passed.')


if __name__ == '__main__':
    main()
