"""
GCSE Maths – Similarity and Congruence
15 foundational · 15 intermediate · 15 difficult · 15 MCQ

Covers:
  Congruence: SSS, SAS, ASA/AAS, RHS
  Similar shapes: scale factor, ratio
  Similar triangles: AA condition, formal proofs
  Linear / area / volume scale factors (LSF, ASF, VSF)
  Similar triangles from parallel lines (Basic Proportionality Theorem)
  Real-world applications: maps, scale models, shadow problems
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
# SVG helpers
# ─────────────────────────────────────────────────────────────────────────────

def _tri(A, B, C, vlabels=("A", "B", "C"), slabels=None,
         color="#1a6fa8", shade="#dbeafe", w=210, h=175):
    """Draw a single labeled triangle."""
    cx = (A[0]+B[0]+C[0])/3
    cy = (A[1]+B[1]+C[1])/3

    def out(px, py, d=20):
        dx, dy = px - cx, py - cy
        n = math.hypot(dx, dy) or 1
        return px + dx/n*d, py + dy/n*d

    svg = (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;'
        f'display:inline-block;margin:4px;vertical-align:middle;">'
        f'<polygon points="{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]}" '
        f'fill="{shade}" stroke="{color}" stroke-width="2"/>'
    )
    for pt, lbl in zip([A, B, C], vlabels):
        lx, ly = out(*pt)
        svg += (f'<text x="{lx:.0f}" y="{ly+5:.0f}" font-size="13" fill="#333" '
                f'text-anchor="middle" font-weight="bold">{lbl}</text>')
    if slabels:
        mids = [((B[0]+C[0])/2, (B[1]+C[1])/2),
                ((A[0]+C[0])/2, (A[1]+C[1])/2),
                ((A[0]+B[0])/2, (A[1]+B[1])/2)]
        for (mx, my), lbl in zip(mids, slabels):
            if lbl:
                dx, dy = mx-cx, my-cy
                n = math.hypot(dx, dy) or 1
                ox, oy = mx+dx/n*14, my+dy/n*14
                svg += (f'<text x="{ox:.0f}" y="{oy+4:.0f}" font-size="12" fill="#555" '
                        f'text-anchor="middle">{lbl}</text>')
    svg += '</svg>'
    return svg


def _two_tris(A1, B1, C1, A2, B2, C2,
              vl1=("A", "B", "C"), vl2=("P", "Q", "R"),
              sl1=None, sl2=None,
              c1="#1a6fa8", c2="#a13544", s1="#dbeafe", s2="#fce7f3",
              w=390, h=175):
    """Draw two similar triangles side by side with a ~ sign."""
    cx1 = (A1[0]+B1[0]+C1[0])/3
    cy1 = (A1[1]+B1[1]+C1[1])/3
    cx2 = (A2[0]+B2[0]+C2[0])/3
    cy2 = (A2[1]+B2[1]+C2[1])/3

    def out1(px, py, d=18):
        dx, dy = px-cx1, py-cy1
        n = math.hypot(dx, dy) or 1
        return px+dx/n*d, py+dy/n*d

    def out2(px, py, d=18):
        dx, dy = px-cx2, py-cy2
        n = math.hypot(dx, dy) or 1
        return px+dx/n*d, py+dy/n*d

    svg = (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;'
        f'display:inline-block;margin:4px;vertical-align:middle;">'
        f'<polygon points="{A1[0]},{A1[1]} {B1[0]},{B1[1]} {C1[0]},{C1[1]}" '
        f'fill="{s1}" stroke="{c1}" stroke-width="2"/>'
    )
    for pt, lbl in zip([A1, B1, C1], vl1):
        lx, ly = out1(*pt)
        svg += f'<text x="{lx:.0f}" y="{ly+5:.0f}" font-size="13" fill="#333" text-anchor="middle" font-weight="bold">{lbl}</text>'
    if sl1:
        m1 = [((B1[0]+C1[0])/2,(B1[1]+C1[1])/2),
              ((A1[0]+C1[0])/2,(A1[1]+C1[1])/2),
              ((A1[0]+B1[0])/2,(A1[1]+B1[1])/2)]
        for (mx,my),lbl in zip(m1,sl1):
            if lbl:
                dx,dy=mx-cx1,my-cy1; n=math.hypot(dx,dy) or 1
                ox,oy=mx+dx/n*13, my+dy/n*13
                svg += f'<text x="{ox:.0f}" y="{oy+4:.0f}" font-size="11" fill="#555" text-anchor="middle">{lbl}</text>'

    svg += (f'<polygon points="{A2[0]},{A2[1]} {B2[0]},{B2[1]} {C2[0]},{C2[1]}" '
            f'fill="{s2}" stroke="{c2}" stroke-width="2"/>')
    for pt, lbl in zip([A2, B2, C2], vl2):
        lx, ly = out2(*pt)
        svg += f'<text x="{lx:.0f}" y="{ly+5:.0f}" font-size="13" fill="#333" text-anchor="middle" font-weight="bold">{lbl}</text>'
    if sl2:
        m2 = [((B2[0]+C2[0])/2,(B2[1]+C2[1])/2),
              ((A2[0]+C2[0])/2,(A2[1]+C2[1])/2),
              ((A2[0]+B2[0])/2,(A2[1]+B2[1])/2)]
        for (mx,my),lbl in zip(m2,sl2):
            if lbl:
                dx,dy=mx-cx2,my-cy2; n=math.hypot(dx,dy) or 1
                ox,oy=mx+dx/n*13, my+dy/n*13
                svg += f'<text x="{ox:.0f}" y="{oy+4:.0f}" font-size="11" fill="#555" text-anchor="middle">{lbl}</text>'

    # Tilde between the two triangles
    gap_x = (min(A2[0],B2[0],C2[0]) + max(A1[0],B1[0],C1[0])) // 2
    svg += f'<text x="{gap_x}" y="{h//2+5}" font-size="22" fill="#555" text-anchor="middle">~</text>'
    svg += '</svg>'
    return svg


def _par_tri(AD_lbl, DB_lbl, DE_lbl, BC_lbl, ratio=0.45, w=210, h=175):
    """Triangle ABC with DE ∥ BC. Labels the four segments."""
    A = (105, 15)
    B = (25, 158)
    C = (185, 158)
    D = (A[0]+ratio*(B[0]-A[0]), A[1]+ratio*(B[1]-A[1]))
    E = (A[0]+ratio*(C[0]-A[0]), A[1]+ratio*(C[1]-A[1]))

    mid_AD = ((A[0]+D[0])/2, (A[1]+D[1])/2)
    mid_DB = ((D[0]+B[0])/2, (D[1]+B[1])/2)
    mid_DE = ((D[0]+E[0])/2, (D[1]+E[1])/2)
    mid_BC = ((B[0]+C[0])/2, (B[1]+C[1])/2)

    svg = (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'style="background:#f9f8f5;border-radius:6px;max-width:100%;'
        f'display:inline-block;margin:4px;vertical-align:middle;">'
        f'<polygon points="{A[0]},{A[1]} {B[0]},{B[1]} {C[0]},{C[1]}" '
        f'fill="#e0f2fe" stroke="#1a6fa8" stroke-width="2"/>'
        f'<polygon points="{A[0]},{A[1]} {D[0]:.1f},{D[1]:.1f} {E[0]:.1f},{E[1]:.1f}" '
        f'fill="#bfdbfe" stroke="#1a6fa8" stroke-width="1.5"/>'
        f'<line x1="{D[0]:.1f}" y1="{D[1]:.1f}" x2="{E[0]:.1f}" y2="{E[1]:.1f}" '
        f'stroke="#a13544" stroke-width="2.5"/>'
        f'<text x="{A[0]}" y="10" font-size="13" fill="#333" text-anchor="middle" font-weight="bold">A</text>'
        f'<text x="{B[0]-12}" y="{B[1]+7}" font-size="13" fill="#333" font-weight="bold">B</text>'
        f'<text x="{C[0]+12}" y="{C[1]+7}" font-size="13" fill="#333" font-weight="bold">C</text>'
        f'<text x="{D[0]-15:.0f}" y="{D[1]+4:.0f}" font-size="12" fill="#333">D</text>'
        f'<text x="{E[0]+15:.0f}" y="{E[1]+4:.0f}" font-size="12" fill="#333">E</text>'
        f'<text x="{mid_AD[0]-16:.0f}" y="{mid_AD[1]+4:.0f}" font-size="11" fill="#1a6fa8" text-anchor="middle">{AD_lbl}</text>'
        f'<text x="{mid_DB[0]-16:.0f}" y="{mid_DB[1]+4:.0f}" font-size="11" fill="#1a6fa8" text-anchor="middle">{DB_lbl}</text>'
        f'<text x="{mid_DE[0]:.0f}" y="{mid_DE[1]-8:.0f}" font-size="11" fill="#a13544" text-anchor="middle">{DE_lbl}</text>'
        f'<text x="{mid_BC[0]:.0f}" y="{mid_BC[1]+16:.0f}" font-size="11" fill="#1a6fa8" text-anchor="middle">{BC_lbl}</text>'
        f'</svg>'
    )
    return svg


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _sc_f1_congruence_sss():
    combos = [(5, 7, 9), (6, 8, 10), (4, 6, 9), (3, 7, 8), (5, 9, 11)]
    a, b, c = random.choice(combos)
    T1, T2 = random.choice([("ABC", "DEF"), ("PQR", "XYZ"), ("ABC", "PQR")])
    svg = _two_tris((25,140),(95,20),(165,140),(220,140),(290,20),(360,140),
                    vl1=(T1[0],T1[1],T1[2]), vl2=(T2[0],T2[1],T2[2]),
                    sl1=(f"{b} cm",f"{c} cm",f"{a} cm"), sl2=(f"{b} cm",f"{c} cm",f"{a} cm"))
    q = (f"Triangle {T1} has sides {a} cm, {b} cm and {c} cm. "
         f"Triangle {T2} has sides {a} cm, {b} cm and {c} cm.<br>{svg}<br>"
         f"State why {T1} ≅ {T2} and name the congruence condition.")
    s = (f"All three pairs of corresponding sides are equal:<br>"
         f"{T1[0]}{T1[1]} = {T2[0]}{T2[1]} = {a} cm, &ensp;"
         f"{T1[1]}{T1[2]} = {T2[1]}{T2[2]} = {b} cm, &ensp;"
         f"{T1[0]}{T1[2]} = {T2[0]}{T2[2]} = {c} cm.<br>"
         f"The triangles are congruent by <strong>SSS (Side-Side-Side)</strong>.")
    return q, s, "If all three corresponding sides are equal, the condition is SSS.", 2


def _sc_f2_congruence_sas():
    angle = random.choice([35, 42, 50, 58, 65, 72])
    a = random.choice([5, 6, 7, 8, 9])
    b = random.choice([8, 9, 10, 11, 12])
    T1, T2 = random.choice([("ABC", "PQR"), ("XYZ", "DEF")])
    q = (f"In triangles {T1} and {T2}: "
         f"{T1[0]}{T1[1]} = {T2[0]}{T2[1]} = {a} cm, "
         f"{T1[0]}{T1[2]} = {T2[0]}{T2[2]} = {b} cm, "
         f"and angle {T1[0]} = angle {T2[0]} = {angle}°. "
         f"State the congruence condition.")
    s = (f"Two sides and the <em>included</em> angle are equal: "
         f"{T1[0]}{T1[1]} = {T2[0]}{T2[1]}, angle {T1[0]} = angle {T2[0]}, {T1[0]}{T1[2]} = {T2[0]}{T2[2]}.<br>"
         f"The triangles are congruent by <strong>SAS (Side-Angle-Side)</strong>.")
    return q, s, "The angle must be the included angle — between the two given sides.", 2


def _sc_f3_congruence_asa():
    ang1 = random.choice([35, 40, 45, 50, 55])
    ang2 = random.choice([60, 65, 70, 75, 80])
    side = random.choice([5, 6, 7, 8, 9])
    T1, T2 = random.choice([("ABC", "PQR"), ("XYZ", "DEF")])
    q = (f"In triangles {T1} and {T2}: "
         f"angle {T1[0]} = angle {T2[0]} = {ang1}°, "
         f"{T1[0]}{T1[1]} = {T2[0]}{T2[1]} = {side} cm, "
         f"angle {T1[1]} = angle {T2[1]} = {ang2}°. "
         f"State the congruence condition.")
    s = (f"Two angles and the included side are equal: "
         f"angle {T1[0]} = angle {T2[0]}, {T1[0]}{T1[1]} = {T2[0]}{T2[1]}, angle {T1[1]} = angle {T2[1]}.<br>"
         f"The triangles are congruent by <strong>ASA (Angle-Side-Angle)</strong>.")
    return q, s, "The side must be the included side — between the two given angles.", 2


def _sc_f4_congruence_rhs():
    hyp = random.choice([10, 13, 15, 17, 20])
    leg = random.choice([5, 6, 8, 9, 12])
    while leg >= hyp:
        leg = random.choice([5, 6, 8, 9, 12])
    T1, T2 = random.choice([("ABC", "PQR"), ("XYZ", "DEF")])
    q = (f"Triangle {T1} has a right angle at {T1[2]}, hypotenuse {T1[0]}{T1[1]} = {hyp} cm, "
         f"and {T1[0]}{T1[2]} = {leg} cm. "
         f"Triangle {T2} has a right angle at {T2[2]}, hypotenuse {T2[0]}{T2[1]} = {hyp} cm, "
         f"and {T2[0]}{T2[2]} = {leg} cm. "
         f"State the congruence condition.")
    s = (f"Both triangles are right-angled (angle {T1[2]} = angle {T2[2]} = 90°), "
         f"with equal hypotenuses and an equal side.<br>"
         f"The triangles are congruent by <strong>RHS (Right angle – Hypotenuse – Side)</strong>.")
    return q, s, "RHS only applies to right-angled triangles: equal hypotenuse + one other equal side.", 2


def _sc_f5_scale_factor():
    combos = [(4, 6, "3/2"), (3, 9, "3"), (5, 10, "2"), (8, 12, "3/2"), (6, 15, "5/2")]
    small, large, sf_str = random.choice(combos)
    sf_dec = large / small
    q = (f"Two similar triangles have a pair of corresponding sides of length {small} cm and {large} cm. "
         f"Find the scale factor from the smaller to the larger triangle.")
    s = (f"Scale factor = larger ÷ smaller<br>"
         f"= {large} ÷ {small}<br>"
         f"= <strong>{sf_str}</strong> (= {sf_dec})")
    return q, s, "Scale factor = corresponding side of larger ÷ corresponding side of smaller.", 2


def _sc_f6_missing_side_from_sf():
    combos = [(2, 5, 10), (3, 4, 12), (1.5, 6, 9), (2.5, 4, 10), (4, 3, 12)]
    sf, small_side, large_side = random.choice(combos)
    q = (f"Two similar shapes have a linear scale factor of {sf} (smaller to larger). "
         f"A side of the smaller shape is {small_side} cm. "
         f"Find the corresponding side of the larger shape.")
    s = (f"Corresponding side = {small_side} × scale factor<br>"
         f"= {small_side} × {sf}<br>"
         f"= <strong>{large_side} cm</strong>")
    return q, s, "Multiply the known side by the scale factor.", 2


def _sc_f7_similar_triangles_sides():
    combos = [
        # (AB, BC, CA, PQ, QR, RP, note)
        (5, 12, 13, 10, 24, 26, "ABC", "PQR", 2),
        (3, 4, 5, 9, 12, 15, "ABC", "XYZ", 3),
        (6, 8, 10, 9, 12, 15, "PQR", "DEF", 1.5),
    ]
    AB, BC, CA, PQ, QR, RP, T1, T2, sf = random.choice(combos)
    svg = _two_tris(
        (20,140),(80,20),(160,140), (220,140),(295,20),(390,140),
        vl1=(T1[0],T1[1],T1[2]), vl2=(T2[0],T2[1],T2[2]),
        sl1=(f"{BC}",f"{CA}",f"{AB}"), sl2=(f"?",f"?",f"{PQ}"),
    )
    q = (f"Triangle {T1} is similar to triangle {T2} ({T1[0]} corresponds to {T2[0]}, etc.).<br>"
         f"{T1[0]}{T1[1]} = {AB} cm, {T1[1]}{T1[2]} = {BC} cm, {T1[0]}{T1[2]} = {CA} cm. "
         f"{T2[0]}{T2[1]} = {PQ} cm.<br>{svg}<br>"
         f"Find {T2[1]}{T2[2]} and {T2[0]}{T2[2]}.")
    s = (f"Scale factor = {T2[0]}{T2[1]} ÷ {T1[0]}{T1[1]} = {PQ} ÷ {AB} = {sf}<br>"
         f"{T2[1]}{T2[2]} = {sf} × {BC} = <strong>{QR} cm</strong><br>"
         f"{T2[0]}{T2[2]} = {sf} × {CA} = <strong>{RP} cm</strong>")
    return q, s, "Find the scale factor first using the given corresponding pair, then multiply each side.", 3


def _sc_f8_angles_similar():
    ang1 = random.choice([40, 45, 50, 55, 60])
    ang2 = random.choice([60, 65, 70, 75, 80])
    ang3 = 180 - ang1 - ang2
    q = (f"Triangle ABC is similar to triangle PQR (A corresponds to P, B to Q, C to R). "
         f"Angle A = {ang1}°, angle B = {ang2}°. "
         f"Find angle C, angle P, angle Q, and angle R.")
    s = (f"Angle C = 180° − {ang1}° − {ang2}° = <strong>{ang3}°</strong><br>"
         f"Corresponding angles in similar triangles are equal:<br>"
         f"Angle P = Angle A = <strong>{ang1}°</strong><br>"
         f"Angle Q = Angle B = <strong>{ang2}°</strong><br>"
         f"Angle R = Angle C = <strong>{ang3}°</strong>")
    return q, s, "Corresponding angles in similar triangles are always equal.", 3


def _sc_f9_area_ratio_from_lsf():
    combos = [(2, 4), (3, 9), (4, 16), (5, 25), (1.5, 2.25)]
    sf, asf = random.choice(combos)
    area_s = random.choice([8, 12, 15, 20, 24])
    area_l = area_s * asf
    q = (f"Two similar shapes have a linear scale factor of {sf}. "
         f"The smaller shape has area {area_s} cm². "
         f"Find the area of the larger shape.")
    s = (f"Area scale factor = LSF² = {sf}² = {asf}<br>"
         f"Larger area = {area_s} × {asf} = <strong>{area_l} cm²</strong>")
    return q, s, "Area scale factor = (linear scale factor)². Multiply the known area by ASF.", 3


def _sc_f10_lsf_from_area():
    combos = [(4, 9, "2:3", "2/3"), (9, 25, "3:5", "3/5"), (16, 49, "4:7", "4/7"),
              (1, 4, "1:2", "1/2"), (25, 100, "1:2", "1/2")]
    a1, a2, ratio_str, sf_str = random.choice(combos)
    import math as _m
    lsf = _m.sqrt(a1/a2)
    q = (f"Two similar shapes have areas {a1} cm² and {a2} cm². "
         f"Find the linear scale factor from the smaller to the larger shape.")
    s = (f"Area scale factor = {a2}/{a1} = {a2//a1 if a2 % a1 == 0 else a2/a1}<br>"
         f"Linear scale factor = √(area ratio) = √({a1}/{a2}) = √{a1}/√{a2}<br>"
         f"= <strong>{ratio_str}</strong>")
    return q, s, "LSF = √(area scale factor). Take the square root of the ratio of areas.", 3


def _sc_f11_volume_ratio_from_lsf():
    combos = [(2, 8), (3, 27), (4, 64), (5, 125)]
    sf, vsf = random.choice(combos)
    vol_s = random.choice([5, 8, 10, 12, 15])
    vol_l = vol_s * vsf
    q = (f"Two similar solids have a linear scale factor of {sf}. "
         f"The smaller solid has volume {vol_s} cm³. "
         f"Find the volume of the larger solid.")
    s = (f"Volume scale factor = LSF³ = {sf}³ = {vsf}<br>"
         f"Larger volume = {vol_s} × {vsf} = <strong>{vol_l} cm³</strong>")
    return q, s, "Volume scale factor = (linear scale factor)³. Multiply the known volume by VSF.", 3


def _sc_f12_similar_rectangles():
    combos = [(6, 4, 9, 6, 1.5), (8, 5, 16, 10, 2), (10, 6, 15, 9, 1.5), (4, 3, 12, 9, 3)]
    AB, BC, PQ, QR, sf = random.choice(combos)
    q = (f"Rectangle ABCD is similar to rectangle PQRS "
         f"(AB corresponds to PQ, BC to QR). "
         f"AB = {AB} cm, BC = {BC} cm, PQ = {PQ} cm. "
         f"Find QR.")
    s = (f"Scale factor = PQ ÷ AB = {PQ} ÷ {AB} = {sf}<br>"
         f"QR = BC × {sf} = {BC} × {sf} = <strong>{QR} cm</strong>")
    return q, s, "Find the scale factor from the given corresponding pair, then apply to BC.", 3


def _sc_f13_perimeter_ratio():
    combos = [(2, 18, 36), (3, 14, 42), (4, 12, 48), (1.5, 20, 30), (2.5, 16, 40)]
    sf, p_small, p_large = random.choice(combos)
    q = (f"Two similar shapes have a scale factor of {sf}. "
         f"The perimeter of the smaller shape is {p_small} cm. "
         f"Find the perimeter of the larger shape.")
    s = (f"Perimeter scales with the linear scale factor.<br>"
         f"Larger perimeter = {p_small} × {sf} = <strong>{p_large} cm</strong>")
    return q, s, "Perimeters (and all lengths) scale with the linear scale factor — NOT its square.", 2


def _sc_f14_map_scale():
    combos = [
        (50000, 4, 200000, 2.0, "km"),
        (25000, 6, 150000, 1.5, "km"),
        (10000, 8, 80000, 0.8, "km"),
        (200000, 3, 600000, 6.0, "km"),
    ]
    scale, map_cm, actual_cm, actual_km, unit = random.choice(combos)
    q = (f"A map has a scale of 1 : {scale:,}. "
         f"A road measures {map_cm} cm on the map. "
         f"Find the actual length of the road, giving your answer in {unit}.")
    s = (f"Actual distance = {map_cm} × {scale:,} cm<br>"
         f"= {actual_cm:,} cm<br>"
         f"= {actual_cm:,} ÷ 100 000 km<br>"
         f"= <strong>{actual_km} km</strong>")
    return q, s, "Multiply map distance by scale factor. Then convert cm to km (÷ 100 000).", 3


def _sc_f15_area_of_smaller():
    combos = [(3, 9, 180, 20), (2, 4, 100, 25), (4, 16, 400, 25), (5, 25, 500, 20)]
    sf, asf, area_large, area_small = random.choice(combos)
    q = (f"Two similar shapes have a scale factor of {sf} (smaller to larger). "
         f"The larger shape has area {area_large} cm². "
         f"Find the area of the smaller shape.")
    s = (f"Area scale factor = {sf}² = {asf}<br>"
         f"Smaller area = {area_large} ÷ {asf} = <strong>{area_small} cm²</strong>")
    return q, s, "Divide the known area by the area scale factor (LSF²) to find the smaller area.", 3


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _sc_i1_aa_similarity_find_side():
    combos = [
        (55, 70, 8, 12, 9, 13.5, "ABC", "PQR"),
        (40, 80, 6, 9, 8, 12, "XYZ", "DEF"),
        (60, 50, 10, 15, 12, 18, "ABC", "PQR"),
    ]
    a1, a2, AB, PQ, BC, QR, T1, T2 = random.choice(combos)
    sf = PQ / AB
    q = (f"In triangles {T1} and {T2}: angle {T1[0]} = angle {T2[0]} = {a1}°, "
         f"angle {T1[1]} = angle {T2[1]} = {a2}°. "
         f"{T1[0]}{T1[1]} = {AB} cm, {T2[0]}{T2[1]} = {PQ} cm, {T1[1]}{T1[2]} = {BC} cm. "
         f"Find {T2[1]}{T2[2]}.")
    s = (f"Since angle {T1[0]} = angle {T2[0]} and angle {T1[1]} = angle {T2[1]}, "
         f"triangle {T1} ~ triangle {T2} by AA.<br>"
         f"Scale factor = {T2[0]}{T2[1]} ÷ {T1[0]}{T1[1]} = {PQ} ÷ {AB} = {sf}<br>"
         f"{T2[1]}{T2[2]} = {sf} × {BC} = <strong>{QR} cm</strong>")
    return q, s, "State AA similarity first, then find the scale factor and multiply.", 4


def _sc_i2_parallel_lines_find_bc():
    combos = [
        (3, 6, 5, 15, 0.333, "3 cm", "6 cm", "5 cm", "?"),
        (4, 8, 6, 18, 0.333, "4 cm", "8 cm", "6 cm", "?"),
        (2, 4, 7, 21, 0.333, "2 cm", "4 cm", "7 cm", "?"),
        (3, 9, 4, 16, 0.25, "3 cm", "9 cm", "4 cm", "?"),
    ]
    AD, DB, DE, BC, r, *lbls = random.choice(combos)
    svg = _par_tri(f"{AD}", f"{DB}", f"{DE}", "?", ratio=r)
    q = (f"In triangle ABC, DE is parallel to BC, with D on AB and E on AC. "
         f"AD = {AD} cm, DB = {DB} cm, DE = {DE} cm.<br>{svg}<br>"
         f"Find BC.")
    sf = (AD + DB) / AD
    s = (f"Since DE ∥ BC, triangle ADE ~ triangle ABC by AA.<br>"
         f"AB = AD + DB = {AD} + {DB} = {AD+DB} cm<br>"
         f"Scale factor (small to large) = AB ÷ AD = {AD+DB} ÷ {AD} = {sf}<br>"
         f"BC = DE × {sf} = {DE} × {sf} = <strong>{BC} cm</strong>")
    return q, s, "Use the AA similarity: SF = AB/AD. Then BC = DE × SF.", 4


def _sc_i3_area_from_lsf():
    combos = [(4, 16, 15, 240), (3, 9, 20, 180), (5, 25, 8, 200), (2, 4, 36, 144)]
    sf, asf, area_s, area_l = random.choice(combos)
    q = (f"Two similar shapes have a linear scale factor of {sf}. "
         f"The smaller shape has area {area_s} cm². "
         f"Find the area of the larger shape.")
    s = (f"Area scale factor = {sf}² = {asf}<br>"
         f"Larger area = {area_s} × {asf} = <strong>{area_l} cm²</strong>")
    return q, s, "ASF = LSF². Larger area = smaller area × ASF.", 3


def _sc_i4_volume_from_lsf():
    combos = [(3, 27, 20, 540), (2, 8, 50, 400), (4, 64, 10, 640), (5, 125, 4, 500)]
    sf, vsf, vol_s, vol_l = random.choice(combos)
    q = (f"Two similar cones have a linear scale factor of {sf}. "
         f"The smaller cone has volume {vol_s} cm³. "
         f"Find the volume of the larger cone.")
    s = (f"Volume scale factor = {sf}³ = {vsf}<br>"
         f"Larger volume = {vol_s} × {vsf} = <strong>{vol_l} cm³</strong>")
    return q, s, "VSF = LSF³. Larger volume = smaller volume × VSF.", 3


def _sc_i5_lsf_from_area_ratio():
    combos = [(36, 81, "2:3"), (25, 100, "1:2"), (16, 25, "4:5"), (9, 49, "3:7")]
    a_s, a_l, lsf_str = random.choice(combos)
    from math import isqrt
    sq_s, sq_l = int(math.sqrt(a_s)), int(math.sqrt(a_l))
    q = (f"Two similar shapes have areas {a_s} cm² and {a_l} cm². "
         f"Find the linear scale factor from the smaller to the larger.")
    s = (f"Area ratio = {a_l} : {a_s}<br>"
         f"LSF = √(larger area ÷ smaller area) = √({a_l}/{a_s}) = √{a_l}/√{a_s}<br>"
         f"= {sq_l}/{sq_s} = <strong>{lsf_str}</strong>")
    return q, s, "LSF = √(area ratio). Take the square root of each area then form the ratio.", 3


def _sc_i6_dimension_from_volume():
    combos = [(8, 27, 2, 3, "radius", "cm"), (8, 125, 4, 10, "height", "cm"),
              (27, 64, 6, 8, "side length", "cm"), (1, 8, 3, 6, "radius", "cm")]
    v_s, v_l, d_s, d_l, dim, unit = random.choice(combos)
    vsf = v_l / v_s
    lsf = round(vsf ** (1/3), 4)
    q = (f"Two similar solids have volumes {v_s} cm³ and {v_l} cm³. "
         f"The smaller solid has {dim} {d_s} {unit}. "
         f"Find the {dim} of the larger solid.")
    s = (f"Volume scale factor = {v_l} ÷ {v_s} = {vsf}<br>"
         f"Linear scale factor = ∛({vsf}) = {lsf}<br>"
         f"Larger {dim} = {d_s} × {lsf} = <strong>{d_l} {unit}</strong>")
    return q, s, "LSF = ∛(volume scale factor). Then multiply the known dimension by the LSF.", 4


def _sc_i7_algebraic_similar_sides():
    # (x+2)/6 = (2x-1)/9: solve → 9(x+2) = 6(2x-1) → 9x+18 = 12x-6 → 24 = 3x → x=8
    # AB=10, BC=6, PQ=15, QR=9. SF=3/2.
    combos = [
        ("(x+2)", "(2x−1)", "6", "9", 8, 10, 15, 6, 9),
        ("(x+1)", "(3x−2)", "4", "8", 1.5, 2.5, 4, 4, 8),  # hmm not clean
    ]
    # Use first clean combo
    q = (f"Triangles ABC and PQR are similar (A↔P, B↔Q, C↔R). "
         f"AB = (x + 2) cm, PQ = (2x − 1) cm, BC = 6 cm, QR = 9 cm. Find x.")
    s = (f"Since the triangles are similar: AB/PQ = BC/QR<br>"
         f"(x + 2)/(2x − 1) = 6/9 = 2/3<br>"
         f"3(x + 2) = 2(2x − 1)<br>"
         f"3x + 6 = 4x − 2<br>"
         f"x = <strong>8</strong><br>"
         f"Check: AB = 10, PQ = 15. BC = 6, QR = 9. Scale factor = 15/10 = 3/2 ✓")
    return q, s, "Set up the proportion AB/PQ = BC/QR and cross-multiply.", 4


def _sc_i8_surface_area_similar_solids():
    combos = [(2, 5, 4, 25, 24, 150), (3, 4, 9, 16, 27, 48), (1, 3, 1, 9, 20, 180)]
    r1, r2, sa_ratio_n, sa_ratio_d, sa_s, sa_l = random.choice(combos)
    q = (f"Two similar pyramids have linear scale factor {r1} : {r2}. "
         f"The smaller pyramid has surface area {sa_s} cm². "
         f"Find the surface area of the larger pyramid.")
    s = (f"Surface area scale factor = {r2}² : {r1}² = {r2**2} : {r1**2}<br>"
         f"Ratio = {sa_ratio_d}/{sa_ratio_n}<br>"
         f"Surface area of larger = {sa_s} × {sa_ratio_d}/{sa_ratio_n} = <strong>{sa_l} cm²</strong>")
    return q, s, "Surface area scales as LSF². Multiply by (larger/smaller)².", 4


def _sc_i9_proof_aa_parallel():
    q = ("In triangle ABC, D lies on AB and E lies on AC such that DE is parallel to BC. "
         "Prove that triangle ADE is similar to triangle ABC.")
    s = ("Since DE ∥ BC:<br>"
         "• Angle ADE = Angle ABC (corresponding angles, DE ∥ BC)<br>"
         "• Angle A is common to both triangles ADE and ABC<br>"
         "Since two pairs of angles are equal, by <strong>AA (Angle-Angle)</strong> similarity,<br>"
         "triangle ADE ~ triangle ABC.")
    return q, s, "Identify two pairs of equal angles: one from parallel lines, one shared.", 4


def _sc_i10_overlapping_similar():
    combos = [
        (6, 4, 9, 6, "ABC", "ADE", 1.5),
        (8, 6, 12, 9, "PQR", "PST", 1.5),
    ]
    AB, AD, AC, AE, T1, T2, sf = random.choice(combos)
    DB, EC = AB - AD, AC - AE
    q = (f"In triangle {T1}, D is on {T1[0]}{T1[1]} and E is on {T1[0]}{T1[2]} "
         f"such that DE ∥ {T1[1]}{T1[2]}. "
         f"{T1[0]}{T1[1]} = {AB} cm, {T1[0]}D = {AD} cm, {T1[0]}{T1[2]} = {AC} cm, {T1[0]}E = {AE} cm. "
         f"Find D{T1[1]} and E{T1[2]}, and state the scale factor of the similar triangles.")
    s = (f"D{T1[1]} = {AB} − {AD} = <strong>{DB} cm</strong><br>"
         f"E{T1[2]} = {AC} − {AE} = <strong>{EC} cm</strong><br>"
         f"Scale factor = {T1[0]}{T1[1]} ÷ {T1[0]}D = {AB} ÷ {AD} = <strong>{sf}</strong>")
    return q, s, "DE ∥ BC creates similar triangles. Subtract to find remaining segment lengths.", 4


def _sc_i11_area_ratio_find_perimeter():
    combos = [(48, 75, "4:5"), (27, 48, "3:4"), (12, 75, "2:5")]
    a_s, a_l, lsf_str = random.choice(combos)
    sq_s = int(math.sqrt(a_s / 3)) if int(math.sqrt(a_s/3))**2 == a_s//3 else int(math.sqrt(a_s))
    sq_l = int(math.sqrt(a_l))
    # Use simpler version
    s_num, s_den = [int(x) for x in lsf_str.split(":")]
    q = (f"Two similar trapezoids have areas {a_s} cm² and {a_l} cm². "
         f"Find the linear scale factor and the ratio of their perimeters.")
    s = (f"Area ratio = {a_l} : {a_s}<br>"
         f"Linear scale factor = √({a_l}) : √({a_s}) = <strong>{lsf_str}</strong><br>"
         f"Perimeter ratio = linear scale factor = <strong>{lsf_str}</strong>")
    return q, s, "LSF = √(area ratio). Perimeter ratio equals the LSF.", 4


def _sc_i12_map_area():
    combos = [
        (25000, 8, 500000, "0.5 km²"),
        (50000, 4, 1000000, "1.0 km²"),
        (10000, 12, 120000, "0.12 km²"),
    ]
    scale, map_cm2, actual_cm2, actual_km2 = random.choice(combos)
    q = (f"A map has scale 1 : {scale:,}. "
         f"A park covers {map_cm2} cm² on the map. "
         f"Find the actual area of the park in km².")
    s = (f"Area scale factor = {scale:,}² = {scale**2:,}<br>"
         f"Actual area = {map_cm2} × {scale**2:,} cm²<br>"
         f"= {actual_cm2:,} cm²<br>"
         f"= {actual_cm2:,} ÷ (100 000)² km² (since 1 km = 100 000 cm)<br>"
         f"= <strong>{actual_km2}</strong>")
    return q, s, "Area scale factor = (linear scale)². Then convert cm² → km² (÷10¹⁰).", 5


def _sc_i13_similar_cones_volume():
    combos = [(4, 6, 20, 67.5), (3, 6, 10, 80), (2, 6, 9, 243)]
    h_s, h_l, vol_s, vol_l = random.choice(combos)
    sf = h_l / h_s
    vsf = sf ** 3
    q = (f"Two similar cones have heights {h_s} cm and {h_l} cm. "
         f"The smaller cone has volume {vol_s}π cm³. "
         f"Find the volume of the larger cone, leaving your answer in terms of π.")
    s = (f"Linear scale factor = {h_l} ÷ {h_s} = {sf}<br>"
         f"Volume scale factor = {sf}³ = {vsf}<br>"
         f"Volume of larger = {vol_s}π × {vsf} = <strong>{vol_l}π cm³</strong>")
    return q, s, "VSF = (height ratio)³. Multiply the smaller volume by the VSF.", 4


def _sc_i14_quadrilateral_angles():
    a, b, c = 85, 110, 75
    d = 360 - a - b - c
    q = (f"Quadrilateral ABCD is similar to quadrilateral PQRS "
         f"(A↔P, B↔Q, C↔R, D↔S). "
         f"Angle A = {a}°, angle B = {b}°, angle C = {c}°. "
         f"Find angle D, and hence write down all four angles of PQRS.")
    s = (f"Angle D = 360° − {a}° − {b}° − {c}° = <strong>{d}°</strong><br>"
         f"Corresponding angles in similar shapes are equal:<br>"
         f"Angle P = {a}°, angle Q = {b}°, angle R = {c}°, angle S = <strong>{d}°</strong>")
    return q, s, "Angles in a quadrilateral sum to 360°. Corresponding angles in similar shapes are equal.", 3


def _sc_i15_chain_scale_factor():
    combos = [
        (2, 3, 3, 5, 4, 10, "2:3", "3:5"),
        (3, 4, 4, 6, 6, 12, "3:4", "4:6"),
        (1, 2, 2, 3, 5, 15, "1:2", "2:3"),
    ]
    r1, r2, r3, r4, side_a, side_c, desc1, desc2 = random.choice(combos)
    sf1 = r2 / r1
    sf2 = r4 / r3
    sf_total = sf1 * sf2
    q = (f"Triangle A is similar to triangle B with scale factor {desc1}. "
         f"Triangle B is similar to triangle C with scale factor {desc2}. "
         f"A side of triangle A is {side_a} cm. "
         f"Find the corresponding side of triangle C.")
    s = (f"Scale factor A to B = {r2}/{r1} = {sf1}<br>"
         f"Scale factor B to C = {r4}/{r3} = {sf2}<br>"
         f"Scale factor A to C = {sf1} × {sf2} = {sf_total}<br>"
         f"Corresponding side of C = {side_a} × {sf_total} = <strong>{side_c} cm</strong>")
    return q, s, "Multiply the individual scale factors to get the overall scale factor.", 4


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT  (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _sc_d1_midpoint_theorem_proof():
    q = ("Triangle ABC has D and E as the midpoints of AB and AC respectively. "
         "Prove that triangle ADE is similar to triangle ABC, and hence show that DE ∥ BC and DE = ½BC.")
    s = ("Since D and E are midpoints: AD = ½AB and AE = ½AC.<br>"
         "Therefore AD/AB = AE/AC = 1/2.<br>"
         "Angle A is common to both triangles ADE and ABC.<br>"
         "Since two sides are in the same ratio and the included angle is equal, "
         "triangle ADE ~ triangle ABC by <strong>SAS similarity</strong>, "
         "with scale factor 1/2.<br>"
         "Since the triangles are similar, angle ADE = angle ABC (corresponding angles), "
         "so DE ∥ BC (corresponding angles with transversal AB are equal). "
         "The scale factor is 1/2, so DE = ½BC. ✓")
    return q, s, "Show AD/AB = AE/AC = 1/2 and angle A is common → SAS similarity.", 5


def _sc_d2_frustum_volume():
    combos = [
        (12, 9, 4, 3, 324, 12, 312),
        (15, 10, 5, 10/3, 500*math.pi/3, 500*math.pi/81, None),
    ]
    # Use the clean combo
    H, R, h_cut, r_cut = 12, 9, 4, 3
    vol_large = round(math.pi * R**2 * H / 3, 4)
    vol_small = round(math.pi * r_cut**2 * h_cut / 3, 4)
    vol_frust = round(vol_large - vol_small, 2)
    q = (f"A cone has height {H} cm and base radius {R} cm. "
         f"A smaller similar cone of height {h_cut} cm is removed from the apex. "
         f"Find the volume of the remaining frustum, leaving your answer in terms of π.")
    s = (f"The small cone is similar to the large cone with LSF = {h_cut}/{H} = 1/3.<br>"
         f"Radius of small cone = {R} × (1/3) = {r_cut} cm.<br>"
         f"Volume of large cone = (1/3)π × {R}² × {H} = {int(vol_large//math.pi)}π cm³<br>"
         f"Volume of small cone = (1/3)π × {r_cut}² × {h_cut} = {int(vol_small//math.pi)}π cm³<br>"
         f"Volume of frustum = {int(vol_large//math.pi)}π − {int(vol_small//math.pi)}π "
         f"= <strong>{int(vol_large//math.pi) - int(vol_small//math.pi)}π cm³</strong>")
    return q, s, "Find the radius of the small cone using the LSF. Then subtract volumes.", 6


def _sc_d3_altitude_in_right_triangle():
    # Right triangle with altitude to hypotenuse: CD² = AD × DB
    combos = [(4, 16, 8), (9, 25, 15), (4, 9, 6)]
    AD, DB, CD = random.choice(combos)
    AB = AD + DB
    q = (f"In right-angled triangle ABC (right angle at C), the altitude from C meets AB at D. "
         f"Given AD = {AD} cm and DB = {DB} cm:<br>"
         f"(i) State why triangle ACD is similar to triangle ACB.<br>"
         f"(ii) Show that CD² = AD × DB.<br>"
         f"(iii) Find CD.")
    s = (f"(i) Angle A is common to both triangles ACD and ACB. "
         f"Angle ADC = Angle ACB = 90°. By AA, triangle ACD ~ triangle ACB.<br>"
         f"(ii) From the similarity: CD/DB = AD/CD → CD² = AD × DB.<br>"
         f"(iii) CD² = {AD} × {DB} = {AD*DB}<br>"
         f"CD = √{AD*DB} = <strong>{CD} cm</strong>")
    return q, s, "Show AA similarity for triangle ACD and ACB. Use the proportion to get CD² = AD·DB.", 5


def _sc_d4_quadratic_from_similarity():
    q = ("Triangles PQR and XYZ are similar (P↔X, Q↔Y, R↔Z). "
         "PQ = x cm, QR = (x + 6) cm, XY = 4 cm, YZ = (x + 2) cm. "
         "Find x and state the scale factor of the similarity.")
    s = ("Since the triangles are similar: PQ/XY = QR/YZ<br>"
         "x/4 = (x + 6)/(x + 2)<br>"
         "x(x + 2) = 4(x + 6)<br>"
         "x² + 2x = 4x + 24<br>"
         "x² − 2x − 24 = 0<br>"
         "(x − 6)(x + 4) = 0<br>"
         "x = <strong>6</strong> (taking the positive value)<br>"
         "Scale factor = PQ/XY = 6/4 = <strong>3/2</strong>")
    return q, s, "Set up the proportion, cross-multiply, and solve the quadratic equation.", 5


def _sc_d5_area_with_given_ratio():
    combos = [(3, 5, 125, 45), (2, 7, 196, 16), (4, 5, 100, 64)]
    r1, r2, area_l, area_s = random.choice(combos)
    q = (f"Two similar triangles have sides in the ratio {r1} : {r2}. "
         f"The larger triangle has area {area_l} cm². "
         f"Find the area of the smaller triangle.")
    s = (f"Area scale factor = ({r1}/{r2})² = {r1**2}/{r2**2}<br>"
         f"Area of smaller = {area_l} × {r1**2}/{r2**2} = {area_l*r1**2//r2**2}<br>"
         f"= <strong>{area_s} cm²</strong>")
    return q, s, "ASF = (LSF)². Smaller area = larger area × (smaller/larger)².", 4


def _sc_d6_basic_proportionality():
    combos = [(3, 5, 16, 6, 10), (2, 6, 16, 4, 12), (4, 6, 20, 8, 12)]
    AD, DB, AC, AE, EC = random.choice(combos)
    q = (f"In triangle ABC, D is on AB with AD = {AD} cm and DB = {DB} cm. "
         f"A line through D parallel to BC meets AC at E. "
         f"AC = {AC} cm. Find AE and EC.")
    s = (f"By the Basic Proportionality Theorem (DE ∥ BC):<br>"
         f"AD/AB = AE/AC<br>"
         f"AB = {AD} + {DB} = {AD+DB} cm<br>"
         f"AE = AC × (AD/AB) = {AC} × ({AD}/{AD+DB}) = {AC*AD//(AD+DB)}<br>"
         f"AE = <strong>{AE} cm</strong><br>"
         f"EC = {AC} − {AE} = <strong>{EC} cm</strong>")
    return q, s, "BPT: AD/AB = AE/AC. Find AE then EC = AC − AE.", 5


def _sc_d7_congruence_proof():
    choice = random.choice([1, 2])
    if choice == 1:
        q = ("Triangle ABC is isosceles with AB = AC. M is the midpoint of BC. "
             "Prove that triangles ABM and ACM are congruent.")
        s = ("In triangles ABM and ACM:<br>"
             "• AB = AC (given: isosceles)<br>"
             "• BM = MC (M is midpoint of BC)<br>"
             "• AM = AM (common side)<br>"
             "By <strong>SSS</strong>, triangle ABM ≅ triangle ACM. ✓")
        hint = "List three pairs of equal sides: AB=AC, BM=MC, AM=AM. Then apply SSS."
    else:
        q = ("ABCD is a parallelogram. Prove that triangles ABC and CDA are congruent.")
        s = ("In triangles ABC and CDA:<br>"
             "• AB = CD (opposite sides of parallelogram)<br>"
             "• BC = DA (opposite sides of parallelogram)<br>"
             "• AC = CA (common diagonal)<br>"
             "By <strong>SSS</strong>, triangle ABC ≅ triangle CDA. ✓")
        hint = "Use properties of parallelogram (opposite sides equal), then apply SSS."
    return q, s, hint, 4


def _sc_d8_both_sa_and_vol_similar():
    combos = [(3, 6, 2, 24, 192, 15, 60), (2, 4, 2, 30, 120, 20, 80)]
    r_s, r_l, sf, vol_s, vol_l, sa_s, sa_l = random.choice(combos)
    q = (f"Two similar cones have radii {r_s} cm and {r_l} cm. "
         f"The smaller has volume {vol_s}π cm³ and surface area {sa_s}π cm². "
         f"Find the volume and surface area of the larger cone.")
    s = (f"Linear scale factor = {r_l}/{r_s} = {sf}<br>"
         f"Volume scale factor = {sf}³ = {sf**3}<br>"
         f"Volume of larger = {vol_s}π × {sf**3} = <strong>{vol_l}π cm³</strong><br>"
         f"Surface area scale factor = {sf}² = {sf**2}<br>"
         f"SA of larger = {sa_s}π × {sf**2} = <strong>{sa_l}π cm²</strong>")
    return q, s, "VSF = LSF³. SA scales as LSF². Apply each to the corresponding smaller value.", 5


def _sc_d9_shadow_height():
    combos = [
        (2, 5, 20, 8, "pole", "tree"),
        (1.8, 2.4, 6, 4.5, "person", "wall"),
        (3, 4, 16, 12, "post", "building"),
    ]
    h1, s1, s2, h2, obj1, obj2 = random.choice(combos)
    q = (f"A vertical {obj1} of height {h1} m casts a shadow of length {s1} m. "
         f"At the same time, a nearby {obj2} casts a shadow of length {s2} m. "
         f"Find the height of the {obj2}.")
    s = (f"The {obj1}, its shadow, and the sun ray form a triangle similar "
         f"to the triangle formed by the {obj2} and its shadow (same sun angle).<br>"
         f"height/{obj1} ÷ shadow/{obj1} = height/{obj2} ÷ shadow/{obj2}<br>"
         f"{h1}/{s1} = h/{s2}<br>"
         f"h = {h1} × {s2} / {s1} = <strong>{h2} m</strong>")
    return q, s, "Set up the ratio: height/shadow = height/shadow. Corresponding sides of similar triangles.", 4


def _sc_d10_angle_bisector_theorem():
    combos = [(9, 6, 10, 6, 4), (12, 8, 15, 9, 6), (15, 10, 20, 12, 8)]
    AB, AC, BC, BD, DC = random.choice(combos)
    q = (f"In triangle ABC, the bisector of angle A meets BC at D. "
         f"AB = {AB} cm, AC = {AC} cm, BC = {BC} cm. "
         f"Find BD and DC. (Use the angle bisector theorem: BD/DC = AB/AC.)")
    s = (f"By the angle bisector theorem: BD/DC = AB/AC = {AB}/{AC} = {AB//AC if AB%AC==0 else AB}/{AC}<br>"
         f"BD + DC = BC = {BC} cm<br>"
         f"BD = BC × AB/(AB + AC) = {BC} × {AB}/{AB+AC} = <strong>{BD} cm</strong><br>"
         f"DC = {BC} − {BD} = <strong>{DC} cm</strong>")
    return q, s, "Angle bisector theorem: BD/DC = AB/AC. Use BD + DC = BC to find both.", 5


def _sc_d11_similar_trapezium():
    combos = [(12, 8, 9, 6, "3:4"), (15, 10, 9, 6, "3:5"), (20, 12, 15, 9, "3:4")]
    AB, CD, PQ, RS, ratio = random.choice(combos)
    sf = PQ / AB
    q = (f"Trapezium ABCD (AB ∥ CD) is similar to trapezium PQRS (PQ ∥ RS). "
         f"AB = {AB} cm, CD = {CD} cm, PQ = {PQ} cm. Find RS.")
    s = (f"Scale factor = PQ ÷ AB = {PQ} ÷ {AB} = {sf}<br>"
         f"RS = CD × {sf} = {CD} × {sf} = <strong>{RS} cm</strong>")
    return q, s, "Find LSF from the parallel sides AB and PQ. Apply to CD to find RS.", 4


def _sc_d12_similar_rectangle_algebra():
    q = ("A rectangle has dimensions (2x + 1) cm by 6 cm. "
         "It is similar to a rectangle with dimensions (x + 5) cm by 4 cm. "
         "Find x and the dimensions of each rectangle.")
    s = ("For similar rectangles, corresponding sides must be in equal ratio.<br>"
         "Orientation: (2x+1)/(x+5) = 6/4 = 3/2<br>"
         "2(2x+1) = 3(x+5)<br>"
         "4x + 2 = 3x + 15<br>"
         "x = <strong>13</strong><br>"
         "Rectangle 1: (2×13+1) by 6 = <strong>27 cm × 6 cm</strong><br>"
         "Rectangle 2: (13+5) by 4 = <strong>18 cm × 4 cm</strong><br>"
         "Check: 27/18 = 3/2 and 6/4 = 3/2 ✓")
    return q, s, "Set up ratio of corresponding sides equal. Cross-multiply and solve for x.", 5


def _sc_d13_series_similar_triangles():
    q = ("Three equilateral triangles have side lengths 8 cm, 4 cm, and 2 cm. "
         "Find the ratio of the total combined area to the area of the largest triangle.")
    s = ("Let the area of the largest (side 8) = A₁.<br>"
         "The scale factors are 1, 1/2, and 1/4 relative to the largest.<br>"
         "Area scale factors: 1, 1/4, 1/16 (squaring each linear scale factor).<br>"
         "Total area = A₁ + A₁/4 + A₁/16 = A₁(1 + 4 + 1)/16 = A₁ × 21/16<br>"
         "Ratio = (21/16) : 1 = <strong>21 : 16</strong>")
    return q, s, "Each area scales as (side ratio)². Sum the three areas and find the ratio to the largest.", 5


def _sc_d14_scale_model_multi():
    combos = [(200, 500, 3, 150, 300), (100, 300, 4, 100, 240)]
    scale, vol_cm3, flr_cm2, vol_m3, flr_m2 = random.choice(combos)
    vol_scale = scale ** 3
    area_scale = scale ** 2
    actual_vol_cm3 = vol_cm3 * vol_scale
    actual_flr_cm2 = flr_cm2 * area_scale
    actual_vol_m3 = actual_vol_cm3 / 1e6
    actual_flr_m2 = actual_flr_cm2 / 1e4
    q = (f"A scale model of a building uses a scale of 1 : {scale}. "
         f"The model has volume {vol_cm3} cm³ and a floor area of {flr_cm2} cm². "
         f"Find: (i) the actual volume of the building in m³, "
         f"(ii) the actual floor area in m².")
    s = (f"Volume scale = {scale}³ = {vol_scale:,}<br>"
         f"(i) Actual volume = {vol_cm3} × {vol_scale:,} = {actual_vol_cm3:,} cm³<br>"
         f"= {actual_vol_cm3:,} ÷ 1,000,000 = <strong>{int(actual_vol_m3)} m³</strong><br>"
         f"Area scale = {scale}² = {area_scale:,}<br>"
         f"(ii) Actual floor area = {flr_cm2} × {area_scale:,} = {int(actual_flr_cm2):,} cm²<br>"
         f"= {int(actual_flr_cm2):,} ÷ 10,000 = <strong>{int(actual_flr_m2)} m²</strong>")
    return q, s, "Volume scale = LSF³; area scale = LSF². Convert cm³→m³ (÷10⁶) and cm²→m² (÷10⁴).", 6


def _sc_d15_lsf_from_vol_and_sa():
    combos = [(2, 8, 4, 3, 27, 9)]
    sf_s, vsf, sasf, sf_l, vsf_l, sasf_l = random.choice(combos)
    q = (f"Two similar solids have volume ratio {sf_s}³ : {sf_l}³ = {sf_s**3} : {sf_l**3}. "
         f"Their surface areas are 80 cm² and 180 cm². "
         f"Find: (i) the linear scale factor, (ii) the volume of the larger if the smaller has volume 40 cm³.")
    sa_ratio = 180 / 80
    lsf = math.sqrt(sa_ratio)
    vsf_val = lsf ** 3
    vol_l = round(40 * vsf_val, 1)
    s = (f"(i) SA ratio = 180/80 = 9/4<br>"
         f"LSF = √(9/4) = 3/2 = <strong>1.5</strong><br>"
         f"(ii) Volume scale factor = 1.5³ = {vsf_val}<br>"
         f"Volume of larger = 40 × {vsf_val} = <strong>{vol_l} cm³</strong>")
    return q, s, "(i) LSF = √(SA ratio). (ii) VSF = LSF³. Multiply smaller volume by VSF.", 6


# ══════════════════════════════════════════════════════════════════════════════
# MCQ  (15 questions)
# ══════════════════════════════════════════════════════════════════════════════

_SC_MCQ_BANK = [
    {"q": "Which set of conditions is sufficient to prove two triangles congruent?",
     "opts": ["A  SSS (three equal sides)", "B  SSA (two sides and a non-included angle)",
              "C  AAA (three equal angles)", "D  Two equal angles only"],
     "ans": "A", "marks": 1,
     "sol": "SSS is a valid congruence condition. SSA is ambiguous, AAA only proves similarity. Answer: <strong>A</strong>",
     "hint": "Three equal corresponding sides → SSS congruence."},

    {"q": "Two similar triangles have a linear scale factor of 3. What is the area scale factor?",
     "opts": ["A  9", "B  3", "C  27", "D  6"],
     "ans": "A", "marks": 1,
     "sol": "ASF = LSF² = 3² = <strong>9</strong>. Answer: A",
     "hint": "Area scale factor = (linear scale factor)²."},

    {"q": "Triangle ABC ~ Triangle PQR. AB = 6 cm, PQ = 9 cm, BC = 8 cm. Find QR.",
     "opts": ["A  12 cm", "B  16 cm", "C  6 cm", "D  5.3 cm"],
     "ans": "A", "marks": 2,
     "sol": "SF = 9/6 = 1.5. QR = 8 × 1.5 = <strong>12 cm</strong>. Answer: A",
     "hint": "Find SF = PQ/AB, then QR = BC × SF."},

    {"q": "Two similar shapes have areas 36 cm² and 81 cm². What is the linear scale factor?",
     "opts": ["A  3:2 (smaller to larger)", "B  9:4", "C  2:3", "D  4:9"],
     "ans": "A", "marks": 2,
     "sol": "LSF = √(81/36) = 9/6 = <strong>3/2</strong> (larger:smaller), or 2:3 smaller:larger. Answer: A",
     "hint": "LSF = √(area ratio). Take square roots of both areas."},

    {"q": "Two similar cones have linear scale factor 4. What is the volume scale factor?",
     "opts": ["A  64", "B  16", "C  4", "D  256"],
     "ans": "A", "marks": 1,
     "sol": "VSF = 4³ = <strong>64</strong>. Answer: A",
     "hint": "Volume scale factor = (linear scale factor)³."},

    {"q": "Which congruence condition applies to two right-angled triangles with equal hypotenuses and one equal leg?",
     "opts": ["A  RHS", "B  SSA", "C  SAS", "D  AAS"],
     "ans": "A", "marks": 1,
     "sol": "Right angle + Hypotenuse + Side = <strong>RHS</strong>. Answer: A",
     "hint": "RHS is specifically for right-angled triangles."},

    {"q": "DE ∥ BC. AD = 4 cm, AB = 10 cm, BC = 15 cm. Find DE.",
     "opts": ["A  6 cm", "B  37.5 cm", "C  10 cm", "D  4 cm"],
     "ans": "A", "marks": 3,
     "sol": "SF = AD/AB = 4/10 = 2/5. DE = BC × 2/5 = 15 × 2/5 = <strong>6 cm</strong>. Answer: A",
     "hint": "SF = AD/AB (smaller/larger). DE = BC × SF."},

    {"q": "Two similar shapes have perimeters 12 cm and 20 cm. What is the area scale factor?",
     "opts": ["A  25:9", "B  5:3", "C  10:6", "D  100:36"],
     "ans": "A", "marks": 2,
     "sol": "LSF = 20:12 = 5:3. ASF = (5/3)² = <strong>25:9</strong>. Answer: A",
     "hint": "LSF = perimeter ratio. ASF = LSF²."},

    {"q": "Two similar cylinders have volumes 27 cm³ and 64 cm³. What is the radius scale factor?",
     "opts": ["A  3:4", "B  9:16", "C  27:64", "D  4:3"],
     "ans": "A", "marks": 3,
     "sol": "VSF = 64/27. LSF = ∛(64/27) = 4/3. Radius scale (smaller:larger) = <strong>3:4</strong>. Answer: A",
     "hint": "LSF = ∛(volume scale factor)."},

    {"q": "In similar triangles, corresponding angles are always:",
     "opts": ["A  Equal", "B  Supplementary", "C  Complementary", "D  Double"],
     "ans": "A", "marks": 1,
     "sol": "Corresponding angles in similar triangles are always <strong>equal</strong>. Answer: A",
     "hint": "Similarity preserves shape (and hence angles) but not size."},

    {"q": "A smaller similar triangle has area 20 cm². The linear scale factor is 4. Find the area of the larger.",
     "opts": ["A  320 cm²", "B  80 cm²", "C  640 cm²", "D  160 cm²"],
     "ans": "A", "marks": 2,
     "sol": "ASF = 4² = 16. Larger area = 20 × 16 = <strong>320 cm²</strong>. Answer: A",
     "hint": "ASF = LSF². Larger area = smaller × ASF."},

    {"q": "Two similar solids have volume ratio 125 : 8. Find the linear scale factor.",
     "opts": ["A  5:2", "B  25:4", "C  125:8", "D  10:4"],
     "ans": "A", "marks": 2,
     "sol": "LSF = ∛(125/8) = 5/2. Scale factor = <strong>5:2</strong>. Answer: A",
     "hint": "LSF = ∛(volume ratio)."},

    {"q": "A map scale is 1 : 50 000. A road is 5 cm on the map. What is the actual length in km?",
     "opts": ["A  2.5 km", "B  25 km", "C  0.25 km", "D  250 km"],
     "ans": "A", "marks": 2,
     "sol": "Actual = 5 × 50 000 = 250 000 cm = <strong>2.5 km</strong>. Answer: A",
     "hint": "Multiply map distance by scale, then convert cm → km (÷100 000)."},

    {"q": "Two similar shapes have surface areas 48 cm² and 75 cm². Find the volume scale factor.",
     "opts": ["A  125:64 (or 5³:4³)", "B  25:16", "C  5:4", "D  75:48"],
     "ans": "A", "marks": 3,
     "sol": "SA ratio = 75/48 = 25/16. LSF = √(25/16) = 5/4. VSF = (5/4)³ = <strong>125/64</strong>. Answer: A",
     "hint": "SA ratio = LSF². So LSF = √(SA ratio). VSF = LSF³."},

    {"q": "DE ∥ BC. AD = 3 cm, DB = 5 cm, AE = 4 cm. Find EC.",
     "opts": ["A  6⅔ cm", "B  5 cm", "C  20/3 cm", "D  8 cm"],
     "ans": "A", "marks": 3,
     "sol": "BPT: AD/DB = AE/EC → 3/5 = 4/EC → EC = 4×5/3 = 20/3 = <strong>6⅔ cm</strong>. Answer: A",
     "hint": "Basic Proportionality Theorem: AD/DB = AE/EC. Cross-multiply."},
]


def similarity_congruence_mcq():
    item = random.choice(_SC_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_similarity_congruence_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _SC_MCQ_BANK, procedural_mcq_for('similarity_congruence'), 'similarity_congruence', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _sc_f1_congruence_sss, _sc_f2_congruence_sas, _sc_f3_congruence_asa,
            _sc_f4_congruence_rhs, _sc_f5_scale_factor, _sc_f6_missing_side_from_sf,
            _sc_f7_similar_triangles_sides, _sc_f8_angles_similar,
            _sc_f9_area_ratio_from_lsf, _sc_f10_lsf_from_area,
            _sc_f11_volume_ratio_from_lsf, _sc_f12_similar_rectangles,
            _sc_f13_perimeter_ratio, _sc_f14_map_scale, _sc_f15_area_of_smaller,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _sc_i1_aa_similarity_find_side, _sc_i2_parallel_lines_find_bc,
            _sc_i3_area_from_lsf, _sc_i4_volume_from_lsf,
            _sc_i5_lsf_from_area_ratio, _sc_i6_dimension_from_volume,
            _sc_i7_algebraic_similar_sides, _sc_i8_surface_area_similar_solids,
            _sc_i9_proof_aa_parallel, _sc_i10_overlapping_similar,
            _sc_i11_area_ratio_find_perimeter, _sc_i12_map_area,
            _sc_i13_similar_cones_volume, _sc_i14_quadrilateral_angles,
            _sc_i15_chain_scale_factor,
        ]
    elif difficulty == 'difficult':
        pool = [
            _sc_d1_midpoint_theorem_proof, _sc_d2_frustum_volume,
            _sc_d3_altitude_in_right_triangle, _sc_d4_quadratic_from_similarity,
            _sc_d5_area_with_given_ratio, _sc_d6_basic_proportionality,
            _sc_d7_congruence_proof, _sc_d8_both_sa_and_vol_similar,
            _sc_d9_shadow_height, _sc_d10_angle_bisector_theorem,
            _sc_d11_similar_trapezium, _sc_d12_similar_rectangle_algebra,
            _sc_d13_series_similar_triangles, _sc_d14_scale_model_multi,
            _sc_d15_lsf_from_vol_and_sa,
        ]
    else:
        f = random.sample([_sc_f1_congruence_sss, _sc_f5_scale_factor,
                           _sc_f9_area_ratio_from_lsf, _sc_f11_volume_ratio_from_lsf], 3)
        i = random.sample([_sc_i1_aa_similarity_find_side, _sc_i5_lsf_from_area_ratio,
                           _sc_i9_proof_aa_parallel, _sc_i13_similar_cones_volume], 4)
        d = random.sample([_sc_d4_quadratic_from_similarity, _sc_d7_congruence_proof,
                           _sc_d9_shadow_height, _sc_d14_scale_model_multi], 3)
        return f + i + d

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_similarity_congruence(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_similarity_congruence_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'similarity_congruence',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_similarity_congruence_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'similarity_congruence',
    )
