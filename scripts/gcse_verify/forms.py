"""Typed forms: how a pupil may enter a keyed answer (must be accepted) and wrong entries (must be rejected)."""
from __future__ import annotations

import re
from fractions import Fraction

from .core import parse_num

SEP = '\x1e'

# Answer types whose key is not typed as such (the pupil picks or arranges items), so no typed form applies.
UNTYPED = ('proof_steps',)


def _fmt(v):
    v = Fraction(v)
    if v.denominator == 1:
        return str(v.numerator)
    s = f'{float(v):.10f}'.rstrip('0').rstrip('.')
    return s


def _terminating(v):
    d = Fraction(v).denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def _num(text):
    try:
        v = parse_num(text)
    except Exception:
        return None
    return None if v is None else Fraction(v)


def _surd_term(k, r):
    k = int(k)
    if k == 1:
        return f'√{r}'
    if k == -1:
        return f'-√{r}'
    return f'{k}√{r}'


def _linear_text(m, c):
    """y = mx + c written the way a pupil would."""
    m, c = Fraction(m), Fraction(c)
    xs = '' if m == 0 else ('x' if m == 1 else ('-x' if m == -1 else f'{_fmt(m)}x'))
    if m == 0:
        return f'y={_fmt(c)}'
    if c == 0:
        return f'y={xs}'
    return f'y={xs}{"+" if c > 0 else "-"}{_fmt(abs(c))}'


def _surd_binomial_parts(raw):
    m = re.fullmatch(r'(-?\d+)\|(\d+)\|(\d+)\|([+-])', raw)
    return m.groups() if m else None


def _frac_numerator_denominator(raw):
    """(numerator text, denominator text) typed in the stacked fraction boxes for a surd or algebraic fraction key."""
    parts = raw.split('|')
    if parts[0] == 'b' and len(parts) == 7:
        _, scale, const, coef, rad, den, sign = parts
        inner = f'{const}{sign}{_surd_term(coef, rad)}'
        s = int(scale)
        head = '' if s == 1 else ('-' if s == -1 else str(s))
        return f'{head}({inner})', den
    if parts[0] == 'd' and len(parts) == 4:
        return f'√{parts[1]}+√{parts[2]}', parts[3]
    if parts[0] == 'e' and len(parts) == 5:
        ip, sc, rad, den = parts[1:]
        sc_i = int(sc)
        tail = f'{"+" if sc_i >= 0 else "-"}{_surd_term(abs(sc_i), rad)}'
        return f'{ip}{tail}', den
    if len(parts) == 3 and all(re.fullmatch(r'-?\d+', x) for x in parts):
        return _surd_term(parts[0], parts[1]), parts[2]
    if len(parts) == 2:
        return parts[0], parts[1]
    return None


def _linear_parts(raw):
    """(letter or None, value) of a linear key such as 'w=12', 'x = -3' or '7'."""
    m = re.fullmatch(r'\s*([A-Za-z])\s*=\s*(.+?)\s*', str(raw))
    if m:
        return m.group(1).lower(), _num(m.group(2))
    return None, _num(raw)


def _other_letter(letter):
    return next(c for c in 'xyn' if c != letter.lower())


# Answer forms (generators set problem['answer_form']; see generators/shared/answer_checkers.py).
FORM_QUESTION_WORDS = {
    'expanded': re.compile(r'expand|simplif', re.I),
    'factorised': re.compile(r'factoris', re.I),
    'simplest_surd': re.compile(r'simplif|simplest|form k', re.I),
    'simplified': re.compile(r'simplif', re.I),
    'probability': re.compile(r'\bP\((?!\s*-?\d+\s*,)|probability', re.I),
}


def _smallest_prime_factor(n):
    n = abs(int(n))
    for p in range(2, int(n ** 0.5) + 1):
        if n % p == 0:
            return p
    return n if n > 1 else None


def wrong_form_entries(at, raw, form, question):
    """[(typed, wrong_form kind)]: entries equal in value to the key but not in the form the question asks for.

    Each must be refused with the form message (and, with no form requested, be accepted as equal).
    """
    raw, q = str(raw), str(question)
    out = []
    if form == 'expanded' and at == 'algebraic':
        product = re.search(r'(?:\([^()]+\)){2,}', q)       # brackets side by side, as the question prints them
        if product:
            out.append((re.sub(r'\s+', '', product.group(0)), 'unexpanded'))
        tail = re.search(r'\+ (\d+)$', raw)
        if tail and int(tail.group(1)) >= 2:
            c = int(tail.group(1))
            out.append((f'{raw[:tail.start()]}+ {c - 1} + 1', 'uncollected'))
    elif form == 'factorised' and at == 'algebraic':
        flat = re.search(r':\s*(.+)$', q)
        if flat:
            out.append((flat.group(1).strip(), 'unfactorised'))
        m = re.fullmatch(r'(\d+)\((\d+)x \+ (\d+)\)', raw)
        if m:
            n, a, b = (int(g) for g in m.groups())
            p = _smallest_prime_factor(n)
            if p and p < n:
                out.append((f'{p}({a * n // p}x + {b * n // p})', 'partly_factorised'))
    elif form == 'simplified' and at == 'algebraic':
        fraction = re.search(r'\(([^()]+)\)/\(([^()]+)\)', q)   # the question's own fraction, as printed
        if fraction:
            out.append((re.sub(r'\s+', '', fraction.group(0)), 'not_simplified'))
    elif form == 'simplest_surd':
        if at == 'surd':
            k, r = (int(x) for x in raw.split('|')) if '|' in raw else (1, int(raw))
            if k > 1:
                out.append((f'√{k * k * r}', 'surd_not_simplest'))
                p = _smallest_prime_factor(k)
                if p:
                    out.append((f'{k // p}√{p * p * r}', 'surd_not_simplest'))
        elif at == 'algebraic_fraction' and re.fullmatch(r'-?\d+\|\d+\|\d+', raw):
            c, r, d = (int(x) for x in raw.split('|'))
            out.append((f'{2 * c}√{r}|{2 * d}', 'fraction_not_simplest'))
    return out


def canonical(at, raw):
    """The plainest way to type the keyed answer."""
    raw = str(raw)
    if at == 'number_fields' and '\x1e' in raw and 'pick|' in raw:
        # a pick field is answered with just the chosen ids ('c1|c3'); the key spells out how many to pick
        return '\x1e'.join('|'.join(part.split('|')[2:]) if part.startswith('pick|') else part
                           for part in raw.split('\x1e'))
    if at == 'linear_equation' and re.fullmatch(r'-?[\d/.]+\|-?[\d/.]+', raw):
        m, c = raw.split('|')
        return _linear_text(_num(m), _num(c))
    if at == 'completed_square' and '|' in raw and raw.split('|')[0].lower() in ('plus', 'minus', 'scaled', 'expand'):
        return '|'.join(raw.split('|')[1:])
    if at == 'algebraic' and _surd_binomial_parts(raw):
        c, b, r, s = _surd_binomial_parts(raw)
        return f'{c}{s}{_surd_term(b, r)}'
    if at == 'algebraic_fraction':
        nd = _frac_numerator_denominator(raw)
        return f'{nd[0]}|{nd[1]}' if nd else raw
    if at == 'number_estimate' and '~' in raw:
        return raw.split('~')[0]
    if at == 'surd':
        if '|' in raw:
            k, r = raw.split('|')
            return f'{k}√{r}' if k != '1' else f'√{r}'
        return f'√{raw}'
    if at == 'pi_multiple':
        return raw + 'π'
    return raw


def accepted_forms(at, raw, question=''):
    """Extra generous spellings of the key. Each should be marked correct.

    ``question`` is the plain question text: an unsimplified fraction is generous only when the question
    does not ask for the simplest form, and an exact decimal only when it does not ask for a fraction.
    """
    raw = str(raw)
    q = str(question).lower()
    out = []
    if at == 'number':
        v = _num(raw)
        if v is None:
            return out
        if not _terminating(v):
            return [f' {raw} ']
        s = _fmt(v)
        out.append(f' {s} ')
        if v < 0:
            out.append(s.replace('-', '−'))
        if v.denominator == 1:
            out.append(f'{s}.0')
            out.append(f'{s}.00')
            if abs(v) >= 1000:
                out.append(f'{abs(v.numerator):,}'.join(['-' if v < 0 else '', '']))
        elif _terminating(v) and '.' in s and len(s.split('.')[-1]) <= 2:
            out.append(s + '0')
    elif at == 'fraction':
        if '/' in raw:
            a, b = raw.split('/')
            out.append(f'{a} / {b}')
            out.append(f' {raw} ')
            v = _num(raw)
            if v is not None and 'simplest' not in q and 'simplify' not in q:
                out.append(f'{2 * int(a)}/{2 * int(b)}')
            if v is not None and _terminating(v) and 'fraction' not in q:
                out.append(_fmt(v))
    elif at == 'bearing':
        v = int(raw)
        out.append(str(v))
        out.append(f'{v:03d}')
        out.append(f'{v:03d}°')
    elif at == 'keyword':
        out.append(raw.upper())
        out.append(f' {raw} ')
    elif at == 'linear' and _linear_parts(raw)[1] is not None:
        letter, val = _linear_parts(raw)
        shown = _fmt(val)
        if letter:                      # the key names its letter: that letter, or none, is accepted
            out += [f'{letter}={shown}', f'{letter} = {shown}', f'{letter.upper()}={shown}', shown, f' {shown} ']
        else:
            out += [f'x={raw}', f'x = {raw}', f' {raw} ']
    elif at == 'linear_equation':
        m = re.fullmatch(r'(-?[\d/.]+)\|(-?[\d/.]+)', raw)
        if m:
            mm, cc = _num(m.group(1)), _num(m.group(2))
            base = _linear_text(mm, cc)
            out.append(base.replace('=', ' = ').replace('+', ' + ').replace('-', ' - ').replace('=  - ', '= -').replace('  ', ' '))
            out.append(base.replace('-', '−'))
            if mm not in (0, 1, -1):
                out.append(base.replace('x', '*x', 1))           # explicit multiplication, y=-2*x-7
            if mm != 0 and cc != 0:
                xs = '' if abs(mm) == 1 and mm > 0 else ('-' if mm == -1 else _fmt(mm))
                out.append(f'y={_fmt(cc)}{"+" if mm > 0 else "-"}{_fmt(abs(mm)) if abs(mm) != 1 else ""}x')
    elif at == 'quadratic_roots':
        parts = [x for x in raw.split(',') if x.strip()]
        if len(parts) == 2 and parts[0].strip() != parts[1].strip():
            out += [f'{parts[1]},{parts[0]}', f'{parts[0]}, {parts[1]}', f'x={parts[0]} or x={parts[1]}']
    elif at == 'completed_square':
        if raw.split('|')[0].lower() in ('plus', 'minus', 'scaled', 'expand'):
            out.append(raw)
    elif at == 'algebraic':
        if _surd_binomial_parts(raw):
            c, b, r, s = _surd_binomial_parts(raw)
            out.append(f'{c} {s} {_surd_term(b, r)}')
            if s == '+':
                out.append(f'{_surd_term(b, r)}+{c}')
            else:
                out.append(f'-{_surd_term(b, r)} + {c}' if not str(c).startswith('-') else f'-{_surd_term(b, r)}{c}')
            out.append(f'{c}{s}{int(b)}*√{r}' if int(b) != 1 else f'{c}{s}√{r}')
        else:
            body = raw
            out.append(body.replace('**', '^').replace(' ', ''))
            out.append(re.sub(r'(?<=\d)\*(?=[a-z])', '', body.replace('**', '^')))
            out.append(body.replace('**2', '²').replace('**3', '³').replace(' ', ''))
            if '=' not in body and '(' not in body and '/' not in body:
                terms = re.findall(r'[+-]?[^+-]+', body.replace(' ', ''))
                if len(terms) >= 2:
                    rev = [t.lstrip('+') for t in reversed(terms)]
                    first = rev[0] if not rev[0].startswith('-') else rev[0]
                    out.append('+'.join(rev).replace('+-', '-'))
            if '=' in body:
                out.append(body.split('=', 1)[1])
    elif at == 'surd':
        c = canonical(at, raw)
        out += [f' {c} ', c.replace('√', ' √', 1)]
    elif at == 'algebraic_fraction':
        c = canonical(at, raw)
        out.append(f' {c} ')
    elif at == 'number_estimate' and '~' in raw:
        v, tol = (_num(x) for x in raw.split('~'))
        if v is not None and tol is not None:
            out += [_fmt(v + tol), _fmt(v - tol), _fmt(v + tol / 2)]
    elif at == 'number_list':
        out.append(', '.join(x.strip() for x in raw.split(',')))
    elif at in ('linear_inequality', 'compound_inequality', 'number_line'):
        parts = raw.split('|')
        v = _num(parts[2])
        if v is not None and v.denominator == 1:
            parts[2] = f'{v.numerator}.0'
            out.append('|'.join(parts))
    elif at == 'coordinate_pairs':
        p = raw.split('|')
        if len(p) == 4:
            out += [f'({p[0]},{p[1]})|({p[2]},{p[3]})', f'({p[2]},{p[3]})|({p[0]},{p[1]})']
    if at in ('fraction', 'number'):
        v = _num(raw)
        vulgar = {Fraction(1, 2): '½', Fraction(1, 4): '¼', Fraction(3, 4): '¾', Fraction(1, 3): '⅓', Fraction(2, 3): '⅔'}
        if v is not None and v > 0 and (v - int(v)) in vulgar:      # the single-character fraction a pupil can type
            out.append((str(int(v)) if int(v) else '') + vulgar[v - int(v)])
    if at in ('fraction', 'number') and FORM_QUESTION_WORDS['probability'].search(q):
        v = _num(raw)
        if v is not None and 0 <= v <= 1:       # "Find P(...)": answer_form 'probability' also takes a percentage
            if _terminating(v * 100):
                out += [f'{_fmt(v * 100)}%', f'{_fmt(v * 100)} %']
            if 0 < v < 1 and _terminating(v):
                out.append(_fmt(v).lstrip('0'))              # .375
    return list(dict.fromkeys(f for f in out if f != raw and f != canonical(at, raw)))


def rejected_forms(at, raw):
    """Plainly wrong entries for the key. Each should be marked incorrect."""
    raw = str(raw)
    out = []
    if at == 'number':
        v = _num(raw)
        if v is not None:
            for w in (v + 1, v * 2 + 3, v - Fraction(1, 2)):
                out.append(_fmt(w))
            if v != 0:
                out.append(_fmt(-v))
    elif at == 'number_fields':
        sep = SEP if SEP in raw else '|'
        parts = raw.split(sep)
        v = _num(parts[0])
        if v is not None:
            out.append(sep.join([_fmt(v + 1)] + parts[1:]))
    elif at in ('standard_form', 'power') and '|' in raw:
        a, n = raw.split('|')
        out.append(f'{a}|{int(n) + 1}')
    elif at == 'bearing':
        v = int(raw)
        out.append(f'{(v + 10) % 360:03d}')
        out.append(f'{(v + 180) % 360:03d}')
    elif at == 'fraction' and '/' in raw:
        a, b = (int(x) for x in raw.split('/'))
        out.append(f'{a + 1}/{b}')
        out.append(f'{b}/{a}' if a != b else f'{a}/{b + 1}')
    elif at == 'linear':
        letter, v = _linear_parts(raw)
        if v is not None:
            out += [_fmt(v + 1), _fmt(-v) if v != 0 else '1', f'{letter or "x"}={_fmt(v + 2)}']
            if letter:                  # the right value under another letter is refused, with its own message
                out.append(f'{_other_letter(letter)}={_fmt(v)}')
    elif at == 'linear_equation':
        m = re.fullmatch(r'(-?[\d/.]+)\|(-?[\d/.]+)', raw)
        if m:
            mm, cc = _num(m.group(1)), _num(m.group(2))
            out += [_linear_text(mm + 1, cc), _linear_text(mm, cc + 1), _linear_text(-mm if mm else 1, cc)]
            if cc != 0:
                out.append(_linear_text(mm, -cc))
    elif at == 'quadratic_roots':
        parts = [x.strip() for x in raw.split(',') if x.strip()]
        vs = [_num(x) for x in parts]
        if len(parts) == 2 and None not in vs:
            out += [parts[0], f'{_fmt(vs[0] + 1)},{parts[1]}', f'{_fmt(-vs[0])},{_fmt(-vs[1])}' if sorted(vs) != sorted(-v for v in vs) else '1,2']
    elif at == 'completed_square':
        nums = raw.split('|')
        if nums[0].lower() in ('plus', 'minus', 'scaled', 'expand'):
            nums = nums[1:]
        if nums and all(_num(x) is not None for x in nums):
            for i in range(len(nums)):
                bumped = list(nums)
                bumped[i] = _fmt(_num(nums[i]) + 1)
                out.append('|'.join(bumped))
            first = list(nums)
            first[0] = _fmt(-_num(nums[0])) if _num(nums[0]) != 0 else '1'
            out.append('|'.join(first))
    elif at == 'algebraic':
        if _surd_binomial_parts(raw):
            c, b, r, s = _surd_binomial_parts(raw)
            out += [f'{int(c) + 1}{s}{_surd_term(b, r)}', f'{c}{s}{_surd_term(int(b) + 1, r)}',
                    f'{c}{"-" if s == "+" else "+"}{_surd_term(b, r)}', f'{c}{s}{_surd_term(b, int(r) + 1)}']
            if int(c) != 0:      # the negative of the key with the surd written first (once accepted by mistake)
                out.append(f'{"" if s == "-" else "-"}{_surd_term(b, r)}{"+" if int(c) < 0 else "-"}{abs(int(c))}')
        else:
            out.append(_perturb_expression(raw))
    elif at == 'surd':
        c = canonical(at, raw)
        k, r = (raw.split('|') + [None])[:2] if '|' in raw else ('1', raw)
        out += [f'{_surd_term(int(k) + 1, r)}', _surd_term(k, int(r) + 1), str(int(k) * int(r))]
    elif at == 'algebraic_fraction':
        out += _wrong_fractions(raw)
    elif at == 'number_estimate' and '~' in raw:
        v, tol = (_num(x) for x in raw.split('~'))
        if v is not None and tol is not None:
            out += [_fmt(v + tol + 1), _fmt(v - tol - 1)]
    elif at == 'number_list':
        parts = [x.strip() for x in raw.split(',') if x.strip()]
        if len(parts) >= 2:
            out += [','.join(reversed(parts)) if parts != list(reversed(parts)) else '', ','.join(parts[:-1]),
                    ','.join(parts[:-1] + [_fmt(_num(parts[-1]) + 1)]) if _num(parts[-1]) is not None else '']
    elif at in ('linear_inequality', 'compound_inequality', 'number_line'):
        parts = raw.split('|')
        flip = {'<': '>', '>': '<', '<=': '>=', '>=': '<='}
        if len(parts) >= 3 and _num(parts[2]) is not None:
            a = list(parts)
            a[1] = flip.get(a[1], a[1])
            out.append('|'.join(a))
            b = list(parts)
            b[2] = _fmt(_num(parts[2]) + 1)
            out.append('|'.join(b))
            if len(parts) == 5 and _num(parts[4]) is not None:
                c = list(parts)
                c[4] = _fmt(_num(parts[4]) + 1)
                out.append('|'.join(c))
    elif at == 'coordinate_pairs':
        p = raw.split('|')
        if len(p) == 4 and _num(p[3]) is not None:
            out += ['|'.join(p[:3] + [_fmt(_num(p[3]) + 1)]), '|'.join([p[1], p[0], p[3], p[2]])]
    elif at == 'number_pair':
        p = raw.split('|')
        if len(p) == 2 and _num(p[0]) is not None:
            out.append(f'{_fmt(_num(p[0]) + 1)}|{p[1]}')
    elif at == 'keyword' and raw.lower() in ('yes', 'no'):
        out.append('no' if raw.lower() == 'yes' else 'yes')
    elif at == 'formula_fraction':
        p = raw.split('|')
        if len(p) == 2:
            out += [f'{p[1]}|{p[0]}'] if p[0] != p[1] else []
    return [o for o in dict.fromkeys(out) if o and o != raw]


def _perturb_expression(raw):
    """A plainly different expression: bump the last number, else flip the first sign, else add 1."""
    rhs_at = raw.find('=') + 1
    head, body = raw[:rhs_at], raw[rhs_at:]
    nums = list(re.finditer(r'\d+', body))
    if nums:
        m = nums[-1]
        return head + body[:m.start()] + str(int(m.group()) + 1) + body[m.end():]
    i = max(body.rfind('+'), body.rfind('-'))
    if i > 0:
        return head + body[:i] + ('-' if body[i] == '+' else '+') + body[i + 1:]
    return head + body + '+1'


def _wrong_fractions(raw):
    parts = raw.split('|')
    nd = _frac_numerator_denominator(raw)
    out = []
    if parts[0] == 'b' and len(parts) == 7:
        out.append('|'.join(parts[:6] + ['+' if parts[6] == '-' else '-']))
        out.append('|'.join(parts[:5] + [str(int(parts[5]) + 1)] + parts[6:]))
    elif parts[0] == 'd' and len(parts) == 4:
        out.append('|'.join(['d', parts[1], str(int(parts[2]) + 1), parts[3]]))
    elif parts[0] == 'e' and len(parts) == 5:
        out.append('|'.join(['e', str(int(parts[1]) + 1)] + parts[2:]))
    elif len(parts) == 3 and all(re.fullmatch(r'-?\d+', x) for x in parts):
        out.append('|'.join([str(int(parts[0]) + 1), parts[1], parts[2]]))
        out.append('|'.join([parts[0], parts[1], str(int(parts[2]) + 1)]))
    elif len(parts) == 2:
        out.append(f'{parts[1]}|{parts[0]}' if parts[0] != parts[1] else raw + '+1')
    # the rejected entry is typed, so convert the wrong key to its typed form
    typed = []
    for w in out:
        nd = _frac_numerator_denominator(w)
        if nd:
            typed.append(f'{nd[0]}|{nd[1]}')
    return typed


def tampered_keys(at, raw):
    """Wrong keys in the key's own format (the negative control: a solver must refuse every one of them)."""
    raw = str(raw)
    out = []
    if at == 'linear':
        letter, v = _linear_parts(raw)
        if v is not None:
            out = [f'{letter}={_fmt(v + 1)}' if letter else _fmt(v + 1),
                   f'{letter}={_fmt(-v)}' if letter and v != 0 else (_fmt(-v) if v != 0 else '1')]
    elif at in ('number', 'number_fields', 'bearing', 'fraction', 'standard_form', 'power',
              'linear_inequality', 'compound_inequality', 'number_line', 'coordinate_pairs',
              'number_pair', 'keyword', 'number_list', 'quadratic_roots'):
        out = rejected_forms(at, raw)
    elif at == 'linear_equation':
        m = re.fullmatch(r'(-?[\d/.]+)\|(-?[\d/.]+)', raw)
        if m:
            mm, cc = _num(m.group(1)), _num(m.group(2))
            out = [f'{_fmt(mm + 1)}|{_fmt(cc)}', f'{_fmt(mm)}|{_fmt(cc + 1)}']
    elif at == 'completed_square':
        parts = raw.split('|')
        kind, nums = parts[0], parts[1:]
        if all(_num(x) is not None for x in nums):
            for i in range(len(nums)):
                bumped = list(nums)
                bumped[i] = _fmt(_num(nums[i]) + 1)
                out.append('|'.join([kind] + bumped))
    elif at == 'algebraic':
        if _surd_binomial_parts(raw):
            c, b, r, s = _surd_binomial_parts(raw)
            out = [f'{int(c) + 1}|{b}|{r}|{s}', f'{c}|{int(b) + 1}|{r}|{s}']
        else:
            out = [_perturb_expression(raw)]
    elif at == 'surd':
        k, r = raw.split('|') if '|' in raw else ('1', raw)
        out = [f'{int(k) + 1}|{r}']
    elif at == 'algebraic_fraction':
        parts = raw.split('|')
        if parts[0] == 'b' and len(parts) == 7:
            out = ['|'.join(parts[:6] + ['+' if parts[6] == '-' else '-']), '|'.join(parts[:5] + [str(int(parts[5]) + 1)] + parts[6:])]
        elif parts[0] == 'd' and len(parts) == 4:
            out = ['|'.join(['d', parts[1], str(int(parts[2]) + 1), parts[3]])]
        elif parts[0] == 'e' and len(parts) == 5:
            out = ['|'.join(['e', str(int(parts[1]) + 1)] + parts[2:])]
        elif len(parts) == 3 and all(re.fullmatch(r'-?\d+', x) for x in parts):
            out = ['|'.join([str(int(parts[0]) + 1), parts[1], parts[2]])]
        elif len(parts) == 2:
            out = [f'{parts[1]}|{parts[0]}' if parts[0] != parts[1] else raw + '+1']
    elif at == 'number_estimate' and '~' in raw:
        v, tol = (_num(x) for x in raw.split('~'))
        if v is not None and tol is not None:
            out = [f'{_fmt(v + 2 * tol + 1)}~{_fmt(tol)}']
    return [o for o in dict.fromkeys(out) if o and o != raw]
