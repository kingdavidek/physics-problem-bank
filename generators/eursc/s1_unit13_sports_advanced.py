"""S1 Unit 1.3 Sports advanced Practice pools (MS / SMS). Isolated from lesson banks.

Five topics: movement (SMS only — MS in s1_sports.py), forces_sport, breathing,
sport_health. Three named blueprints per supported topic × tier × mode;
foundational MS stays empty for breathing and sport_health (matrix —).
"""
import random

from generators.eursc.science_shared import (
    antagonistic_pair,
    circulation_boxes,
    distance_time_graph,
    force_pair,
)
from generators.shared.utils import graded_answer_number_fields, make_graded_problem

_LEVEL = "eursc"
_SUBJECT = "science"


def _u13_variant(topic, mode_tag, difficulty, suffix):
    def decorator(builder):
        def _fn():
            return make_graded_problem(
                builder(), difficulty, _LEVEL, _SUBJECT, topic
            )

        _fn.__name__ = f"{topic}_{difficulty}_{mode_tag}_{suffix}"
        _fn._kind = "number_fields"
        _fn._randomizable = True
        return _fn

    return decorator


def _u13_mcq_field(correct, distractors):
    pool = [correct, *distractors]
    random.shuffle(pool)
    letters = "ABCD"[: len(pool)]
    return pool, letters[pool.index(correct)]


def _u13_order_field(steps, distractors):
    step_ids = tuple(f"s{i + 1}" for i in range(len(steps)))
    bank = [{"id": sid, "text": text} for sid, text in zip(step_ids, steps)]
    for i, text in enumerate(distractors):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"1|{'|'.join(step_ids)}", bank


def _u13_pick_field(correct_texts, distractor_texts, pick_count):
    correct_ids = tuple(f"c{i + 1}" for i in range(len(correct_texts)))
    bank = [{"id": cid, "text": text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({"id": f"d{i + 1}", "text": text})
    random.shuffle(bank)
    return f"pick|{pick_count}|{'|'.join(correct_ids)}", bank, pick_count


# ---------------------------------------------------------------------------
# movement — situational_multi_step (SMS only; MS packs stay in s1_sports.py)
# ---------------------------------------------------------------------------

_MV_SMS_F_SESSION_PACKS = (
    {"who": "Alex", "what": "warm-up lap", "d": 10, "t": 2, "t2": 3},
    {"who": "Sam", "what": "timed drill", "d": 12, "t": 3, "t2": 4},
    {"who": "Jordan", "what": "relay leg", "d": 20, "t": 4, "t2": 5},
)


@_u13_variant("movement", "sms", "foundational", "session_speed_extrapolate")
def _movement_foundational_sms_session_speed_extrapolate():
    pack = random.choice(_MV_SMS_F_SESSION_PACKS)
    speed = pack["d"] / pack["t"]
    distance = speed * pack["t2"]
    question = (
        f"<p>In a fictional school athletics session, {pack['who']} runs "
        f"{pack['what']}: {pack['d']} m in {pack['t']} s.</p>"
        "<p>(i) Find the average speed in m/s.</p>"
        f"<p>(ii) If {pack['who']} kept that average speed for another "
        f"{pack['t2']} s, how many metres would that cover?</p>"
    )
    solution = (
        f"(i) v = d/t = {pack['d']}/{pack['t']} = "
        f"<strong>{speed:g}</strong> m/s<br>"
        f"(ii) distance = v × t = {speed:g} × {pack['t2']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Work out the speed in (i), then use the "
        "same value in (ii)."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (speed, distance),
            ("Average speed (m/s)", "Distance (m)"),
            format_hint="Use v = d/t in (i), then multiply by the extra time.",
        ),
    )


_MV_SMS_F_MINUTES_PACKS = (
    {"d": 60, "min": 1},
    {"d": 120, "min": 2},
    {"d": 180, "min": 3},
)


@_u13_variant("movement", "sms", "foundational", "minutes_seconds_convert")
def _movement_foundational_sms_minutes_seconds_convert():
    pack = random.choice(_MV_SMS_F_MINUTES_PACKS)
    seconds = pack["min"] * 60
    speed = pack["d"] / seconds
    question = (
        f"<p>A fictional runner covers {pack['d']} m in {pack['min']} minute"
        f"{'s' if pack['min'] != 1 else ''}.</p>"
        f"<p>(i) Convert the time to seconds.</p>"
        "<p>(ii) Find the average speed in m/s using metres and seconds.</p>"
    )
    solution = (
        f"(i) {pack['min']} min = {pack['min']} × 60 = "
        f"<strong>{seconds}</strong> s<br>"
        f"(ii) v = d/t = {pack['d']}/{seconds} = <strong>{speed:g}</strong> m/s"
    )
    hint = (
        "<strong>Key idea:</strong> Convert minutes to seconds before using "
        "v = d/t."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (seconds, speed),
            ("Time (s)", "Average speed (m/s)"),
            format_hint="Multiply minutes by 60, then divide distance by time.",
        ),
    )


_MV_SMS_F_RELAY_PACKS = (
    {"d": 40, "t": 8, "t2": 5},
    {"d": 50, "t": 10, "t2": 4},
    {"d": 30, "t": 6, "t2": 6},
)


@_u13_variant("movement", "sms", "foundational", "relay_baton_timing")
def _movement_foundational_sms_relay_baton_timing():
    pack = random.choice(_MV_SMS_F_RELAY_PACKS)
    speed = pack["d"] / pack["t"]
    distance = speed * pack["t2"]
    question = (
        "<p>In a fictional relay practice, the first athlete runs "
        f"{pack['d']} m in {pack['t']} s before passing the baton.</p>"
        "<p>(i) Find the average speed in m/s for that leg.</p>"
        f"<p>(ii) The next runner keeps that speed for {pack['t2']} s. "
        "How many metres do they cover?</p>"
    )
    solution = (
        f"(i) v = {pack['d']}/{pack['t']} = <strong>{speed:g}</strong> m/s<br>"
        f"(ii) distance = {speed:g} × {pack['t2']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Find the first-leg speed, then multiply "
        "by the second runner's time."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (speed, distance),
            ("First-leg speed (m/s)", "Second-leg distance (m)"),
            format_hint="Divide distance by time for leg one, then multiply.",
        ),
    )


_MV_SMS_I_GRAPH_PACKS = (
    {"d": 12, "t": 3, "t_total": 5},
    {"d": 15, "t": 5, "t_total": 8},
    {"d": 20, "t": 4, "t_total": 6},
)


@_u13_variant("movement", "sms", "intermediate", "graph_read_slope")
def _movement_intermediate_sms_graph_read_slope():
    pack = random.choice(_MV_SMS_I_GRAPH_PACKS)
    speed = pack["d"] / pack["t"]
    distance = speed * pack["t_total"]
    graph = str(distance_time_graph(title="Fictional distance–time graph"))
    question = (
        graph
        + "<p>A fictional distance–time graph shows a straight slope from "
        f"0 m at 0 s to {pack['d']} m at {pack['t']} s.</p>"
        "<p>(i) Find the average speed in m/s.</p>"
        f"<p>(ii) If that speed stayed constant from the start, how far would "
        f"the athlete be at {pack['t_total']} s?</p>"
    )
    solution = (
        f"(i) v = {pack['d']}/{pack['t']} = <strong>{speed:g}</strong> m/s<br>"
        f"(ii) distance = {speed:g} × {pack['t_total']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Read distance and time from the slope, "
        "then reuse the speed from (i)."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (speed, distance),
            ("Average speed (m/s)", "Distance (m)"),
            format_hint="Divide the graph readings, then multiply by the later time.",
        ),
    )


_MV_SMS_I_MINUTE_PACKS = (
    {"d": 240, "min": 4, "t2": 10},
    {"d": 300, "min": 5, "t2": 8},
    {"d": 360, "min": 6, "t2": 5},
)


@_u13_variant("movement", "sms", "intermediate", "minute_run_chain")
def _movement_intermediate_sms_minute_run_chain():
    pack = random.choice(_MV_SMS_I_MINUTE_PACKS)
    seconds = pack["min"] * 60
    speed = pack["d"] / seconds
    distance = speed * pack["t2"]
    question = (
        f"<p>A fictional runner covers {pack['d']} m in {pack['min']} minutes.</p>"
        f"<p>(i) Convert the time to seconds.</p>"
        "<p>(ii) Find the average speed in m/s.</p>"
        f"<p>(iii) At that speed, how many metres would be covered in "
        f"{pack['t2']} s?</p>"
    )
    solution = (
        f"(i) {pack['min']} × 60 = <strong>{seconds}</strong> s<br>"
        f"(ii) v = {pack['d']}/{seconds} = <strong>{speed:g}</strong> m/s<br>"
        f"(iii) distance = {speed:g} × {pack['t2']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Convert to seconds, find v, then multiply "
        "by the shorter time in (iii)."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (seconds, speed, distance),
            ("Time (s)", "Average speed (m/s)", "Distance (m)"),
            format_hint="Convert, divide, then use the speed from (ii).",
        ),
    )


_MV_SMS_I_TWO_LEG_PACKS = (
    {"d1": 25, "t1": 5, "t2": 3},
    {"d1": 30, "t1": 6, "t2": 4},
    {"d1": 40, "t1": 8, "t2": 5},
)


@_u13_variant("movement", "sms", "intermediate", "two_leg_pass")
def _movement_intermediate_sms_two_leg_pass():
    pack = random.choice(_MV_SMS_I_TWO_LEG_PACKS)
    speed = pack["d1"] / pack["t1"]
    distance = speed * pack["t2"]
    question = (
        "<p>In a fictional relay practice, one athlete runs "
        f"{pack['d1']} m in {pack['t1']} s.</p>"
        "<p>(i) Find the average speed in m/s.</p>"
        f"<p>(ii) A teammate keeps that speed for {pack['t2']} s. "
        "How many metres do they cover?</p>"
    )
    solution = (
        f"(i) v = {pack['d1']}/{pack['t1']} = <strong>{speed:g}</strong> m/s<br>"
        f"(ii) distance = {speed:g} × {pack['t2']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> The teammate uses the speed you found "
        "in (i)."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (speed, distance),
            ("Average speed (m/s)", "Distance (m)"),
            format_hint="Find v from the first leg, then multiply by the second time.",
        ),
    )


_MV_SMS_D_KM_PACKS = (
    {"km": 0.6, "min": 3, "t2": 6},
    {"km": 0.9, "min": 3, "t2": 10},
    {"km": 1.2, "min": 4, "t2": 5},
)


@_u13_variant("movement", "sms", "difficult", "km_lap_units")
def _movement_difficult_sms_km_lap_units():
    pack = random.choice(_MV_SMS_D_KM_PACKS)
    metres = int(pack["km"] * 1000)
    seconds = pack["min"] * 60
    speed = metres / seconds
    distance = speed * pack["t2"]
    question = (
        f"<p>A fictional swimmer completes {pack['km']} km in {pack['min']} "
        f"minutes during training.</p>"
        "<p>(i) Write the distance in metres.</p>"
        "<p>(ii) Write the time in seconds.</p>"
        "<p>(iii) Find the average speed in m/s.</p>"
        f"<p>(iv) At that speed, how many metres would be covered in "
        f"{pack['t2']} s?</p>"
    )
    solution = (
        f"(i) {pack['km']} km = <strong>{metres}</strong> m<br>"
        f"(ii) {pack['min']} min = <strong>{seconds}</strong> s<br>"
        f"(iii) v = {metres}/{seconds} = <strong>{speed:g}</strong> m/s<br>"
        f"(iv) distance = {speed:g} × {pack['t2']} = "
        f"<strong>{distance:g}</strong> m"
    )
    hint = (
        "<strong>Key idea:</strong> Convert km and minutes to m and s before "
        "using v = d/t; reuse that speed in (iv)."
    )
    return (
        question,
        solution,
        hint,
        4,
        graded_answer_number_fields(
            (metres, seconds, speed, distance),
            (
                "Distance (m)",
                "Time (s)",
                "Average speed (m/s)",
                "Distance (m)",
            ),
            format_hint="Convert units, divide, then multiply by the extra time.",
        ),
    )


_MV_SMS_D_JOURNEY_PACKS = (
    {"d1": 80, "t1": 10, "d2": 60, "t2": 20},
    {"d1": 50, "t1": 5, "d2": 70, "t2": 14},
    {"d1": 90, "t1": 15, "d2": 60, "t2": 12},
)


@_u13_variant("movement", "sms", "difficult", "journey_average_total")
def _movement_difficult_sms_journey_average_total():
    pack = random.choice(_MV_SMS_D_JOURNEY_PACKS)
    speed1 = pack["d1"] / pack["t1"]
    speed2 = pack["d2"] / pack["t2"]
    total_d = pack["d1"] + pack["d2"]
    total_t = pack["t1"] + pack["t2"]
    avg_speed = total_d / total_t
    question = (
        "<p>A fictional athlete runs two sections of a training route.</p>"
        f"<p>Section A: {pack['d1']} m in {pack['t1']} s.</p>"
        f"<p>Section B: {pack['d2']} m in {pack['t2']} s.</p>"
        "<p>(i) Find the average speed for section A in m/s.</p>"
        "<p>(ii) Find the average speed for section B in m/s.</p>"
        "<p>(iii) Find the average speed for the whole journey using total "
        "distance and total time.</p>"
    )
    solution = (
        f"(i) v = {pack['d1']}/{pack['t1']} = <strong>{speed1:g}</strong> m/s<br>"
        f"(ii) v = {pack['d2']}/{pack['t2']} = <strong>{speed2:g}</strong> m/s<br>"
        f"(iii) total d = {total_d} m, total t = {total_t} s → "
        f"v = {total_d}/{total_t} = <strong>{avg_speed:g}</strong> m/s"
    )
    hint = (
        "<strong>Key idea:</strong> Whole-journey average speed uses all the "
        "distance and all the time, not just the faster section."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (speed1, speed2, avg_speed),
            (
                "Section A speed (m/s)",
                "Section B speed (m/s)",
                "Whole-journey average speed (m/s)",
            ),
            format_hint="Divide each section, then use total distance ÷ total time.",
        ),
    )


_MV_SMS_D_REST_PACKS = (
    {"d1": 20, "t1": 4, "rest": 2, "d2": 15, "t2": 3},
    {"d1": 16, "t1": 4, "rest": 3, "d2": 12, "t2": 3},
    {"d1": 24, "t1": 6, "rest": 2, "d2": 10, "t2": 2},
)


@_u13_variant("movement", "sms", "difficult", "graph_rest_sections")
def _movement_difficult_sms_graph_rest_sections():
    pack = random.choice(_MV_SMS_D_REST_PACKS)
    speed1 = pack["d1"] / pack["t1"]
    speed2 = pack["d2"] / pack["t2"]
    total_d = pack["d1"] + pack["d2"]
    total_t = pack["t1"] + pack["rest"] + pack["t2"]
    avg_speed = total_d / total_t
    graph = str(distance_time_graph(title="Fictional d–t with rest section"))
    question = (
        graph
        + "<p>A distance–time graph for a fictional runner shows:</p>"
        f"<ul><li>a slope from 0 m to {pack['d1']} m in {pack['t1']} s;</li>"
        f"<li>a flat section at {pack['d1']} m for {pack['rest']} s;</li>"
        f"<li>then a slope to {pack['d1'] + pack['d2']} m in a further "
        f"{pack['t2']} s.</li></ul>"
        "<p>(i) Find the average speed during the first moving section.</p>"
        "<p>(ii) Find the average speed during the second moving section.</p>"
        "<p>(iii) Find the average speed for the whole journey (include the "
        "rest time in the total time).</p>"
    )
    solution = (
        f"(i) v = {pack['d1']}/{pack['t1']} = <strong>{speed1:g}</strong> m/s<br>"
        f"(ii) v = {pack['d2']}/{pack['t2']} = <strong>{speed2:g}</strong> m/s<br>"
        f"(iii) total d = {total_d} m, total t = {total_t} s → "
        f"v = {total_d}/{total_t} = <strong>{avg_speed:g}</strong> m/s"
    )
    hint = (
        "<strong>Key idea:</strong> Rest time still counts in the total time "
        "for a whole-journey average, even though speed was zero then."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (speed1, speed2, avg_speed),
            (
                "First section speed (m/s)",
                "Second section speed (m/s)",
                "Whole-journey average speed (m/s)",
            ),
            format_hint="Use each slope separately, then total distance ÷ total time.",
        ),
    )


# ---------------------------------------------------------------------------
# forces_sport — multi_step (MS)
# ---------------------------------------------------------------------------

_FS_MS_F_NET_PACKS = (
    {"f1": 2, "f2": 2},
    {"f1": 3, "f2": 3},
    {"f1": 4, "f2": 4},
)


@_u13_variant("forces_sport", "ms", "foundational", "net_zero_then_pair")
def _forces_sport_foundational_ms_net_zero_then_pair():
    pack = random.choice(_FS_MS_F_NET_PACKS)
    net = 0
    correct = "A and B push each other with equal and opposite forces"
    distractors = (
        "only A can push; B has no force on A",
        "forces disappear when objects touch",
        "mass is measured in newtons",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    diagram = str(force_pair(title="Fictional interaction pair"))
    question = (
        diagram
        + f"<p>In a fictional tug-of-war drill, two {pack['f1']} N forces pull "
        "a ring equally opposite.</p>"
        "<p>(i) What is the net force on the ring in newtons?</p>"
        "<p>(ii) Using that result from (i), the sketch shows that</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Equal opposite forces cancel; interaction "
        "pairs act on both objects."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Interaction pair idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract equal forces, then choose the pair idea.",
        ),
    )


@_u13_variant("forces_sport", "ms", "foundational", "friction_grip_then_net")
def _forces_sport_foundational_ms_friction_grip_then_net():
    pack = random.choice(((3, 1), (4, 2), (5, 2)))
    forward, backward = pack
    net = forward - backward
    correct = "friction between shoe and track helps the athlete push forward"
    distractors = (
        "friction only exists in outer space",
        "friction is the same as mass in kilograms",
        "shoes cannot exert forces on the track",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>On a fictional athletics track, a runner's foot pushes with "
        f"{forward} N forward while friction resists with {backward} N.</p>"
        "<p>(i) Find the net forward force in newtons.</p>"
        "<p>(ii) Using that net force from (i), friction between shoe and "
        "track</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract opposing forces, then recall "
        "grip friction helps forward motion."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Friction role"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract the backward force, then choose friction's role.",
        ),
    )


@_u13_variant("forces_sport", "ms", "foundational", "force_order_then_pick")
def _forces_sport_foundational_ms_force_order_then_pick():
    order_raw, order_bank = _u13_order_field(
        (
            "A force can change motion or shape",
            "If A pushes B, B pushes A back",
        ),
        ("A force needs no object to act on",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Push or pull on an object", "Measured in newtons"),
        (
            "A force with no unit in science",
            "A rumour that mass is a force",
        ),
        2,
    )
    question = (
        "<p>A fictional sports-science poster lists force ideas.</p>"
        "<p>(i) Order force effect, then interaction pair.</p>"
        "<p>(ii) Using that order from (i), select the two scientific force "
        "facts.</p>"
    )
    solution = (
        "(i) <strong>effect → interaction pair</strong><br>"
        "(ii) Push/pull on an object and newtons are scientific facts."
    )
    hint = (
        "<strong>Key idea:</strong> Order effects before pairs, then pick "
        "object contact and the SI unit."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Force idea order", "Scientific force facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the ideas, then select two scientific facts.",
        ),
    )


_FS_MS_I_BALANCE_PACKS = (
    {"up": 500, "down": 500},
    {"up": 600, "down": 600},
    {"up": 450, "down": 450},
)


@_u13_variant("forces_sport", "ms", "intermediate", "balance_net_then_cog")
def _forces_sport_intermediate_ms_balance_net_then_cog():
    pack = random.choice(_FS_MS_I_BALANCE_PACKS)
    net = 0
    correct = "less stable because the line of centre of gravity may fall outside the base"
    distractors = (
        "more stable because mass doubles automatically",
        "friction disappears on a narrow base",
        "weight is not a force in newtons",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional gymnast on a beam has an upward support force of "
        f"{pack['up']} N and weight of {pack['down']} N, with no acceleration.</p>"
        "<p>(i) What is the net force in newtons?</p>"
        "<p>(ii) Using equilibrium from (i), a tall narrow pose tends to be</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Balanced forces mean zero net force; "
        "stability links centre of gravity and base width."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Stability idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract weight from support, then choose stability.",
        ),
    )


@_u13_variant("forces_sport", "ms", "intermediate", "friction_slow_then_weight")
def _forces_sport_intermediate_ms_friction_slow_then_weight():
    pack = random.choice(((6, 2), (8, 3), (10, 4)))
    forward, friction = pack
    net = forward - friction
    correct = "the gravitational force on a mass, measured in newtons"
    distractors = (
        "mass in kilograms only",
        "a type of friction with no unit",
        "speed in metres per second",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional puck on ice is pushed with "
        f"{forward} N forward while friction acts with {friction} N backward.</p>"
        "<p>(i) Find the net forward force in newtons.</p>"
        "<p>(ii) Using that contact-force idea from (i), weight on Earth is</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract friction from the push; weight "
        "is a gravitational force in newtons."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Weight definition"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract friction, then define weight.",
        ),
    )


@_u13_variant("forces_sport", "ms", "intermediate", "interaction_order_then_pick")
def _forces_sport_intermediate_ms_interaction_order_then_pick():
    diagram = str(force_pair(title="Fictional matching pushes"))
    order_raw, order_bank = _u13_order_field(
        (
            "Helpful grip between shoe and track",
            "Friction slowing a sliding object",
        ),
        ("Friction exists only in a vacuum",),
    )
    correct = "a matching interaction pair on the two boxes"
    distractors = (
        "unrelated units of time",
        "masses listed in kilograms only",
        "a rumour with no objects",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional forces poster shows friction jobs and an interaction "
        "diagram.</p>"
        "<p>(i) Order helpful grip, then slowing friction.</p>"
        "<p>(ii) Using that friction order from (i), the two arrows on the "
        "boxes are</p>"
    )
    solution = (
        "(i) <strong>grip → slowing</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order friction jobs, then read the "
        "equal-and-opposite pair on the sketch."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Friction job order", "Arrow meaning"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order friction jobs, then choose the pair meaning.",
        ),
    )


@_u13_variant("forces_sport", "ms", "difficult", "resultant_sum_then_eq")
def _forces_sport_difficult_ms_resultant_sum_then_eq():
    pack = random.choice(((4, 1), (5, 2), (6, 2)))
    right, left = pack
    resultant = right - left
    correct = "the resultant force is zero (equilibrium)"
    distractors = (
        "gravity does not exist on Earth",
        "mass becomes zero newtons",
        "friction is forbidden in sport",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional rugby player stands still with forces "
        f"{right} N right and {left} N left along a line.</p>"
        "<p>(i) Find the size of the resultant force in newtons.</p>"
        f"<p>(ii) If a third force balances the {right} N right force, the "
        "player is in equilibrium because</p>"
    )
    solution = (
        f"(i) <strong>{resultant}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract along the line; equilibrium "
        "means net force is zero."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (resultant, letter),
            ("Resultant force (N)", "Equilibrium meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract opposing forces, then choose equilibrium.",
        ),
    )


@_u13_variant("forces_sport", "ms", "difficult", "blocks_push_then_net")
def _forces_sport_difficult_ms_blocks_push_then_net():
    pack = random.choice(((3, 1), (5, 2), (7, 3)))
    push, drag = pack
    net = push - drag
    correct = "the blocks push the sprinter forwards (interaction pair)"
    distractors = (
        "the blocks do nothing back",
        "the sprinter's mass disappears",
        "time stops at the start line",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sprinter pushes starting blocks with "
        f"{push} N backward while air drag is {drag} N forward on the body "
        "(against motion).</p>"
        "<p>(i) Find the net forward force on the sprinter in newtons "
        "(treat drag as opposing forward motion).</p>"
        "<p>(ii) Using that push from (i), when the sprinter pushes the "
        "blocks backward, the blocks</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Net forward = push minus drag; blocks "
        "push back on the sprinter."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net forward force (N)", "Block reaction"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract drag from push, then choose the block reaction.",
        ),
    )


@_u13_variant("forces_sport", "ms", "difficult", "pair_diagram_then_pick")
def _forces_sport_difficult_ms_pair_diagram_then_pick():
    diagram = str(force_pair(title="Fictional equal and opposite"))
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        (
            "Air resistance usually opposes motion through air",
            "Friction can slow a sliding puck on ice",
        ),
        (
            "Air resistance always helps the cyclist",
            "Friction exists only in outer space",
        ),
        2,
    )
    pair_count = 2
    question = (
        diagram
        + "<p>A fictional forces revision sheet shows an interaction pair "
        "and sport friction facts.</p>"
        "<p>(i) How many objects are shown pushing in the diagram?</p>"
        "<p>(ii) Using that count from (i), select the two true friction or "
        "drag facts.</p>"
    )
    solution = (
        f"(i) <strong>{pair_count}</strong><br>"
        "(ii) Drag opposes motion; friction slows sliding on ice."
    )
    hint = (
        "<strong>Key idea:</strong> Count the interacting objects, then pick "
        "true drag and friction statements."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pair_count, pick_raw),
            ("Objects in diagram", "True force facts"),
            field_types=("number", "pick"),
            field_options=(None, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Count objects, then select two true statements.",
        ),
    )


# ---------------------------------------------------------------------------
# forces_sport — situational_multi_step (SMS)
# ---------------------------------------------------------------------------

@_u13_variant("forces_sport", "sms", "foundational", "shoe_grip_then_cancel")
def _forces_sport_foundational_sms_shoe_grip_then_cancel():
    pack = random.choice(((2, 2), (3, 3), (4, 4)))
    f1, f2 = pack
    net = 0
    correct = "each object pushes the other (interaction pair)"
    distractors = (
        "only the shoe pushes",
        "friction is mass in kilograms",
        "forces need no objects",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>At a fictional sports day, a shoe pushes the track with "
        f"{f1} N while the track pushes back with {f2} N on the shoe.</p>"
        "<p>(i) What is the net force on the shoe from these two equal "
        "opposite pushes, in newtons?</p>"
        "<p>(ii) Using that result from (i), the track and shoe</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Equal opposite contact forces cancel; "
        "both objects are in the interaction."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Interaction idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Cancel equal forces, then choose the pair idea.",
        ),
    )


@_u13_variant("forces_sport", "sms", "foundational", "push_pair_then_unit")
def _forces_sport_foundational_sms_push_pair_then_unit():
    pack = random.choice(((1, 1), (2, 2), (3, 3)))
    push, back = pack
    net = push - back
    correct = "the newton (N)"
    distractors = ("the metre (m)", "the second (s)", "the kilogram only")
    options, letter = _u13_mcq_field(correct, distractors)
    diagram = str(force_pair())
    question = (
        diagram
        + "<p>A fictional ball and foot each push with "
        f"{push} N while an equal {back} N push acts the other way on the "
        "ball along the same line.</p>"
        "<p>(i) Find the net force on the ball in newtons.</p>"
        "<p>(ii) Using that force size from (i), the SI unit of force is</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract equal line forces; force is "
        "measured in newtons."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "SI unit of force"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract opposing forces, then name the SI unit.",
        ),
    )


@_u13_variant("forces_sport", "sms", "foundational", "friction_order_then_pick")
def _forces_sport_foundational_sms_friction_order_then_pick():
    order_raw, order_bank = _u13_order_field(
        ("Grip between shoe and track", "Slowing a sliding object"),
        ("Friction only in a vacuum",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("A push can change motion", "Forces come in interaction pairs"),
        ("A force with no object", "Mass measured in newtons as force"),
        2,
    )
    question = (
        "<p>A fictional coach's forces handout lists friction jobs and "
        "general force facts.</p>"
        "<p>(i) Order helpful grip, then slowing friction.</p>"
        "<p>(ii) Using that friction order from (i), select two scientific "
        "force facts.</p>"
    )
    solution = (
        "(i) <strong>grip → slowing</strong><br>"
        "(ii) Push changes motion; interaction pairs are scientific."
    )
    hint = (
        "<strong>Key idea:</strong> Order friction roles, then pick motion "
        "change and interaction pairs."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Friction order", "Force facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order friction jobs, then select two force facts.",
        ),
    )


@_u13_variant("forces_sport", "sms", "intermediate", "gymnast_eq_then_cog")
def _forces_sport_intermediate_sms_gymnast_eq_then_cog():
    pack = random.choice(((400, 400), (550, 550), (480, 480)))
    support, weight = pack
    net = 0
    correct = "the centre of gravity must stay over the base for stability"
    distractors = (
        "mass becomes infinite on a beam",
        "friction removes the need for balance",
        "weight is not measured in newtons",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional gymnast on a beam has support force "
        f"{support} N upward and weight {weight} N downward.</p>"
        "<p>(i) What is the net force in newtons?</p>"
        "<p>(ii) Using equilibrium from (i), staying balanced on a narrow "
        "beam means</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Balanced forces give zero net; stability "
        "needs CoG over the base."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Balance on beam"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Cancel equal forces, then choose the stability idea.",
        ),
    )


@_u13_variant("forces_sport", "sms", "intermediate", "puck_fric_then_net")
def _forces_sport_intermediate_sms_puck_fric_then_net():
    pack = random.choice(((8, 3), (10, 4), (12, 5)))
    applied, friction = pack
    net = applied - friction
    correct = "weight is the gravitational force on a mass in newtons"
    distractors = (
        "weight is mass in kilograms",
        "friction is speed in m/s",
        "net force is always zero",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional hockey puck is pushed with "
        f"{applied} N while ice friction is {friction} N opposing motion.</p>"
        "<p>(i) Find the net forward force in newtons.</p>"
        "<p>(ii) Using that force arithmetic from (i), on Earth weight is</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract friction; weight is a "
        "gravitational force in newtons."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Weight meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract friction, then define weight.",
        ),
    )


@_u13_variant("forces_sport", "sms", "intermediate", "weight_mass_order_then_mcq")
def _forces_sport_intermediate_sms_weight_mass_order_then_mcq():
    order_raw, order_bank = _u13_order_field(
        ("Mass is kilograms of matter", "Weight is gravitational force in newtons"),
        ("Mass and weight are always identical",),
    )
    correct = "mass stays the same on the Moon but weight is smaller"
    distractors = (
        "mass becomes zero on the Moon",
        "weight is measured in kilograms only",
        "friction replaces weight on the Moon",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional shot-put is weighed on Earth and on the Moon in a "
        "public science demo.</p>"
        "<p>(i) Order mass idea, then weight idea.</p>"
        "<p>(ii) Using that order from (i), the shot-put on the Moon has</p>"
    )
    solution = (
        "(i) <strong>mass → weight</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Distinguish kg of matter from N of "
        "gravitational pull; g is weaker on the Moon."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Mass vs weight order", "Moon comparison"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the definitions, then choose the Moon fact.",
        ),
    )


@_u13_variant("forces_sport", "sms", "difficult", "sprinter_blocks_then_resultant")
def _forces_sport_difficult_sms_sprinter_blocks_then_resultant():
    pack = random.choice(((4, 1), (6, 2), (8, 3)))
    right, left = pack
    resultant = right - left
    correct = "the blocks push the sprinter forwards"
    distractors = (
        "the blocks exert no force",
        "mass is measured in seconds",
        "air drag always helps forward motion",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sprinter has "
        f"{right} N forward from the blocks and {left} N backward from early "
        "air drag along the line of motion.</p>"
        "<p>(i) Find the resultant forward force in newtons.</p>"
        "<p>(ii) Using that push idea from (i), when the sprinter pushes "
        "the blocks backward, the blocks</p>"
    )
    solution = (
        f"(i) <strong>{resultant}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract drag from block push; blocks "
        "react forward on the sprinter."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (resultant, letter),
            ("Resultant force (N)", "Block reaction"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract drag, then choose the interaction reaction.",
        ),
    )


@_u13_variant("forces_sport", "sms", "difficult", "air_drag_then_sum")
def _forces_sport_difficult_sms_air_drag_then_sum():
    pack = random.choice(((5, 2), (7, 3), (9, 4)))
    thrust, drag = pack
    net = thrust - drag
    correct = "equilibrium — resultant force is zero"
    distractors = (
        "infinite acceleration",
        "mass becomes a newton",
        "friction is forbidden in cycling",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional cyclist cruises steadily with leg thrust "
        f"{thrust} N forward and air drag {drag} N backward.</p>"
        "<p>(i) Find the net forward force in newtons.</p>"
        f"<p>(ii) If thrust were increased to {thrust + drag} N with the same "
        f"drag, the cyclist would be in</p>"
    )
    solution = (
        f"(i) <strong>{net}</strong> N<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract drag; equal forward and "
        "backward gives equilibrium."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (net, letter),
            ("Net force (N)", "Balanced motion state"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract drag, then identify equilibrium.",
        ),
    )


@_u13_variant("forces_sport", "sms", "difficult", "equilibrium_chain_then_pick")
def _forces_sport_difficult_sms_equilibrium_chain_then_pick():
    order_raw, order_bank = _u13_order_field(
        (
            "Identify all forces on the object",
            "Add forces along each direction",
            "Check if resultant is zero",
        ),
        ("Ignore gravity in sport",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Wide rugby stance improves stability", "High centre of gravity on narrow base is less stable"),
        ("Mass doubles when you lean", "Friction only exists in space"),
        2,
    )
    question = (
        "<p>A fictional forces revision session covers equilibrium checks and "
        "stability in sport.</p>"
        "<p>(i) Order list forces, add along directions, check zero resultant.</p>"
        "<p>(ii) Using that chain from (i), select two true stability facts.</p>"
    )
    solution = (
        "(i) <strong>list → add → check zero</strong><br>"
        "(ii) Wide stance helps; high CoG on narrow base is less stable."
    )
    hint = (
        "<strong>Key idea:</strong> Follow the equilibrium chain, then pick "
        "centre-of-gravity stability facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Equilibrium chain", "Stability facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the equilibrium steps, then pick two stability facts.",
        ),
    )


# ---------------------------------------------------------------------------
# breathing — multi_step (I, D only; foundational MS = [])
# ---------------------------------------------------------------------------

_BR_MS_I_PULSE_PACKS = (
    {"a": 68, "b": 72, "c": 70},
    {"a": 64, "b": 68, "c": 66},
    {"a": 70, "b": 74, "c": 72},
)


@_u13_variant("breathing", "ms", "intermediate", "team_pulse_mean_then_bpm")
def _breathing_intermediate_ms_team_pulse_mean_then_bpm():
    pack = random.choice(_BR_MS_I_PULSE_PACKS)
    mean = (pack["a"] + pack["b"] + pack["c"]) // 3
    scale = mean  # beats per minute if 10 beats in 10 s → same rate
    correct = "gas exchange at the lungs can happen"
    distractors = (
        "bones pump air like a bicycle tyre",
        "mass becomes weight in seconds",
        "friction removes the need for oxygen",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional athletics club publishes aggregate resting pulse data "
        f"(beats per minute): session readings {pack['a']}, {pack['b']}, "
        f"{pack['c']}.</p>"
        "<p>(i) Find the mean pulse rate in beats per minute.</p>"
        "<p>(ii) Using that average from (i), breathing movements move air so "
        "that</p>"
    )
    solution = (
        f"(i) mean = ({pack['a']}+{pack['b']}+{pack['c']})/3 = "
        f"<strong>{mean}</strong> bpm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average the published group readings; "
        "ventilation supports gas exchange."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (mean, letter),
            ("Mean pulse (bpm)", "Why we breathe"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Average the three readings, then choose gas exchange.",
        ),
    )


@_u13_variant("breathing", "ms", "intermediate", "lung_box_then_gas_mcq")
def _breathing_intermediate_ms_lung_box_then_gas_mcq():
    diagram = str(circulation_boxes(title="Fictional circulation schematic"))
    lung_letter = "B"
    correct = "oxygen is added to blood at the lungs"
    distractors = (
        "nitrogen is the only gas in air",
        "the heart digests food",
        "carbon dioxide is pure helium",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional sport-science poster labels heart A, lungs B, body C.</p>"
        "<p>(i) Which letter marks the lungs on the schematic?</p>"
        "<p>(ii) Using that organ from (i), blood passing there</p>"
    )
    solution = (
        f"(i) <strong>{lung_letter}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Match letter B to lungs; gas exchange "
        "adds oxygen to blood."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (lung_letter, letter),
            ("Lung letter", "Gas exchange role"),
            field_types=("mcq", "mcq"),
            field_options=(("A", "B", "C", "none"), options),
            format_hint="Identify the lungs, then choose what happens there.",
        ),
    )


@_u13_variant("breathing", "ms", "intermediate", "circ_order_then_o2_pick")
def _breathing_intermediate_ms_circ_order_then_o2_pick():
    order_raw, order_bank = _u13_order_field(
        ("Heart pumps blood", "Lungs add oxygen", "Body tissues use oxygen"),
        ("Bones pump air like lungs",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Nitrogen is the main gas in ordinary air", "Oxygen is used in respiration"),
        ("Air contains no gases", "Helium is the majority of sports-hall air"),
        2,
    )
    question = (
        "<p>A fictional circulation lesson links heart, lungs and body tissues.</p>"
        "<p>(i) Order heart pump, lungs oxygenate, body use.</p>"
        "<p>(ii) Using that path from (i), select two true air-gas facts.</p>"
    )
    solution = (
        "(i) <strong>heart → lungs → body</strong><br>"
        "(ii) Nitrogen majority; oxygen used in respiration."
    )
    hint = (
        "<strong>Key idea:</strong> Order the circulation path, then pick "
        "nitrogen and oxygen facts."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Circulation order", "Air gas facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the path, then select two air facts.",
        ),
    )


_BR_MS_D_PULSE_PACKS = (
    {"beats": 12, "seconds": 10},
    {"beats": 15, "seconds": 12},
    {"beats": 18, "seconds": 15},
)


@_u13_variant("breathing", "ms", "difficult", "session_pulse_scale_then_beats")
def _breathing_difficult_ms_session_pulse_scale_then_beats():
    pack = random.choice(_BR_MS_D_PULSE_PACKS)
    factor = 60 // pack["seconds"]
    bpm = pack["beats"] * factor
    correct = "air movement, blood transport and cell chemistry work together"
    distractors = (
        "they are three names for friction",
        "the skeleton stores oxygen as a metal bar",
        "speed is measured in newtons",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional training log lists aggregate pulse data: "
        f"{pack['beats']} beats in {pack['seconds']} s for a demo group "
        "(steady rate).</p>"
        "<p>(i) Scale to beats per minute (60 s).</p>"
        "<p>(ii) Using that rate from (i), breathing, circulation and "
        "respiration link because</p>"
    )
    solution = (
        f"(i) {pack['beats']} × {factor} = <strong>{bpm}</strong> bpm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale the published beat count to 60 s; "
        "the three systems work together in sport."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (bpm, letter),
            ("Pulse (bpm)", "Three-system link"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Scale to 60 s, then choose how the systems link.",
        ),
    )


@_u13_variant("breathing", "ms", "difficult", "buoyancy_depth_then_mcq")
def _breathing_difficult_ms_buoyancy_depth_then_mcq():
    depth_count = 3
    correct = "upthrust (buoyancy) is greater in denser salty water"
    distractors = (
        "mass becomes zero underwater",
        "pulse stops at the pool edge",
        "oxygen is a metal",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional swimming lesson compares fresh and salty water at "
        "three published depth markers (shallow, mid, deep).</p>"
        "<p>(i) How many depth markers are listed?</p>"
        "<p>(ii) Using that pool context from (i), a swimmer floats more "
        "easily in denser salty water because</p>"
    )
    solution = (
        f"(i) <strong>{depth_count}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the markers; denser liquid gives "
        "greater upthrust."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (depth_count, letter),
            ("Depth markers", "Buoyancy reason"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count markers, then choose the buoyancy explanation.",
        ),
    )


@_u13_variant("breathing", "ms", "difficult", "full_circ_then_co2_count")
def _breathing_difficult_ms_full_circ_then_co2_count():
    order_raw, order_bank = _u13_order_field(
        ("Heart", "Lungs", "Body tissues"),
        ("Bones as air pumps",),
    )
    gas_count = 2
    diagram = str(circulation_boxes(title="Fictional full circulation"))
    question = (
        diagram
        + "<p>A fictional revision sheet shows the full circulation path and "
        "gas exchange.</p>"
        "<p>(i) Order heart, lungs, body tissues.</p>"
        "<p>(ii) Using that path from (i), how many main gases change "
        "amount in exhaled air compared with inhaled (oxygen down, CO2 up)?</p>"
    )
    solution = (
        "(i) <strong>heart → lungs → body</strong><br>"
        f"(ii) <strong>{gas_count}</strong> gases change (O2 down, CO2 up)."
    )
    hint = (
        "<strong>Key idea:</strong> Order pump → lungs → tissues; two gases "
        "shift in exhaled air."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, gas_count),
            ("Circulation order", "Gases that change"),
            field_types=("order", "number"),
            field_options=(order_bank, None),
            format_hint="Order the path, then count changing gases.",
        ),
    )


# ---------------------------------------------------------------------------
# breathing — situational_multi_step (SMS)
# ---------------------------------------------------------------------------

_BR_SMS_F_PULSE_PACKS = (
    {"beats": 10, "seconds": 10},
    {"beats": 8, "seconds": 8},
    {"beats": 12, "seconds": 12},
)


@_u13_variant("breathing", "sms", "foundational", "club_pulse_table_then_bpm")
def _breathing_foundational_sms_club_pulse_table_then_bpm():
    pack = random.choice(_BR_SMS_F_PULSE_PACKS)
    bpm = pack["beats"] * (60 // pack["seconds"])
    correct = "the heart pumps blood around the body"
    distractors = (
        "the heart digests food",
        "pulse is measured in newtons",
        "air has no nitrogen",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional sports club table shows aggregate demo pulse: "
        f"{pack['beats']} beats in {pack['seconds']} s (steady).</p>"
        "<p>(i) Scale to beats per minute.</p>"
        "<p>(ii) Using that rate from (i), the heart's job in this unit is to</p>"
    )
    solution = (
        f"(i) <strong>{bpm}</strong> bpm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale published beats to 60 s; the heart "
        "is a blood pump."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (bpm, letter),
            ("Pulse (bpm)", "Heart job"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Scale to 60 s, then choose the heart's role.",
        ),
    )


@_u13_variant("breathing", "sms", "foundational", "heart_letter_then_beats")
def _breathing_foundational_sms_heart_letter_then_beats():
    diagram = str(circulation_boxes())
    heart_letter = "A"
    beats = 60
    question = (
        diagram
        + "<p>A fictional poster labels heart A, lungs B, body C.</p>"
        "<p>(i) Which letter is the heart?</p>"
        "<p>(ii) If a published demo shows 10 beats in 10 s at that steady "
        "rate, how many beats in 60 s?</p>"
    )
    solution = (
        f"(i) <strong>{heart_letter}</strong><br>"
        f"(ii) 10 × 6 = <strong>{beats}</strong> beats"
    )
    hint = (
        "<strong>Key idea:</strong> Letter A is the pump; scale 10 in 10 s "
        "to 60 s."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (heart_letter, beats),
            ("Heart letter", "Beats in 60 s"),
            field_types=("mcq", "number"),
            field_options=(("A", "B", "C", "none"), None),
            format_hint="Pick the heart letter, then scale the beat count.",
        ),
    )


@_u13_variant("breathing", "sms", "foundational", "air_gas_pick_then_count")
def _breathing_foundational_sms_air_gas_pick_then_count():
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Nitrogen is the main gas in air", "Oxygen is used by cells"),
        ("Air is pure carbon dioxide", "Helium is the only gas in a sports hall"),
        2,
    )
    fact_count = 2
    question = (
        "<p>A fictional breathing lesson lists four claims about ordinary air.</p>"
        "<p>(i) Select the two true gas facts.</p>"
        "<p>(ii) Using those selections from (i), how many facts did you pick?</p>"
    )
    solution = (
        "(i) Nitrogen majority and oxygen for cells are true.<br>"
        f"(ii) <strong>{fact_count}</strong> facts selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick nitrogen majority and oxygen use, "
        "then count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, fact_count),
            ("True gas facts", "Number picked"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two true facts, then count them.",
        ),
    )


@_u13_variant("breathing", "sms", "intermediate", "team_pulse_range_then_mean")
def _breathing_intermediate_sms_team_pulse_range_then_mean():
    pack = random.choice(_BR_MS_I_PULSE_PACKS)
    mean = (pack["a"] + pack["b"] + pack["c"]) // 3
    range_val = max(pack["a"], pack["b"], pack["c"]) - min(
        pack["a"], pack["b"], pack["c"]
    )
    correct = "muscles need more oxygen delivered by blood"
    distractors = (
        "the skeleton wants fame",
        "time stops during exercise",
        "air contains no oxygen",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional club publishes three aggregate pulse readings after "
        f"training: {pack['a']}, {pack['b']}, {pack['c']} bpm.</p>"
        "<p>(i) Find the mean pulse in bpm.</p>"
        f"<p>(ii) Find the range (highest − lowest) in bpm.</p>"
        f"<p>(iii) Using the mean from (i), during hard exercise pulse often "
        "rises because</p>"
    )
    solution = (
        f"(i) <strong>{mean}</strong> bpm<br>"
        f"(ii) <strong>{range_val}</strong> bpm<br>"
        f"(iii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Average and range the published data; "
        "muscles need more oxygen when working hard."
    )
    return (
        question,
        solution,
        hint,
        3,
        graded_answer_number_fields(
            (mean, range_val, letter),
            ("Mean pulse (bpm)", "Range (bpm)", "Why pulse rises"),
            field_types=("number", "number", "mcq"),
            field_options=(None, None, options),
            format_hint="Mean and range the table, then choose why pulse rises.",
        ),
    )


@_u13_variant("breathing", "sms", "intermediate", "lungs_circ_order_then_mcq")
def _breathing_intermediate_sms_lungs_circ_order_then_mcq():
    diagram = str(circulation_boxes(title="Fictional B lungs"))
    order_raw, order_bank = _u13_order_field(
        ("Lungs add oxygen to blood", "Body tissues use oxygen"),
        ("Heart digests food",),
    )
    correct = "less oxygen and more carbon dioxide than inhaled air"
    distractors = (
        "more oxygen and less carbon dioxide",
        "pure helium only",
        "no nitrogen at all",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional gas-exchange chart follows blood after the heart pumps.</p>"
        "<p>(i) Order lungs oxygenate, then body use.</p>"
        "<p>(ii) Using that gas path from (i), exhaled air usually has</p>"
    )
    solution = (
        "(i) <strong>lungs → body</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Lungs first, tissues second; cells use O2 "
        "and make CO2."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Gas path order", "Exhaled air change"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order lungs then body, then choose exhaled air change.",
        ),
    )


@_u13_variant("breathing", "sms", "intermediate", "sport_demand_pick_then_pulse")
def _breathing_intermediate_sms_sport_demand_pick_then_pulse():
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Blood carries oxygen to muscles", "Breathing moves air for gas exchange"),
        ("Bones pump air", "Friction is respiration"),
        2,
    )
    demand_count = 2
    question = (
        "<p>A fictional sport physiology poster lists four claims about "
        "exercise and gases.</p>"
        "<p>(i) Select the two true ideas about oxygen delivery in sport.</p>"
        "<p>(ii) Using those two from (i), how many true ideas did you select?</p>"
    )
    solution = (
        "(i) Blood carries O2; breathing supports gas exchange.<br>"
        f"(ii) <strong>{demand_count}</strong> ideas selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick blood transport and ventilation for "
        "gas exchange, then count."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, demand_count),
            ("True sport gas ideas", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two true ideas, then count selections.",
        ),
    )


@_u13_variant("breathing", "sms", "difficult", "recovery_pulse_then_scale")
def _breathing_difficult_sms_recovery_pulse_then_scale():
    pack = random.choice(_BR_MS_D_PULSE_PACKS)
    factor = 60 // pack["seconds"]
    bpm = pack["beats"] * factor
    correct = (
        "the body is still supplying extra oxygen and clearing extra carbon dioxide"
    )
    distractors = (
        "the race clock is broken",
        "mass increased during recovery",
        "friction is respiration",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>After a fictional sprint demo, aggregate published pulse shows "
        f"{pack['beats']} beats in {pack['seconds']} s (steady).</p>"
        "<p>(i) Scale to beats per minute.</p>"
        "<p>(ii) Using that elevated rate from (i), breathing stays fast for "
        "a while because</p>"
    )
    solution = (
        f"(i) <strong>{bpm}</strong> bpm<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Scale the published recovery pulse; extra "
        "O2 and CO2 clearing continue after sprint."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (bpm, letter),
            ("Pulse (bpm)", "Recovery breathing"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Scale to 60 s, then choose recovery reason.",
        ),
    )


@_u13_variant("breathing", "sms", "difficult", "salty_buoy_then_pressure")
def _breathing_difficult_sms_salty_buoy_then_pressure():
    markers = 4
    correct = "pressure on the body increases with depth"
    distractors = (
        "pressure falls to zero underwater",
        "buoyancy is mass in kilograms",
        "pulse replaces upthrust",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional open-water course marks four depth levels in salty "
        "water where buoyancy is greater than in fresh water.</p>"
        "<p>(i) How many depth markers are on the course diagram?</p>"
        "<p>(ii) Using that deeper-water context from (i), going deeper "
        "means</p>"
    )
    solution = (
        f"(i) <strong>{markers}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count the markers; deeper water means "
        "greater pressure."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (markers, letter),
            ("Depth markers", "Pressure with depth"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count markers, then choose the pressure fact.",
        ),
    )


@_u13_variant("breathing", "sms", "difficult", "three_system_order_then_pick")
def _breathing_difficult_sms_three_system_order_then_pick():
    order_raw, order_bank = _u13_order_field(
        (
            "Breathing moves air",
            "Circulation transports gases in blood",
            "Respiration uses oxygen in cells",
        ),
        ("Friction stores oxygen in bones",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Heart pumps blood", "Lungs exchange gases", "Body tissues use oxygen"),
        ("Bones pump air", "Helium is used in respiration"),
        3,
    )
    question = (
        "<p>A fictional sport biology review links ventilation, circulation "
        "and cell chemistry.</p>"
        "<p>(i) Order breathing, circulation, respiration.</p>"
        "<p>(ii) Using that chain from (i), select the three genuine "
        "circulation roles.</p>"
    )
    solution = (
        "(i) <strong>breathing → circulation → respiration</strong><br>"
        "(ii) Heart, lungs and body tissues are genuine roles."
    )
    hint = (
        "<strong>Key idea:</strong> Order the three systems, then pick heart, "
        "lungs and body roles."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("System order", "Circulation roles"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the systems, then select three circulation roles.",
        ),
    )


# ---------------------------------------------------------------------------
# sport_health — multi_step (I, D only; foundational MS = [])
# ---------------------------------------------------------------------------

@_u13_variant("sport_health", "ms", "intermediate", "antag_sketch_then_pair_count")
def _sport_health_intermediate_ms_antag_sketch_then_pair_count():
    diagram = str(antagonistic_pair(title="Fictional antagonistic pair"))
    pair_count = 2
    correct = "an antagonistic pair of muscles pulling opposite ways"
    distractors = (
        "two lungs exchanging gases",
        "two food groups on a plate",
        "a banned drug list",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        diagram
        + "<p>A fictional anatomy sketch labels muscle A above a bone and "
        "muscle B below.</p>"
        "<p>(i) How many muscles are in one antagonistic pair?</p>"
        "<p>(ii) Using that count from (i), A and B in the sketch are</p>"
    )
    solution = (
        f"(i) <strong>{pair_count}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A pair means two muscles; they pull "
        "opposite ways around a bone."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pair_count, letter),
            ("Muscles in pair", "Sketch meaning"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count muscles in a pair, then classify A and B.",
        ),
    )


_SH_MS_I_REST_PACKS = (
    {"rest": 2, "days": 7},
    {"rest": 3, "days": 7},
    {"rest": 1, "days": 7},
)


@_u13_variant("sport_health", "ms", "intermediate", "coach_rest_table_then_training")
def _sport_health_intermediate_ms_coach_rest_table_then_training():
    pack = random.choice(_SH_MS_I_REST_PACKS)
    training = pack["days"] - pack["rest"]
    correct = "the skeleton supports the body and protects organs"
    distractors = (
        "the skeleton pumps blood",
        "joints are gases in air",
        "muscles are bones",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional coach publishes a weekly plan table: "
        f"{pack['rest']} rest days in a {pack['days']}-day week.</p>"
        "<p>(i) How many training days are in that week?</p>"
        "<p>(ii) Using that schedule from (i), the skeleton mainly</p>"
    )
    solution = (
        f"(i) {pack['days']} − {pack['rest']} = <strong>{training}</strong> days<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract rest from 7; skeleton supports "
        "and protects."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (training, letter),
            ("Training days", "Skeleton role"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract rest days, then choose the skeleton role.",
        ),
    )


@_u13_variant("sport_health", "ms", "intermediate", "uv_order_then_pick")
def _sport_health_intermediate_ms_uv_order_then_pick():
    order_raw, order_bank = _u13_order_field(
        ("Sensible load and warm-up reduce some injury risk", "Shade and covering reduce UV damage outdoors"),
        ("Ignore bleeding and keep playing",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Use shade during outdoor sessions", "Follow school sun policy"),
        ("Compare pupils' skin colour in class", "Replace water with bleach"),
        2,
    )
    question = (
        "<p>A fictional sport-health policy poster lists injury and sun "
        "protection ideas.</p>"
        "<p>(i) Order injury sense, then UV protection.</p>"
        "<p>(ii) Using that order from (i), select two approved outdoor "
        "protections.</p>"
    )
    solution = (
        "(i) <strong>injury sense → UV protection</strong><br>"
        "(ii) Shade and school sun policy are approved."
    )
    hint = (
        "<strong>Key idea:</strong> Order load then sun sense; pick shade and "
        "policy, not body surveys."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Protection order", "Outdoor protections"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order the ideas, then select two protections.",
        ),
    )


@_u13_variant("sport_health", "ms", "difficult", "muscle_pair_then_bone")
def _sport_health_difficult_ms_muscle_pair_then_bone():
    diagram = str(antagonistic_pair(title="Fictional A above, B below"))
    correct = "muscles pull on bones that meet at a joint"
    distractors = (
        "bones push themselves with no tissue",
        "air is a muscle",
        "speed is a bone",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    parts = 3
    question = (
        diagram
        + "<p>A fictional lever diagram shows muscle A, bone and muscle B "
        "around a joint.</p>"
        "<p>(i) How many main parts (two muscles and one bone) are labelled "
        "in the lever idea?</p>"
        "<p>(ii) Using that lever from (i), a joint needs muscles and a "
        "skeleton because</p>"
    )
    solution = (
        f"(i) <strong>{parts}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Count muscle–bone–muscle; muscles pull "
        "on bones at joints."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (parts, letter),
            ("Lever parts", "Why joint needs both"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count lever parts, then choose why muscles and skeleton matter.",
        ),
    )


@_u13_variant("sport_health", "ms", "difficult", "injury_prevent_pick_then_count")
def _sport_health_difficult_ms_injury_prevent_pick_then_count():
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        (
            "Warm up before hard sessions",
            "Include rest days in a training week",
        ),
        (
            "Ignore bleeding and keep playing",
            "Use banned drugs for unfair advantage",
        ),
        2,
    )
    prevent_count = 2
    question = (
        "<p>A fictional injury-prevention leaflet lists four training habits.</p>"
        "<p>(i) Select the two habits that reduce injury risk.</p>"
        "<p>(ii) Using those two from (i), how many prevention habits did you "
        "select?</p>"
    )
    solution = (
        "(i) Warm-up and rest days reduce risk.<br>"
        f"(ii) <strong>{prevent_count}</strong> habits selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick warm-up and rest; count selections — "
        "no personal injury disclosure."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, prevent_count),
            ("Prevention habits", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two prevention habits, then count them.",
        ),
    )


@_u13_variant("sport_health", "ms", "difficult", "doping_policy_order_then_mcq")
def _sport_health_difficult_ms_doping_policy_order_then_mcq():
    order_raw, order_bank = _u13_order_field(
        (
            "Banned drugs can harm health",
            "Banned drugs make contests unfair",
            "Fair sport follows anti-doping rules",
        ),
        ("Ask classmates what they take",),
    )
    correct = "outdoor sessions still follow the school's sun policy"
    distractors = (
        "pupils must compare skin colour in the quiz",
        "joints become lungs",
        "drugs replace shade",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fair-sport policy covers drugs and outdoor health.</p>"
        "<p>(i) Order harm, unfairness, then follow rules.</p>"
        "<p>(ii) Using that policy chain from (i), cloud cover does not make "
        "UV automatically safe, so</p>"
    )
    solution = (
        "(i) <strong>harm → unfair → rules</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order drug-policy facts; cloud does not "
        "remove need for sun policy."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Policy order", "UV policy reason"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the policy chain, then choose the sun-policy fact.",
        ),
    )


# ---------------------------------------------------------------------------
# sport_health — situational_multi_step (SMS)
# ---------------------------------------------------------------------------

@_u13_variant("sport_health", "sms", "foundational", "skeleton_joint_order_then_count")
def _sport_health_foundational_sms_skeleton_joint_order_then_count():
    order_raw, order_bank = _u13_order_field(
        ("Skeleton supports the body", "Joint is where bones meet", "Antagonistic muscle pair"),
        ("A sports slogan replaces anatomy",),
    )
    step_count = 3
    question = (
        "<p>A fictional anatomy wall chart lists skeleton, joint and muscle "
        "pair ideas.</p>"
        "<p>(i) Order skeleton, joint, antagonistic pair.</p>"
        "<p>(ii) Using that order from (i), how many anatomy steps did you "
        "sequence?</p>"
    )
    solution = (
        "(i) <strong>skeleton → joint → pair</strong><br>"
        f"(ii) <strong>{step_count}</strong> steps."
    )
    hint = (
        "<strong>Key idea:</strong> Framework, meeting place, opposite muscles; "
        "count the ordered steps."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, step_count),
            ("Anatomy order", "Steps sequenced"),
            field_types=("order", "number"),
            field_options=(order_bank, None),
            format_hint="Order the three ideas, then count steps.",
        ),
    )


@_u13_variant("sport_health", "sms", "foundational", "antag_pair_then_mcq")
def _sport_health_foundational_sms_antag_pair_then_mcq():
    diagram = str(antagonistic_pair())
    correct = "they pull in opposite ways around a bone"
    distractors = (
        "they always pull the same way",
        "they are two lungs",
        "they measure pulse in newtons",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    pair_n = 2
    question = (
        diagram
        + "<p>A fictional sport-health poster shows muscles A and B on a "
        "bone sketch.</p>"
        "<p>(i) How many muscles are in one antagonistic pair?</p>"
        "<p>(ii) Using that pair from (i), antagonistic muscles</p>"
    )
    solution = (
        f"(i) <strong>{pair_n}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> A pair is two muscles pulling opposite "
        "ways."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pair_n, letter),
            ("Muscles in pair", "Antagonistic idea"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the pair, then choose how they work.",
        ),
    )


@_u13_variant("sport_health", "sms", "foundational", "safe_sport_pick_then_count")
def _sport_health_foundational_sms_safe_sport_pick_then_count():
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Sensible load and warm-up", "UV shade and covering outdoors"),
        ("Banned performance drugs", "Ignore bleeding and keep playing"),
        2,
    )
    safe_count = 2
    question = (
        "<p>A fictional safe-sport checklist lists four habits.</p>"
        "<p>(i) Select the two approved health protections.</p>"
        "<p>(ii) Using those two from (i), how many protections did you select?</p>"
    )
    solution = (
        "(i) Load/warm-up and UV protection are approved.<br>"
        f"(ii) <strong>{safe_count}</strong> protections."
    )
    hint = (
        "<strong>Key idea:</strong> Pick load sense and sun protection; "
        "count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, safe_count),
            ("Health protections", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two protections, then count them.",
        ),
    )


@_u13_variant("sport_health", "sms", "intermediate", "flex_pair_then_joint_mcq")
def _sport_health_intermediate_sms_flex_pair_then_joint_mcq():
    diagram = str(antagonistic_pair(title="Fictional elbow pair"))
    correct = "bends at the elbow; the opposite muscle relaxes"
    distractors = (
        "lengthens the bones permanently",
        "becomes a joint made of air",
        "stops having mass",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    pair_n = 2
    question = (
        diagram
        + "<p>A fictional diagram shows the upper-arm muscle pair at an elbow "
        "joint.</p>"
        "<p>(i) How many muscles work as one antagonistic pair here?</p>"
        "<p>(ii) Using that pair from (i), when the front muscle shortens, "
        "the arm typically</p>"
    )
    solution = (
        f"(i) <strong>{pair_n}</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Two muscles in a pair; one shortens, the "
        "other relaxes to bend the joint."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pair_n, letter),
            ("Muscles in pair", "Bending at elbow"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Count the pair, then choose what happens when one shortens.",
        ),
    )


@_u13_variant("sport_health", "sms", "intermediate", "helmet_protect_order_then_pick")
def _sport_health_intermediate_sms_helmet_protect_order_then_pick():
    order_raw, order_bank = _u13_order_field(
        ("Helmet protects the skull (skeleton)", "Broken skin should be cleaned and covered"),
        ("Helmet measures pulse rate",),
    )
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        ("Banned drugs can harm health", "Fair sport follows anti-doping rules"),
        ("Secret banned drugs are fair", "Diagnose classmates from their injuries"),
        2,
    )
    question = (
        "<p>A fictional cycling safety and fair-sport poster lists protection "
        "ideas.</p>"
        "<p>(i) Order helmet protection, then wound first-aid sense.</p>"
        "<p>(ii) Using that order from (i), select two fair-sport facts about "
        "banned drugs.</p>"
    )
    solution = (
        "(i) <strong>helmet → first aid</strong><br>"
        "(ii) Drugs harm health; anti-doping rules matter."
    )
    hint = (
        "<strong>Key idea:</strong> Order protection steps; pick general drug "
        "facts, not personal disclosure."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, pick_raw),
            ("Protection order", "Fair-sport drug facts"),
            field_types=("order", "pick"),
            field_options=(order_bank, pick_bank),
            field_pick_counts=(None, pick_count),
            format_hint="Order protection ideas, then select two drug-policy facts.",
        ),
    )


@_u13_variant("sport_health", "sms", "intermediate", "rest_days_table_then_train")
def _sport_health_intermediate_sms_rest_days_table_then_train():
    pack = random.choice(_SH_MS_I_REST_PACKS)
    training = pack["days"] - pack["rest"]
    correct = "a joint is where bones meet and movement can happen"
    distractors = (
        "a joint is a gas in air",
        "a joint never moves",
        "bones are muscles",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional coach table shows "
        f"{pack['rest']} rest days in a {pack['days']}-day week.</p>"
        "<p>(i) How many training days are planned?</p>"
        "<p>(ii) Using that weekly plan from (i), in anatomy a joint is</p>"
    )
    solution = (
        f"(i) <strong>{training}</strong> training days<br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Subtract rest from 7; joints are where "
        "bones meet."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (training, letter),
            ("Training days", "Joint definition"),
            field_types=("number", "mcq"),
            field_options=(None, options),
            format_hint="Subtract rest days, then define a joint.",
        ),
    )


@_u13_variant("sport_health", "sms", "difficult", "overuse_chain_then_mcq")
def _sport_health_difficult_sms_overuse_chain_then_mcq():
    order_raw, order_bank = _u13_order_field(
        (
            "Skeleton provides framework",
            "Joint allows movement",
            "Antagonistic muscles pull opposite ways",
        ),
        ("Muscles push bones like pistons",),
    )
    correct = "raise injury risk; load and recovery matter"
    distractors = (
        "only improve slogans",
        "turn muscle into nitrogen",
        "ban all water",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional training-science review links anatomy and load.</p>"
        "<p>(i) Order skeleton, joint, antagonistic pair.</p>"
        "<p>(ii) Using that body chain from (i), repeating the same action "
        "with no rest can</p>"
    )
    solution = (
        "(i) <strong>skeleton → joint → pair</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order anatomy chain; overuse without "
        "recovery raises injury risk."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Anatomy chain", "Overuse effect"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the anatomy chain, then choose overuse effect.",
        ),
    )


@_u13_variant("sport_health", "sms", "difficult", "uv_policy_pick_then_count")
def _sport_health_difficult_sms_uv_policy_pick_then_count():
    pick_raw, pick_bank, pick_count = _u13_pick_field(
        (
            "Follow school sun policy on cloudy days",
            "Use shade and covering during outdoor sport",
        ),
        (
            "Rank pupils by skin colour",
            "Skip first aid for broken skin",
        ),
        2,
    )
    policy_count = 2
    question = (
        "<p>A fictional UV policy lists four outdoor-session rules.</p>"
        "<p>(i) Select the two approved sun-protection rules.</p>"
        "<p>(ii) Using those two from (i), how many policy rules did you select?</p>"
    )
    solution = (
        "(i) School policy and shade/covering are approved.<br>"
        f"(ii) <strong>{policy_count}</strong> rules selected."
    )
    hint = (
        "<strong>Key idea:</strong> Pick policy and shade; no body surveys; "
        "count selections."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (pick_raw, policy_count),
            ("UV policy rules", "Number selected"),
            field_types=("pick", "number"),
            field_options=(pick_bank, None),
            field_pick_counts=(pick_count, None),
            format_hint="Select two UV rules, then count them.",
        ),
    )


@_u13_variant("sport_health", "sms", "difficult", "fair_sport_order_then_drug_mcq")
def _sport_health_difficult_sms_fair_sport_order_then_drug_mcq():
    order_raw, order_bank = _u13_order_field(
        ("Injury sense and sensible load", "UV protection outdoors", "Anti-doping rules for fair sport"),
        ("Personal drug disclosure in class",),
    )
    correct = "following anti-doping and medical rules without asking classmates what they take"
    distractors = (
        "secret banned drugs are encouraged",
        "ignoring bleeding is fair play",
        "skipping all water is healthy",
    )
    options, letter = _u13_mcq_field(correct, distractors)
    question = (
        "<p>A fictional fair-sport charter covers load, sun and drugs.</p>"
        "<p>(i) Order injury sense, UV protection, anti-doping rules.</p>"
        "<p>(ii) Using that charter from (i), fair sport includes</p>"
    )
    solution = (
        "(i) <strong>injury → UV → anti-doping</strong><br>"
        f"(ii) <strong>{correct}</strong>"
    )
    hint = (
        "<strong>Key idea:</strong> Order health protections; fair sport uses "
        "rules, not personal drug surveys."
    )
    return (
        question,
        solution,
        hint,
        2,
        graded_answer_number_fields(
            (order_raw, letter),
            ("Charter order", "Fair sport includes"),
            field_types=("order", "mcq"),
            field_options=(order_bank, options),
            format_hint="Order the charter, then choose fair-sport inclusion.",
        ),
    )


MOVEMENT_SMS_POOLS = {
    "foundational": [
        _movement_foundational_sms_session_speed_extrapolate,
        _movement_foundational_sms_minutes_seconds_convert,
        _movement_foundational_sms_relay_baton_timing,
    ],
    "intermediate": [
        _movement_intermediate_sms_graph_read_slope,
        _movement_intermediate_sms_minute_run_chain,
        _movement_intermediate_sms_two_leg_pass,
    ],
    "difficult": [
        _movement_difficult_sms_km_lap_units,
        _movement_difficult_sms_journey_average_total,
        _movement_difficult_sms_graph_rest_sections,
    ],
}

FORCES_SPORT_MS_POOLS = {
    "foundational": [
        _forces_sport_foundational_ms_net_zero_then_pair,
        _forces_sport_foundational_ms_friction_grip_then_net,
        _forces_sport_foundational_ms_force_order_then_pick,
    ],
    "intermediate": [
        _forces_sport_intermediate_ms_balance_net_then_cog,
        _forces_sport_intermediate_ms_friction_slow_then_weight,
        _forces_sport_intermediate_ms_interaction_order_then_pick,
    ],
    "difficult": [
        _forces_sport_difficult_ms_resultant_sum_then_eq,
        _forces_sport_difficult_ms_blocks_push_then_net,
        _forces_sport_difficult_ms_pair_diagram_then_pick,
    ],
}

FORCES_SPORT_SMS_POOLS = {
    "foundational": [
        _forces_sport_foundational_sms_shoe_grip_then_cancel,
        _forces_sport_foundational_sms_push_pair_then_unit,
        _forces_sport_foundational_sms_friction_order_then_pick,
    ],
    "intermediate": [
        _forces_sport_intermediate_sms_gymnast_eq_then_cog,
        _forces_sport_intermediate_sms_puck_fric_then_net,
        _forces_sport_intermediate_sms_weight_mass_order_then_mcq,
    ],
    "difficult": [
        _forces_sport_difficult_sms_sprinter_blocks_then_resultant,
        _forces_sport_difficult_sms_air_drag_then_sum,
        _forces_sport_difficult_sms_equilibrium_chain_then_pick,
    ],
}

BREATHING_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _breathing_intermediate_ms_team_pulse_mean_then_bpm,
        _breathing_intermediate_ms_lung_box_then_gas_mcq,
        _breathing_intermediate_ms_circ_order_then_o2_pick,
    ],
    "difficult": [
        _breathing_difficult_ms_session_pulse_scale_then_beats,
        _breathing_difficult_ms_buoyancy_depth_then_mcq,
        _breathing_difficult_ms_full_circ_then_co2_count,
    ],
}

BREATHING_SMS_POOLS = {
    "foundational": [
        _breathing_foundational_sms_club_pulse_table_then_bpm,
        _breathing_foundational_sms_heart_letter_then_beats,
        _breathing_foundational_sms_air_gas_pick_then_count,
    ],
    "intermediate": [
        _breathing_intermediate_sms_team_pulse_range_then_mean,
        _breathing_intermediate_sms_lungs_circ_order_then_mcq,
        _breathing_intermediate_sms_sport_demand_pick_then_pulse,
    ],
    "difficult": [
        _breathing_difficult_sms_recovery_pulse_then_scale,
        _breathing_difficult_sms_salty_buoy_then_pressure,
        _breathing_difficult_sms_three_system_order_then_pick,
    ],
}

SPORT_HEALTH_MS_POOLS = {
    "foundational": [],
    "intermediate": [
        _sport_health_intermediate_ms_antag_sketch_then_pair_count,
        _sport_health_intermediate_ms_coach_rest_table_then_training,
        _sport_health_intermediate_ms_uv_order_then_pick,
    ],
    "difficult": [
        _sport_health_difficult_ms_muscle_pair_then_bone,
        _sport_health_difficult_ms_injury_prevent_pick_then_count,
        _sport_health_difficult_ms_doping_policy_order_then_mcq,
    ],
}

SPORT_HEALTH_SMS_POOLS = {
    "foundational": [
        _sport_health_foundational_sms_skeleton_joint_order_then_count,
        _sport_health_foundational_sms_antag_pair_then_mcq,
        _sport_health_foundational_sms_safe_sport_pick_then_count,
    ],
    "intermediate": [
        _sport_health_intermediate_sms_flex_pair_then_joint_mcq,
        _sport_health_intermediate_sms_helmet_protect_order_then_pick,
        _sport_health_intermediate_sms_rest_days_table_then_train,
    ],
    "difficult": [
        _sport_health_difficult_sms_overuse_chain_then_mcq,
        _sport_health_difficult_sms_uv_policy_pick_then_count,
        _sport_health_difficult_sms_fair_sport_order_then_drug_mcq,
    ],
}
