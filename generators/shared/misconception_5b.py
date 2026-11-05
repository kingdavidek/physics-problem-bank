"""Topic misconception rules, Phase 5b (docs/GCSE_MATHS_HINTS.md, section 23): wider topic coverage.

The same design as ``misconception_cd.py`` (read its header first). This module only holds data and small slip
functions: circle theorems, similarity, and the topics that follow. It adds to the tables of ``misconception_cd``
through ``install(cd)``, which that module calls once, before it builds its derived tables. It imports no
generator, no random numbers and no database. Everything is exact (``Fraction``).

Each family has

* a ``truth`` (the correct answer of every box, rebuilt from the printed numbers: the guard), and
* one or more slips: a *whole vector* over the boxes (``None`` = no slip for that box), so a pupil who made the
  slip in one box is told about that box only.

A rule says nothing when the slip is also the right answer of the question, a number printed in it (unless the
rule is in ``ECHO_OK``), or next to the key. The shared machinery in ``misconceptions.py`` applies those guards.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

from generators.shared.misconception_topics import F, _items, _n, _r, round_sf, round_unit, sqrtq, trig

MESSAGES = {
    # ratio and proportion
    'ratio.shared_equally': 'That shares the amount out equally. In a ratio, the shares are different sizes.',
    # multiples and factors
    'mf.lcm_for_hcf': 'That is the lowest common multiple. The question asks for the highest common factor.',
    'mf.hcf_for_lcm': 'That is the highest common factor. The question asks for the lowest common multiple.',
    'mf.product_for_lcm': 'That is the two numbers multiplied. Their lowest common multiple is smaller when they share a factor.',
    'mf.hcf_for_count': 'That is the highest common factor. The question asks how many factors they have in common.',
    'mf.third_ignored': 'It looks like only two of the three numbers were used. All three must be included.',
    'mf.product_rule_missed': 'Check the rule. The two numbers multiply to give the HCF times the LCM.',
    # decimals and number
    'dec.not_aligned': 'Line up the decimal points first. Write zeros so each number has the same number of decimal places.',
    'num.digit_not_value': 'That is the digit itself. The question asks for its value, which depends on its place.',
    'num.scale_direction': 'Multiplying by a power of ten makes a number bigger, and dividing makes it smaller. Check which.',
    'num.place_names': 'Check the place names. After the decimal point they go tenths, hundredths, thousandths.',
    'num.recurring_stops': 'A recurring decimal does not stop. It cannot be written over a power of ten.',
    'num.bounds_full_unit': 'Check the error. The true value can be half of the rounding unit either side.',
    'num.bounds_combination': 'Check the pairing. For the smallest answer, divide the smallest top by the largest bottom.',
    # shapes and solids
    'mens.hemisphere_half': 'Check the hemisphere. It is half of a sphere, so use half of the sphere formula.',
    'mens.face_missed': 'A prism has a rectangle for every side of its cross-section. One face has been left out.',
    'mens.end_once': 'A prism has two ends. The end shape has to be counted twice.',
    'mens.cube_root_missed': 'Check the last step. To undo a cube, take the cube root.',
    'mens.rise_not_divided': 'That is the volume of the sphere. The water level rises by that volume divided by the area of the base.',
    'mens.mass_formula': 'Check the formula. Mass is density multiplied by volume.',
    'mens.segment_triangle_added': 'The segment is the sector with the triangle taken away. It looks like the triangle was added.',
    'mens.cut_triangle': 'The piece cut off is a triangle, not a rectangle. Check its area.',
    'mens.whole_sector': 'That is the whole sector. The segment is what is left when the triangle is taken away.',
    'mens.cross_section_only': 'That is the area of the cross-section. Multiply it by the length of the prism.',
    'trig.area_half_missed': 'Check the formula. The area of a triangle is half of one side times the other times the sine.',
    'vec.sign_not_changed': 'Reversing a vector changes the sign of both of its parts.',
    'vec.parallel_compare': 'Parallel vectors are multiples of each other. Compare top with top and bottom with bottom.',
    # angles
    'ang.kite_pair': 'A kite has one pair of equal angles. Count both of them before taking away from the total.',
    'ang.exterior_for_interior': 'That is the exterior angle. The question asks for the interior angle.',
    'sim.angles_kept': 'Check the angle. In similar shapes, the lengths scale up but the angles stay the same.',
    # circle theorems
    'circ.centre_double': 'The angle at the centre is double the angle at the circumference. Check whether to double or halve.',
    # review 2026-10-27: the old line said the angle is a right angle, which is the key of every question it spoke on (D5)
    'circ.semicircle_right': 'That is the angle on a straight line. Use the circle theorem for the angle in a semicircle.',
    'circ.semicircle_third': 'The angle in a semicircle is 90°, so the other two angles in that triangle add up to 90°.',
    'circ.opposite_equal': 'Opposite angles in a cyclic quadrilateral add up to 180°. They are not equal.',
    'circ.tangent_right': 'A tangent meets the radius at 90°. That right angle is one of the angles of the triangle.',
    'circ.base_angles_shared': 'The two base angles are equal, so share what is left after the other angle between them.',
    'circ.reflex_missed': 'That is the angle that is less than 180°. The question asks for the reflex angle.',
    'circ.wrong_arc': 'Check which arc the point is on. The angles from the two arcs add up to 180°.',
    'circ.alt_segment_equal': 'The angle in the alternate segment is the same as the angle between the tangent and chord.',
    'circ.wrong_chord': 'Check which chord each angle stands on. Angles on the same chord and the same side are equal.',
    'circ.tangents_right_angles': 'Each tangent meets its radius at a right angle. Count both of them in the four-sided shape.',
    'circ.chord_half': 'That is half the chord. The perpendicular from the centre cuts the chord in two.',
    'circ.secant_sum': 'For two secants from a point outside, take the arcs away from each other. Adding is for chords.',
    'circ.chords_add': 'For chords that cross inside the circle, add the two arcs before halving.',
    # similarity
    'sim.length_squared': 'Lengths and perimeters are multiplied by the scale factor itself. Only areas use its square.',
    'sim.direction': 'Check which way the scale factor goes. The bigger shape has the longer sides.',
    'sim.root_missed': 'The volumes are in the ratio of the cubes of the lengths. Take the cube root first.',
    'sim.sf_inverted': 'Check the scale factor. It is the new length divided by the old length.',
    'sim.part_for_whole': 'Compare the small triangle with the whole triangle, so use the whole side, not a part of it.',
    'sim.chain_steps': 'There are two scale factors. Use both, one after the other.',
    'sim.frustum_whole': 'That is the volume of the whole cone. The small cone has to be taken away.',
    'sim.area_ratio_not_rooted': 'That is the ratio of the areas. The scale factor of the lengths is its square root.',
    # read from the question: substitution, functions, sequences and graphs
    'sub.implied_multiply': 'A number next to a letter means multiply. It is not an addition, and the digits do not join up.',
    'sub.divide_multiplied': 'Check the sign between the parts. A fraction bar with x underneath means divide by x.',
    'sub.letters_added': 'Two letters side by side are multiplied. They are not added.',
    'fn.composite_order': 'In f(g(x)), work out g first. Then put that answer into f.',
    'fn.twice_once': 'Applying f twice means putting the first answer back into f. Do that step again.',
    'fn.machine_order': 'The machine does its steps in the order shown. Check which step comes first.',
    'fn.undo_order': 'To go backwards, undo the last step first. Use the opposite of each step.',
    'seq.square_doubled': 'Square numbers are n times n. Doubling n gives the even numbers instead.',
    'seq.triangle_not_halved': 'Triangle numbers are half of n times the next number up. Check that last halving step.',
    'seq.odd_parity': 'The nth odd number is double n, take away one. Doubling n alone gives the even numbers.',
    'gr.parallel_perpendicular': 'Parallel lines have the same gradient. That value is for a line at right angles.',
    'gr.parallel_intercept': 'The gradient is the number in front of x. The number on its own is the y-intercept.',
    'seq.steps_one_fewer': 'Between the first and last term there is one step fewer than the number of terms. Check your count of steps.',
    'seq.sum_not_halved': 'Check the sum formula. It starts with half of n, because the terms pair up.',
    'seq.geometric_power': 'The first term has no ratio applied. The nth term uses the ratio one time fewer than n.',
    'gr.speed_multiplied': 'Speed is distance divided by time, not distance times time.',
    # Phase 5c (section 25)
    'num.round_dp_as_sf': 'Decimal places are the digits after the point. Significant figures start at the first digit that is not zero.',
    'num.round_sf_zeros': 'A rounded number stays about the same size. Fill the places after the last digit you keep with zeros.',
    'num.index_divided': 'The index counts how many copies of the base are multiplied together. It is not found by one division.',
    'alg.consecutive_equal': 'The integers go up by one each time, so they are not all equal to x. Add in the extra amounts too.',
    'lin.fixed_ignored': 'The fixed charge is paid once. Take it off the total before dividing by the rate.',
    'lin.fixed_added': 'The total already includes the fixed charge. Take it away, rather than adding it on.',
    'lin.cost_not_divided': 'That is the cost of the miles. The question asks how many miles.',
    'mens.perimeter_all_round': 'The perimeter goes all the way round the rectangle. That is two lengths and two widths.',
    'seq.fibonacci_step': 'Each term in this sequence is the sum of the two terms before it. Check which two were added.',
    'seq.term_for_sum': 'That is the last term of the series. The question asks for the sum of all the terms.',
    'seq.geometric_sum_denominator': 'Check the sum formula. The top of the fraction is divided by one less than the ratio.',
    'seq.infinite_denominator': 'The sum to infinity divides the first term by one minus the ratio. Check the bottom of that fraction.',
    'surd.equation_not_squared': 'Square both sides to remove the square root. The root cannot be ignored.',
    'surd.quotient_root_missed': 'Dividing the numbers under the roots is the first step. The square root of the result is still needed.',
    'surd.conjugate_sign': 'Check the last term. A positive surd times a negative surd gives a negative.',
    'surd.conjugate_unsquared': 'The whole number is squared as well as the surd. Check the first term.',
    # Phase 3 batch A
    'frac.denominators_added': 'It looks like the bottoms were added or taken away as well. A common denominator stays as it is.',
    'frac.divide_not_flipped': 'Check the rule for dividing by a fraction. It is not the same as multiplying by it as it stands.',
    'frac.mixed_parts_separate': 'It looks like the whole numbers and the fractions were worked on apart. Treat each mixed number as one fraction.',
    'frac.wholes_dropped': 'It looks like the whole numbers were left out. They are part of each mixed number.',
    'frac.wrong_way_up': 'It looks like the fraction is upside down. The part goes on the top and the whole goes on the bottom.',
    'frac.units_differ': 'The two amounts are in different units. Change them to the same unit before you write the fraction.',
    'frac.hcf_not_used': 'That is the highest common factor. Use it to divide the top and the bottom of the fraction.',
    'frac.one_part_divided': 'It looks like only the top was divided. The bottom needs the same division.',
    'pct.wrong_way_round': 'It looks like the amounts are swapped over. The part is divided by the whole.',
    'int.compound_for_simple': 'It looks like compound interest was worked out. Simple interest is the same amount every year.',
    'int.one_year_only': 'It looks like only one year of interest was used. The interest is paid for every year.',
    'int.principal_missed': 'That is the interest only. The question asks for the total in the account.',
    'int.total_for_interest': 'That is the total in the account. The question asks for the interest only.',
    'int.difference_missed': 'That is the compound interest on its own. The question asks how much more it is than the simple interest.',
    'mf.multiple_not_above': 'That multiple is not greater than the number in the question. Look at the next one up.',
    'mf.count_ends_missed': 'The smallest and the largest factor count too. Check that both are in the list.',
    'mf.count_pairs': 'That counts pairs of factors. The question asks for the number of factors.',
    'mf.count_from_zero': 'That counts the multiples below the smaller number as well. Only count the ones between the two numbers.',
    'mf.square_not_smallest': 'That does make a square number, but it is not the smallest that does. Look at the prime factors.',
    'mf.square_root_used': 'It looks like the square root was used. Look for the prime factors that are not in pairs.',
    'mf.powers_added': 'It looks like the powers were added. Count the choices for each prime, then combine the choices.',
    'mf.powers_not_plus_one': 'Check the choices for each prime. A factor can use none of it, one copy, two, and so on up to the full power.',
    'mf.laps_swapped': 'Check which runner has run which number of laps. The runner with the shorter lap time has run more laps.',
    'mf.laps_times': 'Those are the lap times. The question asks how many laps each runner has run.',
    'num.reciprocal_negative': 'The answer is not the negative of the number. Turn the fraction upside down instead.',
    'num.reciprocal_same': 'That is the number itself. The answer times this number should make one.',
    'num.counting_added': 'It looks like the choices were added. Each choice of one item can go with every choice of the others.',
    'num.counting_stage_missed': 'A stage has been left out. Every choice in the question has to be included.',
    'ratio.difference_as_part': 'It looks like the difference was used as one part. The difference is a number of parts.',
    'ratio.square_as_linear': 'It looks like y was treated as growing in step with x. Here y goes with x squared.',
    'ratio.middle_not_matched': 'The number in both ratios has to be the same before they can be joined. Make it match first.',
    'alg.perimeter_two_sides': 'It looks like the perimeter was used as the sum of only two sides. Count every side of the shape.',
    'alg.x_terms_counted': 'Check the x terms. A number in front of x says how many x there are.',
    'alg.negative_length': 'A length cannot be negative. Check which solution fits the shape.',
    'mf.exponents_swapped': 'It looks like the powers were matched to the other primes. Check which prime each letter belongs to.',
    'alg.form_numbers_swapped': 'It looks like the numbers were matched to the other items. Each number goes with the item it counts.',
    'alg.form_times_added': 'It looks like "times as old" was read as "older than". Times means multiply, not add on.',
    'alg.form_one_length': 'It looks like only one width and one length were added. A rectangle has two of each.',
    'bidmas.missing_inverse': 'Check each step of working backwards. Use the opposite of what the question does.',
    'bidmas.fraction_bar': 'A fraction bar works like brackets. The top line and the bottom line are each worked out before dividing.',
    'surd.square_coefficient_missed': 'The number in front is squared as well as the root. Check the number in front.',
    'dec.rounded_not_difference': 'That is the rounded value. The question asks for the difference between it and the original.',
    # Phase 3 batch B
    'alg.expression_sum': 'It looks like x and y were added. Check what the expression asks you to do with the two numbers.',
    'alg.parallel_one_term': 'It looks like the y term was left as it was. Multiplying an equation multiplies every term in it.',
    'alg.rate_not_divided': 'That is what the amounts add up to. Divide by the difference in the rates to find the number of units.',
    'alg.fee_missed': 'It looks like the fixed fee was left out. It is paid on top of the charge for each unit.',
    'alg.age_future': 'Those are the ages after the years have passed. The question asks for the ages now.',
    'alg.sub_one_term': 'It looks like only one term of each equation was used. Both letters take their numbers.',
    'cts.constant_not_adjusted': 'The squared bracket makes a constant of its own when it is expanded. Allow for it.',
    'cts.square_added': 'The constant from the bracket is taken away from the number at the end, not added to it.',
    'cts.a_square_signed': 'The bracket is being taken away, so the number it makes has to be put back. Check which way that goes.',
    'cts.roots_sign': 'Check the sign when the number is moved to the other side of the equation. A square cannot be negative.',
    'cts.vertex_constant_only': 'The constant comes from expanding the bracket as well as from the number added on. Check that the squared term is in it.',
    'qsim.x_not_y': 'Those are the x-values you were given. The question asks for the y-values.',
    'qsim.circle_y_squared': 'The circle equation gives y squared. The line gives y directly.',
    'qsim.discriminant_four': 'Check the formula for the number of solutions. Each part of it has to be included.',
    'qsim.midpoint_curve': 'The midpoint is not on the curve. Use the mean of the two y-values.',
    'af.undefined_not_divided': 'Check the last step. Once the number is moved across, the x still has a number multiplying it.',
    'fn.inverse_applied': 'That is f applied to the number. The inverse goes the other way.',
    'fn.inverse_sign': 'Undo adding by taking away, and undo taking away by adding. Check the sign.',
    'eq.iterate_constant_once': 'The whole formula is used at each step, including the number that is added on.',
    'eq.iterate_reciprocal': 'Use the whole formula at each step. The number added on comes in as well.',
    'eq.change_constant_sign': 'Check the sign of the last number in the formula when you put each value in.',
    # Phase 3 batch B review (2026-10-28)
    'fn.negative_not_bracketed': 'Put the negative number in brackets when you substitute. Taking away a negative number adds.',
    'cts.min_x_not_y': 'That is the x-value where the minimum is. The question asks for the least value itself.',
    'cts.a_not_multiplied': 'The number outside the bracket multiplies the square as well. Take away that many squares.',
    'alg.bracket_not_all': 'The number in front of the bracket multiplies each part inside it.',
    # Phase 3 batch C1 (statistics, probability, graphs, ratio, trigonometry, Pythagoras)
    'stats.two_way_other_way': 'That adds the other way across the table. Check whether the question asks for a row or a column.',
    'stats.two_way_part_only': 'That is one row or one column. The question asks about everyone, so add every number in the table.',
    'stats.two_way_wrong_total': 'Check which total the missing value belongs to. Use the total of its own row or column.',
    'stats.two_way_two_missing': 'That line has two values missing, so it cannot give one of them yet. Start with a line that has one gap.',
    'stats.percent_wrong_total': 'Check which group the percentage is of. Divide by the total of that group, not by another total.',
    'stats.leaf_only': 'That is only the leaf. Put the stem in front of it to make the full value.',
    'stats.median_middle_row': 'That is the middle row of the table. The median is the middle item once every frequency is counted.',
    'stats.median_position_typed': 'That is the position of the median, not its value. Count down the frequencies to that position.',
    'stats.missing_mean_of_known': 'That is the mean of the values given. Use the mean to find what all the values add up to first.',
    'stats.missing_count_short': 'The mean was multiplied by one fewer than the number of values. The missing value counts in the total too.',
    'stats.mean_of_means': 'That is the mean of the two means. The groups are different sizes, so combine the totals first.',
    'stats.proportion_upside_down': 'It looks like the proportion is upside down. The fraction is the number counted over the sample size.',
    'stats.recapture_upside_down': 'Check the proportion. The fraction tagged in the second catch equals the number tagged over the whole group.',
    'stats.polygon_class_end': 'It looks like the end of each class was used. The points are plotted at the midpoints, so use those.',
    'stats.polygon_freq_mean': 'That is the mean of the frequencies. The mean of the data uses each midpoint times its frequency.',
    'stats.polygon_peak_only': 'That is the highest point only. The total needs the frequency of every point added up.',
    'stats.series_all_points': 'That uses every point on the graph. Only the four points of the year asked for count.',
    'stats.series_not_divided': 'That is the total of the four values. A mean is the total shared out equally, so divide by how many there are.',
    'prob.space_distinct_totals': 'Each total can happen in more than one way. Count the cells in the table, not the different totals.',
    'prob.tree_total_not_group': 'Each pair of branches adds up to the number at the start of that pair, not the overall total.',
    'prob.tree_wrong_group': 'Check which box the branch comes from. Take the value away from the box at the start of its own pair.',
    'prob.condition_wrong_group': 'The condition in the question fixes the total. Divide by the number of people who meet that condition.',
    'prob.two_way_group_total': 'That is out of one group only. A choice from everyone has the whole table as its total.',
    'prob.two_way_one_cell': 'That is one cell of the table only. The event covers a whole row or column, so add along it.',
    'prob.union_as_intersection': 'A ∪ B is all of A and all of B, overlap included. Only the overlap is A ∩ B.',
    'prob.intersection_as_union': 'A ∩ B is only the overlap. All of both circles together is A ∪ B.',
    'prob.complement_ignored': 'The dash means not in that set. Leave out the part that overlaps the other circle.',
    'gr.circle_radius_not_squared': 'k is the radius squared. Square the radius, or add the squares of the coordinates.',
    'gr.circle_coords_added': 'It looks like the coordinates were added. Square each one first, then add the squares.',
    'gr.vt_area_for_gradient': 'That is the area under that part of the graph. Acceleration is the gradient of the line.',
    'gr.vt_gradient_for_area': 'That is the gradient of the line. Distance is the area between the graph and the time axis.',
    'gr.vt_whole_rectangle': 'That treats the speed as constant for the whole journey. Split the area into the shapes under the line.',
    'gr.vt_middle_only': 'That is only the middle part of the journey. The two sloping parts also cover distance.',
    'gr.shift_wrong_way': 'The sign inside the bracket works the other way round. f(x + a) moves the graph left, f(x − a) moves it right.',
    'gr.shift_inside_outside': 'A number added outside f(x) moves the graph up or down. It changes y, not x.',
    'gr.exp_a_at_one': 'a is the value of y where the curve crosses the y-axis.',
    'gr.exp_b_not_divided': 'b is the multiplier from one x value to the next. Divide a y value by the y value before it.',
    'gr.exp_b_difference': 'b is a multiplier, not a difference. Divide one y value by the one before it.',
    'ratio.cube_as_linear': 'It looks like y was treated as growing in step with x. Here y goes with x cubed.',
    'ratio.cube_as_square': 'Here y goes with x cubed, not x squared. Check the power in the formula.',
    'ratio.root_as_linear': 'It looks like y was treated as growing in step with x. Here y goes with the square root of x.',
    'ratio.inverse_square_as_inverse': 'It looks like y was treated as k over x. Here y is k over x squared.',
    'ratio.added_as_part': 'The extra items are not one part of the ratio. Add them to that colour, then set the new pair equal to the new ratio.',
    'ratio.limiting_larger': 'The larger number needs more of the other ingredient than there is. The smaller number is the limit.',
    'trig.graph_other_solution': 'That value is outside the range given. Look for the crossing between the limits in the question.',
    'trig.second_solution_rule': 'Check the second solution. For sine it is 180° minus the first, for cosine 360° minus, for tangent add 180°.',
    'pyth.diagonals_not_halved': 'The diagonals cut each other in half. Use half of each diagonal as the two shorter sides.',
    'pyth.diagonal_squared_not_halved': 'That is the area of the square drawn on the diagonal, not of the square itself.',
    'pyth.half_diagonal_as_side': 'Half the diagonal is not the side. The side comes from the diagonal by Pythagoras.',
    # Phase 3 batch C2 (probability, ratio, graphs and statistics kinds that replaced the last tier echoes)
    'prob.counters_with_replacement': 'The counters are not put back. The second pick has one fewer counter, and one fewer of that colour.',
    'prob.counters_total_typed': 'That is the total number of counters. The question asks how many are the other colour.',
    'prob.union_added': 'The two chances were added as they are. Both events can happen together, so take that overlap away once.',
    'prob.union_product_only': 'That is the chance that both happen. "Or" also counts one happening without the other.',
    'prob.exactly_one_union': 'That counts both events happening as well. Exactly one leaves that overlap out on both sides.',
    'prob.three_with_replacement': 'The counters are not put back. Each pick has one fewer counter than the last.',
    'prob.three_one_colour': 'That is one colour only. Same colour can be all of either colour, so add the two chances.',
    'prob.two_day_independent': 'The chance on the second day depends on the first day. Use the branch that matches.',
    'prob.two_day_both_only': 'That is the chance of both days. At least one day also counts the days on their own.',
    'prob.two_day_one_branch': 'That is one branch only. Exactly one day can happen on either day, so add both branches.',
    'prob.trials_added': 'Chances are not added over the tries. Use one minus the chance of no success at all.',
    'prob.which_bag_joint': 'That is the chance of that bag and that colour together. Divide by the chance of that colour from either bag.',
    'prob.which_bag_counts': 'The bags hold different numbers, so the counts cannot be compared as they are. Use the chance from each bag.',
    'ratio.ages_other_person': 'That is the other person\'s age. Check whose age the question asks for.',
    'ratio.ages_future': 'Those are the ages after the years have passed. The question asks for the age now.',
    'ratio.groups_fractions_added': 'The two fractions are of different groups, so adding them does not work. Find each as a fraction of the whole first.',
    'ratio.groups_one_part': 'That is one of the two groups only. Add the fraction from the other group as well.',
    'ratio.groups_rest_not_taken': 'The second group is the rest of the whole, not the same fraction as the first. Take the first fraction away from one.',
    'ratio.percent_more_half': 'It looks like the total was halved first. Share it so that one part is that much more than the other.',
    'ratio.percent_more_other': 'That is the other person\'s share. Check whose share the question asks for.',
    'ratio.gap_as_part': 'The difference is not one part. It is the difference in parts between the two people, so divide by that.',
    'ratio.cross_multiply_swapped': 'Check which numbers multiply together. Each top goes with the other bottom.',
    'gr.x_intercept_y_intercept': 'That is where the line crosses the y-axis. On the x-axis, y is zero.',
    'gr.coordinate_wrong_letter': 'Check which coordinate was given. Put it in place of the matching letter in the equation.',
    'gr.gradient_rise_only': 'That is the change in y on its own. Divide it by the change in x.',
    'gr.conversion_wrong_way': 'It looks like the conversion went the other way. Start from the value given, on its own axis.',
    'stats.fd_divided': 'The frequency is the height times the width, not the height divided by it.',
    'stats.fd_width_typed': 'That is the width of the class. Use the frequency with it.',
}

TRUTH: dict = {}
PART_TRUTH: dict = {}
PART_TOKENS: dict = {}
PART_RULES: list = []
RULES: list = []
ECHO_OK: set = set()
DECIMAL_TOKENS = frozenset({'len'})
PAIR_TRUTH: dict = {}
PAIR_RULES: list = []


def _i(i, key):
    return F(i[key])


def part(family, truth, decimal=(), integer=()):
    """Register a multi-box family: ``truth(i)`` is the list of correct values (``None`` for a box not modelled).
    ``decimal`` and ``integer`` name the boxes that keep the question's decimal places, or are whole numbers."""
    def vector(i):
        return [None if v is None else F(v) for v in truth(i)]

    def tokens(i):
        return ['len' if k in decimal else ('bearing' if k in integer else 'v') for k in range(len(truth(i)))]
    PART_TRUTH[family] = vector
    PART_TOKENS[family] = tokens


def slip(rule_id, message, family, fn, echo=False):
    """Register a slip of a multi-box family: ``fn(i)`` is a list of vectors (a vector has ``None`` where there is no slip)."""
    def wrapped(i, pi=None):
        out = []
        for vec in fn(i):
            out.append([None if v is None else (F(v) if not isinstance(v, (list, tuple)) else [F(x) for x in v])
                        for v in vec])
        return out
    PART_RULES.append(_r(rule_id, message, [family], wrapped))
    if echo:
        ECHO_OK.add(rule_id)


def scalar(family, truth):
    """Register a one-value family: ``truth(i, pi)`` is the correct answer."""
    TRUTH[family] = lambda i, pi: F(truth(i, pi))


def scalar_slip(rule_id, message, family, fn, echo=False):
    """Register a slip of a one-value family: ``fn(i, pi)`` is a list of the values it reaches."""
    RULES.append(_r(rule_id, message, [family], lambda i, pi: [F(v) for v in fn(i, pi)]))
    if echo:
        ECHO_OK.add(rule_id)


def pair(family, truth):
    PAIR_TRUTH[family] = lambda i: tuple(F(v) for v in truth(i))


def pair_slip(rule_id, message, family, fn, echo=False):
    """``fn(i)`` is a list of (x, y) pairs."""
    PAIR_RULES.append(_r(rule_id, message, [family], lambda i, pi=None: [(F(a), F(b)) for a, b in fn(i)]))
    if echo:
        ECHO_OK.add(rule_id)


# =============================================================================================
# Circle theorems
# =============================================================================================

def _c(i):
    return _i(i, 'centre')


def _a(i):
    return _i(i, 'angle')


part('circ_half', lambda i: [_a(i) / 2])
slip('circ.half_doubled', 'circ.centre_double', 'circ_half', lambda i: [[_a(i) * 2]])
part('circ_double', lambda i: [_a(i) * 2])
slip('circ.double_halved', 'circ.centre_double', 'circ_double', lambda i: [[_a(i) / 2]])
part('circ_half_twice', lambda i: [_c(i) / 2, _c(i) / 2])
slip('circ.half_twice_doubled', 'circ.centre_double', 'circ_half_twice', lambda i: [[_c(i) * 2, _c(i) * 2]])
part('circ_semicircle_90', lambda i: [90])
slip('circ.semicircle_straight', 'circ.semicircle_right', 'circ_semicircle_90', lambda i: [[180]])
part('circ_semi_third', lambda i: [90 - _a(i)])
slip('circ.semi_third_180', 'circ.semicircle_third', 'circ_semi_third', lambda i: [[180 - _a(i)]])
part('circ_alt_semicircle', lambda i: [_a(i), 90 - _a(i)])
slip('circ.alt_semicircle_180', 'circ.semicircle_third', 'circ_alt_semicircle', lambda i: [[None, 180 - _a(i)]])
part('circ_opposite', lambda i: [180 - _a(i)])
slip('circ.opposite_equal', 'circ.opposite_equal', 'circ_opposite', lambda i: [[_a(i)]], echo=True)
part('circ_cyclic2', lambda i: [180 - _i(i, 'a'), 180 - _i(i, 'b')])
slip('circ.cyclic2_equal', 'circ.opposite_equal', 'circ_cyclic2', lambda i: [[_i(i, 'a'), _i(i, 'b')]], echo=True)
part('circ_cyclic_ext', lambda i: [180 - _a(i), _a(i)])
slip('circ.cyclic_ext_equal', 'circ.opposite_equal', 'circ_cyclic_ext', lambda i: [[_a(i), None]], echo=True)
part('circ_cyclic_parallel', lambda i: [180 - _a(i), 180 - _a(i)])
# review 2026-10-27: the second box (angle ABC) is next to DAB, not opposite it; its pair with DAB is co-interior (AD and
# BC are parallel), so the opposite-angles line is said for the first box only and the second box has its own line
slip('circ.cyclic_parallel_equal', 'circ.opposite_equal', 'circ_cyclic_parallel', lambda i: [[_a(i), None]], echo=True)
slip('circ.cyclic_parallel_cointerior', 'ang.cointerior_total', 'circ_cyclic_parallel', lambda i: [[None, _a(i)]], echo=True)
part('circ_centre_cyclic', lambda i: [_c(i) / 2, 180 - _c(i) / 2])
slip('circ.centre_cyclic_equal', 'circ.opposite_equal', 'circ_centre_cyclic', lambda i: [[None, _c(i) / 2]])


def _alg(i):
    a1, b1, a2, b2 = (_i(i, k) for k in ('a1', 'b1', 'a2', 'b2'))
    x = (180 - b1 - b2) / (a1 + a2)
    return [x, a1 * x + b1, a2 * x + b2]


def _alg_equal(i):
    a1, b1, a2, b2 = (_i(i, k) for k in ('a1', 'b1', 'a2', 'b2'))
    if a1 == a2:
        return []
    x = (b2 - b1) / (a1 - a2)
    return [[x, a1 * x + b1, a2 * x + b2]] if x > 0 else []


part('circ_cyclic_alg', _alg)
slip('circ.cyclic_alg_equal', 'circ.opposite_equal', 'circ_cyclic_alg', _alg_equal)
part('circ_tangent_triangle', lambda i: [90, 90 - _a(i)])
slip('circ.tangent_triangle_180', 'circ.tangent_right', 'circ_tangent_triangle', lambda i: [[None, 180 - _a(i)]])
part('circ_tangent_base', lambda i: [(180 - _i(i, 'apex')) / 2])
slip('circ.tangent_base_whole', 'circ.base_angles_shared', 'circ_tangent_base', lambda i: [[180 - _i(i, 'apex')]])
part('circ_tangents_reflex', lambda i: [180 + _a(i)])
slip('circ.tangents_not_reflex', 'circ.reflex_missed', 'circ_tangents_reflex', lambda i: [[180 - _a(i)]])
part('circ_centre_both', lambda i: [(180 - _c(i)) / 2, _c(i) / 2])
slip('circ.centre_both_whole', 'circ.base_angles_shared', 'circ_centre_both', lambda i: [[180 - _c(i), None]])
slip('circ.centre_both_arc', 'circ.wrong_arc', 'circ_centre_both', lambda i: [[None, (360 - _c(i)) / 2]])
part('circ_centre_minor', lambda i: [(180 - _c(i)) / 2, (360 - _c(i)) / 2])
slip('circ.centre_minor_whole', 'circ.base_angles_shared', 'circ_centre_minor', lambda i: [[180 - _c(i), None]])
slip('circ.centre_minor_arc', 'circ.wrong_arc', 'circ_centre_minor', lambda i: [[None, _c(i) / 2]])
part('circ_both_arcs', lambda i: [_c(i) / 2, (360 - _c(i)) / 2])
slip('circ.both_arcs_swapped', 'circ.wrong_arc', 'circ_both_arcs', lambda i: [[(360 - _c(i)) / 2, _c(i) / 2]])
part('circ_both_arcs_sum', lambda i: [_c(i) / 2, (360 - _c(i)) / 2, 180])
slip('circ.both_arcs_sum_swapped', 'circ.wrong_arc', 'circ_both_arcs_sum',
     lambda i: [[(360 - _c(i)) / 2, _c(i) / 2, None]])
part('circ_reflex_half', lambda i: [_i(i, 'reflex') / 2])
slip('circ.reflex_half_arc', 'circ.wrong_arc', 'circ_reflex_half', lambda i: [[(360 - _i(i, 'reflex')) / 2]])
part('circ_isos_same_seg', lambda i: [(180 - _a(i)) / 2, _a(i)])
slip('circ.isos_same_seg_whole', 'circ.base_angles_shared', 'circ_isos_same_seg', lambda i: [[180 - _a(i), None]])
part('circ_alt_straight', lambda i: [_a(i), 180 - _a(i)])
slip('circ.alt_straight_supplement', 'circ.alt_segment_equal', 'circ_alt_straight', lambda i: [[180 - _a(i), None]])
part('circ_same_seg2', lambda i: [_i(i, 'a'), _i(i, 'b')])
slip('circ.same_seg2_swapped', 'circ.wrong_chord', 'circ_same_seg2', lambda i: [[_i(i, 'b'), _i(i, 'a')]], echo=True)
part('circ_alt_triangle', lambda i: [_a(i), 180 - _a(i) - _i(i, 'bac')])
slip('circ.alt_triangle_missed', 'ang.angle_missed', 'circ_alt_triangle',
     lambda i: [[None, 180 - _a(i)], [None, 180 - _i(i, 'bac')]])
part('circ_two_tangents', lambda i: [180 - _i(i, 'p')])
slip('circ.two_tangents_missed', 'circ.tangents_right_angles', 'circ_two_tangents',
     lambda i: [[270 - _i(i, 'p')], [360 - _i(i, 'p')]])
part('circ_secants', lambda i: [(_i(i, 'far') - _i(i, 'near')) / 2])
slip('circ.secants_added', 'circ.secant_sum', 'circ_secants', lambda i: [[(_i(i, 'far') + _i(i, 'near')) / 2]])
part('circ_chords_angle', lambda i: [(_i(i, 'arc1') + _i(i, 'arc2')) / 2])
slip('circ.chords_subtracted', 'circ.chords_add', 'circ_chords_angle',
     lambda i: [[abs(_i(i, 'arc1') - _i(i, 'arc2')) / 2]])
part('circ_three', lambda i: [(180 - _c(i)) / 2, _c(i) / 2, _c(i) / 2, None])
slip('circ.three_whole', 'circ.base_angles_shared', 'circ_three', lambda i: [[180 - _c(i), None, None, None]])
slip('circ.three_doubled', 'circ.centre_double', 'circ_three', lambda i: [[None, _c(i) * 2, _c(i) * 2, None]])
part('ang_isos_apex', lambda i: [180 - 2 * _i(i, 'base')])
slip('circ.isos_apex_one_base', 'ang.isos_one_base', 'ang_isos_apex', lambda i: [[180 - _i(i, 'base')]])


def _chord_half(i):
    r, d = _i(i, 'r'), _i(i, 'd')
    return sqrtq(r * r - d * d)


part('circ_chord_length', lambda i: [2 * _chord_half(i)], decimal=(0,))
slip('circ.chord_half', 'circ.chord_half', 'circ_chord_length', lambda i: [[_chord_half(i)]])


def _tangent_len(i):
    r, ot = _i(i, 'r'), _i(i, 'ot')
    return sqrtq(ot * ot - r * r)


part('circ_tangent_length', lambda i: [_tangent_len(i)], decimal=(0,))
slip('circ.tangent_length_added', 'pyth.added_for_short', 'circ_tangent_length',
     lambda i: [[sqrtq(_i(i, 'ot') ** 2 + _i(i, 'r') ** 2)]])
part('circ_radius_from_angle', lambda i: [_i(i, 'po') * trig('sin', _i(i, 'apb') / 2)], decimal=(0,))
slip('circ.radius_wrong_ratio', 'trig.wrong_ratio', 'circ_radius_from_angle',
     lambda i: [[_i(i, 'po') * trig('cos', _i(i, 'apb') / 2)]])


# =============================================================================================
# Similarity
# =============================================================================================

def _k(i):
    return _i(i, 'k')


part('sim_scale_length', lambda i: [_k(i) * _i(i, 'length')])
slip('sim.length_squared', 'sim.length_squared', 'sim_scale_length', lambda i: [[_k(i) ** 2 * _i(i, 'length')]])
slip('sim.length_divided', 'sim.direction', 'sim_scale_length', lambda i: [[_i(i, 'length') / _k(i)]])
part('sim_area_k', lambda i: [_i(i, 'area') * _k(i) ** 2])
slip('sim.area_k_power', 'sim.wrong_power', 'sim_area_k',
     lambda i: [[_i(i, 'area') * _k(i)], [_i(i, 'area') * _k(i) ** 3]])
part('sim_area_down', lambda i: [_i(i, 'area') / _k(i) ** 2])
slip('sim.area_down_power', 'sim.wrong_power', 'sim_area_down',
     lambda i: [[_i(i, 'area') / _k(i)], [_i(i, 'area') / _k(i) ** 3]])
part('sim_vol_k', lambda i: [_i(i, 'vol') * _k(i) ** 3])
slip('sim.vol_k_power', 'sim.wrong_power', 'sim_vol_k',
     lambda i: [[_i(i, 'vol') * _k(i)], [_i(i, 'vol') * _k(i) ** 2]])


def _rr(i):
    return _i(i, 'r_to') / _i(i, 'r_from')


part('sim_area_ratio', lambda i: [_i(i, 'area') * _rr(i) ** 2])
slip('sim.area_ratio_power', 'sim.wrong_power', 'sim_area_ratio',
     lambda i: [[_i(i, 'area') * _rr(i)], [_i(i, 'area') * _rr(i) ** 3]])


def _ll(i):
    return _i(i, 'l_large') / _i(i, 'l_small')


part('sim_vol_from_lengths', lambda i: [_i(i, 'vol') * _ll(i) ** 3])
slip('sim.vol_lengths_power', 'sim.wrong_power', 'sim_vol_from_lengths',
     lambda i: [[_i(i, 'vol') * _ll(i)], [_i(i, 'vol') * _ll(i) ** 2]])


def _cube_root(x):
    """The exact rational cube root of a Fraction, or ValueError."""
    def root(n):
        r = round(n ** (1 / 3))
        if r ** 3 != n:
            raise ValueError('not a perfect cube')
        return r
    return Fraction(root(x.numerator), root(x.denominator))


def _dim_truth(i):
    return [_i(i, 'dim_small') * _cube_root(_i(i, 'v_large') / _i(i, 'v_small'))]


part('sim_dim_from_vol', _dim_truth)
slip('sim.dim_not_rooted', 'sim.root_missed', 'sim_dim_from_vol',
     lambda i: [[_i(i, 'dim_small') * _i(i, 'v_large') / _i(i, 'v_small')]])
part('sim_sf', lambda i: [_i(i, 'large') / _i(i, 'small')])
slip('sim.sf_inverted', 'sim.sf_inverted', 'sim_sf', lambda i: [[_i(i, 'small') / _i(i, 'large')]])


def _tri_c(i):
    return 180 - _i(i, 'a') - _i(i, 'b')


part('sim_tri_angles', lambda i: [_tri_c(i), _i(i, 'a'), _i(i, 'b'), _tri_c(i)])
slip('sim.tri_angles_360', 'ang.wrong_total', 'sim_tri_angles',
     lambda i: [[360 - _i(i, 'a') - _i(i, 'b'), None, None, 360 - _i(i, 'a') - _i(i, 'b')]])
slip('sim.tri_angles_sum', 'ang.sum_not_subtracted', 'sim_tri_angles',
     lambda i: [[_i(i, 'a') + _i(i, 'b'), None, None, _i(i, 'a') + _i(i, 'b')]])


def _quad_d(i):
    return 360 - _i(i, 'a') - _i(i, 'b') - _i(i, 'c')


part('sim_quad_angles', lambda i: [_quad_d(i), _i(i, 'a'), _i(i, 'b'), _i(i, 'c'), _quad_d(i)])


slip('sim.quad_angles_sum', 'ang.sum_not_subtracted', 'sim_quad_angles',
     lambda i: [[_i(i, 'a') + _i(i, 'b') + _i(i, 'c'), None, None, None, _i(i, 'a') + _i(i, 'b') + _i(i, 'c')]])
part('sim_overlap', lambda i: [_i(i, 'ab') - _i(i, 'ad'), _i(i, 'ac') - _i(i, 'ae'), _i(i, 'ab') / _i(i, 'ad')])
slip('sim.overlap_inverted', 'sim.sf_inverted', 'sim_overlap', lambda i: [[None, None, _i(i, 'ad') / _i(i, 'ab')]])
part('sim_parallel', lambda i: [_i(i, 'de') * (_i(i, 'ad') + _i(i, 'db')) / _i(i, 'ad')])
slip('sim.parallel_part', 'sim.part_for_whole', 'sim_parallel',
     lambda i: [[_i(i, 'de') * _i(i, 'db') / _i(i, 'ad')]])


def _bpt(i):
    ae = _i(i, 'ac') * _i(i, 'ad') / (_i(i, 'ad') + _i(i, 'db'))
    return [ae, _i(i, 'ac') - ae]


def _bpt_part(i):
    ae = _i(i, 'ac') * _i(i, 'ad') / _i(i, 'db')
    return [[ae, _i(i, 'ac') - ae]]


part('sim_bpt', _bpt)
slip('sim.bpt_part', 'sim.part_for_whole', 'sim_bpt', _bpt_part)


def _alg_prop(i):
    a1, b1, a2, b2 = (_i(i, k) for k in ('a1', 'b1', 'a2', 'b2'))
    top, bottom = _i(i, 'top'), _i(i, 'bottom')
    return [(top * b2 - bottom * b1) / (bottom * a1 - top * a2)]


def _alg_prop_inverted(i):
    a1, b1, a2, b2 = (_i(i, k) for k in ('a1', 'b1', 'a2', 'b2'))
    top, bottom = _i(i, 'top'), _i(i, 'bottom')
    denom = top * a1 - bottom * a2
    return [[(bottom * b2 - top * b1) / denom]] if denom != 0 else []


part('sim_alg_prop', _alg_prop)
slip('sim.alg_prop_inverted', 'ratio.parts_swapped', 'sim_alg_prop', _alg_prop_inverted)
part('sim_chain', lambda i: [_i(i, 'side') * _i(i, 'r2') / _i(i, 'r1') * _i(i, 'r4') / _i(i, 'r3')])
slip('sim.chain_one_step', 'sim.chain_steps', 'sim_chain',
     lambda i: [[_i(i, 'side') * _i(i, 'r2') / _i(i, 'r1')], [_i(i, 'side') * _i(i, 'r4') / _i(i, 'r3')]])
part('sim_frustum', lambda i: [(_i(i, 'radius') ** 2 * _i(i, 'height')
                                - (_i(i, 'radius') * _i(i, 'cut') / _i(i, 'height')) ** 2 * _i(i, 'cut')) / 3])
slip('sim.frustum_whole', 'sim.frustum_whole', 'sim_frustum',
     lambda i: [[_i(i, 'radius') ** 2 * _i(i, 'height') / 3]])


def _quad_prop(i):
    xy, qr, yz = _i(i, 'xy'), _i(i, 'add_qr'), _i(i, 'add_yz')
    b, c = yz - xy, -xy * qr
    disc = b * b - 4 * c
    root = sqrtq(disc)
    if root * root != disc:
        raise ValueError('irrational')
    x = (-b + root) / 2
    return [x, x / xy]


part('sim_quad_prop', _quad_prop)
slip('sim.quad_prop_inverted', 'sim.sf_inverted', 'sim_quad_prop',
     lambda i: [[None, 1 / _quad_prop(i)[1]]])
part('sim_shadow', lambda i: [_i(i, 'h1') * _i(i, 's2') / _i(i, 's1')])
slip('sim.shadow_inverted', 'ratio.inverse_for_direct', 'sim_shadow',
     lambda i: [[_i(i, 'h1') * _i(i, 's1') / _i(i, 's2')]])
slip('sim.shadow_additive', 'ratio.additive', 'sim_shadow',
     lambda i: [[_i(i, 'h1') + _i(i, 's2') - _i(i, 's1')]])


def _sides(i):
    k = _i(i, 'known_new') / _i(i, 'known_old')
    return [k * F(o) for o in i['others']]


part('sim_sides', _sides)
slip('sim.sides_additive', 'ratio.additive', 'sim_sides',
     lambda i: [[F(o) + _i(i, 'known_new') - _i(i, 'known_old') for o in i['others']]])
slip('sim.sides_inverted', 'sim.direction', 'sim_sides',
     lambda i: [[F(o) * _i(i, 'known_old') / _i(i, 'known_new') for o in i['others']]])


def _bisector(i):
    total = _i(i, 'ab') + _i(i, 'ac')
    return [_i(i, 'bc') * _i(i, 'ab') / total, _i(i, 'bc') * _i(i, 'ac') / total]


part('sim_bisector', _bisector)
slip('sim.bisector_swapped', 'ratio.parts_swapped', 'sim_bisector', lambda i: [list(reversed(_bisector(i)))])


def _cone(i):
    k = _i(i, 'r_large') / _i(i, 'r_small')
    return k, _i(i, 'vol'), _i(i, 'sa')


def _cone_vectors(i):
    k, vol, sa = _cone(i)
    return [[vol * k ** 3, sa * k ** 2], [vol * k ** 2, sa * k ** 3], [vol * k, sa * k]]


part('sim_cone_scale', lambda i: [_cone(i)[1] * _cone(i)[0] ** 3, _cone(i)[2] * _cone(i)[0] ** 2])
slip('sim.cone_power', 'sim.wrong_power', 'sim_cone_scale', lambda i: _cone_vectors(i)[1:])


def _model(i):
    scale = _i(i, 'scale')
    return [_i(i, 'vol_cm3') * scale ** 3 / 10 ** 6, _i(i, 'flr_cm2') * scale ** 2 / 10 ** 4]


part('sim_model', _model)
slip('sim.model_not_converted', 'unit.not_converted', 'sim_model',
     lambda i: [[_i(i, 'vol_cm3') * _i(i, 'scale') ** 3, _i(i, 'flr_cm2') * _i(i, 'scale') ** 2]])
slip('sim.model_power', 'sim.wrong_power', 'sim_model',
     lambda i: [[_i(i, 'vol_cm3') * _i(i, 'scale') ** 2 / 10 ** 6, _i(i, 'flr_cm2') * _i(i, 'scale') ** 3 / 10 ** 4]])


def _sa_k(i):
    return sqrtq(_i(i, 'sa_large') / _i(i, 'sa_small'))


part('sim_vol_sa', lambda i: [_sa_k(i), _i(i, 'vol') * _sa_k(i) ** 3])
slip('sim.vol_sa_not_rooted', 'sim.area_ratio_not_rooted', 'sim_vol_sa',
     lambda i: [[_i(i, 'sa_large') / _i(i, 'sa_small'), None]])
slip('sim.vol_sa_power', 'sim.wrong_power', 'sim_vol_sa', lambda i: [[None, _i(i, 'vol') * _sa_k(i) ** 2]])


def _map_value(i):
    per = {'km': 100000, 'm': 100, 'cm': 1}[i['unit_word']]
    return _i(i, 'scale') * _i(i, 'map_cm') / per


part('sim_map_length', lambda i: [_map_value(i)])
slip('sim.map_not_converted', 'unit.not_converted', 'sim_map_length',
     lambda i: [[_i(i, 'scale') * _i(i, 'map_cm')]])
slip('sim.map_divided', 'ratio.scale_direction', 'sim_map_length', lambda i: [[_i(i, 'map_cm') / _i(i, 'scale')]])
part('sim_map_area', lambda i: [_i(i, 'map_cm2') * _i(i, 'scale') ** 2 / 10 ** 10])
slip('sim.map_area_linear', 'sim.wrong_power', 'sim_map_area',
     lambda i: [[_i(i, 'map_cm2') * _i(i, 'scale') / 10 ** 5]])


# =============================================================================================
# Ratio and proportion
# =============================================================================================

def _shares(i):
    parts = [F(p) for p in i['parts']]
    if not 2 <= len(parts) <= 6 or any(p <= 0 for p in parts):
        raise ValueError('parts')
    total = F(i['total'] if 'total' in i else i['budget'])
    return total, parts, [total * p / sum(parts) for p in parts]


def _ratio_family(name, boxes, rules=('equal', 'reversed')):
    """boxes(i, shares, unit) -> the answer boxes; the slips share the amount out equally, or swap the parts."""
    def truth(i):
        total, parts, sh = _shares(i)
        return boxes(i, sh, total / sum(parts))

    def equal(i):
        total, parts, _ = _shares(i)
        n = len(parts)
        return [boxes(i, [total / n] * n, total / n)]

    def reversed_(i):
        total, parts, sh = _shares(i)
        return [boxes(i, list(reversed(sh)), total / sum(parts))]
    part(name, truth)
    if 'equal' in rules:
        slip(f'ratio.{name}_equal', 'ratio.shared_equally', name, equal)
    if 'reversed' in rules:
        slip(f'ratio.{name}_swapped', 'ratio.parts_swapped', name, reversed_)


_ratio_family('ratio_share', lambda i, sh, u: list(sh))
_ratio_family('ratio_garden', lambda i, sh, u: [sh[1], sh[2], abs(sh[0] - sh[2])])
_ratio_family('ratio_share_diff', lambda i, sh, u: [sh[0], sh[1], abs(sh[0] - sh[1])])
_ratio_family('ratio_prize', lambda i, sh, u: [u, sh[0], abs(sh[0] - sh[2])])
_ratio_family('ratio_holiday', lambda i, sh, u: [sh[1], sh[2], sh[0] * F(i['rate'])])
_ratio_family('ratio_concert', lambda i, sh, u: [sh[0], sh[1], sh[0] * F(i['adult_price']) + sh[1] * F(i['child_price'])])


def _merge(i, a_parts, b_parts):
    sa, sb = F(i['students_a']), F(i['students_b'])
    return [sa * a_parts[1] / sum(a_parts), sb * b_parts[0] / sum(b_parts)]


part('ratio_merge', lambda i: _merge(i, [F(p) for p in i['a_parts']], [F(p) for p in i['b_parts']]) + [None])
slip('ratio.merge_swapped', 'ratio.parts_swapped', 'ratio_merge',
     lambda i: [_merge(i, [F(p) for p in reversed(i['a_parts'])], [F(p) for p in reversed(i['b_parts'])]) + [None]])


def _hike(i):
    return [F(i['cm1']) * F(i['scale']) / 100, F(i['cm2']) * F(i['scale']) / 100,
            (F(i['cm1']) + F(i['cm2'])) * F(i['scale']) / 10 ** 5]


part('ratio_hike', _hike)
slip('ratio.hike_not_converted', 'unit.not_converted', 'ratio_hike',
     lambda i: [[F(i['cm1']) * F(i['scale']), F(i['cm2']) * F(i['scale']), None]])
slip('ratio.hike_divided', 'ratio.scale_direction', 'ratio_hike',
     lambda i: [[F(i['cm1']) / F(i['scale']), F(i['cm2']) / F(i['scale']), None]])
part('prop_plumbers', lambda i: [F(i['w1']) * F(i['h1']), F(i['w1']) * F(i['h1']) / F(i['w2']),
                                 F(i['w1']) * F(i['h1']) / F(i['h3'])])
slip('prop.plumbers_direct', 'ratio.direct_for_inverse', 'prop_plumbers',
     lambda i: [[None, F(i['h1']) * F(i['w2']) / F(i['w1']), F(i['w1']) * F(i['h3']) / F(i['h1'])]])
part('fdp_dec_and_pct', lambda i: [F(i['a']) / F(i['b']), F(i['a']) / F(i['b']) * 100])
slip('fdp.dec_pct_swapped', 'gen.as_decimal', 'fdp_dec_and_pct', lambda i: [[F(i['a']) / F(i['b']) * 100, None]])
slip('fdp.pct_decimal', 'gen.as_percentage', 'fdp_dec_and_pct', lambda i: [[None, F(i['a']) / F(i['b'])]])
slip('fdp.dec_inverted', 'gen.reciprocal_fraction', 'fdp_dec_and_pct', lambda i: [[F(i['b']) / F(i['a']), None]])


# =============================================================================================
# Angles in plane figures
# =============================================================================================

part('ang_kite', lambda i: [360 - _i(i, 'a') - 2 * _i(i, 'b'), _i(i, 'b')])
slip('ang.kite_one_equal', 'ang.kite_pair', 'ang_kite', lambda i: [[360 - _i(i, 'a') - _i(i, 'b'), None]])
part('ang_isos_parallel', lambda i: [180 - 2 * _i(i, 'base'), _i(i, 'base')])
slip('ang.isos_parallel_one_base', 'ang.isos_one_base', 'ang_isos_parallel',
     lambda i: [[180 - _i(i, 'base'), None]])
slip('ang.isos_parallel_supplement', 'ang.parallel_equal', 'ang_isos_parallel',
     lambda i: [[None, 180 - _i(i, 'base')]])
part('poly_int_ext', lambda i: [(_i(i, 'n') - 2) * 180 / _i(i, 'n'), 360 / _i(i, 'n')])
slip('poly.int_ext_swapped_interior', 'ang.exterior_for_interior', 'poly_int_ext', lambda i: [[360 / _i(i, 'n'), None]])
slip('poly.int_ext_swapped_exterior', 'ang.interior_for_exterior_poly', 'poly_int_ext',
     lambda i: [[None, (_i(i, 'n') - 2) * 180 / _i(i, 'n')]])
_TOTALS = {'straight line': 180, 'point': 360, 'triangle': 180, 'quadrilateral': 360, 'complementary': 90}


def _ang_alg(i):
    terms = [F(t) for t in i['terms']]
    pairs = [(terms[k], terms[k + 1]) for k in range(0, len(terms), 2)]
    total = _TOTALS[i['rule_word']]
    x = (total - sum(b for _, b in pairs)) / sum(a for a, _ in pairs)
    return pairs, x


def _ang_alg_vector(i, total):
    pairs, _ = _ang_alg(i)
    x = (total - sum(b for _, b in pairs)) / sum(a for a, _ in pairs)
    return [x] + [a * x + b for a, b in pairs]


def _ang_alg_totals(i):
    return [_ang_alg_vector(i, t) for t in (90, 180, 360) if t != _TOTALS[i['rule_word']]]


part('ang_alg', lambda i: _ang_alg_vector(i, _TOTALS[i['rule_word']]))
slip('ang.alg_wrong_total', 'ang.wrong_total', 'ang_alg', _ang_alg_totals)


def _poly_alg_vector(i, total):
    offsets, fixed = [F(o) for o in i['offsets']], F(i['fixed'])
    x = (total - sum(offsets) - fixed) / len(offsets)
    return [x] + [x + o for o in offsets] + [fixed]


part('poly_alg', lambda i: _poly_alg_vector(i, (F(i['sides']) - 2) * 180))
slip('poly.alg_wrong_sum', 'ang.polygon_n', 'poly_alg',
     lambda i: [_poly_alg_vector(i, F(i['sides']) * 180), _poly_alg_vector(i, (F(i['sides']) - 1) * 180)])
part('circ_semicircle', lambda i: [90 - _a(i), 90])
slip('circ.semicircle_first_180', 'circ.semicircle_third', 'circ_semicircle', lambda i: [[180 - _a(i), None]])
slip('circ.semicircle_straight_box', 'circ.semicircle_right', 'circ_semicircle', lambda i: [[None, 180]])
part('sim_fields', lambda i: [_i(i, 'bc') * _i(i, 'pq') / _i(i, 'ab'), _i(i, 'ang_b')])
slip('sim.fields_additive', 'ratio.additive', 'sim_fields',
     lambda i: [[_i(i, 'bc') + _i(i, 'pq') - _i(i, 'ab'), None]])
slip('sim.fields_inverted', 'sim.direction', 'sim_fields', lambda i: [[_i(i, 'bc') * _i(i, 'ab') / _i(i, 'pq'), None]])
slip('sim.fields_angle_scaled', 'sim.angles_kept', 'sim_fields',
     lambda i: [[None, _i(i, 'ang_b') * _i(i, 'pq') / _i(i, 'ab')]])
part('circ_cyclic3', lambda i: [180 - _i(i, 'a1'), 180 - _i(i, 'a2'), 2 * _i(i, 'a1')])
slip('circ.cyclic3_equal', 'circ.opposite_equal', 'circ_cyclic3', lambda i: [[_i(i, 'a1'), _i(i, 'a2'), None]], echo=True)
slip('circ.cyclic3_centre', 'circ.centre_double', 'circ_cyclic3', lambda i: [[None, None, _i(i, 'a1')]], echo=True)
part('ang_bearing_turn', lambda i: [_i(i, 'b1') + _i(i, 'turn'), 180 - _i(i, 'turn')], integer=(0, 1))
slip('ang.turn_anticlockwise', 'brg.anticlockwise', 'ang_bearing_turn',
     lambda i: [[(_i(i, 'b1') - _i(i, 'turn')) % 360, None]])
part('circ_alt_segment', lambda i: [_i(i, 'alpha'), 2 * _i(i, 'alpha')])
slip('circ.alt_segment_not_doubled', 'circ.centre_double', 'circ_alt_segment', lambda i: [[None, _i(i, 'alpha')]],
     echo=True)
slip('circ.alt_segment_supplement', 'circ.alt_segment_equal', 'circ_alt_segment', lambda i: [[180 - _i(i, 'alpha'), None]])
part('circ_arcs', lambda i: [_c(i) / 2, (360 - _c(i)) / 2])
slip('circ.arcs_swapped', 'circ.wrong_arc', 'circ_arcs', lambda i: [[(360 - _c(i)) / 2, _c(i) / 2]])
part('circ_tangent_chord', lambda i: [_i(i, 'alpha'), 180 - _i(i, 'alpha') - _i(i, 'beta')])
slip('circ.tangent_chord_missed', 'ang.angle_missed', 'circ_tangent_chord',
     lambda i: [[None, 180 - _i(i, 'alpha')], [None, 180 - _i(i, 'beta')]])
slip('circ.tangent_chord_supplement', 'circ.alt_segment_equal', 'circ_tangent_chord',
     lambda i: [[180 - _i(i, 'alpha'), None]])


def _circ_alg(i):
    a, b, c, d = (_i(i, k) for k in 'abcd')
    x = (2 * d - b) / (a - 2 * c)
    return [x, a * x + b, c * x + d]


def _circ_alg_halved(i):
    a, b, c, d = (_i(i, k) for k in 'abcd')
    if a == c / 2:
        return []
    x = (d / 2 - b) / (a - c / 2)
    return [[x, a * x + b, c * x + d]] if x > 0 else []


part('circ_alg', _circ_alg)
slip('circ.alg_halved', 'circ.centre_double', 'circ_alg', _circ_alg_halved)


# =============================================================================================
# Multiples and factors, decimals, number
# =============================================================================================

def _gcd(a, b):
    return math.gcd(int(a), int(b))


def _lcm(a, b):
    return math.lcm(int(a), int(b))


scalar('mf_multiple', lambda i, pi: _i(i, 'n') * _i(i, 'k'))
scalar_slip('mf.multiple_added', 'op.multiply_needed', 'mf_multiple', lambda i, pi: [_i(i, 'n') + _i(i, 'k')])
scalar('num_hcf', lambda i, pi: _gcd(i['a'], i['b']))
scalar_slip('mf.hcf_lcm', 'mf.lcm_for_hcf', 'num_hcf', lambda i, pi: [_lcm(i['a'], i['b'])])
scalar('num_lcm', lambda i, pi: _lcm(i['a'], i['b']))
scalar_slip('mf.lcm_hcf', 'mf.hcf_for_lcm', 'num_lcm', lambda i, pi: [_gcd(i['a'], i['b'])])
scalar_slip('mf.lcm_product', 'mf.product_for_lcm', 'num_lcm', lambda i, pi: [_i(i, 'a') * _i(i, 'b')])
scalar('mf_common_factor_count', lambda i, pi: sum(1 for d in range(1, _gcd(i['a'], i['b']) + 1)
                                                  if _gcd(i['a'], i['b']) % d == 0))
scalar_slip('mf.count_hcf', 'mf.hcf_for_count', 'mf_common_factor_count', lambda i, pi: [_gcd(i['a'], i['b'])])
scalar('mf_hcf3', lambda i, pi: _gcd(_gcd(i['a'], i['b']), i['c']))
scalar_slip('mf.hcf3_lcm', 'mf.lcm_for_hcf', 'mf_hcf3', lambda i, pi: [math.lcm(int(i['a']), int(i['b']), int(i['c']))])
scalar_slip('mf.hcf3_two_only', 'mf.third_ignored', 'mf_hcf3', lambda i, pi: [_gcd(i['a'], i['b']), _gcd(i['b'], i['c'])])
scalar('mf_lcm3', lambda i, pi: math.lcm(int(i['a']), int(i['b']), int(i['c'])))
scalar_slip('mf.lcm3_hcf', 'mf.hcf_for_lcm', 'mf_lcm3', lambda i, pi: [_gcd(_gcd(i['a'], i['b']), i['c'])])
scalar_slip('mf.lcm3_two_only', 'mf.third_ignored', 'mf_lcm3', lambda i, pi: [_lcm(i['a'], i['b']), _lcm(i['b'], i['c'])])
scalar('mf_other_number', lambda i, pi: _i(i, 'hcf') * _i(i, 'lcm') / _i(i, 'known'))
scalar_slip('mf.other_lcm_only', 'mf.product_rule_missed', 'mf_other_number', lambda i, pi: [_i(i, 'lcm') / _i(i, 'known')])


def _dp(x):
    text = str(x)
    return len(text.split('.')[1]) if '.' in text and 'e' not in text.lower() else 0


def _misaligned(x, dp):
    """The number as a pupil reads it when the digits are lined up on the right: 8.6 with two places is 8.06."""
    v = F(x)
    own = _dp(x)
    if own >= dp or own == 0:
        return v
    whole = int(abs(v))
    digits = str(int((abs(v) - whole) * 10 ** own)).zfill(dp)
    out = whole + Fraction(int(digits), 10 ** dp)
    return -out if v < 0 else out


def _directed_misaligned(i, pi):
    a, b = i['a'], i['b']
    dp = max(_dp(a), _dp(b))
    x, y = _misaligned(a, dp), _misaligned(b, dp)
    return [x + y if i['op'] == '+' else x - y]


RULES.append(_r('dec.directed_not_aligned', 'dec.not_aligned', ['num_directed'], _directed_misaligned))


def _arith_terms(expr):
    """[(sign, number text)] for a plain sum or difference of numbers such as '4.36 + 3.03 - 8.6', else ValueError.

    Review 2026-10-27: the old reader took the numbers and signs out of any expression, so "(-4)^3" was read as
    -4 + 3 and the pupil was told to line up the decimal points. Only numbers joined by + and - are read now; a
    bracket, a power, a product or a letter means no slip.
    """
    import re
    text = str(expr).replace('\u2212', '-').strip()
    if len(text) > 60 or not re.fullmatch(r'-?\d+(?:\.\d+)?(?:\s*[+-]\s*\d+(?:\.\d+)?)+', text):
        raise ValueError('not a plain sum of numbers')
    tokens = re.findall(r'(\d+(?:\.\d+)?)|([+-])', text)
    terms, sign = [], 1
    for num, op in tokens:
        if op:
            sign = 1 if op == '+' else -1
        else:
            terms.append((sign, num))
            sign = 1
    if not 2 <= len(terms) <= 5:
        raise ValueError('not a sum')
    return terms


def _arith_misaligned(i, pi):
    terms = _arith_terms(i['expr'])
    dp = max(_dp(t) for _, t in terms)
    return [sum(sg * _misaligned(t, dp) for sg, t in terms)]


RULES.append(_r('dec.arith_not_aligned', 'dec.not_aligned', ['arith'], _arith_misaligned))


def _printed_short(text, numbers):
    """True when every number that the slip reads with too few decimal places is printed that way in the question.

    Review 2026-10-27: "An item costs \u00a311.36. How much change from \u00a312.50?" is recorded as 12.5 - 11.36, but the
    question prints 12.50, already lined up, so "line up the decimal points" would not fit. The slip needs the short
    form (8.6 beside 3.95) to be what the pupil reads.
    """
    import re
    printed = set(re.findall(r'\d+(?:\.\d+)?', str(text).replace(',', '')))
    dp = max(_dp(x) for x in numbers)
    short = [x for x in numbers if 0 < _dp(x) < dp]
    return bool(short) and all(str(x).lstrip('-') in printed for x in short)


# rule id -> (question text, inputs) -> bool: the rule speaks only when the question reads as the slip needs
TEXT_GUARDS = {
    'dec.directed_not_aligned': lambda text, i: _printed_short(text, [i['a'], i['b']]),
    'dec.arith_not_aligned': lambda text, i: _printed_short(text, [t for _, t in _arith_terms(i['expr'])]),
}


def _pow10_direction(i, pi):
    n, p = F(str(i['n'])), _i(i, 'p')
    return [n / p] if i['op'] == 'multiply' else [n * p]


scalar('num_scale_pow10', lambda i, pi: F(str(i['n'])) * _i(i, 'p') if i['op'] == 'multiply' else F(str(i['n'])) / _i(i, 'p'))
scalar_slip('num.scale_pow10_direction', 'num.scale_direction', 'num_scale_pow10', _pow10_direction)


def _place_value(i, pi):
    s = str(int(i['number']))
    d = str(int(i['digit']))
    if s.count(d) != 1:
        raise ValueError('digit not unique')
    return F(int(d) * 10 ** (len(s) - 1 - s.index(d)))


scalar('num_place_value_digit', _place_value)
scalar_slip('num.place_value_digit_face', 'num.digit_not_value', 'num_place_value_digit', lambda i, pi: [_i(i, 'digit')],
            echo=True)
_POSITIONS = {'tenths': 0, 'hundredths': 1, 'thousandths': 2}


def _decimal_digit(i, k):
    digits = str(i['number']).split('.')[1]
    return F(int(digits[k])) if 0 <= k < len(digits) else None


scalar('num_decimal_place', lambda i, pi: _decimal_digit(i, _POSITIONS[i['position']]))
scalar_slip('num.decimal_place_next', 'num.place_names', 'num_decimal_place',
            lambda i, pi: [v for v in (_decimal_digit(i, _POSITIONS[i['position']] - 1),
                                       _decimal_digit(i, _POSITIONS[i['position']] + 1)) if v is not None])
scalar('num_from_standard_form', lambda i, pi: F(str(i['coef'])) * F(10) ** int(i['power']))
scalar_slip('num.standard_form_sign', 'idx.power_sign_ignored', 'num_from_standard_form',
            lambda i, pi: [F(str(i['coef'])) * F(10) ** -int(i['power'])])
def _recurring_parts(dec):
    """(the fraction a recurring decimal such as '0.272727…' stands for, its repeating block) from the printed digits."""
    text = str(dec).replace('...', '\u2026')
    if not text.startswith('0.') or not text.endswith('\u2026'):
        raise ValueError('shape')
    digits = text[2:-1]
    if not digits.isdigit() or not 2 <= len(digits) <= 12:
        raise ValueError('digits')
    for start in range(len(digits)):
        for period in range(1, len(digits) // 2 + 1):
            block = digits[start:start + period]
            tail = digits[start:]
            if tail == (block * (len(tail) // period + 1))[:len(tail)] and len(tail) >= 2 * period:
                num = int(digits[:start + period]) - (int(digits[:start]) if start else 0)
                return Fraction(num, 10 ** start * (10 ** period - 1)), block
    raise ValueError('no period')


scalar('num_recurring_text', lambda i, pi: _recurring_parts(i['dec'])[0])


def _recurring_block_over_ten(i, pi):
    block = _recurring_parts(i['dec'])[1]
    return [Fraction(int(block), 10 ** len(block))]


scalar_slip('num.recurring_terminating', 'num.recurring_stops', 'num_recurring_text', _recurring_block_over_ten)
pair('num_error_interval', lambda i: (F(str(i['value'])) - F(str(i['unit'])) / 2, F(str(i['value'])) + F(str(i['unit'])) / 2))
pair_slip('num.error_full_unit', 'num.bounds_full_unit', 'num_error_interval',
          lambda i: [(F(str(i['value'])) - F(str(i['unit'])), F(str(i['value'])) + F(str(i['unit'])))])


def _half(i):
    return F(str(i['unit'])) / 2


pair('num_bounds_area', lambda i: ((_i(i, 'length') - _half(i)) * (_i(i, 'width') - _half(i)),
                                   (_i(i, 'length') + _half(i)) * (_i(i, 'width') + _half(i))))
pair_slip('num.bounds_area_full_unit', 'num.bounds_full_unit', 'num_bounds_area',
          lambda i: [((_i(i, 'length') - 2 * _half(i)) * (_i(i, 'width') - 2 * _half(i)),
                      (_i(i, 'length') + 2 * _half(i)) * (_i(i, 'width') + 2 * _half(i)))])
pair('num_bounds_product', lambda i: ((_i(i, 'a') - _half(i)) * (_i(i, 'b') - _half(i)),
                                      (_i(i, 'a') + _half(i)) * (_i(i, 'b') + _half(i))))
pair_slip('num.bounds_product_full_unit', 'num.bounds_full_unit', 'num_bounds_product',
          lambda i: [((_i(i, 'a') - 2 * _half(i)) * (_i(i, 'b') - 2 * _half(i)),
                      (_i(i, 'a') + 2 * _half(i)) * (_i(i, 'b') + 2 * _half(i)))])
pair('num_bounds_density', lambda i: ((_i(i, 'mass') - _half(i)) / (_i(i, 'volume') + _half(i)),
                                      (_i(i, 'mass') + _half(i)) / (_i(i, 'volume') - _half(i))))
pair_slip('num.bounds_density_matched', 'num.bounds_combination', 'num_bounds_density',
          lambda i: [((_i(i, 'mass') - _half(i)) / (_i(i, 'volume') - _half(i)),
                      (_i(i, 'mass') + _half(i)) / (_i(i, 'volume') + _half(i)))])
pair('num_share_ratio', lambda i: (_i(i, 'total') * _i(i, 'r1') / (_i(i, 'r1') + _i(i, 'r2')),
                                   _i(i, 'total') * _i(i, 'r2') / (_i(i, 'r1') + _i(i, 'r2'))))
pair_slip('num.share_ratio_swapped', 'ratio.parts_swapped', 'num_share_ratio',
          lambda i: [(_i(i, 'total') * _i(i, 'r2') / (_i(i, 'r1') + _i(i, 'r2')),
                      _i(i, 'total') * _i(i, 'r1') / (_i(i, 'r1') + _i(i, 'r2')))])
pair_slip('num.share_ratio_equal', 'ratio.shared_equally', 'num_share_ratio',
          lambda i: [(_i(i, 'total') / 2, _i(i, 'total') / 2)])


# =============================================================================================
# Shapes and angles asked as one number
# =============================================================================================

part('circ_centre', lambda i: [2 * _a(i)])
slip('circ.centre_halved', 'circ.centre_double', 'circ_centre', lambda i: [[_a(i) / 2]])
part('circ_chord_radius', lambda i: [sqrtq((_i(i, 'chord') / 2) ** 2 + _i(i, 'd') ** 2)], decimal=(0,))
slip('circ.chord_radius_whole', 'pyth.base_not_halved', 'circ_chord_radius',
     lambda i: [[sqrtq(_i(i, 'chord') ** 2 + _i(i, 'd') ** 2)]])
slip('circ.chord_radius_added', 'pyth.sides_not_squares', 'circ_chord_radius',
     lambda i: [[_i(i, 'chord') / 2 + _i(i, 'd')]])
part('circ_reflex', lambda i: [360 - 2 * _i(i, 'arc')])
slip('circ.reflex_centre_only', 'circ.reflex_missed', 'circ_reflex', lambda i: [[2 * _i(i, 'arc')]])
part('sim_area_scale', lambda i: [_i(i, 'area') * (_i(i, 'q') / _i(i, 'p')) ** 2])
slip('sim.area_scale_power', 'sim.wrong_power', 'sim_area_scale',
     lambda i: [[_i(i, 'area') * (_i(i, 'q') / _i(i, 'p'))], [_i(i, 'area') * (_i(i, 'q') / _i(i, 'p')) ** 3]])
slip('sim.area_scale_inverted', 'sim.direction', 'sim_area_scale',
     lambda i: [[_i(i, 'area') * (_i(i, 'p') / _i(i, 'q')) ** 2]])
part('sim_k_from_area', lambda i: [sqrtq(_i(i, 'large') / _i(i, 'small'))])
slip('sim.k_area_not_rooted', 'sim.area_ratio_not_rooted', 'sim_k_from_area',
     lambda i: [[_i(i, 'large') / _i(i, 'small')]])

# Families asked for a single number. Those in DUAL_ALSO have a part form too (some slots ask them as a one-box
# number_fields answer), so their rules also exist as scalar copies (id + '_s'); those in SCALAR_ONLY are asked only as
# a plain number, so the part form is dropped and the scalar rule keeps the id.
DUAL = ('circ_tangent_length', 'circ_two_tangents', 'sim_area_k', 'sim_map_length')
SCALAR_ONLY = ('circ_centre', 'circ_chord_radius', 'circ_reflex', 'sim_area_scale', 'sim_k_from_area')


# Review 2026-10-27: a box typed with the right answer of another box is most likely an answer in the wrong box (or
# two equal answers), not the slip a rule computes by coincidence ("Share 81 sweets in the ratio 3:2:4", second share
# typed 27, which is the first share and also 81 shared equally). Such a value stays silent, except for the rules whose
# slip *is* the other box's answer (arcs swapped, ratio parts swapped, interior and exterior swapped, and so on).
PART_OTHER_BOX_OK = frozenset({
    'circ.alt_segment_not_doubled', 'circ.alt_straight_supplement', 'circ.arcs_swapped', 'circ.both_arcs_swapped',
    'circ.both_arcs_sum_swapped', 'circ.centre_cyclic_equal', 'circ.cyclic_ext_equal', 'circ.same_seg2_swapped',
    'fdp.dec_pct_swapped', 'fdp.pct_decimal', 'poly.int_ext_swapped_interior', 'poly.int_ext_swapped_exterior',
    'ratio.ratio_share_swapped', 'ratio.ratio_concert_swapped', 'sim.bisector_swapped', 'mf.exponents_swapped',
})


def _make_dual():
    by_family = {}
    for rule in PART_RULES:
        for fam in rule.families:
            if fam in DUAL or fam in SCALAR_ONLY:
                by_family.setdefault(fam, []).append(rule)
    for fam, rules in by_family.items():
        truth = PART_TRUTH[fam]
        TRUTH[fam] = lambda i, pi, t=truth: t(i)[0]
        suffix = '' if fam in SCALAR_ONLY else '_s'
        for rule in rules:
            def values(i, pi, r=rule):
                return [vec[0] for vec in r.slip(i) if vec[0] is not None]
            RULES.append(_r(rule.id + suffix, rule.message, [fam], values))
            if rule.id in ECHO_OK:
                ECHO_OK.add(rule.id + suffix)
    for fam in SCALAR_ONLY:
        PART_RULES[:] = [r for r in PART_RULES if fam not in r.families]
        PART_TRUTH.pop(fam, None)
        PART_TOKENS.pop(fam, None)


def _pi(pi):
    return F(pi)


scalar('mens_cyl_hemisphere', lambda i, pi: pi * _i(i, 'r') ** 2 * _i(i, 'h') + Fraction(2, 3) * pi * _i(i, 'r') ** 3)
scalar_slip('mens.cyl_hemisphere_whole', 'mens.hemisphere_half', 'mens_cyl_hemisphere',
            lambda i, pi: [pi * _i(i, 'r') ** 2 * _i(i, 'h') + Fraction(4, 3) * pi * _i(i, 'r') ** 3])


def _prism_sa_parts(i):
    a, b, length = _i(i, 'a'), _i(i, 'b'), _i(i, 'length')
    return a, b, length, sqrtq(a * a + b * b)


scalar('mens_tri_prism_sa', lambda i, pi: (lambda a, b, n, h: a * b + (a + b + h) * n)(*_prism_sa_parts(i)))
scalar_slip('mens.tri_prism_face_missed', 'mens.face_missed', 'mens_tri_prism_sa',
            lambda i, pi: [(lambda a, b, n, h: a * b + (a + b) * n)(*_prism_sa_parts(i))])
scalar_slip('mens.tri_prism_end_once', 'mens.end_once', 'mens_tri_prism_sa',
            lambda i, pi: [(lambda a, b, n, h: a * b / 2 + (a + b + h) * n)(*_prism_sa_parts(i))])


def _cube_root_q(x):
    return F(repr(round(float(x) ** (1 / 3), 12)))


def _sphere_radius_cubed(i, pi):
    return 3 * _i(i, 'vol') / (4 * pi)


scalar('mens_sphere_radius_from_volume', lambda i, pi: _cube_root_q(_sphere_radius_cubed(i, pi)))
scalar_slip('mens.sphere_radius_no_root', 'mens.cube_root_missed', 'mens_sphere_radius_from_volume',
            lambda i, pi: [_sphere_radius_cubed(i, pi), sqrtq(_sphere_radius_cubed(i, pi))])
scalar('mens_hemi_cone_sa', lambda i, pi: 2 * pi * _i(i, 'r') ** 2 + pi * _i(i, 'r') * sqrtq(_i(i, 'r') ** 2 + _i(i, 'h') ** 2))
scalar_slip('mens.hemi_cone_height', 'mens.height_for_slant', 'mens_hemi_cone_sa',
            lambda i, pi: [2 * pi * _i(i, 'r') ** 2 + pi * _i(i, 'r') * _i(i, 'h')])
scalar('mens_submerged_rise', lambda i, pi: 4 * _i(i, 'sphere_r') ** 3 / (3 * _i(i, 'cyl_r') ** 2))
scalar_slip('mens.submerged_not_divided', 'mens.rise_not_divided', 'mens_submerged_rise',
            lambda i, pi: [Fraction(4, 3) * pi * _i(i, 'sphere_r') ** 3])
scalar('mens_cyl_mass', lambda i, pi: _i(i, 'density') * pi * _i(i, 'r') ** 2 * _i(i, 'h'))
scalar_slip('mens.cyl_mass_formula', 'mens.mass_formula', 'mens_cyl_mass',
            lambda i, pi: [pi * _i(i, 'r') ** 2 * _i(i, 'h') / _i(i, 'density'), pi * _i(i, 'r') ** 2 * _i(i, 'h')])
scalar('mens_segment_60', lambda i, pi: pi * _i(i, 'r') ** 2 / 6 - _i(i, 'r') ** 2 * trig('sin', 60) / 2)
scalar_slip('mens.segment_sector_only', 'mens.whole_sector', 'mens_segment_60',
            lambda i, pi: [pi * _i(i, 'r') ** 2 / 6])
scalar_slip('mens.segment_added', 'mens.segment_triangle_added', 'mens_segment_60',
            lambda i, pi: [pi * _i(i, 'r') ** 2 / 6 + _i(i, 'r') ** 2 * trig('sin', 60) / 2])
scalar('mens_prism_compound', lambda i, pi: (_i(i, 'a') * _i(i, 'h') + _i(i, 'a') * _i(i, 'b') / 2) * _i(i, 'length'))
scalar_slip('mens.prism_compound_rectangle', 'mens.full_rectangle', 'mens_prism_compound',
            lambda i, pi: [(_i(i, 'a') * _i(i, 'h') + _i(i, 'a') * _i(i, 'b')) * _i(i, 'length')])
scalar_slip('mens.prism_compound_area', 'mens.cross_section_only', 'mens_prism_compound',
            lambda i, pi: [_i(i, 'a') * _i(i, 'h') + _i(i, 'a') * _i(i, 'b') / 2])


def _cut_other(i):
    return sqrtq(_i(i, 'slope') ** 2 - _i(i, 'cut') ** 2)


scalar('pyth_cut_corner', lambda i, pi: _i(i, 'length') * _i(i, 'width') - _i(i, 'cut') * _cut_other(i) / 2)
scalar_slip('pyth.cut_corner_full', 'mens.cut_triangle', 'pyth_cut_corner',
            lambda i, pi: [_i(i, 'length') * _i(i, 'width') - _i(i, 'cut') * _cut_other(i)])
scalar('trig_area_side', lambda i, pi: 2 * _i(i, 'area') / (_i(i, 'a') * trig('sin', _i(i, 'angle'))))
scalar_slip('trig.area_side_half', 'trig.area_half_missed', 'trig_area_side',
            lambda i, pi: [_i(i, 'area') / (_i(i, 'a') * trig('sin', _i(i, 'angle')))])
scalar('brg_meeting', lambda i, pi: _i(i, 'sep') / (_i(i, 'v1') + _i(i, 'v2')))
scalar_slip('brg.meeting_difference', 'cm.relative_speed', 'brg_meeting',
            lambda i, pi: [_i(i, 'sep') / abs(_i(i, 'v1') - _i(i, 'v2'))] if _i(i, 'v1') != _i(i, 'v2') else [])
scalar('loci_chord_midpoint', lambda i, pi: sqrtq(_i(i, 'radius') ** 2 - (_i(i, 'chord') / 2) ** 2))
scalar_slip('loci.chord_midpoint_added', 'pyth.added_for_short', 'loci_chord_midpoint',
            lambda i, pi: [sqrtq(_i(i, 'radius') ** 2 + (_i(i, 'chord') / 2) ** 2)])
scalar_slip('loci.chord_midpoint_whole', 'pyth.base_not_halved', 'loci_chord_midpoint',
            lambda i, pi: [sqrtq(_i(i, 'radius') ** 2 - _i(i, 'chord') ** 2)] if _i(i, 'radius') > _i(i, 'chord') else [])
scalar('loci_sector', lambda i, pi: _i(i, 'angle') / 360 * pi * _i(i, 'radius') ** 2)
scalar_slip('loci.sector_whole', 'mens.whole_circle', 'loci_sector', lambda i, pi: [pi * _i(i, 'radius') ** 2])
scalar_slip('loci.sector_arc', 'mens.arc_formula', 'loci_sector',
            lambda i, pi: [_i(i, 'angle') / 360 * 2 * pi * _i(i, 'radius')])
_AREA_UNITS = {'cm\u00b2': 1, 'm\u00b2': 10 ** 4, 'km\u00b2': 10 ** 10}
scalar('loci_scale_area', lambda i, pi: _i(i, 'map_cm2') * _i(i, 'scale') ** 2 / _AREA_UNITS[i['unit_word']])
scalar_slip('loci.scale_area_linear', 'sim.wrong_power', 'loci_scale_area',
            lambda i, pi: [_i(i, 'map_cm2') * _i(i, 'scale') / sqrtq(_AREA_UNITS[i['unit_word']])])
scalar('loci_scale_down', lambda i, pi: _i(i, 'dist_km') * 100000 / _i(i, 'scale'))
scalar_slip('loci.scale_down_units', 'unit.not_converted', 'loci_scale_down',
            lambda i, pi: [_i(i, 'dist_km') * 1000 / _i(i, 'scale'), _i(i, 'dist_km') / _i(i, 'scale')])
scalar_slip('loci.scale_down_direction', 'ratio.scale_direction', 'loci_scale_down',
            lambda i, pi: [_i(i, 'dist_km') * 100000 * _i(i, 'scale')])
scalar('vec_parallel_t', lambda i, pi: _i(i, 'b0') * _i(i, 'a1') / _i(i, 'a0'))
scalar_slip('vec.parallel_t_inverted', 'vec.parallel_compare', 'vec_parallel_t',
            lambda i, pi: [_i(i, 'b0') * _i(i, 'a0') / _i(i, 'a1')] if _i(i, 'a1') != 0 else [])
scalar_slip('vec.parallel_t_additive', 'ratio.additive', 'vec_parallel_t',
            lambda i, pi: [_i(i, 'a1') + _i(i, 'b0') - _i(i, 'a0')])
scalar('vec_parallel_k', lambda i, pi: _i(i, 'b0') / _i(i, 'a0'))
scalar_slip('vec.parallel_k_inverted', 'vec.parallel_compare', 'vec_parallel_k',
            lambda i, pi: [_i(i, 'a0') / _i(i, 'b0')] if _i(i, 'b0') != 0 else [])
scalar_slip('vec.parallel_k_additive', 'ratio.additive', 'vec_parallel_k', lambda i, pi: [_i(i, 'b0') - _i(i, 'a0')])
pair_slip('vec.scale_sign_kept', 'vec.sign_not_changed', 'vec_scale',
          lambda i: [(abs(_i(i, 'k')) * _i(i, 'v0'), abs(_i(i, 'k')) * _i(i, 'v1'))] if _i(i, 'k') < 0 else [],
          echo=True)


def _ship_ab(i):
    if tuple(i.get('want') or ()) != ('ab',):
        raise ValueError('one distance only')
    a = (_i(i, 'd1') * trig('sin', _i(i, 'b1')), _i(i, 'd1') * trig('cos', _i(i, 'b1')))
    b = (_i(i, 'd2') * trig('sin', _i(i, 'b2')), _i(i, 'd2') * trig('cos', _i(i, 'b2')))
    return sqrtq((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


scalar('brg_two_ships', lambda i, pi: _ship_ab(i))
scalar_slip('brg.ship_ab_sides_added', 'pyth.sides_not_squares', 'brg_two_ships', lambda i, pi: [_i(i, 'd1') + _i(i, 'd2')])
scalar_slip('brg.ship_ab_pythagoras', 'brg.pythagoras_misused', 'brg_two_ships',
            lambda i, pi: [sqrtq(_i(i, 'd1') ** 2 + _i(i, 'd2') ** 2)])


# =============================================================================================
# Read from the question: substitution, functions, sequences and graphs.
# The verification hook names only the task for these; the parsers read the numbers from the displayed question
# (``misconception_cd.DERIVE``). A parser that does not recognise the wording returns None (no record, no hint).
# =============================================================================================

import re  # noqa: E402

from generators.shared.misconception_topics import evaluate as _evaluate  # noqa: E402

DERIVE: dict = {}
_EXPR = r'[0-9x+\-*/^\s\u00b2\u00b3()]+'
_OPS = {'+': '+', '-': '-', '\u00d7': '*', '\u00f7': '/'}


def _text(text):
    t = str(text)[:600].replace('\u2212', '-')
    return re.sub(r'\\[()]', ' ', t)


def _sub_x(expr, x):
    """``expr`` with every x replaced by the value in brackets, in the notation of ``evaluate``."""
    e = expr.replace('*', '\u00d7').replace('/', '\u00f7')
    e = re.sub(r'(\d)x', '\\1\u00d7x', e)
    return e.replace('x', f'({x})')


def _num(x):
    x = Fraction(x)
    if x.denominator != 1:
        raise ValueError('not a whole number')
    return str(x.numerator)


def _val(expr, x):
    return _evaluate(_sub_x(expr, _num(x)))


def _clean_expr(expr):
    expr = expr.strip()
    if not 1 <= len(expr) <= 40 or not re.fullmatch(_EXPR, expr) or 'x' not in expr:
        return None
    return expr


def derive_substitute(text):
    t = _text(text)
    m = re.search(r'If\s+x\s*=\s*(-?\d+)\s*,\s*find the value of\s+(.+?)\s*\.?\s*$', t)
    if m:
        expr = _clean_expr(m.group(2))
        return ('gr_subst', {'e': expr, 'x': m.group(1)}) if expr else None
    m = re.search(r'Using(?: the formula)?\s+([a-z])\s*=\s*([a-z+\-* ]+?)\s*,\s*find\s+([a-z])\s+when\s+(.+?)\s*\.?\s*$', t)
    if not m or m.group(1) != m.group(3):
        return None
    vals = re.findall(r'([a-z])\s*=\s*(-?\d+)', m.group(4))
    form = m.group(2).replace(' ', '')
    if not vals or any(k in ('f',) for k, _ in vals) or {k for k, _ in vals} != set(re.findall('[a-z]', form)):
        return None
    inputs = {'form': form}
    inputs.update({k: v for k, v in vals})
    return 'sub_formula', inputs


def _formula_value(i, product=True):
    form = i['form']
    out = []
    for ch in form:
        out.append(f'({i[ch]})' if ch.isalpha() else ch)
    text = ''.join(out)
    return _evaluate(text.replace(')(', ')\u00d7(' if product else ')+('))


def _formula_has_product(i):
    return ')(' in ''.join(f'({i[ch]})' if ch.isalpha() else ch for ch in i['form'])


scalar('sub_formula', lambda i, pi: _formula_value(i))
scalar_slip('sub.formula_letters_added', 'sub.letters_added', 'sub_formula',
            lambda i, pi: [_formula_value(i, product=False)] if _formula_has_product(i) else [])


def _implied(i, join):
    """The value when each "cx" is read as c and x added (or, for a x that is not negative, written side by side)."""
    expr, x = i['e'], Fraction(i['x'])
    found = []

    def piece(m):
        c = Fraction(m.group(1))
        found.append(1)
        if join:
            if x < 0 or x.denominator != 1:
                raise ValueError('no joined reading')
            return '(' + m.group(1) + _num(x) + ')'
        return f'({c + x})' if (c + x).denominator == 1 else f'({float(c + x)})'
    expr = re.sub(r'(\d+)x(?![\^\u00b2\u00b3])', piece, expr)
    if not found:
        raise ValueError('no implied product')
    return _evaluate(_sub_x(expr, _num(x)))


def _implied_values(i, pi):
    out = []
    for join in (True, False):
        try:
            out.append(_implied(i, join))
        except (ValueError, ZeroDivisionError):
            pass
    return out


def _divide_multiplied(i, pi):
    expr, x = i['e'], Fraction(i['x'])
    if not re.search(r'\d+/x', expr):
        return []
    expr = re.sub(r'(\d+)/x', lambda m: f'({int(m.group(1)) * x})', expr)
    return [_evaluate(_sub_x(expr, _num(x)))]


RULES.append(_r('sub.coefficient_implied', 'sub.implied_multiply', ['gr_subst'], _implied_values))
RULES.append(_r('sub.divide_multiplied', 'sub.divide_multiplied', ['gr_subst'], _divide_multiplied))


def derive_fn_eval(text):
    t = _text(text)
    fm = re.search(r'f\(x\)\s*=\s*(' + _EXPR + r')(?=\s*(?:,|\.|\band\b))', t)
    if not fm:
        return None
    fx = _clean_expr(fm.group(1))
    if fx is None:
        return None
    gm = re.search(r'g\(x\)\s*=\s*(' + _EXPR + r')(?=\s*[.,])', t)
    for pat, kind in ((r'f\(g\((-?\d+)\)\)', 'comp'), (r'f\(f\((-?\d+)\)\)', 'twice')):
        m = re.search(pat, t)
        if m:
            if kind == 'comp':
                gx = _clean_expr(gm.group(1)) if gm else None
                return ('fn_comp', {'f': fx, 'g': gx, 'x': m.group(1)}) if gx else None
            return 'fn_twice', {'f': fx, 'x': m.group(1)}
    calls = re.findall(r'\bf\((-?\d+)\)', t)
    if len(calls) != 1 or 'g(' in t:
        return None
    return 'gr_subst', {'e': fx, 'x': calls[0]}


scalar('fn_comp', lambda i, pi: _val(i['f'], _val(i['g'], i['x'])))
scalar_slip('fn.comp_wrong_order', 'fn.composite_order', 'fn_comp', lambda i, pi: [_val(i['g'], _val(i['f'], i['x']))])
scalar('fn_twice', lambda i, pi: _val(i['f'], _val(i['f'], i['x'])))
scalar_slip('fn.twice_applied_once', 'fn.twice_once', 'fn_twice',
            lambda i, pi: [_val(i['f'], i['x']), 2 * _val(i['f'], i['x'])])


def _machine_apply(op, n, v):
    n = Fraction(n)
    if op == '+':
        return v + n
    if op == '-':
        return v - n
    if op == '*':
        return v * n
    if n == 0:
        raise ValueError('divide by zero')
    return v / n


def _machine_undo(op, n, v):
    return _machine_apply({'+': '-', '-': '+', '*': '/', '/': '*'}[op], n, v)


def derive_fn_machine(text):
    t = _text(text)
    m = re.search(r'applies\s*([+\-\u00d7\u00f7])\s*(\d+)\s*then\s*([+\-\u00d7\u00f7])\s*(\d+)', t)
    if not m:
        return None
    ops = {'a': _OPS[m.group(1)], 'p': m.group(2), 'b': _OPS[m.group(3)], 'q': m.group(4)}
    given = re.search(r'The (input|output) is\s*(-?\d+)', t)
    if not given:
        return None
    ops['v'] = given.group(2)
    return ('fn_machine' if given.group(1) == 'input' else 'fn_machine_back'), ops


scalar('fn_machine', lambda i, pi: _machine_apply(i['b'], i['q'], _machine_apply(i['a'], i['p'], _i(i, 'v'))))
scalar_slip('fn.machine_swapped', 'fn.machine_order', 'fn_machine',
            lambda i, pi: [_machine_apply(i['a'], i['p'], _machine_apply(i['b'], i['q'], _i(i, 'v')))])
scalar('fn_machine_back', lambda i, pi: _machine_undo(i['a'], i['p'], _machine_undo(i['b'], i['q'], _i(i, 'v'))))
scalar_slip('fn.machine_back_order', 'fn.undo_order', 'fn_machine_back',
            lambda i, pi: [_machine_undo(i['b'], i['q'], _machine_undo(i['a'], i['p'], _i(i, 'v'))),
                           _machine_apply(i['b'], i['q'], _machine_apply(i['a'], i['p'], _i(i, 'v')))])


def derive_fn_inverse(text):
    t = _text(text)
    m = re.search(r'f\(x\)\s*=\s*(-?\d*)x\s*([+-])\s*(\d+)\s*(?:\.|,|and)', t)
    if not m:
        return None
    y = re.search(r'The output is\s*(-?\d+)', t) or re.search(r'f\(x\)\s*=\s*(-?\d+)\s*\.', t.split('and', 1)[-1])
    if not y:
        return None
    a = {'': 1, '-': -1}.get(m.group(1))
    a = int(m.group(1)) if a is None else a
    b = int(m.group(3)) * (1 if m.group(2) == '+' else -1)
    return 'fn_inverse_lin', {'a': a, 'b': b, 'y': y.group(1)}


scalar('fn_inverse_lin', lambda i, pi: (_i(i, 'y') - _i(i, 'b')) / _i(i, 'a'))
scalar_slip('fn.inverse_wrong_way', 'fn.undo_order', 'fn_inverse_lin',
            lambda i, pi: [(_i(i, 'y') + _i(i, 'b')) / _i(i, 'a'), _i(i, 'y') / _i(i, 'a') - _i(i, 'b')])


def derive_seq_special(text):
    m = re.search(r'(\d+)(?:st|nd|rd|th)\s+(square|triangle|odd|even)\s+number', str(text)[:400])
    if not m or not 1 <= int(m.group(1)) <= 200:
        return None
    return 'seq_special', {'k': m.group(2), 'n': int(m.group(1))}


def _special(i):
    n, k = _i(i, 'n'), i['k']
    return {'square': n * n, 'triangle': n * (n + 1) / 2, 'odd': 2 * n - 1, 'even': 2 * n}[k]


scalar('seq_special', lambda i, pi: _special(i))
scalar_slip('seq.square_doubled', 'seq.square_doubled', 'seq_special',
            lambda i, pi: [2 * _i(i, 'n')] if i['k'] == 'square' else [])
scalar_slip('seq.triangle_not_halved', 'seq.triangle_not_halved', 'seq_special',
            lambda i, pi: [_i(i, 'n') * (_i(i, 'n') + 1)] if i['k'] == 'triangle' else [])
scalar_slip('seq.odd_parity', 'seq.odd_parity', 'seq_special',
            lambda i, pi: [2 * _i(i, 'n'), 2 * _i(i, 'n') + 1] if i['k'] == 'odd' else [])


def derive_gr_parallel(text):
    t = _text(text)
    m = re.search(r'parallel to\s+y\s*=\s*(.+?)\s*\.\s*What', t)
    if not m:
        return None
    line = re.fullmatch(r'(-?\d*)\s*x\s*(?:([+-])\s*(\d+))?', m.group(1).strip())
    if not line:
        return None
    slope = {'': 1, '-': -1}.get(line.group(1))
    slope = int(line.group(1)) if slope is None else slope
    c = 0 if line.group(2) is None else int(line.group(3)) * (1 if line.group(2) == '+' else -1)
    return 'gr_parallel', {'m': slope, 'c': c}


scalar('gr_parallel', lambda i, pi: _i(i, 'm'))
scalar_slip('gr.parallel_intercept', 'gr.parallel_intercept', 'gr_parallel',
            lambda i, pi: [_i(i, 'c')] if _i(i, 'c') != 0 else [], echo=True)
scalar_slip('gr.parallel_perpendicular', 'gr.parallel_perpendicular', 'gr_parallel',
            lambda i, pi: [-1 / _i(i, 'm')] if abs(_i(i, 'm')) > 1 else [])


def derive_gr_speed(text):
    m = re.search(r'travelling\s+(\d+(?:\.\d+)?)\s*km\s+in\s+(\d+(?:\.\d+)?)\s*hours?\b.*Find its speed', _text(text))
    return ('gr_speed', {'d': m.group(1), 't': m.group(2)}) if m else None


scalar('gr_speed', lambda i, pi: F(str(i['d'])) / F(str(i['t'])))
scalar_slip('gr.speed_multiplied', 'gr.speed_multiplied', 'gr_speed', lambda i, pi: [F(str(i['d'])) * F(str(i['t']))])

DERIVE.update({
    'substitute': derive_substitute,
    'fn_eval': derive_fn_eval,
    'fn_machine': derive_fn_machine,
    'fn_inverse_eval': derive_fn_inverse,
    'fn_solve': derive_fn_inverse,
    'seq_special': derive_seq_special,
    'gr_parallel': derive_gr_parallel,
    'gr_speed': derive_gr_speed,
})



def derive_seq_sum_arith(text):
    t = _text(text)
    m = re.search(r'sum of the first (\d+) terms of the arithmetic sequence with first term (-?\d+) and common difference (-?\d+)', t)
    if m:
        return 'seq_sum_arith', {'n': m.group(1), 'a': m.group(2), 'd': m.group(3)}
    m = re.search(r'(\d+) rows of seats\. The first row has (\d+) seats and each subsequent row has (\d+) more seats', t)
    return ('seq_sum_arith', {'n': m.group(1), 'a': m.group(2), 'd': m.group(3)}) if m else None


def derive_seq_mean(text):
    m = re.search(r'first term (-?\d+), common difference (-?\d+), and (\d+) terms.*find the mean', _text(text))
    return ('seq_mean', {'a': m.group(1), 'd': m.group(2), 'n': m.group(3)}) if m else None


def derive_seq_geometric(text):
    m = re.search(r'first term (-?\d+) and common ratio (\d+)\. Find the (\d+)(?:st|nd|rd|th) term', _text(text))
    return ('seq_geo_nth', {'a': m.group(1), 'r': m.group(2), 'n': m.group(3)}) if m else None


def derive_seq_u_n(text):
    m = re.search(r'u_n\s*=\s*([0-9n+\-^\s]+?)\s*\(a\)\s*Find\s+u_\{(\d+)\}', _text(text))
    if not m:
        return None
    expr = _clean_expr(m.group(1).replace('n', 'x'))
    return ('gr_subst', {'e': expr, 'x': m.group(2)}) if expr else None


def _sum_arith(i, last_steps=None):
    a, d, n = _i(i, 'a'), _i(i, 'd'), _i(i, 'n')
    return n / 2 * (2 * a + (n - 1 if last_steps is None else last_steps) * d)


scalar('seq_sum_arith', lambda i, pi: _sum_arith(i))
scalar_slip('seq.sum_extra_step', 'seq.steps_one_fewer', 'seq_sum_arith', lambda i, pi: [_sum_arith(i, _i(i, 'n'))])
scalar_slip('seq.sum_not_halved', 'seq.sum_not_halved', 'seq_sum_arith', lambda i, pi: [2 * _sum_arith(i)])
scalar('seq_mean', lambda i, pi: _sum_arith(i) / _i(i, 'n'))
scalar_slip('seq.mean_extra_step', 'seq.steps_one_fewer', 'seq_mean', lambda i, pi: [_sum_arith(i, _i(i, 'n')) / _i(i, 'n')])
scalar('seq_geo_nth', lambda i, pi: _i(i, 'a') * _i(i, 'r') ** (int(_i(i, 'n')) - 1))
scalar_slip('seq.geometric_power', 'seq.geometric_power', 'seq_geo_nth',
            lambda i, pi: [_i(i, 'a') * _i(i, 'r') ** int(_i(i, 'n'))])

DERIVE.update({
    'seq_sum_arith': derive_seq_sum_arith,
    'seq_rows': derive_seq_sum_arith,
    'seq_mean': derive_seq_mean,
    'seq_geometric': derive_seq_geometric,
    'seq_u_n': derive_seq_u_n,
})


# =============================================================================================
# Phase 5c (docs/GCSE_MATHS_HINTS.md, section 25): rounding, word problems, sequences, surds, angle algebra.
# Every slip below is one the generic rules cannot name: a generic rule would say nothing on the value, or something
# less useful (the generic place-value line for a digit kept without its zeros). Rules that only repeated a generic
# line on the same value (fewer decimal places, a product off by a power of ten) were left out.
# =============================================================================================



def _apart(family, fn, pow10=True, others=None):
    """The slips of ``fn`` that no generic rule could equally explain (review 2026-10-27, section 25).

    A value that is the key with its sign changed, the key turned upside down or the key times a power of ten (up to
    1000 either way) is what the generic sign, reciprocal and place-value lines name; when a topic slip lands on one
    of them, both readings are as likely, so the topic rule stays silent and the generic line speaks. ``pow10=False``
    keeps a slip whose own step is a power of ten (the cost of the miles at £10 a mile). ``others(i, pi, truth)``
    gives further values that another slip reaches (an angle typed in place of x).
    """
    def slips(i, pi):
        t = TRUTH[family](i, pi)
        avoid = set(others(i, pi, t)) if others else set()
        if t != 0:
            avoid |= {-t, 1 / t}
            if pow10:
                avoid |= {t * Fraction(10) ** k for k in (-3, -2, -1, 1, 2, 3)}
        return [v for v in (F(x) for x in fn(i, pi)) if v not in avoid]
    return slips


def _unit10(k):
    """The place value 10 to the power -k as an exact Fraction (k may be negative: tens, hundreds)."""
    return Fraction(10) ** (-k)


# ---- rounding ------------------------------------------------------------------------------------------------------
scalar('num_round_dp', lambda i, pi: round_unit(_i(i, 'n'), _unit10(_n(i['dp']))))


def _round_dp_as_sf(i, pi):
    n, dp = _i(i, 'n'), _n(i['dp'])
    if dp < 1 or n <= 0:
        return []
    c = round_sf(n, dp)
    # Fewer decimal places (down to a whole number, and the generic rule's second step, the tens) is the generic "round
    # to the accuracy asked" line, or a pupil who dropped the decimals. A value that is also one of those is not clearly
    # a confusion of decimal places with significant figures (776.4342 to 3 decimal places and to 3 significant figures
    # are both 776 once cut; 22.835 to 1 significant figure is the tens), so the rule stays silent there.
    coarser = range(min(0, dp - 2), dp)
    # review 2026-10-27: the digits cut off (not rounded) as well: 850.5049 to 2 decimal places typed 850 is the
    # decimals dropped, and also 2 significant figures
    if c in {round_unit(n, _unit10(k)) for k in coarser} | {(n / _unit10(k)).__floor__() * _unit10(k) for k in coarser}:
        return []
    return [c]


scalar_slip('num.round_dp_as_sf', 'num.round_dp_as_sf', 'num_round_dp', _apart('num_round_dp', _round_dp_as_sf))

scalar('num_round_sf', lambda i, pi: round_sf(_i(i, 'n'), _n(i['sf'])))


def _round_sf_digits_only(i, pi):
    n, sf = _i(i, 'n'), _n(i['sf'])
    if n.denominator != 1 or n < 10 ** sf:
        return []
    shift = len(str(int(n))) - sf
    c = round_sf(n, sf) / 10 ** shift
    # four or more places short: the generic place-value line only reaches three, and a rounded-up carry (99 700 to
    # 100 000) is not a digits-only slip
    if shift < 4 or c.denominator != 1 or len(str(int(c))) != sf:
        return []
    return [c]


scalar_slip('num.round_sf_zeros', 'num.round_sf_zeros', 'num_round_sf', _round_sf_digits_only)


def _find_index(i):
    base, value = F(i['base']), F(i['value'])
    if base < 2 or value < base:
        raise ValueError('not a power')
    power, n = base, 1
    while power < value and n < 60:
        power *= base
        n += 1
    if power != value:
        raise ValueError('not a power of the base')
    return Fraction(n)


scalar('num_find_index', lambda i, pi: _find_index(i))
scalar_slip('num.index_divided', 'num.index_divided', 'num_find_index',
            _apart('num_find_index', lambda i, pi: [F(i['value']) / F(i['base'])] if _find_index(i) > 2 else []))

# ---- word problems -------------------------------------------------------------------------------------------------


def _consecutive_start(i):
    n, total = _n(i['n']), F(i['total'])
    return (total - Fraction(n * (n - 1), 2)) / n


scalar('consecutive_sum', lambda i, pi: _consecutive_start(i))
scalar_slip('alg.consecutive_equal', 'alg.consecutive_equal', 'consecutive_sum',
            _apart('consecutive_sum', lambda i, pi: [F(i['total']) / _n(i['n'])]))

scalar('linear_fixed_rate', lambda i, pi: (_i(i, 'total') - _i(i, 'fixed')) / _i(i, 'rate'))
scalar_slip('lin.fixed_ignored', 'lin.fixed_ignored', 'linear_fixed_rate',
            _apart('linear_fixed_rate', lambda i, pi: [_i(i, 'total') / _i(i, 'rate')]))
scalar_slip('lin.fixed_added', 'lin.fixed_added', 'linear_fixed_rate',
            _apart('linear_fixed_rate', lambda i, pi: [(_i(i, 'total') + _i(i, 'fixed')) / _i(i, 'rate')]))
scalar_slip('lin.cost_not_divided', 'lin.cost_not_divided', 'linear_fixed_rate',
            _apart('linear_fixed_rate', lambda i, pi: [_i(i, 'total') - _i(i, 'fixed')], pow10=False))

scalar('think_number', lambda i, pi: (_i(i, 'result') - _i(i, 'add')) / _i(i, 'mult'))
scalar_slip('eq.think_undo_order', 'fn.undo_order', 'think_number',
            _apart('think_number', lambda i, pi: [_i(i, 'result') / _i(i, 'mult') - _i(i, 'add')]))
scalar_slip('eq.think_wrong_inverse', 'seq.constant_inverse', 'think_number',
            _apart('think_number', lambda i, pi: [(_i(i, 'result') + _i(i, 'add')) / _i(i, 'mult')]))

# a rectangle of length 2w + k and width w: the perimeter 2(3w + k) is P
scalar('rect_perimeter_linear', lambda i, pi: (_i(i, 'perimeter') / 2 - _i(i, 'k')) / 3)
scalar_slip('eq.perimeter_one_each', 'mens.perimeter_all_round', 'rect_perimeter_linear',
            _apart('rect_perimeter_linear', lambda i, pi: [(_i(i, 'perimeter') - _i(i, 'k')) / 3]))

# ---- sequences -----------------------------------------------------------------------------------------------------


def _fibonacci_terms(i):
    t = [F(v) for v in _items(i['t'])]
    if _n(i['at']) != len(t) or len(t) < 4 or any(t[k] != t[k - 1] + t[k - 2] for k in range(2, len(t))):
        return None
    return t


scalar_slip('seq.fibonacci_constant_step', 'seq.fibonacci_step', 'seq_terms',
            lambda i, pi: [] if _fibonacci_terms(i) is None else [2 * _fibonacci_terms(i)[-1] - _fibonacci_terms(i)[-2]])


def derive_seq_geometric_sum(text):
    m = re.search(r'sum of the first (\d+) terms of the geometric series with first term (-?\d+) and common ratio (\d+)', _text(text))
    return ('seq_geo_sum', {'n': m.group(1), 'a': m.group(2), 'r': m.group(3)}) if m else None


def derive_seq_geometric_infinite(text):
    m = re.search(r'first term (\d+) and common ratio\s*\\dfrac\{(\d+)\}\{(\d+)\}.*sum to infinity', _text(text))
    return ('seq_geo_inf', {'a': m.group(1), 'rn': m.group(2), 'rd': m.group(3)}) if m else None


def derive_seq_sum_last(text):
    m = re.search(r'first term (\d+), last term (\d+), and (\d+) terms.*Use the formula to find', _text(text))
    return ('seq_sum_last', {'a': m.group(1), 'l': m.group(2), 'n': m.group(3)}) if m else None


def derive_seq_context(text):
    m = re.search(r'earns £(\d+) in year 1\. Each year their salary increases by £(\d+)\..*Enter the salary in year (\d+)',
                  _text(text))
    return ('seq_context', {'wage': m.group(1), 'rise': m.group(2), 'year': m.group(3)}) if m else None


def _geo_sum(i):
    a, r, n = _i(i, 'a'), _i(i, 'r'), _n(int(F(i['n'])))
    if r == 1:
        raise ValueError('ratio one')
    return a * (r ** n - 1) / (r - 1)


scalar('seq_geo_sum', lambda i, pi: _geo_sum(i))
scalar_slip('seq.geometric_sum_unshared', 'seq.geometric_sum_denominator', 'seq_geo_sum',
            _apart('seq_geo_sum', lambda i, pi: [_i(i, 'a') * (_i(i, 'r') ** int(F(i['n'])) - 1)] if _i(i, 'r') != 2 else []))
scalar_slip('seq.geometric_sum_last_term', 'seq.term_for_sum', 'seq_geo_sum',
            _apart('seq_geo_sum', lambda i, pi: [_i(i, 'a') * _i(i, 'r') ** (int(F(i['n'])) - 1)]))


def _geo_ratio(i):
    return _i(i, 'rn') / _i(i, 'rd')


scalar('seq_geo_inf', lambda i, pi: _i(i, 'a') / (1 - _geo_ratio(i)))
scalar_slip('seq.infinite_over_ratio', 'seq.infinite_denominator', 'seq_geo_inf',
            _apart('seq_geo_inf', lambda i, pi: [_i(i, 'a') / _geo_ratio(i)]))
scalar_slip('seq.infinite_plus_ratio', 'seq.infinite_denominator', 'seq_geo_inf',
            _apart('seq_geo_inf', lambda i, pi: [_i(i, 'a') / (1 + _geo_ratio(i))]))

scalar('seq_sum_last', lambda i, pi: _i(i, 'n') * (_i(i, 'a') + _i(i, 'l')) / 2)
scalar_slip('seq.sum_last_not_halved', 'seq.sum_not_halved', 'seq_sum_last',
            _apart('seq_sum_last', lambda i, pi: [_i(i, 'n') * (_i(i, 'a') + _i(i, 'l'))]))

scalar('seq_context', lambda i, pi: _i(i, 'wage') + (_i(i, 'year') - 1) * _i(i, 'rise'))
scalar_slip('seq.context_extra_step', 'seq.steps_one_fewer', 'seq_context',
            _apart('seq_context', lambda i, pi: [_i(i, 'wage') + _i(i, 'year') * _i(i, 'rise')]))

# ---- surds and the angles of a triangle in x -----------------------------------------------------------------------


def derive_surd(text):
    t = _text(text)
    m = re.search(r'Solve:\s*\\sqrt\{x\s*\+\s*(\d+)\}\s*=\s*(\d+)\s*$', t)
    if m:
        return 'surd_sqrt_eq', {'c': m.group(1), 'r': m.group(2)}
    m = re.search(r'Simplify:\s*\\dfrac\{\\sqrt\{(\d+)\}\}\{\\sqrt\{(\d+)\}\}\s*$', t)
    if m:
        return 'surd_div', {'a': m.group(1), 'b': m.group(2)}
    m = re.search(r'Expand and simplify\s*\(\s*(\d+)\s*\+\s*√(\d+)\s*\)\s*\(\s*(\d+)\s*-\s*√(\d+)\s*\)\s*\.?\s*$', t)
    # the same pair of numbers in both brackets, and a real surd (a square number under the root is no surd: review)
    if m and m.group(1) == m.group(3) and m.group(2) == m.group(4) and math.isqrt(int(m.group(2))) ** 2 != int(m.group(2)):
        return 'surd_conj', {'a': m.group(1), 'b': m.group(2)}
    return None


def derive_angle_sum(text):
    t = str(text)[:600]
    if 'angles in a triangle are' not in t:
        return None
    terms = re.findall(r'(\d*)x\s*\+\s*(\d+)\s*\\?\)?°', t)
    if len(terms) != 3:
        return None
    return 'ang_sum_x', {'a': [c or '1' for c, _ in terms], 'b': [b for _, b in terms]}


scalar('surd_sqrt_eq', lambda i, pi: _i(i, 'r') ** 2 - _i(i, 'c'))
scalar_slip('surd.equation_not_squared', 'surd.equation_not_squared', 'surd_sqrt_eq',
            _apart('surd_sqrt_eq', lambda i, pi: [_i(i, 'r') - _i(i, 'c')]))
scalar_slip('surd.equation_sign_moved', 'alg.sign_moved', 'surd_sqrt_eq',
            _apart('surd_sqrt_eq', lambda i, pi: [_i(i, 'r') ** 2 + _i(i, 'c')]))
scalar('surd_div', lambda i, pi: sqrtq(_i(i, 'a') / _i(i, 'b')))
scalar_slip('surd.quotient_root_missed', 'surd.quotient_root_missed', 'surd_div',
            _apart('surd_div', lambda i, pi: [_i(i, 'a') / _i(i, 'b')]))
def _surd_conj(i):
    b = _i(i, 'b')
    if b.denominator != 1 or b < 2 or math.isqrt(int(b)) ** 2 == b:
        raise ValueError('no surd')       # a square number under the root is not a surd (review)
    return _i(i, 'a') ** 2 - b


scalar('surd_conj', lambda i, pi: _surd_conj(i))
scalar_slip('surd.conjugate_sign', 'surd.conjugate_sign', 'surd_conj',
            _apart('surd_conj', lambda i, pi: [_i(i, 'a') ** 2 + _i(i, 'b')]))
scalar_slip('surd.conjugate_unsquared', 'surd.conjugate_unsquared', 'surd_conj',
            _apart('surd_conj', lambda i, pi: [_i(i, 'a') - _i(i, 'b')]))


def _angle_sum_x(i, total):
    a, b = [F(v) for v in i['a']], [F(v) for v in i['b']]
    if len(a) != 3 or len(b) != 3:
        raise ValueError('three angles')
    return (total - sum(b)) / sum(a)


scalar('ang_sum_x', lambda i, pi: _angle_sum_x(i, 180))
def _angles_at(i, pi, x):
    """The three angles at x: a pupil who typed one of them found x and went on (review: 2% of questions)."""
    return [F(a) * x + F(b) for a, b in zip(i['a'], i['b'])]


scalar_slip('ang.sum_x_wrong_total', 'ang.wrong_total', 'ang_sum_x',
            _apart('ang_sum_x', lambda i, pi: [_angle_sum_x(i, 360)], others=_angles_at))

DERIVE.update({
    'seq_geometric': lambda text: derive_seq_geometric(text) or derive_seq_geometric_sum(text),
    'seq_geometric_infinite': derive_seq_geometric_infinite,
    'seq_sum_last': derive_seq_sum_last,
    'seq_context': derive_seq_context,
    'surd': derive_surd,
    'angle_sum': derive_angle_sum,
})



# =============================================================================================
# Phase 3 batch A (docs/GCSE_MATHS_VARIETY.md, Phase 3 batch A build notes): fractions, interest, counting, ratio,
# forming equations, directed and decimal arithmetic. The same contract as above: a rule speaks only when the family's
# ``TRUTH`` rebuilds the stored key from the printed numbers, never gives the corrected value, and stays silent when the
# slip is also the key, a printed number (unless ``echo``) or next to the key.
# =============================================================================================



def _frac(i, a, b):
    return F(i[a]) / F(i[b])


def _pence(v):
    """The value to the nearest penny, half up (the accuracy the money questions state)."""
    v = F(v)
    return Fraction(math.floor(v * 100 + Fraction(1, 2)), 100)


def _op(x, op, y):
    return {'+': x + y, '-': x - y, '*': x * y, '/': x / y}[op]


# ---- fractions -------------------------------------------------------------------------------------------------------

def _add_sub_truth(i, pi=None):
    return _op(_frac(i, 'n1', 'd1'), i['op'], _frac(i, 'n2', 'd2'))


def _add_sub_denominators(i, pi=None):
    n1, d1, n2, d2 = (F(i[k]) for k in ('n1', 'd1', 'n2', 'd2'))
    den = d1 + d2 if i['op'] == '+' else d1 - d2
    if den == 0:
        return []
    return [_op(n1, i['op'], n2) / den]


scalar('frac_add_sub', _add_sub_truth)
scalar_slip('frac.add_sub_denominators', 'frac.denominators_added', 'frac_add_sub', _apart('frac_add_sub', _add_sub_denominators))


def _mul_div_truth(i, pi=None):
    return _op(_frac(i, 'n1', 'd1'), i['op'], _frac(i, 'n2', 'd2'))


def _mul_div_not_flipped(i, pi=None):
    return [_frac(i, 'n1', 'd1') * _frac(i, 'n2', 'd2')] if i['op'] == '/' else []


scalar('frac_mul_div', _mul_div_truth)
scalar_slip('frac.mul_div_not_flipped', 'frac.divide_not_flipped', 'frac_mul_div', _apart('frac_mul_div', _mul_div_not_flipped))


def _mixed(i, w, n, d):
    return F(i[w]) + F(i[n]) / F(i[d])


def _mixed_add_sub_truth(i, pi=None):
    return _op(_mixed(i, 'w1', 'n1', 'd1'), i['op'], _mixed(i, 'w2', 'n2', 'd2'))


def _mixed_wholes_dropped(i, pi=None):
    return [_op(_frac(i, 'n1', 'd1'), i['op'], _frac(i, 'n2', 'd2'))]


def _mixed_denominators_added(i, pi=None):
    n1, d1, n2, d2 = (F(i[k]) for k in ('n1', 'd1', 'n2', 'd2'))
    den = d1 + d2 if i['op'] == '+' else d1 - d2
    if den == 0:
        return []
    return [_op(F(i['w1']), i['op'], F(i['w2'])) + _op(n1, i['op'], n2) / den]


scalar('frac_mixed_add_sub', _mixed_add_sub_truth)
scalar_slip('frac.mixed_wholes_dropped', 'frac.wholes_dropped', 'frac_mixed_add_sub',
            _apart('frac_mixed_add_sub', _mixed_wholes_dropped))
scalar_slip('frac.mixed_denominators_added', 'frac.denominators_added', 'frac_mixed_add_sub',
            _apart('frac_mixed_add_sub', _mixed_denominators_added))


def _mixed_mul_div_truth(i, pi=None):
    return _op(_mixed(i, 'w1', 'n1', 'd1'), i['op'], _mixed(i, 'w2', 'n2', 'd2'))


def _mixed_parts_separate(i, pi=None):
    return [_op(F(i['w1']), i['op'], F(i['w2'])) + _op(_frac(i, 'n1', 'd1'), i['op'], _frac(i, 'n2', 'd2'))]


def _mixed_not_flipped(i, pi=None):
    return [_mixed(i, 'w1', 'n1', 'd1') * _mixed(i, 'w2', 'n2', 'd2')] if i['op'] == '/' else []


scalar('frac_mixed_mul_div', _mixed_mul_div_truth)
scalar_slip('frac.mixed_mul_parts_separate', 'frac.mixed_parts_separate', 'frac_mixed_mul_div',
            _apart('frac_mixed_mul_div', _mixed_parts_separate))
scalar_slip('frac.mixed_mul_not_flipped', 'frac.divide_not_flipped', 'frac_mixed_mul_div',
            _apart('frac_mixed_mul_div', _mixed_not_flipped))


def _other_truth(i, pi=None):
    return F(i['part']) / (F(i['whole']) * F(i['scale']))


scalar('fdp_fraction_of_other', _other_truth)
scalar_slip('frac.other_wrong_way_up', 'frac.wrong_way_up', 'fdp_fraction_of_other',
            lambda i, pi: [F(i['whole']) * F(i['scale']) / F(i['part'])])
scalar_slip('frac.other_units_differ', 'frac.units_differ', 'fdp_fraction_of_other',
            lambda i, pi: [F(i['part']) / F(i['whole'])] if F(i['scale']) != 1 else [])
scalar('fdp_pct_of_other', lambda i, pi: F(i['part']) / F(i['whole']) * 100)
scalar_slip('pct.other_wrong_way_round', 'pct.wrong_way_round', 'fdp_pct_of_other',
            _apart('fdp_pct_of_other', lambda i, pi: [F(i['whole']) / F(i['part']) * 100]))
scalar('mf_hcf_fraction', lambda i, pi: F(i['a']) / F(i['b']))
scalar_slip('frac.hcf_fraction_hcf', 'frac.hcf_not_used', 'mf_hcf_fraction', lambda i, pi: [F(_gcd(i['a'], i['b']))])
scalar_slip('frac.hcf_fraction_top_only', 'frac.one_part_divided', 'mf_hcf_fraction',
            lambda i, pi: [F(i['a']) / _gcd(i['a'], i['b']) / F(i['b'])])


# ---- interest --------------------------------------------------------------------------------------------------------

def _interest_parts(i):
    p, r, y = F(str(i['principal'])), F(str(i['rate'])) / 100, int(i['years'])
    return p, r, y


def _interest_truth(i, pi=None):
    p, r, y = _interest_parts(i)
    simple = p * r * y
    return simple if i['ask'] == 'interest' else p + simple


def _interest_compound(i, pi=None):
    p, r, y = _interest_parts(i)
    grown = p * (1 + r) ** y
    return [_pence(grown - p) if i['ask'] == 'interest' else _pence(grown)]


def _interest_one_year(i, pi=None):
    p, r, y = _interest_parts(i)
    return [p * r if i['ask'] == 'interest' else p + p * r]


def _interest_wrong_quantity(i, pi=None):
    p, r, y = _interest_parts(i)
    return [p * r * y] if i['ask'] == 'total' else []


def _interest_total_for_interest(i, pi=None):
    p, r, y = _interest_parts(i)
    return [p + p * r * y] if i['ask'] == 'interest' else []


scalar('fdp_simple_interest', _interest_truth)
scalar_slip('int.simple_compound', 'int.compound_for_simple', 'fdp_simple_interest', _apart('fdp_simple_interest', _interest_compound))
scalar_slip('int.simple_one_year', 'int.one_year_only', 'fdp_simple_interest', _apart('fdp_simple_interest', _interest_one_year))
scalar_slip('int.simple_principal_missed', 'int.principal_missed', 'fdp_simple_interest', _interest_wrong_quantity)
scalar_slip('int.simple_total_for_interest', 'int.total_for_interest', 'fdp_simple_interest', _interest_total_for_interest)


def _vs_parts(i):
    p, r, y = F(i['principal']), F(i['rate']) / 100, int(i['years'])
    return p, r, y


def _vs_truth(i, pi=None):
    p, r, y = _vs_parts(i)
    return _pence(p * (1 + r) ** y - p - p * r * y)


scalar('fdp_simple_vs_compound', _vs_truth)
scalar_slip('int.vs_compound_alone', 'int.difference_missed', 'fdp_simple_vs_compound',
            lambda i, pi: [_pence(_vs_parts(i)[0] * (1 + _vs_parts(i)[1]) ** _vs_parts(i)[2] - _vs_parts(i)[0])])


# ---- multiples and factors -------------------------------------------------------------------------------------------

def _next_multiple(i, pi=None):
    n, m = int(i['n']), int(i['m'])
    return F((m // n + 1) * n)


scalar('mf_next_multiple', _next_multiple)
scalar_slip('mf.next_multiple_below', 'mf.multiple_not_above', 'mf_next_multiple',
            lambda i, pi: [F((int(i['m']) // int(i['n'])) * int(i['n']))])


def _divisor_count(n):
    return sum(1 for d in range(1, int(n) + 1) if int(n) % d == 0)


scalar('mf_factor_count', lambda i, pi: F(_divisor_count(i['n'])))
scalar_slip('mf.factor_count_ends', 'mf.count_ends_missed', 'mf_factor_count', lambda i, pi: [F(_divisor_count(i['n']) - 2)])
scalar_slip('mf.factor_count_pairs', 'mf.count_pairs', 'mf_factor_count', lambda i, pi: [F((_divisor_count(i['n']) + 1) // 2)])


def _between_count(i, pi=None):
    n, lo, hi = int(i['n']), int(i['lo']), int(i['hi'])
    return F(hi // n - lo // n)


scalar('mf_multiples_between', _between_count)
scalar_slip('mf.multiples_from_zero', 'mf.count_from_zero', 'mf_multiples_between',
            lambda i, pi: [F(int(i['hi']) // int(i['n']))])


def _squarefree_part(n):
    k = 1
    while math.isqrt(int(n) * k) ** 2 != int(n) * k:
        k += 1
    return k


scalar('mf_square_multiplier', lambda i, pi: F(_squarefree_part(i['n'])))
scalar_slip('mf.square_multiplier_self', 'mf.square_not_smallest', 'mf_square_multiplier', lambda i, pi: [F(i['n'])], echo=True)
scalar_slip('mf.square_multiplier_root', 'mf.square_root_used', 'mf_square_multiplier',
            lambda i, pi: [F(math.isqrt(int(i['n']) // _squarefree_part(i['n'])))])


def _prime_exps(i):
    out = [int(i['a1']), int(i['a2'])]
    if int(i['p3']):
        out.append(int(i['a3']))
    return out


scalar('mf_factor_count_primes', lambda i, pi: F(math.prod(e + 1 for e in _prime_exps(i))))
scalar_slip('mf.primes_powers_added', 'mf.powers_added', 'mf_factor_count_primes', lambda i, pi: [F(sum(_prime_exps(i)))])
scalar_slip('mf.primes_powers_product', 'mf.powers_not_plus_one', 'mf_factor_count_primes',
            lambda i, pi: [F(math.prod(_prime_exps(i)))])


def _laps(i):
    lcm = math.lcm(int(i['a']), int(i['b']))
    return lcm // int(i['a']), lcm // int(i['b'])


pair('mf_laps', _laps)
pair_slip('mf.laps_swap', 'mf.laps_swapped', 'mf_laps', lambda i: [(_laps(i)[1], _laps(i)[0])])
pair_slip('mf.laps_lap_times', 'mf.laps_times', 'mf_laps', lambda i: [(int(i['a']), int(i['b']))], echo=True)


# ---- number, ratio and proportion ------------------------------------------------------------------------------------

scalar('num_reciprocal', lambda i, pi: F(i['d']) / F(i['n']))
scalar_slip('num.reciprocal_neg', 'num.reciprocal_negative', 'num_reciprocal', lambda i, pi: [-F(i['n']) / F(i['d'])])
scalar_slip('num.reciprocal_unchanged', 'num.reciprocal_same', 'num_reciprocal', lambda i, pi: [F(i['n']) / F(i['d'])], echo=True)
scalar('num_counting', lambda i, pi: F(i['n1']) * F(i['n2']) * F(i['n3']))
scalar_slip('num.counting_sum', 'num.counting_added', 'num_counting', lambda i, pi: [F(i['n1']) + F(i['n2']) + F(i['n3'])])
scalar_slip('num.counting_stage', 'num.counting_stage_missed', 'num_counting',
            lambda i, pi: [F(i['n1']) * F(i['n2'])] if F(i['n3']) > 1 else [])


def _diff_part(i):
    return F(i['diff']) / (F(i['b']) - F(i['a']))


def _diff_truth(i, pi=None):
    part = _diff_part(i)
    return (F(i['a']) + F(i['b'])) * part if i['ask'] == 'total' else F(i['a']) * part


scalar('ratio_from_difference', _diff_truth)
scalar_slip('ratio.difference_part', 'ratio.difference_as_part', 'ratio_from_difference',
            lambda i, pi: [(F(i['a']) + F(i['b'])) * F(i['diff']) if i['ask'] == 'total' else F(i['a']) * F(i['diff'])])
scalar('prop_square', lambda i, pi: F(i['y1']) * (F(i['x2']) / F(i['x1'])) ** 2)
scalar_slip('ratio.square_linear', 'ratio.square_as_linear', 'prop_square',
            lambda i, pi: [F(i['y1']) * F(i['x2']) / F(i['x1'])])


def _combine(i):
    a, b, c, d = (int(i[k]) for k in ('a', 'b', 'c', 'd'))
    lcm = math.lcm(b, c)
    parts = [a * (lcm // b), lcm, d * (lcm // c)]
    g = math.gcd(math.gcd(parts[0], parts[1]), parts[2])
    return [p // g for p in parts]


part('ratio_combine', _combine)
slip('ratio.combine_chained', 'ratio.middle_not_matched', 'ratio_combine',
     lambda i: [[int(i['a']), int(i['b']), int(i['d'])]] if int(i['b']) != int(i['c']) else [], echo=True)


# ---- forming equations -----------------------------------------------------------------------------------------------

def _whole(values):
    """Only the whole-number slips (review): the answer is a whole number, so a slip that is not one would be typed as a
    decimal or rounded, and a rounded 151/7 = 22 met the key's neighbour 22 (a plain slip by one) and named the wrong
    cause. Prefer silence."""
    return [v for v in values if F(v).denominator == 1]


def _perimeter_truth(i, pi=None):
    a, b, p = F(i['a']), F(i['b']), F(i['p'])
    return p / 2 - a - b if i['kind'] == 'rect' else (p - a + b) / 4


def _perimeter_slips(i, pi=None):
    a, b, p = F(i['a']), F(i['b']), F(i['p'])
    return [p - a - b] if i['kind'] == 'rect' else []


scalar('alg_form_perimeter', _perimeter_truth)
scalar_slip('alg.perimeter_two_sides', 'alg.perimeter_two_sides', 'alg_form_perimeter', _apart('alg_form_perimeter', _perimeter_slips))
scalar_slip('alg.perimeter_sign_moved', 'alg.sign_moved', 'alg_form_perimeter',
            _apart('alg_form_perimeter', lambda i, pi: _whole([(F(i['p']) - F(i['a']) - F(i['b'])) / 4] if i['kind'] == 'tri' else [])))


def _angles_truth(i, pi=None):
    s_ = F(i['c1']) + F(i['c2']) + F(i['c3'])
    return (F(i['total']) - F(i['a']) + F(i['b'])) / s_


scalar('alg_angles', _angles_truth)
scalar_slip('alg.angles_sign_moved', 'alg.sign_moved', 'alg_angles',
            _apart('alg_angles', lambda i, pi: _whole([(F(i['total']) - F(i['a']) - F(i['b'])) / (F(i['c1']) + F(i['c2']) + F(i['c3']))])))
scalar_slip('alg.angles_x_once', 'alg.x_terms_counted', 'alg_angles',
            _apart('alg_angles', lambda i, pi: _whole([(F(i['total']) - F(i['a']) + F(i['b'])) / 3])))


def _area_truth(i, pi=None):
    a, b, area = F(i['a']), F(i['b']), F(i['area'])
    bq, cq = a - b, -(a * b + area)
    disc = bq * bq - 4 * cq
    return (-bq + sqrtq(disc)) / 2


scalar('alg_form_area', _area_truth)
scalar_slip('alg.area_negative_root', 'alg.negative_length', 'alg_form_area',
            lambda i, pi: [F(i['b']) - F(i['a']) - _area_truth(i)])


# ---- arithmetic ------------------------------------------------------------------------------------------------------

def _missing_truth(i, pi=None):
    a, c, form = F(i['a']), F(i['c']), i['form']
    b = F(i['b']) if i.get('b') is not None else None
    if form == 'add_mul':
        return (c - a) / b
    if form == 'bracket_mul':
        return c / a - b
    if form == 'mul_sub':
        return (c + b) / a
    if form == 'sub_square':
        return sqrtq(a - c)
    raise ValueError('form')


def _missing_inverse(i, pi=None):
    a, c, form = F(i['a']), F(i['c']), i['form']
    b = F(i['b']) if i.get('b') is not None else None
    if form == 'add_mul':
        return [(c + a) / b]
    if form == 'bracket_mul':
        return [c / a + b]
    if form == 'mul_sub':
        return [(c - b) / a]
    return []


def _missing_square(i, pi=None):
    return [F(i['a']) - F(i['c'])] if i['form'] == 'sub_square' else []


scalar('bidmas_missing', _missing_truth)
scalar_slip('bidmas.missing_wrong_inverse', 'bidmas.missing_inverse', 'bidmas_missing',
            _apart('bidmas_missing', lambda i, pi: [v for v in _whole(_missing_inverse(i, pi)) if v > 0]))
scalar_slip('bidmas.missing_square_kept', 'alg.root_missed', 'bidmas_missing', _apart('bidmas_missing', _missing_square))


def _bar_truth(i, pi=None):
    return (F(i['a']) + F(i['b']) * F(i['c'])) / (F(i['d']) - F(i['e']))


scalar('bidmas_fraction_bar', _bar_truth)
scalar_slip('bidmas.bar_no_brackets', 'bidmas.fraction_bar', 'bidmas_fraction_bar',
            _apart('bidmas_fraction_bar', lambda i, pi: [F(i['a']) + F(i['b']) * F(i['c']) / F(i['d']) - F(i['e'])]))


def _bar_neg_truth(i, pi=None):
    n, p = F(i['n']), int(i['p'])
    return (F(i['a']) - (-n) ** p) / (F(i['b']) - F(i['e']) ** 2)


scalar('bidmas_fraction_bar_neg', _bar_neg_truth)
scalar_slip('bidmas.bar_neg_no_brackets', 'bidmas.fraction_bar', 'bidmas_fraction_bar_neg',
            _apart('bidmas_fraction_bar_neg',
                   lambda i, pi: [F(i['a']) - (-F(i['n'])) ** int(i['p']) / F(i['b']) - F(i['e']) ** 2]))
scalar_slip('bidmas.bar_neg_square', 'bidmas.negative_square', 'bidmas_fraction_bar_neg',
            _apart('bidmas_fraction_bar_neg',
                   lambda i, pi: [(F(i['a']) + F(i['n']) ** 2) / (F(i['b']) - F(i['e']) ** 2)] if int(i['p']) == 2 else []))
scalar('surds_square', lambda i, pi: F(i['k']) ** 2 * F(i['r']))
scalar_slip('surd.square_coefficient', 'surd.square_coefficient_missed', 'surds_square', lambda i, pi: [F(i['k']) * F(i['r'])])


def _whole_minus_decimal(i, pi):
    """7 - 6.4 worked as (7 - 6) and then the .4 put straight back: 1.4 (the whole part is the only thing subtracted)."""
    a, b = F(str(i['a'])), F(str(i['b']))
    if i.get('op') not in ('-', '−') or a.denominator != 1 or b.denominator == 1 or b >= a:
        return []
    whole = math.floor(b)
    return [a - whole + (b - whole)]


RULES.append(_r('dec.whole_minus_decimal', 'dec.not_aligned', ['num_directed'], _whole_minus_decimal))
scalar('dec_round_error', lambda i, pi: abs(F(str(i['x'])) - Fraction(math.floor(F(str(i['x'])) * 10 ** int(i['dp']) + Fraction(1, 2)), 10 ** int(i['dp']))))
scalar_slip('dec.round_error_rounded', 'dec.rounded_not_difference', 'dec_round_error',
            lambda i, pi: [Fraction(math.floor(F(str(i['x'])) * 10 ** int(i['dp']) + Fraction(1, 2)), 10 ** int(i['dp']))], echo=True)


def _root_mix_truth(i, pi=None):
    root = math.isqrt(int(i['r']))
    if int(i['kind']) == 0:
        return F(root + int(i['b']) * int(i['c']) ** int(i['p']))
    return F(int(i['a']) - root * int(i['c']))


scalar('bidmas_root_mix', _root_mix_truth)
scalar_slip('bidmas.root_mix_left_to_right', 'bidmas.left_to_right', 'bidmas_root_mix',
            _apart('bidmas_root_mix',
                   lambda i, pi: [F((math.isqrt(int(i['r'])) + int(i['b'])) * int(i['c']) ** int(i['p']))] if int(i['kind']) == 0
                   else [F((int(i['a']) - math.isqrt(int(i['r']))) * int(i['c']))]))
scalar('bidmas_sub_neg', lambda i, pi: F(int(i['k1']) * int(i['a']) ** 2 - int(i['k2']) * int(i['b'])))
scalar_slip('bidmas.sub_neg_square', 'bidmas.negative_square', 'bidmas_sub_neg',
            _apart('bidmas_sub_neg', lambda i, pi: [F(-int(i['k1']) * int(i['a']) ** 2 - int(i['k2']) * int(i['b']))]))


def _pf_exponent_list(i):
    n, out = int(i['n']), []
    for key in ('p1', 'p2', 'p3'):
        p_ = int(i[key])
        if p_ < 2:
            continue
        e = 0
        while n % p_ == 0:
            n //= p_
            e += 1
        out.append(e)
    return out


part('mf_pf_exponents', _pf_exponent_list)
def _pf_swapped(i):
    e = _pf_exponent_list(i)
    if e[0] == e[1]:
        return []
    return [[e[1]] + [None] * (len(e) - 1), [None, e[0]] + [None] * (len(e) - 2)]


slip('mf.exponents_swapped', 'mf.exponents_swapped', 'mf_pf_exponents', _pf_swapped, echo=True)


# =============================================================================================
# Phase 3 batch B (docs/GCSE_MATHS_VARIETY.md, Phase 3 batch B build notes): simultaneous equations, completing the square,
# quadratic simultaneous equations, algebraic fractions, functions and iteration. Only the record families whose key is
# one number, a pair or a few boxes can carry a rule; the slots checked by ``@verifies('alg')`` tasks cannot.
# =============================================================================================

def _solve2(i, a1='a1', b1='b1', c1='c1', a2='a2', b2='b2', c2='c2'):
    a1, b1, c1, a2, b2, c2 = (F(i[k]) for k in (a1, b1, c1, a2, b2, c2))
    det = a1 * b2 - a2 * b1
    return (c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det


def _expr_value_truth(i, pi=None):
    x, y = _solve2(i)
    return x * y if i['ask'] == 'xy' else x * x + y * y


def _expr_value_sum(i, pi=None):
    x, y = _solve2(i)
    return [x + y if i['ask'] == 'xy' else (x + y) ** 2]


scalar('sim_expr_value', _expr_value_truth)
scalar_slip('sim.expr_value_sum', 'alg.expression_sum', 'sim_expr_value', _apart('sim_expr_value', _expr_value_sum))

scalar('sim_parallel_k', lambda i, pi: F(i['a2']) * F(i['b1']) / F(i['a1']))
scalar_slip('sim.parallel_k_one_term', 'alg.parallel_one_term', 'sim_parallel_k',
            _apart('sim_parallel_k', lambda i, pi: [F(i['b1'])]), echo=True)


def _equal_cost_truth(i):
    n = (F(i['f2']) - F(i['f1'])) / (F(i['r1']) - F(i['r2']))
    return n, F(i['f1']) + F(i['r1']) * n


pair('sim_equal_cost', _equal_cost_truth)
pair_slip('sim.equal_cost_not_divided', 'alg.rate_not_divided', 'sim_equal_cost',
          lambda i: [(F(i['f2']) - F(i['f1']), _equal_cost_truth(i)[1])] if F(i['r1']) - F(i['r2']) != 1 else [])
pair_slip('sim.equal_cost_fee_missed', 'alg.fee_missed', 'sim_equal_cost',
          lambda i: [(_equal_cost_truth(i)[0], F(i['r1']) * _equal_cost_truth(i)[0])])


def _ages_truth(i):
    k, n, m = F(i['k']), F(i['n']), F(i['m'])
    child = (m - 1) * n / (k - m)
    return k * child, child


pair('sim_ages', _ages_truth)
pair_slip('sim.ages_future', 'alg.age_future', 'sim_ages',
          lambda i: [(_ages_truth(i)[0] + F(i['n']), _ages_truth(i)[1] + F(i['n']))])

pair('sim_sub_solution', lambda i: (F(i['p']) * F(i['x']) + F(i['q']) * F(i['y']), F(i['r']) * F(i['x']) + F(i['s']) * F(i['y'])))
pair_slip('sim.sub_one_term', 'alg.sub_one_term', 'sim_sub_solution',
          lambda i: [(F(i['p']) * F(i['x']), F(i['r']) * F(i['x']))])

scalar('cts_q_given_p', lambda i, pi: F(i['c']) - F(i['p']) ** 2)
scalar_slip('cts.q_constant_kept', 'cts.constant_not_adjusted', 'cts_q_given_p',
            _apart('cts_q_given_p', lambda i, pi: [F(i['c'])]), echo=True)
scalar_slip('cts.q_square_added', 'cts.square_added', 'cts_q_given_p',
            _apart('cts_q_given_p', lambda i, pi: [F(i['c']) + F(i['p']) ** 2]))

pair('cts_a_minus_sq', lambda i: (F(i['a']), F(i['p'])))
pair_slip('cts.a_minus_square_signed', 'cts.a_square_signed', 'cts_a_minus_sq',
          lambda i: [(F(i['c']) - F(i['p']) ** 2, F(i['p']))])

scalar('cts_count_roots', lambda i, pi: _count_roots(i))


def _count_roots(i):
    k = F(i['c']) - (F(i['b']) / 2) ** 2
    return F(2 if k < 0 else 1 if k == 0 else 0)


def _count_roots_flipped(i, pi=None):
    k = F(i['c']) - (F(i['b']) / 2) ** 2
    return [F(2 if k > 0 else 1 if k == 0 else 0)]


scalar_slip('cts.count_sign_flipped', 'cts.roots_sign', 'cts_count_roots', _count_roots_flipped)

pair('cts_from_vertex', lambda i: (-2 * F(i['h']), F(i['h']) ** 2 + F(i['k'])))
pair_slip('cts.vertex_constant_only', 'cts.vertex_constant_only', 'cts_from_vertex',
          lambda i: [(-2 * F(i['h']), F(i['k']))], echo=True)

part('qsim_y_from_x', lambda i: [F(i['x1']) ** 2, F(i['x2']) ** 2])
slip('qsim.y_x_values_typed', 'qsim.x_not_y', 'qsim_y_from_x', lambda i: [[F(i['x1']), F(i['x2'])]], echo=True)

scalar('qsim_circle_line_y', lambda i, pi: F(i['m']) * F(i['x']) + F(i['c']))
scalar_slip('qsim.circle_y_squared', 'qsim.circle_y_squared', 'qsim_circle_line_y',
            _apart('qsim_circle_line_y', lambda i, pi: [F(i['r2']) - F(i['x']) ** 2]))

scalar('qsim_tangent_k', lambda i, pi: F(i['c0']) - F(i['m']) ** 2 / 4)
scalar_slip('qsim.tangent_k_sign', 'qsim.discriminant_four', 'qsim_tangent_k',
            _apart('qsim_tangent_k', lambda i, pi: [F(i['c0']) - F(i['m']) ** 2]))

scalar('qsim_largest_k_miss', lambda i, pi: F(math.ceil(F(i.get('c0', 0)) - F(i['m']) ** 2 / 4) - 1))
scalar_slip('qsim.largest_k_four_missed', 'qsim.discriminant_four', 'qsim_largest_k_miss',
            _apart('qsim_largest_k_miss', lambda i, pi: [F(i.get('c0', 0)) - F(i['m']) ** 2 - 1]))


pair('qsim_midpoint', lambda i: (F(i['m']) / 2, F(i['m']) ** 2 / 2 + F(i['c'])))
pair_slip('qsim.midpoint_on_curve', 'qsim.midpoint_curve', 'qsim_midpoint',
          lambda i: [(F(i['m']) / 2, (F(i['m']) / 2) ** 2)])

scalar('af_undefined', lambda i, pi: -F(i['b']) / F(i['a']))
scalar_slip('af.undefined_not_divided', 'af.undefined_not_divided', 'af_undefined',
            _apart('af_undefined', lambda i, pi: [-F(i['b'])] if F(i['a']) != 1 else []))

scalar('fn_inverse_value', lambda i, pi: (F(i['y']) - F(i['c'])) / F(i['m']))
scalar_slip('fn.inverse_applied', 'fn.inverse_applied', 'fn_inverse_value',
            _apart('fn_inverse_value', lambda i, pi: [F(i['m']) * F(i['y']) + F(i['c'])]))
scalar_slip('fn.inverse_sign', 'fn.inverse_sign', 'fn_inverse_value',
            _apart('fn_inverse_value', lambda i, pi: [(F(i['y']) + F(i['c'])) / F(i['m'])]))


# Phase 3 batch B review (2026-10-28): rules for four slots that now record a family (they were 'alg' tasks, which
# carry no answer record) and for the substitution slot whose family had no rule.
def _sub_coeff_slips(i):
    """x^2 = m x + c to x^2 + p x + q = 0: p = -m and q = -c. The terms moved without changing sign: (m, c), or only
    one of them changed. A slip that is the key with its parts swapped is left to the generic swap line."""
    m, c = F(i['m']), F(i['c'])
    key, swapped = (-m, -c), (-c, -m)
    return [v for v in ((m, c), (-m, c), (m, -c)) if v not in (key, swapped)]


pair('qsim_sub_coeffs', lambda i: (-F(i['m']), -F(i['c'])))
pair_slip('qsim.sub_signs_kept', 'alg.sign_moved', 'qsim_sub_coeffs', _sub_coeff_slips, echo=True)

scalar('fn_neg_input', lambda i, pi: F(i['c']) - F(i['m']) * F(i['x']))
scalar_slip('fn.neg_input_sign', 'fn.negative_not_bracketed', 'fn_neg_input',
            _apart('fn_neg_input', lambda i, pi: [F(i['c']) + F(i['m']) * F(i['x'])]))
# the slot was reached before through the 'fn_eval' task's question parser (family gr_subst), whose one applicable rule
# reads 5x at x = -1 as 5 - 1; kept here so the record family loses nothing
scalar_slip('fn.neg_input_implied', 'sub.implied_multiply', 'fn_neg_input',
            _apart('fn_neg_input', lambda i, pi: [F(i['c']) - (F(i['m']) + F(i['x']))]))

scalar('cts_min_read', lambda i, pi: F(i['k']))
scalar_slip('cts.min_read_x_value', 'cts.min_x_not_y', 'cts_min_read',
            _apart('cts_min_read', lambda i, pi: [-F(i['p'])]), echo=True)


def _nonmonic_min(i, pi=None):
    return F(i['c']) - F(i['b']) ** 2 / (4 * F(i['a']))


scalar('cts_min_nonmonic', _nonmonic_min)
scalar_slip('cts.min_nonmonic_a_missed', 'cts.a_not_multiplied', 'cts_min_nonmonic',
            _apart('cts_min_nonmonic', lambda i, pi: [F(i['c']) - (F(i['b']) / (2 * F(i['a']))) ** 2]))
scalar_slip('cts.min_nonmonic_x_value', 'cts.min_x_not_y', 'cts_min_nonmonic',
            _apart('cts_min_nonmonic', lambda i, pi: [-F(i['b']) / (2 * F(i['a']))]))

scalar('ap_bracket_const', lambda i, pi: F(i['a']) * F(i['b']))
scalar_slip('ap.bracket_second_term', 'alg.bracket_not_all', 'ap_bracket_const',
            _apart('ap_bracket_const', lambda i, pi: [F(i['b'])]), echo=True)


def _iter_linear(i):
    x1 = F(i['a']) * F(i['x0']) + F(i['b'])
    return x1, F(i['a']) * x1 + F(i['b'])


part('eq_iterate_linear', lambda i: list(_iter_linear(i)))
slip('eq.iterate_linear_constant_once', 'eq.iterate_constant_once', 'eq_iterate_linear',
     lambda i: [[None, F(i['a']) * _iter_linear(i)[0]]])


def _iter_recip(i):
    x1 = F(i['a']) + F(i['b']) / F(i['x0'])
    return x1, F(i['a']) + F(i['b']) / x1


part('eq_iterate_recip', lambda i: list(_iter_recip(i)), decimal=(1,))
slip('eq.iterate_recip_a_missed', 'eq.iterate_reciprocal', 'eq_iterate_recip',
     lambda i: [[None, F(i['b']) / _iter_recip(i)[0]]])


def _sign_change(i):
    p, k = F(i['p']), F(i['k'])
    f = [x ** 3 + p * x - k for x in (1, 2, 3)]
    return f + [F(1 if f[1] > 0 else 2)]


part('eq_sign_change', _sign_change)
slip('eq.change_constant_sign', 'eq.change_constant_sign', 'eq_sign_change',
     lambda i: [[F(x) ** 3 + F(i['p']) * F(x) + F(i['k'])
                 for x in (1, 2, 3)] + [None]])

# =============================================================================================
# Phase 3 batch C1 (docs/GCSE_MATHS_VARIETY.md section 21): statistics, probability, graphs, ratio, trigonometry and
# Pythagoras. The same contract: TRUTH rebuilds the key from the printed numbers, _apart drops a slip a generic rule
# explains, and a slip that equals a printed number speaks only with echo=True.
# =============================================================================================

def _cells(i):
    return [[F(v) for v in row] for row in i['cells']]


def _two_way_read_truth(i, pi=None):
    cells = _cells(i)
    k = int(i['index'])
    if i['ask'] == 'row':
        return sum(cells[k])
    if i['ask'] == 'col':
        return cells[0][k] + cells[1][k]
    return sum(sum(r) for r in cells)


def _two_way_other_way(i, pi=None):
    cells = _cells(i)
    if i['ask'] == 'row':
        return [cells[0][j] + cells[1][j] for j in range(3)]
    if i['ask'] == 'col':
        return [sum(r) for r in cells]
    return []


def _two_way_part_only(i, pi=None):
    cells = _cells(i)
    if i['ask'] != 'all':
        return []
    return [sum(r) for r in cells] + [cells[0][j] + cells[1][j] for j in range(3)]


scalar('stats_two_way_read', _two_way_read_truth)
scalar_slip('stats.two_way_other_way', 'stats.two_way_other_way', 'stats_two_way_read', _apart('stats_two_way_read', _two_way_other_way))
scalar_slip('stats.two_way_part_only', 'stats.two_way_part_only', 'stats_two_way_read', _apart('stats_two_way_read', _two_way_part_only))


def _two_way_complete_truth(i):
    r0c1, r0c2, r1c0, row0, row1, col1, col2 = (F(i[k]) for k in ('r0c1', 'r0c2', 'r1c0', 'row0', 'row1', 'col1', 'col2'))
    return [row0 - r0c1 - r0c2, col1 - r0c1, col2 - r0c2]


part('stats_two_way_complete', _two_way_complete_truth)
slip('stats.two_way_complete_grand', 'stats.two_way_wrong_total', 'stats_two_way_complete',
     lambda i: [[F(i['grand']) - F(i['r0c1']) - F(i['r0c2']), None, None]])
slip('stats.two_way_complete_two_missing', 'stats.two_way_two_missing', 'stats_two_way_complete',
     lambda i: [[None, F(i['row1']) - F(i['r1c0']), None], [None, None, F(i['row1']) - F(i['r1c0'])]])


def _two_way_percent_truth(i, pi=None):
    cells = _cells(i)
    r, c = int(i['row']), int(i['col'])
    return 100 * cells[r][c] / sum(cells[r])


def _two_way_percent_slips(i, pi=None):
    cells = _cells(i)
    r, c = int(i['row']), int(i['col'])
    grand = sum(sum(x) for x in cells)
    return [100 * cells[r][c] / grand, 100 * cells[r][c] / (cells[0][c] + cells[1][c])]


scalar('stats_two_way_percent', _two_way_percent_truth)
scalar_slip('stats.percent_wrong_total', 'stats.percent_wrong_total', 'stats_two_way_percent',
            _apart('stats_two_way_percent', _two_way_percent_slips))


def _stem_values(i):
    return [10 * int(st) + int(leaf) for st, row in zip(i['stems'], i['leaves']) for leaf in row]


def _stem_truth(i, pi=None):
    vals = _stem_values(i)
    n = len(vals)
    if i['ask'] == 'median':
        return vals[n // 2]
    if i['ask'] == 'range':
        return vals[-1] - vals[0]
    return vals[3 * (n + 1) // 4 - 1] - vals[(n + 1) // 4 - 1]


scalar('stats_stem_leaf', _stem_truth)
scalar_slip('stats.stem_leaf_only', 'stats.leaf_only', 'stats_stem_leaf',
            _apart('stats_stem_leaf', lambda i, pi: [_stem_values(i)[len(_stem_values(i)) // 2] % 10] if i['ask'] == 'median' else []),
            echo=True)
scalar_slip('stats.stem_range_largest', 'stats.range_largest', 'stats_stem_leaf',
            _apart('stats_stem_leaf', lambda i, pi: [_stem_values(i)[-1]] if i['ask'] == 'range' else []), echo=True)
scalar_slip('stats.stem_iqr_range', 'stats.iqr_range', 'stats_stem_leaf',
            _apart('stats_stem_leaf', lambda i, pi: [_stem_values(i)[-1] - _stem_values(i)[0]] if i['ask'] == 'iqr' else []))
scalar_slip('stats.stem_iqr_upper', 'stats.iqr_upper_quartile', 'stats_stem_leaf',
            _apart('stats_stem_leaf', lambda i, pi: [_stem_values(i)[3 * (len(_stem_values(i)) + 1) // 4 - 1]] if i['ask'] == 'iqr' else []),
            echo=True)


def _table_mode_truth(i, pi=None):
    freqs = [int(f) for f in i['freqs']]
    return F(i['values'][freqs.index(max(freqs))])


scalar('stats_table_mode', _table_mode_truth)
scalar_slip('stats.table_mode_count', 'stats.mode_count', 'stats_table_mode',
            _apart('stats_table_mode', lambda i, pi: [max(int(f) for f in i['freqs'])]), echo=True)


def _table_median_truth(i, pi=None):
    n = sum(int(f) for f in i['freqs'])
    pos, running = (n + 1) // 2, 0
    for v, f in zip(i['values'], i['freqs']):
        running += int(f)
        if running >= pos:
            return F(v)
    return F(i['values'][-1])


scalar('stats_table_median', _table_median_truth)
scalar_slip('stats.table_median_middle_row', 'stats.median_middle_row', 'stats_table_median',
            _apart('stats_table_median', lambda i, pi: [F(i['values'][len(i['values']) // 2])]), echo=True)
scalar_slip('stats.table_median_position', 'stats.median_position_typed', 'stats_table_median',
            _apart('stats_table_median', lambda i, pi: [F(sum(int(f) for f in i['freqs']) + 1) / 2]))

scalar('stats_missing_value', lambda i, pi: F(i['mean']) * _n(i['n']) - sum(F(k) for k in i['known']))
scalar_slip('stats.missing_mean_of_known', 'stats.missing_mean_of_known', 'stats_missing_value',
            _apart('stats_missing_value', lambda i, pi: [sum(F(k) for k in i['known']) / (_n(i['n']) - 1)]))
scalar_slip('stats.missing_count_short', 'stats.missing_count_short', 'stats_missing_value',
            _apart('stats_missing_value', lambda i, pi: [F(i['mean']) * (_n(i['n']) - 1) - sum(F(k) for k in i['known'])]))



scalar('stats_combined_mean', lambda i, pi: (F(i['n1']) * F(i['m1']) + F(i['n2']) * F(i['m2'])) / (F(i['n1']) + F(i['n2'])))
scalar_slip('stats.mean_of_means', 'stats.mean_of_means', 'stats_combined_mean',
            _apart('stats_combined_mean', lambda i, pi: [(F(i['m1']) + F(i['m2'])) / 2]))

scalar('stats_sample_scale', lambda i, pi: F(i['hits']) / F(i['sample']) * F(i['pop']))
scalar_slip('stats.sample_upside_down', 'stats.proportion_upside_down', 'stats_sample_scale',
            _apart('stats_sample_scale', lambda i, pi: [F(i['sample']) / F(i['hits']) * F(i['pop'])]))

scalar('stats_recapture', lambda i, pi: F(i['m']) * F(i['n']) / F(i['k']))
scalar_slip('stats.recapture_upside_down', 'stats.recapture_upside_down', 'stats_recapture',
            _apart('stats_recapture', lambda i, pi: [F(i['n']) * F(i['k']) / F(i['m']), F(i['m']) * F(i['k']) / F(i['n'])]))


def _polygon_truth(i, pi=None):
    freqs = [F(f) for f in i['freqs']]
    if i['ask'] == 'total':
        return sum(freqs)
    mids = [(F(lo) + F(hi)) / 2 for lo, hi in i['intervals']]
    return sum(m * f for m, f in zip(mids, freqs)) / sum(freqs)


def _polygon_class_end(i, pi=None):
    if i['ask'] != 'mean':
        return []
    freqs = [F(f) for f in i['freqs']]
    return [sum(F(hi) * f for (lo, hi), f in zip(i['intervals'], freqs)) / sum(freqs)]


def _polygon_freq_mean(i, pi=None):
    if i['ask'] != 'mean':
        return []
    freqs = [F(f) for f in i['freqs']]
    return [sum(freqs) / len(freqs)]


scalar('stats_polygon', _polygon_truth)
scalar_slip('stats.polygon_peak_only', 'stats.polygon_peak_only', 'stats_polygon',
            _apart('stats_polygon', lambda i, pi: [max(F(f) for f in i['freqs'])] if i['ask'] == 'total' else []), echo=True)
scalar_slip('stats.polygon_class_end', 'stats.polygon_class_end', 'stats_polygon', _apart('stats_polygon', _polygon_class_end))
scalar_slip('stats.polygon_freq_mean', 'stats.polygon_freq_mean', 'stats_polygon', _apart('stats_polygon', _polygon_freq_mean))


def _series_four(i):
    y = int(i['year'])
    return [F(v) for v in i['values'][4 * y:4 * y + 4]]


scalar('stats_series_mean', lambda i, pi: sum(_series_four(i)) / 4)
scalar_slip('stats.series_all_points', 'stats.series_all_points', 'stats_series_mean',
            _apart('stats_series_mean', lambda i, pi: [sum(F(v) for v in i['values']) / 8]))
scalar_slip('stats.series_not_divided', 'stats.series_not_divided', 'stats_series_mean',
            _apart('stats_series_mean', lambda i, pi: [sum(_series_four(i))]))


# ---- probability ----------------------------------------------------------------------------------------------------
def _event_test(text):
    t = str(text).strip().lower()
    m = re.match(r'equal to (\d+)$', t)
    if m:
        return lambda v: v == int(m.group(1))
    m = re.match(r'more than (\d+)$', t)
    if m:
        return lambda v: v > int(m.group(1))
    m = re.match(r'less than (\d+)$', t)
    if m:
        return lambda v: v < int(m.group(1))
    m = re.match(r'a multiple of (\d+)$', t)
    if m:
        return lambda v: v % int(m.group(1)) == 0
    return {'an even number': lambda v: v % 2 == 0, 'an odd number': lambda v: v % 2 == 1,
            'a prime number': lambda v: v > 1 and all(v % d for d in range(2, math.isqrt(v) + 1)),
            'a square number': lambda v: math.isqrt(v) ** 2 == v}.get(t)


def _space_outcomes(i):
    n1, n2 = _n(i['n1']), _n(i['n2'])
    return [(a + b if i['op'] == 'sum' else a * b) for a in range(1, n1 + 1) for b in range(1, n2 + 1)]


def _space_truth(i, pi=None):
    test = _event_test(i['event_word'])
    outcomes = _space_outcomes(i)
    return Fraction(sum(1 for v in outcomes if test(v)), len(outcomes))


def _space_distinct(i, pi=None):
    test = _event_test(i['event_word'])
    distinct = sorted(set(_space_outcomes(i)))
    return [Fraction(sum(1 for v in distinct if test(v)), len(distinct))]


scalar('prob_sample_space', _space_truth)
scalar_slip('prob.space_distinct_totals', 'prob.space_distinct_totals', 'prob_sample_space', _apart('prob_sample_space', _space_distinct))


def _tree_fill_truth(i):
    total, a, aa, bb = (F(i[k]) for k in ('total', 'a', 'aa', 'bb'))
    return [total - a, a - aa, total - a - bb]


part('prob_freq_tree_fill', _tree_fill_truth)
slip('prob.tree_fill_total', 'prob.tree_total_not_group', 'prob_freq_tree_fill',
     lambda i: [[None, F(i['total']) - F(i['aa']), None], [None, None, F(i['total']) - F(i['bb'])]])
slip('prob.tree_fill_wrong_group', 'prob.tree_wrong_group', 'prob_freq_tree_fill',
     lambda i: [[None, None, F(i['a']) - F(i['bb'])]])


def _tree_cond_parts(i):
    aa, ab, ba, bb = (F(i[k]) for k in ('aa', 'ab', 'ba', 'bb'))
    yes = i['cond'] == 'yes'
    pool = aa + ba if yes else ab + bb
    hits = (aa if yes else ab) if i['group'] == 'g1' else (ba if yes else bb)
    group = aa + ab if i['group'] == 'g1' else ba + bb
    return hits, pool, group, aa + ab + ba + bb


scalar('prob_freq_tree_cond', lambda i, pi: _tree_cond_parts(i)[0] / _tree_cond_parts(i)[1])
scalar_slip('prob.tree_cond_joint', 'prob.joint_not_conditional', 'prob_freq_tree_cond',
            _apart('prob_freq_tree_cond', lambda i, pi: [_tree_cond_parts(i)[0] / _tree_cond_parts(i)[3]]))
scalar_slip('prob.tree_cond_wrong_group', 'prob.condition_wrong_group', 'prob_freq_tree_cond',
            _apart('prob_freq_tree_cond', lambda i, pi: [_tree_cond_parts(i)[0] / _tree_cond_parts(i)[2]]))


def _two_way_prob_parts(i):
    cells = _cells(i)
    r, c = int(i['row']), int(i['col'])
    grand = sum(sum(x) for x in cells)
    row_tot, col_tot = sum(cells[r]), cells[0][c] + cells[1][c]
    return cells[r][c], row_tot, col_tot, grand


def _two_way_prob_truth(i, pi=None):
    cell, row_tot, col_tot, grand = _two_way_prob_parts(i)
    ask = i['ask']
    return {'cell': cell / grand, 'col': col_tot / grand, 'row': row_tot / grand,
            'given_row': cell / row_tot, 'given_col': cell / col_tot}[ask]


def _two_way_prob_group_total(i, pi=None):
    cell, row_tot, col_tot, grand = _two_way_prob_parts(i)
    if i['ask'] == 'cell':
        return [cell / row_tot, cell / col_tot]
    return []


def _two_way_prob_one_cell(i, pi=None):
    cell, row_tot, col_tot, grand = _two_way_prob_parts(i)
    return [cell / grand] if i['ask'] in ('row', 'col') else []


def _two_way_prob_joint(i, pi=None):
    cell, row_tot, col_tot, grand = _two_way_prob_parts(i)
    return [cell / grand] if i['ask'] in ('given_row', 'given_col') else []


def _two_way_prob_wrong_group(i, pi=None):
    cell, row_tot, col_tot, grand = _two_way_prob_parts(i)
    if i['ask'] == 'given_row':
        return [cell / col_tot]
    if i['ask'] == 'given_col':
        return [cell / row_tot]
    return []


scalar('prob_two_way', _two_way_prob_truth)
scalar_slip('prob.two_way_group_total', 'prob.two_way_group_total', 'prob_two_way', _apart('prob_two_way', _two_way_prob_group_total))
scalar_slip('prob.two_way_one_cell', 'prob.two_way_one_cell', 'prob_two_way', _apart('prob_two_way', _two_way_prob_one_cell))
scalar_slip('prob.two_way_joint', 'prob.joint_not_conditional', 'prob_two_way', _apart('prob_two_way', _two_way_prob_joint))
scalar_slip('prob.two_way_wrong_group', 'prob.condition_wrong_group', 'prob_two_way', _apart('prob_two_way', _two_way_prob_wrong_group))


def _venn(i):
    return (F(i['a_only']), F(i['b_only']), F(i['both']), F(i['neither']))


def _venn_truth(i, pi=None):
    a, b, c, d = _venn(i)
    total = a + b + c + d
    given = i.get('given')
    if given == 'A':
        return c / (a + c)
    if given == 'B':
        return c / (b + c)
    sets = {'A ∪ B': a + b + c, 'A ∩ B': c, "A'": b + d, "A' ∩ B": b, "A ∩ B'": a, "(A ∪ B)'": d}
    return sets[i['ask_word']] / total


def _venn_slip(wanted, pick):
    """A slip for the Venn family: ``pick(a, b, c, d, total)`` when the question asks ``wanted`` (a set name or 'given')."""
    def fn(i, pi=None):
        a, b, c, d = _venn(i)
        total = a + b + c + d
        key = 'given' if i.get('given') else i['ask_word']
        if key not in wanted:
            return []
        return [pick(a, b, c, d, total)]
    return fn


scalar('prob_venn_set', _venn_truth)
scalar_slip('prob.venn_union_as_intersection', 'prob.union_as_intersection', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(('A ∪ B',), lambda a, b, c, d, t: c / t)))
scalar_slip('prob.venn_union_overlap_twice', 'prob.overlap_counted_twice', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(('A ∪ B',), lambda a, b, c, d, t: (a + b + 2 * c) / t)))
scalar_slip('prob.venn_intersection_as_union', 'prob.intersection_as_union', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(('A ∩ B',), lambda a, b, c, d, t: (a + b + c) / t)))
scalar_slip('prob.venn_set_not_complemented', 'prob.not_complemented', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(("A'", "(A ∪ B)'"), lambda a, b, c, d, t: (a + c) / t if a + c != 0 else 0)))
scalar_slip('prob.venn_set_neither_missed', 'prob.neither_missed', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(("A'",), lambda a, b, c, d, t: b / t)))
scalar_slip('prob.venn_complement_ignored', 'prob.complement_ignored', 'prob_venn_set',
            _apart('prob_venn_set', lambda i, pi: ([(_venn(i)[1] + _venn(i)[2]) / sum(_venn(i))] if i['ask_word'] == "A' ∩ B" else
                                                   [(_venn(i)[0] + _venn(i)[2]) / sum(_venn(i))] if i['ask_word'] == "A ∩ B'" else [])))
scalar_slip('prob.venn_given_joint', 'prob.joint_not_conditional', 'prob_venn_set',
            _apart('prob_venn_set', _venn_slip(('given',), lambda a, b, c, d, t: c / t)))
scalar_slip('prob.venn_given_wrong_circle', 'prob.condition_wrong_group', 'prob_venn_set',
            _apart('prob_venn_set', lambda i, pi: ([_venn(i)[2] / (_venn(i)[1] + _venn(i)[2])] if i.get('given') == 'A' else
                                                   [_venn(i)[2] / (_venn(i)[0] + _venn(i)[2])] if i.get('given') == 'B' else [])))


# ---- graphs ---------------------------------------------------------------------------------------------------------
def _circle_truth(i, pi=None):
    if i['ask'] == 'k':
        return F(i['x']) ** 2 + F(i['y']) ** 2
    return F(math.isqrt(int(F(i['k']))))


def _circle_radius_slip(i, pi=None):
    if i['ask'] != 'k':
        return []
    k = int(F(i['x']) ** 2 + F(i['y']) ** 2)
    r = math.isqrt(k)
    return [r] if r * r == k else []


scalar('gr_circle_k', _circle_truth)
scalar_slip('gr.circle_radius_not_squared', 'gr.circle_radius_not_squared', 'gr_circle_k', _apart('gr_circle_k', _circle_radius_slip))
scalar_slip('gr.circle_coords_added', 'gr.circle_coords_added', 'gr_circle_k',
            _apart('gr_circle_k', lambda i, pi: [abs(F(i['x'])) + abs(F(i['y']))] if i['ask'] == 'k' else []))
# (gr.circle_root_missed and gr.circle_halved went when the radius draw left gcse_gra_circle_equation: review C11)


def _vt_truth(i, pi=None):
    v, t1, t2, t3 = (F(i[k]) for k in ('v', 't1', 't2', 't3'))
    return {'first': v / t1, 'last': v / t3, 'distance': v * t1 / 2 + v * t2 + v * t3 / 2}[i['ask']]


def _vt_area_for_gradient(i, pi=None):
    v, t1, t3 = F(i['v']), F(i['t1']), F(i['t3'])
    return [v * t1 / 2] if i['ask'] == 'first' else [v * t3 / 2] if i['ask'] == 'last' else []


scalar('gr_vt', _vt_truth)
scalar_slip('gr.vt_area_for_gradient', 'gr.vt_area_for_gradient', 'gr_vt', _apart('gr_vt', _vt_area_for_gradient))
scalar_slip('gr.vt_gradient_for_area', 'gr.vt_gradient_for_area', 'gr_vt',
            _apart('gr_vt', lambda i, pi: [F(i['v']) / F(i['t1'])] if i['ask'] == 'distance' else []))
scalar_slip('gr.vt_whole_rectangle', 'gr.vt_whole_rectangle', 'gr_vt',
            _apart('gr_vt', lambda i, pi: [F(i['v']) * (F(i['t1']) + F(i['t2']) + F(i['t3']))] if i['ask'] == 'distance' else []))
scalar_slip('gr.vt_middle_only', 'gr.vt_middle_only', 'gr_vt',
            _apart('gr_vt', lambda i, pi: [F(i['v']) * F(i['t2'])] if i['ask'] == 'distance' else []))


def _transform_truth(i):
    a, x, y = F(i['a']), F(i['x']), F(i['y'])
    return {'f(x) + {a}': (x, y + a), 'f(x) - {a}': (x, y - a), 'f(x + {a})': (x - a, y), 'f(x - {a})': (x + a, y),
            '-f(x)': (x, -y), 'f(-x)': (-x, y)}[i['kind']]


def _transform_shift_wrong_way(i):
    a, x, y = F(i['a']), F(i['x']), F(i['y'])
    return {'f(x + {a})': [(x + a, y)], 'f(x - {a})': [(x - a, y)]}.get(i['kind'], [])


def _transform_inside_outside(i):
    a, x, y = F(i['a']), F(i['x']), F(i['y'])
    return {'f(x) + {a}': [(x + a, y)], 'f(x) - {a}': [(x - a, y)]}.get(i['kind'], [])


pair('gr_transform_point', _transform_truth)
pair_slip('gr.shift_wrong_way', 'gr.shift_wrong_way', 'gr_transform_point', _transform_shift_wrong_way)
pair_slip('gr.shift_inside_outside', 'gr.shift_inside_outside', 'gr_transform_point', _transform_inside_outside)

part('gr_exponential', lambda i: [F(i['ys'][0]), F(i['ys'][1]) / F(i['ys'][0])])
# the y values are read from the drawing, not printed, so a slip that equals one of them may speak (echo)
slip('gr.exp_a_at_one', 'gr.exp_a_at_one', 'gr_exponential', lambda i: [[F(i['ys'][1]), None]], echo=True)
slip('gr.exp_b_not_divided', 'gr.exp_b_not_divided', 'gr_exponential',
     lambda i: [[None, F(i['ys'][1])]] if F(i['ys'][0]) != 1 else [], echo=True)
slip('gr.exp_b_difference', 'gr.exp_b_difference', 'gr_exponential',
     lambda i: [[None, F(i['ys'][1]) - F(i['ys'][0])]] if F(i['ys'][1]) - F(i['ys'][0]) > 0 else [], echo=True)


# ---- ratio and proportion -------------------------------------------------------------------------------------------
def _prop_power_truth(i, pi=None):
    p, x1, y1 = _n(i['p']), F(i['x1']), F(i['y1'])
    k = y1 / x1 ** p
    if i['given'] == 'x':
        return k * F(i['x2']) ** p
    ratio = F(i['y2']) / k
    r = round(float(ratio) ** (1 / p))
    return F(r) if F(r) ** p == ratio else F(0)


def _prop_power_linear(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    return [y1 * F(i['x2']) / x1] if i['given'] == 'x' else [x1 * F(i['y2']) / y1]


def _prop_power_square(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    return [y1 * (F(i['x2']) / x1) ** 2] if i['given'] == 'x' else []


scalar('prop_power', _prop_power_truth)
scalar_slip('ratio.cube_linear', 'ratio.cube_as_linear', 'prop_power', _apart('prop_power', _prop_power_linear))
scalar_slip('ratio.cube_square', 'ratio.cube_as_square', 'prop_power', _apart('prop_power', _prop_power_square))


def _prop_root_truth(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    k = y1 / F(math.isqrt(int(x1)))
    if i['given'] == 'x':
        return k * F(math.isqrt(int(F(i['x2']))))
    return (F(i['y2']) / k) ** 2


scalar('prop_root', _prop_root_truth)
scalar_slip('ratio.root_linear', 'ratio.root_as_linear', 'prop_root', _apart('prop_root', _prop_power_linear))


def _inverse_square_truth(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    k = y1 * x1 ** 2
    if i['given'] == 'x':
        return k / F(i['x2']) ** 2
    sq = k / F(i['y2'])
    return F(math.isqrt(int(sq)))


def _inverse_square_inverse(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    return [y1 * x1 / F(i['x2'])] if i['given'] == 'x' else [x1 * y1 / F(i['y2'])]


def _inverse_square_direct(i, pi=None):
    x1, y1 = F(i['x1']), F(i['y1'])
    return [y1 * (F(i['x2']) / x1) ** 2] if i['given'] == 'x' else []


scalar('prop_inverse_square', _inverse_square_truth)
scalar_slip('ratio.inverse_square_inverse', 'ratio.inverse_square_as_inverse', 'prop_inverse_square',
            _apart('prop_inverse_square', _inverse_square_inverse))
scalar_slip('ratio.inverse_square_direct', 'ratio.direct_for_inverse', 'prop_inverse_square',
            _apart('prop_inverse_square', _inverse_square_direct))


def _ratio_change_t(i):
    a, b, n, c, d = (F(i[k]) for k in ('a', 'b', 'n', 'c', 'd'))
    return n * d / (b * c - a * d)


scalar('ratio_change', lambda i, pi: (F(i['b']) if i['ask'] == 'blue' else F(i['a']) + F(i['b'])) * _ratio_change_t(i))
scalar_slip('ratio.added_as_part', 'ratio.added_as_part', 'ratio_change',
            _apart('ratio_change', lambda i, pi: [(F(i['b']) if i['ask'] == 'blue' else F(i['a']) + F(i['b'])) * F(i['n'])]))


def _limiting_both(i):
    per, a1, a2, h1, h2 = (F(i[k]) for k in ('per', 'a1', 'a2', 'have1', 'have2'))
    return h1 / a1 * per, h2 / a2 * per


scalar('ratio_limiting', lambda i, pi: min(_limiting_both(i)))
scalar_slip('ratio.limiting_larger', 'ratio.limiting_larger', 'ratio_limiting',
            _apart('ratio_limiting', lambda i, pi: [max(_limiting_both(i))]))


# ---- trigonometry ---------------------------------------------------------------------------------------------------
def _trig_read_solutions(i):
    f = math.sin if i['fn_word'] == 'sin' else math.cos
    k = F(i['k'])
    return [x for x in range(0, 361, 30) if abs(f(math.radians(x)) - float(k)) < 1e-9]


def _trig_read_truth(i, pi=None):
    lo, hi = F(i['lo']), F(i['hi'])
    inside = [x for x in _trig_read_solutions(i) if lo <= x <= hi]
    return F(inside[0]) if len(inside) == 1 else F(-1)


scalar('trig_graph_read', _trig_read_truth)
scalar_slip('trig.graph_other_solution', 'trig.graph_other_solution', 'trig_graph_read',
            _apart('trig_graph_read', lambda i, pi: [x for x in _trig_read_solutions(i) if not F(i['lo']) <= x <= F(i['hi'])]))


def _trig_solve_pair(i):
    k = float(F(i['k']))
    fn = i['fn_word']
    if fn == 'sin':
        x1 = math.degrees(math.asin(k))
        return x1, 180 - x1
    if fn == 'cos':
        x1 = math.degrees(math.acos(k))
        return x1, 360 - x1
    x1 = math.degrees(math.atan(k))
    return x1, x1 + 180


def _trig_solve_truth(i):
    x1, x2 = _trig_solve_pair(i)
    return [Fraction(x1).limit_denominator(10 ** 6), Fraction(x2).limit_denominator(10 ** 6)]


def _trig_solve_wrong_rule(i):
    x1, _ = _trig_solve_pair(i)
    fn = i['fn_word']
    others = {'sin': [360 - x1, x1 + 180], 'cos': [180 - x1, x1 + 180], 'tan': [180 - x1, 360 - x1]}[fn]
    return [[None, Fraction(v).limit_denominator(10 ** 6)] for v in others if 0 <= v <= 360]


part('trig_solve_k', _trig_solve_truth, decimal=(0, 1))
slip('trig.second_solution_rule', 'trig.second_solution_rule', 'trig_solve_k', _trig_solve_wrong_rule)


# ---- Pythagoras -----------------------------------------------------------------------------------------------------
scalar('pyth_rhombus', lambda i, pi: sqrtq((F(i['d1']) / 2) ** 2 + (F(i['d2']) / 2) ** 2))
scalar_slip('pyth.diagonals_not_halved', 'pyth.diagonals_not_halved', 'pyth_rhombus',
            _apart('pyth_rhombus', lambda i, pi: [v for v in [sqrtq(F(i['d1']) ** 2 + F(i['d2']) ** 2)] if v is not None]))

scalar('pyth_square_area_diag', lambda i, pi: F(i['d']) ** 2 / 2)
scalar_slip('pyth.diagonal_squared_not_halved', 'pyth.diagonal_squared_not_halved', 'pyth_square_area_diag',
            _apart('pyth_square_area_diag', lambda i, pi: [F(i['d']) ** 2]))
scalar_slip('pyth.half_diagonal_as_side', 'pyth.half_diagonal_as_side', 'pyth_square_area_diag',
            _apart('pyth_square_area_diag', lambda i, pi: [(F(i['d']) / 2) ** 2]))


def _pyth_algebraic_truth(i, pi=None):
    a, b = F(i['a']), F(i['b'])
    # x^2 + (x + a)^2 = (x + b)^2  ->  x^2 + 2(a - b)x + (a^2 - b^2) = 0
    disc = (a - b) ** 2 - (a ** 2 - b ** 2)
    root = sqrtq(disc)
    return (b - a) + root if root is not None else F(0)


scalar('pyth_algebraic', _pyth_algebraic_truth)
scalar_slip('pyth.algebraic_sides_added', 'pyth.sides_not_squares', 'pyth_algebraic',
            _apart('pyth_algebraic', lambda i, pi: [F(i['b']) - F(i['a'])]))


# =============================================================================================
# Phase 3 batch C2 (docs/GCSE_MATHS_VARIETY.md section 23): the harder kinds that replaced the last tier echoes.
# Same contract as the batches above.
# =============================================================================================

def _exact_root(x):
    """The square root of a non-negative Fraction when it is exact, else None (sqrtq gives 60 digits instead)."""
    x = F(x)
    if x < 0:
        return None
    a, b = math.isqrt(x.numerator), math.isqrt(x.denominator)
    return Fraction(a, b) if a * a == x.numerator and b * b == x.denominator else None


def _counters_truth(i, pi=None):
    r, p = F(i['r']), Fraction(int(i['p_num']), int(i['p_den']))
    big = r * (r - 1) / p
    root = _exact_root(1 + 4 * big)
    return (1 + root) / 2 - r if root is not None else F(0)


def _counters_with_replacement(i, pi=None):
    r, p = F(i['r']), Fraction(int(i['p_num']), int(i['p_den']))
    root = _exact_root(r * r / p)
    return [root - r] if root is not None else []


scalar('prob_counters_algebraic', _counters_truth)
scalar_slip('prob.counters_with_replacement', 'prob.counters_with_replacement', 'prob_counters_algebraic',
            _apart('prob_counters_algebraic', _counters_with_replacement))
scalar_slip('prob.counters_total_typed', 'prob.counters_total_typed', 'prob_counters_algebraic',
            _apart('prob_counters_algebraic', lambda i, pi: [_counters_truth(i) + F(i['r'])]))


def _union_truth(i, pi=None):
    pa, pb = F(i['pa']), F(i['pb'])
    return pa + pb - pa * pb if i['ask'] == 'union' else pa + pb - 2 * pa * pb


scalar('prob_independent_union', _union_truth)
scalar_slip('prob.union_added', 'prob.union_added', 'prob_independent_union',
            _apart('prob_independent_union', lambda i, pi: [F(i['pa']) + F(i['pb'])] if i['ask'] == 'union' else []))
scalar_slip('prob.union_product_only', 'prob.union_product_only', 'prob_independent_union',
            _apart('prob_independent_union', lambda i, pi: [F(i['pa']) * F(i['pb'])]))
scalar_slip('prob.exactly_one_union', 'prob.exactly_one_union', 'prob_independent_union',
            _apart('prob_independent_union', lambda i, pi: [F(i['pa']) + F(i['pb']) - F(i['pa']) * F(i['pb'])] if i['ask'] == 'exactly_one' else []))


def _three_same_truth(i, pi=None):
    r, b = int(i['r']), int(i['b'])
    n = r + b
    return Fraction(r * (r - 1) * (r - 2) + b * (b - 1) * (b - 2), n * (n - 1) * (n - 2))


scalar('prob_three_same', _three_same_truth)
scalar_slip('prob.three_with_replacement', 'prob.three_with_replacement', 'prob_three_same',
            _apart('prob_three_same', lambda i, pi: [Fraction(int(i['r']) ** 3 + int(i['b']) ** 3, (int(i['r']) + int(i['b'])) ** 3)]))
scalar_slip('prob.three_one_colour', 'prob.three_one_colour', 'prob_three_same',
            _apart('prob_three_same', lambda i, pi: [Fraction(c * (c - 1) * (c - 2), (int(i['r']) + int(i['b'])) * (int(i['r']) + int(i['b']) - 1) * (int(i['r']) + int(i['b']) - 2))
                                                     for c in (int(i['r']), int(i['b']))]))


def _two_day_truth(i, pi=None):
    p1, pg, pn = F(i['p1']), F(i['p_given']), F(i['p_not_given'])
    if i['ask'] == 'exactly_one':
        return p1 * (1 - pg) + (1 - p1) * pn
    return 1 - (1 - p1) * (1 - pn)


def _two_day_independent(i, pi=None):
    p1 = F(i['p1'])
    if i['ask'] == 'exactly_one':
        return [2 * p1 * (1 - p1)]
    return [1 - (1 - p1) * (1 - p1)]


scalar('prob_two_day', _two_day_truth)
scalar_slip('prob.two_day_independent', 'prob.two_day_independent', 'prob_two_day', _apart('prob_two_day', _two_day_independent))
scalar_slip('prob.two_day_both_only', 'prob.two_day_both_only', 'prob_two_day',
            _apart('prob_two_day', lambda i, pi: [F(i['p1']) * F(i['p_given'])] if i['ask'] == 'at_least_one' else []))
scalar_slip('prob.two_day_one_branch', 'prob.two_day_one_branch', 'prob_two_day',
            _apart('prob_two_day', lambda i, pi: [F(i['p1']) * (1 - F(i['p_given'])), (1 - F(i['p1'])) * F(i['p_not_given'])]
                   if i['ask'] == 'exactly_one' else []))


def _trials_truth(i, pi=None):
    p, target = Fraction(str(i['p'])), F(i['target'])
    n = 1
    while 1 - (1 - p) ** n <= target and n < 500:
        n += 1
    return F(n)


scalar('prob_trials_needed', _trials_truth)
def _trials_added(i, pi=None):
    p, target = Fraction(str(i['p'])), F(i['target'])
    return [F(math.floor(target / p) + 1)]          # the first n with n x p above the target


scalar_slip('prob.trials_added', 'prob.trials_added', 'prob_trials_needed', _apart('prob_trials_needed', _trials_added))


def _which_bag_truth(i, pi=None):
    ja, jb = F(i['r1']) / F(i['n1']) / 2, F(i['r2']) / F(i['n2']) / 2
    return ja / (ja + jb)


scalar('prob_which_bag', _which_bag_truth)
scalar_slip('prob.which_bag_joint', 'prob.which_bag_joint', 'prob_which_bag',
            _apart('prob_which_bag', lambda i, pi: [F(i['r1']) / F(i['n1']) / 2]))
scalar_slip('prob.which_bag_counts', 'prob.which_bag_counts', 'prob_which_bag',
            _apart('prob_which_bag', lambda i, pi: [F(i['r1']) / (F(i['r1']) + F(i['r2']))]))


def _ages_t(i):
    a, b, n, c, d = (F(i[k]) for k in ('a', 'b', 'n', 'c', 'd'))
    den = b * c - a * d
    return n * (d - c) / den if den else F(0)


scalar('ratio_ages', lambda i, pi: (F(i['a']) if i['ask'] == 'younger' else F(i['b'])) * _ages_t(i))
scalar_slip('ratio.ages_other_person', 'ratio.ages_other_person', 'ratio_ages',
            _apart('ratio_ages', lambda i, pi: [(F(i['b']) if i['ask'] == 'younger' else F(i['a'])) * _ages_t(i)]))
scalar_slip('ratio.ages_future', 'ratio.ages_future', 'ratio_ages',
            _apart('ratio_ages', lambda i, pi: [(F(i['a']) if i['ask'] == 'younger' else F(i['b'])) * _ages_t(i) + F(i['n'])]))


def _groups(i):
    return Fraction(str(i['f1'])), Fraction(str(i['s1'])), Fraction(str(i['s2']))


scalar('ratio_fraction_groups', lambda i, pi: (lambda f1, s1, s2: f1 * s1 + (1 - f1) * s2)(*_groups(i)))
scalar_slip('ratio.groups_fractions_added', 'ratio.groups_fractions_added', 'ratio_fraction_groups',
            _apart('ratio_fraction_groups', lambda i, pi: [(lambda f1, s1, s2: s1 + s2)(*_groups(i))]))
scalar_slip('ratio.groups_one_part', 'ratio.groups_one_part', 'ratio_fraction_groups',
            _apart('ratio_fraction_groups', lambda i, pi: [(lambda f1, s1, s2: f1 * s1)(*_groups(i)), (lambda f1, s1, s2: (1 - f1) * s2)(*_groups(i))]))
scalar_slip('ratio.groups_rest_not_taken', 'ratio.groups_rest_not_taken', 'ratio_fraction_groups',
            _apart('ratio_fraction_groups', lambda i, pi: [(lambda f1, s1, s2: f1 * s1 + f1 * s2)(*_groups(i))]))


def _percent_more_truth(i, pi=None):
    total, p = F(i['total']), F(i['p'])
    less = total / (2 + p / 100)
    return less * (1 + p / 100) if i['ask'] == 'more' else less


scalar('ratio_percent_more', _percent_more_truth)
scalar_slip('ratio.percent_more_half', 'ratio.percent_more_half', 'ratio_percent_more',
            _apart('ratio_percent_more', lambda i, pi: [F(i['total']) / 2 * (1 + F(i['p']) / 100) if i['ask'] == 'more' else F(i['total']) / 2 * (1 - F(i['p']) / 100)]))
scalar_slip('ratio.percent_more_other', 'ratio.percent_more_other', 'ratio_percent_more',
            _apart('ratio_percent_more', lambda i, pi: [F(i['total']) - _percent_more_truth(i)]))


def _three_part(i):
    a, b1, b2, c = (int(i[k]) for k in ('a', 'b1', 'b2', 'c'))
    lcm = b1 * b2 // math.gcd(b1, b2)
    return a * lcm // b1, lcm, c * lcm // b2


def _three_part_truth(i, pi=None):
    pa, pb, pc = _three_part(i)
    part = F(i['gap']) / abs(pc - pa)
    return pb * part if i['ask'] == 'B' else (pa + pb + pc) * part


def _three_part_not_matched(i, pi=None):
    a, b1, b2, c, gap = (F(i[k]) for k in ('a', 'b1', 'b2', 'c', 'gap'))
    if b1 == b2 or a == c:
        return []
    part = gap / abs(c - a)
    return [b1 * part, b2 * part] if i['ask'] == 'B' else [(a + b1 + c) * part, (a + b2 + c) * part]


scalar('ratio_three_part_difference', _three_part_truth)
scalar_slip('ratio.three_part_not_matched', 'ratio.middle_not_matched', 'ratio_three_part_difference',
            _apart('ratio_three_part_difference', _three_part_not_matched))
scalar_slip('ratio.gap_as_part', 'ratio.gap_as_part', 'ratio_three_part_difference',
            _apart('ratio_three_part_difference', lambda i, pi: [(_three_part(i)[1] if i['ask'] == 'B' else sum(_three_part(i))) * F(i['gap'])]))


def _algebraic_parts_truth(i, pi=None):
    p, q, r, s, a, b = (F(i[k]) for k in ('p', 'q', 'r', 's', 'a', 'b'))
    den = b * p - a * r
    return (a * s - b * q) / den if den else F(0)


def _cross_swapped(i, pi=None):
    p, q, r, s, a, b = (F(i[k]) for k in ('p', 'q', 'r', 's', 'a', 'b'))
    den = a * p - b * r
    return [(b * s - a * q) / den] if den else []


scalar('ratio_algebraic_parts', _algebraic_parts_truth)
scalar_slip('ratio.cross_multiply_swapped', 'ratio.cross_multiply_swapped', 'ratio_algebraic_parts',
            _apart('ratio_algebraic_parts', _cross_swapped))


pair('gr_x_intercept', lambda i: (-F(i['c']) / F(i['m']), 0))
pair_slip('gr.x_intercept_y_intercept', 'gr.x_intercept_y_intercept', 'gr_x_intercept', lambda i: [(0, F(i['c']))])


def _missing_truth(i, pi=None):
    m, c, g = F(i['m']), F(i['c']), F(i['given'])
    return m * g + c if i['ask'] == 'y' else (g - c) / m


def _whole(values):
    """Only the whole-number slips: the key of this family is always whole, and a slip that lands on a fraction would be
    rounded to the pupil's places by the engine (26/3 read as a typed 9 called the key plus one "sign moved", C2 review)."""
    return [v for v in values if F(v).denominator == 1]


def _missing_wrong_letter(i, pi=None):
    m, c, g = F(i['m']), F(i['c']), F(i['given'])
    return _whole([(g - c) / m] if i['ask'] == 'y' else [m * g + c])


scalar('gr_missing_coordinate', _missing_truth)
scalar_slip('gr.coordinate_wrong_letter', 'gr.coordinate_wrong_letter', 'gr_missing_coordinate',
            _apart('gr_missing_coordinate', _missing_wrong_letter))
scalar_slip('gr.coordinate_sign_moved', 'alg.sign_moved', 'gr_missing_coordinate',
            _apart('gr_missing_coordinate', lambda i, pi: _whole([(F(i['given']) + F(i['c'])) / F(i['m'])]) if i['ask'] == 'x' else []))


scalar('gr_gradient_graph', lambda i, pi: (F(i['y2']) - F(i['y1'])) / (F(i['x2']) - F(i['x1'])))
scalar_slip('gr.gradient_rise_only', 'gr.gradient_rise_only', 'gr_gradient_graph',
            _apart('gr_gradient_graph', lambda i, pi: [F(i['y2']) - F(i['y1'])]), echo=True)


scalar('gr_conversion', lambda i, pi: F(i['y']) if i['ask'] == 'to' else F(i['x']))
scalar_slip('gr.conversion_wrong_way', 'gr.conversion_wrong_way', 'gr_conversion',
            _apart('gr_conversion', lambda i, pi: [F(i['x']) * F(i['x']) / F(i['y'])] if i['ask'] == 'to' else [F(i['y']) * F(i['y']) / F(i['x'])]))


def _fd_truth(i, pi=None):
    width = F(i['hi']) - F(i['lo'])
    return F(i['freq']) / width if i['ask'] == 'density' else Fraction(str(i['fd'])) * width


scalar('stats_frequency_density', _fd_truth)
# (stats.fd_frequency_typed went when the density draw left gcse_stats_frequency_density: review C5)
scalar_slip('stats.fd_width_typed', 'stats.fd_width_typed', 'stats_frequency_density',
            _apart('stats_frequency_density', lambda i, pi: [F(i['hi']) - F(i['lo'])]))
scalar_slip('stats.fd_divided', 'stats.fd_divided', 'stats_frequency_density',
            _apart('stats_frequency_density', lambda i, pi: [Fraction(str(i['fd'])) / (F(i['hi']) - F(i['lo']))] if i['ask'] == 'frequency' else []))


# =============================================================================================
# Installation
# =============================================================================================

_make_dual()


def install(cd):
    """Add everything above to the tables of ``misconception_cd`` (``cd`` is that module's ``globals()``; it is called
    once, before the module builds its derived tables)."""
    cd['TRUTH'].update(TRUTH)
    cd['PART_TRUTH'].update(PART_TRUTH)
    cd['PART_TOKENS'].update(PART_TOKENS)
    cd['PAIR_TRUTH'].update(PAIR_TRUTH)
    cd['PAIR_RULES'] = cd['PAIR_RULES'] + tuple(PAIR_RULES)
    cd['PART_RULES'] = cd['PART_RULES'] + tuple(PART_RULES)
    cd['RULES'] = cd['RULES'] + tuple(RULES)
    cd['ECHO_OK'] = cd['ECHO_OK'] | frozenset(ECHO_OK)
    cd['DECIMAL_TOKENS'] = cd['DECIMAL_TOKENS'] | DECIMAL_TOKENS
    cd['TEXT_GUARDS'] = dict(cd.get('TEXT_GUARDS') or {}, **TEXT_GUARDS)
    cd['PART_OTHER_BOX_QUIET'] = frozenset(r.id for r in PART_RULES) - PART_OTHER_BOX_OK
