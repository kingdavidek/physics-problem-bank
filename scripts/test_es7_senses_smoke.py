"""ES7 — S2 Senses (2.3.1–2.3.8). No new IBL page.

Run: python scripts/test_es7_senses_smoke.py
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
from generators.eursc.science_shared import IBL_PAGES, SYLLABUS_MODULES  # noqa: E402
from generators.shared.lesson_quiz import (  # noqa: E402
    build_lesson_quiz,
    topic_supports_lesson_quiz,
)
from models.lesson_steps import lesson_step_total  # noqa: E402
from models.qotd import list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

TEMPLATES = ROOT / 'templates'
NEW_REFS = ('2.3.1', '2.3.2', '2.3.3', '2.3.4', '2.3.5', '2.3.6', '2.3.7', '2.3.8')
QUIZ_SLUGS = ('vision', 'taste', 'nonhuman_senses')
SVG_SLUGS = {
    'vision': 'Eye schematic',
    'hearing': 'Ear schematic',
    'proprioception_balance': 'Three semicircular canals',
}
DISCLOSE_RE = re.compile(
    r'\b(your diet|have you ever|tell us about your|describe your eating|'
    r'are you allergic|what are you allergic|your body|when did you|'
    r'have you started|are you attracted|your period|have you had sex|'
    r'do you use contraception|your partner|are you gay|your sexuality|'
    r'have you been pregnant|are you pregnant|describe your body|'
    r'do you smoke|have you smoked|do you vape|are you addicted|'
    r'what do you use|list your medication|are you depressed|'
    r'how many hours do you sleep|describe your mood|'
    r'who in your family is ill|have you been ill|'
    r'how do you feel|describe your hunger|are you dizzy|'
    r'map your body|your heartbeat|do you wear glasses)\b',
    re.I,
)


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'es7_{suffix}@example.com',
            'handle': f'es7_{suffix}',
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


def _lesson_path(slug):
    return TEMPLATES / f'eursc_science_{slug}_lesson.html'


def test_manifest_registry_templates():
    science = TOPICS['eursc']['science']
    for ref in NEW_REFS:
        module = SYLLABUS_MODULES[ref]
        slug = module['slug']
        cfg = science[slug]
        src = _lesson_path(slug).read_text(encoding='utf-8')

        assert cfg['name'] == module['name']
        assert cfg['order'] == module['order']
        assert cfg['year'] == 's2'
        assert cfg['unit_code'] == '2.3'
        assert cfg['unit_name'] == 'Senses'
        assert cfg['syllabus_ref'] == ref
        assert cfg.get('lesson_bank') is True
        assert topic_supports_lesson_quiz(cfg)

        assert src.count('class="lesson-section"') == module['sections']
        assert src.count('class="mcq-inline"') == module['checkpoints']
        assert src.count('data-correct=') == module['checkpoints']
        assert 'style="' not in src
        assert 'class="lesson-shell"' in src
        assert ref in src
        assert 'lesson-quickref' in src
        assert lesson_step_total('eursc', 'science', slug) == module['checkpoints']
        assert not DISCLOSE_RE.search(src), slug
        assert "url_for('eursc_ibl_page'" not in src

    shipped = [slug for slug in science if slug != 'es0_fixture']
    assert len(shipped) >= 35, shipped
    orders = [science[slug]['order'] for slug in shipped]
    assert len(orders) == len(set(orders)), orders
    assert 's2_senses' not in science
    assert 's2_touch' not in IBL_PAGES
    assert {'s1_lab', 's1_food', 's2_light', 's2_disease'}.issubset(IBL_PAGES)


def test_bank_size_and_formats():
    for ref in NEW_REFS:
        slug = SYLLABUS_MODULES[ref]['slug']
        cfg = TOPICS['eursc']['science'][slug]
        mcq = 0
        typed = 0
        kinds = set()
        stems = set()
        for difficulty in ('foundational', 'intermediate', 'difficult'):
            for fn in cfg['variants_func'](difficulty, 'lesson'):
                problem = fn()
                stem = _plain(problem.get('question'))
                assert stem not in stems, f'{slug} duplicate stem: {stem[:80]!r}'
                stems.add(stem)
                blob = ' '.join(
                    [
                        stem,
                        str(problem.get('solution') or ''),
                        ' '.join(str(o) for o in (problem.get('options') or [])),
                    ]
                )
                assert not DISCLOSE_RE.search(blob), (slug, stem[:80])
                if problem.get('options') and problem.get('correct_answer'):
                    mcq += 1
                    kinds.add('mcq')
                else:
                    typed += 1
                    kinds.add(problem.get('answer_type') or 'typed')
        assert mcq >= 15, (slug, mcq)
        assert typed >= 8, (slug, typed)
        assert 'mcq' in kinds
        assert 'keyword' in kinds
        assert 'proof_steps' in kinds
        assert 'number' in kinds
        if slug in SVG_SLUGS:
            assert any(
                '<svg' in str(fn().get('question'))
                for difficulty in ('foundational', 'intermediate', 'difficult')
                for fn in cfg['variants_func'](difficulty, 'lesson')
            )

        built = build_lesson_quiz('eursc', 'science', slug, cfg, seed=11)
        assert len(built) == 10
        assert any(p.get('options') for p in built)
        assert any(p.get('answer_type') for p in built)


def test_practice_and_qotd_stay_closed():
    assert ('eursc', 'science') in GENERATOR_LAUNCH_PATHS
    assert ('gcse', 'maths') in GENERATOR_LAUNCH_PATHS
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())
    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'data-launch-gcse-only="1"' in html
        assert 'value="science"' in html
        assert 'value="eursc"' in html
        csrf = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
        posted = client.post(
            '/',
            data={
                'csrf_token': csrf,
                'level': 'eursc',
                'subject': 'science',
                'topic': 'vision',
                'mode': 'standard',
                'difficulty': 'foundational',
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        chunk = body.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in chunk
        assert 'data-subject="science"' in chunk
        assert 'data-topic="vision"' in chunk
        assert 'question-content' in body


def test_lesson_routes_topics_search():
    with app.test_client() as client:
        for ref in NEW_REFS:
            module = SYLLABUS_MODULES[ref]
            slug = module['slug']
            lesson = client.get(f'/topic/eursc/science/{slug}')
            assert lesson.status_code == 200, lesson.data[:400]
            html = lesson.data.decode()
            assert 'lesson-shell' in html
            assert html.count('mcq-inline') == module['checkpoints']
            assert 'data-lesson-content' in html
            assert f'/lesson-quiz/eursc/science/{slug}' in html
            assert ref in html
            needle = SVG_SLUGS.get(slug)
            if needle:
                assert needle in html or '<svg' in html

        topics = client.get('/topics')
        assert topics.status_code == 200
        topics_html = topics.data.decode()
        assert '/topic/eursc/science/vision' in topics_html
        assert '/topic/eursc/science/nonhuman_senses' in topics_html
        assert '2.3 Senses' in topics_html
        assert '/ibl/eursc/science/s2_senses' not in topics_html
        hrefs = re.findall(r'/topic/eursc/science/([a-z0-9_]+)', topics_html)
        shipped = {h for h in hrefs if h != 'es0_fixture'}
        assert len(shipped) >= 35, shipped

        catalog = client.get('/api/v1/topics')
        assert catalog.status_code == 200
        science = next(
            sub
            for level in catalog.get_json()['levels']
            if level['id'] == 'eursc'
            for sub in level['subjects']
            if sub['id'] == 'science'
        )
        slugs = {t['slug'] for t in science['topics']}
        for ref in NEW_REFS:
            assert SYLLABUS_MODULES[ref]['slug'] in slugs
        assert 's2_senses' not in slugs
        assert len({s for s in slugs if s != 'es0_fixture'}) >= 35


def _run_mixed_quiz(client, slug):
    cfg = TOPICS['eursc']['science'][slug]
    bank = answer_bank(cfg)
    auth = register(client, uuid.uuid4().hex[:8])
    r = client.post(
        '/api/v1/lesson-quiz/start',
        json={'level': 'eursc', 'subject': 'science', 'topic': slug},
        headers=auth,
    )
    assert r.status_code == 201, r.data
    start = r.get_json()
    session_id = start['session_id']
    assert start['total'] == 10
    first = start['problem']
    last = client.post(
        f'/api/v1/lesson-quiz/{session_id}/answer',
        json={
            'user_answer': user_answer_for(first, bank),
            'correct_answer': 'A',
            'correct_answer_raw': '999',
            'answer_type': 'text',
        },
        headers=auth,
    )
    assert last.status_code == 200, last.data
    assert last.get_json()['was_correct'] is True
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


def test_mixed_quiz_api():
    with app.test_client() as client:
        for slug in QUIZ_SLUGS:
            _run_mixed_quiz(client, slug)


def main():
    test_manifest_registry_templates()
    test_bank_size_and_formats()
    test_practice_and_qotd_stay_closed()
    test_lesson_routes_topics_search()
    test_mixed_quiz_api()
    print('ES7 Senses lessons smoke tests passed.')


if __name__ == '__main__':
    main()
