"""Smoke test for the hint ladder on the practice page (docs/GCSE_MATHS_HINTS.md, Phase 3). About 10 s.

What it pins:

* ``template``: the GCSE maths practice page renders Show answer locked (hidden, with a note that says how it opens),
  one ``aria-live`` hint area under the feedback line for typed questions, a locked drawer with no ladder for
  multiple choice, no lock for other subjects, no drawer at all in Quick Test, and no change to the other drawer pages.
* ``route``: ``POST /api/v1/problems/check`` builds the ladder only when asked (``hint_ladder`` true), only for a GCSE
  maths problem bound to the session, only after a wrong answer the checker could read, never for Quick Test, and
  stores nothing.
* ``ladder``: on every practice slot rung 1 and rung 2 never show the key (an independent number scan), rung 2 is the
  first step of the stored solution that does not show it, and hand-worked cases for the helpers.
* ``graded``: set work and lesson-quiz results carry the generic message only for a graded wrong answer, nothing before.
* ``client``: byte caps (site.js with its own cap, practice.css, core CSS), cache pins, no em dash in the answer strings
  of site.js, the pieces of the ladder script that make the pacing behave (static, since the browser check is by hand).

Not covered here: the real browser flow. That is checked by hand with Playwright (section 17 of the plan lists the
screenshots).
"""
from __future__ import annotations

import collections
import copy
import os
import re
import sys
import time
import warnings
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('PB_TESTING', '1')
os.environ.setdefault('PB_ALLOW_DEV_SECRET', '1')
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')

from generators.shared import misconceptions as M  # noqa: E402
from gcse_verify import harness  # noqa: E402

warnings.filterwarnings('ignore', category=SyntaxWarning)
START = time.time()
BUDGET_SECONDS = 20.0

# Byte ledger for Phase 3 (docs/GCSE_MATHS_HINTS.md section 17). site.js had no cap before; this is its first.
SITE_JS_BASE_BYTES = 207_046        # before Phase 3
SITE_JS_PHASE3_MAX_ADD = 2_500      # the plan's budget
SITE_JS_PHASE4_MAX_ADD = 900        # 2026-10-26: Phase 4 (MCQ distractor notes) budget, docs/GCSE_MATHS_HINTS.md section 19
SITE_JS_CARD_MAX_ADD = 1_250        # 2026-11-04: hint card and greyed Show answer (docs/GCSE_MATHS_HINTS.md, 'Hint card and Show answer change')
SITE_JS_NOTE_MAX_ADD = 800         # 2026-11-07: the wrong-answer note folded behind an "Add a note" toggle (docs/GCSE_MATHS_HINTS.md, 'Folded wrong-answer note')
SITE_JS_COACH_MAX_ADD = 300        # 2026-11-08: E10 phase 3 coach events (pb-answer-checked, pb-answer-unlocked, pb-hint-shown, pb-hint-bigger), +269 B
SITE_JS_MAX_BYTES = (SITE_JS_BASE_BYTES + SITE_JS_PHASE3_MAX_ADD + SITE_JS_PHASE4_MAX_ADD + SITE_JS_CARD_MAX_ADD
                     + SITE_JS_NOTE_MAX_ADD + SITE_JS_COACH_MAX_ADD)      # 212,796; raise only with a dated ledger line
PRACTICE_CSS_BASE_BYTES = 31_381
PRACTICE_CSS_PHASE3_MAX_ADD = 600
PRACTICE_CSS_CARD_MAX_ADD = 900     # 2026-11-04: hint card and locked Show answer styles (the old ladder lines went)
PRACTICE_CSS_NOTE_MAX_ADD = 900     # 2026-11-07: the "Add a note" toggle and the smaller note chips
CORE_CSS_CAP = 216_000              # as test_u8_a11y_smoke and test_zorp_charm_smoke
TOTAL_CSS_CAP = 274_400 # 2026-11-10: E11 Phase 1 RAISED 273_700 -> 274_400 (+700) for Skip all and the small-card link in the on-demand moments.css (tree 274,251). 2026-11-08: E10 phase 8 RAISED 268_900 -> 273_700 (+4_800) for the on-demand story.css (own cap 4_800 in test_story_chapters_smoke.py; tree 273,520). 2026-11-08: E10 phase 7 RAISED 265_300 -> 268_900 (+3_600) for the on-demand around.css (own cap 4_000 in test_zorp_around_smoke.py; tree 268,821). 2026-11-08: E10 phase 6b RAISED 262_500 -> 265_300 (+2_800) for the on-demand wardrobe.css (profile page only; own cap 2_800 in test_wardrobe_smoke.py; tree 264,949).  2026-11-08: E10 phase 5 added moments.css inside this cap (no raise; tree 260,077).  2026-11-08: E10 phase 4 +5_500 for badge-stage.css (on demand, own cap in test_badge_stage_smoke.py); was 256_000             # 2026-11-08: E10 +10_000 for stage.css (on demand, own cap in test_zorp_stage_smoke.py)  # 2026-11-08: E10 phase 6 RAISED 261_500 -> 262_500 (+1_000) for the on-demand tour.css (own cap 2_800 in test_zorp_tour_smoke.py; tree 262,304).
SERVICE_WORKER_CACHE = 'pb-v124'   # 2026-11-10: E11 Phase 1 bump (was pb-v123, Phase 0); 2026-11-10: E11 Phase 0 bump (was pb-v122, lesson-quiz spotlight); 2026-11-08: E10 phase 8 bump (was pb-v119, review fixes); 2026-11-08: E10 phase 6b bump (was pb-v116, phase 6); 2026-11-08: E10 phase 6 (the app tour) bumped the cache (was pb-v115, phase 5); 2026-11-08: E10 phase 5 (moments) bumped the cache (was pb-v114, phase 4 badges; pb-v113 phase 3); 2026-11-08: E10 review fixes bump (was pb-v118)

ISSUES = collections.defaultdict(list)
HDR = {'Accept': 'application/json'}


def issue(check, where, detail):
    ISSUES[check].append(f'{where}: {detail}')


def expect(check, where, cond, detail):
    if not cond:
        issue(check, where, detail)


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


# ─────────────────────────────────────────────────────────────────────────────
# Independent key scan (does not call M.reveals_key)
# ─────────────────────────────────────────────────────────────────────────────

# Whole-change review 2026-11-03 (F4, F9): the scan below is a token reader, not a copy of the module's regular
# expressions (the old scan shared all four of its blind spots: a spaced minus, the list exemption with signs dropped,
# a numerator|denominator key, and "-x" in a line). It reads the text as a stream of numbers, letters and symbols and
# gives each number its sign from the token before the minus.

_TOKEN = re.compile(r'(?P<num>\d+(?:\.\d+)?)|(?P<let>[a-zA-Z])|(?P<sym>\S)')
_SUPER_CHARS = '\u00b2\u00b3\u2070\u00b9\u2074\u2075\u2076\u2077\u2078\u2079'


def _normalise(text):
    t = str(text).replace('\u2212', '-').replace('\u2013', '-')
    for _ in range(3):      # LaTeX fractions as (a)/(b); wrappers and braces go
        t = re.sub(r'\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}', r'(\1)/(\2)', t)
    t = re.sub(r'\\(?:times|cdot)', '×', t).replace('\\pm', '±')
    t = re.sub(r'\\(?:left|right|boxed|displaystyle|text|mathrm)|\\[()\[\]]', ' ', t)
    t = re.sub(r'(?<=\d),(?=\d{3}(?!\d))', '', t)
    return t.replace('{', ' ').replace('}', ' ')


def _tokens(text):
    """[(kind, text, touches the token before)] with kind 'num', 'let', 'sym' or 'pow' (a superscript character)."""
    out, end = [], -1
    for m in _TOKEN.finditer(_normalise(text)):
        kind = m.lastgroup
        if kind == 'sym' and m.group() in _SUPER_CHARS:
            kind = 'pow'
        out.append((kind, m.group(), m.start() == end))
        end = m.end()
    return out


def _is(tok, kind, text=None):
    return tok is not None and tok[0] == kind and (text is None or tok[1] == text)


def _values(text, *, roots=False):
    """[(value with its sign, decimal places)] for each number in ``text``; a written fraction of two plain numbers
    (3/4, \\frac{3}{4}) is one number. A minus is the number's sign unless a plain number (not a power) stands before
    it. For roots a number written against a letter (2a, 5x) or as a power is not a value, and a factor (x + 4) gives
    the root -4."""
    toks = _tokens(text)

    def at(k):
        return toks[k] if 0 <= k < len(toks) else None
    # fractions: num / num, or (num)/(num) as an unwrapped \frac{num}{num}
    tops, bottoms = {}, set()
    for i, (kind, tok, _) in enumerate(toks):
        if kind != 'num':
            continue
        if _is(at(i + 1), 'sym', '/') and _is(at(i + 2), 'num'):
            tops[i] = i + 2
        elif _is(at(i - 1), 'sym', '(') and _is(at(i + 1), 'sym', ')') and _is(at(i + 2), 'sym', '/') \
                and _is(at(i + 3), 'sym', '(') and _is(at(i + 4), 'num') and _is(at(i + 5), 'sym', ')'):
            tops[i] = i + 4
    bottoms = set(tops.values())
    out = []
    for i, (kind, tok, _) in enumerate(toks):
        if kind != 'num' or i in bottoms:
            continue
        power = _is(at(i - 1), 'sym', '^')
        negative = False
        if _is(at(i - 1), 'sym', '-'):
            prev = at(i - 2)
            negative = prev is None or prev[0] != 'num' or _is(at(i - 3), 'sym', '^')
        if roots:
            if power or (_is(at(i + 1), 'let') and at(i + 1)[2]):
                continue
            if _is(at(i - 1), 'sym') and at(i - 1)[1] in '+-' and _is(at(i - 2), 'let') and _is(at(i - 3), 'sym', '(') \
                    and _is(at(i + 1), 'sym', ')'):
                out.append((Fraction(tok) * (1 if at(i - 1)[1] == '-' else -1), 0))      # (x + 4): the root -4
        value = Fraction(tok)
        places = len(tok.split('.')[1]) if '.' in tok else 0
        if i in tops:
            bottom = Fraction(toks[tops[i]][1])
            if not bottom:
                continue
            value, places = value / bottom, 0
        out.append((-value if negative else value, places))
    return out


def _gradient_terms(text):
    """+1 or -1 for each x with no number in front on the right of "y =" (a line's gradient)."""
    toks = _tokens(text)
    out, rhs = [], False
    for i, (kind, tok, _) in enumerate(toks):
        if kind == 'sym' and tok == '=' and i and toks[i - 1][:2] == ('let', 'y'):
            rhs = True
            continue
        if kind == 'sym' and tok in ',;:.=':
            rhs = False
        before = toks[i - 1] if i else None
        after = toks[i + 1] if i + 1 < len(toks) else None
        if rhs and kind == 'let' and tok == 'x' and not (before and before[0] in ('num', 'let') and toks[i][2]) \
                and not (after and after[0] in ('let', 'num', 'pow') and after[2]):
            out.append(Fraction(-1) if before and before[:2] == ('sym', '-') else Fraction(1))
    return out


def _round_half_up(value, places):
    q = Fraction(10) ** places
    n = abs(value) * q
    whole = n.numerator // n.denominator + (1 if n - n.numerator // n.denominator >= Fraction(1, 2) else 0)
    return (whole if value >= 0 else -whole) / q


def shows_key(text, raw, question='', answer_type=None):
    """True when ``text`` shows any part of the key ``raw``, by a different route from M.reveals_key."""
    low = re.sub(r'\s+', '', str(text).lower())
    roots = answer_type == 'quadratic_roots'
    values = _values(text, roots=roots)
    if answer_type == 'linear_equation':
        values += [(g, 0) for g in _gradient_terms(text)]
    parts = [p.strip() for p in re.split(r'[\x1e|]', str(raw))]
    wanted = []          # (key value with its sign, its places, an item of a list)
    if answer_type == 'algebraic_fraction' and len(parts) == 2 and all(re.fullmatch(r'-?\d+', p.replace('\u2212', '-')) for p in parts) \
            and int(parts[1].replace('\u2212', '-')):
        wanted.append((Fraction(int(parts[0].replace('\u2212', '-')), int(parts[1].replace('\u2212', '-'))), 0, False))
    for part in parts:
        if not part:
            continue
        clean = part.replace('\u2212', '-').replace('%', '').replace('\u00b0', '')
        try:
            kv = Fraction(re.sub(r'\s+', '', clean))
        except (ValueError, ZeroDivisionError):
            kv = None
        if kv is not None:
            wanted.append((kv, len(clean.split('.')[1]) if '.' in clean and '/' not in clean else 0, False))
            continue
        word = re.sub(r'\s+', '', part.lower())
        if word.isalpha():
            if re.search(r'(?<![a-z])' + re.escape(word) + r'(?![a-z])', str(text).lower()):
                return True
        elif word and word in low:
            return True
        elif len(_loose(word)) >= 3 and _loose(word) in _loose(text):
            return True     # review: an algebraic key written in LaTeX (\boxed{2 x^{2} + 4 x + 2}, \dfrac{W}{F})
        # review: the numbers of a list key (6,-3), an assignment (y=36) or a graph reading (23~3.5)
        if '~' in clean:
            pieces, listed = [clean.split('~')[0].strip()], False
        elif '=' in clean:
            pieces, listed = [clean.split('=', 1)[1].strip()], False
        elif ',' in clean and not re.fullmatch(r'\d{1,3}(?:,\d{3})+', clean):
            pieces, listed = [x.strip() for x in clean.split(',')], True
        else:
            pieces, listed = [], False
        for piece in pieces:
            if re.fullmatch(r'-?\d+(?:\.\d+)?', piece):
                wanted.append((Fraction(piece), len(piece.split('.')[1]) if '.' in piece else 0, listed))
    printed = {v for v, _ in _values(question)}
    items = [w for w in wanted if w[2]]
    shown_items = []

    def shows(v, places, kv, kplaces, listed):
        if kv < 0 and v >= 0:
            return False            # a negative key needs its minus sign
        if listed and not roots:
            if v != kv and not (kplaces and places > kplaces and _round_half_up(v, kplaces) == kv):
                return False        # an item of a list is a signed value
        # otherwise a positive key is shown by its value with either sign (cautious)
        return abs(v) == abs(kv) or bool(kplaces and places > kplaces and _round_half_up(abs(v), kplaces) == abs(kv))

    for kv, kplaces, listed in wanted:
        if any(shows(v, places, kv, kplaces, listed) for v, places in values):
            if not listed:
                return True
            shown_items.append(kv)
            if roots or kv not in printed:
                return True         # an item the question prints with its sign is exempt, but never a root
    return bool(items) and len(shown_items) == len(items)     # every item of the list shown


def _loose(text):
    """Independent loose form for algebra: LaTeX fractions and roots unwrapped, wrappers, spaces, brackets and
    multiplication signs dropped (not the module's ``algebra_form``)."""
    t = str(text).lower().replace('**', '^').replace('\u2212', '-').replace('\\pi', 'π')
    for _ in range(3):
        t = re.sub(r'\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}', r'\1/\2', t)
        t = re.sub(r'\\sqrt\{([^{}]*)\}', r'√\1', t)
    t = re.sub(r'\\(?:boxed|left|right|times|cdot|,|\(|\))', '', t)
    return re.sub(r'[\s{}()*×]', '', t)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers on the app
# ─────────────────────────────────────────────────────────────────────────────

def start_practice(client, topic, mode='standard', subject='maths', level='gcse'):
    r = client.post('/', data={'level': level, 'subject': subject, 'topic': topic, 'mode': mode,
                               'difficulty': 'foundational', 'action': 'start'}, follow_redirects=True)
    return r.status_code, r.data.decode()


def stored(client):
    with client.session_transaction() as sess:
        return copy.deepcopy(sess.get('last_problem_payload'))


def bind(client, problem, topic='pythagoras', subject='maths', level='gcse', source=None, mode='standard'):
    with client.session_transaction() as sess:
        payload = {'level': level, 'subject': subject, 'topic': topic, 'mode': mode,
                   'difficulty': 'foundational', 'problem': problem}
        if source:
            payload['source'] = source
        sess['last_problem_payload'] = payload


def typed_problem(topic='pythagoras', want_slip=None, tries=60):
    """A generated typed number problem of ``topic`` (and, with ``want_slip``, one whose first candidate is named)."""
    import random
    from topic_registry import TOPICS
    func = TOPICS['gcse']['maths'][topic]['func']
    for seed in range(tries):
        random.seed(seed)
        p = func('foundational', 'standard')
        if p and not p.get('options') and p.get('answer_type') == 'number' and p.get('correct_answer_raw') is not None:
            return p
    raise AssertionError(f'no typed number problem for {topic}')


# ─────────────────────────────────────────────────────────────────────────────
# template
# ─────────────────────────────────────────────────────────────────────────────

def check_template(app):
    copy_ = M.LADDER_COPY
    with app.test_client() as client:
        status, html = start_practice(client, 'pythagoras')
        expect('template', 'typed page', status == 200 and 'free-response-inline' in html, f'status {status}')
        # no pre-attempt Hint drawer (2026-11-04): a hint shows only after an attempt
        expect('template', 'no drawer', 'practice-hint' not in html and '<details class="practice-hint-drawer"' not in html,
               'the pre-attempt Hint drawer must be gone from the practice page')
        expect('template', 'no hint text', status == 200 and 'hint-reveal' not in html, 'no hint text may be rendered before an attempt')
        # greyed Show answer: not openable, not focusable, explained, with a polite status for the unlock
        expect('template', 'typed page', re.search(r'<details class="answer-reveal" data-locked>', html) is not None,
               'Show answer must be rendered locked (data-locked), not hidden, for a typed GCSE maths question')
        summ = re.search(r'<summary([^>]*)>Show answer<span class="answer-reveal-note"> ([^<]*)</span></summary>', html)
        expect('template', 'locked bar', summ is not None, 'the locked Show answer bar is missing')
        if summ:
            expect('template', 'locked bar', 'aria-disabled="true"' in summ.group(1) and 'tabindex="-1"' in summ.group(1),
                   'the greyed bar must be aria-disabled and out of the tab order')
            expect('template', 'locked bar', summ.group(2).strip() == copy_['locked'], 'the explanation is not the LADDER_COPY text')
        expect('template', 'locked bar', 'Opens after your first try' == copy_['locked'], 'the explanation wording changed')
        status_p = re.search(r'<p class="answer-reveal-status"([^>]*)></p>', html)
        expect('template', 'status', status_p is not None and 'role="status"' in status_p.group(1)
               and f'data-open="{copy_["opened"]}"' in status_p.group(1), 'a polite status region must carry the unlock text')
        expect('template', 'old pieces', 'answer-locked-note' not in html and 'Open Show answer' not in html and ' hidden>' not in html.split('answer-reveal')[1][:80],
               'the locked note and the Open Show answer button are gone')
        box = re.search(r'<div class="free-response-hint"([^>]*)>(.*?)</button>\s*</div>', html, re.S)
        expect('template', 'typed page', box is not None, 'no hint area in the typed block')
        if box:
            inner = box.group(2)
            expect('template', 'hint card', 'aria-live="polite"' in box.group(1), 'the hint area must be a polite live region')
            expect('template', 'hint card', '<div class="hint-card" hidden>' in inner and inner.count('class="hint-card-title') == 2
                   and f'>{copy_["hint"]}</p>' in inner and f'>{copy_["bigger"]}</p>' in inner, 'card: a Hint heading and a Bigger hint subheading')
            expect('template', 'hint card', 'free-response-hint-line' in inner and 'free-response-hint-bigger' in inner, 'card text slots')
            expect('template', 'hint area', re.search(r'<button type="button" class="btn btn-outline btn-sm free-response-hint-more" hidden>', inner)
                   is not None, 'the bigger-hint control must be a real button, hidden until a first wrong attempt')
            expect('template', 'hint area', f'data-more="{copy_["more"]}"' in box.group(1), 'the button words come from LADDER_COPY')
            expect('template', 'order', html.index('free-response-feedback') < html.index('free-response-hint"'),
                   'the hint area must sit under the feedback line')
            expect('template', 'inline style', 'style=' not in box.group(0), 'templates forbid inline style=')
        expect('template', 'typed page', 'tabindex' not in (box.group(0) if box else ''), 'the hint area must not take focus')

        # multiple choice: locked until the pick, no ladder, one polite card slot for the option note
        status, html = start_practice(client, 'pythagoras', mode='mcq')
        expect('template', 'mcq page', status == 200 and 'id="mcq-options"' in html, f'status {status}')
        expect('template', 'mcq page', '<details class="answer-reveal" data-locked>' in html and 'mcq-hint-slot' in html
               and 'practice-hint' not in html, 'multiple choice must render Show answer locked (it opens with the pick) and no Hint drawer')
        expect('template', 'mcq page', 'free-response-hint' not in html, 'multiple choice has no ladder')

        # other subjects are unchanged
        from app import TOPICS
        cs_topic = next((t for t, cfg in TOPICS['gcse'].get('cs', {}).items() if 'standard' in (cfg.get('modes') or ['standard'])), None)
        if cs_topic:
            status, html = start_practice(client, cs_topic, subject='cs')
            if status == 200 and 'answer-reveal' in html:
                expect('template', 'cs page', '<details class="answer-reveal">' in html and 'data-locked' not in html
                       and 'free-response-hint' not in html, 'GCSE computer science must keep the open Show answer drawer')

        # Quick Test: the one-line hint only, no drawer, no ladder (D1c)
        r = client.post('/quicktest/start', data={'level': 'gcse', 'subject': 'maths', 'topic': 'pythagoras', 'mode': 'standard',
                                                  'difficulty': 'foundational'}, follow_redirects=True)
        html = r.data.decode()
        expect('template', 'quick test', r.status_code == 200 and 'quicktest-quiz-runner' in html, f'status {r.status_code}')
        expect('template', 'quick test', 'answer-reveal' not in html and 'data-locked' not in html
               and 'free-response-hint' not in html, 'Quick Test must show no Show answer drawer and no ladder')

    # the other pages with their own drawer are not part of D1 (D1e)
    for name in ('saved_problem', 'shared_question', 'suggestion_view', 'qotd'):
        text = read(f'templates/{name}.html')
        expect('template', name, 'ladder_copy' not in text and 'hint_ladder' not in text and 'data-locked' not in text
               and re.search(r'class="answer-reveal"[^>]*hidden', text) is None, 'this page must not use the ladder or the lock')
    index = read('templates/index.html')
    expect('template', 'index', "problem.options or problem.correct_answer_raw" in index,
           'the lock must apply only when there is something to answer')
    expect('template', 'index', "selected_level == 'gcse' and selected_subject == 'maths'" in index, 'the lock is for GCSE maths only')
    # The "Revise:" link names the topic as the registry does (Phase 5 fix), not the slug title-cased ("Bidmas").
    # Review 2026-10-26: all 32 GCSE maths topics were checked by hand; these four have a name unlike their slug.
    import html as _html
    from topic_registry import TOPICS
    with app.test_client() as client:
        for slug in ('bidmas', 'fdp', 'pythagoras', 'geometry_angles'):
            status, html = start_practice(client, slug)
            got = re.search(r'Revise: ([^<]+)</a>', html)
            want = TOPICS['gcse']['maths'][slug]['name']
            expect('template', f'revise link {slug}', status == 200 and got is not None
                   and _html.unescape(got.group(1)).strip() == want, f'shows {got.group(1) if got else None!r}, want {want!r}')


# ─────────────────────────────────────────────────────────────────────────────
# route
# ─────────────────────────────────────────────────────────────────────────────

def check_route(app):
    problem = typed_problem('geometry_angles') if False else None
    straight = {
        'question': 'Two angles lie on a straight line. One angle is 41°. Find the other angle.',
        'correct_answer_raw': '139', 'answer_type': 'number', 'solution': 'The angles add up to 180°.<br>180 − 41 = <strong>139</strong>°',
        'hint': 'Angles on a straight line add up to 180°.', 'marks': 1,
    }
    with app.test_client() as client:
        bind(client, straight, topic='geometry_angles')
        before = stored(client)
        # not asked: nothing new in the response (Phase 1 and 2 behaviour)
        body = client.post('/api/v1/problems/check', json={'user_answer': '41'}, headers=HDR).get_json()
        expect('route', 'not asked', body.get('hint') == {'kind': 'misconception', 'id': 'ang.supplement'},
               f'without hint_ladder the hint must be the Phase 1 object, got {body.get("hint")}')
        for value in (False, 1, 'true', None):
            body = client.post('/api/v1/problems/check', json={'user_answer': '41', 'hint_ladder': value}, headers=HDR).get_json()
            expect('route', f'hint_ladder={value!r}', 'rung' not in (body.get('hint') or {}), 'only a true boolean asks for the ladder')
        # a recognised slip: its message is the feedback line; the ladder adds rung 1 marker and the bigger hint
        body = client.post('/api/v1/problems/check', json={'user_answer': '41', 'hint_ladder': True}, headers=HDR).get_json()
        hint = body.get('hint') or {}
        expect('route', 'slip', body.get('feedback') == M.MESSAGES['ang.supplement'], 'the slip message must stay the feedback line')
        expect('route', 'slip', hint.get('kind') == 'misconception' and hint.get('rung') == 1 and hint.get('id') == 'ang.supplement'
               and 'text' not in hint, f'a recognised slip needs no nudge text: {hint}')
        expect('route', 'slip', hint.get('bigger') == 'The angles add up to 180°.', f'rung 2 is the first step that hides the key: {hint}')
        expect('route', 'slip', set(hint) <= {'kind', 'id', 'rung', 'bigger'}, f'unexpected keys {sorted(hint)}')
        # no slip: a nudge (the problem's own hint, as it does not show the key)
        body = client.post('/api/v1/problems/check', json={'user_answer': '7', 'hint_ladder': True}, headers=HDR).get_json()
        hint = body.get('hint') or {}
        expect('route', 'nudge', hint.get('kind') == 'nudge' and hint.get('rung') == 1 and hint.get('text') == straight['hint'],
               f'a wrong answer with no slip must get the problem hint as rung 1: {hint}')
        expect('route', 'nudge', 'id' not in hint, 'a nudge carries no rule id')
        expect('route', 'nudge', body.get('feedback') == 'Not quite. Check your working.', 'the checker feedback stays')
        # correct: no ladder at all
        body = client.post('/api/v1/problems/check', json={'user_answer': '139', 'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'correct', body.get('correct') is True and 'hint' not in body, f'a right answer carried a hint: {body}')
        # unreadable: the checker's own message, no ladder, no attempt
        body = client.post('/api/v1/problems/check', json={'user_answer': 'abc', 'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'unreadable', 'hint' not in body and body.get('feedback', '').startswith('Enter'), f'unreadable answer: {body}')
        expect('route', 'session', stored(client) == before, 'the session problem changed after checks (nothing may be stored)')
        extra = set(body) - {'ok', 'correct', 'normalized_user', 'normalized_correct', 'feedback', 'hint', 'cohort', 'practice_streak',
                             'attempt_id', 'score', 'score_total'}
        expect('route', 'keys', not extra, f'unexpected response keys {sorted(extra)}')

        # Quick Test source: the line, never the ladder (D1c)
        bind(client, straight, topic='geometry_angles', source='quicktest')
        body = client.post('/api/v1/problems/check', json={'user_answer': '41', 'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'quick test', body.get('hint') == {'kind': 'misconception', 'id': 'ang.supplement'}
               and body.get('feedback') == M.MESSAGES['ang.supplement'],
               f'Quick Test must get the one-line hint and no ladder: {body.get("hint")}')
        body = client.post('/api/v1/problems/check', json={'user_answer': '7', 'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'quick test', 'hint' not in body, f'Quick Test got a nudge ladder: {body.get("hint")}')

        # a lesson-quiz question is also the session problem (mode 'lesson'): a hand-made request gets no ladder (review)
        bind(client, straight, topic='geometry_angles', mode='lesson')
        for answer in ('41', '7'):
            body = client.post('/api/v1/problems/check', json={'user_answer': answer, 'hint_ladder': True}, headers=HDR).get_json()
            expect('route', 'lesson quiz', 'rung' not in (body.get('hint') or {}), f'a lesson-quiz question got a ladder: {body.get("hint")}')

        # a client-supplied key with no session problem, and another subject: no ladder
        with client.session_transaction() as sess:
            sess.pop('last_problem_payload', None)
        body = client.post('/api/v1/problems/check', json={'user_answer': '7', 'correct_answer_raw': '139', 'answer_type': 'number',
                                                           'level': 'gcse', 'subject': 'maths', 'topic': 'geometry_angles',
                                                           'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'client key', 'hint' not in body, f'a client-supplied key got a ladder: {body}')
        bind(client, straight, topic='motion', subject='physics')
        body = client.post('/api/v1/problems/check', json={'user_answer': '7', 'hint_ladder': True}, headers=HDR).get_json()
        expect('route', 'physics', 'hint' not in body, f'a physics question got a ladder: {body}')

        # a multi-part answer: each part is checked alone, the ladder is built from the whole problem
        multi = {'question': 'Find x and y.', 'correct_answer_raw': '30\x1e150', 'answer_type': 'number_fields',
                 'answer_field_types': ['number', 'number'], 'answer_labels': ['x', 'y'],
                 'solution': 'x is a third of the angle.<br>x = 30° and y = 150°', 'hint': 'Use angles on a line.', 'marks': 2}
        bind(client, multi, topic='geometry_angles')
        body = client.post('/api/v1/problems/check', json={'user_answer': '55', 'correct_answer_raw': '30', 'answer_type': 'number',
                                                           'part_index': 0, 'part_total': 2, 'hint_ladder': True}, headers=HDR).get_json()
        hint = body.get('hint') or {}
        expect('route', 'multi-part', hint.get('rung') == 1 and hint.get('bigger') == 'x is a third of the angle.',
               f'a wrong part must get a ladder built from the whole problem: {hint}')
        expect('route', 'multi-part', not shows_key(hint.get('text', '') + ' ' + hint.get('bigger', ''), multi['correct_answer_raw']),
               'a ladder line shows a part of the key')

    # Quick Test end to end: the session source is set on the question page, and the check route honours it
    with app.test_client() as client:
        r = client.post('/quicktest/start', data={'level': 'gcse', 'subject': 'maths', 'topic': 'pythagoras', 'mode': 'standard',
                                                  'difficulty': 'foundational'}, follow_redirects=True)
        expect('route', 'quick test flow', r.status_code == 200, f'status {r.status_code}')
        s = stored(client) or {}
        expect('route', 'quick test flow', s.get('source') == 'quicktest', f'the Quick Test question must mark the session: {sorted(s)}')
        prob = s.get('problem') or {}
        if prob.get('correct_answer_raw') is not None and not prob.get('options'):
            body = client.post('/api/v1/problems/check', json={'user_answer': '99999', 'hint_ladder': True}, headers=HDR).get_json()
            expect('route', 'quick test flow', 'hint' not in body or 'rung' not in body['hint'], f'ladder in Quick Test: {body}')
    with app.test_client() as client:
        start_practice(client, 'pythagoras')
        s = stored(client) or {}
        expect('route', 'practice session', 'source' not in s, 'a practice question must not carry the Quick Test mark')


# ─────────────────────────────────────────────────────────────────────────────
# ladder content
# ─────────────────────────────────────────────────────────────────────────────

CASES = (
    # (label, solution, hint, key, topic, expected rung 2, expected rung 1 or None for "problem hint")
    ('first step shown', 'Diagonal splits the square into two triangles with legs 10 cm:<br>10² + 10² = d² → 200 = d²<br>d = √200 = <strong>14.14 cm</strong>',
     'Think of the diagonal as a hypotenuse.', '14.14', 'pythagoras',
     'Diagonal splits the square into two triangles with legs 10 cm.', 'Think of the diagonal as a hypotenuse.'),
    ('a step that shows the key is skipped, the next one is used', '3 × 48 = 144<br>Check the units.<br><strong>144 g</strong>', 'Mass = density × volume.', '144', 'mensuration',
     'Check the units.', 'Mass = density × volume.'),
    ('one-line solution has no rung 2', '1 + 2 = <strong>3</strong>', 'Add the numbers.', '3', 'bidmas', '', 'Add the numbers.'),
    ('key at its accuracy is hidden', 'd = √200 = 14.142 (to 3 d.p.)<br>Round to 2 d.p.', 'Use Pythagoras.', '14.14', 'pythagoras', 'Round to 2 d.p.', 'Use Pythagoras.'),
    ('a minus sign matters for a negative key', '3 − 2 = 1<br>1 × −2 = −2', 'Work in order.', '-2', 'bidmas', '3 − 2', 'Work in order.'),
    ('a fraction key in LaTeX is hidden', 'Add the fractions.<br>\\(\\frac{9}{49}\\)', 'Multiply along the branch.', '9/49', 'probability',
     'Add the fractions.', 'Multiply along the branch.'),
    ('a hint that shows the key falls back to the topic line', 'Step one.<br>Step two: 25', 'Here: 146 ÷ 100 = 1.46.', '1.46', 'fdp',
     'Step one.', M.NUDGES['fdp']),
    ('a long hint falls back to the topic line', 'Step one.<br>Step two: 25', 'x' * 200, '25', 'pythagoras', 'Step one.', M.NUDGES['pythagoras']),
    ('no hint and an unknown topic gives the plain default', 'Step one.<br>Step two: 25', '', '25', 'no_such_topic', 'Step one.', M.NUDGE_DEFAULT),
    ('code is never a hint', '<pre>print(1)</pre>', 'Use a loop.', '1', 'bidmas', '', 'Use a loop.'),
    ('a word key is hidden as a word only', 'The answer is not a word like answer.<br>SW is the direction.<br>Look again.', 'Use the compass.', 'sw', 'bearings',
     'The answer is not a word like answer.', 'Use the compass.'),
    ('an algebraic key is hidden', 'Expand the bracket.<br>x = 2x + 1', 'Collect like terms.', '2x+1', 'algebra', 'Expand the bracket.', 'Collect like terms.'),
    ('multi-part keys: every part is hidden', 'Find the first angle.<br>x = 30 and y = 150', 'Look for parallel lines.', '30\x1e150', 'geometry_angles',
     'Find the first angle.', 'Look for parallel lines.'),
)


def check_ladder_cases():
    for label, solution, hint, key, topic, big, text in CASES:
        problem = {'solution': solution, 'hint': hint, 'correct_answer_raw': key, 'answer_type': 'number'}
        got = M.build_ladder(problem, topic=topic, correct_raw=key)
        expect('ladder', label, got.get('bigger') == big, f'rung 2 {got.get("bigger")!r}, wanted {big!r}')
        expect('ladder', label, got.get('text') == text, f'rung 1 {got.get("text")!r}, wanted {text!r}')
        expect('ladder', label, got.get('rung') == 1 and got.get('kind') == 'nudge' and 'id' not in got, f'shape {got}')
        expect('ladder', label, not shows_key(got.get('bigger', ''), key) and (got['text'] in M.NUDGES.values() or not shows_key(got['text'], key)),
               'a rung shows the key')
    got = M.build_ladder({'solution': 'Step one.', 'hint': 'h', 'correct_answer_raw': '5'}, topic='x', correct_raw='5', slip='gen.sign')
    expect('ladder', 'slip', got == {'kind': 'misconception', 'rung': 1, 'id': 'gen.sign', 'bigger': 'Step one.'}, f'slip ladder {got}')
    # rung 2 that only repeats rung 1 is dropped, so the page shows no "Show a bigger hint" (2026-11-07)
    bidmas = {'question': 'Calculate 3 × 3^2', 'solution': 'Indices before multiplication.<br>3^2 = 9<br>3 × 9 = 27',
              'hint': 'Indices (powers) come before multiplication in BIDMAS.', 'correct_answer_raw': '27', 'answer_type': 'number'}
    got = M.build_ladder(bidmas, topic='bidmas', correct_raw='27')
    expect('ladder', 'repeat', got.get('bigger') == '' and got.get('text') == bidmas['hint'], f'a repeated hint was kept: {got}')
    got = M.build_ladder({'solution': 'Angles on a straight line add up to 180°.<br>x = 40', 'correct_answer_raw': '40'},
                         topic='geometry_angles', correct_raw='40', slip='ang.line', slip_text='Angles on a straight line add up to 180°.')
    expect('ladder', 'repeat slip', got.get('bigger') == '', f'a step repeating the slip message was kept: {got}')
    for first, big, same in (
        ('Indices (powers) come before multiplication in BIDMAS.', 'Indices before multiplication.', True),
        ('The nth square number is n².', 'The \\(n\\)th square number is \\(n^2\\).', True),
        ('Cover S in the SDT triangle: Speed = Distance ÷ Time.', 'Speed = Distance ÷ Time', True),
        ('Use a multiplier.', 'Multiplier = 1 + 20/100', False),
        ('Reflection in y = x: swap the two coordinates.', 'Reflection in \\(y = x\\): \\((x, y) \\to (y, x)\\).', False),
        ('Rearrange to make x the subject.', '\\(x = y/k\\)', False),
        ('Collect like terms.', 'Expand the bracket.', False),
    ):
        expect('ladder', 'repeat rule', M.adds_nothing(first, big) is same, f'adds_nothing({first!r}, {big!r}) should be {same}')
    # after the question's own hint, rung 2 must bring something concrete: a number, an operation, or a letter, term or
    # point from the question (2026-11-07: the function machine pair said the same thing in other words)
    for first, big, question, same in (
        ('Reverse the machine: undo the last operation first, then undo the first operation.',
         'Work backwards, undoing each step in reverse order.', 'A machine multiplies by 4 then adds 4. The output is 16. Find the input.', True),
        ('Multiply the probability by the number of trials to predict how many successes to expect.',
         'Expected frequency = probability × number of trials', 'P(red) = 0.3. The spinner is spun 50 times.', True),
        ('Subtract the smaller bearing from the larger.', 'Angle between = larger − smaller', 'Bearings 040° and 125°.', True),
        ('Rotation 90° clockwise about the origin: (x, y) → (y, −x).', 'Rotation 90° CW about origin: \\((x, y) \\to (y, -x)\\).',
         'Rotate (3, 5) by 90° clockwise about the origin.', True),
        ('Treat P = 2l + 2w like a normal equation.', 'Subtract \\(2w\\) from both sides: \\(P - 2w = 2l\\)',
         'Make \\(l\\) the subject of \\(P = 2l + 2w\\).', False),
        ('Move the unwanted terms to the opposite side.', 'Subtract \\(at\\) from both sides.', 'Make \\(u\\) the subject of \\(v = u + at\\).', False),
        ('Work on all three parts simultaneously: subtract then divide.', 'Subtract 5 from all three parts.', 'Solve 11 < 2x + 5 < 19.', False),
        ('Divide the known area by the area scale factor (LSF²) to find the smaller area.', 'Area scale factor = 2²',
         'Two similar shapes have lengths in the ratio 1 : 2. The larger has area 48 cm².', False),
        ('Use the pair you know (a and A) together with the unknown pair (b and B).', 'Sine rule: \\(\\dfrac{a}{\\sin A} = \\dfrac{b}{\\sin B}\\)',
         'In triangle ABC, a = 8, A = 40° and B = 65°. Find b.', False),
    ):
        expect('ladder', 'concrete rule', M.adds_nothing(first, big, question=question) is same,
               f'adds_nothing({first!r}, {big!r}, question=...) should be {same}')
    # unsafe markup and bad input never raise
    for bad in (None, {}, {'solution': 5}, {'solution': '<svg></svg>', 'hint': '$x$'}):
        got = M.build_ladder(bad, topic='bidmas', correct_raw='5')
        expect('ladder', f'bad input {bad!r}', got['bigger'] == '' and got['text'], f'bad input gave {got}')
    expect('ladder', 'reveals_key', M.reveals_key('anything', '') is True, 'with no key to compare, every line is held back')
    expect('ladder', 'copy', all(isinstance(v, str) and v for v in {**M.NUDGES, **M.LADDER_COPY}.values()), 'empty copy')


REVIEW_CASES = (
    # (label, question, solution, key, answer type, expected rung 2) -- the Phase 3 review rules, worked by hand
    ('a worked-out number at the end is hidden', 'A value of 240 is increased by 12%. Find the new value.',
     'Find 12% of 240: 240 × 12/100 = 28.8<br>Add to the original: 240 + 28.8 = <strong>268.8</strong>', '268.8', 'number',
     'Find 12% of 240: 240 × 12/100'),
    ('the last step before a square root keeps its method only', 'The hypotenuse is 11 cm and one side is 5 cm. Find the other side to 2 d.p.',
     'b² = c² − a² = 11² − 5² = 96<br>b = √96 = <strong>9.80</strong> cm', '9.80', 'number', 'b² = c² − a² = 11² − 5²'),
    ('inside LaTeX the closing bracket stays', 'Solve 4x + 2 = -18.', 'Subtract 2: \\(4x = -18 - 2 = -20\\)<br>\\(x = -5\\)', '-5', 'linear',
     'Subtract 2: \\(4x = -18 - 2\\)'),
    ('a number printed in the question is not a result', 'A box holds 3 red and 4 blue counters, 7 in all. Find P(red).',
     'Total = 3 + 4 = 7<br>P(red) = 3/7', '3/7', 'fraction', 'Total = 3 + 4 = 7'),
    ('an angle total is a fact, not a result', 'Two angles of a triangle are 50° and 60°. Find the third.',
     'Angles in a triangle: a + b + c = 180°<br>c = 70°', '70', 'number', 'Angles in a triangle: a + b + c = 180°'),
    ('hiding the number leaves no method: no rung 2, and no later step', 'Find the missing term: 11, 17, 23, ___, 35',
     'The common difference is \\(d = 6\\).<br>Missing term \\(= 23 + 6\\)<br>\\(= 29\\)', '29', 'number', ''),
    ('an ordering proof never has a rung 2', 'Put the steps in order.', 'Step 1. Join OA.<br>Step 2. Triangle OAC is isosceles.',
     '1|s1|s2', 'proof_steps', ''),
    ('an expanded key in LaTeX is hidden', 'Expand and simplify (4x + 5)(x + 4).',
     '\\( (4x + 5)(x + 4) = \\boxed{4 x^{2} + 21 x + 20} \\)', '4*x**2 + 21*x + 20', 'algebraic', ''),
    ('a rearranged formula in LaTeX is hidden', 'Make d the subject of W = Fd.', 'Divide both sides by \\(F\\): \\(d = \\dfrac{W}{F}\\)',
     'd=(w)/(f)', 'algebraic', ''),
    ('a factor shows a root in effect', 'Solve x² + 7x + 12 = 0.', 'Factorise: \\( (x + 4)(x + 3) = 0 \\)<br>x = -4 or x = -3',
     '-4,-3', 'quadratic_roots', ''),
    ('the coefficients of a formula do not show the roots', 'Solve x² - x - 12 = 0 with the formula.',
     'Here \\(a = 1\\), \\(b = -1\\), \\(c = -12\\).<br>x = 4 or x = -3', '4,-3', 'quadratic_roots', 'Here \\(a = 1\\), \\(b = -1\\), \\(c = -12\\).'),
    # whole-change review 2026-11-03 (F4): a root is never exempt because the question prints its number, so a
    # coefficient equal to a root in size is held back (cautious; this case had rung 2 "Here a = 1, b = -5, c = -6.")
    ('a coefficient as large as a root is held back', 'Solve x² - 5x - 6 = 0 with the formula.',
     'Here \\(a = 1\\), \\(b = -5\\), \\(c = -6\\).<br>x = 6 or x = -1', '-1,6', 'quadratic_roots', ''),
    ('F4: a spaced minus is a sign (the minimum value of a completed square)', 'Find the minimum value of 5x² − 20x + 15.',
     '\\( 5x^2 - 20x + 15 = 5(x^2 - 4x + 3) = 5(x - 2)^2 - 5 \\).<br>The minimum value is <strong>-5</strong>.', '-5', 'number', ''),
    ('F4: roots printed in the question are still shown', 'Solve \\( \\dfrac{2}{x} = x - 1 \\).',
     'x = -1 or x = 2 (neither makes the denominator zero).', '-1,2', 'quadratic_roots', ''),
    ('F4: a numerator|denominator key written as one fraction', 'Work out \\( \\dfrac{3x + 5}{x - 2} \\) when x = 4.',
     'The value is \\(\\dfrac{17}{2}\\), which cannot be simplified.', '17|2', 'algebraic_fraction', ''),
    ('F4: a gradient of -1 written as -x', 'Find the equation of the line through (1, -1) and (-1, 1) in the form y = mx + c.',
     'y = −x', '-1|0', 'linear_equation', ''),
    ('F5: a power keeps its superscript', 'Find the smallest whole number that 54 must be multiplied by to give a square number.',
     'Write 54 as a product of prime factors: 54 = 2 × 3<sup>3</sup>.<br>Each power must be even, so multiply by 2 × 3 = <strong>6</strong>.',
     '6', 'number', 'Write 54 as a product of prime factors: 54 = 2 × 3³.'),
    # whole-change review 2026-11-03 (F6): a step that leaves only a trivial move is no rung 2, and no later step is used
    ('F6: a count that leaves only the division', 'In a survey of 63 people: A only 18, B only 21, both 13, neither 11. Find P(A ∩ B).',
     'A ∩ B means in both A and B, so count the overlap only: 13 people.<br>P(A ∩ B) = <strong>13/63</strong>.', '13/63', 'fraction', ''),
    ('F6: the bottom of the fraction with its top in the step', 'In a survey of 50 people: A only 18, B only 15, both 8, neither 9. Find P(B given A).',
     'The choice is made from set A only: A only (18) plus the overlap (8), which is 26 people.<br>Of these, the 8 in the overlap are also in B.'
     '<br>Probability = 8/26 = <strong>4/13</strong>.', '4/13', 'fraction', ''),
    ('F6: a list with as many items as the answer', 'How many factors does 48 have?',
     'The factors of 48 are 1, 2, 3, 4, 6, 8, 12, 16, 24, 48.<br>Counting them gives <strong>10</strong> factors.', '10', 'number', ''),
    ('F6: a list that adds up to the answer', 'The frequency polygon shows the times of some runners. How many runners are there?',
     'Read the frequency at each plotted point: 8, 6, 8, 2.<br>Total = 8 + 6 + 8 + 2 = <strong>24</strong>.', '24', 'number', ''),
    ('F6: an inequality one step from the whole-number answer', 'The line y = −6x + k does not meet the curve y = x² + 4. Find the greatest whole number k.',
     'Equate: \\( x^2 + 4 = -6x + k \\).<br>No real solutions needs \\( b^2 - 4ac < 0 \\): \\( 36 - 16 + 4k < 0 \\), so \\( k < -5 \\).'
     '<br>The greatest whole number below -5 is <strong>-6</strong>.', '-6', 'number', ''),
    ('F6: the rest of a factorised answer', 'Factorise completely 6n² + 12n. Explain why it is a multiple of 6.',
     'The common factor is 6n: \\( 6n^2 + 12n = 6n(n + 2) \\).<br>It is 6 times the integer \\( n(n + 2) \\), so it is a multiple of 6.',
     '6*n*(n + 2)', 'algebraic', ''),
    ('F6: x + 6 = ±3 leaves only the roots', 'Hence solve x² + 12x + 27 = 0.',
     '\\( (x + 6)^2 - 9 = 0 \\).<br>Square root both sides: \\( x + 6 = \\pm 3 \\).<br>x = -3 or x = -9', '-3,-9', 'quadratic_roots', ''),
    ('F6: two points whose midpoint is the answer', 'The line meets the curve at A and B. Find the midpoint of AB.',
     '\\( (x + 6)(x - 2) = 0 \\).<br>\\( A = (-6, 36) \\) and \\( B = (2, 4) \\).<br>Midpoint (-2, 20)', '-2|20', 'number_pair', ''),
    ('F6: a step that still needs counting keeps its rung 2', '2 fair coins are flipped. Find P(exactly 1 head).',
     'There are 2^2 = 4 equally likely outcomes.<br>HT and TH: 2 out of 4 = <strong>1/2</strong>.', '1/2', 'fraction',
     'There are 2^2 = 4 equally likely outcomes.'),
    ('an assignment key shows by its number', 'y = x² and y = 4x + 12 meet where x = 6. Find y.',
     'Substitute \\(x = 6\\): \\(y = 6^2 = 36\\) (matches the line too).', 'y=36', 'linear', ''),
    ('a graph reading shows by its value', 'Use the line of best fit to estimate y when x = 6.',
     'On the line, when x ≈ 6, y ≈ 2×6 + 11 = 23 (accept answers within ±3.5).', '23~3.5', 'number_estimate', ''),
    ('a step that repeats the question is skipped', 'A café mixes milk and syrup in the ratio 6:4 to make 390 ml.',
     'A café mixes milk and syrup in the ratio 6:4 to make 390 ml.<br>Total parts = 10. One part = 390 ÷ 10<br>234 ml and 156 ml',
     '234|156', 'number_fields', 'Total parts = 10. One part = 390 ÷ 10'),
    ('the middle of a calculation is not a step', 'Find angle A.', 'cos A = 0.17, so A = 79.84°<br>= 10132 − 3758.05<br>Angle A = 79.84°',
     '79.84', 'number', ''),
)


def check_ladder_review_cases():
    for label, question, solution, key, answer_type, big in REVIEW_CASES:
        problem = {'question': question, 'solution': solution, 'hint': '', 'correct_answer_raw': key, 'answer_type': answer_type}
        got = M.build_ladder(problem, topic='number', correct_raw=key)
        expect('ladder', label, got.get('bigger') == big, f'rung 2 {got.get("bigger")!r}, wanted {big!r}')
        expect('ladder', label, not shows_key(got.get('bigger', ''), key, question, answer_type), 'rung 2 shows the key')
    # whole-change review 2026-11-03 (F4, F9): the four blind spots, in the module and in the independent scan alike
    for text, key, at, question, want in (
            ('= 5(x − 2)² − 5', '-5', 'number', 'Find the minimum value.', True),
            ('so (x + 6)^2 - 33', '-6|-33', 'number_pair', 'Find the turning point.', True),
            ('x = -1 or x = 2', '-1,2', 'quadratic_roots', 'Solve 2/x = x − 1.', True),
            ('these are 1 and -1', '-1,1', 'quadratic_roots', 'Solve x² − 1 = 0.', True),
            ('these are 2 and -6', '-2,6', 'quadratic_roots', 'Solve x² − 4x − 12 = 0.', True),
            ('The value is \\(\\dfrac{17}{2}\\).', '17|2', 'algebraic_fraction', 'Work it out as a fraction.', True),
            ('y = mx + c → y = −x − 8.', '-1|-8', 'linear_equation', 'Gradient −1, y-intercept −8.', True),
            ('y = −x', '-1|0', 'linear_equation', 'q', True),
            ('y = 3 − x', '-1|3', 'linear_equation', 'q', True),
            ('3 − 2', '-2', 'number', 'Work it out.', False),
            ('Subtract 2: \\(4x = -18 - 2\\)', '-5', 'linear', 'Solve 4x + 2 = -18.', False),
            ('x must be greater than 3 and up to and including 9.', '4,5,6,7,8,9', 'number_list', 'List the integers x with 3 < x ≤ 9.', False),
            ('Start from -3 (included) and go up to, but not including, 4.', '-3,-2,-1,0,1,2,3', 'number_list',
             'Write down all integer values of n such that -3 ≤ n < 4.', False),
            ('Using \\(x = \\dfrac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\\) with a = 1.', '4,2', 'quadratic_roots', 'Solve x² − 6x + 8 = 0.', False),
            ('y = mx + c, so find m first', '1|3', 'linear_equation', 'q', False)):
        given = M.question_values({'question': question})
        expect('ladder', f'blind spot {text!r}', M.reveals_key(text, key, at, given) is want, f'reveals_key should be {want}')
        expect('ladder', f'blind spot {text!r}', shows_key(text, key, question, at) is want, f'the independent scan should say {want}')
    for html, plain in (('54 = 2 × 3<sup>3</sup>', '54 = 2 × 3³'), ('(−4)<sup>2</sup> = 16', '(−4)² = 16'), ('x<sup>2n</sup>', 'x²ⁿ'),
                        ('x<sup>a</sup> and y<sup>ab</sup>', 'x^a and y^(ab)'), ('a<sub>1</sub>', 'a₁'), ('10<sup>&minus;3</sup>', '10⁻³')):
        expect('ladder', f'F5 plain_line {html!r}', M.plain_line(html) == plain, f'{M.plain_line(html)!r}, wanted {plain!r}')
    # a list key: an item the question prints does not hold back the problem's own hint (rung 1)
    problem = {'question': 'List the integers x with 3 < x ≤ 9.', 'solution': 'x is 4 up to 9.', 'correct_answer_raw': '4,5,6,7,8,9',
               'answer_type': 'number_list', 'hint': 'x must be greater than 3 and up to and including 9.'}
    got = M.build_ladder(problem, topic='equations_inequalities', correct_raw=problem['correct_answer_raw'])
    expect('ladder', 'list key', got.get('text') == problem['hint'], f'rung 1 {got.get("text")!r}')
    expect('ladder', 'list key', M.reveals_key('the answers start at 5', '4,5,6,7,8,9', given={Fraction(3), Fraction(9)}),
           'an item the question does not print still counts as shown')


LADDER_RUNS = 4        # whole-change review 2026-11-03 (F9): several draws of each slot, not only run 0 (a leak can sit on one draw)


def _trivial_step(line, raw, answer_type, question):
    """An independent look for a step that leaves only a trivial move (F6), narrower than M.answer_in_effect: a list
    of three or more numbers whose count or sum is a whole-number key, or "N out of D" equal to a fraction key."""
    key = None
    try:
        key = Fraction(str(raw).replace('\u2212', '-')) if answer_type in ('number', 'fraction') else None
    except (ValueError, ZeroDivisionError):
        pass
    if key is None:
        return False
    toks = _tokens(line) + [('sym', '.', False)]
    if key.denominator == 1:
        run, after_comma = [], False        # a run of numbers joined by commas: "1, 2, 3, 6, 9, 18"
        for kind, tok, _ in toks:
            if kind == 'num' and (not run or after_comma):
                run.append(Fraction(tok))
                after_comma = False
            elif kind == 'sym' and tok == ',' and run and not after_comma:
                after_comma = True
            else:
                if len(run) >= 3 and (len(run) == key or sum(run) == key):
                    return True
                run, after_comma = ([Fraction(tok)] if kind == 'num' else []), False
        return False
    for k, (kind, tok, _) in enumerate(toks):      # "2 out of 6"
        if kind == 'num' and k + 6 < len(toks) and [t[1].lower() for t in toks[k + 1:k + 6]] == list('outof') \
                and toks[k + 6][0] == 'num' and Fraction(toks[k + 6][1]) and Fraction(tok) / Fraction(toks[k + 6][1]) == key:
            return True
    return False


def check_ladder_slots():
    """Every practice slot, LADDER_RUNS questions each: neither rung shows the key; rung 2 is a method step (review,
    Phase 3). The counts are for run 0 of each slot."""
    slots = [s for s in harness.enumerate_slots() if s.mode == 'standard']
    n = with_big = from_hint = trimmed = repeats = 0
    tail = re.compile(r'=\s*[£$€]?\s*[-\u2212]?(\d[\d,]*(?:\.\d+)?)\s*(?:\\\))?\s*(?:[a-zA-Z]{1,4}[²³]?|°|%)?\s*(?:\\\))?\s*[.;]?$')
    for slot, run in ((s, r) for s in slots for r in range(LADDER_RUNS)):
        problem, _ = harness.generate(slot, run, record=False)
        raw = problem.get('correct_answer_raw') if isinstance(problem, dict) else None
        if raw is None or problem.get('options'):
            continue
        first = run == 0
        n += first
        ladder = M.build_ladder(problem, topic=slot.slug, correct_raw=str(raw))
        where = f'{slot.label}#{run}'
        question = M.plain_line(problem.get('question'))
        at = problem.get('answer_type')
        expect('ladder', where, ladder['rung'] == 1 and ladder['kind'] == 'nudge', f'shape {ladder}')
        text, big = ladder['text'], ladder['bigger']
        expect('ladder', where, bool(text), 'rung 1 is empty')
        expect('ladder', where, not re.search(r'\s[\u2014\u2013]\s', text + ' ' + ladder['bigger']), 'a spaced dash in a hint line (house style)')
        if text not in M.NUDGES.values() and text != M.NUDGE_DEFAULT:
            from_hint += first
            expect('ladder', where, M.plain_line(problem.get('hint')) == text and len(text) <= M.HINT_MAX_LEN, 'rung 1 is not the problem hint')
            expect('ladder', where, not shows_key(text, raw, question, at), f'rung 1 shows the key {raw!r}: {text!r}')
        if problem.get('answer_type') == 'proof_steps':
            expect('ladder', where, big == '', f'an ordering proof must have no rung 2 (any step is part of the answer): {big!r}')
        if not big and M.solution_step(problem, str(raw)):
            repeats += first        # a step that only repeats rung 1 is dropped (2026-11-07)
        if big:
            with_big += first
            own = isinstance(problem.get('hint'), str) and text == M.plain_line(problem['hint'])
            expect('ladder', where, not M.adds_nothing(text, big, specific=own, question=question),
                   f'rung 2 only repeats rung 1: {text!r} / {big!r}')
            expect('ladder', where, not shows_key(big, raw, question, at), f'rung 2 shows the key {raw!r}: {big!r}')
            expect('ladder', where, not _trivial_step(big, raw, at, question), f'rung 2 leaves only a trivial move to {raw!r}: {big!r}')
            steps = [M.plain_line(x) for x in re.split(r'<br\s*/?>|\n', problem['solution']) if M.plain_line(x)]
            stem = big[:-2].rstrip() if big.endswith('\\)') else big     # a cut inside LaTeX keeps its closing \\)
            # a step ending "...:" is shown ending "." (it introduced the next line)
            source = [x for x in steps if x == big or (x.startswith(stem) and len(x) > len(big))
                      or (x.endswith(':') and big.endswith('.') and x[:-1].rstrip() == big[:-1])]
            expect('ladder', where, bool(source), f'rung 2 is not a step of the solution, or the start of one: {big!r}')
            if source:
                trimmed += source[0] != big
                expect('ladder', where, not shows_key(source[0], raw, question, at), f'rung 2 was cut from a step that shows the key: {source[0]!r}')
                earlier = steps[:steps.index(source[0])]
                expect('ladder', where, all(shows_key(x, raw, question, at) or '$' in x or len(x) > M.STEP_MAX_LEN
                                            or re.sub(r'\s+', '', x) in re.sub(r'\s+', '', question) for x in earlier),
                       f'rung 2 is not the first step that hides the key (skipped {earlier!r})')
            # rung 2 shows the method, not the number a step works out (a number printed in the question may stay)
            m = tail.search(big)
            if m:
                v = Fraction(m.group(1).replace(',', ''))
                printed = {abs(val) for val, _ in _values(question)}
                expect('ladder', where, v in printed or v in (0, 90, 180, 360), f'rung 2 ends in a worked-out number: {big!r}')
            expect('ladder', where, len(big) <= M.STEP_MAX_LEN, 'rung 2 is long')
            expect('ladder', where, re.sub(r'\s+', '', big) not in re.sub(r'\s+', '', question), f'rung 2 repeats the question: {big!r}')
    expect('ladder', 'coverage', n >= 600, f'only {n} typed practice slots were checked')
    expect('ladder', 'coverage', (with_big + repeats) / max(n, 1) >= 0.5,
           f'only {with_big} of {n} slots have a rung 2 step, and {repeats} more only repeat rung 1 (floor 50%)')
    return n, with_big, from_hint, repeats


# ─────────────────────────────────────────────────────────────────────────────
# graded: set work and lesson quiz
# ─────────────────────────────────────────────────────────────────────────────

def check_graded(app):
    from models.class_assignments import serialize_student_work, strip_problem_keys
    straight = {
        'question': 'Two angles lie on a straight line. One angle is 41°. Find the other angle.',
        'correct_answer_raw': '139', 'answer_type': 'number', 'solution': 'x', 'solution_html': 'sol', 'hint': 'h', 'marks': 1,
    }
    expect('graded', 'unit', M.graded_message(straight, '41', level='gcse', subject='maths', topic='geometry_angles') == M.MESSAGES['ang.supplement'],
           'the generic message for 180 minus the key')
    for label, prob, ans, kw in (
        ('correct', straight, '139', {}),
        ('no slip', straight, '7', {}),
        ('blank', straight, '  ', {}),
        ('other subject', straight, '41', {'subject': 'physics'}),
        ('other level', straight, '41', {'level': 'alevel'}),
        ('multiple choice', dict(straight, options=['A  1', 'B  2'], correct_answer='A'), '41', {}),
        ('multi-part', dict(straight, answer_type='number_fields', correct_answer_raw='30\x1e150'), '41', {}),
        ('no key', {'question': 'q'}, '41', {}),
    ):
        args = {'level': 'gcse', 'subject': 'maths', 'topic': 'geometry_angles'}
        args.update(kw)
        expect('graded', label, M.graded_message(prob, ans, **args) == '', 'a message where none belongs')
    expect('graded', 'faults', M.graded_message(None, '41', level='gcse', subject='maths') == '', 'a fault must give no message')

    # set work: nothing before grading, the message after it, never the record
    frozen = dict(straight, answer_record={'f': 'x', 'i': {}})
    data = {'id': 1, 'class_id': 1, 'class_name': 'c', 'level': 'gcse', 'subject': 'maths', 'topic': 'geometry_angles', 'mode': 'standard',
            'difficulty': 'foundational', 'question_count': 3, 'status': 'assigned',
            'problems': [straight, straight, straight], 'answers': [None, {'user_answer': '41', 'correct': False}, {'user_answer': '139', 'correct': True}]}
    work = serialize_student_work(data)
    unanswered, wrong, right = work['problems']
    expect('graded', 'set work', 'hint_message' not in unanswered and not ({'correct_answer_raw', 'solution', 'hint'} & set(unanswered)),
           'an unanswered question must carry no message and no key')
    expect('graded', 'set work', wrong.get('hint_message') == M.MESSAGES['ang.supplement'], f'graded wrong answer: {wrong.get("hint_message")!r}')
    expect('graded', 'set work', 'hint_message' not in right, 'a right answer carries no message')
    expect('graded', 'set work', 'answer_record' not in str(work), 'the answer record reached a set-work payload')
    data['problems'] = [frozen] * 3
    expect('graded', 'set work', 'answer_record' not in str(serialize_student_work(data)), 'the answer record reached a set-work payload (frozen)')
    expect('graded', 'set work', strip_problem_keys(straight, reveal=False).keys() & {'correct_answer_raw', 'hint', 'solution'} == set(),
           'strip_problem_keys changed')
    from flask import render_template
    with app.test_request_context('/class-work/1'):
        html = render_template('student_class_work_detail.html', work=work)
    expect('graded', 'set work page', M.MESSAGES['ang.supplement'] in html, 'the graded page does not show the message')
    expect('graded', 'set work page', html.count(M.MESSAGES['ang.supplement']) == 1, 'the message must show once, for the wrong answer only')
    work['problems'][1].pop('hint_message', None)
    with app.test_request_context('/class-work/1'):
        html = render_template('student_class_work_detail.html', work=work)
    expect('graded', 'set work page', M.MESSAGES['ang.supplement'] not in html, 'the page shows a message that is not in the payload')

    # lesson quiz API: nothing mid-quiz, the message on the results
    from app import get_db
    from models.lesson_quiz import load_lesson_quiz_session
    with app.test_client() as client:
        r = client.post('/api/v1/lesson-quiz/start', json={'level': 'gcse', 'subject': 'maths', 'topic': 'geometry_angles'})
        if r.status_code != 201:
            issue('graded', 'quiz', f'could not start a quiz: {r.status_code} {r.get_json()}')
            return
        sid = r.get_json()['session_id']
        # Every GCSE maths lesson quiz is multiple choice today, so put two typed questions into the stored session.
        from models.lesson_quiz import save_lesson_quiz_session
        with get_db() as conn:
            session_data = load_lesson_quiz_session(conn, sid)
            session_data['problems'][0] = dict(straight)
            session_data['problems'][1] = dict(straight, correct_answer_raw='139')
            save_lesson_quiz_session(conn, sid, session_data)
            session_data = load_lesson_quiz_session(conn, sid)
        problems = session_data['problems']
        expect('graded', 'quiz', all('answer_record' not in p for p in problems), 'the answer record was stored in the quiz row')
        typed = [(i, p) for i, p in enumerate(problems) if not p.get('options') and p.get('correct_answer_raw') is not None]
        expect('graded', 'quiz', bool(typed), 'no typed question in the quiz to test with')
        wanted = {}
        for i, p in enumerate(problems):
            slip = None
            if (i, p) in typed:
                raw = str(p['correct_answer_raw'])
                for trial in (M.format_answer(-Fraction(raw)) if re.fullmatch(r'-?\d+(\.\d+)?', raw) and Fraction(raw) != 0 else None,
                              '99999'):
                    if trial is None:
                        continue
                    msg = M.graded_message(p, trial, level='gcse', subject='maths', topic='geometry_angles')
                    slip = (trial, msg)
                    if msg:
                        break
            wanted[i] = slip
        for i, p in enumerate(problems):
            answer = (wanted[i] or ('A', ''))[0]
            body = client.post(f'/api/v1/lesson-quiz/{sid}/answer', json={'user_answer': answer}).get_json()
            expect('graded', f'quiz answer {i}', 'hint_message' not in str(body), 'the answer response carried a message before the results')
            if i + 1 < len(problems):
                q = client.get(f'/api/v1/lesson-quiz/{sid}/question').get_json()
                expect('graded', f'quiz question {i + 1}', 'hint_message' not in str(q), 'a question carried a message')
        res = client.get(f'/api/v1/lesson-quiz/{sid}/results').get_json()
        entries = res.get('problems') or []
        expect('graded', 'quiz results', len(entries) == len(problems), 'results are missing questions')
        shown = 0
        for i, e in enumerate(entries):
            msg = (wanted[i] or (None, ''))[1]
            if wanted[i] is None and problems[i].get('options'):
                # a multiple-choice question shows the note of the option picked (Phase 4), or nothing when it has none
                from generators.shared import option_notes as _ON
                msg = _ON.picked_note(problems[i], 'A')
            if e.get('was_correct'):
                expect('graded', f'quiz result {i}', 'hint_message' not in e, 'a right answer carries a message')
            else:
                expect('graded', f'quiz result {i}', e.get('hint_message', '') == msg, f'message {e.get("hint_message")!r}, wanted {msg!r}')
                shown += bool(e.get('hint_message'))
            expect('graded', f'quiz result {i}', 'answer_record' not in e, 'the answer record reached the results')
        print(f'  lesson quiz: {len(problems)} questions, {len(typed)} typed, {shown} with a generic message on the results')
    # the results page renders the line for a wrong answer only
    from app import _render_quiz_results
    with app.test_request_context('/lesson-quiz/gcse/maths/geometry_angles/results'):
        page = _render_quiz_results(
            [dict(straight, user_answer='41', answered_correctly=False, score=0, score_total=1, hint_message=M.MESSAGES['ang.supplement']),
             dict(straight, user_answer='139', answered_correctly=True, score=1, score_total=1, hint_message=M.MESSAGES['ang.supplement'])],
            1, 2, 'Angles', '/lesson', 'gcse', 'maths', 'geometry_angles', show_wrong_explanations_only=False, can_retry_wrong=False,
        )
    expect('graded', 'results page', page.count(M.MESSAGES['ang.supplement']) == 1, 'the line must show once, for the wrong answer only')
    # only the graded paths build a message
    src = read('app.py')
    expect('graded', 'routes', src.count('graded_message(') == 2, 'graded_message is called from the two lesson-quiz results routes only')


# ─────────────────────────────────────────────────────────────────────────────
# client: bytes, pins, script pieces
# ─────────────────────────────────────────────────────────────────────────────

def check_client():
    js = ROOT / 'static/js/site.js'
    n = js.stat().st_size
    expect('client', 'site.js', n <= SITE_JS_MAX_BYTES, f'site.js is {n} B, cap {SITE_JS_MAX_BYTES} (baseline {SITE_JS_BASE_BYTES} plus {SITE_JS_PHASE3_MAX_ADD}, {SITE_JS_PHASE4_MAX_ADD}, {SITE_JS_CARD_MAX_ADD})')
    css = ROOT / 'static/css/practice.css'
    c = css.stat().st_size
    css_cap = PRACTICE_CSS_BASE_BYTES + PRACTICE_CSS_PHASE3_MAX_ADD + PRACTICE_CSS_CARD_MAX_ADD + PRACTICE_CSS_NOTE_MAX_ADD
    expect('client', 'practice.css', c <= css_cap, f'practice.css is {c} B, cap {css_cap}')
    sheets = sorted((ROOT / 'static/css').glob('*.css'))
    total = sum(p.stat().st_size for p in sheets)
    lesson_only = {'lesson-pages.css', 'lesson-assist.css', 'stage.css', 'coach.css', 'badge-stage.css', 'moments.css', 'tour.css', 'wardrobe.css', 'around.css', 'story.css'}  # 2026-11-08: E10 phase 6b wardrobe.css is on demand;      # as test_u8_a11y_smoke.LESSON_ONLY (2026-11-08: E10 stage.css is on demand)
    core = sum(p.stat().st_size for p in sheets if p.name not in lesson_only)
    expect('client', 'css total', total <= TOTAL_CSS_CAP, f'total CSS {total} B, cap {TOTAL_CSS_CAP}')
    expect('client', 'css core', core <= CORE_CSS_CAP, f'core CSS {core} B, cap {CORE_CSS_CAP}')
    # cache pins
    base = read('templates/base.html')
    expect('client', 'pins', "js/site.js') }}?v=40" in base, 'site.js must be ?v=40')
    expect('client', 'pins', "css/practice.css') }}?v=32" in base, 'practice.css must be ?v=32')
    expect('client', 'pins', "css/pages.css') }}?v=59" in base, 'pages.css must be ?v=59 (2026-11-08: E10 phase 7 fixed the results ring token)')
    expect('client', 'pins', f"CACHE_VERSION = '{SERVICE_WORKER_CACHE}'" in read('static/js/sw.js'), f'sw.js must be {SERVICE_WORKER_CACHE}')
    # review A6: a failed check (stale tab, lost session, network) must unlock Show answer in every check catch
    js_lines = read('static/js/site.js').split('\n')
    guarded = 0       # six check catches today: proof field, order field, mcq field, number field, proof steps, main box
    for i, line in enumerate(js_lines):
        if '.catch(function (err) {' in line and any("'Could not check answer.'" in l for l in js_lines[i + 1:i + 20]):
            ok = js_lines[i + 1].strip() == 'unlockAnswer();'
            expect('client', 'unlock on error', ok, f'site.js line {i + 1}: a check catch does not call unlockAnswer() first')
            guarded += ok
    expect('client', 'unlock on error', guarded >= 6, f"only {guarded} guarded check catches (want at least 6)")
    # the three em dashes in the answer strings are gone (D7 leftovers)
    text = js.read_text(encoding='utf-8')
    for line_no, line in enumerate(text.split('\n'), 1):
        if re.search(r"(?:[Ff]eedback\.textContent = |\|\| )'[^']*(?:Correct|Not quite)[^']*'", line) and '\\u2014' in line:
            issue('client', f'site.js:{line_no}', 'an em dash in an answer string')
    expect('client', 'site.js', 'Not quite \\u2014' not in text, 'a "Not quite" string still has an em dash')
    # pieces of the ladder that must stay
    for needle, why in (
        ("body.hint_ladder = true", 'the check request must ask for the ladder only where the block has one'),
        ("function unlockAnswer()", 'one place opens the drawer'),
        ("details.answer-reveal[data-locked]", 'only a locked drawer is touched'),
        ("n.textContent = n.getAttribute('data-open')", 'the status note announces the unlock'),
        ("d.firstElementChild.removeAttribute('aria-disabled')", 'the unlocked bar is no longer aria-disabled'),
        ("details[data-locked] > summary", 'a click on the greyed bar is cancelled'),
        ("h.kind === 'misconception' ? (data.feedback", 'the named slip goes in the card, not the red line'),
        ("h.bigger !== text", 'a bigger hint equal to rung 1 is never offered (no duplicate text)'),
        ("data.hint.kind === 'misconception' && block.querySelector('.free-response-hint')", 'the red line is short only where the card shows the slip'),
        ("'% of attempts needed another go ('", 'D8 wording'),
        ("if (hinted && pct < 20) return '';", 'D8 (review): no "only a few needed another go" line straight after a miss'),
        ("host.dataset.hintRung", 'D8 follows the rung'),
        ("more.setAttribute('aria-disabled', 'true')", 'the pressed button is aria-disabled, never disabled or removed (keyboard focus stays on it)'),
        ("unlockAnswer();\n        var isCorrect", 'a multiple choice pick opens the drawer (D1b)'),
    ):
        expect('client', 'site.js', needle in text, why)
    expect('client', 'site.js', text.count('showHintLadder(') == 5, 'the ladder is shown after a typed check, a part check, a proof check and a completed multi-part answer')
    expect('client', 'focus', 'focus()' not in text[text.index('function showHintLadder'):text.index('function onHintMore')],
           'the ladder must not take focus')
    ladder_js = text[text.index('function unlockAnswer'):text.index('function persistMcqAnswer')]
    for words in M.LADDER_COPY.values():
        expect('client', 'site.js', f"'{words}'" not in ladder_js, f'the ladder script holds the copy {words!r}; it belongs in LADDER_COPY')
    css_text = css.read_text(encoding='utf-8')
    expect('client', 'css', '.free-response-hint-more[hidden]' in css_text, 'a hidden .btn is display:none only with this rule')
    card_css = css_text[css_text.index('/* Hint card'):css_text.index('.mcq-options {')]
    expect('client', 'css', 'animation' not in card_css and 'transition' not in card_css, 'the card and the locked bar add no motion')
    expect('client', 'css', '--hint-bg' in card_css and '--hint-border' in card_css and '--on-streak' in card_css
           and not re.search(r'#[0-9a-fA-F]{3,8}\b', card_css), 'the card uses the site hint tokens, no hard-coded colour')
    expect('client', 'css', '[data-locked]' in card_css, 'the greyed Show answer bar needs its style')
    expect('client', 'pages.css', 'practice-hint' not in read('static/css/pages.css'), 'the Hint drawer styles are gone')
    expect('client', 'css', 'style=' not in read('templates/partials/free_response_inline.html').split('free-response-hint"')[1].split('</button>')[0],
           'no inline style in the ladder markup')


# ─────────────────────────────────────────────────────────────────────────────

def main():
    from app import app
    check_template(app)
    check_route(app)
    check_ladder_cases()
    check_ladder_review_cases()
    n, with_big, from_hint, repeats = check_ladder_slots()
    check_graded(app)
    check_client()
    elapsed = time.time() - START
    print(f'GCSE maths hint ladder (Phase 3): {n} typed practice slots checked, {with_big} have a rung 2 step '
          f'({with_big / max(n, 1):.0%}; {repeats} more dropped as repeats of rung 1), {from_hint} use the problem hint as rung 1, {elapsed:.1f}s (budget {BUDGET_SECONDS:g}s)')
    js = (ROOT / 'static/js/site.js').stat().st_size
    css = (ROOT / 'static/css/practice.css').stat().st_size
    print(f'  site.js {js} B (+{js - SITE_JS_BASE_BYTES}, cap {SITE_JS_MAX_BYTES}); practice.css {css} B (+{css - PRACTICE_CSS_BASE_BYTES}, '
          f'cap +{PRACTICE_CSS_PHASE3_MAX_ADD + PRACTICE_CSS_CARD_MAX_ADD + PRACTICE_CSS_NOTE_MAX_ADD})')
    if ISSUES:
        for check, lines in ISSUES.items():
            print(f'FAIL {check}: {len(lines)}')
            for line in lines[:12]:
                print(f'  {line}')
            if len(lines) > 12:
                print(f'  ... and {len(lines) - 12} more')
        sys.exit(1)
    if elapsed > BUDGET_SECONDS * 2:
        print(f'FAIL budget: {elapsed:.1f}s')
        sys.exit(1)
    print('GCSE maths hint ladder smoke (Phase 3) passed.')


if __name__ == '__main__':
    main()
