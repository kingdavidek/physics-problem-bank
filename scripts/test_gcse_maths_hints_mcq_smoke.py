"""Smoke test for the notes on multiple-choice distractors (docs/GCSE_MATHS_HINTS.md section 19, Phase 4). About 10 s.

What it pins:

* ``catalogue``: every note id a generator or a bank row uses has a note, every note is used, no digit in a note
  (D5: a note never shows a value), and the unit table of the option helpers (tagging, ambiguity, the key never gets
  a note, shuffling keeps a note on its option).
* ``verified``: for every procedural multiple-choice generator of waves A and B, over a fixed set of seeds, each note
  is checked by ``gcse_verify/mcq_notes.py`` (written independently from the maths): it recomputes the slip from the
  recorded inputs and the option must equal it. Coverage (verified distractors over all distractors of those
  generators) must stay at or above 50%. Mutation tests: a note moved to another option, or an option changed by one,
  must fail the verifier.
* ``bank``: every ``BANK_WHY`` row names a real bank item with that key, its slip expression (when it has one)
  is recomputed, and each row plus the words of its note is a reviewed pin.
* ``drift``: the multiple-choice questions of the tagged generators are byte for byte what they were before Phase 4
  (a pinned hash of question, options and key over fixed seeds).
* ``leak``: no note text and no ``option_notes`` key in the practice page, a data attribute, the generate API, a
  frozen or previewed set-work payload, the lesson quiz question responses, saved or shared copies.
* ``endpoint``: ``POST /api/v1/problems/option-note`` works for a guest, serves only the session practice problem,
  refuses a stale ``qid``, a bad letter, Quick Test and lesson questions, gives '' for the key or a silent option,
  and is rate limited.
* ``graded``: set work and the lesson quiz results carry the note after grading, for a wrong pick only.
* ``review``: the cases found in the independent review (section 20): an option that is the key rounded keeps no
  note; an option in other units worth the key ("300 m" for "0.3 km") never verifies; a slip is never rounded to
  fewer places than the key prints; an equal split of an odd total, a change that is not a whole number of pounds and
  a common factor below the HCF are never named as other slips.
* ``client``: the page and script pieces, and the byte caps.

Not covered here: the real browser flow (Playwright by hand; section 19 lists the screenshots).
"""
from __future__ import annotations

import collections
import contextlib
import hashlib
import importlib
import io
import json
import os
import pkgutil
import random
import re
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
os.environ.setdefault('PB_TESTING', '1')
os.environ.setdefault('PB_ALLOW_DEV_SECRET', '1')
os.environ.setdefault('CORS_ORIGINS', 'https://app.example.com')

from generators.shared import mcq_notes as COPY  # noqa: E402
from generators.shared import option_notes as ON  # noqa: E402
from generators.shared import verify_hook  # noqa: E402
from gcse_verify import mcq_notes as V  # noqa: E402

warnings.filterwarnings('ignore', category=SyntaxWarning)
START = time.time()
BUDGET_SECONDS = 12.0
SEEDS = 5                       # per generator for the verification (the build notes were run with 40)
COVERAGE_FLOOR = 0.50           # share of procedural distractors of waves A and B with a verified note

WAVES = ('mensuration', 'pythagoras', 'trigonometry', 'number', 'fdp', 'decimals', 'bidmas', 'compound_measures',
         'ratio_proportion')

# Byte ledger (docs/GCSE_MATHS_HINTS.md section 19)
SITE_JS_BASE_BYTES = 209_541        # after Phase 3, before Phase 4
SITE_JS_PHASE4_MAX_ADD = 900
SITE_JS_CARD_MAX_ADD = 1_250        # 2026-11-04: hint card and greyed Show answer (also in the ladder smoke)
SITE_JS_NOTE_MAX_ADD = 800         # 2026-11-07: the wrong-answer note behind "Add a note" (also in the ladder smoke)
SITE_JS_COACH_MAX_ADD = 300        # 2026-11-08: E10 phase 3 coach events, +269 B (also in the ladder smoke)
SITE_JS_RECOVERY_MAX_ADD = 1300    # 2026-11-10: E11 Phase 2 Recovery badges, +804 B; 2026-11-11: answer_seen, +466 B (also in the ladder smoke)
PRACTICE_CSS_BYTES = 31_947         # Phase 4 adds none
CSS_PHASE4_MAX_ADD = 200

# Reviewed pins (2026-10-26): the hash of each BANK_WHY row and the words of its note. Change a row, a bank question or
# a note and this must be re-reviewed on purpose.
BANK_PINS = {
    'bank.left_to_right|What is 2 + 3 × 4?|20': '6d4bc4f0cb',
    'bank.left_to_right|What is 10 − 2 × 3?|24': 'd30c28b943',
    'bank.left_to_right|3 + 4 × 2 − 1 =|13': 'e2f3d726fa',
    'bank.square_the_product|Calculate 2 × 3²|36': '5779ea0316',
    'bank.neg_base_bracket|What is \\( \\left(-2\\right)^{2} \\)?|−4': '24d4d9087e',
    'bank.neg_outside_power|What is \\( -\\left(2\\right)^{2} \\)?|4': 'bd88a97e89',
    'mcq.pct_as_amount|Increase 80 by 10% gives:|90': 'f040b4c4c1',
    'mcq.pct_as_amount|£150 is increased by 12%. What is the new amount?|£162': 'cf40bcb6bc',
    'mcq.pct_as_amount|A £80 coat is reduced by 25% in a sale. What is the sale price?|£55': '62de395254',
    'bank.pct_change_base|A price drops from £50 to £40. The percentage decrease is:|25%': '0ad448f8be',
    'bank.pct_diff_not_share|A price drops from £50 to £40. The percentage decrease is:|10%': 'd36119ebd0',
    'bank.pct_diff_not_share|A value rises from 50 to 65. What is the percentage increase?|15%': 'a0635c9c45',
    'bank.pct_change_base|Bought for £40, sold for £52. The percentage profit is:|23%': 'a548504db8',
    'bank.pct_diff_not_share|Bought for £40, sold for £52. The percentage profit is:|12%': '697955fbdd',
    'bank.pct_successive|£200 is increased by 10% then decreased by 10%. The final amount is:|£200': '0f23dd1b15',
    'bank.reverse_pct|After a 20% discount, the price is £56. What was the original price?|£67.20': '14ffb700c4',
    'mcq.ratio_smaller_share|Share £165 in the ratio 4:7. How much is the larger share?|£60': '93fed17614',
    'bank.part_not_rest|420 pupils: 5/12 walk to school. How many do not walk?|175': '62670be0d4',
    'bank.decimal_point_lost|2.4 × 1.5 =|36': '09ea4b1751',
    'bank.decimal_point_lost|1.2 × 0.5 =|6': '78c12918a1',
    'bank.shift_wrong_way|3.2 × 10 =|0.32': '80974c16b8',
    'bank.round_cut|Round 4.567 to 2 decimal places:|4.56': '48554e78d9',
    'bank.multiplied_not_divided|2.4 kg costs £7.20. The cost per kilogram is:|£17.28': '234b3974fe',
    'bank.longer_is_bigger|Which is the largest?|0.091': '04fb44ae04',
    'bank.longer_is_bigger|Which is the largest?|0.099': '75db9201ed',
    'bank.longer_is_bigger|Which is the largest?|0.19': 'b7eddc8350',
    'bank.not_simplified|0.75 as a fraction in simplest form is:|75/100': '0d382bfce7',
    'bank.not_simplified|20% as a fraction in simplest form is:|2/10': '4334365515',
    'bank.decimal_pct_label|3/5 as a percentage is:|0.6%': '140f1f4348',
    'bank.decimal_pct_label|0.25 as a percentage is:|0.25%': '13b4d5431c',
    'bank.area_scale_linear|A triangle with area 5 cm² is enlarged by scale factor 4. What is the area of the image?|20 cm²': 'd78253c6a1',
    "trans.enlarge_added|Triangle PQR is enlarged by scale factor 3, centre the origin. If P = (2, 1), where is P'?|(5, 4)": 'cae360cefa',
    'trans.line_ignored|What is the image of (5, 2) under a reflection in the line \\(x = 3\\)?|(−5, 2)': 'd4a9a0a57f',
    'trans.wrong_axis|The point (3, 4) is reflected in the x-axis. What are the new coordinates?|(−3, 4)': '450df9e5c7',
    'trans.coords_swapped|The point (3, 4) is reflected in the x-axis. What are the new coordinates?|(4, 3)': '667f89c0d2',
    'trans.wrong_axis|The point (2, 5) is reflected in the y-axis. What are the new coordinates?|(2, −5)': 'c69c876394',
    'trans.coords_swapped|The point (2, 5) is reflected in the y-axis. What are the new coordinates?|(5, 2)': 'aa1d2ad21f',
    'trans.rotate_opposite|What is the image of (3, 1) under a rotation of 90° clockwise about the origin?|(−1, 3)': '6f139b9234',
    'trans.translate_opposite|A shape is translated by \\(\\begin{pmatrix}−2\\\\5\\end{pmatrix}\\). Which statement is true?|Each point moves 2 right and 5 down': '56dc297cdf',
    'vec.added_for_sub|If \\(\\mathbf{a} = \\begin{pmatrix} 4 \\\\ -2 \\end{pmatrix}\\) and \\(\\mathbf{b} = \\begin{pmatrix} 1 \\\\ 3 \\end{pmatrix}\\), then \\(\\mathbf{a} - \\mathbf{b}\\) =|(5, 1)': '712870b548',
    'vec.order_reversed|If \\(\\mathbf{a} = \\begin{pmatrix} 4 \\\\ -2 \\end{pmatrix}\\) and \\(\\mathbf{b} = \\begin{pmatrix} 1 \\\\ 3 \\end{pmatrix}\\), then \\(\\mathbf{a} - \\mathbf{b}\\) =|(-3, 5)': '3d5e8a43a6',
    'bank.magnitude_added|The magnitude of \\(\\begin{pmatrix} 6 \\\\ 8 \\end{pmatrix}\\) is:|14': '89aeda80b9',
    'bank.magnitude_unrooted|The magnitude of \\(\\begin{pmatrix} 6 \\\\ 8 \\end{pmatrix}\\) is:|100': 'e74be464fe',
    'bank.magnitude_added|The position vectors of points P and Q are \\(\\overrightarrow{OP} = \\begin{pmatrix} 1 \\\\ 2 \\end{pmatrix}\\) and \\(\\overrightarrow{OQ} = \\begin{pmatrix} 4 \\\\ 6 \\end{pmatrix}\\). What is the length of \\(\\overrightarrow{PQ}\\)?|7': 'a01fc366cd',
    'bank.magnitude_unrooted|The position vectors of points P and Q are \\(\\overrightarrow{OP} = \\begin{pmatrix} 1 \\\\ 2 \\end{pmatrix}\\) and \\(\\overrightarrow{OQ} = \\begin{pmatrix} 4 \\\\ 6 \\end{pmatrix}\\). What is the length of \\(\\overrightarrow{PQ}\\)?|25': '0747891065',
    'bank.back_bearing_same|The bearing of B from A is 065°. What is the bearing of A from B?|065°': 'f7ef3cf7eb',
    'bank.bearing_over_turn|The bearing of B from A is 230°. What is the bearing of A from B?|410°': '707655e3e4',
    'ang.parallel_equal|Two parallel lines are cut by a transversal. One angle is 65°. What is the alternate interior angle?|115°': '6b51b64707',
    'ang.cointerior_total|Two angles are co-interior (allied angles) on parallel lines. One is 72°. What is the other?|72°': '76f91cde9b',
    'bank.isosceles_not_halved|An isosceles triangle has an apex angle of 40°. What is each base angle?|140°': '40f009678e',
    'bank.cyclic_equal|ABCD is a cyclic quadrilateral. Angle A = 112°. What is angle C?|112°': '24e48ad32f',
    'bank.cyclic_equal|ABCD is a cyclic quadrilateral. Angle DAB = 115°. Find angle BCD.|115°': '48fa53b6af',
    'bank.centre_halved|O is the centre of a circle. Angle ACB = 38°. What is angle AOB?|19°': '7b0fbff1eb',
    'bank.angle_same_centre|O is the centre of a circle. Angle ACB = 38°. What is angle AOB?|38°': '4eb096cd4f',
    'bank.exterior_interior|What is the exterior angle of a regular pentagon?|108°': 'ece995361d',
    'seq.constant_forgotten|The nth term of a sequence is \\(3n + 5\\). What is the 10th term?|30': '575911e378',
    'seq.position_off|The nth term of a sequence is \\(3n + 5\\). What is the 10th term?|38': '89ce43e8b0',
    'seq.first_term_constant|Which of the following is the nth term of the sequence 5, 8, 11, 14, ...?|\\(3n + 5\\)': '3fdc7a858f',
    'bank.second_diff|The second differences of a sequence are all equal to 4. What is the coefficient of \\(n^2\\) in the nth term?|4': '30589989b4',
    'bank.seq_back_one_step|The 4th term of an arithmetic sequence is 22 and the common difference is 5. What is the first term?|17': 'd50513d5b4',
    'bank.seq_start_zero|The nth term 3n + 2 gives:|2, 5, 8, …': '74a1eb6707',
    'bank.same_operation|Solve: x + 5 = 12|x = 17': '7693bce25f',
    'alg.wrong_inverse|Solve: 3x = 15|x = 45': '86c09e5513',
    'bank.same_operation|Solve: 2x + 1 = 9|x = 10': '376063e00f',
    'sim.not_divided|Solve: 2x + 1 = 9|x = 8': 'd278a5b1da',
    'alg.sign_moved|What is the solution to \\(3x + 5 = 14\\)?|x = 19/3': '0f3dc48f27',
    'alg.expand_cross_missed|Expand: (x + 3)(x + 2)|x² + 6': '9d4c6b213b',
    'bank.like_terms_multiplied|Simplify: 4a + 3a|12a': '69f866b412',
    'bank.like_terms_power|Simplify: 4a + 3a|7a²': '269b1ee967',
    'bank.root_both_signs|Solve x² = 16|x = 4 only': '8e0d46a320',
    'bank.square_halved|Solve x² = 16|x = 8': 'dcf618ecae',
    'bank.divided_by_x|Solve: x² = 2x|x = 2 only': '0de47af084',
    'bank.dos_same_signs|Factorise: x² − 9|(x − 3)(x − 3)': '01d26b85b2',
    'bank.product_numbers_added|Simplify: 3x² × 2x|5x³': 'cd7caaca65',
    'bank.product_powers|Simplify: 3x² × 2x|6x²': 'e8ed19d444',
    'bank.rearrange_divide_one|Make x the subject: y = 2x + 1|x = y/2 − 1': '342b6b989d',
    'bank.rearrange_unfinished|Make x the subject: y = 2x + 1|x = y − 1': '7861249aa3',
    'alg.root_signs|Solve: x² − 5x + 6 = 0|x = −2 or x = −3': '81a3dfba0d',
    'alg.root_signs|What are the solutions to \\(x^2 - 5x + 6 = 0\\)?|x = −2 or x = −3': '12ce08dd28',
    'alg.root_signs|Which gives the solutions to \\(x^2 + 2x - 8 = 0\\)?|x = −2 or x = 4': 'c8f96740ce',
    'bank.ineq_not_flipped|Solve \\(-3x \\geq 12\\). Which answer is correct?|\\(x \\geq -4\\)': '176211daa6',
    'bank.discriminant_sign|The discriminant of \\(2x^2 - 3x + 1 = 0\\) is:|17': 'b436266028',
    'bank.sim_other_letter|Solve simultaneously: \\(x + y = 7\\) and \\(x - y = 3\\). What is \\(x\\)?|x = 2': 'cb9a01b719',
    'bank.sim_other_letter|Solve simultaneously: \\(x + y = 10\\) and \\(x - y = 4\\). What is \\(y\\)?|y = 7': '4d04cffefc',
    'bank.sim_constants_added|\\(2x + 3y = 12\\) and \\(2x + y = 8\\). After eliminating \\(x\\), you get:|\\(2y = 20\\)': '96b6a3e12b',
    'bank.sim_letters_added|\\(2x + 3y = 12\\) and \\(2x + y = 8\\). After eliminating \\(x\\), you get:|\\(4y = 4\\)': '4513e870a0',
}
# The hash of the multiple-choice questions of the tagged generators, before and after Phase 4 (must not move).
# Moved on 2026-10-27 (variety Phase 2) for number_mcq 15, 17 and 18 only: a wrong-key-free formatting fix (the 1 d.p.
# error option, "52.0 x 10^-5", and money to the penny).  Every other tagged generator hashes as before.
# Moved again on 2026-10-27 (Phase 2 review) for _trig_proc_find_side only: at 45 degrees the side itself was both the
# key and a distractor (fillers 11 and 12 stood in) and the options mixed "10" with "5.0"; every option is now to 1 d.p.
# and the 45-degree slips are sin 45 times the side and the side over sin 45 (both trig.wrong_ratio, verified).
# Moved again on 2026-11-03 (whole-change review pass 3) for number_mcq 6 (money to the penny; its third option is the
# decrease slip, no longer a repeat) and _sim_proc_elimination (equations labelled (1) and (2); subtract (1) from (2)).
# 2026-11-03: re-pinned after em dashes were removed from step labels and hints in maths_bank_procedural_mcq.py (text only)
DRIFT_PIN = '1fedb043e3a069ca'

ISSUES = collections.defaultdict(list)


def issue(check, where, detail):
    ISSUES[check].append(f'{where}: {detail}')


def expect(check, where, cond, detail):
    if not cond:
        issue(check, where, detail)


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def quiet(fn, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def misconceptions_messages():
    """Every reviewed misconception message: a note the endpoint may return for a question whose option carries a tag from a generator."""
    from generators.shared import misconceptions
    return list(misconceptions.MESSAGES.values())


def all_note_texts():
    texts = list(COPY.NOTES.values()) + list(COPY.BANK_NOTES.values())
    from generators.shared import misconceptions
    texts += [misconceptions.MESSAGES[i] for i in {r[0] for r in COPY.BANK_WHY} if i in misconceptions.MESSAGES]
    return texts


# ─────────────────────────────────────────────────────────────────────────────
# the scope: the procedural multiple-choice generators of waves A and B
# ─────────────────────────────────────────────────────────────────────────────

def scope():
    from generators.gcse import maths_bank_procedural_mcq as P
    from generators.gcse import maths_num_stats_prob_rat as N
    out = []
    for slug in WAVES:
        for fn in P.procedural_mcq_for(slug):
            out.append((slug, fn.__name__, fn))
    out += [('number', f'number_mcq_{k}', lambda k=k: N.number_mcq(k)) for k in range(1, 19)]
    out += [('ratio_proportion', f'ratio_mcq_{k}', lambda k=k: N.ratio_proportion_mcq(k)) for k in range(1, 10)]
    return out


# ─────────────────────────────────────────────────────────────────────────────
# catalogue and helper unit table
# ─────────────────────────────────────────────────────────────────────────────

def check_catalogue():
    used = set()
    for rel in ('generators/gcse/maths_bank_procedural_mcq.py', 'generators/gcse/maths_num_stats_prob_rat.py'):
        used |= set(re.findall(r"'((?:mcq|bank)\.[a-z0-9_]+)'", read(rel)))
    used |= {r[0] for r in COPY.BANK_WHY}
    for note_id in sorted(used):
        expect('catalogue', note_id, bool(ON.note_text(note_id)), 'a generator or a bank row uses an id that has no note')
    defined = set(COPY.NOTES) | set(COPY.BANK_NOTES)
    for note_id in sorted(defined - used):
        expect('catalogue', note_id, False, 'a note nothing uses (dead copy)')
    for note_id in sorted(defined):
        text = ON.note_text(note_id)
        expect('catalogue', note_id, not re.search(r'\d', text), f'a note must show no value (D5): {text!r}')
        expect('catalogue', note_id, '\u2014' not in text and '\u2013' not in text, 'no dash')
        expect('catalogue', note_id, not re.search(r'\b(?:the answer is|equals)\b', text.lower()), f'a note must not give the answer: {text!r}')

    # option helpers
    opts = ['A  10', 'B  12', 'C  14', 'D  16']
    texts = ['10', '12', '14', '16', '12']
    notes = ON.notes_for(opts, texts, ['n.a', 'n.b', None, 'n.c', 'n.b'])
    expect('catalogue', 'notes_for', notes == {'10': 'n.a', '12': 'n.b', '16': 'n.c'}, f'got {notes}')
    clash = ON.notes_for(opts, ['12', '12'], ['n.a', 'n.b'])
    expect('catalogue', 'notes_for', clash == {}, 'two ids on one text must give no note (prefer silence)')
    gone = ON.notes_for(opts, ['99'], ['n.a'])
    expect('catalogue', 'notes_for', gone == {}, 'a tagged candidate that is not an option gets no note')
    plain, tags = ON.split([5, (6, 'n.x'), (7, 8), 'q'])
    expect('catalogue', 'split', plain == [5, 6, (7, 8), 'q'] and tags == [None, 'n.x', None, None], f'{plain} {tags}')
    prob = {'options': opts, 'correct_answer': 'B', 'question': 'q'}
    expect('catalogue', 'with_notes', ON.KEY not in ON.with_notes(dict(prob), {'12': 'n.b'}), 'the key must never carry a note')
    expect('catalogue', 'with_notes', ON.with_notes(dict(prob), {'10': 'n.a', '99': 'n.z'}).get(ON.KEY) == {'10': 'n.a'},
           'a note for an option that does not exist must be dropped')
    dup = {'options': ['A  1', 'B  1', 'C  2'], 'correct_answer': 'C', 'question': 'q'}
    expect('catalogue', 'with_notes', ON.KEY not in ON.with_notes(dup, {'1': 'n.a'}), 'duplicate option texts: silence')
    four = {'options': ['A  1', 'B  2', 'C  3', 'D  4'], 'correct_answer': 'A', 'question': 'q'}
    expect('catalogue', 'with_notes', ON.with_notes(four, {'1': 'a', '2': 'b', '3': 'c', '4': 'd'}).get(ON.KEY) == {'2': 'b', '3': 'c', '4': 'd'},
           'all four options noted: the key still gets none')

    # picked_note: the key, an unknown letter, a silent option and a damaged problem give ''
    real = {'options': ['A  1', 'B  2', 'C  3', 'D  4'], 'correct_answer': 'B', 'question': 'q',
            ON.KEY: {'1': 'mcq.index_mult', '3': 'bank.left_to_right'}}
    expect('catalogue', 'picked_note', ON.picked_note(real, 'A') == COPY.NOTES['mcq.index_mult'], 'note for a distractor')
    expect('catalogue', 'picked_note', ON.picked_note(real, 'C') == COPY.BANK_NOTES['bank.left_to_right'], 'bank note')
    for letter in ('B', 'D', 'Z', '', None, 'a b', 7):
        want = COPY.NOTES['mcq.index_mult'] if str(letter).strip().upper()[:1] == 'A' else ''
        expect('catalogue', f'picked_note {letter!r}', ON.picked_note(real, letter) == want, 'wrong note or a note for the key')
    for bad in (None, {}, {'options': 3}, {ON.KEY: 'x'}, {ON.KEY: {'1': 'nope'}, 'options': ['A  1'], 'correct_answer': 'B'}):
        expect('catalogue', 'picked_note', ON.picked_note(bad, 'A') == '', f'a damaged problem {bad!r} must give nothing')
    qid = ON.fingerprint(real)
    expect('catalogue', 'fingerprint', qid == ON.fingerprint(dict(real, correct_answer='A')) and qid != ON.fingerprint(dict(real, question='r')),
           'the fingerprint depends on the question and options, never on the key')

    # a shuffled question keeps each note on its option text
    from generators.shared.utils import make_problem
    for seed in range(8):
        random.seed(seed)
        p = make_problem('Q?', 'sol', 'hint', 'foundational', 1, 'gcse', 'maths', 'x',
                         options=['A  1', 'B  2', 'C  3', 'D  4'], correct_answer='B')
        by_text = {o[3:]: o[0] for o in p['options']}
        expect('catalogue', 'shuffle', by_text['2'] == p['correct_answer'], 'the key moved off its text')


# ─────────────────────────────────────────────────────────────────────────────
# verified notes and coverage
# ─────────────────────────────────────────────────────────────────────────────

def check_verified():
    total = collections.Counter()
    verified = collections.Counter()
    samples = []                                            # (note id, family, inputs, text, key) that verified
    for slug, label, fn in scope():
        for seed in range(SEEDS):
            random.seed(1000 + seed)
            with verify_hook.recording() as sink, ON.capture() as notes:
                q, _sol, _hint, _marks, opts, letter = quiet(fn)
            texts = {o[0]: o[3:] for o in opts}
            key = texts[letter]
            total[slug] += len(opts) - 1
            for text, note_id in notes.items():
                if text not in texts.values() or text == key:
                    issue('verified', label, f'note {note_id} on a missing option or on the key ({text!r})')
                    continue
                ok, why = False, 'the generator recorded no inputs'
                for rec in sink:
                    ok, why = V.verify_option(note_id, rec['family'], rec['inputs'], text, key)
                    if ok:
                        samples.append((note_id, rec['family'], rec['inputs'], text, key))
                        break
                if ok:
                    verified[slug] += 1
                else:
                    issue('verified', f'{label} seed {seed}', f'{note_id} on {text!r} is not verified: {why} (q {q[:50]!r})')
    all_total = sum(total.values())
    all_ok = sum(verified.values())
    share = all_ok / max(all_total, 1)
    expect('verified', 'coverage', share >= COVERAGE_FLOOR, f'{all_ok} of {all_total} distractors verified ({share:.0%}), floor {COVERAGE_FLOOR:.0%}')
    expect('verified', 'samples', len(samples) >= 150, f'only {len(samples)} verified notes in the sample')

    # mutation tests: a note must fail on an option the slip does not give
    moved = survived = 0
    for note_id, family, inputs, text, key in samples:
        opt = V.read(text)
        if opt.kind != 'num' or opt.value is None or opt.dp < 0:
            continue
        # change the option by one in its last place
        step = V.F(1) / (10 ** opt.dp)
        for delta in (step, -step):
            value = opt.value + delta
            shown = f'{float(value):.{opt.dp}f}'
            mutated = re.sub(r'-?\d+(?:\.\d+)?', shown.replace('-', '−') if value < 0 else shown, text, count=1)
            if V.read(mutated).value == opt.value:
                continue
            moved += 1
            ok, _why = V.verify_option(note_id, family, inputs, mutated, key)
            survived += ok
    expect('verified', 'mutation', moved >= 100, f'only {moved} mutations tried')
    expect('verified', 'mutation', survived <= max(1, moved // 50),
           f'{survived} of {moved} options changed by one still verified; the verifier is too loose')
    # an option equal to the key is never verified, whatever the slip says
    note_id, family, inputs, text, key = samples[0]
    expect('verified', 'key', V.verify_option(note_id, family, inputs, key, key)[0] is False, 'an option worth the key was verified')
    # the id swapped for another slip's id must fail for nearly all
    ids = sorted({s[0] for s in samples})
    swapped = tried = 0
    for i, (note_id, family, inputs, text, key) in enumerate(samples):
        other = ids[(ids.index(note_id) + 1) % len(ids)]
        if other == note_id:
            continue
        tried += 1
        swapped += V.verify_option(other, family, inputs, text, key)[0]
    expect('verified', 'mutation', swapped <= max(2, tried // 10), f'{swapped} of {tried} notes verified under another slip id')
    return all_ok, all_total, {s: (verified[s], total[s]) for s in WAVES}


# ─────────────────────────────────────────────────────────────────────────────
# review cases (section 20)
# ─────────────────────────────────────────────────────────────────────────────

def _notes_of(fn, seeds=60, offset=9000):
    """[(question, options by text, key text, {text: note id}, records)] for ``fn`` over fixed seeds."""
    out = []
    for seed in range(seeds):
        random.seed(offset + seed)
        with verify_hook.recording() as sink, ON.capture() as notes:
            q, _sol, _hint, _marks, opts, letter = quiet(fn)
        texts = {o[0]: o[3:] for o in opts}
        out.append((q, list(texts.values()), texts[letter], dict(notes), list(sink)))
    return out


def check_review():
    from generators.gcse import maths_num_stats_prob_rat as N
    # helper: an option that is the key rounded keeps no note, unless the note is about rounding
    expect('review', 'rounds_from_key', ON.rounds_from_key('6%', '5.9%') and ON.rounds_from_key('£3', '£2.5')
           and not ON.rounds_from_key('6%', '4.6%') and not ON.rounds_from_key('12.38', '12.4')
           and not ON.rounds_from_key('3 km', '0.3 km') and not ON.rounds_from_key('848', '848.72'), 'rounding guard')
    with ON.capture() as sink:
        ON.attach(['A  6%', 'B  5.9%', 'C  6.3%', 'D  1%'], [('6%', 'pct.error_not_compared'), ('6.3%', 'pct.error_wrong_base')], str, '5.9%')
    expect('review', 'attach', sink == {'6.3%': 'pct.error_wrong_base'}, f'the key rounded kept a note: {sink}')
    with ON.capture() as sink:
        ON.attach(['A  12', 'B  12.4', 'C  12.38', 'D  12.5'], [('12', 'mcq.round_dropped'), ('12.38', 'gen.accuracy')], str, '12.4')
    expect('review', 'attach', sink == {'12': 'mcq.round_dropped', '12.38': 'gen.accuracy'}, f'a rounding note was dropped: {sink}')
    # verifier: other units, the key rounded, rounding below the key's places, exact equal split, common factors
    inp = {'scale': 10000, 'cm': 3, 'to': 'km'}
    expect('review', 'units', not V.verify_option('mcq.map_km_factor', 'ratio_map_scale', inp, '300 m', '0.3 km')[0], '300 m verified beside 0.3 km')
    expect('review', 'units', 'worth the same' in V.verify_option('mcq.map_km_factor', 'ratio_map_scale', inp, '300 m', '0.3 km')[1], 'units')
    expect('review', 'key rounded', not V.verify_option('pct.error_not_compared', 'num_pct_error', {'estimate': 96, 'actual': 102}, '6%', '5.9%')[0],
           'an option that is the key rounded verified')
    expect('review', 'key rounded', V.verify_option('pct.error_not_compared', 'num_pct_error', {'estimate': 125, 'actual': 131}, '6%', '4.6%')[0],
           'a true size-of-error option failed')
    expect('review', 'places', not V.verify_option('pct.change_not_applied', 'num_pct_change', {'amount': 10, 'pct': 25, 'sign': 'up'}, '£3', '£12.5')[0],
           'a change of 2.5 verified as "£3"')
    expect('review', 'equal split', not V.verify_option('mcq.ratio_equal_split', 'ratio_larger_share', {'total': 135, 'parts': (2, 7)}, '£67', '£105')[0],
           '£67 verified as half of £135')
    expect('review', 'equal split', V.verify_option('mcq.ratio_equal_split', 'ratio_larger_share', {'total': 90, 'parts': (4, 2)}, '£45', '£60')[0],
           'half of £90 failed')
    expect('review', 'equal split', not V.verify_option('mcq.ratio_equal_split', 'ratio_share_one', {'total': 136, 'parts': (4, 2, 2), 'which': 1}, '68', '34')[0],
           'half of a three-way total verified as an equal split')
    expect('review', 'hcf', not V.verify_option('mcq.hcf_cofactor', 'num_hcf', {'a': 48, 'b': 72}, '2', '24')[0]
           and V.verify_option('mcq.hcf_not_highest', 'num_hcf', {'a': 48, 'b': 72}, '2', '24')[0]
           and V.verify_option('mcq.hcf_cofactor', 'num_hcf', {'a': 60, 'b': 84}, '5', '12')[0]
           and not V.verify_option('mcq.hcf_not_highest', 'num_hcf', {'a': 60, 'b': 84}, '5', '12')[0], 'HCF slips')
    # generators: the cases stay silent or carry the right note on every seed
    for q, opts, key, notes, _recs in _notes_of(lambda: N.ratio_proportion_mcq(4)):
        metres = [t for t in opts if t.endswith(' m')]
        expect('review', 'map metres', not any(t in notes for t in metres), f'a note on a correct answer in metres: {q[:60]!r} {notes}')
    for q, opts, key, notes, _recs in _notes_of(lambda: N.number_mcq(16)):
        for t, n in notes.items():
            want = {'2': 'mcq.hcf_not_highest', '3': 'mcq.hcf_not_highest', '5': 'mcq.hcf_cofactor'}.get(t)
            if want:
                expect('review', 'hcf note', n == want, f'{q!r}: {t} carries {n}, want {want}')
    for k in (2, 9):
        for q, opts, key, notes, recs in _notes_of(lambda k=k: N.ratio_proportion_mcq(k)):
            total = next((r['inputs']['total'] for r in recs if 'total' in r['inputs']), None)
            if total is not None and total % 2:
                expect('review', 'equal split', 'mcq.ratio_equal_split' not in notes.values(), f'odd total {total} named an equal split: {q[:50]!r}')
    for q, opts, key, notes, recs in _notes_of(lambda: N.ratio_proportion_mcq(6)):
        i = recs[0]['inputs']
        if i['amount'] * i['pct'] % 100:
            expect('review', 'rounded change', 'pct.change_not_applied' not in notes.values(), f'a rounded change carried a note: {q[:50]!r} {notes}')
    for q, opts, key, notes, _recs in _notes_of(lambda: N.number_mcq(15)):
        for t in notes:
            expect('review', 'key rounded', not ON.rounds_from_key(t, key), f'{q[:60]!r}: {t} is the key {key} rounded and carries a note')
    expect('review', 'copy', 'mcq.map_unit_step' not in COPY.NOTES and 'not the other way round' not in COPY.NOTES['mcq.pct_of_inverted'],
           'reviewed copy changed back')


# ─────────────────────────────────────────────────────────────────────────────
# bank notes
# ─────────────────────────────────────────────────────────────────────────────

def bank_items():
    import generators.gcse as pkg
    items = []
    for m in pkgutil.iter_modules(pkg.__path__):
        try:
            mod = importlib.import_module('generators.gcse.' + m.name)
        except Exception:  # noqa: BLE001
            continue
        for v in vars(mod).values():
            if isinstance(v, list) and v and all(isinstance(x, dict) and 'q' in x and 'opts' in x for x in v):
                items += v
    return items


def check_bank():
    items = bank_items()
    expect('bank', 'phase5', len(COPY.BANK_WHY) >= 80, f'Phase 5 bank rows (waves C and D) went missing: {len(COPY.BANK_WHY)} rows')
    pins = {}
    for row in COPY.BANK_WHY:
        ok, why = V.verify_bank_row(row, items)
        expect('bank', f'{row[0]} {row[1][:30]}', ok, why)
        text = ON.note_text(row[0])
        pins[f'{row[0]}|{row[1]}|{row[3]}'] = V.bank_row_pin(row, text)
    expect('bank', 'pins', pins == BANK_PINS,
           'the reviewed pins moved: re-review the changed rows then update BANK_PINS ' +
           f'(changed {sorted(k for k in set(pins) | set(BANK_PINS) if pins.get(k) != BANK_PINS.get(k))[:4]})')
    # mutation: a changed distractor or a wrong expression is caught
    row = COPY.BANK_WHY[0]
    expect('bank', 'mutation', not V.verify_bank_row((row[0], row[1], row[2], '21', row[4]), items)[0], 'a changed distractor passed')
    expect('bank', 'mutation', not V.verify_bank_row((row[0], row[1], row[2], row[3], '2+3*4'), items)[0], 'a wrong slip passed')
    expect('bank', 'mutation', not V.verify_bank_row((row[0], row[1], '99', row[3], row[4]), items)[0], 'a wrong key passed')
    expect('bank', 'mutation', not V.verify_bank_row((row[0], 'Other question?', row[2], row[3], row[4]), items)[0], 'a missing item passed')
    expect('bank', 'eval', V.eval_expr('int(4.567*100)/100') == V.F('4.56') and V.eval_expr('-(2**2)') == -4, 'expression evaluator')
    # runtime: a bank question gets its note, a reworded one does not
    q = {'question': 'What is 2 + 3 × 4?', 'options': ['A  20', 'B  14', 'C  24', 'D  9'], 'correct_answer': 'B'}
    expect('bank', 'runtime', ON.bank_notes(q) == {'20': 'bank.left_to_right'}, f'{ON.bank_notes(q)}')
    expect('bank', 'runtime', ON.bank_notes(dict(q, correct_answer='A')) == {}, 'a different key must give nothing')
    expect('bank', 'runtime', ON.bank_notes(dict(q, question='What is 2 + 3 × 5?')) == {}, 'a reworded question must give nothing')
    expect('bank', 'runtime', ON.bank_notes(dict(q, options=['A  21', 'B  14', 'C  24', 'D  9'])) == {}, 'a changed option must give nothing')


# ─────────────────────────────────────────────────────────────────────────────
# drift
# ─────────────────────────────────────────────────────────────────────────────

def check_drift():
    h = hashlib.sha1()
    n = 0
    for slug, label, fn in scope():
        for seed in range(4):
            random.seed(500 + seed)
            q, sol, hint, marks, opts, letter = quiet(fn)
            h.update(json.dumps([label, q, sol, hint, marks, opts, letter], sort_keys=True, ensure_ascii=False).encode())
            n += 1
    got = h.hexdigest()[:16]
    expect('drift', 'questions', got == DRIFT_PIN, f'the tagged generators now give different questions (hash {got}, pinned {DRIFT_PIN}, {n} samples)')
    return n


# ─────────────────────────────────────────────────────────────────────────────
# app helpers
# ─────────────────────────────────────────────────────────────────────────────

HDR = {'Accept': 'application/json'}


def stored(client):
    with client.session_transaction() as sess:
        return json.loads(json.dumps(sess.get('last_problem_payload'), default=str))


def practice_with_notes(client, topics=('bidmas', 'fdp', 'pythagoras', 'mensuration', 'decimals', 'number'), tries=30):
    """Start MCQ practice until the stored problem carries notes; returns (html, stored payload) or (None, None)."""
    for i in range(tries):
        topic = topics[i % len(topics)]
        r = client.post('/', data={'level': 'gcse', 'subject': 'maths', 'topic': topic, 'mode': 'mcq',
                                   'difficulty': 'foundational', 'action': 'start'}, follow_redirects=True)
        payload = stored(client)
        if r.status_code == 200 and payload and (payload.get('problem') or {}).get(ON.KEY):
            return r.data.decode(), payload
    return None, None


def a_note_pick(problem):
    """(letter with a note, letter without one, the key) for a problem with notes."""
    notes = problem[ON.KEY]
    with_note = without = None
    for opt in problem['options']:
        letter, text = opt[0], opt[3:]
        if letter == problem['correct_answer']:
            continue
        if text in notes:
            with_note = with_note or letter
        else:
            without = without or letter
    return with_note, without, problem['correct_answer']


def check_leaks_and_endpoint(app):
    import app as app_module
    texts = all_note_texts()
    with app.test_client() as client:
        html, payload = practice_with_notes(client)
        expect('leak', 'setup', html is not None, 'no practice question with notes in 30 tries')
        if html is None:
            return
        problem = payload['problem']
        qid = ON.fingerprint(problem)
        # --- the practice page
        expect('leak', 'page', ON.KEY not in html and 'option_notes' not in html, 'option_notes is in the page')
        for t in texts:
            if t in html.replace('&#39;', "'"):
                issue('leak', 'page', f'a note text is in the practice page: {t!r}')
                break
        expect('leak', 'page', re.search(r'(?:mcq|bank)\.[a-z_]+', html) is None, 'a note id is in the page')
        m = re.search(r'<div id="mcq-options"[^>]*>', html)
        expect('leak', 'page', m is not None and f'data-note-qid="{qid}"' in m.group(0), 'the options block must carry the question tag')
        if m:
            expect('leak', 'page', not any(o[3:] in m.group(0) and len(o) > 8 for o in problem['options']), 'option text in a data attribute')
        # --- the generate API (a client payload)
        body = client.post('/api/v1/problems/generate', json={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas', 'mode': 'mcq',
                                                              'difficulty': 'foundational', 'action': 'next'}, headers=HDR)
        blob = body.get_data(as_text=True)
        expect('leak', 'generate api', body.status_code == 200 and ON.KEY not in blob and not any(t in blob for t in texts),
               f'the generate API response leaks notes (status {body.status_code})')

        # --- the endpoint on the practice problem
        html, payload = practice_with_notes(client)
        problem = payload['problem']
        qid = ON.fingerprint(problem)
        with_note, without, key = a_note_pick(problem)
        post = lambda **kw: client.post('/api/v1/problems/option-note', json=kw, headers=HDR)  # noqa: E731
        if with_note:
            r = post(letter=with_note, qid=qid)
            want = ON.picked_note(problem, with_note)
            expect('endpoint', 'guest pick', r.status_code == 200 and r.get_json() == {'ok': True, 'note': want} and want,
                   f'{r.status_code} {r.get_json()}')
            expect('endpoint', 'lower case', post(letter=with_note.lower(), qid=qid).get_json().get('note') == want, 'letter case')
        if without:
            expect('endpoint', 'silent option', post(letter=without, qid=qid).get_json() == {'ok': True, 'note': ''}, 'an option without a note')
        r = post(letter=key, qid=qid)
        expect('endpoint', 'the key', r.status_code == 200 and r.get_json() == {'ok': True, 'note': ''}, f'the key must give nothing: {r.get_json()}')
        for bad in ('E', 'AB', '', '1', None):
            r = post(letter=bad, qid=qid)
            expect('endpoint', f'letter {bad!r}', r.status_code == 400 and r.get_json().get('code') == 'invalid_letter', f'{r.status_code}')
        for bad_qid in ('', 'abc', None, qid[:-1], 5):
            r = post(letter=with_note or 'A', qid=bad_qid)
            expect('endpoint', f'qid {bad_qid!r}', r.status_code == 409 and 'note' not in r.get_json(), f'{r.status_code} {r.get_json()}')
        r = client.post('/api/v1/problems/option-note', data='x', headers=HDR)
        expect('endpoint', 'no json', r.status_code == 400, f'{r.status_code}')
        # a new question: the old tag is stale
        practice_with_notes(client)
        new_problem = stored(client)['problem']
        if ON.fingerprint(new_problem) != qid:
            expect('endpoint', 'stale qid', post(letter=with_note or 'A', qid=qid).status_code == 409, 'a stale tab read a note')
        expect('endpoint', 'cookie', True, '')
        # the request cannot name the note, the problem or the key: the answer is exactly the note of the stored question's
        # option A (Phase 2 review: pinned to that, not to "any reviewed text", which a body-honouring endpoint would
        # also have passed), and the note the body names is one that option A of the stored question does not carry
        want_a = ON.picked_note(new_problem, 'A')
        fake = next(i for i, t in COPY.NOTES.items() if t and t != want_a and t not in misconceptions_messages())
        r = client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': ON.fingerprint(new_problem), 'options': ['A  1'],
                                                              'option_notes': {'1': fake}, 'correct_answer': 'D'}, headers=HDR)
        expect('endpoint', 'body ignored', r.status_code == 200 and r.get_json() == {'ok': True, 'note': want_a}, f'{r.get_json()} (want {want_a!r})')

    # no session, no question
    with app.test_client() as client:
        r = client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': 'x'}, headers=HDR)
        expect('endpoint', 'no session', r.status_code == 400 and r.get_json().get('code') == 'session_required', f'{r.status_code} {r.get_json()}')
    # a typed question has no options
    with app.test_client() as client:
        client.post('/', data={'level': 'gcse', 'subject': 'maths', 'topic': 'pythagoras', 'mode': 'standard', 'difficulty': 'foundational',
                               'action': 'start'}, follow_redirects=True)
        r = client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': 'x'}, headers=HDR)
        expect('endpoint', 'typed question', r.status_code == 400, f'{r.status_code}')
    # Quick Test and lesson questions: nothing until the results
    with app.test_client() as client:
        for _ in range(12):
            client.post('/quicktest/start', data={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas', 'mode': 'mcq',
                                                  'difficulty': 'foundational'}, follow_redirects=True)
            payload = stored(client)
            if payload and (payload.get('problem') or {}).get(ON.KEY):
                break
        if payload and (payload.get('problem') or {}).get('options'):
            qid = ON.fingerprint(payload['problem'])
            r = client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': qid}, headers=HDR)
            expect('endpoint', 'quick test', r.status_code == 403 and r.get_json().get('code') == 'not_available', f'{r.status_code} {r.get_json()}')
            expect('endpoint', 'quick test', payload.get('source') == 'quicktest', 'the session lost its Quick Test marker')
        else:
            issue('endpoint', 'quick test', 'could not start a multiple-choice Quick Test question')
    with app.test_client() as client:
        _, payload = practice_with_notes(client)
        with client.session_transaction() as sess:
            sess['last_problem_payload']['mode'] = 'lesson'
            sess.modified = True
        qid = ON.fingerprint(payload['problem'])
        r = client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': qid}, headers=HDR)
        expect('endpoint', 'lesson', r.status_code == 403, f'{r.status_code}')
    # rate limit: counted per question in the signed session, nothing written to the database
    def db_rows():
        from app import get_db
        with get_db() as conn:
            return [tuple(r) for r in conn.execute("SELECT * FROM rate_limit_buckets WHERE bucket_key LIKE 'option_note%'").fetchall()]

    with app.test_client() as client:
        _, payload = practice_with_notes(client)
        qid = ON.fingerprint(payload['problem'])
        old_disabled, old_limit = app_module._rate_limits_disabled, app_module.OPTION_NOTE_PER_QUESTION_LIMIT
        app_module._rate_limits_disabled = lambda: False
        app_module.OPTION_NOTE_PER_QUESTION_LIMIT = 2
        try:
            before = db_rows()
            codes = [client.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': qid}, headers=HDR,
                                 environ_overrides={'REMOTE_ADDR': '10.9.8.7'}).status_code for _ in range(4)]
            after = db_rows()
            # a second client on the same address is not held back by the first
            other = app.test_client()
            _, payload2 = practice_with_notes(other)
            code2 = other.post('/api/v1/problems/option-note', json={'letter': 'A', 'qid': ON.fingerprint(payload2['problem'])},
                               headers=HDR, environ_overrides={'REMOTE_ADDR': '10.9.8.7'}).status_code
        finally:
            app_module._rate_limits_disabled, app_module.OPTION_NOTE_PER_QUESTION_LIMIT = old_disabled, old_limit
        expect('endpoint', 'rate limit', codes[:2] != [429, 429] and codes[-1] == 429, f'status codes {codes}')
        expect('endpoint', 'rate limit shared network', code2 == 200, f'second pupil on the same address got {code2}')
        expect('endpoint', 'rate limit stores nothing', before == after, f'rate_limit_buckets changed: {before} -> {after}')

    # the session cookie stays small with the notes in it
    with app.test_client() as client:
        worst = 0
        for i in range(12):
            r = client.post('/', data={'level': 'gcse', 'subject': 'maths', 'topic': ('number', 'fdp', 'ratio_proportion')[i % 3],
                                       'mode': 'mcq', 'difficulty': 'difficult', 'action': 'start'}, follow_redirects=True)
            with client.session_transaction() as sess:
                ser = app.session_interface.get_signing_serializer(app)
                worst = max(worst, len(ser.dumps(dict(sess))) + 80)     # the cookie value plus its attributes
        expect('endpoint', 'cookie', worst < 3900, f'a session cookie reached {worst} B (browser limit about 4,096)')
        print(f'  largest session cookie seen: {worst} B')


# ─────────────────────────────────────────────────────────────────────────────
# set work, lesson quiz, stored copies
# ─────────────────────────────────────────────────────────────────────────────

def a_problem_with_notes():
    from topic_registry import TOPICS
    for i in range(80):
        topic = ('bidmas', 'fdp', 'decimals', 'pythagoras', 'mensuration', 'number')[i % 6]
        random.seed(i)
        p = quiet(TOPICS['gcse']['maths'][topic]['func'], 'foundational', 'mcq')
        if p and p.get(ON.KEY):
            return topic, p
    raise AssertionError('no multiple-choice problem with notes')


def check_stored_and_graded(app):
    from generators.shared.answer_record import public_problem, public_problems
    from models.class_assignments import (SERVER_ONLY_KEYS, serialize_preview,
                                          serialize_student_work, serialize_teacher_assignment, strip_problem_keys)
    topic, p = a_problem_with_notes()
    texts = all_note_texts()
    with_note, without, key = a_note_pick(p)
    expect('leak', 'server only', ON.KEY in SERVER_ONLY_KEYS, 'option_notes must be a server-only key')
    # storage for sharing, saving, challenges: no notes
    expect('leak', 'public_problem', ON.KEY not in public_problem(p) and ON.KEY in public_problem(p, keep_notes=True),
           'public_problem must strip the notes unless asked to keep them')
    expect('leak', 'public_problem', all(ON.KEY not in q for q in public_problems([p, p])), 'public_problems must strip the notes')
    blob = json.dumps(public_problem(p))
    expect('leak', 'public_problem', not any(t in blob for t in texts), 'a note text is in a stored copy')
    for rel in ('models/sharing.py', 'models/user_data.py', 'models/challenges.py'):
        src = read(rel)
        expect('leak', rel, 'keep_notes' not in src, 'only set work, lesson quizzes and the Quick Test results may keep the notes')
    from app import _freeze_problem_payload, _problem_client_payload
    expect('leak', 'client payload', ON.KEY not in _problem_client_payload(p) and not any(t in json.dumps(_problem_client_payload(p)) for t in texts),
           'the client payload leaks a note')
    # set work: frozen with the notes, never sent before grading
    frozen = _freeze_problem_payload(p)
    expect('leak', 'freeze', frozen.get(ON.KEY) == p[ON.KEY], 'frozen set work must keep the notes for grading')
    for reveal in (False, True):
        expect('leak', f'strip reveal={reveal}', ON.KEY not in strip_problem_keys(frozen, reveal=reveal), 'strip_problem_keys let the notes out')
    base = {'id': 1, 'class_id': 1, 'preview_id': 1, 'class_name': 'c', 'level': 'gcse', 'subject': 'maths', 'topic': topic, 'mode': 'mcq',
            'difficulty': 'foundational', 'question_count': 3, 'status': 'assigned', 'problems': [frozen, frozen, frozen]}
    student = serialize_student_work({**base, 'answers': [None, {'user_answer': with_note, 'correct': False},
                                                          {'user_answer': key, 'correct': True}]})
    teacher = serialize_teacher_assignment({**base, 'recipients': []})
    preview = serialize_preview(base)
    for name, blob in (('student', json.dumps(student)), ('teacher', json.dumps(teacher)), ('preview', json.dumps(preview))):
        expect('leak', f'set work {name}', ON.KEY not in blob, 'option_notes in a set-work payload')
    pre = json.dumps(serialize_student_work({**base, 'answers': [None, None, None]}))
    expect('leak', 'set work before grading', not any(t in pre for t in texts), 'a note was sent before the pupil answered')
    expect('leak', 'teacher', not any(t in json.dumps(teacher) for t in texts) and not any(t in json.dumps(preview) for t in texts),
           'a note is in the teacher or preview payload')
    unanswered, wrong, right = student['problems']
    want = ON.picked_note(p, with_note)
    expect('graded', 'set work', wrong.get('hint_message') == want and want, f'graded wrong pick: {wrong.get("hint_message")!r}')
    expect('graded', 'set work', 'hint_message' not in right and 'hint_message' not in unanswered, 'a right or unanswered question carries a note')
    if without:
        s2 = serialize_student_work({**base, 'answers': [{'user_answer': without, 'correct': False}, None, None]})
        expect('graded', 'set work', not s2['problems'][0].get('hint_message'), 'an option without a note must show nothing extra')
    # lesson quiz API: nothing mid-quiz, the note on the results
    from app import get_db
    from models.lesson_quiz import load_lesson_quiz_session, save_lesson_quiz_session
    with app.test_client() as client:
        r = client.post('/api/v1/lesson-quiz/start', json={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'})
        if r.status_code != 201:
            issue('graded', 'quiz', f'could not start a lesson quiz: {r.status_code} {r.get_json()}')
            return
        sid = r.get_json()['session_id']
        with get_db() as conn:
            data = load_lesson_quiz_session(conn, sid)
            data['problems'][0] = dict(p)
            save_lesson_quiz_session(conn, sid, data)
            data = load_lesson_quiz_session(conn, sid)
        problems = data['problems']
        expect('leak', 'quiz row', ON.KEY in problems[0], 'the lesson quiz row must keep the notes for the results')
        for i, prob in enumerate(problems):
            letter = with_note if i == 0 else (prob.get('correct_answer') or 'A')
            body = client.post(f'/api/v1/lesson-quiz/{sid}/answer', json={'user_answer': letter}).get_json()
            expect('leak', f'quiz answer {i}', ON.KEY not in str(body) and not any(t in str(body) for t in texts), 'a note came back before the results')
            if i + 1 < len(problems):
                q = client.get(f'/api/v1/lesson-quiz/{sid}/question').get_json()
                expect('leak', f'quiz question {i + 1}', ON.KEY not in str(q) and not any(t in str(q) for t in texts), 'a question carried a note')
        res = client.get(f'/api/v1/lesson-quiz/{sid}/results').get_json()
        entries = res.get('problems') or []
        expect('graded', 'quiz results', entries and entries[0].get('hint_message') == want, f'results note {entries[0].get("hint_message") if entries else None!r}')
        expect('leak', 'quiz results', ON.KEY not in json.dumps(res), 'option_notes in the lesson quiz results')
        expect('graded', 'quiz results', all('hint_message' not in e for e in entries[1:] if e.get('was_correct')), 'a right answer carries a note')
    # Quick Test: nothing during the test, the note on the results page for a wrong pick
    from models.quicktest import load_quicktest_session, save_quicktest_session
    with app.test_client() as client:
        r = client.post('/quicktest/start', data={'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas', 'mode': 'mcq',
                                                  'difficulty': 'foundational'}, follow_redirects=True)
        with client.session_transaction() as sess:
            qt_id = sess.get('qt_id')
        if r.status_code != 200 or not qt_id:
            issue('graded', 'quick test', f'could not start a Quick Test: {r.status_code}')
        else:
            during = r.get_data(as_text=True)
            expect('leak', 'quick test page', ON.KEY not in during and not any(t in during for t in texts), 'a note is on the Quick Test page')
            with get_db() as conn:
                qt = load_quicktest_session(conn, qt_id)
                qt['problems'][0] = dict(p)
                qt['answers'] = [{'user_answer': with_note, 'correct': False}] + [{}] * (len(qt['problems']) - 1)
                save_quicktest_session(conn, qt_id, qt)
                saved = load_quicktest_session(conn, qt_id)
            expect('leak', 'quick test row', ON.KEY in saved['problems'][0], 'the Quick Test row must keep the notes for its results')
            page = client.get('/quicktest/results').get_data(as_text=True)
            expect('graded', 'quick test results', page.count(want) == 1, 'the results page must show the note once, for the wrong pick')
            expect('leak', 'quick test results', ON.KEY not in page, 'option_notes in the Quick Test results page')
            qt['answers'][0] = {'user_answer': key, 'correct': True}
            with get_db() as conn:
                save_quicktest_session(conn, qt_id, qt)
            page = client.get('/quicktest/results').get_data(as_text=True)
            expect('graded', 'quick test results', want not in page, 'a right pick must show no note')
    # exports must never carry a note: the data export and the saved copies read stored rows, which hold none
    expect('leak', 'exports', 'problems_json' not in read('models/data_export.py'), 'the data export must not carry stored questions')
    where = {rel: read(rel).count('keep_notes=True') for rel in ('app.py', 'models/class_assignments.py', 'models/quicktest.py')}
    expect('leak', 'keep_notes', where == {'app.py': 1, 'models/class_assignments.py': 2, 'models/quicktest.py': 1},
           f'keep_notes=True belongs to set work, the lesson quiz and the Quick Test rows only: {where}')


# ─────────────────────────────────────────────────────────────────────────────
# client
# ─────────────────────────────────────────────────────────────────────────────

def check_client():
    js = read('static/js/site.js')
    n = len(js.encode('utf-8'))
    cap = SITE_JS_BASE_BYTES + SITE_JS_PHASE4_MAX_ADD + SITE_JS_CARD_MAX_ADD + SITE_JS_NOTE_MAX_ADD + SITE_JS_COACH_MAX_ADD + SITE_JS_RECOVERY_MAX_ADD
    expect('client', 'site.js', n <= cap, f'site.js is {n} B, cap {cap} (Phase 4 budget +{SITE_JS_PHASE4_MAX_ADD})')
    css = (ROOT / 'static/css/practice.css').stat().st_size
    expect('client', 'practice.css', css <= PRACTICE_CSS_BYTES + CSS_PHASE4_MAX_ADD + 1_500 + 900, f'practice.css is {css} B')   # +900 on 2026-11-07 (note toggle)
    base = read('templates/base.html')
    expect('client', 'pins', "js/site.js') }}?v=41" in base, 'site.js must be ?v=41 (2026-11-10: E11 Phase 2 Recovery badges)')
    expect('client', 'pins', "CACHE_VERSION = 'pb-v131'" in read('static/js/sw.js'), 'sw.js must be pb-v131')   # 2026-11-13: E10 Phase 9 review (was pb-v130); 2026-11-13: the sounds' gains and the Settings sample (S3, was pb-v129); 2026-11-13: the celebration sounds (was pb-v128); 2026-11-12: the 10/10 redrawn (was pb-v127); 2026-11-11: E11 Phase 4 bump (was pb-v126, Phase 3); 2026-11-11: E11 Phase 3 bump (was pb-v125, Phase 2); 2026-11-10: E11 Phase 2 bump (was pb-v124, Phase 1); 2026-11-10: E11 Phase 1 bump (was pb-v123, Phase 0); 2026-11-10: E11 Phase 0 bump (was pb-v122, lesson-quiz spotlight); 2026-11-08: E10 phase 8 bump (was pb-v119, review fixes); 2026-11-08: E10 phase 6b bump (was pb-v116, phase 6); 2026-11-08: E10 phase 6 bump (was pb-v115, phase 5); 2026-11-08: E10 phase 5 bump (was pb-v114, phase 4; pb-v113 phase 3); 2026-11-08: E10 review fixes bump (was pb-v118)
    fn = js[js.index('function fetchOptionNote'):js.index('function showMcqRetry')]
    expect('client', 'script', "'/api/v1/problems/option-note'" in fn and 'data-note-qid' in fn, 'the script must call the endpoint with the question tag')
    expect('client', 'script', 'focus(' not in fn and 'animate' not in fn and 'style' not in fn, 'no focus, motion or inline style')
    expect('client', 'script', "classList.contains('is-wrong')" in fn, 'a late answer must not land on a reset question')
    expect('client', 'script', ".mcq-hint-slot .hint-card" in fn and 'hint-card-text' in fn and 'slot.hidden = false' in fn,
           '2026-11-04: the note goes in the hint card, inside the polite .mcq-hint-slot live region (not appended to the red line)')
    persist = js[js.index('function persistMcqAnswer'):js.index('function mcqOptionLetter')]
    expect('client', 'script', '!isReflectionEligible()' in persist.split('fetch(')[0],
           'guests skip the login-only mcq-answer call (it answered 401 on every guest pick)')
    expect('client', 'script', 'fetchOptionNote(block, btn, letter, feedback);' in js and js.count('fetchOptionNote(') == 2,
           'the note is fetched after a wrong pick only')
    wrong_branch = js[js.index("btn.classList.add('is-wrong')"):js.index('showMcqRetry(block);')]
    expect('client', 'script', 'fetchOptionNote(' in wrong_branch, 'the fetch must be in the wrong branch')
    index = read('templates/index.html')
    expect('client', 'template', "hint_ladder and option_note_qid(problem)" in index and 'data-note-qid' in index, 'the options block carries the question tag')
    expect('client', 'template', 'option_note' not in index.replace('option_note_qid', ''), 'the template must not read the notes')
    expect('client', 'script', '\u2014' not in fn, 'no em dash in the note script')
    return n


def check_fillers_unnoted():
    """A note never attaches to a filler: every option a generator tops up with (``option_fillers``) is recorded as the
    question is built, and none may be in the notes the question registered (docs/GCSE_MATHS_VERIFICATION.md)."""
    from generators.gcse import maths_num_stats_prob_rat as N
    made = []
    real = N._option_fillers

    def spy(correct, taken, count):
        got = real(correct, taken, count)
        made.extend(got)
        return got

    N._option_fillers = spy
    used = 0
    try:
        for slug, label, fn in scope():
            if slug not in ('number', 'ratio_proportion'):
                continue
            for seed in range(25):
                random.seed(900 + seed)
                made.clear()
                with ON.capture() as sink:
                    quiet(fn)
                used += len(made)
                for text in made:
                    expect('fillers', f'{label} seed {seed}', text not in sink, f'filler {text!r} carries the note {sink.get(text)}')
    finally:
        N._option_fillers = real
    expect('fillers', 'spy', used > 50, f'only {used} fillers were seen: the check is not testing anything')
    # the map scale slip keeps its note on the option it describes (30 km beside 0.3 km for 3 cm at 1:10000)
    seen_note = False
    for seed in range(25):
        random.seed(seed)
        with ON.capture() as sink:
            out = quiet(N.ratio_proportion_mcq, 4)
        texts = {o[3:] for o in out[4]}
        seen_note = seen_note or any(v == 'mcq.map_km_factor' and k in texts for k, v in sink.items())
        expect('fillers', f'map scale seed {seed}', 'in km' in out[0] and not any(t.endswith(' m') for t in texts),
               f'the map scale question must name km and offer no metres: {out[0]!r} {sorted(texts)}')
    expect('fillers', 'map scale', seen_note, 'the map factor note never attached to its option')


# ─────────────────────────────────────────────────────────────────────────────

def print_pins():
    pins = {f'{r[0]}|{r[1]}|{r[3]}': V.bank_row_pin(r, ON.note_text(r[0])) for r in COPY.BANK_WHY}
    print('BANK_PINS = {')
    for k, v in pins.items():
        print(f'    {k!r}: {v!r},')
    print('}')


def main():
    if '--print-pins' in sys.argv:
        print_pins()
        h = hashlib.sha1()
        for slug, label, fn in scope():
            for seed in range(4):
                random.seed(500 + seed)
                q, sol, hint, marks, opts, letter = quiet(fn)
                h.update(json.dumps([label, q, sol, hint, marks, opts, letter], sort_keys=True, ensure_ascii=False).encode())
        print('DRIFT_PIN =', repr(h.hexdigest()[:16]))
        return
    from app import app
    check_catalogue()
    ok, total, by_wave = check_verified()
    check_review()
    check_bank()
    n_drift = check_drift()
    check_fillers_unnoted()
    check_leaks_and_endpoint(app)
    check_stored_and_graded(app)
    js = check_client()
    elapsed = time.time() - START
    print(f'GCSE maths MCQ notes (Phase 4): {ok} of {total} procedural distractors in waves A and B have a verified note '
          f'({ok / max(total, 1):.0%}, floor {COVERAGE_FLOOR:.0%}; {SEEDS} seeds per generator), {n_drift} drift samples, '
          f'{len(COPY.BANK_WHY)} bank rows, {elapsed:.1f}s (budget {BUDGET_SECONDS:g}s)')
    print('  by topic: ' + ', '.join(f'{k} {v[0]}/{v[1]}' for k, v in by_wave.items()))
    print(f'  site.js {js} B (+{js - SITE_JS_BASE_BYTES}, cap +{SITE_JS_PHASE4_MAX_ADD})')
    if ISSUES:
        for check, lines in ISSUES.items():
            print(f'FAIL {check}: {len(lines)}')
            for line in lines[:12]:
                print(f'  {line}')
            if len(lines) > 12:
                print(f'  ... and {len(lines) - 12} more')
        sys.exit(1)
    if elapsed > BUDGET_SECONDS * 2:
        print(f'FAIL budget: {elapsed:.1f}s')
        sys.exit(1)
    print('GCSE maths MCQ notes smoke (Phase 4) passed.')


if __name__ == '__main__':
    main()
