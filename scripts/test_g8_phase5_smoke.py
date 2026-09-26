"""G8 Phase 5 hardening smoke — run: python scripts/test_g8_phase5_smoke.py"""
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

from app import GENERATOR_LAUNCH_PATHS, app, get_db  # noqa: E402
from models.account_deletion import delete_user_account, remaining_user_rows  # noqa: E402
from models import class_invites as class_invites_model  # noqa: E402
from models.data_export import build_user_export  # noqa: E402
from models.moderation import block_user  # noqa: E402
from models.reflections import save_reflection  # noqa: E402

T3_SECRET = 'SECRET_T3_NOTE_do_not_show'
LAUNCH_PATHS = frozenset({
    ('gcse', 'maths'),
    ('gcse', 'cs'),
    ('eursc', 'science'),
})


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


def assert_no_keys(payload):
    dump = json.dumps(payload)
    assert 'correct_answer' not in dump
    assert 'correct_answer_raw' not in dump
    assert 'solution_html' not in dump
    assert T3_SECRET not in dump
    assert 'problems_json' not in dump


def main():
    assert GENERATOR_LAUNCH_PATHS == LAUNCH_PATHS

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        email_a = f'g8p5a_{suffix}@example.com'
        email_b = f'g8p5b_{suffix}@example.com'
        email_c = f'g8p5c_{suffix}@example.com'
        email_d = f'g8p5d_{suffix}@example.com'
        token_a, uid_a, handle_a = register(client, email_a, f'g8p5a_{suffix}')
        token_b, uid_b, handle_b = register(client, email_b, f'g8p5b_{suffix}')
        token_c, uid_c, _handle_c = register(client, email_c, f'g8p5c_{suffix}')
        token_d, uid_d, handle_d = register(client, email_d, f'g8p5d_{suffix}')
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)
        headers_c = bearer(token_c)
        headers_d = bearer(token_d)

        class_a, _code_a = enable_and_create(client, headers_a, 'Period 5A')
        class_c, code_c = enable_and_create(client, headers_c, 'Period 5C')

        with get_db() as conn:
            save_reflection(
                conn, uid_b, 'gcse', 'maths', 'bidmas',
                source='check',
                prompt_type='forgot_formula',
                reflection_text=T3_SECRET,
            )

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_b},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        invite = r.get_json()['invite']
        invite_id = invite['id']
        assert invite['student_handle'] == handle_b
        assert invite['status'] == 'pending'
        assert 'email' not in json.dumps(invite)
        assert '@example.com' not in json.dumps(invite)

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert r.status_code == 200, r.data
        roster = r.get_json()
        assert roster['roster'] == []
        assert any(item['id'] == invite_id for item in roster['pending_invites'])
        assert_no_keys(roster)

        r = client.get('/api/v1/me/classes', headers=headers_b)
        assert r.status_code == 200, r.data
        me_classes = r.get_json()
        assert me_classes['classes'] == []
        assert me_classes['can_leave'] is False
        assert len(me_classes['invites']) == 1
        assert me_classes['invites'][0]['id'] == invite_id
        assert me_classes['invites'][0]['disclosure']
        assert_no_keys(me_classes)

        r = client.post(
            f'/api/v1/me/class-invites/{invite_id}/accept',
            json={},
            headers=headers_b,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'join_disclosure_required'

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert r.get_json()['roster'] == []

        r = client.post(
            f'/api/v1/me/class-invites/{invite_id}/accept',
            json={'disclosed': True},
            headers=headers_d,
        )
        assert r.status_code == 404

        r = client.post(
            f'/api/v1/me/class-invites/{invite_id}/accept',
            json={'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 200, r.data
        joined = r.get_json()
        assert joined['class']['id'] == class_a
        assert joined['class']['can_leave'] is False
        assert joined['can_leave'] is False

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        members = r.get_json()['roster']
        assert {row['handle'] for row in members} == {handle_b}
        assert r.get_json()['pending_invites'] == []

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_b},
            headers=headers_a,
        )
        assert r.status_code == 409
        assert r.get_json()['code'] == 'already_member'

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_d},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        invite_d = r.get_json()['invite']['id']
        r = client.post(
            f'/api/v1/me/class-invites/{invite_d}/decline',
            headers=headers_d,
        )
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/me/classes', headers=headers_d)
        assert r.get_json()['classes'] == []
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert {row['handle'] for row in r.get_json()['roster']} == {handle_b}

        orig_pending = class_invites_model._pending_count
        class_invites_model._pending_count = (
            lambda conn, cid: class_invites_model.MAX_PENDING_INVITES_PER_CLASS
        )
        try:
            r = client.post(
                f'/api/v1/teacher/classes/{class_a}/invites',
                json={'handle': handle_d},
                headers=headers_a,
            )
            assert r.status_code == 400, r.data
            assert r.get_json()['code'] == 'invite_limit'
        finally:
            class_invites_model._pending_count = orig_pending

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_d},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        invite_expired = r.get_json()['invite']['id']
        with get_db() as conn:
            conn.execute(
                'UPDATE class_invites SET created_at = ? WHERE id = ?',
                ('2000-01-01T00:00:00+00:00', invite_expired),
            )
            conn.commit()
        r = client.get('/api/v1/me/classes', headers=headers_d)
        assert all(item['id'] != invite_expired for item in r.get_json()['invites'])
        r = client.post(
            f'/api/v1/me/class-invites/{invite_expired}/accept',
            json={'disclosed': True},
            headers=headers_d,
        )
        assert r.status_code == 409
        assert r.get_json()['code'] == 'invite_not_pending'
        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_d},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        r = client.post(
            f'/api/v1/me/class-invites/{r.get_json()["invite"]["id"]}/decline',
            headers=headers_d,
        )
        assert r.status_code == 200, r.data

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': 'nobody_here_xyz'},
            headers=headers_a,
        )
        assert r.status_code == 404
        assert r.get_json()['code'] == 'user_not_found'

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_a},
            headers=headers_a,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'self_invite'

        with get_db() as conn:
            block_user(conn, uid_b, uid_c)
        r = client.post(
            f'/api/v1/teacher/classes/{class_c}/invites',
            json={'handle': handle_b},
            headers=headers_c,
        )
        assert r.status_code == 403
        assert r.get_json()['code'] == 'blocked'
        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_c, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 404
        assert r.get_json()['code'] == 'invalid_join_code'

        r = client.get('/api/v1/me/notifications?limit=20', headers=headers_b)
        assert r.status_code == 200, r.data
        notes = r.get_json()['notifications']
        class_notes = [item for item in notes if item.get('type') == 'class_invite']
        assert class_notes
        assert class_notes[0].get('actions') == []
        assert '/classes' in (class_notes[0].get('url') or '')

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
                'mode': 'standard',
                'count': 2,
                'student_ids': [uid_b],
            },
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        assignment = r.get_json()['assignment']
        assert_no_keys(assignment)

        r = client.get(f'/api/v1/teacher/classes/{class_a}/audit', headers=headers_a)
        assert r.status_code == 200, r.data
        audit = r.get_json()
        actions = {event['action'] for event in audit['events']}
        assert 'class_created' in actions
        assert 'invite_sent' in actions
        assert 'invite_accepted' in actions
        assert 'student_joined' in actions
        assert 'assignment_created' in actions
        dump = json.dumps(audit)
        assert email_b not in dump
        assert T3_SECRET not in dump
        assert 'problems_json' not in dump
        assert_no_keys(audit)

        r = client.get(f'/api/v1/teacher/classes/{class_a}/audit', headers=headers_c)
        assert r.status_code == 404
        r = client.get(f'/api/v1/teacher/classes/{class_a}/audit', headers=headers_b)
        assert r.status_code == 404

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster.csv', headers=headers_a)
        assert r.status_code == 200, r.data
        assert 'csv' in (r.mimetype or '')
        roster_csv = r.data.decode()
        assert 'handle' in roster_csv.splitlines()[0]
        assert handle_b in roster_csv
        assert email_b not in roster_csv
        assert email_a not in roster_csv
        assert T3_SECRET not in roster_csv

        r = client.get(f'/api/v1/teacher/classes/{class_a}/assignments.csv', headers=headers_a)
        assert r.status_code == 200, r.data
        assign_csv = r.data.decode()
        assert handle_b in assign_csv
        assert str(assignment['id']) in assign_csv
        assert email_b not in assign_csv
        assert T3_SECRET not in assign_csv
        assert 'correct_answer' not in assign_csv

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster.csv', headers=headers_c)
        assert r.status_code == 404
        r = client.get(f'/api/v1/teacher/classes/{class_a}/assignments.csv', headers=headers_b)
        assert r.status_code == 404

        r = client.post(f'/api/v1/me/classes/{class_a}/leave', headers=headers_b)
        assert r.status_code == 404

        login_web(client, email_a)
        roster_page = client.get(f'/teacher/classes/{class_a}/roster').data.decode()
        assert 'Invite by handle' in roster_page
        assert 'Activity log' in roster_page
        assert 'Roster CSV' in roster_page
        assert '/leave' not in roster_page
        assert T3_SECRET not in roster_page
        assert email_b not in roster_page
        audit_page = client.get(f'/teacher/classes/{class_a}/audit').data.decode()
        assert 'invite accepted' in audit_page or 'invite_accepted' in audit_page
        assert T3_SECRET not in audit_page
        assert email_b not in audit_page
        web_csv = client.get(f'/teacher/classes/{class_a}/roster.csv')
        assert web_csv.status_code == 200
        assert handle_b in web_csv.data.decode()
        logout(client)

        login_web(client, email_b)
        classes_page = client.get('/classes').data.decode()
        assert 'Period 5A' in classes_page
        assert '/leave' not in classes_page
        assert T3_SECRET not in classes_page
        logout(client)

        with get_db() as conn:
            export_b = build_user_export(conn, uid_b)
            export_a = build_user_export(conn, uid_a)
        dump_b = json.dumps(export_b)
        dump_a = json.dumps(export_a)
        assert export_b['class_invites_received']
        assert export_b['classes_joined']
        assert 'problems_json' not in dump_b
        assert email_a not in dump_b
        assert export_a['teacher']['invites_sent']
        assert export_a['teacher']['class_audit']
        assert 'problems_json' not in dump_a
        assert T3_SECRET not in dump_a
        assert email_b not in dump_a
        assert email_d not in dump_a

        with get_db() as conn:
            counts = delete_user_account(conn, uid_b)
            assert counts.get('ok') is True
            leftover = remaining_user_rows(conn, uid_b)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero
            audit_row = conn.execute(
                '''
                SELECT subject_handle FROM class_audit_events
                WHERE class_id = ? AND action = 'invite_accepted'
                ''',
                (class_a,),
            ).fetchone()
            assert audit_row
            assert handle_b.lower() not in (audit_row['subject_handle'] or '').lower()

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert r.status_code == 200
        assert r.get_json()['roster'] == []

        privacy = client.get('/privacy').data.decode()
        assert 'handle invite' in privacy.lower() or 'accepting an invite' in privacy.lower()
        simple = client.get('/privacy/simple').data.decode()
        assert 'invite' in simple.lower()

    print('G8 Phase 5 hardening smoke tests passed.')


if __name__ == '__main__':
    main()
