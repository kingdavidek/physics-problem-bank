"""School rounding helpers (halves round up), shared by the GCSE maths generators.

Python's built-in ``round`` and ``format(x, '.2f')`` round halves to even and act on
the binary value, so ``round(5.625, 2)`` is 5.62 and ``f"{4.475:.2f}"`` is 4.47.
Pupils are taught to round halves up (5.63, 4.48). The helpers below work on the
shortest decimal representation of the number and use ``ROUND_HALF_UP``.

``round_half_up`` is a drop-in for ``round``; ``fmt_dp`` is a drop-in for the
``:.Nf`` format spec (trailing zeros kept).
"""
import builtins
import math
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP


def _quantize(d, places):
    """Half-up quantize with enough precision that big values (1e30) never raise."""
    exp = Decimal(1).scaleb(-int(places))
    prec = max(28, d.adjusted() + int(places) + 3)
    return d.quantize(exp, rounding=ROUND_HALF_UP, context=Context(prec=prec))


def _to_decimal(x):
    if isinstance(x, Decimal):
        return x
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return Decimal(x)
    if isinstance(x, float):
        if not math.isfinite(x):
            return None
        return Decimal(repr(x))
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError):
        return None


def round_half_up(x, ndigits=None):
    """Drop-in for ``round`` with school half-up rounding (away from zero on ties)."""
    d = _to_decimal(x)
    if d is None:
        return builtins.round(x) if ndigits is None else builtins.round(x, ndigits)
    if ndigits is None:
        return int(_quantize(d, 0))
    rounded = _quantize(d, ndigits)
    if isinstance(x, int) and not isinstance(x, bool):
        return int(rounded)
    return float(rounded)


def fmt_dp(x, dp=2):
    """Fixed ``dp`` decimal places with halves rounded up: fmt_dp(4.475, 2) -> '4.48'."""
    d = _to_decimal(x)
    if d is None:
        return format(x, f'.{int(dp)}f')
    rounded = _quantize(d, dp)
    text = format(rounded, 'f')
    if rounded == 0 and text.startswith('-'):
        text = text[1:]
    return text
