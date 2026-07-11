"""
Helpers for topic variant queues: 7 practice variants and 7 MCQ variants per difficulty tier.
"""
import importlib
import inspect
import pkgutil
import random
import re

_RANDOM_VALUE_OPS = re.compile(
    r"\brandom\.(?:randint|uniform|random|shuffle|sample|choices|triangular|gauss|getrandbits)\b"
)

TIER_VARIANT_COUNT = 7

STANDARD_MODE_ALIASES = frozenset({"revision", "exam", "practice", "standard"})


def normalize_mode(mode):
    """Map legacy revision/exam modes to standard practice; keep mcq and lesson."""
    if not mode:
        return "standard"
    m = str(mode).strip().lower()
    if m in STANDARD_MODE_ALIASES:
        return "standard"
    if m == "mcq":
        return "mcq"
    if m == "lesson":
        return "lesson"
    return "standard"


def select_tier_variants(pool, count=TIER_VARIANT_COUNT):
    """Return up to `count` distinct variant callables from a practice pool."""
    if not pool:
        return []
    if len(pool) >= count:
        return random.sample(pool, count)
    shuffled = random.sample(pool, len(pool))
    out = list(shuffled)
    idx = 0
    while len(out) < count:
        out.append(shuffled[idx % len(shuffled)])
        idx += 1
    return out[:count]


def _bank_pool_for_difficulty(bank, difficulty):
    tagged = [item for item in bank if item.get("difficulty") == difficulty]
    if len(tagged) >= TIER_VARIANT_COUNT:
        return tagged
    if tagged:
        return tagged

    n = len(bank)
    if n == 0:
        return []
    third = max(1, n // 3)
    if difficulty == "foundational":
        return bank[:third]
    if difficulty == "intermediate":
        return bank[third : 2 * third] if n > third else bank
    return bank[2 * third :] if n > 2 * third else bank


def normalize_mcq_bank(items):
    """Ensure each MCQ dict has difficulty, sol, hint, and marks for variant pooling."""
    n = len(items)
    third = max(1, n // 3) if n else 0
    out = []
    for i, raw in enumerate(items):
        item = dict(raw)
        if "difficulty" not in item:
            if i < third:
                item["difficulty"] = "foundational"
            elif i < 2 * third:
                item["difficulty"] = "intermediate"
            else:
                item["difficulty"] = "difficult"
        if "hint" not in item:
            item["hint"] = item.get("sol", "")
        if "sol" not in item:
            item["sol"] = f"Answer: {item.get('ans', '')}<br><br>{item.get('hint', '')}"
        item.setdefault("marks", 1)
        out.append(item)
    return out


def make_mcq_variant_fns(bank, topic_slug, difficulty, count=TIER_VARIANT_COUNT):
    """
    Build `count` named MCQ variant functions that draw from `bank` for `difficulty`.
    Each returns (q, s, hint, marks, opts, ans).
    """
    pool = _bank_pool_for_difficulty(bank, difficulty) or list(bank)
    if not pool:
        return []

    fns = []
    for i in range(count):
        preferred = pool
        if len(pool) >= count:
            preferred = [pool[(i + j) % len(pool)] for j in range(len(pool))]

        def _variant(items=preferred, variant_index=i):
            item = random.choice(items)
            hint = item.get("hint") or item.get("sol", "")
            return (
                item["q"],
                item["sol"],
                hint,
                item.get("marks", 1),
                item["opts"],
                item["ans"],
            )

        _variant.__name__ = f"{topic_slug}_mcq_{difficulty}_{i + 1}"
        if all(isinstance(x, dict) for x in preferred) and not any(callable(x) for x in preferred):
            _variant._bank_only = True
        fns.append(_variant)
    return fns


def mcq_variants_from_bank(bank, topic_slug, difficulty, count=TIER_VARIANT_COUNT):
    return make_mcq_variant_fns(normalize_mcq_bank(bank), topic_slug, difficulty, count)


def mcq_variants_from_bank_with_procedural(
    bank, procedural_fns, topic_slug, difficulty, count=TIER_VARIANT_COUNT
):
    """
    Bank-backed MCQ variants. When difficulty is 'difficult', the random pool also
    includes procedural generators (each returns a 6-tuple).
    """
    normalized = normalize_mcq_bank(bank)
    pool = _bank_pool_for_difficulty(normalized, difficulty) or list(normalized)
    proc = list(procedural_fns) if difficulty == "difficult" else []
    entries = list(pool) + proc

    def _dispatch():
        if not entries:
            raise ValueError(f"No MCQ pool for {topic_slug} ({difficulty})")
        pick = random.choice(entries)
        if callable(pick):
            return pick()
        hint = pick.get("hint") or pick.get("sol", "")
        return (
            pick["q"],
            pick["sol"],
            hint,
            pick.get("marks", 1),
            pick["opts"],
            pick["ans"],
        )

    if proc:
        _dispatch._randomizable = True
    else:
        _dispatch._bank_only = True

    return mcq_variants_from_fn(_dispatch, topic_slug, difficulty, count)


def mcq_variants_from_fn(
    mcq_fn, topic_slug, difficulty, count=TIER_VARIANT_COUNT, *, slot_param=None
):
    """Named wrappers around a procedural MCQ generator (one per queue slot).

    When ``slot_param`` is set (e.g. ``"mcq_type"`` or ``"slot_index"``), each
    queue slot binds to a fixed value so rerolling keeps the same question stem.
    """
    fns = []
    sig = inspect.signature(mcq_fn)
    use_slot = slot_param is not None and slot_param in sig.parameters

    for i in range(count):
        if use_slot:
            slot_value = i + 1 if slot_param == "mcq_type" else i

            def _variant(sv=slot_value, fn=mcq_fn, param=slot_param):
                return fn(**{param: sv})

            _variant.__name__ = f"{topic_slug}_mcq_{difficulty}_{i + 1}"
            bound = lambda sv=slot_value, fn=mcq_fn, param=slot_param: fn(**{param: sv})
            bound.__name__ = _variant.__name__
            _variant._randomizable = variant_is_randomizable(bound)
        else:
            def _variant(fn=mcq_fn):
                return fn()

            _variant.__name__ = f"{topic_slug}_mcq_{difficulty}_{i + 1}"
            _variant._mcq_source = mcq_fn
        fns.append(_variant)
    return fns


def mcq_variants_from_pool(generator_fns, topic_slug, difficulty, count=TIER_VARIANT_COUNT):
    """One queue slot per generator in ``generator_fns`` (cycled if needed)."""
    pool = list(generator_fns)
    if not pool:
        return []

    fns = []
    for i in range(count):
        gen = pool[i % len(pool)]

        def _variant(source=gen):
            return source()

        _variant.__name__ = f"{topic_slug}_mcq_{difficulty}_{i + 1}"
        _variant._randomizable = variant_is_randomizable(gen)
        fns.append(_variant)
    return fns


_IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")


def _probe_variant_varies(fn, attempts=8):
    """Empirically decide if a variant produces different content across runs.

    Returns True/False, or None if the variant could not be executed (so the
    caller can fall back to static analysis). For MCQ generators that return a
    tuple, only the question text (first element) is compared so option
    shuffling does not count as rerollable content.
    """
    def _question_text(result):
        if isinstance(result, tuple) and result:
            return str(result[0])
        return str(result)

    try:
        first = _question_text(fn())
    except Exception:
        return None
    for _ in range(attempts - 1):
        try:
            nxt = _question_text(fn())
        except Exception:
            return None
        if nxt != first:
            return True
    return False


def variant_is_randomizable(fn, _depth=0, _seen=None):
    """True when re-running the same named variant can change its content.

    Explicit markers win first (``_fixed_stem`` / ``_randomizable`` /
    ``_bank_only``). Otherwise we run the variant a few times and check whether
    the output changes; this catches randomisation that static source inspection
    cannot (e.g. ``random.choice`` picking numeric values, or thin one-line
    wrappers that delegate to a randomising generator). Static analysis is kept
    only as a fallback for variants that cannot be executed safely.
    """
    if fn is None:
        return False
    if getattr(fn, "_fixed_stem", False):
        return False
    if getattr(fn, "_randomizable", False):
        return True
    if getattr(fn, "_bank_only", False):
        return False

    source_fn = getattr(fn, "_mcq_source", None)
    if source_fn is not None:
        return variant_is_randomizable(source_fn, _depth, _seen)

    probed = _probe_variant_varies(fn)
    if probed is not None:
        return probed

    # --- Static fallback (only when the variant cannot be executed) ---
    try:
        source = inspect.getsource(fn)
    except (OSError, TypeError):
        return False

    if _RANDOM_VALUE_OPS.search(source):
        return True

    # Follow delegation into same-module callables the wrapper references.
    if _depth < 6:
        if _seen is None:
            _seen = set()
        _seen.add(getattr(fn, "__name__", None))
        module_globals = getattr(fn, "__globals__", {})
        own_module = getattr(fn, "__module__", None)
        for name in set(_IDENTIFIER_RE.findall(source)):
            if name in _seen:
                continue
            target = module_globals.get(name)
            if not callable(target):
                continue
            if getattr(target, "__module__", None) != own_module:
                continue
            _seen.add(name)
            if variant_is_randomizable(target, _depth + 1, _seen):
                return True

    if "random.choice" in source:
        return False
    return False


_VARIANT_BY_NAME_CACHE = {}


def lookup_variant_by_name(variant_name):
    """Find a module-level variant generator by its ``__name__``."""
    if not variant_name:
        return None
    if variant_name in _VARIANT_BY_NAME_CACHE:
        return _VARIANT_BY_NAME_CACHE[variant_name]

    import generators

    found = None
    for _importer, modname, _ispkg in pkgutil.walk_packages(
        generators.__path__, generators.__name__ + "."
    ):
        try:
            mod = importlib.import_module(modname)
        except ImportError:
            continue
        obj = getattr(mod, variant_name, None)
        if callable(obj) and getattr(obj, "__name__", None) == variant_name:
            found = obj
            break

    _VARIANT_BY_NAME_CACHE[variant_name] = found
    return found


def pick_named_variant(variants, variant_name=None):
    """
    Resolve a variant callable. When ``variant_name`` is set, keep that variant
    even if it is outside the current random tier sample.
    """
    if not variants:
        raise ValueError("No variants available")
    if variant_name is None:
        return random.choice(variants)

    variant_map = {v.__name__: v for v in variants}
    fn = variant_map.get(variant_name)
    if fn is not None:
        return fn

    fn = lookup_variant_by_name(variant_name)
    if fn is not None:
        return fn

    raise ValueError(f"Unknown variant: {variant_name}")


def resolve_variant_callable(variants_func, difficulty, mode, variant_name):
    """Return the callable for a named variant in the current queue, if any."""
    if not variants_func or not variant_name:
        return None
    variants = variants_func(difficulty, normalize_mode(mode))
    if not variants:
        return None
    try:
        return pick_named_variant(variants, variant_name)
    except ValueError:
        return None


def dispatch_mcq_generator(variants_func, difficulty, variant_name, topic_config_fields):
    """
    Run MCQ variants and return a make_problem-ready dict payload.
    topic_config_fields: (difficulty, marks, level, subject, topic) passed to make_problem.
    """
    from generators.shared.utils import make_problem

    variants = variants_func(difficulty, "mcq")
    q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
    level, subject, topic = topic_config_fields
    return make_problem(
        q, s, hint, difficulty, marks, level, subject, topic,
        options=opts, correct_answer=ans,
    )


def run_mcq_variant(variants, variant_name=None):
    """Call an MCQ variant by name; returns 6-tuple from the variant callable."""
    return pick_named_variant(variants, variant_name)()


def run_practice_variant(variants_func, difficulty, mode, variant_name=None):
    """Return (q, s, hint, marks) from a named practice variant."""
    variants = variants_func(difficulty, normalize_mode(mode))
    if not variants:
        raise ValueError("No practice variants available")
    return pick_named_variant(variants, variant_name)()


def apply_practice_variants_return(pool, difficulty, mode, mixed_builder=None):
    """
    Standard tail for *_variants functions.
    `mixed_builder` optional callable returning a mixed-difficulty list.
    """
    mode = normalize_mode(mode)
    if mode == "mcq":
        return []
    if difficulty in ("foundational", "intermediate", "difficult"):
        return select_tier_variants(pool, TIER_VARIANT_COUNT)
    if mixed_builder:
        return mixed_builder()
    return select_tier_variants(pool, TIER_VARIANT_COUNT)
