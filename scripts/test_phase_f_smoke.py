"""Phase F + M1 smoke test — run: python scripts/test_phase_f_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402


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


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'phf_a_{suffix}'
        handle_b = f'phf_b_{suffix}'
        email_a = f'phf_a_{suffix}@example.com'
        email_b = f'phf_b_{suffix}@example.com'

        # Topics catalog (public)
        r = client.get('/api/v1/topics')
        assert r.status_code == 200, r.data
        catalog = r.get_json()
        assert catalog['ok'] is True
        assert any(level['id'] == 'gcse' for level in catalog['levels'])
        maths = next(
            s
            for level in catalog['levels'] if level['id'] == 'gcse'
            for s in level['subjects'] if s['id'] == 'maths'
        )
        assert any(t['slug'] == 'bidmas' for t in maths['topics'])

        register(client, email_a, handle_a)

        # Settings PATCH gap fixed
        r = client.patch(
            '/api/v1/me/settings',
            json={'show_study_streak': True, 'show_milestones': True},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['settings']['show_study_streak'] is True

        # Generate problem API
        r = client.post(
            '/api/v1/problems/generate',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'mcq',
                'difficulty': 'foundational',
                'action': 'start',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        gen = r.get_json()
        assert gen['ok'] is True
        assert gen['problem']['question_html']
        assert 'selection' in gen
        first_variant = gen['selection'].get('variant_name')

        # Next advances queue
        r = client.post(
            '/api/v1/problems/generate',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'mcq',
                'difficulty': 'foundational',
                'action': 'next',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        next_gen = r.get_json()
        if first_variant and next_gen['selection'].get('variant_name'):
            # Different slots when multiple variants exist
            assert next_gen['selection']['queue_position'] >= 1

        # Save problem
        r = client.post(
            '/api/v1/me/saved-problems',
            json={},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        saved_id = r.get_json()['saved_id']

        r = client.get('/api/v1/me/saved-problems')
        assert r.status_code == 200
        assert any(item['id'] == saved_id for item in r.get_json()['saved_problems'])

        r = client.delete(f'/api/v1/me/saved-problems/{saved_id}')
        assert r.status_code == 200

        # Feed pagination fields
        r = client.get('/api/v1/feed?limit=5')
        assert r.status_code == 200
        assert 'next_before_id' in r.get_json()

        r = client.get('/api/v1/me/notifications?limit=5')
        assert r.status_code == 200
        assert 'next_before_id' in r.get_json()

        # Block / report
        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        register(client, email_b, handle_b)

        r = client.post(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 200
        assert r.get_json()['following'] is True

        r = client.post(
            f'/api/v1/users/{handle_a}/report',
            json={'report_type': 'spam', 'note': 'test'},
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['ok'] is True

        r = client.post(f'/api/v1/users/{handle_a}/block')
        assert r.status_code == 200
        assert r.get_json()['blocked'] is True

        # Cannot follow blocked user
        r = client.post(f'/api/v1/users/{handle_a}/follow')
        assert r.status_code == 403

        r = client.get('/api/v1/me/blocks')
        assert r.status_code == 200
        assert any(b['handle'] == handle_a for b in r.get_json()['blocked'])

        r = client.delete(f'/api/v1/users/{handle_a}/block')
        assert r.status_code == 200

    print('Phase F smoke tests passed.')


if __name__ == '__main__':
    main()
