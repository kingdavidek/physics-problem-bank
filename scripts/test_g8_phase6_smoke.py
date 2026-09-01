"""G8 Phase 6 verification smoke — sample teacher/student flows.

Run: python scripts/test_g8_phase6_smoke.py
"""
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
from models.reflections import save_reflection  # noqa: E402
from models.user_data import record_quiz_attempt, upsert_lesson_progress  # noqa: E402

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


def dump_ok(payload, *, emails=()):
    text = json.dumps(payload)
    assert T3_SECRET not in text
    assert 'reflection_text' not in text
    assert 'problems_json' not in text
    assert 'correct_answer_raw' not in text
    for email in emails:
        assert email not in text
    return text


def stored_problems(assignment_id):
    with get_db() as conn:
        row = conn.execute(
            'SELECT problems_json FROM class_assignments WHERE id = ?',
            (assignment_id,),
        ).fetchone()
    assert row, assignment_id
    return json.loads(row['problems_json'])


def main():
    assert GENERATOR_LAUNCH_PATHS == LAUNCH_PATHS
    leave_rules = [rule.rule for rule in app.url_map.iter_rules() if '/leave' in rule.rule]
    assert leave_rules == [], leave_rules

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        email_a = f'g8p6a_{suffix}@example.com'
        email_b = f'g8p6b_{suffix}@example.com'
        email_c = f'g8p6c_{suffix}@example.com'
        email_d = f'g8p6d_{suffix}@example.com'
        emails = (email_a, email_b, email_c, email_d)
        token_a, uid_a, _handle_a = register(client, email_a, f'g8p6a_{suffix}')
        token_b, uid_b, handle_b = register(client, email_b, f'g8p6b_{suffix}')
        token_c, _uid_c, _handle_c = register(client, email_c, f'g8p6c_{suffix}')
        token_d, uid_d, handle_d = register(client, email_d, f'g8p6d_{suffix}')
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)
        headers_c = bearer(token_c)
        headers_d = bearer(token_d)

        # Teacher A: enable → class. Teacher C is a second teacher (authz foil).
        class_a, code_a = enable_and_create(client, headers_a, 'Verify 6A')
        class_c, code_c = enable_and_create(client, headers_c, 'Verify 6C')

        # Student B joins A by code after disclosure.
        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a},
            headers=headers_b,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'join_disclosure_required'
        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 201, r.data
        assert r.get_json()['class']['can_leave'] is False

        # Teacher A invites D — not on the roster until accept + disclosure.
        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/invites',
            json={'handle': handle_d},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        invite_d = r.get_json()['invite']['id']
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        handles = {row['handle'] for row in r.get_json()['roster']}
        assert handles == {handle_b}
        r = client.post(
            f'/api/v1/me/class-invites/{invite_d}/accept',
            json={},
            headers=headers_d,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'join_disclosure_required'
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert {row['handle'] for row in r.get_json()['roster']} == {handle_b}
        r = client.post(
            f'/api/v1/me/class-invites/{invite_d}/accept',
            json={'disclosed': True},
            headers=headers_d,
        )
        assert r.status_code == 200, r.data
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert {row['handle'] for row in r.get_json()['roster']} == {handle_b, handle_d}

        # Student B's second class: accept C's handle invite after disclosure.
        r = client.post(
            f'/api/v1/teacher/classes/{class_c}/invites',
            json={'handle': handle_b},
            headers=headers_c,
        )
        assert r.status_code == 201, r.data
        invite_c = r.get_json()['invite']['id']
        r = client.post(
            f'/api/v1/me/class-invites/{invite_c}/accept',
            json={'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 200, r.data
        r = client.get('/api/v1/me/classes', headers=headers_b)
        joined_ids = {item['id'] for item in r.get_json()['classes']}
        assert joined_ids == {class_a, class_c}
        assert r.get_json()['can_leave'] is False

        with get_db() as conn:
            record_quiz_attempt(
                conn, uid_b, 'gcse', 'maths', 'algebra', 4, 10,
                ['A'] * 10, [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            upsert_lesson_progress(
                conn, uid_b, 'gcse', 'maths', 'algebra',
                's-1', 'Intro', completed_keys=['s-1'], step_total=4,
            )
            save_reflection(
                conn, uid_b, 'gcse', 'maths', 'algebra',
                source='check',
                prompt_type='forgot_formula',
                reflection_text=T3_SECRET,
            )

        # Teacher A removes D, then T0–T2 for B.
        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/members/{uid_d}/remove',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        roster = r.get_json()
        dump_ok(roster, emails=emails)
        assert {row['handle'] for row in roster['roster']} == {handle_b}

        r = client.get(f'/api/v1/teacher/classes/{class_a}/progress', headers=headers_a)
        assert r.status_code == 200, r.data
        dump_ok(r.get_json(), emails=emails)

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        progress = r.get_json()['progress']
        dump_ok(progress, emails=emails)
        assert progress['handle'] == handle_b
        assert all('reflection_text' not in gap for gap in progress.get('skill_gaps') or [])

        # Set work → student completes → teacher scores.
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
        dump_ok(assignment, emails=emails)
        aid = assignment['id']
        r = client.post(f'/api/v1/me/class-work/{aid}/reroll', headers=headers_b)
        assert r.status_code == 404
        problems = stored_problems(aid)
        for index, problem in enumerate(problems):
            answer = problem.get('correct_answer_raw')
            if answer is None:
                answer = problem.get('correct_answer')
            r = client.post(
                f'/api/v1/me/class-work/{aid}/answer',
                json={'index': index, 'user_answer': answer},
                headers=headers_b,
            )
            assert r.status_code == 200, r.data
        done = r.get_json()['class_work']
        assert done['status'] == 'complete'
        assert done['can_leave'] is False
        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/assignments/{aid}',
            headers=headers_a,
        )
        rec = r.get_json()['assignment']['recipients'][0]
        assert rec['handle'] == handle_b
        assert rec['status'] == 'complete'
        assert rec['answered_count'] == 2
        dump_ok(r.get_json(), emails=emails)

        # Audit + CSV: handles, never emails or T3.
        r = client.get(f'/api/v1/teacher/classes/{class_a}/audit', headers=headers_a)
        assert r.status_code == 200, r.data
        actions = {event['action'] for event in r.get_json()['events']}
        assert 'class_created' in actions
        assert 'student_joined' in actions
        assert 'invite_sent' in actions
        assert 'invite_accepted' in actions
        assert 'student_removed' in actions
        assert 'assignment_created' in actions
        dump_ok(r.get_json(), emails=emails)

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster.csv', headers=headers_a)
        assert r.status_code == 200, r.data
        roster_csv = r.data.decode()
        assert handle_b in roster_csv
        assert handle_d not in roster_csv
        for email in emails:
            assert email not in roster_csv
        assert T3_SECRET not in roster_csv

        r = client.get(f'/api/v1/teacher/classes/{class_a}/assignments.csv', headers=headers_a)
        assert r.status_code == 200, r.data
        assign_csv = r.data.decode()
        assert handle_b in assign_csv
        assert str(aid) in assign_csv
        for email in emails:
            assert email not in assign_csv
        assert T3_SECRET not in assign_csv

        # Guest / other teacher cannot see roster, progress, audit, or CSV.
        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster')
        assert r.status_code == 401
        for path in (
            f'/api/v1/teacher/classes/{class_a}/roster',
            f'/api/v1/teacher/classes/{class_a}/progress',
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            f'/api/v1/teacher/classes/{class_a}/audit',
            f'/api/v1/teacher/classes/{class_a}/roster.csv',
            f'/api/v1/teacher/classes/{class_a}/assignments.csv',
            f'/api/v1/teacher/classes/{class_a}/assignments/{aid}',
        ):
            r = client.get(path, headers=headers_c)
            assert r.status_code == 404, path
            r = client.get(path, headers=headers_b)
            assert r.status_code == 404, path

        r = client.post(f'/api/v1/me/classes/{class_a}/leave', headers=headers_b)
        assert r.status_code == 404
        r = client.post(f'/api/v1/me/classes/{class_c}/leave', headers=headers_b)
        assert r.status_code == 404

        login_web(client, email_a)
        roster_page = client.get(f'/teacher/classes/{class_a}/roster').data.decode()
        assert handle_b in roster_page
        assert 'Invite by handle' in roster_page
        assert 'Activity log' in roster_page
        assert T3_SECRET not in roster_page
        assert email_b not in roster_page
        assert '/leave' not in roster_page
        assert 'Leave class' not in roster_page
        detail = client.get(f'/teacher/classes/{class_a}/students/{uid_b}').data.decode()
        assert handle_b in detail
        assert T3_SECRET not in detail
        assert 'Private reflection notes are not shown' in detail
        assert email_b not in detail
        audit_page = client.get(f'/teacher/classes/{class_a}/audit').data.decode()
        assert T3_SECRET not in audit_page
        assert email_b not in audit_page
        assert '/leave' not in audit_page
        logout(client)

        login_web(client, email_b)
        classes_page = client.get('/classes').data.decode()
        assert 'Verify 6A' in classes_page
        assert 'Verify 6C' in classes_page
        assert '/leave' not in classes_page
        assert 'Leave class' not in classes_page
        work_page = client.get('/class-work').data.decode()
        assert '/leave' not in work_page
        assert T3_SECRET not in work_page
        logout(client)

        guest = client.get(f'/teacher/classes/{class_a}/roster', follow_redirects=False)
        assert guest.status_code in (302, 401)

    print('G8 Phase 6 verification smoke tests passed.')


if __name__ == '__main__':
    main()
