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
    _algebra_problem_from_output,
    _bidmas_problem,
    _dec_problem_from_output,
    _mf_problem_from_output,
    _fdp_problem,
    _fdp_problem_from_output,
    _surd_problem,
    _surd_problem_from_output,
    gcse_bidmas_brackets,
    gcse_bidmas_power,
    gcse_bidmas_simple,
    gcse_dec_fraction_to_decimal,
    gcse_dec_ordering,
    gcse_dec_practice_order_mixed,
    gcse_dec_recurring,
    gcse_fdp_decimal_to_fraction,
    gcse_fdp_decimal_to_percentage,
    gcse_fdp_fraction_to_decimal,
    gcse_fdp_share_in_ratio,
    gcse_maths_algebra,
    gcse_maths_bidmas,
    gcse_maths_decimals,
    gcse_maths_fdp,
    gcse_maths_multiples_factors,
    gcse_maths_surds,
    gcse_mf_hcf_lcm_product_rule,
    gcse_mf_lcm_buses_word,
    gcse_mf_prime,
    gcse_mf_primes_in_range,
    gcse_neg_add_subtract,
    gcse_surds_simplify,
    _vec_problem_from_output,
    gcse_vectors,
    gcse_vectors_variants,
    _trig_problem_from_output,
    gcse_trigonometry,
    gcse_trigonometry_variants,
)
from generators.gcse.maths_basic_topics_mcq import (  # noqa: E402
    _practice_pools,
    gcse_maths_algebra_variants,
    gcse_maths_bidmas_variants,
    gcse_maths_decimals_variants,
    gcse_maths_fdp_variants,
    gcse_maths_multiples_factors_variants,
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
from generators.gcse.transformations import (  # noqa: E402
    gcse_transformations,
    gcse_transformations_variants,
)
from generators.gcse.maths_constructions_loci import (  # noqa: E402
    gcse_constructions_loci,
    gcse_constructions_loci_variants,
)
from generators.shared.utils import make_graded_problem, make_problem  # noqa: E402
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
from generators.gcse.equations_inequalities import (  # noqa: E402
    _eq_problem_from_output,
    gcse_equations_inequalities,
    gcse_equations_inequalities_variants,
)
from generators.gcse.simultaneous_equations import (  # noqa: E402
    _sim_problem_from_output,
    gcse_simultaneous_equations,
    gcse_simultaneous_equations_variants,
)
from generators.gcse.graphical_simultaneous_equations import (  # noqa: E402
    _gsim_problem_from_output,
    gcse_graphical_simultaneous_equations,
    gcse_graphical_simultaneous_equations_variants,
)
from generators.gcse.completing_the_square import (  # noqa: E402
    _cts_problem_from_output,
    gcse_completing_the_square,
    gcse_completing_the_square_variants,
)
from generators.gcse.quadratic_simultaneous_equations import (  # noqa: E402
    _qsim_problem_from_output,
    gcse_quadratic_simultaneous_equations,
    gcse_quadratic_simultaneous_equations_variants,
)
from generators.gcse.changing_the_subject import (  # noqa: E402
    _subj_problem_from_output,
    gcse_changing_the_subject,
    gcse_changing_the_subject_variants,
)
from generators.gcse.functions import (  # noqa: E402
    _fn_problem_from_output,
    gcse_functions,
    gcse_functions_variants,
)
from generators.gcse.maths_bearings import (  # noqa: E402
    _brg_problem_from_output,
    gcse_bearings,
    gcse_bearings_variants,
)
from generators.gcse.maths_similarity_congruence import (  # noqa: E402
    gcse_similarity_congruence,
    gcse_similarity_congruence_variants,
)
from generators.gcse.maths_circle_theorems import (  # noqa: E402
    gcse_circle_theorems,
    gcse_circle_theorems_variants,
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
from generators.gcse.gcse_cs_db_sql_lesson import (  # noqa: E402
    _db_problem_from_output,
    gcse_db_sql,
    gcse_db_sql_variants,
)
from generators.gcse.gcse_cs_systems_software_lesson import (  # noqa: E402
    _sw_problem_from_output,
    gcse_systems_software,
    gcse_systems_software_variants,
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
from generators.gcse.cs_cyber_security import (  # noqa: E402
    _cy_problem_from_output,
    gcse_cyber_security,
    gcse_cyber_security_variants,
)
from generators.gcse.gcse_cs_ethical_lesson import (  # noqa: E402
    _eth_problem_from_output,
    gcse_ethical,
    gcse_ethical_variants,
)
from generators.gcse.cs import (  # noqa: E402
    _py_problem_from_output,
    gcse_python_programming,
    gcse_python_variants,
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
    check_linear,
    check_linear_equation,
    check_linear_inequality,
    check_compound_inequality,
    check_number_line,
    check_formula_fraction,
    check_coordinate_pairs,
    check_two_var_equation,
    check_quadratic_roots,
    check_vector,
    check_vector_combo,
    check_vector_pair,
    check_keyword,
    check_text,
    check_number_estimate,
    check_standard_form,
    check_surd,
    check_pi_multiple,
    check_bearing,
    check_binary,
    check_hex,
    check_fraction,
    check_algebraic_fraction,
)
from generators.shared.utils import problem_from_choice_output  # noqa: E402
from app import app  # noqa: E402

def _bind_check_session(client, *, level, subject, topic, difficulty, correct_answer_raw, answer_type, problem=None):
    """Store grading keys in session so SymPy-backed check types are allowed."""
    payload_problem = problem if isinstance(problem, dict) else {
        'correct_answer_raw': correct_answer_raw,
        'answer_type': answer_type,
    }
    if isinstance(payload_problem, dict) and payload_problem.get('correct_answer_raw') is None:
        payload_problem = {
            **payload_problem,
            'correct_answer_raw': correct_answer_raw,
            'answer_type': answer_type,
        }
    with client.session_transaction() as sess:
        sess['last_problem_payload'] = {
            'level': level,
            'subject': subject,
            'topic': topic,
            'mode': 'practice',
            'difficulty': difficulty,
            'problem': payload_problem,
        }


def _post_problems_check(client, json_body, *, problem=None, headers=None):
    """POST /api/v1/problems/check, binding session for SymPy-backed types."""
    body = dict(json_body)
    answer_type = (body.get('answer_type') or 'number').strip()
    if answer_type in ('algebraic', 'quadratic_roots'):
        _bind_check_session(
            client,
            level=body.get('level') or 'gcse',
            subject=body.get('subject') or 'maths',
            topic=body.get('topic') or 'bidmas',
            difficulty=body.get('difficulty') or 'foundational',
            correct_answer_raw=body.get('correct_answer_raw'),
            answer_type=answer_type,
            problem=problem,
        )
    else:
        # Avoid session_mismatch when a prior SymPy check left grading keys in session.
        with client.session_transaction() as sess:
            sess.pop('last_problem_payload', None)
    kwargs = {'json': body}
    if headers is not None:
        kwargs['headers'] = headers
    response = client.post('/api/v1/problems/check', **kwargs)
    # Drop bound keys so follow-up direct client.post checks are not poisoned.
    if answer_type in ('algebraic', 'quadratic_roots'):
        with client.session_transaction() as sess:
            sess.pop('last_problem_payload', None)
    return response




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


def test_checker_linear_unit():
    same = check_linear('3', '3')
    assert same['correct'] is True
    assert same['normalized_correct'] == 'x = 3'
    assert same['normalized_user'] == 'x = 3'

    with_var = check_linear('x=3', 'x = 3')
    assert with_var['correct'] is True

    plain_from_var = check_linear('x=3', '3')
    assert plain_from_var['correct'] is True
    assert plain_from_var['normalized_user'] == 'x = 3'

    negative = check_linear('x=-2', '-2')
    assert negative['correct'] is True

    fraction = check_linear('1/2', '0.5')
    assert fraction['correct'] is True

    other_var = check_linear('t=1', 't=1')
    assert other_var['correct'] is True
    assert other_var['normalized_correct'] == 't = 1'

    bad = check_linear('3', '4')
    assert bad['correct'] is False

    empty = check_linear('3', '')
    assert empty['correct'] is False

    via_registry = check_answer('linear', 'x=3', '3')
    assert via_registry['correct'] is True


def test_checker_quadratic_roots_unit():
    order_free = check_quadratic_roots('3,-2', '-2, 3')
    assert order_free['correct'] is True
    assert order_free['normalized_correct'] == '-2,3'
    assert order_free['normalized_user'] == '-2,3'

    braces = check_quadratic_roots('{3,-2}', '3, -2')
    assert braces['correct'] is True

    equivalent = check_quadratic_roots('1/2,3', '0.5, 3')
    assert equivalent['correct'] is True

    words = check_quadratic_roots('3,-2', 'x=3 or x=-2')
    assert words['correct'] is True

    pipe = check_quadratic_roots('3|-2', '3, -2')
    assert pipe['correct'] is True

    single = check_quadratic_roots('3', '3')
    assert single['correct'] is True
    assert single['normalized_correct'] == '3'

    bad = check_quadratic_roots('3,-2', '3, 2')
    assert bad['correct'] is False

    missing = check_quadratic_roots('3,-2', '3')
    assert missing['correct'] is False

    four_wrong = check_quadratic_roots('-2,-1,1,2', '1, -1')
    assert four_wrong['correct'] is False
    assert 'four solutions' in (four_wrong.get('feedback') or '').lower()
    assert 'enter 4' not in (four_wrong.get('feedback') or '').lower()
    assert 'commas' not in (four_wrong.get('feedback') or '').lower()

    four_wrong_vals = check_quadratic_roots('-2,-1,1,2', '1, -1, 2, 3')
    assert four_wrong_vals['correct'] is False
    assert 'four solutions' in (four_wrong_vals.get('feedback') or '').lower()
    assert 'enter 4' not in (four_wrong_vals.get('feedback') or '').lower()
    assert 'commas' not in (four_wrong_vals.get('feedback') or '').lower()

    via_registry = check_answer('quadratic_roots', '{3,-2}', '-2,3')
    assert via_registry['correct'] is True

    surd_roots = check_quadratic_roots('-3+sqrt(14),-3-sqrt(14)', '-3+√14, -3-√14')
    assert surd_roots['correct'] is True

    surd_pm = check_quadratic_roots('-3+sqrt(14),-3-sqrt(14)', '-3±√14')
    assert surd_pm['correct'] is True

    surd_sqrt_notation = check_quadratic_roots('-3+sqrt(14),-3-sqrt(14)', '-3+sqrt(14), -3-sqrt(14)')
    assert surd_sqrt_notation['correct'] is True


def test_checker_vector_unit():
    same = check_vector('3|4', '(3, 4)')
    assert same['correct'] is True
    assert same['normalized_correct'] == '(3, 4)'
    assert same['normalized_user'] == '(3, 4)'

    comma = check_vector('3|4', '3, 4')
    assert comma['correct'] is True

    pipe = check_vector('-2|5', '-2|5')
    assert pipe['correct'] is True

    pmatrix = check_vector('1|2', r'\begin{pmatrix} 1 \\ 2 \end{pmatrix}')
    assert pmatrix['correct'] is True

    fraction = check_vector('1/2|3', '0.5, 3')
    assert fraction['correct'] is True

    bad = check_vector('3|4', '(3, 5)')
    assert bad['correct'] is False

    empty = check_vector('3|4', '')
    assert empty['correct'] is False

    via_registry = check_answer('vector', '3|4', '3, 4')
    assert via_registry['correct'] is True

    rounded_unit = check_vector('0.707|0.707', '0.7, 0.7')
    assert rounded_unit['correct'] is True

    strict_dp = check_vector('0.707|0.707|dp:3', '0.7, 0.7')
    assert strict_dp['correct'] is False

    strict_ok = check_vector('0.707|0.707|dp:3', '0.707, 0.707')
    assert strict_ok['correct'] is True


def test_checker_linear_equation_and_keyword_unit():
    eq = check_linear_equation('3|5', 'y = 3x + 5')
    assert eq['correct'] is True

    eq_colon = check_linear_equation('2:3', 'y=2x-3')
    assert eq_colon['correct'] is False

    pos = check_keyword('positive', 'positive correlation')
    assert pos['correct'] is True

    neg = check_keyword('negative', 'Negative')
    assert neg['correct'] is True

    text_ok = check_text('malicious|software', 'Malicious software damages systems')
    assert text_ok['correct'] is True
    assert text_ok['confidence'] == 'high'

    av = check_text(
        'scan|malware',
        'Scans files and memory for known malware signatures and suspicious behaviour',
    )
    assert av['correct'] is True, av

    av_synonym = check_text(
        'scan|malware',
        'Antivirus software detects viruses and other threats on the computer',
    )
    assert av_synonym['correct'] is True, av_synonym

    energy_ok = check_text('energy|waste', 'High energy use and e-waste from old devices')
    assert energy_ok['correct'] is True

    text_partial = check_text('malicious|software', 'It is malicious')
    assert text_partial['correct'] is False
    assert text_partial['score'] == 1
    assert text_partial['score_total'] == 2
    assert text_partial['confidence'] == 'medium'

    ram_ok = check_text('register|cpu', 'A CPU register is very fast storage')
    assert ram_ok['correct'] is True

    via_registry = check_answer('text', 'personal|data', 'Protects personal data')
    assert via_registry['correct'] is True


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


# Answer depends on a random branch (terminating vs. recurring decimal); only the
# terminating branch is graded, so a single call can legitimately be ungraded.
DEC_SOMETIMES_UNGRADED_VARIANTS = {'gcse_dec_fraction_to_decimal'}
DEC_UNGRADED_VARIANTS = set()
DEC_ORDER_MIXED_VARIANTS = {'gcse_dec_practice_order_mixed'}
DEC_NUMBER_LIST_VARIANTS = {'gcse_dec_ordering'}
DEC_FRACTION_VARIANTS = {'gcse_dec_practice_decimal_to_fraction', 'gcse_dec_recurring'}
DEC_NUMBER_PAIR_VARIANTS = {'gcse_dec_practice_bounds', 'gcse_dec_proc_bounds_dynamic'}


def test_decimals_variant_queue_is_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_decimals_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            if name in DEC_UNGRADED_VARIANTS:
                problem = gcse_maths_decimals(difficulty, 'practice', variant_name=name)
                assert problem.get('correct_answer_raw') is None, name
                continue
            if name in DEC_SOMETIMES_UNGRADED_VARIANTS:
                graded = [
                    gcse_maths_decimals(difficulty, 'practice', variant_name=name)
                    for _ in range(20)
                ]
                assert any(p.get('correct_answer_raw') is not None for p in graded), name
                assert all(p.get('answer_type') in (None, 'number') for p in graded), name
                continue
            problem = gcse_maths_decimals(difficulty, 'practice', variant_name=name)
            assert problem.get('correct_answer_raw') is not None, name
            if name in DEC_NUMBER_LIST_VARIANTS:
                assert problem.get('answer_type') == 'number_list', name
            elif name in DEC_ORDER_MIXED_VARIANTS:
                assert problem.get('answer_type') == 'proof_steps', name
            elif name in DEC_FRACTION_VARIANTS:
                assert problem.get('answer_type') == 'fraction', name
            elif name in DEC_NUMBER_PAIR_VARIANTS:
                assert problem.get('answer_type') == 'number_pair', name
            else:
                assert problem.get('answer_type') == 'number', name


def test_decimals_ordering_uses_number_list_checker():
    out = gcse_dec_ordering()
    problem = _dec_problem_from_output(out, 'foundational')
    assert problem.get('answer_type') == 'number_list'
    raw = problem['correct_answer_raw']
    result = check_answer('number_list', raw, raw)
    assert result['correct'] is True


def test_decimals_order_mixed_uses_order_checker():
    out = gcse_dec_practice_order_mixed()
    problem = _dec_problem_from_output(out, 'intermediate')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_step_bank')
    assert problem.get('answer_order_matters') is True


def test_decimals_recurring_uses_fraction_checker():
    out = gcse_dec_recurring()
    problem = _dec_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'fraction'
    raw = problem['correct_answer_raw']
    result = check_answer('fraction', raw, raw)
    assert result['correct'] is True


def test_decimals_check_api():
    problem = gcse_maths_decimals(
        'intermediate', 'practice', variant_name='gcse_dec_practice_bounds'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'number_pair'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': correct,
                'correct_answer_raw': correct,
                'answer_type': 'number_pair',
                'level': 'gcse', 'subject': 'maths', 'topic': 'decimals',
                'difficulty': 'intermediate',
            },
        )
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


MF_UNGRADED_VARIANTS = set()
MF_MCQ_VARIANTS = {
    'gcse_mf_find_factor',
    'gcse_mf_prime_factors',
}
MF_PICK_VARIANTS = {
    'gcse_mf_factor_pairs',
}
MF_DIVISIBILITY_VARIANTS = {
    'gcse_mf_divisibility_digit',
}
MF_KEYWORD_VARIANTS = {'gcse_mf_prime', 'gcse_mf_lcm_buses_word'}
MF_NUMBER_PAIR_VARIANTS = {'gcse_mf_hcf_lcm_product_rule'}
MF_NUMBER_LIST_VARIANTS = {'gcse_mf_primes_in_range'}


def test_multiples_factors_variant_queue_is_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_multiples_factors_variants(difficulty, 'practice')
        assert variants, difficulty
        for fn in variants:
            name = fn.__name__
            problem = gcse_maths_multiples_factors(difficulty, 'practice', variant_name=name)
            if name in MF_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, name
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, name
            if name in MF_KEYWORD_VARIANTS:
                assert problem.get('answer_type') == 'keyword', name
            elif name in MF_MCQ_VARIANTS:
                assert problem.get('options'), name
                assert problem.get('correct_answer'), name
            elif name in MF_PICK_VARIANTS:
                assert problem.get('answer_type') == 'proof_steps', name
            elif name in MF_DIVISIBILITY_VARIANTS:
                assert (
                    problem.get('answer_type') == 'number_list'
                    or problem.get('options')
                ), name
            elif name in MF_NUMBER_PAIR_VARIANTS:
                assert problem.get('answer_type') == 'number_pair', name
            elif name in MF_NUMBER_LIST_VARIANTS:
                assert problem.get('answer_type') == 'number_list', name
            else:
                assert problem.get('answer_type') == 'number', name


def test_multiples_factors_prime_uses_keyword_checker():
    out = gcse_mf_prime()
    problem = _mf_problem_from_output(out, 'foundational')
    assert problem.get('answer_type') == 'keyword'
    raw = problem['correct_answer_raw']
    assert raw in ('yes', 'no')
    result = check_answer('keyword', raw, raw)
    assert result['correct'] is True


def test_multiples_factors_primes_in_range_uses_number_list_checker():
    out = gcse_mf_primes_in_range()
    problem = _mf_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'number_list'
    raw = problem['correct_answer_raw']
    result = check_answer('number_list', raw, raw)
    assert result['correct'] is True


def test_multiples_factors_mcq_variants_are_graded():
    import generators.gcse.maths as m

    for name in MF_MCQ_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _mf_problem_from_output(out, 'foundational')
        assert problem.get('options'), name
        assert problem.get('correct_answer'), name


def test_multiples_factors_pick_variants_are_graded():
    import generators.gcse.maths as m

    for name in MF_PICK_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _mf_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('answer_step_bank'), name


def test_multiples_factors_divisibility_variants_are_graded():
    import generators.gcse.maths as m

    for _ in range(12):
        out = m.gcse_mf_divisibility_digit()
        problem = _mf_problem_from_output(out, 'intermediate')
        graded = (
            problem.get('correct_answer_raw')
            or problem.get('correct_answer')
        )
        assert graded, 'gcse_mf_divisibility_digit'


def test_multiples_factors_check_api():
    problem = gcse_maths_multiples_factors(
        'foundational', 'practice', variant_name='gcse_mf_hcf'
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
                'level': 'gcse', 'subject': 'maths', 'topic': 'multiples_factors',
                'difficulty': 'foundational',
            },
        )
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


FDP_UNGRADED_VARIANTS = set()

FDP_MCQ_VARIANTS = {
    'gcse_fdp_best_value_comparison',
}

FDP_ORDER_VARIANTS = {
    'gcse_fdp_order_mixed_values',
}

FDP_MULTI_STEP_VARIANTS = {
    'gcse_fdp_multi_step',
}

FDP_RECURRING_VARIANTS = {
    'gcse_fdp_recurring',
}

FDP_FRACTION_VARIANTS = (
    'gcse_fdp_decimal_to_fraction',
    'gcse_fdp_percentage_to_fraction',
)

FDP_MULTIPART_VARIANTS = (
    'gcse_fdp_share_in_ratio',
    'gcse_fdp_multi_step',
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
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, name
            if name in FDP_MCQ_VARIANTS:
                assert problem.get('options'), name
            elif name in FDP_ORDER_VARIANTS:
                assert problem.get('answer_type') == 'proof_steps', name
            elif name in FDP_RECURRING_VARIANTS:
                assert problem.get('answer_type') == 'fraction', name


def test_fdp_mcq_variants_are_graded():
    import generators.gcse.maths as m

    for name in FDP_MCQ_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _fdp_problem_from_output(out, 'difficult')
        assert problem.get('options'), name
        assert problem.get('correct_answer'), name


def test_fdp_order_variants_are_graded():
    import generators.gcse.maths as m

    for name in FDP_ORDER_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _fdp_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('answer_step_bank'), name


def test_fdp_recurring_variants_use_fraction_checker():
    import generators.gcse.maths as m

    for name in FDP_RECURRING_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _fdp_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'fraction', name


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

    problem = None
    for _ in range(40):
        candidate = _surd_problem_from_output(m.gcse_surds_show_that_rationalise(), 'difficult')
        raw = candidate.get('correct_answer_raw') or ''
        if candidate.get('answer_type') == 'algebraic_fraction' and raw.startswith('e|'):
            problem = candidate
            break
    assert problem is not None

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


def test_check_algebraic_vector_bc_notation():
    from generators.shared.answer_checkers import check_algebraic

    raw = '(c - b)/2'
    for user in (
        '0.5 BC',
        '0.5BC',
        '1/2 BC',
        'BC/2',
        '1/2*BC',
        '(c-b)/2',
        'c/2 - b/2',
        '0.5*(c-b)',
    ):
        assert check_algebraic(raw, user)['correct'] is True, user
    assert check_algebraic('b*c', 'bc')['correct'] is False


def test_check_proof_steps_order_and_set():
    from generators.shared.answer_checkers import check_proof_steps

    ordered = check_proof_steps('1|s1|s2|s3', 's1|s2|s3')
    assert ordered['correct'] is True
    assert 'step_feedback' not in ordered

    wrong_order = check_proof_steps('1|s1|s2|s3', 's1|s3|s2')
    assert wrong_order['correct'] is False
    assert wrong_order['step_feedback'] == [
        {'id': 's1', 'status': 'correct', 'hint': 'Correct step in the correct place.'},
        {'id': 's3', 'status': 'wrong_order', 'hint': 'This step should be in position 3, not 2.'},
        {'id': 's2', 'status': 'wrong_order', 'hint': 'This step should be in position 2, not 3.'},
    ]
    assert 'Green = correct' in wrong_order['feedback']

    mixed = check_proof_steps('1|s1|s2|s3', 's2|d1|s1|s3')
    assert mixed['correct'] is False
    assert mixed['step_feedback'][0]['status'] == 'wrong_order'
    assert mixed['step_feedback'][1]['status'] == 'wrong'
    assert mixed['step_feedback'][2]['status'] == 'wrong_order'

    assert check_proof_steps('1|s1|s2|s3', 's1|s2')['correct'] is False

    unordered = check_proof_steps('0|c1|c2|c3', 'c3|c1|c2')
    assert unordered['correct'] is True
    wrong_set = check_proof_steps('0|c1|c2|c3', 'c1|c2|c3|d1')
    assert wrong_set['correct'] is False
    assert wrong_set['step_feedback'][-1]['status'] == 'wrong'
    assert check_proof_steps('0|c1|c2|c3', 'c1|c2')['correct'] is False

    pick_two = check_proof_steps('pick|2|c1|c2|c3|c4|c5', 'c1|c3')
    assert pick_two['correct'] is True
    assert pick_two['score'] == 2
    assert pick_two['score_total'] == 2
    assert check_proof_steps('pick|2|c1|c2|c3|c4|c5', 'c1|c2|c3')['correct'] is False
    partial_pick = check_proof_steps('pick|2|c1|c2|c3|c4|c5', 'c1|d1')
    assert partial_pick['correct'] is False
    assert partial_pick['score'] == 1
    assert partial_pick['score_total'] == 2
    assert partial_pick['step_feedback'] == [
        {'id': 'c1', 'status': 'correct', 'hint': 'This is a correct step.'},
        {'id': 'd1', 'status': 'wrong', 'hint': 'This step should not be selected.'},
    ]
    assert '1/2 correct' in partial_pick['feedback']
    pick_three = check_proof_steps('pick|3|c1|c2|c3', 'c1|d1|d2')
    assert pick_three['correct'] is False
    assert pick_three['score'] == 1
    assert pick_three['score_total'] == 3
    assert pick_three['feedback'].startswith('1/3 correct')
    assert check_proof_steps('pick|2|c1|c2|c3|c4|c5', 'c1')['correct'] is False


def test_cy_gdpr_principles_pick_from_bank():
    from generators.gcse.cs_cyber_security import _cy_d2_gdpr_principle, _cy_problem_from_output

    out = _cy_d2_gdpr_principle()
    assert len(out) == 5
    problem = _cy_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 2
    assert problem.get('correct_answer_raw', '').startswith('pick|2|')
    bank = problem.get('answer_step_bank') or []
    assert len(bank) == 9
    ids = {step['id'] for step in bank}
    assert {'c1', 'c2', 'c3', 'c4', 'c5', 'd1', 'd2', 'd3', 'd4'}.issubset(ids)


def test_cy_worm_vs_virus_pick_from_bank():
    from generators.gcse.cs_cyber_security import _cy_d12_worm_vs_virus, _cy_problem_from_output

    out = _cy_d12_worm_vs_virus()
    assert len(out) == 5
    problem = _cy_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 2
    assert problem.get('correct_answer_raw', '').startswith('pick|2|')
    assert len(problem.get('answer_step_bank') or []) == 8


def test_cy_multipart_data_protection_inline_fields():
    from generators.gcse.cs_cyber_security import _cy_d14_multipart_data_protection, _cy_problem_from_output

    out = _cy_d14_multipart_data_protection()
    assert len(out) == 5
    problem = _cy_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_types') == ['mcq', 'pick', 'mcq']
    assert problem.get('answer_field_pick_counts') == [None, 2, None]
    assert len(problem.get('answer_field_options') or []) == 3
    pick_bank = (problem.get('answer_field_options') or [])[1]
    assert len(pick_bank) == 6


def test_cy_multipart_attack_scenario_inline_fields():
    from generators.gcse.cs_cyber_security import _cy_d13_multipart_attack_scenario, _cy_problem_from_output

    out = _cy_d13_multipart_attack_scenario()
    assert len(out) == 5
    problem = _cy_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert problem.get('answer_field_types') == ['mcq', 'mcq', 'pick']
    assert problem.get('answer_field_pick_counts') == [None, None, 3]
    raw = problem.get('correct_answer_raw') or ''
    assert '\x1e' in raw
    parts = raw.split('\x1e')
    assert len(parts) == 3
    assert parts[0] in 'ABC'
    assert parts[1] in 'ABC'
    assert parts[2].startswith('pick|3|')
    opts = problem.get('answer_field_options') or []
    assert any('Phishing' in str(o) for o in opts[0])
    assert any('trick' in str(o).lower() or 'manipulat' in str(o).lower() for o in opts[1])


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
        r = _post_problems_check(
            client,
            {
                'user_answer': 'a - b',
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'algebraic',
            },
            headers={'Accept': 'application/json'}
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
}

AF_FRACTION_VARIANTS = (
    '_af_f_cancel_numeric',
    '_af_f_multiply',
    '_af_f_same_denominator_add',
    '_af_f_divide',
    '_af_i_diff_denominator_add',
    '_af_i_single_fraction_add',
    '_af_i_multiply_two',
    '_af_d_add_reciprocal_style',
    '_af_d_subtract_fractions',
)

AF_ALGEBRAIC_VARIANTS = (
    '_af_i_difference_of_squares',
    '_af_i_quadratic_cancel',
)

AF_NUMBER_VARIANTS = (
    '_af_f_factor_cancel',
    '_af_d_simplify_nested',
)

AF_LINEAR_VARIANTS = (
    '_af_d_solve_simple',
    '_af_d_equation_with_linear_den',
)


def test_af_fraction_variants_use_stacked_fraction_ui():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_FRACTION_VARIANTS:
        for _ in range(12):
            out = getattr(af_mod, name)()
            assert len(out) >= 5, name
            raw = out[4]
            if isinstance(raw, int):
                problem = _af_problem_from_output(out, 'foundational')
                assert problem.get('answer_type') == 'number', name
                break
            problem = _af_problem_from_output(out, 'foundational')
            assert problem.get('answer_type') == 'algebraic_fraction', name
            assert '|' in (problem.get('correct_answer_raw') or ''), name
            break


def test_af_number_variants_are_graded():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_NUMBER_VARIANTS:
        out = getattr(af_mod, name)()
        assert len(out) == 5, name
        problem = _af_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw'), name


def test_af_linear_variants_are_graded():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_LINEAR_VARIANTS:
        out = getattr(af_mod, name)()
        assert len(out) == 5, name
        problem = _af_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'linear', name
        assert problem.get('correct_answer_raw'), name


def test_af_algebraic_variants_are_graded():
    import generators.gcse.algebraic_fractions as af_mod

    for name in AF_ALGEBRAIC_VARIANTS:
        out = getattr(af_mod, name)()
        assert len(out) == 5, name
        problem = _af_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'algebraic', name
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
        if candidate.get('answer_type') == 'algebraic_fraction':
            pilot = candidate
            break
        if candidate.get('answer_type') == 'number':
            continue
    assert pilot is not None
    assert pilot.get('correct_answer_raw') is not None
    assert '|' in pilot['correct_answer_raw']

    number_pilot = _af_problem(_af_f_factor_cancel, 'foundational')
    assert number_pilot.get('answer_type') == 'number'


def test_af_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_algebraic_fractions_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_algebraic_fractions(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in AF_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            assert problem.get('correct_answer_raw') is not None, (
                difficulty,
                variant.__name__,
            )


def test_af_check_api_fraction():
    problem = None
    for _ in range(20):
        candidate = gcse_algebraic_fractions(
            'foundational', 'practice', variant_name='_af_f_cancel_numeric'
        )
        if candidate.get('answer_type') == 'algebraic_fraction':
            problem = candidate
            break
    assert problem is not None
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebraic_fractions',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic_fraction',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_af_check_api_number():
    problem = gcse_algebraic_fractions(
        'foundational', 'practice', variant_name='_af_f_factor_cancel'
    )
    assert problem.get('answer_type') == 'number'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebraic_fractions',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_af_diff_denominator_check_api_accepts_equivalent():
    problem = gcse_algebraic_fractions(
        'intermediate', 'practice', variant_name='_af_i_diff_denominator_add'
    )
    assert problem.get('answer_type') == 'algebraic_fraction'
    raw = problem['correct_answer_raw']
    num, den = raw.split('|', 1)

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebraic_fractions',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic_fraction',
                'user_answer': f'{num}|{den}',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_af_stacked_fraction_partial_renders():
    with app.test_request_context():
        from flask import render_template

        html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '39|6x',
                'answer_type': 'algebraic_fraction',
                'answer_format_hint': 'Enter the numerator and denominator',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='algebraic_fractions',
            fr_difficulty='intermediate',
        )
        assert 'free-response-row--algebraic-fraction' in html
        assert 'free-response-input-alg-frac-num' in html
        assert 'free-response-input-alg-frac-den' in html
        assert html.count('free-response-check-btn') == 1


def test_check_general_algebraic_fraction_equivalence():
    assert check_algebraic_fraction('39|6x', '13|2x')['correct'] is True
    assert check_algebraic_fraction('39|6x', '39|6x')['correct'] is True
    assert check_algebraic_fraction('3|4', '6|8')['correct'] is True
    assert check_algebraic_fraction('39|6x', '39|3x')['correct'] is False
    assert check_algebraic_fraction('x+2|x+5', 'x+2|x+5')['correct'] is True
    assert check_algebraic_fraction('x+2|x+5', 'x+3|x+5')['correct'] is False


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


def test_number_prime_factor_product_uses_mcq():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    problem = _number_problem_from_output(
        num_mod._number_inter_prime_factor_product(), 'intermediate'
    )
    assert problem.get('options') and len(problem['options']) == 4
    assert problem.get('correct_answer') in 'ABCD'


def test_number_recurring_decimal_uses_fraction_checker():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    problem = _number_problem_from_output(
        num_mod._number_diff_recurring_decimal_fraction(), 'difficult'
    )
    assert problem.get('answer_type') == 'fraction'
    assert problem.get('correct_answer_raw')
    assert '/' in problem['correct_answer_raw']


def test_all_number_practice_variants_graded():
    import generators.gcse.maths_num_stats_prob_rat as num_mod

    for name in dir(num_mod):
        if not name.startswith('_number_'):
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


DATA_REP_UNGRADED = ()


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


def test_dr_lossy_lossless_pick_fields():
    from generators.gcse.cs_data_rep import gcse_data_rep

    problem = gcse_data_rep('difficult', 'practice', variant_name='_dr_d10_lossy_lossless_compare')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, 1]
    assert problem.get('answer_labels') == ['Lossy advantage', 'Lossless advantage']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 6
    assert len(opts[1]) == 6
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('pick|1|')


def test_dr_metadata_pick_fields():
    from generators.gcse.cs_data_rep import gcse_data_rep

    problem = gcse_data_rep('difficult', 'practice', variant_name='_dr_d12_metadata_vs_payload')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, 1]
    assert problem.get('answer_labels') == ['Why metadata is useful', 'Privacy concern']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 6
    assert len(opts[1]) == 6
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('pick|1|')


def test_data_rep_overflow_unicode_mcq_variants():
    from generators.shared.answer_checkers import check_mcq

    overflow = gcse_data_rep(
        'intermediate', 'practice', variant_name='_dr_i6_overflow'
    )
    assert overflow.get('answer_type') == 'number_fields'
    assert overflow.get('answer_field_types') == ['mcq']
    assert overflow.get('correct_answer_raw') in 'ABCD'
    assert check_mcq(overflow['correct_answer_raw'], overflow['correct_answer_raw'])['correct'] is True

    unicode_q = gcse_data_rep(
        'intermediate', 'practice', variant_name='_dr_i7_unicode_vs_ascii'
    )
    assert unicode_q.get('answer_type') == 'number_fields'
    assert unicode_q.get('answer_field_types') == ['mcq']
    assert unicode_q.get('correct_answer_raw') in 'ABCD'
    assert check_mcq(unicode_q['correct_answer_raw'], unicode_q['correct_answer_raw'])['correct'] is True


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
    from generators.shared.answer_checkers import check_text

    problem = _dr_problem_from_output(
        dr_mod._dr_d13_multipart_number_systems(), 'difficult'
    )
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert len(problem.get('answer_labels') or []) == 3
    assert problem.get('answer_field_types') == ['binary', 'hex', 'text']
    assert '\x1e' in problem['correct_answer_raw']
    parts = problem['correct_answer_raw'].split('\x1e')
    assert len(parts) == 3
    assert check_answer('binary', parts[0], parts[0].split('|', 1)[1])['correct'] is True
    assert check_answer('hex', parts[1], parts[1].split('|', 1)[1])['correct'] is True
    assert parts[2].startswith('2@')
    assert check_text(parts[2], 'hexadecimal is shorter and easier to read than binary')['correct'] is True
    assert check_text(parts[2], 'one hex digit')['correct'] is False


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


DB_SQL_UNGRADED = (
)


def test_db_sql_variants_are_graded():
    import generators.gcse.gcse_cs_db_sql_lesson as db_mod

    for pool in (db_mod._FOUNDATIONAL, db_mod._INTERMEDIATE, db_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _db_problem_from_output(out, 'intermediate')
            if fn.__name__ in DB_SQL_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            if problem.get('options') and problem.get('correct_answer'):
                continue
            assert problem.get('answer_type') in (
                'text', 'sql', 'number_fields', 'proof_steps',
            ), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_db_sql_write_query_exact_grading():
    from generators.shared.answer_checkers import check_sql

    problem = gcse_db_sql('intermediate', 'practice', variant_name='_db_i2_where_example')
    assert problem.get('answer_type') == 'sql'
    raw = problem.get('correct_answer_raw') or ''
    assert check_sql(raw, 'SELECT Surname FROM Pupil WHERE YearGroup = 11')['correct'] is True
    assert check_sql(raw, 'SELECT * FROM Pupil')['correct'] is False

    insert = gcse_db_sql('intermediate', 'practice', variant_name='_db_i4_insert')
    assert insert.get('answer_type') == 'sql'
    assert insert.get('answer_input_lines') == 3
    assert check_sql(
        insert['correct_answer_raw'],
        "INSERT INTO Pupil (PupilID, FirstName, YearGroup) VALUES (42, 'Ali', 10)",
    )['correct'] is True

    group = gcse_db_sql('difficult', 'practice', variant_name='_db_d11_count_group')
    canonical = group['correct_answer_raw']
    assert check_sql(
        canonical,
        'SELECT YearGroup, COUNT(PupilID) FROM Pupil GROUP BY YearGroup',
    )['correct'] is True
    assert check_sql(
        canonical,
        'select yeargroup count() from pupil group by yeargroup',
    )['correct'] is False
    assert check_sql(
        canonical,
        'SELECT YearGroup, COUNT(*) FROM Pupil GROUP BY YearGroup',
    )['correct'] is False

    order = gcse_db_sql('difficult', 'practice', variant_name='_db_d2_order_desc')
    partial = check_sql(
        order['correct_answer_raw'],
        'SELECT Score FROM Grade ORDER Score DESC 5',
    )
    assert partial['correct'] is False
    assert partial['score'] >= 8
    assert 'parts correct' in partial['feedback']


def test_db_sql_multipart_query_writing():
    from generators.shared.answer_checkers import check_proof_steps, check_sql

    problem = gcse_db_sql('difficult', 'practice', variant_name='_db_d13_multipart_query_writing')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_types') == ['sql', 'sql', 'pick']
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert check_sql(
        parts[0],
        "SELECT FirstName, Surname FROM Member WHERE Town = 'Leeds'",
    )['correct'] is True
    assert check_sql(
        parts[1],
        "SELECT * FROM Member WHERE Age >= 18 ORDER BY Surname ASC",
    )['correct'] is True
    pick_ids = parts[2].split('|')[2:]
    assert check_proof_steps(parts[2], '|'.join(pick_ids[:1]))['correct'] is True


def test_db_sql_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_db_sql_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            if variant.__name__ in DB_SQL_UNGRADED:
                continue
            problem = gcse_db_sql(difficulty, 'practice', variant_name=variant.__name__)
            graded = problem.get('correct_answer_raw') or (
                problem.get('options') and problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_db_sql_mcq_option_length_not_biased():
    """Correct MCQ option should not always be the longest (avoids length tell)."""
    import generators.gcse.gcse_cs_db_sql_lesson as db_mod

    mcq_fns = []
    for pool in (db_mod._FOUNDATIONAL, db_mod._INTERMEDIATE, db_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            if len(out) >= 5 and isinstance(out[4], dict) and out[4].get('type') == 'mcq':
                mcq_fns.append(fn)

    longest_correct = 0
    trials = 0
    for fn in mcq_fns:
        for _ in range(20):
            problem = _db_problem_from_output(fn(), 'intermediate')
            opts = [o.split('  ', 1)[1] for o in problem['options']]
            idx = ord(problem['correct_answer']) - ord('A')
            if len(opts[idx]) == max(len(o) for o in opts):
                longest_correct += 1
            trials += 1

    bank_longest = 0
    for _ in range(100):
        problem = gcse_db_sql('foundational', 'mcq')
        opts = problem['options']
        ans = problem['correct_answer']
        texts = [o.split('  ', 1)[1] for o in opts]
        idx = ord(ans) - ord('A')
        if len(texts[idx]) == max(len(t) for t in texts):
            bank_longest += 1

    assert trials > 0
    assert longest_correct / trials < 0.45, longest_correct / trials
    assert bank_longest / 100 < 0.55, bank_longest / 100


def test_db_sql_check_api():
    problem = gcse_db_sql('foundational', 'practice', variant_name='_db_i1_select_star')
    assert problem.get('answer_type') == 'sql'
    assert problem.get('answer_input_lines') == 1
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'db_sql',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'sql',
                'user_answer': 'SELECT * FROM Pupil',
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'correct_answer_raw': raw,
                'answer_type': 'sql',
                'user_answer': 'SELECT Pupil FROM *',
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is False


SYSTEMS_SOFTWARE_UNGRADED = (
)


def test_systems_software_variants_are_graded():
    import generators.gcse.gcse_cs_systems_software_lesson as sw_mod

    for pool in (sw_mod._FOUNDATIONAL, sw_mod._INTERMEDIATE, sw_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _sw_problem_from_output(out, 'intermediate')
            if fn.__name__ in SYSTEMS_SOFTWARE_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            if problem.get('options') and problem.get('correct_answer'):
                continue
            assert problem.get('answer_type') in (
                'text', 'number_fields', 'proof_steps',
            ), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_systems_software_classify_match_fields():
    problem = gcse_systems_software(
        'difficult', 'practice', variant_name='_sw_d10_classify_software'
    )
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq', 'mcq', 'mcq']
    assert len(problem.get('answer_field_options') or []) == 4


def test_systems_software_multipart_inline_fields():
    from generators.shared.answer_checkers import check_proof_steps

    os_mgmt = gcse_systems_software(
        'difficult', 'practice', variant_name='_sw_d13_multipart_os_management'
    )
    assert os_mgmt.get('answer_type') == 'number_fields'
    assert os_mgmt.get('answer_inline_sections') is True
    assert os_mgmt.get('answer_field_types') == ['pick', 'pick', 'pick']
    assert os_mgmt.get('answer_field_pick_counts') == [2, 2, 2]
    parts = (os_mgmt.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    for part in parts:
        pick_count = int(part.split('|', 2)[1])
        pick_ids = part.split('|')[2:]
        assert check_proof_steps(part, '|'.join(pick_ids[:pick_count]))['correct'] is True

    utilities = gcse_systems_software(
        'difficult', 'practice', variant_name='_sw_d14_multipart_utilities'
    )
    assert utilities.get('answer_inline_sections') is True
    assert utilities.get('answer_field_types') == ['pick', 'pick', 'pick']
    assert utilities.get('answer_field_pick_counts') == [1, 1, 2]


def test_systems_software_exam_pick_variants():
    os_funcs = gcse_systems_software(
        'difficult', 'practice', variant_name='_sw_d6_exam_os_functions'
    )
    assert os_funcs.get('answer_type') == 'proof_steps'
    assert os_funcs.get('answer_pick_count') == 5
    assert os_funcs.get('correct_answer_raw', '').startswith('pick|5|')

    utilities = gcse_systems_software(
        'difficult', 'practice', variant_name='_sw_d7_exam_utilities'
    )
    assert utilities.get('answer_pick_count') == 3


def test_systems_software_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_systems_software_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            if variant.__name__ in SYSTEMS_SOFTWARE_UNGRADED:
                continue
            problem = gcse_systems_software(
                difficulty, 'practice', variant_name=variant.__name__
            )
            graded = problem.get('correct_answer_raw') or (
                problem.get('options') and problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_systems_software_check_api():
    problem = gcse_systems_software(
        'foundational', 'practice', variant_name='_sw_f9_file_management'
    )
    assert problem.get('answer_type') == 'proof_steps'
    raw = problem['correct_answer_raw']
    pick_count = int(raw.split('|', 2)[1])
    pick_ids = raw.split('|')[2:][:pick_count]

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'systems_software',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'proof_steps',
                'user_answer': '|'.join(pick_ids),
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_systems_software_mcq_option_length_not_biased():
    """Correct MCQ option should not always be the longest (avoids length tell)."""
    import generators.gcse.gcse_cs_systems_software_lesson as sw_mod

    mcq_fns = []
    for pool in (sw_mod._FOUNDATIONAL, sw_mod._INTERMEDIATE, sw_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            if len(out) >= 5 and isinstance(out[4], dict) and out[4].get('type') == 'mcq':
                mcq_fns.append(fn)

    longest_correct = 0
    trials = 0
    for fn in mcq_fns:
        for _ in range(20):
            problem = _sw_problem_from_output(fn(), 'intermediate')
            opts = [o.split('  ', 1)[1] for o in problem['options']]
            idx = ord(problem['correct_answer']) - ord('A')
            if len(opts[idx]) == max(len(o) for o in opts):
                longest_correct += 1
            trials += 1

    bank_longest = 0
    for _ in range(100):
        problem = gcse_systems_software('foundational', 'mcq')
        opts = problem['options']
        ans = problem['correct_answer']
        texts = [o.split('  ', 1)[1] for o in opts]
        idx = ord(ans) - ord('A')
        if len(texts[idx]) == max(len(t) for t in texts):
            bank_longest += 1

    assert trials > 0
    assert longest_correct / trials < 0.45, longest_correct / trials
    assert bank_longest / 100 < 0.55, bank_longest / 100


ALGORITHMS_UNGRADED = (
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
            graded = problem.get('correct_answer_raw') or (
                problem.get('options') and problem.get('correct_answer')
            )
            assert graded, fn.__name__
            if problem.get('options') and problem.get('correct_answer'):
                continue
            assert problem.get('answer_type') in (
                'number', 'number_fields', 'proof_steps', 'text', 'keyword',
            ), fn.__name__


def test_algorithms_binary_pseudocode_fix():
    from generators.shared.answer_checkers import check_mcq, check_text, check_number

    problem = gcse_algorithms(
        'difficult', 'practice', variant_name='_alg_d6_pseudocode_binary'
    )
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_types') == [
        'mcq', 'text', 'number', 'text', 'number', 'number',
    ]
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 6
    assert parts[0] in 'ABC'
    assert check_mcq(parts[0], parts[0])['correct'] is True
    assert check_text(parts[1], 'mid ← (low + high) DIV 2')['correct'] is True
    assert check_text(parts[1], 'mid = (low + high) / 2')['correct'] is False
    assert check_number(parts[2], '2')['correct'] is True
    assert check_text(parts[3], 'found ← FALSE')['correct'] is True
    assert check_number(parts[4], '8')['correct'] is True
    assert check_number(parts[5], '10')['correct'] is True
    assert 'three faults' in (problem.get('question') or '').lower()


def test_algorithms_multipart_numeric_fields():
    import generators.gcse.cs_algorithms as alg_mod
    from generators.shared.answer_checkers import check_number_fields

    search = _alg_problem_from_output(
        alg_mod._alg_d13_multipart_search_compare(), 'difficult'
    )
    assert search.get('answer_type') == 'number_fields'
    assert search.get('answer_inline_sections') is True
    assert search.get('answer_field_types') == ['mcq', 'number', 'mcq']
    parts = (search.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert parts[0] in 'ABC'
    assert check_number_fields(parts[1], parts[1])['correct'] is True
    assert parts[2] in 'ABC'
    opts = search.get('answer_field_options') or []
    assert opts[0] and 'Binary search' in opts[0]
    assert opts[2] and any('ordered' in str(o) for o in opts[2])

    trace = _alg_problem_from_output(
        alg_mod._alg_d14_multipart_trace_table(), 'difficult'
    )
    assert trace.get('answer_type') == 'number_fields'
    assert trace.get('answer_inline_sections') is True
    assert trace.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert trace.get('answer_field_row_sizes') == [4, 1, 1]
    assert trace.get('answer_field_group_labels') == ['(a)', '(b)', '(c)']
    assert 'number' in (trace.get('answer_field_types') or [])
    assert 'mcq' in (trace.get('answer_field_types') or [])
    assert trace['correct_answer_raw'].split('\x1e')[4] == '10'
    assert trace['correct_answer_raw'].split('\x1e')[5] in 'ABC'


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
            graded = problem.get('correct_answer_raw') or (
                problem.get('options') and problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_algorithms_mcq_option_length_not_biased():
    import generators.gcse.cs_algorithms as alg_mod

    mcq_fns = []
    for pool in (alg_mod._FOUNDATIONAL, alg_mod._INTERMEDIATE, alg_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            if len(out) >= 5 and isinstance(out[4], dict) and out[4].get('type') == 'mcq':
                mcq_fns.append(fn)

    longest_correct = 0
    trials = 0
    for fn in mcq_fns:
        for _ in range(20):
            problem = _alg_problem_from_output(fn(), 'intermediate')
            opts = [o.split('  ', 1)[1] for o in problem['options']]
            idx = ord(problem['correct_answer']) - ord('A')
            if len(opts[idx]) == max(len(o) for o in opts):
                longest_correct += 1
            trials += 1

    bank_longest = 0
    for _ in range(100):
        problem = gcse_algorithms('foundational', 'mcq')
        texts = [o.split('  ', 1)[1] for o in problem['options']]
        idx = ord(problem['correct_answer']) - ord('A')
        if len(texts[idx]) == max(len(t) for t in texts):
            bank_longest += 1

    assert trials > 0
    assert longest_correct / trials < 0.45, longest_correct / trials
    assert bank_longest / 100 < 0.55, bank_longest / 100


def test_algorithms_order_and_pick_variants():
    from generators.shared.answer_checkers import check_proof_steps

    decomp = gcse_algorithms(
        'foundational', 'practice', variant_name='_alg_f2_decomposition'
    )
    assert decomp.get('answer_type') == 'proof_steps'
    assert decomp.get('answer_order_matters') is True
    raw = decomp.get('correct_answer_raw') or ''
    assert raw.startswith('1|')
    step_ids = raw.split('|')[1:]
    assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True

    compare = gcse_algorithms(
        'intermediate', 'practice', variant_name='_alg_i8_linear_vs_binary'
    )
    assert compare.get('answer_type') == 'proof_steps'
    assert compare.get('answer_pick_count') == 2
    assert (compare.get('correct_answer_raw') or '').startswith('pick|2|')

    flowchart = gcse_algorithms(
        'intermediate', 'practice', variant_name='_alg_i9_flowchart_to_pseudo'
    )
    assert flowchart.get('answer_type') == 'proof_steps'
    assert flowchart.get('answer_order_matters') is True
    assert flowchart.get('answer_pick_count') is None
    hint = (flowchart.get('answer_format_hint') or '').lower()
    assert '6' not in hint and 'six' not in hint
    assert 'how many' not in hint
    flow_raw = flowchart.get('correct_answer_raw') or ''
    assert flow_raw.startswith('1|')
    flow_ids = flow_raw.split('|')[1:]
    assert len(flow_ids) == 6
    assert len(flowchart.get('answer_step_bank') or []) > 6
    assert check_proof_steps(flow_raw, '|'.join(flow_ids))['correct'] is True
    assert check_proof_steps(flow_raw, '|'.join(flow_ids[:3]))['correct'] is False

    linear = gcse_algorithms(
        'difficult', 'practice', variant_name='_alg_d15_pseudocode_linear'
    )
    assert linear.get('answer_type') == 'proof_steps'
    assert linear.get('answer_order_matters') is True
    assert linear.get('answer_pick_count') is None
    lin_hint = (linear.get('answer_format_hint') or '').lower()
    assert '11' not in lin_hint and 'eleven' not in lin_hint
    assert 'how many' not in lin_hint
    lin_raw = linear.get('correct_answer_raw') or ''
    assert lin_raw.startswith('1|')
    lin_ids = lin_raw.split('|')[1:]
    assert len(lin_ids) == 11
    assert len(linear.get('answer_step_bank') or []) > 11
    assert check_proof_steps(lin_raw, '|'.join(lin_ids))['correct'] is True
    assert check_proof_steps(lin_raw, '|'.join(lin_ids[:5]))['correct'] is False


def test_algorithms_flowchart_fix_variants():
    from generators.shared.answer_checkers import check_mcq, check_proof_steps

    f12 = gcse_algorithms(
        'foundational', 'practice', variant_name='_alg_f12_flowchart_fix_decision'
    )
    assert f12.get('answer_type') == 'number_fields'
    assert f12.get('answer_field_types') == ['mcq']
    assert f12.get('correct_answer_raw') in 'ABCD'
    assert '<svg' in (f12.get('question') or '').lower()
    assert 'flowchart' in (f12.get('question') or '').lower()
    assert check_mcq(f12['correct_answer_raw'], f12['correct_answer_raw'])['correct'] is True

    i11 = gcse_algorithms(
        'intermediate', 'practice', variant_name='_alg_i11_flowchart_fix_symbols'
    )
    assert i11.get('answer_type') == 'proof_steps'
    assert i11.get('answer_pick_count') == 2
    assert '<svg' in (i11.get('question') or '').lower()
    raw = i11.get('correct_answer_raw') or ''
    assert raw.startswith('pick|2|')
    pick_ids = raw.split('|')[2:]
    assert len(pick_ids) == 2
    assert check_proof_steps(raw, '|'.join(pick_ids))['correct'] is True

    d16 = gcse_algorithms(
        'difficult', 'practice', variant_name='_alg_d16_flowchart_fix_multipart'
    )
    assert d16.get('answer_type') == 'number_fields'
    assert d16.get('answer_inline_sections') is True
    assert d16.get('answer_field_types') == ['mcq', 'mcq', 'mcq']
    assert d16.get('answer_field_group_labels') == ['(a)', '(b)', '(c)']
    assert '<svg' in (d16.get('question') or '').lower()
    parts = (d16.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert all(p in 'ABCD' for p in parts)
    assert check_mcq(parts[0], parts[0])['correct'] is True
    assert check_mcq(parts[1], parts[1])['correct'] is True
    assert check_mcq(parts[2], parts[2])['correct'] is True


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
)

CYBER_UNGRADED = (
)

ETHICAL_UNGRADED = (
)

NETWORKS_UNGRADED = (
)

PYTHON_MCQ_VARIANTS = (
    'py_found_hello',
    'py_found_for',
    'py_found_index',
    'py_found_modulo',
    'py_inter_fizzbuzz',
)

PYTHON_RUN_VARIANTS = (
    'py_found_age',
)

PYTHON_TIER3_VARIANTS = ()


def _python_graded_run_variant_names():
    return tuple(
        name for name in _python_write_code_variant_names()
        if name not in PYTHON_MCQ_VARIANTS
    )


def _python_write_code_variant_names():
    import generators.gcse.cs as py_mod

    names = []
    for name in dir(py_mod):
        if not (
            name.startswith('py_found_')
            or name.startswith('py_inter_')
            or name.startswith('py_diff_')
        ):
            continue
        fn = getattr(py_mod, name)
        if callable(fn):
            names.append(name)
    return names


def test_python_mcq_variants_are_graded():
    import generators.gcse.cs as py_mod

    for name in PYTHON_MCQ_VARIANTS:
        out = getattr(py_mod, name)()
        assert len(out) == 5, name
        difficulty = (
            'foundational'
            if name.startswith('py_found_')
            else 'intermediate'
            if name.startswith('py_inter_')
            else 'difficult'
        )
        problem = _py_problem_from_output(out, difficulty)
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name


def test_python_ungraded_variants_remain_ungraded():
    import generators.gcse.cs as py_mod

    graded = set(PYTHON_MCQ_VARIANTS) | set(_python_graded_run_variant_names())
    ungraded = []
    for name in _python_write_code_variant_names():
        if name in graded:
            continue
        out = getattr(py_mod, name)()
        problem = _py_problem_from_output(out, 'intermediate')
        if problem.get('correct_answer_raw') or problem.get('correct_answer'):
            continue
        ungraded.append(name)
    assert ungraded == [], f'unexpected ungraded: {ungraded}'


def test_python_run_variants_are_graded():
    import generators.gcse.cs as py_mod

    for name in _python_graded_run_variant_names():
        out = getattr(py_mod, name)()
        assert len(out) == 5, name
        difficulty = (
            'foundational'
            if name.startswith('py_found_')
            else 'intermediate'
            if name.startswith('py_inter_')
            else 'difficult'
        )
        problem = _py_problem_from_output(out, difficulty)
        assert problem.get('answer_type') == 'python_run', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_tests'), name
        assert len(problem['answer_tests']) >= 1, name


def test_python_run_checker_unit():
    import json

    from generators.gcse.cs import py_found_age

    out = py_found_age()
    problem = _py_problem_from_output(out, 'foundational')
    raw = problem['correct_answer_raw']
    good = json.dumps([
        {'stdout': t['stdout']} for t in problem['answer_tests']
    ])
    assert check_answer('python_run', raw, good)['correct'] is True
    bad = json.dumps([{'stdout': 'wrong'}] * len(problem['answer_tests']))
    assert check_answer('python_run', raw, bad)['correct'] is False
    err = json.dumps([{'stdout': '', 'error': 'ValueError'}])
    assert check_answer('python_run', raw, err)['correct'] is False


def test_python_run_error_sanitizer():
    import json

    from generators.shared.answer_checkers import _sanitize_python_student_error

    leaky = (
        'Traceback (most recent call last):\n'
        '  File "/lib/python311.zip/_pyodide/_base.py", line 501, in eval_code\n'
        '  File "<student>", line 2\n'
        "    while password = 'secure':\n"
        '    ^^^^^^^^^^^^^^^^^^^^\n'
        "SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?"
    )
    cleaned = _sanitize_python_student_error(leaky)
    assert '_pyodide' not in cleaned
    assert '/lib/python' not in cleaned
    assert 'your code' in cleaned
    assert 'line 2' in cleaned
    assert 'SyntaxError' in cleaned

    result = check_answer(
        'python_run',
        '[{"stdout":"Access granted."}]',
        json.dumps([{'stdout': '', 'error': leaky}]),
    )
    assert result['correct'] is False
    assert '_pyodide' not in result['feedback']
    assert 'your code' in result['feedback']


def test_python_run_rejects_password_loop_without_input():
    import json

    from generators.gcse.cs import py_inter_password

    problem = _py_problem_from_output(py_inter_password(), 'intermediate')
    raw = problem['correct_answer_raw']
    assert '"min_inputs":2' in raw.replace(' ', '')

    skipped_loop = json.dumps([
        {'stdout': 'Access granted.', 'input_calls': 0},
        {'stdout': 'Access granted.', 'input_calls': 0},
    ])
    assert check_answer('python_run', raw, skipped_loop)['correct'] is False

    correct_calls = json.dumps([
        {'stdout': 'Access granted.', 'input_calls': 2},
        {'stdout': 'Access granted.', 'input_calls': 3},
    ])
    assert check_answer('python_run', raw, correct_calls)['correct'] is True


def test_python_tier3_variants_are_graded():
    import json

    from generators.gcse.cs import (
        py_diff_file,
        py_diff_read_scores_file,
        py_found_variables,
    )

    vars_problem = _py_problem_from_output(py_found_variables(), 'foundational')
    assert vars_problem.get('answer_type') == 'python_run'
    assert '"validate":"variables_triple"' in vars_problem['correct_answer_raw'].replace(' ', '')
    ok_vars = json.dumps([{'stdout': 'Alice 16 1.65', 'input_calls': 0}])
    assert check_answer('python_run', vars_problem['correct_answer_raw'], ok_vars)['correct']
    bad_vars = json.dumps([{'stdout': '16 16 16', 'input_calls': 0}])
    assert not check_answer('python_run', vars_problem['correct_answer_raw'], bad_vars)['correct']

    file_problem = _py_problem_from_output(py_diff_file(), 'difficult')
    assert file_problem.get('answer_tests')[0].get('files')
    file_ok = json.dumps([
        {'stdout': '1: first line\n2: second line', 'input_calls': 1},
        {'stdout': 'File not found.', 'input_calls': 1},
    ])
    assert check_answer('python_run', file_problem['correct_answer_raw'], file_ok)['correct']

    scores_problem = _py_problem_from_output(py_diff_read_scores_file(), 'difficult')
    scores_ok = json.dumps([
        {'stdout': 'Highest: 90\nAverage: 65.6', 'input_calls': 0},
        {'stdout': 'Highest: 30\nAverage: 20.0', 'input_calls': 0},
    ])
    assert check_answer('python_run', scores_problem['correct_answer_raw'], scores_ok)['correct']


def test_python_run_check_api():
    import json

    problem = gcse_python_programming(
        'foundational', 'practice', variant_name='py_found_age'
    )
    assert problem.get('answer_type') == 'python_run'
    payload = json.dumps([
        {'stdout': t['stdout']} for t in problem['answer_tests']
    ])
    result = check_answer('python_run', problem['correct_answer_raw'], payload)
    assert result.get('normalized_correct')
    assert result.get('normalized_user')

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'python_programming',
                'difficulty': 'foundational',
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': 'python_run',
                'user_answer': payload,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_python_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        pool = gcse_python_variants(difficulty, 'practice')
        assert pool, difficulty
        for variant in pool:
            problem = gcse_python_programming(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in PYTHON_MCQ_VARIANTS:
                assert problem.get('correct_answer') in 'ABCD', variant.__name__
                assert problem.get('options'), variant.__name__
                continue
            assert problem.get('answer_type') == 'python_run', variant.__name__
            assert problem.get('correct_answer_raw'), variant.__name__
            assert problem.get('answer_tests'), variant.__name__


def test_python_mcq_check_api():
    problem = gcse_python_programming(
        'foundational', 'practice', variant_name='py_found_hello'
    )
    letter = problem['correct_answer']
    assert letter in 'ABCD'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'python_programming',
                'difficulty': 'foundational',
                'correct_answer_raw': letter,
                'answer_type': 'mcq',
                'user_answer': letter,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


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
            if problem.get('options') and problem.get('correct_answer'):
                continue
            assert problem.get('answer_type') in ('number', 'text', 'keyword', 'number_fields', 'proof_steps'), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_cs_embedded_constraints_pick_from_bank():
    from generators.gcse.cs_computer_systems import gcse_computer_systems

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d3_embedded_constraints')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 2
    assert problem.get('correct_answer_raw', '').startswith('pick|2|')
    assert len(problem.get('answer_step_bank') or []) == 8


def test_cs_fde_trace_order_steps():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d1_fde_full_trace')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_order_matters') is True
    raw = problem.get('correct_answer_raw') or ''
    assert raw.startswith('1|')
    step_ids = raw.split('|')[1:]
    assert len(step_ids) == 3
    assert len(problem.get('answer_step_bank') or []) == 6
    assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True
    assert check_proof_steps(raw, '|'.join(reversed(step_ids)))['correct'] is False


def test_cs_bios_role_order_steps():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d8_bios_role')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_order_matters') is True
    raw = problem.get('correct_answer_raw') or ''
    assert raw.startswith('1|')
    step_ids = raw.split('|')[1:]
    assert len(step_ids) == 4
    assert len(problem.get('answer_step_bank') or []) == 7
    assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True


def test_cs_multi_core_pick_from_bank():
    from generators.gcse.cs_computer_systems import gcse_computer_systems

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d12_multi_core')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 2
    assert problem.get('correct_answer_raw', '').startswith('pick|2|')
    assert len(problem.get('answer_step_bank') or []) == 7


def test_cs_multipart_cpu_performance_inline_fields():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d13_multipart_cpu_performance')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert problem.get('answer_field_types') == ['mcq', 'order', 'order']
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert parts[0] in ('A', 'B', 'C')
    assert parts[1].startswith('1|')
    assert parts[2].startswith('1|')
    core_ids = parts[1].split('|')[1:]
    cache_ids = parts[2].split('|')[1:]
    assert len(core_ids) == 2
    assert len(cache_ids) == 2
    assert check_proof_steps(parts[1], '|'.join(core_ids))['correct'] is True
    assert check_proof_steps(parts[1], '|'.join(reversed(core_ids)))['correct'] is False
    assert check_proof_steps(parts[2], '|'.join(cache_ids))['correct'] is True
    opts = problem.get('answer_field_options') or []
    assert len(opts[0]) == 3
    assert len(opts[1]) == 5
    assert len(opts[2]) == 5


def test_cs_open_source_os_text_keywords():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_text

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d10_open_source_os')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['text', 'text']
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('1@')
    assert parts[1].startswith('1@')
    assert check_text(parts[0], 'transparent')['correct'] is True
    assert check_text(parts[0], 'free to modify the source code')['correct'] is True
    assert check_text(parts[1], 'learning is difficult')['correct'] is True
    assert check_text(parts[1], 'fewer drivers for some hardware')['correct'] is True


def test_cs_d14_multipart_memory_inline_fields():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_proof_steps, check_text

    problem = gcse_computer_systems('difficult', 'practice', variant_name='_cs_d14_multipart_memory')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_types') == ['pick', 'text', 'text']
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert parts[0].startswith('pick|1|')
    assert check_text(parts[1], 'secondary storage used when RAM is full')['correct'] is True
    assert check_text(parts[2], 'slower than RAM causes thrashing')['correct'] is True
    pick_ids = parts[0].split('|')[2:]
    assert check_proof_steps(parts[0], '|'.join(pick_ids[:1]))['correct'] is True


def test_cs_intermediate_pick_variants():
    from generators.gcse.cs_computer_systems import gcse_computer_systems

    for variant_name in (
        '_cs_i1_von_neumann',
        '_cs_i2_cache_purpose',
        '_cs_i5_utility_software',
        '_cs_i6_storage_compare',
        '_cs_i7_clock_cores',
        '_cs_i8_fetch_step',
        '_cs_i9_app_vs_system',
    ):
        problem = gcse_computer_systems('intermediate', 'practice', variant_name=variant_name)
        assert problem.get('answer_type') == 'proof_steps', variant_name
        assert problem.get('correct_answer_raw', '').startswith('pick|'), variant_name


def test_cs_difficult_pick_order_variants():
    from generators.gcse.cs_computer_systems import gcse_computer_systems

    pick_variants = (
        '_cs_d3_embedded_constraints',
        '_cs_d4_optical_storage',
        '_cs_d7_hdd_defrag',
        '_cs_d11_control_bus',
        '_cs_d12_multi_core',
    )
    order_variants = (
        '_cs_d6_multitasking_os',
    )
    for variant_name in pick_variants:
        problem = gcse_computer_systems('difficult', 'practice', variant_name=variant_name)
        assert problem.get('answer_type') == 'proof_steps', variant_name
        assert problem.get('correct_answer_raw', '').startswith('pick|'), variant_name
    for variant_name in order_variants:
        problem = gcse_computer_systems('difficult', 'practice', variant_name=variant_name)
        assert problem.get('answer_type') == 'proof_steps', variant_name
        assert problem.get('correct_answer_raw', '').startswith('1|'), variant_name


def test_cs_foundational_graded_variants():
    from generators.gcse.cs_computer_systems import gcse_computer_systems
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_computer_systems('foundational', 'practice', variant_name='_cs_f5_fde_order')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_order_matters') is True
    raw = problem.get('correct_answer_raw') or ''
    step_ids = raw.split('|')[1:]
    assert len(step_ids) == 3
    assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True

    problem = gcse_computer_systems('foundational', 'practice', variant_name='_cs_f10_embedded')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 1
    assert problem.get('correct_answer_raw', '').startswith('pick|1|')


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
            if problem.get('options') and problem.get('correct_answer'):
                continue
            assert problem.get('answer_type') in (
                'number', 'text', 'keyword', 'number_fields', 'proof_steps',
            ), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__


def test_computer_networks_multipart_inline():
    from generators.shared.answer_checkers import check_proof_steps

    home = gcse_computer_networks(
        'difficult', 'practice', variant_name='_net_d13_multipart_home_network'
    )
    assert home.get('answer_type') == 'number_fields'
    assert home.get('answer_inline_sections') is True
    assert home.get('answer_field_types') == ['pick', 'pick', 'pick']
    parts = (home.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    lan_ids = parts[0].split('|')[2:]
    assert check_proof_steps(parts[0], '|'.join(lan_ids[:1]))['correct'] is True

    proto = gcse_computer_networks(
        'difficult', 'practice', variant_name='_net_d14_multipart_protocols'
    )
    assert proto.get('answer_field_types') == ['pick', 'pick', 'pick']


def test_computer_networks_mcq_option_length_not_biased():
    import generators.gcse.cs_computer_networks as net_mod

    mcq_fns = []
    for pool in (net_mod._FOUNDATIONAL, net_mod._INTERMEDIATE, net_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            if len(out) >= 5 and isinstance(out[4], dict) and out[4].get('type') == 'mcq':
                mcq_fns.append(fn)

    longest_correct = 0
    trials = 0
    for fn in mcq_fns:
        for _ in range(20):
            problem = _net_problem_from_output(fn(), 'intermediate')
            opts = [o.split('  ', 1)[1] for o in problem['options']]
            idx = ord(problem['correct_answer']) - ord('A')
            if len(opts[idx]) == max(len(o) for o in opts):
                longest_correct += 1
            trials += 1

    bank_longest = 0
    for _ in range(100):
        problem = gcse_computer_networks('foundational', 'mcq')
        texts = [o.split('  ', 1)[1] for o in problem['options']]
        idx = ord(problem['correct_answer']) - ord('A')
        if len(texts[idx]) == max(len(t) for t in texts):
            bank_longest += 1

    assert trials > 0
    assert longest_correct / trials < 0.45, longest_correct / trials
    assert bank_longest / 100 < 0.55, bank_longest / 100


def test_cyber_security_definition_variants_are_graded():
    import generators.gcse.cs_cyber_security as cy_mod

    weak_text = []
    for pool in (cy_mod._FOUNDATIONAL, cy_mod._INTERMEDIATE, cy_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _cy_problem_from_output(out, 'intermediate')
            if fn.__name__ in CYBER_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('answer_type') in (
                'number_fields', 'proof_steps',
            ), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__
            if problem.get('answer_type') in ('text', 'keyword'):
                weak_text.append(fn.__name__)
    assert not weak_text, weak_text


def test_ethical_definition_variants_are_graded():
    import generators.gcse.gcse_cs_ethical_lesson as eth_mod

    weak_text = []
    for pool in (eth_mod._FOUNDATIONAL, eth_mod._INTERMEDIATE, eth_mod._DIFFICULT):
        for fn in pool:
            out = fn()
            problem = _eth_problem_from_output(out, 'intermediate')
            if fn.__name__ in ETHICAL_UNGRADED:
                assert len(out) == 4, fn.__name__
                assert not problem.get('correct_answer_raw'), fn.__name__
                continue
            assert len(out) == 5, fn.__name__
            assert problem.get('answer_type') in (
                'number_fields', 'proof_steps',
            ), fn.__name__
            assert problem.get('correct_answer_raw'), fn.__name__
            if problem.get('answer_type') in ('text', 'keyword'):
                weak_text.append(fn.__name__)
    assert not weak_text, weak_text


def test_cs_definition_topics_check_api():
    from generators.shared.answer_checkers import check_mcq

    malware = gcse_cyber_security('foundational', 'practice', variant_name='_cy_f1_malware_virus')
    gdpr = gcse_ethical('foundational', 'practice', variant_name='_eth_f2_gdpr')
    ram = gcse_computer_systems('foundational', 'practice', variant_name='_cs_f3_ram_vs_rom')

    with app.test_client() as client:
        register(client, 'text42@example.com', 'text42user')
        for topic, problem in (
            ('cyber_security', malware),
            ('ethical', gdpr),
            ('computer_systems', ram),
        ):
            field_types = problem.get('answer_field_types') or []
            if field_types == ['mcq']:
                check_type = 'mcq'
                user_answer = 'A' if problem['correct_answer_raw'] != 'A' else 'B'
            else:
                check_type = problem['answer_type']
                user_answer = 'placeholder'
            payload = {
                'user_answer': user_answer,
                'correct_answer_raw': problem['correct_answer_raw'],
                'answer_type': check_type,
                'level': 'gcse',
                'subject': 'cs',
                'topic': topic,
                'difficulty': 'foundational',
            }
            if field_types:
                payload['answer_field_types'] = field_types
            r = client.post(
                '/api/v1/problems/check',
                json=payload,
                headers={'Accept': 'application/json'},
            )
            assert r.status_code == 200, (topic, r.data)

        letter = malware['correct_answer_raw']
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': letter,
                'correct_answer_raw': letter,
                'answer_type': 'mcq',
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'cyber_security',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        assert r.get_json()['correct'] is True
        assert check_mcq(letter, letter)['correct'] is True


def test_cy_practice_definition_mcq_variants():
    from generators.shared.answer_checkers import check_mcq

    for variant_name in (
        '_cy_f1_malware_virus',
        '_cy_f3_firewall',
        '_cy_f7_ransomware',
        '_cy_f10_trojan',
        '_cy_i1_dos',
        '_cy_i4_symmetric',
        '_cy_i6_sql_injection',
        '_cy_d1_pen_test',
        '_cy_d10_risk_assessment',
    ):
        diff = 'foundational'
        if variant_name.startswith('_cy_i'):
            diff = 'intermediate'
        elif variant_name.startswith('_cy_d'):
            diff = 'difficult'
        problem = gcse_cyber_security(diff, 'practice', variant_name=variant_name)
        assert problem.get('answer_type') == 'number_fields', variant_name
        assert problem.get('answer_field_types') == ['mcq'], variant_name
        letter = problem.get('correct_answer_raw')
        assert letter in 'ABCD', variant_name
        assert check_mcq(letter, letter)['correct'] is True


def test_cy_backup_match_mcq():
    problem = gcse_cyber_security('intermediate', 'practice', variant_name='_cy_i10_backup')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq']
    assert problem.get('answer_labels') == ['Full backup', 'Incremental backup']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2 and all(len(row) == 3 for row in opts)


def test_eth_multipart_legislation_inline_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d14_multipart_legislation')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert problem.get('answer_field_types') == ['mcq', 'mcq', 'pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [None, None, 1, 1]
    law_opts = (problem.get('answer_field_options') or [])[0]
    assert 'Computer Misuse Act 1990' in law_opts


def test_eth_wearable_select_all_impacts():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d2_wearable_implant')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_order_matters') is False
    assert not problem.get('answer_pick_count')
    raw = problem.get('correct_answer_raw') or ''
    assert raw.startswith('0|')
    assert len(problem.get('answer_step_bank') or []) == 8
    correct_ids = raw.split('|')[1:]
    assert check_proof_steps(raw, '|'.join(correct_ids))['correct'] is True
    assert check_proof_steps(raw, '|'.join(correct_ids[:2]))['correct'] is False


def test_eth_privacy_debate_pick_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d1_privacy_debate')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_labels') == ['Citizens value', 'Governments argue']
    assert problem.get('answer_field_pick_counts') == [1, 1]
    opts = problem.get('answer_field_options') or []
    assert len(opts[0]) == 7
    assert len(opts[1]) == 6


def test_eth_mixed_scenario_pick_from_bank():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d10_mixed_scenario')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 3
    assert problem.get('correct_answer_raw', '').startswith('pick|3|')
    bank = problem.get('answer_step_bank') or []
    assert len(bank) == 12
    assert all(' — ' in step['text'] for step in bank)


def test_eth_job_automation_pick_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d5_job_automation')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, 1]
    assert problem.get('answer_labels') == ['Positive impact', 'Negative impact']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 6
    assert len(opts[1]) == 6
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('pick|1|')


def test_eth_implant_ethics_pick_from_bank():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d8_implant_ethics')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 1
    assert problem.get('correct_answer_raw', '').startswith('pick|1|')
    assert len(problem.get('answer_step_bank') or []) == 10


def test_split_question_sections_html_markers():
    from app import split_question_sections

    q = (
        "A technology company releases a new smartphone every year.<br><br>"
        "<strong>a)</strong> Describe one impact. [2]<br>"
        "<strong>b)</strong> Describe one problem. [2]<br>"
        "<strong>c)</strong> Suggest two ways. [2]"
    )
    parts = split_question_sections(q, ['(a)', '(b)', '(c)'])
    assert parts['intro'].startswith('A technology company')
    assert len(parts['sections']) == 3
    assert parts['sections'][0]['text'].startswith('<strong>a)</strong>')
    assert parts['sections'][1]['text'].startswith('<strong>b)</strong>')
    assert parts['sections'][2]['text'].startswith('<strong>c)</strong>')

    q_roman = (
        "O is the centre. Angle AOB = 100°.<br>"
        "<strong>(i)</strong> Find angle OAB.<br>"
        "<strong>(ii)</strong> Find angle ACB.<br>"
        "<strong>(iii)</strong> Find angle ADB.<br>"
        "<strong>(iv)</strong> Select the correct relationship."
    )
    parts_roman = split_question_sections(q_roman, ['(i)', '(ii)', '(iii)', '(iv)'])
    assert parts_roman['intro'].startswith('O is the centre')
    assert len(parts_roman['sections']) == 4
    assert parts_roman['sections'][0]['text'].startswith('<strong>(i)</strong>')
    assert parts_roman['sections'][1]['text'].startswith('<strong>(ii)</strong>')
    assert parts_roman['sections'][2]['text'].startswith('<strong>(iii)</strong>')
    assert parts_roman['sections'][3]['text'].startswith('<strong>(iv)</strong>')


def test_eth_multipart_smartphone_lifecycle_inline_fields():
    from generators.gcse.gcse_cs_ethical_lesson import _eth_d13_multipart_smartphone_lifecycle, _eth_problem_from_output

    out = _eth_d13_multipart_smartphone_lifecycle()
    assert len(out) == 5
    problem = _eth_problem_from_output(out, 'difficult')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)']
    assert problem.get('answer_field_types') == ['pick', 'pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, 1, 2]
    raw = problem.get('correct_answer_raw') or ''
    assert '\x1e' in raw
    parts = raw.split('\x1e')
    assert len(parts) == 3
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('pick|1|')
    assert parts[2].startswith('pick|2|')
    assert len((problem.get('answer_field_options') or [])[2]) == 8


def test_eth_right_to_erasure_pick_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d11_right_to_erasure')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, None]
    assert problem.get('answer_inline_sections') is True
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 6
    assert len(opts[1]) == 8
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('0|')
    retention_ids = parts[1].split('|')[1:]
    assert check_proof_steps(parts[1], '|'.join(retention_ids))['correct'] is True
    assert check_proof_steps(parts[1], '|'.join(retention_ids[:2]))['correct'] is False


def test_eth_exam_structure_order_steps():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d9_exam_structure')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_order_matters') is True
    raw = problem.get('correct_answer_raw') or ''
    assert raw.startswith('1|')
    step_ids = raw.split('|')[1:]
    assert len(step_ids) == 3
    assert len(problem.get('answer_step_bank') or []) == 7
    assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True
    assert check_proof_steps(raw, '|'.join(reversed(step_ids)))['correct'] is False


def test_eth_breach_response_order_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d7_breach_response')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['order', 'order']
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('1|')
    assert parts[1].startswith('1|')
    legal_ids = parts[0].split('|')[1:]
    assert check_proof_steps(parts[0], '|'.join(legal_ids))['correct'] is True
    assert check_proof_steps(parts[0], '|'.join(reversed(legal_ids)))['correct'] is False


def test_eth_patent_trademark_match_mcq():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i9_patent_trademark')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq']
    assert problem.get('answer_labels') == ['Patent', 'Trademark']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2 and all(len(row) == 3 for row in opts)


def test_eth_ai_bias_definition_and_example_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i7_ai_bias')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(a)', '(b)']
    assert problem.get('answer_field_types') == ['mcq', 'pick']
    assert problem.get('answer_field_pick_counts') == [None, 1]
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0] in 'ABC'
    assert parts[1].startswith('pick|1|')
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 3
    assert any('unfair' in str(o).lower() for o in opts[0])
    assert len(opts[1]) == 6


def test_eth_licence_compare_select_all_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical
    from generators.shared.answer_checkers import check_proof_steps

    problem = gcse_ethical('difficult', 'practice', variant_name='_eth_d6_licence_compare')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [None, None]
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 8
    assert len(opts[1]) == 9
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('0|')
    assert parts[1].startswith('0|')
    os_ids = parts[0].split('|')[1:]
    prop_ids = parts[1].split('|')[1:]
    assert check_proof_steps(parts[0], '|'.join(os_ids))['correct'] is True
    assert check_proof_steps(parts[1], '|'.join(prop_ids))['correct'] is True
    assert check_proof_steps(parts[0], '|'.join(os_ids[:2]))['correct'] is False


def test_eth_surveillance_pick_fields():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i6_surveillance')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['pick', 'pick']
    assert problem.get('answer_field_pick_counts') == [1, 1]
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert len(opts[0]) == 6
    assert len(opts[1]) == 7
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 2
    assert parts[0].startswith('pick|1|')
    assert parts[1].startswith('pick|1|')


def test_eth_cma_offences_pick_from_bank():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i2_cma_offences')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 2
    assert problem.get('correct_answer_raw', '').startswith('pick|2|')
    assert len(problem.get('answer_step_bank') or []) == 7


def test_eth_planned_obsolescence_match_mcq():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i4_planned_obsolescence')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq']
    assert problem.get('answer_labels') == ['Planned obsolescence', 'Environmental concern']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2 and all(len(row) == 3 for row in opts)


def test_eth_gdpr_principles_pick_from_bank():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('intermediate', 'practice', variant_name='_eth_i1_gdpr_principles')
    assert problem.get('answer_type') == 'proof_steps'
    assert problem.get('answer_pick_count') == 3
    assert problem.get('correct_answer_raw', '').startswith('pick|3|')
    assert len(problem.get('answer_step_bank') or []) == 11


def test_eth_definition_mcq_variants():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    for variant_name in ('_eth_f3_copyright', '_eth_f5_open_source', '_eth_i3_copyright_example'):
        difficulty = 'intermediate' if variant_name.startswith('_eth_i') else 'foundational'
        problem = gcse_ethical(difficulty, 'practice', variant_name=variant_name)
        assert problem.get('answer_type') == 'number_fields', variant_name
        assert problem.get('answer_field_types') == ['mcq'], variant_name
        assert problem.get('correct_answer_raw') in 'ABCD', variant_name
        opts = (problem.get('answer_field_options') or [])[0]
        assert len(opts) == 4, variant_name
        assert not problem.get('options'), variant_name
        assert not problem.get('correct_answer'), variant_name


def test_eth_ethical_vs_legal_match_mcq():
    from generators.gcse.gcse_cs_ethical_lesson import gcse_ethical

    problem = gcse_ethical('foundational', 'practice', variant_name='_eth_f10_ethical_vs_legal')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq']
    assert problem.get('answer_labels') == ['Ethical', 'Legal']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2 and all(len(row) == 3 for row in opts)
    raw = problem.get('correct_answer_raw') or ''
    assert '\x1e' in raw


def test_cy_auth_vs_authz_match_mcq():
    problem = gcse_cyber_security('intermediate', 'practice', variant_name='_cy_i7_auth_vs_authz')
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_field_types') == ['mcq', 'mcq']
    opts = problem.get('answer_field_options') or []
    assert len(opts) == 2
    assert all(len(row) == 3 for row in opts)
    assert 'Authentication' in (problem.get('answer_labels') or [])
    raw = problem['correct_answer_raw']
    assert '\x1e' in raw
    parts = raw.split('\x1e')
    assert len(parts) == 2
    assert all(p in 'ABC' for p in parts)


def test_cs_text_partial_score_recorded():
    import uuid

    from models.user import User, normalize_email
    from models.user_data import list_generator_mcq_attempts
    from app import get_db

    email = f'pt_{uuid.uuid4().hex[:8]}@example.com'
    handle = f'pt{uuid.uuid4().hex[:6]}'
    problem = gcse_cyber_security('foundational', 'practice', variant_name='_cy_f5_strong_password')
    correct_raw = problem['correct_answer_raw']
    one_correct = correct_raw.split('|')[2]
    with app.test_client() as client:
        register(client, email, handle)
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': one_correct,
                'correct_answer_raw': correct_raw,
                'answer_type': problem['answer_type'],
                'answer_step_bank': problem.get('answer_step_bank'),
                'answer_pick_count': problem.get('answer_pick_count'),
                'answer_order_matters': problem.get('answer_order_matters'),
                'level': 'gcse',
                'subject': 'cs',
                'topic': 'cyber_security',
                'difficulty': 'foundational',
            },
            headers={'Accept': 'application/json'},
        )
        data = r.get_json()
        assert data['correct'] is False
        assert data['score'] == 1
        assert data['score_total'] == 2

        with get_db() as conn:
            user = User.get_by_email(conn, normalize_email(email))
            attempts = list_generator_mcq_attempts(conn, user.id, limit=1)
            assert attempts
            latest = attempts[0]
            assert latest['score'] == 1
            assert latest['score_total'] == 2
            assert latest['correct'] == 0


def test_cs_text_problems_expose_grading_keywords():
    from generators.shared.answer_checkers import check_proof_steps

    av = gcse_cyber_security('foundational', 'practice', variant_name='_cy_f4_antivirus')
    assert av.get('answer_type') == 'number_fields'
    assert av.get('answer_field_types') == ['mcq']
    assert av.get('correct_answer_raw') in 'ABCD'
    assert len((av.get('answer_field_options') or [])[0]) == 4

    phys = gcse_cyber_security('foundational', 'practice', variant_name='_cy_f8_physical_security')
    assert phys.get('answer_type') == 'proof_steps'
    assert phys.get('answer_pick_count') == 2
    assert len(phys.get('answer_step_bank') or []) >= 5
    assert phys['correct_answer_raw'].startswith('pick|2|')

    full = check_proof_steps(phys['correct_answer_raw'], '|'.join(
        phys['correct_answer_raw'].split('|')[2:4]
    ))
    assert full['correct'] is True, full
    assert full['score'] == 2

    one_measure = check_proof_steps(phys['correct_answer_raw'], phys['correct_answer_raw'].split('|')[2])
    assert one_measure['correct'] is False
    assert one_measure['score'] == 1
    assert one_measure['score_total'] == 2

    bio = gcse_cyber_security('difficult', 'practice', variant_name='_cy_d4_bio_vs_password')
    assert bio.get('answer_type') == 'number_fields'
    assert bio.get('answer_field_types') == ['pick', 'pick']
    assert bio.get('answer_labels') == ['Advantage', 'Risk']
    assert len(bio.get('answer_field_options') or []) == 2


def test_cs_definition_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variants, ungraded, gen in (
            (gcse_cyber_security_variants, CYBER_UNGRADED, gcse_cyber_security),
            (gcse_ethical_variants, ETHICAL_UNGRADED, gcse_ethical),
        ):
            pool = variants(difficulty, 'practice')
            assert pool, difficulty
            for variant in pool:
                if variant.__name__ in ungraded:
                    continue
                problem = gen(difficulty, 'practice', variant_name=variant.__name__)
                assert problem.get('correct_answer_raw'), (difficulty, variant.__name__)
                assert problem.get('answer_type') in ('keyword', 'number_fields', 'proof_steps'), variant.__name__


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
                graded = problem.get('correct_answer_raw') or (
                    problem.get('options') and problem.get('correct_answer')
                )
                assert graded, (difficulty, variant.__name__)


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


EQ_LINEAR_VARIANTS = (
    '_eq_found_one_step_add',
    '_eq_found_two_step',
    '_eq_found_fraction_eq',
    '_eq_inter_both_sides',
    '_eq_inter_word_perimeter',
    '_eq_diff_quadratic_from_geometry',
)

EQ_QUADRATIC_VARIANTS = (
    '_eq_diff_quadratic_factorise',
    '_eq_diff_quadratic_formula_generated',
)

EQ_UNGRADED_VARIANTS = (
)

EQ_MULTIPART_NUMBER_FIELDS_VARIANTS = (
    '_eq_diff_cafe_prices_multipart',
    '_eq_diff_phone_plans_multipart',
)

EQ_FORMULA_FRACTION_VARIANTS = (
    '_eq_diff_subject_appears_twice',
    '_eq_found_rearrange_numeric_var',
)

EQ_ALGEBRAIC_REARRANGE_VARIANTS = (
    '_eq_diff_rearrange_complex',
    '_eq_diff_rearrange_kinetic_var',
    '_eq_found_rearrange_one_step',
    '_eq_inter_rearrange_two_step',
    '_eq_inter_rearrange_sqrt',
    '_eq_inter_rearrange_two_step_numeric_var',
)

EQ_SHOW_THAT_CHECKPOINT_VARIANTS = (
    '_eq_diff_prove_identity',
)

EQ_COMPLETED_SQUARE_VARIANTS = (
    '_eq_diff_complete_square',
)

EQ_COORDINATE_PAIRS_VARIANTS = (
    '_eq_diff_simult_one_quadratic',
)

EQ_LINEAR_INEQUALITY_VARIANTS = (
    '_eq_found_simple_inequality',
    '_eq_found_ineq_solve_two_step',
    '_eq_found_write_ineq_from_words',
    '_eq_inter_neg_ineq_flip',
    '_eq_inter_savings_inequality_var',
)

EQ_COMPOUND_INEQUALITY_VARIANTS = (
    '_eq_inter_compound_ineq',
    '_eq_diff_quadratic_ineq',
)

EQ_NUMBER_LINE_VARIANTS = (
    '_eq_inter_ineq_on_number_line',
)


def test_equations_linear_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_LINEAR_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'linear', name
        assert problem.get('correct_answer_raw') is not None, name


def test_equations_quadratic_roots_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_QUADRATIC_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'quadratic_roots', name
        assert problem.get('correct_answer_raw') is not None, name
        assert len(problem.get('answer_labels') or []) >= 2, name


def test_equations_ungraded_variants_remain_ungraded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_UNGRADED_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 4, name
        problem = _eq_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_equations_linear_inequality_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_LINEAR_INEQUALITY_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'linear_inequality', name
        assert problem.get('correct_answer_raw') is not None, name


def test_equations_compound_inequality_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_COMPOUND_INEQUALITY_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'compound_inequality', name
        assert problem.get('correct_answer_raw') is not None, name


def test_equations_number_line_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_NUMBER_LINE_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'number_line', name
        assert problem.get('correct_answer_raw') is not None, name
        assert problem.get('answer_axis_min') is not None, name
        assert problem.get('answer_axis_max') is not None, name
        parts = problem['correct_answer_raw'].split('|')
        assert len(parts) == 5, name
        lo = int(parts[2])
        hi = int(parts[4])
        assert problem['answer_axis_min'] <= lo, name
        assert problem['answer_axis_max'] >= hi, name


def test_equations_formula_fraction_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_FORMULA_FRACTION_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'formula_fraction', name
        assert problem.get('answer_subject'), name
        assert '|' in (problem.get('correct_answer_raw') or ''), name


def test_equations_algebraic_rearrange_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_ALGEBRAIC_REARRANGE_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('answer_subject'), name
        assert problem.get('correct_answer_raw'), name


def test_equations_show_that_checkpoint_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_SHOW_THAT_CHECKPOINT_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('answer_field_types') == [
            'algebraic', 'algebraic', 'algebraic',
        ], name
        parts = problem['correct_answer_raw'].split('\x1e')
        assert len(parts) == 3, name
        assert check_answer('algebraic', parts[2], '12x')['correct'] is True


def test_equations_completed_square_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_COMPLETED_SQUARE_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'completed_square', name
        assert (problem.get('correct_answer_raw') or '').startswith('plus|'), name


def test_equations_coordinate_pairs_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_COORDINATE_PAIRS_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'coordinate_pairs', name
        labels = problem.get('answer_labels') or []
        assert len(labels) == 2, name
        parts = (problem.get('correct_answer_raw') or '').split('|')
        assert len(parts) == 4, name


def test_equations_multipart_number_fields_variants_are_graded():
    import generators.gcse.equations_inequalities as eq_mod

    for name in EQ_MULTIPART_NUMBER_FIELDS_VARIANTS:
        out = getattr(eq_mod, name)()
        assert len(out) == 5, name
        problem = _eq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('correct_answer_raw') is not None, name
        labels = problem.get('answer_labels') or []
        assert len(labels) >= 2, name
        assert '\x1e' in problem['correct_answer_raw'], name
        parts = problem['correct_answer_raw'].split('\x1e')
        assert len(parts) == len(labels), name
        if name == '_eq_diff_cafe_prices_multipart':
            assert len(labels) == 4, name
            assert parts[0].startswith('eq:'), name
            assert parts[1].startswith('eq:'), name
        if name == '_eq_diff_phone_plans_multipart':
            assert len(labels) == 4, name
            assert parts[2].isdigit() or parts[2].replace('.', '', 1).isdigit(), name
            assert '|' in parts[3], name


def test_check_two_var_equation():
    raw = 'eq:c,t:10:11:53'
    assert check_two_var_equation(raw, '10c + 11t = 53')['correct'] is True
    assert check_two_var_equation(raw, '11t + 10c = 53')['correct'] is True
    assert check_two_var_equation(raw, '53 = 10c + 11t')['correct'] is True
    assert check_two_var_equation(raw, '10c+11t=53')['correct'] is True
    assert check_two_var_equation(raw, '10c + 11t = 54')['correct'] is False
    assert check_two_var_equation(raw, '5c + 17t = 61')['correct'] is False


def test_check_linear_inequality():
    assert check_linear_inequality('x|>=|6', 'x|>=|6')['correct'] is True
    assert check_linear_inequality('x|>=|6', 'x|>|6')['correct'] is False
    assert check_linear_inequality('w|<=|20', 'w|<=|20')['correct'] is True


def test_check_compound_inequality():
    assert check_compound_inequality('x|<|2|<=|7', 'x|<|2|<=|7')['correct'] is True
    assert check_compound_inequality('x|<|-2|<|3', 'x|<|-2|<|3')['correct'] is True
    assert check_compound_inequality('x|<|2|<=|7', 'x|<|2|<|7')['correct'] is False


def test_check_number_line():
    assert check_number_line('x|<|0|<|5', 'x|<|0|<|5')['correct'] is True
    assert check_number_line('x|<=|-1|<=|4', 'x|<=|-1|<=|4')['correct'] is True
    assert check_number_line('x|<|0|<|5', 'x|<=|0|<|5')['correct'] is False
    assert check_number_line('x|<|0|<|5', 'x|<|0|<=|5')['correct'] is False
    wrong = check_number_line('x|<|0|<|5', 'x|<|1|<|5')
    assert wrong['correct'] is False
    assert 'endpoint' in wrong['feedback'].lower() or 'circle' in wrong['feedback'].lower()


def test_check_formula_fraction():
    assert check_formula_fraction('d-b|a-c', 'd-b|a-c')['correct'] is True
    assert check_formula_fraction('d-b|a-c', 'd - b|a - c')['correct'] is True
    assert check_formula_fraction('d-b|a-c', 'b-d|c-a')['correct'] is False
    assert check_formula_fraction('d-b|a-c', 'd-b|a-c|extra')['correct'] is False


def test_check_algebraic_kinetic_formula():
    from generators.shared.answer_checkers import check_algebraic

    raw = 'v=√(2e/m)'
    assert check_algebraic(raw, 'v=√(2e/m)')['correct'] is True
    assert check_algebraic(raw, 'v=√((2e)/(m))')['correct'] is True
    assert check_algebraic(raw, 'v=sqrt(2e/m)')['correct'] is True
    assert check_algebraic(raw, 'V=√(2E/m)')['correct'] is True
    assert check_algebraic(raw, 'v=√(2e/m)+1')['correct'] is False

    raw_mass = 'v=√(2e/3)'
    assert check_algebraic(raw_mass, 'v=√(2E/3)')['correct'] is True
    assert check_algebraic(raw_mass, '√2E/√3')['correct'] is True
    assert check_algebraic(raw_mass, 'sqrt(2e/3)')['correct'] is True
    assert check_algebraic(raw_mass, '√(2e/4)')['correct'] is False

    raw_pi = 'r=√(a/π)'
    assert check_algebraic(raw_pi, 'r=√(A/π)')['correct'] is True
    assert check_algebraic(raw_pi, 'r=√(a/pi)')['correct'] is True
    assert check_algebraic(raw_pi, 'r=sqrt(a/pi)')['correct'] is True
    assert check_algebraic(raw_pi, '√A/√π')['correct'] is True
    assert check_algebraic(raw_pi, '√A/√pi')['correct'] is True
    assert check_algebraic(raw_pi, '(√A)/(√π)')['correct'] is True
    assert check_algebraic(raw_pi, '√(A)/√(π)')['correct'] is True
    assert check_algebraic(raw_pi, '√A/√e')['correct'] is False


def test_check_algebraic_power_and_product_flexibility():
    from generators.shared.answer_checkers import check_algebraic

    raw = 'u=(s-3*t^2/2)/(t)'
    for user in (
        '(s-0.5*3*t*t)/t',
        '(s-1.5*t^2)/t',
        '(s-3*t**2/2)/t',
        'u=(s-0.5*3*t^2)/t',
        '(s-3t^2/2)/t',
    ):
        assert check_algebraic(raw, user)['correct'] is True, user
    assert check_algebraic(raw, '(s-3*t^2)/t')['correct'] is False

    raw_mass = 'v=√(2e/10)'
    assert check_algebraic(raw_mass, '√2E/√10')['correct'] is True
    assert check_algebraic(raw_mass, 'v=√2E/√10')['correct'] is True
    assert check_algebraic(raw_mass, '√(2E)/√(10)')['correct'] is True
    assert check_algebraic(raw_mass, 'sqrt(2E)/sqrt(10)')['correct'] is True
    assert check_algebraic(raw_mass, '√2e/√5')['correct'] is False


def test_check_linear_inequality_natural_text():
    assert check_linear_inequality('m|<|40', 'm < 40')['correct'] is True
    assert check_linear_inequality('m|<|40', 'm<40')['correct'] is True
    assert check_linear_inequality('m|<|40', 'm ≤ 40')['correct'] is False
    assert check_linear_inequality('w|<=|20', 'w<=20')['correct'] is True


def test_check_coordinate_pairs():
    raw = '-2|4|4|16'
    assert check_coordinate_pairs(raw, '(-2, 4)|(4, 16)')['correct'] is True
    assert check_coordinate_pairs(raw, '(4, 16)|(-2, 4)')['correct'] is True
    assert check_coordinate_pairs(raw, '-2,4|4,16')['correct'] is True
    assert check_coordinate_pairs(raw, '(-2, 4)|(4, 15)')['correct'] is False
    assert check_coordinate_pairs(raw, '(-2, 4)')['correct'] is False


def test_equations_simple_inequality_check_api():
    problem = gcse_equations_inequalities(
        'foundational', 'practice', variant_name='_eq_found_simple_inequality'
    )
    assert problem.get('answer_type') == 'linear_inequality'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'linear_inequality',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_equations_number_line_check_api():
    problem = gcse_equations_inequalities(
        'intermediate', 'practice', variant_name='_eq_inter_ineq_on_number_line'
    )
    assert problem.get('answer_type') == 'number_line'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'intermediate',
                'correct_answer_raw': correct,
                'answer_type': 'number_line',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        parts = str(correct).split('|')
        assert len(parts) == 5, correct
        parts[1] = '<' if parts[1] == '<=' else '<='
        derived_wrong = '|'.join(parts)
        assert derived_wrong != correct
        wrong = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'intermediate',
                'correct_answer_raw': correct,
                'answer_type': 'number_line',
                'user_answer': derived_wrong,
            },
        )
        assert wrong.status_code == 200
        assert wrong.get_json()['correct'] is False


def test_equations_formula_fraction_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_subject_appears_twice'
    )
    assert problem.get('answer_type') == 'formula_fraction'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'formula_fraction',
                'user_answer': 'd - b|a - c',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_equations_rearrange_complex_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_rearrange_complex'
    )
    assert problem.get('answer_type') == 'algebraic'
    assert problem.get('answer_subject') == 'v'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'algebraic',
                'user_answer': 'v=sqrt(2E/m)',
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        wrong = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'algebraic',
                'user_answer': 'v=√(2e/m)+1',
            }
        )
        assert wrong.status_code == 200
        assert wrong.get_json()['correct'] is False


def test_equations_simult_quadratic_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_simult_one_quadratic'
    )
    assert problem.get('answer_type') == 'coordinate_pairs'
    correct = problem['correct_answer_raw']
    parts = correct.split('|')
    assert len(parts) == 4
    x1, y1, x2, y2 = parts

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'coordinate_pairs',
                'user_answer': f'({x1}, {y1})|({x2}, {y2})',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        swapped = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'coordinate_pairs',
                'user_answer': f'({x2}, {y2})|({x1}, {y1})',
            },
        )
        assert swapped.status_code == 200
        assert swapped.get_json()['correct'] is True


def test_equations_cafe_multipart_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_cafe_prices_multipart'
    )
    assert problem.get('answer_type') == 'number_fields'
    correct = problem['correct_answer_raw']
    parts = correct.split('\x1e')
    assert len(parts) == 4

    with app.test_client() as client:
        eq_parts = parts[0][3:].split(':')
        coef_c, coef_t, total = eq_parts[1], eq_parts[2], eq_parts[3]
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[0],
                'answer_type': 'two_var_equation',
                'user_answer': f'{coef_t}t + {coef_c}c = {total}',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[2],
                'answer_type': 'number',
                'user_answer': parts[2],
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


def test_equations_kinetic_var_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_rearrange_kinetic_var'
    )
    assert problem.get('answer_type') == 'algebraic'
    assert problem.get('answer_subject') == 'v'
    correct = problem['correct_answer_raw']
    assert correct.startswith('v=√(2e/')

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'algebraic',
                'user_answer': correct,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_equations_phone_plans_check_api():
    problem = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_phone_plans_multipart'
    )
    assert problem.get('answer_type') == 'number_fields'
    correct = problem['correct_answer_raw']
    parts = correct.split('\x1e')
    assert len(parts) == 4
    assert problem.get('answer_field_types') == [
        'algebraic', 'algebraic', 'number', 'linear_inequality',
    ]

    with app.test_client() as client:
        r0 = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[0],
                'answer_type': 'algebraic',
                'user_answer': parts[0],
            }
        )
        assert r0.status_code == 200
        assert r0.get_json()['correct'] is True

        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[2],
                'answer_type': 'number',
                'user_answer': parts[2],
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        ineq = parts[3]
        minutes = ineq.split('|')[-1]
        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': ineq,
                'answer_type': 'linear_inequality',
                'user_answer': f'm < {minutes}',
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


def test_equations_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_equations_inequalities_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_equations_inequalities(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in EQ_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_equations_check_api_linear_and_quadratic():
    linear = gcse_equations_inequalities(
        'foundational', 'practice', variant_name='_eq_found_one_step_add'
    )
    assert linear.get('answer_type') == 'linear'
    correct_linear = linear['correct_answer_raw']

    quad = gcse_equations_inequalities(
        'difficult', 'practice', variant_name='_eq_diff_quadratic_factorise'
    )
    assert quad.get('answer_type') == 'quadratic_roots'
    correct_quad = quad['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'foundational',
                'correct_answer_raw': correct_linear,
                'answer_type': 'linear',
                'user_answer': f'x={correct_linear}',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'equations_inequalities',
                'difficulty': 'difficult',
                'correct_answer_raw': correct_quad,
                'answer_type': 'quadratic_roots',
                'user_answer': correct_quad,
            }
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True


VEC_VECTOR_VARIANTS = (
    '_vectors_found_add_simple',
    '_vectors_found_subtract_simple',
    '_vectors_found_displacement',
    '_vectors_inter_path_addition',
)

VEC_COMBO_VARIANTS = (
    '_vectors_diff_geometric_ratio',
    '_vectors_diff_trapezium_ratio',
)

VEC_PAIR_VARIANTS = (
    '_vectors_diff_vector_method_simultaneous',
)

VEC_UNGRADED_VARIANTS = (
)

VEC_PLAN_B_SCAFFOLD_VARIANTS = (
    '_vectors_inter_collinear_points',
    '_vectors_diff_geometry_proof',
    '_vectors_diff_triangle_midpoint',
    '_vectors_diff_vector_proof_sim',
)

VEC_PLAN_C_STEP_BANK_VARIANTS = (
    '_vectors_found_column_meaning',
    '_vectors_diff_vector_inequality',
)


def test_vectors_vector_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in VEC_VECTOR_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _vec_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'vector', name
        assert problem.get('correct_answer_raw') is not None, name


def test_vectors_combo_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in VEC_COMBO_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _vec_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'vector_combo', name
        assert problem.get('answer_labels'), name
        assert problem.get('correct_answer_raw') is not None, name


def test_vectors_trapezium_ratio_check_api():
    problem = gcse_vectors(
        'difficult', 'practice', variant_name='_vectors_diff_trapezium_ratio'
    )
    assert problem.get('answer_type') == 'vector_combo'
    assert problem.get('answer_labels') == ['AB']
    assert problem.get('correct_answer_raw') == '1/2'

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'vectors',
                'difficulty': 'difficult',
                'correct_answer_raw': '1/2',
                'answer_type': 'vector_combo',
                'user_answer': '1/2',
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_check_vector_combo():
    assert check_vector_combo('-2/5|1/5', '-2/5|1/5')['correct'] is True
    assert check_vector_combo('-2/5|1/5', '-4/10|2/10')['correct'] is True
    assert check_vector_combo('-2/5|1/5', '1/5|-2/5')['correct'] is False
    assert check_vector_combo('-2/5|1/5', '-2/5')['correct'] is False


def test_vectors_geometric_ratio_check_api():
    problem = gcse_vectors(
        'difficult', 'practice', variant_name='_vectors_diff_geometric_ratio'
    )
    assert problem.get('answer_type') == 'vector_combo'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'vectors',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'vector_combo',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_vectors_pair_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in VEC_PAIR_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _vec_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'vector_pair', name
        assert problem.get('answer_labels') == ['x', 'y'], name
        assert problem.get('correct_answer_raw') is not None, name


def test_check_vector_pair():
    assert check_vector_pair('5|1|2|7', '5|1|2|7')['correct'] is True
    assert check_vector_pair('5|1|2|7', '5|1|3|7')['correct'] is False
    assert check_vector_pair('5|1|2|7', '5|1|2')['correct'] is False


def test_vectors_simultaneous_check_api():
    problem = gcse_vectors(
        'difficult', 'practice', variant_name='_vectors_diff_vector_method_simultaneous'
    )
    assert problem.get('answer_type') == 'vector_pair'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'vectors',
                'difficulty': 'difficult',
                'correct_answer_raw': correct,
                'answer_type': 'vector_pair',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_vectors_ungraded_variants_remain_ungraded():
    import generators.gcse.maths as maths_mod

    for name in VEC_UNGRADED_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 4, name
        problem = _vec_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_vectors_plan_b_scaffold_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in VEC_PLAN_B_SCAFFOLD_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _vec_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_field_types'), name
        assert len(problem.get('answer_labels') or []) >= 2, name


def test_vectors_plan_c_step_bank_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in VEC_PLAN_C_STEP_BANK_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _vec_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_step_bank'), name


def test_vectors_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_vectors_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_vectors(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in VEC_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


TRIG_NUMBER_VARIANTS = (
    '_trig_found_sin_side',
    '_trig_found_pythagoras',
    '_trig_inter_elevation',
    '_trig_diff_sine_rule_side',
)

TRIG_EXACT_VARIANTS = (
    '_trig_found_exact_values',
    '_trig_diff_exact_compound',
)

TRIG_KEYWORD_VARIANTS = (
    '_trig_inter_converse_pyth',
)

TRIG_UNGRADED_VARIANTS = (
)

TRIG_PLAN_B_SCAFFOLD_VARIANTS = (
    '_trig_inter_exact_expression',
)


def test_trig_number_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in TRIG_NUMBER_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _trig_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw') is not None, name


def test_trig_exact_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in TRIG_EXACT_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _trig_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') in (
            'number', 'fraction', 'surd', 'algebraic_fraction'
        ), name
        assert problem.get('correct_answer_raw') is not None, name


def test_trig_keyword_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in TRIG_KEYWORD_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _trig_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'keyword', name
        assert problem.get('correct_answer_raw') in ('yes', 'no'), name


def test_trig_ungraded_variants_remain_ungraded():
    import generators.gcse.maths as maths_mod

    for name in TRIG_UNGRADED_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 4, name
        problem = _trig_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_trig_plan_b_scaffold_variants_are_graded():
    import generators.gcse.maths as maths_mod

    for name in TRIG_PLAN_B_SCAFFOLD_VARIANTS:
        out = getattr(maths_mod, name)()
        assert len(out) == 5, name
        problem = _trig_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_field_types'), name


def test_trig_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_trigonometry_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_trigonometry(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in TRIG_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


TRANS_COORD_VARIANTS = (
    '_trans_found_translate',
    '_trans_found_reflect_xaxis',
    '_trans_inter_rotate_not_origin',
    '_trans_diff_three_transformations',
)

TRANS_NUMBER_VARIANTS = (
    '_trans_inter_area_after_enlargement',
    '_trans_diff_area_scale_factor',
)

TRANS_MCQ_DESCRIBE_VARIANTS = (
    '_trans_found_describe_translation',
    '_trans_found_describe_reflection_axis',
    '_trans_found_describe_rotation_90',
    '_trans_found_describe_rotation_180',
    '_trans_inter_describe_enlargement_full',
    '_trans_inter_describe_rotation_full',
    '_trans_diff_negative_enlarge_describe',
)

TRANS_FIELDS_MCQ_VARIANTS = (
    '_trans_inter_invariant_reflection',
    '_trans_inter_combination_reflect_reflect',
    '_trans_diff_self_inverse',
    '_trans_diff_invariant_rotation',
    '_trans_diff_combination_single_equiv',
    '_trans_diff_two_reflections_intersecting',
    '_trans_diff_two_reflections_parallel',
    '_trans_diff_congruent_similar',
)

TRANS_UNGRADED_VARIANTS = (
)

CL_NUMBER_VARIANTS = (
    '_cl_f15_scale_drawing_length',
    '_cl_i10_scale_bearing',
    '_cl_i14_count_loci_intersections',
    '_cl_i15_scale_area',
    '_cl_d3_chord_midpoint',
    '_cl_d6_difference_squares',
    '_cl_d11_sector_area_sprinkler',
)

CL_FIELDS_VARIANTS = (
    '_cl_i5_treasure_hunt',
    '_cl_d10_incircle_radius',
    '_cl_d17_treasure_hunt_multi',
    '_cl_d18_triangle_centres_multi',
)

CL_MCQ_VARIANTS = (
    '_cl_f1_equidistant_two_points',
    '_cl_f2_fixed_distance_point',
    '_cl_f3_equidistant_two_lines',
    '_cl_f4_fixed_distance_segment',
    '_cl_f5_perp_bisector_property',
    '_cl_f6_angle_bisector_property',
    '_cl_f7_rolling_wheel',
    '_cl_f8_closer_to_A',
    '_cl_f11_triangle_tools',
    '_cl_f12_locus_around_rectangle',
    '_cl_f13_bisector_right_angle',
    '_cl_f14_two_circle_region',
    '_cl_i1_combined_loci',
    '_cl_i3_ladder_midpoint',
    '_cl_i4_semicircle_locus',
    '_cl_i13_garden_sprinkler',
    '_cl_d4_constant_area_locus',
    '_cl_d7_three_loci',
    '_cl_d12_two_radio_towers',
    '_cl_d15_multi_locus_garden',
    '_cl_d16_garden_sprinkler_multi',
)

CL_PROOF_STEPS_VARIANTS = (
    '_cl_f9_construct_perp_bisector_steps',
    '_cl_f10_construct_angle_bisector_steps',
    '_cl_i2_equilateral_triangle',
    '_cl_i6_perp_from_external_point',
    '_cl_i7_triangle_sss_steps',
    '_cl_i8_construct_60',
    '_cl_i9_perp_at_point_on_line',
    '_cl_i11_circumcircle',
    '_cl_i12_incircle',
    '_cl_d1_locus_proof',
    '_cl_d9_regular_hexagon',
    '_cl_d13_construct_45',
    '_cl_d14_construct_30',
    '_cl_d2_ladder_ellipse',
)

CL_UNGRADED_VARIANTS = (
    '_cl_d5_apollonius_circle',
)


def test_transformations_coord_variants_are_graded():
    import generators.gcse.transformations as trans_mod

    for name in TRANS_COORD_VARIANTS:
        out = getattr(trans_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'transformations')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('correct_answer_raw'), name


def test_transformations_number_variants_are_graded():
    import generators.gcse.transformations as trans_mod

    for name in TRANS_NUMBER_VARIANTS:
        out = getattr(trans_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'intermediate', 'gcse', 'maths', 'transformations')
        assert problem.get('answer_type') == 'number', name


def test_transformations_describe_mcq_variants_are_graded():
    import generators.gcse.transformations as trans_mod

    for name in TRANS_MCQ_DESCRIBE_VARIANTS:
        out = getattr(trans_mod, name)()
        assert len(out) == 6, name
        problem = make_problem(
            out[0], out[1], out[2], 'intermediate', out[3],
            'gcse', 'maths', 'transformations',
            options=out[4], correct_answer=out[5],
        )
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name


def test_transformations_fields_mcq_variants_are_graded():
    import generators.gcse.transformations as trans_mod

    for name in TRANS_FIELDS_MCQ_VARIANTS:
        out = getattr(trans_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'intermediate', 'gcse', 'maths', 'transformations')
        assert problem.get('answer_type') == 'number_fields', name
        field_types = problem.get('answer_field_types') or []
        assert field_types, name
        field_options = problem.get('answer_field_options') or []
        assert len(field_options) == len(field_types), name
        if all(t == 'mcq' for t in field_types):
            assert all(opts and len(opts) == 3 for opts in field_options), name
        assert problem.get('correct_answer_raw'), name
        if name == '_trans_diff_two_reflections_intersecting':
            assert problem.get('answer_inline_sections'), name
            assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)'], name
        if name == '_trans_diff_two_reflections_parallel':
            assert problem.get('answer_inline_sections'), name
            assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)'], name
            assert problem.get('answer_field_types')[-1] == 'mcq', name
        if name == '_trans_diff_congruent_similar':
            assert problem.get('answer_inline_sections'), name
            assert problem.get('answer_field_section_keys') == ['(a)', '(b)', '(c)', '(d)'], name
            assert all(t == 'mcq' for t in field_types), name


def test_trans_congruent_similar_variant_is_randomizable():
    import generators.gcse.transformations as trans_mod
    from generators.shared.variant_utils import variant_is_randomizable

    assert variant_is_randomizable(trans_mod._trans_diff_congruent_similar)
    questions = {trans_mod._trans_diff_congruent_similar()[0] for _ in range(12)}
    assert len(questions) > 1


def test_transformations_ungraded_variants_remain_ungraded():
    import generators.gcse.transformations as trans_mod

    for name in TRANS_UNGRADED_VARIANTS:
        out = getattr(trans_mod, name)()
        assert len(out) == 4, name
        problem = make_graded_problem(out, 'intermediate', 'gcse', 'maths', 'transformations')
        assert problem.get('correct_answer_raw') is None, name


def test_transformations_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variant in gcse_transformations_variants(difficulty, 'practice'):
            problem = gcse_transformations(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in TRANS_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            if variant.__name__ in TRANS_MCQ_DESCRIBE_VARIANTS:
                assert problem.get('options') and problem.get('correct_answer'), variant.__name__
                continue
            if variant.__name__ in TRANS_FIELDS_MCQ_VARIANTS:
                assert problem.get('answer_type') == 'number_fields', variant.__name__
                assert problem.get('correct_answer_raw'), variant.__name__
                continue
            graded = problem.get('correct_answer_raw') or problem.get('correct_answer')
            assert graded, (difficulty, variant.__name__)


def test_constructions_loci_number_variants_are_graded():
    import generators.gcse.maths_constructions_loci as cl_mod

    for name in CL_NUMBER_VARIANTS:
        out = getattr(cl_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'constructions_loci')
        assert problem.get('answer_type') == 'number', name


def test_constructions_loci_fields_variants_are_graded():
    import generators.gcse.maths_constructions_loci as cl_mod

    for name in CL_FIELDS_VARIANTS:
        out = getattr(cl_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'difficult', 'gcse', 'maths', 'constructions_loci')
        assert problem.get('answer_type') == 'number_fields', name


def test_constructions_loci_mcq_variants_are_graded():
    import generators.gcse.maths_constructions_loci as cl_mod

    for name in CL_MCQ_VARIANTS:
        out = getattr(cl_mod, name)()
        assert len(out) == 6, name
        problem = gcse_constructions_loci('foundational', 'practice', variant_name=name)
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name


def test_constructions_loci_proof_steps_variants_are_graded():
    import generators.gcse.maths_constructions_loci as cl_mod

    for name in CL_PROOF_STEPS_VARIANTS:
        out = getattr(cl_mod, name)()
        assert len(out) == 5, name
        problem = gcse_constructions_loci('foundational', 'practice', variant_name=name)
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_step_bank'), name
        assert problem.get('answer_order_matters') is True, name


def test_constructions_loci_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_constructions_loci as cl_mod

    for name in CL_UNGRADED_VARIANTS:
        out = getattr(cl_mod, name)()
        assert len(out) == 4, name
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'constructions_loci')
        assert problem.get('correct_answer_raw') is None, name


def test_constructions_loci_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variant in gcse_constructions_loci_variants(difficulty, 'practice'):
            problem = gcse_constructions_loci(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in CL_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            if variant.__name__ in CL_MCQ_VARIANTS:
                assert problem.get('options') and problem.get('correct_answer'), variant.__name__
                continue
            if variant.__name__ in CL_PROOF_STEPS_VARIANTS:
                assert problem.get('answer_type') == 'proof_steps', variant.__name__
                assert problem.get('correct_answer_raw'), variant.__name__
                continue
            graded = problem.get('correct_answer_raw') or problem.get('correct_answer')
            assert graded, (difficulty, variant.__name__)


def test_trig_exact_fraction_check():
    assert check_fraction('1/2', '1/2')['correct'] is True
    assert check_fraction('1/2', '0.5')['correct'] is True


def test_trig_exact_surd_fraction_check():
    assert check_algebraic_fraction('1|2|2', '√2/2')['correct'] is True
    assert check_algebraic_fraction('1|3|2', '√3/2')['correct'] is True
    assert check_algebraic_fraction('1|3|3', '√3/3')['correct'] is True


def test_trig_check_api():
    problem = gcse_trigonometry(
        'foundational', 'practice', variant_name='_trig_found_pythagoras'
    )
    assert problem.get('answer_type') == 'number'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'trigonometry',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'number',
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


SIM_PAIR_VARIANTS = (
    '_sim_f_add_to_eliminate',
    '_sim_f_classic_pair',
    '_sim_d_general_elimination',
)

SIM_UNGRADED_VARIANTS = (
)

GSIM_GRADED_VARIANTS = (
    '_gsim_f_read_intersection',
    '_gsim_f_read_y_at_crossing',
    '_gsim_i_negative_gradient',
)

GSIM_UNGRADED_VARIANTS = (
)

GSIM_MCQ_PRACTICE_VARIANTS = (
    '_gsim_f_meaning_of_crossing',
    '_gsim_f_which_point_on_both',
    '_gsim_i_equations_from_graph',
    '_gsim_i_no_solution_parallel',
)


def test_simultaneous_pair_variants_are_graded():
    import generators.gcse.simultaneous_equations as sim_mod

    for name in SIM_PAIR_VARIANTS:
        out = getattr(sim_mod, name)()
        assert len(out) == 5, name
        problem = _sim_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'number_pair', name
        assert problem.get('correct_answer_raw') is not None, name


def test_simultaneous_ungraded_variants_remain_ungraded():
    import generators.gcse.simultaneous_equations as sim_mod

    for name in SIM_UNGRADED_VARIANTS:
        out = getattr(sim_mod, name)()
        assert len(out) == 4, name
        problem = _sim_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_simultaneous_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_simultaneous_equations_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_simultaneous_equations(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in SIM_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_graphical_simultaneous_variants_are_graded():
    import generators.gcse.graphical_simultaneous_equations as gsim_mod

    for name in GSIM_GRADED_VARIANTS:
        out = getattr(gsim_mod, name)()
        assert len(out) == 5, name
        problem = _gsim_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw') is not None, name

    for name in GSIM_UNGRADED_VARIANTS:
        out = getattr(gsim_mod, name)()
        assert len(out) == 4, name
        problem = _gsim_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_graphical_simultaneous_mcq_practice_variants():
    import generators.gcse.graphical_simultaneous_equations as gsim_mod

    for name in GSIM_MCQ_PRACTICE_VARIANTS:
        out = getattr(gsim_mod, name)()
        assert len(out) == 6, name
        problem = _gsim_problem_from_output(out, 'foundational')
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name
        assert problem.get('correct_answer_raw') is None, name


def test_graphical_simultaneous_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_graphical_simultaneous_equations_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_graphical_simultaneous_equations(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in GSIM_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_simultaneous_graph_interpret_is_mcq():
    problem = gcse_simultaneous_equations(
        'intermediate', 'practice', variant_name='_sim_i_graph_interpret'
    )
    assert problem.get('options') and len(problem['options']) == 4
    assert problem.get('correct_answer') in 'ABCD'


def test_simultaneous_check_api():
    problem = gcse_simultaneous_equations(
        'foundational', 'practice', variant_name='_sim_f_classic_pair'
    )
    assert problem.get('answer_type') == 'number_pair'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'simultaneous_equations',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'number_pair',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


CTS_UNGRADED_VARIANTS = (
)

CTS_GRADED_VARIANTS = (
    '_cts_f_half_coefficient',
    '_cts_f_write_completed_form',
    '_cts_d_factor_a_out',
    '_cts_i_solve_integer_roots',
    '_cts_i_turning_point',
    '_cts_d_solve_surd',
    '_cts_d_exam_show_that',
)

QSIM_UNGRADED_VARIANTS = (
)

QSIM_MCQ_PRACTICE_VARIANTS = (
    '_qsim_f_what_is_intersection',
    '_qsim_f_substitute_step',
    '_qsim_f_rearrange_only',
    '_qsim_i_check_pair',
)

QSIM_GRADED_VARIANTS = (
    '_qsim_f_simple_integer',
    '_qsim_i_find_x_only',
    '_qsim_d_word_problem',
)


def test_completing_the_square_variants_are_graded():
    import generators.gcse.completing_the_square as cts_mod

    for name in CTS_GRADED_VARIANTS:
        out = getattr(cts_mod, name)()
        assert len(out) == 5, name
        problem = _cts_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw') is not None, name
        if name in (
            '_cts_f_write_completed_form',
            '_cts_d_factor_a_out',
        ):
            assert problem.get('answer_type') == 'completed_square', name
        if name == '_cts_d_exam_show_that':
            assert problem.get('answer_type') == 'number_fields', name
            assert problem.get('answer_field_types') == [
                'algebraic', 'algebraic',
            ], name

    for name in CTS_UNGRADED_VARIANTS:
        out = getattr(cts_mod, name)()
        assert len(out) == 4, name
        problem = _cts_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_completing_the_square_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_completing_the_square_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_completing_the_square(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in CTS_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_quadratic_simultaneous_variants_are_graded():
    import generators.gcse.quadratic_simultaneous_equations as qsim_mod

    for name in QSIM_GRADED_VARIANTS:
        out = getattr(qsim_mod, name)()
        assert len(out) == 5, name
        problem = _qsim_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw') is not None, name

    for name in QSIM_UNGRADED_VARIANTS:
        out = getattr(qsim_mod, name)()
        assert len(out) == 4, name
        problem = _qsim_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_quadratic_simultaneous_mcq_practice_variants():
    import generators.gcse.quadratic_simultaneous_equations as qsim_mod

    for name in QSIM_MCQ_PRACTICE_VARIANTS:
        out = getattr(qsim_mod, name)()
        assert len(out) == 6, name
        problem = _qsim_problem_from_output(out, 'foundational')
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name
        assert problem.get('correct_answer_raw') is None, name


def test_quadratic_simultaneous_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_quadratic_simultaneous_equations_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_quadratic_simultaneous_equations(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in QSIM_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_quadratic_simultaneous_intersection_meaning_is_mcq():
    problem = gcse_quadratic_simultaneous_equations(
        'foundational', 'practice', variant_name='_qsim_f_what_is_intersection'
    )
    assert problem.get('options') and len(problem['options']) == 4
    assert problem.get('correct_answer') in 'ABCD'


def test_completing_the_square_check_api():
    problem = gcse_completing_the_square(
        'intermediate', 'practice', variant_name='_cts_i_solve_integer_roots'
    )
    assert problem.get('answer_type') == 'quadratic_roots'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'completing_the_square',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'quadratic_roots',
                'user_answer': raw,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_check_completed_square():
    from generators.shared.answer_checkers import check_completed_square

    assert check_completed_square('scaled|3|4|-9', '3|4|-9')['correct'] is True
    assert check_completed_square('plus|2|5', '2|5')['correct'] is True
    assert check_completed_square('minus|3|-2', '3|-2')['correct'] is True
    assert check_completed_square('expand|8|7', '8|7')['correct'] is True
    assert check_completed_square('scaled|3|4|-9', '3|4|-8')['correct'] is False
    assert check_completed_square('plus|2|5', '-2|5')['correct'] is False
    assert check_completed_square('minus|3|-2', '-3|-2')['correct'] is False


def test_completing_the_square_completed_square_api():
    problem = gcse_completing_the_square(
        'difficult', 'practice', variant_name='_cts_d_factor_a_out'
    )
    assert problem.get('answer_type') == 'completed_square'
    assert problem.get('answer_template_kind') == 'scaled'
    raw = problem['correct_answer_raw']
    user = '|'.join(raw.split('|')[1:])

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'completing_the_square',
                'difficulty': 'difficult',
                'correct_answer_raw': raw,
                'answer_type': 'completed_square',
                'user_answer': user,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_quadratic_simultaneous_check_api():
    problem = gcse_quadratic_simultaneous_equations(
        'foundational', 'practice', variant_name='_qsim_f_simple_integer'
    )
    assert problem.get('answer_type') == 'number_fields'
    raw = problem['correct_answer_raw']
    labels = problem['answer_labels']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'quadratic_simultaneous_equations',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'number_fields',
                'answer_labels': labels,
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


SUBJ_UNGRADED_VARIANTS = (
)

SUBJ_MCQ_PRACTICE_VARIANTS = (
    '_cts_f_first_step',
)

SUBJ_GRADED_VARIANTS = (
    '_cts_f_two_step_y_mx_c',
    '_cts_i_sqrt_area',
    '_cts_d_kinetic',
)

FN_UNGRADED_VARIANTS = (
)

FN_GRADED_VARIANTS = (
    '_fn_f_evaluate_linear',
    '_fn_f_meaning_notation',
    '_fn_d_solve_f_equals',
    '_fn_i_write_composite_rule',
    '_fn_i_inverse_linear',
    '_fn_d_multipart_quadratic_graph',
    '_fn_d_multipart_composite_inverse',
    '_fn_d_multipart_domain_range',
)


def test_changing_the_subject_variants_are_graded():
    import generators.gcse.changing_the_subject as subj_mod

    for name in SUBJ_GRADED_VARIANTS:
        out = getattr(subj_mod, name)()
        assert len(out) == 5, name
        problem = _subj_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw') is not None, name

    for name in SUBJ_UNGRADED_VARIANTS:
        out = getattr(subj_mod, name)()
        assert len(out) == 4, name
        problem = _subj_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_changing_the_subject_mcq_practice_variants():
    import generators.gcse.changing_the_subject as subj_mod

    for name in SUBJ_MCQ_PRACTICE_VARIANTS:
        out = getattr(subj_mod, name)()
        assert len(out) == 6, name
        problem = _subj_problem_from_output(out, 'foundational')
        assert problem.get('options') and len(problem['options']) == 4, name
        assert problem.get('correct_answer') in 'ABCD', name
        assert problem.get('correct_answer_raw') is None, name


def test_changing_the_subject_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_changing_the_subject_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_changing_the_subject(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in SUBJ_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_functions_variants_are_graded():
    import generators.gcse.functions as fn_mod

    for name in FN_GRADED_VARIANTS:
        out = getattr(fn_mod, name)()
        assert len(out) == 5, name
        problem = _fn_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw') is not None, name

    for name in FN_UNGRADED_VARIANTS:
        out = getattr(fn_mod, name)()
        assert len(out) == 4, name
        problem = _fn_problem_from_output(out, 'intermediate')
        assert problem.get('correct_answer_raw') is None, name


def test_functions_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_functions_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_functions(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in FN_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = (
                problem.get('correct_answer_raw')
                or problem.get('correct_answer')
            )
            assert graded, (difficulty, variant.__name__)


def test_check_changing_the_subject_simple_fraction():
    from generators.shared.answer_checkers import check_algebraic

    raw = 'i=(p)/(v)'
    for user in ('P/V', 'p/v', 'I = P/V', '(p)/(v)'):
        assert check_algebraic(raw, user)['correct'] is True, user
    assert check_algebraic(raw, 'V/P')['correct'] is False


def test_changing_the_subject_check_api():
    problem = gcse_changing_the_subject(
        'foundational', 'practice', variant_name='_cts_f_two_step_y_mx_c'
    )
    assert problem.get('answer_type') == 'algebraic'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'changing_the_subject',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic',
                'user_answer': raw.replace('*', ' '),
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_functions_inverse_linear_check_api():
    problem = gcse_functions(
        'intermediate', 'practice', variant_name='_fn_i_inverse_linear'
    )
    assert problem.get('answer_type') == 'algebraic'
    assert problem.get('answer_wrong_hint')
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic',
                'user_answer': raw,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_functions_composite_rule_check_api():
    problem = gcse_functions(
        'intermediate', 'practice', variant_name='_fn_i_write_composite_rule'
    )
    assert problem.get('answer_type') == 'algebraic'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic',
                'user_answer': raw.replace('+', ' + '),
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_functions_multipart_composite_inverse_check_api():
    problem = gcse_functions(
        'difficult', 'practice', variant_name='_fn_d_multipart_composite_inverse'
    )
    assert problem.get('answer_type') == 'number_fields'
    field_types = problem.get('answer_field_types') or []
    assert field_types == ['algebraic', 'number', 'algebraic']
    parts = problem['correct_answer_raw'].split('\x1e')
    assert len(parts) == 3

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[0],
                'answer_type': 'algebraic',
                'user_answer': parts[0].replace('+', ' + '),
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[1],
                'answer_type': 'number',
                'user_answer': parts[1],
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True

        r3 = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[2],
                'answer_type': 'algebraic',
                'user_answer': parts[2],
            }
        )
        assert r3.status_code == 200
        assert r3.get_json()['correct'] is True


def test_functions_multipart_quadratic_graph_check_api():
    problem = gcse_functions(
        'difficult', 'practice', variant_name='_fn_d_multipart_quadratic_graph'
    )
    assert problem.get('answer_type') == 'number_fields'
    field_types = problem.get('answer_field_types') or []
    assert field_types == ['vector', 'number', 'linear']
    parts = problem['correct_answer_raw'].split('\x1e')
    assert len(parts) == 3

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[0],
                'answer_type': 'vector',
                'user_answer': parts[0].replace('|', ', '),
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[1],
                'answer_type': 'number',
                'user_answer': parts[1],
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True

        r3 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[2],
                'answer_type': 'linear',
                'user_answer': f'x = {parts[2]}',
            },
        )
        assert r3.status_code == 200
        assert r3.get_json()['correct'] is True


def test_functions_multipart_domain_range_check_api():
    problem = gcse_functions(
        'difficult', 'practice', variant_name='_fn_d_multipart_domain_range'
    )
    assert problem.get('answer_type') == 'number_fields'
    field_types = problem.get('answer_field_types') or []
    assert field_types == ['number', 'mcq', 'fraction']
    field_options = problem.get('answer_field_options') or []
    assert len(field_options) == 3
    assert field_options[1] and len(field_options[1]) == 3
    parts = problem['correct_answer_raw'].split('\x1e')
    assert len(parts) == 3

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[0],
                'answer_type': 'number',
                'user_answer': parts[0],
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True

        r2 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[1],
                'answer_type': 'mcq',
                'user_answer': parts[1],
            },
        )
        assert r2.status_code == 200
        assert r2.get_json()['correct'] is True

        r3 = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'difficult',
                'correct_answer_raw': parts[2],
                'answer_type': 'fraction',
                'user_answer': parts[2],
            },
        )
        assert r3.status_code == 200
        assert r3.get_json()['correct'] is True


def test_functions_check_api():
    problem = gcse_functions(
        'foundational', 'practice', variant_name='_fn_f_evaluate_linear'
    )
    assert problem.get('answer_type') == 'number'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'functions',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


ALGEBRA_LINEAR_VARIANTS = (
    'algebra_practice_linear_1',
    'algebra_practice_linear_2',
    'algebra_practice_linear_3',
    'algebra_practice_linear_both_sides',
    'algebra_practice_brackets_both_sides',
    'algebra_practice_consecutive_integers',
)

ALGEBRA_QUADRATIC_ROOTS_VARIANTS = (
    'algebra_practice_factorise_1',
    'algebra_practice_factorise_2',
    'algebra_practice_factorise_3',
    'algebra_practice_quadratic_1',
)

ALGEBRA_NUMBER_VARIANTS = (
    'algebra_practice_substitution',
    'algebra_practice_word_linear',
)

ALGEBRA_ALGEBRAIC_VARIANTS = (
    'algebra_practice_expand_binomial',
    'algebra_practice_expand_mixed',
    'algebra_practice_factorise_hcf',
    'algebra_practice_change_subject',
    'algebra_practice_quadratic_3',
)

ALGEBRA_NUMBER_PAIR_VARIANTS = (
    'algebra_practice_simultaneous',
)


def test_algebra_linear_variants_are_graded():
    import generators.gcse.maths as m

    for name in ALGEBRA_LINEAR_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _algebra_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'linear', name
        assert problem.get('correct_answer_raw') is not None, name


def test_algebra_quadratic_roots_variants_are_graded():
    import generators.gcse.maths as m

    for name in ALGEBRA_QUADRATIC_ROOTS_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _algebra_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'quadratic_roots', name
        assert problem.get('correct_answer_raw') is not None, name
        assert len(problem.get('answer_labels') or []) >= 2, name


def test_algebra_number_and_pair_variants_are_graded():
    import generators.gcse.maths as m

    for name in ALGEBRA_NUMBER_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _algebra_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw') is not None, name

    for name in ALGEBRA_NUMBER_PAIR_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _algebra_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_pair', name
        assert problem.get('correct_answer_raw') is not None, name


def test_algebra_algebraic_variants_are_graded():
    import generators.gcse.maths as m

    for name in ALGEBRA_ALGEBRAIC_VARIANTS:
        out = getattr(m, name)()
        assert len(out) == 5, name
        problem = _algebra_problem_from_output(out, 'intermediate')
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw') is not None, name


def test_algebra_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_maths_algebra_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_maths_algebra(
                difficulty, 'practice', variant_name=variant.__name__
            )
            assert problem.get('correct_answer_raw') is not None, (
                difficulty,
                variant.__name__,
            )


def test_algebra_fallback_random_is_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        problem = gcse_maths_algebra(difficulty, 'practice')
        assert problem.get('correct_answer_raw') is not None, difficulty
        assert problem.get('answer_type') in (
            'linear',
            'quadratic_roots',
            'number',
            'number_pair',
            'algebraic',
        ), (difficulty, problem.get('answer_type'))


def test_algebra_linear_check_api():
    problem = gcse_maths_algebra(
        'foundational', 'practice', variant_name='algebra_practice_linear_1'
    )
    assert problem.get('answer_type') == 'linear'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'difficulty': 'foundational',
                'correct_answer_raw': raw,
                'answer_type': 'linear',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_algebra_quadratic_roots_check_api():
    problem = gcse_maths_algebra(
        'intermediate', 'practice', variant_name='algebra_practice_factorise_1'
    )
    assert problem.get('answer_type') == 'quadratic_roots'
    raw = problem['correct_answer_raw']
    roots = [part.strip() for part in raw.split(',')]
    reversed_raw = ','.join(reversed(roots))

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'quadratic_roots',
                'user_answer': reversed_raw,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_algebra_simultaneous_check_api():
    problem = gcse_maths_algebra(
        'difficult', 'practice', variant_name='algebra_practice_simultaneous'
    )
    assert problem.get('answer_type') == 'number_pair'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'difficulty': 'difficult',
                'correct_answer_raw': raw,
                'answer_type': 'number_pair',
                'user_answer': raw,
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_algebra_expand_check_api():
    problem = gcse_maths_algebra(
        'intermediate', 'practice', variant_name='algebra_practice_expand_binomial'
    )
    assert problem.get('answer_type') == 'algebraic'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic',
                'user_answer': raw,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_algebra_change_subject_check_api():
    problem = gcse_maths_algebra(
        'intermediate', 'practice', variant_name='algebra_practice_change_subject'
    )
    assert problem.get('answer_type') == 'algebraic'
    raw = problem['correct_answer_raw']

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebra',
                'difficulty': 'intermediate',
                'correct_answer_raw': raw,
                'answer_type': 'algebraic',
                'user_answer': raw,
            }
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


def test_vectors_check_api():
    problem = gcse_vectors(
        'foundational', 'practice', variant_name='_vectors_found_add_simple'
    )
    assert problem.get('answer_type') == 'vector'
    correct = problem['correct_answer_raw']

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'vectors',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'vector',
                'user_answer': correct.replace('|', ', '),
            },
        )
        assert r.status_code == 200
        assert r.get_json()['correct'] is True


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


def test_geometry_proof_variants_use_plan_b_scaffolds():
    import generators.gcse.geometry_angles as geom_mod

    for name in GEOMETRY_PROOF_VARIANTS:
        out = getattr(geom_mod, name)()
        assert len(out) == 5, name
        problem = _geom_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert len(labels) >= 2, name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_field_types'), name


def test_geometry_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_geometry_angles_variants(difficulty, 'practice')
        assert variants, difficulty
        for variant in variants:
            problem = gcse_geometry_angles(
                difficulty, 'practice', variant_name=variant.__name__
            )
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

PYTHAGORAS_CHOICE_VARIANTS = (
    '_py_d4_pythagoras_proof_check',
)

PYTHAGORAS_UNGRADED_VARIANTS = ()


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
        assert not problem.get('options'), name


def test_pythagoras_proof_check_uses_choice_buttons():
    import generators.gcse.maths_pythagoras as pyth_mod
    from generators.shared.variant_utils import variant_is_randomizable

    assert variant_is_randomizable(pyth_mod._py_d4_pythagoras_proof_check) is True

    seen = set()
    for _ in range(20):
        out = pyth_mod._py_d4_pythagoras_proof_check()
        assert len(out) == 5
        problem = _pyth_problem_from_output(out, 'difficult')
        assert problem.get('options') and len(problem['options']) == 4, problem
        assert problem.get('correct_answer') in ('A', 'B', 'C', 'D')
        assert problem.get('correct_answer_raw') is None
        seen.add(problem['question'])
    assert len(seen) >= 2, seen


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

COMPOUND_ALGEBRAIC_VARIANTS = (
)

COMPOUND_SCAFFOLD_VARIANTS = (
    '_cm_d5_algebraic_sdt',
    '_cm_d7_harmonic_mean_prove',
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
)


def test_compound_measures_number_variants_are_graded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_NUMBER_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') == 'number', name


def test_compound_measures_algebraic_variants_are_graded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_ALGEBRAIC_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw'), name
        assert check_answer(
            'algebraic',
            problem['correct_answer_raw'],
            problem['correct_answer_raw'],
        )['correct'] is True, name


def test_compound_measures_scaffold_variants_are_graded():
    import generators.gcse.maths_compound_measures as cm_mod

    for name in COMPOUND_SCAFFOLD_VARIANTS:
        out = getattr(cm_mod, name)()
        assert len(out) == 5, name
        problem = _cm_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'number_fields', name
        labels = problem.get('answer_labels') or []
        assert len(labels) >= 2, name
        assert '\x1e' in problem['correct_answer_raw'], name
        parts = problem['correct_answer_raw'].split('\x1e')
        assert len(parts) == len(labels), name


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
    '_brg_diff_prove_bearing',
)

BEARINGS_UNGRADED_VARIANTS = (
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

SEQUENCES_UNGRADED_VARIANTS = ()

SEQUENCES_MCQ_VARIANTS = (
    '_seq_found_identify_rule',
    '_seq_found_term_to_term_rule',
)

SEQUENCES_NUMBER_LIST_VARIANTS = (
    '_seq_found_nth_term_find_terms',
)

SEQUENCES_ALGEBRAIC_VARIANTS = (
    '_seq_inter_find_nth_term',
    '_seq_inter_nth_term_negative_d',
    '_seq_inter_quadratic_identify',
    '_seq_diff_quadratic_nth_term',
)

SEQUENCES_PLAN_C_STEP_BANK_VARIANTS = (
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


def test_sequences_mcq_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_MCQ_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'foundational')
        assert problem.get('options'), name
        assert problem.get('correct_answer'), name


def test_sequences_number_list_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_NUMBER_LIST_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'number_list', name
        assert problem.get('correct_answer_raw'), name


def test_sequences_algebraic_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_ALGEBRAIC_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        difficulty = 'difficult' if name.startswith('_seq_diff_') else 'intermediate'
        problem = _seq_problem_from_output(out, difficulty)
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw'), name


def test_sequences_plan_c_step_bank_variants_are_graded():
    import generators.gcse.sequences as seq_mod

    for name in SEQUENCES_PLAN_C_STEP_BANK_VARIANTS:
        out = getattr(seq_mod, name)()
        assert len(out) == 5, name
        problem = _seq_problem_from_output(out, 'difficult')
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_step_bank'), name


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


def test_sequences_algebraic_check_api():
    problem = gcse_sequences(
        'intermediate', 'practice', variant_name='_seq_inter_find_nth_term'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'algebraic'

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'sequences',
                'difficulty': 'intermediate',
                'correct_answer_raw': correct,
                'answer_type': 'algebraic',
                'user_answer': correct.replace(' ', ''),
            }
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


AP_UNGRADED_VARIANTS = ()

AP_ALGEBRAIC_VARIANTS = (
    '_ap_f_expand_consecutive',
    '_ap_i_identity_expand',
)

AP_MULTIPART_VARIANTS = (
    '_ap_f_sum_consecutive',
)

AP_COUNTEREXAMPLE_VARIANTS = (
    '_ap_f_counterexample',
    '_ap_d_disprove_always_prime',
)

AP_PROOF_STEPS_VARIANTS = (
    '_ap_f_even_form',
    '_ap_f_odd_form',
    '_ap_i_square_difference',
    '_ap_i_product_consecutive',
    '_ap_i_multiple_of_three',
    '_ap_i_sum_three_consecutive',
    '_ap_d_n_squared_plus_n',
    '_ap_d_odd_square',
    '_ap_d_even_sum_squares',
    '_ap_d_four_consecutive',
)


def test_algebraic_proof_ungraded_variants_remain_ungraded():
    import generators.gcse.algebraic_proof as ap_mod

    for name in AP_UNGRADED_VARIANTS:
        out = getattr(ap_mod, name)()
        assert len(out) == 4, name
        problem = ap_mod._ap_problem_from_output(out, 'foundational')
        assert problem.get('correct_answer_raw') is None, name


def test_algebraic_proof_proof_steps_variants_are_graded():
    import generators.gcse.algebraic_proof as ap_mod
    from generators.gcse.algebraic_proof import gcse_algebraic_proof

    for name in AP_PROOF_STEPS_VARIANTS:
        out = getattr(ap_mod, name)()
        assert len(out) == 5, name
        difficulty = (
            'foundational' if name.startswith('_ap_f_')
            else 'intermediate' if name.startswith('_ap_i_')
            else 'difficult'
        )
        problem = gcse_algebraic_proof(difficulty, 'practice', variant_name=name)
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_step_bank'), name
        assert problem.get('answer_order_matters') is True, name


def test_algebraic_proof_algebraic_variants_are_graded():
    import generators.gcse.algebraic_proof as ap_mod

    for name in AP_ALGEBRAIC_VARIANTS:
        out = getattr(ap_mod, name)()
        assert len(out) == 5, name
        difficulty = 'intermediate' if name.startswith('_ap_i_') else 'foundational'
        problem = ap_mod._ap_problem_from_output(out, difficulty)
        assert problem.get('answer_type') == 'algebraic', name
        assert problem.get('correct_answer_raw'), name


def test_algebraic_proof_multipart_variants_use_number_fields():
    import generators.gcse.algebraic_proof as ap_mod

    for name in AP_MULTIPART_VARIANTS:
        out = getattr(ap_mod, name)()
        assert len(out) == 5, name
        problem = ap_mod._ap_problem_from_output(out, 'foundational')
        assert problem.get('answer_type') == 'number_fields', name


def test_algebraic_proof_counterexample_variants_are_graded():
    import generators.gcse.algebraic_proof as ap_mod

    for name in AP_COUNTEREXAMPLE_VARIANTS:
        out = getattr(ap_mod, name)()
        assert len(out) == 5, name
        difficulty = 'difficult' if name.startswith('_ap_d_') else 'foundational'
        problem = ap_mod._ap_problem_from_output(out, difficulty)
        assert problem.get('answer_type') == 'number', name
        assert problem.get('correct_answer_raw'), name


def test_algebraic_proof_variant_queues_are_graded():
    from generators.gcse.algebraic_proof import gcse_algebraic_proof, gcse_algebraic_proof_variants

    graded_names = (
        AP_ALGEBRAIC_VARIANTS + AP_MULTIPART_VARIANTS + AP_COUNTEREXAMPLE_VARIANTS
        + AP_PROOF_STEPS_VARIANTS
    )
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        variants = gcse_algebraic_proof_variants(difficulty, 'practice')
        for variant in variants:
            problem = gcse_algebraic_proof(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in AP_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            if variant.__name__ in graded_names:
                assert problem.get('correct_answer_raw'), variant.__name__
            else:
                assert problem.get('correct_answer_raw') or problem.get('correct_answer'), (
                    difficulty, variant.__name__
                )


def test_algebraic_proof_algebraic_check_api():
    from generators.gcse.algebraic_proof import gcse_algebraic_proof

    problem = gcse_algebraic_proof(
        'foundational', 'practice', variant_name='_ap_f_expand_consecutive'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') == 'algebraic'

    with app.test_client() as client:
        r = _post_problems_check(
            client,
            {
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'algebraic_proof',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': 'algebraic',
                'user_answer': correct.replace(' ', ''),
            }
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


SC_UNGRADED_VARIANTS = ()

SC_PROOF_STEP_VARIANTS = (
    '_sc_i9_proof_aa_parallel',
    '_sc_d1_midpoint_theorem_proof',
    '_sc_d7_congruence_proof',
)

SC_PROOF_STEP_WITH_SVG = (
    '_sc_d1_midpoint_theorem_proof',
)

SC_GRADED_VARIANTS = (
    '_sc_f1_congruence_sss', '_sc_f2_congruence_sas', '_sc_f3_congruence_asa',
    '_sc_f4_congruence_rhs', '_sc_f5_scale_factor', '_sc_f6_missing_side_from_sf',
    '_sc_f7_similar_triangles_sides', '_sc_f8_angles_similar',
    '_sc_f9_area_ratio_from_lsf', '_sc_f10_lsf_from_area',
    '_sc_f11_volume_ratio_from_lsf', '_sc_f12_similar_rectangles',
    '_sc_f13_perimeter_ratio', '_sc_f14_map_scale', '_sc_f15_area_of_smaller',
    '_sc_i1_aa_similarity_find_side', '_sc_i2_parallel_lines_find_bc',
    '_sc_i3_area_from_lsf', '_sc_i4_volume_from_lsf',
    '_sc_i5_lsf_from_area_ratio', '_sc_i6_dimension_from_volume',
    '_sc_i7_algebraic_similar_sides', '_sc_i8_surface_area_similar_solids',
    '_sc_i10_overlapping_similar', '_sc_i11_area_ratio_find_perimeter',
    '_sc_i12_map_area', '_sc_i13_similar_cones_volume',
    '_sc_i14_quadrilateral_angles', '_sc_i15_chain_scale_factor',
    '_sc_d2_frustum_volume', '_sc_d3_altitude_in_right_triangle',
    '_sc_d4_quadratic_from_similarity', '_sc_d5_area_with_given_ratio',
    '_sc_d6_basic_proportionality', '_sc_d8_both_sa_and_vol_similar',
    '_sc_d9_shadow_height', '_sc_d10_angle_bisector_theorem',
    '_sc_d11_similar_trapezium', '_sc_d12_similar_rectangle_algebra',
    '_sc_d13_series_similar_triangles', '_sc_d14_scale_model_multi',
    '_sc_d15_lsf_from_vol_and_sa',
)


def test_similarity_congruence_graded_variants_are_graded():
    import generators.gcse.maths_similarity_congruence as sc_mod

    for name in SC_GRADED_VARIANTS:
        out = getattr(sc_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'similarity_congruence')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') in ('number', 'number_fields'), name


def test_sc_d12_similar_rectangle_algebra_is_randomizable():
    import generators.gcse.maths_similarity_congruence as sc_mod
    from generators.shared.variant_utils import variant_is_randomizable

    assert variant_is_randomizable(sc_mod._sc_d12_similar_rectangle_algebra) is True
    questions = {sc_mod._sc_d12_similar_rectangle_algebra()[0] for _ in range(16)}
    assert len(questions) > 1


def test_sc_d3_altitude_multipart_fields():
    import generators.gcse.maths_similarity_congruence as sc_mod
    from generators.shared.answer_checkers import check_proof_steps

    problem = make_graded_problem(
        sc_mod._sc_d3_altitude_in_right_triangle(),
        'difficult', 'gcse', 'maths', 'similarity_congruence',
    )
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(i)', '(ii)', '(iii)']
    assert problem.get('answer_field_types') == ['mcq', 'pick', 'number']
    assert problem.get('answer_field_pick_counts') == [None, 1, None]
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 3
    assert parts[0] in 'ABCD'
    assert parts[1].startswith('pick|1|')
    assert parts[2].isdigit()
    opts = problem.get('answer_field_options') or []
    assert len(opts[0]) == 4
    assert len(opts[1]) == 5
    pick_id = parts[1].split('|')[2]
    assert check_proof_steps(parts[1], pick_id)['correct'] is True


def test_similarity_congruence_proof_step_variants_are_graded():
    import generators.gcse.maths_similarity_congruence as sc_mod
    from generators.shared.answer_checkers import check_proof_steps

    for name in SC_PROOF_STEP_VARIANTS:
        out = getattr(sc_mod, name)()
        assert len(out) == 5, name
        if name in SC_PROOF_STEP_WITH_SVG:
            assert '<svg' in out[0], name
        else:
            assert '<svg' not in out[0], name
        problem = make_graded_problem(out, 'difficult', 'gcse', 'maths', 'similarity_congruence')
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('answer_order_matters') is True, name
        assert problem.get('answer_step_bank'), name
        raw = problem.get('correct_answer_raw') or ''
        assert raw.startswith('1|'), name
        step_ids = raw.split('|')[1:]
        assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True, name
        assert check_proof_steps(raw, '|'.join(reversed(step_ids)))['correct'] is False, name


def test_similarity_congruence_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_similarity_congruence as sc_mod

    for name in SC_UNGRADED_VARIANTS:
        out = getattr(sc_mod, name)()
        assert len(out) == 4, name
        problem = make_graded_problem(out, 'difficult', 'gcse', 'maths', 'similarity_congruence')
        assert problem.get('correct_answer_raw') is None, name


def test_similarity_congruence_mcq_fields_have_options():
    import generators.gcse.maths_similarity_congruence as sc_mod

    for name in ('_sc_f1_congruence_sss', '_sc_f2_congruence_sas',
                 '_sc_f3_congruence_asa', '_sc_f4_congruence_rhs'):
        out = getattr(sc_mod, name)()
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'similarity_congruence')
        assert problem.get('answer_type') == 'number_fields', name
        field_types = problem.get('answer_field_types') or []
        assert 'mcq' in field_types, name
        field_options = problem.get('answer_field_options') or []
        assert any(opts for opts in field_options), name
        opts = field_options[0]
        assert len(opts) == 4, name
        assert problem.get('correct_answer_raw') in 'ABCD', name


def test_similarity_congruence_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variant in gcse_similarity_congruence_variants(difficulty, 'practice'):
            problem = gcse_similarity_congruence(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in SC_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            graded = problem.get('correct_answer_raw') or problem.get('correct_answer')
            assert graded, (difficulty, variant.__name__)


def test_similarity_congruence_check_api():
    problem = gcse_similarity_congruence(
        'foundational', 'practice', variant_name='_sc_f5_scale_factor'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') in ('number', 'number_fields')

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'similarity_congruence',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': problem.get('answer_type'),
                'answer_field_types': problem.get('answer_field_types'),
                'answer_field_options': problem.get('answer_field_options'),
                'user_answer': correct,
            },
        )
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] is True
        assert data['correct'] is True


def test_similarity_congruence_single_field_session_check():
    """Per-field ratio/mcq checks must not 403 when raw matches a single-field problem."""
    cases = (
        ('_sc_f10_lsf_from_area', 'ratio'),
        ('_sc_f1_congruence_sss', 'mcq'),
    )
    with app.test_client() as client:
        for variant_name, field_type in cases:
            problem = gcse_similarity_congruence(
                'foundational', 'practice', variant_name=variant_name
            )
            assert problem.get('answer_type') == 'number_fields', variant_name
            correct = problem['correct_answer_raw']
            with client.session_transaction() as sess:
                sess['last_problem_payload'] = {
                    'level': 'gcse',
                    'subject': 'maths',
                    'topic': 'similarity_congruence',
                    'mode': 'practice',
                    'difficulty': 'foundational',
                    'problem': problem,
                }
            r = client.post(
                '/api/v1/problems/check',
                json={
                    'user_answer': correct,
                    'correct_answer_raw': correct,
                    'answer_type': field_type,
                    'part_index': 0,
                    'part_total': 1,
                },
                headers={'Accept': 'application/json'},
            )
            assert r.status_code == 200, (variant_name, r.get_json())
            assert r.get_json()['correct'] is True, variant_name


CT_UNGRADED_VARIANTS = (
)

CT_PROOF_STEPS_VARIANTS = (
    '_ct_d2_prove_angle',
    '_ct_d4_alternate_segment_proof',
    '_ct_d10_prove_cyclic',
)

CT_GRADED_VARIANTS = (
    '_ct_f1_centre_to_circum', '_ct_f2_circum_to_centre', '_ct_f3_semicircle_direct',
    '_ct_f4_semicircle_third_angle', '_ct_f5_same_segment_equal',
    '_ct_f6_same_segment_context', '_ct_f7_cyclic_quad_opposite',
    '_ct_f8_cyclic_quad_two_unknowns', '_ct_f9_tangent_right_angle',
    '_ct_f10_tangent_isosceles', '_ct_f11_two_tangents_equal',
    '_ct_f12_two_tangents_angle_at_centre', '_ct_f13_alternate_segment_basic',
    '_ct_f14_alternate_segment_straight_line', '_ct_f15_radii_isosceles_ct1',
    '_ct_i1_centre_isosceles_multistep', '_ct_i2_alternate_segment_plus_parallel',
    '_ct_i3_cyclic_quad_algebra', '_ct_i4_tangent_chord_kite',
    '_ct_i5_chord_bisect_pythagoras', '_ct_i6_same_segment_with_isosceles',
    '_ct_i7_ct1_and_ct3_combined', '_ct_i8_cyclic_quad_parallel_lines',
    '_ct_i9_alternate_segment_and_cyclic', '_ct_i10_reflex_centre_angle',
    '_ct_i11_tangent_from_external_distance', '_ct_i12_ct1_twice',
    '_ct_i13_ct3_in_triangle', '_ct_i14_semicircle_tangent',
    '_ct_i15_cyclic_quad_exterior_angle', '_ct_d1_three_theorems',
    '_ct_d3_complex_cyclic_poly', '_ct_d5_find_radius_from_tangent',
    '_ct_d6_three_circle_angles', '_ct_d7_angle_in_cyclic_quad_algebra',
    '_ct_d8_two_chords_intersect', '_ct_d9_secant_external',
    '_ct_d11_multi_step_tangent_chord', '_ct_d12_tangent_chord_parallel',
    '_ct_d13_ct1_ct4_ct5_combined', '_ct_d14_chord_and_tangent_lengths',
    '_ct_d15_algebraic_full',
)


def test_circle_theorems_graded_variants_are_graded():
    import generators.gcse.maths_circle_theorems as ct_mod

    for name in CT_GRADED_VARIANTS:
        out = getattr(ct_mod, name)()
        assert len(out) == 5, name
        problem = make_graded_problem(out, 'foundational', 'gcse', 'maths', 'circle_theorems')
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_type') in ('number', 'number_fields'), name


def test_circle_theorems_ungraded_variants_remain_ungraded():
    import generators.gcse.maths_circle_theorems as ct_mod

    for name in CT_UNGRADED_VARIANTS:
        out = getattr(ct_mod, name)()
        assert len(out) == 4, name
        problem = make_graded_problem(out, 'difficult', 'gcse', 'maths', 'circle_theorems')
        assert problem.get('correct_answer_raw') is None, name


def test_circle_theorems_proof_steps_variants_are_graded():
    import generators.gcse.maths_circle_theorems as ct_mod
    from generators.shared.answer_checkers import check_proof_steps

    for name in CT_PROOF_STEPS_VARIANTS:
        out = getattr(ct_mod, name)()
        assert len(out) == 5, name
        problem = gcse_circle_theorems('difficult', 'practice', variant_name=name)
        assert problem.get('answer_type') == 'proof_steps', name
        assert problem.get('correct_answer_raw'), name
        assert problem.get('answer_step_bank'), name
        assert problem.get('answer_order_matters') is True, name
        raw = problem['correct_answer_raw']
        step_ids = raw.split('|')[1:]
        assert check_proof_steps(raw, '|'.join(step_ids))['correct'] is True, name
        assert check_proof_steps(raw, '|'.join(reversed(step_ids)))['correct'] is False, name


def test_circle_theorems_algebra_variants_use_number_fields():
    import generators.gcse.maths_circle_theorems as ct_mod

    for name in ('_ct_i3_cyclic_quad_algebra', '_ct_d7_angle_in_cyclic_quad_algebra'):
        out = getattr(ct_mod, name)()
        problem = make_graded_problem(out, 'intermediate', 'gcse', 'maths', 'circle_theorems')
        assert problem.get('answer_type') == 'number_fields', name
        assert problem.get('correct_answer_raw'), name


def test_ct_d1_three_theorems_multipart_fields():
    import generators.gcse.maths_circle_theorems as ct_mod
    from generators.shared.answer_checkers import check_proof_steps

    problem = make_graded_problem(
        ct_mod._ct_d1_three_theorems(),
        'difficult', 'gcse', 'maths', 'circle_theorems',
    )
    assert problem.get('answer_type') == 'number_fields'
    assert problem.get('answer_inline_sections') is True
    assert problem.get('answer_field_section_keys') == ['(i)', '(ii)', '(iii)', '(iv)']
    assert problem.get('answer_field_types') == ['number', 'number', 'number', 'pick']
    assert problem.get('answer_field_pick_counts') == [None, None, None, 1]
    parts = (problem.get('correct_answer_raw') or '').split('\x1e')
    assert len(parts) == 4
    assert parts[0].isdigit()
    assert parts[1].isdigit()
    assert parts[2].isdigit()
    assert parts[3].startswith('pick|1|')
    opts = problem.get('answer_field_options') or []
    assert len(opts[3]) == 5
    pick_id = parts[3].split('|')[2]
    assert check_proof_steps(parts[3], pick_id)['correct'] is True


def test_circle_theorems_variant_queues_are_graded():
    for difficulty in ('foundational', 'intermediate', 'difficult'):
        for variant in gcse_circle_theorems_variants(difficulty, 'practice'):
            problem = gcse_circle_theorems(
                difficulty, 'practice', variant_name=variant.__name__
            )
            if variant.__name__ in CT_UNGRADED_VARIANTS:
                assert problem.get('correct_answer_raw') is None, variant.__name__
                continue
            if variant.__name__ in CT_PROOF_STEPS_VARIANTS:
                assert problem.get('answer_type') == 'proof_steps', variant.__name__
                assert problem.get('correct_answer_raw'), variant.__name__
                continue
            graded = problem.get('correct_answer_raw') or problem.get('correct_answer')
            assert graded, (difficulty, variant.__name__)


def test_circle_theorems_check_api():
    problem = gcse_circle_theorems(
        'foundational', 'practice', variant_name='_ct_f1_centre_to_circum'
    )
    correct = problem['correct_answer_raw']
    assert problem.get('answer_type') in ('number', 'number_fields')

    with app.test_client() as client:
        r = client.post(
            '/api/v1/problems/check',
            json={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'circle_theorems',
                'difficulty': 'foundational',
                'correct_answer_raw': correct,
                'answer_type': problem.get('answer_type'),
                'answer_field_types': problem.get('answer_field_types'),
                'answer_field_options': problem.get('answer_field_options'),
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

        roots_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '-0.67,-2',
                'answer_type': 'quadratic_roots',
                'answer_labels': ['Root 1', 'Root 2'],
                'answer_format_hint': 'Enter each root in its own box',
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='algebra',
            fr_difficulty='difficult',
        )
        assert 'free-response-row--quadratic-roots-pair' in roots_html
        assert roots_html.count('free-response-input-quadratic-root') == 2
        assert 'free-response-input-quadratic-roots"' not in roots_html
        assert roots_html.count('free-response-check-btn') == 1

        four_roots_html = render_template(
            'partials/free_response_inline.html',
            problem={
                'correct_answer_raw': '-2,-1,1,2',
                'answer_type': 'quadratic_roots',
                'answer_labels': ['Root 1', 'Root 2', 'Root 3', 'Root 4'],
            },
            fr_level='gcse',
            fr_subject='maths',
            fr_topic='equations_inequalities',
            fr_difficulty='difficult',
        )
        assert 'free-response-row--quadratic-roots-multi' in four_roots_html
        assert four_roots_html.count('free-response-input-quadratic-root') == 4
        assert four_roots_html.count('free-response-check-btn') == 1

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
        wrong = '5' if str(problem['correct_answer_raw']).strip() != '5' else '7'
        r = client.post(
            '/api/v1/problems/check',
            json={
                'user_answer': wrong,
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
    test_decimals_variant_queue_is_graded()
    test_decimals_ordering_uses_number_list_checker()
    test_decimals_order_mixed_uses_order_checker()
    test_decimals_recurring_uses_fraction_checker()
    test_decimals_check_api()
    test_multiples_factors_variant_queue_is_graded()
    test_multiples_factors_mcq_variants_are_graded()
    test_multiples_factors_pick_variants_are_graded()
    test_multiples_factors_divisibility_variants_are_graded()
    test_multiples_factors_prime_uses_keyword_checker()
    test_multiples_factors_primes_in_range_uses_number_list_checker()
    test_multiples_factors_check_api()
    test_fdp_graded_variants_return_five_tuple()
    test_fdp_ungraded_variants_remain_four_tuple()
    test_fdp_fraction_variants_use_fraction_checker()
    test_fdp_multipart_variants_use_number_fields()
    test_fdp_mcq_variants_are_graded()
    test_fdp_order_variants_are_graded()
    test_fdp_recurring_variants_use_fraction_checker()
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
    test_check_algebraic_vector_bc_notation()
    test_check_proof_steps_order_and_set()
    test_check_algebraic_surd_binomial()
    test_surds_algebraic_check_api()
    test_surds_compare_uses_choice_buttons()
    test_surds_generator_payload()
    test_surds_variant_queues_are_graded()
    test_surds_check_api()
    test_af_fraction_variants_use_stacked_fraction_ui()
    test_af_number_variants_are_graded()
    test_af_linear_variants_are_graded()
    test_af_algebraic_variants_are_graded()
    test_af_ungraded_variants_remain_four_tuple()
    test_af_generator_payload()
    test_af_variant_queues_are_graded()
    test_af_check_api_fraction()
    test_af_check_api_number()
    test_af_diff_denominator_check_api_accepts_equivalent()
    test_af_stacked_fraction_partial_renders()
    test_check_general_algebraic_fraction_equivalence()
    test_number_numeric_variants_return_five_tuple()
    test_number_standard_form_variants_graded()
    test_number_power_variants_graded()
    test_number_fraction_variants_graded()
    test_number_compare_choice_variants()
    test_number_share_ratio_graded()
    test_number_prime_factor_product_uses_mcq()
    test_number_recurring_decimal_uses_fraction_checker()
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
    test_data_rep_overflow_unicode_mcq_variants()
    test_data_rep_core_variants_are_graded()
    test_dr_lossy_lossless_pick_fields()
    test_dr_metadata_pick_fields()
    test_data_rep_multipart_number_systems()
    test_data_rep_variant_queues_are_graded()
    test_data_rep_check_api()
    test_db_sql_variants_are_graded()
    test_db_sql_write_query_exact_grading()
    test_db_sql_multipart_query_writing()
    test_db_sql_variant_queues_are_graded()
    test_db_sql_mcq_option_length_not_biased()
    test_db_sql_check_api()
    test_systems_software_variants_are_graded()
    test_systems_software_classify_match_fields()
    test_systems_software_multipart_inline_fields()
    test_systems_software_exam_pick_variants()
    test_systems_software_variant_queues_are_graded()
    test_systems_software_check_api()
    test_systems_software_mcq_option_length_not_biased()
    test_algorithms_trace_variants_are_graded()
    test_algorithms_multipart_numeric_fields()
    test_algorithms_binary_pseudocode_fix()
    test_algorithms_variant_queues_are_graded()
    test_algorithms_mcq_option_length_not_biased()
    test_algorithms_order_and_pick_variants()
    test_algorithms_flowchart_fix_variants()
    test_algorithms_check_api()
    test_computer_systems_numeric_variants_are_graded()
    test_cs_embedded_constraints_pick_from_bank()
    test_cs_fde_trace_order_steps()
    test_cs_bios_role_order_steps()
    test_cs_multi_core_pick_from_bank()
    test_cs_multipart_cpu_performance_inline_fields()
    test_cs_open_source_os_text_keywords()
    test_cs_d14_multipart_memory_inline_fields()
    test_cs_intermediate_pick_variants()
    test_cs_difficult_pick_order_variants()
    test_cs_foundational_graded_variants()
    test_cyber_security_definition_variants_are_graded()
    test_ethical_definition_variants_are_graded()
    test_cs_definition_topics_check_api()
    test_cy_practice_definition_mcq_variants()
    test_cy_auth_vs_authz_match_mcq()
    test_eth_ethical_vs_legal_match_mcq()
    test_eth_gdpr_principles_pick_from_bank()
    test_eth_cma_offences_pick_from_bank()
    test_eth_surveillance_pick_fields()
    test_eth_job_automation_pick_fields()
    test_eth_implant_ethics_pick_from_bank()
    test_eth_licence_compare_select_all_fields()
    test_eth_ai_bias_definition_and_example_fields()
    test_eth_patent_trademark_match_mcq()
    test_eth_breach_response_order_fields()
    test_eth_exam_structure_order_steps()
    test_eth_right_to_erasure_pick_fields()
    test_eth_mixed_scenario_pick_from_bank()
    test_eth_privacy_debate_pick_fields()
    test_eth_wearable_select_all_impacts()
    test_eth_multipart_legislation_inline_fields()
    test_eth_multipart_smartphone_lifecycle_inline_fields()
    test_eth_planned_obsolescence_match_mcq()
    test_eth_definition_mcq_variants()
    test_cy_gdpr_principles_pick_from_bank()
    test_cy_worm_vs_virus_pick_from_bank()
    test_cy_multipart_attack_scenario_inline_fields()
    test_cy_multipart_data_protection_inline_fields()
    test_cy_backup_match_mcq()
    test_cs_text_partial_score_recorded()
    test_cs_text_problems_expose_grading_keywords()
    test_cs_definition_variant_queues_are_graded()
    test_python_mcq_variants_are_graded()
    test_python_ungraded_variants_remain_ungraded()
    test_python_run_variants_are_graded()
    test_python_run_checker_unit()
    test_python_run_error_sanitizer()
    test_python_run_rejects_password_loop_without_input()
    test_python_tier3_variants_are_graded()
    test_python_variant_queues_are_graded()
    test_python_mcq_check_api()
    test_python_run_check_api()
    test_computer_networks_numeric_variants_are_graded()
    test_computer_networks_multipart_inline()
    test_computer_networks_mcq_option_length_not_biased()
    test_computer_systems_networks_variant_queues()
    test_computer_systems_networks_check_api()
    test_checker_linear_unit()
    test_checker_quadratic_roots_unit()
    test_checker_vector_unit()
    test_checker_linear_equation_and_keyword_unit()
    test_checker_number_estimate_unit()
    test_graphs_core_variants_are_graded()
    test_graphs_multipart_and_choice_variants()
    test_graphs_variant_queues_are_graded()
    test_equations_linear_variants_are_graded()
    test_equations_quadratic_roots_variants_are_graded()
    test_equations_ungraded_variants_remain_ungraded()
    test_equations_linear_inequality_variants_are_graded()
    test_equations_compound_inequality_variants_are_graded()
    test_equations_number_line_variants_are_graded()
    test_equations_formula_fraction_variants_are_graded()
    test_equations_algebraic_rearrange_variants_are_graded()
    test_equations_show_that_checkpoint_variants_are_graded()
    test_equations_completed_square_variants_are_graded()
    test_equations_coordinate_pairs_variants_are_graded()
    test_equations_multipart_number_fields_variants_are_graded()
    test_check_two_var_equation()
    test_check_linear_inequality()
    test_check_linear_inequality_natural_text()
    test_check_compound_inequality()
    test_check_number_line()
    test_check_formula_fraction()
    test_check_algebraic_kinetic_formula()
    test_check_algebraic_power_and_product_flexibility()
    test_check_coordinate_pairs()
    test_equations_simple_inequality_check_api()
    test_equations_number_line_check_api()
    test_equations_formula_fraction_check_api()
    test_equations_rearrange_complex_check_api()
    test_equations_simult_quadratic_check_api()
    test_equations_cafe_multipart_check_api()
    test_equations_kinetic_var_check_api()
    test_equations_phone_plans_check_api()
    test_equations_variant_queues_are_graded()
    test_equations_check_api_linear_and_quadratic()
    test_vectors_vector_variants_are_graded()
    test_vectors_combo_variants_are_graded()
    test_vectors_pair_variants_are_graded()
    test_check_vector_combo()
    test_check_vector_pair()
    test_vectors_geometric_ratio_check_api()
    test_vectors_trapezium_ratio_check_api()
    test_vectors_simultaneous_check_api()
    test_vectors_ungraded_variants_remain_ungraded()
    test_vectors_plan_b_scaffold_variants_are_graded()
    test_vectors_plan_c_step_bank_variants_are_graded()
    test_vectors_variant_queues_are_graded()
    test_vectors_check_api()
    test_trig_number_variants_are_graded()
    test_trig_exact_variants_are_graded()
    test_trig_keyword_variants_are_graded()
    test_trig_ungraded_variants_remain_ungraded()
    test_trig_plan_b_scaffold_variants_are_graded()
    test_trig_variant_queues_are_graded()
    test_transformations_coord_variants_are_graded()
    test_transformations_number_variants_are_graded()
    test_transformations_ungraded_variants_remain_ungraded()
    test_transformations_variant_queues_are_graded()
    test_constructions_loci_number_variants_are_graded()
    test_constructions_loci_fields_variants_are_graded()
    test_constructions_loci_proof_steps_variants_are_graded()
    test_constructions_loci_ungraded_variants_remain_ungraded()
    test_constructions_loci_variant_queues_are_graded()
    test_trig_exact_fraction_check()
    test_trig_exact_surd_fraction_check()
    test_trig_check_api()
    test_simultaneous_pair_variants_are_graded()
    test_simultaneous_ungraded_variants_remain_ungraded()
    test_simultaneous_variant_queues_are_graded()
    test_graphical_simultaneous_variants_are_graded()
    test_graphical_simultaneous_mcq_practice_variants()
    test_graphical_simultaneous_variant_queues_are_graded()
    test_simultaneous_graph_interpret_is_mcq()
    test_simultaneous_check_api()
    test_completing_the_square_variants_are_graded()
    test_completing_the_square_variant_queues_are_graded()
    test_quadratic_simultaneous_variants_are_graded()
    test_quadratic_simultaneous_mcq_practice_variants()
    test_quadratic_simultaneous_variant_queues_are_graded()
    test_quadratic_simultaneous_intersection_meaning_is_mcq()
    test_completing_the_square_check_api()
    test_check_completed_square()
    test_completing_the_square_completed_square_api()
    test_quadratic_simultaneous_check_api()
    test_changing_the_subject_variants_are_graded()
    test_changing_the_subject_mcq_practice_variants()
    test_changing_the_subject_variant_queues_are_graded()
    test_check_changing_the_subject_simple_fraction()
    test_functions_variants_are_graded()
    test_functions_variant_queues_are_graded()
    test_functions_composite_rule_check_api()
    test_functions_inverse_linear_check_api()
    test_functions_multipart_composite_inverse_check_api()
    test_functions_multipart_quadratic_graph_check_api()
    test_functions_multipart_domain_range_check_api()
    test_changing_the_subject_check_api()
    test_functions_check_api()
    test_standard_form_check_api()
    test_number_generator_payload()
    test_number_variant_queue_graded_when_numeric()
    test_number_practice_pool_has_graded_variants()
    test_check_api_without_session()
    test_check_api_with_session_binding()
    test_check_api_number_fields_partial_with_session()
    test_geometry_core_variants_are_graded()
    test_geometry_multipart_variants_use_number_fields()
    test_geometry_proof_variants_use_plan_b_scaffolds()
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
    test_pythagoras_proof_check_uses_choice_buttons()
    test_pythagoras_distance_formula_graded()
    test_checker_surd_unit()
    test_pythagoras_surd_check_api()
    test_pythagoras_variant_queues_are_graded()
    test_pythagoras_check_api()
    test_compound_measures_number_variants_are_graded()
    test_compound_measures_algebraic_variants_are_graded()
    test_compound_measures_scaffold_variants_are_graded()
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
    test_sequences_mcq_variants_are_graded()
    test_sequences_number_list_variants_are_graded()
    test_sequences_algebraic_variants_are_graded()
    test_sequences_plan_c_step_bank_variants_are_graded()
    test_sequences_variant_queues_are_graded()
    test_sequences_check_api()
    test_sequences_algebraic_check_api()
    test_algebraic_proof_ungraded_variants_remain_ungraded()
    test_algebraic_proof_proof_steps_variants_are_graded()
    test_algebraic_proof_algebraic_variants_are_graded()
    test_algebraic_proof_multipart_variants_use_number_fields()
    test_algebraic_proof_counterexample_variants_are_graded()
    test_algebraic_proof_variant_queues_are_graded()
    test_algebraic_proof_algebraic_check_api()
    test_similarity_congruence_graded_variants_are_graded()
    test_sc_d12_similar_rectangle_algebra_is_randomizable()
    test_sc_d3_altitude_multipart_fields()
    test_similarity_congruence_proof_step_variants_are_graded()
    test_similarity_congruence_ungraded_variants_remain_ungraded()
    test_similarity_congruence_mcq_fields_have_options()
    test_similarity_congruence_variant_queues_are_graded()
    test_similarity_congruence_check_api()
    test_similarity_congruence_single_field_session_check()
    test_circle_theorems_graded_variants_are_graded()
    test_circle_theorems_ungraded_variants_remain_ungraded()
    test_circle_theorems_algebra_variants_use_number_fields()
    test_circle_theorems_variant_queues_are_graded()
    test_circle_theorems_check_api()
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
