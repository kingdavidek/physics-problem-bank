"""ES10 — European School whole-suite QA smoke.

Run: python scripts/test_es10_whole_suite_smoke.py
"""
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import GENERATOR_LAUNCH_PATHS, app, get_db  # noqa: E402
from generators.eursc.science_shared import IBL_PAGES, SYLLABUS_MODULES  # noqa: E402
from generators.shared.lesson_quiz import topic_supports_lesson_quiz  # noqa: E402
from models.lesson_search import build_lesson_search_docs  # noqa: E402
from models.lesson_steps import lesson_step_total  # noqa: E402
from models.qotd import list_mcq_topic_paths  # noqa: E402
from models.revision_planner import revision_plan_for_user, upsert_revision_plan_settings  # noqa: E402
from models.topic_status import (  # noqa: E402
    catalog_extra_entries,
    milestone_keys_for_statuses,
    subject_badge_key,
)
from models.user_data import record_quiz_attempt  # noqa: E402
from topic_registry import TOPICS, validate_topic_registry  # noqa: E402

TEMPLATES = ROOT / 'templates'
NINE_UNITS = (
    ('1.1', 'Science Lab'),
    ('1.2', 'Food'),
    ('1.3', 'Sports'),
    ('1.4', 'Puberty'),
    ('2.1', 'Universe'),
    ('2.2', 'Health'),
    ('2.3', 'Senses'),
    ('3.1', 'Machines'),
    ('3.2', 'Living Earth'),
)
SENSITIVE_REFS = tuple(
    ref
    for ref in SYLLABUS_MODULES
    if ref.startswith('1.4.') or ref.startswith('2.2.')
)
SEARCH_QUERIES = (
    ('calibration', 'measurement'),
    ('reproducibility', 'what_is_science'),
    ('infectious', 'infectious_disease'),
    ('quadrat', 'ecology_field_project'),
    ('lever', 'force_work_machines'),
)
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
_OBJECTIVE_STOP = frozenset(
    {
        'that', 'this', 'with', 'from', 'into', 'when', 'they', 'them', 'their',
        'have', 'been', 'being', 'such', 'only', 'does', 'must', 'should', 'will',
        'here', 'where', 'what', 'which', 'than', 'then', 'your', 'pupil', 'class',
        'group', 'lesson', 'ideas', 'idea', 'name', 'named', 'using', 'used',
        'describe', 'explain', 'outline', 'state', 'plan', 'write', 'read', 'give',
        'link', 'follow', 'choose', 'record', 'present', 'analyse', 'analyze',
        'recognise', 'recognize', 'distinguish', 'identify', 'compare', 'order',
        'critique', 'model', 'public', 'teacher', 'simple', 'another', 'other',
        'through', 'between', 'without', 'need', 'needs', 'including', 'including',
    }
)


def _production_eursc_slugs():
    return {
        slug
        for slug in TOPICS['eursc']['science']
        if slug != 'es0_fixture'
    }


def _lesson_path(slug):
    return TEMPLATES / f'eursc_science_{slug}_lesson.html'


def _objective_traceable(objective, lesson_html):
    tokens = [
        word
        for word in re.findall(r'[a-z]{4,}', objective.lower())
        if word not in _OBJECTIVE_STOP
    ]
    if not tokens:
        return True
    hay = lesson_html.lower()

    def token_hits(token):
        if token in hay:
            return True
        if token.endswith('ies') and f'{token[:-3]}y' in hay:
            return True
        if token.endswith('s') and token[:-1] in hay:
            return True
        return False

    return any(token_hits(token) for token in tokens)


def bearer(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}


def register(client, suffix):
    r = client.post(
        '/api/v1/auth/register',
        json={
            'email': f'es10_{suffix}@example.com',
            'handle': f'es10_{suffix}',
            'password': 'password123',
            'age_confirm': True,
        },
        headers={'Accept': 'application/json'},
    )
    assert r.status_code == 201, r.data
    return bearer(r.get_json()['token']), r.get_json()['user']['id']


def test_manifest_registry_bijection():
    assert len(SYLLABUS_MODULES) == 46
    validate_topic_registry()
    science = TOPICS['eursc']['science']
    slugs = _production_eursc_slugs()
    assert len(slugs) == 46
    manifest_slugs = {module['slug'] for module in SYLLABUS_MODULES.values()}
    assert manifest_slugs == slugs
    for ref, module in SYLLABUS_MODULES.items():
        slug = module['slug']
        cfg = science[slug]
        assert cfg['name'] == module['name']
        assert cfg['order'] == module['order']
        assert cfg['year'] == module['year']
        assert cfg['unit_code'] == module['unit_code']
        assert cfg['unit_name'] == module['unit_name']
        assert cfg['syllabus_ref'] == ref
        assert cfg.get('lesson_bank') is True
        assert topic_supports_lesson_quiz(cfg)


def test_templates_depth_and_objectives():
    missing_objectives = []
    for ref, module in SYLLABUS_MODULES.items():
        slug = module['slug']
        src = _lesson_path(slug).read_text(encoding='utf-8')
        assert src.count('class="lesson-section"') == module['sections'], slug
        assert src.count('class="mcq-inline"') == module['checkpoints'], slug
        assert src.count('data-correct=') == module['checkpoints'], slug
        assert 'style="' not in src, slug
        assert 'class="lesson-shell"' in src, slug
        assert 'lesson-quickref' in src, slug
        assert ref in src, slug
        assert lesson_step_total('eursc', 'science', slug) == module['checkpoints']
        for objective in module.get('objectives') or ():
            if not _objective_traceable(objective, src):
                missing_objectives.append((ref, objective))
    assert not missing_objectives, missing_objectives[:5]


def test_topics_catalog_and_units():
    with app.test_client() as client:
        topics = client.get('/topics')
        assert topics.status_code == 200
        html = topics.data.decode()
        assert 'data-level-filter="eursc"' in html
        assert 'European School' in html
        for code, name in NINE_UNITS:
            assert f'{code} {name}' in html, (code, name)
        for year in ('S1', 'S2', 'S3'):
            assert year in html
        hrefs = {
            slug
            for slug in re.findall(r'/topic/eursc/science/([a-z0-9_]+)', html)
            if slug != 'es0_fixture'
        }
        assert hrefs == _production_eursc_slugs()
        ibl_hrefs = {
            slug
            for slug in re.findall(r'/ibl/eursc/science/([a-z0-9_]+)', html)
        }
        assert ibl_hrefs == set(IBL_PAGES)
        assert 'topic-card-badge--ibl' in html

        catalog = client.get('/api/v1/topics')
        assert catalog.status_code == 200
        science = next(
            sub
            for level in catalog.get_json()['levels']
            if level['id'] == 'eursc'
            for sub in level['subjects']
            if sub['id'] == 'science'
        )
        catalog_slugs = {topic['slug'] for topic in science['topics'] if topic['slug'] != 'es0_fixture'}
        assert catalog_slugs == _production_eursc_slugs()
        orders = [topic['order'] for topic in science['topics'] if topic['slug'] != 'es0_fixture']
        assert len(orders) == len(set(orders))
        assert all(topic.get('supports_lesson_quiz') for topic in science['topics'] if topic['slug'] != 'es0_fixture')


def test_ibl_suite():
    assert set(IBL_PAGES) == {
        's1_lab',
        's1_food',
        's2_light',
        's2_disease',
        's3_robot',
        's3_field',
    }
    with app.test_client() as client:
        for slug, page in IBL_PAGES.items():
            src = (TEMPLATES / page['template']).read_text(encoding='utf-8')
            assert 'class="mcq-inline"' not in src, slug
            assert 'does not replace classroom practical work' in src, slug
            assert 'Teacher rubric' in src, slug
            ok = client.get(f'/ibl/eursc/science/{slug}')
            assert ok.status_code == 200, slug
            html = ok.data.decode()
            assert 'data-lesson-subject="science"' in html, slug
            assert 'lesson-pages.css' in html, slug
            assert client.get('/ibl/eursc/science/not_a_page').status_code == 404


def test_search_corpus_and_queries():
    docs = build_lesson_search_docs()
    paths = {
        doc['path']
        for doc in docs
        if doc['level'] == 'eursc' and doc['subject'] == 'science' and not doc['path'].endswith('/es0_fixture')
    }
    assert len(paths) == 46
    with app.test_client() as client:
        for query, slug in SEARCH_QUERIES:
            r = client.get(f'/api/v1/search?q={query}')
            assert r.status_code == 200, query
            hits = r.get_json().get('topics') or []
            urls = ' '.join(item.get('url', '') for item in hits)
            assert f'/topic/eursc/science/{slug}' in urls, (query, urls[:200])


def test_revision_planner_eursc():
    utc_today = datetime.now(timezone.utc).date()
    exam_date = (utc_today + timedelta(days=14)).isoformat()
    with app.test_client() as client:
        auth, user_id = register(client, uuid.uuid4().hex[:8])
        with get_db() as conn:
            record_quiz_attempt(
                conn,
                user_id,
                'eursc',
                'science',
                'measurement',
                4,
                10,
                ['A'] * 10,
                [{'question': 'Q', 'correct_answer': 'B'}] * 10,
            )
            upsert_revision_plan_settings(conn, user_id, 'eursc', 'science', exam_date)
            plan = revision_plan_for_user(conn, user_id)
            assert plan is not None
            assert plan['level'] == 'eursc'
            assert plan['subject'] == 'science'
            assert plan['sessions']
            topic_keys = {
                (item['level'], item['subject'], item['topic'])
                for session in plan['sessions']
                for item in session.get('topics') or []
            }
            assert ('eursc', 'science', 'measurement') in topic_keys

        r = client.put(
            '/api/v1/me/revision-plan',
            json={'level': 'eursc', 'subject': 'science', 'exam_date': exam_date},
            headers=auth,
        )
        assert r.status_code == 200, r.data
        body = r.get_json()['revision_plan']
        assert body['level'] == 'eursc'
        assert body['subject'] == 'science'
        session_topic = body['sessions'][0]['topics'][0]
        assert session_topic.get('lesson_quiz_url')


def test_subject_badges_catalog():
    slugs = sorted(TOPICS['eursc']['science'])
    statuses = {
        ('eursc', 'science', slug): {
            'lesson_complete': True,
            'ninja': False,
            'master_ever': False,
        }
        for slug in slugs
    }
    keys = milestone_keys_for_statuses(statuses)
    completed_key = subject_badge_key('completed', 'eursc', 'science')
    assert completed_key in keys
    assert completed_key in catalog_extra_entries()


def test_sensitive_content_regression():
    science = TOPICS['eursc']['science']
    for ref in SENSITIVE_REFS:
        slug = SYLLABUS_MODULES[ref]['slug']
        lesson_src = _lesson_path(slug).read_text(encoding='utf-8')
        assert not DISCLOSE_RE.search(lesson_src), slug
        cfg = science[slug]
        for difficulty in ('foundational', 'intermediate', 'difficult'):
            for fn in cfg['variants_func'](difficulty, 'lesson'):
                problem = fn()
                blob = ' '.join(
                    [
                        str(problem.get('question') or ''),
                        str(problem.get('solution') or ''),
                        str(problem.get('hint') or ''),
                        ' '.join(str(o) for o in (problem.get('options') or [])),
                    ]
                )
                assert not DISCLOSE_RE.search(blob), (slug, difficulty)


def test_qotd_excludes_eursc_and_practice_allows_science():
    assert ('eursc', 'science') in GENERATOR_LAUNCH_PATHS
    assert ('gcse', 'maths') in GENERATOR_LAUNCH_PATHS
    assert ('gcse', 'cs') in GENERATOR_LAUNCH_PATHS
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())


def test_shared_lesson_system():
    components = (ROOT / 'static' / 'css' / 'components.css').read_text(encoding='utf-8')
    assert '[data-lesson-subject="science"] .lesson-hero' in components
    lesson_css = (ROOT / 'static' / 'css' / 'lesson-pages.css').read_text(encoding='utf-8')
    assert 'lesson-figure-caption' in lesson_css
    assert 'lesson-table-wrap' in lesson_css
    assert 'lesson-gloss' in lesson_css
    assert '@media print' in lesson_css
    practice = (ROOT / 'static' / 'css' / 'practice.css').read_text(encoding='utf-8')
    assert '.mcq-feedback.is-correct' in practice
    js = (ROOT / 'static' / 'js' / 'site.js').read_text(encoding='utf-8')
    assert 'function enhanceMcqFeedback' in js
    assert "setAttribute('aria-live', 'polite')" in js
    assert 'function initLessonPresentation' in js
    with app.test_client() as client:
        lesson = client.get('/topic/eursc/science/measurement')
        assert lesson.status_code == 200, lesson.data[:400]
        html = lesson.data.decode()
        assert 'data-lesson-subject="science"' in html
        assert 'lesson-pages.css' in html
        assert 'style="' not in Path(TEMPLATES / 'eursc_science_measurement_lesson.html').read_text(encoding='utf-8')


def main():
    test_manifest_registry_bijection()
    test_templates_depth_and_objectives()
    test_topics_catalog_and_units()
    test_ibl_suite()
    test_search_corpus_and_queries()
    test_revision_planner_eursc()
    test_subject_badges_catalog()
    test_sensitive_content_regression()
    test_qotd_excludes_eursc_and_practice_allows_science()
    test_shared_lesson_system()
    print('ES10 whole-suite QA smoke tests passed.')


if __name__ == '__main__':
    main()
