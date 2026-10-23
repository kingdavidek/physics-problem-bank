"""Re-solve one generated problem from its recorded inputs and compare with the key."""
from __future__ import annotations

import re
from fractions import Fraction

from . import core
from .latex import numbers_in, plain
from .registry import DIAGRAM_CHECKS, NEEDS_PROBLEM, SOLVERS, fr

_OPTION = re.compile(r'^\s*([A-H])\s*[.):]?\s+(.*)$', re.S)


class Outcome:
    """Result of verifying one problem: status in {'verified', 'norecord', 'failed'}."""

    def __init__(self, status, findings=None, expected=None):
        self.status = status
        self.findings = findings or []          # list of (kind, message)
        self.expected = expected


def parse_options(p):
    """[(letter, text)] for an MCQ-style problem, or None."""
    opts = p.get('options')
    if not opts:
        return None
    out = []
    for o in opts:
        m = _OPTION.match(str(o))
        if not m:
            return None
        out.append((m.group(1), plain(m.group(2))))
    return out


def _flatten_numbers(value):
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float, Fraction)):
        return [value]
    if isinstance(value, str) and re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        return [Fraction(value)]
    if isinstance(value, (list, tuple, set)):
        out = []
        for v in value:
            out.extend(_flatten_numbers(v))
        return out
    return []


_UP_WORDS = re.compile(r'increas|rise|rose|raise|interest|grow|appreciat|VAT|profit|mark-?up|pay rise', re.I)
_DOWN_WORDS = re.compile(r'decreas|reduc|discount|depreciat|fall|fell|loss|sale|\boff\b|drop|cut', re.I)


def _compact(text):
    return re.sub(r'\s+', '', str(text).replace('−', '-'))


def presence_guard(record, question_text):
    """Messages for recorded inputs that the question does not show (numbers not declared derived, the
    whole of an ``expr`` for arithmetic, and the direction of a percentage change)."""
    present = numbers_in(question_text)
    msgs = []
    sign = record['inputs'].get('sign')
    if sign == 'up' and not _UP_WORDS.search(question_text):
        msgs.append("recorded sign='up' but the question has no increase wording")
    if sign == 'down' and not _DOWN_WORDS.search(question_text):
        msgs.append("recorded sign='down' but the question has no decrease wording")
    if record['family'] == 'arith' and isinstance(record['inputs'].get('expr'), str):
        # The solver evaluates the recorded string, so the same expression must be the one the pupil sees.
        if _compact(record['inputs']['expr']) not in _compact(question_text):
            msgs.append(f"expression {record['inputs']['expr']!r} is not shown in the question as written")
    for name, value in record['inputs'].items():
        if name.endswith('_word') and isinstance(value, str):
            # a recorded wording (a colour, an event, a shape name) has to be the one the pupil reads
            if _compact(value).lower() not in _compact(question_text).lower():
                msgs.append(f'recorded wording {name}={value!r} does not appear in the question text')
            continue
        if name in record['derived']:
            continue
        if name == 'expr' and isinstance(value, str):
            for f in numbers_in(value):
                if f != 0 and f not in present:
                    msgs.append(f'expression {value!r} has the number {f} which is not in the question text')
                    break
            continue
        for v in _flatten_numbers(value):
            f = abs(fr(v))
            if f in (0, 1):         # 0 and 1 are often unwritten (x, not 1x; a missing + 0)
                continue
            if f not in present:
                msgs.append(f'recorded input {name}={v!r} does not appear in the question text '
                            f'(declare derived=({name!r},) if it is computed)')
                break
    return msgs


def solve_record(record, problem=None, records=None):
    """Run the registered solver. Raises core.Cannot when it cannot read the inputs."""
    fam = record['family']
    fn = SOLVERS.get(fam)
    if fn is None:
        raise core.Cannot(f'no solver registered for family {fam!r}')
    kwargs = dict(record['inputs'])
    if fam in NEEDS_PROBLEM:
        if problem is None:
            raise core.Cannot(f'solver {fam} needs the generated problem')
        kwargs['_p'] = problem
        kwargs['_records'] = records or [record]
    try:
        out = fn(**kwargs)
    except core.Cannot:
        raise
    except (TypeError, KeyError, ValueError, ZeroDivisionError, AttributeError, IndexError) as exc:
        raise core.Cannot(f'solver {fam} failed on inputs {record["inputs"]}: {exc!r}') from exc
    if isinstance(out, core.AnyOf):
        return out
    if not isinstance(out, list):
        out = [out]
    return out


def _steps_key(p):
    """For proof_steps keys ('1|s1|s2' ordered, 'pick|3|c1|c2|c3' chosen): (how, required texts, other bank texts)."""
    raw = str(p.get('correct_answer_raw'))
    parts = raw.split('|')
    bank = {str(b.get('id')): plain(str(b.get('text'))) for b in (p.get('answer_step_bank') or [])}
    ids = parts[2:] if parts[0] == 'pick' else parts[1:]
    if not ids or any(i not in bank for i in ids):
        return None
    required = [bank[i] for i in ids]
    others = [t for i, t in bank.items() if i not in ids]
    return ('steps_pick' if parts[0] == 'pick' else 'steps_order'), required, others


def key_fields_for(p):
    """(fields, how) describing the generator's key: practice raw fields or the keyed option text."""
    if p.get('answer_type') == 'proof_steps' and p.get('correct_answer_raw') is not None:
        sk = _steps_key(p)
        if sk is None:
            return None, 'none'
        return sk[1], sk[0]
    opts = parse_options(p)
    if opts is not None:
        letter = str(p.get('correct_answer', '')).strip().upper()
        texts = [t for ltr, t in opts if ltr == letter]
        return ([texts[0]] if len(texts) == 1 else None), 'option'
    raw = p.get('correct_answer_raw')
    at = p.get('answer_type')
    if raw is None or not at:
        return None, 'none'
    fields = core.split_key(at, raw)
    if at == 'linear':
        fields = [re.sub(r'^\s*[A-Za-z]\s*=\s*', '', f) for f in fields]      # 'w=12' keys a plain 12
    return fields, 'raw'


def verify_problem(p, records):
    """Re-solve ``p`` using the last record; return an Outcome."""
    if not records:
        return Outcome('norecord')
    rec = records[-1]
    qtext = plain(p['question'])
    findings = []

    try:
        expected = solve_record(rec, p, records)
    except core.Cannot as exc:
        return Outcome('failed', [('unreadable', str(exc))])

    for msg in presence_guard(rec, qtext):
        findings.append(('presence', msg))
    check = DIAGRAM_CHECKS.get(rec['family'])
    if check is not None:
        try:
            for msg in check(rec['inputs'], str(p['question'])):
                findings.append(('diagram', msg))
        except core.Cannot as exc:
            findings.append(('diagram', f'drawing unreadable: {exc}'))

    if isinstance(expected, list) and expected and isinstance(expected[0], core.Verdict):
        for v in expected:
            if not v.ok:
                findings.append((v.kind, v.message))
        return Outcome('failed' if findings else 'verified', findings, expected)

    fields, how = key_fields_for(p)
    if how == 'steps_pick':
        atom = expected[0]
        others = _steps_key(p)[2]
        for t in fields:
            if not atom.test(t):
                findings.append(('answer', f'keyed step {t!r} does not satisfy: {atom.desc}'))
        for t in others:
            if atom.test(t):
                findings.append(('answer', f'distractor {t!r} also satisfies: {atom.desc}'))
        return Outcome('failed' if findings else 'verified', findings, expected)
    if fields is None:
        findings.append(('answer', f'no key to compare against ({how}); answer_type={p.get("answer_type")!r}'))
        return Outcome('failed', findings, expected)

    specs = core.stated_specs(qtext)
    if how == 'raw' and p.get('answer_type') == 'number_fields':
        fields, extra = _mcq_field_texts(p, fields, expected)
        findings.extend(extra)
    ok, msgs, kind = core.match_answer(expected, fields, specs)
    if not ok:
        for m in msgs:
            findings.append((kind, m))

    if how == 'option':
        findings.extend(_option_checks(p, expected, specs))

    if findings:
        return Outcome('failed', findings, expected)
    return Outcome('verified', [], expected)


def _mcq_field_texts(p, fields, expected):
    """For a Pick expected on a multiple-choice field of a number_fields key: swap the keyed letter for its
    option text, and report any other option of that field that also satisfies the same test."""
    if isinstance(expected, core.AnyOf) or not isinstance(expected, list) or len(expected) != len(fields):
        return fields, []
    types = p.get('answer_field_types') or []
    options = p.get('answer_field_options') or []
    out, findings = list(fields), []
    for i, atom in enumerate(expected):
        if not isinstance(atom, core.Pick) or i >= len(types) or types[i] != 'mcq' or i >= len(options):
            continue
        letter = str(fields[i]).strip().upper()
        opts = [plain(str(o)) for o in (options[i] or [])]
        idx = 'ABCDEFGH'.find(letter)
        if len(letter) != 1 or idx < 0 or idx >= len(opts):
            findings.append(('answer', f'field {i + 1}: key {fields[i]!r} does not point at one of {opts}'))
            continue
        out[i] = opts[idx]
        for j, text in enumerate(opts):
            if j != idx and atom.test(text):
                findings.append(('mcq', f'field {i + 1}: option {"ABCDEFGH"[j]} ({text!r}) also satisfies: {atom.desc}'))
    return out, findings


def _option_checks(p, expected, specs):
    """MCQ structure against the recomputed value: one option equals it, and it is the keyed one; no equivalents."""
    out = []
    opts = parse_options(p)
    letter = str(p.get('correct_answer', '')).strip().upper()
    if len(opts) < 2:
        return out
    atoms_set = expected if isinstance(expected, core.AnyOf) else [expected]
    atoms = atoms_set[0]
    if len(atoms) != 1:
        return out
    atom = atoms[0]
    matching = []
    for ltr, text in opts:
        ok, _, _ = core.match_atom(atom, text, specs)
        if ok:
            matching.append(ltr)
    if letter and matching and matching != [letter]:
        out.append(('mcq', f'options {matching} all equal the recomputed value but the key is {letter}'))
    if not isinstance(atom, core.Pick):
        canon = {}
        for ltr, text in opts:
            c = core.canon_option(atom, text)
            if c in canon:
                out.append(('mcq', f'options {canon[c]} and {ltr} are equivalent ("{text}")'))
            canon.setdefault(c, ltr)
    return out
