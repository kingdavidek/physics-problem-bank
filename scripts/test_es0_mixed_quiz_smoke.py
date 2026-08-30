"""ES0 — mixed lesson quiz + eursc hierarchy smoke.

Run: python scripts/test_es0_mixed_quiz_smoke.py
"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import GENERATOR_LAUNCH_PATHS, app  # noqa: E402
from generators.shared.lesson_quiz import (  # noqa: E402
    build_lesson_quiz,
    grade_lesson_quiz_problem,
    topic_supports_lesson_quiz,
)
from generators.shared.utils import (  # noqa: E402
    make_problem,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
FILENAME_RE = re.compile(
    r'^(gcse|alevel|myp|eursc)_([a-z]+)_([a-z0-9_]+)_lesson\.html$'
)
from topic_registry import TOPICS  # noqa: E402


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'es0_{suffix}@example.com',
            'handle': f'es0_{suffix}',
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    return bearer(r.get_json()['token'])


def known_answer(problem):
    text = problem.get('question_html') or problem.get('question') or ''
    if 'ES0-MCQ-D' in text:
        return 'C'
    if 'ES0-MCQ' in text:
        return 'B'
    if 'ES0-NUM-F' in text:
        return '2000'
    if 'ES0-NUM-I' in text:
        return '3000'
    if 'ES0-NUM-D' in text:
        return '500'
    if 'ES0-KEY-F' in text:
        return 'second'
    if 'ES0-KEY-I' in text:
        return 'kilogram'
    if 'ES0-KEY-D' in text:
        return 'kelvin'
    if 'ES0-ORD' in text:
        return 'q|h|t'
    if 'ES0-PICK' in text:
        return 'metre|second'
    if problem.get('options') and problem.get('correct_answer'):
        return str(problem['correct_answer'])[:1]
    raise AssertionError(f'unknown fixture question: {text[:120]!r}')


def test_filename_pattern():
    name = 'eursc_science_es0_fixture_lesson.html'
    match = FILENAME_RE.match(name)
    assert match, name
    assert match.groups() == ('eursc', 'science', 'es0_fixture')


def test_practice_generator_accepts_eursc():
    assert ('eursc', 'science') in GENERATOR_LAUNCH_PATHS
    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'data-launch-gcse-only="1"' in html
        assert 'value="science"' in html
        assert 'value="eursc"' in html
        assert 'data-level-filter="eursc"' not in html

        csrf = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
        posted = client.post(
            '/',
            data={
                'csrf_token': csrf,
                'level': 'eursc',
                'subject': 'science',
                'topic': 'es0_fixture',
                'mode': 'standard',
                'difficulty': 'foundational',
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        chunk = body.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in chunk
        assert 'data-subject="science"' in chunk
        assert 'data-topic="es0_fixture"' in chunk
        assert 'ES0-MCQ-F' in body


def test_eursc_hierarchy_shell():
    cfg = TOPICS['eursc']['science']['es0_fixture']
    assert topic_supports_lesson_quiz(cfg)
    assert cfg.get('year') == 's1'
    assert cfg.get('unit_name') == 'Science Lab'

    with app.test_client() as client:
        r = client.get('/topics')
        assert r.status_code == 200, r.data[:400]
        html = r.data.decode()
        assert 'data-level-filter="eursc"' in html
        assert 'European School' in html
        assert 'Integrated Science' in html
        assert 'id="icon-science"' in html
        assert 'topic-group--science' in html
        assert 'data-level="eursc"' in html
        assert 'S1' in html
        assert 'Science Lab' in html
        assert '/topic/eursc/science/es0_fixture' in html

        lesson = client.get('/topic/eursc/science/es0_fixture')
        assert lesson.status_code == 200, lesson.data[:400]
        assert b'lesson-shell' in lesson.data

        catalog = client.get('/api/v1/topics')
        assert catalog.status_code == 200
        levels = catalog.get_json()['levels']
        eursc = next(level for level in levels if level['id'] == 'eursc')
        assert eursc['label'] == 'European School'
        science = next(sub for sub in eursc['subjects'] if sub['id'] == 'science')
        assert science['label'] == 'Integrated Science'
        fixture = next(t for t in science['topics'] if t['slug'] == 'es0_fixture')
        assert fixture['supports_lesson_quiz'] is True
        assert fixture['year'] == 's1'


def test_grade_each_mixed_format():
    mcq = make_problem(
        'mcq', 'sol', 'hint', 'foundational', 1, 'eursc', 'science', 'es0_fixture',
        options=['A  no', 'B  yes'],
        correct_answer='B',
        choice_no_shuffle=True,
    )
    assert grade_lesson_quiz_problem(mcq, 'B')['correct'] is True
    assert grade_lesson_quiz_problem(mcq, 'A')['correct'] is False

    numeric = make_problem(
        'num', 'sol', 'hint', 'foundational', 1, 'eursc', 'science', 'es0_fixture',
        correct_answer_raw='2000',
        answer_type='number',
    )
    assert grade_lesson_quiz_problem(numeric, '2000')['correct'] is True
    assert grade_lesson_quiz_problem(numeric, '7')['correct'] is False

    keyword = make_problem(
        'key', 'sol', 'hint', 'foundational', 1, 'eursc', 'science', 'es0_fixture',
        correct_answer_raw='second',
        answer_type='keyword',
    )
    assert grade_lesson_quiz_problem(keyword, 'Second')['correct'] is True

    order_extra = problem_extra_from_graded_answer(
        proof_steps_answer(
            ['q', 'h', 't'],
            [
                {'id': 'q', 'text': 'Ask'},
                {'id': 'h', 'text': 'Hypothesize'},
                {'id': 't', 'text': 'Test'},
                {'id': 'x', 'text': 'Skip'},
            ],
            order_matters=True,
        )
    )
    order = make_problem(
        'ord', 'sol', 'hint', 'foundational', 1, 'eursc', 'science', 'es0_fixture',
        **order_extra,
    )
    assert grade_lesson_quiz_problem(order, 'q|h|t')['correct'] is True
    assert grade_lesson_quiz_problem(order, 't|h|q')['correct'] is False

    pick_extra = problem_extra_from_graded_answer(
        proof_steps_answer(
            ['metre', 'second'],
            [
                {'id': 'metre', 'text': 'metre'},
                {'id': 'second', 'text': 'second'},
                {'id': 'litre', 'text': 'litre'},
            ],
            pick_count=2,
        )
    )
    pick = make_problem(
        'pick', 'sol', 'hint', 'foundational', 1, 'eursc', 'science', 'es0_fixture',
        **pick_extra,
    )
    assert grade_lesson_quiz_problem(pick, 'second|metre')['correct'] is True
    assert grade_lesson_quiz_problem(pick, 'metre|litre')['correct'] is False


def test_mixed_quiz_api_web_retry_security():
    cfg = TOPICS['eursc']['science']['es0_fixture']
    built = build_lesson_quiz('eursc', 'science', 'es0_fixture', cfg, seed=7)
    assert len(built) == 10
    kinds = set()
    for problem in built:
        if problem.get('options'):
            kinds.add('mcq')
        else:
            kinds.add(problem.get('answer_type') or 'typed')
    assert 'mcq' in kinds
    assert any(k != 'mcq' for k in kinds)

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        auth = register(client, suffix)

        r = client.post(
            '/api/v1/lesson-quiz/start',
            json={'level': 'eursc', 'subject': 'science', 'topic': 'es0_fixture'},
            headers=auth,
        )
        assert r.status_code == 201, r.data
        start = r.get_json()
        session_id = start['session_id']
        assert start['total'] == 10
        first = start['problem']
        assert first['question_html']
        assert 'correct_answer' not in first
        assert 'correct_answer_raw' not in first
        assert 'solution_html' not in first

        r = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=auth)
        assert r.status_code == 200, r.data
        q1 = r.get_json()['problem']
        assert 'correct_answer' not in q1
        assert 'correct_answer_raw' not in q1

        spoof = client.post(
            f'/api/v1/lesson-quiz/{session_id}/answer',
            json={
                'user_answer': known_answer(q1),
                'correct_answer': 'A',
                'correct_answer_raw': '999',
                'answer_type': 'text',
            },
            headers=auth,
        )
        assert spoof.status_code == 200, spoof.data
        assert spoof.get_json()['was_correct'] is True

        for _ in range(9):
            q = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=auth)
            assert q.status_code == 200, q.data
            problem = q.get_json()['problem']
            r = client.post(
                f'/api/v1/lesson-quiz/{session_id}/answer',
                json={'user_answer': known_answer(problem)},
                headers=auth,
            )
            assert r.status_code == 200, r.data
        body = r.get_json()
        assert body['finished'] is True
        assert body['score'] == 10

        results = client.get(f'/api/v1/lesson-quiz/{session_id}/results', headers=auth)
        assert results.status_code == 200, results.data
        payload = results.get_json()
        assert payload['score'] == 10
        assert len(payload['problems']) == 10
        assert payload['problems'][0].get('solution_html')
        types_seen = set()
        for item in payload['problems']:
            assert item['was_correct'] is True
            if item.get('options'):
                types_seen.add('mcq')
            elif item.get('answer_type') == 'proof_steps':
                types_seen.add('proof_steps')
            elif item.get('answer_type'):
                types_seen.add(item['answer_type'])
        assert 'mcq' in types_seen

        other = register(client, suffix + 'b')
        denied = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=other)
        assert denied.status_code == 403

        web = client.get('/lesson-quiz/eursc/science/es0_fixture', follow_redirects=True)
        assert web.status_code == 200, web.data[:400]
        html = web.data.decode()
        assert 'data-quiz-runner' in html
        assert 'quiz-runner-active' in html
        assert 'free-response-inline' in html or 'mcq-options' in html

        csrf = re.search(r'name="csrf_token" value="([^"]+)"', html)
        assert csrf, 'csrf missing on mixed quiz page'
        nxt = client.post(
            '/lesson-quiz/eursc/science/es0_fixture/next',
            data={
                'csrf_token': csrf.group(1),
                'qt_user_answer': 'nope',
                'qt_checked': '1',
                'qt_correct': '1',
            },
            follow_redirects=True,
        )
        assert nxt.status_code == 200
        assert b'qt-user-answer' in nxt.data or b'lesson-quiz-form' in nxt.data or b'Submit quiz' in nxt.data or b'Check' in nxt.data

        # Finish remaining mixed questions with wrong answers, then retry.
        for _ in range(20):
            page = nxt.data.decode()
            if 'Retry wrong' in page or 'quiz-results' in page or 'correct out of' in page:
                break
            token = re.search(r'name="csrf_token" value="([^"]+)"', page)
            if not token:
                break
            nxt = client.post(
                '/lesson-quiz/eursc/science/es0_fixture/next',
                data={
                    'csrf_token': token.group(1),
                    'qt_user_answer': 'wrong',
                    'qt_checked': '1',
                    'qt_correct': '1',
                },
                follow_redirects=True,
            )
            assert nxt.status_code == 200
        results_html = nxt.data.decode()
        assert 'correct out of' in results_html or 'Retry wrong' in results_html
        retry = re.search(
            r'action="([^"]+retry-wrong[^"]*)"',
            results_html,
        )
        if retry:
            token = re.search(r'name="csrf_token" value="([^"]+)"', results_html)
            retried = client.post(
                retry.group(1) if retry.group(1).startswith('/') else '/lesson-quiz/eursc/science/es0_fixture/retry-wrong',
                data={'csrf_token': token.group(1) if token else ''},
                follow_redirects=True,
            )
            assert retried.status_code == 200
            assert b'retry' in retried.data.lower() or b'Check' in retried.data


def main():
    test_filename_pattern()
    test_practice_generator_accepts_eursc()
    test_eursc_hierarchy_shell()
    test_grade_each_mixed_format()
    test_mixed_quiz_api_web_retry_security()
    print('ES0 mixed quiz + eursc hierarchy smoke tests passed.')


if __name__ == '__main__':
    main()
