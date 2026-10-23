"""Recorder hook for the GCSE maths answer-verification test.

Generators call ``record('family', name=value, ...)`` once per variant, after the
inputs are drawn and before the problem is returned. In production the call is a
no-op: it returns at once unless a test has activated a sink with ``recording()``.

Rules (see docs/GCSE_MATHS_VERIFICATION.md):

* ``record`` never draws from ``random``, never returns a value the generator uses,
  and never changes the problem, so pupil output stays byte-identical.
* Record the inputs the pupil is *given* (the numbers in the question), not the
  answer. The test recomputes the answer with its own solver in
  ``scripts/gcse_verify/`` and that solver must not import generator helpers.
* Every recorded numeric input has to appear in the question text, or be listed in
  ``derived=`` (the presence guard stops recorded values drifting from shown values).
* ``ask=`` (or any other string input) names which quantity the question asks for.
"""
from __future__ import annotations

import contextlib
import contextvars
import functools

_SINK: contextvars.ContextVar = contextvars.ContextVar('gcse_verify_sink', default=None)


def record(family, derived=(), **inputs):
    """Record one variant's inputs for the verification test (no-op unless a sink is active)."""
    sink = _SINK.get()
    if sink is None:
        return
    sink.append({'family': family, 'inputs': inputs, 'derived': tuple(derived)})


def verifies(family, derived=(), **inputs):
    """Decorator form of ``record``: tags a variant function with a verification family.

    Used where the displayed question is itself the input (algebra families re-solved from the maths the
    pupil sees, so there is nothing to copy into a ``record`` line). The function runs unchanged and the
    record is written after it returns; no random numbers are drawn and the return value is untouched.
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            out = fn(*args, **kwargs)
            record(family, derived=derived, **inputs)
            return out
        return wrapper
    return deco


@contextlib.contextmanager
def recording():
    """Activate a sink for the duration of the ``with`` block and yield the list of records."""
    sink = []
    token = _SINK.set(sink)
    try:
        yield sink
    finally:
        _SINK.reset(token)


def is_recording():
    return _SINK.get() is not None
