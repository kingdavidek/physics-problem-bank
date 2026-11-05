"""GCSE maths hints census (Stage 1 of docs/GCSE_MATHS_HINTS_REVIEW_PLAN.md). A reusable tool, not a smoke test.

Writes ``review_data.json`` for the review page: for every GCSE maths topic (alphabetical by display name) one row per
practice slot with the question, the key, rung 1 (the hint a pupil sees after a wrong typed answer with no recognised
slip), rung 2 (the bigger hint) and automatic flags; every slip message that can fire on the topic's practice slots with
one example; every multiple-choice distractor note with one example.

Everything goes through the real code: ``build_ladder`` for the two rungs, ``_diagnose`` for the messages (candidates
from the rules, as the hints smokes do), the topic functions in MCQ mode for the notes. Nothing is stored or changed.

Usage (from the repo root, Python 3.12 with PB_TESTING=1 PB_ALLOW_DEV_SECRET=1 CORS_ORIGINS=https://app.example.com):

    python -B scripts/hints_census.py [--out PATH] [--seeds 3] [--note-seeds 10] [--topics a,b] [--no-messages]
"""
from __future__ import annotations

import argparse
import collections
import datetime
import difflib
import json
import os
import re
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('PB_TESTING', '1')
os.environ.setdefault('PB_ALLOW_DEV_SECRET', '1')
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')
warnings.filterwarnings('ignore')

from generators.shared import misconceptions as M  # noqa: E402
from generators.shared import option_notes as ON  # noqa: E402
from gcse_verify import harness  # noqa: E402
from gcse_verify.register import RETIRED  # noqa: E402
import test_gcse_maths_hints_smoke as S  # noqa: E402 - slip candidates and the real diagnosis path
import test_gcse_maths_hints_ladder_smoke as L  # noqa: E402 - the independent key scan
from topic_registry import TOPICS  # noqa: E402

DEFAULT_OUT = '/mnt/user-data/outputs/hint_review/review_data.json'
TIER_LETTER = {'foundational': 'F', 'intermediate': 'I', 'difficult': 'D'}
TIER_ORDER = {'F': 0, 'I': 1, 'D': 2}
FLAGS = ('same_as_bigger', 'bigger_restates_question', 'generic', 'default_hint', 'no_bigger', 'mentions_missing',
         'pre_attempt_phrasing', 'long', 'bigger_shows_result', 'weak')

GENERIC_MIN_SLOTS = 8
HINT_LONG, BIGGER_LONG, WEAK_SHORT = 160, 200, 25

# Openings that read oddly after a wrong attempt ("Start by" is fine). Matched at the start of the hint, lower case.
PRE_ATTEMPT_START = (
    r'remember\b', r'before you\b', r'before starting\b', r'before beginning\b', r'first\b',
    r'begin by\b', r'you will need\b', r"you'll need\b", r'you are going to\b', r"you're going to\b", r'make sure you\b',
    r'read the question\b', r'read through\b', r'always\b', r'never\b', r'when you\b', r'to start,', r'to begin,',
    r'you should\b', r'you need to start\b', r'think about what you\b', r"don't forget\b", r'do not forget\b',
)
PRE_ATTEMPT_ANYWHERE = (r'\bbefore you (?:start|begin|answer|calculate|work)\b', r'\bwhen you start\b', r'\bat the start\b')
VAGUE = (
    'check your working', 'think carefully', 'try again', 'have another go', 'read the question carefully',
    'look carefully', 'check your answer', 'be careful', 'think about it', 'read the question', 'check your calculation',
    'check your calculations', 'have a go', 'work carefully',
)
VISUAL_WORD = re.compile(r'\b(?:the|this|that|each)\s+(diagram|figure|graph|table|chart|sketch|picture|drawing|number line|'
                         r'venn diagram|histogram|ogive|scatter graph|grid)\b', re.I)
QUESTION_POINTS = re.compile(r'\b(?:diagram|figure|graph|table|chart|venn diagram)\b[^.?]{0,40}\b(?:shown|below|above|opposite)\b'
                             r'|\b(?:shown|given|drawn)\s+(?:below|above|opposite)\b|\b(?:in|on|from|use)\s+the\s+'
                             r'(?:diagram|figure|graph|table|chart)\b|\bthe\s+(?:diagram|figure)\b', re.I)
SVG_RE = re.compile(r'<svg\b.*?</svg\s*>|<img\b[^>]*>|<canvas\b.*?</canvas\s*>', re.I | re.S)
TAIL_RESULT = re.compile(r'[=\u2248]\s*[£$€]?\s*[-−]?\d[\d,]*(?:\.\d+)?\s*(?:\\\))?\s*(?:°|%|[a-zA-Z]{1,4}(?:[²³]|/[a-zA-Z]{1,3})?)?'
                         r'\s*(?:\\\))?\s*[.;]?\s*$')


# ─────────────────────────────────────────────────────────────────────────────
# Text helpers
# ─────────────────────────────────────────────────────────────────────────────

def has_visual(problem):
    """True when the pupil sees a drawing, graph or table with the question."""
    for value in problem.values():
        if isinstance(value, str) and re.search(r'<svg\b|<img\b|<canvas\b|<table\b', value, re.I):
            return True
    return False


def question_text(problem):
    """The question as plain text (LaTeX kept), with '[diagram]' where a drawing was removed."""
    raw = str(problem.get('question') or '')
    had = bool(SVG_RE.search(raw))
    text = SVG_RE.sub(' [diagram] ', raw)
    text = re.sub(r'</t[dh]\s*>', ' | ', text, flags=re.I)
    text = re.sub(r'</tr\s*>', ' ; ', text, flags=re.I)
    text = M.plain_line(text)
    text = re.sub(r'(?:\[diagram\]\s*){2,}', '[diagram] ', text).strip()
    if not had and has_visual({k: v for k, v in problem.items() if k != 'question'}):
        text += ' [diagram]'
    return text


def answer_text(problem):
    ans = problem.get('correct_answer')
    if ans in (None, ''):
        ans = problem.get('correct_answer_raw')
    return M.plain_line(str(ans if ans is not None else '').replace('\x1e', '; '))


def squash(text):
    return re.sub(r'[^a-z0-9]+', '', str(text).lower().replace('−', '-'))


def words(text):
    return re.findall(r'[a-z]{2,}|\d+(?:\.\d+)?', str(text).lower())


def solution_steps(problem):
    sol = problem.get('solution')
    if not isinstance(sol, str):
        return []
    return [x for x in (M.plain_line(s) for s in M._STEP_SPLIT_RE.split(sol)) if x]


def hint_source(problem, topic, raw):
    """Which of the four sources ``nudge_line`` takes (a re-statement of its order, checked against its text)."""
    record = problem.get('answer_record')
    family = record.get('f') if isinstance(record, dict) else None
    if family and M.NUDGES.get(family):
        return 'family'
    hint = problem.get('hint')
    if isinstance(hint, str) and not any(m in hint.lower() for m in M._UNSAFE_MARKUP):
        if M._ok_line(M.plain_line(hint), M.HINT_MAX_LEN, raw, problem.get('answer_type'), M.question_values(problem)):
            return 'question'
    return 'topic' if M.NUDGES.get(topic) else 'default'


# ─────────────────────────────────────────────────────────────────────────────
# One practice question: the two rungs
# ─────────────────────────────────────────────────────────────────────────────

def ladder_row(slot, problem):
    """The data of one generated question, or None when no wrong typed answer gets a ladder for it."""
    raw = problem.get('correct_answer_raw') if isinstance(problem, dict) else None
    if raw is None or problem.get('options'):
        return None
    raw = str(raw)
    ladder = M.build_ladder(problem, topic=slot.slug, correct_raw=raw)
    source = hint_source(problem, slot.slug, raw)
    text = ladder['text']
    if source == 'question':
        assert text == M.plain_line(problem.get('hint')), (slot.label, text)
    steps = solution_steps(problem)
    return {
        'question': question_text(problem), 'answer': answer_text(problem), 'hint': text, 'hint_source': source,
        'bigger': ladder['bigger'], 'raw': raw, 'at': problem.get('answer_type'), 'visual': has_visual(problem),
        'q_values': M.question_values(problem), 'q_numbers': M.question_numbers(problem), 'steps': len(steps),
    }


def flags_for(d):
    """Flags of one seed's data (all except 'generic', which needs the whole corpus)."""
    out = set()
    hint, big, question = d['hint'], d['bigger'], d['question']
    if d['hint_source'] == 'default':
        out.add('default_hint')
    if big:
        h, b = squash(hint), squash(big)
        if h and b and (h == b or h in b or b in h or difflib.SequenceMatcher(None, h, b).ratio() >= 0.9):
            out.add('same_as_bigger')
        q = squash(question)
        bw = words(big)
        qw = set(words(question))
        if b in q or (len(bw) >= 3 and sum(w in qw for w in bw) / len(bw) >= 0.85):
            out.add('bigger_restates_question')
        shows = L.shows_key(big, d['raw'], question, d['at'])
        m = TAIL_RESULT.search(big)
        tail_new = False
        if m:
            nums = [v for v, _, _ in M._number_tokens(m.group(0))]
            tail_new = bool(nums) and not all(v in d['q_numbers'] or v in M._FIXED_TOTALS for v in nums)
        last = M._number_tokens(big)[-1:]       # a long decimal at the end ("= 60 × 0.7071") is a worked-out value
        if last and last[0][1] >= 3 and last[0][0] not in d['q_numbers']:
            tail_new = True
        if shows or tail_new:
            out.add('bigger_shows_result')
        if len(big) > BIGGER_LONG:
            out.add('long')
    elif d['steps'] >= 2 and d['at'] != 'proof_steps':
        out.add('no_bigger')
    if len(hint) > HINT_LONG:
        out.add('long')
    low = hint.lower().strip()
    if any(re.match(p, low) for p in PRE_ATTEMPT_START) or any(re.search(p, low) for p in PRE_ATTEMPT_ANYWHERE) \
            or any(re.search(p, big.lower()) for p in PRE_ATTEMPT_ANYWHERE):
        out.add('pre_attempt_phrasing')
    bare = low.rstrip('.! ')
    if len(hint) < WEAK_SHORT or any(bare == v or bare.startswith(v + ' ') and len(bare) < 40 for v in VAGUE):
        out.add('weak')
    if not d['visual']:
        qwords = {m.group(1).lower() for m in VISUAL_WORD.finditer(question)}
        for text in (hint, big):
            for m in VISUAL_WORD.finditer(text):
                if m.group(1).lower() not in qwords and m.group(1).lower() not in question.lower():
                    out.add('mentions_missing')
        if QUESTION_POINTS.search(question) and '[diagram]' not in question:
            out.add('mentions_missing')
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Slip messages that can fire on a problem (the real diagnosis path)
# ─────────────────────────────────────────────────────────────────────────────

def messages_of(slot, problem, question):
    """{rule id: (typed, key, message)} for each slip that fires on this question, found as the smokes do: the rules'
    own candidates, each run through ``_diagnose``."""
    found = {}
    for at, raw, where in S.answer_units(problem):
        part = where != 'whole'
        form = None if part else S.problem_answer_form(problem)
        exs = M.typed_examples(problem, at, raw, slot.slug, form)
        tried = collections.Counter()
        for rid, typed in exs:
            if rid in found or tried[rid] >= 3:
                continue
            tried[rid] += 1
            res = S.check_answer(at, raw, typed, form=form)
            if res.get('correct'):
                continue
            got = S.run_diag(problem, at, raw, typed, topic=slot.slug, form=form)
            if got is not None and got.kind == 'misconception':
                found.setdefault(got.rule_id, (typed, raw, got.message))
    rec = problem.get('answer_record')
    if rec is not None:
        st = S.new_topic_state()
        try:
            S.topic_item(slot, 0, problem, st)
        except Exception:  # noqa: BLE001 - a census must go on
            pass
        for rid, ex in {**st['examples'], **st['cd']['examples']}.items():
            found.setdefault(rid, (ex[3], ex[2], ex[4]))
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Multiple-choice notes
# ─────────────────────────────────────────────────────────────────────────────

def notes_of(problem):
    notes = problem.get(ON.KEY)
    if not isinstance(notes, dict):
        return []
    key_letter = str(problem.get('correct_answer') or '').strip().upper()[:1]
    texts = {str(o)[0]: ON.option_text(o) for o in problem.get('options') or []}
    out = []
    for option, note_id in notes.items():
        out.append((note_id, ON.note_text(note_id), option, texts.get(key_letter, '')))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def census(seeds=3, note_seeds=10, only=None, with_messages=True, log=print):
    t0 = time.time()
    names = {slug: cfg['name'] for slug, cfg in TOPICS['gcse']['maths'].items() if not only or slug in only}
    slots = [s for s in harness.enumerate_slots() if s.slug in names and s.key not in RETIRED]
    std = [s for s in slots if s.mode == 'standard']

    per_slot = {}                       # slot -> [data per seed]
    skipped = collections.Counter()
    msgs = collections.defaultdict(dict)    # topic -> rule id -> record
    for n, slot in enumerate(std, 1):
        datas = []
        for run in range(seeds):
            try:
                problem, _ = harness.generate(slot, run, record=False)
            except Exception as exc:  # noqa: BLE001
                skipped[f'error {type(exc).__name__}'] += 1
                continue
            if not isinstance(problem, dict):
                skipped['not a problem'] += 1
                continue
            d = ladder_row(slot, problem)
            if d is None:
                skipped['no typed key (options or none)'] += 1
                continue
            datas.append(d)
            if with_messages:
                for rid, (typed, key, message) in messages_of(slot, problem, d['question']).items():
                    rec = msgs[slot.slug].setdefault(rid, {
                        'id': f'msg/{slot.slug}/{rid}', 'text': message, 'example_question': d['question'],
                        'example_typed': typed, 'example_answer': d['answer'] if key == d['raw'] else key, 'slots': set()})
                    rec['slots'].add(slot.label)
        per_slot[slot] = datas
        if n % 200 == 0:
            log(f'  {n}/{len(std)} practice slots, {time.time() - t0:.0f}s')

    # generic: one hint text on many slots
    spread = collections.defaultdict(set)
    for slot, datas in per_slot.items():
        for d in datas:
            spread[d['hint']].add(slot.label)

    topics = {slug: {'slug': slug, 'name': name, 'practice': [], 'messages': [], 'notes': []} for slug, name in names.items()}
    for slot, datas in per_slot.items():
        if not datas:
            continue
        first = datas[0]
        flags = set()
        for d in datas:
            flags |= flags_for(d)
            if len(spread[d['hint']]) >= GENERIC_MIN_SLOTS:
                flags.add('generic')
        tier = TIER_LETTER[slot.tier]
        topics[slot.slug]['practice'].append({
            'id': f'{slot.slug}/{tier}/{slot.fn}', 'tier': tier, 'slot': slot.fn, 'question': first['question'],
            'answer': first['answer'], 'hint': first['hint'], 'hint_source': first['hint_source'], 'bigger': first['bigger'],
            'flags': [f for f in FLAGS if f in flags]})
    for t in topics.values():
        t['practice'].sort(key=lambda r: (not r['flags'], TIER_ORDER[r['tier']]))      # stable: slot order inside a tier
        for rid, rec in sorted(msgs.get(t['slug'], {}).items()):
            t['messages'].append({'id': rec['id'], 'text': rec['text'], 'example_question': rec['example_question'],
                                  'example_typed': rec['example_typed'], 'example_answer': rec['example_answer'],
                                  'count_slots': len(rec['slots'])})

    # notes: the MCQ-mode slots, several seeds each
    seen_notes = collections.defaultdict(dict)
    for slot in (s for s in slots if s.mode == 'mcq'):
        for run in range(note_seeds):
            try:
                problem, _ = harness.generate(slot, run, record=False)
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(problem, dict):
                continue
            for note_id, text, option, key in notes_of(problem):
                seen_notes[slot.slug].setdefault(note_id, {
                    'id': f'note/{slot.slug}/{note_id}', 'text': text, 'example_question': question_text(problem),
                    'option': option, 'answer': key})
    for slug, found in seen_notes.items():
        topics[slug]['notes'] = [found[k] for k in sorted(found)]

    return topics, names, skipped, time.time() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--note-seeds', type=int, default=10)
    ap.add_argument('--topics', default='', help='comma-separated topic slugs (default: all)')
    ap.add_argument('--no-messages', action='store_true')
    args = ap.parse_args()
    only = {x for x in args.topics.split(',') if x} or None
    topics, names, skipped, secs = census(args.seeds, args.note_seeds, only, not args.no_messages)

    data = {
        'generated': datetime.date.today().isoformat(),
        'topics': [{'slug': slug, 'name': names[slug], 'practice': topics[slug]['practice'],
                    'messages': topics[slug]['messages'], 'notes': topics[slug]['notes']}
                   for slug in sorted(names, key=lambda s: names[s].lower())],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

    flag_total = collections.Counter()
    print(f'\n{"topic":42} {"rows":>5} {"flagged":>7} {"msgs":>5} {"notes":>5}')
    per_topic = {}
    for t in data['topics']:
        c = collections.Counter(f for r in t['practice'] for f in r['flags'])
        flag_total += c
        per_topic[t['name']] = c
        flagged = sum(1 for r in t['practice'] if r['flags'])
        print(f'{t["name"][:42]:42} {len(t["practice"]):5} {flagged:7} {len(t["messages"]):5} {len(t["notes"]):5}')
    rows = sum(len(t['practice']) for t in data['topics'])
    flagged_rows = sum(1 for t in data['topics'] for r in t['practice'] if r['flags'])
    print(f'\nrows {rows}, flagged rows {flagged_rows}, skipped {dict(skipped)}')
    print('flags overall:', {f: flag_total[f] for f in FLAGS})
    print('flags per topic (total flags):')
    for name, c in sorted(per_topic.items(), key=lambda kv: -sum(kv[1].values())):
        print(f'  {name[:40]:40} {sum(c.values()):4}  {dict(c)}')
    print(f'messages {sum(len(t["messages"]) for t in data["topics"])}, notes {sum(len(t["notes"]) for t in data["topics"])}')
    print(f'{out}: {out.stat().st_size / 1e6:.2f} MB, {secs:.0f}s')


if __name__ == '__main__':
    main()
