"""Retired GCSE maths practice variants stay usable — run: python scripts/test_gcse_maths_retired_compat_smoke.py

Phase 1 of docs/GCSE_MATHS_VARIETY.md took 76 variant names out of the practice pools (scripts/gcse_verify/register.RETIRED).
A queue stored before the change, or a saved problem that is rerolled, still names them.  This smoke checks, through
the same app functions the routes use, that

  * every retired name generates a problem through its topic generator (mode practice, its own tier);
  * a stored queue that holds retired names carries on: the next question is served by name, with no rebuild;
  * a retired name can be rerolled when it is randomised, exactly as before;
  * a name that really is unknown still falls back to a rebuilt queue (the safety net is untouched);
  * no retired name is in a pool a new queue is built from, and every retired function is defined in exactly one module.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('SECRET_KEY', 'pb-testing')

import random  # noqa: E402

from app import (TOPICS, _build_problem_queue, _can_reroll_variant, _generate_queued_problem,  # noqa: E402
                 _persist_queue_state, _reroll_variant_problem, _selection_key, app)
from gcse_verify import register, variety  # noqa: E402

FAILURES = []


def fail(msg):
    FAILURES.append(msg)


def main():
    pool_names = {}
    for slug in sorted({k.split('/')[0] for k in register.RETIRED}):
        cfg = TOPICS['gcse']['maths'][slug]
        for tier in ('foundational', 'intermediate', 'difficult'):
            names = set()
            for i in range(25):         # a queue is 7 slots drawn from the pool, so build it often enough to see the pool
                random.seed(i)
                names |= set(_build_problem_queue(cfg, 'gcse', 'maths', slug, 'practice', tier) or ())
            pool_names[(slug, tier)] = names

    served = 0
    rerolled = 0
    resumed = 0
    for key, (_replaced_by, _reason, tier) in sorted(register.RETIRED.items()):
        slug, fn = key.split('/', 1)
        cfg = TOPICS['gcse']['maths'][slug]
        if fn in pool_names[(slug, tier)]:
            fail(f'{key} is retired but a new queue can still contain it')
        random.seed(hash(key) & 0xFFFF)
        try:
            problem = cfg['func'](tier, 'practice', variant_name=fn)
        except Exception as exc:  # noqa: BLE001
            fail(f'{key} does not generate: {exc!r}')
            continue
        if not problem or not problem.get('question') or not problem.get('solution'):
            fail(f'{key} generated an empty problem')
            continue
        served += 1

        if _can_reroll_variant(cfg, 'practice', tier, fn):
            again = _reroll_variant_problem(cfg, 'practice', tier, fn)
            if not again or not again.get('question'):
                fail(f'{key} cannot be rerolled')
            else:
                rerolled += 1

        # a queue stored before Phase 1: a retired name in the middle, then a name that still exists
        live = sorted(pool_names[(slug, tier)])
        if not live:
            continue
        stored = [live[0], fn, live[-1]]
        with app.test_request_context('/'):
            qkey = _selection_key('gcse', 'maths', slug, 'practice', tier)
            _persist_queue_state(None, qkey, stored, 0, live[0])
            p, meta = _generate_queued_problem(cfg, 'gcse', 'maths', slug, 'practice', tier, 'next')
            if meta['variant_name'] != fn or meta['queue_position'] != 2 or meta['queue_length'] != 3:
                fail(f'{key}: the stored queue was not resumed on the retired name ({meta})')
            elif not p.get('question'):
                fail(f'{key}: the resumed question is empty')
            else:
                resumed += 1

    # a name that is unknown everywhere still rebuilds the queue
    slug, tier = 'algebra', 'foundational'
    cfg = TOPICS['gcse']['maths'][slug]
    with app.test_request_context('/'):
        qkey = _selection_key('gcse', 'maths', slug, 'practice', tier)
        _persist_queue_state(None, qkey, ['no_such_variant_zzz'], -1, None)
        p, meta = _generate_queued_problem(cfg, 'gcse', 'maths', slug, 'practice', tier, 'next')
        if meta['variant_name'] == 'no_such_variant_zzz' or not p.get('question'):
            fail(f'an unknown variant name did not rebuild the queue ({meta})')

    # a fresh process (no app, nothing preloaded) resolves a retired name and returns None for an unknown one: the
    # global lookup once crashed on an import cycle in generators.shared before it could say "unknown"
    probe = ('import sys; sys.path.insert(0, sys.argv[1]); '
             'from generators.shared.variant_utils import lookup_variant_by_name as L; '
             'assert L("no_such_variant_zzz") is None; f = L(sys.argv[2]); assert f is not None and f.__name__ == sys.argv[2]; '
             'print("ok")')
    some = sorted(register.RETIRED)[0].split('/', 1)[1]
    run = subprocess.run([sys.executable, '-B', '-c', probe, str(ROOT), some], capture_output=True, text=True, timeout=90)
    if run.returncode != 0 or 'ok' not in run.stdout:
        fail(f'the name lookup fails in a fresh process: {(run.stderr or run.stdout).strip()[-300:]}')

    # one module per retired function
    for key in sorted(register.RETIRED):
        slug, fn = key.split('/', 1)
        mods = variety.defining_modules(fn, ROOT)
        if len(mods) != 1:
            fail(f'{key} is defined in {len(mods)} modules: {sorted(mods)}')

    if FAILURES:
        print('\n'.join(FAILURES[:30]))
        print(f'{len(FAILURES)} failure(s)')
        sys.exit(1)
    print(f'retired variants: {served} of {len(register.RETIRED)} generate by name, {resumed} resume from a stored queue, '
          f'{rerolled} reroll; unknown names still rebuild')
    print('GCSE maths retired-variant compatibility smoke passed.')


if __name__ == '__main__':
    main()
