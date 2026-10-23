"""Safe reader for the algebra shown in questions, options and keys (no eval, exec or sympify).

``tex_to_text`` flattens the LaTeX / HTML a generator produced into a plain maths string; ``parse`` builds a
small syntax tree from it with a hand-written recursive-descent parser; ``to_sympy`` turns the tree into a
sympy expression.  Everything is an allowlist: numbers, single-letter symbols, ``+ - * / ^``, brackets,
``sqrt`` and pi.  Anything else raises ``Cannot`` (a loud "could not read", never a silent skip).

Caps (plan section 4, Security): input of at most 300 characters, exponents of at most 10, nested powers
whose exponents multiply to at most 100 (so ``((9^10)^10)^10`` cannot build a huge number), bracket depth of
at most 40; anything the arithmetic still cannot handle becomes ``Cannot``.
"""
from __future__ import annotations

import html
import re
from fractions import Fraction

import sympy

from .core import Cannot

MAX_LEN = 300
MAX_EXP = 10
MAX_POW_PRODUCT = MAX_EXP ** 2
MAX_DEPTH = 40

_GREEK = {'rho': 'ρ', 'theta': 'θ', 'Delta': 'Δ', 'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'lambda': 'λ',
          'mu': 'μ', 'omega': 'ω', 'phi': 'φ', 'sigma': 'σ', 'delta': 'δ', 'epsilon': 'ε', 'pi': 'π'}
_SUPER = {'²': '^2', '³': '^3', '⁴': '^4', '¹': '^1'}


def _group(s, i):
    """Return (content, index after the closing brace) for the ``{`` at s[i]."""
    if i >= len(s) or s[i] != '{':
        raise Cannot(f'expected a brace group in {s!r}')
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise Cannot(f'unbalanced braces in {s!r}')


def _skip_ws(s, i):
    while i < len(s) and s[i] == ' ':
        i += 1
    return i


def tex_to_text(raw):
    """LaTeX / HTML to a plain maths string (fractions become (a)/(b), roots become sqrt(a))."""
    s = html.unescape(str(raw))
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'</?[A-Za-z][A-Za-z0-9]*(?:\s[^>]*)?/?>', ' ', s)
    s = s.replace('\u00a0', ' ')
    s = s.replace('\\(', ' ').replace('\\)', ' ').replace('\\[', ' ').replace('\\]', ' ')
    s = re.sub(r'\\(?:displaystyle|textstyle|boxed)\b', ' ', s)
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch != '\\':
            out.append(ch)
            i += 1
            continue
        m = re.match(r'\\([A-Za-z]+)', s[i:])
        if not m:                                   # \, \; \  \! \% etc.
            nxt = s[i + 1:i + 2]
            out.append('%' if nxt == '%' else ' ')
            i += 2
            continue
        name = m.group(1)
        i += 1 + len(name)
        if name in ('dfrac', 'frac', 'tfrac'):
            i = _skip_ws(s, i)
            a, i = _group(s, i)
            i = _skip_ws(s, i)
            b, i = _group(s, i)
            out.append(f'(({tex_to_text(a)})/({tex_to_text(b)}))')
        elif name == 'sqrt':
            i = _skip_ws(s, i)
            if i < len(s) and s[i] == '[':
                raise Cannot('nth roots are not supported')
            a, i = _group(s, i)
            out.append(f'sqrt({tex_to_text(a)})')
        elif name in ('text', 'mathrm', 'textbf', 'mathbf', 'operatorname'):
            i = _skip_ws(s, i)
            a, i = _group(s, i)
            out.append(f' {a} ')
        elif name in ('left', 'right'):
            pass
        elif name == 'times' or name == 'cdot':
            out.append('*')
        elif name == 'div':
            out.append('/')
        elif name == 'pm':
            out.append('±')
        elif name in ('leq', 'le', 'leqslant'):
            out.append('<=')
        elif name in ('geq', 'ge', 'geqslant'):
            out.append('>=')
        elif name == 'lt':
            out.append('<')
        elif name == 'gt':
            out.append('>')
        elif name in ('neq', 'ne'):
            out.append('!=')
        elif name in ('ldots', 'dots', 'cdots'):
            out.append('...')
        elif name in ('square', 'Box', 'boxed'):
            out.append('□')
        elif name in _GREEK:
            out.append(_GREEK[name])
        elif name in ('circ', 'degree'):
            out.append('°')
        elif name == 'infty':
            out.append('inf')
        elif name == 'sum':
            out.append('sum')
        elif name in ('quad', 'qquad'):
            out.append(' ')
        elif name in ('equiv',):
            out.append('==')
        elif name in ('overline',):
            i = _skip_ws(s, i)
            a, i = _group(s, i)
            out.append(f'[{a}]')
        else:
            raise Cannot(f'unsupported LaTeX command \\{name}')
    t = ''.join(out)
    for k, v in _SUPER.items():
        t = t.replace(k, v)
    t = (t.replace('−', '-').replace('–', '-').replace('×', '*').replace('÷', '/').replace('·', '*')
         .replace('≤', '<=').replace('≥', '>=').replace('≠', '!=').replace('√', 'sqrt').replace('\u2009', ' '))
    t = re.sub(r'\^\s*\{([^{}]*)\}', r'^(\1)', t)
    t = re.sub(r'_\s*\{([^{}]*)\}', r'_\1', t)
    t = t.replace('{', '(').replace('}', ')')
    return re.sub(r'\s+', ' ', t).strip()


def math_segments(raw):
    """The ``\\( ... \\)`` segments of a question as plain maths strings (in order)."""
    segs = re.findall(r'\\\((.*?)\\\)', str(raw), flags=re.S)
    return [tex_to_text(x) for x in segs]


# ───────────────────────────── relations ─────────────────────────────

_REL = re.compile(r'(<=|>=|!=|==|<|>|=)')


def split_relations(text):
    """Split ``a < b <= c`` at top-level relation symbols. Returns (parts, ops)."""
    parts, ops, depth, last = [], [], 0, 0
    i = 0
    while i < len(text):
        c = text[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        elif depth == 0:
            m = _REL.match(text, i)
            if m:
                parts.append(text[last:i].strip())
                ops.append(m.group(1))
                i = m.end()
                last = i
                continue
        i += 1
    parts.append(text[last:].strip())
    return parts, ops


# ───────────────────────────── tokenizer / parser ─────────────────────────────

_TOKEN = re.compile(r'\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<sqrt>sqrt|√)|(?P<pi>pi|π)|(?P<sym>[A-Za-zρθΔαβγλμωφσδε](?:_\d+)?)'
                    r'|(?P<op>\*\*|[-+*/^()±]))')


def tokenize(text):
    s = str(text).strip()
    if len(s) > MAX_LEN:
        raise Cannot(f'expression longer than {MAX_LEN} characters')
    toks, i = [], 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        # a word such as "sqrt" or "pi" must be read before single letters
        m = _TOKEN.match(s, i)
        if not m:
            raise Cannot(f'cannot read {s[i:i + 12]!r} in {s!r}')
        if m.group('sqrt'):
            toks.append(('sqrt', 'sqrt'))
        elif m.group('pi'):
            toks.append(('pi', 'pi'))
        elif m.group('num'):
            toks.append(('num', m.group('num')))
        elif m.group('sym'):
            toks.append(('sym', m.group('sym')))
        else:
            op = m.group('op')
            toks.append(('op', '^' if op == '**' else op))
        i = m.end()
    return toks


class _Parser:
    def __init__(self, toks, funcs):
        self.t = toks
        self.i = 0
        self.funcs = funcs

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else (None, None)

    def eat(self, kind=None, val=None):
        tok = self.peek()
        if tok[0] is None or (kind and tok[0] != kind) or (val and tok[1] != val):
            raise Cannot(f'unexpected {tok} (wanted {kind} {val})')
        self.i += 1
        return tok

    def expr(self):
        node = self.term()
        while self.peek() in (('op', '+'), ('op', '-'), ('op', '±')):
            op = self.eat()[1]
            rhs = self.term()
            node = ('add', node, rhs) if op == '+' else ('sub', node, rhs) if op == '-' else ('pm', node, rhs)
        return node

    def term(self):
        node = self.unary()
        while True:
            tok = self.peek()
            if tok == ('op', '*'):
                self.eat()
                node = ('mul', node, self.unary())
            elif tok == ('op', '/'):
                self.eat()
                node = ('div', node, self.unary())
            elif tok[0] in ('sym', 'pi', 'sqrt') or tok == ('op', '('):
                node = ('mul', node, self.power())          # implicit multiplication
            elif tok[0] == 'num' and node[0] in ('num',) and False:
                break
            else:
                return node

    def unary(self):
        tok = self.peek()
        if tok == ('op', '-'):
            self.eat()
            return ('neg', self.unary())
        if tok == ('op', '+'):
            self.eat()
            return self.unary()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == ('op', '^'):
            self.eat()
            tok = self.peek()
            if tok == ('op', '-'):
                self.eat()
                exp = ('neg', self.atom())
            else:
                exp = self.atom()
            return ('pow', base, exp)
        return base

    def atom(self):
        tok = self.eat()
        kind, val = tok
        if kind == 'num':
            return ('num', Fraction(val))
        if kind == 'pi':
            return ('pi',)
        if kind == 'sym':
            if val in self.funcs and self.peek() == ('op', '('):
                self.eat()
                arg = self.expr()
                self.eat('op', ')')
                return ('call', val, arg)
            return ('sym', val)
        if kind == 'sqrt':
            if self.peek() == ('op', '('):
                self.eat()
                arg = self.expr()
                self.eat('op', ')')
            else:
                arg = self.atom()
            return ('sqrt', arg)
        if tok == ('op', '('):
            node = self.expr()
            self.eat('op', ')')
            return ('paren', node)
        raise Cannot(f'unexpected token {tok}')


def _pow_product(node):
    """Largest product of literal exponents along any chain of nested powers in the tree."""
    best = 1
    stack = [(node, 1)]
    while stack:
        n, acc = stack.pop()
        if n[0] == 'pow':
            e = n[2]
            while e[0] in ('paren', 'neg'):
                e = e[1]
            mag = abs(e[1]) if e[0] == 'num' else MAX_EXP     # to_sympy caps any other exponent at MAX_EXP
            acc = acc * max(mag, 1)
            best = max(best, acc)
            stack.append((n[1], acc))
            stack.append((n[2], 1))
        elif n[0] == 'call':
            # a function body may hold a power of up to MAX_EXP, so each nested call counts as one
            acc = acc * MAX_EXP
            best = max(best, acc)
            stack.append((n[2], acc))
        else:
            stack.extend((c, acc) for c in n[1:] if isinstance(c, tuple))
    return best


def parse(text, funcs=()):
    """Syntax tree of a maths string (raises Cannot). ``funcs`` names single-letter functions such as f, g."""
    toks = tokenize(text)
    if not toks:
        raise Cannot('empty expression')
    depth = 0
    for tok in toks:
        depth += tok == ('op', '(')
        depth -= tok == ('op', ')')
        if depth > MAX_DEPTH:
            raise Cannot(f'brackets nested deeper than {MAX_DEPTH}')
    p = _Parser(toks, set(funcs))
    node = p.expr()
    if p.i != len(toks):
        raise Cannot(f'unread tokens {toks[p.i:]} in {text!r}')
    if _pow_product(node) > MAX_POW_PRODUCT:
        raise Cannot(f'nested powers multiply beyond {MAX_POW_PRODUCT} in {text!r}')
    return node


def symbol(name):
    return sympy.Symbol(name)


def to_sympy(node, defs=None):
    """sympy expression for a syntax tree. ``defs`` maps function names to (parameter, tree)."""
    k = node[0]
    if k == 'num':
        return sympy.Rational(node[1].numerator, node[1].denominator)
    if k == 'pi':
        return sympy.pi
    if k == 'sym':
        return symbol(node[1])
    if k == 'paren':
        return to_sympy(node[1], defs)
    if k == 'neg':
        return -to_sympy(node[1], defs)
    if k == 'add':
        return to_sympy(node[1], defs) + to_sympy(node[2], defs)
    if k == 'sub':
        return to_sympy(node[1], defs) - to_sympy(node[2], defs)
    if k == 'pm':
        raise Cannot('plus-or-minus needs expand_pm')
    if k == 'mul':
        return to_sympy(node[1], defs) * to_sympy(node[2], defs)
    if k == 'div':
        d = to_sympy(node[2], defs)
        if d == 0:
            raise Cannot('division by zero in expression')
        return to_sympy(node[1], defs) / d
    if k == 'sqrt':
        return sympy.sqrt(to_sympy(node[1], defs))
    if k == 'pow':
        base = to_sympy(node[1], defs)
        exp = to_sympy(node[2], defs)
        if exp.is_number:
            if abs(exp) > MAX_EXP:
                raise Cannot(f'exponent {exp} exceeds {MAX_EXP}')
        else:
            raise Cannot('symbolic exponents are not supported')
        return base ** exp
    if k == 'call':
        if not defs or node[1] not in defs:
            raise Cannot(f'function {node[1]} is not defined')
        param, body = defs[node[1]]
        arg = to_sympy(node[2], defs)
        return to_sympy(body, defs).subs(symbol(param), arg)
    raise Cannot(f'unknown node {k}')


def expr(text, funcs=(), defs=None):
    """Parse ``text`` straight to a sympy expression."""
    tree = parse(text, funcs)
    try:
        return to_sympy(tree, defs)
    except (ValueError, OverflowError, RecursionError, MemoryError) as e:
        raise Cannot(f'cannot evaluate {text!r}: {type(e).__name__}') from None


def expand_pm(text):
    """Both readings of a ± expression."""
    return [text.replace('±', '+'), text.replace('±', '-')] if '±' in text else [text]


# ───────────────────────────── structure of the written form ─────────────────────────────

def top_factors(node):
    """Multiplicative factors at the top level of a tree (a bracket is one factor; a sum is one factor)."""
    if node[0] == 'mul':
        return top_factors(node[1]) + top_factors(node[2])
    if node[0] == 'paren':
        inner = node[1]
        return top_factors(inner) if inner[0] == 'mul' else [node]
    if node[0] == 'neg':
        return [('num', Fraction(-1))] + top_factors(node[1])
    return [node]


def strip_paren(node):
    while node[0] == 'paren':
        node = node[1]
    return node


def is_sum(node):
    node = strip_paren(node)
    return node[0] in ('add', 'sub')


def has_bracketed_sum(node):
    """True when a sum sits inside brackets that are multiplied (a product such as (x + 1)(2x + 2) or 3(x + 2))."""
    node = strip_paren(node)
    if node[0] == 'mul':
        facs = top_factors(node)
        return any(f[0] == 'paren' and is_sum(f) for f in facs)
    if node[0] in ('add', 'sub'):
        return has_bracketed_sum(node[1]) or has_bracketed_sum(node[2])
    return False


def is_product_form(node):
    """The written form is a single product with at least one factor that is a bracketed sum (factorised form)."""
    node = strip_paren(node)
    if node[0] in ('neg',):
        return is_product_form(node[1])
    if node[0] != 'mul':
        return False
    return any(f[0] == 'paren' and is_sum(f) for f in top_factors(node))


# ───────────────────────────── equality ─────────────────────────────

class _Det:
    """A tiny deterministic generator (a linear congruential sequence) for the sample points of ``equivalent``."""

    def __init__(self, seed):
        self.state = seed + 12345

    def randint(self, lo, hi):
        self.state = (self.state * 1103515245 + 12345) % 2147483648
        return lo + (self.state >> 8) % (hi - lo + 1)


def _points(symbols, n, rng):
    return [{s: sympy.Rational(rng.randint(-9, 9), rng.randint(1, 5)) for s in symbols} for _ in range(n)]


def _zero(d):
    """True when the sympy number ``d`` is zero (exact for rationals, to 1e-18 for radicals)."""
    if d == 0:
        return True
    if d.is_Rational:
        return False
    try:
        return abs(complex(sympy.N(d, 30))) < 1e-18
    except (TypeError, ValueError):
        return bool(sympy.simplify(d) == 0)


def equivalent(a, b, tries=4):
    """Exact-value equivalence of two sympy expressions (sample points first, simplify only if inconclusive)."""
    if a == b:
        return True
    syms = sorted((a.free_symbols | b.free_symbols), key=lambda s: s.name)
    if not syms:
        return _zero(a - b)
    rng = _Det(0)
    good = 0
    for pt in _points(syms, tries * 3, rng):
        try:
            va, vb = a.subs(pt), b.subs(pt)
        except Exception:
            continue
        if va.has(sympy.zoo, sympy.nan, sympy.oo, -sympy.oo) or vb.has(sympy.zoo, sympy.nan, sympy.oo, -sympy.oo):
            continue
        if not _zero(va - vb):
            return False
        good += 1
        if good >= tries:
            break
    if good < 3:
        try:
            return bool(sympy.simplify(a - b) == 0)
        except Exception:
            return False
    return True


def lowered(text):
    """Lower-case a maths string (the app's checker lower-cases typed answers too)."""
    return str(text).lower()
