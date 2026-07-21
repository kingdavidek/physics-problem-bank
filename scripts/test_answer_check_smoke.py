"""Answer check smoke test — run: python scripts/test_answer_check_smoke.py"""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generators.gcse.algebraic_fractions import (  # noqa: E402
    _af_f_cancel_numeric,
    _af_f_factor_cancel,
    _af_f_multiply,
    _af_problem,
    _af_problem_from_output,
    gcse_algebraic_fractions,
    gcse_algebraic_fractions_variants,
)
from generators.gcse.maths import (  # noqa: E402
    _bidmas_problem,
    _fdp_problem,
    _fdp_problem_from_output,
    _surd_problem,
    _surd_problem_from_output,
    gcse_bidmas_brackets,
    gcse_bidmas_power,
    gcse_bidmas_simple,
    gcse_fdp_decimal_to_fraction,
    gcse_fdp_decimal_to_percentage,
    gcse_fdp_fraction_to_decimal,
    gcse_fdp_share_in_ratio,
    gcse_maths_bidmas,
    gcse_maths_fdp,
    gcse_maths_surds,
    gcse_neg_add_subtract,
    gcse_surds_simplify,
)
from generators.gcse.maths_basic_topics_mcq import (  # noqa: E402
    _practice_pools,
    gcse_maths_bidmas_variants,
    gcse_maths_fdp_variants,
    gcse_maths_surds_variants,
)
from generators.gcse.maths_num_stats_prob_rat import (  # noqa: E402
    _number_found_square_cube,
    _number_problem_from_output,
    _prob_problem_from_output,
    _stats_problem_from_output,
    gcse_number,
    gcse_number_variants,
    gcse_probability,
    gcse_probability_variants,
    gcse_statistics,
    gcse_statistics_variants,
    gcse_ratio_proportion,
    gcse_ratio_proportion_variants,
    _ratio_problem_from_output,
    gcse_graphs,
    gcse_graphs_variants,
    _gr_problem_from_output,
)
from generators.gcse.geometry_angles import (  # noqa: E402
    _geom_problem_from_output,
    gcse_geometry_angles,
    gcse_geometry_angles_variants,
)
from generators.gcse.maths_mensuration import (  # noqa: E402
    _mens_problem_from_output,
    gcse_mensuration,
    gcse_mensuration_variants,
)
from generators.gcse.maths_pythagoras import (  # noqa: E402
    _pyth_problem_from_output,
    gcse_pythagoras,
    gcse_pythagoras_variants,
)
from generators.gcse.maths_compound_measures import (  # noqa: E402
    _cm_problem_from_output,
    gcse_compound_measures,
    gcse_compound_measures_variants,
)
from generators.gcse.maths_bearings import (  # noqa: E402
    _brg_problem_from_output,
    gcse_bearings,
    gcse_bearings_variants,
)
from generators.gcse.sequences import (  # noqa: E402
    _seq_problem_from_output,
    gcse_sequences,
    gcse_sequences_variants,
)
from generators.gcse.cs_data_rep import (  # noqa: E402
    _dr_problem_from_output,
    gcse_data_rep,
    gcse_data_rep_variants,
)
from generators.gcse.cs_algorithms import (  # noqa: E402
    _alg_problem_from_output,
    gcse_algorithms,
    gcse_algorithms_variants,
)
from generators.gcse.cs_computer_systems import (  # noqa: E402
    _cs_problem_from_output,
    gcse_computer_systems,
    gcse_computer_systems_variants,
)
from generators.gcse.cs_computer_networks import (  # noqa: E402
    _net_problem_from_output,
    gcse_computer_networks,
    gcse_computer_networks_variants,
)
from generators.shared.answer_checkers import (  # noqa: E402
    check_answer,
    check_number,
    check_number_fields,
    check_number_list,
    check_number_pair,
    check_power,
    check_ratio,
    check_ratio_exact,
    check_linear_equation,
    check_keyword,
    check_number_estimate,
    check_standard_form,
    check_surd,
    check_pi_multiple,
    check_bearing,
    check_binary,
    check_hex,
    check_fraction,
)
from generators.shared.utils import problem_from_choice_output  # noqa: E402
from app import app  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle):
    r = client.get('/register')
    token = csrf_from(r.data.decode())
    r = client.post(
        '/register',
        data={
            'csrf_token': token,
            'email': email,
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200


BIDMAS_RANDOM_POOLS = {
    'foundational': [
        gcse_bidmas_simple, gcse_bidmas_brackets, gcse_bidmas_power, gcse_neg_add_subtract,
    ],
}


def _bidmas_pool_functions(difficulty):
    from generators.gcse import maths as m

    pools = {
        'foundational': [
            m.gcse_bidmas_simple, m.gcse_bidmas_brackets, m.gcse_bidmas_power,
            m.gcse_neg_add_subtract, m.gcse_neg_multiply_divide,
            m.gcse_bidmas_proc_subtract_multiply, m.gcse_bidmas_proc_divide_add,
            m.gcse_bidmas_proc_two_products,
        ],
        'intermediate': [
            m.gcse_bidmas_mixed, m.gcse_neg_powers, m.gcse_bidmas_with_negatives,
            m.gcse_bidmas_proc_nested_brackets, m.gcse_bidmas_proc_power_then_multiply,
            m.gcse_bidmas_proc_bracket_over_divisor,
        ],
        'difficult': [
            m.gcse_bidmas_hard, m.gcse_bidmas_with_negatives, m.gcse_bidmas_brackets,
            m.gcse_bidmas_proc_square_bracket_divide, m.gcse_bidmas_proc_nested_inner_bracket,
            m.gcse_bidmas_proc_negative_coefficient,
        ],
    }
    return pools[difficulty]


def test_checker_unit():
    ok = check_number('42', '42')
    assert ok['correct'] is True
    assert ok['normalized_user'] == '42'
    assert ok['normalized_correct'] == '42'

    ok = check_number('42', ' 42 ')
    assert ok['correct'] is True

    bad = check_number('42', 'abc')
    assert bad['correct'] is False

    neg = check_number('-5', '−5')
    assert neg['correct'] is True

    via_registry = check_answer('number', '10', '10')
    assert via_registry['correct'] is True


def test_checker_standard_form_unit():
    ok = check_standard_form('3.2|5', '3.2|5')
    assert ok['correct'] is True
    assert ok['normalized_user'] == '3.2|5'

    equiv = check_standard_form('3.2|5', '32|4')
    assert equiv['correct'] is True

    neg = check_standard_form('4.5|-3', '4.5|-3')
    assert neg['correct'] is True

    bad = check_standard_form('3.2|5', '3.2|6')
    assert bad['correct'] is False

    via_registry = check_answer('standard_form', '2.5|-2', '2.5|-2')
    assert via_registry['correct'] is True


def test_checker_number_pair_and_list_unit():
    pair_ok = check_number_pair('28|42', '28|42')
    assert pair_ok['correct'] is True

    pair_bad = check_number_pair('28|42', '28|41')
    assert pair_bad['correct'] is False

    list_ok = check_number_list('0.12,0.45,0.67', '0.12, 0.45, 0.67')
    assert list_ok['correct'] is True

    list_bad = check_number_list('0.12,0.45,0.67', '0.45,0.12,0.67')
    assert list_bad['correct'] is False


def test_checker_power_and_fraction_unit():
    power_ok = check_power('2|12', '2|12')
    assert power_ok['correct'] is True
    assert power_ok['normalized_user'] == '2|12'

    power_bad = check_power('2|12', '2|11')
    assert power_bad['correct'] is False

    frac_ok = check_number('1/16', '1/16')
    assert frac_ok['correct'] is True
    assert frac_ok['normalized_correct'] == '1/16'

    frac_bad = check_number('1/16', '1/8')
    assert frac_bad['correct'] is False

    frac_multi_slash = check_number('1/16', '1/2/8')
    assert frac_multi_slash['correct'] is False

    via_registry = check_answer('power', '3|5', '3|5')
    assert via_registry['correct'] is True


def test_checker_fraction_unit():
    same = check_fraction('3/4', '3/4')
    assert same['correct'] is True
    assert same['normalized_correct'] == '3/4'
    assert same['normalized_user'] == '3/4'

    decimal = check_fraction('3/4', '0.75')
    assert decimal['correct'] is True
    assert decimal['normalized_user'] == '0.75'

    equivalent = check_fraction('3/4', '6/8')
    assert equivalent['correct'] is True
    assert equivalent['normalized_user'] != equivalent['normalized_correct']

    mixed = check_fraction('3/2', '1 1/2')
    assert mixed['correct'] is True
    assert mixed['normalized_user'] == '1 1/2'

    pipe_raw = check_fraction('3|4', '0.75')
    assert pipe_raw['correct'] is True

    bad = check_fraction('3/4', '1/2')
    assert bad['correct'] is False

    invalid = check_fraction('3/4', '1/2/4')
    assert invalid['correct'] is False

    via_registry = check_answer('fraction', '3/4', '0.75')
    assert via_registry['correct'] is True


def test_checker_number_fields_unit():
    ok = check_number_fields('1/2|3|0.25', '2/4|3|1/4')
    assert ok['correct'] is True
    assert ok['normalized_correct'] == '0.5|3|0.25'

    missing = check_number_fields('1/2|3|0.25', '1/2|3')
    assert missing['correct'] is False

    invalid = check_number_fields('1/2|3', '1/2/3|3')
    assert invalid['correct'] is False

    via_registry = check_answer('number_fields', '1/3|2/3', '2/6|4/6')
    assert via_registry['correct'] is True

    mixed = check_number_fields('27|12|22:21', '27|12|44:42')
    assert mixed['correct'] is True
    assert mixed['normalized_correct'] == '27|12|22:21'

    mixed_registry = check_answer('number_fields', '27|12|22:21', '27|12|22:21')
    assert mixed_registry['correct'] is True


def test_checker_ratio_unit():
    ok = check_ratio('3|5', '3:5')
    assert ok['correct'] is True
    assert ok['normalized_user'] == '3:5'

    equiv = check_ratio('3|5', '6:10')
    assert equiv['correct'] is True

    exact = check_ratio_exact('8|12', '8:12')
    assert exact['correct'] is True

    exact_bad = check_ratio_exact('8|12', '2:3')
    assert exact_bad['correct'] is False

    via_registry = check_answer('ratio', '2|3', '4:6')
    assert via_registry['correct'] is True


def test_checker_linear_equation_and_keyword_unit():
    eq = check_linear_equation('3|5', 'y = 3x + 5')
    assert eq['correct'] is True

    eq_colon = check_linear_equation('2:3', 'y=2x-3')
    assert eq_colon['correct'] is False

    pos = check_keyword('positive', 'positive correlation')
    assert pos['correct'] is True

    neg = check_keyword('negative', 'Negative')
    assert neg['correct'] is True


def test_checker_number_estimate_unit():
    ok = check_number_estimate('33~4', '32')
    assert ok['correct'] is True

    edge = check_number_estimate('33~4', '37')
    assert edge['correct'] is True

    bad = check_number_estimate('33~4', '28')
    assert bad['correct'] is False

    via_registry = check_answer('number_estimate', '10~2', '11')
    assert via_registry['correct'] is True


def test_bidmas_variants_expose_raw():
    for fn in BIDMAS_RANDOM_POOLS['foundational']:
        out = fn()
        assert len(out) == 5, fn.__name__
        q, s, hint, marks, raw = out
        assert q and s and hint
        assert isinstance(raw, (int, float))


def test_all_bidmas_practice_variants_return_five_tuple():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for fn in _bidmas_pool_functions(difficulty):
            out = fn()
            assert len(out) == 5, fn.__name__
            q, s, hint, marks, raw = out
            assert q and s and hint
            assert isinstance(raw, (int, float)), fn.__name__


def test_foundational_practice_pool_returns_five_tuple():
    for fn in _practice_pools('bidmas')['foundational']:
        out = fn()
        assert len(out) == 5, fn.__name__


def test_bidmas_generator_payload():
    pilot = _bidmas_problem(gcse_bidmas_simple, 'foundational')
    assert pilot.get('correct_answer_raw') is not None
    assert pilot.get('answer_type') == 'number'

    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for fn in _bidmas_pool_functions(difficulty):
            problem = _bidmas_problem(fn, difficulty)
            assert problem.get('correct_answer_raw') is not None, fn.__name__
            assert problem.get('answer_type') == 'number', fn.__name__


def test_bidmas_variant_queue_always_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_bidmas_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            problem = gcse_maths_bidmas(difficulty, 'practice', variant_name=name)
            assert problem.get('correct_answer_raw') is not None, name
            assert problem.get('answer_type') == 'number', name


FDP_UNGRADED_VARIANTS = {
    'gcse_fdp_multi_step',
    'gcse_fdp_recurring',
    'gcse_fdp_order_mixed_values',
    'gcse_fdp_best_value_comparison',
}

FDP_FRACTION_VARIANTS = (
    'gcse_fdp_decimal_to_fraction',
    'gcse_fdp_percentage_to_fraction',
)

FDP_MULTIPART_VARIANTS = (
    'gcse_fdp_share_in_ratio',
)


def _fdp_pool_functions(difficulty):
    from generators.gcse import maths as m

    pools = {
        'foundational': [
            m.gcse_fdp_decimal_to_percentage,
            m.gcse_fdp_percentage_to_decimal,
            m.gcse_fdp_decimal_to_fraction,
            m.gcse_fdp_fraction_to_decimal,
            m.gcse_fdp_percentage_to_fraction,
            m.gcse_fdp_fraction_to_percentage,
        ],
        'intermediate': [
            m.gcse_fdp_fraction_to_decimal,
            m.gcse_fdp_percentage_to_fraction,
            m.gcse_fdp_fraction_to_percentage,
            m.gcse_fdp_fraction_of_amount,
            m.gcse_fdp_percentage_increase,
            m.gcse_fdp_percentage_decrease,
            m.gcse_fdp_percentage_change,
            m.gcse_fdp_reverse_percentage,
            m.gcse_fdp_order_mixed_values,
        ],
        'difficult': [
            m.gcse_fdp_multi_step,
            m.gcse_fdp_recurring,
            m.gcse_fdp_compound_percentage,
            m.gcse_fdp_reverse_percentage_two_step,
            m.gcse_fdp_share_in_ratio,
            m.gcse_fdp_profit_loss_percentage,
            m.gcse_fdp_best_value_comparison,
            m.gcse_fdp_fraction_word_problem,
        ],
    }
    return pools.get(difficulty, pools['foundational'])


def test_fdp_graded_variants_return_five_tuple():
    import generators.gcse.maths as m

    for fn in _fdp_pool_functions('foundational') + _fdp_pool_functions('intermediate'):
        if fn.__name__ in FDP_UNGRADED_VARIANTS:
            continue
        out = fn()
        assert len(out) == 5, fn.__name__


def test_fdp_ungraded_variants_remain_four_tuple():
    import generators.gcse.maths as m

    for name in FDP_UNGRADED_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 4, name


def test_fdp_fraction_variants_use_fraction_checker():
    import generators.gcse.maths as m

    for name in FDP_FRACTION_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _fdp_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'fraction', name
        assert problem.get('correct_answer_raw'), name


def test_fdp_multipart_variants_use_number_fields():
    import generators.gcse.maths as m

    for name in FDP_MULTIPART_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _fdp_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name


def test_fdp_generator_payload():
    pilot = _fdp_problem(gcse_fdp_decimal_to_percentage, 'foundational')
    assert pilot.get('correct_answer_raw') is not None
    assert pilot.get('answer_type') == 'number'

    fraction_pilot = _fdp_problem(gcse_fdp_decimal_to_fraction, 'foundational')
    assert fraction_pilot.get('answer_type') == 'fraction'


def test_fdp_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_fdp_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            problem = gcse_maths_fdp(difficulty, 'practice', variant_name=name)
            if name in FDP_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, name
                continue
            assert problem.get('correct_answer_raw') is not None, name


def test_fdp_check_api_fraction():
    problem = gcse_maths_fdp(
        'foundational', 'practice', variant_name='gcse_fdp_decimal_to_fraction'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'fraction'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_fdp_check_api_number():
    problem = gcse_maths_fdp(
        'foundational', 'practice', variant_name='gcse_fdp_decimal_to_percentage'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


SURDS_UNGRADED_VARIANTS = set()

SURDS_ALGEBRAIC_FRACTION_VARIANTS = (
    'gcse_surds_rationalise_simple',
    'gcse_surds_rationalise_compound',
    'gcse_surds_show_that_rationalise',
    'gcse_surds_rationalise_binomial_diff',
    'gcse_surds_practice_rationalise_binomial_diff',
)

SURDS_ALGEBRAIC_VARIANTS = (
    'gcse_surds_identity',
    'gcse_surds_expand_double',
    'gcse_surds_square_bracket',
    'gcse_surds_square_bracket_minus',
)

SURDS_EXPAND_NUMBER_VARIANTS = (
    'gcse_surds_expand_simple',
)

SURDS_SURD_VARIANTS = (
    'gcse_surds_simplify',
    'gcse_surds_simplify_multiple',
    'gcse_surds_add_subtract',
    'gcse_surds_practice_mixed_simplify',
    'gcse_surds_expand_diff_subtract',
    'gcse_surds_practice_perimeter_exact',
)

SURDS_NUMBER_VARIANTS = (
    'gcse_surds_practice_surd_equation',
)

SURDS_MULTIPART_VARIANTS = (
    'gcse_surds_practice_between_which_integers',
)


def test_surds_surd_variants_use_surd_checker():
    import generators.gcse.maths as m

    for name in SURDS_SURD_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _surd_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'surd', name
        assert problem.get('correct_answer_raw'), name


def test_surds_ungraded_variants_remain_four_tuple():
    import generators.gcse.maths as m

    for name in SURDS_UNGRADED_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 4, name
        problem = _surd_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_surds_number_variants_are_graded():
    import generators.gcse.maths as m

    for name in SURDS_NUMBER_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _surd_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number', name


def test_surds_multipart_variants_use_number_fields():
    import generators.gcse.maths as m

    for name in SURDS_MULTIPART_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _surd_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name


def test_surds_algebraic_variants_use_algebraic_checker():
    import generators.gcse.maths as m

    for name in SURDS_ALGEBRAIC_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _surd_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw'), name


def test_surds_expand_simple_uses_number_checker():
    import generators.gcse.maths as m

    out = m.gcse_surds_expand_simple()
    assert len(out) == 5
    problem = _surd_problem_from_output(out, 'intermediate')
    assert problem.get('answer_type') == 'number'
    assert problem.get('correct_answer_raw')


def test_surds_algebraic_fraction_variants_are_graded():
    import generators.gcse.maths as m

    for name in SURDS_ALGEBRAIC_FRACTION_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _surd_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        if name == 'gcse_surds_rationalise_simple':
            assert problem.get('answer_type') in ('algebraic_fraction', 'surd'), name
        elif name == 'gcse_surds_show_that_rationalise':
            assert problem.get('answer_type') in ('algebraic_fraction', 'number'), name
        else:
            assert problem.get('answer_type') == 'algebraic_fraction', name


def test_check_algebraic_fraction_binomial():
    from generators.shared.answer_checkers import check_algebraic_fraction

    raw = 'b|2|4|1|6|5|-'
    assert check_algebraic_fraction(raw, '2(4-√6)|5')['correct'] is True
    assert check_algebraic_fraction(raw, '8-2√6|5')['correct'] is True
    assert check_algebraic_fraction(raw, '(8-2√6)|5')['correct'] is True
    assert check_algebraic_fraction(raw, '16-4√6|10')['correct'] is True
    assert check_algebraic_fraction(raw, '(4-√6)|5')['correct'] is False


def test_check_algebraic_fraction_expanded_binomial():
    from generators.shared.answer_checkers import check_algebraic_fraction

    raw = 'e|6|-3|3|1'
    assert check_algebraic_fraction(raw, '6-3√3')['correct'] is True
    assert check_algebraic_fraction(raw, '6-3√3|1')['correct'] is True
    assert check_algebraic_fraction(raw, '3(2-√3)')['correct'] is True


def test_check_algebraic_fraction_empty_denominator_defaults_to_one():
    from generators.shared.answer_checkers import check_algebraic_fraction

    raw = 'b|3|2|1|3|1|-'
    for user in ('3(2-√3)|', '3(2-√3)|1', '3(2-√3)'):
        assert check_algebraic_fraction(raw, user)['correct'] is True, user


def test_check_algebraic_fraction_two_surds():
    from generators.shared.answer_checkers import check_algebraic_fraction

    raw = 'd|10|18|8'
    assert check_algebraic_fraction(raw, '√18+√10|8')['correct'] is True
    assert check_algebraic_fraction(raw, '√10+√18|8')['correct'] is True
    assert check_algebraic_fraction(raw, '(√18+√10)|8')['correct'] is True
    assert check_algebraic_fraction(raw, '3√2+√10|8')['correct'] is True
    assert check_algebraic_fraction(raw, '√18+√10|4')['correct'] is False
    assert check_algebraic_fraction(raw, '√18+√10')['correct'] is False


def test_surds_rationalise_binomial_diff_intermediate_check_api():
    import generators.gcse.maths as m

    problem = _surd_problem_from_output(
        m.gcse_surds_rationalise_binomial_diff(), 'intermediate'
    )
    assert problem.get('answer_type') == 'algebraic_fraction'
    assert problem['correct_answer_raw'].startswith('d|')

    _, rad1, rad2, denom = problem['correct_answer_raw'].split('|')
    user = f'√{rad1}+√{rad2}|{denom}'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': user,
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic_fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_surds_show_that_rationalise_check_api():
    import generators.gcse.maths as m

    problem = _surd_problem_from_output(m.gcse_surds_show_that_rationalise(), 'difficult')
    assert problem.get('answer_type') == 'algebraic_fraction'
    assert problem['correct_answer_raw'].startswith('e|')

    parts = problem['correct_answer_raw'].split('|')
    int_part, surd_coef, rad, denom = parts[1], parts[2], parts[3], parts[4]
    sc = int(surd_coef)
    op = '+' if sc >= 0 else '-'
    abs_sc = abs(sc)
    surd = f'√{rad}' if abs_sc == 1 else f'{abs_sc}√{rad}'
    user = f'{int_part}{op}{surd}|{denom}'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': user,
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic_fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_surds_rationalise_compound_check_api():
    import generators.gcse.maths as m

    problem = _surd_problem_from_output(m.gcse_surds_rationalise_compound(), 'intermediate')
    assert problem.get('answer_type') == 'algebraic_fraction'
    raw = problem['correct_answer_raw']
    parts = raw.split('|')
    scale, const, rad, denom = parts[1], parts[2], parts[4], parts[5]

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': f'{scale}({const}-√{rad})|{denom}',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic_fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_surds_rationalise_binomial_diff_check_api():
    import generators.gcse.maths as m

    problem = _surd_problem_from_output(
        m.gcse_surds_practice_rationalise_binomial_diff(), 'difficult'
    )
    assert problem.get('answer_type') == 'algebraic_fraction'
    _, rad1, rad2, denom = problem['correct_answer_raw'].split('|')

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': f'√{rad1}+√{rad2}|{denom}',
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic_fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_check_algebraic_fraction_surd():
    from generators.shared.answer_checkers import check_algebraic_fraction

    raw = '3|5|7'
    for user in ('3√5|7', '3√5 / 7', '√5|7'):
        if user == '√5|7':
            continue
        result = check_algebraic_fraction(raw, user)
        assert result['correct'] is True, user

    assert check_algebraic_fraction('3|5|7', '6√5|14')['correct'] is True
    assert check_algebraic_fraction('3|5|7', '3√5|14')['correct'] is False


def test_surds_rationalise_simple_check_api():
    import generators.gcse.maths as m

    problem = None
    for _ in range(40):
        candidate = _surd_problem_from_output(m.gcse_surds_rationalise_simple(), 'intermediate')
        if candidate.get('answer_type') == 'algebraic_fraction':
            problem = candidate
            break
    assert problem is not None

    coef, rad, denom = problem['correct_answer_raw'].split('|')
    user = f'{coef}√{rad}|{denom}' if coef != '1' else f'√{rad}|{denom}'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': user,
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic_fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_check_algebraic_identity():
    from generators.shared.answer_checkers import check_algebraic

    for user in ('a-b', 'a - b', 'a−b', 'A - B'):
        result = check_algebraic('a-b', user)
        assert result['correct'] is True, user
    assert check_algebraic('a-b', 'b-a')['correct'] is False


def test_check_algebraic_surd_binomial():
    from generators.shared.answer_checkers import check_algebraic

    raw = '11|5|3|+'
    for user in ('11+5√3', '11 + 5√3', '5√3+11'):
        result = check_algebraic(raw, user)
        assert result['correct'] is True, user
    assert check_algebraic('25|6|2|-', '25-6√2')['correct'] is True
    assert check_algebraic('25|6|2|-', '25+6√2')['correct'] is False


def test_surds_algebraic_check_api():
    problem = gcse_maths_surds(
        'intermediate', 'practice', variant_name='gcse_surds_identity'
    )
    assert problem.get('answer_type') == 'algebraic'
    assert problem['correct_answer_raw'] == 'a-b'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': 'a - b',
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_surds_compare_uses_choice_buttons():
    from generators.gcse.maths import gcse_surds_practice_compare

    problem = _surd_problem_from_output(gcse_surds_practice_compare(), 'intermediate')
    assert problem.get('options') and len(problem['options']) == 2
    assert problem.get('correct_answer') in ('A', 'B')
    assert problem.get('correct_answer_raw') is None


def test_surds_generator_payload():
    pilot = _surd_problem(gcse_surds_simplify, 'foundational')
    assert pilot.get('correct_answer_raw') is not None
    assert pilot.get('answer_type') == 'surd'


def test_surds_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_surds_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            problem = gcse_maths_surds(difficulty, 'practice', variant_name=name)
            if name in SURDS_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, name
                continue
            if name == 'gcse_surds_practice_compare':
                assert problem.get('correct_answer') in ('A', 'B'), name
                continue
            assert problem.get('correct_answer_raw') is not None, name


def test_surds_check_api():
    problem = gcse_maths_surds(
        'foundational', 'practice', variant_name='gcse_surds_simplify'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'surd'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': f'√{correct}' if '|' not in correct else (
                    f"{correct.split('|')[0]}√{correct.split('|')[1]}"
                ),
                'correct_answer_raw': correct,
                'answer_type': 'surd',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


AF_UNGRADED_VARIANTS = {
    '_af_f_same_denominator_add',
    '_af_f_divide',
    '_af_i_diff_denominator_add',
    '_af_i_difference_of_squares',
    '_af_i_single_fraction_add',
    '_af_i_multiply_two',
    '_af_i_quadratic_cancel',
    '_af_d_add_reciprocal_style',
    '_af_d_subtract_fractions',
}

AF_FRACTION_VARIANTS = (
    '_af_f_cancel_numeric',
    '_af_f_multiply',
)

AF_NUMBER_VARIANTS = (
    '_af_f_factor_cancel',
    '_af_d_solve_simple',
    '_af_d_simplify_nested',
    '_af_d_equation_with_linear_den',
)


def test_af_fraction_variants_use_fraction_checker():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_FRACTION_VARIANTS:
        for _ in range(8):
            out = getattr(af_mod, name)()
            raw = out[4]
            if name in ('_af_f_multiply', '_af_f_cancel_numeric') and isinstance(raw, int):
                continue
            assert len(out) == 5, name
            problem = _af_problem_from_output(out, 'foundational')
            assert problem.get('answer_type') == 'fraction', name
            assert problem.get('correct_answer_raw'), name
            break


def test_af_number_variants_are_graded():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_NUMBER_VARIANTS:
        out = getattr(af_mod, name)()
        assert len(out) == 5, name
        problem = _af_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw'), name


def test_af_ungraded_variants_remain_four_tuple():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_UNGRADED_VARIANTS:
        out = getattr(af_mod, name)()
        assert len(out) == 4, name
        problem = _af_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_af_generator_payload():
    pilot = None
    for _ in range(12):
        candidate = _af_problem(_af_f_cancel_numeric, 'foundational')
        if candidate.get('answer_type') == 'fraction':
            pilot = candidate
            break
    assert pilot is not None
    assert pilot.get('correct_answer_raw') is not None

    number_pilot = _af_problem(_af_f_factor_cancel, 'foundational')
    assert number_pilot.get('answer_type') == 'number'


def test_af_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_algebraic_fractions_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            problem = gcse_algebraic_fractions(
                difficulty, 'practice', variant_name=name
            )
            if name in AF_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, name
                continue
            assert problem.get('correct_answer_raw') is not None, name


def test_af_check_api_fraction():
    problem = None
    for _ in range(12):
        candidate = gcse_algebraic_fractions(
            'foundational', 'practice', variant_name='_af_f_cancel_numeric'
        )
        if candidate.get('answer_type') == 'fraction':
            problem = candidate
            break
    assert problem is not None
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'fraction'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_af_check_api_number():
    problem = gcse_algebraic_fractions(
        'foundational', 'practice', variant_name='_af_f_factor_cancel'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


NUMBER_NUMERIC_VARIANTS = (
    '_number_found_place_value_digit',
    '_number_found_decimal_place_value',
    '_number_found_round_nearest_10_100',
    '_number_found_round_decimal_places',
    '_number_found_significant_figures_simple',
    '_number_found_negative_add_subtract',
    '_number_found_multiply_by_power_10',
    '_number_found_square_cube',
    '_number_found_percentage_of_amount',
    '_number_found_fraction_of_amount',
    '_number_found_estimate_simple',
    '_number_inter_standard_form_to_ordinary',
    '_number_inter_percentage_increase',
    '_number_inter_percentage_decrease',
    '_number_inter_reverse_percentage_increase',
    '_number_inter_reverse_percentage_decrease',
    '_number_inter_repeated_percentage_change',
    '_number_inter_calculator_estimate_fraction',
    '_number_inter_vat_word_problem',
    '_number_inter_calculate_to_sf',
    '_number_diff_compound_interest',
    '_number_diff_depreciation',
    '_number_diff_reverse_compound',
    '_number_diff_fractional_indices',
    '_number_diff_percentage_error',
    '_number_diff_find_index_n',
    '_number_diff_salary_percentage_chain',
)

NUMBER_STANDARD_FORM_VARIANTS = (
    '_number_found_standard_form_large',
    '_number_inter_standard_form_small',
    '_number_inter_standard_form_multiply',
    '_number_inter_standard_form_divide',
    '_number_diff_standard_form_context',
    '_number_diff_standard_form_mixed_operations',
    '_number_diff_sf_population_difference',
)

NUMBER_COMPARE_CHOICE_VARIANTS = (
    '_number_inter_sf_which_larger',
    '_number_diff_best_value',
)

NUMBER_POWER_VARIANTS = (
    '_number_found_indices_multiply',
    '_number_inter_index_division',
    '_number_inter_index_power_of_power',
)

NUMBER_FRACTION_VARIANTS = (
    '_number_diff_negative_indices',
    '_number_diff_zero_negative_combined',
)


def _number_numeric_functions():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    return [getattr(num_mod, name) for name in NUMBER_NUMERIC_VARIANTS]


def test_number_numeric_variants_return_five_tuple():
    for fn in _number_numeric_functions():
        out = fn()
        assert len(out) == 5, fn.__name__
        q, s, hint, marks, raw = out
        assert q and s and hint
        assert isinstance(raw, (int, float)), fn.__name__


def test_number_compare_choice_variants():
    import generators.gcse.maths_num_stats_prob_rat as num_mod
    from generators.gcse.maths import gcse_surds_practice_compare

    for name in NUMBER_COMPARE_CHOICE_VARIANTS:
        fn = getattr(num_mod, name)
        problem = _number_problem_from_output(fn(), 'intermediate')
        assert problem.get('options') and len(problem['options']) == 2, name
        assert problem.get('correct_answer') in ('A', 'B'), name
        assert problem.get('correct_answer_raw') is None, name
        assert 'Which' in problem['question'] or 'better value' in problem['question'].lower(), name
        if name == '_number_inter_sf_which_larger':
            assert '\\(' in problem['question'], name
            assert '\\(' in problem['solution'], name

    surd = problem_from_choice_output(gcse_surds_practice_compare(), 'intermediate', 'gcse', 'maths', 'surds')
    assert surd.get('options') and len(surd['options']) == 2
    assert surd.get('correct_answer') in ('A', 'B')


def test_number_standard_form_variants_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    for name in NUMBER_STANDARD_FORM_VARIANTS:
        fn = getattr(num_mod, name)
        out = fn()
        assert len(out) == 5, name
        problem = _number_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'standard_form', name
        assert '|' in problem.get('correct_answer_raw', ''), name


def test_number_power_variants_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    for name in NUMBER_POWER_VARIANTS:
        fn = getattr(num_mod, name)
        out = fn()
        assert len(out) == 5, name
        problem = _number_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'power', name
        assert '|' in problem.get('correct_answer_raw', ''), name
        assert f'^{{{problem["correct_answer_raw"].split("|")[1]}}}' in problem['solution'], name


def test_number_fraction_variants_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    for name in NUMBER_FRACTION_VARIANTS:
        fn = getattr(num_mod, name)
        out = fn()
        assert len(out) == 5, name
        _, _, _, _, raw = out
        assert isinstance(raw, str) and '/' in raw, name
        problem = _number_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'number', name
        assert '/' in problem.get('correct_answer_raw', ''), name
        assert 'fraction' in (problem.get('answer_format_hint') or '').lower(), name


def test_standard_form_check_api():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '3.2|5',
                'correct_answer_raw': '3.2|5',
                'answer_type': 'standard_form',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True


def test_number_generator_payload():
    pilot = _number_problem_from_output(_number_found_square_cube(), 'foundational')
    assert pilot.get('correct_answer_raw') is not None
    assert pilot.get('answer_type') == 'number'

    for fn in _number_numeric_functions():
        problem = _number_problem_from_output(fn(), 'intermediate')
        assert problem.get('correct_answer_raw') is not None, fn.__name__
        assert problem.get('answer_type') == 'number', fn.__name__


def test_number_variant_queue_graded_when_numeric():
    for fn in _number_numeric_functions():
        name = fn.__name__
        for difficulty in ('foundational', 'intermediate', 'difficult'):
            problem = gcse_number(difficulty, 'practice', variant_name=name)
            assert problem.get('correct_answer_raw') is not None, f'{name}@{difficulty}'
            assert problem.get('answer_type') == 'number', f'{name}@{difficulty}'


def test_number_practice_pool_has_graded_variants():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_number_variants(difficulty, 'practice')
        assert variants, difficulty
        graded = 0
        for fn in variants:
            if len(fn()) >= 5:
                graded += 1
        assert graded >= 1, difficulty


def test_check_api_without_session():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '14',
                'correct_answer_raw': '14',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '13',
                'correct_answer_raw': '14',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['correct'] is False


def test_check_api_with_session_binding():
    problem = _bidmas_problem(gcse_bidmas_simple, 'foundational')
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
                'problem': problem,
            }

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': '99999',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 403, r.data
        assert r.get_json()['code'] == 'session_mismatch'


def test_check_api_number_fields_partial_with_session():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    problem = _ratio_problem_from_output(ratio_mod._ratio_share_three(), 'foundational')
    assert problem.get('answer_type') == 'number_fields'
    parts = problem['correct_answer_raw'].split('|')
    assert len(parts) == 3

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'ratio_proportion',
                'mode': 'practice',
                'difficulty': 'foundational',
                'problem': problem,
            }

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': parts[0],
                'correct_answer_raw': parts[0],
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json()['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': parts[0],
                'correct_answer_raw': '99999',
                'answer_type': 'number',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 403, r.data
        assert r.get_json()['code'] == 'session_mismatch'


def test_number_share_ratio_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    problem = _number_problem_from_output(num_mod._number_inter_share_ratio(), 'intermediate')
    assert problem.get('answer_type') == 'number_pair'
    assert '|' in problem.get('correct_answer_raw', '')
    assert problem.get('answer_labels') and len(problem['answer_labels']) == 2


def test_all_number_practice_variants_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    skip = {'_number_inter_prime_factor_product', '_number_diff_recurring_decimal_fraction'}
    for name in dir(num_mod):
        if not name.startswith('_number_') or name in skip:
            continue
        fn = getattr(num_mod, name)
        if not callable(fn) or name.endswith('_raw') or 'random' in name or name.endswith('_answer'):
            continue
        if name in (
            '_number_fmt', '_number_sf_value', '_number_mcq_options',
            '_number_problem_from_output', '_number_prime_factor_string',
        ):
            continue
        try:
            out = fn()
        except TypeError:
            continue
        if not isinstance(out, tuple) or len(out) < 4:
            continue
        problem = _number_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') or problem.get('options'), name


PROBABILITY_CORE_VARIANTS = (
    '_prob_single_die',
    '_prob_single_bag',
    '_prob_complement',
    '_prob_expected_frequency',
    '_prob_relative_frequency',
    '_prob_mutually_exclusive',
    '_prob_two_coins',
    '_prob_tree_replacement',
    '_prob_tree_no_replacement',
    '_prob_at_least_one',
    '_prob_conditional_simple',
    '_prob_venn_total',
    '_prob_diff_venn_three_clubs',
    '_prob_diff_venn_three_fill_in',
    '_prob_or_not_exclusive',
    '_prob_independent_product',
    '_prob_tree_simple',
    '_prob_tree_different',
    '_prob_tree_at_least_one_colour',
)


PROBABILITY_FRACTION_VARIANTS = (
    '_prob_single_die',
    '_prob_single_bag',
    '_prob_mutually_exclusive',
    '_prob_two_coins',
    '_prob_tree_replacement',
    '_prob_tree_no_replacement',
    '_prob_conditional_simple',
    '_prob_venn_total',
    '_prob_or_not_exclusive',
    '_prob_independent_product',
    '_prob_tree_simple',
    '_prob_tree_different',
    '_prob_tree_at_least_one_colour',
)


def test_probability_fraction_variants_use_fraction_checker():
    import generators.gcse.maths_num_stats_prob_rat as prob_mod

    for name in PROBABILITY_FRACTION_VARIANTS:
        out = getattr(prob_mod, name)()
        assert len(out) == 5, name
        problem = _prob_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'fraction', name
        assert problem.get('correct_answer_raw'), name


def test_probability_core_variants_are_graded():
    import generators.gcse.maths_num_stats_prob_rat as prob_mod

    for name in PROBABILITY_CORE_VARIANTS:
        out = getattr(prob_mod, name)()
        assert len(out) == 5, name
        problem = _prob_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') in (
            'number', 'number_fields', 'fraction'
        ), name


def test_probability_tree_diagrams_use_inline_inputs():
    import generators.gcse.maths_num_stats_prob_rat as prob_mod

    fill_in_cases = (
        prob_mod._prob_tree_replacement(blank=True),
        prob_mod._prob_tree_no_replacement(blank=True),
        prob_mod._prob_tree_simple(blank=True),
        prob_mod._prob_tree_different(blank=True),
        prob_mod._prob_tree_at_least_one_colour(blank=True),
    )
    for out in fill_in_cases:
        problem = _prob_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'fraction', out[0][:40]
        assert '/' in problem.get('correct_answer_raw', '')
        assert 'prob-tree-input' in problem['question']
        assert problem['question'].count('prob-tree-input') == 10

    structure_cases = (
        prob_mod._prob_tree_replacement(structure_only=True),
        prob_mod._prob_tree_no_replacement(structure_only=True),
        prob_mod._prob_tree_different(blank=False),
        prob_mod._prob_tree_at_least_one_colour(blank=False),
    )
    for out in structure_cases:
        problem = _prob_problem_from_output(out, 'intermediate')
        assert 'prob-tree-input' not in problem['question'], out[0][:40]
        assert problem.get('answer_type') == 'fraction'

    venn_cases = (
        prob_mod._prob_diff_venn_three_clubs(),
        prob_mod._prob_diff_venn_three_fill_in(),
    )
    expected_counts = (3, 10)
    for out, expected_count in zip(venn_cases, expected_counts):
        problem = _prob_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields'
        assert len(problem.get('answer_labels') or []) == expected_count
        assert len(problem['correct_answer_raw'].split('|')) == expected_count
        field_types = problem.get('answer_field_types') or []
        if expected_count == 3:
            assert field_types == ['fraction', 'fraction', 'fraction']
        else:
            assert field_types[-2:] == ['fraction', 'fraction']
            assert field_types[:8] == ['number'] * 8


def test_probability_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_probability_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_probability(
                difficulty, 'practice', variant_name=variant.__name__
            )
            assert problem.get('correct_answer_raw'), (
                difficulty, variant.__name__
            )


def test_probability_check_api_accepts_fraction():
    problem = gcse_probability(
        'foundational', 'practice', variant_name='_prob_found_01'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'fraction'

    with app.test_client() as client:
        response = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'probability',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'fraction',
                'user_answer': correct,
            },
            headers={'Accept': 'application/json'},
        )
        assert response.status_code == 200, response.data
        assert response.get_json()['correct'] is True

        response = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '2/4',
                'correct_answer_raw': '1/2',
                'answer_type': 'fraction',
            },
            headers={'Accept': 'application/json'},
        )
        assert response.status_code == 200, response.data
        assert response.get_json()['correct'] is True

        response = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '2/4|3/6|1',
                'correct_answer_raw': '1/2|1/2|1',
                'answer_type': 'number_fields',
            },
            headers={'Accept': 'application/json'},
        )
        assert response.status_code == 200, response.data
        assert response.get_json()['correct'] is True


STATISTICS_CORE_VARIANTS = (
    '_stats_mean_list',
    '_stats_median_list',
    '_stats_mode_list',
    '_stats_range_list',
    '_stats_grouped_midpoint',
    '_stats_freq_mean',
    '_stats_estimated_mean_grouped',
    '_stats_pie_angle',
    '_stats_line_best_fit',
    '_stats_cumulative_frequency',
    '_stats_box_iqr',
    '_stats_bar_read',
    '_stats_hist_density',
)


def test_statistics_core_variants_are_graded():
    import generators.gcse.maths_num_stats_prob_rat as stats_mod

    for name in STATISTICS_CORE_VARIANTS:
        out = getattr(stats_mod, name)()
        assert len(out) == 5, name
        problem = _stats_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') in ('number', 'number_estimate'), name


def test_statistics_multipart_variants_use_number_fields():
    import generators.gcse.maths_num_stats_prob_rat as stats_mod

    multipart_cases = (
        stats_mod._stats_diff_cf_multipart(),
        stats_mod._stats_diff_histogram_multipart(),
    )
    expected_counts = (3, 3)
    for out, expected_count in zip(multipart_cases, expected_counts):
        problem = _stats_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields'
        assert len(problem.get('answer_labels') or []) == expected_count
        assert len(problem['correct_answer_raw'].split('|')) == expected_count


def test_statistics_choice_variants_use_buttons():
    import generators.gcse.maths_num_stats_prob_rat as stats_mod

    for name in ('_stats_scatter_correlation', '_stats_compare_distributions'):
        out = getattr(stats_mod, name)()
        assert len(out) == 5, name
        problem = _stats_problem_from_output(out, 'intermediate')
        assert problem.get('options'), name
        assert problem.get('correct_answer'), name
        assert problem.get('correct_answer_raw') is None, name


def test_statistics_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_statistics_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_statistics(
                difficulty, 'practice', variant_name=variant.__name__
            )
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


RATIO_CORE_VARIANTS = (
    '_ratio_simplify',
    '_ratio_equivalent',
    '_ratio_share_two',
    '_ratio_share_three',
    '_ratio_fraction_of_total',
    '_ratio_three_part_as_fraction',
    '_ratio_find_missing_part',
    '_ratio_unitary_cost',
    '_ratio_recipe_scale',
    '_ratio_scale_map',
    '_ratio_inverse_workers',
    '_ratio_direct_formula',
    '_ratio_inverse_formula',
    '_ratio_convert_units',
    '_ratio_density_style',
)

RATIO_FRACTION_VARIANTS = (
    '_ratio_fraction_of_total',
    '_ratio_three_part_as_fraction',
)


def test_ratio_fraction_variants_use_fraction_checker():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    for name in RATIO_FRACTION_VARIANTS:
        out = getattr(ratio_mod, name)()
        assert len(out) == 5, name
        problem = _ratio_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'fraction', name
        assert problem.get('correct_answer_raw'), name


def test_ratio_core_variants_are_graded():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    for name in RATIO_CORE_VARIANTS:
        out = getattr(ratio_mod, name)()
        assert len(out) == 5, name
        problem = _ratio_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') or problem.get('correct_answer'), name
        if name == '_ratio_best_buy':
            continue
        assert problem.get('answer_type') in (
            'number', 'number_pair', 'number_fields', 'ratio', 'ratio_exact', 'fraction'
        ), name


def test_ratio_fraction_check_api():
    problem = gcse_ratio_proportion(
        'foundational', 'practice', variant_name='_ratio_found_04'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'fraction'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'ratio_proportion',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'fraction',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_ratio_multipart_variants_use_number_fields():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    cases = (
        ratio_mod._ratio_inter_cafe_ingredients(),
        ratio_mod._ratio_diff_merge_classes(),
        ratio_mod._ratio_diff_concert_tickets(),
    )
    for out in cases:
        problem = _ratio_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields'
        assert len(problem.get('answer_labels') or []) == 3


def test_ratio_choice_and_pair_variants():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    choice = _ratio_problem_from_output(ratio_mod._ratio_best_buy(), 'foundational')
    assert choice.get('options') and choice.get('correct_answer')

    pair = _ratio_problem_from_output(ratio_mod._ratio_share_two(), 'foundational')
    assert pair.get('answer_type') == 'number_pair'
    assert len(pair.get('answer_labels') or []) == 2


def test_ratio_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_ratio_proportion_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_ratio_proportion(
                difficulty, 'practice', variant_name=variant.__name__
            )
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_ratio_merge_classes_number_fields_check():
    import generators.gcse.maths_num_stats_prob_rat as ratio_mod

    problem = _ratio_problem_from_output(ratio_mod._ratio_diff_merge_classes(), 'difficult')
    assert problem.get('answer_type') == 'number_fields'
    correct = problem['correct_answer_raw']
    parts = correct.split('|')
    assert len(parts) == 3
    assert ':' in parts[2]

    ok = check_answer('number_fields', correct, correct)
    assert ok['correct'] is True

    a, b = parts[2].split(':')
    user = f"{parts[0]}|{parts[1]}|{int(a)*2}:{int(b)*2}"
    ok_equiv = check_answer('number_fields', correct, user)
    assert ok_equiv['correct'] is True


def test_ratio_proportion_check_api():
    ratio_problem = gcse_ratio_proportion(
        'foundational', 'practice', variant_name='_ratio_found_01'
    )
    assert ratio_problem.get('answer_type') == 'ratio'
    correct_ratio = ratio_problem['correct_answer_raw']

    share_problem = gcse_ratio_proportion(
        'foundational', 'practice', variant_name='_ratio_found_03'
    )
    assert share_problem.get('answer_type') == 'number_pair'
    correct_share = share_problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'ratio_proportion',
                'difficulty': 'foundational',
                'correct_answer_raw': correct_ratio,
                'answer_type': 'ratio',
                'user_answer': correct_ratio.replace('|', ':'),
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'ratio_proportion',
                'difficulty': 'foundational',
                'correct_answer_raw': correct_share,
                'answer_type': 'number_pair',
                'user_answer': correct_share,
            },
        )
        assert r2.status_code == 200
        data2 = r2.get_json()
        assert data2['ok'] is True
        assert data2['correct'] is True


DATA_REP_UNGRADED = (
    '_dr_i6_overflow',
    '_dr_i7_unicode_vs_ascii',
    '_dr_d10_lossy_lossless_compare',
    '_dr_d12_metadata_vs_payload',
)


def test_checker_binary_hex_unit():
    ok_bin = check_binary('0|1101', '1101')
    assert ok_bin['correct'] is True
    assert ok_bin['normalized_user'] == '1101'

    padded = check_binary('8|00010110', '10100110')
    assert padded['correct'] is False

    padded_ok = check_binary('8|00010110', '00010110')
    assert padded_ok['correct'] is True

    ok_hex = check_hex('0|ff', 'FF')
    assert ok_hex['correct'] is True
    assert ok_hex['normalized_user'] == 'FF'

    via_registry = check_answer('hex', '0|2A', '2a')
    assert via_registry['correct'] is True


def test_data_rep_core_variants_are_graded():
    import generators.gcse.cs_data_rep as dr_mod

    pools = (
        dr_mod._FOUNDATIONAL,
        dr_mod._INTERMEDIATE,
        dr_mod._DIFFICULT,
    )
    for pool in pools:
        for fn in pool:
            out = fn()
            problem = _dr_problem_from_output(out, 'intermediate')
            if fn.__name__ in DATA_REP_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__
            assert problem.get('answer_type') in (
                'number', 'binary', 'hex', 'keyword', 'number_fields'
            ), fn.__name__


def test_data_rep_multipart_number_systems():
    import generators.gcse.cs_data_rep as dr_mod

    problem = _dr_problem_from_output(
        dr_mod._dr_d13_multipart_number_systems(), 'difficult'
    )
    assert problem.get('answer_type') == 'number_fields'
    assert len(problem.get('answer_labels') or []) == 2
    assert '\x1e' in problem['correct_answer_raw']
    parts = problem['correct_answer_raw'].split('\x1e')
    assert len(parts) == 2
    assert check_answer('binary', parts[0], parts[0].split('|', 1)[1])['correct'] is True
    assert check_answer('hex', parts[1], parts[1].split('|', 1)[1])['correct'] is True


def test_data_rep_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_data_rep_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            if variant.__name__ in DATA_REP_UNGRADED:
                continue
            problem = gcse_data_rep(
                difficulty, 'practice', variant_name=variant.__name__
            )
            assert problem.get('correct_answer_raw'), (difficulty, variant.__name__)


def test_data_rep_check_api():
    binary_problem = gcse_data_rep(
        'foundational', 'practice', variant_name='_dr_f2_binary_to_denary'
    )
    assert binary_problem.get('answer_type') == 'number'
    correct_denary = binary_problem['correct_answer_raw']

    hex_problem = gcse_data_rep(
        'foundational', 'practice', variant_name='_dr_f4_denary_to_hex'
    )
    assert hex_problem.get('answer_type') == 'hex'
    correct_hex = hex_problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'data_rep',
                'difficulty': 'foundational',
                'correct_answer_raw': correct_denary,
                'answer_type': 'number',
                'user_answer': correct_denary,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        hex_bits = correct_hex.split('|', 1)[1]
        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'data_rep',
                'difficulty': 'foundational',
                'correct_answer_raw': correct_hex,
                'answer_type': 'hex',
                'user_answer': hex_bits,
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


ALGORITHMS_UNGRADED = (
    '_alg_f1_abstraction',
    '_alg_f2_decomposition',
    '_alg_f4_flowchart_symbol',
    '_alg_f10_algorithm_definition',
    '_alg_i1_pseudocode_linear',
    '_alg_i3_binary_next_half',
    '_alg_i4_bubble_after_pass',
    '_alg_i5_merge_concept',
    '_alg_i6_trace_if',
    '_alg_i8_linear_vs_binary',
    '_alg_i9_flowchart_to_pseudo',
    '_alg_d2_bubble_trace',
    '_alg_d6_pseudocode_binary',
    '_alg_d7_identify_sort',
    '_alg_d8_merge_full',
    '_alg_d10_fix_pseudocode',
    '_alg_d11_insertion_pass',
    '_alg_d12_while_condition',
)


def test_algorithms_trace_variants_are_graded():
    import generators.gcse.cs_algorithms as alg_mod

    pools = (alg_mod._FOUNDATIONAL, alg_mod._INTERMEDIATE, alg_mod._DIFFICULT)
    for pool in pools:
        for fn in pool:
            out = fn()
            problem = _alg_problem_from_output(out, 'intermediate')
            if fn.__name__ in ALGORITHMS_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__
            assert problem.get('answer_type') in ('number', 'number_fields'), fn.__name__


def test_algorithms_multipart_numeric_fields():
    import generators.gcse.cs_algorithms as alg_mod

    search = _alg_problem_from_output(
        alg_mod._alg_d13_multipart_search_compare(), 'difficult'
    )
    assert search.get('answer_type') == 'number_fields'
    assert search.get('correct_answer_raw')

    trace = _alg_problem_from_output(
        alg_mod._alg_d14_multipart_trace_table(), 'difficult'
    )
    assert trace.get('answer_type') == 'number_fields'
    assert trace['correct_answer_raw'] == '10'


def test_algorithms_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_algorithms_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            if variant.__name__ in ALGORITHMS_UNGRADED:
                continue
            problem = gcse_algorithms(
                difficulty, 'practice', variant_name=variant.__name__
            )
            assert problem.get('correct_answer_raw'), (difficulty, variant.__name__)


def test_algorithms_check_api():
    problem = gcse_algorithms(
        'foundational', 'practice', variant_name='_alg_f5_pseudocode_output'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'algorithms',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


SYSTEMS_UNGRADED = (
    '_cs_f1_cpu_alu', '_cs_f2_cpu_cu', '_cs_f3_ram_vs_rom', '_cs_f4_rom_use',
    '_cs_f5_fde_order', '_cs_f6_register', '_cs_f7_os_definition',
    '_cs_f8_input_device', '_cs_f9_ssd_hdd', '_cs_f10_embedded',
    '_cs_i1_von_neumann', '_cs_i2_cache_purpose', '_cs_i3_virtual_memory',
    '_cs_i4_os_functions', '_cs_i5_utility_software', '_cs_i6_storage_compare',
    '_cs_i7_clock_cores', '_cs_i8_fetch_step', '_cs_i9_app_vs_system',
    '_cs_i10_secondary_primary', '_cs_d3_embedded_constraints',
    '_cs_d4_optical_storage', '_cs_d5_heat_sink', '_cs_d6_multitasking_os',
    '_cs_d7_hdd_defrag', '_cs_d8_bios_role', '_cs_d9_address_bus',
    '_cs_d10_open_source_os', '_cs_d11_control_bus', '_cs_d12_multi_core',
    '_cs_d13_multipart_cpu_performance', '_cs_d14_multipart_memory',
)

NETWORKS_UNGRADED = (
    '_net_f1_lan', '_net_f2_wan', '_net_f3_client_server', '_net_f4_p2p',
    '_net_f5_star_topology', '_net_f6_router_role', '_net_f7_http',
    '_net_f8_nic', '_net_f9_wifi_wap', '_net_f10_packet',
    '_net_i1_topology_compare', '_net_i2_switch_vs_hub', '_net_i3_dns',
    '_net_i5_mac_vs_ip', '_net_i6_tcp_udp', '_net_i7_email_protocols',
    '_net_i8_https', '_net_i9_cloud', '_net_i10_bus_topology',
    '_net_d1_packet_switching', '_net_d2_firewall', '_net_d3_nat',
    '_net_d4_mesh_topology', '_net_d5_layered', '_net_d6_four_layer_send',
    '_net_d7_bandwidth_latency', '_net_d8_vlan_scenario', '_net_d9_pop_imap',
    '_net_d10_traceroute_concept', '_net_d11_wireless_security',
    '_net_d12_http_status', '_net_d13_multipart_home_network',
    '_net_d14_multipart_protocols',
)


def test_computer_systems_numeric_variants_are_graded():
    import generators.gcse.cs_computer_systems as cs_mod

    for pool in (cs_mod._FOUNDATIONAL, cs_mod._INTERMEDIATE, cs_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _cs_problem_from_output(out, 'intermediate')
            if fn.__name__ in SYSTEMS_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('answer_type') == 'number', fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_computer_networks_numeric_variants_are_graded():
    import generators.gcse.cs_computer_networks as net_mod

    for pool in (net_mod._FOUNDATIONAL, net_mod._INTERMEDIATE, net_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _net_problem_from_output(out, 'intermediate')
            if fn.__name__ in NETWORKS_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('answer_type') == 'number', fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_computer_systems_networks_variant_queues():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variants, ungraded, gen in (
            (gcse_computer_systems_variants, SYSTEMS_UNGRADED, gcse_computer_systems),
            (gcse_computer_networks_variants, NETWORKS_UNGRADED, gcse_computer_networks),
        ):
            pool = variants(difficulty, 'practice')
            assert pool, difficulty
            for variant in pool:
                if variant.__name__ in ungraded:
                    continue
                problem = gen(difficulty, 'practice', variant_name=variant.__name__)
                assert problem.get('correct_answer_raw'), (difficulty, variant.__name__)


def test_computer_systems_networks_check_api():
    sys_problem = gcse_computer_systems(
        'foundational', 'practice', variant_name='_cs_f11_fde_stage_count'
    )
    net_problem = gcse_computer_networks(
        'intermediate', 'practice', variant_name='_net_i11_http_port'
    )

    with app.test_client() as client:
        for topic, problem in (
            ('computer_systems', sys_problem),
            ('computer_networks', net_problem),
        ):
            r = client.post(
                '/api/v1/problems/check',
                json={
                    'level': 'gcse',
                    'subject': 'cs',
                    'topic': topic,
                    'difficulty': 'foundational',
                    'correct_answer_raw': problem['correct_answer_raw'],
                    'answer_type': 'number',
                    'user_answer': problem['correct_answer_raw'],
                },
            )
            assert r.status_code == 200
            assert r.get_json()['correct'] is True


GRAPHS_CORE_VARIANTS = (
    '_gra_coordinate_quadrant',
    '_gra_substitute_linear',
    '_gra_gradient_two_points',
    '_gra_y_intercept',
    '_gra_equation_from_gradient_intercept',
    '_gra_parallel_gradient',
    '_gra_distance_time_speed',
    '_gra_quadratic_substitute',
    '_gra_root_from_factorised',
    '_gra_midpoint',
    '_gra_line_intersection_simple',
    '_gra_reciprocal_value',
    '_gra_cubic_substitute',
    '_gra_scatter_line_of_best_fit',
)


def test_graphs_core_variants_are_graded():
    import generators.gcse.maths_num_stats_prob_rat as gr_mod

    for name in GRAPHS_CORE_VARIANTS:
        out = getattr(gr_mod, name)()
        assert len(out) == 5, name
        problem = _gr_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') or problem.get('correct_answer'), name


def test_graphs_multipart_and_choice_variants():
    import generators.gcse.maths_num_stats_prob_rat as gr_mod

    line = _gr_problem_from_output(gr_mod._gra_diff_line_equation_multipart(), 'difficult')
    assert line.get('answer_type') == 'number_fields'
    assert line.get('answer_field_types') == ['number', 'number', 'linear_equation']

    scatter = _gr_problem_from_output(gr_mod._gra_diff_scatter_multipart(), 'difficult')
    assert scatter.get('answer_field_types') == ['keyword', 'number_estimate', 'number_estimate']
    scatter_parts = (scatter.get('correct_answer_raw') or '').split('|')
    assert '~' in scatter_parts[1]

    scatter_single = _gr_problem_from_output(gr_mod._gra_scatter_line_of_best_fit(), 'intermediate')
    assert scatter_single.get('answer_type') == 'number_estimate'

    quad = _gr_problem_from_output(gr_mod._gra_diff_quadratic_features_multipart(), 'difficult')
    assert quad.get('answer_type') == 'number_fields'
    assert len(quad.get('answer_labels') or []) == 5

    choice = _gr_problem_from_output(gr_mod._gra_scatter_positive(), 'foundational')
    assert choice.get('options') and choice.get('correct_answer')


def test_graphs_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_graphs_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_graphs(
                difficulty, 'practice', variant_name=variant.__name__
            )
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


GEOMETRY_CORE_VARIANTS = (
    '_geom_found_straight_line',
    '_geom_found_around_point',
    '_geom_found_triangle_sum',
    '_geom_found_isosceles',
    '_geom_found_exterior_angle',
    '_geom_found_quadrilateral',
    '_geom_found_corresponding',
    '_geom_found_alternate',
    '_geom_found_cointerior',
    '_geom_found_polygon_sum',
    '_geom_found_regular_exterior',
    '_geom_found_complementary',
    '_geom_found_equilateral',
    '_geom_inter_regular_polygon_n',
    '_geom_inter_complex_parallel',
    '_geom_inter_angle_at_centre',
    '_geom_inter_same_segment',
    '_geom_inter_tangent_radius',
    '_geom_inter_bearing',
    '_geom_inter_polygon_algebra',
    '_geom_diff_two_tangents',
    '_geom_diff_similar_area',
    '_geom_diff_chord_distance',
    '_geom_diff_reflex_centre',
)

GEOMETRY_MULTIPART_VARIANTS = (
    '_geom_found_vertically_opposite',
    '_geom_found_multistep_lines',
    '_geom_inter_algebraic_straight',
    '_geom_inter_algebraic_triangle',
    '_geom_inter_angle_semicircle',
    '_geom_inter_cyclic_quad',
    '_geom_inter_similar_triangles',
    '_geom_inter_isosceles_parallel',
    '_geom_inter_interior_exterior',
    '_geom_inter_kite_angles',
    '_geom_diff_alternate_segment',
    '_geom_diff_multi_circle',
    '_geom_diff_algebraic_circle',
    '_geom_diff_polygon_algebra',
    '_geom_diff_tangent_chord',
    '_geom_diff_bearing_complex',
    '_geom_diff_inscribed_angles',
)

GEOMETRY_PROOF_VARIANTS = (
    '_geom_diff_prove_triangle_sum',
    '_geom_diff_cyclic_quad_proof',
    '_geom_diff_regular_polygon_proof',
)


def test_geometry_core_variants_are_graded():
    import generators.gcse.geometry_angles as geom_mod

    for name in GEOMETRY_CORE_VARIANTS:
        out = getattr(geom_mod, name)()
        assert len(out) == 5, name
        problem = _geom_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') == 'number', name


def test_geometry_multipart_variants_use_number_fields():
    import generators.gcse.geometry_angles as geom_mod

    for name in GEOMETRY_MULTIPART_VARIANTS:
        out = getattr(geom_mod, name)()
        assert len(out) == 5, name
        problem = _geom_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert labels, name
        assert len(problem['correct_answer_raw'].split('|')) == len(labels), name


def test_geometry_proof_variants_remain_ungraded():
    import generators.gcse.geometry_angles as geom_mod

    for name in GEOMETRY_PROOF_VARIANTS:
        out = getattr(geom_mod, name)()
        assert len(out) == 4, name
        problem = _geom_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw') is None, name


def test_geometry_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_geometry_angles_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_geometry_angles(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in GEOMETRY_PROOF_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_geometry_check_api_accepts_degree_symbol():
    problem = gcse_geometry_angles(
        'foundational', 'practice', variant_name='_geom_found_straight_line'
    )
    correct = problem['correct_answer_raw']
    assert correct is not None

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'geometry_angles',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': f'{correct}°',
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


MENSURATION_CORE_VARIANTS = (
    '_mens_found_rect_area',
    '_mens_found_rect_perimeter',
    '_mens_found_triangle_area',
    '_mens_found_parallelogram_area',
    '_mens_found_trapezium_area',
    '_mens_found_circle_circumference',
    '_mens_found_circle_area',
    '_mens_found_cuboid_volume',
    '_mens_found_cuboid_surface_area',
    '_mens_found_triangular_prism_vol',
    '_mens_found_compound_area_L',
    '_mens_found_area_to_length',
    '_mens_found_unit_conversion_area',
    '_mens_found_density',
    '_mens_found_diameter_from_circumference',
    '_mens_inter_arc_length',
    '_mens_inter_sector_area',
    '_mens_inter_cylinder_volume',
    '_mens_inter_cylinder_surface_area',
    '_mens_inter_cone_volume',
    '_mens_inter_sphere_volume',
    '_mens_inter_sphere_surface_area',
    '_mens_inter_pyramid_volume',
    '_mens_inter_annulus_area',
    '_mens_inter_perimeter_sector',
    '_mens_inter_cone_surface_area',
    '_mens_inter_find_radius_from_area',
    '_mens_inter_rate_fill',
    '_mens_inter_similar_area',
    '_mens_inter_composite_cylinder_hemisphere',
    '_mens_diff_cone_slant_from_height',
    '_mens_diff_sphere_radius_from_volume',
    '_mens_diff_frustum_volume',
    '_mens_diff_hemisphere_cone_surface_area',
    '_mens_diff_sector_minus_triangle',
    '_mens_diff_similar_volume',
    '_mens_diff_density_3d',
    '_mens_diff_sphere_submerged',
    '_mens_diff_prism_composite_cross_section',
    '_mens_diff_find_height_from_volume',
    '_mens_diff_cone_height_from_slant',
    '_mens_diff_surface_area_prism',
)

MENSURATION_MULTIPART_VARIANTS = (
    '_mens_inter_cylinder_tank_multipart',
    '_mens_inter_garden_plot_multipart',
    '_mens_inter_cone_container_multipart',
    '_mens_diff_optimize_box',
    '_mens_diff_silo_multipart',
    '_mens_diff_similar_prisms_multipart',
    '_mens_diff_frustum_tank_multipart',
)

MENSURATION_EXACT_PI_VARIANTS = (
    '_mens_diff_exact_pi_answer',
    '_mens_diff_arc_exact',
)


def test_mensuration_core_variants_are_graded():
    import generators.gcse.maths_mensuration as mens_mod

    for name in MENSURATION_CORE_VARIANTS:
        out = getattr(mens_mod, name)()
        assert len(out) == 5, name
        problem = _mens_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') == 'number', name


def test_mensuration_multipart_variants_use_number_fields():
    import generators.gcse.maths_mensuration as mens_mod

    for name in MENSURATION_MULTIPART_VARIANTS:
        out = getattr(mens_mod, name)()
        assert len(out) == 5, name
        problem = _mens_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert labels, name
        assert len(problem['correct_answer_raw'].split('|')) == len(labels), name


def test_mensuration_exact_pi_variants_use_pi_multiple():
    import generators.gcse.maths_mensuration as mens_mod

    for name in MENSURATION_EXACT_PI_VARIANTS:
        out = getattr(mens_mod, name)()
        assert len(out) == 5, name
        problem = _mens_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'pi_multiple', name
        assert problem.get('correct_answer_raw'), name


def test_mensuration_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_mensuration_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_mensuration(
                difficulty, 'practice', variant_name=variant.__name__
            )
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)
            if variant.__name__ in MENSURATION_EXACT_PI_VARIANTS:
                assert problem.get('answer_type') == 'pi_multiple', variant.__name__


def test_mensuration_pi_multiple_and_check_api():
    import generators.gcse.maths_mensuration as mens_mod
    from generators.shared.answer_checkers import check_answer

    out = mens_mod._mens_diff_arc_exact()
    problem = _mens_problem_from_output(out, 'difficult')
    correct = problem['correct_answer_raw']
    assert problem['answer_type'] == 'pi_multiple'

    ok = check_answer('pi_multiple', correct, correct)
    assert ok['correct'] is True
    ok_pi = check_answer('pi_multiple', correct, f'{correct}π')
    assert ok_pi['correct'] is True
    bad = check_answer('pi_multiple', correct, '999')
    assert bad['correct'] is False

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'mensuration',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'pi_multiple',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_mensuration_fraction_and_check_api():
    import generators.gcse.maths_mensuration as mens_mod

    out = mens_mod._mens_found_triangle_area()
    problem = _mens_problem_from_output(out, 'foundational')
    correct = problem['correct_answer_raw']
    assert '/' in correct or correct.isdigit()

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'mensuration',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


PYTHAGORAS_NUMBER_VARIANTS = (
    '_py_f1_find_hypotenuse',
    '_py_f2_find_shorter_side',
    '_py_f5_ladder_wall',
    '_py_f6_rectangle_diagonal',
    '_py_f7_distance_on_grid',
    '_py_f8_square_diagonal',
    '_py_i1_perimeter',
    '_py_i3_isosceles_height',
    '_py_i4_3d_space_diagonal',
    '_py_i6_coordinate_distance',
    '_py_i7_ladder_slips',
    '_py_i8_cone_slant',
    '_py_d1_composite_area',
)

PYTHAGORAS_KEYWORD_VARIANTS = (
    '_py_f3_is_right_yes',
    '_py_f4_is_right_no',
)

PYTHAGORAS_MULTIPART_VARIANTS = (
    '_py_i2_area_then_side',
    '_py_i5_3d_two_step',
    '_py_d5_two_triangles',
    '_py_d6_roof_truss_multi',
    '_py_d7_coordinate_journey_multi',
    '_py_d8_ladder_slip_multi',
)

PYTHAGORAS_SURD_VARIANTS = (
    '_py_d2_distance_formula',
)

PYTHAGORAS_SURD_MULTIPART_VARIANTS = (
    '_py_d3_3d_diagonal_exact',
)

PYTHAGORAS_UNGRADED_VARIANTS = (
    '_py_d4_pythagoras_proof_check',
)


def test_pythagoras_number_variants_are_graded():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_NUMBER_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 5, name
        problem = _pyth_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') == 'number', name


def test_pythagoras_keyword_variants_are_graded():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_KEYWORD_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 5, name
        problem = _pyth_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'keyword', name
        assert problem.get('correct_answer_raw') in ('yes', 'no'), name


def test_pythagoras_multipart_variants_use_number_fields():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_MULTIPART_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 5, name
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert labels, name
        assert len(problem['correct_answer_raw'].split('|')) == len(labels), name


def test_pythagoras_two_triangles_keyword_field():
    import generators.gcse.maths_pythagoras as pyth_mod
    from generators.shared.variant_utils import variant_is_randomizable

    assert variant_is_randomizable(pyth_mod._py_d5_two_triangles) is True

    seen_keywords = set()
    for _ in range(24):
        out = pyth_mod._py_d5_two_triangles()
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('answer_field_types') == ['keyword', 'number']
        parts = problem['correct_answer_raw'].split('|')
        assert parts[0] in ('both', '1', '2', 'neither')
        assert parts[1]
        seen_keywords.add(parts[0])

    assert len(seen_keywords) >= 2, seen_keywords

    assert check_keyword('both', 'both')['correct'] is True
    assert check_keyword('both', '1 and 2')['correct'] is True
    assert check_keyword('both', '1')['correct'] is False
    assert check_keyword('both', 'neither')['correct'] is False
    assert check_keyword('neither', 'neither')['correct'] is True
    assert check_keyword('neither', 'none')['correct'] is True
    assert check_keyword('1', 'triangle 1')['correct'] is True

    with app.test_client() as client:
        for answer in ('both', 'Both triangles', '1 and 2'):
            response = client.post(
                '/api/v1/problems/check',
                json={
                    'user_answer': answer,
                    'correct_answer_raw': 'both',
                    'answer_type': 'keyword',
                },
                headers={'Accept': 'application/json'},
            )
            assert response.status_code == 200, response.data
            assert response.get_json()['correct'] is True, answer

        response = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '1',
                'correct_answer_raw': 'both',
                'answer_type': 'keyword',
            },
            headers={'Accept': 'application/json'},
        )
        assert response.status_code == 200, response.data
        assert response.get_json()['correct'] is False


def test_pythagoras_surd_variants_use_surd_checker():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_SURD_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 5, name
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'surd', name
        assert problem.get('correct_answer_raw'), name


def test_pythagoras_surd_multipart_variants():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_SURD_MULTIPART_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 5, name
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        field_types = problem.get('answer_field_types') or []
        assert field_types == ['surd', 'number'], name
        raw = problem['correct_answer_raw']
        sep = '\x1e' if '\x1e' in raw else '|'
        assert len(raw.split(sep)) == 2, name


def test_pythagoras_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_pythagoras as pyth_mod

    for name in PYTHAGORAS_UNGRADED_VARIANTS:
        out = getattr(pyth_mod, name)()
        assert len(out) == 4, name
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw') is None, name


def test_pythagoras_distance_formula_graded():
    import generators.gcse.maths_pythagoras as pyth_mod

    out = pyth_mod._py_d2_distance_formula()
    assert len(out) == 5
    problem = _pyth_problem_from_output(out, 'difficult')
    assert problem.get('correct_answer_raw')
    assert problem.get('answer_type') == 'surd'


def test_checker_surd_unit():
    ok = check_surd('113', '√113')
    assert ok['correct'] is True
    ok2 = check_surd('113', 'sqrt(113)')
    assert ok2['correct'] is True
    bad = check_surd('113', '√112')
    assert bad['correct'] is False
    ok3 = check_surd('2|5', '2√5')
    assert ok3['correct'] is True
    ok4 = check_surd('289', '17')
    assert ok4['correct'] is True
    ok5 = check_surd('289', '√289')
    assert ok5['correct'] is True


def test_pythagoras_surd_check_api():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'correct_answer_raw': '113',
                'answer_type': 'surd',
                'user_answer': '√113',
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'pythagoras',
                'difficulty': 'difficult',
                'correct_answer_raw': '4|3',
                'answer_type': 'surd',
                'user_answer': '4√3',
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


def test_pythagoras_3d_diagonal_exact_check_api():
    import generators.gcse.maths_pythagoras as pyth_mod

    problem = _pyth_problem_from_output(pyth_mod._py_d3_3d_diagonal_exact(), 'difficult')
    raw = problem['correct_answer_raw']
    sep = '\x1e' if '\x1e' in raw else '|'
    parts = raw.split(sep)
    assert len(parts) == 2
    surd_raw, dec_raw = parts[0], parts[1]
    if '|' in surd_raw:
        coeff, rad = surd_raw.split('|', 1)
        user_surd = f'{coeff}√{rad}'
    else:
        user_surd = f'√{surd_raw}'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'correct_answer_raw': surd_raw,
                'answer_type': 'surd',
                'user_answer': user_surd,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'correct_answer_raw': dec_raw,
                'answer_type': 'number',
                'user_answer': dec_raw,
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


def test_pythagoras_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_pythagoras_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_pythagoras(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in PYTHAGORAS_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_pythagoras_check_api():
    problem = gcse_pythagoras(
        'foundational', 'practice', variant_name='_py_f1_find_hypotenuse'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'pythagoras',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


COMPOUND_NUMBER_VARIANTS = (
    '_cm_f1_sdt_find_speed',
    '_cm_f2_sdt_find_distance',
    '_cm_f10_convert_kmh_to_ms',
    '_cm_i1_average_speed_two_legs',
    '_cm_i9_average_speed_equal_distances',
    '_cm_d4_water_pressure',
)

COMPOUND_KEYWORD_VARIANTS = (
    '_cm_f15_density_compare',
    '_cm_i13_floating_sinking',
)

COMPOUND_MULTIPART_VARIANTS = (
    '_cm_i10_sdt_ms_and_km',
    '_cm_i12_pressure_unit_conversion',
    '_cm_i14_speed_convert_then_distance',
    '_cm_d1_meeting_problem',
    '_cm_d8_density_kg_m3_use',
    '_cm_d9_concentration',
    '_cm_d12_hydraulic_press',
    '_cm_d14_pressure_minimum_area',
    '_cm_d15_mass_flow_rate',
)

COMPOUND_UNGRADED_VARIANTS = (
    '_cm_d5_algebraic_sdt',
    '_cm_d7_harmonic_mean_prove',
)


def test_compound_measures_number_variants_are_graded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_NUMBER_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') == 'number', name


def test_compound_measures_keyword_variants_are_graded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_KEYWORD_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'keyword', name
        assert problem.get('correct_answer_raw'), name


def test_compound_measures_multipart_variants_use_number_fields():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_MULTIPART_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert labels, name
        assert len(problem['correct_answer_raw'].split('|')) == len(labels), name


def test_compound_measures_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_UNGRADED_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 4, name
        problem = _cm_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw') is None, name


def test_compound_measures_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_compound_measures_variants(difficulty, 'practice')
        for variant in variants:
            problem = gcse_compound_measures(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in COMPOUND_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_compound_measures_check_api():
    problem = gcse_compound_measures(
        'foundational', 'practice', variant_name='_cm_f1_sdt_find_speed'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'compound_measures',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_compound_measures_keyword_check_api():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'correct_answer_raw': 'float',
                'answer_type': 'keyword',
                'user_answer': 'floats',
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


BEARINGS_BEARING_VARIANTS = (
    '_brg_found_cardinal',
    '_brg_found_back_lt_180',
    '_brg_found_reading',
    '_brg_inter_return_bearing_context',
)

BEARINGS_NUMBER_VARIANTS = (
    '_brg_found_angle_between',
    '_brg_inter_east_component',
    '_brg_inter_distance_pythagoras',
    '_brg_diff_elevation_and_bearing',
)

BEARINGS_KEYWORD_VARIANTS = (
    '_brg_found_quadrant',
)

BEARINGS_MULTIPART_VARIANTS = (
    '_brg_inter_single_leg_multipart',
    '_brg_inter_two_ships_port_multipart',
    '_brg_diff_return_voyage_multipart',
)

BEARINGS_UNGRADED_VARIANTS = (
    '_brg_diff_prove_bearing',
)


def test_checker_bearing_unit():
    ok = check_bearing('045', '45')
    assert ok['correct'] is True
    ok2 = check_bearing('045', '045°')
    assert ok2['correct'] is True
    bad = check_bearing('045', '46')
    assert bad['correct'] is False


def test_bearings_bearing_variants_are_graded():
    import generators.gcse.maths_bearings as brg_mod

    for name in BEARINGS_BEARING_VARIANTS:
        out = getattr(brg_mod, name)()
        assert len(out) == 5, name
        problem = _brg_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'bearing', name
        assert problem.get('correct_answer_raw'), name


def test_bearings_number_variants_are_graded():
    import generators.gcse.maths_bearings as brg_mod

    for name in BEARINGS_NUMBER_VARIANTS:
        out = getattr(brg_mod, name)()
        assert len(out) == 5, name
        problem = _brg_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw'), name


def test_bearings_keyword_variants_are_graded():
    import generators.gcse.maths_bearings as brg_mod

    for name in BEARINGS_KEYWORD_VARIANTS:
        out = getattr(brg_mod, name)()
        assert len(out) == 5, name
        problem = _brg_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'keyword', name


def test_bearings_multipart_variants_use_number_fields():
    import generators.gcse.maths_bearings as brg_mod

    for name in BEARINGS_MULTIPART_VARIANTS:
        out = getattr(brg_mod, name)()
        assert len(out) == 5, name
        problem = _brg_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert labels, name


def test_bearings_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_bearings as brg_mod

    for name in BEARINGS_UNGRADED_VARIANTS:
        out = getattr(brg_mod, name)()
        assert len(out) == 4, name
        problem = _brg_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw') is None, name


def test_bearings_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_bearings_variants(difficulty, 'practice')
        for variant in variants:
            problem = gcse_bearings(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in BEARINGS_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_bearings_check_api():
    problem = gcse_bearings(
        'foundational', 'practice', variant_name='_brg_found_cardinal'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'bearing'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bearings',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'bearing',
                'user_answer': str(int(correct)),
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


SEQUENCES_NUMBER_VARIANTS = (
    '_seq_found_next_term_arithmetic',
    '_seq_found_nth_term_find_value',
    '_seq_found_square_numbers',
    '_seq_inter_which_term',
    '_seq_inter_sum_arithmetic',
    '_seq_diff_sum_of_squares',
)

SEQUENCES_KEYWORD_VARIANTS = (
    '_seq_found_is_term_in_seq',
    '_seq_inter_not_in_seq',
)

SEQUENCES_MULTIPART_VARIANTS = (
    '_seq_diff_find_a_and_d',
    '_seq_diff_convergence_check',
)

SEQUENCES_FRACTION_VARIANTS = (
    '_seq_diff_arithmetic_mean',
    '_seq_diff_nth_term_with_fractions',
)

SEQUENCES_UNGRADED_VARIANTS = (
    '_seq_found_identify_rule',
    '_seq_found_term_to_term_rule',
    '_seq_found_nth_term_find_terms',
    '_seq_inter_find_nth_term',
    '_seq_inter_nth_term_negative_d',
    '_seq_inter_quadratic_identify',
    '_seq_diff_quadratic_nth_term',
    '_seq_diff_recurring_decimal_proof',
    '_seq_diff_show_divisible',
    '_seq_diff_arithmetic_proof',
)


def test_sequences_number_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_NUMBER_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw'), name


def test_sequences_keyword_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_KEYWORD_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'keyword', name


def test_sequences_multipart_variants_use_number_fields():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_MULTIPART_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name


def test_sequences_fraction_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_FRACTION_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw'), name


def test_sequences_ungraded_variants_remain_ungraded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_UNGRADED_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 4, name
        problem = _seq_problem_from_output(out, 'difficult')
        assert problem.get('correct_answer_raw') is None, name


def test_sequences_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_sequences_variants(difficulty, 'practice')
        for variant in variants:
            problem = gcse_sequences(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in SEQUENCES_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_sequences_check_api():
    problem = gcse_sequences(
        'foundational', 'practice', variant_name='_seq_found_next_term_arithmetic'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'sequences',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_free_response_partial_renders_one_row():
    with app.test_request_context():
        from flask import render_template

        number_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '1910',
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='number',
            fr_difficulty='intermediate',
        )
        assert 'free-response-row--number' in number_html
        assert 'free-response-row--standard-form' not in number_html
        assert 'free-response-row--number-pair' not in number_html
        assert number_html.count('free-response-check-btn') == 1

        sf_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '3.2|5',
                'answer_type': 'standard_form',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='number',
            fr_difficulty='foundational',
        )
        assert 'free-response-row--standard-form' in sf_html
        assert 'free-response-row--number"' not in sf_html
        assert 'free-response-row--number-pair' not in sf_html
        assert '× 10^' in sf_html
        assert sf_html.count('free-response-check-btn') == 1

        pi_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '4',
                'answer_type': 'pi_multiple',
                'answer_format_hint': 'Enter the multiple of π',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='mensuration',
            fr_difficulty='difficult',
        )
        assert 'free-response-row--pi-multiple' in pi_html
        assert 'free-response-pi-sep' in pi_html
        assert 'π' in pi_html
        assert 'free-response-row--number"' not in pi_html
        assert pi_html.count('free-response-check-btn') == 1

        pair_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '28|42',
                'answer_type': 'number_pair',
                'answer_labels': ['First share (£)', 'Second share (£)'],
                'answer_pair_sep': 'and',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='number',
            fr_difficulty='intermediate',
        )
        assert 'free-response-row--number-pair' in pair_html
        assert 'free-response-row--standard-form' not in pair_html
        assert 'free-response-row--number"' not in pair_html
        assert pair_html.count('free-response-check-btn') == 1

        power_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '2|12',
                'answer_type': 'power',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='number',
            fr_difficulty='intermediate',
        )
        assert 'free-response-row--power' in power_html
        assert 'free-response-row--standard-form' not in power_html
        assert 'free-response-input-base' in power_html
        assert 'free-response-input-index' in power_html
        assert power_html.count('free-response-check-btn') == 1

        fields_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '1/2|1/3|2/3',
                'answer_type': 'number_fields',
                'answer_labels': ['Branch 1', 'Branch 2', 'Final probability'],
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='probability',
            fr_difficulty='difficult',
        )
        assert 'free-response-row--number-fields' in fields_html
        assert fields_html.count('free-response-input-field') == 3
        assert 'Final probability' in fields_html
        assert fields_html.count('free-response-field-check-btn') == 3
        assert 'free-response-fields-stack' in fields_html
        assert 'free-response-fields-grid' not in fields_html

        ratio_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '3|5',
                'answer_type': 'ratio',
                'answer_format_hint': 'Enter ratio as a:b',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='ratio_proportion',
            fr_difficulty='foundational',
        )
        assert 'free-response-row--ratio' in ratio_html
        assert 'free-response-input-ratio' in ratio_html


def test_mcq_attempt_grouping_for_display():
    from models.user_data import group_mcq_attempts_for_display

    group_id = 'g_test_multipart'
    attempts = [
        {
            'id': 6,
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'graphs',
            'mode': 'mcq',
            'difficulty': 'difficult',
            'user_answer': 'wrong',
            'correct_answer': '3',
            'correct': 0,
            'created_at': '2026-07-15T18:00:05',
            'attempt_group_id': group_id,
            'part_index': 2,
            'part_total': 3,
        },
        {
            'id': 5,
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'graphs',
            'mode': 'mcq',
            'difficulty': 'difficult',
            'user_answer': '2',
            'correct_answer': '2',
            'correct': 1,
            'created_at': '2026-07-15T18:00:04',
            'attempt_group_id': group_id,
            'part_index': 1,
            'part_total': 3,
        },
        {
            'id': 4,
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'graphs',
            'mode': 'mcq',
            'difficulty': 'difficult',
            'user_answer': 'bad',
            'correct_answer': 'positive',
            'correct': 0,
            'created_at': '2026-07-15T18:00:03',
            'attempt_group_id': group_id,
            'part_index': 0,
            'part_total': 3,
        },
        {
            'id': 3,
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'graphs',
            'mode': 'mcq',
            'difficulty': 'difficult',
            'user_answer': '7',
            'correct_answer': '7',
            'correct': 1,
            'created_at': '2026-07-15T18:00:02',
            'attempt_group_id': group_id,
            'part_index': 0,
            'part_total': 3,
        },
        {
            'id': 2,
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'number',
            'mode': 'mcq',
            'difficulty': 'foundational',
            'user_answer': '4',
            'correct_answer': '4',
            'correct': 1,
            'created_at': '2026-07-15T17:00:00',
            'attempt_group_id': None,
            'part_index': None,
            'part_total': None,
        },
    ]

    grouped = group_mcq_attempts_for_display(attempts)
    assert len(grouped) == 2
    multipart = next(item for item in grouped if item.get('is_multipart'))
    assert multipart['score'] == 1
    assert multipart['total'] == 3
    assert multipart['topic'] == 'graphs'
    single = next(item for item in grouped if not item.get('is_multipart'))
    assert bool(single['correct']) is True


def test_generator_page_renders_free_response():
    with app.test_client() as client:
        r = client.post(
            '/',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
                'action': 'start',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert 'free-response-inline' in body
        assert 'free-response-check-btn' in body


def test_quicktest_page_renders_free_response():
    with app.test_client() as client:
        r = client.post(
            '/quicktest/start',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert 'free-response-inline' in body
        assert 'free-response-check-btn' in body
        assert 'quicktest-next-form' in body
        assert 'name="qt_user_answer"' in body
        assert 'name="qt_checked"' in body


def test_quicktest_next_stores_free_response_answer():
    with app.test_client() as client:
        client.post(
            '/quicktest/start',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            follow_redirects=True,
        )
        r = client.post(
            '/quicktest/next',
            data={
                'qt_user_answer': '42',
                'qt_checked': '1',
                'qt_correct': '1',
            },
            follow_redirects=False,
        )
        assert r.status_code in (302, 303), r.data
        with client.session_transaction() as sess:
            qt_id = sess.get('qt_id')
        assert qt_id
        from models.quicktest import load_quicktest_session
        from app import get_db

        with get_db() as conn:
            data = load_quicktest_session(conn, qt_id)
        answers = data.get('answers') or []
        assert len(answers) == 1
        assert answers[0].get('user_answer') == '42'
        assert answers[0].get('checked') is True
        assert answers[0].get('correct') is True


def test_quicktest_check_wrong_answer_not_session_mismatch():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['last_problem_payload'] = {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
                'problem': {'correct_answer_raw': '999', 'answer_type': 'number'},
            }
        client.post(
            '/quicktest/start',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            follow_redirects=True,
        )
        r = client.get('/quicktest')
        assert r.status_code == 200, r.data
        with client.session_transaction() as sess:
            stored = sess.get('last_problem_payload') or {}
            problem = stored.get('problem') or {}
        assert problem.get('correct_answer_raw') is not None
        assert str(problem.get('correct_answer_raw')) != '999'
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '5',
                'correct_answer_raw': str(problem['correct_answer_raw']),
                'answer_type': problem.get('answer_type', 'number'),
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        body = r.get_json()
        assert body.get('correct') is False
        assert 'mismatch' not in (body.get('error') or '').lower()


def test_quicktest_results_summary():
    from app import _quicktest_results_summary

    problems = [
        {'options': ['A', 'B'], 'correct_answer': 'A', 'marks': 1},
        {'correct_answer_raw': '5', 'answer_type': 'number', 'marks': 2},
        {'question': 'Explain', 'marks': 2},
    ]
    answers = [
        {'user_answer': 'A', 'correct': True},
        {'user_answer': '5', 'checked': True, 'correct': True},
        {'checked': False, 'correct': None},
    ]
    summary = _quicktest_results_summary(problems, answers)
    assert summary['mcq_score'] == 1
    assert summary['mcq_total'] == 1
    assert summary['graded_score'] == 1
    assert summary['graded_total'] == 1
    assert summary['checked_total'] == 1


def test_quicktest_saves_to_profile_when_logged_in():
    import uuid

    from models.user import User, normalize_email
    from models.user_data import list_quiz_attempts
    from app import get_db

    email = f'qt_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'qt{uuid.uuid4().hex[:6]}'
    with app.test_client() as client:
        register(client, email, handle)
        client.post(
            '/quicktest/start',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            follow_redirects=True,
        )
        for _ in range(20):
            r = client.post(
                '/quicktest/next',
                data={
                    'qt_user_answer': '1',
                    'qt_checked': '1',
                    'qt_correct': '0',
                },
                follow_redirects=False,
            )
            if r.status_code in (302, 303) and r.location and 'results' in r.location:
                break
            if r.status_code in (302, 303):
                client.get(r.location)
        r = client.get('/quicktest/results')
        assert r.status_code == 200, r.data
        with get_db() as conn:
            user = User.get_by_email(conn, normalize_email(email))
            attempts = list_quiz_attempts(conn, user.id, limit=5)
        assert any(item['topic'] == 'bidmas' for item in attempts)


def test_quicktest_api_payload_includes_grading_fields():
    with app.test_client() as client:
        r = client.post(
            '/api/v1/quicktest/start',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 201, r.data
        problem = r.get_json().get('problem') or {}
        assert problem.get('correct_answer_raw') is not None


def test_saved_problem_reroll_keeps_free_response_payload():
    email = f'fr_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'fr{uuid.uuid4().hex[:6]}'

    with app.test_client() as client:
        register(client, email, handle)

        r = client.post(
            '/',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'practice',
                'difficulty': 'foundational',
                'action': 'start',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200, r.data
        assert 'free-response-inline' in r.data.decode()

        r = client.post(
            '/saved-problems/save',
            data={'csrf_token': csrf_from(r.data.decode())},
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
        )
        assert r.status_code == 200, r.data
        saved_id = r.get_json()['saved_id']

        r = client.get(f'/saved-problems/{saved_id}')
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert 'saved-free-response' in body
        assert 'free-response-check-btn' in body

        if 'New numbers' in body:
            r = client.post(
                f'/saved-problems/{saved_id}/reroll',
                data={'csrf_token': csrf_from(body)},
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                },
            )
            assert r.status_code == 200, r.data
            payload = r.get_json()
            assert payload['ok'] is True
            assert payload['problem'].get('correct_answer_raw') is not None


def _generate_practice_bidmas(client):
    return client.post(
        '/',
        data={
            'level': 'gcse',
            'subject': 'maths',
            'topic': 'bidmas',
            'mode': 'practice',
            'difficulty': 'foundational',
            'action': 'start',
        },
        follow_redirects=True,
    )


def test_saved_problem_check_saves_practice_history():
    import uuid

    from models.user import User, normalize_email
    from models.user_data import list_generator_mcq_attempts
    from app import get_db

    email = f'sv_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'sv{uuid.uuid4().hex[:6]}'
    with app.test_client() as client:
        register(client, email, handle)
        r = _generate_practice_bidmas(client)
        assert r.status_code == 200, r.data
        r = client.post(
            '/saved-problems/save',
            data={'csrf_token': csrf_from(r.data.decode())},
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
        )
        assert r.status_code == 200, r.data
        saved_id = r.get_json()['saved_id']

        r = client.get(f'/saved-problems/{saved_id}')
        assert r.status_code == 200, r.data
        with client.session_transaction() as sess:
            problem = (sess.get('last_problem_payload') or {}).get('problem') or {}
        assert problem.get('correct_answer_raw') is not None

        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': '999',
                'correct_answer_raw': str(problem['correct_answer_raw']),
                'answer_type': problem.get('answer_type', 'number'),
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        assert r.get_json().get('correct') is False

        with get_db() as conn:
            user = User.get_by_email(conn, normalize_email(email))
            attempts = list_generator_mcq_attempts(conn, user.id, limit=5)
        assert any(item['topic'] == 'bidmas' for item in attempts)


def test_shared_question_renders_trackable_free_response():
    import uuid

    email = f'sh_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'sh{uuid.uuid4().hex[:6]}'
    with app.test_client() as client:
        register(client, email, handle)
        r = _generate_practice_bidmas(client)
        r = client.post(
            '/shared-questions/share',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'visibility': 'public',
            },
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        share_id = r.get_json()['share_id']

        r = client.get(f'/shared/{share_id}')
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert 'shared-free-response' in body or 'free-response-inline' in body
        assert 'data-level="gcse"' in body
        assert 'free-response-check-btn' in body


def test_suggestion_view_renders_trackable_free_response():
    import uuid

    suffix = uuid.uuid4().hex[:8]
    email_a = f'sg_a_{suffix}@example.com'
    email_b = f'sg_b_{suffix}@example.com'
    handle_a = f'sga{suffix[:6]}'
    handle_b = f'sgb{suffix[:6]}'
    with app.test_client() as client:
        register(client, email_b, handle_b)
        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})

        register(client, email_a, handle_a)
        r = _generate_practice_bidmas(client)
        r = client.post(
            '/suggestions',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'recipient_handle': handle_b,
                'note': 'Try this',
            },
            headers={'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json'},
        )
        assert r.status_code == 200, r.data
        suggestion_id = r.get_json()['suggestion_id']

        client.post('/logout', data={'csrf_token': csrf_from(client.get('/profile').data.decode())})
        r = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': email_b,
                'password': 'password123',
            },
            follow_redirects=True,
        )

        r = client.get(f'/suggestions/{suggestion_id}')
        assert r.status_code == 200, r.data
        body = r.data.decode()
        assert 'suggestion-free-response' in body or 'free-response-inline' in body
        assert 'data-level="gcse"' in body
        assert 'free-response-check-btn' in body


def main():
    test_checker_unit()
    test_checker_standard_form_unit()
    test_checker_number_pair_and_list_unit()
    test_checker_power_and_fraction_unit()
    test_checker_fraction_unit()
    test_checker_number_fields_unit()
    test_bidmas_variants_expose_raw()
    test_all_bidmas_practice_variants_return_five_tuple()
    test_foundational_practice_pool_returns_five_tuple()
    test_bidmas_generator_payload()
    test_bidmas_variant_queue_always_graded()
    test_fdp_graded_variants_return_five_tuple()
    test_fdp_ungraded_variants_remain_four_tuple()
    test_fdp_fraction_variants_use_fraction_checker()
    test_fdp_multipart_variants_use_number_fields()
    test_fdp_generator_payload()
    test_fdp_variant_queues_are_graded()
    test_fdp_check_api_fraction()
    test_fdp_check_api_number()
    test_surds_surd_variants_use_surd_checker()
    test_surds_ungraded_variants_remain_four_tuple()
    test_surds_number_variants_are_graded()
    test_surds_multipart_variants_use_number_fields()
    test_surds_algebraic_variants_use_algebraic_checker()
    test_surds_expand_simple_uses_number_checker()
    test_surds_algebraic_fraction_variants_are_graded()
    test_check_algebraic_fraction_surd()
    test_check_algebraic_fraction_binomial()
    test_check_algebraic_fraction_expanded_binomial()
    test_check_algebraic_fraction_empty_denominator_defaults_to_one()
    test_check_algebraic_fraction_two_surds()
    test_surds_rationalise_simple_check_api()
    test_surds_rationalise_compound_check_api()
    test_surds_show_that_rationalise_check_api()
    test_surds_rationalise_binomial_diff_intermediate_check_api()
    test_surds_rationalise_binomial_diff_check_api()
    test_check_algebraic_identity()
    test_check_algebraic_surd_binomial()
    test_surds_algebraic_check_api()
    test_surds_compare_uses_choice_buttons()
    test_surds_generator_payload()
    test_surds_variant_queues_are_graded()
    test_surds_check_api()
    test_af_fraction_variants_use_fraction_checker()
    test_af_number_variants_are_graded()
    test_af_ungraded_variants_remain_four_tuple()
    test_af_generator_payload()
    test_af_variant_queues_are_graded()
    test_af_check_api_fraction()
    test_af_check_api_number()
    test_number_numeric_variants_return_five_tuple()
    test_number_standard_form_variants_graded()
    test_number_power_variants_graded()
    test_number_fraction_variants_graded()
    test_number_compare_choice_variants()
    test_number_share_ratio_graded()
    test_all_number_practice_variants_graded()
    test_probability_core_variants_are_graded()
    test_probability_tree_diagrams_use_inline_inputs()
    test_probability_variant_queues_are_graded()
    test_probability_check_api_accepts_fraction()
    test_statistics_core_variants_are_graded()
    test_statistics_multipart_variants_use_number_fields()
    test_statistics_choice_variants_use_buttons()
    test_statistics_variant_queues_are_graded()
    test_checker_ratio_unit()
    test_ratio_fraction_variants_use_fraction_checker()
    test_ratio_core_variants_are_graded()
    test_ratio_fraction_check_api()
    test_ratio_multipart_variants_use_number_fields()
    test_ratio_choice_and_pair_variants()
    test_ratio_variant_queues_are_graded()
    test_ratio_merge_classes_number_fields_check()
    test_ratio_proportion_check_api()
    test_checker_binary_hex_unit()
    test_data_rep_core_variants_are_graded()
    test_data_rep_multipart_number_systems()
    test_data_rep_variant_queues_are_graded()
    test_data_rep_check_api()
    test_algorithms_trace_variants_are_graded()
    test_algorithms_multipart_numeric_fields()
    test_algorithms_variant_queues_are_graded()
    test_algorithms_check_api()
    test_computer_systems_numeric_variants_are_graded()
    test_computer_networks_numeric_variants_are_graded()
    test_computer_systems_networks_variant_queues()
    test_computer_systems_networks_check_api()
    test_checker_linear_equation_and_keyword_unit()
    test_checker_number_estimate_unit()
    test_graphs_core_variants_are_graded()
    test_graphs_multipart_and_choice_variants()
    test_graphs_variant_queues_are_graded()
    test_standard_form_check_api()
    test_number_generator_payload()
    test_number_variant_queue_graded_when_numeric()
    test_number_practice_pool_has_graded_variants()
    test_check_api_without_session()
    test_check_api_with_session_binding()
    test_check_api_number_fields_partial_with_session()
    test_geometry_core_variants_are_graded()
    test_geometry_multipart_variants_use_number_fields()
    test_geometry_proof_variants_remain_ungraded()
    test_geometry_variant_queues_are_graded()
    test_geometry_check_api_accepts_degree_symbol()
    test_mensuration_core_variants_are_graded()
    test_mensuration_multipart_variants_use_number_fields()
    test_mensuration_exact_pi_variants_use_pi_multiple()
    test_mensuration_variant_queues_are_graded()
    test_mensuration_pi_multiple_and_check_api()
    test_mensuration_fraction_and_check_api()
    test_pythagoras_number_variants_are_graded()
    test_pythagoras_keyword_variants_are_graded()
    test_pythagoras_multipart_variants_use_number_fields()
    test_pythagoras_two_triangles_keyword_field()
    test_pythagoras_ungraded_variants_remain_ungraded()
    test_pythagoras_distance_formula_graded()
    test_checker_surd_unit()
    test_pythagoras_surd_check_api()
    test_pythagoras_variant_queues_are_graded()
    test_pythagoras_check_api()
    test_compound_measures_number_variants_are_graded()
    test_compound_measures_keyword_variants_are_graded()
    test_compound_measures_multipart_variants_use_number_fields()
    test_compound_measures_ungraded_variants_remain_ungraded()
    test_compound_measures_variant_queues_are_graded()
    test_compound_measures_check_api()
    test_compound_measures_keyword_check_api()
    test_checker_bearing_unit()
    test_bearings_bearing_variants_are_graded()
    test_bearings_number_variants_are_graded()
    test_bearings_keyword_variants_are_graded()
    test_bearings_multipart_variants_use_number_fields()
    test_bearings_ungraded_variants_remain_ungraded()
    test_bearings_variant_queues_are_graded()
    test_bearings_check_api()
    test_sequences_number_variants_are_graded()
    test_sequences_keyword_variants_are_graded()
    test_sequences_multipart_variants_use_number_fields()
    test_sequences_fraction_variants_are_graded()
    test_sequences_ungraded_variants_remain_ungraded()
    test_sequences_variant_queues_are_graded()
    test_sequences_check_api()
    test_free_response_partial_renders_one_row()
    test_mcq_attempt_grouping_for_display()
    test_generator_page_renders_free_response()
    test_quicktest_page_renders_free_response()
    test_quicktest_next_stores_free_response_answer()
    test_quicktest_check_wrong_answer_not_session_mismatch()
    test_quicktest_results_summary()
    test_quicktest_saves_to_profile_when_logged_in()
    test_quicktest_api_payload_includes_grading_fields()
    test_saved_problem_reroll_keeps_free_response_payload()
    test_saved_problem_check_saves_practice_history()
    test_shared_question_renders_trackable_free_response()
    test_suggestion_view_renders_trackable_free_response()
    print('test_answer_check_smoke: all checks passed')


if __name__ == '__main__':
    main()
