"""E9 Zorp voice: rules, copy extractor, reading level and the generated inventory.

Spec: docs/ZORP_CHARM.md section 3.3 (voice and the mechanical rules) and Appendix A (the inventory
this module generates between the COPY-INVENTORY markers). Pure Python, standard library only, no
import of the app: it reads the source files as text (JavaScript by regex, Python by `ast`, Jinja
templates by a small tolerant HTML scanner).

`extract()` lists every line Zorp (and the system voice beside him) says, `lint()` returns rule
violations, `reading_levels()` measures the Flesch-Kincaid numbers, and `render_inventory()` /
`update_doc()` regenerate Appendix A. Since Phase 3 scripts/test_zorp_voice_smoke.py ENFORCES the
rules: any `error` or unjustified `warn` fails the build (`info` notes are only listed).

Voices (section 3.3.2): `zorp` (first person allowed) and `system` (no "I", no character).

Templates mark every line they own with `data-zorp-voice="<voice>:<surface>[:dismiss]"`, for example
`data-zorp-voice="zorp:welcome_line"`, `data-zorp-voice="system:button_label"` or, for the text of an
attribute, `data-zorp-voice="system:system_badge@aria-label"`. `<surface>` is a key of SURFACE_NAMES;
`:dismiss` marks a dismissal label (checked for neutral wording). The scan reads every file under
templates/ that carries the attribute. JavaScript and Python sources are read by the extractors below.

Add a source: mark the template line, or write an extractor, call it from `extract()`, and run
`python scripts/test_zorp_voice_smoke.py --write` to regenerate the appendix.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / 'docs' / 'ZORP_CHARM.md'
MARK_BEGIN = '<!--COPY-INVENTORY-BEGIN-->'
MARK_END = '<!--COPY-INVENTORY-END-->'

# ---------------------------------------------------------------------------------------------
# Rules (section 3.3.4)
# ---------------------------------------------------------------------------------------------

# 30 characters exactly: the worst-case topic label a corner message is rendered with.
SAMPLE_TOPIC = 'Electric fields and potentials'
SAMPLES = {
    'topic_label': SAMPLE_TOPIC,
    'topic': SAMPLE_TOPIC,
    'handle': 'mia_k_class1',
    'score': '7',
    'total': '10',
    'days': '7',
    'cs': '7',
    'os_': '5',
    'title': 'Week warrior',
    'emoji': '\U0001F3C5',
    'class_name': 'Year 9 Physics',
}
PLACEHOLDER_SAMPLE = 'Sam'  # stands in for a Jinja expression with no literal fallback

# Per-surface length limits in characters (None: no limit set by the plan).
LIMITS = {
    'guide_line': 100,
    'reward_line': 80,
    'corner_message': 100,
    'button_label': 22,
    'detail_label': 20,
    'welcome_line': 70,
}
SURFACE_NAMES = {
    'guide_line': 'Guide line',
    'reward_line': 'Reward line',
    'corner_message': 'Corner message',
    'button_label': 'Button label',
    'detail_label': 'Bubble detail label',
    'welcome_line': 'Welcome line',
    'bot_note': 'Bot note',
    'spot_label': 'Tour spot label',
    'heading': 'Heading',
    'system_notification': 'Notification',
    'system_empty_state': 'Empty state',
    'system_offline': 'Offline page',
    'system_banner': 'PWA banner',
    'system_badge': 'Tab badge label',
    'system_feedback': 'Answer feedback',
    'system_settings': 'Settings copy',
    'system_toast': 'Toast',
    'system_bot': 'Bot card',
}
# Surfaces that hold a button, tag or heading rather than a sentence (kind 'label': no reading level).
LABEL_SURFACES = frozenset({'button_label', 'detail_label', 'spot_label', 'heading'})


def kind_of(surface):
    return 'label' if surface in LABEL_SURFACES else 'line'


# Banned phrases (case-insensitive; apostrophes normalised first). The two streak ones are
# contextual: "lost" and "break" (also "broke", "broken") are only banned when the same sentence
# mentions a streak, before or after the word.
BANNED_PHRASES = (
    (r"\blost\b(?=[^.!?]*\bstreak)|\bstreak[^.!?]*\blost\b", 'lost (your streak)'),
    (r"\b(?:break(?:ing|s)?|broken?)\b(?=[^.!?]*\bstreak)|\bstreak[^.!?]*\b(?:break(?:ing|s)?|broken?)\b",
     'break (your streak)'),
    (r"\bat risk\b", 'at risk'),
    # Final audit B2 (2026-10-12): the spec's Do/Don't table also bans urgency, a streak that ends and comparison.
    (r"\bbefore midnight\b", 'before midnight'),
    (r"\btonight\b", 'tonight'),
    (r"\bstreak[^.!?]*\b(?:resets?|ends?|gone)\b|\b(?:resets?|ends?|gone)\b[^.!?]*\bstreak", 'streak resets / ends / gone'),
    (r"\bahead of you\b", 'ahead of you'),
    (r"\bdon't miss\b", "don't miss"),
    (r"\blast chance\b", 'last chance'),
    (r"\bhurry\b", 'hurry'),
    (r"\bbefore it's too late\b", "before it's too late"),
    (r"\bcome back\b", 'come back'),
    (r"\bmiss(?:ed)? you\b", 'miss you / missed you'),
    (r"\bi'm sad\b", "I'm sad"),
    (r"\bdisappointed\b", 'disappointed'),
    (r"\bfailed\b", 'failed'),
    (r"\byou forgot\b", 'you forgot'),
    (r"\bonly \d+ left\b", 'only N left'),
    (r"\beveryone else\b", 'everyone else'),
    (r"\bfriends are ahead\b", 'friends are ahead'),
    (r"\beasy\b", 'easy'),
    (r"\bobviously\b", 'obviously'),
    (r"\bsimply\b", 'simply'),
    (r"\blazy\b", 'lazy'),
)
# Warn level: allowed when the source line carries a `voice-ok` justification comment.
WARN_PHRASES = (
    (r"\bjust\b", 'just'),
    (r"\b(?:don't|do not) worry\b", "don't worry"),
)
# "lose / losing" is loss wording, but physics says it plainly ("friction makes the ball lose energy"): the ban is
# per sentence and lifted when the sentence names a physics quantity.
LOSE_RE = r"\blos(?:e|es|ing)\b"
PHYSICS_TERMS = r"\b(?:energy|mass|charge|heat|friction|momentum|force|speed|velocity|current|voltage|power|pressure|temperature)\b"
# "behind" compares the pupil with others (spec 3.3.3): banned in Zorp's voice only.
BEHIND_RE = r"\bbehind\b"
US_SPELLINGS = (
    (r"\bcolors?\b", 'color'),
    (r"\bfavorites?\b", 'favorite'),
    (r"\bcenters?\b", 'center'),
    (r"\bbehaviors?\b", 'behavior'),
    (r"\banalyz\w*", 'analyze'),
    (r"\borganiz\w*", 'organize'),
    (r"\brealiz\w*", 'realize'),
    (r"\brecogniz\w*", 'recognize'),
    (r"\bpracticing\b", 'practicing'),
    (r"\blicense\b", 'license (noun)'),
    (r"\bmath\b", 'math'),
    (r"\bgotten\b", 'gotten'),
    (r"\bmom\b", 'mom'),
)
# "practise" is the verb, "practice" the noun (section 3.3.4).
PRACTISE_VERB = r"\b(?:to practice|practice this|practice a)\b"
# Glossary (3.3.4): terms Zorp does not use, with the preferred wording.
GLOSSARY_BAD = (
    (r"\bfreeze\b", 'say "streak skip" (profile.html uses "skip")'),
    (r"\bdms?\b", 'say "chat" (3.3.6)'),
)
GLOSSARY_WARN = (
    (r"\bhabit\b", 'streak copy should not frame a habit'),
)
FIRST_PERSON = r"\b(?:i|i'm|i'll|i've|i'd|my|me|we|our|us)\b"
# The system voice has no "I" (3.3.2); "we", "our" and "us" (the Problem Bank) are fine there.
SYSTEM_FIRST_PERSON = r"\b(?:i|i'm|i'll|i've|i'd|my|me)\b"
EMOJI_RE = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B50\u2B55\uFE0F\u200D]')
DASH_RE = re.compile('[\u2013\u2014]|(?<=\\s)-(?=\\s)')   # an em or en dash, or a spaced hyphen standing in for one
FK_MAX_LINE = 8.0
# D11 (2026-10-04): the per-line grade limit applies only to lines of this many words or more.
# The long-word check and the mean grade still cover every line.
FK_MIN_WORDS_LINE = 8
FK_MAX_MEAN = 5.0
EXCLAIM_MAX_SHARE = 0.25  # at most one Zorp line in four carries a "!"
# Words of 4+ syllables are allowed only from this list (physics terms and placeholders).
LONG_WORD_ALLOW = frozenset({
    'electromagnetic', 'electromagnetism', 'thermodynamics', 'acceleration', 'gravitational',
    'photosynthesis', 'conservation', 'temperature', 'velocity', 'resistance', 'multiplication',
    'accuracy',  # the name of a leaderboard tab in the UI ("Effort" and "Accuracy"), so the line must say it
})
# Dismissal labels (3.3.3): neutral, never confirmshaming. A new label needs a deliberate edit here.
DISMISS_APPROVED = frozenset({'Not now', 'Skip intro', 'Keep learning', 'Skip for now'})
SHAMING = (r"\bno thanks\b", r"^no\b", r"\bi don't\b", r"\bi'd rather\b", r"\bnever mind\b",
           r"\bnot interested\b", r"\bgive up\b", r"\bi'll pass\b", r"\bnot for me\b")


# ---------------------------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Item:
    path: str          # repo-relative source file
    line: int          # 1-based line in that file (0 when unknown)
    voice: str         # 'zorp' | 'system'
    surface: str       # key of SURFACE_NAMES
    kind: str          # 'line' (a sentence Zorp says), 'label' (button, heading, tag)
    text: str          # rendered text (f-strings use SAMPLES)
    template: str = ''  # source form when it differs from `text`
    where: str = ''    # step id, reward key, selector
    justified: bool = False  # the source line carries a `voice-ok` comment
    dismiss: bool = False    # a dismissal label (Not now, Skip intro, the stay label): checked for neutral wording

    @property
    def ref(self):
        return f'{self.path}:{self.line}' if self.line else self.path


@dataclass(frozen=True)
class Violation:
    item: Item
    rule: str
    detail: str
    level: str  # 'error' | 'warn' | 'info'


def _norm(text):
    return text.replace('\u2019', "'").replace('\u2018', "'").lower()


def length_limit(item):
    return LIMITS.get(item.surface)


# ---------------------------------------------------------------------------------------------
# Reading level
# ---------------------------------------------------------------------------------------------

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['\u2019-][A-Za-z0-9]+)*")


def syllables(word):
    """Vowel groups, minus a silent final e (kept after consonant + le), minimum 1; a number is 1."""
    w = re.sub(r'[^a-z0-9]', '', word.lower())
    if not w:
        return 0
    if w.isdigit():
        return 1
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and n > 1 and not re.search(r'[^aeiouy]le$', w):
        n -= 1
    return max(1, n)


def words_of(text):
    return _WORD_RE.findall(text)


def sentence_count(text):
    return max(1, len(re.findall(r'[.!?]+(?=\s|$)', text.strip())))


def flesch_kincaid(text):
    """Flesch-Kincaid grade level: 0.39 * words/sentence + 11.8 * syllables/word - 15.59."""
    words = words_of(text)
    if not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / sentence_count(text) + 11.8 * syl / len(words) - 15.59


def long_words(text):
    """Words of four or more syllables that are not on the allowlist."""
    out = []
    for w in words_of(text):
        if syllables(w) >= 4 and re.sub(r"[^a-z]", '', w.lower()) not in LONG_WORD_ALLOW:
            out.append(w)
    return out


def zorp_lines(items):
    return [i for i in items if i.voice == 'zorp' and i.kind == 'line']


def reading_levels(items):
    """{'per_line': [(item, grade)], 'mean', 'pooled', 'max', 'n'} over all Zorp lines."""
    lines = zorp_lines(items)
    per = [(i, flesch_kincaid(i.text)) for i in lines]
    grades = [g for _, g in per]
    limited = [g for i, g in per if len(words_of(i.text)) >= FK_MIN_WORDS_LINE]
    all_text = ' '.join(i.text for i in lines)
    return {
        'per_line': per,
        'mean': sum(grades) / len(grades) if grades else 0.0,
        'pooled': flesch_kincaid(all_text) if lines else 0.0,
        'max': max(grades) if grades else 0.0,
        'max_limited': max(limited) if limited else 0.0,
        'n': len(lines),
    }


def exclamation_share(items):
    lines = zorp_lines(items)
    if not lines:
        return 0.0
    return sum(1 for i in lines if '!' in i.text) / len(lines)


# ---------------------------------------------------------------------------------------------
# Lint
# ---------------------------------------------------------------------------------------------

def lint(items):
    """Every rule violation. System-voice items get the first-person, banned-phrase, spelling and
    "practise" rules (3.3.2, 3.3.4); emoji and dashes in system strings are listed as `info` (house
    style, not a Zorp rule). Zorp items get every rule. Levels: `error` fails, `warn` fails unless the
    source line carries a `voice-ok` comment, `info` is listed only."""
    out = []
    for it in items:
        low = _norm(it.text)
        for pat, name in BANNED_PHRASES:
            if re.search(pat, low):
                out.append(Violation(it, 'banned phrase', name, 'error'))
        if any(re.search(LOSE_RE, sent) and not re.search(PHYSICS_TERMS, sent) for sent in re.split(r'(?<=[.!?])\s+', low)):
            out.append(Violation(it, 'banned phrase', 'lose / losing', 'error'))
        if it.voice == 'zorp' and re.search(BEHIND_RE, low):
            out.append(Violation(it, 'banned phrase', 'behind (compares the pupil with others)', 'error'))
        for pat, name in US_SPELLINGS:
            if re.search(pat, low):
                out.append(Violation(it, 'US spelling', name, 'error'))
        if re.search(PRACTISE_VERB, low):
            out.append(Violation(it, 'practise verb', 'the verb is "practise"', 'error'))
        if it.dismiss:
            if re.search(FIRST_PERSON, low) or any(re.search(p, low) for p in SHAMING):
                out.append(Violation(it, 'dismiss label', 'a dismissal must be neutral (3.3.3)', 'error'))
            if it.text not in DISMISS_APPROVED:
                out.append(Violation(it, 'dismiss label', f'{it.text!r} is not an approved dismissal label (DISMISS_APPROVED)', 'error'))
        if it.voice == 'system':
            if re.search(SYSTEM_FIRST_PERSON, low):
                out.append(Violation(it, 'system voice', 'first person in the system voice', 'error'))
            for rx, what in ((EMOJI_RE, 'emoji or symbol'), (DASH_RE, 'em or en dash')):
                if rx.search(it.text):
                    out.append(Violation(it, 'house style', f'{what} in a system string (listed, not a Zorp rule)', 'info'))
            continue
        for pat, name in WARN_PHRASES:
            if re.search(pat, low) and not it.justified:
                out.append(Violation(it, 'warn phrase', f'{name} (needs a voice-ok comment)', 'warn'))
        for pat, advice in GLOSSARY_BAD:
            if re.search(pat, low):
                out.append(Violation(it, 'glossary', advice, 'error'))
        for pat, advice in GLOSSARY_WARN:
            if re.search(pat, low) and not it.justified:
                out.append(Violation(it, 'glossary', advice, 'warn'))
        if EMOJI_RE.search(it.text):
            out.append(Violation(it, 'characters', 'emoji', 'error'))
        if DASH_RE.search(it.text):
            out.append(Violation(it, 'characters', 'em or en dash', 'error'))
        if it.text.count('!') > 1:
            out.append(Violation(it, 'exclamation', 'more than one "!" in a line', 'error'))
        limit = length_limit(it)
        if limit is not None and len(it.text) > limit:
            out.append(Violation(it, 'length', f'{len(it.text)} characters, limit {limit} for a {SURFACE_NAMES[it.surface].lower()}', 'error'))
        if it.kind == 'line':
            grade = flesch_kincaid(it.text)
            if grade > FK_MAX_LINE and len(words_of(it.text)) >= FK_MIN_WORDS_LINE:
                out.append(Violation(it, 'reading level', f'grade {grade:.1f}, limit {FK_MAX_LINE:g}', 'error'))
            for w in long_words(it.text):
                out.append(Violation(it, 'long word', f'"{w}" has four or more syllables and is not on the allowlist', 'error'))
    levels = reading_levels(items)
    if levels['n'] and levels['mean'] > FK_MAX_MEAN:
        out.append(Violation(Item('(inventory)', 0, 'zorp', 'guide_line', 'line', ''), 'reading level',
                             f"mean grade {levels['mean']:.1f} over {levels['n']} lines, limit {FK_MAX_MEAN:g}", 'error'))
    share = exclamation_share(items)
    if share > EXCLAIM_MAX_SHARE:
        out.append(Violation(Item('(inventory)', 0, 'zorp', 'guide_line', 'line', ''), 'exclamation',
                             f'{share:.0%} of Zorp lines carry a "!", limit {EXCLAIM_MAX_SHARE:.0%}', 'error'))
    return out


# ---------------------------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------------------------

def _read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def js_unescape(raw):
    def sub(m):
        s = m.group(1)
        if s[0] == 'u' and len(s) == 5:
            return chr(int(s[1:], 16))
        return {'n': '\n', 't': '\t'}.get(s, s)
    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", sub, raw)


_JS_STR = re.compile(r"'((?:[^'\\]|\\.)*)'")


def js_strings(segment):
    return [js_unescape(m.group(1)) for m in _JS_STR.finditer(segment)]


def _has_voice_ok(source_line):
    return 'voice-ok' in source_line


def _array_strings(src, start_line, start_col):
    """Single-quoted strings of a JS array literal that opens at src[start_line][start_col:].
    -> ([(1-based line, decoded string)], index of the line holding the closing bracket or None)."""
    out = []
    in_str, buf, str_line = False, [], 0
    for li in range(start_line, len(src)):
        text = src[li]
        k = start_col if li == start_line else 0
        while k < len(text):
            ch = text[k]
            if in_str:
                if ch == '\\':
                    buf.append(text[k:k + 2])
                    k += 2
                    continue
                if ch == "'":
                    out.append((str_line, js_unescape(''.join(buf))))
                    in_str, buf = False, []
                else:
                    buf.append(ch)
            elif ch == "'":
                in_str, str_line = True, li + 1
            elif ch == '/' and text[k:k + 2] == '//':
                break  # line comment: an apostrophe in it must not open a string
            elif ch in '"`':
                raise ValueError(f'line {li + 1}: only single-quoted strings are read in a lines array')
            elif ch == ']':
                return out, li
            k += 1
    return out, None


def extract_guide_catalog(path='static/js/guide-catalog.js'):
    """Lines and labels of the catalog, in file order, by regex over a line scan."""
    src = _read(path).split('\n')
    items, errors = [], []
    section = None      # 'origin' | 'tours' | 'rewards'
    group = ''          # tour name
    step = ''           # step id or reward key
    i = 0
    blocks_seen = 0
    lines_tokens = sum(1 for ln in src if re.match(r'\s*lines:\s*\[', ln))
    while i < len(src):
        ln = src[i]
        n = i + 1
        s = ln.strip()
        if re.match(r'origin:\s*\[', s):
            section, group = 'origin', ''
        elif re.match(r'tours:\s*\{', s):
            section, group = 'tours', ''
        elif re.match(r'rewards:\s*\{', s):
            section, group = 'rewards', ''
        elif section == 'tours' and re.match(r"^\s{6}\w+:\s*\[$", ln):
            group = s.split(':')[0]
        elif section == 'rewards' and re.match(r"^\s{6}'?[\w:]+'?:\s*\{$", ln):
            step = re.match(r"'?([\w:]+)'?", s).group(1)
        m = re.match(r"id:\s*'([^']+)'", s)
        if m:
            step = m.group(1)
        if re.match(r'lines:\s*\[', s):
            blocks_seen += 1
            surface = 'reward_line' if section == 'rewards' else 'guide_line'
            try:
                strings, end = _array_strings(src, i, ln.index('[') + 1)
            except ValueError as err:
                errors.append(f'{path}:{n}: {err}')
                strings, end = None, i
            if strings is None:
                strings = []
            elif end is None:
                errors.append(f'{path}:{n}: unterminated lines array')
                end = i
            elif not strings:
                errors.append(f'{path}:{n}: lines array yielded no strings')
            for lineno, t in strings:
                items.append(Item(path, lineno, 'zorp', surface, 'line', t, where=step,
                                  justified=_has_voice_ok(src[lineno - 1])))
            i = end
        else:
            for key, surface, kind in (('primary', 'button_label', 'label'), ('skipLabel', 'button_label', 'label'),
                                       ('spotLabel', 'spot_label', 'label'), ('heading', 'heading', 'label')):
                mm = re.match(rf"{key}:\s*'((?:[^'\\]|\\.)*)'", s)
                if mm:
                    items.append(Item(path, n, 'zorp', surface, kind, js_unescape(mm.group(1)), where=f'{step} {key}'.strip(),
                                      dismiss=key == 'skipLabel'))
        i += 1
    if not items:
        errors.append(f'{path}: nothing extracted')
    if blocks_seen != lines_tokens:
        errors.append(f'{path}: parsed {blocks_seen} of {lines_tokens} lines arrays')
    return items, errors


def _js_concat(expr, env):
    """Render a JS `a + 'b' + c` expression -> (rendered, template); names come from env."""
    out, tpl = [], []
    for part in re.split(r"\s\+\s", expr.strip()):
        part = part.strip()
        m = _JS_STR.fullmatch(part)
        if m:
            out.append(js_unescape(m.group(1)))
            tpl.append(js_unescape(m.group(1)))
        elif part in env:
            out.append(env[part])
            tpl.append('{' + part + '}')
        else:
            raise ValueError(f'unknown name {part!r} in {expr!r}')
    return ''.join(out), ''.join(tpl)


def extract_guide_js(path='static/js/guide.js'):
    """Reward fallbacks and headings baked into guide.js (buildRewardStep, renderStep)."""
    text = _read(path)
    items, errors = [], []

    def line_of(pos):
        return text.count('\n', 0, pos) + 1

    def add(pos, surface, kind, rendered, where, template=''):
        ln = line_of(pos)
        items.append(Item(path, ln, 'zorp', surface, kind, rendered, template=template, where=where,
                          justified=_has_voice_ok(text.split('\n')[ln - 1])))

    found = 0
    for m in re.finditer(r"template\.lines \|\| \[(.*?)\],\n", text):
        expr = m.group(1)
        try:
            rendered, tpl = _js_concat(expr, {'n': SAMPLES['days']})
        except ValueError as err:
            errors.append(f'{path}:{line_of(m.start())}: {err}')
            continue
        add(m.start(), 'reward_line', 'line', rendered, 'fallback line', template=tpl if tpl != rendered else '')
        found += 1
    if found != 3:
        errors.append(f'{path}: expected 3 reward fallback lines, found {found}')
    heads = 0
    for pat, where in ((r"title: title \|\| '([^']*)'", 'milestone fallback heading'),
                       (r"heading: n \+ '([^']*)'", 'streak heading'),
                       (r"\? 'First correct' : 'Lesson complete'", 'first correct / lesson complete headings'),
                       (r"\? 'Well done' : 'Zorp'", 'reward / default headings')):
        m = re.search(pat, text)
        if not m:
            errors.append(f'{path}: heading pattern {where!r} not found')
            continue
        if where == 'streak heading':
            add(m.start(), 'heading', 'label', SAMPLES['days'] + m.group(1), where, template='{n}' + m.group(1))
            heads += 1
        elif m.groups():
            add(m.start(), 'heading', 'label', m.group(1), where)
            heads += 1
        else:
            for lit in js_strings(m.group(0)):
                add(m.start(), 'heading', 'label', lit, where)
                heads += 1
    for m in re.finditer(r"\.primary \|\| '([^']*)'", text):
        add(m.start(), 'button_label', 'label', m.group(1), 'primary fallback')
    return items, errors


# ---- Python (ast) -----------------------------------------------------------------------------

class _NoSample(Exception):
    pass


def _render_expr(node):
    """(rendered, template) for a FormattedValue's expression."""
    if isinstance(node, ast.Name):
        if node.id not in SAMPLES:
            raise _NoSample(f'no sample value for {node.id!r}')
        return SAMPLES[node.id], '{' + node.id + '}'
    if isinstance(node, ast.Constant):
        return str(node.value), str(node.value)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get'
            and len(node.args) == 2 and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[1], ast.Constant)):
        key = str(node.args[0].value)
        sample = SAMPLES['handle'] if 'handle' in key else str(node.args[1].value)
        return sample, '{' + ast.unparse(node) + '}'
    raise _NoSample(f'cannot render {ast.unparse(node)!r}')


def _variants(node):
    """Every string a message expression can produce: [(rendered, template)] or None if not a literal."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [(node.value, node.value)]
    if isinstance(node, ast.JoinedStr):
        rendered, template = [], []
        for part in node.values:
            if isinstance(part, ast.Constant):
                rendered.append(part.value)
                template.append(part.value)
            elif isinstance(part, ast.FormattedValue):
                r, t = _render_expr(part.value)
                rendered.append(r)
                template.append(t)
        return [(''.join(rendered), ''.join(template))]
    if isinstance(node, ast.IfExp):
        a, b = _variants(node.body), _variants(node.orelse)
        return (a or []) + (b or []) or None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = _variants(node.left), _variants(node.right)
        if a is None and b is None:
            return None
        if a is None or b is None:  # 'text ' + name: a message we cannot render must not vanish silently
            raise _NoSample(f'cannot render {ast.unparse(node)!r} (concatenation with a non-literal)')
        return [(ra + rb, ta + tb) for ra, ta in a for rb, tb in b]
    return None


def _py_items(path, tree, voice, surface_for, src_lines):
    items, errors = [], []
    for node, surface, *extra in surface_for(tree):
        try:
            variants = _variants(node)
        except _NoSample as err:
            errors.append(f'{path}:{node.lineno}: {err}')
            continue
        if not variants:
            continue
        for rendered, template in variants:
            items.append(Item(path, node.lineno, voice, surface, kind_of(surface), rendered,
                              template=template if template != rendered else '',
                              justified=_has_voice_ok(src_lines[node.lineno - 1]),
                              dismiss=bool(extra and extra[0])))
    return items, errors


def extract_buddy(path='models/buddy.py'):
    """Corner bubble messages, detail labels and action labels from models/buddy.py (ast)."""
    src = _read(path)
    tree = ast.parse(src)
    keymap = {'message': 'corner_message', 'detail': 'detail_label', 'action_label': 'button_label', 'label': 'button_label'}

    def pairs(t):
        for node in ast.walk(t):
            if isinstance(node, ast.Dict):
                # {'kind': 'stay', 'label': ...} is the dismissal ("Keep learning", D10)
                stay = any(isinstance(k, ast.Constant) and k.value == 'kind' and isinstance(v, ast.Constant)
                           and v.value == 'stay' for k, v in zip(node.keys, node.values))
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value in keymap:
                        yield v, keymap[k.value], stay and k.value == 'label'
            elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id == 'message':
                yield node.value, 'corner_message'

    items, errors = _py_items(path, tree, 'zorp', pairs, src.split('\n'))
    items.sort(key=lambda i: (i.line, i.text))
    if not items:
        errors.append(f'{path}: nothing extracted')
    return items, errors


def extract_notifications(path='app.py'):
    """The notification message strings of _serialize_notification_item (system voice)."""
    src = _read(path)
    tree = ast.parse(src)
    fn = next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_serialize_notification_item'), None)
    if fn is None:
        return [], [f'{path}: _serialize_notification_item not found']

    def pairs(_):
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id == 'message':
                yield node.value, 'system_notification'

    items, errors = _py_items(path, tree, 'system', pairs, src.split('\n'))
    items.sort(key=lambda i: i.line)
    if not items:
        errors.append(f'{path}: no notification messages')
    return items, errors


# ---- Templates (data-zorp-voice scan) -----------------------------------------------------------

def jinja_text(raw):
    """Visible text candidates of a template text run: Jinja comments dropped, {{ expr }} replaced by
    its literal fallback (`or 'x'` / `else 'x'`) or a placeholder, `{% %}` tags split the run."""
    raw = re.sub(r'\{#.*?#\}', '', raw, flags=re.S)

    def expr(m):
        fb = re.search(r"\b(?:or|else)\s+'([^']*)'", m.group(1))
        return fb.group(1) if fb else '\x00'

    raw = re.sub(r'\{\{(.*?)\}\}', expr, raw, flags=re.S)
    out = []
    for seg in re.split(r'\{%.*?%\}', raw, flags=re.S):
        seg = re.sub(r'\s+', ' ', seg).strip()
        if not seg or not seg.replace('\x00', '').strip():
            continue  # empty, or only a placeholder (a name or a label that comes from data)
        out.append(seg.replace('\x00', PLACEHOLDER_SAMPLE))
    return out


_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
MARK_ATTR = 'data-zorp-voice'


class _MarkScan(HTMLParser):
    """Collects the text of every element that carries data-zorp-voice (children included)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.open = []      # [(depth, mark, line, parts)]
        self.hits = []      # (mark, line, text)
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or '') for k, v in attrs}
        mark = attrs.get(MARK_ATTR)
        if mark is not None:
            m = re.fullmatch(r'(zorp|system):(\w+)(?::(dismiss))?(?:@([\w-]+))?', mark)
            if not m or m.group(2) not in SURFACE_NAMES:
                self.errors.append(f'line {self.getpos()[0]}: bad {MARK_ATTR}="{mark}"')
            elif m.group(4):
                for t in jinja_text(attrs.get(m.group(4), '')):
                    self.hits.append((m.groups(), self.getpos()[0], t))
            elif tag in _VOID:
                self.errors.append(f'line {self.getpos()[0]}: {MARK_ATTR} on a void element <{tag}>')
            else:
                self.open.append((self.depth + 1, m.groups(), self.getpos()[0], []))
        if tag not in _VOID:
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        for _, _, _, parts in self.open:
            parts.append(data)

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        if self.open and self.open[-1][0] == self.depth:
            _, mark, line, parts = self.open.pop()
            for t in jinja_text(''.join(parts)):
                self.hits.append((mark, line, t))
        self.depth = max(0, self.depth - 1)


def marked_templates():
    """Repo-relative paths of the templates that carry data-zorp-voice."""
    out = []
    for f in sorted((ROOT / 'templates').rglob('*.html')):
        try:
            if MARK_ATTR in f.read_text(encoding='utf-8'):
                out.append(f.relative_to(ROOT).as_posix())
        except OSError:
            continue
    return out


def extract_templates():
    items, errors = [], []
    for path in marked_templates():
        parser = _MarkScan()
        try:
            parser.feed(_read(path))
            parser.close()
        except (OSError, ValueError) as err:
            errors.append(f'{path}: {err}')
            continue
        errors.extend(f'{path}: {e}' for e in parser.errors)
        if parser.open:
            errors.append(f'{path}: {len(parser.open)} {MARK_ATTR} element(s) never closed')
        for (voice, surface, dismiss, _attr), line, text in parser.hits:
            items.append(Item(path, line, voice, surface, kind_of(surface), text, where=MARK_ATTR, dismiss=bool(dismiss)))
    items.sort(key=lambda i: (i.path, i.line, i.text))
    return items, errors


# ---- Other JavaScript and Python sources ------------------------------------------------------

def extract_bot(path='models/bot.py'):
    """The Problem Bank bot's feed card and prompts (models/bot.py). The bot is a system account, not
    Zorp, so it speaks in the system voice (section 3.3.6)."""
    src = _read(path)
    tree = ast.parse(src)
    names = {'BOT_PROMPT', 'BOT_PROMPT_DONE'}

    def pairs(t):
        for node in ast.walk(t):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) \
                    and node.targets[0].id in names:
                yield node.value, 'system_bot'
            elif isinstance(node, ast.Dict):
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value == 'bot_note':
                        yield v, 'bot_note'
                    elif isinstance(k, ast.Constant) and k.value == 'card_label':
                        yield v, 'system_bot'

    items, errors = _py_items(path, tree, 'system', pairs, src.split('\n'))
    items.sort(key=lambda i: (i.line, i.text))
    if len(items) != 4:
        errors.append(f'{path}: expected 4 bot strings (2 prompts, card label, note), found {len(items)}')
    return items, errors


def _js_fallbacks(path, spec):
    """spec: [(regex with one string group, voice, surface, dismiss, expected count)] -> (items, errors)."""
    text = _read(path)
    lines = text.split('\n')
    items, errors = [], []
    for rx, voice, surface, dismiss, want in spec:
        found = 0
        for n, ln in enumerate(lines, 1):
            for m in re.finditer(rx, ln):
                items.append(Item(path, n, voice, surface, kind_of(surface), js_unescape(m.group(1)),
                                  justified=_has_voice_ok(ln), dismiss=dismiss))
                found += 1
        if found != want:
            errors.append(f'{path}: pattern {rx!r} found {found}, expected {want}')
    return items, errors


def extract_study_buddy_js(path='static/js/study-buddy.js'):
    """The corner bubble's fallbacks when the prompt carries no label (study-buddy.js)."""
    items, errors = _js_fallbacks(path, [
        (r"prompt\.detail \|\| '([^']*)'", 'zorp', 'detail_label', False, 1),
        (r"action_label \|\| '([^']*)'", 'zorp', 'button_label', False, 2),
        (r"stay \? escapeText\(stay\.label\) : '([^']*)'", 'zorp', 'button_label', True, 1),
    ])
    return items, errors


def extract_notification_toasts(path='static/js/notifications.js'):
    """Toasts shown from the notification panel (system voice)."""
    return _js_fallbacks(path, [
        (r"showToast\((?:err\.message \|\| )?'((?:[^'\\]|\\.)*)'", 'system', 'system_toast', False, 3),
    ])


def extract_feed_js(path='static/js/feed.js'):
    """The bot note fallback of the feed card (it must match models/bot.py)."""
    return _js_fallbacks(path, [
        (r"challenge\.bot_note \|\| '((?:[^'\\]|\\.)*)'", 'system', 'bot_note', False, 1),
    ])


def extract_site_feedback(path='static/js/site.js'):
    """Answer-feedback strings (listed only; E9 does not change them)."""
    text = _read(path)
    lines = text.split('\n')
    items, errors = [], []
    for n, ln in enumerate(lines, 1):
        for m in re.finditer(r"(?:[Ff]eedback\.textContent = |\|\| )'((?:[^'\\]|\\.)*(?:Correct|Not quite|key ideas)[^']*)'", ln):
            items.append(Item(path, n, 'system', 'system_feedback', 'line', js_unescape(m.group(1))))
    if not items:
        errors.append(f'{path}: no answer feedback strings found')
    return items, errors


EXTRACTORS = (
    extract_guide_catalog,
    extract_guide_js,
    extract_study_buddy_js,
    extract_buddy,
    extract_bot,
    extract_templates,
    extract_notifications,
    extract_notification_toasts,
    extract_feed_js,
    extract_site_feedback,
)


def extract():
    """-> (items, errors). Errors mean a source moved or changed shape; the smoke fails on them."""
    items, errors = [], []
    for fn in EXTRACTORS:
        try:
            got, err = fn()
        except Exception as exc:  # noqa: BLE001 - a broken extractor must surface as an error, not a crash
            got, err = [], [f'{fn.__name__}: {type(exc).__name__}: {exc}']
        items.extend(got)
        errors.extend(err)
    return items, errors


# ---------------------------------------------------------------------------------------------
# Inventory (Appendix A)
# ---------------------------------------------------------------------------------------------

def _cell(text):
    return text.replace('|', '\\|').replace('\n', ' ')


def _group_title(path):
    return f'`{path}`'


def _summary_rows(items):
    order = []
    for it in items:
        key = (it.path, it.voice)
        if key not in order:
            order.append(key)
    rows = ['| Source | Voice | Items |', '|---|---|---|']
    for path, voice in order:
        group = [i for i in items if i.path == path and i.voice == voice]
        parts = []
        for surface in SURFACE_NAMES:
            n = sum(1 for i in group if i.surface == surface)
            if n:
                parts.append(f'{n} {SURFACE_NAMES[surface].lower()}{"s" if n != 1 else ""}')
        rows.append(f"| {_group_title(path)} | {'Zorp' if voice == 'zorp' else 'System'} | {len(group)}: {', '.join(parts)} |")
    return rows


def render_inventory(items, errors=()):
    """The Markdown between the COPY-INVENTORY markers (without the markers). Deterministic."""
    out = []
    out.append('Generated by `python scripts/test_zorp_voice_smoke.py --write` from `models/zorp_voice.py`. Do not edit by hand: '
               '`test_inventory_doc_in_sync` fails when the copy drifts (line numbers alone may lag; `--write` refreshes them). Sources: JavaScript by regex, Python by `ast`, templates by `data-zorp-voice`. F-strings are rendered with sample values (topic label of '
               f'{len(SAMPLE_TOPIC)} characters). `FK` is the Flesch-Kincaid grade of a line (section 3.3.4); labels have none.')
    out.append('')
    out.extend(_summary_rows(items))
    levels = reading_levels(items)
    lines = zorp_lines(items)
    out.append('')
    out.append('**Status (the lint is enforcing since Phase 3; the numbers below are limits that now hold):**')
    out.append('')
    out.append(f"- Zorp lines: {levels['n']}. Flesch-Kincaid grade: mean {levels['mean']:.1f} (limit {FK_MAX_MEAN:g}), "
               f"pooled {levels['pooled']:.1f}, highest {levels['max']:.1f}; "
               f"highest among lines of {FK_MIN_WORDS_LINE} words or more {levels['max_limited']:.1f} (limit {FK_MAX_LINE:g}, D11).")
    out.append(f"- Lines with a \"!\": {sum(1 for i in lines if '!' in i.text)} of {len(lines)} ({exclamation_share(items):.0%}; limit {EXCLAIM_MAX_SHARE:.0%}).")
    for surface, limit in LIMITS.items():
        group = [i for i in items if i.voice == 'zorp' and i.surface == surface]
        if group:
            top = max(group, key=lambda i: len(i.text))
            over = sum(1 for i in group if len(i.text) > limit)
            out.append(f'- {SURFACE_NAMES[surface]}: longest {len(top.text)} characters (limit {limit}), {over} over.')
    found = lint(items)
    out.append(f"- Rule hits: {sum(1 for v in found if v.level == 'error')} errors and "
               f"{sum(1 for v in found if v.level == 'warn')} warnings (any of either fails `scripts/test_zorp_voice_smoke.py`); "
               f"{sum(1 for v in found if v.level == 'info')} notes (a dash or symbol in a system string, listed only).")
    if errors:
        out.append(f'- Extraction errors: {len(errors)} (see test output).')
    out.append('')
    out.append('| Ref | Voice | Surface | Chars | FK | Text |')
    out.append('|---|---|---|---|---|---|')
    for it in items:
        fk = f'{flesch_kincaid(it.text):.1f}' if it.kind == 'line' and it.voice == 'zorp' else ''
        shown = it.template or it.text
        out.append(f"| `{it.ref}` | {'Zorp' if it.voice == 'zorp' else 'System'} | {SURFACE_NAMES[it.surface]} | "
                   f"{len(it.text)} | {fk} | {_cell(shown)} |")
    return '\n'.join(out)


def update_doc(doc_path=None, write=False):
    """Regenerate Appendix A. Returns (in_sync, new_text). With write=True the file is updated."""
    doc_path = DOC_PATH if doc_path is None else doc_path
    items, errors = extract()
    # newline='' keeps the file's own line endings (a Windows checkout may be CRLF), so --write
    # never rewrites every line of the doc
    with open(doc_path, encoding='utf-8', newline='') as fh:
        text = fh.read()
    if text.count(MARK_BEGIN) != 1 or text.count(MARK_END) != 1:
        raise ValueError(f'{doc_path}: expected exactly one of each COPY-INVENTORY marker')
    b, e = text.find(MARK_BEGIN), text.find(MARK_END)
    if e < b:
        raise ValueError(f'{doc_path}: COPY-INVENTORY markers out of order')
    nl = '\r\n' if '\r\n' in text else '\n'
    body = nl + render_inventory(items, errors).replace('\n', nl) + nl
    new = text[:b + len(MARK_BEGIN)] + body + text[e:]
    if write and new != text:
        with open(doc_path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new)
    return new == text, new
