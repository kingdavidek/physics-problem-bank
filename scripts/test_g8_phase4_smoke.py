"""G8 Phase 4 frozen set-work smoke — run: python scripts/test_g8_phase4_smoke.py"""
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


def join(client, headers, code):
    r = client.post(
        '/api/v1/me/classes/join',
        json={'code': code, 'disclosed': True},
        headers=headers,
    )
    assert r.status_code == 201, r.data


def assert_no_keys(payload):
    dump = json.dumps(payload)
    assert 'correct_answer' not in dump
    assert 'correct_answer_raw' not in dump
    assert 'solution_html' not in dump
    assert T3_SECRET not in dump
    assert '@example.com' not in dump


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

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_a, uid_a, _handle_a = register(
            client, f'g8p4a_{suffix}@example.com', f'g8p4a_{suffix}'
        )
        token_b, uid_b, handle_b = register(
            client, f'g8p4b_{suffix}@example.com', f'g8p4b_{suffix}'
        )
        token_c, uid_c, _handle_c = register(
            client, f'g8p4c_{suffix}@example.com', f'g8p4c_{suffix}'
        )
        token_d, uid_d, handle_d = register(
            client, f'g8p4d_{suffix}@example.com', f'g8p4d_{suffix}'
        )
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)
        headers_c = bearer(token_c)
        headers_d = bearer(token_d)

        class_a, code_a = enable_and_create(client, headers_a, 'Period 4A')
        class_c, _code_c = enable_and_create(client, headers_c, 'Period 4C')
        join(client, headers_b, code_a)
        join(client, headers_d, code_a)

        with get_db() as conn:
            save_reflection(
                conn, uid_b, 'gcse', 'maths', 'bidmas',
                source='check',
                prompt_type='forgot_formula',
                reflection_text=T3_SECRET,
            )

        scope = {
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'bidmas',
            'difficulty': 'foundational',
            'mode': 'standard',
            'count': 3,
        }

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'preview': True},
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        preview = r.get_json()['preview']
        assert preview['question_count'] == 3
        assert len(preview['problems']) == 3
        assert_no_keys(preview)
        preview_id = preview['preview_id']

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'level': 'alevel', 'subject': 'physics', 'topic': 'particles', 'preview': True},
            headers=headers_a,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'invalid_topic'

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'count': 21, 'student_ids': [uid_b]},
            headers=headers_a,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'invalid_count'

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={'preview_id': preview_id, 'student_ids': [uid_b]},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        assignment_b = r.get_json()['assignment']
        aid_b = assignment_b['id']
        assert_no_keys(assignment_b)
        assert assignment_b['can_reroll'] is False
        assert len(assignment_b['recipients']) == 1
        assert assignment_b['recipients'][0]['handle'] == handle_b
        assert assignment_b['recipients'][0]['answered_count'] == 0
        assert assignment_b['recipients'][0]['question_count'] == 3

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'preview': True},
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        stale_id = r.get_json()['preview']['preview_id']
        with get_db() as conn:
            conn.execute(
                'UPDATE class_assignment_previews SET created_at = ? WHERE id = ?',
                ('2000-01-01T00:00:00+00:00', stale_id),
            )
            conn.commit()
        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={'preview_id': stale_id, 'student_ids': [uid_b]},
            headers=headers_a,
        )
        assert r.status_code == 404

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'student_ids': [uid_d]},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        assignment_d = r.get_json()['assignment']
        aid_d = assignment_d['id']
        assert aid_d != aid_b

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/assignments',
            json={**scope, 'all': True},
            headers=headers_a,
        )
        assert r.status_code == 201, r.data
        assignment_all = r.get_json()['assignment']
        assert {row['student_id'] for row in assignment_all['recipients']} == {uid_b, uid_d}

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/assignments/{aid_b}',
            headers=headers_c,
        )
        assert r.status_code == 404
        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/assignments/{aid_b}',
            headers=headers_b,
        )
        assert r.status_code == 404

        r = client.get('/api/v1/me/class-work', headers=headers_b)
        assert r.status_code == 200, r.data
        work_list = r.get_json()
        assert work_list['can_leave'] is False
        ids_b = {item['assignment_id'] for item in work_list['class_work']}
        assert aid_b in ids_b
        assert aid_d not in ids_b
        assert_no_keys(work_list)

        r = client.get(f'/api/v1/me/class-work/{aid_b}', headers=headers_b)
        assert r.status_code == 200, r.data
        work = r.get_json()['class_work']
        assert work['can_reroll'] is False
        assert work['can_leave'] is False
        assert_no_keys(work)
        assert work['answered_count'] == 0

        r = client.get(f'/api/v1/me/class-work/{aid_d}', headers=headers_b)
        assert r.status_code == 404
        r = client.get(f'/api/v1/me/class-work/{aid_b}', headers=headers_d)
        assert r.status_code == 404

        r = client.post(f'/api/v1/me/class-work/{aid_b}/reroll', headers=headers_b)
        assert r.status_code == 404
        r = client.post(f'/api/v1/me/classes/{class_a}/leave', headers=headers_b)
        assert r.status_code == 404

        problems = stored_problems(aid_b)
        first = problems[0]
        stored_key = first.get('correct_answer_raw')
        if stored_key is None:
            stored_key = first.get('correct_answer')
        assert stored_key is not None

        r = client.post(
            f'/api/v1/me/class-work/{aid_b}/answer',
            json={
                'index': 0,
                'user_answer': 'definitely-wrong-xyz',
                'correct_answer': stored_key,
                'correct_answer_raw': stored_key,
            },
            headers=headers_b,
        )
        assert r.status_code == 200, r.data
        after_wrong = r.get_json()['class_work']
        assert after_wrong['problems'][0]['answered'] is True
        assert after_wrong['problems'][0]['correct'] is False
        assert after_wrong['answered_count'] == 1
        dump_after = json.dumps(after_wrong)
        assert 'correct_answer' in dump_after or 'solution_html' in dump_after
        assert_no_keys({'problems': after_wrong['problems'][1:]})

        r = client.post(
            f'/api/v1/me/class-work/{aid_b}/answer',
            json={'index': 0, 'user_answer': stored_key},
            headers=headers_b,
        )
        assert r.status_code == 400
        assert r.get_json()['code'] == 'already_answered'

        for index, problem in enumerate(problems[1:], start=1):
            answer = problem.get('correct_answer_raw')
            if answer is None:
                answer = problem.get('correct_answer')
            r = client.post(
                f'/api/v1/me/class-work/{aid_b}/answer',
                json={'index': index, 'user_answer': answer},
                headers=headers_b,
            )
            assert r.status_code == 200, r.data

        done = r.get_json()['class_work']
        assert done['status'] == 'complete'
        assert done['answered_count'] == 3
        assert done['score'] >= 2

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/assignments/{aid_b}',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        teacher_view = r.get_json()['assignment']
        assert_no_keys(teacher_view)
        rec = teacher_view['recipients'][0]
        assert rec['answered_count'] == 3
        assert rec['question_count'] == 3
        assert rec['score'] == done['score']
        assert rec['status'] == 'complete'

        r = client.get(f'/api/v1/teacher/classes/{class_a}/progress', headers=headers_a)
        assert r.status_code == 200
        aggregates = r.get_json()['aggregates']
        assert_no_keys(aggregates)
        assert aggregates['set_work']['available'] is True
        assert aggregates['set_work']['assigned'] >= 4
        assert aggregates['set_work']['complete'] >= 1

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            headers=headers_a,
        )
        assert r.status_code == 200
        progress = r.get_json()['progress']
        assert_no_keys(progress)
        assert any(item['assignment_id'] == aid_b for item in progress['set_work'])

        r = client.get('/api/v1/me/export', headers=headers_b)
        assert r.status_code in (200, 403)

        with get_db() as conn:
            from models.data_export import build_user_export
            payload = build_user_export(conn, uid_b)
        class_work = payload.get('class_work') or []
        assert class_work
        export_dump = json.dumps(payload)
        assert 'problems_json' not in export_dump
        assert 'correct_answer_raw' not in export_dump
        assert f'g8p4a_{suffix}@example.com' not in export_dump

        login_web(client, f'g8p4a_{suffix}@example.com')
        set_page = client.get(f'/teacher/classes/{class_a}/assignments').data.decode()
        assert 'Set work' in set_page
        assert 'Preview questions' in set_page
        assert '/leave' not in set_page
        scores = client.get(
            f'/teacher/classes/{class_a}/assignments/{aid_b}'
        ).data.decode()
        assert handle_b in scores
        assert T3_SECRET not in scores
        assert f'g8p4b_{suffix}@example.com' not in scores
        assert '/leave' not in scores
        roster_page = client.get(f'/teacher/classes/{class_a}/roster').data.decode()
        assert 'Set work:' in roster_page
        logout(client)

        login_web(client, f'g8p4b_{suffix}@example.com')
        mine = client.get('/class-work').data.decode()
        assert 'My class work' in mine
        assert 'cannot reroll' in mine.lower() or 'cannot reroll' in mine
        detail = client.get(f'/class-work/{aid_b}').data.decode()
        assert 'frozen' in detail.lower()
        assert T3_SECRET not in detail
        classes_page = client.get('/classes').data.decode()
        assert 'Leave class' not in classes_page
        assert '/leave' not in classes_page
        logout(client)

        assert GENERATOR_LAUNCH_PATHS == LAUNCH_PATHS

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/members/{uid_d}/remove',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        r = client.get(f'/api/v1/me/class-work/{aid_d}', headers=headers_d)
        assert r.status_code == 404
        r = client.get('/api/v1/me/class-work', headers=headers_d)
        assert r.status_code == 200
        ids_d = {item['assignment_id'] for item in r.get_json()['class_work']}
        assert aid_d not in ids_d

        with get_db() as conn:
            delete_user_account(conn, uid_d)
            leftover = remaining_user_rows(conn, uid_d)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero
            rec_d = conn.execute(
                'SELECT COUNT(*) AS n FROM class_assignment_recipients WHERE student_id = ?',
                (uid_d,),
            ).fetchone()['n']
            assert rec_d == 0

    print('G8 Phase 4 frozen set-work smoke tests passed.')


if __name__ == '__main__':
    main()
