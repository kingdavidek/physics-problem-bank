"""Hand-worked examples for the Phase 5b rules (docs/GCSE_MATHS_HINTS.md, section 23).

Read by scripts/gcse_hints_cd.py, which concatenates these tables onto its own and runs them with the same code:

  PART_TX_5B     per-box rules: (rule id, family, inputs, keys of every box, box index, typed, question)
  EXPR_TX_5B     algebraic-answer rules: (rule id, family, inputs, key, typed text(s), question)
  PAIR_TX_5B     pair rules: (rule id, family, inputs, key pair, typed pair, question)
  DERIVE_TX_5B   parsers that read a family from the displayed question
  SCALAR_TX_5B   one-value rules: (rule id, family, inputs, answer type, key, typed, question)

Every typed value below was worked by hand from the inputs (the comment says how when it is not obvious). The shape
of each question does not matter to the rule, only the accuracy it states.
"""
from __future__ import annotations

Q = 'Find the angle.'
L = 'Find the length.'
R2DP = 'Find the length. Give your answer to 2 decimal places.'
V = 'Find the value.'
R1DP = 'Find the length. Give your answer to 1 decimal place.'

PART_TX_5B = (
    # ---- circle theorems -------------------------------------------------------------------------------------------
    ('circ.half_doubled', 'circ_half', {'angle': 140}, ['70'], 0, '280', Q),                 # 2 x 140
    ('circ.double_halved', 'circ_double', {'angle': 64}, ['128'], 0, '32', Q),               # 64 / 2
    ('circ.half_twice_doubled', 'circ_half_twice', {'centre': 110}, ['55', '55'], 1, '220', Q),
    ('circ.semicircle_straight', 'circ_semicircle_90', {}, ['90'], 0, '180', Q),
    ('circ.semi_third_180', 'circ_semi_third', {'angle': 60}, ['30'], 0, '120', Q),          # 180 - 60
    ('circ.alt_semicircle_180', 'circ_alt_semicircle', {'angle': 40}, ['40', '50'], 1, '140', Q),
    ('circ.opposite_equal', 'circ_opposite', {'angle': 115}, ['65'], 0, '115', Q),
    ('circ.cyclic2_equal', 'circ_cyclic2', {'a': 105, 'b': 85}, ['75', '95'], 0, '105', Q),
    ('circ.cyclic2_equal', 'circ_cyclic2', {'a': 105, 'b': 85}, ['75', '95'], 1, '85', Q),
    ('circ.cyclic_ext_equal', 'circ_cyclic_ext', {'angle': 80}, ['100', '80'], 0, '80', Q),
    ('circ.cyclic_parallel_equal', 'circ_cyclic_parallel', {'angle': 70}, ['110', '110'], 0, '70', Q),
    ('circ.cyclic_parallel_cointerior', 'circ_cyclic_parallel', {'angle': 70}, ['110', '110'], 1, '70', Q),
    ('circ.centre_cyclic_equal', 'circ_centre_cyclic', {'centre': 120}, ['60', '120'], 1, '60', Q),
    # 4x + 6 = 2x + 24 gives x = 9 and both angles 42; the right x is 25 (106 and 74)
    ('circ.cyclic_alg_equal', 'circ_cyclic_alg', {'a1': 4, 'b1': 6, 'a2': 2, 'b2': 24}, ['25', '106', '74'], 0, '9', V),
    ('circ.cyclic_alg_equal', 'circ_cyclic_alg', {'a1': 4, 'b1': 6, 'a2': 2, 'b2': 24}, ['25', '106', '74'], 1, '42', Q),
    ('circ.tangent_triangle_180', 'circ_tangent_triangle', {'angle': 60}, ['90', '30'], 1, '120', Q),
    ('circ.tangent_base_whole', 'circ_tangent_base', {'apex': 40}, ['70'], 0, '140', Q),
    ('circ.tangents_not_reflex', 'circ_tangents_reflex', {'angle': 60}, ['240'], 0, '120', Q),
    ('circ.centre_both_whole', 'circ_centre_both', {'centre': 130}, ['25', '65'], 0, '50', Q),
    ('circ.centre_both_arc', 'circ_centre_both', {'centre': 130}, ['25', '65'], 1, '115', Q),
    ('circ.centre_minor_whole', 'circ_centre_minor', {'centre': 130}, ['25', '115'], 0, '50', Q),
    ('circ.centre_minor_arc', 'circ_centre_minor', {'centre': 130}, ['25', '115'], 1, '65', Q),
    ('circ.both_arcs_swapped', 'circ_both_arcs', {'centre': 80}, ['40', '140'], 0, '140', Q),
    ('circ.both_arcs_swapped', 'circ_both_arcs', {'centre': 80}, ['40', '140'], 1, '40', Q),
    ('circ.both_arcs_sum_swapped', 'circ_both_arcs_sum', {'centre': 110}, ['55', '125', '180'], 1, '55', Q),
    ('circ.reflex_half_arc', 'circ_reflex_half', {'reflex': 250}, ['125'], 0, '55', Q),     # (360 - 250) / 2
    ('circ.isos_same_seg_whole', 'circ_isos_same_seg', {'angle': 42}, ['69', '42'], 0, '138', Q),
    ('circ.alt_straight_supplement', 'circ_alt_straight', {'angle': 65}, ['65', '115'], 0, '115', Q),
    ('circ.same_seg2_swapped', 'circ_same_seg2', {'a': 46, 'b': 21}, ['46', '21'], 0, '21', Q),
    ('circ.alt_triangle_missed', 'circ_alt_triangle', {'angle': 50, 'bac': 34}, ['50', '96'], 1, ('130', '146'), Q),
    ('circ.two_tangents_missed', 'circ_two_tangents', {'p': 80}, ['100'], 0, ('190', '280'), Q),
    ('circ.secants_added', 'circ_secants', {'far': 120, 'near': 20}, ['50'], 0, '70', Q),
    ('circ.chords_subtracted', 'circ_chords_angle', {'arc1': 80, 'arc2': 60}, ['70'], 0, '10', Q),
    ('circ.three_whole', 'circ_three', {'centre': 110}, ['35', '55', '55', 'pick|1|c1'], 0, '70', Q),
    ('circ.three_doubled', 'circ_three', {'centre': 110}, ['35', '55', '55', 'pick|1|c1'], 1, '220', Q),
    ('circ.isos_apex_one_base', 'ang_isos_apex', {'base': 30}, ['120'], 0, '150', Q),
    ('circ.chord_half', 'circ_chord_length', {'r': 25, 'd': 23}, ['19.6'], 0, '9.8', R2DP),   # 2 root 96 = 19.60
    ('circ.tangent_length_added', 'circ_tangent_length', {'r': 5, 'ot': 15}, ['14.14'], 0, '15.81', R2DP),
    ('circ.radius_wrong_ratio', 'circ_radius_from_angle', {'apb': 120, 'po': 13}, ['11.26'], 0, '6.5', R2DP),
    # ---- similarity ------------------------------------------------------------------------------------------------
    ('sim.length_squared', 'sim_scale_length', {'k': 2, 'length': 18}, ['36'], 0, '72', L),
    ('sim.length_divided', 'sim_scale_length', {'k': 2, 'length': 18}, ['36'], 0, '9', L),
    ('sim.area_k_power', 'sim_area_k', {'k': 4, 'area': 15}, ['240'], 0, ('60', '960'), V),
    ('sim.area_down_power', 'sim_area_down', {'k': 3, 'area': 180}, ['20'], 0, '60', V),
    ('sim.vol_k_power', 'sim_vol_k', {'k': 3, 'vol': 20}, ['540'], 0, ('60', '180'), V),
    ('sim.area_ratio_power', 'sim_area_ratio', {'r_from': 5, 'r_to': 3, 'area': 125}, ['45'], 0, ('75', '27'), V),
    ('sim.vol_lengths_power', 'sim_vol_from_lengths', {'l_small': 4, 'l_large': 6, 'vol': 20}, ['67.5'], 0,
     ('30', '45'), V),
    ('sim.dim_not_rooted', 'sim_dim_from_vol', {'v_small': 8, 'v_large': 27, 'dim_small': 2}, ['3'], 0, '6.75', L),
    ('sim.sf_inverted', 'sim_sf', {'small': 4, 'large': 6}, ['3/2'], 0, '2/3', V),
    ('sim.tri_angles_360', 'sim_tri_angles', {'a': 50, 'b': 60}, ['70', '50', '60', '70'], 0, '250', Q),
    ('sim.tri_angles_sum', 'sim_tri_angles', {'a': 50, 'b': 60}, ['70', '50', '60', '70'], 3, '110', Q),
    ('sim.quad_angles_sum', 'sim_quad_angles', {'a': 85, 'b': 110, 'c': 75}, ['90', '85', '110', '75', '90'], 0, '270', Q),
    ('sim.overlap_inverted', 'sim_overlap', {'ab': 6, 'ad': 4, 'ac': 9, 'ae': 6}, ['2', '3', '3/2'], 2, '2/3', V),
    ('sim.parallel_part', 'sim_parallel', {'ad': 3, 'db': 6, 'de': 5}, ['15'], 0, '10', L),
    ('sim.bpt_part', 'sim_bpt', {'ad': 3, 'db': 5, 'ac': 16}, ['6', '10'], 0, '9.6', L),
    ('sim.bpt_part', 'sim_bpt', {'ad': 3, 'db': 5, 'ac': 16}, ['6', '10'], 1, '6.4', L),
    # (x + 2) / (2x - 1) = 6 / 9 gives x = 8; with the ratio the other way up (x + 2) x 6 = (2x - 1) x 9 gives x = 7/4
    ('sim.alg_prop_inverted', 'sim_alg_prop', {'a1': 1, 'b1': 2, 'a2': 2, 'b2': -1, 'top': 6, 'bottom': 9}, ['8'], 0,
     '1.75', V),
    ('sim.chain_one_step', 'sim_chain', {'r1': 2, 'r2': 3, 'r3': 3, 'r4': 5, 'side': 4}, ['10'], 0, '6', L),
    ('sim.frustum_whole', 'sim_frustum', {'height': 12, 'radius': 9, 'cut': 4}, ['312'], 0, '324', V),
    ('sim.quad_prop_inverted', 'sim_quad_prop', {'xy': 4, 'add_qr': 6, 'add_yz': 2}, ['6', '3/2'], 1, '2/3', V),
    ('sim.shadow_inverted', 'sim_shadow', {'h1': 2, 's1': 5, 's2': 20}, ['8'], 0, '0.5', L),
    ('sim.shadow_additive', 'sim_shadow', {'h1': 2, 's1': 5, 's2': 20}, ['8'], 0, '17', L),
    ('sim.sides_additive', 'sim_sides', {'known_new': 12, 'known_old': 8, 'others': [14]}, ['21'], 0, '18', L),
    ('sim.sides_inverted', 'sim_sides', {'known_new': 15, 'known_old': 10, 'others': [12]}, ['18'], 0, '8', L),
    ('sim.bisector_swapped', 'sim_bisector', {'ab': 9, 'ac': 6, 'bc': 10}, ['6', '4'], 0, '4', L),
    ('sim.cone_power', 'sim_cone_scale', {'r_small': 3, 'r_large': 6, 'vol': 10, 'sa': 18}, ['80', '72'], 0,
     ('40', '20'), V),
    ('sim.cone_power', 'sim_cone_scale', {'r_small': 3, 'r_large': 6, 'vol': 10, 'sa': 18}, ['80', '72'], 1,
     ('144', '36'), V),
    ('sim.model_not_converted', 'sim_model', {'scale': 200, 'vol_cm3': 500, 'flr_cm2': 3}, ['4000', '12'], 0,
     '4000000000', V),
    ('sim.model_power', 'sim_model', {'scale': 200, 'vol_cm3': 500, 'flr_cm2': 3}, ['4000', '12'], 0, '20', V),
    ('sim.vol_sa_not_rooted', 'sim_vol_sa', {'sa_small': 80, 'sa_large': 180, 'vol': 40}, ['1.5', '135'], 0, '2.25', V),
    ('sim.vol_sa_power', 'sim_vol_sa', {'sa_small': 80, 'sa_large': 180, 'vol': 40}, ['1.5', '135'], 1, '90', V),
    ('sim.map_not_converted', 'sim_map_length', {'scale': 50000, 'map_cm': 4, 'unit_word': 'km'}, ['2'], 0, '200000', L),
    ('sim.map_divided', 'sim_map_length', {'scale': 50000, 'map_cm': 4, 'unit_word': 'km'}, ['2'], 0, '0.00008', L),
    ('sim.map_area_linear', 'sim_map_area', {'scale': 25000, 'map_cm2': 8}, ['0.5'], 0, '2', V),
    # ---- ratio and proportion --------------------------------------------------------------------------------------
    # review: 81 in 3:2:4 shared equally is 27, which is also the first share, so that example is silent now; 84 in 3:2:7
    # gives 21, 14, 49 and 28 each when shared equally
    ('ratio.ratio_share_equal', 'ratio_share', {'total': 84, 'parts': [3, 2, 7]}, ['21', '14', '49'], 1, '28', V),
    ('ratio.ratio_share_swapped', 'ratio_share', {'total': 81, 'parts': [3, 2, 4]}, ['27', '18', '36'], 0, '36', V),
    # 540 in 5:3:4 gives 225, 135, 180; soil, compost, sand; the boxes are compost, sand, soil minus sand. (Review: 540
    # shared equally is 180, the sand box's answer, so the equal-share example uses 660 in 6:3:2: 360, 180, 120; 220 each.)
    ('ratio.ratio_garden_equal', 'ratio_garden', {'total': 660, 'parts': [6, 3, 2]}, ['180', '120', '240'], 0, '220', V),
    ('ratio.ratio_garden_swapped', 'ratio_garden', {'total': 540, 'parts': [5, 3, 4]}, ['135', '180', '45'], 1, '225', V),
    # 480 in 5:3:4 gives 200, 120, 160
    ('ratio.ratio_share_diff_equal', 'ratio_share_diff', {'total': 480, 'parts': [5, 3, 4]}, ['200', '120', '80'], 1,
     '160', V),
    ('ratio.ratio_share_diff_swapped', 'ratio_share_diff', {'total': 480, 'parts': [5, 3, 4]}, ['200', '120', '80'], 2,
     '40', V),
    # 1200 in 5:3:2: one part 120, shares 600, 360, 240 (review: 600 in 3:2:1 made both slips another box's answer)
    ('ratio.ratio_prize_equal', 'ratio_prize', {'total': 1200, 'parts': [5, 3, 2]}, ['120', '600', '360'], 0, '400', V),
    ('ratio.ratio_prize_swapped', 'ratio_prize', {'total': 1200, 'parts': [5, 3, 2]}, ['120', '600', '360'], 1, '240', V),
    # 600 in 1:3:2: shares 100, 300, 200; meals in euros at 1.2 is 120
    # 900 in 2:5:2: meals 200, activities 500, souvenirs 200; 300 each when shared equally
    ('ratio.ratio_holiday_equal', 'ratio_holiday', {'budget': 900, 'parts': [2, 5, 2], 'rate': 1.2}, ['500', '200', '240'],
     0, '300', V),
    ('ratio.ratio_holiday_swapped', 'ratio_holiday', {'budget': 600, 'parts': [1, 3, 2], 'rate': 1.2},
     ['300', '200', '120'], 1, '100', V),
    ('ratio.ratio_concert_equal', 'ratio_concert',
     {'total': 440, 'parts': [3, 2], 'adult_price': 12, 'child_price': 6}, ['264', '176', '4224'], 0, '220', V),
    ('ratio.ratio_concert_swapped', 'ratio_concert',
     {'total': 440, 'parts': [3, 2], 'adult_price': 12, 'child_price': 6}, ['264', '176', '4224'], 0, '176', V),
    # class A 60 in 2:3 (24 boys, 36 girls), class B 80 in 6:4 (48 boys, 32 girls); review: 72 in 4:2 made the boys of A
    # equal to the boys of B, the other box's answer
    ('ratio.merge_swapped', 'ratio_merge', {'students_a': 60, 'a_parts': [2, 3], 'students_b': 80, 'b_parts': [6, 4]},
     ['36', '48', '18:17'], 0, '24', V),
    ('ratio.merge_swapped', 'ratio_merge', {'students_a': 60, 'a_parts': [2, 3], 'students_b': 80, 'b_parts': [6, 4]},
     ['36', '48', '18:17'], 1, '32', V),
    ('ratio.hike_not_converted', 'ratio_hike', {'scale': 50000, 'cm1': 8, 'cm2': 3.8}, ['4000', '1900', '5.9'], 0,
     '400000', V),
    ('ratio.hike_divided', 'ratio_hike', {'scale': 50000, 'cm1': 8, 'cm2': 3.8}, ['4000', '1900', '5.9'], 0, '0.00016', V),
    ('prop.plumbers_direct', 'prop_plumbers', {'w1': 5, 'h1': 12, 'w2': 12, 'h3': 6}, ['60', '5', '10'], 1, '28.8', V),
    ('prop.plumbers_direct', 'prop_plumbers', {'w1': 5, 'h1': 12, 'w2': 12, 'h3': 6}, ['60', '5', '10'], 2, '2.5', V),
    ('fdp.dec_pct_swapped', 'fdp_dec_and_pct', {'a': 2, 'b': 5}, ['0.4', '40'], 0, '40', V),
    ('fdp.pct_decimal', 'fdp_dec_and_pct', {'a': 2, 'b': 5}, ['0.4', '40'], 1, '0.4', V),
    ('fdp.dec_inverted', 'fdp_dec_and_pct', {'a': 2, 'b': 5}, ['0.4', '40'], 0, '2.5', V),
    # ---- angles in plane figures -----------------------------------------------------------------------------------
    ('ang.kite_one_equal', 'ang_kite', {'a': 78, 'b': 56}, ['170', '56'], 0, '226', Q),            # 360 - 78 - 56
    ('ang.isos_parallel_one_base', 'ang_isos_parallel', {'base': 53}, ['74', '53'], 0, '127', Q),
    ('ang.isos_parallel_supplement', 'ang_isos_parallel', {'base': 53}, ['74', '53'], 1, '127', Q),
    ('poly.int_ext_swapped_interior', 'poly_int_ext', {'n': 12}, ['150', '30'], 0, '30', Q),
    ('poly.int_ext_swapped_exterior', 'poly_int_ext', {'n': 12}, ['150', '30'], 1, '150', Q),
    # (4x + 10) + (2x + 44) = 180 gives x = 21; with 90 it gives x = 6 and with 360 it gives x = 51
    ('ang.alg_wrong_total', 'ang_alg', {'rule_word': 'straight line', 'terms': [4, 10, 2, 44]}, ['21', '94', '86'], 0,
     ('6', '51'), V),
    # five angles total 540, so x = 70; with 900 it gives 160 and with 720 it gives 115
    ('poly.alg_wrong_sum', 'poly_alg', {'offsets': [20, 30, 50, 60], 'fixed': 100, 'sides': 5},
     ['70', '90', '100', '120', '130', '100'], 0, ('160', '115'), V),
    ('circ.semicircle_first_180', 'circ_semicircle', {'angle': 45}, ['45', '90'], 0, '135', Q),
    ('circ.semicircle_straight_box', 'circ_semicircle', {'angle': 45}, ['45', '90'], 1, '180', Q),
    # QR = 9 x 12 / 6 = 18; added 9 + 6 = 15; upside down 9 x 6 / 12 = 4.5; the angle scaled 50 x 2 = 100
    ('sim.fields_additive', 'sim_fields', {'ab': 6, 'bc': 9, 'pq': 12, 'ang_b': 50}, ['18', '50'], 0, '15', L),
    ('sim.fields_inverted', 'sim_fields', {'ab': 6, 'bc': 9, 'pq': 12, 'ang_b': 50}, ['18', '50'], 0, '4.5', L),
    ('sim.fields_angle_scaled', 'sim_fields', {'ab': 6, 'bc': 9, 'pq': 12, 'ang_b': 50}, ['18', '50'], 1, '100', Q),
    ('circ.cyclic3_equal', 'circ_cyclic3', {'a1': 46, 'a2': 35}, ['134', '145', '92'], 0, '46', Q),
    ('circ.cyclic3_equal', 'circ_cyclic3', {'a1': 46, 'a2': 35}, ['134', '145', '92'], 1, '35', Q),
    ('circ.cyclic3_centre', 'circ_cyclic3', {'a1': 46, 'a2': 35}, ['134', '145', '92'], 2, '46', Q),
    ('ang.turn_anticlockwise', 'ang_bearing_turn', {'b1': 34, 'turn': 91}, ['125', '89'], 0, '303', Q),     # 34 - 91 + 360
    ('circ.alt_segment_not_doubled', 'circ_alt_segment', {'alpha': 43}, ['43', '86'], 1, '43', Q),
    ('circ.alt_segment_supplement', 'circ_alt_segment', {'alpha': 43}, ['43', '86'], 0, '137', Q),
    ('circ.arcs_swapped', 'circ_arcs', {'centre': 130}, ['65', '115'], 0, '115', Q),
    ('circ.tangent_chord_missed', 'circ_tangent_chord', {'alpha': 60, 'beta': 32}, ['60', '88'], 1, ('120', '148'), Q),
    ('circ.tangent_chord_supplement', 'circ_tangent_chord', {'alpha': 60, 'beta': 32}, ['60', '88'], 0, '120', Q),
    # 3x + 1 = 2(x + 12) gives x = 23 (angles 70 and 35); halved the other way, 3x + 1 = (x + 12) / 2 gives x = 2
    ('circ.alg_halved', 'circ_alg', {'a': 3, 'b': 1, 'c': 1, 'd': 12}, ['23', '70', '35'], 0, '2', V),
    # ---- one-number circle and similarity families (batch 3) ----
    ('circ.centre_halved', 'circ_centre', {'angle': 40}, ['80'], 0, '20', Q),                 # centre angle is 2 x 40
    # chord 16 and 6 from the centre: half-chord 8, radius 10; the whole chord gives sqrt(256 + 36), the sum 8 + 6
    ('circ.chord_radius_whole', 'circ_chord_radius', {'chord': 16, 'd': 6}, ['10'], 0, '17.09', R2DP),
    ('circ.chord_radius_added', 'circ_chord_radius', {'chord': 16, 'd': 6}, ['10'], 0, '14', R2DP),
    ('circ.reflex_centre_only', 'circ_reflex', {'arc': 70}, ['220'], 0, '140', Q),            # 360 - 2 x 70 against 2 x 70
    # 12 scaled by (4 / 2)^2 = 48; to the power 1 it is 24, to the power 3 it is 96; the ratio upside down gives 12 / 4 = 3
    ('sim.area_scale_power', 'sim_area_scale', {'area': 12, 'p': 2, 'q': 4}, ['48'], 0, ('24', '96'), V),
    ('sim.area_scale_inverted', 'sim_area_scale', {'area': 12, 'p': 2, 'q': 4}, ['48'], 0, '3', V),
    ('sim.k_area_not_rooted', 'sim_k_from_area', {'large': 36, 'small': 4}, ['3'], 0, '9', V),   # 36 / 4 = 9, root 3
)

EXPR_TX_5B = (
    # 3 pens at p and 4 notebooks at n: 3p + 4n; the numbers matched to the other items 3n + 4p
    ('alg.form_cost_swapped', 'alg_form_expr', {'kind': 'cost', 'var1': 'p', 'var2': 'n', 'k1': 3, 'k2': 4}, '3p+4n', '3n+4p',
     'Write an expression for the total cost.'),
    # n + (n + 3) + 4n = 6n + 3; "times as old" as older: n + (n + 3) + (n + 4) = 3n + 7
    ('alg.form_times_as_more', 'alg_form_expr', {'kind': 'ages', 'var1': 'n', 'var2': '', 'k1': 3, 'k2': 4}, '6n+3', '3n+7',
     'Write an expression for the total of the three ages.'),
    # 2w + 2(w + 3) = 4w + 6; one width and one length: w + (w + 3) = 2w + 3
    ('alg.form_one_length', 'alg_form_expr', {'kind': 'perimeter', 'var1': 'w', 'var2': '', 'k1': 3, 'k2': 0}, '4w+6', '2w+3',
     'Write an expression for the perimeter of the rectangle.'),
)
DERIVE_TX_5B = (
    ('substitute', r'If \( x = -2 \), find the value of \( 2x^2 - 4x + 7 \).', ('gr_subst', {'e': '2x^2 - 4x + 7', 'x': '-2'})),
    ('substitute', r'Using \(s = vt\), find \(s\) when \(v = 11\) and \(t = 5\).', ('sub_formula', {'form': 'vt', 'v': '11', 't': '5'})),
    ('substitute', r'Using \(v = u + at\), find \(v\) when \(u = 8\), \(a = 4\) and \(t = 5\).',
     ('sub_formula', {'form': 'u+at', 'u': '8', 'a': '4', 't': '5'})),
    ('fn_eval', r'A function is defined by \(f(x) = 5x + 3\) . Find \(f(5)\) .', ('gr_subst', {'e': '5x + 3', 'x': '5'})),
    ('fn_eval', r'If \(f(x) = x^2 + x - 1\) , find \(f(4)\) .', ('gr_subst', {'e': 'x^2 + x - 1', 'x': '4'})),
    ('fn_eval', r'\(f(x) = 4x + 5\) and \(g(x) = 2x + 3\). Find \(f(g(3))\) .', ('fn_comp', {'f': '4x + 5', 'g': '2x + 3', 'x': '3'})),
    ('fn_eval', r'\(f(x) = 4x + 4\). Find \(f(f(3))\) (apply \(f\) twice).', ('fn_twice', {'f': '4x + 4', 'x': '3'})),
    ('fn_machine', r'A function machine applies +1 then ×5 . The input is 1 . What is the output?',
     ('fn_machine', {'a': '+', 'p': '1', 'b': '*', 'q': '5', 'v': '1'})),
    ('fn_machine', r'A function machine applies ×2 then +5 . The output is 11 . What was the input ?',
     ('fn_machine_back', {'a': '*', 'p': '2', 'b': '+', 'q': '5', 'v': '11'})),
    ('fn_inverse_eval', r'\(f(x) = 3x + 6\). The output is 18 . What was the input ? (Use \(f^{-1}\).)',
     ('fn_inverse_lin', {'a': 3, 'b': 6, 'y': '18'})),
    ('fn_solve', r'\(f(x) = 4x + 6\) and \(f(x) = 30\) . Find \(x\) .', ('fn_inverse_lin', {'a': 4, 'b': 6, 'y': '30'})),
    ('seq_special', 'Write down the 9th square number.', ('seq_special', {'k': 'square', 'n': 9})),
    ('seq_special', 'The triangle numbers are 1, 3, 6, 10, 15, ... Find the 12th triangle number.',
     ('seq_special', {'k': 'triangle', 'n': 12})),
    ('seq_special', 'The sequence of odd numbers starts: 1, 3, 5, 7, 9, ... Find the 16th odd number.',
     ('seq_special', {'k': 'odd', 'n': 16})),
    ('gr_parallel', 'A line is parallel to y = −2x − 3. What is its gradient?', ('gr_parallel', {'m': -2, 'c': -3})),
    ('gr_parallel', 'A line is parallel to y = x − 4. What is its gradient?', ('gr_parallel', {'m': 1, 'c': -4})),
    ('gr_parallel', 'A line is parallel to y = −x. What is its gradient?', ('gr_parallel', {'m': -1, 'c': 0})),
    ('gr_speed', 'The distance‑time graph below shows a hiker travelling 48 km in 2 hours at a constant speed. Find its speed.',
     ('gr_speed', {'d': '48', 't': '2'})),
)
DERIVE_TX_5B = DERIVE_TX_5B + (
    ('seq_sum_arith', 'Find the sum of the first 17 terms of the arithmetic sequence with first term 8 and common difference 4.',
     ('seq_sum_arith', {'n': '17', 'a': '8', 'd': '4'})),
    ('seq_rows', 'A theatre has 20 rows of seats. The first row has 23 seats and each subsequent row has 3 more seats than the row '
     'in front. Find the total number of seats in the theatre.', ('seq_sum_arith', {'n': '20', 'a': '23', 'd': '3'})),
    ('seq_mean', r'An arithmetic sequence has first term 5, common difference 4, and 32 terms. Show that the mean of the sequence '
     r'equals \(\dfrac{a+l}{2}\) and find the mean.', ('seq_mean', {'a': '5', 'd': '4', 'n': '32'})),
    ('seq_geometric', 'A geometric sequence has first term 2 and common ratio 3. Find the 9th term.',
     ('seq_geo_nth', {'a': '2', 'r': '3', 'n': '9'})),
    ('seq_u_n', r'The nth term of a sequence is \(u_n = 2n^2 + 3n\) (a) Find \(u_{14}\) (b) Show that the second difference is '
     r'constant and state its value. Enter your answer to part (a).', ('gr_subst', {'e': '2x^2 + 3x', 'x': '14'})),
)
DERIVE_NONE_5B = (
    ('seq_geometric', 'Find the sum of the first 10 terms of the arithmetic series with first term 2 and common difference 3.'),
    ('seq_mean', 'An arithmetic sequence has 32 terms. Find the mean.'),
    ('fn_eval', r'\(f(x) = 2x + 3\). Find \(f(1)\) and \(f(5)\) .'),
    ('fn_eval', r'\(f(x) = 2x - 2\). Find \(f(0) + f(3)\) .'),
    ('fn_eval', r'\(f(x) = 2x + 3\). Find \(f(g(2))\) .'),
    ('substitute', r'Using the formula \(v = u + at\), find \(t\) when \(v = 10\), \(u = 2\), \(a = 8\).'),
    ('substitute', r'If \( x = 3 \), find the value of \( y \).'),
    ('fn_solve', r'\(f(x) = x^2 - 8x + 15\). Solve \(f(x) = 0\) .'),
    ('fn_machine', 'A function machine applies ×2 then +5 . What is the output?'),
    ('seq_special', 'Find the 5th prime number.'),
    ('gr_parallel', 'A line is parallel to the line through (1, 2) and (3, 4). What is its gradient?'),
    ('gr_speed', 'A car travels 40 km in 2 hours. Find its speed.'),
)

PAIR_TX_5B = (
    ('num.error_full_unit', 'num_error_interval', {'value': 16.6, 'unit': 0.1}, 'number_pair', '16.55|16.65', '16.5|16.7', V),
    # (15 +- 0.5) by (8 +- 0.5) gives 108.75 to 131.75; with a whole unit either side it gives 98 to 144
    ('num.bounds_area_full_unit', 'num_bounds_area', {'length': 15, 'width': 8, 'unit': 1}, 'number_pair',
     '108.75|131.75', '98|144', V),
    ('num.bounds_product_full_unit', 'num_bounds_product', {'a': 36, 'b': 24, 'unit': 1}, 'number_pair',
     '834.25|894.25', '805|925', V),
    # 44 g and 9 cm3 to the nearest 2: 43 / 10 and 45 / 8; matched the other way, 43 / 8 and 45 / 10
    ('num.bounds_density_matched', 'num_bounds_density', {'mass': 44, 'volume': 9, 'unit': 2}, 'number_pair',
     '4.3|5.625', '5.375|4.5', V),
    ('num.share_ratio_swapped', 'num_share_ratio', {'total': 105, 'r1': 2, 'r2': 3}, 'number_pair', '42|63', '63|42', V),
    ('num.share_ratio_equal', 'num_share_ratio', {'total': 105, 'r1': 2, 'r2': 3}, 'number_pair', '42|63', '52.5|52.5', V),
    # (-2)(3, -1) = (-6, 2); the signs kept gives (6, -2)
    ('vec.scale_sign_kept', 'vec_scale', {'k': -2, 'v0': 3, 'v1': -1}, 'vector', '-6|2', '6|-2', V),
)

# (rule id, family, inputs, answer type, key, typed, question)
SCALAR_TX_5B = (
    ('num.scale_pow10_direction', 'num_scale_pow10', {'n': 69.766, 'op': 'multiply', 'p': 1000}, 'number', '69766', '0.069766', V),
    ('num.scale_pow10_direction', 'num_scale_pow10', {'n': 164.59, 'op': 'divide', 'p': 10}, 'number', '16.459', '1645.9', V),
    ('mf.multiple_added', 'mf_multiple', {'n': 4, 'k': 6}, 'number', '24', '10', V),
    ('mf.hcf_lcm', 'num_hcf', {'a': 18, 'b': 48}, 'number', '6', '144', V),
    ('mf.lcm_hcf', 'num_lcm', {'a': 12, 'b': 18}, 'number', '36', '6', V),
    ('mf.lcm_product', 'num_lcm', {'a': 12, 'b': 18}, 'number', '36', '216', V),
    ('mf.count_hcf', 'mf_common_factor_count', {'a': 36, 'b': 48}, 'number', '6', '12', V),     # HCF 12 has 6 factors
    ('mf.hcf3_lcm', 'mf_hcf3', {'a': 12, 'b': 18, 'c': 30}, 'number', '6', '180', V),
    ('mf.hcf3_two_only', 'mf_hcf3', {'a': 12, 'b': 18, 'c': 35}, 'number', '1', '6', V),
    ('mf.lcm3_hcf', 'mf_lcm3', {'a': 4, 'b': 6, 'c': 10}, 'number', '60', '2', V),
    ('mf.lcm3_two_only', 'mf_lcm3', {'a': 4, 'b': 6, 'c': 10}, 'number', '60', '12', V),
    ('mf.other_lcm_only', 'mf_other_number', {'hcf': 9, 'lcm': 324, 'known': 81}, 'number', '36', '4', V),
    # 8.6 - 3.95 lined up on the right is 8.06 - 3.95
    ('dec.directed_not_aligned', 'num_directed', {'a': 8.6, 'op': '-', 'b': 3.95}, 'number', '4.65', '4.11',
     'Find the difference between 8.6 and 3.95.'),
    ('dec.arith_not_aligned', 'arith', {'expr': '4.36 + 3.03 + 8.6'}, 'number', '15.99', '15.45', 'Calculate 4.36 + 3.03 + 8.6'),
    ('num.place_value_digit_face', 'num_place_value_digit', {'number': 8467, 'digit': 4}, 'number', '400', '4', V),
    ('num.decimal_place_next', 'num_decimal_place', {'number': 2.127, 'position': 'hundredths'}, 'number', '2', '7', V),
    ('num.standard_form_sign', 'num_from_standard_form', {'coef': 7.3, 'power': -3}, 'number', '0.0073', '7300', V),
    ('num.recurring_terminating', 'num_recurring_text', {'dec': '0.666\u2026'}, 'fraction', '2/3', '3/5', V),
    # ---- mensuration and shapes (batch 3), worked with pi to 2 decimal places ----
    ('mens.cyl_hemisphere_whole', 'mens_cyl_hemisphere', {'r': 3, 'h': 4}, 'number', '169.65', '226.19', R2DP),  # 54pi against 72pi
    # right-angled ends 3, 4 and hypotenuse 5: 12 + 12 x 10 = 132; faces 3 x 10 + 4 x 10 only gives 12 + 70 = 82
    ('mens.tri_prism_face_missed', 'mens_tri_prism_sa', {'a': 3, 'b': 4, 'length': 10}, 'number', '132', '82', V),
    ('mens.tri_prism_end_once', 'mens_tri_prism_sa', {'a': 3, 'b': 4, 'length': 10}, 'number', '132', '126', V),  # 6 + 120
    # r cubed is 27.0, so r = 3 and the cube is 27; the square root of 27 is 5.2
    ('mens.sphere_radius_no_root', 'mens_sphere_radius_from_volume', {'vol': 113.1}, 'number', '3', ('27', '5.2'), R2DP),
    ('mens.hemi_cone_height', 'mens_hemi_cone_sa', {'r': 3, 'h': 4}, 'number', '103.67', '94.25', R2DP),     # 33pi against 30pi
    ('mens.submerged_not_divided', 'mens_submerged_rise', {'sphere_r': 6, 'cyl_r': 9}, 'number', '3.56', '904.78', R2DP),
    ('mens.cyl_mass_formula', 'mens_cyl_mass', {'density': 2, 'r': 3, 'h': 5}, 'number', '282.74', ('70.69', '141.37'), R2DP),
    ('mens.segment_sector_only', 'mens_segment_60', {'r': 6}, 'number', '3.26', '18.85', R2DP),     # 6pi - 9 sqrt3 against 6pi
    ('mens.segment_added', 'mens_segment_60', {'r': 6}, 'number', '3.26', '34.44', R2DP),          # 6pi + 9 sqrt3
    # rectangle 12 plus triangle 4 over length 5 is 80; a triangle drawn as a rectangle gives 100; the area alone is 16
    ('mens.prism_compound_rectangle', 'mens_prism_compound', {'a': 4, 'h': 3, 'b': 2, 'length': 5}, 'number', '80', '100', V),
    ('mens.prism_compound_area', 'mens_prism_compound', {'a': 4, 'h': 3, 'b': 2, 'length': 5}, 'number', '80', '16', V),
    ('pyth.cut_corner_full', 'pyth_cut_corner', {'length': 10, 'width': 8, 'slope': 5, 'cut': 3}, 'number', '74', '68', V),
    ('trig.area_side_half', 'trig_area_side', {'a': 8, 'angle': 30, 'area': 10}, 'number', '5', '2.5', R2DP),
    ('brg.meeting_difference', 'brg_meeting', {'sep': 100, 'v1': 15, 'v2': 25}, 'number', '2.5', '10', R2DP),
    ('loci.chord_midpoint_added', 'loci_chord_midpoint', {'radius': 13, 'chord': 10}, 'number', '12', '13.9', R1DP),
    ('loci.chord_midpoint_whole', 'loci_chord_midpoint', {'radius': 13, 'chord': 10}, 'number', '12', '8.3', R1DP),
    ('loci.sector_whole', 'loci_sector', {'angle': 90, 'radius': 4}, 'number', '12.57', '50.27', R2DP),   # 4pi against 16pi
    ('loci.sector_arc', 'loci_sector', {'angle': 90, 'radius': 4}, 'number', '12.57', '6.28', R2DP),       # 2pi
    ('loci.scale_area_linear', 'loci_scale_area', {'scale': 10, 'map_cm2': 5, 'unit_word': 'cm\u00b2'}, 'number', '500', '50', V),
    ('loci.scale_down_units', 'loci_scale_down', {'scale': 25000, 'dist_km': 5}, 'number', '20', ('0.2', '0.0002'), V),
    ('loci.scale_down_direction', 'loci_scale_down', {'scale': 25000, 'dist_km': 5}, 'number', '20', '12500000000', V),
    ('vec.parallel_t_inverted', 'vec_parallel_t', {'a0': 4, 'a1': 2, 'b0': 10}, 'number', '5', '20', V),
    ('vec.parallel_t_additive', 'vec_parallel_t', {'a0': 4, 'a1': 2, 'b0': 10}, 'number', '5', '8', V),
    ('vec.parallel_k_inverted', 'vec_parallel_k', {'a0': 2, 'a1': 5, 'b0': 8, 'b1': 20}, 'number', '4', '0.25', V),
    ('vec.parallel_k_additive', 'vec_parallel_k', {'a0': 2, 'a1': 5, 'b0': 8, 'b1': 20}, 'number', '4', '6', V),
    # A at 0 degrees 6 km, B at 60 degrees 10 km: AB^2 = 36 + 100 - 120 x 0.5 = 76
    ('brg.ship_ab_sides_added', 'brg_two_ships', {'b1': 0, 'd1': 6, 'b2': 60, 'd2': 10, 'want': ('ab',)}, 'number', '8.72', '16', R2DP),
    ('brg.ship_ab_pythagoras', 'brg_two_ships', {'b1': 0, 'd1': 6, 'b2': 60, 'd2': 10, 'want': ('ab',)}, 'number', '8.72', '11.66', R2DP),
)

# the one-number copies of the part rules are the same slips; each is run on the single box of its part example
_SCALAR_DUAL = ('circ_tangent_length', 'circ_two_tangents', 'sim_area_k', 'sim_map_length')
# asked only as a plain number: the rules keep their ids and the part form does not exist
_SCALAR_ONLY = ('circ_centre', 'circ_chord_radius', 'circ_reflex', 'sim_area_scale', 'sim_k_from_area')
SCALAR_TX_5B = SCALAR_TX_5B + tuple(
    (rid + ('_s' if fam in _SCALAR_DUAL else ''), fam, inputs, 'number', keys[0], typed, question)
    for rid, fam, inputs, keys, box, typed, question in PART_TX_5B
    if (fam in _SCALAR_DUAL or fam in _SCALAR_ONLY) and len(keys) == 1)
PART_TX_5B = tuple(row for row in PART_TX_5B if row[1] not in _SCALAR_ONLY)

# ---- read from the question (DERIVE parsers): substitution, functions, sequences, graphs ----
SCALAR_TX_5B = SCALAR_TX_5B + (
    # v = u + at with u = 8, a = 4, t = 5 is 8 + 20 = 28; reading "at" as a + t gives 8 + 4 + 5 = 17
    ('sub.formula_letters_added', 'sub_formula', {'form': 'u+at', 'u': 8, 'a': 4, 't': 5}, 'number', '28', '17', V),
    # y = 5x + 5 at x = -2 is -5; "5x" as 5 + x gives 5 - 2 + 5 = 8.  y = 6x at x = 3 is 18; 63 side by side, 6 + 3 = 9 added
    ('sub.coefficient_implied', 'gr_subst', {'e': '5x + 5', 'x': '-2'}, 'number', '-5', '8', V),
    ('sub.coefficient_implied', 'gr_subst', {'e': '6x', 'x': '3'}, 'number', '18', ('63', '9'), V),
    ('sub.divide_multiplied', 'gr_subst', {'e': '12/x', 'x': '4'}, 'number', '3', '48', V),
    # f(g(3)): g(3) = 9, f(9) = 41; the other way round f(3) = 17, g(17) = 37
    ('fn.comp_wrong_order', 'fn_comp', {'f': '4x + 5', 'g': '2x + 3', 'x': 3}, 'number', '41', '37', V),
    # f(3) = 16, f(16) = 68; applied once it is 16, doubled it is 32
    ('fn.twice_applied_once', 'fn_twice', {'f': '4x + 4', 'x': 3}, 'number', '68', ('16', '32'), V),
    ('fn.machine_swapped', 'fn_machine', {'a': '+', 'p': 1, 'b': '*', 'q': 5, 'v': 1}, 'number', '10', '6', V),   # 1 x 5 + 1
    # output 11 from x2 then +5: (11 - 5) / 2 = 3; 11 / 2 - 5 = 0.5; 11 x 2 + 5 = 27
    ('fn.machine_back_order', 'fn_machine_back', {'a': '*', 'p': 2, 'b': '+', 'q': 5, 'v': 11}, 'number', '3', ('0.5', '27'), V),
    # 3x + 6 = 18 gives x = 4; (18 + 6) / 3 = 8; 18 / 3 - 6 = 0
    ('fn.inverse_wrong_way', 'fn_inverse_lin', {'a': 3, 'b': 6, 'y': 18}, 'number', '4', ('8', '0'), V),
    ('seq.square_doubled', 'seq_special', {'k': 'square', 'n': 9}, 'number', '81', '18', V),
    ('seq.triangle_not_halved', 'seq_special', {'k': 'triangle', 'n': 12}, 'number', '78', '156', V),     # 12 x 13
    ('seq.odd_parity', 'seq_special', {'k': 'odd', 'n': 16}, 'number', '31', ('32', '33'), V),
    ('gr.parallel_intercept', 'gr_parallel', {'m': 2, 'c': 6}, 'number', '2', '6', V),
    ('gr.parallel_perpendicular', 'gr_parallel', {'m': 2, 'c': 6}, 'number', '2', '-0.5', V),
    ('gr.speed_multiplied', 'gr_speed', {'d': 48, 't': 2}, 'number', '24', '96', V),
)
SCALAR_TX_5B = SCALAR_TX_5B + (
    # 17 terms, a = 8, d = 4: 17/2 x (16 + 64) = 680; 17 steps instead of 16 gives 17/2 x (16 + 68) = 714; not halved, 1360
    ('seq.sum_extra_step', 'seq_sum_arith', {'n': 17, 'a': 8, 'd': 4}, 'number', '680', '714', V),
    ('seq.sum_not_halved', 'seq_sum_arith', {'n': 17, 'a': 8, 'd': 4}, 'number', '680', '1360', V),
    # 32 terms, a = 5, d = 4: last term 129, mean 67; 32 steps gives last term 133 and mean 69
    ('seq.mean_extra_step', 'seq_mean', {'a': 5, 'd': 4, 'n': 32}, 'number', '67', '69', V),
    # 2 x 3^8 = 13122; the ratio nine times gives 2 x 3^9 = 39366
    ('seq.geometric_power', 'seq_geo_nth', {'a': 2, 'r': 3, 'n': 9}, 'number', '13122', '39366', V),
)


# ---- Phase 5c (docs/GCSE_MATHS_HINTS.md, section 25): rounding, word problems, sequences, surds ----
Q_DP1 = 'Round 812.2411 to 1 decimal place.'
Q_TAXI = 'A taxi charges a £14 fixed fare plus £7 per mile. The total fare is £105. How many miles were travelled?'

SCALAR_TX_5B = SCALAR_TX_5B + (
    # 812.2411 to 1 decimal place is 812.2; to 1 significant figure it is 800. 577.6647 to 1 decimal place is 577.7; to 1 sf, 600
    ('num.round_dp_as_sf', 'num_round_dp', {'n': 812.2411, 'dp': 1}, 'number', '812.2', '800', Q_DP1),
    ('num.round_dp_as_sf', 'num_round_dp', {'n': 577.6647, 'dp': 1}, 'number', '577.7', '600', 'Round 577.6647 to 1 decimal place.'),
    # 76243 to 1 significant figure is 80000; the digit alone is 8
    # (no accuracy in the question text: the truth guard then compares exactly, which the mutation check needs)
    ('num.round_sf_zeros', 'num_round_sf', {'n': 76243, 'sf': 1}, 'number', '80000', '8', V),
    # 3^6 = 729; 729 / 3 = 243
    ('num.index_divided', 'num_find_index', {'base': 3, 'value': 729}, 'number', '6', '243', r'Find the value of \(n\) if \(3^{n} = 729\).'),
    # 8 integers from 12 sum to 12 + 13 + ... + 19 = 124; 124 / 8 = 15.5
    ('alg.consecutive_equal', 'consecutive_sum', {'n': 8, 'total': 124}, 'linear', '12', '15.5',
     r'The sum of 8 consecutive integers starting from \( x \) is 124. Find \( x \).'),
    # (105 - 14) / 7 = 13 miles; 105 / 7 = 15; (105 + 14) / 7 = 17; 105 - 14 = 91
    ('lin.fixed_ignored', 'linear_fixed_rate', {'fixed': 14, 'rate': 7, 'total': 105}, 'number', '13', '15', Q_TAXI),
    ('lin.fixed_added', 'linear_fixed_rate', {'fixed': 14, 'rate': 7, 'total': 105}, 'number', '13', '17', Q_TAXI),
    ('lin.cost_not_divided', 'linear_fixed_rate', {'fixed': 14, 'rate': 7, 'total': 105}, 'number', '13', '91', Q_TAXI),
    # 8x + 2 = 18 gives 2; 18 / 8 - 2 = 0.25; (18 + 2) / 8 = 2.5
    ('eq.think_undo_order', 'think_number', {'mult': 8, 'add': 2, 'result': 18}, 'linear', '2', '0.25',
     'I think of a number. I multiply it by 8 and add 2. The result is 18. What is the number?'),
    ('eq.think_wrong_inverse', 'think_number', {'mult': 8, 'add': 2, 'result': 18}, 'linear', '2', '2.5',
     'I think of a number. I multiply it by 8 and add 2. The result is 18. What is the number?'),
    # length 2w + 4, width w, perimeter 80: 2(3w + 4) = 80 gives w = 12; the perimeter taken as one length and one width: (80 - 4) / 3
    ('eq.perimeter_one_each', 'rect_perimeter_linear', {'k': 4, 'perimeter': 80}, 'linear', 'w=12', '25.33',
     r'A rectangle has length \(2\text{w} + 4\) and width \(\text{w}\). Its perimeter is 80 cm. Find \(w\).'),
    # 1, 1, 2, 3, 5 continues 8; the last gap (2) repeated gives 5 + 2 = 7
    ('seq.fibonacci_constant_step', 'seq_terms', {'t': [1, 1, 2, 3, 5], 'at': 5}, 'number', '8', '7',
     'A Fibonacci-type sequence starts: 1, 1, 2, 3, 5, ___ Find the next term.'),
    # 2 (3^10 - 1) / 2 = 59048; without the division by r - 1: 118096; the 10th term 2 x 3^9 = 39366
    ('seq.geometric_sum_unshared', 'seq_geo_sum', {'n': 10, 'a': 2, 'r': 3}, 'number', '59048', '118096', V),
    ('seq.geometric_sum_last_term', 'seq_geo_sum', {'n': 10, 'a': 2, 'r': 3}, 'number', '59048', '39366', V),
    # 5 / (1 - 1/4) = 20/3; divided by the ratio 5 / (1/4) = 20; 5 / (1 + 1/4) = 4
    ('seq.infinite_over_ratio', 'seq_geo_inf', {'a': 5, 'rn': 1, 'rd': 4}, 'number', '20/3', '20', V),
    # 7 / (1 + 1/3) = 21/4 (the 4 of a ratio of 1/4 is printed in its question, so this one uses a ratio of 1/3)
    ('seq.infinite_plus_ratio', 'seq_geo_inf', {'a': 7, 'rn': 1, 'rd': 3}, 'number', '21/2', '5.25', V),
    # 20 (6 + 120) / 2 = 1260; not halved 2520
    ('seq.sum_last_not_halved', 'seq_sum_last', {'a': 6, 'l': 120, 'n': 20}, 'number', '1260', '2520', V),
    # 294 + 8 x 30 = 534 in year 9; nine rises give 294 + 9 x 30 = 564
    ('seq.context_extra_step', 'seq_context', {'wage': 294, 'rise': 30, 'year': 9}, 'number', '534', '564', V),
    # x + 32 = 64 gives 32; the root dropped without squaring: 8 - 32 = -24; the 32 added instead: 64 + 32 = 96
    ('surd.equation_not_squared', 'surd_sqrt_eq', {'c': 32, 'r': 8}, 'number', '32', '-24', V),
    ('surd.equation_sign_moved', 'surd_sqrt_eq', {'c': 32, 'r': 8}, 'number', '32', '96', V),
    # sqrt(20) / sqrt(5) = sqrt(4) = 2; the root left off: 4
    ('surd.quotient_root_missed', 'surd_div', {'a': 20, 'b': 5}, 'number', '2', '4', V),
    # (3 + sqrt 7)(3 - sqrt 7) = 9 - 7 = 2; 9 + 7 = 16; the 3 not squared: 3 - 7 = -4
    ('surd.conjugate_sign', 'surd_conj', {'a': 3, 'b': 7}, 'number', '2', '16', V),
    ('surd.conjugate_unsquared', 'surd_conj', {'a': 3, 'b': 7}, 'number', '2', '-4', V),
    # (x + 5) + (3x + 15) + (2x + 70) = 6x + 90 = 180 gives x = 15; a total of 360 gives 6x = 270, so x = 45
    ('ang.sum_x_wrong_total', 'ang_sum_x', {'a': ['1', '3', '2'], 'b': ['5', '15', '70']}, 'linear', '15', '45', V),
)

DERIVE_TX_5B = DERIVE_TX_5B + (
    ('seq_geometric', 'Find the sum of the first 10 terms of the geometric series with first term 2 and common ratio 3.',
     ('seq_geo_sum', {'n': '10', 'a': '2', 'r': '3'})),
    ('seq_geometric_infinite', r'A geometric series has first term 5 and common ratio \(\dfrac{1}{4}\) Find the sum to infinity.',
     ('seq_geo_inf', {'a': '5', 'rn': '1', 'rd': '4'})),
    ('seq_sum_last', r'An arithmetic series has first term 6, last term 120, and 20 terms. (a) Derive the formula '
     r'\(S_n = \dfrac{n(a+l)}{2}\) by pairing terms. (b) Use the formula to find \(S_{20}\) Enter your answer to part (b).',
     ('seq_sum_last', {'a': '6', 'l': '120', 'n': '20'})),
    ('seq_context', 'A worker earns £294 in year 1. Each year their salary increases by £30. Write a formula for the salary in '
     r'year \(n\), then use it to find the salary in year 9. Enter the salary in year 9.',
     ('seq_context', {'wage': '294', 'rise': '30', 'year': '9'})),
    ('surd', r'Solve: \( \sqrt{x + 32} = 8 \)', ('surd_sqrt_eq', {'c': '32', 'r': '8'})),
    ('surd', r'Simplify: \( \dfrac{\sqrt{20}}{\sqrt{5}} \)', ('surd_div', {'a': '20', 'b': '5'})),
    ('surd', 'Expand and simplify (  3 + √7  )(  3 − √7  ).', ('surd_conj', {'a': '3', 'b': '7'})),
    ('angle_sum', r'The angles in a triangle are \(x + 5\)°, \(3x + 15\)°, and \(2x + 70\)°. Form an equation and find \(x\).',
     ('ang_sum_x', {'a': ['1', '3', '2'], 'b': ['5', '15', '70']})),
)
DERIVE_NONE_5B = DERIVE_NONE_5B + (
    ('seq_geometric_infinite', 'A geometric series has first term 5 and common ratio 0.5. Find the sum to infinity.'),
    ('seq_sum_last', 'An arithmetic series has 20 terms. Use the formula to find the sum.'),
    ('seq_context', 'A worker earns £294 in year 3. Each year their salary increases by £30. Enter the salary in year 9.'),
    ('surd', r'Solve: \( \sqrt{x - 3} = 4 \)'),
    ('surd', r'Simplify fully: \( \sqrt{50} + \sqrt{8} \)'),
    ('surd', 'Expand and simplify (  3 + √7  )(  4 − √7  ).'),
    ('surd', 'Expand and simplify (  5 + √3  )(  5 + √3  ).'),
    ('surd', r'Simplify: \( \dfrac{\sqrt{20}}{5} \)'),
    ('angle_sum', r'The angles in a triangle are \(x + 5\)° and \(3x + 15\)°. Find \(x\).'),
    ('angle_sum', r'The angles in a quadrilateral are \(x + 5\)°, \(3x + 15\)°, and \(2x + 70\)°. Find \(x\).'),
)


# ---- Phase 3 batch A (docs/GCSE_MATHS_VARIETY.md): fractions, interest, counting, ratio, forming equations ----
SCALAR_TX_5B = SCALAR_TX_5B + (
    # 1/3 + 1/4 = 7/12; the bottoms added gives 2/7
    ('frac.add_sub_denominators', 'frac_add_sub', {'n1': 1, 'd1': 3, 'op': '+', 'n2': 1, 'd2': 4}, 'fraction', '7/12', '2/7', V),
    # (2/3) / (4/5) = 5/6; multiplied as it stands, 8/15
    ('frac.mul_div_not_flipped', 'frac_mul_div', {'n1': 2, 'd1': 3, 'op': '/', 'n2': 4, 'd2': 5}, 'fraction', '5/6', '8/15', V),
    # 1 1/2 + 2 1/3 = 23/6; wholes dropped 1/2 + 1/3 = 5/6; bottoms added 3 + 2/5 = 17/5
    ('frac.mixed_wholes_dropped', 'frac_mixed_add_sub', {'w1': 1, 'n1': 1, 'd1': 2, 'op': '+', 'w2': 2, 'n2': 1, 'd2': 3},
     'fraction', '23/6', '5/6', V),
    ('frac.mixed_denominators_added', 'frac_mixed_add_sub', {'w1': 1, 'n1': 1, 'd1': 2, 'op': '+', 'w2': 2, 'n2': 1, 'd2': 3},
     'fraction', '23/6', '17/5', V),
    # 1 1/2 x 2 1/3 = 7/2; parts apart 2 + 1/6 = 13/6.  1 1/2 / 2 1/3 = 9/14; not flipped 7/2
    ('frac.mixed_mul_parts_separate', 'frac_mixed_mul_div', {'w1': 1, 'n1': 1, 'd1': 2, 'op': '*', 'w2': 2, 'n2': 1, 'd2': 3},
     'fraction', '7/2', '13/6', V),
    ('frac.mixed_mul_not_flipped', 'frac_mixed_mul_div', {'w1': 1, 'n1': 1, 'd1': 2, 'op': '/', 'w2': 2, 'n2': 1, 'd2': 3},
     'fraction', '9/14', '7/2', V),
    # 50 cm of 2 m: 50 / 200 = 1/4; upside down 4; units ignored 50 / 2 = 25
    ('frac.other_wrong_way_up', 'fdp_fraction_of_other', {'part': 50, 'whole': 2, 'scale': 100}, 'fraction', '1/4', '4', V),
    ('frac.other_units_differ', 'fdp_fraction_of_other', {'part': 50, 'whole': 2, 'scale': 100}, 'number', '0.25', '25', V),
    # 15 of 60 is 25%; the other way round 400
    ('pct.other_wrong_way_round', 'fdp_pct_of_other', {'part': 15, 'whole': 60}, 'number', '25', '400', V),
    # 18/24 = 3/4; the HCF 6 typed; only the top divided 3/24 = 1/8
    ('frac.hcf_fraction_hcf', 'mf_hcf_fraction', {'a': 18, 'b': 24}, 'fraction', '3/4', '6', V),
    ('frac.hcf_fraction_top_only', 'mf_hcf_fraction', {'a': 18, 'b': 24}, 'fraction', '3/4', '1/8', V),
    # 800 at 3% for 4 years: simple interest 96, total 896; compound interest 100.41; one year 24
    ('int.simple_compound', 'fdp_simple_interest', {'principal': 800, 'rate': 3, 'years': 4, 'ask': 'interest'},
     'number', '96', '100.41', V),
    ('int.simple_one_year', 'fdp_simple_interest', {'principal': 800, 'rate': 3, 'years': 4, 'ask': 'interest'},
     'number', '96', '24', V),
    ('int.simple_principal_missed', 'fdp_simple_interest', {'principal': 800, 'rate': 3, 'years': 4, 'ask': 'total'},
     'number', '896', '96', V),
    ('int.simple_total_for_interest', 'fdp_simple_interest', {'principal': 800, 'rate': 3, 'years': 4, 'ask': 'interest'},
     'number', '96', '896', V),
    # compound 100.41 less simple 96 is 4.41
    ('int.vs_compound_alone', 'fdp_simple_vs_compound', {'principal': 800, 'rate': 3, 'years': 4}, 'number', '4.41', '100.41', V),
    # next multiple of 7 above 50 is 56; the one below is 49
    ('mf.next_multiple_below', 'mf_next_multiple', {'n': 7, 'm': 50}, 'number', '56', '49', V),
    # 12 has 6 factors (1, 2, 3, 4, 6, 12); 1 and 12 left out gives 4; pairs give 3
    ('mf.factor_count_ends', 'mf_factor_count', {'n': 12}, 'number', '6', '4', V),
    ('mf.factor_count_pairs', 'mf_factor_count', {'n': 12}, 'number', '6', '3', V),
    # multiples of 6 from 20 to 100: 24 ... 96 is 13 of them; counting from zero gives 16
    ('mf.multiples_from_zero', 'mf_multiples_between', {'n': 6, 'lo': 20, 'hi': 100}, 'number', '13', '16', V),
    # 18 x 2 = 36; the number itself 18; the root of the square part, 3
    ('mf.square_multiplier_self', 'mf_square_multiplier', {'n': 18}, 'number', '2', '18', V),
    ('mf.square_multiplier_root', 'mf_square_multiplier', {'n': 18}, 'number', '2', '3', V),
    # 2^3 x 3^2: (3 + 1)(2 + 1) = 12; powers added 5; powers multiplied 6
    ('mf.primes_powers_added', 'mf_factor_count_primes', {'a1': 3, 'a2': 2, 'p3': 0, 'a3': 0}, 'number', '12', '5', V),
    ('mf.primes_powers_product', 'mf_factor_count_primes', {'a1': 3, 'a2': 2, 'p3': 0, 'a3': 0}, 'number', '12', '6', V),
    # reciprocal of 3/4 is 4/3; negated -3/4; unchanged 3/4
    ('num.reciprocal_neg', 'num_reciprocal', {'n': 3, 'd': 4}, 'fraction', '4/3', '-3/4', V),
    ('num.reciprocal_unchanged', 'num_reciprocal', {'n': 3, 'd': 4}, 'fraction', '4/3', '3/4', V),
    # 3 x 4 x 2 = 24; added 9; the last stage left out 12
    ('num.counting_sum', 'num_counting', {'n1': 3, 'n2': 4, 'n3': 2}, 'number', '24', '9', V),
    ('num.counting_stage', 'num_counting', {'n1': 3, 'n2': 4, 'n3': 2}, 'number', '24', '12', V),
    # 3 : 5 with a difference of 12 is 6 per part, so 48 in all; the difference used as one part, 8 x 12 = 96
    ('ratio.difference_part', 'ratio_from_difference', {'a': 3, 'b': 5, 'diff': 12, 'ask': 'total'}, 'number', '48', '96', V),
    # review: the smaller share asked for, 3 x 6 = 18; the difference used as one part, 3 x 12 = 36
    ('ratio.difference_part', 'ratio_from_difference', {'a': 3, 'b': 5, 'diff': 12, 'ask': 'smaller'}, 'number', '18', '36', V),
    # y = 12 at x = 2 and y proportional to x squared: at x = 6 it is 12 x 9 = 108; linearly 36
    ('ratio.square_linear', 'prop_square', {'y1': 12, 'x1': 2, 'x2': 6}, 'number', '108', '36', V),
    # perimeter 40, rectangle sides x + 5 and x + 7: x = 8; two sides only 40 - 5 - 7 = 28
    ('alg.perimeter_two_sides', 'alg_form_perimeter', {'a': 5, 'b': 7, 'p': 40, 'kind': 'rect'}, 'number', '8', '28', V),
    # triangle (p - a + b) / 4 = 10; the sign not moved (38 - 4 - 6) / 4 = 7
    ('alg.perimeter_sign_moved', 'alg_form_perimeter', {'a': 4, 'b': 6, 'p': 38, 'kind': 'tri'}, 'number', '10', '7', V),
    # (180 - 12 + 6) / 6 = 29; sign not moved 162 / 6 = 27; x counted once 174 / 3 = 58
    ('alg.angles_sign_moved', 'alg_angles', {'total': 180, 'a': 12, 'b': 6, 'c1': 1, 'c2': 2, 'c3': 3}, 'number', '29', '27', V),
    ('alg.angles_x_once', 'alg_angles', {'total': 180, 'a': 12, 'b': 6, 'c1': 1, 'c2': 2, 'c3': 3}, 'number', '29', '58', V),
    # (x + 5)(x - 2) = 18 gives x = 4 or -7; the negative root typed
    ('alg.area_negative_root', 'alg_form_area', {'a': 5, 'b': 2, 'area': 18}, 'number', '4', '-7', V),
    # 3 + 3 x ? = 15: 4; the wrong inverse (15 + 3) / 3 = 6
    ('bidmas.missing_wrong_inverse', 'bidmas_missing', {'form': 'add_mul', 'a': 3, 'b': 3, 'c': 15}, 'number', '4', '6', V),
    # 50 - ?^2 = 14: 6; the square left in place 50 - 14 = 36
    ('bidmas.missing_square_kept', 'bidmas_missing', {'form': 'sub_square', 'a': 50, 'c': 14}, 'number', '6', '36', V),
    # (4 + 2 x 6) / (10 - 6) = 4; without brackets 4 + 12 / 10 - 6 = -0.8
    ('bidmas.bar_no_brackets', 'bidmas_fraction_bar', {'a': 4, 'b': 2, 'c': 6, 'd': 10, 'e': 6}, 'number', '4', '-0.8', V),
    # (21 - (-3)^2) / (8 - 2^2) = 3; without brackets 21 - 9 / 8 - 4 = 15.875; (21 + 9) / 4 = 7.5
    ('bidmas.bar_neg_no_brackets', 'bidmas_fraction_bar_neg', {'a': 21, 'b': 8, 'n': 3, 'p': 2, 'e': 2}, 'number', '3', '15.875', V),
    ('bidmas.bar_neg_square', 'bidmas_fraction_bar_neg', {'a': 21, 'b': 8, 'n': 3, 'p': 2, 'e': 2}, 'number', '3', '7.5', V),
    # (3 root 5)^2 = 45; the number in front not squared 15
    ('surd.square_coefficient', 'surds_square', {'k': 3, 'r': 5}, 'number', '45', '15', V),
    # 7 - 2.4 = 4.6; whole parts only subtracted, the .4 put back: 5.4
    ('dec.whole_minus_decimal', 'num_directed', {'a': 7, 'op': '-', 'b': 2.4}, 'number', '4.6', '5.4', V),
    # 3.7468 to 2 dp is 3.75, a difference of 0.0032
    ('dec.round_error_rounded', 'dec_round_error', {'x': 3.7468, 'dp': 2}, 'number', '0.0032', '3.75', V),
    # sqrt 16 + 3 x 2^2 = 4 + 12 = 16; adding first, (4 + 3) x 4 = 28
    ('bidmas.root_mix_left_to_right', 'bidmas_root_mix', {'kind': 0, 'r': 16, 'b': 3, 'c': 2, 'p': 2, 'a': 0}, 'number', '16', '28', V),
    # 3 x (-4)^2 - 2 x 5 = 48 - 10 = 38; the negative square taken as -16: -48 - 10 = -58
    ('bidmas.sub_neg_square', 'bidmas_sub_neg', {'k1': 3, 'a': -4, 'k2': 2, 'b': 5}, 'number', '38', '-58', V),
)
PAIR_TX_5B = PAIR_TX_5B + (
    # 12 and 18 minute laps: 3 and 2 laps in 36 minutes; swapped 2 and 3; the lap times 12 and 18
    ('mf.laps_swap', 'mf_laps', {'a': 12, 'b': 18}, 'number_pair', '3|2', '2|3', V),
    ('mf.laps_lap_times', 'mf_laps', {'a': 12, 'b': 18}, 'number_pair', '3|2', '12|18', V),
)
PART_TX_5B = PART_TX_5B + (
    # 2 : 3 and 4 : 5 combine to 8 : 12 : 15; the middle not matched gives 2 : 3 : 5
    ('ratio.combine_chained', 'ratio_combine', {'a': 2, 'b': 3, 'c': 4, 'd': 5}, ['8', '12', '15'], 0, '2', V),
    # 72 = 2^3 x 3^2: a = 3 and b = 2; the powers matched to the other primes gives a = 2 and b = 3
    ('mf.exponents_swapped', 'mf_pf_exponents', {'n': 72, 'p1': 2, 'p2': 3, 'p3': 0}, ['3', '2'], 0, '2', V),
)

# ---- Phase 3 batch B (docs/GCSE_MATHS_VARIETY.md): simultaneous equations, completing the square, quadratic simultaneous
# equations, algebraic fractions, functions and iteration ----
SCALAR_TX_5B = SCALAR_TX_5B + (
    # 2x + y = 11 and x - y = 1 give x = 4, y = 3: xy = 12; x + y typed 7
    ('sim.expr_value_sum', 'sim_expr_value', {'a1': 2, 'b1': 1, 'c1': 11, 'a2': 1, 'b2': -1, 'c2': 1, 'ask': 'xy'}, 'number', '12', '7', V),
    # 2x + 3y = 5 and 6x + ky = 20: k = 9; the 3 copied
    ('sim.parallel_k_one_term', 'sim_parallel_k', {'kind': 'none', 'a1': 2, 'b1': 3, 'c1': 5, 'a2': 6, 'c2': 20}, 'number', '9', '3', V),
    # x^2 + 6x + 5 = (x + 3)^2 + q: q = 5 - 9 = -4; the 5 kept; the 9 added gives 14
    ('cts.q_constant_kept', 'cts_q_given_p', {'b': 6, 'c': 5, 'p': 3}, 'number', '-4', '5', V),
    ('cts.q_square_added', 'cts_q_given_p', {'b': 6, 'c': 5, 'p': 3}, 'number', '-4', '14', V),
    # x^2 + 4x + 1 = (x + 2)^2 - 3: two solutions; the sign flipped gives none
    ('cts.count_sign_flipped', 'cts_count_roots', {'b': 4, 'c': 1}, 'number', '2', '0', V),
    # circle of radius squared 25 and y = x - 1 at x = 4: y = 3; y squared 25 - 16 = 9
    ('qsim.circle_y_squared', 'qsim_circle_line_y', {'r2': 25, 'm': 1, 'c': -1, 'x': 4}, 'number', '3', '9', V),
    # y = 4x + 1 touching y = x^2 + 1... k = 1 - 4 = -3; the 4 missed in the discriminant: 1 - 16 = -15
    ('qsim.tangent_k_sign', 'qsim_tangent_k', {'m': 4, 'c0': 1}, 'number', '-3', '-15', V),
    # y = 5x + k misses y = x^2: k < -6.25, the greatest whole number is -7; the 4 missed gives -26
    ('qsim.largest_k_four_missed', 'qsim_largest_k_miss', {'m': 5}, 'number', '-7', '-26', V),
    # 2x - 10 is zero at x = 5; the 10 typed (not divided by 2)
    ('af.undefined_not_divided', 'af_undefined', {'a': 2, 'b': -10}, 'number', '5', '10', V),
    # f(x) = 2x + 3, f^-1(11) = 4; f applied to 11 gives 25; the sign of the 3 changed gives 7
    ('fn.inverse_applied', 'fn_inverse_value', {'m': 2, 'c': 3, 'y': 11}, 'number', '4', '25', V),
    ('fn.inverse_sign', 'fn_inverse_value', {'m': 2, 'c': 3, 'y': 11}, 'number', '4', '7', V),
    # batch B review (2026-10-28)
    # y = 4x + k misses y = x^2 - 2: k < -2 - 4 = -6, so -7; the 4 missed: -2 - 16 - 1 = -19
    ('qsim.largest_k_four_missed', 'qsim_largest_k_miss', {'m': 4, 'c0': -2}, 'number', '-7', '-19', V),
    # f(x) = 12 - 5x at -2: 12 + 10 = 22; the minus sign lost: 12 - 10 = 2
    ('fn.neg_input_sign', 'fn_neg_input', {'c': 12, 'm': 5, 'x': -2}, 'number', '22', '2', V),
    # the same, 5x at x = -2 read as 5 - 2 = 3: 12 - 3 = 9
    ('fn.neg_input_implied', 'fn_neg_input', {'c': 12, 'm': 5, 'x': -2}, 'number', '22', '9', V),
    # y = (x + 4)^2 - 7: least value -7; the x-value of the minimum, -4, typed
    ('cts.min_read_x_value', 'cts_min_read', {'p': 4, 'k': -7}, 'number', '-7', '-4', V),
    # 2x^2 + 12x + 25 = 2(x + 3)^2 + 7: least value 7; 25 - 9 = 16 (the 2 not multiplied); the x-value -3
    ('cts.min_nonmonic_a_missed', 'cts_min_nonmonic', {'a': 2, 'b': 12, 'c': 25}, 'number', '7', '16', V),
    ('cts.min_nonmonic_x_value', 'cts_min_nonmonic', {'a': 2, 'b': 12, 'c': 25}, 'number', '7', '-3', V),
    # 4(n + 6) - 4n = 24; only the n multiplied: the 6 typed
    ('ap.bracket_second_term', 'ap_bracket_const', {'a': 4, 'b': 6}, 'number', '24', '6', V),
)
PAIR_TX_5B = PAIR_TX_5B + (
    # fees 10 and 22, rates 5 and 2: 4 units at a cost of 30; the 12 not divided by 3; the fee missed gives 20
    ('sim.equal_cost_not_divided', 'sim_equal_cost', {'f1': 10, 'r1': 5, 'f2': 22, 'r2': 2}, 'number_pair', '4|30', '12|30', V),
    ('sim.equal_cost_fee_missed', 'sim_equal_cost', {'f1': 10, 'r1': 5, 'f2': 22, 'r2': 2}, 'number_pair', '4|30', '4|20', V),
    # parent 3 times the child, in 6 years twice as old: 18 and 6 now; 24 and 12 later
    ('sim.ages_future', 'sim_ages', {'k': 3, 'n': 6, 'm': 2}, 'number_pair', '18|6', '24|12', V),
    # x = 3 and y = 1 in 2x + 3y and 4x - 2y: 9 and 10; the first terms only 6 and 12
    ('sim.sub_one_term', 'sim_sub_solution', {'p': 2, 'q': 3, 'r': 4, 's': -2, 'x': 3, 'y': 1}, 'number_pair', '9|10', '6|12', V),
    # 2 + 6x - x^2 = 11 - (x - 3)^2; the 9 taken from the 2 gives -7
    ('cts.a_minus_square_signed', 'cts_a_minus_sq', {'c': 2, 'b': 6, 'a': 11, 'p': 3}, 'number_pair', '11|3', '-7|3', V),
    # minimum at (3, -2): b = -6 and c = 9 - 2 = 7; the squared part missed gives c = -2
    ('cts.vertex_constant_only', 'cts_from_vertex', {'h': 3, 'k': -2}, 'number_pair', '-6|7', '-6|-2', V),
    # y = x^2 and y = 3x + 4 meet at x = 4 and -1: midpoint (1.5, 8.5); the mean x put in the curve gives 2.25
    ('qsim.midpoint_on_curve', 'qsim_midpoint', {'m': 3, 'c': 4}, 'number_pair', '1.5|8.5', '1.5|2.25', V),
    # batch B review: x^2 = 3x - 2 gives x^2 - 3x + 2 = 0, so p = -3 and q = 2; the signs kept give 3 and -2
    ('qsim.sub_signs_kept', 'qsim_sub_coeffs', {'m': 3, 'c': -2}, 'number_pair', '-3|2', '3|-2', V),
)
PART_TX_5B = PART_TX_5B + (
    # x = 3 and -2 in y = x^2: 9 and 4; the x-values typed
    ('qsim.y_x_values_typed', 'qsim_y_from_x', {'m': 1, 'c': 6, 'x1': 3, 'x2': -2}, ['9', '4'], 0, '3', V),
    # x_{n+1} = 2 x_n + 3 from 1: 5 and 13; the 3 missed at the second step gives 10
    ('eq.iterate_linear_constant_once', 'eq_iterate_linear', {'a': 2, 'b': 3, 'x0': 1}, ['5', '13'], 1, '10', V),
    # x_{n+1} = 2 + 6 / x_n from 3: 4 and 3.5; the 2 missed gives 1.5
    ('eq.iterate_recip_a_missed', 'eq_iterate_recip', {'a': 2, 'b': 6, 'x0': 3}, ['4', '3.5'], 1, '1.5', V),
    # x^3 + 2x - 10 at 1, 2, 3: -7, 2, 23 and n = 1; the sign of the 10 changed gives 13 at x = 1
    ('eq.change_constant_sign', 'eq_sign_change', {'p': 2, 'k': 10}, ['-7', '2', '23', '1'], 0, '13', V),
)

# ---- Phase 3 batch C1 (docs/GCSE_MATHS_VARIETY.md section 21): statistics, probability, graphs, ratio, trigonometry,
# Pythagoras ----
_C1_CELLS = [[10, 20, 10], [20, 30, 10]]
_C1_VENN = {'a_only': 15, 'b_only': 22, 'both': 3, 'neither': 16}
SCALAR_TX_5B = SCALAR_TX_5B + (
    # Year 10 row 10 + 20 + 5 = 35; the first column added instead, 10 + 8 = 18
    ('stats.two_way_other_way', 'stats_two_way_read', {'cells': [[10, 20, 5], [8, 12, 15]], 'ask': 'row', 'index': 0}, 'number', '35', '18', V),
    # everyone: 70; one row only, 35
    ('stats.two_way_part_only', 'stats_two_way_read', {'cells': [[10, 20, 5], [8, 12, 15]], 'ask': 'all', 'index': 0}, 'number', '70', '35', V),
    # 18 of the 40 in row 0: 45%; out of everyone (80) gives 22.5%
    ('stats.percent_wrong_total', 'stats_two_way_percent', {'cells': [[12, 18, 10], [15, 15, 10]], 'row': 0, 'col': 1}, 'number', '45', '22.5', V),
    # stems 2 and 3, leaves 1 5 | 2 4 8: values 21, 25, 32, 34, 38; median 32; the leaf alone, 2
    ('stats.stem_leaf_only', 'stats_stem_leaf', {'stems': [2, 3], 'leaves': [[1, 5], [2, 4, 8]], 'ask': 'median'}, 'number', '32', '2', V),
    # range 38 - 21 = 17; the largest value typed
    ('stats.stem_range_largest', 'stats_stem_leaf', {'stems': [2, 3], 'leaves': [[1, 5], [2, 4, 8]], 'ask': 'range'}, 'number', '17', '38', V),
    # 11 values 12 15 18 | 20 23 26 29 | 31 34 37 39: Q1 is the 3rd (18), Q3 the 9th (34): IQR 16; the range 27; Q3 alone
    ('stats.stem_iqr_range', 'stats_stem_leaf', {'stems': [1, 2, 3], 'leaves': [[2, 5, 8], [0, 3, 6, 9], [1, 4, 7, 9]], 'ask': 'iqr'}, 'number', '16', '27', V),
    ('stats.stem_iqr_upper', 'stats_stem_leaf', {'stems': [1, 2, 3], 'leaves': [[2, 5, 8], [0, 3, 6, 9], [1, 4, 7, 9]], 'ask': 'iqr'}, 'number', '16', '34', V),
    # values 0 to 3 with frequencies 4, 7, 9, 5: the mode is 2; its frequency 9 typed
    ('stats.table_mode_count', 'stats_table_mode', {'values': [0, 1, 2, 3], 'freqs': [4, 7, 9, 5]}, 'number', '2', '9', V),
    # values 1 to 4 with frequencies 2, 9, 3, 1 (15 items): the 8th item is a 2; the middle row (3) typed; the position 8 typed
    ('stats.table_median_middle_row', 'stats_table_median', {'values': [1, 2, 3, 4], 'freqs': [2, 9, 3, 1]}, 'number', '2', '3', V),
    ('stats.table_median_position', 'stats_table_median', {'values': [1, 2, 3, 4], 'freqs': [2, 9, 3, 1]}, 'number', '2', '8', V),
    # mean of 4 values is 20, three are 7, 18, 14: the fourth is 80 - 39 = 41; the mean of the three (13); 20 x 3 - 39 = 21
    ('stats.missing_mean_of_known', 'stats_missing_value', {'n': 4, 'mean': 20, 'known': [7, 18, 14]}, 'number', '41', '13', V),
    ('stats.missing_count_short', 'stats_missing_value', {'n': 4, 'mean': 20, 'known': [7, 18, 14]}, 'number', '41', '21', V),
    # 7 pupils at 48 and 14 at 30: (336 + 420) / 21 = 36; the mean of the means is 39
    ('stats.mean_of_means', 'stats_combined_mean', {'n1': 7, 'm1': 48, 'n2': 14, 'm2': 30}, 'number', '36', '39', V),
    # 8 of 50 scaled to 1000: 160; upside down, 50/8 x 1000 = 6250
    ('stats.sample_upside_down', 'stats_sample_scale', {'hits': 8, 'sample': 50, 'pop': 1000}, 'number', '160', '6250', V),
    # 50 tagged, 15 of a second catch of 60: 50 x 60 / 15 = 200; upside down, 60 x 15 / 50 = 18
    ('stats.recapture_upside_down', 'stats_recapture', {'m': 50, 'n': 60, 'k': 15}, 'number', '200', '18', V),
    # classes 0-10, 10-20, 20-30 with frequencies 2, 4, 4: midpoints give 170 / 10 = 17; the class ends give 220 / 10 = 22
    ('stats.polygon_class_end', 'stats_polygon', {'intervals': [[0, 10], [10, 20], [20, 30]], 'freqs': [2, 4, 4], 'ask': 'mean'}, 'number', '17', '22', V),
    # frequencies 2, 4, 4: total 10; the highest point, 4, typed
    ('stats.polygon_peak_only', 'stats_polygon', {'intervals': [[0, 10], [10, 20], [20, 30]], 'freqs': [2, 4, 4], 'ask': 'total'}, 'number', '10', '4', V),
    # four classes with frequencies 4, 6, 4, 6: mean 420 / 20 = 21; the mean of the frequencies is 5
    ('stats.polygon_freq_mean', 'stats_polygon', {'intervals': [[0, 10], [10, 20], [20, 30], [30, 40]], 'freqs': [4, 6, 4, 6], 'ask': 'mean'}, 'number', '21', '5', V),
    # second year 5, 8, 4, 9: mean 6.5; all eight points give 58 / 8 = 7.25; the total 26
    ('stats.series_all_points', 'stats_series_mean', {'values': [8, 6, 11, 7, 5, 8, 4, 9], 'year': 1}, 'number', '6.5', '7.25', V),
    ('stats.series_not_divided', 'stats_series_mean', {'values': [8, 6, 11, 7, 5, 8, 4, 9], 'year': 1}, 'number', '6.5', '26', V),
    # two dice, total 7: 6 of 36; one of the 11 different totals
    ('prob.space_distinct_totals', 'prob_sample_space', {'n1': 6, 'n2': 6, 'op': 'sum', 'event_word': 'equal to 7'}, 'fraction', '1/6', '1/11', V),
    # tree 36, 4, 16, 144: given "yes" (52), adults 36: 9/13; out of 200 gives 9/50; out of the adults (40) gives 9/10
    ('prob.tree_cond_joint', 'prob_freq_tree_cond', {'aa': 36, 'ab': 4, 'ba': 16, 'bb': 144, 'cond': 'yes', 'group': 'g1'}, 'fraction', '9/13', '9/50', V),
    ('prob.tree_cond_wrong_group', 'prob_freq_tree_cond', {'aa': 36, 'ab': 4, 'ba': 16, 'bb': 144, 'cond': 'yes', 'group': 'g1'}, 'fraction', '9/13', '9/10', V),
    # cell 20 of 100: 1/5; out of its row (40) gives 1/2; given the row, 1/2 is right and 1/5 (out of everyone) or 2/5 (the column) are slips
    ('prob.two_way_group_total', 'prob_two_way', {'cells': _C1_CELLS, 'ask': 'cell', 'row': 0, 'col': 1}, 'fraction', '1/5', '1/2', V),
    ('prob.two_way_joint', 'prob_two_way', {'cells': _C1_CELLS, 'ask': 'given_row', 'row': 0, 'col': 1}, 'fraction', '1/2', '1/5', V),
    # the whole column 1 (50 of 100): 1/2; one cell of it (20 of 100) typed
    ('prob.two_way_one_cell', 'prob_two_way', {'cells': _C1_CELLS, 'ask': 'col', 'row': 0, 'col': 1}, 'fraction', '1/2', '1/5', V),
    ('prob.two_way_wrong_group', 'prob_two_way', {'cells': _C1_CELLS, 'ask': 'given_row', 'row': 0, 'col': 1}, 'fraction', '1/2', '2/5', V),
    # Venn 15, 22, 3, 16 (56 people): A union B is 40/56 = 5/7; the overlap alone 3/56; the overlap twice 43/56
    ('prob.venn_union_as_intersection', 'prob_venn_set', dict(_C1_VENN, ask_word='A ∪ B'), 'fraction', '5/7', '3/56', V),
    ('prob.venn_union_overlap_twice', 'prob_venn_set', dict(_C1_VENN, ask_word='A ∪ B'), 'fraction', '5/7', '43/56', V),
    ('prob.venn_intersection_as_union', 'prob_venn_set', dict(_C1_VENN, ask_word='A ∩ B'), 'fraction', '3/56', '5/7', V),
    # A' is 38/56 = 19/28; A itself 18/56 = 9/28; B only 22/56 = 11/28
    ('prob.venn_set_not_complemented', 'prob_venn_set', dict(_C1_VENN, ask_word="A'"), 'fraction', '19/28', '9/28', V),
    ('prob.venn_set_neither_missed', 'prob_venn_set', dict(_C1_VENN, ask_word="A'"), 'fraction', '19/28', '11/28', V),
    # A' and B is B only, 22/56 = 11/28; the whole of B is 25/56
    ('prob.venn_complement_ignored', 'prob_venn_set', dict(_C1_VENN, ask_word="A' ∩ B"), 'fraction', '11/28', '25/56', V),
    # given A (18 people), also in B: 3/18 = 1/6; out of everyone 3/56; out of B (25) 3/25
    ('prob.venn_given_joint', 'prob_venn_set', dict(_C1_VENN, ask_word='who play football', given='A'), 'fraction', '1/6', '3/56', V),
    ('prob.venn_given_wrong_circle', 'prob_venn_set', dict(_C1_VENN, ask_word='who play football', given='A'), 'fraction', '1/6', '3/25', V),
    # circle through (3, 4): k = 25; the radius 5; the coordinates added 7
    ('gr.circle_radius_not_squared', 'gr_circle_k', {'ask': 'k', 'x': 3, 'y': 4}, 'number', '25', '5', V),
    ('gr.circle_coords_added', 'gr_circle_k', {'ask': 'k', 'x': 3, 'y': 4}, 'number', '25', '7', V),
    # x^2 + y^2 = 49: radius 7; 49 typed; 49 halved
    # v = 12 over 4 s, 6 s flat, 2 s to stop: acceleration 3; the area of the first triangle 24
    ('gr.vt_area_for_gradient', 'gr_vt', {'v': 12, 't1': 4, 't2': 6, 't3': 2, 'ask': 'first'}, 'number', '3', '24', V),
    # distance 24 + 72 + 12 = 108; the gradient 3; the whole rectangle 12 x 12 = 144; the middle only 72
    ('gr.vt_gradient_for_area', 'gr_vt', {'v': 12, 't1': 4, 't2': 6, 't3': 2, 'ask': 'distance'}, 'number', '108', '3', V),
    ('gr.vt_whole_rectangle', 'gr_vt', {'v': 12, 't1': 4, 't2': 6, 't3': 2, 'ask': 'distance'}, 'number', '108', '144', V),
    ('gr.vt_middle_only', 'gr_vt', {'v': 12, 't1': 4, 't2': 6, 't3': 2, 'ask': 'distance'}, 'number', '108', '72', V),
    # y = kx^3, x = 2 gives y = 40: k = 5, so x = 3 gives 135; linear 60; squared 90
    ('ratio.cube_linear', 'prop_power', {'p': 3, 'x1': 2, 'y1': 40, 'given': 'x', 'x2': 3}, 'number', '135', '60', V),
    ('ratio.cube_square', 'prop_power', {'p': 3, 'x1': 2, 'y1': 40, 'given': 'x', 'x2': 3}, 'number', '135', '90', V),
    # y = k root x, x = 16 gives 12: k = 3, so x = 25 gives 15; linear 18.75
    ('ratio.root_linear', 'prop_root', {'x1': 16, 'y1': 12, 'given': 'x', 'x2': 25}, 'number', '15', '18.75', V),
    # y = k / x^2, x = 2 gives 9: k = 36, so x = 3 gives 4; inverse without the square 6; direct square 20.25
    ('ratio.inverse_square_inverse', 'prop_inverse_square', {'x1': 2, 'y1': 9, 'given': 'x', 'x2': 3}, 'number', '4', '6', V),
    ('ratio.inverse_square_direct', 'prop_inverse_square', {'x1': 2, 'y1': 9, 'given': 'x', 'x2': 3}, 'number', '4', '20.25', V),
    # 2 : 3, 8 more red makes 4 : 3: t = 24 / 6 = 4, blue 12; 8 taken as one part gives 24
    ('ratio.added_as_part', 'ratio_change', {'a': 2, 'b': 3, 'n': 8, 'c': 4, 'd': 3, 'ask': 'blue'}, 'number', '12', '24', V),
    # 12 cakes need 300 g flour and 4 eggs; 1000 g and 10 eggs: 40 by flour, 30 by eggs, so 30; the larger 40
    ('ratio.limiting_larger', 'ratio_limiting', {'per': 12, 'a1': 300, 'a2': 4, 'have1': 1000, 'have2': 10}, 'number', '30', '40', V),
    # sin x = 0.5 between 90 and 180: 150; the other crossing 30
    ('trig.graph_other_solution', 'trig_graph_read', {'fn_word': 'sin', 'k': '0.5', 'lo': 90, 'hi': 180}, 'number', '150', '30', V),
    # diagonals 12 and 16: halves 6 and 8, side 10; the whole diagonals give 20
    ('pyth.diagonals_not_halved', 'pyth_rhombus', {'d1': 12, 'd2': 16}, 'number', '10', '20', V),
    # diagonal 10: area 50; the diagonal squared 100; half the diagonal squared 25
    ('pyth.diagonal_squared_not_halved', 'pyth_square_area_diag', {'d': 10}, 'number', '50', '100', V),
    ('pyth.half_diagonal_as_side', 'pyth_square_area_diag', {'d': 10}, 'number', '50', '25', V),
    # x, x + 7 and x + 8: x = 5; the sides added, 8 - 7 = 1
    ('pyth.algebraic_sides_added', 'pyth_algebraic', {'a': 7, 'b': 8}, 'number', '5', '1', V),
    # ---- Phase 3 batch C2 ------------------------------------------------------------------------------------------
    # 3 red, P(both red) = 1/100: n(n - 1) = 600, n = 25, blue 22; with replacement n = 3 / sqrt(1/100) = 30, blue 27
    ('prob.counters_with_replacement', 'prob_counters_algebraic', {'r': 3, 'p_num': 1, 'p_den': 100}, 'number', '22', '27', V),
    # 3 red, P(both red) = 1/35: n = 15, blue 12; the total 15 typed
    ('prob.counters_total_typed', 'prob_counters_algebraic', {'r': 3, 'p_num': 1, 'p_den': 35}, 'number', '12', '15', V),
    # P(A) = 0.3, P(B) = 0.2 independent: P(A or B) = 0.5 - 0.06 = 0.44; added 0.5; the product 0.06; exactly one 0.38
    ('prob.union_added', 'prob_independent_union', {'pa': '0.3', 'pb': '0.2', 'ask': 'union'}, 'number', '0.44', '0.5', V),
    ('prob.union_product_only', 'prob_independent_union', {'pa': '0.3', 'pb': '0.2', 'ask': 'union'}, 'number', '0.44', '0.06', V),
    ('prob.exactly_one_union', 'prob_independent_union', {'pa': '0.3', 'pb': '0.2', 'ask': 'exactly_one'}, 'number', '0.38', '0.44', V),
    # 7 red and 3 blue, three without replacement: (210 + 6)/720 = 3/10; with replacement (343 + 27)/1000 = 37/100; red only 7/24
    ('prob.three_with_replacement', 'prob_three_same', {'r': 7, 'b': 3}, 'fraction', '3/10', '37/100', V),
    ('prob.three_one_colour', 'prob_three_same', {'r': 7, 'b': 3}, 'fraction', '3/10', '7/24', V),
    # rain Monday 0.7; Tuesday 0.4 after rain, 0.2 after none: at least one 1 - 0.3 x 0.8 = 0.76; independent 1 - 0.3^2 = 0.91;
    # both days 0.28
    ('prob.two_day_independent', 'prob_two_day', {'p1': '0.7', 'p_given': '0.4', 'p_not_given': '0.2', 'ask': 'at_least_one'}, 'number', '0.76', '0.91', V),
    ('prob.two_day_both_only', 'prob_two_day', {'p1': '0.7', 'p_given': '0.4', 'p_not_given': '0.2', 'ask': 'at_least_one'}, 'number', '0.76', '0.28', V),
    # 0.5; 0.4 after, 0.8 after none: exactly one 0.5 x 0.6 + 0.5 x 0.8 = 0.7; one branch 0.3
    ('prob.two_day_one_branch', 'prob_two_day', {'p1': '0.5', 'p_given': '0.4', 'p_not_given': '0.8', 'ask': 'exactly_one'}, 'number', '0.7', '0.3', V),
    # P(head) = 0.4, above 0.99: 1 - 0.6^n passes at n = 10; 0.4 n > 0.99 gives 3
    ('prob.trials_added', 'prob_trials_needed', {'p': '0.4', 'target': '0.99'}, 'number', '10', '3', V),
    # bag A 7 of 8 red, bag B 2 of 10: P(A | red) = (7/16) / (7/16 + 1/10) = 35/43; the joint 7/16; the counts 7/9
    ('prob.which_bag_joint', 'prob_which_bag', {'r1': 7, 'n1': 8, 'r2': 2, 'n2': 10}, 'fraction', '35/43', '7/16', V),
    ('prob.which_bag_counts', 'prob_which_bag', {'r1': 7, 'n1': 8, 'r2': 2, 'n2': 10}, 'fraction', '35/43', '7/9', V),
    # ages 2 : 5, in 8 years 2 : 3: t = 2, the younger is 4 and the older 10; in 8 years 12
    ('ratio.ages_other_person', 'ratio_ages', {'a': 2, 'b': 5, 'n': 8, 'c': 2, 'd': 3, 'ask': 'younger'}, 'number', '4', '10', V),
    ('ratio.ages_future', 'ratio_ages', {'a': 2, 'b': 5, 'n': 8, 'c': 2, 'd': 3, 'ask': 'younger'}, 'number', '4', '12', V),
    # 4/5 girls, 3/5 of them and 1/5 of the boys walk: 12/25 + 1/25 = 13/25; added 4/5; girls only 12/25; 4/5 of both 16/25
    ('ratio.groups_fractions_added', 'ratio_fraction_groups', {'f1': '4/5', 's1': '3/5', 's2': '1/5'}, 'fraction', '13/25', '4/5', V),
    ('ratio.groups_one_part', 'ratio_fraction_groups', {'f1': '4/5', 's1': '3/5', 's2': '1/5'}, 'fraction', '13/25', '12/25', V),
    ('ratio.groups_rest_not_taken', 'ratio_fraction_groups', {'f1': '4/5', 's1': '3/5', 's2': '1/5'}, 'fraction', '13/25', '16/25', V),
    # 132 shared, 20% more: 6 : 5, one part 12, the larger share 72; half plus 20% is 79.2; the other share 60
    ('ratio.percent_more_half', 'ratio_percent_more', {'total': 132, 'p': 20, 'ask': 'more'}, 'number', '72', '79.2', V),
    ('ratio.percent_more_other', 'ratio_percent_more', {'total': 132, 'p': 20, 'ask': 'more'}, 'number', '72', '60', V),
    # A : B = 1 : 3, B : C = 2 : 5, C gets 26 more than A: 2 : 6 : 15, 13 parts is 26, B = 12; unmatched 26 / 4 a part,
    # B = 3 x 6.5 = 19.5; 26 taken as one part, B = 6 x 26 = 156
    ('ratio.three_part_not_matched', 'ratio_three_part_difference', {'a': 1, 'b1': 3, 'b2': 2, 'c': 5, 'gap': 26, 'ask': 'B'}, 'number', '12', '19.5', V),
    ('ratio.gap_as_part', 'ratio_three_part_difference', {'a': 1, 'b1': 3, 'b2': 2, 'c': 5, 'gap': 26, 'ask': 'B'}, 'number', '12', '156', V),
    # (x + 7) : (2x + 2) = 4 : 5: 5x + 35 = 8x + 8, x = 9; the other way, 4x + 28 = 10x + 10, x = 3
    ('ratio.cross_multiply_swapped', 'ratio_algebraic_parts', {'p': 1, 'q': 7, 'r': 2, 's': 2, 'a': 4, 'b': 5}, 'number', '9', '3', V),
    # (a, -7) on y = -2x + 9: a = 8; -7 put in for x gives 23; the sign of 9 kept, (-7 + 9) / -2 = -1
    ('gr.coordinate_wrong_letter', 'gr_missing_coordinate', {'m': -2, 'c': 9, 'ask': 'x', 'given': -7}, 'number', '8', '23', V),
    ('gr.coordinate_sign_moved', 'gr_missing_coordinate', {'m': -2, 'c': 9, 'ask': 'x', 'given': -7}, 'number', '8', '-1', V),
    # marked points (0, 0) and (4, -8): gradient -2; the rise -8 on its own
    ('gr.gradient_rise_only', 'gr_gradient_graph', {'x1': 0, 'y1': 0, 'x2': 4, 'y2': -8}, 'number', '-2', '-8', V),
    # 40 miles is 64 km: converting 40 the wrong way reads 40 km as 25 miles
    ('gr.conversion_wrong_way', 'gr_conversion', {'x': 40, 'y': 64, 'ask': 'to'}, 'number', '64', '25', V),
    # class 20 to 40 with frequency 18: density 0.9; the frequency 18 typed; class 10 to 40 with 18: 0.6, the width 30
    ('stats.fd_width_typed', 'stats_frequency_density', {'lo': 10, 'hi': 40, 'ask': 'density', 'freq': 18}, 'number', '0.6', '30', V),
    # class 20 to 40 drawn 1.5 high: frequency 30; divided instead, 0.075
    ('stats.fd_divided', 'stats_frequency_density', {'lo': 20, 'hi': 40, 'ask': 'frequency', 'fd': '1.5'}, 'number', '30', '0.075', V),
)
PAIR_TX_5B = PAIR_TX_5B + (
    # (2, 5) on y = f(x + 3) goes to (-1, 5); the wrong way (5, 5); on y = f(x) + 3 it goes to (2, 8), not (5, 5)
    ('gr.shift_wrong_way', 'gr_transform_point', {'kind': 'f(x + {a})', 'a': 3, 'x': 2, 'y': 5}, 'number_pair', '-1|5', '5|5', V),
    ('gr.shift_inside_outside', 'gr_transform_point', {'kind': 'f(x) + {a}', 'a': 3, 'x': 2, 'y': 5}, 'number_pair', '2|8', '5|5', V),
    # Phase 3 batch C2: y = -2x + 12 crosses the x-axis at (6, 0); the y-intercept (0, 12) typed
    ('gr.x_intercept_y_intercept', 'gr_x_intercept', {'m': -2, 'c': 12}, 'number_pair', '6|0', '0|12', V),
)
PART_TX_5B = PART_TX_5B + (
    # row 0: a + 16 + 24 = 48 so a = 8; b = 22 - 16 = 6; c = 54 - 24 = 30; the grand total used for a gives 49; row 1 gives 36
    ('stats.two_way_complete_grand', 'stats_two_way_complete',
     {'r0c1': 16, 'r0c2': 24, 'r1c0': 5, 'row0': 48, 'row1': 41, 'col0': 13, 'col1': 22, 'col2': 54, 'grand': 89}, ['8', '6', '30'], 0, '49', V),
    ('stats.two_way_complete_two_missing', 'stats_two_way_complete',
     {'r0c1': 16, 'r0c2': 24, 'r1c0': 5, 'row0': 48, 'row1': 41, 'col0': 13, 'col1': 22, 'col2': 54, 'grand': 89}, ['8', '6', '30'], 1, '36', V),
    # 128 people, 84 adults, 43 of them yes, 21 of the children no: a = 44, b = 41, c = 23; 128 - 43 = 85; 84 - 21 = 63
    ('prob.tree_fill_total', 'prob_freq_tree_fill', {'total': 128, 'a': 84, 'aa': 43, 'bb': 21}, ['44', '41', '23'], 1, '85', V),
    ('prob.tree_fill_wrong_group', 'prob_freq_tree_fill', {'total': 128, 'a': 84, 'aa': 43, 'bb': 21}, ['44', '41', '23'], 2, '63', V),
    # points 3, 6, 12, 24: a = 3 and b = 2; the value at x = 1 (6) typed for a and for b; the difference 3 for b
    ('gr.exp_a_at_one', 'gr_exponential', {'ys': [3, 6, 12, 24]}, ['3', '2'], 0, '6', V),
    ('gr.exp_b_not_divided', 'gr_exponential', {'ys': [3, 6, 12, 24]}, ['3', '2'], 1, '6', V),
    # points 2, 8, 32, 128: a = 2, b = 4; the difference 8 - 2 = 6 typed for b
    ('gr.exp_b_difference', 'gr_exponential', {'ys': [2, 8, 32, 128]}, ['2', '4'], 1, '6', V),
    # sin x = 0.35: 20.5 and 159.5; the cosine rule 360 - 20.5 = 339.5 typed for the second
    ('trig.second_solution_rule', 'trig_solve_k', {'fn_word': 'sin', 'k': '0.35'}, ['20.5', '159.5'], 1, '339.5',
     'Solve sin x = 0.35 for 0° ≤ x ≤ 360°. Give both solutions, correct to 1 decimal place.'),
)
