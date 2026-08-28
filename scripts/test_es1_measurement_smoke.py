"""ES1 — Measurement (1.1.2) lesson + mixed quiz smoke.

Run: python scripts/test_es1_measurement_smoke.py
"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import GENERATOR_LAUNCH_GCSE_MATHS_CS, app  # noqa: E402
from generators.eursc.science_shared import SYLLABUS_MODULES  # noqa: E402
from generators.shared.lesson_quiz import (  # noqa: E402
    build_lesson_quiz,
    topic_supports_lesson_quiz,
)
from models.lesson_steps import lesson_step_total  # noqa: E402
from models.qotd import list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

LESSON = ROOT / 'templates' / 'eursc_science_measurement_lesson.html'
REF = '1.1.2'


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'es1_{suffix}@example.com',
            'handle': f'es1_{suffix}',
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    return bearer(r.get_json()['token'])


def _plain(text):
    stripped = re.sub(r'<[^>]+>', ' ', str(text or ''))
    return re.sub(r'\s+', ' ', stripped).strip()


def _option_body(option):
    text = str(option or '')
    if len(text) >= 3 and text[0] in 'ABCD' and text[1:3] == '  ':
        return text[3:].strip()
    return text[1:].strip() if text else ''


def _typed_user_answer(problem):
    raw = str(problem.get('correct_answer_raw') or '')
    answer_type = problem.get('answer_type')
    if answer_type == 'number_estimate':
        return raw.split('~', 1)[0].split('|', 1)[0]
    if answer_type == 'proof_steps':
        parts = raw.split('|')
        if parts and parts[0] == 'pick':
            return '|'.join(parts[2:])
        return '|'.join(parts[1:])
    return raw


def answer_bank(cfg):
    """Map normalised question stems to a user answer that grades correct."""
    mapping = {}
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for fn in cfg['variants_func'](difficulty, 'lesson'):
            problem = fn()
            stem = _plain(problem.get('question'))
            if problem.get('options') and problem.get('correct_answer'):
                letter = str(problem['correct_answer'])[:1]
                body = ''
                for option in problem['options']:
                    if str(option)[:1] == letter:
                        body = _option_body(option)
                        break
                mapping[stem] = ('mcq', body)
            else:
                mapping[stem] = ('typed', _typed_user_answer(problem))
    return mapping


def user_answer_for(problem, bank):
    stem = _plain(problem.get('question_html') or problem.get('question'))
    kind_payload = bank.get(stem)
    if kind_payload is None:
        for key, value in bank.items():
            if key and (key in stem or stem in key):
                kind_payload = value
                break
    assert kind_payload, f'unmapped question: {stem[:160]!r}'
    kind, payload = kind_payload
    if kind == 'mcq':
        for option in problem.get('options') or []:
            if _option_body(option) == payload:
                return str(option)[:1]
        raise AssertionError(f'option body {payload!r} missing in {problem.get("options")}')
    return payload


def test_manifest_registry_template():
    module = SYLLABUS_MODULES[REF]
    cfg = TOPICS['eursc']['science']['measurement']
    src = LESSON.read_text(encoding='utf-8')

    assert module['slug'] == 'measurement'
    assert cfg['name'] == module['name']
    assert cfg['order'] == module['order']
    assert cfg['year'] == module['year']
    assert cfg['unit_code'] == module['unit_code']
    assert cfg['unit_name'] == module['unit_name']
    assert cfg['syllabus_ref'] == REF
    assert cfg.get('lesson_bank') is True
    assert topic_supports_lesson_quiz(cfg)

    assert src.count('class="lesson-section"') == module['sections']
    assert src.count('class="mcq-inline"') == module['checkpoints']
    assert src.count('data-correct=') == module['checkpoints']
    assert 'style="' not in src
    assert 'class="lesson-shell"' in src
    assert '1.1.2' in src
    assert 'lesson-quickref' in src
    assert lesson_step_total('eursc', 'science', 'measurement') == module['checkpoints']


def test_bank_size_and_formats():
    cfg = TOPICS['eursc']['science']['measurement']
    mcq = 0
    typed = 0
    kinds = set()
    stems = set()
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for fn in cfg['variants_func'](difficulty, 'lesson'):
            problem = fn()
            stem = _plain(problem.get('question'))
            assert stem not in stems, f'duplicate stem: {stem[:80]!r}'
            stems.add(stem)
            if problem.get('options') and problem.get('correct_answer'):
                mcq += 1
                kinds.add('mcq')
            else:
                typed += 1
                kinds.add(problem.get('answer_type') or 'typed')
    assert mcq >= 15, mcq
    assert typed >= 8, typed
    assert 'mcq' in kinds
    assert 'number' in kinds
    assert 'number_estimate' in kinds
    assert 'keyword' in kinds
    assert 'proof_steps' in kinds

    built = build_lesson_quiz('eursc', 'science', 'measurement', cfg, seed=11)
    assert len(built) == 10
    assert any(p.get('options') for p in built)
    assert any(p.get('answer_type') for p in built)


def test_practice_and_qotd_stay_closed():
    assert GENERATOR_LAUNCH_GCSE_MATHS_CS is True
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())
    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'data-launch-gcse-only="1"' in html
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
        posted = client.post(
            '/',
            data={
                'csrf_token': csrf,
                'level': 'eursc',
                'subject': 'science',
                'topic': 'measurement',
                'mode': 'standard',
                'difficulty': 'foundational',
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        assert 'value="gcse"' in body or 'id="level-select" value="gcse"' in body
        assert 'Convert 3 km' not in body


def test_lesson_route_topics_search():
    with app.test_client() as client:
        lesson = client.get('/topic/eursc/science/measurement')
        assert lesson.status_code == 200, lesson.data[:400]
        html = lesson.data.decode()
        assert 'lesson-shell' in html
        assert html.count('mcq-inline') == 7
        assert 'data-lesson-content' in html
        assert '/lesson-quiz/eursc/science/measurement' in html
        assert '1.1.2' in html

        topics = client.get('/topics')
        assert topics.status_code == 200
        topics_html = topics.data.decode()
        assert '/topic/eursc/science/measurement' in topics_html
        assert 'Measurement and SI Units' in topics_html
        assert 'topic-mastery' in topics_html
        assert 'S1' in topics_html
        assert 'Science Lab' in topics_html

        catalog = client.get('/api/v1/topics')
        assert catalog.status_code == 200
        science = next(
            sub
            for level in catalog.get_json()['levels']
            if level['id'] == 'eursc'
            for sub in level['subjects']
            if sub['id'] == 'science'
        )
        topic = next(t for t in science['topics'] if t['slug'] == 'measurement')
        assert topic['supports_lesson_quiz'] is True
        assert topic['year'] == 's1'
        assert topic.get('syllabus_ref') == REF

        search = client.get('/api/v1/search?q=calibration')
        assert search.status_code == 200
        names = [item.get('name', '') for item in search.get_json().get('topics') or []]
        assert any('measurement' in name.lower() for name in names)


def test_mastery_ring_after_checkpoints():
    cfg = TOPICS['eursc']['science']['measurement']
    total = SYLLABUS_MODULES[REF]['checkpoints']
    keys = [f'step-{i}' for i in range(total)]
    with app.test_client() as client:
        auth = register(client, uuid.uuid4().hex[:8])
        r = client.post(
            '/api/v1/me/lesson-progress',
            json={
                'level': 'eursc',
                'subject': 'science',
                'topic': 'measurement',
                'section_key': keys[-1],
                'section_label': cfg['name'],
                'completed_keys': keys,
                'step_total': total,
            },
            headers=auth,
        )
        assert r.status_code == 200, r.data
        progress = r.get_json()['progress']
        assert len(progress.get('completed_keys') or []) == total
        assert progress['step_total'] == total

        me = client.get(
            '/api/v1/me/lesson-progress/eursc/science/measurement',
            headers=auth,
        )
        assert me.status_code == 200, me.data
        saved = me.get_json()['progress']
        assert len(saved.get('completed_keys') or []) == total
        assert saved['step_total'] == total

        topics = client.get('/topics')
        assert topics.status_code == 200
        assert 'topic-mastery' in topics.data.decode()
        assert '/topic/eursc/science/measurement' in topics.data.decode()


def test_mixed_quiz_api():
    cfg = TOPICS['eursc']['science']['measurement']
    bank = answer_bank(cfg)
    with app.test_client() as client:
        auth = register(client, uuid.uuid4().hex[:8])
        r = client.post(
            '/api/v1/lesson-quiz/start',
            json={'level': 'eursc', 'subject': 'science', 'topic': 'measurement'},
            headers=auth,
        )
        assert r.status_code == 201, r.data
        start = r.get_json()
        session_id = start['session_id']
        assert start['total'] == 10
        first = start['problem']
        assert 'correct_answer' not in first
        assert 'correct_answer_raw' not in first

        spoof = client.post(
            f'/api/v1/lesson-quiz/{session_id}/answer',
            json={
                'user_answer': user_answer_for(first, bank),
                'correct_answer': 'A',
                'correct_answer_raw': '999',
                'answer_type': 'text',
            },
            headers=auth,
        )
        assert spoof.status_code == 200, spoof.data
        assert spoof.get_json()['was_correct'] is True

        last = spoof
        for _ in range(9):
            q = client.get(f'/api/v1/lesson-quiz/{session_id}/question', headers=auth)
            assert q.status_code == 200, q.data
            problem = q.get_json()['problem']
            last = client.post(
                f'/api/v1/lesson-quiz/{session_id}/answer',
                json={'user_answer': user_answer_for(problem, bank)},
                headers=auth,
            )
            assert last.status_code == 200, last.data
        body = last.get_json()
        assert body['finished'] is True
        assert body['score'] == 10

        results = client.get(f'/api/v1/lesson-quiz/{session_id}/results', headers=auth)
        assert results.status_code == 200, results.data
        payload = results.get_json()
        assert payload['score'] == 10
        types_seen = set()
        for item in payload['problems']:
            assert item['was_correct'] is True
            if item.get('options'):
                types_seen.add('mcq')
            elif item.get('answer_type'):
                types_seen.add(item['answer_type'])
        assert 'mcq' in types_seen
        assert any(k != 'mcq' for k in types_seen)

        web = client.get(
            '/lesson-quiz/eursc/science/measurement',
            follow_redirects=True,
        )
        assert web.status_code == 200, web.data[:400]
        html = web.data.decode()
        assert 'data-quiz-runner' in html
        assert 'quiz-runner-active' in html


def main():
    test_manifest_registry_template()
    test_bank_size_and_formats()
    test_practice_and_qotd_stay_closed()
    test_lesson_route_topics_search()
    test_mastery_ring_after_checkpoints()
    test_mixed_quiz_api()
    print('ES1 measurement lesson + mixed quiz smoke tests passed.')


if __name__ == '__main__':
    main()
