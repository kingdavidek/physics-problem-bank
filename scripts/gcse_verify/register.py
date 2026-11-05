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
    'algebraic_proof/standard/gcse_ap_i_difference_of_squares_identity': frozenset({(1, 2)}),
    'algebraic_proof/standard/gcse_ap_d_difference_squares_multiple_of_eight': frozenset({(1, 2)}),
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

# ── Variety (docs/GCSE_MATHS_VARIETY.md, Phases 0 and 1) ────────────────────────────────────────────────────────
# Practice variants taken out of their tier's pool.  Each function stays defined at module level, in exactly one
# generator module, so a queue, a saved problem or a test that still names it resolves through the global
# fallback (variant_utils.lookup_variant_by_name); the verification smoke generates and re-solves every one on
# 2 seeds each run (check "retired").  Key: 'slug/fn'.  Value: (replaced_by, reason, tier it left).
RETIRED = {
    'algebra/algebra_practice_linear_1': ('algebra_practice_linear', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'algebra/algebra_practice_linear_2': ('algebra_practice_linear', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'algebra/algebra_practice_linear_3': ('algebra_practice_linear', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'algebra/algebra_practice_factorise_1': ('algebra_practice_factorise', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'algebra/algebra_practice_factorise_2': ('algebra_practice_factorise', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'algebra/algebra_practice_factorise_3': ('algebra_practice_factorise', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'algebra/algebra_practice_quadratic_2': ('algebra_practice_consecutive_integers', 'exact duplicate of algebra_practice_consecutive_integers', 'difficult'),
    'algebra/algebra_practice_quadratic_3': ('algebra_practice_expand_mixed', 'exact duplicate of algebra_practice_expand_mixed', 'difficult'),
    'bearings/_brg_found_back_gt_180': ('_brg_found_back_bearing', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'bearings/_brg_found_back_lt_180': ('_brg_found_back_bearing', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'bearings/_brg_found_compass_NE': ('_brg_found_compass_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'bearings/_brg_found_compass_NW': ('_brg_found_compass_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'bearings/_brg_found_compass_SE': ('_brg_found_compass_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'bearings/_brg_found_compass_SW': ('_brg_found_compass_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'constructions_loci/_cl_d13_construct_45': ('_cl_d_construct_angle', 'merged sibling (the new slot draws it at random)', 'difficult'),
    'constructions_loci/_cl_d14_construct_30': ('_cl_d_construct_angle', 'merged sibling (the new slot draws it at random)', 'difficult'),
    'equations_inequalities/_eq_found_negative_answer': ('_eq_found_two_step_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'equations_inequalities/_eq_found_two_step': ('_eq_found_two_step_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'graphs/_gra_diff_11': ('_gra_diff_01', 'exact duplicate of _gra_diff_01', 'difficult'),
    'graphs/_gra_diff_13': ('_gra_diff_06', 'exact duplicate of _gra_diff_06', 'difficult'),
    'graphs/_gra_diff_15': ('_gra_diff_10', 'exact duplicate of _gra_diff_10', 'difficult'),
    'graphs/_gra_diff_16': ('_gra_diff_02', 'exact duplicate of _gra_diff_02', 'difficult'),
    'graphs/_gra_diff_17': ('_gra_diff_04', 'exact duplicate of _gra_diff_04', 'difficult'),
    'graphs/_gra_found_10': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'graphs/_gra_found_11': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'graphs/_gra_found_12': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'graphs/_gra_found_13': ('_gra_found_02', 'exact duplicate of _gra_found_02', 'foundational'),
    'graphs/_gra_found_14': ('_gra_found_04', 'exact duplicate of _gra_found_04', 'foundational'),
    'graphs/_gra_found_15': ('_gra_found_08', 'exact duplicate of _gra_found_08', 'foundational'),
    'graphs/_gra_inter_11': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'graphs/_gra_inter_12': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'graphs/_gra_inter_13': ('_gra_scatter_correlation_any', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'graphs/_gra_inter_15': ('_gra_inter_06', 'exact duplicate of _gra_inter_06', 'intermediate'),
    'probability/_prob_diff_17': ('gcse_prob_independent_union', 'exact duplicate of _prob_diff_03, itself retired in batch C2', 'difficult'),
    'probability/_prob_found_13': ('_prob_found_01', 'exact duplicate of _prob_found_01', 'foundational'),
    'pythagoras/_py_f3_is_right_yes': ('_py_f_is_right_angled', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'pythagoras/_py_f4_is_right_no': ('_py_f_is_right_angled', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'ratio_proportion/_ratio_diff_05': ('gcse_ratio_three_part_difference', 'exact duplicate of _ratio_diff_01, itself retired in batch C2', 'difficult'),
    'ratio_proportion/_ratio_diff_07': ('_ratio_diff_02', 'exact duplicate of _ratio_diff_02', 'difficult'),
    'ratio_proportion/_ratio_diff_08': ('_ratio_diff_03', 'exact duplicate of _ratio_diff_03', 'difficult'),
    'ratio_proportion/_ratio_diff_12': ('_ratio_diff_04', 'exact duplicate of _ratio_diff_04', 'difficult'),
    'ratio_proportion/_ratio_diff_13': ('_ratio_diff_03', 'exact duplicate of _ratio_diff_03', 'difficult'),
    'ratio_proportion/_ratio_diff_18': ('gcse_ratio_change_after_adding', 'exact duplicate of _ratio_diff_10 (itself retired in batch C1 as a tier echo)', 'difficult'),
    'ratio_proportion/_ratio_inter_10': ('_ratio_inter_01', 'exact duplicate of _ratio_inter_01', 'intermediate'),
    'ratio_proportion/_ratio_inter_11': ('_ratio_inter_02', 'exact duplicate of _ratio_inter_02', 'intermediate'),
    'ratio_proportion/_ratio_inter_12': ('_ratio_inter_03', 'exact duplicate of _ratio_inter_03', 'intermediate'),
    'ratio_proportion/_ratio_inter_13': ('_ratio_inter_09', 'exact duplicate of _ratio_inter_09', 'intermediate'),
    'sequences/_seq_inter_find_nth_term': ('_seq_inter_find_nth_term_any', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'sequences/_seq_inter_nth_term_negative_d': ('_seq_inter_find_nth_term_any', 'merged sibling (the new slot draws it at random)', 'intermediate'),
    'statistics/_stats_diff_02': ('_stats_diff_09', 'exact duplicate of _stats_diff_09', 'difficult'),
    'statistics/_stats_diff_10': ('gcse_stats_combined_mean', 'exact duplicate of _stats_diff_03 (itself retired in batch C1 as a tier echo)', 'difficult'),
    'statistics/_stats_diff_11': ('_stats_diff_05', 'exact duplicate of _stats_diff_05', 'difficult'),
    'statistics/_stats_diff_12': ('gcse_stats_capture_recapture', 'exact duplicate of _stats_diff_04 (itself retired in batch C1 as a tier echo)', 'difficult'),
    'statistics/_stats_diff_13': ('_stats_diff_05', 'exact duplicate of _stats_diff_05', 'difficult'),
    'statistics/_stats_diff_14': ('gcse_stats_missing_frequency_mean', 'exact duplicate of _stats_diff_06 (itself retired in batch C1 as a tier echo)', 'difficult'),
    'statistics/_stats_diff_15': ('_stats_diff_09', 'exact duplicate of _stats_diff_09', 'difficult'),
    'statistics/_stats_diff_16': ('_stats_diff_05', 'exact duplicate of _stats_diff_05', 'difficult'),
    'statistics/_stats_diff_17': ('_stats_diff_09', 'exact duplicate of _stats_diff_09', 'difficult'),
    'statistics/_stats_found_09': ('_stats_found_01', 'exact duplicate of _stats_found_01', 'foundational'),
    'statistics/_stats_found_10': ('_stats_found_02', 'exact duplicate of _stats_found_02', 'foundational'),
    'statistics/_stats_found_11': ('_stats_found_03', 'exact duplicate of _stats_found_03', 'foundational'),
    'statistics/_stats_found_12': ('_stats_found_04', 'exact duplicate of _stats_found_04', 'foundational'),
    'statistics/_stats_found_13': ('_stats_found_05', 'exact duplicate of _stats_found_05', 'foundational'),
    'statistics/_stats_found_14': ('_stats_found_06', 'exact duplicate of _stats_found_06', 'foundational'),
    'statistics/_stats_found_15': ('_stats_found_07', 'exact duplicate of _stats_found_07', 'foundational'),
    'statistics/_stats_inter_10': ('_stats_inter_02', 'exact duplicate of _stats_inter_02', 'intermediate'),
    'statistics/_stats_inter_12': ('_stats_inter_05', 'exact duplicate of _stats_inter_05', 'intermediate'),
    'statistics/_stats_inter_13': ('_stats_inter_06', 'exact duplicate of _stats_inter_06', 'intermediate'),
    'statistics/_stats_inter_14': ('_stats_inter_07', 'exact duplicate of _stats_inter_07', 'intermediate'),
    'statistics/_stats_inter_15': ('_stats_inter_08', 'exact duplicate of _stats_inter_08', 'intermediate'),
    'transformations/_trans_found_reflect_xaxis': ('_trans_found_reflect_axis', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'transformations/_trans_found_reflect_xk': ('_trans_found_reflect_line_k', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'transformations/_trans_found_reflect_yaxis': ('_trans_found_reflect_axis', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'transformations/_trans_found_reflect_yk': ('_trans_found_reflect_line_k', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'vectors/_vectors_diff_vector_proof_sim': ('_vectors_diff_geometry_proof', 'exact duplicate of _vectors_diff_geometry_proof', 'difficult'),
    'vectors/_vectors_found_magnitude_3_4': ('_vectors_found_magnitude_triple', 'merged sibling (the new slot draws it at random)', 'foundational'),
    'vectors/_vectors_found_magnitude_6_8': ('_vectors_found_magnitude_triple', 'merged sibling (the new slot draws it at random)', 'foundational'),
    # Phase 3 batch C1 (2026-10-28): echoes of foundational or intermediate kinds that sat in a difficult tier, each
    # replaced by a harder kind from the section 4 gap list (docs/GCSE_MATHS_VARIETY.md section 21).
    'statistics/_stats_diff_01': ('gcse_stats_freq_polygon_mean', 'tier echo of _stats_inter_02 (estimated mean from a histogram) in the difficult tier', 'difficult'),
    'statistics/_stats_diff_03': ('gcse_stats_combined_mean', 'tier echo of _stats_inter_08 (compare two distributions) in the difficult tier', 'difficult'),
    'statistics/_stats_diff_04': ('gcse_stats_capture_recapture', 'tier echo of _stats_inter_04 (line of best fit) in the difficult tier', 'difficult'),
    'statistics/_stats_diff_06': ('gcse_stats_missing_frequency_mean', 'tier echo of _stats_inter_01 (mean from a frequency table) in the difficult tier', 'difficult'),
    'statistics/_stats_diff_07': ('gcse_stats_two_way_percent', 'tier echo of _stats_found_08 and _stats_inter_03 (pie chart angle) in the difficult tier', 'difficult'),
    'statistics/_stats_diff_08': ('gcse_stats_stem_leaf_iqr', 'tier echo of _stats_inter_06 (box plot IQR) in the difficult tier', 'difficult'),
    'probability/_prob_diff_09': ('gcse_prob_two_dice_product', 'tier echo of _prob_found_05 and _prob_inter_08 (relative frequency) in the difficult tier', 'difficult'),
    'probability/_prob_diff_10': ('gcse_prob_frequency_tree_conditional', 'tier echo of _prob_found_04 and _prob_inter_07 (expected frequency) in the difficult tier', 'difficult'),
    'probability/_prob_diff_11': ('gcse_prob_two_way_conditional', 'tier echo of _prob_found_02 (one bag of counters) in the difficult tier', 'difficult'),
    'probability/_prob_diff_12': ('gcse_prob_venn_set_notation', 'tier echo of _prob_found_07 and _prob_inter_01 (two coins) in the difficult tier', 'difficult'),
    'probability/_prob_diff_15': ('gcse_prob_venn_conditional', 'tier echo of _prob_found_03 and _prob_inter_14 (the complement) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_03': ('gcse_gra_circle_tangent', 'tier echo of _gra_inter_06 (root from a factorised quadratic) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_05': ('gcse_gra_exponential_read', 'tier echo of _gra_found_09 and _gra_inter_09 (a reciprocal value) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_07': ('gcse_gra_perpendicular_line', 'tier echo of _gra_found_08 and _gra_inter_07 (a midpoint) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_08': ('gcse_gra_circle_equation', 'tier echo of _gra_inter_08 (where two simple lines meet) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_09': ('gcse_gra_transformation_point', 'tier echo of _gra_found_05 and _gra_inter_02 (equation from gradient and intercept) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_14': ('gcse_gra_vt_distance', 'tier echo of _gra_found_07 and _gra_inter_04 (speed from a distance-time graph) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_06': ('gcse_ratio_inverse_square', 'tier echo of _ratio_found_12 and _ratio_inter_07 (density style rate) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_09': ('gcse_ratio_fraction_of_groups', 'tier echo of _ratio_found_07 and _ratio_inter_08 (recipe scaling) in the difficult tier; its C1 replacement, the limiting recipe, moved to the intermediate tier in batch C2', 'difficult'),
    'ratio_proportion/_ratio_diff_10': ('gcse_ratio_change_after_adding', 'tier echo of _ratio_found_09 and _ratio_inter_16 (three-part sharing) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_11': ('gcse_ratio_proportional_cube', 'tier echo of _ratio_found_08 and _ratio_inter_06 (unit conversion) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_15': ('gcse_ratio_proportional_root', 'tier echo of _ratio_found_10 and _ratio_inter_14 (best buy) in the difficult tier', 'difficult'),
    # Phase 3 batch C2 (2026-10-28): the last tier echoes into the difficult tiers and the intermediate graphs tier's
    # echoes of foundational kinds, each replaced by a harder kind of generators/gcse/maths_variety_c2.py
    'probability/_prob_diff_01': ('gcse_prob_counters_algebraic', 'tier echo of _prob_found_14 (at least one success) in the difficult tier', 'difficult'),
    'probability/_prob_found_15': ('_prob_found_11', 'C9 (whole-change review): a conditional probability by the formula P(B|A) is Higher content; the copy in the Foundation tier is retired and _prob_diff_02 (the same question) is back in the difficult tier; _prob_found_11 is the nearest Foundation kind (an independent product)', 'foundational'),
    'probability/_prob_diff_03': ('gcse_prob_independent_union', 'tier echo of _prob_found_12 and _prob_inter_06 (A or B, not exclusive) in the difficult tier', 'difficult'),
    'probability/_prob_diff_07': ('gcse_prob_three_same_colour', 'tier echo of _prob_found_10 and _prob_inter_04 (a Venn total) in the difficult tier', 'difficult'),
    'probability/_prob_diff_08': ('gcse_prob_two_day_dependent', 'tier echo of _prob_found_11 and _prob_inter_05 (independent product) in the difficult tier', 'difficult'),
    'probability/_prob_diff_14': ('gcse_prob_trials_needed', 'tier echo of _prob_found_06 and _prob_inter_15 (mutually exclusive) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_01': ('gcse_ratio_three_part_difference', 'tier echo of _ratio_inter_19 (merging classes) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_14': ('gcse_ratio_percent_more', 'tier echo of _ratio_found_11 and _ratio_inter_18 (map scale) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_16': ('gcse_ratio_algebraic_parts', 'tier echo of _ratio_found_15 and _ratio_inter_17 (inverse proportion formula) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_17': ('gcse_ratio_expression_ratio', 'tier echo of _ratio_found_14 and _ratio_inter_05 (direct proportion formula) in the difficult tier', 'difficult'),
    'ratio_proportion/_ratio_diff_19': ('gcse_ratio_ages', 'tier echo of _ratio_inter_03 (a map and a hike) in the difficult tier', 'difficult'),
    'graphs/_gra_diff_12': ('gcse_gra_perpendicular_bisector', 'tier echo of _gra_inter_14 (a line of best fit) in the difficult tier', 'difficult'),
    'graphs/_gra_inter_01': ('gcse_gra_gradient_from_graph', 'tier echo of _gra_found_03 (gradient from two points) in the intermediate tier', 'intermediate'),
    'graphs/_gra_inter_02': ('gcse_gra_line_through_two_points', 'tier echo of _gra_found_05 (equation from gradient and intercept) in the intermediate tier', 'intermediate'),
    'graphs/_gra_inter_03': ('gcse_gra_parallel_through_point', 'tier echo of _gra_found_06 (gradient of a parallel line) in the intermediate tier', 'intermediate'),
    'graphs/_gra_inter_04': ('gcse_gra_conversion_graph', 'tier echo of _gra_found_07 (speed from a distance-time graph) in the intermediate tier', 'intermediate'),
    'graphs/_gra_inter_07': ('gcse_gra_x_intercept', 'tier echo of _gra_found_08 (a midpoint) in the intermediate tier', 'intermediate'),
    'graphs/_gra_inter_09': ('gcse_gra_missing_coordinate', 'tier echo of _gra_found_09 (a reciprocal value) in the intermediate tier', 'intermediate'),
}

# Pairs of slots of one tier that look like siblings (same templates, same record families) but that a person
# judged to be different skills, so they stay apart.  Key: 'slug/tier/fn_a+fn_b' (names sorted), value: reason of
# 20+ characters.
VARIETY_EXEMPT = {
    'transformations/foundational/_trans_found_describe_reflection_axis+_trans_found_describe_rotation_90': (
        'Same wording ("describe the transformation") but a reflection and a rotation are different skills, reviewed 2026-10-27.'),
    'transformations/intermediate/_trans_inter_enlarge_neg_sf+_trans_inter_enlarge_not_origin': (
        'Same wording ("enlarge by scale factor k, centre (a, b)") but a negative scale factor (image inverted on the other '
        'side of the centre) is a separate Higher skill with its own misconception; kept apart in the Phase 0/1 review, 2026-10-27.'),
}

# Reviewed siblings whose merge waits for a later phase: they always count as ONE strict kind (whatever the sampled
# templates show) and are not reported as D2.  Key: 'slug/tier/fn_a+fn_b' (names sorted), value: reason.
# Empty: the one entry (algebra intermediate factorise_1/2/3, "solve x^2 + bx + c = 0 by factorising" at three root
# ranges) was merged in Phase 3 batch A once the tier had 8 other kinds; the three names are in RETIRED.
VARIETY_DEFERRED = {}     # empty since Phase 3 batch A merged algebra factorise_1/2/3 into algebra_practice_factorise

# Reviewed near-duplicates (whole-change review C6): slots of one tier that a teacher reads as one kind of question
# (same skill, only the wording or the numbers differ) although their templates and record families differ, so the
# sibling rule D2 cannot see them.  Each group counts as ONE strict kind in the variety report (so "9 strict kinds" is
# honest); the content is not changed.  Replacing a member with a genuinely new kind is the way to take a group out.
# Written as groups, expanded below into the 'slug/tier/a+b' keys that VARIETY_DEFERRED uses (a star around the
# first name in sorted order).
_NEAR_DUPLICATE_GROUPS = (
    ('quadratic_simultaneous_equations', 'foundational',
     ('gcse_qsim_f_y_from_x_values', '_qsim_f_find_y_given_x', 'gcse_qsim_f_circle_line_y'),
     'substitute a given x into y = x\u00b2 or the line to find y'),
    ('quadratic_simultaneous_equations', 'foundational',
     ('gcse_qsim_f_expand_substitution', '_qsim_f_rearrange_only', '_qsim_f_substitute_step'),
     'substitute and rearrange to the quadratic in the form x\u00b2 + px + q = 0'),
    ('algebraic_proof', 'difficult', ('gcse_ap_d_euler_prime_counterexample', '_ap_d_disprove_always_prime'),
     'give the smallest counterexample to a statement "... is prime for every n"'),
    ('completing_the_square', 'foundational', ('gcse_cts_f_negative_half', '_cts_f_half_coefficient'),
     'find p in (x + p)\u00b2 + q (a negative coefficient is the same step)'),
    ('completing_the_square', 'foundational',
     ('gcse_cts_f_find_q_given_p', '_cts_f_square_the_half', '_cts_f_missing_constant'),
     'find the constant q once p is known'),
    ('functions', 'foundational', ('gcse_fn_f_negative_input', '_fn_f_evaluate_linear'),
     'evaluate a linear function at a given input (a negative input is the same step)'),
    ('ratio_proportion', 'difficult',
     ('gcse_ratio_proportional_square', 'gcse_ratio_proportional_cube', 'gcse_ratio_proportional_root',
      'gcse_ratio_inverse_square'),
     'y = kx\u207f: find k from a pair, substitute (one skill with four exponents)'),
    ('decimals', 'foundational',
     ('gcse_dec_subtract_from_whole', 'gcse_dec_add_subtract', 'gcse_dec_proc_difference', 'gcse_dec_proc_three_add'),
     'add or subtract decimals'),
    ('decimals', 'foundational', ('gcse_dec_multiply_power10', 'gcse_dec_proc_divide_power10'),
     'multiply or divide a decimal by a power of 10 (same helper family and template)'),
    ('graphs', 'intermediate', ('gcse_gra_x_intercept', 'gcse_gra_missing_coordinate'),
     'put y = a number into a line and solve for x'),
)
VARIETY_NEAR_DUPLICATES = {}
for _slug, _tier, _names, _why in _NEAR_DUPLICATE_GROUPS:
    _names = sorted(_names)
    for _other in _names[1:]:
        VARIETY_NEAR_DUPLICATES[f'{_slug}/{_tier}/{_names[0]}+{_other}'] = f'reviewed near-duplicate: {_why}'
del _slug, _tier, _names, _why, _other

# The concept slot of each band that holds reviewed definitions (Phase 2, docs/GCSE_MATHS_VARIETY.md 5.3): the last
# slot of the band serves only the STATIC_EXEMPT items of the band (bank items flagged "concept": True), and every
# other slot of the band serves computed questions only, so those slots are re-solved in full.  Key 'slug/tier',
# value the slot name.  The smoke fails when this differs from the concept slots the generators build.
CONCEPT_SLOTS = {
    'bidmas/foundational': 'bidmas_mcq_foundational_7',
    'constructions_loci/difficult': 'constructions_loci_mcq_difficult_7',
    'constructions_loci/intermediate': 'constructions_loci_mcq_intermediate_7',
    'pythagoras/foundational': 'pythagoras_mcq_foundational_7',
    'simultaneous_equations/difficult': 'simultaneous_equations_mcq_difficult_7',
    'trigonometry/difficult': 'trigonometry_mcq_difficult_7',
    'trigonometry/foundational': 'trigonometry_mcq_foundational_7',
    'trigonometry/intermediate': 'trigonometry_mcq_intermediate_7',
}

# Practice slots that give the same question, worked solution and key for every seed (proofs, constructions, fixed
# formulas): the default verification run generates them on 2 seeds instead of 20 (--deep runs every seed).  Measured
# over 220 seeds each on 2026-10-27 (variety review).  The smoke fails if a listed slot gives two different questions
# or is no longer a practice slot; --deep lists any unlisted slot that was fixed on all its seeds.  Key: 'slug/tier/fn'.
FIXED_VARIANTS = frozenset({
    'changing_the_subject/difficult/_cts_d_V_lwh',
    'changing_the_subject/difficult/_cts_d_density',
    'changing_the_subject/intermediate/_cts_i_circumference',
    'changing_the_subject/intermediate/_cts_i_sqrt_area',
    'changing_the_subject/intermediate/_cts_i_triangle_area',
    'circle_theorems/foundational/_ct_f3_semicircle_direct',
    'constructions_loci/difficult/_cl_d1_locus_proof',
    'constructions_loci/foundational/_cl_f10_construct_angle_bisector_steps',
    'constructions_loci/foundational/_cl_f9_construct_perp_bisector_steps',
    'constructions_loci/intermediate/_cl_i11_circumcircle',
    'constructions_loci/intermediate/_cl_i12_incircle',
    'constructions_loci/intermediate/_cl_i6_perp_from_external_point',
    'constructions_loci/intermediate/_cl_i8_construct_60',
    'constructions_loci/intermediate/_cl_i9_perp_at_point_on_line',
    'equations_inequalities/difficult/_eq_diff_prove_identity',
    'equations_inequalities/difficult/_eq_diff_rearrange_complex',
    'equations_inequalities/difficult/_eq_diff_simult_non_integer',
    'equations_inequalities/difficult/_eq_diff_subject_appears_twice',
    'equations_inequalities/foundational/_eq_found_rearrange_one_step',
    'equations_inequalities/intermediate/_eq_inter_rearrange_sqrt',
    'equations_inequalities/intermediate/_eq_inter_rearrange_two_step',
    'functions/difficult/_fn_d_domain_valid',
    'geometry_angles/difficult/_geom_diff_cyclic_quad_proof',
    'geometry_angles/difficult/_geom_diff_prove_triangle_sum',
    'geometry_angles/foundational/_geom_found_equilateral',
    'pythagoras/difficult/_py_d6_roof_truss_multi',
    'pythagoras/difficult/_py_d7_coordinate_journey_multi',
    'pythagoras/intermediate/_py_i5_3d_two_step',
    'sequences/difficult/_seq_diff_arithmetic_proof',
    'sequences/difficult/_seq_diff_show_divisible',
    'similarity_congruence/difficult/_sc_d13_series_similar_triangles',
    'similarity_congruence/difficult/_sc_d15_lsf_from_vol_and_sa',
    'similarity_congruence/difficult/_sc_d1_midpoint_theorem_proof',
    'similarity_congruence/difficult/_sc_d2_frustum_volume',
    'similarity_congruence/difficult/_sc_d4_quadratic_from_similarity',
    'similarity_congruence/intermediate/_sc_i14_quadrilateral_angles',
    'similarity_congruence/intermediate/_sc_i7_algebraic_similar_sides',
    'similarity_congruence/intermediate/_sc_i9_proof_aa_parallel',
    'simultaneous_equations/difficult/_sim_d_matching_x_terms',
    'simultaneous_equations/foundational/_sim_f_classic_pair',
    'simultaneous_equations/intermediate/_sim_i_find_y_only',
    'surds/difficult/gcse_surds_identity',
    'transformations/difficult/_trans_diff_prove_isometry',
    'trigonometry/intermediate/_trig_inter_exact_expression',
    'vectors/difficult/_vectors_diff_geometry_proof',
    'vectors/difficult/_vectors_diff_trapezium_ratio',
    'vectors/difficult/_vectors_diff_triangle_midpoint',
    'vectors/difficult/_vectors_diff_vector_inequality',
    'vectors/foundational/_vectors_found_magnitude_zero',
})

# Ratchets that may only improve.  'tier_kinds': strict practice kinds per 'slug/tier'; 'mcq_kinds': MCQ kinds per
# band 'slug/tier' (bands of the direct topics are read from 4 fixed-seed draws per slot, so their floors sit a
# little under the measured value); 'queue_repeat_mean_max': the mean share of 7-question queues that repeat a kind.
# Topics whose three MCQ bands together have fewer than ten kinds of question (the quiz builder's kind, which ignores
# the sign between terms), so a ten-question lesson quiz cannot avoid asking one kind twice.  They are kept out of
# VARIETY_FLOORS['quiz_repeat_max'] and reported apart; an entry whose quizzes stop repeating fails the smoke (stale).
# Phase 4 content removes them (docs/GCSE_MATHS_VARIETY.md section 16).
QUIZ_THIN_TOPICS = {
    'functions': 'eight generators, seven kinds: f(g(4)) and g(f(4)) are one kind of question',
    'quadratic_simultaneous_equations': 'four generators in all three bands',
}

VARIETY_FLOORS = {
    'tier_kinds': {
        'algebra/difficult': 9,
        'algebra/foundational': 9,
        'algebra/intermediate': 9,
        'algebraic_fractions/difficult': 9,
        'algebraic_fractions/foundational': 9,
        'algebraic_fractions/intermediate': 9,
        'algebraic_proof/difficult': 8,
        'algebraic_proof/foundational': 9,
        'algebraic_proof/intermediate': 9,
        'bearings/difficult': 18,
        'bearings/foundational': 11,
        'bearings/intermediate': 18,
        'bidmas/difficult': 9,
        'bidmas/foundational': 9,
        'bidmas/intermediate': 9,
        'changing_the_subject/difficult': 10,
        'changing_the_subject/foundational': 9,
        'changing_the_subject/intermediate': 10,
        'circle_theorems/difficult': 15,
        'circle_theorems/foundational': 15,
        'circle_theorems/intermediate': 15,
        'completing_the_square/difficult': 9,
        'completing_the_square/foundational': 6,
        'completing_the_square/intermediate': 9,
        'compound_measures/difficult': 15,
        'compound_measures/foundational': 15,
        'compound_measures/intermediate': 15,
        'constructions_loci/difficult': 17,
        'constructions_loci/foundational': 15,
        'constructions_loci/intermediate': 15,
        'decimals/difficult': 9,
        'decimals/foundational': 5,
        'decimals/intermediate': 10,
        'equations_inequalities/difficult': 22,
        'equations_inequalities/foundational': 16,
        'equations_inequalities/intermediate': 19,
        'fdp/difficult': 9,
        'fdp/foundational': 9,
        'fdp/intermediate': 10,
        'functions/difficult': 9,
        'functions/foundational': 8,
        'functions/intermediate': 9,
        'geometry_angles/difficult': 14,
        'geometry_angles/foundational': 15,
        'geometry_angles/intermediate': 15,
        'graphical_simultaneous_equations/difficult': 9,
        'graphical_simultaneous_equations/foundational': 9,
        'graphical_simultaneous_equations/intermediate': 9,
        'graphs/difficult': 12,
        'graphs/foundational': 10,
        'graphs/intermediate': 13,
        'mensuration/difficult': 18,
        'mensuration/foundational': 15,
        'mensuration/intermediate': 18,
        'multiples_factors/difficult': 9,
        'multiples_factors/foundational': 9,
        'multiples_factors/intermediate': 9,
        'number/difficult': 20,
        'number/foundational': 16,
        'number/intermediate': 21,
        'probability/difficult': 17,
        'probability/foundational': 15,
        'probability/intermediate': 18,
        'pythagoras/difficult': 9,
        'pythagoras/foundational': 9,
        'pythagoras/intermediate': 9,
        'quadratic_simultaneous_equations/difficult': 9,
        'quadratic_simultaneous_equations/foundational': 5,
        'quadratic_simultaneous_equations/intermediate': 9,
        'ratio_proportion/difficult': 11,
        'ratio_proportion/foundational': 16,
        'ratio_proportion/intermediate': 18,
        'sequences/difficult': 15,
        'sequences/foundational': 15,
        'sequences/intermediate': 14,
        'similarity_congruence/difficult': 15,
        'similarity_congruence/foundational': 15,
        'similarity_congruence/intermediate': 15,
        'simultaneous_equations/difficult': 9,
        'simultaneous_equations/foundational': 9,
        'simultaneous_equations/intermediate': 9,
        'statistics/difficult': 9,
        'statistics/foundational': 12,
        'statistics/intermediate': 16,
        'surds/difficult': 9,
        'surds/foundational': 9,
        'surds/intermediate': 9,
        'transformations/difficult': 13,
        'transformations/foundational': 13,
        'transformations/intermediate': 14,
        'trigonometry/difficult': 10,
        'trigonometry/foundational': 10,
        'trigonometry/intermediate': 12,
        'vectors/difficult': 13,
        'vectors/foundational': 13,
        'vectors/intermediate': 13,
    },
    'mcq_kinds': {
        'algebra/difficult': 7,
        'algebra/foundational': 6,
        'algebra/intermediate': 9,
        'algebraic_fractions/difficult': 5,
        'algebraic_fractions/foundational': 7,
        'algebraic_fractions/intermediate': 7,
        'algebraic_proof/difficult': 10,
        'algebraic_proof/foundational': 4,
        'algebraic_proof/intermediate': 9,
        'bearings/difficult': 8,
        'bearings/foundational': 6,
        'bearings/intermediate': 8,
        'bidmas/difficult': 6,
        'bidmas/foundational': 9,
        'bidmas/intermediate': 6,
        'changing_the_subject/difficult': 5,
        'changing_the_subject/foundational': 5,
        'changing_the_subject/intermediate': 6,
        'circle_theorems/difficult': 5,
        'circle_theorems/foundational': 13,
        'circle_theorems/intermediate': 11,
        'completing_the_square/difficult': 13,
        'completing_the_square/foundational': 11,
        'completing_the_square/intermediate': 11,
        'compound_measures/difficult': 7,
        'compound_measures/foundational': 6,
        'compound_measures/intermediate': 7,
        'constructions_loci/difficult': 7,
        'constructions_loci/foundational': 5,
        'constructions_loci/intermediate': 7,
        'decimals/difficult': 10,
        'decimals/foundational': 8,
        'decimals/intermediate': 8,
        'equations_inequalities/difficult': 7,
        'equations_inequalities/foundational': 5,
        'equations_inequalities/intermediate': 6,
        'fdp/difficult': 12,
        'fdp/foundational': 8,
        'fdp/intermediate': 12,
        'functions/difficult': 5,
        'functions/foundational': 9,
        'functions/intermediate': 10,
        'geometry_angles/difficult': 7,
        'geometry_angles/foundational': 7,
        'geometry_angles/intermediate': 7,
        'graphical_simultaneous_equations/difficult': 9,
        'graphical_simultaneous_equations/foundational': 5,
        'graphical_simultaneous_equations/intermediate': 12,
        'graphs/difficult': 15,
        'graphs/foundational': 6,
        'graphs/intermediate': 15,
        'mensuration/difficult': 8,
        'mensuration/foundational': 7,
        'mensuration/intermediate': 8,
        'multiples_factors/difficult': 12,
        'multiples_factors/foundational': 9,
        'multiples_factors/intermediate': 12,
        'number/difficult': 6,
        'number/foundational': 6,
        'number/intermediate': 5,
        'probability/difficult': 15,
        'probability/foundational': 22,
        'probability/intermediate': 22,
        'pythagoras/difficult': 6,
        'pythagoras/foundational': 5,
        'pythagoras/intermediate': 7,
        'quadratic_simultaneous_equations/difficult': 7,
        'quadratic_simultaneous_equations/foundational': 4,
        'quadratic_simultaneous_equations/intermediate': 6,
        'ratio_proportion/difficult': 5,
        'ratio_proportion/foundational': 8,
        'ratio_proportion/intermediate': 6,
        'sequences/difficult': 9,
        'sequences/foundational': 8,
        'sequences/intermediate': 9,
        'similarity_congruence/difficult': 7,
        'similarity_congruence/foundational': 6,
        'similarity_congruence/intermediate': 7,
        'simultaneous_equations/difficult': 5,
        'simultaneous_equations/foundational': 5,
        'simultaneous_equations/intermediate': 6,
        'statistics/difficult': 16,
        'statistics/foundational': 17,
        'statistics/intermediate': 19,
        'surds/difficult': 11,
        'surds/foundational': 6,
        'surds/intermediate': 10,
        'transformations/difficult': 7,
        'transformations/foundational': 6,
        'transformations/intermediate': 7,
        'trigonometry/difficult': 9,
        'trigonometry/foundational': 5,
        'trigonometry/intermediate': 6,
        'vectors/difficult': 6,
        'vectors/foundational': 5,
        'vectors/intermediate': 6,
    },
    # 0.286 as built; 0.293 after the review counted the three algebra factorise range siblings as one kind
    # (VARIETY_DEFERRED): the pupils' queues did not change, the measure became honest.  Phase 3 batch A: 0.198
    # measured (28 tiers that repeat a kind in every queue fell to 19).
    # C6/C10 (2026-11-03): 0.053 measured once the reviewed near-duplicates count as one kind (0.0 before: with every slot its
    # own kind a 7-slot queue could not repeat one).  A tripwire on the whole report, not a per-tier target: the tiers that
    # repeat are the ones listed by the report as below 9 kinds.
    'queue_repeat_mean_max': 0.054,     # Phase 3 batch B: 0.198 before (0.0 measured after: the 19 tiers that repeated a kind in every queue all had fewer than 7 kinds)
    # Phase 2 (2026-10-27): the share of lesson quizzes with two questions of one kind (builder kind, GCSE maths
    # only).  53.2% before the kind check; 0.4% at 960 quizzes after (docs/GCSE_MATHS_VARIETY.md Phase 2).
    'quiz_repeat_max': 0.02,
}
