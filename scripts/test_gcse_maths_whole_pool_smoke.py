"""GCSE maths Quick Test and set work draw from the whole tier pool (decision V8). Run:
python scripts/test_gcse_maths_whole_pool_smoke.py

docs/GCSE_MATHS_VARIETY.md, Phase 3 batch C2. A 10-question Quick Test and a piece of set work (up to 20 questions)
used to cycle the 7-slot practice queue, so they repeated a kind by construction. They now draw from every slot of
the chosen topic and difficulty (generators/shared/whole_pool.py) and no slot comes round again until the pool is
exhausted. Checked here, through the builders the routes call:

  * practice mode, every tier: no repeated slot (each slot is one strict kind after Phase 3) in the first
    min(pool, 10) questions of a Quick Test and the first min(pool, 20) of a 20-question set work; the repeat rates
    for 10 and 20 are printed; every name drawn is in the tier pool;
  * multiple choice: a Quick Test walks the band's slots without a repeat and refuses a repeated kind or source
    generator while it can (the lesson-quiz rule);
  * determinism: one seed gives one plan and one set of questions, twice;
  * a Quick Test session stored before the change (problems built by cycling the queue) still runs through the
    question, answer and results routes, and so does one started now; nothing new is stored about a pupil (the
    session row has the same keys as before, and a stored problem carries no key that the generator did not give);
  * set work: 20 frozen questions, graded from the stored copy, and nothing a pupil is sent before grading holds a
    key, a solution or a form;
  * mixed difficulty draws across the three tiers; other subjects keep the queue (their builders are untouched).
"""
import json
import os
import random
import re
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ.setdefault('SECRET_KEY', 'pb-testing')

from app import TOPICS, _freeze_class_work_problems, app, get_db  # noqa: E402
from generators.shared import whole_pool  # noqa: E402
from generators.shared.answer_record import public_problem  # noqa: E402
from generators.shared.question_kind import quiz_kind  # noqa: E402
from generators.shared.variant_utils import tier_pool  # noqa: E402
from generators.shared.whole_pool import PoolDraw, generate_from_pool  # noqa: E402
from models.class_assignments import MAX_ASSIGNMENT_QUESTIONS  # noqa: E402
from models.quicktest import QUICKTEST_LENGTH, build_quicktest_problems, load_quicktest_session, save_quicktest_session  # noqa: E402

TIERS = ('foundational', 'intermediate', 'difficult')
SESSION_KEYS = {'problems', 'answers', 'index', 'topic_name', 'level', 'subject', 'topic', 'difficulty', 'mode',
                'owner_user_id', 'updated_at'}
SVG_COUNTER = re.compile(r'(sk-[a-z]+)-\d+')
LEAK_KEYS = ('correct_answer', 'correct_answer_raw', 'solution_html', 'solution', 'hint', 'hint_html', 'answer_form',
             'answer_record', 'option_notes', 'answer_step_prereqs')
FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def recording(cfg, names):
    """A copy of a topic config whose generator notes the variant name of every call."""
    func = cfg['func']

    def wrapped(difficulty, mode, variant_name=None):
        names.append(variant_name)
        return func(difficulty, mode, variant_name=variant_name)

    return {**cfg, 'func': wrapped}


def old_cycle_problems(cfg, tier, mode, count=QUICKTEST_LENGTH):
    """The problems a Quick Test stored before batch C2: the 7-slot queue, then the first slots again."""
    queue = list(cfg['variants_func'](tier, mode) or [])
    return [cfg['func'](tier, mode, variant_name=queue[i % len(queue)].__name__) for i in range(count)]


def _named(n):
    def fn():
        return n
    fn.__name__ = n
    return fn


def _keys(obj, out=None):
    out = set() if out is None else out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.add(k)
            _keys(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _keys(v, out)
    return out


def check_pool_draw():
    pool = [_named(n) for n in 'abcde']
    d = PoolDraw(pool, random.Random(3))
    got = [d.next().__name__ for _ in range(12)]
    if sorted(got[:5]) != list('abcde') or sorted(got[5:10]) != list('abcde'):
        fail(f'PoolDraw does not use every slot once before repeating: {got}')
    if [d.next() for _ in range(3)] and PoolDraw([], random.Random(1)).next() is not None:
        fail('PoolDraw of an empty pool must yield None')
    one = PoolDraw(pool[:1], random.Random(1))
    if [one.next().__name__ for _ in range(3)] != ['a', 'a', 'a']:
        fail('a pool of one slot must yield it every time')


def check_flag_stays_put():
    """The whole-pool flag is set only inside tier_pool: a plain variants call after it gives the 7-slot sample again, the
    practice queue builder is untouched, and a variants function that raises leaves the flag reset (C2 review)."""
    from generators.shared import variant_utils as vu
    cfg = TOPICS['gcse']['maths']['statistics']
    for tier in TIERS:
        full = len(tier_pool(cfg['variants_func'], tier, 'standard'))
        if vu._WHOLE_POOL.get():
            fail(f'{tier}: the whole-pool flag is still set after tier_pool')
        plain = len(cfg['variants_func'](tier, 'standard') or [])
        if plain != min(vu.TIER_VARIANT_COUNT, full):
            fail(f'{tier}: a plain variants call after tier_pool gave {plain} slots, not the {vu.TIER_VARIANT_COUNT}-slot sample (pool {full})')

    class Boom(Exception):
        pass

    def raising(_difficulty, _mode):
        raise Boom()
    try:
        tier_pool(raising, 'foundational', 'standard')
    except Boom:
        pass
    if vu._WHOLE_POOL.get():
        fail('the whole-pool flag stays set when the variants function raises')
    with app.test_request_context('/'):
        from app import _build_problem_queue
        queue = _build_problem_queue(cfg, 'gcse', 'maths', 'statistics', 'standard', 'intermediate') or []
    if len(queue) != vu.TIER_VARIANT_COUNT:
        fail(f'the practice queue holds {len(queue)} slots, not {vu.TIER_VARIANT_COUNT}')


def check_practice_tiers():
    """No repeated slot while the pool lasts, for Quick Test (10) and set work (20), in every GCSE maths tier."""
    maths = TOPICS['gcse']['maths']
    rep10 = rep20 = tiers = 0
    pool_sizes = []
    t0 = time.time()
    for slug in sorted(maths):
        cfg = maths[slug]
        for tier in TIERS:
            pool = [fn.__name__ for fn in tier_pool(cfg['variants_func'], tier, 'standard')]
            n = len(pool)
            pool_sizes.append(n)
            if n != len(set(pool)):
                fail(f'{slug}/{tier}: the tier pool lists a slot twice')
            tiers += 1
            # Quick Test through the real builder, variant names recorded from the generator calls
            names = []
            random.seed(tiers)
            problems, _cfg = build_quicktest_problems('gcse', 'maths', slug, 'standard', tier,
                                                      {'gcse': {'maths': {slug: recording(cfg, names)}}},
                                                      rng=random.Random(tiers))
            if len(problems) != QUICKTEST_LENGTH or len(names) != QUICKTEST_LENGTH:
                fail(f'{slug}/{tier}: Quick Test built {len(problems)} problems from {len(names)} calls')
                continue
            if any(name not in pool for name in names):
                fail(f'{slug}/{tier}: a Quick Test drew a name outside the tier pool: {sorted(set(names) - set(pool))}')
            first = names[:min(n, QUICKTEST_LENGTH)]
            if len(set(first)) != len(first):
                fail(f'{slug}/{tier}: a Quick Test repeated a slot within the first {len(first)} questions: {names}')
            rep10 += len(set(names)) < len(names)
            # set work of 20 through the real builder
            names = []
            original = cfg['func']
            cfg['func'] = recording(cfg, names)['func']
            try:
                with app.test_request_context('/'):
                    random.seed(tiers + 1000)
                    frozen, _mode = _freeze_class_work_problems('gcse', 'maths', slug, 'standard', tier,
                                                                MAX_ASSIGNMENT_QUESTIONS, rng=random.Random(tiers + 1000))
            finally:
                cfg['func'] = original
            if len(frozen) != MAX_ASSIGNMENT_QUESTIONS:
                fail(f'{slug}/{tier}: set work froze {len(frozen)} problems')
                continue
            used = [nm for nm in names if nm is not None]
            if any(name not in pool for name in used):
                fail(f'{slug}/{tier}: set work drew a name outside the tier pool')
            first = used[:min(n, MAX_ASSIGNMENT_QUESTIONS)]
            if len(set(first)) != len(first):
                fail(f'{slug}/{tier}: set work repeated a slot within the first {len(first)} questions: {used}')
            if len(used) >= 2 * n and sorted(used[:n]) != sorted(used[n:2 * n]):
                fail(f'{slug}/{tier}: the second pass of set work does not cover the pool again')
            rep20 += len(set(used[:MAX_ASSIGNMENT_QUESTIONS])) < min(len(used), MAX_ASSIGNMENT_QUESTIONS)
            for p in frozen:
                if 'answer_record' in p:
                    fail(f'{slug}/{tier}: a frozen set-work problem holds answer_record')
    small10 = sum(1 for n in pool_sizes if n < QUICKTEST_LENGTH)
    small20 = sum(1 for n in pool_sizes if n < MAX_ASSIGNMENT_QUESTIONS)
    print(f'  practice: {tiers} tiers, pools {min(pool_sizes)} to {max(pool_sizes)} slots; a 10-question Quick Test '
          f'repeats a kind in {rep10} tiers ({100 * rep10 / tiers:.1f}%, the {small10} tiers under 10 kinds, once each); '
          f'20-question set work repeats in {rep20} tiers ({100 * rep20 / tiers:.1f}%, the {small20} under 20 kinds); '
          f'no repeat within the pool size anywhere; {time.time() - t0:.1f}s')
    if rep10 != small10 or rep20 != small20:
        fail(f'repeat counts do not match the pool sizes (10: {rep10} vs {small10}; 20: {rep20} vs {small20})')


def check_mcq_quick_tests():
    """A multiple-choice Quick Test walks the seven slots without a repeat and avoids a repeated kind while it can."""
    maths = TOPICS['gcse']['maths']
    t0 = time.time()
    distinct = tests = dup_texts = 0
    for slug in sorted(maths):
        cfg = maths[slug]
        for tier in TIERS:
            names = []
            random.seed(hash((slug, tier)) & 0xFFFF)
            problems, _cfg = build_quicktest_problems('gcse', 'maths', slug, 'mcq', tier,
                                                      {'gcse': {'maths': {slug: recording(cfg, names)}}},
                                                      rng=random.Random(7))
            if len(problems) != QUICKTEST_LENGTH:
                fail(f'{slug}/{tier} mcq: {len(problems)} problems')
                continue
            if any(not p.get('options') or not p.get('correct_answer') for p in problems):
                fail(f'{slug}/{tier} mcq: a Quick Test question is not multiple choice')
            # the draw walks the band's slots: the first seven generator calls name seven different slots (a refused
            # kind costs a call and moves on to the next slot, so the walk holds whatever is refused)
            slots = {fn.__name__ for fn in tier_pool(cfg['variants_func'], tier, 'mcq')}
            if len(set(names[:len(slots)])) != len(slots) or any(n not in slots for n in names):
                fail(f'{slug}/{tier} mcq: the slot walk repeated a slot early or left the band: {names}')
            kinds = [quiz_kind(p) for p in problems]
            distinct += len(set(kinds))
            tests += 1
            texts = [p.get('question') for p in problems]
            dup_texts += len(texts) - len(set(texts))
    print(f'  multiple choice: {tests} Quick Tests, mean {distinct / tests:.2f} distinct kinds in 10 (a band holds 5 to '
          f'12 kinds until Phase 4); {dup_texts} identical question texts over all tests (bands of fewer than ten fixed '
          f'items must repeat one), {time.time() - t0:.1f}s')
    # the kind check does more than the slot walk: with it off the same draws give fewer distinct kinds
    off = on = 0
    for slug in ('statistics', 'number', 'probability', 'algebra', 'graphs', 'fdp'):
        cfg = maths[slug]
        for seed in range(4):
            for check in (False, True):
                random.seed(seed)
                drawn = generate_from_pool(cfg['func'], cfg['variants_func'], 'intermediate', 'mcq', QUICKTEST_LENGTH,
                                           rng=random.Random(seed), kind_check=check)
                k = len({quiz_kind(p) for p, _ in drawn})
                if check:
                    on += k
                else:
                    off += k
    if on <= off:
        fail(f'the multiple-choice kind check does not raise the number of distinct kinds ({on} with, {off} without)')


def check_determinism():
    for slug, mode in (('bidmas', 'standard'), ('statistics', 'standard'), ('probability', 'mcq'), ('graphs', 'mcq')):
        runs = []
        for _ in range(2):
            random.seed(42)
            problems, _cfg = build_quicktest_problems('gcse', 'maths', slug, mode, 'intermediate', TOPICS,
                                                      rng=random.Random(42))
            runs.append([(SVG_COUNTER.sub(r'\1-N', str(p.get('question'))), p.get('correct_answer'), p.get('correct_answer_raw'))
                         for p in problems])
        if runs[0] != runs[1]:
            fail(f'{slug} {mode}: the same seed gave two different Quick Tests')
        plans = []
        for _ in range(2):
            pool = tier_pool(TOPICS['gcse']['maths'][slug]['variants_func'], 'intermediate', mode)
            d = PoolDraw(pool, random.Random(5))
            plans.append([d.next().__name__ for _ in range(25)])
        if plans[0] != plans[1]:
            fail(f'{slug} {mode}: the same seed gave two different draw plans')
    with app.test_request_context('/'):
        runs = []
        for _ in range(2):
            random.seed(9)
            frozen, _mode = _freeze_class_work_problems('gcse', 'maths', 'algebra', 'standard', 'difficult', 12,
                                                        rng=random.Random(9))
            runs.append([SVG_COUNTER.sub(r'\1-N', str(p.get('question_html'))) for p in frozen])
        if runs[0] != runs[1]:
            fail('the same seed gave two different pieces of set work')


def run_quicktest(client, expect_total):
    """Walk a stored Quick Test session through the web routes; returns the results page text."""
    r = client.get('/quicktest')
    if r.status_code != 200:
        fail(f'quick test question page: {r.status_code}')
        return ''
    for _ in range(expect_total):
        r = client.post('/quicktest/next', data={'qt_user_answer': '1', 'qt_checked': '1', 'qt_correct': '0'},
                        follow_redirects=False)
        if r.status_code not in (302, 303):
            fail(f'quick test next: {r.status_code}')
            return ''
    r = client.get('/quicktest/results')
    if r.status_code != 200:
        fail(f'quick test results page: {r.status_code}')
        return ''
    return r.get_data(as_text=True)


def check_sessions():
    cfg = TOPICS['gcse']['maths']['bidmas']
    with app.test_client() as client:
        # a session stored before the change: ten problems built by cycling the queue, the old row shape
        random.seed(1)
        old = old_cycle_problems(cfg, 'intermediate', 'standard')
        qt_id = f'qt_a_{uuid.uuid4().hex}'
        data = {'problems': old, 'answers': [], 'index': 0, 'topic_name': 'BIDMAS', 'level': 'gcse', 'subject': 'maths',
                'topic': 'bidmas', 'difficulty': 'intermediate', 'mode': 'standard', 'owner_user_id': None}
        with get_db() as conn:
            save_quicktest_session(conn, qt_id, data)
        with client.session_transaction() as sess:
            sess['qt_id'] = qt_id
        page = run_quicktest(client, QUICKTEST_LENGTH)
        if 'quicktest' not in page.lower():
            fail('an old stored session did not reach the results page')
        with get_db() as conn:
            stored = load_quicktest_session(conn, qt_id)
        if len(stored.get('answers') or []) != QUICKTEST_LENGTH:
            fail(f'an old stored session recorded {len(stored.get("answers") or [])} answers')
        # a session started now, through the web form: the stored row has the same keys as before and nothing new
        with client.session_transaction() as sess:
            sess.pop('qt_id', None)
        _hdr, uid = register(client, f'wp_{uuid.uuid4().hex[:8]}@example.com', f'wp{uuid.uuid4().hex[:8]}')
        with client.session_transaction() as sess:          # difficult needs an account (review A4)
            sess['_user_id'] = str(uid)
            sess['_fresh'] = True
        r = client.post('/quicktest/start', data={'level': 'gcse', 'subject': 'maths', 'topic': 'statistics',
                                                  'mode': 'standard', 'difficulty': 'difficult'}, follow_redirects=False)
        if r.status_code not in (302, 303):
            fail(f'quick test start: {r.status_code}')
            return
        with client.session_transaction() as sess:
            qt_id = sess.get('qt_id')
        with get_db() as conn:
            stored = load_quicktest_session(conn, qt_id)
        if set(stored) != SESSION_KEYS:
            fail(f'the stored Quick Test session has new or missing keys: {sorted(set(stored) ^ SESSION_KEYS)}')
        allowed = set()
        random.seed(3)
        for name in {fn.__name__ for fn in tier_pool(TOPICS['gcse']['maths']['statistics']['variants_func'], 'difficult', 'standard')}:
            allowed |= set(public_problem(TOPICS['gcse']['maths']['statistics']['func']('difficult', 'standard', variant_name=name), keep_notes=True))
        extra = {k for p in stored['problems'] for k in p} - allowed
        if extra:
            fail(f'a stored Quick Test problem carries keys the generator does not give: {sorted(extra)}')
        if any('answer_record' in p for p in stored['problems']):
            fail('a stored Quick Test problem holds answer_record')
        page = run_quicktest(client, QUICKTEST_LENGTH)
        if not page:
            fail('a new session did not reach the results page')
        # the API path too
        r = client.post('/api/v1/quicktest/start', json={'level': 'gcse', 'subject': 'maths', 'topic': 'fdp',
                                                          'mode': 'mcq', 'difficulty': 'foundational'})
        if r.status_code != 201:
            fail(f'api quick test start: {r.status_code} {r.data[:200]!r}')
            return
        body = r.get_json()
        sid = body.get('session_id')
        if body.get('total') != QUICKTEST_LENGTH or not (body.get('problem') or {}).get('options'):
            fail(f'api quick test start payload: {sorted(body)}')
        dump = json.dumps(body)
        if 'variant_name' in dump and '"variant_name": null' not in dump:
            fail('the Quick Test API payload names a variant')
        for i in range(QUICKTEST_LENGTH):
            r = client.post(f'/api/v1/quicktest/{sid}/answer', json={'user_answer': 'A'})
            if r.status_code != 200:
                fail(f'api quick test answer {i}: {r.status_code}')
                break
        r = client.get(f'/api/v1/quicktest/{sid}/results')
        if r.status_code != 200:
            fail(f'api quick test results: {r.status_code}')


def register(client, email, handle):
    r = client.post('/api/v1/auth/register', json={'email': email, 'handle': handle, 'password': 'password123',
                                                    'age_confirm': True}, headers={'Accept': 'application/json'})
    if r.status_code != 201:
        fail(f'register: {r.status_code} {r.data[:200]!r}')
        return None, None
    body = r.get_json()
    return {'Authorization': f'Bearer {body["token"]}', 'Accept': 'application/json'}, body['user']['id']


def check_set_work():
    """A 20-question piece of set work: frozen whole, graded from the stored copy, no key before grading."""
    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        teacher, _tid = register(client, f'c2t_{suffix}@example.com', f'c2t_{suffix}')
        pupil, pid = register(client, f'c2p_{suffix}@example.com', f'c2p_{suffix}')
        if not teacher or not pupil:
            return
        r = client.post('/api/v1/me/teacher/enable', headers=teacher)
        r = client.post('/api/v1/teacher/classes', json={'name': 'C2 class'}, headers=teacher)
        if r.status_code != 201:
            fail(f'create class: {r.status_code}')
            return
        klass = r.get_json()['class']
        r = client.post('/api/v1/me/classes/join', json={'code': klass['join_code'], 'disclosed': True}, headers=pupil)
        if r.status_code != 201:
            fail(f'join class: {r.status_code}')
            return
        for slug, mode in (('probability', 'standard'), ('number', 'mcq')):
            scope = {'level': 'gcse', 'subject': 'maths', 'topic': slug, 'difficulty': 'intermediate', 'mode': mode,
                     'count': MAX_ASSIGNMENT_QUESTIONS}
            r = client.post(f'/api/v1/teacher/classes/{klass["id"]}/assignments', json={**scope, 'preview': True},
                            headers=teacher)
            if r.status_code != 200:
                fail(f'{slug} preview: {r.status_code} {r.data[:200]!r}')
                continue
            preview = r.get_json()['preview']
            if preview['question_count'] != MAX_ASSIGNMENT_QUESTIONS or len(preview['problems']) != MAX_ASSIGNMENT_QUESTIONS:
                fail(f'{slug} preview has {len(preview["problems"])} problems')
            leaked = _keys(preview) & set(LEAK_KEYS)
            if leaked:
                fail(f'{slug} preview leaks {sorted(leaked)}')
            r = client.post(f'/api/v1/teacher/classes/{klass["id"]}/assignments',
                            json={'preview_id': preview['preview_id'], 'student_ids': [pid]}, headers=teacher)
            if r.status_code != 201:
                fail(f'{slug} assign: {r.status_code} {r.data[:200]!r}')
                continue
            aid = r.get_json()['assignment']['id']
            r = client.get(f'/api/v1/me/class-work/{aid}', headers=pupil)
            if r.status_code != 200:
                fail(f'{slug} pupil view: {r.status_code}')
                continue
            work = r.get_json()['class_work']
            leaked = _keys(work) & set(LEAK_KEYS)
            if leaked:
                fail(f'{slug}: the pupil is sent {sorted(leaked)} before grading')
            if work['question_count'] != MAX_ASSIGNMENT_QUESTIONS:
                fail(f'{slug}: the pupil sees {work["question_count"]} questions')
            # the stored copy is graded whole: answer the first question wrongly and see the stored key used
            with get_db() as conn:
                row = conn.execute('SELECT problems_json FROM class_assignments WHERE id = ?', (aid,)).fetchone()
            problems = json.loads(row['problems_json'])
            texts = [p.get('question_html') or p.get('question') for p in problems]
            if mode == 'standard' and len(set(texts)) < MAX_ASSIGNMENT_QUESTIONS - 1:
                # 18 slots in the pool, so the second pass may bring one kind back (with new numbers)
                fail(f'{slug}: set work repeats the same question text ({len(set(texts))} distinct of {len(texts)})')
            first = problems[0]
            wrong = 'A' if first.get('options') and str(first.get('correct_answer')).strip().upper() != 'A' else ('B' if first.get('options') else '999999')
            r = client.post(f'/api/v1/me/class-work/{aid}/answer', json={'index': 0, 'user_answer': wrong}, headers=pupil)
            if r.status_code != 200:
                fail(f'{slug} answer: {r.status_code} {r.data[:200]!r}')
                continue
            graded = r.get_json()['class_work']
            first_out = (graded.get('problems') or [{}])[0]
            if graded.get('answered_count') != 1 or graded.get('score') != 0 or first_out.get('correct') is not False:
                fail(f'{slug}: a wrong answer was not graded wrong from the stored copy: {sorted(graded)}')
            leaked = _keys(graded) & {'answer_form', 'answer_record', 'answer_step_prereqs'}
            if leaked:
                fail(f'{slug}: the graded view leaks {sorted(leaked)}')
            leaked = _keys(graded['problems'][1:]) & set(LEAK_KEYS)
            if leaked:
                fail(f'{slug}: an unanswered question is sent with {sorted(leaked)}')


def check_mixed_and_other_subjects():
    # mixed difficulty: the union of the three tiers, each slot once
    cfg = TOPICS['gcse']['maths']['number']
    pool = tier_pool(cfg['variants_func'], 'mixed', 'standard')
    tiers = [set(fn.__name__ for fn in tier_pool(cfg['variants_func'], t, 'standard')) for t in TIERS]
    if {fn.__name__ for fn in pool} != set().union(*tiers) or len(pool) != len({fn.__name__ for fn in pool}):
        fail('the mixed pool is not the union of the three tiers')
    names = []
    random.seed(11)
    problems, _cfg = build_quicktest_problems('gcse', 'maths', 'number', 'standard', 'mixed',
                                              {'gcse': {'maths': {'number': recording(cfg, names)}}}, rng=random.Random(11))
    if len(problems) != QUICKTEST_LENGTH or len(set(names)) != QUICKTEST_LENGTH:
        fail(f'a mixed Quick Test repeated a slot: {names}')
    if not all(any(n in t for t in tiers) for n in names):
        fail('a mixed Quick Test drew outside the three tiers')
    # each slot is called with its own tier, so a topic whose practice pools exist only for the three tiers (bidmas,
    # algebra, decimals, fdp, multiples_factors, surds: the C2 review found every draw raising) builds a mixed test
    # too, and every question carries the tier it came from
    for slug in ('bidmas', 'surds'):
        cfg = TOPICS['gcse']['maths'][slug]
        names = []
        random.seed(12)
        try:
            problems, _cfg = build_quicktest_problems('gcse', 'maths', slug, 'standard', 'mixed',
                                                      {'gcse': {'maths': {slug: recording(cfg, names)}}},
                                                      rng=random.Random(12))
        except ValueError as exc:
            fail(f'a mixed Quick Test on {slug} failed: {exc}')
            continue
        by_tier = {t: {fn.__name__ for fn in tier_pool(cfg['variants_func'], t, 'standard')} for t in TIERS}
        if len(problems) != QUICKTEST_LENGTH or len(set(names)) != QUICKTEST_LENGTH:
            fail(f'a mixed Quick Test on {slug} repeated a slot: {names}')
        if {p.get('difficulty') for p in problems} - set(TIERS):
            fail(f'a mixed Quick Test on {slug} labelled a question with a difficulty outside the tiers')
        if any(name not in by_tier.get(p.get('difficulty'), ()) for p, name in zip(problems, names)):
            fail(f'a mixed Quick Test on {slug} called a slot with a tier that does not hold it')
    # other subjects keep the old builder (nothing changed for them)
    if whole_pool.uses_whole_pool('gcse', 'cs') or whole_pool.uses_whole_pool('eursc', 'science'):
        fail('the whole-pool draw must apply to GCSE maths only (decision V8)')
    cs = TOPICS['gcse']['cs']
    slug = sorted(cs)[0]
    problems, _cfg = build_quicktest_problems('gcse', 'cs', slug, 'standard', 'foundational', TOPICS)
    if len(problems) != QUICKTEST_LENGTH:
        fail(f'gcse cs Quick Test built {len(problems)} problems')


def main():
    t0 = time.time()
    check_pool_draw()
    check_flag_stays_put()
    check_practice_tiers()
    check_mcq_quick_tests()
    check_determinism()
    check_sessions()
    check_set_work()
    check_mixed_and_other_subjects()
    if FAILURES:
        print('\n'.join(FAILURES[:40]))
        print(f'FAILED: {len(FAILURES)} issue(s)')
        sys.exit(1)
    print(f'GCSE maths whole-pool Quick Test and set work smoke passed ({time.time() - t0:.1f}s)')


if __name__ == '__main__':
    main()
