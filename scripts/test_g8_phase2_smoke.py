"""G8 Phase 2 roster/join smoke — run: python scripts/test_g8_phase2_smoke.py"""
import json
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
from models.classes import (  # noqa: E402
    CLASS_ACTIVE_MEMBER_CAP,
    JOIN_DISCLOSURE,
    join_class,
    teacher_can_view,
)
from models.data_export import build_user_export  # noqa: E402
from models.user import utc_now_iso  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def csrf_from(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, 'csrf token not found'
    return match.group(1)


def logout(client):
    html = client.get('/').data.decode()
    client.post('/logout', data={'csrf_token': csrf_from(html)}, follow_redirects=True)


def login_web(client, email):
    html = client.get('/login').data.decode()
    client.post(
        '/login',
        data={
            'csrf_token': csrf_from(html),
            'email': email,
            'password': 'password123',
        },
        follow_redirects=True,
    )


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
    return body['token'], body['user']['id'], body['user']['handle']


def enable_and_create(client, headers, name):
    r = client.post('/api/v1/me/teacher/enable', headers=headers)
    assert r.status_code == 200, r.data
    r = client.post('/api/v1/teacher/classes', json={'name': name}, headers=headers)
    assert r.status_code == 201, r.data
    klass = r.get_json()['class']
    return klass['id'], klass['join_code']


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_a, uid_a, handle_a = register(client, f'g8p2a_{suffix}@example.com', f'g8p2a_{suffix}')
        token_b, uid_b, handle_b = register(client, f'g8p2b_{suffix}@example.com', f'g8p2b_{suffix}')
        token_c, uid_c, _handle_c = register(client, f'g8p2c_{suffix}@example.com', f'g8p2c_{suffix}')
        token_d, uid_d, handle_d = register(client, f'g8p2d_{suffix}@example.com', f'g8p2d_{suffix}')
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)
        headers_c = bearer(token_c)
        headers_d = bearer(token_d)

        class_a, code_a = enable_and_create(client, headers_a, 'Period 3')
        class_c, code_c = enable_and_create(client, headers_c, 'Period 4')

        r = client.post('/api/v1/me/classes/join', json={'code': code_a}, headers=headers_b)
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'join_disclosure_required'

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': False},
            headers=headers_b,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'join_disclosure_required'

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': 'NOPECODE', 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 404
        assert r.get_json()['code'] == 'invalid_join_code'

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_a,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'self_join'

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 201, r.data
        joined = r.get_json()
        assert joined['class']['id'] == class_a
        assert joined['class']['can_leave'] is False
        assert joined['disclosure'] == JOIN_DISCLOSURE
        assert 'email' not in json.dumps(joined['class'])

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a.lower(), 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 409
        assert r.get_json()['code'] == 'already_member'

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_c, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 201, r.data

        r = client.get('/api/v1/me/classes', headers=headers_b)
        assert r.status_code == 200
        mine = r.get_json()
        assert mine['can_leave'] is False
        assert mine['disclosure'] == JOIN_DISCLOSURE
        assert {item['id'] for item in mine['classes']} == {class_a, class_c}
        assert all(item['can_leave'] is False for item in mine['classes'])
        dump = json.dumps(mine)
        assert 'join_code' not in dump
        assert '@example.com' not in dump

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert r.status_code == 200, r.data
        roster = r.get_json()
        assert len(roster['roster']) == 1
        member = roster['roster'][0]
        assert member['handle'] == handle_b
        assert member['student_id'] == uid_b
        assert 'email' not in member
        assert handle_a not in json.dumps(roster['roster'])
        assert f'g8p2b_{suffix}@example.com' not in json.dumps(roster)

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_c)
        assert r.status_code == 404

        with get_db() as conn:
            assert teacher_can_view(conn, uid_a, uid_b) is True
            assert teacher_can_view(conn, uid_c, uid_b) is True
            assert teacher_can_view(conn, uid_a, uid_c) is False
            exported_b = build_user_export(conn, uid_b)
            assert any(row['id'] == class_a for row in exported_b['classes_joined'])
            assert all('join_code' not in row for row in exported_b['classes_joined'])
            assert all('email' not in row for row in exported_b['classes_joined'])

        now = utc_now_iso()
        with get_db() as conn:
            for i in range(CLASS_ACTIVE_MEMBER_CAP - 1):
                cursor = conn.execute(
                    '''
                    INSERT INTO users (email, handle, password_hash, created_at, last_login_at, is_active)
                    VALUES (?, ?, 'x', ?, NULL, 1)
                    ''',
                    (f'g8fill{i:02d}_{suffix}@example.com', f'g8f{i:02d}{suffix[:6]}', now),
                )
                join_class(conn, cursor.lastrowid, code_a, disclosed=True)

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_d,
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['code'] == 'class_full'

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/members/{uid_b}/remove',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['membership']['status'] == 'removed'

        with get_db() as conn:
            assert teacher_can_view(conn, uid_a, uid_b) is False

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert all(item['student_id'] != uid_b for item in r.get_json()['roster'])

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 201, r.data

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/members/{uid_b}/remove',
            headers=headers_a,
        )
        assert r.status_code == 200

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_d,
        )
        assert r.status_code == 201, r.data

        r = client.post(f'/api/v1/me/classes/{class_a}/leave', headers=headers_b)
        assert r.status_code == 404
        r = client.post(f'/api/v1/me/classes/{class_c}/leave', headers=headers_b)
        assert r.status_code == 404

        login_web(client, f'g8p2b_{suffix}@example.com')
        page = client.get('/classes').data.decode()
        assert 'Join a class' in page
        assert JOIN_DISCLOSURE in page
        assert 'name="disclosed"' in page
        assert '/leave' not in page
        assert 'Leave class' not in page
        assert 'Period 4' in page

        logout(client)
        login_web(client, f'g8p2a_{suffix}@example.com')
        roster_page = client.get(f'/teacher/classes/{class_a}/roster').data.decode()
        assert f'@{handle_d}' in roster_page or handle_d in roster_page
        assert '/leave' not in roster_page
        assert 'Leave class' not in roster_page
        assert f'g8p2d_{suffix}@example.com' not in roster_page
        assert 'Remove' in roster_page

        other_roster = client.get(f'/teacher/classes/{class_c}/roster')
        assert other_roster.status_code == 404

        with get_db() as conn:
            delete_user_account(conn, uid_d)
            leftover = remaining_user_rows(conn, uid_d)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero
            delete_user_account(conn, uid_b)
            leftover_b = remaining_user_rows(conn, uid_b)
            nonzero_b = {table: n for table, n in leftover_b.items() if n}
            assert not nonzero_b, nonzero_b

    print('G8 Phase 2 roster/join smoke tests passed.')


if __name__ == '__main__':
    main()
