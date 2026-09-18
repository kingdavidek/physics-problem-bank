"""G8 Phase 3 T0–T2 dashboard smoke — run: python scripts/test_g8_phase3_smoke.py"""
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
from models.classes import teacher_can_view  # noqa: E402
from models.reflections import save_reflection  # noqa: E402
from models.user_data import record_quiz_attempt, upsert_lesson_progress  # noqa: E402

T3_SECRET = 'SECRET_T3_NOTE_do_not_show'


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


def assert_no_t3(payload):
    dump = json.dumps(payload)
    assert 'reflection_text' not in dump
    assert T3_SECRET not in dump
    assert '@example.com' not in dump


def main():
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        token_a, uid_a, _handle_a = register(
            client, f'g8p3a_{suffix}@example.com', f'g8p3a_{suffix}'
        )
        token_b, uid_b, handle_b = register(
            client, f'g8p3b_{suffix}@example.com', f'g8p3b_{suffix}'
        )
        token_c, uid_c, _handle_c = register(
            client, f'g8p3c_{suffix}@example.com', f'g8p3c_{suffix}'
        )
        headers_a = bearer(token_a)
        headers_b = bearer(token_b)
        headers_c = bearer(token_c)

        class_a, code_a = enable_and_create(client, headers_a, 'Period 3')
        class_c, _code_c = enable_and_create(client, headers_c, 'Period 4')

        r = client.post(
            '/api/v1/me/classes/join',
            json={'code': code_a, 'disclosed': True},
            headers=headers_b,
        )
        assert r.status_code == 201, r.data

        with get_db() as conn:
            record_quiz_attempt(
                conn, uid_b, 'gcse', 'maths', 'algebra', 4, 10,
                ['A'] * 10, [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            upsert_lesson_progress(
                conn, uid_b, 'gcse', 'maths', 'algebra',
                's-1', 'Intro', completed_keys=['s-1'], step_total=4,
            )
            for topic in ('algebra', 'bidmas'):
                save_reflection(
                    conn, uid_b, 'gcse', 'maths', topic,
                    source='check',
                    prompt_type='forgot_formula',
                    reflection_text=T3_SECRET,
                )
            assert teacher_can_view(conn, uid_a, uid_b) is True

        r = client.get(f'/api/v1/teacher/classes/{class_a}/progress', headers=headers_a)
        assert r.status_code == 200, r.data
        aggregates = r.get_json()['aggregates']
        assert_no_t3(aggregates)
        assert aggregates['student_count'] == 1
        assert aggregates['avg_quiz_pct'] == 40.0
        assert aggregates['quiz_attempts_7d'] == 1
        assert aggregates['set_work']['available'] is False
        assert any(item['topic'] == 'algebra' for item in aggregates['top_weak_topics'])

        r = client.get(f'/api/v1/teacher/classes/{class_a}/progress', headers=headers_c)
        assert r.status_code == 404
        r = client.get(f'/api/v1/teacher/classes/{class_a}/progress', headers=headers_b)
        assert r.status_code == 404

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            headers=headers_a,
        )
        assert r.status_code == 200, r.data
        progress = r.get_json()['progress']
        assert_no_t3(progress)
        assert progress['handle'] == handle_b
        assert progress['student_id'] == uid_b
        assert any(item['topic'] == 'algebra' for item in progress['weak_topics'])
        assert progress['recent_quizzes']
        assert progress['recent_quizzes'][0]['score'] == 4
        assert 'problems' not in progress['recent_quizzes'][0]
        assert 'correct_answer' not in json.dumps(progress['recent_quizzes'])
        assert progress['lessons']
        assert progress['lessons'][0]['completed_count'] >= 1
        assert isinstance(progress['due_today_count'], int)
        assert any(gap['prompt_type'] == 'forgot_formula' for gap in progress['skill_gaps'])
        assert all('reflection_text' not in gap for gap in progress['skill_gaps'])

        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            headers=headers_c,
        )
        assert r.status_code == 404
        r = client.get(
            f'/api/v1/teacher/classes/{class_c}/students/{uid_b}/progress',
            headers=headers_a,
        )
        assert r.status_code == 404
        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_a}/progress',
            headers=headers_a,
        )
        assert r.status_code == 404

        r = client.get(f'/api/v1/teacher/classes/{class_a}/roster', headers=headers_a)
        assert r.status_code == 200
        roster_body = r.get_json()
        assert_no_t3(roster_body)
        member = roster_body['roster'][0]
        assert member['handle'] == handle_b
        assert member['quiz_count_7d'] == 1
        assert member['last_active']
        assert roster_body['aggregates']['student_count'] == 1

        r = client.post(f'/api/v1/me/classes/{class_a}/leave', headers=headers_b)
        assert r.status_code == 404

        login_web(client, f'g8p3a_{suffix}@example.com')
        roster_page = client.get(f'/teacher/classes/{class_a}/roster').data.decode()
        assert 'Class snapshot' in roster_page
        assert handle_b in roster_page
        assert T3_SECRET not in roster_page
        assert f'g8p3b_{suffix}@example.com' not in roster_page
        assert '/leave' not in roster_page
        assert 'Leave class' not in roster_page
        assert 'Progress' in roster_page

        detail = client.get(
            f'/teacher/classes/{class_a}/students/{uid_b}'
        ).data.decode()
        assert handle_b in detail
        assert 'Skill-gap labels' in detail
        assert 'Forgot a formula' in detail or 'forgot_formula' in detail
        assert T3_SECRET not in detail
        assert 'Private reflection notes are not shown' in detail
        assert '/leave' not in detail

        other = client.get(f'/teacher/classes/{class_c}/students/{uid_b}')
        assert other.status_code == 404

        logout(client)

        r = client.post(
            f'/api/v1/teacher/classes/{class_a}/members/{uid_b}/remove',
            headers=headers_a,
        )
        assert r.status_code == 200
        r = client.get(
            f'/api/v1/teacher/classes/{class_a}/students/{uid_b}/progress',
            headers=headers_a,
        )
        assert r.status_code == 404
        with get_db() as conn:
            assert teacher_can_view(conn, uid_a, uid_b) is False

    print('G8 Phase 3 T0–T2 dashboard smoke tests passed.')


if __name__ == '__main__':
    main()
