"""Phase 1 audit — find non-MCQ practice problems missing correct_answer_raw.

Usage:
  python scripts/audit_correct_answer_raw.py
  python scripts/audit_correct_answer_raw.py --level gcse --subject maths
  python scripts/audit_correct_answer_raw.py --topic bidmas --missing-only
  python scripts/audit_correct_answer_raw.py --json
  python scripts/audit_correct_answer_raw.py --fail-on-missing

Exit codes:
  0  audit completed (or no missing when --fail-on-missing)
  1  missing graded answers found (only with --fail-on-missing)
  2  fatal error generating a problem
"""
from __future__ import annotations

import argparse
import inspect
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from topic_registry import TOPICS  # noqa: E402

DIFFICULTIES = ('foundational', 'intermediate', 'difficult')
PRACTICE_MODE = 'practice'

POOL_ATTRS = {
    'foundational': (
        '_FOUNDATIONAL', '_foundational', '_found_pool', 'FOUNDATIONAL',
        '_FOUND_POOL', 'found_pool',
    ),
    'intermediate': (
        '_INTERMEDIATE', '_intermediate', '_inter_pool', 'INTERMEDIATE',
        '_INTER_POOL', 'inter_pool',
    ),
    'difficult': (
        '_DIFFICULT', '_difficult', '_diff_pool', 'DIFFICULT',
        '_DIFF_POOL', 'diff_pool',
    ),
}

# When a topic has no variants_func, generate this many problems per difficulty.
SAMPLE_WITHOUT_VARIANTS = 8
# Extra samples of variants_func to discover variants beyond a single random draw.
VARIANT_SAMPLE_ROUNDS = 40


def _iter_topics(level=None, subject=None, topic=None):
    for lvl, subjects in TOPICS.items():
        if level and lvl != level:
            continue
        for subj, topics in subjects.items():
            if subject and subj != subject:
                continue
            for slug, cfg in topics.items():
                if topic and slug != topic:
                    continue
                yield lvl, subj, slug, cfg


def _pool_from_module(mod, difficulty):
    if mod is None:
        return None
    for attr in POOL_ATTRS.get(difficulty, ()):
        val = getattr(mod, attr, None)
        if isinstance(val, list) and val and all(callable(x) for x in val):
            return list(val)
    for name in ('_POOLS', '_PRACTICE_POOLS'):
        pools = getattr(mod, name, None)
        if isinstance(pools, dict):
            val = pools.get(difficulty)
            if isinstance(val, list) and val and all(callable(x) for x in val):
                return list(val)
    return None


def _collect_variant_callables(variants_func, difficulty, mode=PRACTICE_MODE):
    """Return unique practice variant callables for a difficulty tier."""
    mod = inspect.getmodule(variants_func)
    pool = _pool_from_module(mod, difficulty)
    if pool is not None:
        return pool

    seen = {}
    for _ in range(VARIANT_SAMPLE_ROUNDS):
        try:
            batch = variants_func(difficulty, mode) or []
        except TypeError:
            try:
                batch = variants_func(difficulty) or []
            except Exception:
                break
        except Exception:
            break
        for fn in batch:
            if callable(fn) and not getattr(fn, '__name__', '').endswith('_mcq'):
                # Skip pure MCQ factories when present in practice queues
                name = getattr(fn, '__name__', repr(fn))
                seen[name] = fn
    return list(seen.values())


def _generate_problem(func, difficulty, mode, variant_name=None):
    kwargs = {}
    if variant_name is not None:
        kwargs['variant_name'] = variant_name
    try:
        return func(difficulty, mode, **kwargs)
    except TypeError:
        # Older generators may not accept variant_name
        return func(difficulty, mode)


def _is_mcq(problem):
    return bool(problem and problem.get('options'))


def _has_raw(problem):
    raw = problem.get('correct_answer_raw') if problem else None
    return raw is not None and str(raw).strip() != ''


def audit_topic(level, subject, topic, cfg, *, samples=SAMPLE_WITHOUT_VARIANTS):
    """Audit one topic. Returns a dict summary."""
    func = cfg['func']
    variants_func = cfg.get('variants_func')
    name = cfg.get('name', topic)

    rows = []
    errors = []

    for difficulty in DIFFICULTIES:
        if variants_func:
            variants = _collect_variant_callables(variants_func, difficulty)
            if not variants:
                # Fall back to anonymous samples
                for i in range(samples):
                    try:
                        problem = _generate_problem(func, difficulty, PRACTICE_MODE)
                    except Exception as exc:
                        errors.append({
                            'difficulty': difficulty,
                            'variant': f'<sample_{i}>',
                            'error': f'{type(exc).__name__}: {exc}',
                        })
                        continue
                    rows.append(_classify_row(difficulty, f'<sample_{i}>', problem))
                continue

            for vf in variants:
                vname = getattr(vf, '__name__', repr(vf))
                try:
                    problem = _generate_problem(
                        func, difficulty, PRACTICE_MODE, variant_name=vname
                    )
                except Exception as exc:
                    errors.append({
                        'difficulty': difficulty,
                        'variant': vname,
                        'error': f'{type(exc).__name__}: {exc}',
                    })
                    continue
                rows.append(_classify_row(difficulty, vname, problem))
        else:
            for i in range(samples):
                try:
                    problem = _generate_problem(func, difficulty, PRACTICE_MODE)
                except Exception as exc:
                    errors.append({
                        'difficulty': difficulty,
                        'variant': f'<sample_{i}>',
                        'error': f'{type(exc).__name__}: {exc}',
                    })
                    continue
                rows.append(_classify_row(difficulty, f'<sample_{i}>', problem))

    graded = [r for r in rows if r['status'] == 'graded']
    missing = [r for r in rows if r['status'] == 'missing']
    mcq = [r for r in rows if r['status'] == 'mcq']

    return {
        'level': level,
        'subject': subject,
        'topic': topic,
        'name': name,
        'has_variants_func': bool(variants_func),
        'total': len(rows),
        'graded': len(graded),
        'missing': len(missing),
        'mcq': len(mcq),
        'errors': errors,
        'missing_variants': [
            {
                'difficulty': r['difficulty'],
                'variant': r['variant'],
                'answer_type': r.get('answer_type'),
            }
            for r in missing
        ],
        'graded_variants': [
            {
                'difficulty': r['difficulty'],
                'variant': r['variant'],
                'answer_type': r.get('answer_type'),
            }
            for r in graded
        ],
    }


def _classify_row(difficulty, variant, problem):
    if _is_mcq(problem):
        return {
            'difficulty': difficulty,
            'variant': variant,
            'status': 'mcq',
            'answer_type': None,
        }
    if _has_raw(problem):
        return {
            'difficulty': difficulty,
            'variant': variant,
            'status': 'graded',
            'answer_type': problem.get('answer_type') or 'number',
        }
    return {
        'difficulty': difficulty,
        'variant': variant,
        'status': 'missing',
        'answer_type': problem.get('answer_type'),
    }


def _print_human(results, *, missing_only=False, show_graded=False):
    total_graded = sum(r['graded'] for r in results)
    total_missing = sum(r['missing'] for r in results)
    total_mcq = sum(r['mcq'] for r in results)
    total_errors = sum(len(r['errors']) for r in results)
    total_problems = sum(r['total'] for r in results)

    print('Phase 1 audit - correct_answer_raw coverage (non-MCQ practice)')
    print('=' * 72)
    print(
        f'Topics: {len(results)}  |  problems: {total_problems}  |  '
        f'graded: {total_graded}  |  missing: {total_missing}  |  '
        f'mcq-skipped: {total_mcq}  |  errors: {total_errors}'
    )
    print()

    for r in results:
        if missing_only and r['missing'] == 0 and not r['errors']:
            continue
        header = (
            f"{r['level']}/{r['subject']}/{r['topic']}  "
            f"({r['name']})  "
            f"graded={r['graded']} missing={r['missing']} "
            f"mcq={r['mcq']} total={r['total']}"
        )
        print(header)
        if r['errors']:
            for err in r['errors']:
                print(
                    f"  ERROR  {err['difficulty']}/{err['variant']}: {err['error']}"
                )
        for item in r['missing_variants']:
            print(f"  MISSING  {item['difficulty']}/{item['variant']}")
        if show_graded:
            for item in r['graded_variants']:
                at = item.get('answer_type') or 'number'
                print(f"  GRADED   {item['difficulty']}/{item['variant']}  [{at}]")
        if not missing_only or r['missing'] or r['errors']:
            print()

    print('-' * 72)
    print(
        f'Summary: {total_graded} graded, {total_missing} missing '
        f'correct_answer_raw (of {total_problems - total_mcq} non-MCQ).'
    )
    if total_missing:
        print(
            'Note: missing does not always mean a bug - conceptual / Phase 2+ '
            'variants (text, fractions, surds) are expected to stay ungraded.'
        )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Audit practice problems for missing correct_answer_raw.'
    )
    parser.add_argument('--level', help='Filter by level (e.g. gcse)')
    parser.add_argument('--subject', help='Filter by subject (e.g. maths)')
    parser.add_argument('--topic', help='Filter by topic slug (e.g. bidmas)')
    parser.add_argument(
        '--samples',
        type=int,
        default=SAMPLE_WITHOUT_VARIANTS,
        help='Samples per difficulty when topic has no variants_func',
    )
    parser.add_argument(
        '--missing-only',
        action='store_true',
        help='Only print topics that have missing / errors',
    )
    parser.add_argument(
        '--show-graded',
        action='store_true',
        help='Also list graded variants',
    )
    parser.add_argument('--json', action='store_true', help='Emit JSON report')
    parser.add_argument(
        '--fail-on-missing',
        action='store_true',
        help='Exit 1 if any non-MCQ problem is missing correct_answer_raw',
    )
    args = parser.parse_args(argv)

    results = []
    fatal = False
    for level, subject, topic, cfg in _iter_topics(
        level=args.level, subject=args.subject, topic=args.topic
    ):
        try:
            results.append(
                audit_topic(
                    level, subject, topic, cfg, samples=max(1, args.samples)
                )
            )
        except Exception as exc:
            fatal = True
            results.append({
                'level': level,
                'subject': subject,
                'topic': topic,
                'name': cfg.get('name', topic),
                'has_variants_func': bool(cfg.get('variants_func')),
                'total': 0,
                'graded': 0,
                'missing': 0,
                'mcq': 0,
                'errors': [{
                    'difficulty': '*',
                    'variant': '*',
                    'error': f'{type(exc).__name__}: {exc}',
                }],
                'missing_variants': [],
                'graded_variants': [],
            })

    results.sort(key=lambda r: (r['level'], r['subject'], r['topic']))

    if args.json:
        payload = {
            'topics': results,
            'summary': {
                'topics': len(results),
                'total': sum(r['total'] for r in results),
                'graded': sum(r['graded'] for r in results),
                'missing': sum(r['missing'] for r in results),
                'mcq': sum(r['mcq'] for r in results),
                'errors': sum(len(r['errors']) for r in results),
            },
        }
        print(json.dumps(payload, indent=2))
    else:
        _print_human(
            results,
            missing_only=args.missing_only,
            show_graded=args.show_graded,
        )

    if fatal:
        return 2
    if args.fail_on_missing and any(r['missing'] for r in results):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
