"""Phase E smoke test — run: python scripts/test_phase_e_smoke.py"""
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from generators.gcse.maths_num_stats_prob_rat import graphs_mcq  # noqa: E402
from models.gamification import get_study_streak  # noqa: E402
from models.qotd import get_daily_question  # noqa: E402


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

        # QOTD: scatter MCQ letters must match option text (not an empty "correct")
        saw_correlation = False
        for slot in range(7):
            q, _s, _h, _m, opts, letter = graphs_mcq(slot_index=slot, difficulty='foundational')
            if 'type of correlation' not in q.lower():
                continue
            saw_correlation = True
            chosen = next(opt for opt in opts if str(opt)[:1] == letter)
            assert chosen.strip() != letter
            assert any(
                word in chosen.lower()
                for word in ('positive', 'negative', 'no correlation')
            )
        assert saw_correlation
        for slot in range(7):
            q, *_rest = graphs_mcq(slot_index=slot, difficulty='difficult')
            assert 'What type of correlation does this show?' not in q

        suffix_c = uuid.uuid4().hex[:8]
        token_c, uid_c = register(client, f'c_{suffix_c}')
        auth_c = bearer(token_c)

        r = client.get('/api/v1/qotd/today', headers=auth_c)
        assert r.status_code == 200
        qotd = r.get_json()
        assert qotd['question_html']
        assert qotd['options']
        assert qotd['difficulty'] == 'difficult'
        assert not qotd.get('solution_html')
        assert not qotd.get('correct_answer')

        daily = get_daily_question()
        assert daily['problem']['difficulty'] == 'difficult'
        again = get_daily_question()
        assert again['problem']['correct_answer'] == daily['problem']['correct_answer']
        assert again['topic'] == daily['topic']
        correct_letter = daily['problem']['correct_answer']
        wrong_letter = 'B' if correct_letter != 'B' else 'A'

        with get_db() as conn:
            before_mcq = conn.execute(
                'SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ?',
                (uid_c,),
            ).fetchone()['n']
            before_events = conn.execute(
                'SELECT COUNT(*) AS n FROM user_activity_events WHERE user_id = ?',
                (uid_c,),
            ).fetchone()['n']

        r = client.post(
            '/api/v1/qotd/today/answer',
            json={'answer': wrong_letter},
            headers=auth_c,
        )
        assert r.status_code == 200
        answered = r.get_json()
        assert answered['correct'] is False
        assert answered['correct_answer'] == correct_letter
        assert answered['solution_html']

        r = client.get('/api/v1/qotd/today', headers=auth_c)
        replay = r.get_json()
        assert replay['answered'] is True
        assert replay['solution_html']
        assert replay['correct_answer'] == correct_letter

        with get_db() as conn:
            after_mcq = conn.execute(
                'SELECT COUNT(*) AS n FROM generator_mcq_attempts WHERE user_id = ?',
                (uid_c,),
            ).fetchone()['n']
            after_events = conn.execute(
                'SELECT COUNT(*) AS n FROM user_activity_events WHERE user_id = ?',
                (uid_c,),
            ).fetchone()['n']
            streak = get_study_streak(conn, uid_c)
        assert after_mcq == before_mcq
        assert after_events == before_events
        assert streak['current'] >= 1

        # Existing A/B answers still feed the friend mini-leaderboard
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
