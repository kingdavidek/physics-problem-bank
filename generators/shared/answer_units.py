"""Units and symbols typed beside a number (146%, £1100, 2√7 cm, 35 cm², 12.5 m/s, 45°, 3.5kg, 1,100).

``strip_units`` is the one place that reads them. The numeric checkers (number, fraction, pi_multiple, surd, bearing,
standard form, number_estimate and the numeric fields of number_fields) call it before they parse, and the hint
diagnosis (generators/shared/misconceptions.py) calls it on the pupil's text, so the checker and the hints always read
the same number.

What is accepted, and what is refused (docs/GCSE_MATHS_VERIFICATION.md section "Units and symbols"):

* A trailing unit from a fixed whitelist (``_ATOMS``: lengths, masses, times, capacities, angles, compound units
  such as m/s, km/h, g/cm³, with ², ³, ^2, "squared" or "square" in front), a % sign, a degree sign, or a currency
  symbol either side (£, €, $) or p / pence after the number. Anything else is left alone, so "Enter a number" still
  fires for text that is not a unit.
* The unit must agree with the question. The question's own text (``question``, from the stored problem only) is
  read for the unit it asks for ("in cm", "(m/s)", "to the nearest metre", "to metres", "in pence") and for the units
  it uses. With an asked unit the typed unit must be that unit (1 ml and 1 cm³ agree). With no asked unit, the
  quantity the question asks for decides the dimension ("find the area": cm², not cm), and a unit of a family the
  question uses at another scale (cm when the question says m) is refused; a bare "units" always passes. One field
  of an answer in several fields is not held to a unit asked for another part. With no question at all (a direct
  call) every whitelisted unit passes.
* A wrong unit is never converted and never read as the same number: "35 m" for a question in cm, "£5" where pence
  are asked and "5p" where pounds are asked are refused with a message that names the unit asked for.
* "%" is dropped when a sentence of the question asks for a percentage (146% and 146 are both right) and refused
  otherwise ("find 25% of 250": 62.5% is not 62.5). A probability question (form "probability") keeps its own rule:
  a percentage there is a fraction of 1.
* "1,100" and "1 100" are one thousand one hundred (groups of exactly three digits). A comma in any other place
  ("3,5") used to be deleted, so it read as 35; it is now refused with a hint to use a decimal point.

Everything is bounded: a field longer than ``MAX_UNIT_FIELD_LEN`` is left untouched, the question's markup is read up
to ``MAX_RAW_QUESTION_LEN`` characters and its visible text cut to ``MAX_QUESTION_LEN``, there is no eval and no SymPy,
and every regular expression here is linear.
"""
from __future__ import annotations

import html
import re
from functools import lru_cache

MAX_UNIT_FIELD_LEN = 60
MAX_QUESTION_LEN = 6000           # of visible text, after the markup is dropped
MAX_RAW_QUESTION_LEN = 120000     # of stored markup read for that text (the largest drawn question is about 11 KB)

# Answer types whose typed value is a number (or a number with a surd or pi) and may carry a unit.
UNIT_ANSWER_TYPES = frozenset({
    'number', 'fraction', 'pi_multiple', 'surd', 'bearing', 'standard_form', 'number_estimate',
})

# ---------------------------------------------------------------------------------------------------------------
# The unit whitelist: spelling -> (base unit, dimension)
# ---------------------------------------------------------------------------------------------------------------

_ATOMS: dict[str, str] = {}      # spelling -> base unit
_DIM: dict[str, str] = {}        # base unit -> dimension


def _add(base, dim, spellings):
    _DIM[base] = dim
    _ATOMS[base] = base
    for word in spellings.split():
        _ATOMS[word] = base


_add('mm', 'length', 'millimetre millimetres millimeter millimeters')
_add('cm', 'length', 'centimetre centimetres centimeter centimeters')
_add('m', 'length', 'metre metres meter meters')
_add('km', 'length', 'kilometre kilometres kilometer kilometers')
_add('in', 'length', 'inch inches')
_add('ft', 'length', 'foot feet')
_add('yd', 'length', 'yard yards')
_add('mi', 'length', 'mile miles')
_add('mg', 'mass', 'milligram milligrams')
_add('g', 'mass', 'gram grams gramme grammes')
_add('kg', 'mass', 'kilogram kilograms kilogramme kilogrammes kilo kilos')
_add('t', 'mass', 'tonne tonnes')
_add('lb', 'mass', 'lbs pound_mass')
_add('oz', 'mass', 'ounce ounces')
_add('s', 'time', 'sec secs second seconds')
_add('min', 'time', 'mins minute minutes')
_add('h', 'time', 'hr hrs hour hours')
_add('day', 'time', 'days')
_add('week', 'time', 'weeks')
_add('month', 'time', 'months')
_add('year', 'time', 'years yr yrs')
_add('ml', 'capacity', 'millilitre millilitres milliliter milliliters cc')
_add('cl', 'capacity', 'centilitre centilitres')
_add('l', 'capacity', 'litre litres liter liters')
_add('deg', 'angle', 'degree degrees')
_add('rad', 'angle', 'radian radians')
_add('ha', 'land', 'hectare hectares')
_add('unit', 'neutral', 'units')

# Science and computing units (whole-change review A3, 2026-10-29: "5 bits" for "How many bits is that?" was answered
# "Enter a valid number"). They are read only where the question names them ("in joules", "how many kJ", "a force of
# 180 N", "1 KB = 1000 bytes"), or, for the SI unit alone, where the question asks for that quantity ("calculate the
# kinetic energy": 8 J), so a scale the question never mentions (8 kJ) is not taken as the same number.
_add('j', 'energy', 'joule joules')
_add('kj', 'energy', 'kilojoule kilojoules')
_add('mj', 'energy', 'megajoule megajoules')          # MJ: no question uses millijoules
_add('kwh', 'energy', '')
_add('cal', 'energy', 'calorie calories')
_add('kcal', 'energy', 'kilocalorie kilocalories')
_add('n', 'force', 'newton newtons')
_add('kn', 'force', 'kilonewton kilonewtons')
_add('w', 'power', 'watt watts')
_add('kw', 'power', 'kilowatt kilowatts')
_add('mw', 'power', 'megawatt megawatts')             # MW
_add('pa', 'pressure', 'pascal pascals')
_add('kpa', 'pressure', 'kilopascal kilopascals')
_add('hz', 'frequency', 'hertz')
_add('khz', 'frequency', 'kilohertz')
_add('mhz', 'frequency', 'megahertz')
_add('ghz', 'frequency', 'gigahertz')
_add('v', 'voltage', 'volt volts')
_add('ohm', 'resistance', 'ohms')
_add('amp', 'current', 'amps ampere amperes')
_add('bit', 'data', 'bits')
_add('byte', 'data', 'bytes')
_add('kb', 'data', 'kilobyte kilobytes')
_add('mb', 'data', 'megabyte megabytes')
_add('gb', 'data', 'gigabyte gigabytes')
_add('tb', 'data', 'terabyte terabytes')
_SCIENCE_DIMS = frozenset({'energy', 'force', 'power', 'pressure', 'frequency', 'voltage', 'resistance', 'current',
                           'data'})
_NAMED_ONLY = frozenset(b for b, d in _DIM.items() if d in _SCIENCE_DIMS)
# the SI unit of each quantity, taken where the question asks for that quantity and names no unit of it
_SI_FOR = {'energy': 'j', 'force': 'n', 'power': 'w', 'pressure': 'pa', 'frequency': 'hz', 'voltage': 'v',
           'resistance': 'ohm', 'current': 'amp'}
# one-letter units: in a question they count only as a capital beside a number or after "in" ("180 N", "in J"), so
# "3n", "in terms of n" or "3i + 4j" never name one
_LETTER_UNITS = frozenset({'j', 'n', 'w', 'v'})
# a quantity measured in another unit's terms: 1 Pa is 1 N/m² (so "20 N/m²" is a pressure in Pa)
_DIM_EXPAND = {'pressure': (('force', 1), ('length', -2)), 'energy': (('force', 1), ('length', 1)),
               'power': (('force', 1), ('length', 1), ('time', -1))}
# families where a unit at another scale from the one the question uses is refused (times never are: a speed in km/h
# from a time in minutes is right)
_SCALE_DIMS = frozenset({'length', 'mass', 'capacity'}) | _SCIENCE_DIMS
_SHOWN = {'unit': 'units', 'deg': 'degrees', 'year': 'years', 'day': 'days', 'week': 'weeks', 'month': 'months',
          'j': 'J', 'kj': 'kJ', 'mj': 'MJ', 'kwh': 'kWh', 'n': 'N', 'kn': 'kN', 'w': 'W', 'kw': 'kW', 'mw': 'MW',
          'pa': 'Pa', 'kpa': 'kPa', 'hz': 'Hz', 'khz': 'kHz', 'mhz': 'MHz', 'ghz': 'GHz', 'v': 'V', 'ohm': 'ohms',
          'amp': 'amps', 'bit': 'bits', 'byte': 'bytes', 'kb': 'KB', 'mb': 'MB', 'gb': 'GB', 'tb': 'TB'}

# a speed written as one word
_COMPOUND_WORDS = {'mph': (('mi', 1), ('h', -1)), 'kph': (('km', 1), ('h', -1)), 'kmh': (('km', 1), ('h', -1))}

_CURRENCY_SYMBOLS = {'£': '£', '€': '€', '$': '$'}
_CURRENCY_WORDS = {
    'p': 'p', 'pence': 'p', 'penny': 'p', 'pound': '£', 'pounds': '£', 'euro': '€', 'euros': '€',
    'dollar': '$', 'dollars': '$',
}
_CURRENCY_NAMES = {'p': 'pence (p)', '£': 'pounds (£)', '€': 'euros (€)', '$': 'dollars ($)'}
_PERCENT_WORDS = ('%', 'percent', 'per cent')
_TIME_WORDS = {'s': 'seconds', 'min': 'minutes', 'h': 'hours', 'day': 'days', 'week': 'weeks', 'month': 'months',
               'year': 'years', 'l': 'litres'}

_SUPER = str.maketrans({'²': '^2', '³': '^3'})
_NBSP = str.maketrans({'\u00a0': ' ', '\u202f': ' ', '\u2009': ' ', '\u2007': ' '})

_ATOM_RE = re.compile(
    r'(?:(?P<pre>sq\.?|square|cubic)\s+)?(?P<name>[a-z]+)\s*(?:\^\s*(?P<p1>[23])|(?P<p2>[23])|\s+(?P<p3>squared|cubed))?')


def _atom(text):
    """One unit with its power: 'cm^2' -> ('cm', 2); None when it is not on the whitelist."""
    m = _ATOM_RE.fullmatch(text.strip())
    if not m:
        return None
    name = m.group('name')
    power = 1
    if m.group('pre'):
        power = 3 if m.group('pre') == 'cubic' else 2
    explicit = m.group('p1') or m.group('p2')
    if explicit:
        power *= int(explicit)
    elif m.group('p3'):
        power *= 2 if m.group('p3') == 'squared' else 3
    if name in _COMPOUND_WORDS:
        if power != 1 or m.group('pre'):
            return None
        return name
    base = _ATOMS.get(name)
    if base is None:
        return None
    return base, power


def parse_unit(tail):
    """A unit expression as a frozenset of (base, exponent), or None.

    cm -> {(cm,1)}; cm² -> {(cm,2)}; m/s -> {(m,1),(s,-1)}; "metres per second" the same; mph -> {(mi,1),(h,-1)};
    "per kg" -> {(kg,-1)}.
    """
    t = str(tail or '').lower().translate(_SUPER).strip().rstrip('.').strip()
    if not t or len(t) > 40:
        return None
    t = re.sub(r'\s+', ' ', t)
    if t.startswith('per '):
        t = '/' + t[4:]
    parts = re.split(r'\s*/\s*|\s+per\s+', t)
    if len(parts) > 2:
        return None
    out: dict[str, int] = {}
    for index, part in enumerate(parts):
        if not part:
            if index == 0 and len(parts) == 2:
                continue            # "/kg": per kilogram
            return None
        atom = _atom(part)
        if atom is None:
            return None
        if isinstance(atom, str):
            for base, power in _COMPOUND_WORDS[atom]:
                out[base] = out.get(base, 0) + power
            continue
        base, power = atom
        out[base] = out.get(base, 0) + (power if index == 0 else -power)
    out = {b: p for b, p in out.items() if p}
    return frozenset(out.items()) if out else None


def _fmt_unit(unit):
    """How a unit reads in a message: cm², km/h, m/s², seconds."""
    pairs = sorted(unit, key=lambda bp: -bp[1])
    if len(pairs) == 1 and pairs[0][1] == 1 and pairs[0][0] in _TIME_WORDS:
        return _TIME_WORDS[pairs[0][0]]
    if pairs == [('in', 1)]:
        return 'inches'                 # "the answer in in." read badly

    def one(base, power):
        return _SHOWN.get(base, base) + {1: '', 2: '²', 3: '³'}.get(power, f'^{power}')

    top = [one(b, p) for b, p in pairs if p > 0]
    bottom = [one(b, -p) for b, p in pairs if p < 0]
    text = '·'.join(top) if top else '1'
    if bottom:
        text += '/' + '·'.join(bottom)
    return text


def _canon(unit):
    """A unit with ml written as cm³ (1 ml is 1 cm³) and Pa as N/m², so either agrees with the other."""
    out: dict[str, int] = {}
    for base, power in unit:
        if base == 'ml':
            base, power = 'cm', 3 * power
        elif base == 'pa':
            out['m'] = out.get('m', 0) - 2 * power
            base = 'n'
        out[base] = out.get(base, 0) + power
    return frozenset((b, p) for b, p in out.items() if p)


def _dims(unit):
    """The dimension of a unit, ignoring its scale: cm² and m² are both {(length, 2)}; Pa and N/m² agree."""
    out: dict[str, int] = {}
    for base, power in unit:
        dim = _DIM.get(base, base)
        for d, p in _DIM_EXPAND.get(dim, ((dim, 1),)):
            out[d] = out.get(d, 0) + p * power
    return frozenset((d, p) for d, p in out.items() if p)


def _kind(unit):
    """The kind of quantity a unit measures, with its powers: cm, cm² and cm³ are three kinds, cm and km one."""
    return _dims(unit)


_ANGLE_KIND = frozenset({('angle', 1)})


def _is_degree(unit):
    return all(base == 'deg' for base, _ in unit)


def _is_neutral(unit):
    return all(_DIM.get(base) == 'neutral' for base, _ in unit)


# ---------------------------------------------------------------------------------------------------------------
# The question: units it uses and the unit it asks for
# ---------------------------------------------------------------------------------------------------------------

class QuestionUnits:
    """What the question's own text says about units (all empty for no question)."""

    __slots__ = ('known', 'asked', 'used', 'measured', 'asked_currency', 'currencies', 'asks_percent',
                 'mentions_percent', 'target', 'targets', 'involves_angle', 'involves_money')

    def __init__(self):
        self.known = False                  # a question was given
        self.asked: list[frozenset] = []    # the units it asks the answer in
        self.used: set[str] = set()         # base units it uses anywhere
        self.measured: set[frozenset] = set()   # units written as measurements, with their powers ("40 cm3",
        #                                         "(km/h)", "250 people/km^2" per km², "in minutes"); not "hours studied"
        self.asked_currency: set[str] = set()
        self.currencies: set[str] = set()
        self.asks_percent = False
        self.mentions_percent = False
        self.target = None                  # the one quantity it asks for ('area', 'length', ...), or None
        self.targets = frozenset()          # every quantity it asks for ("find the height and volume of the box")
        self.involves_angle = False         # it is about angles, turns or temperatures (a degree sign may fit)
        self.involves_money = False         # it is about money (a currency symbol may fit)

    def named(self):
        """The base units the question names: the units it uses and the units it asks for."""
        return set(self.used) | {b for a in self.asked for b, _ in a}

    def kinds(self):
        """The kinds of quantity the question measures or asks for (a length, an area, a speed, an angle, ...), see
        ``_kind``: "find the height and volume of the box" with lengths in cm measures lengths and asks for a volume."""
        kinds = {_kind(u) for u in self.measured} | {_kind(u) for u in self.asked}
        for target in self.targets:
            kinds.update(_TARGET_KINDS.get(target, ()))
        if self.involves_angle:
            kinds.add(_ANGLE_KIND)
        return kinds


# The unit a question asks for is read only from phrases that say so: "in cm", "to the nearest metre", "into m/s",
# "to km", "(in cm)". A unit in brackets alone is an axis label or a caption ("Time (hours)"), not an instruction.
_ASK_INTRO_RE = re.compile(
    r'(?:\bin\s+terms\s+of\s+|\bin\s+|\bto\s+the\s+nearest\s+|\bnearest\s+|\binto\s+|\bto\s+)(?:the\s+)?'
    r'(?P<rest>[^.?!;:,)\n]{1,40})')
_ASK_FOLLOWER_RE = re.compile(
    r'\s*(?:$|[.,;:?!()]|(?:and|or|to|correct|giving|give|rounded|using|if|when|for|then|so|as|of)\b)')
_HOW_MANY_RE = re.compile(r'\b(?:how\s+many|number\s+of)\s+(?:more\s+|fewer\s+)?'
                          r'(?P<unit>[a-z]+(?:\s*\^\s*[23]|[23](?![\d.]))?)(?![a-z])')
# "All lengths are in cm", "times measured in seconds": a statement about the data, not the unit asked for.
_STATEMENT_BEFORE_RE = re.compile(
    r'\b(?:are|is|were|was|measured|given|recorded|shown|marked|labelled|labeled|written|drawn)\s*$')
_UNIT_CUT_RE = re.compile(
    r'(?:(?:sq\.?|square|cubic)\s+)?[a-z]+(?:\s*\^\s*[23]|[23](?![\d.])|\s+squared|\s+cubed)?'
    r'(?:\s*(?:/|\bper\b)\s*[a-z]+(?:\s*\^\s*[23]|[23](?![\d.]))?)?')
_CURRENCY_ASK_RE = re.compile(
    r'(?:\bin|\bto|\bhow\s+many)\s+(?:the\s+)?(pence|penny|pounds?|euros?|dollars?)(?![a-z])'
    r'|\bnearest\s+(?:the\s+)?(pounds?|euros?|dollars?)(?![a-z])'
    r'|(?:\bin|\bnearest|\bto)\s*(£|€|\$)(?!\s*\.?\d)|\(\s*(?:in\s+)?(p|£|€|\$)\s*\)')
# "to the nearest penny" (or cent) is how accurately to give an amount in pounds (or euros), not the unit asked for:
# "Find the cost per kilogram, to the nearest penny." is answered £5.97, and 5.97p is 5.97 pence (whole-change review
# A1, 2026-10-29: £5.97 was refused as "asks for the answer in pence" and 5.97p accepted). "in pence" and "how many
# pence" still ask for pence.
_NEAREST_SUBUNIT_RE = re.compile(r'\bnearest\s+(?:the\s+)?(penny|pence|cents?)(?![a-z])')
# A percentage is asked for only by a sentence that asks something ("find", "what", "convert", ...) and names a
# percentage as a word, or by "as a %", "in %", "(%)". A % written on a number ("find 25% of 250", "write 24% as a
# decimal") is data, and "The percentage increase is 20%. Find the original price." asks for a price (review
# 2026-10-28: both of those used to let "62.5%", "0.24%" or "100%" through as the bare number).
_SENTENCE_SPLIT_RE = re.compile(r'[?!;]|\.(?!\d)')
_ASK_VERB_RE = re.compile(
    r'\b(?:what|which|how|find|work\s+out|calculate|determine|give|write|express|state|convert|change|estimate)\b')
_PERCENT_WORD_RE = re.compile(r'\b(?:percentage|percent|per\s+cent)\b')
_PERCENT_SYMBOL_ASK_RE = re.compile(r'\bas\s+a\s+%|\bin\s+%|\(\s*%\s*\)')

# The quantity a question asks for, read from its first words after the verb: "find the area", "what is the side
# length", "how far". Only these quantities, and only when the question asks for exactly one of them.
_TARGET_FILLER = (r'(?:(?:exact|total|surface|curved|new|original|real|actual|perpendicular|side|slant|missing|'
                  r'average|mean|least|greatest|largest|smallest|shortest|longest|minimum|maximum|full|outer|inner|'
                  r'shaded|remaining|approximate|estimated|final|whole|straight|direct|return|top|base|'
                  r'cross-sectional|kinetic|gravitational|potential|elastic|useful|wasted|input|output|electrical|'
                  r'thermal|resultant|stopping|braking|thinking|wave|time|uncompressed|compressed|acute|obtuse|'
                  r'reflex|interior|exterior|unknown|marked|required|arc|three-figure|other|shorter|longer|third|'
                  r'adjacent|opposite|apex|straight-line|vertical|horizontal|'
                  r'size\s+of\s+(?:the|this))\s+){0,3}')
_TARGET_WORDS = {
    'area': 'area', 'volume': 'volume', 'speed': 'speed', 'velocity': 'speed', 'mass': 'mass', 'density': 'density',
    'acceleration': 'acceleration', 'time': 'time', 'period': 'time',
    # lengths
    'perimeter': 'length', 'length': 'length', 'distance': 'length', 'height': 'length', 'width': 'length',
    'depth': 'length', 'radius': 'length', 'diameter': 'length', 'circumference': 'length', 'wavelength': 'length',
    'side': 'length', 'hypotenuse': 'length', 'diagonal': 'length', 'edge': 'length',
    # physics and computing quantities (whole-change review A3: their units are now read, see _SCIENCE_DIMS)
    'energy': 'energy', 'work done': 'energy', 'force': 'force', 'weight': 'force', 'power': 'power',
    'pressure': 'pressure', 'current': 'current', 'voltage': 'voltage', 'potential difference': 'voltage',
    'resistance': 'resistance', 'frequency': 'frequency', 'file size': 'data',
    # an angle or a bearing is in degrees (whole-change review A3: "61 kg" was right for an angle)
    'angle': 'angle', 'bearing': 'angle',
    # quantities no unit on the list can measure: any listed unit is refused for them ("the number of colours", "the
    # largest denary number": a count is not 4096 bits; "the number of minutes" asks for minutes, read below)
    'charge': 'other', 'momentum': 'other', 'efficiency': 'other', 'number': 'count', 'denary': 'count',
    # a pure number: "find the scale factor", "what is its gradient?", "find the probability that ..." (fix pass 1a,
    # 2026-11-03: "5 cm" was right for a scale factor and "-4°" for a gradient)
    'scale factor': 'count', 'gradient': 'count', 'probability': 'count',
}
_TARGET_WORD_ALT = (r'(work\s+done|potential\s+difference|file\s+size|scale\s+factor|'
                    + '|'.join(sorted({w for w in _TARGET_WORDS if ' ' not in w}, key=len, reverse=True)) + r')s?\b')
_TARGET_RE = re.compile(
    r'\b(?:find|calculate|work\s+out|what\s+is|what\s+was|what\s+will\s+be|estimate|determine|state|write\s+down)\s+'
    r'(?:the\s+|its\s+|their\s+|this\s+)?(?:size\s+of\s+(?:the\s+)?)?' + _TARGET_FILLER + _TARGET_WORD_ALT +
    r'|\bhow\s+(far|fast|heavy|high|tall|wide|deep|long\b(?=[^.?!]{0,60}\btak))\b'
    r'|\bas\s+a\s+(fraction|decimal)\s+of\b')
# "find the height and volume of the box", "the area and the perimeter": every quantity named after the verb
_TARGET_AND_RE = re.compile(r'\s+and\s+(?:the\s+|its\s+|their\s+)?' + _TARGET_FILLER + _TARGET_WORD_ALT)
# "how long does the journey take" is a time ("how long is the journey" may be either, so it is not read); "as a
# fraction of" has no unit
_HOW_TARGET = {'far': 'length', 'fast': 'speed', 'heavy': 'mass', 'high': 'length', 'tall': 'length', 'wide': 'length',
               'deep': 'length', 'fraction': 'other', 'decimal': 'other'}
# a question about angles, turns or temperatures, where a typed degree sign can fit the answer. Words that name a
# shape or a line ("triangle numbers", "a parallel circuit", "a line parallel to y = 2x") do not count: a gradient,
# a count or a length is not in degrees (fix pass 1a, 2026-11-03: "21°" was right for the 6th triangle number)
_ANGLE_WORDS_RE = re.compile(
    r'[°∠θ]|\b(?:angles?|degrees?|bearings?|sectors?|pie\s+charts?|rotat\w*|turns?|interior|exterior|sin|cos|tan|'
    r'trigonometr\w*|radians?|elevation|depression|temperatures?|celsius|fahrenheit|compass)\b')
_LABEL_FOLLOWERS = frozenset('_₀₁₂₃₄₅₆₇₈₉')
_LABEL_NUMBER_RE = re.compile(r'\s*\d')
# a one-letter unit name written as a letter in an expression, beside a sign ("(m + 7)", "x = 2s"); "(m)" is a unit.
# An inequality counts too: "the classes are 20 < t ≤ 30" names t, so a drawn axis "... 14 16 t (minutes)" is not
# 16 tonnes (fix review 2026-11-03: "39 minutes" for the mean of race times was refused as two kinds of quantity)
_VARIABLE_RE = re.compile(r'[+\-−=×*<>≤≥]\s*\x00(?![a-z])|(?<![a-z])\x00\s*[+\-−=×*<>≤≥]')
_BRACKET_CLOSE_RE = re.compile(r'(?:\s*\^\s*[23]|[23])?\s*\)')
_UNIT_PREFIX_RE = re.compile(r'(?:sq\.?|square|cubic)\s+$')
_PER_BEFORE_RE = re.compile(r'(?:/|\bper)\s*$')
_QUALIFIED_PREV_RE = re.compile(r'(?:\d|\)|π|/|\bin|\bper|\bto|\bnearest)\s*$')
_WORD_RE = re.compile(r'(?<![a-z])(?P<tok>[a-z]+)(?![a-z])')
_AMBIGUOUS = frozenset({'second', 'minute', 'min', 'in', 'foot', 'ha', 'unit'}) | {
    w for w in _ATOMS if len(w) <= 3}


def question_plain_text(question, lower=True):
    """The visible text of a question (HTML tags and LaTeX wrappers dropped), lower-cased, bounded.

    ``lower=False`` keeps the capitals (the one-letter units are read only as capitals: "180 N", not "3n").

    The tags go before the text is cut: a drawn question carries 6 to 11 KB of SVG markup ahead of the words that
    ask for the answer, and cutting the raw string first dropped them (review 2026-10-28: "work out the acceleration"
    after a velocity-time graph was never read, so 2.5 m/s passed). The raw string is bounded first at a larger size,
    so the tag regex still runs over a bounded input."""
    t = str(question or '')[:MAX_RAW_QUESTION_LEN]
    t = html.unescape(re.sub(r'<[^>]*>', ' ', t))[:MAX_QUESTION_LEN]
    t = re.sub(r'\\(?:text|textrm|mathrm|mathit|mathbf|textbf)\s*\{([^{}]*)\}', r' \1 ', t)
    t = (t.replace('\\%', '%').replace('\\$', '$').replace('\\pounds', '£').replace('\\circ', '°')
         .replace('^°', '°').replace('^{\\circ}', '°'))
    t = re.sub(r'\\(?:[,;:!]|quad|qquad|ldots|cdot|times|left|right|\(|\)|\[|\])', ' ', t)
    t = t.replace('{', ' ').replace('}', ' ').translate(_SUPER).translate(_NBSP)
    t = re.sub(r'\s+', ' ', t).strip()
    return t.lower() if lower else t


def _unit_at(t, start, base):
    """The whole unit written where a used unit word starts ("cm^2", "km/h", "square metres", "/km²" read as per
    km²), or the base alone when the words around it do not read as one unit."""
    pre = _UNIT_PREFIX_RE.search(t, max(0, start - 8), start)
    begin = pre.start() if pre else start
    cut = _UNIT_CUT_RE.match(re.sub(r'\.(?!\d)', ' ', t[begin:begin + 40]))     # "80 cm3." is cm³
    candidate = cut.group(0) if cut else ''
    unit = parse_unit(candidate)
    while unit is None and ' ' in candidate:
        candidate = candidate.rsplit(' ', 1)[0]
        unit = parse_unit(candidate)
    if unit is None or base not in {b for b, _ in unit}:
        unit = frozenset({(base, 1)})
    per = _PER_BEFORE_RE.search(t, max(0, begin - 5), begin)
    if per:
        # "(km/h)" read from its h is km/h; "250 people/km^2" and "per kg" are per km² and per kg
        whole = re.search(r'(?<![a-z])[a-z]+(?:\^?[23])?\s*$', t[max(0, per.start() - 12):per.start()])
        joined = parse_unit(whole.group(0).strip() + '/' + candidate) if whole and per.group(0).startswith('/') else None
        unit = joined if joined is not None else frozenset((b, -p) for b, p in unit)
    return unit


def _letter_units_ok(unit, t, cased, start, end):
    """False when the unit has a one-letter unit (J, N, W, V) that the question does not print as a capital in
    t[start:end] ("in terms of n" is not newtons). ``cased`` is the question with its capitals, aligned with ``t``."""
    if not any(b in _LETTER_UNITS for b, _ in unit):
        return True
    if cased is None:
        return False
    for m in _WORD_RE.finditer(t, start, end):
        if m.group('tok') in _LETTER_UNITS and not cased[m.start()].isupper():
            return False
    return True


@lru_cache(maxsize=512)
def question_units(question):
    info = QuestionUnits()
    if question is None or not str(question).strip():
        return info
    info.known = True
    t = question_plain_text(question)
    cased = question_plain_text(question, lower=False)
    if len(cased) != len(t):
        cased = None                # a character that changes length in lower case: one-letter units are not read

    # the unit the question asks for
    for m in _ASK_INTRO_RE.finditer(t):
        rest, start = m.group('rest'), m.start('rest')
        cut = _UNIT_CUT_RE.match(rest)
        candidate = cut.group(0) if cut else ''
        unit = parse_unit(candidate)
        while unit is None and ' ' in candidate:
            candidate = candidate.rsplit(' ', 1)[0]
            unit = parse_unit(candidate)
        if unit is None or _is_neutral(unit) or unit in info.asked:
            continue
        if _STATEMENT_BEFORE_RE.search(t, max(0, m.start() - 12), m.start()):
            continue                # "all lengths are in cm": the units it uses (read below), not an instruction
        if _ASK_FOLLOWER_RE.match(t, start + len(candidate)) and _letter_units_ok(
                unit, t, cased, start, start + len(candidate)):
            info.asked.append(unit)
    # "how many grams are in 200 cm3?", "how many km in 2 s?": the counted unit is the one asked for (one unit only,
    # so "how many minutes per day" asks for minutes)
    for m in _HOW_MANY_RE.finditer(t):
        unit = parse_unit(m.group('unit'))
        if (unit is not None and not _is_neutral(unit) and unit not in info.asked
                and _letter_units_ok(unit, t, cased, m.start('unit'), m.end('unit'))):
            info.asked.append(unit)
    for m in _CURRENCY_ASK_RE.finditer(t):
        word = m.group(1) or m.group(2) or m.group(3) or m.group(4)
        info.asked_currency.add(_CURRENCY_SYMBOLS.get(word) or _CURRENCY_WORDS[word])
    if not info.asked_currency:
        for m in _NEAREST_SUBUNIT_RE.finditer(t):
            if m.group(1).startswith('cent'):
                info.asked_currency.add('$' if '$' in t and '€' not in t else '€')
            else:
                info.asked_currency.add('£')

    # the units it uses
    variables = {}                  # one-letter unit names written as letters in an expression
    for m in _WORD_RE.finditer(t):
        tok = m.group('tok')
        if tok in _COMPOUND_WORDS:
            info.used.update(base for base, _ in _COMPOUND_WORDS[tok])
            info.measured.add(frozenset(_COMPOUND_WORDS[tok]))      # "mph" is only ever a unit
            continue
        base = _ATOMS.get(tok)
        if base is None or _DIM.get(base) == 'neutral' or tok == 'in':
            continue                # "in" is the word far more often than the inch
        if t[m.end():m.end() + 1] in _LABEL_FOLLOWERS:
            continue                # "l₁", "l_2": a line's name on a graph, not litres
        before = t[max(0, m.start() - 12):m.start()]
        qualified = bool(_QUALIFIED_PREV_RE.search(before)) or (
            before.rstrip().endswith('(') and _BRACKET_CLOSE_RE.match(t, m.end()) is not None)
        if _LABEL_NUMBER_RE.match(t, m.end()) and not re.search(r'\d\s*$', before):
            continue                # "in year 5", "day 3", "year 10 pupils": a name, not a time
        if len(tok) == 1:
            if tok not in variables:
                variables[tok] = bool(_VARIABLE_RE.search(t.replace(tok, '\x00')))
            if variables[tok]:
                continue            # "5(m + 7) - 5m": a letter in an expression, not metres
        if tok in _LETTER_UNITS:
            # "180 N", "a 5 J store": a capital straight after a number ("3n" and "3i + 4j" name no unit)
            if cased is None or not cased[m.start()].isupper() or not re.search(r'\d\s*$', t[max(0, m.start() - 4):m.start()]):
                continue
        elif tok in _AMBIGUOUS and not qualified:
            continue
        info.used.add(base)
        whole = _unit_at(t, m.start(), base)
        info.used.update(b for b, _ in whole)      # "(km/h)" read from its h uses km too
        if qualified:
            info.measured.add(whole)
    for sym in ('£', '€', '$'):
        if sym in t:
            info.currencies.add(sym)
    for m in re.finditer(r'(?<![a-z0-9])(pence|penny|pounds|euros|dollars)(?![a-z])|\d(p)(?![a-z])',
                         _NEAREST_SUBUNIT_RE.sub(' ', t)):     # "to the nearest penny" is an accuracy, not pence
        info.currencies.add(_CURRENCY_WORDS[m.group(1) or m.group(2)])
    info.mentions_percent = bool(re.search(r'%|percent|per cent', t))
    asks = bool(_PERCENT_SYMBOL_ASK_RE.search(t)) or any(
        _ASK_VERB_RE.search(s) and _PERCENT_WORD_RE.search(s) for s in _SENTENCE_SPLIT_RE.split(t))
    info.asks_percent = asks and not info.asked and not info.asked_currency
    targets = set()
    for m in _TARGET_RE.finditer(t):
        if m.group(1):
            targets.add(_TARGET_WORDS[re.sub(r'\s+', ' ', m.group(1))])
            end = m.end()
            while (more := _TARGET_AND_RE.match(t, end)) is not None:
                targets.add(_TARGET_WORDS[re.sub(r'\s+', ' ', more.group(1))])
                end = more.end()
        else:
            targets.add(_HOW_TARGET.get(m.group(2) or m.group(3), 'time'))
    # "how many points satisfy both conditions?", "how many rest days is that?", "the number of books read": a count,
    # which takes no unit (fix pass 1a, 2026-11-03: "0 cm" was right for a number of points, "2 seconds" for the mode of
    # a number of books). "how many cm", "how many pence", "the number of minutes" ask for a unit.
    for m in _HOW_MANY_RE.finditer(t):
        word = m.group('unit')
        if parse_unit(word) is None and word not in _CURRENCY_WORDS and word not in ('sq', 'square', 'cubic'):
            targets.add('count')
    info.targets = frozenset(targets)
    info.target = targets.pop() if len(targets) == 1 else None
    # "Enter a number (degrees optional)" is a signal that a degree sign may fit, not that the answer is an angle: the
    # geometry and bearings wrappers print it under "Find the length AT" and "Find the straight-line distance" too
    info.involves_angle = bool(_ANGLE_WORDS_RE.search(t)) or 'deg' in info.used or info.target == 'angle'
    # money is involved only where the question names a currency: "paid by card" in a frequency tree, "save" in a
    # computing question or "wages" with no £ do not make a count an amount of money (fix pass 1a, 2026-11-03)
    info.involves_money = bool(info.currencies or info.asked_currency)
    return info


# ---------------------------------------------------------------------------------------------------------------
# One typed value
# ---------------------------------------------------------------------------------------------------------------

_THOUSANDS_COMMA_RE = re.compile(r'([+\-−]?)(\d{1,3}(?:,\d{3})+)(\.\d+)?')
_THOUSANDS_SPACE_RE = re.compile(r'([+\-−]?)(\d{1,3}(?: \d{3})+)(\.\d+)?')
_COMMA_BETWEEN_DIGITS_RE = re.compile(r'\d\s*,\s*\d')
_LEAD_CURRENCY_RE = re.compile(r'([+\-−]?)\s*([£€$])\s*(.+)')
_HEAD_END_RE = re.compile(r'[0-9)π]$|pi$')

DECIMAL_COMMA_FEEDBACK = 'Use a decimal point, not a comma. For example, write 3.5.'


def _mismatch_message(typed, qu, *, currency=False, percent=False, kind=None, percent_asked=False):
    if percent:
        return 'Check the units. The question does not ask for a percentage.'
    if percent_asked:
        return 'Check the units. The question asks for a percentage.'
    if kind == 'bearing':
        return 'Check the units. A bearing is an angle in degrees.'
    if currency:
        asked = qu.asked_currency or qu.currencies
        names = ' or '.join(_CURRENCY_NAMES[c] for c in sorted(asked))
        if qu.asked_currency:
            return f'Check the units. The question asks for the answer in {names}.'
        return f'Check the units. The question uses {names}.'
    if qu.asked:
        names = ' or '.join(dict.fromkeys(_fmt_unit(u) for u in qu.asked))
        return f'Check the units. The question asks for the answer in {names}.'
    names = ' or '.join(sorted(_fmt_unit(frozenset({(b, 1)})) for b in qu.used))
    return f'Check the units. The question uses {names}.'


def _length_word(qu):
    """A length unit the question uses, for a message ("cm"), or cm."""
    for base in ('cm', 'm', 'mm', 'km'):
        if base in qu.used:
            return base
    return 'cm'


KIND_UNIT_FEEDBACK = 'Check the units. Type just the number.'


def _named_ok(unit, qu, target=None):
    """A science or computing unit (kJ, N, MB, ...) counts only where the question names it, or, for the SI unit of
    the quantity asked for, where the question names no unit of that quantity ("calculate the kinetic energy": 8 J,
    not 8 kJ). A radian counts only where the question names radians."""
    named = qu.named()
    for base, _ in unit:
        if base in named:
            continue
        dim = _DIM.get(base)
        if base in _NAMED_ONLY:
            if target != dim or _SI_FOR.get(dim) != base or any(_DIM.get(b) == dim for b in named):
                return False
        elif base == 'rad':
            return False
    return True


def _fits_target(unit, target, qu=None):
    """True when the unit can measure the quantity asked for (an area in cm², a speed in km/h, an angle in degrees)."""
    dims = _dims(unit)
    if target == 'area':
        return dims == frozenset({('length', 2)}) or dims == frozenset({('land', 1)})
    if target == 'volume':
        return dims in (frozenset({('length', 3)}), frozenset({('capacity', 1)}))
    if target == 'speed':
        return dims == frozenset({('length', 1), ('time', -1)})
    if target == 'mass':
        return dims == frozenset({('mass', 1)})
    if target == 'density':
        return dims in (frozenset({('mass', 1), ('length', -3)}), frozenset({('mass', 1), ('capacity', -1)}))
    if target == 'acceleration':
        return dims == frozenset({('length', 1), ('time', -2)})
    if target == 'time':
        return dims == frozenset({('time', 1)})
    if target == 'angle':
        return dims == frozenset({('angle', 1)}) and (qu is None or _named_ok(unit, qu, target))
    if target in _SCIENCE_DIMS:
        return dims == _dims(frozenset({(_SI_FOR.get(target) or 'byte', 1)})) and (
            qu is None or _named_ok(unit, qu, target))
    if target in ('other', 'count'):
        return False
    return dims == frozenset({('length', 1)})


_TARGET_KINDS = {
    'area': (frozenset({('length', 2)}), frozenset({('land', 1)})),
    'volume': (frozenset({('length', 3)}), frozenset({('capacity', 1)})),
    'speed': (frozenset({('length', 1), ('time', -1)}),), 'mass': (frozenset({('mass', 1)}),),
    'density': (frozenset({('mass', 1), ('length', -3)}),), 'acceleration': (frozenset({('length', 1), ('time', -2)}),),
    'time': (frozenset({('time', 1)}),), 'length': (frozenset({('length', 1)}),),
    **{dim: (_kind(frozenset({(si, 1)})),) for dim, si in _SI_FOR.items()},
    'data': (frozenset({('data', 1)}),),
}


def _target_message(qu):
    u = _length_word(qu)
    return {
        'area': f'Check the units. An area is in square units, such as {u}².',
        'volume': f'Check the units. A volume is in cubic units, such as {u}³.',
        'speed': 'Check the units. A speed is a distance per time, such as m/s or km/h.',
        'mass': 'Check the units. A mass is in units such as g or kg.',
        'density': 'Check the units. A density is a mass per volume, such as g/cm³.',
        'acceleration': 'Check the units. An acceleration is in units such as m/s².',
        'time': 'Check the units. A time is in units such as seconds, minutes or hours.',
        'angle': 'Check the units. An angle is in degrees.',
        'energy': 'Check the units. Energy is in joules (J).',
        'force': 'Check the units. A force is in newtons (N).',
        'power': 'Check the units. Power is in watts (W).',
        'pressure': 'Check the units. Pressure is in pascals (Pa).',
        'frequency': 'Check the units. Frequency is in hertz (Hz).',
        'voltage': 'Check the units. A voltage is in volts (V).',
        'resistance': 'Check the units. Resistance is in ohms.',
        'current': 'Check the units. A current is in amps.',
        'data': KIND_UNIT_FEEDBACK,
        'count': KIND_UNIT_FEEDBACK,
        'other': 'Check the units. That unit does not measure what the question asks for.',
    }.get(qu.target, f'Check the units. A length is in units such as {u}, not square or cubic units.')


def _involved(unit, qu, multi=False):
    """True when the unit measures the kind of quantity the question is about.

    A question that names no unit for the answer and asks for no one quantity the rules can read (whole-change review
    A3, 2026-10-29: "61 kg" and "61 km/h" were right for an angle, "5 kg" for a number of bits) takes a unit only
    when it measures one kind of quantity and the unit is of that kind: cm where it measures lengths in cm or m, cm³
    where it measures cm³, a degree sign where it is about angles or temperatures (``QuestionUnits.kinds``). Where it
    measures several kinds (a mass and a length, years and a rate per year) the quantity asked for cannot be told, so
    the pupil is asked to type just the number (fix pass 1a, 2026-11-03: "80 cm" was right for "two 40 cm3 samples
    give 80 cm3", "448 hours" for money after 3 years, "0 cm" for a number of points). One field of an answer in
    several fields takes a unit of any kind the question measures or asks for. The value must still be right."""
    named = qu.named()
    rest = []
    for base, power in unit:
        if _DIM.get(base) == 'neutral':
            continue
        if (base in _NAMED_ONLY or base == 'rad') and base not in named:
            return False
        rest.append((base, power))
    if not rest:
        return True
    if all(p < 0 for _, p in rest):
        # "£5.97/kg": an amount per unit of something the question uses (a price per kilogram)
        return all(any(_DIM.get(b) == _DIM.get(n) for n in named) for b, _ in rest)
    kinds = qu.kinds()
    return _kind(frozenset(rest)) in kinds and (multi or len(kinds) == 1)


def _unit_refusal(unit, qu, kind, multi=False):
    """None when the typed unit agrees with the question, else the kind message.

    ``multi`` is one field of an answer in several fields (number_fields). The question then asks for several
    quantities at once ("the bearing to the nearest degree and the distance", "the speed in km/h, then how far"), so
    a unit asked for one part is not forced on every part: a field passes with any asked unit, and with another unit
    when no asked unit has its dimension (km for the distance beside a bearing asked in degrees) and it agrees with
    the units the question uses. Review 2026-10-28: "59.55 km|131°" and "22 km/h|66 km|8 hours" were refused.

    Never a unit of the wrong kind of quantity (whole-change review A3, 2026-10-29): an angle asked for takes degrees
    only, and where nothing says what is asked, a unit is taken only when the question is about that kind of quantity
    (``_involved``); otherwise the pupil is asked to type just the number.
    """
    if _is_neutral(unit):
        return None
    if kind == 'bearing':
        return None if _is_degree(unit) else _mismatch_message(unit, qu, kind='bearing')
    if not qu.known:
        return None
    judged = False          # True when the unit asked for, or the quantity asked for, has judged the unit's kind
    if qu.asked:
        asked = {_canon(a) for a in qu.asked}
        if _canon(unit) in asked:
            return None
        if not multi or any(_dims(a) == _dims(unit) for a in qu.asked):
            return _mismatch_message(unit, qu)
    elif not multi and qu.asks_percent:
        return _mismatch_message(unit, qu, percent_asked=True)
    elif not multi and qu.asked_currency and any(p > 0 for _, p in unit):
        return _mismatch_message(unit, qu, currency=True)          # "4.9 kg" for a cost to the nearest penny
    elif qu.target and not multi:
        # One quantity asked for and no unit named: the unit must be able to measure it (35 cm for an area is
        # refused). Review 2026-10-28: the scale check below passed it, because the question uses cm.
        if not _fits_target(unit, qu.target, qu):
            return _target_message(qu)
        judged = True
    if not judged and not _involved(unit, qu, multi):
        return KIND_UNIT_FEEDBACK
    if _is_degree(unit):
        return None
    # No unit is asked for. A unit of a family the question already uses, at another scale (m where the question
    # says cm), is refused for lengths, masses, capacities and the science and computing units. Times are never
    # refused here (a speed in km/h from a time in minutes is right).
    used = qu.named()
    for base in {b for b, _ in unit} - used:
        dim = _DIM.get(base)
        if dim in _SCALE_DIMS and any(_DIM.get(u) == dim for u in used):
            return _mismatch_message(unit, qu)
    return None


def _currency_refusal(symbol, qu, multi=False):
    if not qu.known:
        return None
    if not multi and qu.target and not qu.currencies:
        return _target_message(qu)      # "24p" for a length: money is not a length
    if qu.asked_currency:
        return None if symbol in qu.asked_currency else _mismatch_message(None, qu, currency=True)
    if qu.currencies:
        return None if symbol in qu.currencies else _mismatch_message(None, qu, currency=True)
    if not qu.involves_money:
        return KIND_UNIT_FEEDBACK       # "£61" for an angle, or for "work out 3 + 4" (whole-change review A3)
    return None


def _clean_thousands(head, kind):
    """(clean head, refusal): "1,100" and "1 100" lose their separators; any other comma between digits is refused."""
    m = _THOUSANDS_COMMA_RE.fullmatch(head) or _THOUSANDS_SPACE_RE.fullmatch(head)
    if m:
        return (m.group(1) + m.group(2).replace(',', '').replace(' ', '') + (m.group(3) or '')), None
    if kind != 'fraction' and _COMMA_BETWEEN_DIGITS_RE.search(head) and '|' not in head:
        return head, DECIMAL_COMMA_FEEDBACK
    return head, None


def strip_value_units(text, *, question=None, kind='number', form=None, multi=False):
    """(clean text, refusal message or None) for one typed value.

    ``kind`` is the checker's answer type ('number', 'surd', 'bearing', ...). The clean text is what the checker's
    own parser should read: no unit, no currency symbol, no percent sign, no thousands separator. A refusal is a
    pupil-facing sentence; the value is then marked wrong with that sentence (never read as another unit).
    ``multi`` marks one field of an answer in several fields (see ``_unit_refusal``).
    """
    if not isinstance(text, str):
        return text, None
    s = text.translate(_NBSP).strip()
    if not s or len(s) > MAX_UNIT_FIELD_LEN:
        return text, None
    qu = question_units(question if question is None else str(question))

    currency = None
    percent = False
    unit = None
    sign = ''

    # a currency symbol in front (-£5, £ 3.50) or behind (3.50€)
    m = _LEAD_CURRENCY_RE.fullmatch(s)
    if m:
        sign, currency, s = m.group(1), m.group(2), m.group(3).strip()
    elif s[-1] in _CURRENCY_SYMBOLS:
        currency, s = s[-1], s[:-1].rstrip()

    # a unit, %, degree sign or pence after the number: the first place where the rest is wholly a unit
    for i, ch in enumerate(s):
        if not (ch.isascii() and ch.isalpha() or ch in '%°' or (ch == '/' and s[i + 1:i + 2].isalpha())):
            continue                    # "/kg" starts a unit too (£5.97/kg); "3/4" does not
        head = s[:i].rstrip()
        if not head or not _HEAD_END_RE.search(head.lower()):
            continue
        tail = s[i:].strip()
        low = tail.lower().rstrip('.')
        if low in _PERCENT_WORDS:
            percent = True
        elif low in _CURRENCY_WORDS:
            if currency is not None:
                return text, None
            currency = _CURRENCY_WORDS[low]
        elif low in ('°', 'deg', 'degree', 'degrees') or re.fullmatch(r'°\s*[cf]', low):
            unit = frozenset({('deg', 1)})
        else:
            unit = parse_unit(tail)
            if unit is None:
                continue
        s = head
        break

    if currency is not None and (percent or (unit is not None and any(p > 0 for _, p in unit))):
        return text, None               # £5 cm, £5%: not a number with a unit (£3.50 per kg is fine)
    if not any(ch.isdigit() for ch in s) and 'π' not in s and 'pi' not in s.lower():
        return text, None               # "£", "cm": no number to judge; the checker's own message stands

    refusal = None
    if percent and kind == 'bearing':
        refusal = _mismatch_message(None, qu, kind='bearing')
    elif percent:
        if form == 'probability' and kind in ('number', 'fraction'):
            return text, None           # the checker reads a percentage of a probability itself
        if qu.known and not qu.asks_percent:
            # A % changes the number (62.5% is 0.625), so it is dropped only where a percentage is asked for.
            refusal = _mismatch_message(None, qu, percent=True)
    if refusal is None and unit is not None:
        refusal = _unit_refusal(unit, qu, kind, multi=multi)
    if refusal is None and currency is not None:
        refusal = _currency_refusal(currency, qu, multi=multi)

    head = (sign + s).strip()
    if kind != 'bearing':
        head, comma = _clean_thousands(head, kind)
        refusal = refusal or comma
    elif _COMMA_BETWEEN_DIGITS_RE.search(head):
        refusal = refusal or DECIMAL_COMMA_FEEDBACK
    return head, refusal


def strip_units(answer_type, text, *, question=None, form=None, multi=False):
    """(clean text, refusal) for a whole typed answer of ``answer_type``; other types come back unchanged.

    ``multi`` is True when the text is one field of a stored number_fields answer checked on its own.
    """
    if answer_type not in UNIT_ANSWER_TYPES or not isinstance(text, str):
        return text, None
    if answer_type == 'standard_form':
        parts = text.split('|')
        if len(parts) > 3:
            return text, None
        cleaned, refusal = [], None
        for part in parts:
            c, r = strip_value_units(part, question=question, kind='number', form=form, multi=multi)
            cleaned.append(c)
            refusal = refusal or r
        return '|'.join(cleaned), refusal
    return strip_value_units(text, question=question, kind=answer_type, form=form, multi=multi)


# A session copy of a problem keeps at most 4,000 characters of its question (app._slim_problem_for_session: the
# cookie must stay small), and a drawn question carries 6 to 11 KB of SVG before the words that ask for the answer.
# When the question is cut, the slim copy carries this key: the question's text with the markup dropped, read by
# ``problem_question_text`` instead of the cut question, so Quick Test, saved, shared, suggestion and lesson-quiz checks
# read the same words as practice (whole-change review A2, 2026-10-29: "6 inches to centimetres ... in centimetres"
# lost its ask, and "15 inches" was marked right).
UNITS_TEXT_KEY = 'question_units_text'


def units_source_text(question):
    """The question with its tags dropped (entities kept), whitespace folded, bounded: what ``question_plain_text``
    reads from it, so reading this text gives the same units as reading the whole question."""
    t = re.sub(r'<[^>]*>', ' ', str(question or '')[:MAX_RAW_QUESTION_LEN])
    return re.sub(r'\s+', ' ', t).strip()[:MAX_QUESTION_LEN]


def problem_question_text(problem):
    """The text a stored problem's units are read from: its question and its answer-format hint."""
    if not isinstance(problem, dict):
        return None
    q = problem.get(UNITS_TEXT_KEY)
    if not isinstance(q, str) or not q:
        q = problem.get('question')
    hint = problem.get('answer_format_hint')
    if not q and not hint:
        return None
    return f"{q or ''} {hint or ''}"
