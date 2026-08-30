"""ES Practice generator — five-family standard slots + launch gate + safety.

Run: python scripts/test_es_practice_slots_smoke.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PB_TESTING"] = "1"

from app import GENERATOR_LAUNCH_PATHS, _generator_topic_options, app  # noqa: E402
from generators.eursc.science_shared import (  # noqa: E402
    EURSC_PRACTICE_SLOT_COUNT,
    IBL_PAGES,
    SYLLABUS_MODULES,
    bind_eursc_topic,
    eursc_slot_family,
)
from generators.shared.lesson_quiz import build_lesson_quiz  # noqa: E402
from models.qotd import list_mcq_topic_paths  # noqa: E402
from topic_registry import TOPICS  # noqa: E402

DIFFS = ("foundational", "intermediate", "difficult")
SCIENCE = TOPICS["eursc"]["science"]


def _syllabus_topics():
    return {slug: cfg for slug, cfg in SCIENCE.items() if slug != "es0_fixture"}


def test_practice_slot_count():
    for slug, cfg in _syllabus_topics().items():
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            lesson = vf(difficulty, "lesson")
            practice = vf(difficulty, "standard")
            mcq = vf(difficulty, "mcq")
            assert len(lesson) >= EURSC_PRACTICE_SLOT_COUNT, (slug, difficulty, len(lesson))
            assert len(practice) == EURSC_PRACTICE_SLOT_COUNT, (
                slug,
                difficulty,
                len(practice),
            )
            assert len(mcq) >= 1, (slug, difficulty)
            practice_names = [fn.__name__ for fn in practice]
            assert len(set(practice_names)) == len(practice_names), (
                slug,
                difficulty,
                "duplicate practice slots",
            )
            for fn in practice:
                assert fn in lesson, (slug, difficulty, fn.__name__)


def test_practice_slots_are_explicit_and_stable():
    cfg = SCIENCE["energy"]
    vf = cfg["variants_func"]
    first = [fn.__name__ for fn in vf("intermediate", "standard")]
    second = [fn.__name__ for fn in vf("intermediate", "standard")]
    assert first == second
    assert len(first) == EURSC_PRACTICE_SLOT_COUNT
    src = (ROOT / "generators" / "eursc" / "s3_machines.py").read_text(encoding="utf-8")
    assert "_EN_STANDARD" in src
    for name in first:
        assert name in src, name


def test_standard_generate_does_not_leak_lesson_items():
    cfg = SCIENCE["energy"]
    vf = cfg["variants_func"]
    gen = cfg["func"]
    lesson = vf("intermediate", "lesson")
    practice = vf("intermediate", "standard")
    practice_names = {fn.__name__ for fn in practice}
    hidden = [fn for fn in lesson if fn.__name__ not in practice_names]
    assert hidden, "energy intermediate should keep extra lesson items"
    payload = gen("intermediate", "standard")
    # Generated problem comes from one of the five named slots.
    named = gen("intermediate", "standard", variant_name=practice[0].__name__)
    assert named.get("question")
    try:
        gen("intermediate", "standard", variant_name=hidden[0].__name__)
    except ValueError as err:
        assert "Unknown standard variant" in str(err)
    else:
        raise AssertionError("standard generate leaked a lesson-only variant")


def test_empty_standard_pool_does_not_fallback_to_lesson():
    def _mcq():
        return {"question": "lesson-only"}

    _mcq.__name__ = "dummy_mcq"
    _mcq._kind = "mcq"
    generate, variants = bind_eursc_topic(
        "dummy",
        {"foundational": [_mcq]},
        {"foundational": ()},
    )
    assert variants("foundational", "lesson") == [_mcq]
    assert variants("foundational", "standard") == []
    try:
        generate("foundational", "standard")
    except ValueError as err:
        assert "No standard variants" in str(err)
    else:
        raise AssertionError("empty standard pool fell back to lesson")


def test_lesson_quiz_still_uses_full_bank():
    cfg = SCIENCE["measurement"]
    lesson_len = len(cfg["variants_func"]("foundational", "lesson"))
    assert lesson_len > EURSC_PRACTICE_SLOT_COUNT
    quiz = build_lesson_quiz("eursc", "science", "measurement", cfg, seed=17)
    assert len(quiz) == 10


def test_standard_recipe_order():
    """Every named standard tier is MCQ, keyword, data, ordered, pick — in that order."""
    want = ("mcq", "keyword", "data", "order", "pick")
    for slug, cfg in _syllabus_topics().items():
        vf = cfg["variants_func"]
        for difficulty in DIFFS:
            practice = vf(difficulty, "standard")
            fams = tuple(eursc_slot_family(getattr(fn, "_kind", "")) for fn in practice)
            assert fams == want, (slug, difficulty, fams)


def test_movement_standard_is_kinematics():
    """1.3.1 is v=d/t and distance–time graphs, not the canvas joint/muscle row."""
    cfg = SCIENCE["movement"]
    vf = cfg["variants_func"]
    for difficulty in DIFFS:
        for fn in vf(difficulty, "standard"):
            problem = fn()
            blob = " ".join(
                [
                    fn.__name__,
                    str(problem.get("question") or ""),
                    str(problem.get("solution") or ""),
                ]
            ).lower()
            assert "antagonistic" not in blob, (difficulty, fn.__name__)
            assert any(
                token in blob
                for token in ("speed", "distance", "metre", "graph", "time", "second")
            ), (difficulty, fn.__name__, blob[:120])


def test_practice_home_and_api_accept_eursc():
    assert GENERATOR_LAUNCH_PATHS == frozenset(
        {('gcse', 'maths'), ('gcse', 'cs'), ('eursc', 'science')}
    )
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())
    with app.test_client() as client:
        home = client.get('/')
        assert home.status_code == 200
        html = home.data.decode()
        assert 'value="eursc"' in html
        assert 'value="science"' in html
        assert 'Measurement and SI Units' in html
        posted = client.post(
            '/',
            data={
                'level': 'eursc',
                'subject': 'science',
                'topic': 'measurement',
                'mode': 'standard',
                'difficulty': 'foundational',
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        chunk = body.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in chunk
        assert 'data-topic="measurement"' in chunk
        assert 'The SI prefix kilo means' in body

        with app.test_client() as api_client:
            gen = api_client.post(
                '/api/v1/problems/generate',
                json={
                    'level': 'eursc',
                    'subject': 'science',
                    'topic': 'measurement',
                    'mode': 'standard',
                    'difficulty': 'foundational',
                    'action': 'start',
                },
                headers={'Accept': 'application/json'},
            )
            assert gen.status_code == 200, gen.data[:400]
            payload = gen.get_json()
            assert payload['ok'] is True
            problem = payload['problem']
            assert problem.get('level') == 'eursc'
            assert problem.get('subject') == 'science'
            assert problem.get('topic') == 'measurement'
            assert problem.get('question_html')

            blocked = api_client.post(
                '/api/v1/problems/generate',
                json={
                    'level': 'gcse',
                    'subject': 'physics',
                    'topic': 'forces',
                    'mode': 'standard',
                    'difficulty': 'foundational',
                },
                headers={'Accept': 'application/json'},
            )
            assert blocked.status_code == 404


# Keep in sync with scripts/test_es10_whole_suite_smoke.py::DISCLOSE_RE
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
VIR_CALC_RE = re.compile(r'calculate resistance|what is the resistance|R\s*=\s*V\s*/\s*I', re.I)
POWER_CALC_RE = re.compile(r'power in watts\?|P\s*=\s*W\s*/\s*t', re.I)
SENSITIVE_SLUGS = tuple(
    SYLLABUS_MODULES[ref]['slug']
    for ref in SYLLABUS_MODULES
    if ref.startswith('1.4.') or ref.startswith('2.2.') or ref == '2.3.7'
)


def _problem_blob(problem):
    return ' '.join(
        [
            str(problem.get('question') or ''),
            str(problem.get('solution') or ''),
            ' '.join(str(o) for o in (problem.get('options') or [])),
        ]
    )


def test_sensitive_standard_slots_and_templates_pass_disclose():
    templates = ROOT / 'templates'
    for slug in SENSITIVE_SLUGS:
        src = (templates / f'eursc_science_{slug}_lesson.html').read_text(encoding='utf-8')
        assert not DISCLOSE_RE.search(src), slug
        cfg = SCIENCE[slug]
        vf = cfg['variants_func']
        for difficulty in DIFFS:
            for mode in ('lesson', 'standard'):
                for fn in vf(difficulty, mode):
                    blob = _problem_blob(fn())
                    assert not DISCLOSE_RE.search(blob), (slug, difficulty, mode, fn.__name__)


def test_ibl_pages_are_not_generator_topics():
    science_slugs = set(SCIENCE)
    manifest_slugs = {module['slug'] for module in SYLLABUS_MODULES.values()}
    picker = {(row['level'], row['subject'], row['slug']) for row in _generator_topic_options()}
    assert IBL_PAGES
    for slug, page in IBL_PAGES.items():
        assert slug not in science_slugs, slug
        assert slug not in manifest_slugs, slug
        assert ('eursc', 'science', slug) not in picker
        assert page.get('template', '').startswith('eursc_science_ibl_')
    with app.test_client() as client:
        sample = next(iter(IBL_PAGES))
        r = client.get(f'/ibl/eursc/science/{sample}')
        assert r.status_code == 200, sample


def test_s3_standard_slots_have_no_power_or_vir_calculations():
    for slug in ('force_work_machines', 'energy', 'electric_current'):
        cfg = SCIENCE[slug]
        vf = cfg['variants_func']
        for difficulty in DIFFS:
            for fn in vf(difficulty, 'standard'):
                blob = _problem_blob(fn())
                assert not VIR_CALC_RE.search(blob), (slug, difficulty, fn.__name__, blob[:120])
                assert not POWER_CALC_RE.search(blob), (slug, difficulty, fn.__name__, blob[:120])
    fw_src = (ROOT / 'generators' / 'eursc' / 's3_machines.py').read_text(encoding='utf-8')
    assert 'are not claimed in this lesson' in fw_src
    assert '_EC_STANDARD' in fw_src


def _assert_grader_ready(problem, family, *, slug, difficulty, name):
    assert problem.get('question'), (slug, difficulty, name)
    if family == 'mcq':
        assert problem.get('options'), (slug, difficulty, name)
        assert problem.get('correct_answer'), (slug, difficulty, name)
        return
    assert problem.get('correct_answer_raw') not in (None, ''), (slug, difficulty, name)
    answer_type = problem.get('answer_type')
    assert answer_type, (slug, difficulty, name)
    if family in ('order', 'pick'):
        assert answer_type == 'proof_steps', (slug, difficulty, name, answer_type)
    elif family == 'keyword':
        assert answer_type in ('keyword', 'text'), (slug, difficulty, name, answer_type)
    else:
        assert answer_type in (
            'number',
            'number_estimate',
            'number_fields',
            'number_pair',
            'number_list',
        ), (slug, difficulty, name, answer_type)


def test_standard_matrix_payloads():
    """46 × 3 × 5 named slots; every payload is grader-ready."""
    topics = _syllabus_topics()
    assert len(topics) == 46
    assert set(topics) == {module['slug'] for module in SYLLABUS_MODULES.values()}
    total = 0
    want = ('mcq', 'keyword', 'data', 'order', 'pick')
    for slug, cfg in topics.items():
        vf = cfg['variants_func']
        gen = cfg['func']
        for difficulty in DIFFS:
            practice = vf(difficulty, 'standard')
            assert len(practice) == EURSC_PRACTICE_SLOT_COUNT, (slug, difficulty)
            names = [fn.__name__ for fn in practice]
            assert len(set(names)) == len(names), (slug, difficulty, names)
            fams = tuple(eursc_slot_family(getattr(fn, '_kind', '')) for fn in practice)
            assert fams == want, (slug, difficulty, fams)
            for fn, family in zip(practice, fams):
                problem = fn()
                _assert_grader_ready(
                    problem, family, slug=slug, difficulty=difficulty, name=fn.__name__
                )
                via_generate = gen(difficulty, 'standard', variant_name=fn.__name__)
                _assert_grader_ready(
                    via_generate,
                    family,
                    slug=slug,
                    difficulty=difficulty,
                    name=fn.__name__,
                )
                total += 1
    assert total == 46 * 3 * EURSC_PRACTICE_SLOT_COUNT


def test_standard_generate_never_leaks_lesson_items():
    for slug, cfg in _syllabus_topics().items():
        vf = cfg['variants_func']
        gen = cfg['func']
        for difficulty in DIFFS:
            lesson = vf(difficulty, 'lesson')
            practice = vf(difficulty, 'standard')
            practice_names = {fn.__name__ for fn in practice}
            hidden = [fn for fn in lesson if fn.__name__ not in practice_names]
            if not hidden:
                continue
            try:
                gen(difficulty, 'standard', variant_name=hidden[0].__name__)
            except ValueError as err:
                assert 'Unknown standard variant' in str(err), (slug, difficulty, err)
            else:
                raise AssertionError(
                    f'{slug} {difficulty} standard generate leaked {hidden[0].__name__}'
                )


def test_web_and_api_generate_year_sample():
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())
    samples = (
        ('measurement', 's1'),
        (SYLLABUS_MODULES['1.4.1']['slug'], 's1-puberty'),
        (SYLLABUS_MODULES['2.2.1']['slug'], 's2-health'),
        (SYLLABUS_MODULES['3.1.4']['slug'], 's3-current'),
    )
    assert samples[1][0] == 'puberty_maturity'
    assert samples[3][0] == 'electric_current'
    for slug, _label in samples:
        with app.test_client() as client:
            home = client.get('/')
            assert home.status_code == 200
            posted = client.post(
                '/',
                data={
                    'level': 'eursc',
                    'subject': 'science',
                    'topic': slug,
                    'mode': 'standard',
                    'difficulty': 'foundational',
                },
            )
            assert posted.status_code == 200, slug
            body = posted.data.decode()
            chunk = body.split('id="page-data"', 1)[1][:500]
            assert 'data-level="eursc"' in chunk, slug
            assert f'data-topic="{slug}"' in chunk, slug
            assert 'question-content' in body, slug
        with app.test_client() as api_client:
            gen = api_client.post(
                '/api/v1/problems/generate',
                json={
                    'level': 'eursc',
                    'subject': 'science',
                    'topic': slug,
                    'mode': 'standard',
                    'difficulty': 'foundational',
                    'action': 'start',
                },
                headers={'Accept': 'application/json'},
            )
            assert gen.status_code == 200, (slug, gen.data[:400])
            payload = gen.get_json()
            assert payload['ok'] is True, slug
            problem = payload['problem']
            assert problem.get('level') == 'eursc'
            assert problem.get('topic') == slug
            assert problem.get('question_html')
            if problem.get('options'):
                assert problem.get('correct_answer')
            else:
                assert problem.get('correct_answer_raw') not in (None, '')
                assert problem.get('answer_type')


def _topics_for_year(year):
    return [module['slug'] for module in SYLLABUS_MODULES.values() if module['year'] == year]


def _assert_practice_home_body(body, slug, difficulty):
    assert 'Daily limit reached' not in body, (slug, difficulty)
    assert 'Your session expired' not in body, (slug, difficulty)
    assert 'Difficult questions require a free account' not in body, (slug, difficulty)
    chunk = body.split('id="page-data"', 1)[1][:600]
    assert 'data-level="eursc"' in chunk, (slug, difficulty)
    assert f'data-topic="{slug}"' in chunk, (slug, difficulty)
    assert 'question-content' in body or 'mcq-options' in body, (slug, difficulty)
    if slug in SENSITIVE_SLUGS:
        assert not DISCLOSE_RE.search(body), (slug, difficulty)
    if slug in ('force_work_machines', 'energy', 'electric_current'):
        assert not VIR_CALC_RE.search(body), (slug, difficulty)
        assert not POWER_CALC_RE.search(body), (slug, difficulty)


def _register_practice_user(client, suffix):
    handle = f'es6{suffix}'[:20]
    registered = client.post(
        '/register',
        data={
            'email': f'{handle}@example.com',
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert registered.status_code == 200, registered.data[:400]


def test_web_and_api_generate_all_years():
    """Practice home + API generate every syllabus topic at every difficulty.

    Difficult is account-gated, so this wave uses a registered session. Guest
    foundational generate is covered by test_web_and_api_generate_year_sample.
    """
    years = {year: _topics_for_year(year) for year in ('s1', 's2', 's3')}
    assert len(years['s1']) == 18
    assert len(years['s2']) == 17
    assert len(years['s3']) == 11
    assert 'puberty_maturity' in years['s1']
    assert 'healthy_living' in years['s2']
    assert 'interoception' in years['s2']
    assert 'electric_current' in years['s3']
    with app.test_client() as home_client:
        home = home_client.get('/')
        assert home.status_code == 200
        picker = home.data.decode()
        assert 'value="eursc"' in picker
        assert 'value="science"' in picker
        for slug in _syllabus_topics():
            assert f'value="{slug}"' in picker, slug
        blocked = home_client.post(
            '/',
            data={
                'level': 'eursc',
                'subject': 'science',
                'topic': 'measurement',
                'mode': 'standard',
                'difficulty': 'difficult',
            },
        )
        assert blocked.status_code == 200
        assert 'Difficult questions require a free account' in blocked.data.decode()
    for year, slugs in years.items():
        with app.test_client() as client:
            _register_practice_user(client, f'{year}_{os.getpid()}')
            for slug in slugs:
                for difficulty in DIFFS:
                    posted = client.post(
                        '/',
                        data={
                            'level': 'eursc',
                            'subject': 'science',
                            'topic': slug,
                            'mode': 'standard',
                            'difficulty': difficulty,
                        },
                    )
                    assert posted.status_code == 200, (year, slug, difficulty)
                    _assert_practice_home_body(posted.data.decode(), slug, difficulty)
                    api = client.post(
                        '/api/v1/problems/generate',
                        json={
                            'level': 'eursc',
                            'subject': 'science',
                            'topic': slug,
                            'mode': 'standard',
                            'difficulty': difficulty,
                            'action': 'start',
                        },
                        headers={'Accept': 'application/json'},
                    )
                    assert api.status_code == 200, (year, slug, difficulty, api.data[:400])
                    payload = api.get_json()
                    assert payload['ok'] is True, (year, slug, difficulty)
                    problem = payload['problem']
                    assert problem.get('question_html'), (year, slug, difficulty)
                    if problem.get('options'):
                        assert problem.get('correct_answer'), (year, slug, difficulty)
                    else:
                        assert problem.get('correct_answer_raw') not in (None, '')
                        assert problem.get('answer_type')


def main():
    test_practice_slot_count()
    test_practice_slots_are_explicit_and_stable()
    test_standard_generate_does_not_leak_lesson_items()
    test_empty_standard_pool_does_not_fallback_to_lesson()
    test_lesson_quiz_still_uses_full_bank()
    test_standard_recipe_order()
    test_movement_standard_is_kinematics()
    test_practice_home_and_api_accept_eursc()
    test_sensitive_standard_slots_and_templates_pass_disclose()
    test_ibl_pages_are_not_generator_topics()
    test_s3_standard_slots_have_no_power_or_vir_calculations()
    test_standard_matrix_payloads()
    test_standard_generate_never_leaks_lesson_items()
    test_web_and_api_generate_year_sample()
    test_web_and_api_generate_all_years()
    print("ES practice-slot smoke tests passed.")


if __name__ == "__main__":
    main()
