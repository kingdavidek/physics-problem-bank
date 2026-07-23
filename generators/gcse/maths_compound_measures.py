"""
GCSE Maths – Compound Measures
15 foundational · 15 intermediate · 15 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
Show-that and express-in-terms variants use Plan A checkpoints (number / algebraic).
"""
import random
import math
from generators.shared.utils import make_problem
from generators.gcse.maths_bank_procedural_mcq import procedural_mcq_for
from generators.shared.variant_utils import (
    select_tier_variants,
    mcq_variants_from_bank_with_procedural,
    mcq_variants_from_fn,
    run_mcq_variant,
    pick_named_variant,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _dp(v, places=2):
    """Format a number neatly — strip trailing zeros from decimals."""
    if isinstance(v, int) or (isinstance(v, float) and v == int(v)):
        return str(int(v))
    return f"{v:.{places}f}".rstrip('0').rstrip('.')


def _cm_raw(value, places=2):
    """Canonical numeric string for typed answer checking."""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return _dp(value, places)
    return str(value)


def _cm_fields_answer(values, labels, places=2, field_types=None):
    types = tuple(field_types) if field_types else None
    payload = {
        'type': 'number_fields',
        'values': tuple(
            str(v) if types and types[i] == 'algebraic' else _cm_raw(v, places)
            for i, v in enumerate(values)
        ),
        'labels': tuple(labels),
    }
    if types:
        payload['field_types'] = types
    return payload


def _cm_keyword_answer(value):
    return {'type': 'keyword', 'value': str(value).strip().lower()}


def _cm_algebraic_answer(expr, format_hint=None):
    payload = {'type': 'algebraic', 'value': str(expr)}
    if format_hint:
        payload['format_hint'] = format_hint
    return payload


def _cm_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'number_fields':
            values = raw.get('values') or ()
            labels = raw.get('labels') or ()
            field_types = raw.get('field_types') or ()
            if values and labels and len(values) == len(labels):
                sep = (
                    '\x1e'
                    if field_types and any(t != 'number' for t in field_types)
                    else '|'
                )
                extra = {
                    'correct_answer_raw': sep.join(str(v) for v in values),
                    'answer_type': 'number_fields',
                    'answer_labels': list(labels),
                    'answer_field_types': list(field_types) if field_types else (
                        ['number'] * len(labels)
                    ),
                    'answer_format_hint': 'Complete every step',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'keyword':
            value = raw.get('value')
            if value is not None and str(value).strip():
                extra = {
                    'correct_answer_raw': str(value).strip().lower(),
                    'answer_type': 'keyword',
                    'answer_format_hint': 'Enter your answer in words',
                }
        elif isinstance(raw, dict) and raw.get('type') == 'algebraic':
            text = str(raw.get('value') or '')
            extra = {
                'correct_answer_raw': text,
                'answer_type': 'algebraic',
                'answer_format_hint': raw.get(
                    'format_hint',
                    'Enter the simplified expression in terms of v',
                ),
            }
        elif isinstance(raw, (int, float)):
            extra = {
                'correct_answer_raw': _cm_raw(raw),
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
        elif isinstance(raw, str):
            extra = {
                'correct_answer_raw': raw,
                'answer_type': 'number',
                'answer_format_hint': 'Enter a number',
            }
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'maths', 'compound_measures', **extra
    )

def _formula_tri(top, bl, br, cover=None):
    """
    Classic formula triangle: top quantity alone; bottom row is bl × br.
    Cover top → multiply bottom pair; cover a bottom letter → top ÷ other bottom.
    """
    shade = "#ffd080"
    normal_top = "#dbeafe"
    normal_bl = "#e8f4fd"
    normal_br = "#fef9c3"
    c_top = shade if cover == "top" else normal_top
    c_bl = shade if cover == "bl" else normal_bl
    c_br = shade if cover == "br" else normal_br
    stroke = "#1a6fa8"
    return (
        '<svg width="200" height="160" viewBox="0 0 200 160" '
        'style="background:#f9f8f5;border-radius:6px;max-width:170px;'
        'display:inline-block;margin:6px 4px;vertical-align:middle;">'
        f'<polygon points="100,12 58,78 142,78" fill="{c_top}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<polygon points="58,78 12,150 100,150 100,78" fill="{c_bl}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<polygon points="100,78 142,78 188,150 100,150" fill="{c_br}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<polygon points="100,12 12,150 188,150" fill="none" stroke="{stroke}" stroke-width="2.5"/>'
        f'<line x1="58" y1="78" x2="142" y2="78" stroke="{stroke}" stroke-width="1.5"/>'
        f'<line x1="100" y1="78" x2="100" y2="150" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="100" y="52" font-size="18" fill="#333" text-anchor="middle" font-weight="bold">{top}</text>'
        f'<text x="56" y="128" font-size="16" fill="#333" text-anchor="middle" font-weight="bold">{bl}</text>'
        f'<text x="144" y="128" font-size="16" fill="#333" text-anchor="middle" font-weight="bold">{br}</text>'
        '<text x="100" y="128" font-size="14" fill="#555" text-anchor="middle">×</text>'
        "</svg>"
    )


def _sdt(cover=None): return _formula_tri("D", "S", "T", cover)
def _dmv(cover=None): return _formula_tri("M", "ρ", "V", cover)
def _pfa(cover=None): return _formula_tri("F", "P", "A", cover)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cm_f1_sdt_find_speed():
    combos = [(120,3,40),(150,3,50),(180,4,45),(200,5,40),
              (240,4,60),(300,5,60),(180,2,90),(350,7,50)]
    d, t, s = random.choice(combos)
    q = (f"A car travels {d} km in {t} hours. Find the average speed in km/h.<br>{_sdt('bl')}")
    sol = (f"Speed = Distance ÷ Time<br>"
           f"= {d} ÷ {t}<br>"
           f"= <strong>{s} km/h</strong>")
    return q, sol, "Cover S in the SDT triangle: Speed = Distance ÷ Time.", 2, s


def _cm_f2_sdt_find_distance():
    combos = [(60,3,180),(50,4,200),(80,3,240),(45,4,180),(70,3,210),(40,5,200)]
    s, t, d = random.choice(combos)
    q = (f"A cyclist travels at a constant speed of {s} km/h for {t} hours. "
         f"How far does she travel?<br>{_sdt('top')}")
    sol = (f"Distance = Speed × Time<br>"
           f"= {s} × {t}<br>"
           f"= <strong>{d} km</strong>")
    return q, sol, "Cover D in the SDT triangle: Distance = Speed × Time.", 2, d


def _cm_f3_sdt_find_time():
    combos = [(80,200,2.5),(60,180,3),(50,200,4),(100,250,2.5),(70,280,4),(90,360,4)]
    s, d, t = random.choice(combos)
    q = (f"A train travels {d} km at an average speed of {s} km/h. "
         f"How long does the journey take?<br>{_sdt('br')}")
    sol = (f"Time = Distance ÷ Speed<br>"
           f"= {d} ÷ {s}<br>"
           f"= <strong>{_dp(t)} hours</strong>")
    return q, sol, "Cover T in the SDT triangle: Time = Distance ÷ Speed.", 2, t


def _cm_f4_dmv_find_density():
    combos = [(480,60,8),(270,30,9),(156,12,13),(350,50,7),(810,90,9),(480,80,6)]
    m, v, d = random.choice(combos)
    q = (f"A metal block has a mass of {m} g and a volume of {v} cm³. "
         f"Find its density.<br>{_dmv('bl')}")
    sol = (f"Density = Mass ÷ Volume<br>"
           f"= {m} ÷ {v}<br>"
           f"= <strong>{d} g/cm³</strong>")
    return q, sol, "Cover ρ in the DMV triangle: Density = Mass ÷ Volume.", 2, d


def _cm_f5_dmv_find_mass():
    combos = [(8.9,100,890),(7.8,50,390),(2.7,200,540),(11.3,40,452),(19.3,10,193)]
    d, v, m = random.choice(combos)
    q = (f"A material has a density of {d} g/cm³. "
         f"Find the mass of a {v} cm³ block of this material.<br>{_dmv('top')}")
    sol = (f"Mass = Density × Volume<br>"
           f"= {d} × {v}<br>"
           f"= <strong>{_dp(m)} g</strong>")
    return q, sol, "Cover M in the DMV triangle: Mass = Density × Volume.", 2, m


def _cm_f6_dmv_find_volume():
    combos = [(540,2.7,200),(390,7.8,50),(891,8.9,100),(108,2.7,40),(452,11.3,40)]
    m, d, v = random.choice(combos)
    q = (f"An object has a mass of {m} g and is made of a material with "
         f"density {d} g/cm³. Find its volume.<br>{_dmv('br')}")
    sol = (f"Volume = Mass ÷ Density<br>"
           f"= {m} ÷ {d}<br>"
           f"= <strong>{_dp(v)} cm³</strong>")
    return q, sol, "Cover V in the DMV triangle: Volume = Mass ÷ Density.", 2, v


def _cm_f7_pfa_find_pressure():
    combos = [(400,20,20),(150,5,30),(600,30,20),(800,40,20),(240,8,30),(500,25,20)]
    f, a, p = random.choice(combos)
    q = (f"A force of {f} N acts on a surface of area {a} m². "
         f"Find the pressure in Pa (N/m²).<br>{_pfa('bl')}")
    sol = (f"Pressure = Force ÷ Area<br>"
           f"= {f} ÷ {a}<br>"
           f"= <strong>{p} Pa</strong>")
    return q, sol, "Cover P in the PFA triangle: Pressure = Force ÷ Area. 1 Pa = 1 N/m².", 2, p


def _cm_f8_pfa_find_force():
    combos = [(30,5,150),(20,8,160),(25,4,100),(15,12,180),(40,3,120),(50,6,300)]
    p, a, f = random.choice(combos)
    q = (f"The pressure on a surface is {p} Pa. The area of the surface is {a} m². "
         f"Find the force exerted.<br>{_pfa('top')}")
    sol = (f"Force = Pressure × Area<br>"
           f"= {p} × {a}<br>"
           f"= <strong>{f} N</strong>")
    return q, sol, "Cover F in the PFA triangle: Force = Pressure × Area.", 2, f


def _cm_f9_pfa_find_area():
    combos = [(240,8,30),(300,12,25),(180,9,20),(480,16,30),(360,12,30)]
    f, p, a = random.choice(combos)
    q = (f"A force of {f} N produces a pressure of {p} Pa. "
         f"Find the area over which the force acts.<br>{_pfa('br')}")
    sol = (f"Area = Force ÷ Pressure<br>"
           f"= {f} ÷ {p}<br>"
           f"= <strong>{a} m²</strong>")
    return q, sol, "Cover A in the PFA triangle: Area = Force ÷ Pressure.", 2, a


def _cm_f10_convert_kmh_to_ms():
    kmh = random.choice([18, 36, 54, 72, 90, 108, 126, 144])
    ms = kmh * 5 / 18
    q = f"Convert {kmh} km/h into m/s."
    sol = (f"To convert km/h to m/s: multiply by 5 and divide by 18 (or divide by 3.6).<br>"
           f"{kmh} × 5 ÷ 18 = {kmh * 5} ÷ 18<br>"
           f"= <strong>{_dp(ms)} m/s</strong>")
    return q, sol, "km/h → m/s: multiply by 5/18 (equivalently, divide by 3.6).", 2, ms


def _cm_f11_convert_ms_to_kmh():
    ms = random.choice([5, 10, 15, 20, 25, 30, 40])
    kmh = ms * 3.6
    q = f"Convert {ms} m/s into km/h."
    sol = (f"To convert m/s to km/h: multiply by 3.6 (or multiply by 18 and divide by 5).<br>"
           f"{ms} × 3.6 = <strong>{_dp(kmh)} km/h</strong>")
    return q, sol, "m/s → km/h: multiply by 3.6.", 2, kmh


def _cm_f12_population_density_find():
    combos = [(12000,20,600),(15000,25,600),(24000,30,800),
              (30000,40,750),(45000,50,900),(60000,60,1000),
              (20000,40,500),(18000,30,600),(48000,60,800)]
    pop, area, dens = random.choice(combos)
    q = (f"A town has a population of {pop:,} people and covers an area of {area} km². "
         f"Find the population density in people/km².")
    sol = (f"Population Density = Population ÷ Area<br>"
           f"= {pop:,} ÷ {area}<br>"
           f"= <strong>{dens:,} people/km²</strong>")
    return q, sol, "Population Density = Population ÷ Area.", 2, dens


def _cm_f13_population_find_pop():
    combos = [(200,8,1600),(250,10,2500),(300,12,3600),(400,15,6000),(500,20,10000)]
    dens, area, pop = random.choice(combos)
    q = (f"A region has a population density of {dens} people/km² and covers {area} km². "
         f"Estimate the total population.")
    sol = (f"Population = Density × Area<br>"
           f"= {dens} × {area}<br>"
           f"= <strong>{pop:,} people</strong>")
    return q, sol, "Population = Density × Area.", 2, pop


def _cm_f14_flow_rate_volume():
    combos = [(2,10,20),(3,8,24),(4,15,60),(5,12,60),(6,10,60),(8,5,40),(10,20,200)]
    rate, time, vol = random.choice(combos)
    q = (f"Water flows from a tap at a rate of {rate} litres per minute. "
         f"How many litres flow in {time} minutes?")
    sol = (f"Volume = Rate × Time<br>"
           f"= {rate} × {time}<br>"
           f"= <strong>{vol} litres</strong>")
    return q, sol, "Volume = Flow Rate × Time.", 2, vol


def _cm_f15_density_compare():
    scenarios = [
        ("Object A: mass 300 g, volume 50 cm³", 6.0,
         "Object B: mass 480 g, volume 60 cm³", 8.0, "Object B"),
        ("Object A: mass 200 g, volume 40 cm³", 5.0,
         "Object B: mass 280 g, volume 40 cm³", 7.0, "Object B"),
        ("Material X: mass 150 g, volume 25 cm³", 6.0,
         "Material Y: mass 350 g, volume 50 cm³", 7.0, "Material Y"),
        ("Stone A: mass 250 g, volume 100 cm³", 2.5,
         "Stone B: mass 360 g, volume 120 cm³", 3.0, "Stone B"),
    ]
    d1txt, d1, d2txt, d2, winner = random.choice(scenarios)
    q = (f"{d1txt}. {d2txt}. Which has the greater density? Show your working.")
    sol = (f"Density of first: {d1} g/cm³<br>"
           f"Density of second: {d2} g/cm³<br>"
           f"Since {d2} > {d1}, the denser object is <strong>{winner}</strong>.")
    return q, sol, "Calculate density = mass ÷ volume for each, then compare.", 3, _cm_keyword_answer(winner)


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cm_i1_average_speed_two_legs():
    combos = [(60,3,40,2,180,80,260,5),(80,2,40,3,160,120,280,5),
              (50,4,100,2,200,200,400,6),(60,2,30,4,120,120,240,6)]
    s1, t1, s2, t2, d1, d2, total_d, total_t = random.choice(combos)
    avg = total_d / total_t
    q = (f"A driver travels {d1} km at {s1} km/h, then {d2} km at {s2} km/h. "
         f"Find the average speed for the whole journey.")
    sol = (f"Time for first leg  = {d1} ÷ {s1} = {t1} h<br>"
           f"Time for second leg = {d2} ÷ {s2} = {t2} h<br>"
           f"Total distance = {d1} + {d2} = {total_d} km<br>"
           f"Total time     = {t1} + {t2} = {total_t} h<br>"
           f"Average speed  = {total_d} ÷ {total_t} = <strong>{_dp(avg)} km/h</strong>")
    return q, sol, "Average speed = total distance ÷ total time (NOT the mean of the two speeds).", 4, avg


def _cm_i2_time_hours_minutes():
    combos = [(60,1,30,90),(80,2,15,175),(90,1,20,120),(120,1,15,150),(100,1,30,250)]
    s, h, m, d = random.choice(combos)
    t_h = h + m / 60
    q = (f"A train travels at {s} km/h for {h} hour{'s' if h > 1 else ''} and {m} minutes. "
         f"How far does it travel?")
    sol = (f"Convert time: {h} h {m} min = {h} + {m}/60 = {_dp(t_h)} h<br>"
           f"Distance = {s} × {_dp(t_h)} = <strong>{d} km</strong>")
    return q, sol, "Convert minutes to hours (÷60) before using D = S × T.", 3, d


def _cm_i3_alloy_density_by_vol():
    combos = [(9,3,40,20),(10,2,30,60),(8,4,50,30),(11,3,60,40),(9,4,30,20)]
    d1, d2, v1, v2 = random.choice(combos)
    m1, m2 = d1 * v1, d2 * v2
    total_m, total_v = m1 + m2, v1 + v2
    d_mix = round(total_m / total_v, 3)
    q = (f"An alloy is made by mixing {v1} cm³ of Metal A (density {d1} g/cm³) "
         f"with {v2} cm³ of Metal B (density {d2} g/cm³). "
         f"Find the density of the alloy.")
    sol = (f"Mass A = {d1} × {v1} = {m1} g<br>"
           f"Mass B = {d2} × {v2} = {m2} g<br>"
           f"Total mass = {total_m} g;  Total volume = {total_v} cm³<br>"
           f"Density = {total_m} ÷ {total_v} = <strong>{_dp(d_mix)} g/cm³</strong>")
    return q, sol, "Mass = density × volume for each. Sum masses, sum volumes, then divide.", 4, d_mix


def _cm_i4_pfa_box_weight():
    combos = [(10,1,1,100,100),(20,2,1,200,100),(30,1.5,2,300,100),(50,2,2.5,500,100),(40,2,2,400,100)]
    mass_kg, L, W, force, pressure = random.choice(combos)
    area = round(L * W, 2)
    q = (f"A box of mass {mass_kg} kg rests on a floor. "
         f"Its base measures {L} m × {W} m. "
         f"Find the pressure the box exerts on the floor. (g = 10 N/kg)")
    sol = (f"Weight = mass × g = {mass_kg} × 10 = {force} N<br>"
           f"Area = {L} × {W} = {area} m²<br>"
           f"Pressure = {force} ÷ {area} = <strong>{_dp(pressure)} Pa</strong>")
    return q, sol, "Weight (force) = mass × g. Pressure = force ÷ area.", 4, pressure


def _cm_i5_sdt_time_in_minutes():
    combos = [(60,15,0.25,15),(80,30,0.5,40),(90,20,1/3,30),(120,15,0.25,30),(100,30,0.5,50)]
    s, t_min, t_h, d = random.choice(combos)
    q = (f"A car travels at {s} km/h for {t_min} minutes. "
         f"How far does it travel? Give your answer in km.")
    sol = (f"Convert time: {t_min} min = {t_min}/60 = {_dp(t_h)} hours<br>"
           f"Distance = {s} × {_dp(t_h)} = <strong>{_dp(d)} km</strong>")
    return q, sol, "Convert minutes to hours (÷60) before using Distance = Speed × Time.", 3, d


def _cm_i6_flow_rate_fill_tank():
    combos = [(4,60,15),(5,100,20),(6,120,20),(8,80,10),(10,200,20),(4,80,20),(5,75,15)]
    rate, vol, time = random.choice(combos)
    q = (f"A bath holds {vol} litres of water. "
         f"A tap fills it at {rate} litres per minute. "
         f"How long does it take to fill the bath?")
    sol = (f"Time = Volume ÷ Rate<br>"
           f"= {vol} ÷ {rate}<br>"
           f"= <strong>{time} minutes</strong>")
    return q, sol, "Time = Volume ÷ Flow Rate.", 3, time


def _cm_i7_density_sphere():
    combos = [(3, 2.7), (4, 7.8), (5, 8.9), (2, 11.3)]
    r_cm, density = random.choice(combos)
    vol = round((4 / 3) * math.pi * r_cm ** 3, 1)
    mass = round(density * vol, 1)
    q = (f"A solid sphere has radius {r_cm} cm. It is made from a material with "
         f"density {density} g/cm³. "
         f"Find the mass of the sphere. (V = 4πr³/3)")
    sol = (f"Volume = (4/3) × π × {r_cm}³ = (4/3) × π × {r_cm**3} = {vol} cm³<br>"
           f"Mass = Density × Volume = {density} × {vol} = <strong>{mass} g</strong>")
    return q, sol, "V = 4πr³/3. Then mass = density × volume.", 4, mass


def _cm_i8_density_unit_conversion():
    combos = [(1.0,1000),(2.7,2700),(7.8,7800),(8.9,8900),(11.3,11300),(0.9,900)]
    d_gcm3, d_kgm3 = random.choice(combos)
    q = (f"A material has a density of {d_gcm3} g/cm³. "
         f"Express this density in kg/m³.")
    sol = (f"1 g/cm³ = 1000 kg/m³ &nbsp;(1 g = 0.001 kg; 1 cm³ = 10⁻⁶ m³)<br>"
           f"{d_gcm3} g/cm³ × 1000 = <strong>{d_kgm3} kg/m³</strong>")
    return q, sol, "Multiply by 1000 to convert g/cm³ → kg/m³.", 3, d_kgm3


def _cm_i9_average_speed_equal_distances():
    """Classic trap: equal distances at two different speeds."""
    combos = [(40,60,48),(30,60,40),(50,100,200/3),(60,90,72),(40,80,160/3)]
    s1, s2, avg = random.choice(combos)
    avg_val = 2 * s1 * s2 / (s1 + s2)
    wrong = (s1 + s2) / 2
    q = (f"A car travels from A to B at {s1} km/h, then returns from B to A at {s2} km/h. "
         f"Find the average speed for the whole journey.")
    sol = (f"Let distance A→B = d km.<br>"
           f"Time A→B = d/{s1}; Time B→A = d/{s2}<br>"
           f"Total distance = 2d; Total time = d/{s1} + d/{s2} = d({s1}+{s2})/({s1}×{s2})<br>"
           f"Average speed = 2d ÷ [d({s1}+{s2})/({s1}×{s2})] = 2×{s1}×{s2}/({s1}+{s2})<br>"
           f"= {2*s1*s2}/{s1+s2} = <strong>{_dp(avg_val)} km/h</strong><br>"
           f"(Caution: simply averaging gives {_dp(wrong)} km/h — this is WRONG.)")
    return q, sol, "Average speed = total distance ÷ total time. Do NOT average the two speeds.", 5, avg_val


def _cm_i10_sdt_ms_and_km():
    combos = [(20,60,1200,1.2),(15,120,1800,1.8),(25,30,750,0.75),(30,60,1800,1.8)]
    speed_ms, time_s, dist_m, dist_km = random.choice(combos)
    q = (f"A train travels at {speed_ms} m/s for {time_s} seconds. "
         f"Find the distance in (a) metres and (b) kilometres.")
    sol = (f"(a) Distance = {speed_ms} × {time_s} = <strong>{dist_m} m</strong><br>"
           f"(b) {dist_m} ÷ 1000 = <strong>{_dp(dist_km)} km</strong>")
    return q, sol, "D = S × T (in m and s → m). Then divide by 1000 to get km.", 3, _cm_fields_answer(
        (dist_m, dist_km), ("Distance (m)", "Distance (km)")
    )


def _cm_i11_population_density_area():
    combos = [(200,2000,10),(250,5000,20),(300,6000,20),
              (400,4000,10),(500,10000,20),(250,2500,10)]
    dens, pop, area = random.choice(combos)
    q = (f"A region has a population of {pop:,} people and a "
         f"population density of {dens} people/km². "
         f"Find the area of the region.")
    sol = (f"Area = Population ÷ Density<br>"
           f"= {pop:,} ÷ {dens}<br>"
           f"= <strong>{_dp(area)} km²</strong>")
    return q, sol, "Area = Population ÷ Population Density.", 3, area


def _cm_i12_pressure_unit_conversion():
    combos = [(500,25,20,200000),(800,40,20,200000),(1000,50,20,200000),(600,30,20,200000)]
    f_N, a_cm2, p_ncm2, p_Pa = random.choice(combos)
    a_m2 = a_cm2 / 10000
    q = (f"A force of {f_N} N acts on a surface area of {a_cm2} cm². "
         f"Find the pressure in (a) N/cm² and (b) Pa.")
    sol = (f"(a) Pressure = {f_N} ÷ {a_cm2} = <strong>{_dp(p_ncm2)} N/cm²</strong><br>"
           f"(b) 1 N/cm² = 10 000 Pa &nbsp;(since 1 cm² = 10⁻⁴ m²)<br>"
           f"Pressure = {_dp(p_ncm2)} × 10 000 = <strong>{p_Pa:,} Pa</strong>")
    return q, sol, "1 cm² = 10⁻⁴ m², so 1 N/cm² = 10 000 Pa.", 4, _cm_fields_answer(
        (p_ncm2, p_Pa), ("Pressure (N/cm²)", "Pressure (Pa)")
    )


def _cm_i13_floating_sinking():
    """Object density vs water (1 g/cm³) — float or sink?"""
    combos = [(80,120,True),(100,80,False),(60,100,True),(150,100,False),(90,150,True)]
    mass_g, vol_cm3, floats = random.choice(combos)
    density = round(mass_g / vol_cm3, 4)
    q = (f"An object has mass {mass_g} g and volume {vol_cm3} cm³. "
         f"The density of water is 1 g/cm³. "
         f"Will the object float or sink? Show your working.")
    sol = (f"Density = {mass_g} ÷ {vol_cm3} = {density} g/cm³<br>"
           f"Compare to water (1 g/cm³):<br>"
           f"{density} {'<' if floats else '>'} 1  →  the object will "
           f"<strong>{'float' if floats else 'sink'}</strong>.")
    return q, sol, "Density < 1 g/cm³ → floats; Density > 1 g/cm³ → sinks.", 3, _cm_keyword_answer(
        "float" if floats else "sink"
    )


def _cm_i14_speed_convert_then_distance():
    combos = [(10,54,10,1/6,9),(15,54,20,1/3,18),(20,72,15,1/4,18),(25,90,20,1/3,30)]
    speed_ms, speed_kmh, time_min, time_h, dist_km = random.choice(combos)
    q = (f"A runner's speed is {speed_ms} m/s. "
         f"(i) Convert this to km/h. "
         f"(ii) How far does the runner travel in {time_min} minutes? Give your answer in km.")
    sol = (f"(i) {speed_ms} m/s × 3.6 = <strong>{_dp(speed_kmh)} km/h</strong><br>"
           f"(ii) Time = {time_min} min = {time_min}/60 = {_dp(time_h)} hours<br>"
           f"Distance = {_dp(speed_kmh)} × {_dp(time_h)} = <strong>{_dp(dist_km)} km</strong>")
    return q, sol, "(i) Multiply m/s by 3.6. (ii) Convert minutes to hours before D = S × T.", 4, _cm_fields_answer(
        (speed_kmh, dist_km), ("Speed (km/h)", "Distance (km)")
    )


def _cm_i15_hollow_cylinder_mass():
    combos = [(5,2,10,2.7),(6,3,12,7.8),(8,4,15,2.7),(10,5,20,8.9)]
    R, r, h, density = random.choice(combos)
    vol = round(math.pi * (R ** 2 - r ** 2) * h, 1)
    mass = round(density * vol, 0)
    q = (f"A hollow cylinder (pipe) has outer radius {R} cm, inner radius {r} cm, "
         f"and height {h} cm. It is made of a material with density {density} g/cm³. "
         f"Find the mass of the cylinder.")
    sol = (f"Volume = π(R² − r²)h = π({R}² − {r}²) × {h} = π × {R**2-r**2} × {h} = {vol} cm³<br>"
           f"Mass = {density} × {vol} = <strong>{_dp(int(mass))} g</strong>")
    return q, sol, "Hollow volume = π(R²−r²)h. Then mass = density × volume.", 5, int(mass)


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _cm_d1_meeting_problem():
    combos = [(4,3,7,14,2,8),(5,3,8,24,3,15),(6,4,10,30,3,18),(5,5,10,30,3,15),(4,6,10,40,4,16)]
    s1, s2, rel, dist, time_h, meet = random.choice(combos)
    q = (f"A and B are {dist} km apart. Person P walks from A toward B at {s1} km/h. "
         f"At the same time, person Q walks from B toward A at {s2} km/h. "
         f"(i) After how many hours do they meet? "
         f"(ii) How far from A do they meet?")
    sol = (f"(i) They close the gap at combined speed {s1} + {s2} = {rel} km/h.<br>"
           f"Time = {dist} ÷ {rel} = <strong>{time_h} hours</strong><br>"
           f"(ii) Distance P travels = {s1} × {time_h} = <strong>{meet} km from A</strong>")
    return q, sol, "Relative speed towards each other = s1 + s2. Time = gap ÷ relative speed.", 5, _cm_fields_answer(
        (time_h, meet), ("Time (hours)", "Distance from A (km)")
    )


def _cm_d2_overtaking():
    combos = [(60,90,20,10,20),(70,100,30,7,14),(80,110,30,8,16),(60,100,30,9,18)]
    s_slow, s_fast, head_start_min, head_km, time_min = random.choice(combos)
    rel = s_fast - s_slow
    q = (f"Vehicle A travels at {s_slow} km/h. "
         f"Vehicle B leaves the same point {head_start_min} minutes later at {s_fast} km/h. "
         f"How long after B departs does B overtake A?")
    sol = (f"Head-start distance = {s_slow} × ({head_start_min}/60) = {head_km} km<br>"
           f"Closing speed = {s_fast} − {s_slow} = {rel} km/h<br>"
           f"Time = {head_km} ÷ {rel} = {_dp(head_km/rel)} h = <strong>{time_min} minutes</strong>")
    return q, sol, "Head-start distance = slow speed × head-start time. Then time = gap ÷ closing speed.", 5, time_min


def _cm_d3_alloy_percentage_density():
    combos = [(70,30,7.8,2.7),(80,20,7.8,2.7),(60,40,8.9,2.7),(75,25,11.3,2.7)]
    p_A, p_B, d_A, d_B = random.choice(combos)
    v_A = p_A / d_A
    v_B = p_B / d_B
    total_v = round(v_A + v_B, 6)
    density = round(100 / total_v, 3)
    q = (f"An alloy is {p_A}% metal A (density {d_A} g/cm³) and {p_B}% metal B "
         f"(density {d_B} g/cm³) by mass. "
         f"Find the density of the alloy to 3 significant figures.")
    sol = (f"Take 100 g of alloy as reference.<br>"
           f"Mass A = {p_A} g → Volume A = {p_A}/{d_A} = {round(v_A,4)} cm³<br>"
           f"Mass B = {p_B} g → Volume B = {p_B}/{d_B} = {round(v_B,4)} cm³<br>"
           f"Total volume = {round(v_A,4)} + {round(v_B,4)} = {total_v} cm³<br>"
           f"Density = 100 ÷ {total_v} = <strong>{density} g/cm³</strong>")
    return q, sol, "Use 100 g as the reference. Find volumes via density, sum them, divide 100 g by total volume.", 6, density


def _cm_d4_water_pressure():
    combos = [(3,1000,10,30000),(5,1000,10,50000),(10,1000,10,100000),(4,1000,10,40000)]
    depth_m, rho, g, pressure = random.choice(combos)
    q = (f"Water pressure at depth h metres is given by P = ρgh, "
         f"where ρ = 1000 kg/m³ and g = 10 N/kg. "
         f"Find the pressure at a depth of {depth_m} m, stating units.")
    sol = (f"P = ρgh = 1000 × 10 × {depth_m}<br>"
           f"= <strong>{pressure:,} Pa</strong> ({pressure//1000} kPa)")
    return q, sol, "Substitute into P = ρgh. Ensure SI units throughout → answer in Pa.", 4, pressure


def _cm_d5_algebraic_sdt():
    combos = [(120,2,3),(180,2,3),(240,3,4),(300,2,4)]
    d, f1, f2 = random.choice(combos)
    # Both halves: first d/2 at v, second d/2 at f2*v
    # Total time = (d/2)/v + (d/2)/(f2*v) = d/(2v)(1 + 1/f2) = d(f2+1)/(2f2*v)
    half = d // 2
    num = d * (f2 + 1)
    den_factor = 2 * f2
    q = (
        f"A journey of {d} km is split into two equal halves. "
        f"The first half is done at speed v km/h and the second half at {f2}v km/h. "
        f"Find the total journey time in terms of v by completing the steps below."
    )
    sol = (
        f"<strong>Formula:</strong> speed = distance ÷ time "
        f"(rearranged: time = distance ÷ speed).<br>"
        f"Time first half = ({d}/2)/v = {half}/v hours<br>"
        f"Time second half = ({d}/2)/({f2}v) = {half}/({f2}v) hours<br>"
        f"Total = {half}/v + {half}/({f2}v) = ({half}×{f2} + {half}) / ({f2}v)<br>"
        f"= <strong>{num}/({den_factor}v) hours</strong>"
    )
    return (
        q, sol,
        "Time = distance ÷ speed for each leg. Add fractions over a common denominator.",
        5,
        _cm_fields_answer(
            (
                f'{half}/v',
                f'{half}/({f2}*v)',
                f'{num}/({den_factor}*v)',
            ),
            (
                f'Step 1: time for the first {half} km (in terms of v)',
                f'Step 2: time for the second {half} km (in terms of v)',
                'Step 3: simplified total time',
            ),
            field_types=('algebraic', 'algebraic', 'algebraic'),
        ),
    )


def _cm_d6_two_pipes():
    combos = [(8,3,5,60,12),(10,4,6,60,10),(12,2,10,80,8),(6,2,4,80,20),(10,2,8,100,12)]
    r_fill, r_drain, net, vol, time_min = random.choice(combos)
    q = (f"A tank of {vol} litres has a fill pipe running at {r_fill} L/min "
         f"and a drain pipe at {r_drain} L/min, both open at the same time. "
         f"How long does it take to fill the empty tank?")
    sol = (f"Net fill rate = {r_fill} − {r_drain} = {net} L/min<br>"
           f"Time = {vol} ÷ {net} = <strong>{time_min} minutes</strong>")
    return q, sol, "Net rate = fill rate − drain rate. Time = volume ÷ net rate.", 4, time_min


def _cm_d7_harmonic_mean_prove():
    combos = [(30,60,40),(40,60,48),(50,100,200/3),(60,90,72)]
    s1, s2, avg = random.choice(combos)
    avg_val = 2 * s1 * s2 / (s1 + s2)
    avg_out = avg_val if avg_val != int(avg_val) else int(avg_val)
    q = (
        f"A car travels from X to Y at {s1} km/h and returns at {s2} km/h. "
        f"Let the distance XY be d km. Complete the steps to find the average speed "
        f"for the whole journey."
    )
    prod = s1 * s2
    total_s = s1 + s2
    num = 2 * s1 * s2
    sol = (
        f"<strong>Formulae</strong><br>"
        f"speed = distance ÷ time<br>"
        f"time = distance ÷ speed<br>"
        f"average speed = total distance ÷ total time<br><br>"
        f"<strong>Step 1 — total time (in terms of d)</strong><br>"
        f"Time X→Y = \\(\\dfrac{{d}}{{{s1}}}\\) hours<br>"
        f"Time Y→X = \\(\\dfrac{{d}}{{{s2}}}\\) hours<br>"
        f"Total time = \\(\\dfrac{{d}}{{{s1}}} + \\dfrac{{d}}{{{s2}}}\\)<br>"
        f"= \\(\\dfrac{{d({s1} + {s2})}}{{{s1} \\times {s2}}}\\) "
        f"= \\(\\dfrac{{{total_s}d}}{{{prod}}}\\) hours<br><br>"
        f"<strong>Step 2 — average-speed formula</strong><br>"
        f"Total distance for the round trip = 2d<br>"
        f"Average speed = \\(\\dfrac{{2d}}{{\\text{{total time}}}} "
        f"= \\dfrac{{2d}}{{\\dfrac{{{total_s}d}}{{{prod}}}}}\\)<br>"
        f"= \\(\\dfrac{{2 \\times {s1} \\times {s2}}}{{{s1} + {s2}}}\\)<br><br>"
        f"<strong>Step 3 — work out the value</strong><br>"
        f"= \\(\\dfrac{{{num}}}{{{total_s}}}\\) "
        f"= <strong>{_dp(avg_val)} km/h</strong>"
    )
    return (
        q, sol,
        "Write total time in terms of d, then average speed = 2d ÷ total time.",
        6,
        _cm_fields_answer(
            (
                f'd/{s1} + d/{s2}',
                f'2*{s1}*{s2}/({s1}+{s2})',
                avg_out,
            ),
            (
                'Step 1: total time for the round trip (in terms of d)',
                'Step 2: simplified average-speed formula',
                'Step 3: average speed (km/h)',
            ),
            field_types=('algebraic', 'algebraic', 'number'),
        ),
    )


def _cm_d8_density_kg_m3_use():
    combos = [(0.8,800,0.5,400),(2.7,2700,1.0,2700),(7.8,7800,0.5,3900),(1.0,1000,2.0,2000)]
    d_gcm3, d_kgm3, vol_m3, mass_kg = random.choice(combos)
    q = (f"A material has density {d_gcm3} g/cm³. "
         f"(i) Convert the density to kg/m³. "
         f"(ii) Find the mass in kg of {vol_m3} m³ of this material.")
    sol = (f"(i) {d_gcm3} g/cm³ × 1000 = <strong>{d_kgm3} kg/m³</strong><br>"
           f"(ii) Mass = {d_kgm3} × {vol_m3} = <strong>{_dp(mass_kg)} kg</strong>")
    return q, sol, "1 g/cm³ = 1000 kg/m³. Then mass (kg) = density (kg/m³) × volume (m³).", 5, _cm_fields_answer(
        (d_kgm3, mass_kg), ("Density (kg/m³)", "Mass (kg)")
    )


def _cm_d9_concentration():
    combos = [(30,1.0,30,500,15),(40,0.5,20,250,10),(20,2.0,40,500,10),(50,0.5,25,200,10)]
    conc, vol1, mass1, vol2_mL, mass2 = random.choice(combos)
    q = (f"A salt solution has concentration {conc} g/L. "
         f"(i) How many grams of salt are in {vol1} litre(s)? "
         f"(ii) How many grams are in {vol2_mL} mL?")
    sol = (f"(i) Mass = {conc} × {vol1} = <strong>{_dp(mass1)} g</strong><br>"
           f"(ii) {vol2_mL} mL = {vol2_mL}/1000 = {vol2_mL/1000} L<br>"
           f"Mass = {conc} × {vol2_mL/1000} = <strong>{_dp(mass2)} g</strong>")
    return q, sol, "Mass = concentration × volume. Convert mL to L first (divide by 1000).", 5, _cm_fields_answer(
        (mass1, mass2), ("Mass (g) in (i)", "Mass (g) in (ii)")
    )


def _cm_d10_relative_speed():
    combos = [(90,60,30,True,60,2),(100,70,30,True,45,1.5),(80,50,30,False,110,3),
              (90,50,40,False,130,2)]
    s1, s2, dist_km, same_dir, rel, t_min = random.choice(combos)
    if same_dir:
        rel = s1 - s2
        t_h = dist_km / rel
        t_min = round(t_h * 60)
    else:
        rel = s1 + s2
        t_h = dist_km / rel
        t_min = round(t_h * 60)
    direction_txt = "same" if same_dir else "opposite"
    action_txt = "catches" if same_dir else "meet"
    q = (f"Train A travels at {s1} km/h. Train B travels at {s2} km/h. "
         f"They start {dist_km} km apart, moving in the {direction_txt} direction. "
         f"How long before A {action_txt} B? Give your answer in minutes.")
    sol = (f"Relative speed = {s1} {'−' if same_dir else '+'} {s2} = {rel} km/h<br>"
           f"Time = {dist_km} ÷ {rel} = {_dp(dist_km/rel)} h = <strong>{t_min} minutes</strong>")
    return q, sol, "Same direction: relative speed = difference. Opposite: relative speed = sum.", 5, t_min


def _cm_d11_composite_density_ratio():
    combos = [(2,1,8.9,2.7),(3,1,7.8,0.9),(1,2,11.3,1.0),(2,3,8.9,0.9)]
    r1, r2, d1, d2 = random.choice(combos)
    v1, v2 = r1, r2
    m1, m2 = d1 * v1, d2 * v2
    total_m, total_v = m1 + m2, v1 + v2
    density_mix = round(total_m / total_v, 3)
    q = (f"A composite material is made from two substances in the volume ratio {r1}:{r2}. "
         f"Substance A has density {d1} g/cm³; Substance B has density {d2} g/cm³. "
         f"Find the density of the composite material.")
    sol = (f"Let volumes be {v1} cm³ and {v2} cm³ (using the ratio directly).<br>"
           f"Mass A = {d1} × {v1} = {m1} g;  Mass B = {d2} × {v2} = {m2} g<br>"
           f"Total mass = {m1+m2} g;  Total volume = {total_v} cm³<br>"
           f"Density = {total_m} ÷ {total_v} = <strong>{density_mix} g/cm³</strong>")
    return q, sol, "Use the ratio directly as volumes. Mass = density × volume for each. Then total M ÷ total V.", 5, density_mix


def _cm_d12_hydraulic_press():
    combos = [(20,4,100,500),(30,5,200,1200),(40,8,200,1000),(50,10,250,1250)]
    f_in, a_in, a_out, f_out = random.choice(combos)
    p = f_in / a_in
    q = (f"In a hydraulic press, an input force of {f_in} N is applied over area {a_in} cm². "
         f"The output piston has area {a_out} cm². "
         f"(i) Find the pressure transmitted through the fluid. "
         f"(ii) Find the output force.")
    sol = (f"(i) Pressure = {f_in} ÷ {a_in} = <strong>{_dp(p)} N/cm²</strong><br>"
           f"(ii) Pascal's Law: pressure is equal throughout the fluid.<br>"
           f"Output force = {_dp(p)} × {a_out} = <strong>{_dp(f_out)} N</strong>")
    return q, sol, "P = F/A at input. Pascal's Law: same P at output → F_out = P × A_out.", 5, _cm_fields_answer(
        (p, f_out), ("Pressure (N/cm²)", "Output force (N)")
    )


def _cm_d13_three_leg_average():
    combos = [(60,90,45,1,2,2,300,5,60),(80,60,40,2,1,3,400,6,400/6),
              (50,100,75,3,1,2,450,6,75),(60,80,40,1,2,3,380,6,380/6)]
    s1,s2,s3,t1,t2,t3,total_d,total_t,avg = random.choice(combos)
    avg_val = total_d / total_t
    d1, d2, d3 = s1*t1, s2*t2, s3*t3
    q = (f"A car travels {t1} hour{'s' if t1>1 else ''} at {s1} km/h, "
         f"then {t2} hour{'s' if t2>1 else ''} at {s2} km/h, "
         f"then {t3} hours at {s3} km/h. "
         f"Find the average speed for the whole journey.")
    sol = (f"Distances: {s1}×{t1}={d1}, {s2}×{t2}={d2}, {s3}×{t3}={d3} km<br>"
           f"Total distance = {d1}+{d2}+{d3} = {total_d} km<br>"
           f"Total time = {t1}+{t2}+{t3} = {total_t} h<br>"
           f"Average speed = {total_d} ÷ {total_t} = <strong>{_dp(avg_val)} km/h</strong>")
    return q, sol, "Compute each leg's distance. Average speed = total distance ÷ total time.", 5, avg_val


def _cm_d14_pressure_minimum_area():
    combos = [(500,2000,5000,0.25 * 5000/2000),(800,4000,8000,0.2),(1000,5000,10000,0.2),(1200,6000,12000,0.2)]
    mass_kg, max_pressure, weight, min_area = random.choice(combos)
    weight = mass_kg * 10
    min_area = weight / max_pressure
    q = (f"A crate has mass {mass_kg} kg. "
         f"The floor can withstand a maximum pressure of {max_pressure:,} Pa. "
         f"(i) Find the weight of the crate. (g = 10 N/kg) "
         f"(ii) Find the minimum base area the crate must have.")
    sol = (f"(i) Weight = {mass_kg} × 10 = <strong>{weight:,} N</strong><br>"
           f"(ii) Minimum area = Force ÷ Max Pressure = {weight:,} ÷ {max_pressure:,} = "
           f"<strong>{_dp(min_area)} m²</strong>")
    return q, sol, "Weight = mg. Minimum area = weight ÷ max pressure.", 5, _cm_fields_answer(
        (weight, min_area), ("Weight (N)", "Minimum area (m²)")
    )


def _cm_d15_mass_flow_rate():
    combos = [(3,2,1.0,18.85,1885.0),(4,1,0.9,50.27,45.24),(2,3,1.2,37.70,45.24)]
    r_cm, speed_ms, density_gcm3, area_cm2, mass_rate_gs = random.choice(combos)
    area = round(math.pi * r_cm ** 2, 2)
    speed_cm_s = speed_ms * 100
    vol_rate = round(area * speed_cm_s, 2)
    mass_rate = round(density_gcm3 * vol_rate, 2)
    q = (f"A fluid (density {density_gcm3} g/cm³) flows through a circular pipe of "
         f"radius {r_cm} cm at {speed_ms} m/s. "
         f"Find: (i) the cross-sectional area (cm²), "
         f"(ii) the volume flow rate (cm³/s), "
         f"(iii) the mass flow rate (g/s).")
    sol = (f"(i) Area = π × {r_cm}² = <strong>{area} cm²</strong><br>"
           f"(ii) Convert speed: {speed_ms} m/s = {speed_cm_s} cm/s<br>"
           f"Volume flow rate = {area} × {speed_cm_s} = <strong>{vol_rate} cm³/s</strong><br>"
           f"(iii) Mass flow rate = {density_gcm3} × {vol_rate} = <strong>{mass_rate} g/s</strong>")
    return q, sol, "Volume flow = area × speed. Mass flow = density × volume flow.", 6, _cm_fields_answer(
        (area, vol_rate, mass_rate),
        ("Area (cm²)", "Volume flow rate (cm³/s)", "Mass flow rate (g/s)"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ  (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_CM_MCQ_BANK = [
    {"q": "A car travels 150 km in 2.5 hours. What is its average speed?",
     "opts": ["A  60 km/h", "B  375 km/h", "C  147.5 km/h", "D  15 km/h"],
     "ans": "A", "marks": 1,
     "sol": "Speed = 150 ÷ 2.5 = <strong>60 km/h</strong>. Answer: A",
     "hint": "Speed = Distance ÷ Time."},

    {"q": "A train travels at 80 km/h for 3.5 hours. How far does it travel?",
     "opts": ["A  280 km", "B  22.9 km", "C  83.5 km", "D  240 km"],
     "ans": "A", "marks": 1,
     "sol": "Distance = 80 × 3.5 = <strong>280 km</strong>. Answer: A",
     "hint": "Distance = Speed × Time."},

    {"q": "A cyclist travels 240 km at 60 km/h. How long does this take?",
     "opts": ["A  4 hours", "B  14,400 hours", "C  6 hours", "D  3 hours"],
     "ans": "A", "marks": 1,
     "sol": "Time = 240 ÷ 60 = <strong>4 hours</strong>. Answer: A",
     "hint": "Time = Distance ÷ Speed."},

    {"q": "A metal block has mass 560 g and volume 80 cm³. Find its density.",
     "opts": ["A  7 g/cm³", "B  480 g/cm³", "C  0.14 g/cm³", "D  44,800 g/cm³"],
     "ans": "A", "marks": 1,
     "sol": "Density = 560 ÷ 80 = <strong>7 g/cm³</strong>. Answer: A",
     "hint": "Density = Mass ÷ Volume."},

    {"q": "A material has density 8.9 g/cm³. What is the mass of 100 cm³?",
     "opts": ["A  890 g", "B  8.9 g", "C  0.089 g", "D  891 g"],
     "ans": "A", "marks": 1,
     "sol": "Mass = 8.9 × 100 = <strong>890 g</strong>. Answer: A",
     "hint": "Mass = Density × Volume."},

    {"q": "Convert 72 km/h to m/s.",
     "opts": ["A  20 m/s", "B  259.2 m/s", "C  25.9 m/s", "D  0.02 m/s"],
     "ans": "A", "marks": 2,
     "sol": "72 × 5/18 = 72000/3600 = <strong>20 m/s</strong>. Answer: A",
     "hint": "km/h → m/s: multiply by 5/18 (or divide by 3.6)."},

    {"q": "Convert 15 m/s to km/h.",
     "opts": ["A  54 km/h", "B  4.17 km/h", "C  150 km/h", "D  5.4 km/h"],
     "ans": "A", "marks": 2,
     "sol": "15 × 3.6 = <strong>54 km/h</strong>. Answer: A",
     "hint": "m/s → km/h: multiply by 3.6."},

    {"q": "A force of 600 N acts on an area of 30 m². What is the pressure?",
     "opts": ["A  20 Pa", "B  18,000 Pa", "C  630 Pa", "D  570 Pa"],
     "ans": "A", "marks": 1,
     "sol": "Pressure = 600 ÷ 30 = <strong>20 Pa</strong>. Answer: A",
     "hint": "Pressure = Force ÷ Area."},

    {"q": "A car goes from A to B at 40 km/h and returns at 60 km/h. What is the average speed?",
     "opts": ["A  48 km/h", "B  50 km/h", "C  52 km/h", "D  45 km/h"],
     "ans": "A", "marks": 3,
     "sol": "2×40×60/(40+60) = 4800/100 = <strong>48 km/h</strong>. Answer: A",
     "hint": "Average speed ≠ mean of speeds; use total distance ÷ total time."},

    {"q": "An object has mass 80 g and volume 120 cm³. Water density = 1 g/cm³. Does it float?",
     "opts": ["A  Yes — density < 1 g/cm³", "B  No — density > 1 g/cm³",
              "C  Exactly on the surface", "D  Cannot be determined"],
     "ans": "A", "marks": 2,
     "sol": "Density = 80/120 = 0.667 g/cm³ < 1 → <strong>floats</strong>. Answer: A",
     "hint": "Object floats if density < density of liquid."},

    {"q": "A town has 24,000 people in 40 km². Find the population density.",
     "opts": ["A  600 people/km²", "B  960,000 people/km²",
              "C  60 people/km²", "D  6000 people/km²"],
     "ans": "A", "marks": 1,
     "sol": "24,000 ÷ 40 = <strong>600 people/km²</strong>. Answer: A",
     "hint": "Population density = population ÷ area."},

    {"q": "A material has density 2.7 g/cm³. Express this in kg/m³.",
     "opts": ["A  2700 kg/m³", "B  0.0027 kg/m³", "C  27 kg/m³", "D  270 kg/m³"],
     "ans": "A", "marks": 2,
     "sol": "1 g/cm³ = 1000 kg/m³ → 2.7 × 1000 = <strong>2700 kg/m³</strong>. Answer: A",
     "hint": "Multiply by 1000 to convert g/cm³ → kg/m³."},

    {"q": "A tap flows at 5 L/min. How many litres flow in 20 minutes?",
     "opts": ["A  100 litres", "B  4 litres", "C  25 litres", "D  0.25 litres"],
     "ans": "A", "marks": 1,
     "sol": "Volume = 5 × 20 = <strong>100 litres</strong>. Answer: A",
     "hint": "Volume = Flow Rate × Time."},

    {"q": "A force of 500 N acts on 25 cm². Find the pressure in N/cm².",
     "opts": ["A  20 N/cm²", "B  12,500 N/cm²", "C  475 N/cm²", "D  2 N/cm²"],
     "ans": "A", "marks": 2,
     "sol": "Pressure = 500 ÷ 25 = <strong>20 N/cm²</strong>. Answer: A",
     "hint": "Pressure = Force ÷ Area (keep area in cm² here)."},

    {"q": "A car: 120 km in 2 h, then 90 km in 1 h, then 90 km in 3 h. Average speed?",
     "opts": ["A  50 km/h", "B  60 km/h", "C  100 km/h", "D  45 km/h"],
     "ans": "A", "marks": 3,
     "sol": "Total d = 300 km; total t = 6 h. Average = 300/6 = <strong>50 km/h</strong>. Answer: A",
     "hint": "Average speed = total distance ÷ total time."},
]


def compound_measures_mcq():
    item = random.choice(_CM_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_compound_measures_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _CM_MCQ_BANK, procedural_mcq_for('compound_measures'), 'compound_measures', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _cm_f1_sdt_find_speed,   _cm_f2_sdt_find_distance, _cm_f3_sdt_find_time,
            _cm_f4_dmv_find_density, _cm_f5_dmv_find_mass,     _cm_f6_dmv_find_volume,
            _cm_f7_pfa_find_pressure,_cm_f8_pfa_find_force,    _cm_f9_pfa_find_area,
            _cm_f10_convert_kmh_to_ms,_cm_f11_convert_ms_to_kmh,
            _cm_f12_population_density_find, _cm_f13_population_find_pop,
            _cm_f14_flow_rate_volume, _cm_f15_density_compare,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _cm_i1_average_speed_two_legs,  _cm_i2_time_hours_minutes,
            _cm_i3_alloy_density_by_vol,    _cm_i4_pfa_box_weight,
            _cm_i5_sdt_time_in_minutes,     _cm_i6_flow_rate_fill_tank,
            _cm_i7_density_sphere,          _cm_i8_density_unit_conversion,
            _cm_i9_average_speed_equal_distances, _cm_i10_sdt_ms_and_km,
            _cm_i11_population_density_area,_cm_i12_pressure_unit_conversion,
            _cm_i13_floating_sinking,       _cm_i14_speed_convert_then_distance,
            _cm_i15_hollow_cylinder_mass,
        ]
    elif difficulty == 'difficult':
        pool = [
            _cm_d1_meeting_problem,       _cm_d2_overtaking,
            _cm_d3_alloy_percentage_density, _cm_d4_water_pressure,
            _cm_d5_algebraic_sdt,         _cm_d6_two_pipes,
            _cm_d7_harmonic_mean_prove,   _cm_d8_density_kg_m3_use,
            _cm_d9_concentration,         _cm_d10_relative_speed,
            _cm_d11_composite_density_ratio, _cm_d12_hydraulic_press,
            _cm_d13_three_leg_average,    _cm_d14_pressure_minimum_area,
            _cm_d15_mass_flow_rate,
        ]
    else:  # mixed
        f = random.sample([_cm_f1_sdt_find_speed, _cm_f4_dmv_find_density,
                           _cm_f7_pfa_find_pressure, _cm_f10_convert_kmh_to_ms,
                           _cm_f12_population_density_find], 4)
        i = random.sample([_cm_i1_average_speed_two_legs, _cm_i3_alloy_density_by_vol,
                           _cm_i9_average_speed_equal_distances, _cm_i12_pressure_unit_conversion,
                           _cm_i13_floating_sinking], 4)
        d = random.sample([_cm_d1_meeting_problem, _cm_d3_alloy_percentage_density,
                           _cm_d7_harmonic_mean_prove, _cm_d12_hydraulic_press], 2)
        return f + i + d

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_compound_measures(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_compound_measures_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'compound_measures',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_compound_measures_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    out = variant()
    return _cm_problem_from_output(out, difficulty)
