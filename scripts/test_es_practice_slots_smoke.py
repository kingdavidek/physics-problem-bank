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

from app import (  # noqa: E402
    GENERATOR_DEFAULT_LEVEL,
    GENERATOR_DEFAULT_SUBJECT,
    GENERATOR_DEFAULT_TOPIC,
    GENERATOR_LAUNCH_PATHS,
    _generator_topic_options,
    app,
)
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
        chunk = html.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in chunk
        assert 'data-subject="science"' in chunk
        assert 'data-topic="what_is_science"' in chunk
        assert GENERATOR_DEFAULT_LEVEL == 'eursc'
        assert GENERATOR_DEFAULT_SUBJECT == 'science'
        assert GENERATOR_DEFAULT_TOPIC == 'what_is_science'
        assert 'id="mode-row" hidden' not in html
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


def test_practice_home_filters_mode_and_remembers_selection():
    with app.test_client() as client:
        home = client.get('/')
        html = home.data.decode()
        chunk = html.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in chunk
        assert 'data-topic="what_is_science"' in chunk
        assert 'id="mode-row" hidden' not in html

        gcse = client.get('/?level=gcse&subject=maths&topic=algebra')
        gcse_html = gcse.data.decode()
        gcse_chunk = gcse_html.split('id="page-data"', 1)[1][:500]
        assert 'data-level="gcse"' in gcse_chunk
        assert 'data-topic="algebra"' in gcse_chunk
        assert 'id="mode-row"' in gcse_html
        assert 'id="mode-row" hidden' not in gcse_html

        posted = client.post(
            '/',
            data={
                'level': 'eursc',
                'subject': 'science',
                'topic': 'measurement',
                'mode': 'mcq',
                'difficulty': 'intermediate',
            },
        )
        assert posted.status_code == 200
        body = posted.data.decode()
        post_chunk = body.split('id="page-data"', 1)[1][:500]
        assert 'data-topic="measurement"' in post_chunk
        assert 'badge-mcq' not in body
        assert 'id="mode-row" hidden' not in body

        remembered = client.get('/')
        remembered_html = remembered.data.decode()
        remembered_chunk = remembered_html.split('id="page-data"', 1)[1][:500]
        assert 'data-level="eursc"' in remembered_chunk
        assert 'data-topic="measurement"' in remembered_chunk
        assert 'value="intermediate"' in remembered_html
        assert re.search(
            r'<option value="intermediate"[^>]*selected',
            remembered_html,
        )
        assert 'id="mode-row" hidden' not in remembered_html

        with app.test_client() as api_client:
            gen = api_client.post(
                '/api/v1/problems/generate',
                json={
                    'level': 'eursc',
                    'subject': 'science',
                    'topic': 'measurement',
                    'mode': 'mcq',
                    'difficulty': 'foundational',
                    'action': 'start',
                },
                headers={'Accept': 'application/json'},
            )
            assert gen.status_code == 200, gen.data[:400]
            payload = gen.get_json()
            assert payload['ok'] is True
            assert payload['problem']['mode'] == 'standard'


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
            str(problem.get('hint') or ''),
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
    assert 'Calculate the work done, in joules' in fw_src
    assert '_FW_STANDARD' in fw_src
    assert '_EC_STANDARD' in fw_src


def _option_body(option):
    text = str(option or '')
    if len(text) >= 3 and text[0] in 'ABCD' and text[1:3] == '  ':
        return text[3:].strip()
    return text.strip()


def test_force_work_machines_wording():
    banned = re.compile(
        r'in this lesson|a science line is|work in joules\?|science reply|'
        r'select the correct proof steps|the quiz should store a private map',
        re.I,
    )
    cfg = SCIENCE['force_work_machines']
    vf = cfg['variants_func']
    for difficulty in DIFFS:
        for fn in vf(difficulty, 'lesson'):
            problem = fn()
            blob = _problem_blob(problem)
            assert not banned.search(blob), (fn.__name__, blob[:220])
            if problem.get('options') and problem.get('correct_answer'):
                letter = str(problem['correct_answer'])[:1]
                body = ''
                for option in problem['options']:
                    if str(option)[:1] == letter:
                        body = _option_body(option)
                        break
                sol = str(problem.get('solution') or '')
                assert len(sol) > 20, (fn.__name__, sol)
                if body and body not in ('A', 'B', 'C', 'None of these letters'):
                    stop = {
                        'using', 'which', 'these', 'those', 'about', 'being',
                        'with', 'from', 'that', 'this', 'only', 'none',
                    }
                    tokens = [
                        t.lower()
                        for t in re.findall(r'[A-Za-z]{4,}', body)
                        if t.lower() not in stop
                    ]
                    sol_l = sol.lower()
                    assert tokens and any(t in sol_l for t in tokens[:8]), (
                        fn.__name__,
                        body,
                        sol,
                    )
            if problem.get('answer_type') == 'proof_steps':
                hint = str(problem.get('answer_format_hint') or '')
                assert 'proof' not in hint.lower(), (fn.__name__, hint)
                raw = str(problem.get('correct_answer_raw') or '')
                parts = raw.split('|')
                ids = parts[2:] if parts and parts[0] == 'pick' else parts[1:]
                id_to_text = {
                    str(step.get('id')): str(step.get('text') or '')
                    for step in (problem.get('answer_step_bank') or [])
                }
                sol = str(problem.get('solution') or '')
                for sid in ids:
                    text = id_to_text.get(sid, '')
                    assert text and text in sol, (fn.__name__, sid, text, sol)


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


def test_phase7_verification_samples():
    """Final gate: sensitive + S3 Practice-home samples, IBL/QOTD invariants."""
    samples = (
        SYLLABUS_MODULES['1.4.1']['slug'],
        SYLLABUS_MODULES['2.2.1']['slug'],
        SYLLABUS_MODULES['2.3.7']['slug'],
        SYLLABUS_MODULES['3.1.4']['slug'],
    )
    assert samples == (
        'puberty_maturity',
        'healthy_living',
        'interoception',
        'electric_current',
    )
    assert all(level != 'eursc' for level, *_rest in list_mcq_topic_paths())
    science_slugs = set(SCIENCE)
    picker = {(row['level'], row['subject'], row['slug']) for row in _generator_topic_options()}
    for slug in IBL_PAGES:
        assert slug not in science_slugs, slug
        assert ('eursc', 'science', slug) not in picker
    with app.test_client() as client:
        for slug in samples:
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
            _assert_practice_home_body(posted.data.decode(), slug, 'foundational')
            api = client.post(
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
            assert api.status_code == 200, (slug, api.data[:400])
            payload = api.get_json()
            assert payload['ok'] is True, slug
            problem = payload['problem']
            assert problem.get('question_html'), slug
            blob = ' '.join(
                [
                    str(problem.get('question_html') or ''),
                    str(problem.get('solution_html') or ''),
                ]
            )
            if slug in SENSITIVE_SLUGS:
                assert not DISCLOSE_RE.search(blob), slug
            if slug == 'electric_current':
                assert not VIR_CALC_RE.search(blob), slug
                assert not POWER_CALC_RE.search(blob), slug


def main():
    test_practice_slot_count()
    test_practice_slots_are_explicit_and_stable()
    test_standard_generate_does_not_leak_lesson_items()
    test_empty_standard_pool_does_not_fallback_to_lesson()
    test_lesson_quiz_still_uses_full_bank()
    test_standard_recipe_order()
    test_movement_standard_is_kinematics()
    test_practice_home_and_api_accept_eursc()
    test_practice_home_filters_mode_and_remembers_selection()
    test_sensitive_standard_slots_and_templates_pass_disclose()
    test_ibl_pages_are_not_generator_topics()
    test_s3_standard_slots_have_no_power_or_vir_calculations()
    test_force_work_machines_wording()
    test_standard_matrix_payloads()
    test_standard_generate_never_leaks_lesson_items()
    test_web_and_api_generate_year_sample()
    test_web_and_api_generate_all_years()
    test_phase7_verification_samples()
    print("ES practice-slot smoke tests passed.")


if __name__ == "__main__":
    main()
