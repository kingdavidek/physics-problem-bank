"""GCSE maths answer-verification helpers (see docs/GCSE_MATHS_VERIFICATION.md).

Independence rule: the ``solvers_*`` modules recompute answers from the inputs a
generator records. They may import only the standard library, sympy and
``generators.shared.rounding``; never a generator module or one of its helpers.
"""
