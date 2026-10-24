"""Verification register: which GCSE maths slots are verified, pending, or pinned.

The register is the ratchet.  Every topic is in VERIFIED_TOPICS and verified slot by slot; a new topic must be
added there with its solvers (PENDING_TOPICS is empty and the test fails if anything is left pending).  Static MCQ
bank items either have a re-solve spec in solvers_bank_*.py (keyed by item digest) or are listed in STATIC_EXEMPT
with a reason and pinned by digest; changing or adding an item fails the test until it has a spec or an entry
(run the test with --print-digests to list the digests).
"""
from __future__ import annotations

VERIFIED_TOPICS = (
    'number', 'ratio_proportion', 'bidmas', 'multiples_factors', 'decimals', 'fdp',
    'pythagoras', 'compound_measures', 'mensuration', 'trigonometry', 'bearings',
    # Phase 2 (algebra)
    'algebra', 'equations_inequalities', 'changing_the_subject', 'sequences', 'surds',
    'simultaneous_equations', 'completing_the_square', 'quadratic_simultaneous_equations', 'graphs',
    'graphical_simultaneous_equations', 'algebraic_fractions', 'functions', 'algebraic_proof',
    # Phase 3
    'statistics', 'probability', 'geometry_angles', 'transformations',
    'similarity_congruence', 'circle_theorems', 'constructions_loci', 'vectors',
)

# The Phase 2 (algebra) topics: heavier solvers, so the default run uses fewer seeds for them.
ALGEBRA_TOPICS = (
    'algebra', 'equations_inequalities', 'changing_the_subject', 'sequences', 'surds',
    'simultaneous_equations', 'completing_the_square', 'quadratic_simultaneous_equations', 'graphs',
    'graphical_simultaneous_equations', 'algebraic_fractions', 'functions', 'algebraic_proof',
)

# The Phase 3 topics (statistics, probability, geometry): their questions get the same cosmetic algebra check.
PHASE3_TOPICS = (
    'statistics', 'probability', 'geometry_angles', 'transformations',
    'similarity_congruence', 'circle_theorems', 'constructions_loci', 'vectors',
)

PENDING_TOPICS = ()

# Slots in verified topics that cannot be re-solved, with the reason.  Key: 'slug/mode/fn'.  Empty in Phase 1.
EXEMPT = {}

# Ordered-proof slots whose steps are not a strict chain: the pairs of canonical step positions (1-based) that a
# person read and judged logically independent, so a pupil may put them either way round (decided 2026-10-23,
# docs/GCSE_MATHS_VERIFICATION.md "Decisions").  The test compares this with the order spec each problem carries;
# an ordered-proof slot that is not listed here must be a strict chain, so adding or widening an alternative order
# in a generator fails the test until the pairs are re-read and listed.  Key: 'slug/mode/fn'.
ORDER_FREE_PAIRS = {
    'algebraic_proof/standard/_ap_f_even_form': frozenset({(1, 2), (1, 3)}),
    'algebraic_proof/standard/_ap_f_odd_form': frozenset({(1, 2)}),
    'algebraic_proof/standard/_ap_i_product_consecutive': frozenset({(3, 4)}),
    'algebraic_proof/standard/_ap_d_n_squared_plus_n': frozenset({(3, 4)}),
    'similarity_congruence/standard/_sc_i9_proof_aa_parallel': frozenset({(1, 3), (2, 3)}),
    'similarity_congruence/standard/_sc_d1_midpoint_theorem_proof': frozenset({(1, 3), (2, 3), (5, 6)}),
    'similarity_congruence/standard/_sc_d7_congruence_proof': frozenset({(1, 2), (1, 3), (2, 3)}),
    'circle_theorems/standard/_ct_d2_prove_angle': frozenset({(2, 3)}),
    'circle_theorems/standard/_ct_d10_prove_cyclic': frozenset({(1, 2), (1, 3), (2, 3)}),
    'constructions_loci/standard/_cl_i2_equilateral_triangle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_i11_circumcircle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_i12_incircle': frozenset({(1, 2)}),
    'constructions_loci/standard/_cl_d1_locus_proof': frozenset(
        {(1, 5), (1, 6), (2, 5), (2, 6), (2, 7), (3, 5), (3, 6), (3, 7), (4, 5), (4, 6), (4, 7)}),
    'sequences/standard/_seq_diff_show_divisible': frozenset({(1, 2)}),
    'sequences/standard/_seq_diff_arithmetic_proof': frozenset({(1, 2)}),
    'vectors/standard/_vectors_diff_vector_inequality': frozenset({(1, 2)}),
}

# Topics whose lesson quiz cannot have the usual shape (ten questions, 3 foundational + 4 intermediate + 3 difficult)
# because a band has too few distinct question texts for the quiz's no-repeat rule.  Slug -> (fewest questions the
# quiz must still have, reason).  Empty since 2026-10-23: algebraic_proof, vectors, pythagoras and
# simultaneous_equations were the four short topics and now have enough distinct questions in every band, so
# the quiz sweep asserts 10 questions in the 3 / 4 / 3 mix, with no repeat, for every topic.  A new entry
# means a band is short of content; the fix is more questions, not a change to the quiz builder.
QUIZ_SHAPE = {}

# Static MCQ bank items that are not re-solved.  Every other bank item (319 of 334 at Phase 4) has a solver in
# solvers_bank_*.py, keyed by the item's digest (mcq.item_digest: question, sorted option texts, keyed text), so it
# is checked against a recomputed answer and a changed item fails until its solver is updated.  The items below
# have nothing to compute: they ask for a definition, a name, a choice of method or a plain-language description.
# They stay pinned by digest and a person reviews any change.  Digest -> (category, reason of 20+ characters).
# Reviewed 2026-10-23 (Phase 4); every key and option below was read by hand again.
STATIC_EXEMPT = {
    'd2ad3f201b3c': ('conceptual', 'BIDMAS: what the letter I stands for. Vocabulary of the mnemonic; nothing to compute.'),
    'bbd4b325472c': ('conceptual', 'Definition of the hypotenuse (the side opposite the right angle); a naming convention.'),
    '74b0c6a3fb7c': ('conceptual', 'What the SOH CAH TOA mnemonic is for; vocabulary, nothing to compute.'),
    '2383102f84e0': ('method', 'Choice of rule (cosine rule for two sides and the included angle); a method judgement.'),
    'e747319c3334': ('conceptual', 'Which ratio is outside the GCSE right-angled set (sec); syllabus knowledge, no computation.'),
    '6b871d529a0a': ('conceptual', 'Definition of the angle of elevation (measured up from the horizontal); a naming convention.'),
    '44b1476f6ef1': ('method', 'Best first step in a 3D trigonometry problem; a method judgement, not a calculation.'),
    'f201e85aaa3b': ('method', 'Choice of rule for an angle from three sides (cosine rule rearranged); a method judgement.'),
    'e8537eb33269': ('conceptual', 'Meaning of sin A greater than 1 in the sine rule (no such triangle); interpretation, not a number.'),
    '0b8800279556': ('conceptual', 'Plain-language description of elimination; a definition, nothing to compute.'),
    '5d9cdf21e4ce': ('method', 'Which tools construct a triangle from three sides (ruler and compasses); a method statement.'),
    'cfc695431cea': ('conceptual', 'Locus equidistant from two intersecting lines (the angle bisectors); described in words only.'),
    'aa47f1d3264c': ('conceptual', 'Region closer to A and within 6 cm of B described in words; a region has no single value.'),
    '9ff174a302c5': ('conceptual', 'Shape of the locus of points at a fixed distance from a segment (stadium); described in words.'),
    'c0446fea7f9a': ('method', 'Method for constructing 30 degrees (build 60 degrees then bisect); a construction procedure.'),
}
