"""G8 Phase 1 teacher/class smoke — run: python scripts/test_g8_phase1_smoke.py"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ.setdefault('SECRET_KEY', 'pb-testing')

from app import app, get_db  # noqa: E402
from models.account_deletion import delete_user_account, remaining_user_rows  # noqa: E402
from models.classes import CLASS_ACTIVE_MEMBER_CAP, teacher_can_view, teacher_owns_class  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, 'csrf token not found'
    return match.group(1)


def register(client, email, handle):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': email,
            'handle': handle,
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
        suffix = uuid.uuid4().hex[:8]
        token_a, uid_a = register(client, f'g8a_{suffix}@example.com', f'g8a_{suffix}')
        token_b, uid_b = register(client, f'g8b_{suffix}@example.com', f'g8b_{suffix}')
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)

        r = client.get('/api/v1/me/teacher', headers=headers_a)
        assert r.status_code == 200
        assert r.get_json()['enabled'] is False

        r = client.post('/api/v1/teacher/classes', json={'name': 'Period 3'}, headers=headers_a)
        assert r.status_code == 403
        assert r.get_json()['code'] == 'teacher_required'

        r = client.post('/api/v1/me/teacher/enable', headers=headers_a)
        assert r.status_code == 200
        enabled = r.get_json()
        assert enabled['ok'] is True
        assert enabled['enabled'] is True
        assert enabled['active_member_cap'] == CLASS_ACTIVE_MEMBER_CAP

        r = client.post('/api/v1/me/teacher/enable', headers=headers_a)
        assert r.status_code == 200
        assert r.get_json()['enabled'] is True

        r = client.post(
            '/api/v1/teacher/classes',
            json={'name': 'Period 3', 'level': 'gcse', 'subject': 'maths', 'org_id': 1},
            headers=headers_a,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'invalid_field'

        r = client.post(
            '/api/v1/teacher/classes',
            json={'name': 'Period 3', 'level': 'gcse', 'subject': 'maths'},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        klass = r.get_json()['class']
        class_id = klass['id']
        code_one = klass['join_code']
        assert len(code_one) == 8
        assert klass['org_id'] is None
        assert klass['archived_at'] is None
        assert klass['active_member_cap'] == CLASS_ACTIVE_MEMBER_CAP

        r = client.get('/api/v1/teacher/classes', headers=headers_a)
        assert r.status_code == 200
        assert len(r.get_json()['classes']) == 1

        r = client.get(f'/api/v1/teacher/classes/{class_id}', headers=headers_b)
        assert r.status_code == 404
        r = client.get('/api/v1/teacher/classes', headers=headers_b)
        assert r.status_code == 403
        r = client.post(
            f'/api/v1/teacher/classes/{class_id}/rotate-code',
            headers=headers_b,
        )
        assert r.status_code == 404

        r = client.post(f'/api/v1/teacher/classes/{class_id}/rotate-code', headers=headers_a)
        assert r.status_code == 200
        code_two = r.get_json()['class']['join_code']
        assert code_two != code_one

        r = client.post(f'/api/v1/teacher/classes/{class_id}/archive', headers=headers_a)
        assert r.status_code == 200
        assert r.get_json()['class']['archived_at']

        r = client.post(f'/api/v1/teacher/classes/{class_id}/rotate-code', headers=headers_a)
        assert r.status_code == 400
        assert r.get_json()['code'] == 'class_archived'

        r = client.post('/api/v1/me/classes/join', json={'code': code_two}, headers=headers_b)
        assert r.status_code == 400
        assert r.get_json()['code'] == 'join_disclosure_required'
        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_two, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 404
        assert r.get_json()['code'] == 'invalid_join_code'
        r = client.post(f'/api/v1/me/classes/{class_id}/leave', headers=headers_b)
        assert r.status_code == 404
        r = client.get(f'/api/v1/teacher/classes/{class_id}/roster', headers=headers_a)
        assert r.status_code == 200
        assert r.get_json()['roster'] == []

        with get_db() as conn:
            assert teacher_owns_class(conn, uid_a, class_id)
            assert not teacher_owns_class(conn, uid_b, class_id)
            assert teacher_can_view(conn, uid_a, uid_b) is False

        html = client.get('/login').data.decode()
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(html),
                'email': f'g8a_{suffix}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )
        page = client.get('/teacher/classes').data.decode()
        assert 'Teacher classes' in page
        assert 'Archived' in page
        assert '/leave' not in page
        assert 'Leave class' not in page

        with get_db() as conn:
            delete_user_account(conn, uid_a)
            leftover = remaining_user_rows(conn, uid_a)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero

    print('G8 Phase 1 teacher/class smoke tests passed.')


if __name__ == '__main__':
    main()
