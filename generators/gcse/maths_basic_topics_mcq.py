"""
MCQ banks (15 each) and variants for GCSE maths topics:
bidmas, fdp, multiples_factors, decimals, algebra, surds
"""
import random
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    run_mcq_variant,
)

_LESSON_QUIZ_MIX = (
    ("foundational", 3),
    ("intermediate", 4),
    ("difficult", 3),
)


def _item_to_problem(item, difficulty, topic):
    return make_problem(
        item["q"], item["sol"], item["hint"], difficulty, item["marks"],
        "gcse", "maths", topic,
        options=item["opts"], correct_answer=item["ans"],
    )


def _sample_bank(bank, difficulty, count, seen_questions=None):
    pool = [i for i in bank if i.get("difficulty") == difficulty]
    if seen_questions is not None:
        pool = [i for i in pool if i["q"] not in seen_questions]
    if len(pool) >= count:
        chosen = random.sample(pool, count)
    else:
        chosen = list(pool)
        while len(chosen) < count and pool:
            item = random.choice(pool)
            if item["q"] not in {c["q"] for c in chosen}:
                chosen.append(item)
            elif len({c["q"] for c in chosen}) >= len(pool):
                break
    if seen_questions is not None:
        for item in chosen:
            seen_questions.add(item["q"])
    return chosen


def _mcq_dispatch(bank, topic, difficulty, variant_name=None):
    variants = mcq_variants_from_bank_with_procedural(
        bank, procedural_mcq_for(topic), topic, difficulty
    )
    q, s, hint, marks, opts, ans = run_mcq_variant(variants, variant_name)
    return make_problem(
        q, s, hint, difficulty, marks, "gcse", "maths", topic,
        options=opts, correct_answer=ans,
    )


def _practice_pools(topic):
    from generators.gcse import maths as m
    return {
        "bidmas": {
            "foundational": [
                m.gcse_bidmas_simple, m.gcse_bidmas_brackets, m.gcse_bidmas_power,
                m.gcse_bidmas_proc_subtract_multiply,
                m.gcse_bidmas_proc_divide_add,
                m.gcse_bidmas_proc_two_products,
            ],
            "intermediate": [
                m.gcse_bidmas_mixed, m.gcse_neg_powers, m.gcse_bidmas_with_negatives,
                m.gcse_bidmas_proc_nested_brackets,
                m.gcse_bidmas_proc_power_then_multiply,
                m.gcse_bidmas_proc_bracket_over_divisor,
            ],
            "difficult": [
                m.gcse_bidmas_hard, m.gcse_bidmas_with_negatives, m.gcse_bidmas_brackets,
                m.gcse_bidmas_proc_square_bracket_divide,
                m.gcse_bidmas_proc_nested_inner_bracket,
                m.gcse_bidmas_proc_negative_coefficient,
            ],
        },
        "fdp": {
            "foundational": [
                m.gcse_fdp_decimal_to_percentage, m.gcse_fdp_percentage_to_decimal,
                m.gcse_fdp_decimal_to_fraction,
            ],
            "intermediate": [
                m.gcse_fdp_fraction_to_decimal, m.gcse_fdp_percentage_to_fraction,
                m.gcse_fdp_fraction_to_percentage,
                m.gcse_fdp_fraction_of_amount, m.gcse_fdp_percentage_increase,
                m.gcse_fdp_percentage_decrease, m.gcse_fdp_percentage_change,
                m.gcse_fdp_reverse_percentage, m.gcse_fdp_order_mixed_values,
            ],
            "difficult": [
                m.gcse_fdp_multi_step, m.gcse_fdp_recurring,
                m.gcse_fdp_compound_percentage, m.gcse_fdp_reverse_percentage_two_step,
                m.gcse_fdp_share_in_ratio, m.gcse_fdp_profit_loss_percentage,
                m.gcse_fdp_best_value_comparison, m.gcse_fdp_fraction_word_problem,
            ],
        },
        "multiples_factors": {
            "foundational": [
                m.gcse_mf_find_multiple, m.gcse_mf_find_factor, m.gcse_mf_prime,
            ],
            "intermediate": [
                m.gcse_mf_factor_pairs, m.gcse_mf_hcf, m.gcse_mf_lcm,
                m.gcse_mf_lcm_buses_word, m.gcse_mf_hcf_tiles_word,
                m.gcse_mf_common_factors_count, m.gcse_mf_hcf_using_primes,
                m.gcse_mf_divisibility_digit,
            ],
            "difficult": [
                m.gcse_mf_prime_factors,
                m.gcse_mf_hcf_three_numbers, m.gcse_mf_lcm_three_numbers,
                m.gcse_mf_hcf_lcm_product_rule, m.gcse_mf_number_from_hcf_lcm,
                m.gcse_mf_lcm_from_prime_forms, m.gcse_mf_primes_in_range,
            ],
        },
        "decimals": {
            "foundational": [
                m.gcse_dec_ordering, m.gcse_dec_add_subtract, m.gcse_dec_multiply_power10,
                m.gcse_dec_proc_three_add,
                m.gcse_dec_proc_divide_power10,
                m.gcse_dec_proc_difference,
            ],
            "intermediate": [
                m.gcse_dec_practice_word_total, m.gcse_dec_practice_decimal_to_fraction,
                m.gcse_dec_practice_estimate_product, m.gcse_dec_practice_order_mixed,
                m.gcse_dec_multiply, m.gcse_dec_divide, m.gcse_dec_fraction_to_decimal,
                m.gcse_dec_proc_money_change,
                m.gcse_dec_proc_mean,
                m.gcse_dec_proc_map_scale,
            ],
            "difficult": [
                m.gcse_dec_practice_mixed_ops, m.gcse_dec_practice_bounds,
                m.gcse_dec_practice_word_unit_price, m.gcse_dec_recurring,
                m.gcse_dec_divide, m.gcse_dec_round,
                m.gcse_dec_proc_multi_step_shop,
                m.gcse_dec_proc_bounds_dynamic,
                m.gcse_dec_proc_density,
            ],
        },
        "algebra": {
            "foundational": [
                m.algebra_practice_linear_1, m.algebra_practice_linear_2,
                m.algebra_practice_linear_3,
            ],
            "intermediate": [
                m.algebra_practice_factorise_1, m.algebra_practice_factorise_2,
                m.algebra_practice_factorise_3,
                m.algebra_practice_expand_binomial, m.algebra_practice_linear_both_sides,
                m.algebra_practice_substitution, m.algebra_practice_factorise_hcf,
                m.algebra_practice_change_subject,
            ],
            "difficult": [
                m.algebra_practice_quadratic_1, m.algebra_practice_word_linear,
                m.algebra_practice_simultaneous, m.algebra_practice_expand_mixed,
                m.algebra_practice_brackets_both_sides, m.algebra_practice_consecutive_integers,
                m.algebra_practice_quadratic_2, m.algebra_practice_quadratic_3,
            ],
        },
        "surds": {
            "foundational": [
                m.gcse_surds_simplify, m.gcse_surds_simplify_multiple, m.gcse_surds_add_subtract,
            ],
            "intermediate": [
                m.gcse_surds_expand_simple, m.gcse_surds_rationalise_simple, m.gcse_surds_multiply,
                m.gcse_surds_practice_divide, m.gcse_surds_practice_compare,
                m.gcse_surds_practice_mixed_simplify, m.gcse_surds_practice_double_bracket,
                m.gcse_surds_square_bracket,
            ],
            "difficult": [
                m.gcse_surds_rationalise_compound, m.gcse_surds_exact_area, m.gcse_surds_identity,
                m.gcse_surds_practice_surd_equation, m.gcse_surds_practice_rationalise_binomial_diff,
                m.gcse_surds_practice_between_which_integers, m.gcse_surds_practice_perimeter_exact,
                m.gcse_surds_expand_diff_subtract,
            ],
        },
    }[topic]


def _variants_for_basic_topic(bank, topic, difficulty, mode):
    if mode == "mcq":
        return mcq_variants_from_bank_with_procedural(
            bank, procedural_mcq_for(topic), topic, difficulty
        )
    pools = _practice_pools(topic)
    return select_tier_variants(pools.get(difficulty, []))


# ══════════════════════════════════════════════════════════════════════════════
# BIDMAS (15)
# ══════════════════════════════════════════════════════════════════════════════

_BIDMAS_MCQ_BANK = [
    {"q": "In BIDMAS, which operation is done first in 3 + 4 × 5?",
     "opts": ["A  Addition", "B  Multiplication", "C  Subtraction", "D  Division"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "× before + → 4×5 first. Answer: <strong>B</strong>",
     "hint": "Multiply before add."},
    {"q": "What is 2 + 3 × 4?",
     "opts": ["A  20", "B  14", "C  24", "D  9"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "3×4=12, 2+12=<strong>14</strong>. Answer: B",
     "hint": "BIDMAS: multiply first."},
    {"q": "What is (2 + 3) × 4?",
     "opts": ["A  14", "B  20", "C  9", "D  24"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "Brackets: 5×4=<strong>20</strong>. Answer: B",
     "hint": "Brackets first."},
    {"q": "What does the 'I' in BIDMAS stand for?",
     "opts": ["A  Integers", "B  Indices (powers)", "C  Inverse", "D  Integration"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>Indices</strong> (powers). Answer: B",
     "hint": "I = indices."},
    {"q": "Calculate 2 × 3²",
     "opts": ["A  36", "B  18", "C  12", "D  6"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "3²=9, 2×9=<strong>18</strong>. Answer: B",
     "hint": "Power before multiply."},
    {"q": "−3 + (−5) equals:",
     "opts": ["A  2", "B  −8", "C  8", "D  −2"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "Adding negatives → <strong>−8</strong>. Answer: B",
     "hint": "Number line left."},
    {"q": "−4 × −2 equals:",
     "opts": ["A  −8", "B  8", "C  −6", "D  6"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "Same signs → <strong>positive 8</strong>. Answer: B",
     "hint": "− × − = +."},
    {"q": "What is 10 − 2 × 3?",
     "opts": ["A  24", "B  4", "C  16", "D  6"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": "2×3=6, 10−6=<strong>4</strong>. Answer: B",
     "hint": "Multiply before subtract."},
    {"q": "What is 20 ÷ (2 + 3)?",
     "opts": ["A  10", "B  4", "C  5", "D  2"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": "Bracket 5, 20÷5=<strong>4</strong>. Answer: B",
     "hint": "Bracket then divide."},
    {"q": r"What is \( \left(-2\right)^{2} \)?",
     "opts": ["A  −4", "B  4", "C  −2", "D  2"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": r"\(\left(-2\right)^{2} = (-2)\times(-2) = 4\). Answer: <strong>B</strong>",
     "hint": r"The negative is inside the brackets."},
    {"q": r"What is \( -\left(2\right)^{2} \)?",
     "opts": ["A  4", "B  −4", "C  2", "D  −2"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": r"\(-\left(2^{2}\right) = -(4) = -4\). Answer: <strong>B</strong>",
     "hint": r"Only 2 is squared; the minus stays outside."},
    {"q": "6 + 18 ÷ 3² =",
     "opts": ["A  8", "B  24", "C  4", "D  2"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "3²=9, 18÷9=2, 6+2=<strong>8</strong>. Answer: A",
     "hint": "Indices, divide, add."},
    {"q": "Which is equal to 5 − (−3)?",
     "opts": ["A  2", "B  8", "C  −8", "D  −2"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": "Subtract negative = add: <strong>8</strong>. Answer: B",
     "hint": "Minus a negative."},
    {"q": r"Calculate \( 2 \times \left(5 - 7\right)^{2} + 1 \)",
     "opts": ["A  9", "B  −7", "C  17", "D  5"],
     "ans": "A", "marks": 3, "difficulty": "difficult",
     "sol": r"\(5-7=-2\), \(\left(-2\right)^{2}=4\), \(2\times4+1=9\). Answer: <strong>A</strong>",
     "hint": r"Bracket, then square the bracketed value, then multiply and add."},
    {"q": "3 + 4 × 2 − 1 =",
     "opts": ["A  9", "B  10", "C  13", "D  6"],
     "ans": "B", "marks": 2, "difficulty": "difficult",
     "sol": "4×2=8, 3+8−1=<strong>10</strong>. Answer: B",
     "hint": "× then +/− left to right."},
]


def bidmas_mcq():
    item = random.choice(_BIDMAS_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_bidmas_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_BIDMAS_MCQ_BANK, "bidmas", difficulty, mode)


def gcse_maths_bidmas_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_BIDMAS_MCQ_BANK, "bidmas", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# FDP (15)
# ══════════════════════════════════════════════════════════════════════════════

_FDP_MCQ_BANK = [
    {"q": "0.25 as a percentage is:",
     "opts": ["A  2.5%", "B  25%", "C  0.25%", "D  250%"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "0.25×100=<strong>25%</strong>. Answer: B",
     "hint": "×100 for %."},
    {"q": "50% as a decimal is:",
     "opts": ["A  0.05", "B  0.5", "C  5", "D  50"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "50÷100=<strong>0.5</strong>. Answer: B",
     "hint": "÷100."},
    {"q": "1/4 as a decimal is:",
     "opts": ["A  0.4", "B  0.25", "C  0.14", "D  4"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "1÷4=<strong>0.25</strong>. Answer: B",
     "hint": "Divide top by bottom."},
    {"q": "0.75 as a fraction in simplest form is:",
     "opts": ["A  75/100", "B  3/4", "C  7/5", "D  3/5"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>3/4</strong>. Answer: B",
     "hint": "Simplify 75/100."},
    {"q": "20% as a fraction in simplest form is:",
     "opts": ["A  1/5", "B  2/10", "C  20/100 only", "D  1/20"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "20/100=<strong>1/5</strong>. Answer: A",
     "hint": "Simplify over 100."},
    {"q": "3/5 as a percentage is:",
     "opts": ["A  35%", "B  60%", "C  53%", "D  0.6%"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "3/5=0.6=<strong>60%</strong>. Answer: B",
     "hint": "Decimal then ×100."},
    {"q": "0.125 as a fraction is:",
     "opts": ["A  1/8", "B  1/4", "C  125/10", "D  1/125"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": "<strong>1/8</strong>. Answer: A",
     "hint": "Eighths."},
    {"q": "37.5% as a fraction is:",
     "opts": ["A  3/8", "B  3/4", "C  37/5", "D  3/10"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "37.5%=0.375=<strong>3/8</strong>. Answer: A",
     "hint": "0.375 = three eighths."},
    {"q": "Which is the largest?",
     "opts": ["A  0.4", "B  3/8", "C  38%", "D  2/5"],
     "ans": "C", "marks": 2, "difficulty": "intermediate",
     "sol": "38%=0.38; others smaller. Answer: <strong>C</strong>",
     "hint": "Convert to decimals."},
    {"q": "1/3 as a decimal (to 2 d.p.) is about:",
     "opts": ["A  0.33", "B  0.3 exactly", "C  3.0", "D  0.13"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": "1÷3≈<strong>0.33</strong>. Answer: A",
     "hint": "Recurring decimal."},
    {"q": "Increase 80 by 10% gives:",
     "opts": ["A  88", "B  90", "C  8", "D  108"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "10% of 80=8, 80+8=<strong>88</strong>. Answer: A",
     "hint": "Find 10% then add."},
    {"q": "A price drops from £50 to £40. The percentage decrease is:",
     "opts": ["A  10%", "B  20%", "C  25%", "D  80%"],
     "ans": "B", "marks": 2, "difficulty": "difficult",
     "sol": "10/50=<strong>20%</strong>. Answer: B",
     "hint": "Change ÷ original."},
    {"q": "0.2 recurring (0.2̄) as a fraction is:",
     "opts": ["A  1/5", "B  2/9", "C  2/10", "D  1/9"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "<strong>2/9</strong>. Answer: B",
     "hint": "Single digit repeat → over 9."},
    {"q": "3/8 as a decimal and percentage is:",
     "opts": ["A  0.375 and 37.5%", "B  0.38 and 38%", "C  3.8 and 380%", "D  0.83 and 83%"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>0.375 and 37.5%</strong>. Answer: A",
     "hint": "Divide then ×100."},
    {"q": "Which equals 1/2?",
     "opts": ["A  0.2", "B  50%", "C  0.02", "D  5%"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "1/2=<strong>50%</strong>. Answer: B",
     "hint": "Half."},
    {"q": "Find 3/8 of 240.",
     "opts": ["A  80", "B  90", "C  96", "D  72"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "240÷8=30, 30×3=<strong>90</strong>. Answer: B",
     "hint": "Find one eighth, then multiply by 3."},
    {"q": "£150 is increased by 12%. What is the new amount?",
     "opts": ["A  £162", "B  £168", "C  £178", "D  £180"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "12% of 150=18, 150+18=<strong>£168</strong>. Answer: B",
     "hint": "Find 12% and add."},
    {"q": "A £80 coat is reduced by 25% in a sale. What is the sale price?",
     "opts": ["A  £55", "B  £60", "C  £65", "D  £70"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "25% of 80=20, 80−20=<strong>£60</strong>. Answer: B",
     "hint": "Find the discount, then subtract."},
    {"q": "A value rises from 50 to 65. What is the percentage increase?",
     "opts": ["A  15%", "B  25%", "C  30%", "D  130%"],
     "ans": "C", "marks": 2, "difficulty": "intermediate",
     "sol": "Change=15, (15÷50)×100=<strong>30%</strong>. Answer: C",
     "hint": "Change ÷ original × 100."},
    {"q": "After a 20% discount, the price is £56. What was the original price?",
     "opts": ["A  £67.20", "B  £70", "C  £72", "D  £80"],
     "ans": "B", "marks": 3, "difficulty": "intermediate",
     "sol": "56÷0.8=<strong>£70</strong>. Answer: B",
     "hint": "Divide by 0.8 (multiplier after 20% off)."},
    {"q": "£200 is increased by 10% then decreased by 10%. The final amount is:",
     "opts": ["A  £200", "B  £198", "C  £220", "D  £180"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "200×1.1=220, 220×0.9=<strong>£198</strong>. Answer: B",
     "hint": "Apply each change with a multiplier in order."},
    {"q": "Share £165 in the ratio 4:7. How much is the larger share?",
     "opts": ["A  £60", "B  £65", "C  £105", "D  £110"],
     "ans": "C", "marks": 3, "difficulty": "difficult",
     "sol": "11 parts, 165÷11=15, 7×15=<strong>£105</strong>. Answer: C",
     "hint": "Find one part, multiply by 7."},
    {"q": "Bought for £40, sold for £52. The percentage profit is:",
     "opts": ["A  12%", "B  23%", "C  30%", "D  32%"],
     "ans": "C", "marks": 3, "difficulty": "difficult",
     "sol": "Profit=12, (12÷40)×100=<strong>30%</strong>. Answer: C",
     "hint": "Profit ÷ cost × 100."},
    {"q": "420 pupils: 5/12 walk to school. How many do not walk?",
     "opts": ["A  175", "B  245", "C  265", "D  280"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "Walk=175, 420−175=<strong>245</strong>. Answer: B",
     "hint": "Find 5/12 of 420, subtract from total."},
    {"q": "After a 15% increase then a 10% decrease, the price is £103.50. The original price was:",
     "opts": ["A  £90", "B  £95", "C  £100", "D  £115"],
     "ans": "C", "marks": 4, "difficulty": "difficult",
     "sol": "Multiplier=1.15×0.9=1.035, 103.50÷1.035=<strong>£100</strong>. Answer: C",
     "hint": "Divide by the combined multiplier."},
]


def fdp_mcq():
    item = random.choice(_FDP_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_fdp_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_FDP_MCQ_BANK, "fdp", difficulty, mode)


def gcse_maths_fdp_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_FDP_MCQ_BANK, "fdp", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# MULTIPLES & FACTORS (15)
# ══════════════════════════════════════════════════════════════════════════════

_MF_MCQ_BANK = [
    {"q": "Which is a multiple of 7?",
     "opts": ["A  1", "B  21", "C  3", "D  14.5"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "21=7×3. Answer: <strong>B</strong>",
     "hint": "In 7 times table."},
    {"q": "Which is a factor of 24?",
     "opts": ["A  5", "B  6", "C  7", "D  9"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "24÷6=4. Answer: <strong>B</strong>",
     "hint": "Divides exactly."},
    {"q": "The 4th multiple of 5 is:",
     "opts": ["A  9", "B  20", "C  25", "D  15"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "5×4=<strong>20</strong>. Answer: B",
     "hint": "Multiply."},
    {"q": "Which number is prime?",
     "opts": ["A  15", "B  17", "C  21", "D  27"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "17 has factors 1 and 17 only. Answer: <strong>B</strong>",
     "hint": "Exactly two factors."},
    {"q": "Which is NOT a factor of 30?",
     "opts": ["A  6", "B  10", "C  4", "D  15"],
     "ans": "C", "marks": 1, "difficulty": "foundational",
     "sol": "30÷4 not whole. Answer: <strong>C</strong>",
     "hint": "Test division."},
    {"q": "HCF of 12 and 18 is:",
     "opts": ["A  3", "B  6", "C  36", "D  2"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "Largest common factor: <strong>6</strong>. Answer: B",
     "hint": "Greatest shared factor."},
    {"q": "LCM of 4 and 6 is:",
     "opts": ["A  2", "B  12", "C  24", "D  10"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "Smallest in both tables: <strong>12</strong>. Answer: B",
     "hint": "First common multiple."},
    {"q": "24 written as a product of primes is:",
     "opts": ["A  2³ × 3", "B  4 × 6", "C  2 × 12", "D  8 × 3 only"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>2³ × 3</strong>. Answer: A",
     "hint": "Factor tree."},
    {"q": "36 written as a product of primes is:",
     "opts": ["A  2² × 3²", "B  6² only", "C  2 × 18", "D  4 × 9"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>2² × 3²</strong>. Answer: A",
     "hint": "Prime factorisation."},
    {"q": "All prime numbers (except 2) are:",
     "opts": ["A  Even", "B  Odd", "C  Multiples of 3", "D  Square"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": "Except 2, primes are <strong>odd</strong>. Answer: B",
     "hint": "2 is the only even prime."},
    {"q": "HCF of 16 and 24 is:",
     "opts": ["A  4", "B  8", "C  2", "D  48"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>8</strong>. Answer: B",
     "hint": "List factors."},
    {"q": "LCM of 5 and 12 is:",
     "opts": ["A  17", "B  60", "C  30", "D  10"],
     "ans": "B", "marks": 2, "difficulty": "difficult",
     "sol": "5 and 12 coprime → LCM=<strong>60</strong>. Answer: B",
     "hint": "5×12."},
    {"q": "200 as a product of prime factors is:",
     "opts": ["A  2³ × 5²", "B  20 × 10", "C  4 × 50", "D  2 × 100"],
     "ans": "A", "marks": 3, "difficulty": "difficult",
     "sol": "<strong>2³ × 5²</strong>. Answer: A",
     "hint": "200=8×25."},
    {"q": "A factor pair of 20 is:",
     "opts": ["A  2 and 20", "B  4 and 5", "C  3 and 7", "D  1 and 19 only"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "4×5=20. Answer: <strong>B</strong>",
     "hint": "Multiply to 20."},
    {"q": "Why is 33 <strong>not</strong> a prime number?",
     "opts": ["A  It is odd", "B  It is divisible by 3 and 11", "C  It is less than 40", "D  It has exactly two factors"],
     "ans": "B", "marks": 1, "difficulty": "difficult",
     "sol": "33=3×11 so it has more than two factors. Answer: <strong>B</strong>",
     "hint": "Find a factor other than 1 and itself."},
    {"q": "Buses leave every 8 min and 12 min. Both leave at 9:00. When is the next time they leave together?",
     "opts": ["A  9:20", "B  9:24", "C  9:32", "D  9:36"],
     "ans": "B", "marks": 3, "difficulty": "intermediate",
     "sol": "LCM(8,12)=24 min → <strong>9:24</strong>. Answer: B",
     "hint": "Find the LCM of the two intervals."},
    {"q": "A floor is 120 cm by 84 cm. What is the side length of the largest square tile (no gaps)?",
     "opts": ["A  6 cm", "B  12 cm", "C  24 cm", "D  42 cm"],
     "ans": "B", "marks": 3, "difficulty": "intermediate",
     "sol": "HCF(120,84)=<strong>12 cm</strong>. Answer: B",
     "hint": "Largest square tile = HCF of length and width."},
    {"q": "How many factors do 12 and 18 have in common?",
     "opts": ["A  2", "B  3", "C  4", "D  6"],
     "ans": "C", "marks": 2, "difficulty": "intermediate",
     "sol": "Common: 1, 2, 3, 6 → <strong>4</strong>. Answer: C",
     "hint": "List factors of each and count matches."},
    {"q": "HCF of 72 (= 2³×3²) and 120 (= 2³×3×5) is:",
     "opts": ["A  12", "B  24", "C  360", "D  6"],
     "ans": "B", "marks": 3, "difficulty": "intermediate",
     "sol": "Lowest powers: 2³×3=<strong>24</strong>. Answer: B",
     "hint": "Use lowest prime power in each shared prime."},
    {"q": "5_4 is divisible by 6. The missing digit could be:",
     "opts": ["A  1 or 4", "B  2 or 5", "C  0, 3, 6 or 9", "D  7 only"],
     "ans": "C", "marks": 2, "difficulty": "intermediate",
     "sol": "Even (ends 4) and digit sum 9+□ divisible by 3 → <strong>0, 3, 6 or 9</strong>. Answer: C",
     "hint": "Divisible by 6 means divisible by 2 and 3."},
    {"q": "HCF of 24, 36 and 60 is:",
     "opts": ["A  6", "B  12", "C  24", "D  120"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "HCF(24,36)=12, HCF(12,60)=<strong>12</strong>. Answer: B",
     "hint": "Find HCF of two numbers, then with the third."},
    {"q": "LCM of 4, 6 and 10 is:",
     "opts": ["A  20", "B  30", "C  60", "D  120"],
     "ans": "C", "marks": 3, "difficulty": "difficult",
     "sol": "LCM(4,6)=12, LCM(12,10)=<strong>60</strong>. Answer: C",
     "hint": "Build LCM step by step."},
    {"q": "HCF of 14 and 35 is 7 and LCM is 70. Does 7 × 70 = 14 × 35?",
     "opts": ["A  Yes, both equal 490", "B  No", "C  Yes, both equal 245", "D  Only for prime numbers"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "7×70=490, 14×35=490 → <strong>Yes</strong>. Answer: A",
     "hint": "HCF × LCM always equals the product of the two numbers."},
    {"q": "HCF is 6, LCM is 72 and one number is 24. The other number is:",
     "opts": ["A  12", "B  18", "C  30", "D  36"],
     "ans": "B", "marks": 4, "difficulty": "difficult",
     "sol": "6×72=432, 432÷24=<strong>18</strong>. Answer: B",
     "hint": "Multiply HCF by LCM, divide by the known number."},
    {"q": "LCM of 12 (= 2²×3) and 18 (= 2×3²) is:",
     "opts": ["A  6", "B  18", "C  36", "D  216"],
     "ans": "C", "marks": 3, "difficulty": "difficult",
     "sol": "Highest powers: 2²×3²=<strong>36</strong>. Answer: C",
     "hint": "Take the highest index of each prime."},
]


def multiples_factors_mcq():
    item = random.choice(_MF_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_multiples_factors_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_MF_MCQ_BANK, "multiples_factors", difficulty, mode)


def gcse_maths_multiples_factors_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_MF_MCQ_BANK, "multiples_factors", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# DECIMALS (15)
# ══════════════════════════════════════════════════════════════════════════════

_DEC_MCQ_BANK = [
    {"q": "Which is the largest?",
     "opts": ["A  0.19", "B  0.9", "C  0.091", "D  0.099"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": (
         "Compare tenths: 0.9 has 9 tenths; the others have 0 or 1 tenth.<br>"
         "<strong>0.9</strong> is largest. Answer: B"
     ),
     "hint": "Line up decimal places — compare the tenths column first, then hundredths if needed."},
    {"q": "3.45 + 1.2 =",
     "opts": ["A  4.65", "B  3.57", "C  4.57", "D  5.65"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": (
         "Line up decimals (write 1.2 as 1.20): 3.45 + 1.20<br>"
         "Hundredths: 5+0=5, tenths: 4+2=6, units: 3+1=4 → <strong>4.65</strong>. Answer: A"
     ),
     "hint": "Align decimal points, pad with zeros, then add column by column from right to left."},
    {"q": "5.6 − 2.34 =",
     "opts": ["A  3.26", "B  3.34", "C  2.26", "D  7.94"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": (
         "Write 5.6 as 5.60. Subtract: 5.60 − 2.34<br>"
         "Hundredths: 0−4 (borrow) → 6, tenths: 5−3=2, units: 5−2=3 → <strong>3.26</strong>. Answer: A"
     ),
     "hint": "Align decimal points, add trailing zeros, subtract column by column (borrow when needed)."},
    {"q": "3.2 × 10 =",
     "opts": ["A  32", "B  0.32", "C  320", "D  3.20"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "×10 moves the decimal point 1 place right: 3.2 → <strong>32</strong>. Answer: A",
     "hint": "Multiplying by 10 shifts every digit one place to the left (decimal point moves right)."},
    {"q": "450 ÷ 100 =",
     "opts": ["A  4.5", "B  45", "C  0.45", "D  4500"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "÷100 moves the decimal point 2 places left: 450. → <strong>4.5</strong>. Answer: A",
     "hint": "Dividing by 100 shifts the decimal point two places to the left."},
    {"q": "1.25 × 100 =",
     "opts": ["A  12.5", "B  125", "C  0.125", "D  1250"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "×100 moves the point 2 places right: 1.25 → <strong>125</strong>. Answer: B",
     "hint": "×100 = move the decimal point two places to the right."},
    {"q": "2.4 × 1.5 =",
     "opts": ["A  3.6", "B  36", "C  3.56", "D  0.36"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": (
         "Remove decimals: 24 × 15 = 360<br>"
         "Both factors have 1 d.p. → answer needs 2 d.p. → <strong>3.6</strong>. Answer: A"
     ),
     "hint": "Multiply as whole numbers, then count total decimal places in both factors."},
    {"q": "4.8 ÷ 0.2 =",
     "opts": ["A  24", "B  2.4", "C  0.24", "D  96"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": (
         "×10 both: 48 ÷ 2<br>"
         "48 ÷ 2 = <strong>24</strong>. Answer: A"
     ),
     "hint": "Multiply dividend and divisor by 10 so the divisor becomes a whole number, then divide."},
    {"q": "3/8 as a decimal is:",
     "opts": ["A  0.375", "B  0.38", "C  0.83", "D  3.8"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": "Divide: 3 ÷ 8 = <strong>0.375</strong>. Answer: A",
     "hint": "Use short division — divide 3 by 8, continuing with remainders × 10 for each decimal digit."},
    {"q": "Round 4.567 to 2 decimal places:",
     "opts": ["A  4.56", "B  4.57", "C  4.6", "D  4.55"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": (
         "3rd decimal digit is 7 (≥ 5) → round the 2nd place up<br>"
         "4.56 → <strong>4.57</strong>. Answer: B"
     ),
     "hint": "Look at the digit after the 2nd decimal place — 5 or more means round up."},
    {"q": "0.3̄ (0.333…) as a fraction is:",
     "opts": ["A  1/3", "B  3/10", "C  33/100", "D  3/9"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": (
         "Let x = 0.333…<br>"
         "10x = 3.333… → 10x − x = 3 → 9x = 3 → x = <strong>1/3</strong>. Answer: A"
     ),
     "hint": (
         "Let x equal the decimal. Multiply by 10 so the digits after the point match, "
         "subtract x to cancel the repeat, then solve."
     )},
    {"q": "1.2 × 0.5 =",
     "opts": ["A  0.6", "B  6", "C  1.7", "D  0.06"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": (
         "12 × 5 = 60; 1 d.p. + 1 d.p. = 2 d.p. → <strong>0.6</strong>. Answer: A"
     ),
     "hint": "Multiply as integers (12 × 5), then put the decimal point back — two places total."},
    {"q": "Order smallest to largest: 0.4, 0.04, 0.44",
     "opts": ["A  0.04, 0.4, 0.44", "B  0.4, 0.04, 0.44", "C  0.44, 0.4, 0.04", "D  0.04, 0.44, 0.4"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": (
         "Pad to 2 d.p.: 0.04, 0.40, 0.44<br>"
         "Compare: <strong>0.04, 0.4, 0.44</strong>. Answer: A"
     ),
     "hint": "Write all numbers to the same number of decimal places, then compare digit by digit."},
    {"q": "7.5 ÷ 0.25 =",
     "opts": ["A  30", "B  3", "C  0.3", "D  300"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": (
         "×100 both (0.25 has 2 d.p.): 750 ÷ 25 = <strong>30</strong>. Answer: A"
     ),
     "hint": "Multiply both numbers by 100 to turn 0.25 into 25, then divide."},
    {"q": "0.08 × 0.5 =",
     "opts": ["A  0.04", "B  0.4", "C  4", "D  0.004"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": (
         "8 × 5 = 40; 2 d.p. + 1 d.p. = 3 d.p. → <strong>0.04</strong>. Answer: A"
     ),
     "hint": "Multiply 8 × 5 = 40, then place the decimal point — three decimal places in total."},
    {"q": "0.625 as a fraction in simplest form is:",
     "opts": ["A  5/8", "B  625/1000", "C  62/100", "D  6/25"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": (
         "0.625 = 625/1000<br>"
         "HCF = 125: 625÷125 = 5, 1000÷125 = 8 → <strong>5/8</strong>. Answer: A"
     ),
     "hint": "Write over 1000 (three decimal places), then cancel the highest common factor."},
    {"q": "A length is 5.3 cm to 1 decimal place. The greatest possible true length is:",
     "opts": ["A  5.34 cm", "B  5.35 cm", "C  5.4 cm", "D  5.25 cm"],
     "ans": "B", "marks": 2, "difficulty": "difficult",
     "sol": (
         "1 d.p. → accuracy ±0.05 cm<br>"
         "Upper bound = 5.3 + 0.05 = <strong>5.35 cm</strong> (not included in interval). Answer: B"
     ),
     "hint": "Add half of the last decimal place (0.05) to get the upper bound."},
    {"q": "2.4 kg costs £7.20. The cost per kilogram is:",
     "opts": ["A  £3.00", "B  £30.00", "C  £0.30", "D  £17.28"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": (
         "Cost per kg = total ÷ mass<br>"
         "£7.20 ÷ 2.4 = <strong>£3.00</strong> per kg. Answer: A"
     ),
     "hint": "Divide the total cost by the number of kilograms to find the price for 1 kg."},
]


def decimals_mcq():
    item = random.choice(_DEC_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_decimals_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_DEC_MCQ_BANK, "decimals", difficulty, mode)


def gcse_maths_decimals_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_DEC_MCQ_BANK, "decimals", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# ALGEBRA (15)
# ══════════════════════════════════════════════════════════════════════════════

_ALG_MCQ_BANK = [
    {"q": "Solve: x + 5 = 12",
     "opts": ["A  x = 7", "B  x = 17", "C  x = 5", "D  x = −7"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "x=<strong>7</strong>. Answer: A",
     "hint": "Subtract 5."},
    {"q": "Solve: 3x = 15",
     "opts": ["A  x = 5", "B  x = 45", "C  x = 12", "D  x = 3"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "x=<strong>5</strong>. Answer: A",
     "hint": "Divide by 3."},
    {"q": "Solve: 2x + 1 = 9",
     "opts": ["A  x = 4", "B  x = 5", "C  x = 8", "D  x = 10"],
     "ans": "A", "marks": 2, "difficulty": "foundational",
     "sol": "2x=8, x=<strong>4</strong>. Answer: A",
     "hint": "Subtract 1, divide 2."},
    {"q": "Expand: 3(x + 2)",
     "opts": ["A  3x + 2", "B  3x + 6", "C  x + 5", "D  3x + 5"],
     "ans": "B", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>3x + 6</strong>. Answer: B",
     "hint": "Multiply each term inside."},
    {"q": "Factorise: 6x + 9",
     "opts": ["A  3(2x + 3)", "B  6(x + 9)", "C  9(6x + 1)", "D  3(2x + 9)"],
     "ans": "A", "marks": 2, "difficulty": "foundational",
     "sol": "HCF 3: <strong>3(2x+3)</strong>. Answer: A",
     "hint": "Take out HCF."},
    {"q": "Simplify: 4a + 3a",
     "opts": ["A  7a", "B  12a", "C  7a²", "D  1a"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>7a</strong>. Answer: A",
     "hint": "Like terms."},
    {"q": "Solve: 5x − 3 = 2x + 6",
     "opts": ["A  x = 3", "B  x = 9", "C  x = 1", "D  x = −3"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "3x=9, x=<strong>3</strong>. Answer: A",
     "hint": "Collect x terms."},
    {"q": "Expand: (x + 3)(x + 2)",
     "opts": ["A  x² + 5x + 6", "B  x² + 6", "C  2x + 5", "D  x² + 5x + 5"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>x² + 5x + 6</strong>. Answer: A",
     "hint": "FOIL."},
    {"q": "Solve x² = 16",
     "opts": ["A  x = 4 only", "B  x = 4 or x = −4", "C  x = 8", "D  x = 2"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "x=±<strong>4</strong>. Answer: B",
     "hint": "Two solutions."},
    {"q": "Factorise: x² − 9",
     "opts": ["A  (x − 3)(x − 3)", "B  (x + 3)(x − 3)", "C  (x − 9)(x + 1)", "D  x(x − 9)"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "Difference of squares: <strong>(x+3)(x−3)</strong>. Answer: B",
     "hint": "a²−b²."},
    {"q": "Solve: x² − 5x + 6 = 0",
     "opts": ["A  x = 2 or x = 3", "B  x = 1 or x = 6", "C  x = −2 or x = −3", "D  x = 5 or x = 6"],
     "ans": "A", "marks": 3, "difficulty": "intermediate",
     "sol": "(x−2)(x−3)=0. Answer: <strong>A</strong>",
     "hint": "Factorise quadratic."},
    {"q": "Make x the subject: y = 2x + 1",
     "opts": ["A  x = (y − 1)/2", "B  x = y/2 − 1", "C  x = 2y + 1", "D  x = y − 1"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "x=<strong>(y−1)/2</strong>. Answer: A",
     "hint": "Rearrange."},
    {"q": "Simplify: 3x² × 2x",
     "opts": ["A  5x³", "B  6x³", "C  6x²", "D  5x²"],
     "ans": "B", "marks": 1, "difficulty": "intermediate",
     "sol": "<strong>6x³</strong>. Answer: B",
     "hint": "Multiply coefficients and indices."},
    {"q": "Solve: 2(x − 4) = 10",
     "opts": ["A  x = 9", "B  x = 5", "C  x = 7", "D  x = 1"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "x−4=5, x=<strong>9</strong>. Answer: A",
     "hint": "Divide by 2 first or expand."},
    {"q": "The nth term 3n + 2 gives:",
     "opts": ["A  5, 8, 11, …", "B  2, 5, 8, …", "C  3, 6, 9, …", "D  5, 7, 9, …"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "n=1→5, n=2→8: <strong>5,8,11…</strong>. Answer: A",
     "hint": "Substitute n=1,2,3."},
    {"q": "Solve: x² = 2x",
     "opts": ["A  x = 0 or x = 2", "B  x = 2 only", "C  x = 0 only", "D  x = 1 or x = 2"],
     "ans": "A", "marks": 3, "difficulty": "difficult",
     "sol": "x(x−2)=0 → x=0 or 2. Answer: <strong>A</strong>",
     "hint": "Rearrange to zero."},
    {"q": "If x = 4, what is 2x² − 3x + 1?",
     "opts": ["A  15", "B  21", "C  25", "D  9"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "2(16)−12+1=<strong>21</strong>. Answer: B",
     "hint": "Substitute x = 4 into the expression."},
    {"q": "Solve simultaneously: x + y = 7 and 2x − y = 2",
     "opts": ["A  x = 3, y = 4", "B  x = 2, y = 5", "C  x = 4, y = 3", "D  x = 5, y = 2"],
     "ans": "A", "marks": 3, "difficulty": "difficult",
     "sol": "Add equations: 3x=9, x=3, y=<strong>4</strong>. Answer: A",
     "hint": "Eliminate y by adding the equations."},
    {"q": "A plumber charges £25 call-out plus £18 per hour. A job costs £97. How many hours?",
     "opts": ["A  3", "B  4", "C  5", "D  6"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "25+18h=97 → 18h=72 → h=<strong>4</strong>. Answer: B",
     "hint": "Form a linear equation and solve."},
]


def algebra_mcq():
    item = random.choice(_ALG_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_algebra_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_ALG_MCQ_BANK, "algebra", difficulty, mode)


def gcse_maths_algebra_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_ALG_MCQ_BANK, "algebra", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# SURDS (15)
# ══════════════════════════════════════════════════════════════════════════════

_SURD_MCQ_BANK = [
    {"q": "√36 simplifies to:",
     "opts": ["A  6", "B  18", "C  3√6", "D  6√6"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "36=6² → <strong>6</strong>. Answer: A",
     "hint": "Perfect square."},
    {"q": "√50 in simplified surd form is:",
     "opts": ["A  5√2", "B  25√2", "C  2√5", "D  10√5"],
     "ans": "A", "marks": 2, "difficulty": "foundational",
     "sol": "√(25×2)=<strong>5√2</strong>. Answer: A",
     "hint": "Largest square factor."},
    {"q": "√12 simplifies to:",
     "opts": ["A  2√3", "B  6", "C  3√2", "D  4√3"],
     "ans": "A", "marks": 1, "difficulty": "foundational",
     "sol": "<strong>2√3</strong>. Answer: A",
     "hint": "4×3."},
    {"q": "√8 + √2 equals:",
     "opts": ["A  √10", "B  3√2", "C  4√2", "D  √6"],
     "ans": "B", "marks": 2, "difficulty": "foundational",
     "sol": "2√2+√2=<strong>3√2</strong>. Answer: B",
     "hint": "Simplify √8 first."},
    {"q": "√18 ÷ √2 equals:",
     "opts": ["A  √9 = 3", "B  √16", "C  √6", "D  9"],
     "ans": "A", "marks": 2, "difficulty": "foundational",
     "sol": "√(18/2)=√9=<strong>3</strong>. Answer: A",
     "hint": "√a÷√b=√(a/b)."},
    {"q": "Rationalise: 1/√2 gives:",
     "opts": ["A  √2/2", "B  2", "C  1/2", "D  √2"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "×√2/√2=<strong>√2/2</strong>. Answer: A",
     "hint": "Multiply top and bottom by √2."},
    {"q": "√3 × √12 equals:",
     "opts": ["A  √15", "B  6", "C  3√2", "D  36"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "√36=<strong>6</strong>. Answer: B",
     "hint": "√a×√b=√(ab)."},
    {"q": "(√5)² equals:",
     "opts": ["A  5", "B  25", "C  √25", "D  10"],
     "ans": "A", "marks": 1, "difficulty": "intermediate",
     "sol": "<strong>5</strong>. Answer: A",
     "hint": "Square cancels root."},
    {"q": "√20 − √5 equals:",
     "opts": ["A  √15", "B  √5", "C  0", "D  3√5"],
     "ans": "B", "marks": 2, "difficulty": "intermediate",
     "sol": "2√5−√5=<strong>√5</strong>. Answer: B",
     "hint": "Simplify √20."},
    {"q": "Which is irrational?",
     "opts": ["A  √4", "B  0.5", "C  √7", "D  3/4"],
     "ans": "C", "marks": 1, "difficulty": "intermediate",
     "sol": "√7 not exact decimal. Answer: <strong>C</strong>",
     "hint": "Non-recurring non-terminating."},
    {"q": "√48 simplifies to:",
     "opts": ["A  4√3", "B  8√6", "C  2√12", "D  6√2"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "<strong>4√3</strong>. Answer: A",
     "hint": "16×3."},
    {"q": "Expand (2 + √3)(2 − √3) equals:",
     "opts": ["A  1", "B  4 − 3", "C  4 + 3", "D  7"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "4−3=<strong>1</strong>. Answer: A",
     "hint": "Difference of squares."},
    {"q": "√75 in simplest form is:",
     "opts": ["A  5√3", "B  15√5", "C  3√25", "D  25√3"],
     "ans": "A", "marks": 2, "difficulty": "difficult",
     "sol": "<strong>5√3</strong>. Answer: A",
     "hint": "25×3."},
    {"q": "1/(√5 − √3) rationalised is best written as:",
     "opts": ["A  (√5 + √3)/2", "B  √5 − √3", "C  2/(√5 − √3)", "D  √2"],
     "ans": "A", "marks": 3, "difficulty": "difficult",
     "sol": "×(√5+√3)/(√5+√3)=(5−3)/(√5−√3)… = <strong>(√5+√3)/2</strong>. Answer: A",
     "hint": "Use conjugate √5+√3."},
    {"q": "√2 × √8 + √18 simplifies to:",
     "opts": ["A  4 + 3√2", "B  7√2", "C  5√2", "D  6"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "4+3√2=<strong>7√2</strong>. Answer: B",
     "hint": "Simplify each surd first."},
    {"q": "Which equals √45?",
     "opts": ["A  9√5", "B  3√5", "C  5√3", "D  15√3"],
     "ans": "B", "marks": 2, "difficulty": "foundational",
     "sol": "<strong>3√5</strong>. Answer: B",
     "hint": "9×5."},
    {"q": "√72 ÷ √8 simplifies to:",
     "opts": ["A  3", "B  √9", "C  6", "D  9"],
     "ans": "A", "marks": 2, "difficulty": "intermediate",
     "sol": "√(72/8)=√9=<strong>3</strong>. Answer: A",
     "hint": "√a÷√b=√(a/b)."},
    {"q": "Solve: √(x + 5) = 4",
     "opts": ["A  x = 9", "B  x = 11", "C  x = 16", "D  x = 21"],
     "ans": "B", "marks": 3, "difficulty": "difficult",
     "sol": "x+5=16 → x=<strong>11</strong>. Answer: B",
     "hint": "Square both sides."},
    {"q": "Between which consecutive integers does √50 lie?",
     "opts": ["A  6 and 7", "B  7 and 8", "C  8 and 9", "D  5 and 6"],
     "ans": "B", "marks": 2, "difficulty": "difficult",
     "sol": "49<50<64 → between <strong>7 and 8</strong>. Answer: B",
     "hint": "Compare with nearby square numbers."},
]


def surds_mcq():
    item = random.choice(_SURD_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


def gcse_maths_surds_variants(difficulty, mode="practice"):
    return _variants_for_basic_topic(_SURD_MCQ_BANK, "surds", difficulty, mode)


def gcse_maths_surds_mcq(difficulty, variant_name=None):
    return _mcq_dispatch(_SURD_MCQ_BANK, "surds", difficulty, variant_name)


# ══════════════════════════════════════════════════════════════════════════════
# Lesson quiz builder (optional per-topic; generic uses generator mcq mode)
# ══════════════════════════════════════════════════════════════════════════════

_TOPIC_MCQ = {
    "bidmas": (bidmas_mcq, _BIDMAS_MCQ_BANK, "bidmas"),
    "fdp": (fdp_mcq, _FDP_MCQ_BANK, "fdp"),
    "multiples_factors": (multiples_factors_mcq, _MF_MCQ_BANK, "multiples_factors"),
    "decimals": (decimals_mcq, _DEC_MCQ_BANK, "decimals"),
    "algebra": (algebra_mcq, _ALG_MCQ_BANK, "algebra"),
    "surds": (surds_mcq, _SURD_MCQ_BANK, "surds"),
}


def build_topic_lesson_quiz(topic_slug):
    """Build 10-question quiz from a basic topic's MCQ bank with 3/4/3 mix."""
    mcq_fn, bank, topic = _TOPIC_MCQ[topic_slug]
    problems = []
    seen_questions = set()
    for difficulty, count in _LESSON_QUIZ_MIX:
        for item in _sample_bank(bank, difficulty, count, seen_questions):
            problems.append(_item_to_problem(item, difficulty, topic))
    random.shuffle(problems)
    return problems[:10]
