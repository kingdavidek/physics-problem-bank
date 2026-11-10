"""Misconception diagnosis for GCSE maths typed answers (docs/GCSE_MATHS_HINTS.md, Phase 1).

After a wrong typed answer the pupil gets one short line that names the likely slip ("Check the sign.")
instead of a bare "Not quite". Phase 1 uses key-only rules: they work from the stored answer and the
question text alone, so they need no generator change and no recorded inputs.

How a diagnosis is made (``diagnose``):

* only for a GCSE maths problem bound to the session, only after the checker called the answer wrong, and
  never for an answer the checker could not read or one that has its own message (a wrong written form, a
  wrong letter, a recurring decimal);
* the pupil's value is read with the checker's own parsers, so diagnosis sees exactly what the grader saw;
* every rule gives exact candidate values computed from the key (never from a generator helper, so a
  generator bug cannot hide inside a rule); a candidate the checker would accept is dropped;
* a candidate matches when the pupil's value equals it, or equals it rounded half up to the accuracy the
  question states (a pupil who made the slip still rounds as told);
* a message is returned only when exactly one distinct message matches. Rules may share a message; two
  different messages on the same value mean no diagnosis.

Phase 2 adds topic rules (``misconception_topics.py``). They read the question's own numbers from
``problem['answer_record']`` (see ``answer_record.py``), rebuild the correct answer from them as a guard, and then
compute the exact value each slip gives. A typed value that matches a topic rule wins over a generic rule that
names the same value (the topic rule knows the question; the generic rule only guesses from the key). Two
different topic messages on one value still mean silence, and silence is the fallback everywhere.

Privacy and safeguarding: nothing here is stored. The module has no database, session, log or random
access, adds nothing to a problem, and returns the text for the one response that follows the one wrong
answer. Candidate values are computed at check time and thrown away. Per decision D5 a message names the
slip and the step to fix, never the corrected value or the factor to apply to the pupil's number.

Copy rules (docs/GCSE_MATHS_HINTS.md section 6) are enforced on ``MESSAGES`` by ``models/zorp_voice.py``
(the ``system_hint`` surface), which reads the dictionary below with ``ast``: keep every message a plain
string literal.
"""
from __future__ import annotations

import ast
import difflib
import html as _html
import json as _json
import re
from dataclasses import dataclass, replace as _dc_replace
from fractions import Fraction
from typing import Callable, Optional

from generators.shared import answer_checkers as _ac
from generators.shared import answer_units as _units
from generators.shared import misconception_topics as _topics

# ---------------------------------------------------------------------------------------------
# Copy: the only place the messages live. System voice (no "I", no Zorp), at most two short
# sentences, at most 120 characters, no value and no factor (D5).
# ---------------------------------------------------------------------------------------------

MESSAGES = {
    'gen.sign': 'Check the sign. Look again at each step where a number could change from positive to negative.',
    'gen.pow10': 'Check the place value. Count how far the decimal point should move.',
    'gen.accuracy': 'Nearly there. Round to the accuracy the question asks for.',
    'gen.truncated': 'Nearly there. Look at the next digit to decide whether to round up or down.',
    'gen.early_round': 'Very close. Keep every digit until the last step, then round as the question asks.',
    'gen.reciprocal': 'Check the division. It looks like the numbers were divided the other way round.',
    'gen.reciprocal_fraction': 'Check the fraction. It looks like the top and bottom have been swapped.',
    'gen.pair_swapped': 'Those two values look swapped round. Check which one comes first.',
    'gen.one_root': 'That is one solution. This equation has two, so find the other one too.',
    'gen.as_percentage': 'That looks like a decimal. The question asks for a percentage, so change it into one.',
    'gen.as_decimal': 'That looks like a percentage. The question asks for a decimal, so change it into one.',
    'ang.supplement': 'Check which angle fact applies. Some pairs of angles are equal, and others add up to 180°.',
    'ang.complement': 'Check which total applies. A right angle is 90°, a straight line is 180° and a full turn is 360°.',
    'brg.three_figures': 'Correct! Bearings are written with three figures, so 5° is written 005°.',
    # Topic messages (Phase 2): they name a slip that the recorded inputs of the question confirm is computable.
    # No value and no factor appears in any of them (D5).
    'mens.circumference_formula': 'That looks like the circumference. For an area, the radius is squared, not doubled.',
    'mens.area_formula': 'That looks like the area formula. The question asks for the circumference.',
    'mens.not_squared': 'Check the power. It looks like the radius was not squared.',
    'mens.not_cubed': 'Check the power. It looks like the radius was not cubed.',
    'mens.radius_not_diameter': 'It looks like the radius was used where the diameter belongs. Check which one the formula needs.',
    'mens.diameter_as_radius': 'It looks like the diameter was used as the radius. Check which one the formula needs.',
    'mens.whole_circle': 'That is the whole circle. The question asks for only part of it.',
    'mens.arc_formula': 'That looks like the arc length formula. The question asks for an area.',
    'mens.sector_formula': 'That looks like the sector area formula. The question asks for a length.',
    'mens.perimeter_arc_only': 'That is the curved edge only. The perimeter of a sector also has two straight edges.',
    'mens.curved_only': 'That is the curved surface only. The total surface area also includes the flat ends.',
    'mens.volume_for_area': 'That looks like a volume. The question asks for a surface area.',
    'mens.area_for_volume': 'That looks like a surface area. The question asks for a volume.',
    'mens.no_third': 'That looks like the volume of the matching prism or cylinder. Check the formula for a cone or pyramid.',
    'mens.slant_for_height': 'Check the height. This volume needs the perpendicular height, not the slant height.',
    'mens.height_for_slant': 'Check the slant height. This area needs the slant height, not the perpendicular height.',
    'mens.full_rectangle': 'That looks like the answer for a full rectangle. A triangle or trapezium covers only part of one.',
    'mens.faces_missed': 'A cuboid has six faces in three matching pairs. Check that every face is counted.',
    'mens.cutout_added': 'Check the cut-out. It should be taken away from the large rectangle, not added.',
    'mens.area_for_perimeter': 'That looks like the area. The question asks for the perimeter.',
    'mens.half_perimeter': 'Check the perimeter. A rectangle has two lengths and two widths.',
    'mens.annulus_order': 'Check the order. Square each radius first, then subtract.',
    'mens.hole_ignored': 'That is the whole outer circle. The hole in the middle needs removing.',
    'mens.diameter_found': 'That looks like the diameter. The question asks for the radius.',
    'mens.radius_found': 'That looks like the radius. The question asks for the diameter.',
    'mens.area_units': 'Check the units. An area in square units changes by the conversion factor squared.',
    'mens.volume_units': 'Check the units. The rate is in litres, but the volume is in cubic centimetres.',
    'gen.squared': 'That looks like the length squared. Take the square root to finish.',
    'unit.not_converted': 'That is still in the original units. The question asks for a different unit.',
    'sim.wrong_power': 'Check the scale factor. Areas and volumes need the right power of it.',
    'pyth.sides_not_squares': 'That looks like the side lengths added or subtracted directly. Pythagoras uses their squares.',
    'pyth.subtracted_for_hyp': 'To find the hypotenuse, add the squares. Subtracting finds a shorter side.',
    'pyth.added_for_short': 'To find a shorter side, subtract the squares. Adding finds the hypotenuse.',
    'pyth.base_not_halved': 'Check the base. The height splits it in two, so the triangle uses half of it.',
    'pyth.one_step_short': 'That is the diagonal of one face. The space diagonal needs one more step.',
    'pyth.perimeter_sides': 'Check the perimeter. It needs all three sides, and one is the hypotenuse.',
    'pyth.original_position': 'That is the height before the ladder slid. Use the new distance from the wall.',
    'trig.wrong_ratio': 'Check which ratio fits. Label the sides from the angle first.',
    'trig.rearranged': 'Check how the formula is rearranged. Decide whether the unknown side is on the top or the bottom.',
    'trig.radians': 'Check that your calculator is in degrees, not radians.',
    'trig.ratio_not_inverted': 'That is the ratio of the sides. Use the inverse button to turn it into an angle.',
    'trig.other_angle': 'That is the other acute angle. Label the sides from the angle you want, then pick the ratio.',
    'trig.area_sine': 'Check the formula. The area of a triangle uses the sine of the angle between the two sides.',
    'trig.area_parallelogram': 'That looks like the area of a parallelogram. A triangle covers only part of it.',
    'trig.half_angle': 'That is half of the apex angle. The apex angle is the whole angle between the equal sides.',
    'trig.cosine_sign': 'Check the signs in the cosine rule. Look at which terms are added and which are subtracted.',
    'trig.sine_rule_inverted': 'Check the sine rule. Each side goes with the angle opposite it.',
    'pct.change_not_applied': 'That is the size of the change. Now apply it to the original amount.',
    'pct.opposite': 'Check the direction of the change. The percentage looks like it was applied the opposite way.',
    'pct.reverse_as_forward': 'This takes the percentage of the new amount. Divide by the multiplier instead.',
    'pct.wrong_base': 'Check which amount to divide by. A percentage change is a fraction of the original amount.',
    'pct.change_not_compared': 'That is the change in value. A percentage compares the change with the original amount.',
    'pct.error_wrong_base': 'Check which amount to divide by. Percentage error compares the error with the actual value.',
    'pct.error_not_compared': 'That is the size of the error. A percentage error compares it with the actual value.',
    'pct.changes_added': 'Check the two changes. The second percentage applies to the new amount, not the original.',
    'pct.same_each_year': 'It looks like the change came from the original amount every year. Each year uses the new amount.',
    'pct.years_missed': 'Check the number of years. The multiplier applies once for each year.',
    'pct.of_divided': 'Check the method. A percentage of an amount is a fraction out of a hundred of it.',
    'fdp.other_part': 'That answers a different part of the question. Read again what the question asks for.',
    'fdp.fraction_inverted': 'Check the fraction. It looks like the top and bottom were used the opposite way round.',
    'fdp.bottom_only': 'It looks like only the bottom of the fraction was used. The top says how many parts to take.',
    'fdp.place_value_fraction': 'Check the place value. The bottom of the fraction comes from the last decimal place.',
    'fdp.per_cent': 'Check the bottom of the fraction. Per cent means out of a hundred.',
    'dec.mean_total': 'That is the total. A mean divides the total by how many values there are.',
    'dec.estimate_exact': 'That is the exact calculation. An estimate rounds each number first.',
    'dec.estimate_order': 'Check the order. Round each number first, then calculate.',
    'num.double_negative': 'Check the signs. Look again at what happens when a negative number is added or subtracted.',
    'idx.multiplied': 'Check the power. It looks like the number was multiplied by the power instead of by itself.',
    'idx.negative_power': 'Check the negative power. It does not make the number negative.',
    'idx.power_sign_ignored': 'Check the sign of the power. A negative power is not the same as a positive one.',
    'idx.zero_power': 'Check the power of zero. It has its own rule that does not depend on the number.',
    'idx.fraction_power': 'Check the fractional power. The bottom of the fraction tells you which root to take.',
    'bidmas.left_to_right': 'Check the order. Multiply and divide before you add and subtract.',
    'bidmas.brackets_ignored': 'Check the brackets. Work out what is inside them first.',
    'bidmas.negative_square': 'Check what the power applies to. Brackets decide whether the negative sign is included.',
    'op.multiply_needed': 'Check the calculation. This one needs the numbers multiplied.',
    'op.divide_needed': 'Check the calculation. This one needs a division.',
    'ratio.scale_direction': 'Check the scale. A real distance is bigger than its distance on the map.',
    'ratio.inverse_for_direct': 'Check the type of proportion. Here, both quantities increase together.',
    'ratio.direct_for_inverse': 'Check the type of proportion. Here, when one quantity goes up, the other goes down.',
    'ratio.additive': 'Check the method. Proportion works by multiplying, not by adding the same amount.',
    'ratio.unit_only': 'That is the amount for one. Now scale it up to the number asked for.',
    'ratio.parts_swapped': 'Check which ratio part goes with which quantity.',
    'ratio.part_to_part': 'Check the total. A fraction compares one part with the whole, not with the other parts.',
    'cm.minutes_decimal': 'Check the time. Minutes are not hundredths of an hour, so they need converting.',
    'cm.minutes_not_converted': 'Check the units of time. The speed is per hour, but the time is in minutes.',
    'cm.speed_direction': 'Check which way the conversion goes. Think about whether the number should get bigger or smaller.',
    'cm.speed_one_unit': 'It looks like only one unit was converted. Both the distance and the time units need changing.',
    'cm.mean_of_densities': 'Check the method. The density of a mixture is its total mass divided by its total volume.',
    'cm.mean_of_speeds': 'Check the average speed. It is total distance over total time, not the mean of the speeds.',
    'cm.weight_force': 'Pressure uses force, not mass. Turn the mass into a force first.',
    'cm.rates_combined': 'Check the combined rate. The drain takes water out while the other pipe fills the tank.',
    'cm.relative_speed': 'Check the relative speed. Whether speeds add or subtract depends on the directions.',
    # Phase 5, wave C: probability, statistics, angles, bearings (docs/GCSE_MATHS_HINTS.md section 21)
    'prob.boundary': 'Check the boundary. Decide whether the number named in the question counts or not.',
    'prob.one_not_prime': 'Check which numbers count. One is not a prime number, because it has only one factor.',
    'prob.other_colour': 'That is the probability of the other colour. Check which colour the question asks about.',
    'prob.not_complemented': 'That is the probability of the event itself. The question asks for the chance that it does not happen.',
    'prob.expected_not_scaled': 'That is the probability of one trial. Multiply it by the number of trials to find how many to expect.',
    'prob.other_outcome': 'That is the relative frequency of the other outcome. Check which outcome the question asks about.',
    'prob.multiplied_for_or': 'Check the sign between the chances. Separate outcomes joined by or are added.',
    'prob.one_outcome': 'That counts only one of the outcomes. Both outcomes in the question count.',
    'prob.single_outcome': 'That counts only one of the ways. Check how many different outcomes give the result asked for.',
    'prob.put_back_missed': 'Check the second draw. The item is put back, so the bag is full again.',
    'prob.removed_missed': 'Check the second draw. Nothing is put back, so the number left has changed.',
    'prob.first_draw_only': 'That is the first draw only. The question needs the probability of both draws.',
    'prob.added_for_and': 'It looks like these were added. When both events must happen, multiply.',
    'prob.one_order': 'That is only one order. There is another way to get the result asked for.',
    'prob.complement_missed': 'That is the chance of the opposite outcome, and the question asks about the outcome itself.',
    'prob.one_attempt': 'That is the chance for one attempt only. The question covers all of the attempts.',
    'prob.all_succeed': 'That is the chance that every attempt succeeds. At least one success is a wider event.',
    'prob.joint_not_conditional': 'That is the chance of both events. Divide by the chance of the event already known.',
    'prob.overlap_missed': 'That leaves out the overlap. All of a circle counts, including the part shared with the other.',
    'prob.total_wrong': 'Check the total. The bottom of the fraction is everyone in the whole group or diagram.',
    'prob.neither_missed': 'Check the region. Not A includes the part outside both circles as well as the B only part.',
    'prob.overlap_counted_twice': 'The overlap has been counted twice. Take the part in both groups away once.',
    'prob.overlap_removed_twice': 'The overlap has been taken away twice. It only needs removing once.',
    'stats.median_unsorted': 'Check the order. Put the values in order from smallest to largest before finding the middle.',
    'stats.median_mean': 'That is the mean. The median is the middle value when the numbers are in order.',
    'stats.range_largest': 'That is the largest value. The range needs the smallest value taken away from it.',
    'stats.range_unsorted': 'Check the values subtracted. The range uses the largest and smallest values, not the first and last.',
    'stats.mean_divisor': 'Check what the total is divided by. It should be how many values there are.',
    'stats.mean_median': 'That is the middle value. The mean is the total divided by how many values there are.',
    'stats.mode_count': 'That is how many times it appears. The mode is the value itself.',
    'stats.midpoint_width': 'That is the width of the class. The midpoint is halfway between the two ends.',
    'stats.midpoint_not_halved': 'That is the two ends added together, and a midpoint is the value halfway between them.',
    'stats.freq_ignored': 'Check the weighting. Each value counts as many times as its frequency says.',
    'stats.mean_divisor_rows': 'Check what the total is divided by. It should be the total frequency, not the number of rows.',
    'stats.use_midpoint': 'Check the values used for each class. An estimate of the mean uses the midpoint of each class.',
    'stats.pie_percentage': 'That is the percentage. A sector angle is that share of 360°.',
    'stats.pie_one_item': 'That is the angle for one item. Multiply it by how many are in the group.',
    'stats.pie_other_sector': 'That is the angle of the other sector. Check which group the question asks about.',
    'stats.iqr_range': 'That is the range. Use the upper and lower quartiles instead of the smallest and largest values.',
    'stats.iqr_upper_quartile': 'That is the upper quartile only. Take the lower quartile away from it.',
    'stats.fd_multiplied': 'Check the calculation. Divide the frequency by the width of the class.',
    'ang.sum_not_subtracted': 'That is the total of the angles given. Take it away from the full total to find the missing one.',
    'ang.wrong_total': 'Check which total fits. A right angle is 90°, a line or a triangle 180°, and a point or a four-sided shape 360°.',
    'ang.angle_missed': 'It looks like one of the given angles was left out. Take away every angle you are given.',
    'ang.parallel_equal': 'Check the angle pair. Alternate and corresponding angles are equal, rather than adding to 180°.',
    'ang.cointerior_total': 'Check the angle pair. Co-interior angles add up to 180°, rather than being equal.',
    'ang.interior_for_exterior': 'That is the angle inside the triangle. The question asks for the exterior angle.',
    'ang.polygon_n': 'Check the formula. The sum of the interior angles uses two fewer than the number of sides.',
    'ang.exterior_sum_confused': 'That is the sum of the exterior angles. The question asks for the interior angles.',
    'ang.one_interior': 'That is one interior angle of a regular polygon. The question asks for the sum.',
    'ang.interior_for_exterior_poly': 'That is the interior angle. The question asks for the exterior angle.',
    'ang.exterior_total': 'Check the total. The exterior angles of any polygon add up to 360°, not 180°.',
    'ang.interior_as_exterior': 'Check the angle. The interior and exterior angles are different, and they add up to 180°.',
    'ang.angle_for_sides': 'That is the size of an angle. The question asks for the number of sides.',
    'ang.isos_one_base': 'It looks like only one base angle was used. Both base angles are equal and both count.',
    'ang.isos_bases_added': 'That is the two base angles added. Take it away from the total to find the apex angle.',
    'ang.equilateral_total': 'That is the total of the three angles. Each one is a third of it.',
    'brg.reversed': 'That is the bearing in the opposite direction. Check which point the bearing is measured from.',
    'brg.anticlockwise': 'Check the direction. Bearings are measured clockwise from north.',
    'brg.same_direction': 'That is the bearing in the original direction. The bearing back is measured from the other point.',
    'brg.north_line': 'Check the angle used. Each bearing is measured clockwise from the north line at its own point.',
    'brg.angle_only': 'That is the angle from the north-south line. Turn it into a bearing measured clockwise from north.',
    'brg.quadrant': 'Check which quarter the direction is in. The angle is measured from north or south, towards east or west.',
    'brg.added': 'Check the calculation. The angle between two bearings is their difference, not their sum.',
    'brg.reflex': 'That is the reflex angle. The question asks for the angle between the two directions.',
    'brg.from_north': 'That is the angle from north. The question measures from the east-west line.',
    'brg.road_other_end': 'That is the angle to the other end of the road. Check which direction the question measures from.',
    'brg.east_north_swapped': 'Check which ratio goes with which direction. East uses the sine of the bearing and north uses the cosine.',
    'brg.path_length': 'That is the total length of the journey. The question asks for the straight-line distance.',
    'brg.quarter_missed': 'Check the quarter. The angle from the north-south line then needs turning into a bearing.',
    'brg.from_east_not_north': 'That angle is measured from the east-west line. A bearing is measured clockwise from north.',
    'alg.root_signs': 'Check the signs of the roots. A root has the opposite sign to the number in its bracket.',
    'sim.not_divided': 'Check the last step. Divide by the number in front of the letter you are finding.',
    'cts.half_not_squared': 'Check the last step. Halve the number in front of x, then square the result.',
    'cts.whole_squared': 'Check the first step. Halve the number in front of x before squaring.',
    'cts.not_halved': 'Check the first step. The number in the bracket is half of the number in front of x.',
    'alg.sign_moved': 'Check the sign of the term that moved. A term changes sign when it moves to the other side.',
    'alg.wrong_inverse': 'Check the last step. Multiply to undo divide, and divide to undo multiply.',
    'alg.one_term_divided': 'It looks like only one term was divided. When both sides are divided, every term is divided.',
    'alg.bracket_partial': 'Check the brackets. Every term inside a bracket is multiplied by the number outside.',
    'alg.root_missed': 'Check the last step. To undo a square, take the square root of both sides.',
    'alg.expand_cross_missed': 'Check every pair of terms. Each term in the first bracket multiplies each term in the second.',
    'seq.step_as_term': 'That is the step between terms. The question asks for a term in the sequence.',
    'seq.pattern_multiplied': 'Check the pattern. These terms change by multiplying, not by adding the same amount each time.',
    'seq.gaps_not_constant': 'Check the pattern. The gaps between the terms are not all the same size.',
    'seq.constant_forgotten': 'Check the rule. The term number is multiplied first, and then the other number is added or subtracted.',
    'seq.constant_sign': 'Check the sign of the constant. It is added or subtracted exactly as it appears in the rule.',
    'seq.position_off': 'Check the position. Put the number of the term in place of n, not the number before or after it.',
    'seq.constant_inverse': 'Check the inverse step. Undo an added number by subtracting it, and the other way round.',
    'seq.constant_first': 'Check the order. Deal with the added or subtracted number before dividing by the multiplier.',
    'seq.first_term_constant': 'It looks like the first term was used as the constant. Compare the rule with the first term to find it.',
    'seq.difference_constant': 'It looks like the step was used as the constant. Compare the rule with the first term to find it.',
    'seq.constant_sign_rule': 'Check the sign of the constant. Compare the rule with the first term to see what must be added or taken away.',
    'seq.add_not_multiply': 'Check the rule. The step multiplies n, because the terms go up by the same amount for each position.',
    'trans.coords_swapped': 'It looks like x and y were swapped. The x value is written first.',
    'trans.wrong_axis': 'Check which line the shape is reflected in. Count the distance to the mirror line to find each new point.',
    'trans.line_ignored': 'Check the mirror line. It is not an axis, so measure the distance from the line itself.',
    'trans.rotate_opposite': 'Check the turn direction. A clockwise turn and the opposite turn give different images.',
    'trans.centre_ignored': 'Check the centre. Distances are measured from the centre of the turn or enlargement, not always the origin.',
    'trans.enlarge_added': 'Check the enlargement. Each distance from the centre is multiplied by the scale factor, not added to.',
    'trans.enlarge_inverted': 'Check the scale factor. Above one the image is bigger, and below one it is smaller.',
    'trans.negative_ignored': 'Check the sign of the scale factor. A negative one puts the image on the other side of the centre.',
    'trans.translate_opposite': 'Check the direction of the translation. A positive number moves right or up.',
    'trans.vector_swapped': 'It looks like the two parts of the vector were swapped. The top number is the move right or left.',
    'vec.order_reversed': 'That vector points the opposite way. Check which point or vector comes first.',
    'vec.added_for_sub': 'It looks like the vectors were added. The question asks for a subtraction.',
    'vec.subtracted_for_add': 'It looks like the vectors were subtracted. The question asks for an addition.',
    'vec.scalar_added': 'Check the multiplication. A scalar multiplies each part of the vector, it is not added.',
    'vec.midpoint_not_halved': 'That is the two points added together, and a midpoint is the point halfway between them.',
    'vec.midpoint_difference': 'Check the midpoint. Add the matching values before halving, rather than subtracting.',
    'vec.not_divided': 'Check the last step. After taking the known vector away, divide by the number in front of x.',
    'brg.pythagoras_misused': 'Pythagoras only works with a right angle. This triangle needs the cosine rule.',
}

# Rung 1 when no slip is recognised (Phase 3, section 5): a method nudge for the topic (a record family may get its own
# line later). The problem's own hint is tried first because it is more specific; a topic line takes over when that hint
# would show the answer or is long. System voice, same lint as MESSAGES (the ``system_hint`` surface), no digits.
NUDGES = {
    'bidmas': 'Work through the brackets first, then powers, then multiply and divide, then add and subtract.',
    'multiples_factors': 'List the factors or multiples in order and check each one against the question.',
    'decimals': 'Line up the decimal points and check the place value of each digit.',
    'fdp': 'Decide whether to multiply or divide, then check that the size of your answer makes sense.',
    'number': 'Read the question again and write down each step before you use the calculator.',
    'ratio_proportion': 'Find what one part or one unit is worth first, then scale up to the amount asked for.',
    'algebra': 'Do the same thing to both sides, one step at a time, and keep track of the signs.',
    'equations_inequalities': 'Undo each step one at a time, doing the same to both sides. Then check your answer in the original.',
    'changing_the_subject': 'Say which letter you want on its own, then undo what is done to it, one step at a time.',
    'sequences': 'Look at the gap between neighbouring terms, then test your rule on the first two terms.',
    'surds': 'Look for the biggest square number that goes into the surd, then simplify.',
    'simultaneous_equations': 'Make the number in front of one letter match in both equations, then add or subtract to remove it.',
    'completing_the_square': 'Halve the number in front of x and put it in the bracket. Then take away its square.',
    'quadratic_simultaneous_equations': 'Use the straight-line equation to replace one letter, then solve and find the other letter each time.',
    'graphs': 'Pick points you can read exactly from the graph and use them in your working.',
    'graphical_simultaneous_equations': 'The solutions are where the two lines cross. Read off the x and y values at each crossing point.',
    'algebraic_fractions': 'Factorise the top and the bottom first, then cancel any common factors.',
    'functions': 'Work from the inside outwards: do the inner function first, then the outer one.',
    'algebraic_proof': 'Write each number in algebra, then simplify. Show that the result fits the pattern in the question.',
    'geometry_angles': 'Name the angle fact you are using, such as angles on a line, before you work anything out.',
    'pythagoras': 'Mark the longest side, the hypotenuse, first. Then decide whether to add or subtract the squares.',
    'trigonometry': 'Label the three sides from the angle. Then pick sine, cosine or tangent.',
    'mensuration': 'Write the formula first, then check which lengths it needs, such as the radius.',
    'bearings': 'Draw a north line at the starting point and measure clockwise from it.',
    'transformations': 'Pick one corner and follow it through, then do the rest of the shape.',
    'similarity_congruence': 'Match up the sides that fit together, then find the scale factor from a pair you know.',
    'circle_theorems': 'Name the circle theorem you are using and mark the angles it links.',
    'constructions_loci': 'Think about which points fit each rule, then see where the rules overlap.',
    'compound_measures': 'Check the units first. Then write the formula and put the values in.',
    'vectors': 'Work out a route from the start to the end using vectors you know, and take care with direction.',
    'statistics': 'Write down what the question asks for, such as the mean or the median, and put the data in order.',
    'probability': 'Ask whether events happen one after another, and whether anything is put back. Then multiply or add.',
}
NUDGE_DEFAULT = 'Check each step against the numbers in the question.'

# The text around the ladder on the practice page (Phase 3). The template renders it; site.js never holds copy of its
# own. Same lint as MESSAGES. 'locked' (typed) and 'locked_pick' (multiple choice) tell the pupil how Show answer opens;
# 'opened' is read out when it does. Review: the first wording ("once you have answered") was untrue after a first
# wrong typed answer, which leaves the drawer locked.
LADDER_COPY = {
    'hint': 'Hint',
    'bigger': 'Bigger hint',
    'more': 'Show a bigger hint',
    'locked': 'Opens after your first try',
    'opened': 'Show answer is now open.',
}

# ---------------------------------------------------------------------------------------------
# Reading the key and the pupil's answer
# ---------------------------------------------------------------------------------------------

SCALAR_TYPES = frozenset({'number', 'fraction', 'linear', 'pi_multiple', 'bearing'})
PAIR_TYPES = frozenset({'number_pair', 'vector'})
ROOTS_TYPES = frozenset({'quadratic_roots'})
DIAGNOSABLE_TYPES = SCALAR_TYPES | PAIR_TYPES | ROOTS_TYPES

# Topics whose number answers are angles in degrees (the 180 minus and 90 minus rules).
ANGLE_TOPICS = frozenset({'geometry_angles', 'circle_theorems'})

_POW10_STEPS = (1, 2, 3, -1, -2, -3)


def _expand(answer_type, text):
    if answer_type in _ac._VERBATIM_ANSWER_TYPES:
        return text
    return _ac._expand_vulgar_fractions(text)


def _linear_body(text):
    s = str(text or '').strip()
    m = re.fullmatch(r'[A-Za-z]\s*[==]\s*(.+)', s)
    return m.group(1) if m else s


def read_key(answer_type, raw):
    """The key as an exact Fraction (scalar types), or None when it cannot be read exactly."""
    raw = str(raw if raw is not None else '').strip()
    if not raw or '|' in raw:
        return None
    if answer_type == 'linear':
        raw = _linear_body(raw)
    if answer_type == 'bearing':
        parsed = _ac._parse_number(_ac._normalize_numeric_string(raw))
        return None if parsed is None else Fraction(int(round(parsed)) % 360)
    return _ac._parse_fraction_value(raw)


def read_user_scalar(answer_type, text, form=None):
    """The pupil's answer as an exact Fraction, read the way the checker reads it (None: not a number)."""
    if answer_type == 'bearing':
        # Read as check_bearing reads it (whole degrees); 000 to 360 only, anything else has the checker's own message.
        parsed = _ac._parse_number(_ac._normalize_numeric_string(text))
        if parsed is None:
            return None
        deg = int(round(parsed))
        if not 0 <= deg <= 360:
            return None
        # Whole-change review 2026-11-03 (F10): a bearing typed with a decimal part is read as typed for the diagnosis
        # ("8.2" for 082 is not 8, which is 90 - 82, "measured from east"); the checker still marks it to the degree.
        exact = Fraction(str(parsed))
        return Fraction(deg) if exact == deg else exact
    text = _expand(answer_type, str(text or ''))
    if answer_type == 'linear':
        text = _linear_body(text)
    if answer_type == 'pi_multiple':
        spelled = _ac._pi_multiple_value(text.strip())
        if spelled is not None:
            return Fraction(spelled)
        text = _ac._strip_pi_suffix(text) if len(text) <= _ac.MAX_SYMPY_EXPR_LEN else ''
    value = _ac._parse_fraction_value(text)
    if value is None and form == _ac.FORM_PROBABILITY and answer_type in ('number', 'fraction'):
        pct = _ac._percentage_value(text)
        if pct is not None:
            value = Fraction(pct)
    return value


# ---------------------------------------------------------------------------------------------
# Accuracy stated in the question
# ---------------------------------------------------------------------------------------------

_WORD_NUMBERS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
_DP_RE = re.compile(r'\b(\d+|one|two|three|four|five)\s*(?:decimal\s*places?|d\.?\s?p\b\.?)', re.I)
_SF_RE = re.compile(r'\b(\d+|one|two|three|four|five)\s*(?:significant\s*figures?|s\.?\s?f\b\.?)', re.I)
_NEAREST_RE = re.compile(r'nearest\s+((?:\d+(?:\.\d+)?)|(?:[a-z]+(?:\s+number)?))', re.I)
_NEAREST_WORDS = {
    'whole': 1, 'integer': 1, 'unit': 1, 'degree': 1, 'minute': 1, 'second': 1, 'hour': 1, 'metre': 1, 'meter': 1,
    'centimetre': 1, 'millimetre': 1, 'kilometre': 1, 'cm': 1, 'mm': 1, 'm': 1, 'km': 1, 'kg': 1, 'g': 1,
    'gram': 1, 'kilogram': 1, 'litre': 1, 'ml': 1, 'pound': 1, 'penny': Fraction(1, 100), 'cent': Fraction(1, 100),
    'tenth': Fraction(1, 10), 'hundredth': Fraction(1, 100), 'ten': 10, 'hundred': 100, 'thousand': 1000,
    'person': 1, 'people': 1, 'year': 1, 'day': 1, 'week': 1, 'month': 1, 'mile': 1, 'item': 1,
}
# "Estimate by rounding each number to ...": the accuracy is for the numbers in the question, not the answer.
_ROUNDS_INPUTS_RE = re.compile(r'\bround(?:ing)?\s+(?:each|every|both|all)\b', re.I)
# "Round 5304 to the nearest 10": a rounding task, where one step off means rounding the wrong way (there is no
# calculation, so "keep every digit" would make no sense).
_ROUNDING_TASK_RE = re.compile(r'^\s*(?:round|write)\s+[-\u2212]?\d[\d.,]*\s+(?:to|correct\s+to)\b', re.I)
# A value read off a graph: one step off in the last place is a reading, not a rounding slip, so the last-place
# rules stay silent.
_GRAPH_READING_RE = re.compile(r'\bgraph\b|\bcurve\b|\bogive\b|\bread\s+(?:off|from)\b', re.I)
# Division words: "the numbers were divided the other way round" only makes sense when the question divides.
_DIVISION_RE = re.compile(
    r'\u00f7|/|\\frac|\bdivid|\bper\b|\bgradient\b|\bspeed\b|\bvelocity\b|\bdensity\b|\bpressure\b|\brate\b|\bmean\b|'
    r'\baverage\b|\bshare[ds]?\b|\bsplit\b|\bratio\b|\bproportion|\bscale\s+factor\b|\bhow\s+many\s+times\b|'
    r'\bunit\s+price\b|\bfrequency\s+density\b', re.I)
# The answer is a percentage, or a decimal converted from one (a factor of 100 is then a form slip, not place value).
_PCT_ASK_RE = re.compile(
    r'\bas\s+an?\s+percentage\b|\bpercentage\s+(?:increase|decrease|change|profit|loss|error|gain|reduction|discount)\b|'
    r'\bwhat\s+percentage\b|\b(?:find|calculate|work\s+out|give)\s+the\s+percentage\b', re.I)
_DEC_ASK_RE = re.compile(r'\bas\s+a\s+decimal\b', re.I)
# The question asks for an angle (the 180 minus and 90 minus rules): every ask names an angle and none names a
# length, a count, a bearing or a letter to solve for.
_ASK_RE = re.compile(r'\b(?:find|calculate|work\s+out|what\s+is|what\s+are|write\s+down|determine|how\s+many)\b[^.?]*',
                     re.I)
_ANGLE_WORD_RE = re.compile(r'\bangles?\b', re.I)
_NOT_ANGLE_RE = re.compile(
    r'\bbearing|\bsides?\b|\blength|\bradius\b|\bdiameter\b|\barea\b|\bdistance\b|\bperimeter\b|\bsum\b|'
    r'\bnumber\s+of\b|\bvalue\s+of\b|\bfind\s+[a-z]\s*(?:,|\band\b|$)', re.I)
MAX_TEXT = 6000
MAX_LABELS = 12


def plain_text(*parts):
    """Visible text of question HTML: tags dropped, entities decoded, spaces collapsed (capped)."""
    out = []
    for part in parts:
        if not part:
            continue
        s = str(part)[:MAX_TEXT * 4]
        s = re.sub(r'<[^>]*>', ' ', s)
        out.append(_html.unescape(s))
    return re.sub(r'\s+', ' ', ' '.join(out)).strip()[:MAX_TEXT]


def stated_specs(text):
    """Rounding instructions in the text, in order: ('dp', n), ('sf', n), ('unit', Fraction)."""
    found = []
    for m in _DP_RE.finditer(text):
        n = m.group(1).lower()
        found.append(('dp', _WORD_NUMBERS.get(n) or int(n)))
    for m in _SF_RE.finditer(text):
        n = m.group(1).lower()
        found.append(('sf', _WORD_NUMBERS.get(n) or int(n)))
    for m in _NEAREST_RE.finditer(text):
        word = m.group(1).lower().strip()
        if re.fullmatch(r'\d+(?:\.\d+)?', word):
            found.append(('unit', Fraction(word)))
            continue
        first = word.split()[0]
        first = re.sub(r's$', '', first) if first not in ('cm', 'mm', 'km', 'kg', 'ml') else first
        if first in _NEAREST_WORDS:
            found.append(('unit', Fraction(_NEAREST_WORDS[first])))
    seen, out = set(), []
    for spec in found:
        if spec not in seen and ((spec[0] != 'unit' and 0 <= spec[1] <= 9) or (spec[0] == 'unit' and spec[1] > 0)):
            seen.add(spec)
            out.append(spec)
    return out


def _adjusted(x):
    """Exponent e with 10**e <= |x| < 10**(e+1) (x not zero)."""
    a, e = abs(x), 0
    while a >= 10:
        a /= 10
        e += 1
    while a < 1:
        a *= 10
        e -= 1
    return e


def grid_unit(spec, x):
    """The size of one step on the grid the spec rounds ``x`` to."""
    kind, n = spec
    if kind == 'dp':
        return Fraction(1, 10 ** n)
    if kind == 'sf':
        if x == 0:
            return None
        e = _adjusted(x) - n + 1
        return Fraction(10) ** e
    return Fraction(n)


def round_half_up(x, unit):
    """Round x to a multiple of ``unit``, halves away from zero (school rounding, as generators/shared/rounding.py)."""
    q = Fraction(x) / unit
    n = (abs(q) + Fraction(1, 2)).__floor__()
    return (n if q >= 0 else -n) * unit


def apply_spec(x, spec):
    unit = grid_unit(spec, x)
    return Fraction(x) if unit is None else round_half_up(x, unit)


def _stated_spec_for_key(text, key):
    """The first stated accuracy whose grid the key sits on (a key that is not on it was not rounded that way)."""
    if key == 0:
        return None
    if _ROUNDS_INPUTS_RE.search(text):
        return None
    for spec in stated_specs(text):
        unit = grid_unit(spec, key)
        if unit and (key / unit).denominator == 1:
            return spec
    return None


def _asks_for_angle(text):
    asks = _ASK_RE.findall(text or '')
    return bool(asks) and all(_ANGLE_WORD_RE.search(a) and not _NOT_ANGLE_RE.search(a) for a in asks)


def _part_labels(problem, correct_raw):
    """The labels of the parts of a multi-part answer whose key is ``correct_raw`` (None: not a part)."""
    problem = problem or {}
    if problem.get('answer_type') != 'number_fields':
        return None
    stored = str(problem.get('correct_answer_raw') or '')
    sep = '\x1e' if '\x1e' in stored else '|'
    parts = stored.split(sep)
    labels = problem.get('answer_labels')
    if isinstance(labels, str):
        try:
            labels = ast.literal_eval(labels) if len(labels) <= 2000 else []
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            labels = []
    if not isinstance(labels, (list, tuple)) or len(parts) > MAX_LABELS:
        return []
    idx = [i for i, part in enumerate(parts) if part == str(correct_raw)]
    return [str(labels[i]) for i in idx if i < len(labels)]


def _is_angle_answer(problem, correct_raw, text):
    """An answer in degrees: a part whose label carries a degree sign, or a question that asks only for angles."""
    labels = _part_labels(problem, correct_raw)
    if labels is not None:
        return bool(labels) and all('\u00b0' in lab and 'bearing' not in lab.lower() for lab in labels)
    return _asks_for_angle(text)


def _coarser(spec, steps):
    kind, n = spec
    if kind == 'dp':
        return ('dp', n - steps) if n - steps >= 0 else None
    if kind == 'sf':
        return ('sf', n - steps) if n - steps >= 1 else None
    return ('unit', Fraction(n) * 10 ** steps)


# ---------------------------------------------------------------------------------------------
# Context and rules
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Ctx:
    answer_type: str
    key: Optional[Fraction] = None            # scalar key
    spec: Optional[tuple] = None              # stated accuracy the key sits on
    fractional: bool = False                  # the key is a fraction (type fraction, or written with a slash)
    angle: bool = False                       # a degree answer between 0 and 180 in an angle topic
    rounding_task: bool = False               # the question asks to round a given number
    divides: bool = False                     # the question involves a division (or the answer solves an equation)
    pct_ask: bool = False                     # the answer is a percentage
    dec_ask: bool = False                     # the answer is a decimal converted from a percentage
    pair: Optional[tuple] = None              # (a, b) as Decimals, for number_pair and vector
    roots: Optional[tuple] = None             # the two distinct roots (SymPy), for quadratic_roots
    form: Optional[str] = None


@dataclass(frozen=True)
class Rule:
    id: str
    message: str                              # a key of MESSAGES
    kind: str                                 # 'scalar' | 'pair' | 'roots'
    types: frozenset
    candidates: Callable                      # Ctx -> list of exact values (Fractions, or the swapped pair)
    needs_spec: bool = False
    region: Optional[Callable] = None         # (Ctx, P) -> bool, for a slip that is a range of values
    when: Optional[Callable] = None           # Ctx -> bool


def _sgn(x):
    return 1 if x >= 0 else -1


def _c_sign(ctx):
    return [-ctx.key] if ctx.key != 0 else []


def _c_pow10(ctx):
    if ctx.key == 0:
        return []
    # A factor of 100 between a percentage and a decimal is a form slip, with its own message.
    skip = {-2} if ctx.pct_ask else ({2} if ctx.dec_ask else set())
    return [ctx.key * Fraction(10) ** j for j in _POW10_STEPS if j not in skip]


def _c_as_percentage(ctx):
    return [ctx.key / 100] if ctx.key != 0 else []


def _c_as_decimal(ctx):
    return [ctx.key * 100] if ctx.key != 0 else []


def _c_accuracy_coarser(ctx):
    """The key rounded to one or two places fewer. A value within one step of the key is left to the
    last-place rules (very close), so the two never name different slips for one answer."""
    unit = grid_unit(ctx.spec, ctx.key)
    out = []
    for steps in (1, 2):
        spec = _coarser(ctx.spec, steps)
        if spec is None:
            continue
        c = apply_spec(ctx.key, spec)
        if abs(c - ctx.key) > unit and c not in out:
            out.append(c)
    return out


def _c_accuracy_finer(ctx):
    """One representative of the range of unrounded values that round to the key."""
    unit = grid_unit(ctx.spec, ctx.key)
    return [ctx.key + _sgn(ctx.key) * unit / 4]


def _r_accuracy_finer(ctx, p):
    return p != ctx.key and apply_spec(p, ctx.spec) == ctx.key


def _c_last_place(ctx):
    """The two neighbours of the key on its grid (one step either way in the last place). From the key alone the
    direction cannot tell a cut-off from a value rounded too early, so both directions share one message."""
    unit = grid_unit(ctx.spec, ctx.key)
    s = _sgn(ctx.key)
    up, down = ctx.key + s * unit, ctx.key - s * unit
    if ctx.spec[0] == 'sf' and down != 0 and _adjusted(down) < _adjusted(ctx.key):
        down = ctx.key - s * unit / 10      # below a power of ten the significant-figure grid is finer (1000 -> 999)
    return [down, up]


def _c_reciprocal(ctx):
    if ctx.key == 0 or abs(ctx.key) == 1:
        return []
    return [1 / ctx.key]


def _c_supplement(ctx):
    return [180 - ctx.key]


def _c_complement(ctx):
    return [90 - ctx.key] if ctx.key < 90 else []


def _c_swapped(ctx):
    a, b = ctx.pair
    return [(b, a)] if a != b else []


def _c_one_root(ctx):
    return list(ctx.roots)


def _c_roots_negated(ctx):
    """Both roots with their signs flipped, as one set (the bracket (x + 2) read as a root of +2).

    Only for whole-number or fraction roots (review 2026-10-26): the message speaks of the number in a bracket, which
    is the factorising route; roots with a surd come from the formula, where flipped signs have other causes.
    """
    if not all(getattr(r, 'is_rational', False) for r in ctx.roots):
        return []
    negated = tuple(-r for r in ctx.roots)
    if {_ac._format_quadratic_root(r) for r in negated} == {_ac._format_quadratic_root(r) for r in ctx.roots}:
        return []              # the pair is its own mirror image (for example 3 and -3): nothing to say
    return [negated]


def _c_bearing_reversed(ctx):
    return [(ctx.key + 180) % 360]


def _c_bearing_anticlockwise(ctx):
    return [(360 - ctx.key) % 360] if ctx.key not in (0, 180) else []


_NUM_TYPES = frozenset({'number', 'linear', 'pi_multiple'})

GENERIC_RULES = (
    Rule('gen.sign', 'gen.sign', 'scalar', SCALAR_TYPES - {'bearing'}, _c_sign),
    Rule('gen.pow10', 'gen.pow10', 'scalar', _NUM_TYPES, _c_pow10),
    Rule('gen.accuracy_coarser', 'gen.accuracy', 'scalar', frozenset({'number', 'linear'}), _c_accuracy_coarser,
         needs_spec=True),
    Rule('gen.accuracy_finer', 'gen.accuracy', 'scalar', frozenset({'number', 'linear'}), _c_accuracy_finer,
         needs_spec=True, region=_r_accuracy_finer),
    # One step off in the last place: rounded the wrong way in a rounding task, else a near miss in a calculation.
    Rule('gen.truncated', 'gen.truncated', 'scalar', frozenset({'number', 'linear'}), _c_last_place, needs_spec=True,
         when=lambda ctx: ctx.rounding_task),
    Rule('gen.early_round', 'gen.early_round', 'scalar', frozenset({'number', 'linear'}), _c_last_place,
         needs_spec=True, when=lambda ctx: not ctx.rounding_task),
    Rule('gen.reciprocal', 'gen.reciprocal', 'scalar', _NUM_TYPES, _c_reciprocal,
         when=lambda ctx: not ctx.fractional and ctx.divides),
    Rule('gen.as_percentage', 'gen.as_percentage', 'scalar', frozenset({'number'}), _c_as_percentage,
         when=lambda ctx: ctx.pct_ask),
    Rule('gen.as_decimal', 'gen.as_decimal', 'scalar', frozenset({'number'}), _c_as_decimal,
         when=lambda ctx: ctx.dec_ask),
    Rule('gen.reciprocal_fraction', 'gen.reciprocal_fraction', 'scalar', frozenset({'number', 'fraction'}),
         _c_reciprocal, when=lambda ctx: ctx.fractional),
    Rule('ang.supplement', 'ang.supplement', 'scalar', frozenset({'number'}), _c_supplement,
         when=lambda ctx: ctx.angle),
    Rule('ang.complement', 'ang.complement', 'scalar', frozenset({'number'}), _c_complement,
         when=lambda ctx: ctx.angle),
    Rule('gen.pair_swapped', 'gen.pair_swapped', 'pair', PAIR_TYPES, _c_swapped),
    Rule('gen.one_root', 'gen.one_root', 'roots', ROOTS_TYPES, _c_one_root),
    # Phase 5: the signs of both roots flipped, and the two commonest bearing slips that need only the key
    Rule('alg.root_signs', 'alg.root_signs', 'roots_set', ROOTS_TYPES, _c_roots_negated),
    Rule('brg.reversed', 'brg.reversed', 'scalar', frozenset({'bearing'}), _c_bearing_reversed),
    Rule('brg.anticlockwise', 'brg.anticlockwise', 'scalar', frozenset({'bearing'}), _c_bearing_anticlockwise),
)
RULES_BY_ID = {r.id: r for r in GENERIC_RULES}


def _applies(rule, ctx):
    if ctx.answer_type not in rule.types:
        return False
    if rule.needs_spec and ctx.spec is None:
        return False
    return rule.when is None or bool(rule.when(ctx))


def _tidy(rule, ctx):
    """A rule's usable scalar candidates: never the key itself, and never a value that rounds to the key."""
    if rule.region is not None:
        return list(rule.candidates(ctx))
    out = []
    for c in rule.candidates(ctx):
        if c == ctx.key or (ctx.spec and apply_spec(c, ctx.spec) == ctx.key):
            continue
        out.append(c)
    return out


# ---------------------------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------------------------

def _pair_of(answer_type, raw):
    if answer_type == 'number_pair':
        return _ac._parse_number_pair(raw)
    s, _dp = _ac._split_vector_correct_raw(raw)
    return _ac._parse_vector_pair(s)


def _user_pair(answer_type, text):
    if answer_type == 'number_pair':
        return _ac._parse_number_pair(text)
    return _ac._parse_vector_pair(text)


def _roots_of(raw, expand):
    parts = _ac._split_quadratic_roots_raw(raw)
    if parts is None or len(parts) > 2:
        return None                          # more than two roots is never one of these slips (and stays cheap)
    if expand:
        parts = _ac._expand_quadratic_root_pm(parts)
        if len(parts) > 2:
            return None
    roots = [_ac._root_to_sympy(p) for p in parts]
    return None if any(r is None for r in roots) else roots


def build_ctx(problem, answer_type, correct_raw, topic='', form=None):
    """The rule context for a stored problem and (part of) its key, or None when this answer has none."""
    if answer_type in SCALAR_TYPES:
        key = read_key(answer_type, correct_raw)
        if key is None:
            return None
        question = plain_text((problem or {}).get('question'))
        text = plain_text(question, (problem or {}).get('answer_format_hint'))
        spec = None if answer_type in ('pi_multiple', 'fraction') else _stated_spec_for_key(text, key)
        rounding_task = bool(_ROUNDING_TASK_RE.search(question))
        if spec is not None and not rounding_task and _GRAPH_READING_RE.search(question):
            spec = None                          # a value read off a graph: no rounding advice
        raw = str(correct_raw)
        pct, dec = bool(_PCT_ASK_RE.search(question)), bool(_DEC_ASK_RE.search(question)) and '%' in question
        return Ctx(
            answer_type=answer_type, key=key, spec=spec, form=form,
            fractional=answer_type == 'fraction' or '/' in raw,
            angle=(answer_type == 'number' and topic in ANGLE_TOPICS and 0 < key < 180
                   and _is_angle_answer(problem, correct_raw, question)),
            rounding_task=rounding_task,
            divides=answer_type == 'linear' or bool(_DIVISION_RE.search(question)),
            pct_ask=pct and not dec, dec_ask=dec and not pct,
        )
    if answer_type in PAIR_TYPES:
        pair = _pair_of(answer_type, correct_raw)
        return Ctx(answer_type=answer_type, pair=pair, form=form) if pair else None
    if answer_type in ROOTS_TYPES:
        roots = _roots_of(correct_raw, expand=False)
        if not roots or len(roots) != 2 or _ac._sympy_roots_equal(roots[0], roots[1]):
            return None
        return Ctx(answer_type=answer_type, roots=tuple(roots), form=form)
    return None


# ---------------------------------------------------------------------------------------------
# Typing a candidate (used to check the checker's verdict, and by the tests)
# ---------------------------------------------------------------------------------------------

def format_answer(value):
    """A Fraction as the text a pupil would type: a decimal when it terminates, else n/d."""
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    d = value.denominator
    k = next((j for j in range(1, 13) if (10 ** j) % d == 0), None)
    if k is None:
        return f'{value.numerator}/{value.denominator}'
    scaled = abs(value.numerator) * (10 ** k) // d
    digits = str(scaled).rjust(k + 1, '0')
    text = f'{digits[:-k]}.{digits[-k:]}'.rstrip('0').rstrip('.')
    return ('-' if value < 0 else '') + text


def _match_value(rule, ctx, c):
    """The value a pupil who made this slip would type: the candidate, rounded as told when a rule gave it exactly."""
    if rule.region is not None:
        return c
    if ctx.spec is None:
        return c
    rounded = apply_spec(c, ctx.spec)
    # Rounded as told only while the rounding keeps the value recognisable (within 5%): 0.357 -> 0.36 is the slip,
    # 0.007 -> 0.01 is any small number.
    if rounded == 0 or abs(rounded - c) * 20 > abs(c):
        return c
    return rounded


def typed_examples(problem, answer_type, correct_raw, topic='', form=None):
    """[(rule id, typed text)] for every rule that has a candidate on this answer (tests and coverage)."""
    ctx = build_ctx(problem, answer_type, correct_raw, topic, form)
    out = []
    if ctx is None:
        return out
    for rule in GENERIC_RULES:
        if not _applies(rule, ctx):
            continue
        if rule.kind == 'scalar':
            for c in _tidy(rule, ctx):
                out.append((rule.id, format_answer(_match_value(rule, ctx, c))))
        elif rule.kind == 'pair':
            for a, b in rule.candidates(ctx):
                out.append((rule.id, f'{_ac._format_number(a)}|{_ac._format_number(b)}'))
        elif rule.kind == 'roots_set':
            for roots in rule.candidates(ctx):
                out.append((rule.id, ','.join(_ac._format_quadratic_root(r) for r in roots)))
        else:
            for root in rule.candidates(ctx):
                out.append((rule.id, _ac._format_quadratic_root(root)))
    return out


# ---------------------------------------------------------------------------------------------
# Topic rules (Phase 2): recorded inputs
# ---------------------------------------------------------------------------------------------

_cd = _topics._cd
MESSAGES.update(_cd.MESSAGES_5B)       # Phase 5b messages (data in misconception_5b.py)
TOPIC_RULES = _topics.RULES
TOPIC_RULES_BY_ID = _topics.RULES_BY_ID
_TOPIC_TYPES = frozenset({'number', 'pi_multiple', 'fraction', 'bearing', 'linear'})
# family -> the answer types a record of that family may sit on (Phase 5: pairs, expressions and several boxes too)
RECORD_TYPES = {fam: _TOPIC_TYPES for fam in _topics.FAMILIES}
for _fam in _cd.PART_FAMILIES:
    RECORD_TYPES[_fam] = RECORD_TYPES.get(_fam, frozenset()) | {'number_fields'}
for _fam in _cd.PAIR_FAMILIES:
    RECORD_TYPES[_fam] = RECORD_TYPES.get(_fam, frozenset()) | PAIR_TYPES
for _fam in _cd.EXPR_FAMILIES:
    RECORD_TYPES[_fam] = RECORD_TYPES.get(_fam, frozenset()) | {'algebraic'}
del _fam
RECORDED_FAMILIES = RECORD_TYPES
EXPR_TYPES = frozenset({'algebraic'})
_RECORD_MAX_BYTES = 256          # as generators/shared/answer_record.MAX_BYTES (that module imports this one lazily)
_TYPED_RE = re.compile(r'[+\-\u2212]?\d+(?:\.(\d+))?')


def read_record(problem, answer_type, correct_raw):
    """(family, inputs) from the problem's answer record, if it belongs to this very answer; else None."""
    if not isinstance(problem, dict):
        return None
    rec = problem.get('answer_record')
    if not isinstance(rec, dict):
        return None
    family, inputs = rec.get('f'), rec.get('i')
    if family not in RECORDED_FAMILIES or answer_type not in RECORDED_FAMILIES[family] or not isinstance(inputs, dict):
        return None
    if (problem.get('answer_type') or 'number') != answer_type or str(problem.get('correct_answer_raw')) != str(correct_raw):
        return None
    try:   # the 256-byte cap is checked again on the way in (defence in depth: a record is only ever this small)
        if len(_json.dumps(rec, separators=(',', ':'), ensure_ascii=False).encode('utf-8')) > _RECORD_MAX_BYTES:
            return None
    except (TypeError, ValueError, RecursionError):
        return None
    return family, inputs


def _agrees(truth, ctx):
    """The rebuilt answer reproduces the stored key (at the stated accuracy, or exactly when none is stated)."""
    if truth is None:
        return False
    truth = Fraction(truth)
    if ctx.spec is not None:
        return apply_spec(truth, ctx.spec) == ctx.key
    return truth == ctx.key


def _places_of(x):
    """Decimal places of an exact value when it terminates within six places, else six."""
    x = Fraction(x)
    for k in range(7):
        if (x * 10 ** k).denominator == 1:
            return k
    return 6


def _near_key(ctx, p, places):
    """A typed value next to the key: an early rounding or a small arithmetic slip, which the generic rules speak to.
    A topic rule that happens to land there is not shown (review 2026-10-26: "252" for a surface area of 254 was
    called "a volume"; "79" for 80 matched 79.2 rounded to the pupil's own places).

    With a stated accuracy: one step of it either side (as ``gen.early_round``). Without: at most two units in the
    last place (the finer of the pupil's and the key's decimal places) and at most 2% of the key, so that 7 for a
    hypotenuse of 5 (the sides added) is still a slip, but 65 for 66 is not.
    """
    diff = abs(Fraction(p) - ctx.key)
    if ctx.spec is not None:
        step = grid_unit(ctx.spec, ctx.key)
        if step is not None and diff <= step:
            return True
        # Whole-change review 2026-11-03 (F3): the key rounded one or two steps coarser than the question asks ("70" for
        # a distance of 69.8 to 1 d.p.) is the accuracy slip of the generic rules, never a topic slip that lands there.
        return any(s is not None and apply_spec(ctx.key, s) == Fraction(p) for s in (_coarser(ctx.spec, 1),
                                                                                    _coarser(ctx.spec, 2)))
    typed = places if places is not None else _places_of(p)
    # Phase 5b review: the key itself, typed as a plain decimal cut or rounded to fewer places (13 or 14 for 13.5), is
    # the right answer written short, not a slip; "13" for QR = 13.5 was called "adding the same amount" (9 + 12 - 8).
    # For a number answer typed as a plain number this silences every topic rule; other answer types keep only exact
    # slips (see ``_key_cut_short`` and ``_topic_hits``).
    if places is not None and ctx.answer_type == 'number' and _key_cut_short(ctx, p, typed):
        return True
    step = Fraction(1, 10 ** max(typed, _places_of(ctx.key)))
    return diff <= 2 * step and diff * 50 <= abs(ctx.key)


# Topic rules whose slip is, by its nature, the key written as a short decimal (see ``_topic_hits``).
CUT_SHORT_RULES = frozenset({'num.recurring_terminating'})


def _key_cut_short(ctx, p, typed):
    """The typed value is the key itself rounded or cut to the ``typed`` decimal places the pupil used (fewer than the
    key needs), and that shorter form keeps a digit of the key (not 0 for 0.25)."""
    if typed is None or ctx.key is None or typed >= _places_of(ctx.key) or Fraction(1, 10 ** typed) > abs(ctx.key):
        return False
    unit = Fraction(1, 10 ** typed)
    whole = abs(ctx.key) / unit
    cut = Fraction(whole.numerator // whole.denominator) * unit * (1 if ctx.key > 0 else -1)
    return Fraction(p) in (round_half_up(ctx.key, unit), cut)


def _quiet_hit(ctx, rule, p, places, quiet):
    """The typed value is also a quiet value (a number from the question, or a slip with no message): silence."""
    if not quiet:
        return False
    nums, extra = quiet
    pool = list(extra)
    if rule.id not in _topics.ECHO_OK and ctx.answer_type != 'pi_multiple':
        pool += nums           # a coefficient of pi is not a number copied from the question
    return any(p == q or p == _topic_shown(ctx, q, places, to_whole=True) for q in pool)


def topic_quiet(problem, answer_type, correct_raw):
    """The quiet values of this answer's record (see misconception_topics.QUIET), or None."""
    rec = read_record(problem, answer_type, correct_raw)
    if rec is None:
        return None
    pi = Fraction(1) if answer_type == 'pi_multiple' else _topics.PI
    return _topics.quiet_values(rec[0], rec[1], pi)


def topic_candidates(problem, answer_type, correct_raw, ctx):
    """[(rule, exact value)] for a scalar answer, or None when there is no usable record, or [] when the guard fails.

    A candidate equal to the key (or that rounds to it at the stated accuracy) is not a slip and is dropped; so is
    one that lands within two steps of the key, or on a quiet value (see ``_near_key`` and ``_quiet_hit``).
    """
    rec = read_record(problem, answer_type, correct_raw)
    if rec is None or ctx is None or ctx.key is None:
        return None
    family, inputs = rec
    pi = Fraction(1) if answer_type == 'pi_multiple' else _topics.PI
    try:
        if not _agrees(_topics.TRUTH[family](inputs, pi), ctx):
            return []
    except Exception:  # noqa: BLE001 - a record that does not fit the family is simply not used
        return []
    quiet = _topics.quiet_values(family, inputs, pi)
    out = []
    guards = getattr(_cd, 'TEXT_GUARDS', None) or {}
    text = None
    for rule in _topics.RULES_BY_FAMILY.get(family, ()):
        guard = guards.get(rule.id)
        if guard is not None:          # Phase 5b review: a rule that needs the question to read a certain way
            if text is None:
                text = plain_text((problem or {}).get('question'))
            try:
                if not guard(text, inputs):
                    continue
            except Exception:  # noqa: BLE001 - a guard that cannot read the record keeps the rule quiet
                continue
        try:
            values = [Fraction(c) for c in rule.slip(inputs, pi) if c is not None]
        except Exception:  # noqa: BLE001
            continue
        for c in values:
            if c == ctx.key or (ctx.spec is not None and apply_spec(c, ctx.spec) == ctx.key):
                continue
            shown = _topic_shown(ctx, c)
            places = _typed_places(format_answer(shown))
            if _near_key(ctx, shown, places) or _quiet_hit(ctx, rule, shown, places, quiet):
                continue
            out.append((rule, c))
    return out


def _typed_places(text):
    """Decimal places the pupil typed in a plain number (None for anything else, or more than six)."""
    m = _TYPED_RE.fullmatch(str(text or '').strip())
    if not m:
        return None
    places = len(m.group(1) or '')
    return places if places <= 6 else None


def _told(ctx, c):
    """The value a pupil who rounds as the question says would type for exact value ``c`` (as ``_match_value``)."""
    if ctx.spec is None:
        return c
    rounded = apply_spec(c, ctx.spec)
    if rounded == 0 or abs(rounded - c) * 20 > abs(c):
        return c
    return rounded


def _topic_shown(ctx, c, places=None, to_whole=False):
    """The text-able value for candidate ``c``: as told, else rounded to the pupil's own places, else to six.

    ``to_whole``: a whole number typed may stand for ``c`` rounded to no places. Only the quiet check (silence) does
    that; a slip itself never matches a whole typed value by rounding when the question states no accuracy (whole-change
    review 2026-11-03, F2: "12" for x = 11 was called "the sign of the term that moved" through 35/3 = 11.67)."""
    if ctx.spec is not None:
        return _told(ctx, c)
    # Rounded to the pupil's own places only when the exact value needs more than two decimal places (review
    # 2026-10-26, found by --deep: 22.5 "rounded" to 23 called a typed 23 "brackets ignored" when the key was -23; a
    # pupil who reached 22.5 with no accuracy asked would type 22.5).
    if places is not None and (places >= 1 or to_whole) and (c * 100).denominator != 1:
        shown = round_half_up(c, Fraction(1, 10 ** places))
        if shown != 0 and abs(shown - c) * 20 <= abs(c):
            return shown
    d = c.denominator
    for q in (2, 5):
        while d % q == 0:
            d //= q
    if d != 1 or c.denominator > 10 ** 12:
        return round_half_up(c, Fraction(1, 10 ** 6))      # not a terminating decimal: six places is what is typed
    return c


def topic_examples(problem, answer_type, correct_raw, topic='', form=None):
    """[(rule id, typed text)] for every topic candidate of this answer (tests and coverage)."""
    ctx = build_ctx(problem, answer_type, correct_raw, topic, form)
    cands = topic_candidates(problem, answer_type, correct_raw, ctx)
    return [(rule.id, format_answer(_topic_shown(ctx, c))) for rule, c in cands or []]


def _topic_hits(ctx, cands, user_text, accepts, quiet=None):
    p = read_user_scalar(ctx.answer_type, user_text, ctx.form)
    if p is None or not cands:
        return {}
    places = _typed_places(user_text)
    if _near_key(ctx, p, places):
        return {}
    # Whole-change review 2026-11-03 (F1): the key rounded or cut to the pupil's own places (0.4 for 4/9, 7 for 7 1/4)
    # is the right answer written short. A slip that only rounds to it never speaks there ("the item is put back" for
    # 0.4), and neither does one that is exactly that short decimal by chance (3/10 without replacement for a key of
    # 9/25 typed 0.3): only a rule whose slip is the key written short by its nature (0.3 for 1/3, a recurring
    # decimal read as ending) may speak, and only at its exact value. Only a plain decimal typed counts as written short
    # (3/10 typed as a fraction is the slip itself).
    typed_dp = _typed_places(_plain_number_text(ctx.answer_type, user_text))
    exact_only = ctx.spec is None and typed_dp is not None and _key_cut_short(ctx, p, typed_dp)
    hits = {}
    hushed = {}
    rivals = {}
    for rule, c in cands:
        shown = _topic_shown(ctx, c, places)
        matched = p == shown or p == c
        # F2: a whole typed value never names a slip that only rounds to it, but that slip is still another way to it
        loose = matched or p == _topic_shown(ctx, c, places, to_whole=True)
        if not loose:
            continue
        # A candidate the checker accepts is a right answer, never a slip.
        if accepts(format_answer(shown)):
            continue
        if not matched or (exact_only and (rule.id not in CUT_SHORT_RULES or p != c)):
            rivals.setdefault(rule.message, rule.id)
            continue
        if _quiet_hit(ctx, rule, p, places, quiet):
            hushed.setdefault(rule.message, rule.id)
            continue
        hits.setdefault(rule.message, rule.id)
    # Review 2026-10-26: a rule kept quiet (the value is printed in the question) is still another way to reach the
    # typed value. If it names a different slip, the value is ambiguous: silence, never the remaining message (a mean
    # of 9 that is both the middle value and the total over n - 1 was called "the middle value"). The same for a slip
    # that may not speak on this value (F1, F2) but still reaches it.
    if hits and any(m not in hits for m in list(hushed) + list(rivals)):
        hits.update(hushed)
        hits.update(rivals)
    return hits


def _plain_number_text(answer_type, text):
    """The number part of a typed answer as the pupil wrote it: a linear answer without "x =", a multiple of pi without
    its pi (for reading the decimal places typed)."""
    t = str(text or '').strip()
    if answer_type == 'linear':
        t = _linear_body(t)
    elif answer_type == 'pi_multiple':
        t = re.sub(r'\s*(?:\u03c0|\\pi|pi)\s*$', '', t, flags=re.I)
    return t


# ---------------------------------------------------------------------------------------------
# Phase 5: a part of a multi-box answer, a pair, an expression
# ---------------------------------------------------------------------------------------------

def read_part_record(problem, part, correct_raw):
    """(family, inputs, all parts' keys) when the answer record belongs to part ``part`` of this answer, else None."""
    if part is None or not isinstance(problem, dict) or problem.get('answer_type') != 'number_fields':
        return None
    rec = problem.get('answer_record')
    if not isinstance(rec, dict):
        return None
    family, inputs = rec.get('f'), rec.get('i')
    if family not in _cd.PART_FAMILIES or not isinstance(inputs, dict):
        return None
    try:
        if len(_json.dumps(rec, separators=(',', ':'), ensure_ascii=False).encode('utf-8')) > _RECORD_MAX_BYTES:
            return None
    except (TypeError, ValueError, RecursionError):
        return None
    stored = str(problem.get('correct_answer_raw') or '')
    parts = stored.split('\x1e' if '\x1e' in stored else '|')
    if not isinstance(part, int) or isinstance(part, bool) or not 0 <= part < len(parts) \
            or parts[part] != str(correct_raw) or len(parts) > MAX_LABELS * 2:
        return None
    return family, inputs, parts


def _part_spec(text, key, token):
    """The accuracy that applies to one box of a multi-box answer. Bearings are whole degrees; lengths take the
    coarsest decimal-place rule of the question that the key sits on (a mixed question has more than one)."""
    if token in _cd.INTEGER_TOKENS:
        return ('unit', Fraction(1))
    if token not in _cd.DECIMAL_TOKENS or key == 0:
        return None
    best = None
    for spec in stated_specs(text):
        if spec[0] != 'dp':
            continue
        unit = grid_unit(spec, key)
        if unit and (key / unit).denominator == 1 and (best is None or unit > grid_unit(best, key)):
            best = spec
    return best


# Review 2026-10-26: a slip of the whole shape (turned the other way, reflected in the other axis, scale factor sign
# ignored) gives every box of an image about the origin with its sign flipped. One box with only its sign wrong is
# just as likely an arithmetic sign slip, and naming the whole-shape slip would contradict a box already marked right
# (P' x right, P' y typed with the wrong sign: "Check the turn direction"). Such a box gets the generic sign line.
# Whole-change review 2026-11-03 (F7): the same for a quadratic simultaneous pair. For x = -2 the y box typed -4 is
# both 2x and -(x squared), so "multiplied by the power" is no likelier than (-2) squared read as -4, or a sign slip.
_NO_SIGN_ONLY_PARTS = frozenset({'trans_apply', 'qsim_solve'})


def part_topic(problem, part, answer_type, correct_raw, topic='', form=None):
    """(ctx, [(rule, exact value)], quiet) for one box of a multi-box answer, or None (no record, or a mismatch).

    The rebuilt answer has to reproduce the key of every box (each at its own accuracy) before any rule is used.
    """
    rec = read_part_record(problem, part, correct_raw)
    if rec is None:
        return None
    family, inputs, keys = rec
    base = build_ctx(problem, answer_type, correct_raw, topic, form)
    if base is None or base.key is None:
        return None
    try:
        tokens = _cd.PART_TOKENS[family](inputs)
        truth = _cd.PART_TRUTH[family](inputs)
    except Exception:  # noqa: BLE001
        return []
    if not (len(tokens) == len(truth) == len(keys)):
        return []
    text = plain_text((problem or {}).get('question'), (problem or {}).get('answer_format_hint'))
    specs = []
    for j, raw in enumerate(keys):
        if truth[j] is None:             # a box the family does not model (a pick, a ratio): it has no slip and no key to check
            specs.append(None)
            continue
        key_j = read_key('number', raw)
        if key_j is None:
            return []
        spec_j = _part_spec(text, key_j, tokens[j])
        mine = Fraction(truth[j])
        if (apply_spec(mine, spec_j) if spec_j is not None else mine) != key_j:
            return []
        specs.append(spec_j)
    ctx = _dc_replace(base, spec=specs[part])
    quiet = _topics.quiet_values(family, inputs, Fraction(1))
    # Phase 5b review: the right answer of another box, typed here, is silent for the rules in PART_OTHER_BOX_QUIET
    other_keys = {read_key('number', raw) for j, raw in enumerate(keys) if j != part and truth[j] is not None}
    other_box_quiet = getattr(_cd, 'PART_OTHER_BOX_QUIET', frozenset())
    cands = []
    for rule in _cd.PART_BY_FAMILY.get(family, ()):
        try:
            vectors = rule.slip(inputs)
        except Exception:  # noqa: BLE001
            continue
        for vec in vectors:
            if not isinstance(vec, (list, tuple)) or len(vec) != len(tokens):
                continue
            entry = vec[part]
            values = entry if isinstance(entry, (list, tuple)) else [entry]
            for c in values:
                if c is None:
                    continue
                c = Fraction(c)
                if c == ctx.key or (ctx.spec is not None and apply_spec(c, ctx.spec) == ctx.key):
                    continue
                if family in _NO_SIGN_ONLY_PARTS and c == -ctx.key and rule.message not in _SIGN_MESSAGES:
                    continue       # one box with only its sign wrong: a sign line, never a whole-shape slip
                shown = _topic_shown(ctx, c)
                if _near_key(ctx, shown, _typed_places(format_answer(shown))):
                    continue
                if rule.id in other_box_quiet and (c in other_keys or shown in other_keys):
                    continue
                cands.append((rule, c))
    return ctx, cands, quiet


_SIGN_MESSAGES = frozenset({'alg.root_signs', 'alg.sign_moved', 'vec.order_reversed', 'vec.sign_not_changed'})


def _one_sign_off(shown, key):
    """The pair differs from the key only in sign (each value equal to the key's or its negative).

    Review 2026-10-26: the midpoint of (-3, 0) and (0, -1) typed as (-1.5, 0.5) matched "subtracted instead of added",
    because the zeros make the difference equal to the key in x; a pupil with the x value right most likely slipped on
    one sign. Only rules whose message is itself about signs (or about the vector pointing the other way) may speak.
    """
    if shown == key:
        return False
    return all(s == k or s == -k for s, k in zip(shown, key))


def _pair_numbers(inputs):
    vals = []
    for v in list(inputs.values())[:_topics.MAX_TERMS]:
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        try:
            vals.append(_topics.F(v))
        except (ValueError, ZeroDivisionError, OverflowError):
            pass
    return [(vals[k], vals[k + 1]) for k in range(0, len(vals) - 1, 2)]


def pair_topic_hits(problem, ctx, text, accepts, topic=''):
    """{message: rule id} for a pair answer (a vector or a coordinate pair) from the answer record, or None."""
    rec = read_record(problem, ctx.answer_type, problem.get('correct_answer_raw'))
    if rec is None or rec[0] not in _cd.PAIR_FAMILIES or ctx.pair is None:
        return None
    family, inputs = rec
    user = _user_pair(ctx.answer_type, text)
    if user is None:
        return {}
    question = plain_text(problem.get('question'), problem.get('answer_format_hint'))
    key = tuple(Fraction(c) for c in ctx.pair)
    spec = _stated_spec_for_key(question, key[0]) if key[0] != 0 else None
    if spec is None and key[1] != 0:
        spec = _stated_spec_for_key(question, key[1])

    def told(x):
        x = Fraction(x)
        return apply_spec(x, spec) if spec is not None else x

    try:
        truth = _cd.PAIR_TRUTH[family](inputs)
        if (told(truth[0]), told(truth[1])) != key:
            return {}
        typed = (Fraction(user[0]), Fraction(user[1]))
        printed = _pair_numbers(inputs)
    except Exception:  # noqa: BLE001
        return {}
    hits = {}
    for rule in _cd.PAIR_BY_FAMILY.get(family, ()):
        try:
            slips = rule.slip(inputs)
        except Exception:  # noqa: BLE001
            continue
        for cand in slips:
            shown = (told(cand[0]), told(cand[1]))
            if shown == key or shown != typed:
                continue
            if _one_sign_off(shown, key) and rule.message not in _SIGN_MESSAGES:
                continue               # one value right and the other only negated: a sign slip explains it as well
            if typed in printed and rule.id not in _topics.ECHO_OK:
                continue               # the pair is one the question printed: more likely copied than computed
            if accepts(f'{_ac._format_number(_decimal_of(shown[0]))}|{_ac._format_number(_decimal_of(shown[1]))}'):
                continue
            hits.setdefault(rule.message, rule.id)
    return hits


def _decimal_of(x):
    from decimal import Decimal
    x = Fraction(x)
    return Decimal(x.numerator) / Decimal(x.denominator)


def expr_hits(problem, correct_raw, text, accepts):
    """{message: rule id} for an algebraic answer from the answer record, or None when there is no usable record.

    Both the rebuilt answer and every slip are compared with the typed text by the checker's own safe algebra
    (``answer_checkers._algebraic_answers_equivalent``: the same parser, the same caps).
    """
    rec = read_record(problem, 'algebraic', correct_raw)
    if rec is None or rec[0] not in _cd.EXPR_FAMILIES:
        return None
    family, inputs = rec
    if len(text) > _ac.MAX_SYMPY_EXPR_LEN:
        return {}
    try:
        subject, truth = _cd.EXPR_TRUTH[family](inputs)
    except Exception:  # noqa: BLE001
        return {}
    prefix = f'{subject}=' if subject else ''
    if not _ac._algebraic_answers_equivalent(str(correct_raw), prefix + truth):
        return {}                        # the rebuilt answer is not the key: stay silent
    hits = {}
    for rule in _cd.EXPR_BY_FAMILY.get(family, ()):
        try:
            slips = rule.slip(inputs)
        except Exception:  # noqa: BLE001
            continue
        for cand in slips[:8]:
            full = prefix + cand
            if len(full) > _ac.MAX_SYMPY_EXPR_LEN:
                continue
            if _ac._algebraic_answers_equivalent(full, text):
                # the typed text is this slip: a slip that is also the key (or that the checker accepts) is no slip
                if _ac._algebraic_answers_equivalent(str(correct_raw), full) or accepts(full):
                    continue
                hits.setdefault(rule.message, rule.id)
                break
    return hits


# ---------------------------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Diagnosis:
    rule_id: str
    message: str
    kind: str          # 'misconception' (after a wrong answer) | 'note' (on a correct answer)


def _scalar_hits(ctx, user_text, accepts):
    p = read_user_scalar(ctx.answer_type, user_text, ctx.form)
    if p is None:
        return {}
    hits = {}
    for rule in GENERIC_RULES:
        if rule.kind != 'scalar' or not _applies(rule, ctx):
            continue
        for c in _tidy(rule, ctx):
            if rule.region is not None:
                matched = rule.region(ctx, p)
            else:
                matched = p == _match_value(rule, ctx, c) or p == c
            if not matched:
                continue
            # A candidate the checker accepts is a right answer, never a slip.
            if accepts(format_answer(c)) or accepts(format_answer(_match_value(rule, ctx, c))):
                continue
            hits.setdefault(rule.message, rule.id)
            break
    return hits


def _pair_hits(ctx, user_text, accepts):
    user = _user_pair(ctx.answer_type, user_text)
    if user is None:
        return {}
    hits = {}
    for rule in GENERIC_RULES:
        if rule.kind != 'pair' or not _applies(rule, ctx):
            continue
        for a, b in rule.candidates(ctx):
            if user == (a, b):
                if accepts(f'{_ac._format_number(a)}|{_ac._format_number(b)}'):
                    continue
                hits.setdefault(rule.message, rule.id)
    return hits


def _roots_hits(ctx, user_text, accepts):
    user = _roots_of(user_text, expand=True)
    if not user or len(user) > 2:
        return {}
    hits = {}
    for rule in GENERIC_RULES:
        if rule.kind not in ('roots', 'roots_set') or not _applies(rule, ctx):
            continue
        if rule.kind == 'roots_set':
            # the typed roots are the key's roots with their signs flipped (as a set, in either order)
            for roots in rule.candidates(ctx):
                if len(user) == len(roots) and all(any(_ac._sympy_roots_equal(r, u) for u in user) for r in roots):
                    if accepts(','.join(_ac._format_quadratic_root(r) for r in roots)):
                        continue
                    hits.setdefault(rule.message, rule.id)
            continue
        for root in rule.candidates(ctx):
            if all(_ac._sympy_roots_equal(root, u) for u in user):
                if accepts(_ac._format_quadratic_root(root)):
                    continue
                hits.setdefault(rule.message, rule.id)
    return hits


def diagnose(problem, user_answer, result, *, answer_type, correct_raw, accepts, level, subject, topic='',
             form=None, part=None):
    """A Diagnosis for this check, or None. Never raises: a fault here must not break answer checking.

    ``result`` is the checker's result for ``user_answer`` against ``correct_raw`` (not changed here).
    ``accepts(text)`` says whether the checker would mark ``text`` right for this problem.
    """
    try:
        return _diagnose(problem, user_answer, result, answer_type, correct_raw, accepts, level, subject, topic, form,
                         part)
    except Exception:  # noqa: BLE001 - feedback is a courtesy; the grade itself has already been decided
        return None


def _diagnose(problem, user_answer, result, answer_type, correct_raw, accepts, level, subject, topic, form,
              part=None):
    if level != 'gcse' or subject != 'maths' or not isinstance(result, dict):
        return None
    if result.get('correct'):
        if answer_type == 'bearing':
            typed = re.sub(r'[\s°]', '', _units.strip_units('bearing', str(user_answer or ''))[0])
            expected = str(result.get('normalized_correct') or '')
            if re.fullmatch(r'\d{1,2}', typed) and expected.startswith('0'):
                return Diagnosis('brg.three_figures', MESSAGES['brg.three_figures'], 'note')
        return None
    if (result.get('wrong_form') or result.get('wrong_letter') or result.get('unit_mismatch')
            or result.get('power_tower') or result.get('feedback') == _ac._RECURRING_FEEDBACK):
        return None
    # The pupil's text is read the way the checker read it: unit, %, currency symbol and thousands separator gone
    # (a refusal for a unit that disagrees with the question already returned above), so a typed "£17.50" or
    # "35 cm" reaches the rules as 17.5 or 35.
    text = str(user_answer or '')
    if answer_type in _units.UNIT_ANSWER_TYPES:
        text, _refusal = _units.strip_units(answer_type, _ac._expand_vulgar_fractions(text),
                                            question=_units.problem_question_text(problem), form=form,
                                            multi=part is not None)
    if answer_type in EXPR_TYPES:
        hits = expr_hits(problem, correct_raw, text, accepts)
        if not hits or len(hits) != 1:
            return None
        message_id, rule_id = next(iter(hits.items()))
        return Diagnosis(rule_id, MESSAGES[message_id], 'misconception')
    if answer_type not in DIAGNOSABLE_TYPES:
        return None
    ctx = build_ctx(problem, answer_type, correct_raw, topic, form)
    if ctx is None:
        return None
    if ctx.answer_type in SCALAR_TYPES:
        # A topic rule that knows the question wins over a generic guess at the same typed value; two different
        # topic messages on one value are silence, never a fall back to the generic rules.
        if part is not None and (problem or {}).get('answer_type') == 'number_fields':
            found = part_topic(problem, part, answer_type, correct_raw, topic, form)
            hits = _topic_hits(found[0], found[1], text, accepts, found[2]) if found else {}
        else:
            hits = _topic_hits(ctx, topic_candidates(problem, answer_type, correct_raw, ctx), text, accepts,
                               topic_quiet(problem, answer_type, correct_raw))
        if not hits:
            hits = _scalar_hits(ctx, text, accepts)
    elif ctx.answer_type in PAIR_TYPES:
        hits = pair_topic_hits(problem, ctx, text, accepts, topic) or _pair_hits(ctx, text, accepts)
    else:
        hits = _roots_hits(ctx, text, accepts)
    if len(hits) != 1:
        return None
    message_id, rule_id = next(iter(hits.items()))
    return Diagnosis(rule_id, MESSAGES[message_id], 'misconception')


# ---------------------------------------------------------------------------------------------
# Hint ladder (Phase 3, docs/GCSE_MATHS_HINTS.md section 5)
#
# Rung 1 comes with the first wrong attempt: the recognised slip (the ``feedback`` line) or, when none is
# recognised, a nudge. Rung 2 is the first step of the stored worked solution that does not show the answer, and the
# pupil asks for it. Nothing here is stored: it is built for one response from the session problem and thrown away.
# ---------------------------------------------------------------------------------------------

_TAG_RE = re.compile(r'<[^>]*>')
_STEP_SPLIT_RE = re.compile(r'<br\s*/?>|\n', re.I)
_NUM_TOKEN_RE = re.compile(r'(?:([-\u2212])\s*)?(?<![\d.])(\d+(?:\.\d+)?(?:\s*/\s*\d+)?)')
_FRAC_RE = re.compile(r'\\d?frac\s*\{\s*(\d+)\s*\}\s*\{\s*(\d+)\s*\}')
_THOUSANDS_RE = re.compile(r'(?<=\d),(?=\d{3}(?!\d))')
_UNSAFE_MARKUP = ('$', '<svg', '<pre', '<math')   # maths in \( \) or \[ \] is fine: the page typesets it
HINT_MAX_LEN = 160          # a rung 1 line taken from the problem's own hint
STEP_MAX_LEN = 200          # a rung 2 line


_SUP_RE = re.compile(r'<(sup|sub)\b[^>]*>(.*?)</\1\s*>', re.I | re.S)
_SUPERSCRIPT = str.maketrans('0123456789-−+()n', '⁰¹²³⁴⁵⁶⁷⁸⁹'
                                                     '⁻⁻⁺⁽⁾ⁿ')
_SUBSCRIPT = str.maketrans('0123456789-−+()', '₀₁₂₃₄₅₆₇₈₉'
                                                  '₋₋₊₍₎')


def _script(m):
    """A <sup> or <sub> as plain text: Unicode superscript or subscript characters when it has a form for each
    character (3<sup>3</sup> is 3³), else ^ or _ before it (x<sup>a</sup> is x^a, x<sup>2n</sup> is x^(2n))."""
    inner = re.sub(r'\s+', '', _html.unescape(_TAG_RE.sub('', m.group(2))))
    if not inner:
        return ''
    sup = m.group(1).lower() == 'sup'
    table = _SUPERSCRIPT if sup else _SUBSCRIPT
    if all(ord(ch) in table for ch in inner):
        return inner.translate(table)
    return ('^' if sup else '_') + (inner if len(inner) == 1 else f'({inner})')


def plain_line(html_text):
    """Visible text of a short HTML snippet: tags dropped, entities decoded, spaces collapsed.

    Whole-change review 2026-11-03 (F5): a superscript or subscript keeps its meaning (54 = 2 × 3<sup>3</sup> reads
    "54 = 2 × 3³", not "54 = 2 × 33")."""
    text = _SUP_RE.sub(_script, str(html_text or ''))
    # a line break or block tag becomes a space ("right.<br>Example" must not read "right.Example"); other tags go
    text = re.sub(r'<(?:br|/?p|/?div|/?li)\b[^>]*>', ' ', text, flags=re.I)
    text = _html.unescape(_TAG_RE.sub('', text))
    # house style for a line the page shows as a hint: a spaced dash in generator text becomes a colon (review)
    text = re.sub(r'\s+[\u2014\u2013]\s+', ': ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _frac(token):
    try:
        t = re.sub(r'\s+', '', token)
        if '/' in t:
            a, b = t.split('/', 1)
            return Fraction(int(a), int(b)) if int(b) else None
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        return None


_EXPONENT_DIGITS_RE = re.compile(r'\^\s*\{?\s*[\d.]*$')


def _minus_is_sign(text, at):
    """Is the minus sign at ``at`` the sign of the number after it?

    Whole-change review 2026-11-03 (F4): a spaced minus is a sign too ("5(x − 2)² − 5" holds the term −5, "y = −x − 6"
    the intercept −6). The only minus that is not a sign is a subtraction between two plain numbers ("3 − 2"); a minus
    after a letter, a bracket, a power (², ^2, ^{2}), an operator or at the start is the sign of what follows."""
    before = text[:at].rstrip()
    if not before or not (before[-1].isdigit() and before[-1].isascii() or before[-1] in '.%'):
        return True
    return bool(_EXPONENT_DIGITS_RE.search(before))       # 2(x + 3)^2 - 33: the 2 is a power, not a number


def _number_tokens(text):
    """Every number written in ``text`` (also with thousands commas removed): (value, decimal places, has a minus sign)."""
    out = []
    for variant in {text, _THOUSANDS_RE.sub('', text)}:
        for m in _NUM_TOKEN_RE.finditer(variant):
            tok = m.group(2)
            v = _frac(tok)
            if v is not None:
                places = len(tok.split('.', 1)[1]) if '.' in tok and '/' not in tok else 0
                out.append((v, places, bool(m.group(1)) and _minus_is_sign(variant, m.start())))
    return out


_LIST_RE = re.compile(r'-?\d+(?:\.\d+)?(?:\s*,\s*-?\d+(?:\.\d+)?)+')
_THOUSANDS_KEY_RE = re.compile(r'\d{1,3}(?:,\d{3})+(?:\.\d+)?')
_ASSIGN_RE = re.compile(r'[a-z]\s*=\s*(-?\d+(?:\.\d+)?(?:\s*/\s*\d+)?)')
_TOLERANCE_RE = re.compile(r'(-?\d+(?:\.\d+)?)\s*~\s*\d+(?:\.\d+)?')       # a graph reading: value~tolerance
_ROOTS_TYPES = frozenset({'quadratic_roots'})
_FACTOR_RE = re.compile(r'\(\s*[a-z]\s*[+\-\u2212]\s*(\d+(?:\.\d+)?)\s*\)')   # (x + 4): the root -4 in effect
_FRACTION_PARTS_TYPES = frozenset({'algebraic_fraction'})      # a key stored as numerator|denominator
_LINE_TYPES = frozenset({'linear_equation'})                    # a key stored as gradient|intercept
_ROOT_NOT_VALUE_RE = re.compile(r'(?<![\d.])\d+(?:\.\d+)?(?=[a-z])|\^\s*\{?\s*\d+(?:\.\d+)?\s*\}?|[²³]')
_LINE_RHS_RE = re.compile(r'\by\s*=\s*([^=,;:.]*(?:\.\d[^=,;:.]*)*)')
_BARE_X_RE = re.compile(r'([-\u2212+]?)\s*(?<![\w.^)}\u00b2\u00b3])x(?![\w\u00b2\u00b3^])')


def _bare_letter_terms(text):
    """Number tokens for an x with no number in front, on the right of "y =": "y = \u2212x \u2212 8" holds the gradient \u22121, and
    "y = x + 2" the gradient 1 (whole-change review 2026-11-03, F4)."""
    out = []
    for rhs in _LINE_RHS_RE.findall(text.replace('\\(', ' ').replace('\\)', ' ')):
        for m in _BARE_X_RE.finditer(rhs):
            out.append((Fraction(1), 0, m.group(1) in ('-', '\u2212')))
    return out


def _num_atom(clean, listed=False):
    v = _frac(clean.lstrip('-'))
    if v is None:
        return None
    places = len(clean.split('.', 1)[1]) if '.' in clean and '/' not in clean else 0
    return (v, places, clean.startswith('-'), listed)


def key_atoms(correct_raw, answer_type=None):
    """The parts of the stored key as (numbers, words): numbers are (value, decimal places, negative, listed), words
    are text keys.

    Review (Phase 3): a list key (``6,-3``) gives each number (``listed``), and an assignment key (``y=36``) or a
    graph reading with a tolerance (``23~3.5``) gives its number too, besides the word itself. Whole-change review
    2026-11-03 (F4): a fraction stored as numerator|denominator (``algebraic_fraction``, ``17|2``) gives its value
    17/2 as well, since \\(\\dfrac{17}{2}\\) reads as one number."""
    nums, words = [], []
    parts = [p.strip() for p in re.split(r'[\x1e|]', str(correct_raw or ''))]
    if answer_type in _FRACTION_PARTS_TYPES and len(parts) == 2 \
            and all(re.fullmatch(r'[-−]?\d+', p) for p in parts) and int(parts[1].replace('−', '-')):
        value = Fraction(int(parts[0].replace('−', '-')), int(parts[1].replace('−', '-')))
        nums.append((abs(value), 0, value < 0, False))
    for part in parts:
        part = part.strip()
        if not part:
            continue
        clean = part.replace('−', '-').replace('%', '').replace('°', '').strip()
        m = re.fullmatch(r'-?\d+(?:\.\d+)?(?:\s*/\s*\d+)?', clean)
        if m:
            atom = _num_atom(clean)
            if atom is not None:
                nums.append(atom)
                continue
        if _LIST_RE.fullmatch(clean) and not _THOUSANDS_KEY_RE.fullmatch(clean):
            nums.extend(a for a in (_num_atom(x.strip(), True) for x in clean.split(',')) if a is not None)
        m = _ASSIGN_RE.fullmatch(clean.lower()) or _TOLERANCE_RE.fullmatch(clean)
        if m:
            atom = _num_atom(re.sub(r'\s+', '', m.group(1)))
            if atom is not None:
                nums.append(atom)
        words.append(re.sub(r'\s+', '', part.lower()))
    return nums, words


_LATEX_FRAC_RE = re.compile(r'\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}')
_LATEX_SQRT_RE = re.compile(r'\\sqrt\s*\{([^{}]*)\}')


def algebra_form(text):
    """A loose, comparable form of an expression in a key or in LaTeX: lower case, fractions as a/b, roots as √,
    powers as ^, no spaces, brackets, braces, multiplication signs or LaTeX wrappers. Used only to hold a line back."""
    t = str(text or '').lower().replace('**', '^').replace('−', '-').replace('\\pi', 'π').replace('\\cdot', '*')
    t = t.replace('\\times', '*').replace('×', '*')
    for _ in range(3):
        t = _LATEX_FRAC_RE.sub(r'(\1)/(\2)', t)
        t = _LATEX_SQRT_RE.sub(r'√(\1)', t)
    t = re.sub(r'\\(left|right|boxed|displaystyle|,|;|!|\(|\)|\[|\])', '', t)
    return re.sub(r'[\s{}()*]', '', t)


def reveals_key(text, correct_raw, answer_type=None, given=()):
    """True when ``text`` shows the key: any number equal to a key value (also at the key's own accuracy) or any
    non-numeric key written out (also as LaTeX, compared loosely). Deliberately cautious: a step that merely repeats a
    number from the question and equals the key is dropped too. For roots, a factor such as (x + 4) shows the root
    -4 in effect, so the number in a factor is compared without its sign. ``given`` holds numbers printed in the question,
    with their signs (``question_values``): one item of a list key (``4,5,6,7,8,9`` for 3 < x <= 9) that the question
    already prints with the same sign does not count as shown, unless every item is shown; roots are never exempt."""
    nums, words = key_atoms(correct_raw, answer_type)
    if not nums and not words:
        return True      # no key to compare with: show nothing rather than risk it
    text = _FRAC_RE.sub(r'\1/\2', str(text or ''))
    low = text.lower()
    roots = answer_type in _ROOTS_TYPES
    factors = {Fraction(m) for m in _FACTOR_RE.findall(text)} if roots else set()
    if nums:
        # For roots, a number written as a coefficient (2a, 4ac, 5x) or as a power (x^2) is not a root value.
        tokens = _number_tokens(_ROOT_NOT_VALUE_RE.sub(' ', text) if roots else text)
        if answer_type in _LINE_TYPES:
            tokens += _bare_letter_terms(text)
        given = {Fraction(g) for g in given}
        listed_shown, printed_shown = set(), False
        for v, places, neg in tokens:
            for j, (k, kp, kneg, listed) in enumerate(nums):
                # A negative key is shown only by a number with a minus sign ("3 - 2" does not show minus two). A
                # positive one is shown by its value with either sign (cautious: "these are 2 and -6" gives the root 6
                # in effect), except an item of a list, which is a signed value ("-3 <= n" prints -3, not 3).
                if kneg and not neg or listed and not roots and neg and not kneg:
                    continue
                if not (v == k or (kp and places > kp and round_half_up_fraction(v, kp) == k)):
                    continue
                if not listed:
                    return True
                listed_shown.add(j)
                # Whole-change review 2026-11-03 (F4): an item of a list key that the question prints with the same sign
                # (9 of "3 < x <= 9") does not count as shown, but never for roots, and never once every item is shown.
                if roots or (-k if kneg else k) not in given:
                    return True
                printed_shown = True
        if printed_shown and listed_shown == {j for j, atom in enumerate(nums) if atom[3]}:
            return True
    if factors and any(k in factors for k, _, _, _ in nums):
        return True
    squashed = re.sub(r'\s+', '', low).replace('×', '*').replace('−', '-')
    loose = algebra_form(text)
    for w in words:
        w = w.replace('×', '*').replace('−', '-')
        if not w:
            continue
        if w.isalpha():
            if re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', low):
                return True
        elif w in squashed:
            return True
        else:
            aw = algebra_form(w)
            # an expression key (letters or operators, not a bare number list) written out in any notation
            if len(aw) >= 3 and re.search(r'[a-zπ√^/+=-]', aw) and aw in loose:
                return True
            rhs = aw.split('=', 1)[1] if '=' in aw else ''
            if len(rhs) >= 3 and re.search(r'[a-zπ√]', rhs) and rhs in loose:
                return True
    return False


def round_half_up_fraction(value, places):
    """``value`` (a Fraction) rounded half up to ``places`` decimal places, as a Fraction."""
    scale = 10 ** places
    scaled = value * scale
    floor = scaled.numerator // scaled.denominator
    rem = scaled - floor
    return Fraction(floor + (1 if rem >= Fraction(1, 2) else 0), scale)


def _ok_line(text, limit, correct_raw, answer_type=None, given=()):
    return (bool(text) and len(text) <= limit and not any(m in text.lower() for m in _UNSAFE_MARKUP)
            and not reveals_key(text, correct_raw, answer_type, given))


def question_numbers(problem):
    """Every number printed in the question, as Fractions (signs dropped)."""
    question = plain_line(problem.get('question')) if isinstance(problem, dict) else ''
    return {v for v, _, _ in _number_tokens(question)}


def question_values(problem):
    """Every number printed in the question, as Fractions with their signs (the list-key exemption of
    ``reveals_key``: the question "Solve 2/x = x − 1" prints 1, never −1)."""
    question = plain_line(problem.get('question')) if isinstance(problem, dict) else ''
    return {-v if neg else v for v, _, neg in _number_tokens(question)}


# Whole-change review 2026-11-03 (F6): a step that leaves only a trivial last move gives the answer away in effect.
_LIST_RUN_RE = re.compile(r'(?<![\d.])\d+(?:\.\d+)?(?:\s*,\s*(?:(?:\.\.\.|…)\s*,\s*)?\d+(?:\.\d+)?){2,}')
_PM_RESULT_RE = re.compile(r'[a-z]\s*(?:[+\-−]\s*\d+(?:\.\d+)?\s*)?=\s*(?:\\pm|±)')
_POINT_RE = re.compile(r'\(\s*([-−]?\s*\d+(?:\.\d+)?)\s*,\s*([-−]?\s*\d+(?:\.\d+)?)\s*\)')


def _signed(token):
    t = re.sub(r'\s+', '', token).replace('−', '-')
    return -Fraction(t[1:]) if t.startswith('-') else Fraction(t)


_OUT_OF_RE = re.compile(r'(?<![\d.])(\d+)\b[^.;:\d]{0,40}?\bout\s+of\s+(\d+)\b', re.I)
_COUNT_TAIL_RE = re.compile(r'(?<![\d.^])(\d+)\s+[a-z]+(?:\s+[a-z]+){0,2}\s*[.;]?\s*$', re.I)   # "13 people."
_POWER_RE = re.compile(r'\d+(?:\.\d+)?\s*\^\s*\{?\s*\d+\s*\}?|\d+[²³⁰-⁹]+')    # 2^5 is no count
_TAIL_RELATION_RE = re.compile(
    r'[a-z]\s*(?:<|>|≤|≥|\\lt\b|\\gt\b|\\leq?\b|\\geq?\b|\\leqslant\b|\\geqslant\b)\s*([-−]?\s*\d+(?:\.\d+)?)'
    r'\s*(?:\\\))?\s*[.;]?\s*$')


def answer_in_effect(line, correct_raw, answer_type, q_numbers):
    """True when a step that hides the key still leaves only a trivial move to it (whole-change review 2026-11-03, F6):

    * a fraction key a/b and a step that shows a multiple of a, m·a, while m·b is in the step or the question ("count
      the overlap only: 13 people" in a survey of 63, key 13/63; "18 plus 8, which is 26 people", then 8 of them);
    * a whole-number key K and a list of three or more numbers in the step with K items (K − 1 for a list of five or
      more: the values for n = 1 to 9 when the answer is 10), or adding up to K ("The factors of 48 are 1, 2, ...");
    * a whole-number key and a step that ends in an inequality for a letter at a number within one of it ("so k < −5"
      when the greatest whole k is −6);
    * an algebraic key with a number in front and a step that shows the rest of it ("6 times the integer n(n + 2)").
    """
    text = _FRAC_RE.sub(r'\1/\2', str(line or ''))
    raw = str(correct_raw or '').strip()
    if answer_type in _ROOTS_TYPES:
        return bool(_PM_RESULT_RE.search(text))       # "x + 6 = ±3": the roots are one move away
    if answer_type == 'number_pair':
        try:      # "(−6, 36) and (2, 4)" for the midpoint (−2, 20): only the halving is left
            key = tuple(_signed(p) for p in raw.split('|'))
            points = [(_signed(a), _signed(b)) for a, b in _POINT_RE.findall(text)]
        except (ValueError, ZeroDivisionError):
            return False
        if len(key) != 2:
            return False
        return any(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2) == key for i, p in enumerate(points) for q in points[i + 1:])
    if answer_type == 'algebraic':
        loose = algebra_form(raw)
        m = re.match(r'\d+', loose)
        rest = loose[m.end():] if m else ''
        return len(rest) >= 4 and bool(re.search(r'[a-z]', rest)) and bool(re.search(r'[-+^/]', rest)) \
            and rest in algebra_form(text)
    if answer_type not in ('number', 'fraction', 'linear'):
        return False
    try:
        key = read_key(answer_type, raw)
    except Exception:  # noqa: BLE001 - an odd key simply gets no extra check
        key = None
    if key is None:
        return False
    if answer_type == 'fraction' and key.denominator > 1 and key.numerator:
        a, b = abs(key.numerator), key.denominator
        for m in _OUT_OF_RE.finditer(text):            # "4 red counters out of 8"
            n, d = _frac(m.group(1)), _frac(m.group(2))
            if n is not None and d and n / d == abs(key):
                return True
        m = _COUNT_TAIL_RE.search(text)               # "count the overlap only: 13 people."
        if m:
            n = _frac(m.group(1))
            step = {v for v, _, _ in _number_tokens(_POWER_RE.sub(' ', text[:m.start(1)]))}
            if n is not None and n.denominator == 1 and n:
                n = n.numerator
                # the count is the top (its bottom in the step or the question), or the bottom with its top in the step
                return (n % a == 0 and n // a * b in step | set(q_numbers)) or (n % b == 0 and n // b * a in step)
        return False
    if key.denominator != 1:
        return False
    for run in _LIST_RUN_RE.findall(_THOUSANDS_RE.sub('', text)):
        items = [Fraction(x) for x in re.findall(r'\d+(?:\.\d+)?', run)]
        if len(items) == key or (len(items) >= 5 and len(items) == key - 1) or sum(items) == key:
            return True
    m = _TAIL_RELATION_RE.search(text)
    if m:
        written = re.sub(r'\s+', '', m.group(1)).replace('−', '-')
        bound = _frac(written.lstrip('-'))
        if bound is not None:
            return abs(key - (-bound if written.startswith('-') else bound)) <= 1
    return False


# A step that ends in a worked-out number ("= 28.8", "= £10.0", "= 96 cm²", also inside \( \)).
_RESULT_TAIL_RE = re.compile(
    r'\s*=\s*[£$€]?\s*[-−]?\d[\d,]*(?:\.\d+)?\s*(\\\))?\s*(?:°|%|[a-zA-Z]{1,4}(?:[²³]|/[a-zA-Z]{1,3})?)?\s*(\\\))?'
    r'\s*(?:\([^()]*\))?\s*[.;]?\s*$')     # a note in brackets after the number goes with it
_FIXED_TOTALS = frozenset({Fraction(0), Fraction(90), Fraction(180), Fraction(360)})   # "= 0", "= 180°": facts, not results
_WORKING_RE = re.compile(r'=|[\d)}]\s*[+×÷/\-−]\s*[\d(\\]|\\(?:times|div)')
_CLAUSE_RE = re.compile(r'[.;,:]\s')
NO_STEP_TYPES = frozenset({'proof_steps'})   # the solution is the ordered list itself: any step gives part of it away


def _hide_result(line, question_numbers):
    """Rung 2 shows the method, not the numbers it produces (review, Phase 3): a step that ends in a worked-out
    number that is not printed in the question loses that tail ("11² − 5² = 96" becomes "11² − 5²"). Returns ''
    when nothing that shows a method is left."""
    m = _RESULT_TAIL_RE.search(line)
    if not m:
        return line
    tail_nums = [v for v, _, _ in _number_tokens(m.group(0))]
    if tail_nums and all(v in question_numbers or v in _FIXED_TOTALS for v in tail_nums):
        return line          # a number from the question or an angle or zero total, not a result
    kept = (line[:m.start()].rstrip() + (m.group(1) or m.group(2) or '')).rstrip()
    last = _CLAUSE_RE.split(kept)[-1]       # the clause that lost its number must still show working
    return kept if _WORKING_RE.search(last) else ''


def solution_step(problem, correct_raw):
    """Rung 2: a method step from the stored worked solution that does not give the answer away, or ''.

    The first step that is plain, short, does not repeat the question and does not show the key, with any worked-out
    number at its end hidden (review, Phase 3). If hiding that number leaves no method, there is no rung 2: a later step
    is nearer the answer, so the search never moves on past it. Never for an ordering proof."""
    solution = problem.get('solution') if isinstance(problem, dict) else None
    if not isinstance(solution, str) or not solution or '<pre' in solution:
        return ''
    answer_type = problem.get('answer_type')
    if answer_type in NO_STEP_TYPES:
        return ''
    question = plain_line(problem.get('question'))
    q_squashed = re.sub(r'\s+', '', question)
    q_numbers = question_numbers(problem)
    q_values = question_values(problem)
    for raw in _STEP_SPLIT_RE.split(solution[:4000]):
        if any(m in raw.lower() for m in _UNSAFE_MARKUP):
            continue
        line = plain_line(raw)
        if not line or (len(line) >= 8 and re.sub(r'\s+', '', line) in q_squashed):
            continue
        if line.startswith('='):
            return ''           # the middle of a calculation, not a step that stands on its own
        # The whole step must hide the key first (a step that shows it is never cut down and reused), then any
        # worked-out number at its end is hidden as well.
        if not _ok_line(line, STEP_MAX_LEN, correct_raw, answer_type, q_values):
            continue
        if answer_in_effect(line, correct_raw, answer_type, q_numbers):
            return ''           # only a trivial move is left, and a later step is nearer still: no rung 2
        line = _hide_result(line, q_numbers)
        # a step that introduced the next line ("... with legs 4 cm:") reads as a sentence on its own
        if line.endswith(':'):
            line = line[:-1].rstrip() + '.'
        # once cut down, a line that only repeats the question is no hint either
        return '' if len(line) >= 4 and re.sub(r'\s+', '', line) in q_squashed else line
    return ''


# Rung 2 must add something to the line above it (2026-11-07: "Indices (powers) come before multiplication in
# BIDMAS." then "Indices before multiplication." is the same hint twice). Filler words and plural endings are ignored;
# a number, a symbol or a new idea counts as something new.
_REPEAT_FILLER = frozenset((
    'a an the in of to is are be by for it its on at as and or so this that these those with from into your you then '
    'than also just only each which what when how do does first next now step steps use using remember work out find '
    'calculate start there here will can must should always').split())
_REPEAT_TEX = (('\\left', ''), ('\\right', ''), ('\\times', '×'), ('\\div', '÷'), ('\\sqrt', '√'), ('\\to', '→'),
               ('\\pi', 'π'), ('\\leq', '≤'), ('\\geq', '≥'), ('\\le', '≤'), ('\\ge', '≥'), ('\\dfrac', '/'),
               ('\\frac', '/'), ('−', '-'), ('²', '^2'), ('³', '^3'))
_REPEAT_TOKEN_RE = re.compile(r'[a-z]+|\d+(?:\.\d+)?|[=×÷+\-/^√<>≤≥%°π→]')


def _repeat_tokens(text):
    text = str(text).lower()
    for tex, sym in _REPEAT_TEX:
        text = text.replace(tex, sym)
    text = re.sub(r'\\[a-z]+', ' ', text)
    out = set()
    for tok in _REPEAT_TOKEN_RE.findall(text):
        if tok in _REPEAT_FILLER:
            continue
        if tok.isalpha() and len(tok) > 3 and tok.endswith('s') and not tok.endswith('ss'):
            tok = tok[:-1]          # "indices" and "indice", "powers" and "power" are the same word here
        out.add(tok)
    return out


# After the question's own hint, rung 2 must also bring something concrete (2026-11-07: "Reverse the machine: undo
# the last operation first, then undo the first operation." then "Work backwards, undoing each step in reverse order."
# says the same thing in other words). Concrete means a number the hint does not have (a value from the question or
# one worked from it), an operation the hint does not name ("Subtract \(2w\) from both sides" after "Treat P = 2l + 2w
# like a normal equation"; "subtract" and "−" are the same operation), or a letter, term or named point from the
# question that the hint does not mention. Labels such as "Step 1", "(a)" or "CT4" do not count, nor do names of rules
# and methods ("SOH", "LSF", "SAS").
_STEP_LABEL_RE = re.compile(r'\b(?:step|method|part)\s*\d+\s*:?|(?:^|\s)\(?[a-h]\)\s|\((?:i|ii|iii|iv|v|vi)\)|\bCT\d+\b', re.I)
_OPERATION_WORDS = (
    ('−', r'\b(?:subtract\w*|minus|take away|difference)\b'), ('+', r'\b(?:add|adding|added|plus|sum\w*|total)\b'),
    ('×', r'\b(?:multipl\w*|times|product)\b'), ('÷', r'\b(?:divid\w*|quotient)\b'), ('√', r'\b(?:square roots?|root)\b'))
_NOT_POINTS = frozenset((
    'SOH CAH TOA LSF ASF VSF SF HCF LCM SSS SAS ASA AAS RHS AA BIDMAS BODMAS SDT DMV PFA CT SA FOIL CW ACW BPT LHS').split())


def _concrete(text):
    """(numbers, letters, point names, operations) in a line, for ``adds_nothing``."""
    # a power is an operation, not a value: "LSF²" and "2²" share no number, and "n²" and \(n^2\) are the same
    t = re.sub(r'\^\{?-?\d+\}?|[²³⁴⁻¹]+', ' ^ ', _STEP_LABEL_RE.sub(' ', str(text)))
    low = t.lower()
    ops = {sym for sym, pattern in _OPERATION_WORDS if re.search(pattern, low)}
    ops |= set(re.findall(r'[+×÷√−^]|\\times|\\div|\\sqrt|\\d?frac', t))
    ops |= {'−' for _ in re.findall(r'(?<=[\s\d)])-(?=[\s\d(])', t)}    # a minus sign, not a hyphen ("x-terms")
    ops |= {'÷' for _ in re.findall(r'(?<=[\d)])/|/(?=[\d(])', t)}        # a division, not a unit ("km/h", "N/cm")
    ops = {{'\\times': '×', '\\div': '÷', '\\sqrt': '√', '\\frac': '÷', '\\dfrac': '÷'}.get(o, o) for o in ops}
    letters = set()
    for seg in re.findall(r'\\\((.*?)\\\)', t):           # every letter of a LaTeX term (\(at\) gives a and t)
        letters |= set(re.findall(r'[A-Za-z]', re.sub(r'\\[A-Za-z]+', ' ', seg)))
    t = re.sub(r'\\[A-Za-z]+', ' ', t).replace('\\(', ' ').replace('\\)', ' ')
    numbers = set(re.findall(r'\d+(?:\.\d+)?', t))
    letters |= set(re.findall(r'(?<![A-Za-z])[A-Za-z](?![A-Za-z])', t))
    letters -= {'a', 'A', 'I'}                                # the article and the pronoun, not variables
    points = {w for w in re.findall(r'\b[A-Z]{2,4}\b', t) if w not in _NOT_POINTS}
    return numbers, letters, points, ops


def adds_nothing(first, bigger, *, specific=True, question=''):
    """True when ``bigger`` says nothing that ``first`` has not said: the same line, a near copy or a piece of it, or
    (when ``first`` is the question's own hint, ``specific``) only words, numbers and symbols ``first`` already has,
    or (given the ``question``) nothing concrete that ``first`` lacks (see ``_concrete``). A general line (a slip
    message or a topic nudge) can offer several facts, so a step that picks the one that applies ("The angles add up to
    180°." after "Some pairs of angles are equal, and others add up to 180°.") is kept. The page shows no "Show a
    bigger hint" button when rung 2 is dropped."""
    if not first or not bigger:
        return False
    f = re.sub(r'[^a-z0-9]+', '', str(first).lower())
    b = re.sub(r'[^a-z0-9]+', '', str(bigger).lower())
    if len(b) >= 4 and (b in f or difflib.SequenceMatcher(None, f, b).ratio() >= 0.9):
        return True
    if not specific:
        return False
    tokens = _repeat_tokens(bigger)
    if tokens and tokens <= _repeat_tokens(first):
        return True
    if not question:
        return False
    n1, l1, p1, o1 = _concrete(first)
    n2, l2, p2, o2 = _concrete(bigger)
    _, lq, pq, _ = _concrete(question)
    return not (n2 - n1 or o2 - o1 or (l2 & lq) - l1 or (p2 & pq) - p1)


def nudge_line(problem, family, topic, correct_raw):
    """Rung 1 when no slip is recognised: a family line, else the problem's own hint (if it is short and does not
    show the answer), else the topic line, else the plain default."""
    if family and NUDGES.get(family):
        return NUDGES[family]
    hint = problem.get('hint') if isinstance(problem, dict) else None
    if isinstance(hint, str) and not any(m in hint.lower() for m in _UNSAFE_MARKUP):
        line = plain_line(hint)
        if _ok_line(line, HINT_MAX_LEN, correct_raw, problem.get('answer_type'), question_values(problem)):
            return line
    return NUDGES.get(topic) or NUDGE_DEFAULT


def build_ladder(problem, *, topic, correct_raw, slip=None, slip_text=''):
    """The ``hint`` object for a wrong answer on the practice page.

    ``slip`` is the recognised rule id (its message ``slip_text`` is already the ``feedback`` line), else None. Returns
    ``{'kind', 'rung': 1, 'text'?, 'bigger'}``; ``bigger`` is '' when no step of the solution can be shown, or when the
    step only repeats the first line (``adds_nothing``), and the page then shows no "Show a bigger hint" button.
    """
    raw = str((problem or {}).get('correct_answer_raw') or correct_raw or '')
    record = (problem or {}).get('answer_record')
    family = record.get('f') if isinstance(record, dict) else None
    ladder = {'kind': 'misconception' if slip else 'nudge', 'rung': 1}
    if slip:
        ladder['id'] = slip
    else:
        ladder['text'] = nudge_line(problem, family, topic, raw)
    bigger = solution_step(problem, raw)
    first = slip_text if slip else ladder['text']
    own = (problem or {}).get('hint')
    specific = not slip and isinstance(own, str) and first == plain_line(own)
    question = plain_line((problem or {}).get('question'))
    ladder['bigger'] = '' if adds_nothing(first, bigger, specific=specific, question=question) else bigger
    return ladder


def graded_message(problem, user_answer, *, level, subject, topic=''):
    """The generic slip message for one graded wrong answer, or '' (set work and lesson-quiz results).

    Only generic rules can run there, because the answer record is never stored with a frozen problem or a quiz row.
    A multiple-choice question gets the note of the option the pupil picked (Phase 4, ``option_notes``), if it has one.
    Called only after the answer has been graded; never raises.
    """
    try:
        if level != 'gcse' or subject != 'maths' or not isinstance(problem, dict):
            return ''
        if problem.get('options'):
            from generators.shared import option_notes
            return option_notes.picked_note(problem, user_answer)
        raw = problem.get('correct_answer_raw')
        if raw is None or user_answer is None or not str(user_answer).strip():
            return ''
        answer_type = problem.get('answer_type') or 'number'
        if answer_type not in DIAGNOSABLE_TYPES:
            return ''
        form = _ac.problem_answer_form(problem)

        def check(text):
            return _ac.check_answer(answer_type, str(raw), text, form=form, subject=problem.get('answer_subject'),
                                    labels=problem.get('answer_labels'),
                                    question=_units.problem_question_text(problem))

        result = check(str(user_answer))
        if result.get('correct'):
            return ''
        found = _diagnose(problem, user_answer, result, answer_type, str(raw), lambda t: bool(check(t).get('correct')),
                          level, subject, topic, form)
        return found.message if found is not None and found.kind == 'misconception' else ''
    except Exception:  # noqa: BLE001 - a courtesy line; the grade is already decided
        return ''
