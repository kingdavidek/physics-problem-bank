"""Phase 5 hand-worked cases and checks for the GCSE maths hints smoke (``scripts/test_gcse_maths_hints_smoke.py``).

This is a helper module, not a smoke: its name does not match ``scripts/test_*_smoke.py``, so the number of smoke
files stays the same. The smoke calls ``bind(...)`` and then the ``check_*`` functions; every number in the tables
below was worked by hand (not by the rule code), so a wrong formula in ``misconception_cd`` fails a table row.

Tables
  GENERIC_EXAMPLES  generic rules added in Phase 5 (bearings, signs of quadratic roots)
  TX                one row per scalar topic rule: (rule id, family, recorded inputs, answer type, key, typed, question)
  PAIR_TX           vector and coordinate-pair rules: (rule id, family, inputs, answer type, key, typed, question)
  PART_TX           per-box rules: (rule id, family, inputs, keys of every box, box index, typed, question)
  EXPR_TX           algebraic-answer rules: (rule id, family, inputs, key, typed text(s), question)
  DERIVE_TX         the parsers that read a recorded family from the displayed question
"""
from __future__ import annotations

import collections
import dataclasses
import time
from fractions import Fraction

import gcse_hints_5b as B5

M = T = CD = AC = None
check_answer = issue = run_diag = None


def bind(modules, checker, report, diag):
    """Hand the smoke's own objects over (this file imports no app code at import time)."""
    global M, T, CD, AC, check_answer, issue, run_diag
    M, T, CD, AC = modules
    check_answer, issue, run_diag = checker, report, diag


Q = 'Work out the answer.'
R2DP = 'Give your answer to 2 d.p.'

# ─────────────────────────────────────────────────────────────────────────────
# generic rules
# ─────────────────────────────────────────────────────────────────────────────

GENERIC_EXAMPLES = (
    ('bearing, the back bearing without the half turn', 'Find the bearing of A from B.', 'bearing', '250', '070',
     'bearings', 'brg.reversed'),
    ('bearing, turned the other way round', 'Find the bearing of A from B.', 'bearing', '040', '320', 'bearings',
     'brg.anticlockwise'),
    ('bearing, 180 has no anticlockwise slip', 'Find the bearing of A from B.', 'bearing', '180', '180.5', 'bearings', None),
    ('bearing, a negative bearing is out of range and gets no sign slip', 'Find the bearing.', 'bearing', '250', '-250',
     'bearings', None),
    ('quadratic roots with their signs flipped', 'Solve x^2 - 7x + 10 = 0', 'quadratic_roots', '2,5', '-2,-5', 'algebra',
     'alg.root_signs'),
    ('... in either order', 'Solve x^2 - 7x + 10 = 0', 'quadratic_roots', '2,5', '-5,-2', 'algebra', 'alg.root_signs'),
    ('... only one root flipped is the one-root slip, not the sign slip', 'Solve x^2 - 7x + 10 = 0', 'quadratic_roots',
     '2,5', '-2,5', 'algebra', None),
)

# ─────────────────────────────────────────────────────────────────────────────
# scalar topic rules (probability, statistics, angles, bearings, algebra, sequences, graphs, vectors)
# ─────────────────────────────────────────────────────────────────────────────

DIE = 'A fair die is rolled. Find the probability.'
BAG = 'A bag holds some counters. One is taken at random. Find the probability.'
TWO_DRAW = 'Two counters are drawn from a bag. Find the probability.'
COINS = 'Some fair coins are flipped. Find the probability.'
VENN = 'Use the Venn diagram to find the probability.'
BEARING_Q = 'A ship sails 10 km on a bearing of 060°. Find how far it is from the start. ' + R2DP
STATS_Q = 'Find the statistic for this data.'
ANGLE_Q = 'Find the angle.'

TX = (
    # ---- probability ----
    ('prob.die_boundary', 'prob_die', {'event_word': 'greater than 4'}, 'fraction', '1/3', '1/2', DIE),
    ('prob.die_one_prime', 'prob_die', {'event_word': 'prime number'}, 'fraction', '1/2', '2/3', DIE),
    ('prob.bag_odds', 'prob_bag', {'n_first': 2, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                   'colour_word': 'red'}, 'fraction', '2/5', '2/3', BAG),
    ('prob.bag_other_colour', 'prob_bag', {'n_first': 2, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                           'colour_word': 'red'}, 'fraction', '2/5', '3/5', BAG),
    ('prob.complement_not_taken', 'prob_complement', {'p': 0.3}, 'number', '0.7', '0.3',
     'The probability that a bus is late is 0.3. Find P(a bus is not late).'),
    ('prob.expected_inverted', 'prob_expected', {'a': 1, 'b': 4, 'n': 40}, 'number', '10', '160', Q),
    ('prob.expected_not_scaled', 'prob_expected', {'a': 1, 'b': 4, 'n': 40}, 'number', '10', '0.25', Q),
    ('prob.relative_other', 'prob_relative', {'success': 1, 'trials': 5}, 'number', '0.2', '0.8', Q),
    ('prob.relative_odds', 'prob_relative', {'success': 1, 'trials': 5}, 'number', '0.2', '0.25', Q),
    ('prob.die_or_multiplied', 'prob_die_or', {'a': 1, 'b': 4}, 'fraction', '1/3', '1/36', DIE),
    ('prob.die_or_one_outcome', 'prob_die_or', {'a': 1, 'b': 4}, 'fraction', '1/3', '1/6', DIE),
    ('prob.coins_single', 'prob_coins', {'n': 2, 'style_word': 'same'}, 'fraction', '1/2', '1/4', COINS),
    ('prob.coins_exact_only', 'prob_coins', {'n': 4, 'style_word': 'at least', 'r': 2}, 'fraction', '11/16', '3/8', COINS),
    ('prob.coins_boundary', 'prob_coins', {'n': 4, 'style_word': 'at least', 'r': 2}, 'fraction', '11/16', '5/16', COINS),
    ('prob.tree_put_back_missed', 'prob_tree', {'n_first': 2, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                                'replace': True, 'ask': 'both'}, 'fraction', '4/25', '1/10', TWO_DRAW),
    ('prob.tree_removed_missed', 'prob_tree', {'n_first': 3, 'first_word': 'red', 'n_second': 2, 'second_word': 'blue',
                                               'replace': False, 'ask': 'both'}, 'fraction', '3/10', '9/25', TWO_DRAW),
    ('prob.tree_first_only', 'prob_tree', {'n_first': 2, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                           'replace': True, 'ask': 'both'}, 'fraction', '4/25', '2/5', TWO_DRAW),
    ('prob.tree_added', 'prob_tree', {'n_first': 2, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                      'replace': True, 'ask': 'both'}, 'fraction', '4/25', '4/5', TWO_DRAW),
    ('prob.tree_one_order', 'prob_tree', {'n_first': 6, 'first_word': 'red', 'n_second': 4, 'second_word': 'blue',
                                          'replace': False, 'ask': 'different'}, 'fraction', '8/15', '4/15', TWO_DRAW),
    ('prob.tree_complement', 'prob_tree', {'n_first': 6, 'first_word': 'red', 'n_second': 4, 'second_word': 'blue',
                                           'replace': False, 'ask': 'different'}, 'fraction', '8/15', '7/15', TWO_DRAW),
    ('prob.tree_single_case', 'prob_tree', {'n_first': 5, 'first_word': 'red', 'n_second': 3, 'second_word': 'blue',
                                            'replace': False, 'ask': 'at_least_first'}, 'fraction', '25/28', '5/14', TWO_DRAW),
    ('prob.at_least_fail_all', 'prob_at_least_one', {'p_fail': 0.2, 'attempts': 2}, 'number', '0.96', '0.04', Q),
    ('prob.at_least_one_attempt', 'prob_at_least_one', {'p_fail': 0.2, 'attempts': 2}, 'number', '0.96', '0.8', Q),
    ('prob.at_least_all_succeed', 'prob_at_least_one', {'p_fail': 0.2, 'attempts': 2}, 'number', '0.96', '0.64', Q),
    ('prob.conditional_joint', 'prob_conditional', {'pa_n': 1, 'pa_d': 2, 'pab_n': 1, 'pab_d': 8}, 'fraction', '1/4', '1/8', Q),
    ('prob.venn_overlap_missed', 'prob_venn2', {'a_only': 3, 'b_only': 2, 'both': 1, 'neither': 4, 'ask_word': 'P(A)'},
     'fraction', '2/5', '3/10', VENN),
    ('prob.venn_wrong_total', 'prob_venn2', {'a_only': 3, 'b_only': 2, 'both': 1, 'neither': 4, 'ask_word': 'P(A)'},
     'fraction', '2/5', '2/3', VENN),
    ('prob.venn_complement', 'prob_venn2', {'a_only': 3, 'b_only': 2, 'both': 1, 'neither': 4, 'ask_word': 'P(neither)'},
     'fraction', '2/5', '3/5', VENN),
    ('prob.venn_not_complemented', 'prob_venn2', {'a_only': 3, 'b_only': 2, 'both': 1, 'neither': 4, 'ask_word': 'P(not A)'},
     'fraction', '3/5', '2/5', VENN),
    ('prob.venn_neither_missed', 'prob_venn2', {'a_only': 3, 'b_only': 2, 'both': 1, 'neither': 4, 'ask_word': 'P(not A)'},
     'fraction', '3/5', '1/5', VENN),
    ('prob.union_counted_twice', 'prob_union', {'total': 20, 'a': 8, 'b': 6, 'both': 2}, 'fraction', '3/5', '7/10', Q),
    ('prob.union_multiplied', 'prob_union', {'total': 20, 'a': 8, 'b': 6, 'both': 2}, 'fraction', '3/5', '3/25', Q),
    ('prob.union_removed_twice', 'prob_union', {'total': 20, 'a': 8, 'b': 6, 'both': 2}, 'fraction', '3/5', '1/2', Q),
    ('prob.union_wrong_total', 'prob_union', {'total': 20, 'a': 8, 'b': 6, 'both': 2}, 'fraction', '3/5', '6/7', Q),
    ('prob.independent_added', 'prob_independent', {'a': 1, 'b': 2, 'c': 1, 'd': 3}, 'fraction', '1/6', '5/6', Q),
    # ---- statistics ----
    ('stats.median_unsorted', 'stats_list', {'stat_word': 'median', 'values': [9, 3, 12, 5, 2]}, 'number', '5', '12', STATS_Q),
    ('stats.median_is_mean', 'stats_list', {'stat_word': 'median', 'values': [9, 3, 12, 5, 2]}, 'number', '5', '6.2', STATS_Q),
    ('stats.range_largest', 'stats_list', {'stat_word': 'range', 'values': [9, 3, 12, 5, 2]}, 'number', '10', '12', STATS_Q),
    ('stats.range_first_last', 'stats_list', {'stat_word': 'range', 'values': [9, 3, 12, 5, 2]}, 'number', '10', '7', STATS_Q),
    ('stats.mean_total', 'stats_list', {'stat_word': 'mean', 'values': [9, 3, 12, 5, 2]}, 'number', '6.2', '31', STATS_Q),
    ('stats.mean_divisor', 'stats_list', {'stat_word': 'mean', 'values': [9, 3, 12, 5, 2]}, 'number', '6.2', '7.75', STATS_Q),
    ('stats.mean_is_median', 'stats_list', {'stat_word': 'mean', 'values': [9, 3, 12, 5, 2]}, 'number', '6.2', '5', STATS_Q),
    ('stats.mode_count', 'stats_list', {'stat_word': 'mode', 'values': [2, 5, 5, 5, 7, 1]}, 'number', '5', '3', STATS_Q),
    ('stats.midpoint_width', 'stats_midpoint', {'low': 12, 'high': 20}, 'number', '16', '8', Q),
    ('stats.midpoint_not_halved', 'stats_midpoint', {'low': 12, 'high': 20}, 'number', '16', '32', Q),
    ('stats.freq_unweighted', 'stats_freq_mean', {'values': [1, 2, 6], 'freqs': [4, 4, 2]}, 'number', '2.4', '3', Q),
    ('stats.freq_total', 'stats_freq_mean', {'values': [1, 2, 6], 'freqs': [4, 4, 2]}, 'number', '2.4', '24', Q),
    ('stats.freq_rows', 'stats_freq_mean', {'values': [1, 2, 6], 'freqs': [4, 4, 2]}, 'number', '2.4', '8', Q),
    ('stats.hist_ends', 'stats_hist_mean', {'intervals': [[0, 10], [10, 30]], 'freqs': [3, 1], 'n': 4}, 'number', '8.75',
     ('2.5', '15'), Q),
    ('stats.hist_total', 'stats_hist_mean', {'intervals': [[0, 10], [10, 30]], 'freqs': [3, 1], 'n': 4}, 'number', '8.75', '35', Q),
    ('stats.hist_rows', 'stats_hist_mean', {'intervals': [[0, 10], [10, 30]], 'freqs': [3, 1], 'n': 4}, 'number', '8.75',
     '17.5', Q),
    ('stats.pie_percentage', 'stats_pie', {'freq': 20, 'total': 80}, 'number', '90', '25', Q),
    ('stats.pie_one_item', 'stats_pie', {'freq': 20, 'total': 80}, 'number', '90', '4.5', Q),
    ('stats.pie_other_sector', 'stats_pie', {'freq': 20, 'total': 80}, 'number', '90', '270', Q),
    ('stats.iqr_range', 'stats_box', {'min_val': 10, 'q1': 20, 'q2': 25, 'q3': 35, 'max_val': 50}, 'number', '15', '40', Q),
    ('stats.iqr_upper_quartile', 'stats_box', {'min_val': 10, 'q1': 20, 'q2': 25, 'q3': 35, 'max_val': 50}, 'number', '15',
     '35', Q),
    ('stats.fd_multiplied', 'stats_fd', {'freq': 20, 'width': 5}, 'number', '4', '100', Q),
    ('stats.fd_inverted', 'stats_fd', {'freq': 20, 'width': 5}, 'number', '4', '0.25', Q),
    # ---- geometry angles ----
    ('ang.rule_sum_not_subtracted', 'ang_rule', {'rule_word': 'triangle', 'given': [50, 60]}, 'number', '70', '110', ANGLE_Q),
    ('ang.rule_wrong_total', 'ang_rule', {'rule_word': 'triangle', 'given': [50, 60]}, 'number', '70', '250', ANGLE_Q),
    ('ang.rule_angle_missed', 'ang_rule', {'rule_word': 'triangle', 'given': [50, 60]}, 'number', '70', '120', ANGLE_Q),
    ('ang.alternate_supplemented', 'ang_parallel', {'kind_word': 'alternate', 'angle': 70}, 'number', '70', '110', ANGLE_Q),
    ('ang.cointerior_equalled', 'ang_parallel', {'kind_word': 'co-interior', 'angle': 70}, 'number', '110', '70', ANGLE_Q),
    ('ang.exterior_interior', 'ang_exterior', {'a': 50, 'b': 60}, 'number', '110', '70', ANGLE_Q),
    ('ang.poly_n_times', 'poly_sum', {'n': 6}, 'number', '720', '1080', Q),
    ('ang.poly_exterior_total', 'poly_sum', {'n': 6}, 'number', '720', '360', Q),
    ('ang.poly_one_interior', 'poly_sum', {'n': 6}, 'number', '720', '120', Q),
    ('ang.poly_ext_interior', 'poly_exterior', {'shape_word': 'hexagon'}, 'number', '60', '120', ANGLE_Q),
    ('ang.poly_ext_half', 'poly_exterior', {'shape_word': 'hexagon'}, 'number', '60', '30', ANGLE_Q),
    ('ang.poly_n_interior_as_exterior', 'poly_n_from_interior', {'interior': 120}, 'number', '6', '3', Q),
    ('ang.poly_n_angle_found', 'poly_n_from_interior', {'interior': 120}, 'number', '6', '60', Q),
    ('ang.poly_ratio_angle_found', 'poly_interior_ratio', {'k': 4}, 'number', '10', '36', Q),
    ('ang.isos_one_base', 'ang_isos_apex', {'base': 50}, 'number', '80', '130', ANGLE_Q),
    ('ang.isos_bases_added', 'ang_isos_apex', {'base': 50}, 'number', '80', '100', ANGLE_Q),
    ('ang.equilateral_total', 'ang_equilateral', {'shape_word': 'equilateral'}, 'number', '60', '180', ANGLE_Q),
    # ---- bearings (one typed value) ----
    ('brg.back_same_direction', 'brg_back', {'b': 60}, 'number', '240', '60', Q),
    ('brg.back_anticlockwise', 'brg_back', {'b': 60}, 'number', '240', '300', Q),
    ('brg.back_north_line', 'brg_back', {'b': 60}, 'number', '240', '120', Q),
    ('brg.compass_angle_only', 'brg_compass', {'ns': 'S', 'x': 30, 'ew': 'W'}, 'bearing', '210', '30', Q),
    ('brg.compass_quadrant', 'brg_compass', {'ns': 'S', 'x': 30, 'ew': 'W'}, 'bearing', '210', '330', Q),
    ('brg.between_added', 'brg_angle_between', {'b1': 40, 'b2': 100}, 'number', '60', '140', Q),
    ('brg.between_reflex', 'brg_angle_between', {'b1': 40, 'b2': 100}, 'number', '60', '300', Q),
    ('brg.east_from_north', 'brg_angle_from_east', {'b': 50}, 'number', '40', '50', Q),
    ('brg.east_other_end', 'brg_angle_from_east', {'b': 50}, 'number', '40', '140', Q),
    ('brg.legs_swapped', 'brg_legs', {'legs': [[10, 60]], 'want': ['north']}, 'number', '5', '8.66', BEARING_Q),
    ('brg.legs_swapped', 'brg_en', {'east': 6, 'north': 8, 'want': ['north']}, 'number', '8', '6', Q),
    ('brg.legs_radians', 'brg_legs', {'legs': [[10, 60]], 'want': ['north']}, 'number', '5', '-9.52', BEARING_Q),
    ('brg.legs_path', 'brg_legs', {'legs': [[10, 0], [10, 60]], 'want': ['dist']}, 'number', '17.32', '20', BEARING_Q),
    ('brg.legs_components_added', 'brg_legs', {'legs': [[10, 0], [10, 60]], 'want': ['dist']}, 'number', '17.32', '23.66',
     BEARING_Q),
    ('brg.legs_components_added', 'brg_en', {'east': 6, 'north': 8, 'want': ['dist']}, 'number', '10', '14', Q),
    ('brg.legs_acute', 'brg_legs', {'legs': [[20, 180], [10, 90]], 'want': ['bearing']}, 'bearing', '153', '27', Q),
    ('brg.legs_acute', 'brg_en', {'east': 10, 'north': -20, 'want': ['bearing']}, 'bearing', '153', '27', Q),
    ('brg.legs_from_east', 'brg_legs', {'legs': [[20, 180], [10, 90]], 'want': ['bearing']}, 'bearing', '153', '63', Q),
    ('brg.legs_from_east', 'brg_en', {'east': 10, 'north': -20, 'want': ['bearing']}, 'bearing', '153', '63', Q),
    # ---- algebra and sequences (inputs read from the displayed question) ----
    ('alg.lin_sign_moved', 'lin_eq', {'a': [4, 2, 0, 18]}, 'linear', 'x = 4', 'x = 5', Q),
    ('alg.lin_wrong_inverse', 'lin_eq', {'a': [7, 0, 0, 28]}, 'linear', 'x = 4', 'x = 196', Q),
    ('alg.lin_one_term_divided', 'lin_eq', {'a': [4, 2, 0, 18]}, 'linear', 'x = 4', 'x = 2.5', Q),
    ('alg.lin_bracket_partial', 'lin_eq', {'a': [2, 8, 4, 2], 'br': [[0, 2, 1, 4], [1, 4, 1, 4]]}, 'linear', 'x = 3',
     'x = 9', Q),
    ('seq.step_as_term', 'seq_terms', {'t': [11, 17, 23, 35], 'at': 3}, 'number', '29', '6', Q),
    ('seq.geometric_added', 'seq_terms', {'t': [2, 4, 8, 16], 'at': 4}, 'number', '32', '24', Q),
    ('seq.quadratic_gaps', 'seq_terms', {'t': [1, 4, 9, 16], 'at': 4}, 'number', '25', '23', Q),
    ('seq.nth_constant_forgotten', 'seq_nth', {'a': 4, 'b': -3, 'n': 13}, 'number', '49', '52', Q),
    ('seq.nth_constant_sign', 'seq_nth', {'a': 4, 'b': -3, 'n': 13}, 'number', '49', '55', Q),
    ('seq.nth_position_off', 'seq_nth', {'a': 4, 'b': -3, 'n': 13}, 'number', '49', '45', Q),
    ('seq.which_inverse', 'seq_which', {'a': 5, 'b': -5, 'v': 60}, 'number', '13', '11', Q),
    ('seq.which_divide_first', 'seq_which', {'a': 5, 'b': -5, 'v': 60}, 'number', '13', '17', Q),
    # ---- graphs and vectors (one number) ----
    ('gr.subst_negative_power', 'gr_subst', {'e': 'x² + 2x + 3', 'x': -3}, 'number', '6', '-12', Q),
    ('gr.subst_power_multiplied', 'gr_subst', {'e': 'x² + 2x + 3', 'x': -3}, 'number', '6', '-9', Q),
    ('vec.magnitude_not_rooted', 'vec_magnitude', {'x': 5, 'y': 12}, 'number', '13', '169', Q),
    ('vec.magnitude_added', 'vec_magnitude', {'x': 5, 'y': 12}, 'number', '13', '17', Q),
    # completing the square: x^2 + 14x + c needs (14 / 2)^2 = 49; (x + p)^2 for x^2 + 12x has p = 6
    ('cts.half_not_squared', 'cts_square', {'b': 14}, 'number', '49', '7', Q),
    ('cts.whole_squared', 'cts_square', {'b': 14}, 'number', '49', '196', Q),
    ('cts.not_halved', 'cts_half', {'b': 12}, 'number', '6', '12', Q),
)

# ─────────────────────────────────────────────────────────────────────────────
# pairs: (rule id, family, inputs, answer type, key, typed, question)
# ─────────────────────────────────────────────────────────────────────────────

PAIR_TX = (
    ('vec.sub_reversed', 'vec_sub', {'a0': 5, 'a1': 2, 'b0': 1, 'b1': 4}, 'vector', '4|-2', '-4|2', Q),
    ('vec.sub_added', 'vec_sub', {'a0': 5, 'a1': 2, 'b0': 1, 'b1': 4}, 'vector', '4|-2', '6|6', Q),
    ('vec.displacement_reversed', 'vec_displacement', {'a0': 1, 'a1': 2, 'b0': 4, 'b1': 6}, 'vector', '3|4', '-3|-4', Q),
    ('vec.add_subtracted', 'vec_add', {'a0': 2, 'a1': 3, 'b0': 4, 'b1': -1}, 'vector', '6|2', '-2|4', Q),
    ('vec.add_subtracted', 'vec_path_add', {'a0': 1, 'a1': 5, 'b0': -3, 'b1': 5}, 'vector', '-2|10', '4|0', Q),
    ('vec.scale_added', 'vec_scale', {'k': 3, 'v0': 2, 'v1': -1}, 'vector', '6|-3', '5|2', Q),
    ('vec.translate_opposite', 'vec_translate', {'p0': 1, 'p1': 2, 'v0': 3, 'v1': -1}, 'number_pair', '4|1', '-2|3', Q),
    ('vec.translate_swapped', 'vec_translate', {'p0': 1, 'p1': 2, 'v0': 3, 'v1': -1}, 'number_pair', '4|1', '0|5', Q),
    ('vec.midpoint_sum', 'vec_midpoint', {'a0': 2, 'a1': 6, 'b0': 4, 'b1': -2}, 'number_pair', '3|2', '6|4', Q),
    ('vec.midpoint_difference', 'vec_midpoint', {'a0': 2, 'a1': 6, 'b0': 4, 'b1': -2}, 'number_pair', '3|2', '-1|4', Q),
    ('vec.section_reversed', 'vec_section', {'ax': 0, 'ay': 0, 'bx': 10, 'by': 5, 'm': 1, 'n': 4}, 'number_pair', '2|1', '8|4', Q),
    ('vec.equation_sign', 'vec_equation', {'c0': 10, 'c1': 4, 'b0': 2, 'b1': -2}, 'vector', '4|3', '6|1', Q),
    ('vec.equation_not_divided', 'vec_equation', {'c0': 10, 'c1': 4, 'b0': 2, 'b1': -2}, 'vector', '4|3', '8|6', Q),
    ('gr.midpoint_sum', 'gr_midpoint', {'x1': 2, 'y1': 6, 'x2': 4, 'y2': -2}, 'number_pair', '3|2', '6|4', Q),
    ('gr.midpoint_difference', 'gr_midpoint', {'x1': 2, 'y1': 6, 'x2': 4, 'y2': -2}, 'number_pair', '3|2', '-1|4', Q),
    ('gr.roots_signs', 'gr_roots', {'s1': '-', 'c1': 5, 's2': '-', 'c2': 2}, 'number_pair', '2|5', ('-2|-5', '-5|-2'), Q),
    ('gr.roots_signs', 'gr_roots', {'s1': '+', 'c1': 4, 's2': '+', 'c2': 1}, 'number_pair', '-4|-1', '4|1', Q),
    # 3x + 2y = 13 and x + 2y = 7 have x = 3 and y = 2
    ('sim.back_sign', 'linear_system_2', {'a1': 3, 'b1': 2, 'c1': 13, 'a2': 1, 'b2': 2, 'c2': 7}, 'number_pair', '3|2', '3|11',
     'Solve the simultaneous equations.'),
    ('sim.back_not_divided', 'linear_system_2', {'a1': 3, 'b1': 2, 'c1': 13, 'a2': 1, 'b2': 2, 'c2': 7}, 'number_pair', '3|2',
     ('3|4', '9|2'), 'Solve the simultaneous equations.'),
)

# ─────────────────────────────────────────────────────────────────────────────
# parts: (rule id, family, inputs, keys of every box, box index, typed, question)
# ─────────────────────────────────────────────────────────────────────────────

LEGS_Q = 'A ship sails 10 km on a bearing of 060°. Find how far east and north it is. Give your answers to 2 d.p.'
TURN_Q = 'Find the image of the point. Write down its coordinates.'
SHIPS_Q = ('Two ships leave port O. Ship A sails 10 km on bearing 010° and ship B sails 10 km on bearing 070°. Find the '
           'angle AOB, the distance AB to 2 d.p., and the bearings of A from B and of B from A.')
L1 = {'legs': [[10, 60]], 'want': ['east', 'north']}
L2 = {'legs': [[10, 0], [10, 60]], 'want': ['dist', 'bearing']}
L3 = {'legs': [[20, 180], [10, 90]], 'want': ['dist', 'bearing']}
L4 = {'east': 10, 'north': -20, 'want': ['dist', 'bearing']}
SHIPS = {'b1': 10, 'd1': 10, 'b2': 70, 'd2': 10, 'want': ['angle', 'ab', 'bearing_a_from_b', 'bearing_b_from_a']}
REFLECT = {'kind': 'reflect', 'pts': [[4, 3]], 'line_word': 'y = 1'}
ROTATE = {'kind': 'rotate', 'pts': [[2, 1]], 'turn_word': '90° clockwise'}
ROTATE_C = {'kind': 'rotate', 'pts': [[2, 1]], 'turn_word': '90° clockwise', 'cx': 1, 'cy': 1}
ROTATE_C2 = {'kind': 'rotate', 'pts': [[4, 3]], 'turn_word': '90° clockwise', 'cx': 1, 'cy': 2}   # image (2, -1)
ENLARGE_NEG_C = {'kind': 'enlarge', 'pts': [[3, 2]], 'k': -2, 'cx': 1, 'cy': 1}                # image (-3, -1)
ENLARGE = {'kind': 'enlarge', 'pts': [[2, 3]], 'k': 2}
ENLARGE_NEG = {'kind': 'enlarge', 'pts': [[2, 3]], 'k': -2}
ENLARGE_C = {'kind': 'enlarge', 'pts': [[2, 3]], 'k': 2, 'cx': 1, 'cy': 1}
TRANSLATE = {'kind': 'translate', 'pts': [[1, 2]], 'dx': 3, 'dy': -1}

QSIM = {'m': -5, 'c': -6}
QSIM_Q = 'Solve the simultaneous equations. Give both pairs of values.'
QSIM2 = {'m': -1, 'c': 12}                     # y = x^2 and y = -x + 12 meet at (3, 9) and (-4, 16)

PART_TX = (
    ('brg.part_swapped', 'brg_legs', L1, ['8.66', '5'], 1, '8.66', LEGS_Q),
    ('brg.part_swapped', 'brg_en', {'east': 6, 'north': 8, 'want': ['east', 'north']}, ['6', '8'], 0, '8', LEGS_Q),
    ('brg.part_radians', 'brg_legs', L1, ['8.66', '5'], 0, '-3.05', LEGS_Q),
    ('brg.part_path', 'brg_legs', L2, ['17.32', '30'], 0, '20', LEGS_Q),
    ('brg.part_components_added', 'brg_legs', L2, ['17.32', '30'], 0, '23.66', LEGS_Q),
    ('brg.part_components_added', 'brg_en', L4, ['22.36', '153'], 0, '30', LEGS_Q),
    ('brg.part_reversed', 'brg_legs', L2, ['17.32', '30'], 1, '210', LEGS_Q),
    ('brg.part_anticlockwise', 'brg_legs', L2, ['17.32', '30'], 1, '330', LEGS_Q),
    ('brg.part_acute', 'brg_legs', L3, ['22.36', '153'], 1, '27', LEGS_Q),
    ('brg.part_acute', 'brg_en', L4, ['22.36', '153'], 1, '27', LEGS_Q),
    ('brg.part_from_east', 'brg_legs', L3, ['22.36', '153'], 1, '63', LEGS_Q),
    ('brg.part_from_east', 'brg_en', L4, ['22.36', '153'], 1, '63', LEGS_Q),
    ('brg.ships_added', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 0, '80', SHIPS_Q),
    ('brg.ships_reflex', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 0, '300', SHIPS_Q),
    ('brg.ships_sides_added', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 1, '20', SHIPS_Q),
    ('brg.ships_pythagoras', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 1, '14.14', SHIPS_Q),
    ('brg.ships_reversed', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 2, '130', SHIPS_Q),
    ('brg.ships_anticlockwise', 'brg_two_ships', SHIPS, ['60', '10', '310', '130'], 2, '50', SHIPS_Q),
    ('trans.coords_swapped', 'trans_apply', REFLECT, ['4', '-1'], 0, '-1', TURN_Q),
    ('trans.wrong_axis', 'trans_apply', REFLECT, ['4', '-1'], 0, '-2', TURN_Q),
    ('trans.line_ignored', 'trans_apply', REFLECT, ['4', '-1'], 1, '-3', TURN_Q),
    # the other way round about (1, 2) gives (0, 5); about the origin the other turn only flips signs (see other_cases)
    ('trans.rotate_opposite', 'trans_apply', ROTATE_C2, ['2', '-1'], 1, '5', TURN_Q),
    ('trans.centre_ignored', 'trans_apply', ROTATE_C, ['1', '0'], 1, '-2', TURN_Q),
    ('trans.centre_ignored', 'trans_apply', ENLARGE_C, ['3', '5'], 1, '6', TURN_Q),
    ('trans.enlarge_added', 'trans_apply', ENLARGE, ['4', '6'], 1, '5', TURN_Q),
    ('trans.enlarge_inverted', 'trans_apply', ENLARGE, ['4', '6'], 1, '1.5', TURN_Q),
    ('trans.negative_ignored', 'trans_apply', ENLARGE_NEG_C, ['-3', '-1'], 0, '5', TURN_Q),
    ('trans.translate_opposite', 'trans_apply', TRANSLATE, ['4', '1'], 0, '-2', TURN_Q),
    ('trans.vector_swapped', 'trans_apply', TRANSLATE, ['4', '1'], 1, '5', TURN_Q),
    # y = x^2 and y = -5x - 6 meet where x^2 + 5x + 6 = 0, so at (-3, 9) and (-2, 4)
    ('qsim.root_signs', 'qsim_solve', QSIM, ['-3', '9', '-2', '4'], 0, ('3', '2'), QSIM_Q),
    ('qsim.root_signs', 'qsim_solve', QSIM, ['-3', '9', '-2', '4'], 2, '3', QSIM_Q),
    ('qsim.pairs_swapped', 'qsim_solve', QSIM, ['-3', '9', '-2', '4'], 1, '-3', QSIM_Q),
    # whole-change review 2026-11-03 (F7): the y box of x = 3 (2x = 6); for x = -2 above, -4 is only the sign of 4
    # (other_cases), and for x = -3, -6 is printed in the question
    ('qsim.y_doubled', 'qsim_solve', QSIM2, ['-4', '16', '3', '9'], 3, '6', QSIM_Q),
)
PART_TX = PART_TX + B5.PART_TX_5B        # Phase 5b rows (scripts/gcse_hints_5b.py)
PAIR_TX = PAIR_TX + B5.PAIR_TX_5B
TX = TX + B5.SCALAR_TX_5B

# ─────────────────────────────────────────────────────────────────────────────
# expressions: (rule id, family, inputs, key, typed text(s), question)
# ─────────────────────────────────────────────────────────────────────────────

NTH_Q = 'Find the nth term of the arithmetic sequence: 3, 7, 11, 15, 19'
EXPR_TX = (
    ('seq.find_first_term', 'seq_nth_find', {'t': [3, 7, 11, 15, 19]}, '4n-1', '4n+3', NTH_Q),
    ('seq.find_difference_constant', 'seq_nth_find', {'t': [3, 7, 11, 15, 19]}, '4n-1', '4n+4', NTH_Q),
    ('seq.find_constant_sign', 'seq_nth_find', {'t': [3, 7, 11, 15, 19]}, '4n-1', '4n+1', NTH_Q),
    ('seq.find_add_not_multiply', 'seq_nth_find', {'t': [3, 7, 11, 15, 19]}, '4n-1', 'n+4', NTH_Q),
    ('alg.expand_cross_missed', 'expand2', {'p': 1, 'q': 2, 'r': 1, 's': 3}, 'x^2 + 5x + 6', ('x^2+6', 'x^2+3x+6'),
     'Expand and simplify (x + 2)(x + 3).'),
    ('alg.rearr_sign_moved', 'rearrange', {'v': 'y', 'f': 'a=3*y+1'}, 'y=(A-1)/3', 'y=(a+1)/3',
     'Make y the subject of A = 3y + 1.'),
    ('alg.rearr_one_term_divided', 'rearrange', {'v': 'y', 'f': 'a=3*y+1'}, 'y=(A-1)/3', ('y=a-1/3', 'y=a/3-1'),
     'Make y the subject of A = 3y + 1.'),
    ('alg.rearr_wrong_inverse', 'rearrange', {'v': 'y', 'f': 'a=3*y'}, 'y=A/3', 'y=3a', 'Make y the subject of A = 3y.'),
    ('alg.rearr_root_missed', 'rearrange', {'v': 'r', 'f': 'a=pi*r**2'}, 'r=√(A/π)', 'r=a/pi',
     'Make r the subject of A = pi r squared.'),
    ('alg.rearr_sign_moved', 'rearrange', {'v': 'x', 'f': 'y=5*x**2+3'}, 'x=√((y-3)/(5))', 'x=sqrt((y+3)/(5))',
     'Make x the subject of y = 5x squared + 3.'),
)

# ─────────────────────────────────────────────────────────────────────────────
# the parsers that read a family from the displayed question: (task, question, expected (family, inputs))
# ─────────────────────────────────────────────────────────────────────────────

DERIVE_TX = (
    ('solve_linear', r'Solve: \( 6x + 1 = 74 \)', ('lin_eq', {'a': [6, 1, 0, 74]})),
    ('solve_linear', r'Solve \(7x = 28\).', ('lin_eq', {'a': [7, 0, 0, 28]})),
    ('solve_linear', r'Solve: \( 2(x + 4) = 4(x + 4) - 14 \)', ('lin_eq', {'a': [2, 8, 4, 2], 'br': [[0, 2, 1, 4], [1, 4, 1, 4]]})),
    ('solve_linear', r'Solve \(3x + 2 = x + 12\).', ('lin_eq', {'a': [3, 2, 1, 12]})),
    ('seq_next', 'Find the missing term: 11, 17, 23, ___, 35', ('seq_terms', {'t': [11, 17, 23, 35], 'at': 3})),
    ('seq_next', 'Write down the next term in the sequence: 2, 4, 8, 16, ___ Use the pattern.',
     ('seq_terms', {'t': [2, 4, 8, 16], 'at': 4})),
    ('seq_nth_value', r'The nth term of a sequence is \(4n + 2\). Find the 18th term.', ('seq_nth', {'a': 4, 'b': 2, 'n': 18})),
    ('seq_nth_value', r'The nth term of a sequence is \(8n\). Find the 70th term.', ('seq_nth', {'a': 8, 'b': 0, 'n': 70})),
    ('seq_nth_value', r'The nth term of a sequence is \(3n - 1\). Find the 5th term.', ('seq_nth', {'a': 3, 'b': -1, 'n': 5})),
    ('seq_which_term', r'The nth term of a sequence is \(3n - 1\) Which term has value 59?',
     ('seq_which', {'a': 3, 'b': -1, 'v': 59})),
    ('seq_find_nth', 'Find the nth term of the arithmetic sequence: 3, 7, 11, 15, 19', ('seq_nth_find', {'t': [3, 7, 11, 15, 19]})),
    ('solve_system', r'Solve the simultaneous equations: \(2x + y = 8\) (1) \(x + 2y = 7\) (2)',
     ('linear_system_2', {'a1': 2, 'b1': 1, 'c1': 8, 'a2': 1, 'b2': 2, 'c2': 7})),
    ('solve_system', r'Solve the simultaneous equations: \(y = 3x\) (1) \(3x + 2y = 9\) (2)',
     ('linear_system_2', {'a1': -3, 'b1': 1, 'c1': 0, 'a2': 3, 'b2': 2, 'c2': 9})),
    ('qsim_solve', r'Solve: \(y = x^2\) \(y = -5x - 6\)', ('qsim_solve', {'m': -5, 'c': -6})),
    ('cts_missing_constant', r'You are completing \(x^2 + 14x + c\). What must c be so the expression becomes \((x + 7)^2\)?',
     ('cts_square', {'b': 14})),
    ('cts_square_the_half', r'The x² + 4x + … form uses half the x-coefficient (2). What number do you subtract when building '
     r'\((x + 2)^2\)?', ('cts_square', {'b': 4})),
    ('cts_half', r'Complete the square for \(x^2 + 12x - 11\). What is the value of p in \((x + p)^2 + \ldots\)?',
     ('cts_half', {'b': 12})),
    ('cts_half', r'Complete the square for \(x^2 - 12x + 5\). What is the value of p in \((x + p)^2 + \ldots\)?',
     ('cts_half', {'b': -12})),
    ('gr_subst', 'For y = x² + 2x + 3, find y when x = -3.', ('gr_subst', {'e': 'x² + 2x + 3', 'x': -3})),
    ('gr_midpoint', 'Find the midpoint of (2, 6) and (4, -2).', ('gr_midpoint', {'x1': 2, 'y1': 6, 'x2': 4, 'y2': -2})),
    ('gr_roots', 'Find the roots of y = (x − 5)(x − 2).', ('gr_roots', {'s1': '-', 'c1': 5, 's2': '-', 'c2': 2})),
    ('gr_roots', 'Find the roots of y = (x + 4)x.', ('gr_roots', {'s1': '+', 'c1': 4, 's2': '+', 'c2': 0})),
    ('expand', r'Expand and simplify \((x + 2)(x + 3)\).', ('expand2', {'p': 1, 'q': 2, 'r': 1, 's': 3})),
    ('expand', r'Expand and simplify \((2x + 1)(x - 4)\).', ('expand2', {'p': 2, 'q': 1, 'r': 1, 's': -4})),
    ('rearrange', r'Make \(y\) the subject of the formula: \( A = 3y + 1 \)', ('rearrange', {'v': 'y', 'f': 'a=3*y+1'})),
    ('rearrange', r'Make \(r\) the subject of \(A = \pi r^2\).', ('rearrange', {'v': 'r', 'f': 'a=pi*r**2'})),
)
# text a parser must not read (no record, so no rule): the wrong shape, two unknowns, a quadratic, or no equation
DERIVE_NONE = (
    ('solve_linear', r'Solve \(x^2 = 9\).'), ('solve_linear', r'Solve \(x + y = 9\).'), ('solve_linear', 'Solve the equation.'),
    ('solve_linear', r'Solve \(3 = 3\).'),
    ('seq_next', 'Find the next term: 2, 4, 6, 8'), ('seq_next', 'Find the missing term: 2, ___, ___, 8'),
    ('seq_nth_value', r'The nth term is \(n^2\). Find the 5th term.'),
    ('seq_find_nth', 'Find the nth term of the sequence: 1, 4, 9, 16, ...'),
    ('seq_find_nth', 'Find the nth term of the geometric sequence: 2, 4, 8, 16, ...'),
    ('solve_system', r'Solve: \(x + y = 5\) (1) \(2x + 2y = 10\) (2)'), ('solve_system', r'Solve: \(x^2 + y = 5\) (1) \(x + y = 3\) (2)'),
    ('solve_system', r'Solve \(x + y = 5\).'),
    ('qsim_solve', r'Solve: \(y = 3x\) \(y = -5x - 6\)'), ('qsim_solve', r'Solve: \(y = x^2\) \(y = x^2 + 1\)'),
    ('cts_half', 'Complete the square.'), ('cts_missing_constant', r'Find \(x\) when \(x + 7 = 9\).'),
    ('gr_midpoint', 'Find the midpoint of A and B.'), ('gr_roots', 'Find the roots of y = x^2 - 4.'),
    ('expand', r'Expand \(3(x + 2)\).'),
    ('rearrange', r'Make \(t\) the subject of \(v = \dfrac{s}{t}\).'),
    ('rearrange', 'Make y the subject.'),
)

EXPR_TX = EXPR_TX + B5.EXPR_TX_5B
DERIVE_TX = DERIVE_TX + B5.DERIVE_TX_5B
DERIVE_NONE = DERIVE_NONE + B5.DERIVE_NONE_5B


# ─────────────────────────────────────────────────────────────────────────────
# running the tables
# ─────────────────────────────────────────────────────────────────────────────

def _accepts(at, key):
    return lambda t: bool(check_answer(at, key, t).get('correct'))


def _typed_tuple(typed):
    return typed if isinstance(typed, tuple) else (typed,)


def run_pair(case):
    rid, fam, inputs, at, key, typed, question = case
    prob = {'question': question, 'answer_type': at, 'correct_answer_raw': key, 'answer_record': {'f': fam, 'i': inputs}}
    rule = CD_RULES_BY_ID[rid]
    failed = []
    for t in _typed_tuple(typed):
        if check_answer(at, key, t).get('correct'):
            failed.append(f'{rid} ({fam}): the example {t!r} is accepted by the checker (key {key!r})')
            continue
        got = M._diagnose(prob, t, check_answer(at, key, t), at, key, _accepts(at, key), 'gcse', 'maths', '', None)
        if got is None or got.message != M.MESSAGES[rule.message]:
            failed.append(f'{rid} ({fam}): key {key!r}, typed {t!r}: expected {rule.message!r}, got '
                          f'{got.rule_id if got else None!r}')
    return failed


def part_problem(fam, inputs, keys, question):
    sep = '\x1e' if any('|' in k for k in keys) else '|'          # a pick box (pick|1|c1) is why a key can hold a bar
    return {'question': question, 'answer_type': 'number_fields', 'correct_answer_raw': sep.join(keys),
            'answer_record': {'f': fam, 'i': inputs}}


def run_part(case):
    rid, fam, inputs, keys, part, typed, question = case
    prob = part_problem(fam, inputs, keys, question)
    rule = CD_RULES_BY_ID[rid]
    key = keys[part]
    failed = []
    for t in _typed_tuple(typed):
        if check_answer('number', key, t).get('correct'):
            failed.append(f'{rid} ({fam}): the example {t!r} is accepted by the checker (key {key!r})')
            continue
        got = M._diagnose(prob, t, check_answer('number', key, t), 'number', key, _accepts('number', key), 'gcse', 'maths',
                          '', None, part=part)
        if got is None or got.message != M.MESSAGES[rule.message]:
            failed.append(f'{rid} ({fam}) box {part}: key {key!r}, typed {t!r}: expected {rule.message!r}, got '
                          f'{got.rule_id if got else None!r}')
    return failed


def run_expr(case):
    rid, fam, inputs, key, typed, question = case
    prob = {'question': question, 'answer_type': 'algebraic', 'correct_answer_raw': key,
            'answer_record': {'f': fam, 'i': inputs}}
    rule = CD_RULES_BY_ID[rid]
    failed = []
    for t in _typed_tuple(typed):
        if check_answer('algebraic', key, t).get('correct'):
            failed.append(f'{rid} ({fam}): the example {t!r} is accepted by the checker (key {key!r})')
            continue
        got = M._diagnose(prob, t, check_answer('algebraic', key, t), 'algebraic', key, _accepts('algebraic', key), 'gcse',
                          'maths', '', None)
        if got is None or got.message != M.MESSAGES[rule.message]:
            failed.append(f'{rid} ({fam}): key {key!r}, typed {t!r}: expected {rule.message!r}, got '
                          f'{got.rule_id if got else None!r}')
    return failed


CD_RULES_BY_ID: dict = {}


def run_tables(only_rule=None, only_family=None):
    """Run the pair, part and expression tables. Returns the failing case descriptions."""
    CD_RULES_BY_ID.clear()
    CD_RULES_BY_ID.update({r.id: r for r in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES})
    failed = []
    for rows, fn, fam_at in ((PAIR_TX, run_pair, 1), (PART_TX, run_part, 1), (EXPR_TX, run_expr, 1)):
        for case in rows:
            if (only_rule and case[0] != only_rule) or (only_family and case[fam_at] != only_family):
                continue
            rule = CD_RULES_BY_ID.get(case[0])
            if rule is None:
                failed.append(f'{case[0]}: no such rule')
            elif case[1] not in rule.families:
                failed.append(f'{case[0]}: example family {case[1]} is not one of the rule families {rule.families}')
            else:
                failed.extend(fn(case))
    return failed


def run_derive():
    failed = []
    for task, question, want in DERIVE_TX:
        fn = CD.DERIVE.get(task)
        if fn is None:
            failed.append(f'derive {task}: no such parser')
            continue
        got = fn(M.plain_text(question))
        if got is None or (got[0], _norm(got[1])) != (want[0], _norm(want[1])):
            failed.append(f'derive {task} on {question!r}: expected {want}, got {got}')
    for task, question in DERIVE_NONE:
        got = CD.DERIVE[task](M.plain_text(question))
        if got is not None:
            failed.append(f'derive {task} read {question!r} as {got} (it should read nothing)')
    return failed


def _norm(inputs):
    return {k: [list(x) if isinstance(x, (list, tuple)) else x for x in v] if isinstance(v, (list, tuple)) else v
            for k, v in inputs.items()}


Q5B = 'Find the missing values.'
V_5C = 'Find the value.'


def other_cases():
    """Behaviours the tables cannot express: (name, ok)."""
    out = []

    def case(name, ok):
        out.append((name, ok))

    CD_RULES_BY_ID.update({r.id: r for r in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES})
    # ---- boxes ----
    legs = part_problem('brg_legs', L2, ['17.32', '30'], LEGS_Q)

    def box(prob, part, key, typed, topic=''):
        res = check_answer('number', key, typed)
        return M._diagnose(prob, typed, res, 'number', key, _accepts('number', key), 'gcse', 'maths', topic, None, part=part)

    case('a box: 20 for the first box is the path length', (box(legs, 0, '17.32', '20') or M.Diagnosis('', '', '')).rule_id
         == 'brg.part_path')
    case('... the same 20 typed in the other box is not (that box is a bearing)', box(legs, 1, '30', '20') is None)
    case('... the key of a box is never diagnosed', box(legs, 0, '17.32', '17.32') is None and box(legs, 1, '30', '30') is None)
    case('... a part index that is out of range reads no record',
         all(M.read_part_record(legs, p, '17.32') is None for p in (-1, 2, 99, True, '0', None)))
    case('... a box whose key is not the stored one reads no record', M.read_part_record(legs, 0, '30') is None)
    case('... a record on a single-box answer is not read as boxes',
         M.read_part_record(dict(legs, answer_type='number'), 0, '17.32') is None)
    case('... a box rule needs every box to reproduce its key (a changed key gives nothing)',
         box(part_problem('brg_legs', L2, ['17.32', '31'], LEGS_Q), 0, '17.32', '20') is None)
    big = dict(legs, answer_record={'f': 'brg_legs', 'i': dict(L2, pad='x' * 300)})
    case('... a record over 256 bytes is not read', M.read_part_record(big, 0, '17.32') is None)
    # two messages on one value in a box: silence (perpendicular legs make the path and the components both 7)
    perp = part_problem('brg_legs', {'legs': [[3, 0], [4, 90]], 'want': ['dist', 'bearing']}, ['5', '53'], LEGS_Q)
    case('two different messages on one box value: silence, and no generic fallback', box(perp, 0, '5', '7') is None)
    # equal turn slips are not a collision
    case('a box typed far from every candidate gets nothing', box(legs, 0, '17.32', '19.9') is None)
    # ---- pairs ----
    sub = {'question': Q, 'answer_type': 'vector', 'correct_answer_raw': '4|-2', 'answer_record': {'f': 'vec_sub', 'i': {
        'a0': 5, 'a1': 2, 'b0': 1, 'b1': 4}}}
    case('a pair: the key is never diagnosed', M.diagnose(sub, '4|-2', check_answer('vector', '4|-2', '4|-2'),
                                                           answer_type='vector', correct_raw='4|-2',
                                                           accepts=_accepts('vector', '4|-2'), level='gcse', subject='maths') is None)
    other = dict(sub, correct_answer_raw='5|5')
    case('a pair record whose key differs from the one asked is ignored', M.read_record(other, 'vector', '4|-2') is None
         and run_diag(other, 'vector', '5|5', '-4|2') is None)
    wrong_truth = dict(sub, answer_record={'f': 'vec_sub', 'i': {'a0': 5, 'a1': 2, 'b0': 1, 'b1': 5}})
    case('a pair record that does not reproduce the key gives no topic message',
         run_diag(wrong_truth, 'vector', '4|-2', '-4|3') is None)
    case('a pair record on a different answer type is ignored', M.read_record(sub, 'number', '4|-2') is None)
    mid = {'question': 'Find the midpoint of (2, 2) and (2, 2).', 'answer_type': 'number_pair', 'correct_answer_raw': '2|2',
           'answer_record': {'f': 'gr_midpoint', 'i': {'x1': 2, 'y1': 2, 'x2': 2, 'y2': 2}}}
    case('a pair slip that equals the key is dropped (midpoint of equal points)',
         run_diag(mid, 'number_pair', '2|2', '4|4') is not None and run_diag(mid, 'number_pair', '2|2', '2|2') is None)
    # ---- expressions ----
    nth = {'question': NTH_Q, 'answer_type': 'algebraic', 'correct_answer_raw': '4n',
           'answer_record': {'f': 'seq_nth_find', 'i': {'t': [4, 8, 12, 16, 20]}}}
    case('an expression: the first term and the step are both 4, so 4n+4 has two messages and is silent',
         run_diag(nth, 'algebraic', '4n', '4n+4') is None)
    case('... the key is never diagnosed', run_diag(nth, 'algebraic', '4n', '4n') is None and run_diag(nth, 'algebraic', '4n',
                                                                                                        '4*n') is None)
    case('... n+4 is still named (the step added, not multiplied)',
         (run_diag(nth, 'algebraic', '4n', 'n+4') or M.Diagnosis('', '', '')).rule_id == 'seq.find_add_not_multiply')
    t0 = time.time()
    bombs = ('9**9**9**9*n', 'n' * 600, '(' * 300 + 'n' + ')' * 300, '4n+' + '4n+' * 150 + '1', 'x' * 150 + '+4n+4',
             'sqrt(' * 60 + 'n' + ')' * 60)
    quiet_bombs = all(run_diag(nth, 'algebraic', '4n', b) is None for b in bombs)
    case('... bombs get no diagnosis', quiet_bombs)
    case('... and cost almost nothing (the checker\'s own caps)', time.time() - t0 < 1.5)
    nth_bad = dict(nth, answer_record={'f': 'seq_nth_find', 'i': {'t': [3, 7, 11, 16, 19]}})
    case('... a record that is not arithmetic gives no message', run_diag(nth_bad, 'algebraic', '4n', 'n+4') is None)
    case('... an expression record on a number answer is ignored', M.read_record(nth, 'number', '4n') is None)
    # ---- parsers: bombs ----
    t0 = time.time()
    junk = ('(' * 400, r'\(' + 'x+' * 300 + r'\)', r'Solve \(' + '(' * 60 + 'x' + ')' * 60 + r' = 3\)', 'x' * 5000,
            r'Make \(y\) the subject of the formula: \( A = ' + '3y+' * 40 + '1 \\)', '1,' * 3000)
    ok = True
    for task, fn in CD.DERIVE.items():
        for text in junk:
            try:
                fn(M.plain_text(text))
            except Exception:  # noqa: BLE001
                ok = False
    case('the parsers survive junk and deep nesting without raising', ok)
    case('... and cost almost nothing', time.time() - t0 < 1.0)
    # ---- build_record: a drawing record is dropped beside a topic record; two topic records are not stored ----
    from generators.shared import answer_record as AR
    prob = {'answer_type': 'number', 'correct_answer_raw': '7', 'question': 'q'}
    good = {'family': 'gr_subst', 'inputs': {'task': 'x'}}
    draw = {'family': 'gr_drawn', 'inputs': {'a': 1}}
    a = {'family': 'vec_magnitude', 'inputs': {'x': 3, 'y': 4}}
    got = AR.build_record([a, draw], dict(prob, correct_answer_raw='5'), M.RECORDED_FAMILIES)
    case('a drawing record beside one topic record: the topic record is stored', got == {'f': 'vec_magnitude', 'i': {'x': 3, 'y': 4}})
    case('two topic records: none is stored', AR.build_record([a, a], dict(prob, correct_answer_raw='5'), M.RECORDED_FAMILIES) is None)
    case('two drawing records: none is stored (nothing to say)',
         AR.build_record([draw, draw], dict(prob, correct_answer_raw='5'), M.RECORDED_FAMILIES) is None)
    case('a boxes family on a boxes answer is stored; on a single number it is not',
         AR.build_record([{'family': 'trans_apply', 'inputs': TRANSLATE}], dict(prob, answer_type='number_fields',
                                                                               correct_answer_raw='4|1'), M.RECORDED_FAMILIES)
         is not None
         and AR.build_record([{'family': 'trans_apply', 'inputs': TRANSLATE}], dict(prob, correct_answer_raw='4'),
                             M.RECORDED_FAMILIES) is None)
    case('a family read from the question that cannot be read gives no record',
         AR.build_record([{'family': 'alg', 'inputs': {'task': 'solve_linear'}}], dict(prob, question='Solve the equation.',
                                                                                    answer_type='linear'),
                         M.RECORDED_FAMILIES) is None)
    case('a family read from the question: the record holds the numbers',
         AR.build_record([{'family': 'alg', 'inputs': {'task': 'solve_linear'}}],
                         dict(prob, question=r'Solve \(7x = 28\).', answer_type='linear', correct_answer_raw='x = 4'),
                         M.RECORDED_FAMILIES) == {'f': 'lin_eq', 'i': {'a': [7, 0, 0, 28]}})
    # ---- review 2026-10-26: narrowed rules ----
    turn = part_problem('trans_apply', ROTATE, ['1', '-2'], TURN_Q)
    got = box(turn, 0, '1', '-1')
    case('a box with only its sign wrong is the generic sign line, never "Check the turn direction"',
         got is not None and got.rule_id == 'gen.sign')
    got = box(part_problem('trans_apply', ENLARGE_NEG, ['-4', '-6'], TURN_Q), 0, '-4', '4')
    case('... nor "Check the sign of the scale factor" for one box', got is not None and got.rule_id == 'gen.sign')
    qsim = part_problem('qsim_solve', QSIM, ['-3', '9', '-2', '4'], QSIM_Q)
    case('a y box typed with the other pair\'s y value is not called a sign slip', box(qsim, 1, '9', '4') is None)
    got = box(qsim, 3, '4', '-4')
    case('F7: y = 4 at x = -2 typed -4 is a sign slip, not "multiplied by the power" (2x and -(x squared) are both -4)',
         got is None or got.rule_id != 'qsim.y_doubled')
    mid0 = {'question': 'Find the midpoint of (-3, 0) and (0, -1).', 'answer_type': 'number_pair',
            'correct_answer_raw': '-1.5|-0.5', 'answer_record': {'f': 'gr_midpoint', 'i': {'x1': -3, 'y1': 0, 'x2': 0,
                                                                                          'y2': -1}}}
    case('a pair with one value right and the other only negated is not "subtracted instead of added"',
         run_diag(mid0, 'number_pair', '-1.5|-0.5', '-1.5|0.5') is None)
    case('... the whole pair negated is still the opposite vector',
         (run_diag(sub, 'vector', '4|-2', '-4|2') or M.Diagnosis('', '', '')).rule_id == 'vec.sub_reversed')
    pvi = {'question': r'Make \(I\) the subject of the formula \(P = VI\).', 'answer_type': 'algebraic',
           'correct_answer_raw': 'i=(p)/(v)', 'answer_record': {'f': 'rearrange', 'i': {'v': 'i', 'f': 'p=v*i'}}}
    case('no term moves in P = VI, so -P/V is not "the sign of the term that moved"',
         run_diag(pvi, 'algebraic', 'i=(p)/(v)', 'i=-p/v') is None)
    lin = {'question': r'Solve \(\dfrac{x + 3}{5} = 4\).', 'answer_type': 'number', 'correct_answer_raw': '17',
           'answer_record': {'f': 'lin_eq', 'i': {'a': ['1/5', '3/5', 0, 4]}}}
    got = run_diag(lin, 'number', '17', '19.4')
    case('(x + 3)/5 = 4 typed 19.4 is not "only one term was divided" (the step multiplies)',
         got is None or got.rule_id != 'alg.lin_one_term_divided')
    coins = {'question': '3 fair coins are flipped. Find P(at least 1 head).', 'answer_type': 'fraction',
             'correct_answer_raw': '7/8', 'answer_record': {'f': 'prob_coins', 'i': {'n': 3, 'r': 1, 'style_word': 'at least'}}}
    got = run_diag(coins, 'fraction', '7/8', '1/2')
    case('one half in a coin question is never named as a slip', got is None or not got.rule_id.startswith('prob.'))
    surd = {'question': 'Solve x^2 + 6x - 5 = 0.', 'answer_type': 'quadratic_roots',
            'correct_answer_raw': '-3+sqrt(14),-3-sqrt(14)'}
    case('roots with a surd: flipped signs get no bracket message',
         run_diag(surd, 'quadratic_roots', '-3+sqrt(14),-3-sqrt(14)', '3-sqrt(14),3+sqrt(14)') is None)
    sym = {'question': 'Find the roots of y = (x + 2)(x - 2).', 'answer_type': 'number_pair', 'correct_answer_raw': '-2|2',
           'answer_record': {'f': 'gr_roots', 'i': {'s1': '+', 'c1': 2, 's2': '-', 'c2': 2}}}
    got = run_diag(sym, 'number_pair', '-2|2', '2|-2')
    case('roots -2 and 2 typed the other way round are the order, not the signs (found by --deep)',
         got is not None and got.rule_id == 'gen.pair_swapped')
    # found by --deep: the mean of 2, 4, 9, 9, 10, 11, 11 is 8; 9 is the middle value, and the total over n - 1 is 9.33,
    # which a pupil rounds to 9 (a printed number, so that rule is kept quiet). Two slips reach 9: silence.
    mean9 = {'question': 'The values are 2, 4, 9, 9, 10, 11, 11. Find the mean.', 'answer_type': 'number',
             'correct_answer_raw': '8', 'answer_record': {'f': 'stats_list', 'i': {'stat_word': 'mean',
                                                                                 'values': [2, 4, 9, 9, 10, 11, 11]}}}
    case('9 is the middle value and also the total over n - 1 rounded (kept quiet): two slips, so silence',
         run_diag(mean9, 'number', '8', '9') is None)
    case('... 9.33 is still named', (run_diag(mean9, 'number', '8', '9.33') or M.Diagnosis('', '', '')).rule_id
         == 'stats.mean_divisor')
    arith = {'question': 'Calculate ( 5² − 1 ) ÷ ( 2 − 3 ) + 1', 'answer_type': 'number', 'correct_answer_raw': '-23',
             'answer_record': {'f': 'arith', 'i': {'expr': '(5² − 1) ÷ (2 − 3) + 1'}}}
    got = run_diag(arith, 'number', '-23', '23')
    case('a slip worth 22.5 is not "rounded" to a typed 23: the sign line speaks (found by --deep)',
         got is not None and got.rule_id == 'gen.sign')
    # ---- Phase 5b review (2026-10-27) ----
    def scalar(fam, inputs, key, question, typed, at='number'):
        prob = {'question': question, 'answer_type': at, 'correct_answer_raw': key, 'answer_record': {'f': fam, 'i': inputs}}
        return run_diag(prob, at, key, typed)

    def rid(got):
        return got.rule_id if got is not None else None

    case('5b review: "(-4)^3" is not a sum of decimals, so -1 is never "line up the decimal points"',
         rid(scalar('arith', {'expr': '(-4)^3'}, '-64', 'Calculate (-4)^3', '-1')) != 'dec.arith_not_aligned')
    case('... nor a power beside decimals: 1.5^2 + 2.25 is not read as 1.5 + 2 + 2.25 (5.3 with 1.5 as 1.05)',
         rid(scalar('arith', {'expr': '1.5^2 + 2.25'}, '4.5', 'Calculate 1.5^2 + 2.25', '5.3')) != 'dec.arith_not_aligned')
    case('5b review: change from \u00a312.50 is printed lined up, so 0.69 is not a lining-up slip',
         rid(scalar('num_directed', {'a': 12.5, 'op': '-', 'b': 11.36}, '1.14',
                    'An item costs \u00a311.36. How much change from \u00a312.50?', '0.69')) != 'dec.directed_not_aligned')
    case('... while 1.66 - 1.5 typed 0.61 still is (1.5 read as 1.05)',
         rid(scalar('num_directed', {'a': 1.66, 'op': '-', 'b': 1.5}, '0.16', 'Calculate 1.66 \u2212 1.5', '0.61'))
         == 'dec.directed_not_aligned')
    share = part_problem('ratio_share', {'total': 81, 'parts': [3, 2, 4]}, ['27', '18', '36'], 'Share 81 sweets in the ratio 3:2:4.')
    case('5b review: the first share typed in the second box (27, also 81 shared equally) is silent',
         rid(box(share, 1, '18', '27')) != 'ratio.ratio_share_equal')
    case('... the share typed in the box of another part stays a "parts swapped" slip when the rule is a swap',
         rid(box(share, 0, '27', '36')) == 'ratio.ratio_share_swapped')
    cones = part_problem('sim_cone_scale', {'r_small': 6, 'r_large': 12, 'vol': 96, 'sa': 96}, ['768', '384'], Q5B)
    case('5b review: equal printed volume and area (96 and 96): the other box\'s answer is silent',
         box(cones, 0, '768', '384') is None and box(cones, 1, '384', '768') is None)
    sides = part_problem('sim_sides', {'known_new': 12, 'known_old': 8, 'others': [9]}, ['13.5'], Q5B)
    case('5b review: QR = 13.5 typed 13 is the key cut short, not "adding the same amount"', box(sides, 0, '13.5', '13') is None)
    case('... 13.5 typed 14 likewise', box(sides, 0, '13.5', '14') is None)
    tri = part_problem('ang_alg', {'rule_word': 'triangle', 'terms': [3, 11, 2, 6, 3, 35]}, ['16', '59', '38', '83'], Q5B)
    case('5b review: angle 2 typed with angle 3 (83) is not "check which total fits"', box(tri, 2, '38', '83') is None)
    case('5b review: the semicircle line no longer states the answer (a right angle)',
         'right angle' not in M.MESSAGES['circ.semicircle_right'] and '90' not in M.MESSAGES['circ.semicircle_right'])
    for gone in ('ang.cross_swapped', 'ang.vertical_swapped', 'ang.turn_supplement', 'circ.alt_parallel_supplement',
                 'circ.same_segment_supplement', 'circ.same_segment_supplement_s'):
        case(f'5b review: {gone} only ever repeated the generic angle line and is gone',
             gone not in CD_RULES_BY_ID and gone not in {r.id for r in CD.RULES})
    # ---- Phase 5c (2026-10-27) ----
    def r5c(fam, inputs, key, question, typed, at='number'):
        return rid(scalar(fam, inputs, key, question, typed, at))

    case('5c: 776.4342 to 3 decimal places typed 776 is also the decimals dropped: no "significant figures" line',
         r5c('num_round_dp', {'n': 776.4342, 'dp': 3}, '776.434', 'Round 776.4342 to 3 decimal places.', '776')
         != 'num.round_dp_as_sf')
    case('... 20.984 to 2 decimal places typed 21 is 2 significant figures and 1 decimal place: no such line',
         r5c('num_round_dp', {'n': 20.984, 'dp': 2}, '20.98', 'Round 20.984 to 2 decimal places.', '21') != 'num.round_dp_as_sf')
    case('... 22.835 to 1 decimal place typed 20 is the tens, which the generic accuracy line already names',
         r5c('num_round_dp', {'n': 22.835, 'dp': 1}, '22.8', 'Round 22.835 to 1 decimal place.', '20') != 'num.round_dp_as_sf')
    case('... a record of 0 decimal places (never generated) is not read as a significant-figure confusion',
         r5c('num_round_dp', {'n': 812.2411, 'dp': 0}, '812', 'Round 812.2411 to the nearest whole number.', '800')
         != 'num.round_dp_as_sf')
    case('... while 812.2411 to 1 decimal place typed 800 is named',
         r5c('num_round_dp', {'n': 812.2411, 'dp': 1}, '812.2', 'Round 812.2411 to 1 decimal place.', '800')
         == 'num.round_dp_as_sf')
    case('5c: 5304 to 1 significant figure typed 5 is only three places short (the generic place-value line speaks)',
         r5c('num_round_sf', {'n': 5304, 'sf': 1}, '5000', 'Round 5304 to 1 significant figure.', '5') != 'num.round_sf_zeros')
    case('... 76243 to 1 significant figure typed 8 is named, and typed 80000 (the key) is not',
         r5c('num_round_sf', {'n': 76243, 'sf': 1}, '80000', V_5C, '8') == 'num.round_sf_zeros'
         and r5c('num_round_sf', {'n': 76243, 'sf': 1}, '80000', V_5C, '80000') is None)
    case('5c: the sum to infinity with a ratio of 1/2: a over r is the key, so only the plus line is left (5 / 1.5 = 3.33)',
         r5c('seq_geo_inf', {'a': 5, 'rn': 1, 'rd': 2}, '10', V_5C, '3.33') == 'seq.infinite_plus_ratio'
         and r5c('seq_geo_inf', {'a': 5, 'rn': 1, 'rd': 2}, '10', V_5C, '10') is None)
    case('5c: 50 shared at 5 each after a fixed 10: 50 / 5 = 10 is the fixed charge printed in the question, so silent',
         r5c('linear_fixed_rate', {'fixed': 10, 'rate': 5, 'total': 50}, '8', 'A taxi charges a \u00a310 fixed fare plus \u00a35 per mile. '
             'The total fare is \u00a350. How many miles were travelled?', '10') != 'lin.fixed_ignored')
    case('5c: an arithmetic pattern is not a Fibonacci pattern, so no Fibonacci line',
         r5c('seq_terms', {'t': [2, 4, 6, 8, 10], 'at': 5}, '12', 'A sequence starts: 2, 4, 6, 8, 10, ___ Find the next term.', '14')
         != 'seq.fibonacci_constant_step')
    case('5c: inputs that do not reproduce the key give nothing (square root equation, key 33 for r = 8, c = 32)',
         r5c('surd_sqrt_eq', {'c': 32, 'r': 8}, '33', V_5C, '-24') is None)
    case('5c: the angles of a triangle taken as 90 give x = 0 here, which is no 360 slip',
         r5c('ang_sum_x', {'a': ['1', '3', '2'], 'b': ['5', '15', '70']}, '15', V_5C, '0', at='linear') != 'ang.sum_x_wrong_total')
    case('5c: the old sum-variant parser result is gone (an arithmetic series is not read as a geometric one)',
         CD.DERIVE['seq_geometric']('Find the sum of the first 10 terms of the arithmetic series with first term 2 and common '
                                    'difference 3.') is None)
    # ---- section 25 review (2026-10-27): a 5c slip that lands on the key's sign, reciprocal or a power of ten is silent ----
    case('5c review: sqrt(x + 21) = 6 typed -15 is also the key with its sign changed: no "square both sides" line',
         r5c('surd_sqrt_eq', {'c': 21, 'r': 6}, '15', V_5C, '-15') != 'surd.equation_not_squared')
    case('... (2 + sqrt 3)(2 - sqrt 3) typed -1 is the key with its sign changed, so no "first term" line',
         r5c('surd_conj', {'a': 2, 'b': 3}, '1', V_5C, '-1') != 'surd.conjugate_unsquared')
    think = 'I think of a number. I multiply it by {} and add {}. The result is {}. What is the number?'
    case('... "multiply by 5 and add 5, result 15" typed -2 is the key with its sign changed: no "undo the last step" line',
         r5c('think_number', {'mult': 5, 'add': 5, 'result': 15}, '2', think.format(5, 5, 15), '-2', at='linear')
         != 'eq.think_undo_order')
    case('... "multiply by 4 and add 2, result 10" typed 0.5 is the key upside down: no "undo the last step" line',
         r5c('think_number', {'mult': 4, 'add': 2, 'result': 10}, '2', think.format(4, 2, 10), '0.5', at='linear')
         != 'eq.think_undo_order')
    case('... a £36 fixed fare, £2 a mile, £44 in all, typed 40 (ten times the key): no "fixed charge" line',
         r5c('linear_fixed_rate', {'fixed': 36, 'rate': 2, 'total': 44}, '4', 'A taxi charges a £36 fixed fare plus £2 per '
             'mile. The total fare is £44. How many miles were travelled?', '40') != 'lin.fixed_added')
    case('... while at £10 a mile the cost of the miles (130 for 13) keeps its own line',
         r5c('linear_fixed_rate', {'fixed': 28, 'rate': 10, 'total': 158}, '13', 'A taxi charges a £28 fixed fare plus £10 per '
             'mile. The total fare is £158. How many miles were travelled?', '130') == 'lin.cost_not_divided')
    case('5c review: x + 30, 4x + 13, x + 17 with a total of 360 gives 50, which is also the first angle: silent',
         r5c('ang_sum_x', {'a': ['1', '4', '1'], 'b': ['30', '13', '17']}, '20', V_5C, '50', at='linear')
         != 'ang.sum_x_wrong_total')
    case('5c review: a square number under the root is no surd, so (2 + √4)(2 − √4) is not read',
         CD.DERIVE['surd']('Expand and simplify (  2 + √4  )(  2 − √4  ).') is None
         and r5c('surd_conj', {'a': 2, 'b': 4}, '0', V_5C, '8') is None)
    case('5c review: 850.5049 to 2 decimal places typed 850 is also the decimals cut off: no "significant figures" line',
         r5c('num_round_dp', {'n': 850.5049, 'dp': 2}, '850.5', 'Round 850.5049 to 2 decimal places.', '850')
         != 'num.round_dp_as_sf')
    case('5c review: the index line no longer says "multiplied by itself" (3 to the 6 is five multiplications)',
         'by itself' not in M.MESSAGES['num.index_divided'])
    case('5c review: the Fibonacci line fits both readings of its value (the last gap repeated, or the wrong pair added)',
         'gap' not in M.MESSAGES['seq.fibonacci_step'])
    # Phase 3 batch A review: a slip that is not a whole number is not matched by rounding when the answer is whole
    case('batch A review: 7 x ? - 4 = 80 typed 11 (one off 12) is not "the wrong inverse" (76/7 rounds to 11)',
         r5c('bidmas_missing', {'form': 'mul_sub', 'a': 7, 'b': 4, 'c': 80}, '12',
             'Find the positive whole number that goes in the box. 7 × □ − 4 = 80', '11') != 'bidmas.missing_wrong_inverse')
    case('... angles (x + 24), (3x - 5) and 3x on a line typed 22 (one off 23) is not "the sign" (151/7 rounds to 22)',
         r5c('alg_angles', {'total': 180, 'a': 24, 'b': 5, 'c1': 1, 'c2': 3, 'c3': 3}, '23',
             'The sizes of angles on a straight line are (x + 24)°, (3x − 5)° and 3x°.', '22') != 'alg.angles_sign_moved')
    case('... the denominators line reads for a subtraction too', 'taken away' in M.MESSAGES['frac.denominators_added'])
    del good
    return out


def used_messages():
    return {r.message for r in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES}


def check_tables():
    for line in run_tables():
        issue('unit_table', 'phase 5 tables', line)
    for line in run_derive():
        issue('unit_table', 'phase 5 parsers', line)
    for name, ok in other_cases():
        if not ok:
            issue('unit_table', 'phase 5 cases', name)
    have = {c[0] for c in PAIR_TX + PART_TX + EXPR_TX}
    for rule in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES:
        if rule.id not in have:
            issue('unit_table', rule.id, 'rule has no hand-worked example')
        if rule.message not in M.MESSAGES:
            issue('unit_table', rule.id, f'message id {rule.message!r} missing from MESSAGES')
    for fams, rows, label in ((CD.PAIR_FAMILIES, PAIR_TX, 'pair'), (CD.PART_FAMILIES, PART_TX, 'boxes'),
                              (CD.EXPR_FAMILIES, EXPR_TX, 'expression')):
        covered = {c[1] for c in rows}
        for fam in sorted(fams - covered):
            issue('unit_table', fam, f'{label} family has no hand-worked example (its truth guard is untested)')
    for task in CD.DERIVE:
        if task not in {t for t, *_ in DERIVE_TX}:
            issue('unit_table', task, 'parser has no hand-worked example')
    for rid in sorted(have - set(CD_RULES_BY_ID)):
        issue('unit_table', rid, 'example for a rule that does not exist')
    # generic rules added in Phase 5 are in the smoke's own EXAMPLES (GENERIC_EXAMPLES), nothing to do here


# ─────────────────────────────────────────────────────────────────────────────
# mutation: perturb each rule's value, and each family's truth, by one unit; the tables must notice
# ─────────────────────────────────────────────────────────────────────────────

def check_mutation():
    killed = total = 0
    saved = {name: dict(getattr(CD, name)) for name in ('PAIR_BY_FAMILY', 'PART_BY_FAMILY', 'EXPR_BY_FAMILY')}
    saved_truth = {name: dict(getattr(CD, name)) for name in ('PAIR_TRUTH', 'PART_TRUTH', 'EXPR_TRUTH')}

    def bump(kind, orig):
        if kind == 'pair':
            return lambda i, o=orig: [(Fraction(a) + 1, b) for a, b in o(i)]
        if kind == 'part':
            def f(i, pi=None, o=orig):
                return [[(None if e is None else [Fraction(x) + 1 for x in (e if isinstance(e, (list, tuple)) else [e])])
                         for e in vec] for vec in o(i)]
            return f
        return lambda i, o=orig: [c + '+1' for c in o(i)]

    try:
        for kind, by_family in (('pair', 'PAIR_BY_FAMILY'), ('part', 'PART_BY_FAMILY'), ('expr', 'EXPR_BY_FAMILY')):
            table = getattr(CD, by_family)
            for rule in {r.id: r for rules in saved[by_family].values() for r in rules}.values():
                total += 1
                mutant = dataclasses.replace(rule, slip=bump(kind, rule.slip))
                for fam in rule.families:
                    table[fam] = tuple(mutant if r is rule else r for r in saved[by_family][fam])
                if run_tables(only_rule=rule.id):
                    killed += 1
                else:
                    issue('mutation', rule.id, 'a rule whose value is off by one still passes the Phase 5 table')
                for fam in rule.families:
                    table[fam] = saved[by_family][fam]
        for kind, name in (('pair', 'PAIR_TRUTH'), ('part', 'PART_TRUTH'), ('expr', 'EXPR_TRUTH')):
            table = getattr(CD, name)
            for fam in sorted(saved_truth[name]):
                total += 1
                orig = saved_truth[name][fam]
                if kind == 'pair':
                    table[fam] = lambda i, o=orig: (Fraction(o(i)[0]) + 1, o(i)[1])
                elif kind == 'part':
                    table[fam] = lambda i, o=orig: [Fraction(v) + 1 for v in o(i)]
                else:
                    table[fam] = lambda i, o=orig: (o(i)[0], o(i)[1] + '+1')
                if run_tables(only_family=fam):
                    killed += 1
                else:
                    issue('mutation', fam, 'a truth guard that is off by one still passes the Phase 5 table')
                table[fam] = orig
    finally:
        for name, value in saved.items():
            getattr(CD, name).clear()
            getattr(CD, name).update(value)
        for name, value in saved_truth.items():
            getattr(CD, name).clear()
            getattr(CD, name).update(value)
    return killed, total


# ─────────────────────────────────────────────────────────────────────────────
# generated questions: pairs, boxes and expressions
# ─────────────────────────────────────────────────────────────────────────────

def new_state():
    return {'fired': collections.Counter(), 'applicable': collections.Counter(), 'collided': collections.Counter(),
            'slot_fired': set(), 'slot_fired_near': set(), 'families': collections.defaultdict(set), 'guard_fail': [],
            'records': 0, 'checks': 0, 'examples': {}, 'quiet': collections.Counter()}


def near_key_values(key):
    """Typed values next to a scalar key that are far likelier an arithmetic slip or the key written short than a
    named misconception (whole-change review 2026-11-03, F9): one either side of a whole-number key, and a key that is
    not whole rounded or cut to no and to one decimal place."""
    key = Fraction(key)
    if key.denominator == 1:
        return {key - 1, key + 1}
    out = set()
    for places in (0, 1):
        unit = Fraction(1, 10 ** places)
        scaled = abs(key) / unit
        cut = Fraction(scaled.numerator // scaled.denominator)
        up = cut + (1 if scaled - cut >= Fraction(1, 2) else 0)
        sign = 1 if key > 0 else -1
        out |= {sign * cut * unit, sign * up * unit}
    return out - {key}


def handles(problem):
    rec = problem.get('answer_record')
    if not isinstance(rec, dict):
        return False
    fam = rec.get('f')
    return fam in CD.PAIR_FAMILIES or fam in CD.EXPR_FAMILIES or (
        fam in CD.PART_FAMILIES and problem.get('answer_type') == 'number_fields')


def _fmt_pair_value(x):
    return AC._format_number(M._decimal_of(x))


def _terminates(x):
    x = Fraction(x)
    d = x.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def item(slot, run, problem, st):
    """One generated question whose record is a pair, a set of boxes or an expression."""
    rec = problem['answer_record']
    fam, inputs = rec['f'], rec['i']
    at, raw = problem.get('answer_type') or 'number', str(problem.get('correct_answer_raw'))
    label = f'{slot.label}#{run}'
    st['records'] += 1
    st['families'][fam].add(slot.label)
    if problem.get('options') or at not in M.RECORDED_FAMILIES.get(fam, ()):
        issue('rule_sound', label, f'a record on a question that cannot use one ({at}, family {fam!r})')
        return
    if fam in CD.EXPR_FAMILIES:
        _expr_item(slot, label, problem, fam, inputs, at, raw, st)
    elif fam in CD.PAIR_FAMILIES:
        _pair_item(slot, label, problem, fam, inputs, at, raw, st)
    else:
        _part_item(slot, label, problem, fam, inputs, raw, st)


def _record_fire(st, slot, rid, example, near=False):
    st['fired'][rid] += 1
    # a firing only next to the key (near_key_values) does not count the slot as covered (F9)
    st['slot_fired_near' if near else 'slot_fired'].add(slot.label)
    st['examples'].setdefault(rid, example)


EXPR_PER_FAMILY = 4            # algebra costs real time (SymPy): after this many, a question only gets one diagnosis


def _expr_light(slot, problem, fam, inputs, at, raw, st):
    """One diagnosis for the slot count: the first slip whose message no other slip shares."""
    if slot.label in st['slot_fired']:
        return                                          # the other seed of this practice slot already counted
    prefix = ''
    try:
        subject, truth = CD.EXPR_TRUTH[fam](inputs)
        prefix = f'{subject}=' if subject else ''
        rules = CD.EXPR_BY_FAMILY.get(fam, ())
        count = collections.Counter()
        slips = []
        for rule in rules:
            for c in rule.slip(inputs)[:8]:
                slips.append((rule, prefix + c))
                count[rule.message] += 1
    except Exception:  # noqa: BLE001
        return
    for rule, full in slips:
        if len({r.message for r, f in slips if f == full}) != 1 or len(full) > AC.MAX_SYMPY_EXPR_LEN:
            continue
        got = run_diag(problem, at, raw, full, topic=slot.slug)
        if got is not None and got.message == M.MESSAGES[rule.message]:
            st['slot_fired'].add(slot.label)
            return


def _expr_item(slot, label, problem, fam, inputs, at, raw, st):
    seen = st.setdefault('expr_seen', collections.Counter())
    if seen[fam] >= EXPR_PER_FAMILY and all(st['fired'][r.id] for r in CD.EXPR_BY_FAMILY.get(fam, ())):
        _expr_light(slot, problem, fam, inputs, at, raw, st)
        return
    seen[fam] += 1
    try:
        subject, truth = CD.EXPR_TRUTH[fam](inputs)
    except Exception:  # noqa: BLE001
        st['guard_fail'].append(label)
        return
    prefix = f'{subject}=' if subject else ''
    if not AC._algebraic_answers_equivalent(raw, prefix + truth):
        st['guard_fail'].append(label)
        return
    cands = []
    for rule in CD.EXPR_BY_FAMILY.get(fam, ()):
        try:
            slips = rule.slip(inputs)[:8]
        except Exception:  # noqa: BLE001
            continue
        for c in slips:
            full = prefix + c
            if len(full) > AC.MAX_SYMPY_EXPR_LEN or AC._algebraic_answers_equivalent(raw, full):
                continue
            cands.append((rule, full))
    groups = []
    for rule, full in cands:
        for g in groups:
            if g[0][1] == full or AC._algebraic_answers_equivalent(g[0][1], full):
                g.append((rule, full))
                break
        else:
            groups.append([(rule, full)])
    for g in groups:
        rules = {rule.id: rule for rule, _ in g}
        messages = {r.message for r in rules.values()}
        typed = g[0][1]
        for rid in rules:
            st['applicable'][rid] += 1                  # an expression has no quiet values: every candidate counts
        st['checks'] += 1
        res = check_answer(at, raw, typed)
        if res.get('correct'):
            issue('rule_sound', label, f'{sorted(rules)} candidate {typed!r} is accepted by the checker (key {raw!r})')
            continue
        got = run_diag(problem, at, raw, typed, topic=slot.slug, result=res)
        if len(messages) >= 2:
            for rid in rules:
                st['collided'][rid] += 1
            if got is not None:
                issue('no_collision', label, f'{typed!r} matches {sorted(messages)} but the pupil is shown {got.message!r}')
            continue
        want = next(iter(messages))
        if got is None or got.message != M.MESSAGES[want]:
            issue('rule_reachable', label, f'{typed!r} (rules {sorted(rules)}, key {raw!r}) got {got.rule_id if got else None!r}')
            continue
        _record_fire(st, slot, got.rule_id, (slot.label, M.plain_text(problem.get('question'))[:90], raw, typed, got.message))


def _pair_item(slot, label, problem, fam, inputs, at, raw, st):
    ctx = M.build_ctx(problem, at, raw, slot.slug, None)
    if ctx is None or ctx.pair is None:
        st['guard_fail'].append(label)
        return
    key = tuple(Fraction(c) for c in ctx.pair)
    question = M.plain_text(problem.get('question'), problem.get('answer_format_hint'))
    spec = M._stated_spec_for_key(question, key[0]) if key[0] != 0 else None
    if spec is None and key[1] != 0:
        spec = M._stated_spec_for_key(question, key[1])

    def told(x):
        x = Fraction(x)
        return M.apply_spec(x, spec) if spec is not None else x

    try:
        truth = CD.PAIR_TRUTH[fam](inputs)
        if (told(truth[0]), told(truth[1])) != key:
            st['guard_fail'].append(label)
            return
        printed = M._pair_numbers(inputs)
    except Exception:  # noqa: BLE001
        st['guard_fail'].append(label)
        return
    groups = collections.defaultdict(list)
    for rule in CD.PAIR_BY_FAMILY.get(fam, ()):
        try:
            slips = rule.slip(inputs)
        except Exception:  # noqa: BLE001
            continue
        for c in slips:
            shown = (told(c[0]), told(c[1]))
            if shown == key or not (_terminates(shown[0]) and _terminates(shown[1])):
                continue
            groups[shown].append(rule)
    for shown, rules in groups.items():
        if M._one_sign_off(shown, key):
            rules = [r for r in rules if r.message in M._SIGN_MESSAGES]      # one sign slip explains it: those stay quiet
            if not rules:
                continue
        typed = f'{_fmt_pair_value(shown[0])}|{_fmt_pair_value(shown[1])}'
        messages = {r.message for r in rules}
        quiet = shown in printed and not all(r.id in T.ECHO_OK for r in rules)
        if quiet:
            st['quiet'][rules[0].id] += 1
            continue
        for r in rules:
            st['applicable'][r.id] += 1
        st['checks'] += 1
        res = check_answer(at, raw, typed)
        if res.get('correct'):
            issue('rule_sound', label, f'{[r.id for r in rules]} candidate {typed!r} is accepted by the checker (key {raw!r})')
            continue
        got = run_diag(problem, at, raw, typed, topic=slot.slug, result=res)
        if len(messages) >= 2:
            for r in rules:
                st['collided'][r.id] += 1
            if got is not None:
                issue('no_collision', label, f'{typed!r} matches {sorted(messages)} but the pupil is shown {got.message!r}')
            continue
        want = next(iter(messages))
        if got is None or got.message != M.MESSAGES[want]:
            issue('rule_reachable', label, f'{typed!r} (rules {[r.id for r in rules]}, key {raw!r}) got '
                                           f'{got.rule_id if got else None!r}')
            continue
        _record_fire(st, slot, got.rule_id, (slot.label, M.plain_text(problem.get('question'))[:90], raw, typed, got.message))


def _part_item(slot, label, problem, fam, inputs, raw, st):
    sep = '\x1e' if '\x1e' in raw else '|'
    keys = raw.split(sep)
    seen_guard = False
    for j, key in enumerate(keys):
        found = M.part_topic(problem, j, 'number', key, slot.slug)
        if found is None:
            continue
        if found == []:
            if not seen_guard:
                st['guard_fail'].append(label)
                seen_guard = True
            continue
        ctx, cands, quiet = found
        accepts = _accepts('number', key)
        groups = collections.defaultdict(list)
        for rule, c in cands:
            groups[Fraction(c)].append(rule)
        for c, rules in groups.items():
            shown = M._topic_shown(ctx, c)
            typed = M.format_answer(shown)
            st['checks'] += 1
            res = check_answer('number', key, typed)
            if res.get('correct'):
                issue('rule_sound', label, f'{[r.id for r in rules]} box {j} candidate {typed!r} is accepted (key {key!r})')
                continue
            hits = M._topic_hits(ctx, cands, typed, accepts, quiet)
            if not hits:
                st['quiet'][rules[0].id] += 1                  # printed in the question, or next to the key: said nothing
                continue
            for r in rules:
                st['applicable'][r.id] += 1
            got = M._diagnose(problem, typed, res, 'number', key, accepts, 'gcse', 'maths', slot.slug, None, part=j)
            if len(hits) >= 2:
                for r in rules:
                    st['collided'][r.id] += 1
                if got is not None:
                    issue('no_collision', label, f'box {j}: {typed!r} matches {sorted(hits)} but the pupil is shown {got.message!r}')
                continue
            if got is None or got.message != next(iter((M.MESSAGES[m] for m in hits))):
                issue('rule_reachable', label, f'box {j}: {typed!r} (rules {[r.id for r in rules]}, key {key!r}) got '
                                               f'{got.rule_id if got else None!r}')
                continue
            _record_fire(st, slot, got.rule_id, (slot.label, M.plain_text(problem.get('question'))[:90], key, typed, got.message),
                         near=M.read_user_scalar('number', typed) in near_key_values(ctx.key))


def check_rules_fire(st):
    for rule in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES:
        n = st['fired'][rule.id]
        if n < 1:
            issue('rule_reachable', rule.id, 'a Phase 5 rule that never fires on a generated question (dead rule or untested family)')
        app = st['applicable'][rule.id]
        if app and n / app < 0.5:
            issue('rule_reachable', rule.id, f'unambiguous on only {n}/{app} of its candidates (below 50%: review)')
    for fam in sorted(CD.PAIR_FAMILIES | CD.PART_FAMILIES | CD.EXPR_FAMILIES):
        if fam not in st['families']:
            issue('rule_reachable', fam, 'a recorded family that no generated practice question carries')
    if st['records'] and len(st['guard_fail']) / st['records'] > 0.05:
        issue('rule_sound', 'guard', f'{len(st["guard_fail"])} of {st["records"]} Phase 5 records do not reproduce their key: '
                                     f'{st["guard_fail"][:4]}')


# ─────────────────────────────────────────────────────────────────────────────
# the check route: a box, a pair and an expression are diagnosed from the session problem only
# ─────────────────────────────────────────────────────────────────────────────

def check_routes(client, bind, stored, messages):
    hdr = {'Accept': 'application/json'}

    def post(body):
        return client.post('/api/v1/problems/check', json=body, headers=hdr).get_json()

    def shown(body, rid):
        return body.get('correct') is False and body.get('hint', {}).get('id') == rid \
            and body.get('feedback') == M.MESSAGES[CD_RULES_BY_ID[rid].message]

    CD_RULES_BY_ID.update({r.id: r for r in CD.PAIR_RULES + CD.PART_RULES + CD.EXPR_RULES})
    boxes = part_problem('trans_apply', TRANSLATE, ['4', '1'], TURN_Q)
    boxes.update(answer_field_types=['number', 'number'], answer_labels=['x', 'y'])
    bind(client, boxes, topic='geometry_transformations')
    before = stored(client)
    body = post({'user_answer': '-2', 'correct_answer_raw': '4', 'answer_type': 'number', 'part_index': 0, 'part_total': 2})
    if not shown(body, 'trans.translate_opposite'):
        issue('no_leak', 'route', f'a box of a multi-box answer was not diagnosed by the check route: {body}')
    if 'answer_record' in str(body) or stored(client) != before:
        issue('no_leak', 'route', 'the box response or the session changed')
    body = post({'user_answer': '-2', 'correct_answer_raw': '1', 'answer_type': 'number', 'part_index': 1, 'part_total': 2})
    if 'hint' in body or body.get('feedback') in messages:
        issue('no_leak', 'route', f'-2 typed in the other box was diagnosed with the first box rule: {body}')
    body = post({'user_answer': '-2', 'correct_answer_raw': '9', 'answer_type': 'number', 'part_index': 0, 'part_total': 2})
    if 'hint' in body:
        issue('no_leak', 'route', 'a key the client made up was used for a box')
    body = post({'user_answer': '-2|3', 'answer_type': 'number_fields'})
    if 'hint' in body or body.get('feedback') in messages:
        issue('no_leak', 'route', 'a whole multi-box answer was diagnosed')
    vec = {'question': Q, 'answer_type': 'vector', 'correct_answer_raw': '4|-2',
           'answer_record': {'f': 'vec_sub', 'i': {'a0': 5, 'a1': 2, 'b0': 1, 'b1': 4}}}
    bind(client, vec, topic='vectors')
    body = post({'user_answer': '-4|2'})
    if not shown(body, 'vec.sub_reversed'):
        issue('no_leak', 'route', f'a vector slip was not diagnosed by the check route: {body}')
    expr = {'question': 'Make y the subject of A = 3y + 1.', 'answer_type': 'algebraic', 'correct_answer_raw': 'y=(A-1)/3',
            'answer_record': {'f': 'rearrange', 'i': {'v': 'y', 'f': 'a=3*y+1'}}}
    bind(client, expr, topic='algebra')
    body = post({'user_answer': 'y=(a+1)/3'})
    if not shown(body, 'alg.rearr_sign_moved'):
        issue('no_leak', 'route', f'an expression slip was not diagnosed by the check route: {body}')
    body = post({'user_answer': 'y=(a+1)/3', 'hint_ladder': True})
    if (body.get('hint') or {}).get('id') != 'alg.rearr_sign_moved' or 'answer_record' in str(body):
        issue('no_leak', 'route', f'the hint ladder lost the expression slip or leaked the record: {body}')
    bind(client, {k: v for k, v in expr.items() if k != 'answer_record'}, topic='algebra')
    body = post({'user_answer': 'y=(a+1)/3', 'answer_record': expr['answer_record']})
    if 'hint' in body or body.get('feedback') in messages:
        issue('no_leak', 'route', f'an answer_record sent by the client was used for an expression: {body}')
