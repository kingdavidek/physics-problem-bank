"""
GCSE Maths – Mensuration
15 foundational · 18 intermediate · 18 difficult · 18 MCQ
Each variant returns (question, solution, hint, marks).
Final answers are wrapped in <strong> tags.
"""
import random
import math
from fractions import Fraction
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

def _dp(x, places=2):
    """Round to `places` decimal places and strip unnecessary trailing zeros."""
    val = round(x, places)
    if val == int(val):
        return str(int(val))
    return f"{val:.{places}f}".rstrip('0').rstrip('.')


def _pi_str(coeff):
    """Return a clean multiple-of-π string, e.g. 12π or 3.5π."""
    c = _dp(coeff, 2)
    return f"{c}π"


def _rect_svg(w, h, label_area=True):
    """Simple labelled rectangle SVG."""
    W, H = 140, 80
    x0, y0 = 30, 20
    area = w * h
    return (
        f'<svg width="200" height="125" viewBox="0 0 200 125" style="max-width:100%;vertical-align:middle;">'
        f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>'
        f'<text x="{x0+W//2}" y="{y0-6}" font-size="12" fill="#1a6fa8" text-anchor="middle">{w} cm</text>'
        f'<text x="{x0-8}" y="{y0+H//2}" font-size="12" fill="#1a6fa8" text-anchor="middle" '
        f'transform="rotate(-90,{x0-8},{y0+H//2})">{h} cm</text>'
        f'</svg>'
    )


def _triangle_svg(base, height):
    """Right-triangle SVG labelled with base and height."""
    return (
        f'<svg width="200" height="130" viewBox="0 0 200 130" style="max-width:100%;vertical-align:middle;">'
        f'<polygon points="30,110 170,110 30,20" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>'
        f'<line x1="30" y1="20" x2="30" y2="110" stroke="#aaa" stroke-width="1" stroke-dasharray="4,3"/>'
        f'<text x="100" y="124" font-size="12" fill="#1a6fa8" text-anchor="middle">{base} cm</text>'
        f'<text x="16" y="68" font-size="12" fill="#a13544" text-anchor="middle">{height} cm</text>'
        f'</svg>'
    )


def _circle_svg(r_label):
    return (
        f'<svg width="160" height="160" viewBox="0 0 160 160" style="max-width:100%;vertical-align:middle;">'
        f'<circle cx="80" cy="80" r="60" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="2"/>'
        f'<line x1="80" y1="80" x2="140" y2="80" stroke="#a13544" stroke-width="1.5"/>'
        f'<text x="110" y="73" font-size="12" fill="#a13544" text-anchor="middle">{r_label}</text>'
        f'</svg>'
    )


def _cuboid_svg(l, w, h):
    """Isometric-ish cuboid SVG."""
    return (
        f'<svg width="200" height="160" viewBox="0 0 200 160" style="max-width:100%;vertical-align:middle;">'
        # front face
        f'<polygon points="40,50 140,50 140,130 40,130" fill="#e8f4fd" stroke="#1a6fa8" stroke-width="1.5"/>'
        # top face
        f'<polygon points="40,50 90,20 190,20 140,50" fill="#c8e4f8" stroke="#1a6fa8" stroke-width="1.5"/>'
        # right face
        f'<polygon points="140,50 190,20 190,100 140,130" fill="#b0d4f0" stroke="#1a6fa8" stroke-width="1.5"/>'
        # labels
        f'<text x="90" y="145" font-size="12" fill="#1a6fa8" text-anchor="middle">{l} cm</text>'
        f'<text x="172" y="62" font-size="12" fill="#1a6fa8">{w} cm</text>'
        f'<text x="23" y="92" font-size="12" fill="#1a6fa8" text-anchor="middle">{h} cm</text>'
        f'</svg>'
    )


def _sector_svg(r_label, angle):
    """SVG of a sector with radius r_label and given angle."""
    theta = math.radians(angle)
    cx, cy, r = 90, 110, 80
    ex = cx + r * math.cos(-theta)
    ey = cy + r * math.sin(-theta)
    large = 1 if angle > 180 else 0
    return (
        f'<svg width="180" height="130" viewBox="0 0 180 130" style="max-width:100%;vertical-align:middle;">'
        f'<path d="M{cx},{cy} L{cx+r},{cy} A{r},{r},0,{large},0,{ex:.1f},{ey:.1f} Z" '
        f'fill="#fef4e8" stroke="#8a5300" stroke-width="2"/>'
        f'<text x="{cx+r//2}" y="{cy-6}" font-size="12" fill="#8a5300" text-anchor="middle">{r_label}</text>'
        f'<text x="{cx+14}" y="{cy+18}" font-size="12" fill="#a13544">{angle}°</text>'
        f'</svg>'
    )


def _mens_abc_block(*parts):
    """Format sub-questions or solution steps as a), b), c)."""
    return "".join(
        f"<br><strong>{chr(ord('a') + i)})</strong> {text}"
        for i, text in enumerate(parts)
    )


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (15 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _mens_found_rect_area():
    l = random.randint(4, 20)
    w = random.randint(3, 15)
    area = l * w
    svg = _rect_svg(l, w)
    q = (f"Find the area of a rectangle with length {l} cm and width {w} cm.<br>{svg}")
    s = (f"Area of a rectangle = length × width<br>"
         f"\\(= {l} \\times {w}\\)<br>"
         f"<strong>\\(= {area}\\text{{ cm}}^2\\)</strong>")
    return q, s, "Area = l × w", 1


def _mens_found_rect_perimeter():
    l = random.randint(5, 20)
    w = random.randint(3, 14)
    P = 2 * (l + w)
    q = f"Find the perimeter of a rectangle with length {l} cm and width {w} cm."
    s = (f"Perimeter = 2(l + w) = 2({l} + {w}) = 2 × {l+w}<br>"
         f"<strong>= {P} cm</strong>")
    return q, s, "Perimeter = 2(l + w)", 1


def _mens_found_triangle_area():
    b = random.randint(4, 20)
    h = random.randint(3, 16)
    area = Fraction(b * h, 2)
    svg = _triangle_svg(b, h)
    q = (f"Find the area of a triangle with base {b} cm and perpendicular height {h} cm.<br>{svg}")
    s = (f"Area = ½ × base × height<br>"
         f"= ½ × {b} × {h}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Area = ½ × b × h", 1


def _mens_found_parallelogram_area():
    b = random.randint(5, 18)
    h = random.randint(3, 12)
    area = b * h
    q = (f"A parallelogram has base {b} cm and perpendicular height {h} cm. "
         f"Find its area.")
    s = (f"Area of a parallelogram = base × perpendicular height<br>"
         f"= {b} × {h}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Area = base × perpendicular height (not the slant)", 2


def _mens_found_trapezium_area():
    a = random.randint(4, 12)
    b = random.randint(a + 2, a + 10)
    h = random.randint(3, 10)
    area = Fraction((a + b) * h, 2)
    q = (f"Find the area of a trapezium with parallel sides {a} cm and {b} cm, "
         f"and perpendicular height {h} cm.")
    s = (f"Area = ½(a + b)h<br>"
         f"= ½ × ({a} + {b}) × {h}<br>"
         f"= ½ × {a+b} × {h}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Area = ½(a + b)h", 2


def _mens_found_circle_circumference():
    r = random.randint(3, 12)
    d = 2 * r
    circ = round(math.pi * d, 2)
    svg = _circle_svg(f"{r} cm")
    q = (f"Find the circumference of a circle with radius {r} cm. "
         f"Give your answer to 2 decimal places.<br>{svg}")
    s = (f"C = πd = π × {d}<br>"
         f"<strong>= {circ} cm</strong>")
    return q, s, "C = πd = 2πr", 2


def _mens_found_circle_area():
    r = random.randint(3, 12)
    area = round(math.pi * r * r, 2)
    svg = _circle_svg(f"{r} cm")
    q = (f"Find the area of a circle with radius {r} cm. "
         f"Give your answer to 2 decimal places.<br>{svg}")
    s = (f"A = πr²<br>"
         f"= π × {r}²<br>"
         f"= π × {r*r}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "A = πr²", 2


def _mens_found_cuboid_volume():
    l = random.randint(3, 10)
    w = random.randint(2, 8)
    h = random.randint(2, 8)
    vol = l * w * h
    svg = _cuboid_svg(l, w, h)
    q = (f"Find the volume of a cuboid with length {l} cm, width {w} cm, and height {h} cm.<br>{svg}")
    s = (f"V = l × w × h<br>"
         f"= {l} × {w} × {h}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = l × w × h", 2


def _mens_found_cuboid_surface_area():
    l = random.randint(3, 10)
    w = random.randint(2, 8)
    h = random.randint(2, 7)
    sa = 2 * (l*w + l*h + w*h)
    q = (f"Find the surface area of a cuboid with length {l} cm, width {w} cm, and height {h} cm.")
    s = (f"SA = 2(lw + lh + wh)<br>"
         f"= 2({l}×{w} + {l}×{h} + {w}×{h})<br>"
         f"= 2({l*w} + {l*h} + {w*h})<br>"
         f"= 2 × {l*w + l*h + w*h}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "SA = 2(lw + lh + wh)", 3


def _mens_found_triangular_prism_vol():
    b = random.randint(4, 12)
    h = random.randint(3, 10)
    length = random.randint(5, 15)
    area_cross = Fraction(b * h, 2)
    vol = area_cross * length
    q = (f"A triangular prism has a cross-section that is a right triangle with base {b} cm "
         f"and height {h} cm. The length of the prism is {length} cm. Find the volume.")
    s = (f"Area of cross-section = ½ × {b} × {h} = {area_cross} cm²<br>"
         f"Volume = cross-sectional area × length<br>"
         f"= {area_cross} × {length}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = area of cross-section × length", 3


def _mens_found_compound_area_L():
    a = random.randint(5, 12)
    b = random.randint(3, a - 2)
    c = random.randint(3, 10)
    d_val = random.randint(2, c - 1)
    # L-shape: big rectangle (a × c) minus small rectangle (b × d_val)
    area = a * c - b * d_val
    q = (f"An L-shaped figure is made from a {a} cm × {c} cm rectangle with a "
         f"{b} cm × {d_val} cm rectangle cut from one corner. Find the area.")
    s = (f"Area = large rectangle − cut-out rectangle<br>"
         f"= ({a} × {c}) − ({b} × {d_val})<br>"
         f"= {a*c} − {b*d_val}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Split into simpler rectangles or subtract", 3


def _mens_found_area_to_length():
    w = random.randint(3, 10)
    area = random.randint(w * 4, w * 14)
    l = area / w
    q = (f"A rectangle has area {area} cm² and width {w} cm. Find its length.")
    s = (f"Area = length × width<br>"
         f"\\(l = \\dfrac{{\\text{{Area}}}}{{w}} = \\dfrac{{{area}}}{{{w}}}\\)<br>"
         f"<strong>= {_dp(l)} cm</strong>")
    return q, s, "Rearrange: length = area ÷ width", 2


def _mens_found_unit_conversion_area():
    l_cm = random.randint(20, 80)
    w_cm = random.randint(10, 50)
    area_cm2 = l_cm * w_cm
    area_m2 = area_cm2 / 10000
    q = (f"A rectangle measures {l_cm} cm by {w_cm} cm. "
         f"Find its area in m².")
    s = (f"Area = {l_cm} × {w_cm} = {area_cm2} cm²<br>"
         f"1 m² = 10 000 cm²<br>"
         f"Area = {area_cm2} ÷ 10 000<br>"
         f"<strong>= {_dp(area_m2, 4)} m²</strong>")
    return q, s, "1 m = 100 cm, so 1 m² = 100² = 10 000 cm²", 2


def _mens_found_density():
    density = random.randint(2, 9)
    vol = random.randint(10, 60)
    mass = density * vol
    q = (f"A material has density {density} g/cm³ and volume {vol} cm³. "
         f"Find its mass in grams.")
    s = (f"Mass = density × volume<br>"
         f"= {density} × {vol}<br>"
         f"<strong>= {mass} g</strong>")
    return q, s, "Mass = density × volume", 2


def _mens_found_diameter_from_circumference():
    C = random.randint(20, 80)
    d = round(C / math.pi, 2)
    q = (f"A circle has circumference {C} cm. Find the diameter to 2 decimal places.")
    s = (f"C = πd<br>"
         f"\\(d = \\dfrac{{C}}{{\\pi}} = \\dfrac{{{C}}}{{\\pi}}\\)<br>"
         f"<strong>= {d} cm</strong>")
    return q, s, "Rearrange C = πd to find d = C ÷ π", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (18 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _mens_inter_arc_length():
    r = random.randint(4, 15)
    angle = random.choice([30, 45, 60, 90, 120, 150, 135, 270])
    arc = round(angle / 360 * 2 * math.pi * r, 2)
    svg = _sector_svg(f"{r} cm", angle)
    q = (f"Find the arc length of a sector with radius {r} cm and angle {angle}°. "
         f"Give your answer to 2 d.p.<br>{svg}")
    s = (f"Arc length = \\(\\dfrac{{\\theta}}{{360}} \\times 2\\pi r\\)<br>"
         f"= \\(\\dfrac{{{angle}}}{{360}} \\times 2\\pi \\times {r}\\)<br>"
         f"<strong>= {arc} cm</strong>")
    return q, s, "Arc length = (θ/360) × 2πr", 2


def _mens_inter_sector_area():
    r = random.randint(4, 14)
    angle = random.choice([30, 45, 60, 90, 120, 150, 135, 240])
    area = round(angle / 360 * math.pi * r * r, 2)
    svg = _sector_svg(f"{r} cm", angle)
    q = (f"Find the area of a sector with radius {r} cm and angle {angle}°. "
         f"Give your answer to 2 d.p.<br>{svg}")
    s = (f"Sector area = \\(\\dfrac{{\\theta}}{{360}} \\times \\pi r^2\\)<br>"
         f"= \\(\\dfrac{{{angle}}}{{360}} \\times \\pi \\times {r}^2\\)<br>"
         f"= \\(\\dfrac{{{angle}}}{{360}} \\times \\pi \\times {r*r}\\)<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Sector area = (θ/360) × πr²", 3


def _mens_inter_cylinder_volume():
    r = random.randint(2, 9)
    h = random.randint(4, 20)
    vol = round(math.pi * r * r * h, 2)
    q = (f"Find the volume of a cylinder with radius {r} cm and height {h} cm. "
         f"Give your answer to 2 d.p.")
    s = (f"V = πr²h<br>"
         f"= π × {r}² × {h}<br>"
         f"= π × {r*r} × {h}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = πr²h", 3


def _mens_inter_cylinder_surface_area():
    r = random.randint(2, 8)
    h = random.randint(5, 18)
    sa = round(2 * math.pi * r * (r + h), 2)
    q = (f"Find the total surface area of a closed cylinder with radius {r} cm "
         f"and height {h} cm. Give your answer to 2 d.p.")
    s = (f"SA = 2πr(r + h)<br>"
         f"= 2π × {r} × ({r} + {h})<br>"
         f"= 2π × {r} × {r+h}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "SA = 2πrh (curved) + 2πr² (two ends)", 3


def _mens_inter_cone_volume():
    r = random.randint(3, 10)
    h = random.randint(5, 18)
    vol = round(math.pi * r * r * h / 3, 2)
    q = (f"Find the volume of a cone with base radius {r} cm and perpendicular height {h} cm. "
         f"Give your answer to 2 d.p.")
    s = (f"V = ⅓πr²h<br>"
         f"= ⅓ × π × {r}² × {h}<br>"
         f"= ⅓ × π × {r*r} × {h}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = ⅓πr²h", 3


def _mens_inter_sphere_volume():
    r = random.randint(2, 9)
    vol = round(4/3 * math.pi * r**3, 2)
    q = (f"Find the volume of a sphere with radius {r} cm. "
         f"Give your answer to 2 d.p.")
    s = (f"V = \\(\\frac{{4}}{{3}}\\pi r^3\\)<br>"
         f"= \\(\\frac{{4}}{{3}} \\times \\pi \\times {r}^3\\)<br>"
         f"= \\(\\frac{{4}}{{3}} \\times \\pi \\times {r**3}\\)<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = (4/3)πr³", 3


def _mens_inter_sphere_surface_area():
    r = random.randint(2, 9)
    sa = round(4 * math.pi * r * r, 2)
    q = (f"Find the surface area of a sphere with radius {r} cm. Give your answer to 2 d.p.")
    s = (f"SA = 4πr²<br>"
         f"= 4 × π × {r}²<br>"
         f"= 4 × π × {r*r}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "SA = 4πr²", 2


def _mens_inter_pyramid_volume():
    l = random.randint(4, 10)
    w = random.randint(3, 9)
    h = random.randint(5, 15)
    base_area = l * w
    vol = round(base_area * h / 3, 2)
    q = (f"A square-based pyramid has a rectangular base {l} cm × {w} cm and "
         f"perpendicular height {h} cm. Find its volume.")
    s = (f"V = ⅓ × base area × height<br>"
         f"= ⅓ × ({l} × {w}) × {h}<br>"
         f"= ⅓ × {base_area} × {h}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "V = ⅓ × base area × height", 3


def _mens_inter_annulus_area():
    R = random.randint(6, 14)
    r = random.randint(2, R - 2)
    area = round(math.pi * (R*R - r*r), 2)
    q = (f"Find the area of an annulus (ring) with outer radius {R} cm and "
         f"inner radius {r} cm. Give your answer to 2 d.p.")
    s = (f"Area = π(R² − r²)<br>"
         f"= π({R}² − {r}²)<br>"
         f"= π({R*R} − {r*r})<br>"
         f"= π × {R*R - r*r}<br>"
         f"<strong>= {area} cm²</strong>")
    return q, s, "Subtract inner circle area from outer: π(R²−r²)", 3


def _mens_inter_perimeter_sector():
    r = random.randint(5, 14)
    angle = random.choice([45, 60, 90, 120, 150, 180])
    arc = round(angle / 360 * 2 * math.pi * r, 2)
    perimeter = round(arc + 2 * r, 2)
    q = (f"Find the perimeter of a sector with radius {r} cm and angle {angle}°. "
         f"Give your answer to 2 d.p.")
    s = (f"Perimeter = arc length + 2 radii<br>"
         f"Arc = \\(\\frac{{{angle}}}{{360}} \\times 2\\pi \\times {r} = {arc}\\) cm<br>"
         f"Perimeter = {arc} + 2 × {r} = {arc} + {2*r}<br>"
         f"<strong>= {perimeter} cm</strong>")
    return q, s, "Perimeter of sector = arc + 2r", 3


def _mens_inter_cone_surface_area():
    r = random.randint(3, 10)
    l_slant = random.randint(r + 2, r + 12)
    sa = round(math.pi * r * (r + l_slant), 2)
    q = (f"A cone has base radius {r} cm and slant height {l_slant} cm. "
         f"Find the total surface area to 2 d.p.")
    s = (f"SA = πr(r + l)<br>"
         f"= π × {r} × ({r} + {l_slant})<br>"
         f"= π × {r} × {r + l_slant}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "SA = πrl (curved) + πr² (base) = πr(r + l)", 3


def _mens_inter_find_radius_from_area():
    r = random.randint(3, 12)
    area = round(math.pi * r * r, 2)
    q = (f"A circle has area {area} cm². Find its radius to 2 d.p.")
    s = (f"A = πr²<br>"
         f"\\(r = \\sqrt{{\\dfrac{{A}}{{\\pi}}}} = \\sqrt{{\\dfrac{{{area}}}{{\\pi}}}}\\)<br>"
         f"<strong>= {_dp(r, 2)} cm</strong> (using \\(r^2 = {area}/\\pi ≈ {_dp(area/math.pi,2)}\\))")
    return q, s, "Rearrange A = πr² to get r = √(A/π)", 3


def _mens_inter_rate_fill():
    r = random.randint(2, 7)
    h = random.randint(8, 25)
    vol_L = round(math.pi * r * r * h / 1000, 2)  # 1 L = 1000 cm³
    rate = random.randint(2, 8)
    time_min = round(vol_L / rate, 2)
    q = (f"Water flows into a cylindrical tank at {rate} litres per minute. "
         f"The tank has radius {r} cm and height {h} cm. "
         f"How long does it take to fill the tank? Give your answer to 2 d.p. (1 litre = 1000 cm³)")
    s = (f"Volume = πr²h = π × {r}² × {h} = {round(math.pi*r*r*h,2)} cm³<br>"
         f"In litres: {round(math.pi*r*r*h,2)} ÷ 1000 = {vol_L} litres<br>"
         f"Time = volume ÷ rate = {vol_L} ÷ {rate}<br>"
         f"<strong>= {time_min} minutes</strong>")
    return q, s, "Volume in litres ÷ flow rate = time", 4


def _mens_inter_similar_area():
    k = random.choice([2, 3, 4, 5])
    area1 = random.randint(10, 40)
    area2 = area1 * k * k
    q = (f"Two similar shapes have lengths in ratio 1 : {k}. "
         f"The area of the smaller shape is {area1} cm². Find the area of the larger shape.")
    s = (f"Length ratio = 1 : {k}<br>"
         f"Area ratio = 1² : {k}² = 1 : {k*k}<br>"
         f"Area of larger = {area1} × {k*k}<br>"
         f"<strong>= {area2} cm²</strong>")
    return q, s, "Area scale factor = (length scale factor)²", 3


def _mens_inter_composite_cylinder_hemisphere():
    r = random.randint(2, 7)
    h = random.randint(6, 18)
    vol_cyl = round(math.pi * r * r * h, 2)
    vol_hemi = round(2/3 * math.pi * r**3, 2)
    total = round(vol_cyl + vol_hemi, 2)
    q = (f"A composite solid consists of a cylinder with radius {r} cm and height {h} cm, "
         f"with a hemisphere of the same radius placed on top. "
         f"Find the total volume to 2 d.p.")
    s = (f"Cylinder: V = πr²h = π × {r}² × {h} = {vol_cyl} cm³<br>"
         f"Hemisphere: V = ½ × \\(\\frac{{4}}{{3}}\\)πr³ = \\(\\frac{{2}}{{3}}\\)πr³ "
         f"= \\(\\frac{{2}}{{3}}\\) × π × {r}³ = {vol_hemi} cm³<br>"
         f"Total = {vol_cyl} + {vol_hemi}<br>"
         f"<strong>= {total} cm³</strong>")
    return q, s, "Total volume = cylinder + hemisphere = πr²h + (2/3)πr³", 4


# ---------- INTERMEDIATE (multi-step, real-world, a/b/c) ----------

def _mens_inter_cylinder_tank_multipart():
    """Closed cylindrical tank — volume, surface area, fill time."""
    r = random.randint(30, 60)
    h = random.randint(80, 150)
    rate = random.randint(4, 10)
    vol_cm3 = math.pi * r * r * h
    vol_L = round(vol_cm3 / 1000, 2)
    sa = round(2 * math.pi * r * (r + h), 2)
    time_min = round(vol_L / rate, 2)
    intro = (
        f"A closed cylindrical water tank has radius {r} cm and height {h} cm. "
        f"Water flows in at {rate} litres per minute (1 litre = 1000 cm³)."
    )
    q = intro + _mens_abc_block(
        "Find the volume of the tank in cm³, then convert to litres to 2 d.p. (1000 cm³ = 1 litre).",
        "Find the total surface area of the tank to 2 d.p.",
        "How long does it take to fill the empty tank? Give your answer in minutes to 2 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> \(V = \pi r^2 h = \pi \times {r}^2 \times {h} = {round(vol_cm3, 2)}\) cm³<br>"
        rf"In litres: {round(vol_cm3, 2)} ÷ 1000 = <strong>{vol_L} litres</strong><br>"
        rf"<strong>b)</strong> \(SA = 2\pi r(r + h) = 2\pi \times {r} \times {r + h}\)<br>"
        rf"= 2π × {r} × {r+h} = <strong>{sa} cm²</strong><br>"
        rf"<strong>c)</strong> Time = {vol_L} ÷ {rate} = <strong>{time_min} minutes</strong>"
    )
    hint = "Use V = πr²h then convert to litres; SA = 2πr(r + h); time = volume ÷ rate."
    return q, s, hint, 5


def _mens_inter_garden_plot_multipart():
    """Rectangular plot with semicircular end — perimeter, area, turf cost."""
    length = random.randint(14, 22)
    width = random.randint(8, 14)
    cost_per_m2 = random.randint(5, 12)
    rect_area = length * width
    semi_area = round(math.pi * width * width / 8, 2)
    total_area = round(rect_area + semi_area, 2)
    arc = round(math.pi * width / 2, 2)
    perimeter = round(2 * length + width + arc, 2)
    total_cost = round(total_area * cost_per_m2, 2)
    intro = (
        f"A garden plot is a rectangle {length} m by {width} m with a semicircle of "
        f"diameter {width} m on one of the shorter sides. Turf costs £{cost_per_m2} per m²."
    )
    q = intro + _mens_abc_block(
        "Find the perimeter of the plot. Give your answer in metres to 2 d.p.",
        "Find the area of the plot in m² to 2 d.p.",
        "Find the cost of turfing the whole plot.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Perimeter = 2 × {length} + {width} + semicircle arc<br>"
        rf"Arc = \(\dfrac{{\pi \times {width}}}{{2}} = {arc}\) m<br>"
        rf"Perimeter = {2*length} + {width} + {arc} = <strong>{perimeter} m</strong><br>"
        rf"<strong>b)</strong> Rectangle area = {length} × {width} = {rect_area} m²<br>"
        rf"Semicircle area = \(\dfrac{{\pi \times {width}^2}}{{8}} = {semi_area}\) m²<br>"
        rf"Total area = {rect_area} + {semi_area} = <strong>{total_area} m²</strong><br>"
        rf"<strong>c)</strong> Cost = {total_area} × {cost_per_m2} = <strong>£{total_cost}</strong>"
    )
    hint = "Perimeter uses the curved arc instead of one width; area = rectangle + half circle; then multiply by the cost per m²."
    return q, s, hint, 5


def _mens_inter_cone_container_multipart():
    """Cone — volume, curved surface area, painting cost."""
    r = random.randint(4, 9)
    h = random.randint(8, 18)
    cost_per_m2 = random.randint(6, 14)
    slant = math.sqrt(r * r + h * h)
    vol = round(math.pi * r * r * h / 3, 2)
    curved = round(math.pi * r * slant, 2)
    curved_m2 = curved / 10000
    paint_cost = round(curved_m2 * cost_per_m2, 2)
    intro = (
        f"A conical container has base radius {r} cm and perpendicular height {h} cm. "
        f"Only the curved surface is painted at £{cost_per_m2} per m²."
    )
    q = intro + _mens_abc_block(
        "Find the volume of the cone to 2 d.p.",
        "Find the curved surface area to 2 d.p. (do not include the base).",
        "Find the cost of painting the curved surface only.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> \(V = \dfrac{{1}}{{3}}\pi r^2 h = \dfrac{{1}}{{3}} \times \pi \times {r}^2 \times {h}\)<br>"
        rf"<strong>= {vol} cm³</strong><br>"
        rf"<strong>b)</strong> Slant height \(l = \sqrt{{{r}^2 + {h}^2}} = {_dp(slant, 2)}\) cm<br>"
        rf"Curved area = \(\pi r l = \pi \times {r} \times {_dp(slant, 2)}\) = <strong>{curved} cm²</strong><br>"
        rf"<strong>c)</strong> {curved} cm² = {curved_m2:.4f} m²; cost = <strong>£{paint_cost}</strong>"
    )
    hint = "Use V = ⅓πr²h; find l = √(r² + h²) then curved area = πrl; convert cm² to m² for the cost."
    return q, s, hint, 5


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (18 variants)
# ══════════════════════════════════════════════════════════════════════════════

def _mens_diff_cone_slant_from_height():
    r = random.randint(3, 10)
    h = random.randint(4, 16)
    slant = round(math.sqrt(r*r + h*h), 4)
    sa = round(math.pi * r * (r + slant), 2)
    q = (f"A cone has base radius {r} cm and perpendicular height {h} cm. "
         f"Find the total surface area to 2 d.p.")
    s = (f"First find slant height: \\(l = \\sqrt{{r^2 + h^2}} = \\sqrt{{{r}^2 + {h}^2}} = "
         f"\\sqrt{{{r*r + h*h}}} ≈ {round(slant,2)}\\) cm<br>"
         f"SA = πr(r + l) = π × {r} × ({r} + {round(slant,2)})<br>"
         f"= π × {r} × {round(r + slant, 2)}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "Find slant height using Pythagoras: l = √(r² + h²), then SA = πr(r + l)", 4


def _mens_diff_sphere_radius_from_volume():
    r_true = random.randint(3, 10)
    vol = round(4/3 * math.pi * r_true**3, 2)
    q = (f"A sphere has volume {vol} cm³. Find its radius to 2 d.p.")
    s = (f"V = \\(\\frac{{4}}{{3}}\\pi r^3\\)<br>"
         f"\\(r^3 = \\dfrac{{3V}}{{4\\pi}} = \\dfrac{{3 \\times {vol}}}{{4\\pi}} = "
         f"\\dfrac{{{3*vol}}}{{4\\pi}} ≈ {_dp(3*vol/(4*math.pi), 2)}\\)<br>"
         f"\\(r = \\sqrt[3]{{{_dp(3*vol/(4*math.pi),2)}}} \\)<br>"
         f"<strong>≈ {r_true} cm</strong>")
    return q, s, "Rearrange V = (4/3)πr³ → r³ = 3V/(4π), then cube root", 4


def _mens_diff_exact_pi_answer():
    r = random.randint(3, 9)
    h = random.randint(5, 15)
    # Cylinder volume in terms of π
    coeff = r * r * h
    q = (f"Find the exact volume of a cylinder with radius {r} cm and height {h} cm. "
         f"Give your answer in terms of π.")
    s = (f"V = πr²h<br>"
         f"= π × {r}² × {h}<br>"
         f"= π × {r*r} × {h}<br>"
         f"<strong>= {coeff}π cm³</strong>")
    return q, s, "Leave answer as a multiple of π — do not use 3.14…", 2


def _mens_diff_frustum_volume():
    R = random.randint(5, 12)
    r = random.randint(2, R - 2)
    h = random.randint(6, 18)
    vol = round(math.pi * h / 3 * (R*R + R*r + r*r), 2)
    q = (f"A frustum is formed by removing a small cone from the top of a large cone. "
         f"The frustum has large radius {R} cm, small radius {r} cm, and "
         f"perpendicular height {h} cm. Find the volume to 2 d.p.")
    s = (f"V = \\(\\dfrac{{\\pi h}}{{3}}(R^2 + Rr + r^2)\\)<br>"
         f"= \\(\\dfrac{{\\pi \\times {h}}}{{3}}({R}^2 + {R}\\times{r} + {r}^2)\\)<br>"
         f"= \\(\\dfrac{{\\pi \\times {h}}}{{3}}({R*R} + {R*r} + {r*r})\\)<br>"
         f"= \\(\\dfrac{{\\pi \\times {h}}}{{3}} \\times {R*R + R*r + r*r}\\)<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "Frustum volume = (πh/3)(R² + Rr + r²)", 5


def _mens_diff_hemisphere_cone_surface_area():
    r = random.randint(3, 8)
    h = random.randint(r + 2, r + 12)
    slant = round(math.sqrt(r*r + h*h), 4)
    sa_hemi_curved = round(2 * math.pi * r * r, 2)
    sa_cone_curved = round(math.pi * r * slant, 2)
    total = round(sa_hemi_curved + sa_cone_curved, 2)
    q = (f"A solid is made by joining a hemisphere of radius {r} cm to the flat base of a cone "
         f"with the same base radius and perpendicular height {h} cm. "
         f"Find the total surface area to 2 d.p. (Do not include the circular join.)")
    s = (f"Cone slant height: l = √({r}² + {h}²) = √{r*r + h*h} ≈ {round(slant,2)} cm<br>"
         f"Curved surface of hemisphere = 2πr² = 2π × {r}² = {sa_hemi_curved} cm²<br>"
         f"Curved surface of cone = πrl = π × {r} × {round(slant,2)} = {sa_cone_curved} cm²<br>"
         f"Total SA = {sa_hemi_curved} + {sa_cone_curved}<br>"
         f"<strong>= {total} cm²</strong>")
    return q, s, "SA = curved hemisphere (2πr²) + curved cone (πrl); no flat circles needed", 5


def _mens_diff_sector_minus_triangle():
    r = random.randint(6, 14)
    angle = 60  # equilateral triangle inside sector
    sector_area = round(60/360 * math.pi * r*r, 4)
    triangle_area = round(0.5 * r * r * math.sin(math.radians(60)), 4)
    segment = round(sector_area - triangle_area, 2)
    q = (f"A sector has radius {r} cm and angle 60°. Find the area of the minor segment "
         f"(the region between the chord and the arc). Give your answer to 2 d.p.")
    s = (f"Area of sector = \\(\\frac{{60}}{{360}} \\times \\pi \\times {r}^2 = "
         f"\\frac{{\\pi \\times {r*r}}}{{6}} ≈ {round(sector_area,2)}\\) cm²<br>"
         f"Area of triangle = \\(\\frac{{1}}{{2}} r^2 \\sin\\theta = "
         f"\\frac{{1}}{{2}} \\times {r*r} \\times \\sin 60° ≈ {round(triangle_area,2)}\\) cm²<br>"
         f"Segment area = sector − triangle = {round(sector_area,2)} − {round(triangle_area,2)}<br>"
         f"<strong>= {segment} cm²</strong>")
    return q, s, "Segment area = sector area − triangle area; triangle area = ½r²sinθ", 4


def _mens_diff_similar_volume():
    k = random.choice([2, 3, 4])
    vol1 = random.randint(10, 50)
    vol2 = vol1 * k**3
    q = (f"Two similar cones have lengths in ratio 1 : {k}. "
         f"The smaller cone has volume {vol1} cm³. Find the volume of the larger cone.")
    s = (f"Length ratio = 1 : {k}<br>"
         f"Volume ratio = 1³ : {k}³ = 1 : {k**3}<br>"
         f"Volume of larger = {vol1} × {k**3}<br>"
         f"<strong>= {vol2} cm³</strong>")
    return q, s, "Volume scale factor = (length scale factor)³", 3


def _mens_diff_density_3d():
    density = round(random.uniform(2.0, 9.0), 1)
    r = random.randint(3, 8)
    h = random.randint(6, 18)
    vol = round(math.pi * r * r * h, 4)
    mass = round(density * vol, 2)
    q = (f"A solid cylinder has radius {r} cm, height {h} cm, and is made from a material "
         f"with density {density} g/cm³. Find the mass of the cylinder to 2 d.p.")
    s = (f"V = πr²h = π × {r}² × {h} = {round(vol,2)} cm³<br>"
         f"Mass = density × volume = {density} × {round(vol,2)}<br>"
         f"<strong>= {mass} g</strong>")
    return q, s, "Mass = density × volume; find volume first using V = πr²h", 4


def _mens_diff_sphere_submerged():
    sphere_r = random.randint(2, 5)
    cyl_r = sphere_r + random.randint(2, 5)
    vol_sphere = round(4/3 * math.pi * sphere_r**3, 4)
    rise = round(vol_sphere / (math.pi * cyl_r**2), 2)
    q = (f"A sphere of radius {sphere_r} cm is fully submerged in a cylinder of radius "
         f"{cyl_r} cm. By how much does the water level rise? Give your answer to 2 d.p.")
    s = (f"Volume displaced = volume of sphere = \\(\\frac{{4}}{{3}}\\pi \\times {sphere_r}^3\\) "
         f"= {round(vol_sphere,2)} cm³<br>"
         f"Rise = \\(\\dfrac{{\\text{{Volume}}}}{{\\pi r^2_{{cyl}}}} = "
         f"\\dfrac{{{round(vol_sphere,2)}}}{{\\pi \\times {cyl_r}^2}} = "
         f"\\dfrac{{{round(vol_sphere,2)}}}{{{round(math.pi*cyl_r**2,2)}}}\\)<br>"
         f"<strong>≈ {rise} cm</strong>")
    return q, s, "Rise = sphere volume ÷ (π × cylinder radius²)", 4


def _mens_diff_prism_composite_cross_section():
    a = random.randint(4, 8)
    b = random.randint(3, 6)
    h = random.randint(3, 7)
    length = random.randint(8, 20)
    # Cross-section: rectangle (a × h) on top of a triangle (base a, height b)
    cross_section = a * h + Fraction(a * b, 2)
    vol = cross_section * length
    q = (f"A prism has length {length} cm. Its cross-section is a compound shape: "
         f"a rectangle {a} cm wide and {h} cm tall, with a triangle of base {a} cm "
         f"and height {b} cm attached below. Find the volume of the prism.")
    s = (f"Cross-section area = rectangle + triangle<br>"
         f"= ({a} × {h}) + (½ × {a} × {b})<br>"
         f"= {a*h} + {Fraction(a*b,2)}<br>"
         f"= {cross_section} cm²<br>"
         f"Volume = {cross_section} × {length}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "Find cross-section area first (rectangle + triangle), then multiply by length", 5


def _mens_diff_find_height_from_volume():
    r = random.randint(2, 7)
    vol = random.randint(100, 800)
    h = round(vol / (math.pi * r * r), 2)
    q = (f"A cylinder has radius {r} cm and volume {vol} cm³. "
         f"Find the height of the cylinder to 2 d.p.")
    s = (f"V = πr²h<br>"
         f"\\(h = \\dfrac{{V}}{{\\pi r^2}} = \\dfrac{{{vol}}}{{\\pi \\times {r}^2}} = "
         f"\\dfrac{{{vol}}}{{{round(math.pi*r*r,4)}}}\\)<br>"
         f"<strong>= {h} cm</strong>")
    return q, s, "Rearrange V = πr²h → h = V/(πr²)", 3


def _mens_diff_arc_exact():
    r = random.randint(4, 12)
    angle = random.choice([90, 120, 60, 45])
    frac = Fraction(angle, 360)
    # Arc = (θ/360) × 2πr
    coeff = frac * 2 * r
    q = (f"Find the arc length of a sector with radius {r} cm and angle {angle}°. "
         f"Give your answer in terms of π.")
    s = (f"Arc = \\(\\dfrac{{{angle}}}{{360}} \\times 2\\pi \\times {r}\\)<br>"
         f"= \\({frac} \\times {2*r}\\pi\\)<br>"
         f"<strong>= {coeff}π cm</strong>")
    return q, s, "Simplify the fraction (θ/360) before multiplying", 3


def _mens_diff_cone_height_from_slant():
    r = random.randint(3, 9)
    slant = random.randint(r + 2, r + 12)
    h = round(math.sqrt(slant**2 - r**2), 2)
    vol = round(math.pi * r**2 * h / 3, 2)
    q = (f"A cone has base radius {r} cm and slant height {slant} cm. "
         f"Find the volume of the cone to 2 d.p.")
    s = (f"Height: h = \\(\\sqrt{{l^2 - r^2}} = \\sqrt{{{slant}^2 - {r}^2}} = "
         f"\\sqrt{{{slant**2} - {r**2}}} = \\sqrt{{{slant**2 - r**2}}} ≈ {h}\\) cm<br>"
         f"V = ⅓πr²h = ⅓ × π × {r}² × {h} = ⅓ × π × {r*r} × {h}<br>"
         f"<strong>= {vol} cm³</strong>")
    return q, s, "Use Pythagoras to find h = √(l²−r²), then V = ⅓πr²h", 4


def _mens_diff_surface_area_prism():
    a = random.randint(3, 7)
    b = random.randint(4, 9)
    c = round(math.sqrt(a*a + b*b), 2)
    length = random.randint(8, 18)
    # Right-triangle cross section: sides a, b, c
    tri_area = Fraction(a * b, 2)
    perimeter = a + b + c
    sa = round(2 * tri_area + perimeter * length, 2)
    q = (f"A triangular prism has a right-angle triangular cross-section with legs "
         f"{a} cm and {b} cm. The length of the prism is {length} cm. "
         f"Find the total surface area. Give your answer to 2 d.p.")
    s = (f"Hypotenuse = \\(\\sqrt{{{a}^2 + {b}^2}} = \\sqrt{{{a*a + b*b}}} = {c}\\) cm<br>"
         f"Triangle area = ½ × {a} × {b} = {tri_area} cm²<br>"
         f"Two triangular ends = 2 × {tri_area} = {2*tri_area} cm²<br>"
         f"Three rectangular faces: perimeter × length = ({a} + {b} + {c}) × {length} "
         f"= {round(perimeter,2)} × {length} = {round(perimeter*length,2)} cm²<br>"
         f"SA = {2*tri_area} + {round(perimeter*length,2)}<br>"
         f"<strong>= {sa} cm²</strong>")
    return q, s, "SA = 2 × (triangle area) + (perimeter of triangle) × length", 5


def _mens_diff_optimize_box():
    total = random.randint(150, 400)
    # Square-based box, open top: SA = x² + 4xh = total
    # For simplicity, give x and find h from SA constraint
    x = random.randint(5, 12)
    h = round((total - x*x) / (4 * x), 2)
    vol = round(x * x * h, 2)
    q = (f"An open-topped box has a square base of side {x} cm. The total surface area "
         f"of the box (base + four sides) is {total} cm². Find the height and volume of the box. "
         f"Give your answers to 2 d.p.")
    s = (f"SA = x² + 4xh<br>"
         f"{total} = {x}² + 4 × {x} × h<br>"
         f"{total} = {x*x} + {4*x}h<br>"
         f"{4*x}h = {total - x*x}<br>"
         f"h = {total - x*x} ÷ {4*x} = <strong>{h} cm</strong><br>"
         f"Volume = x²h = {x}² × {h} = {x*x} × {h}<br>"
         f"<strong>Volume = {vol} cm³</strong>")
    return q, s, "Write SA = x² + 4xh, substitute values, solve for h, then find volume", 5


# ---------- DIFFICULT (multi-step, real-world, a/b/c) ----------

def _mens_diff_silo_multipart():
    """Cylinder with hemisphere on top — volume, surface area, mass."""
    r = random.randint(3, 7)
    h = random.randint(10, 22)
    density = round(random.uniform(0.8, 2.5), 1)
    vol_cyl = math.pi * r * r * h
    vol_hemi = 2 / 3 * math.pi * r ** 3
    vol_total = round(vol_cyl + vol_hemi, 2)
    sa = round(2 * math.pi * r * h + 2 * math.pi * r * r, 2)
    mass = round(density * vol_total, 2)
    intro = (
        f"A grain silo is modelled as a cylinder of radius {r} m and height {h} m "
        f"with a hemisphere of the same radius on top. The grain has density {density} tonnes/m³ "
        f"(1 tonne = 1000 kg; treat volume in m³)."
    )
    q = intro + _mens_abc_block(
        "Find the total volume of the silo in m³ to 2 d.p.",
        "Find the outer surface area to 2 d.p. (include the curved surfaces only — no base).",
        "Find the mass of grain when the silo is full, in tonnes to 2 d.p.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Cylinder: \(\pi r^2 h = \pi \times {r}^2 \times {h} = {round(vol_cyl, 2)}\) m³<br>"
        rf"Hemisphere: \(\dfrac{{2}}{{3}}\pi r^3 = {round(vol_hemi, 2)}\) m³<br>"
        rf"Total volume = <strong>{vol_total} m³</strong><br>"
        rf"<strong>b)</strong> Curved cylinder + curved hemisphere = \(2\pi rh + 2\pi r^2\)<br>"
        rf"= 2π × {r} × {h} + 2π × {r}² = <strong>{sa} m²</strong><br>"
        rf"<strong>c)</strong> Mass = {density} × {vol_total} = <strong>{mass} tonnes</strong>"
    )
    hint = "Add cylinder and hemisphere volumes; outer SA = curved cylinder + curved hemisphere; mass = density × volume."
    return q, s, hint, 5


def _mens_diff_similar_prisms_multipart():
    """Similar prisms — scale factor, surface-area ratio, larger volume."""
    k = random.choice([2, 3])
    l1 = random.randint(4, 8)
    w1 = random.randint(3, 6)
    h1 = random.randint(5, 10)
    sa1 = 2 * (l1 * w1 + l1 * h1 + w1 * h1)
    vol1 = l1 * w1 * h1
    sa2 = sa1 * k * k
    vol2 = vol1 * k ** 3
    intro = (
        f"Two similar cuboid boxes have corresponding lengths in ratio 1 : {k}. "
        f"The smaller box measures {l1} cm × {w1} cm × {h1} cm."
    )
    q = intro + _mens_abc_block(
        "Write down the length scale factor from the smaller box to the larger box.",
        f"The total surface area of the smaller box is {sa1} cm². Find the surface area of the larger box.",
        f"The volume of the smaller box is {vol1} cm³. Find the volume of the larger box.",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> Length scale factor = <strong>{k}</strong><br>"
        rf"<strong>b)</strong> Area scale factor = {k}² = {k*k}<br>"
        rf"Larger SA = {sa1} × {k*k} = <strong>{sa2} cm²</strong><br>"
        rf"<strong>c)</strong> Volume scale factor = {k}³ = {k**3}<br>"
        rf"Larger volume = {vol1} × {k**3} = <strong>{vol2} cm³</strong>"
    )
    hint = "Lengths scale by k; areas by k²; volumes by k³."
    return q, s, hint, 5


def _mens_diff_frustum_tank_multipart():
    """Frustum — set up volume, calculate, partial fill in litres."""
    R = random.randint(6, 10)
    r = random.randint(3, R - 2)
    h = random.randint(8, 16)
    fill_pct = random.choice([60, 75, 80])
    vol_full = math.pi * h / 3 * (R * R + R * r + r * r)
    vol_full = round(vol_full, 2)
    vol_part = round(vol_full * fill_pct / 100, 2)
    litres = round(vol_part / 1000, 2)
    intro = (
        f"A bucket is modelled as a frustum with top radius {R} cm, bottom radius {r} cm, "
        f"and perpendicular height {h} cm."
    )
    q = intro + _mens_abc_block(
        "Write down the formula for the volume of a frustum and substitute the given radii and height.",
        "Calculate the full volume of the bucket to 2 d.p.",
        f"The bucket is filled to {fill_pct}% of its capacity. Find the volume of water in litres to 2 d.p. (1000 cm³ = 1 litre).",
    )
    s = (
        rf"{intro}<br>"
        rf"<strong>a)</strong> \(V = \dfrac{{\pi h}}{{3}}(R^2 + Rr + r^2)\)<br>"
        rf"= \(\dfrac{{\pi \times {h}}}{{3}}({R}^2 + {R}\times{r} + {r}^2)\)<br>"
        rf"<strong>b)</strong> \(= \dfrac{{\pi \times {h}}}{{3}} \times {R*R + R*r + r*r} = {vol_full}\) cm³<br>"
        rf"<strong>Full volume = {vol_full} cm³</strong><br>"
        rf"<strong>c)</strong> {fill_pct}% of {vol_full} = {vol_part} cm³ = {vol_part/1000:.4f} litres<br>"
        rf"<strong>= {litres} litres</strong>"
    )
    hint = "Use V = (πh/3)(R² + Rr + r²); for part (c) find the percentage of the volume then convert cm³ to litres."
    return q, s, hint, 5


# ══════════════════════════════════════════════════════════════════════════════
# MCQ (18 questions)
# ══════════════════════════════════════════════════════════════════════════════

_MENS_MCQ_BANK = [
    {   # 1 – area of triangle
        "q": r"A triangle has base 10 cm and perpendicular height 6 cm. What is its area?",
        "opts": ["A  30 cm²", "B  60 cm²", "C  45 cm²", "D  15 cm²"],
        "ans": "A",
        "sol": r"Area = ½ × base × height = ½ × 10 × 6 = <strong>30 cm²</strong>. Answer: A",
        "hint": "Area = ½ × b × h",
        "marks": 1,
    },
    {   # 2 – circumference
        "q": r"A circle has diameter 14 cm. What is its circumference to 2 d.p.?",
        "opts": ["A  43.98 cm", "B  153.94 cm", "C  87.96 cm", "D  21.99 cm"],
        "ans": "A",
        "sol": r"C = πd = π × 14 ≈ <strong>43.98 cm</strong>. Answer: A",
        "hint": "C = πd",
        "marks": 1,
    },
    {   # 3 – volume of cuboid
        "q": r"Find the volume of a cuboid measuring 5 cm × 3 cm × 4 cm.",
        "opts": ["A  60 cm³", "B  94 cm²", "C  47 cm³", "D  120 cm³"],
        "ans": "A",
        "sol": r"V = 5 × 3 × 4 = <strong>60 cm³</strong>. Answer: A",
        "hint": "V = l × w × h",
        "marks": 1,
    },
    {   # 4 – area of circle (exact)
        "q": r"A circle has radius 6 cm. Which expression gives its exact area?",
        "opts": [r"A  36π cm²", r"B  12π cm²", r"C  6π cm²", r"D  72π cm²"],
        "ans": "A",
        "sol": r"A = πr² = π × 6² = <strong>36π cm²</strong>. Answer: A",
        "hint": "A = πr²",
        "marks": 1,
    },
    {   # 5 – trapezium area
        "q": r"A trapezium has parallel sides 8 cm and 12 cm, and height 5 cm. Find the area.",
        "opts": ["A  50 cm²", "B  100 cm²", "C  40 cm²", "D  60 cm²"],
        "ans": "A",
        "sol": r"Area = ½(8+12)×5 = ½×20×5 = <strong>50 cm²</strong>. Answer: A",
        "hint": "Area = ½(a+b)h",
        "marks": 1,
    },
    {   # 6 – volume of cylinder
        "q": r"A cylinder has radius 4 cm and height 10 cm. What is its volume to 2 d.p.?",
        "opts": ["A  502.65 cm³", "B  251.33 cm³", "C  160.00 cm³", "D  1005.31 cm³"],
        "ans": "A",
        "sol": r"V = πr²h = π × 16 × 10 ≈ <strong>502.65 cm³</strong>. Answer: A",
        "hint": "V = πr²h",
        "marks": 2,
    },
    {   # 7 – volume of sphere
        "q": r"A sphere has radius 3 cm. What is its volume to 2 d.p.?",
        "opts": ["A  113.10 cm³", "B  56.55 cm³", "C  339.29 cm³", "D  37.70 cm³"],
        "ans": "A",
        "sol": r"V = (4/3)πr³ = (4/3)π×27 ≈ <strong>113.10 cm³</strong>. Answer: A",
        "hint": "V = (4/3)πr³",
        "marks": 2,
    },
    {   # 8 – surface area of sphere
        "q": r"A sphere has radius 5 cm. Find its surface area to 2 d.p.",
        "opts": ["A  314.16 cm²", "B  523.60 cm²", "C  157.08 cm²", "D  628.32 cm²"],
        "ans": "A",
        "sol": r"SA = 4πr² = 4π×25 ≈ <strong>314.16 cm²</strong>. Answer: A",
        "hint": "SA = 4πr²",
        "marks": 2,
    },
    {   # 9 – sector area
        "q": r"A sector has radius 8 cm and angle 90°. Find the area to 2 d.p.",
        "opts": ["A  50.27 cm²", "B  100.53 cm²", "C  25.13 cm²", "D  201.06 cm²"],
        "ans": "A",
        "sol": r"A = (90/360)×π×64 = ¼×64π ≈ <strong>50.27 cm²</strong>. Answer: A",
        "hint": "Sector area = (θ/360)×πr²",
        "marks": 2,
    },
    {   # 10 – surface area of cuboid
        "q": r"Find the surface area of a cuboid with length 6 cm, width 4 cm, height 3 cm.",
        "opts": ["A  108 cm²", "B  72 cm²", "C  54 cm²", "D  216 cm²"],
        "ans": "A",
        "sol": r"SA = 2(lw+lh+wh) = 2(24+18+12) = 2×54 = <strong>108 cm²</strong>. Answer: A",
        "hint": "SA = 2(lw + lh + wh)",
        "marks": 2,
    },
    {   # 11 – volume of cone
        "q": r"A cone has base radius 6 cm and height 9 cm. What is its volume to 2 d.p.?",
        "opts": ["A  339.29 cm³", "B  1017.88 cm³", "C  113.10 cm³", "D  678.58 cm³"],
        "ans": "A",
        "sol": r"V = ⅓πr²h = ⅓×π×36×9 = ⅓×π×324 ≈ <strong>339.29 cm³</strong>. Answer: A",
        "hint": "V = (1/3)πr²h",
        "marks": 2,
    },
    {   # 12 – arc length
        "q": r"A sector has radius 10 cm and angle 120°. What is the arc length to 2 d.p.?",
        "opts": ["A  20.94 cm", "B  41.89 cm", "C  10.47 cm", "D  62.83 cm"],
        "ans": "A",
        "sol": r"Arc = (120/360)×2π×10 = ⅓×20π ≈ <strong>20.94 cm</strong>. Answer: A",
        "hint": "Arc = (θ/360)×2πr",
        "marks": 2,
    },
    {   # 13 – similar volume
        "q": r"Two similar cylinders have radii in ratio 1 : 3. The smaller has volume 20 cm³. Find the larger volume.",
        "opts": ["A  540 cm³", "B  180 cm³", "C  60 cm³", "D  1620 cm³"],
        "ans": "A",
        "sol": r"Volume ratio = 1³ : 3³ = 1 : 27. Larger = 20 × 27 = <strong>540 cm³</strong>. Answer: A",
        "hint": "Volume scale factor = (length scale factor)³",
        "marks": 3,
    },
    {   # 14 – density
        "q": r"A spherical ball has radius 4 cm and is made of rubber with density 1.2 g/cm³. Find its mass to 2 d.p.",
        "opts": ["A  321.70 g", "B  241.27 g", "C  964.51 g", "D  804.25 g"],
        "ans": "A",
        "sol": r"V = (4/3)π×64 ≈ 268.08 cm³. Mass = 1.2 × 268.08 ≈ <strong>321.70 g</strong>. Answer: A",
        "hint": "Find volume of sphere, then mass = density × volume",
        "marks": 3,
    },
    {   # 15 – frustum volume
        "q": r"A frustum has large radius 6 cm, small radius 2 cm, and height 9 cm. Find its volume to 2 d.p.",
        "opts": ["A  488.69 cm³", "B  678.58 cm³", "C  244.35 cm³", "D  339.29 cm³"],
        "ans": "A",
        "sol": r"V = (π×9/3)(36+12+4) = 3π×52 ≈ <strong>488.69 cm³</strong>. Answer: A",
        "hint": "V = (πh/3)(R²+Rr+r²)",
        "marks": 3,
    },
    {
        "q": r"A silo is a cylinder of radius 4 m and height 10 m with a hemisphere of radius 4 m on top (no base). Find the total volume to 2 d.p.",
        "opts": ["A  636.61 m³", "B  502.65 m³", "C  804.25 m³", "D  335.10 m³"],
        "ans": "A",
        "sol": (r"Cylinder: \(\pi r^2 h = \pi \times 16 \times 10 = 160\pi\) m³.<br>"
                r"Hemisphere: \(\frac{2}{3}\pi r^3 = \frac{128\pi}{3}\) m³.<br>"
                r"Total = \(160\pi + \frac{128\pi}{3} = \frac{608\pi}{3} \approx\) <strong>636.61 m³</strong>. Answer: A"),
        "hint": "Add cylinder volume and hemisphere volume (⅔πr³).",
        "marks": 3,
        "difficulty": "difficult",
    },
    {
        "q": r"A cone has base radius 5 cm and perpendicular height 12 cm. Find its total surface area to 2 d.p.",
        "opts": ["A  282.74 cm²", "B  204.20 cm²", "C  157.08 cm²", "D  439.82 cm²"],
        "ans": "A",
        "sol": (r"Slant height \(l = \sqrt{5^2 + 12^2} = 13\) cm.<br>"
                r"TSA = \(\pi r l + \pi r^2 = \pi \times 5 \times 13 + \pi \times 25 = 90\pi \approx\) "
                r"<strong>282.74 cm²</strong>. Answer: A"),
        "hint": "Find slant height with Pythagoras; TSA = curved area + base area.",
        "marks": 3,
        "difficulty": "difficult",
    },
    {
        "q": r"Two similar solids have corresponding lengths in ratio 2 : 3. The smaller has surface area 48 cm². Find the surface area of the larger solid.",
        "opts": ["A  108 cm²", "B  72 cm²", "C  162 cm²", "D  32 cm²"],
        "ans": "A",
        "sol": (r"Area scale factor = \(\left(\frac{3}{2}\right)^2 = \frac{9}{4}\).<br>"
                r"Larger SA = \(48 \times \frac{9}{4} =\) <strong>108 cm²</strong>. Answer: A"),
        "hint": "Surface areas scale with the square of the linear scale factor.",
        "marks": 3,
        "difficulty": "difficult",
    },
]


def mensuration_mcq():
    item = random.choice(_MENS_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def gcse_mensuration_variants(difficulty, mode='practice'):
    if mode == 'mcq':
        return mcq_variants_from_bank_with_procedural(
            _MENS_MCQ_BANK, procedural_mcq_for('mensuration'), 'mensuration', difficulty
        )

    if difficulty == 'foundational':
        pool = [
            _mens_found_rect_area,
            _mens_found_rect_perimeter,
            _mens_found_triangle_area,
            _mens_found_parallelogram_area,
            _mens_found_trapezium_area,
            _mens_found_circle_circumference,
            _mens_found_circle_area,
            _mens_found_cuboid_volume,
            _mens_found_cuboid_surface_area,
            _mens_found_triangular_prism_vol,
            _mens_found_compound_area_L,
            _mens_found_area_to_length,
            _mens_found_unit_conversion_area,
            _mens_found_density,
            _mens_found_diameter_from_circumference,
        ]
    elif difficulty == 'intermediate':
        pool = [
            _mens_inter_arc_length,
            _mens_inter_sector_area,
            _mens_inter_cylinder_volume,
            _mens_inter_cylinder_surface_area,
            _mens_inter_cone_volume,
            _mens_inter_sphere_volume,
            _mens_inter_sphere_surface_area,
            _mens_inter_pyramid_volume,
            _mens_inter_annulus_area,
            _mens_inter_perimeter_sector,
            _mens_inter_cone_surface_area,
            _mens_inter_find_radius_from_area,
            _mens_inter_rate_fill,
            _mens_inter_similar_area,
            _mens_inter_composite_cylinder_hemisphere,
            _mens_inter_cylinder_tank_multipart,
            _mens_inter_garden_plot_multipart,
            _mens_inter_cone_container_multipart,
        ]
    elif difficulty == 'difficult':
        pool = [
            _mens_diff_cone_slant_from_height,
            _mens_diff_sphere_radius_from_volume,
            _mens_diff_exact_pi_answer,
            _mens_diff_frustum_volume,
            _mens_diff_hemisphere_cone_surface_area,
            _mens_diff_sector_minus_triangle,
            _mens_diff_similar_volume,
            _mens_diff_density_3d,
            _mens_diff_sphere_submerged,
            _mens_diff_prism_composite_cross_section,
            _mens_diff_find_height_from_volume,
            _mens_diff_arc_exact,
            _mens_diff_cone_height_from_slant,
            _mens_diff_surface_area_prism,
            _mens_diff_optimize_box,
            _mens_diff_silo_multipart,
            _mens_diff_similar_prisms_multipart,
            _mens_diff_frustum_tank_multipart,
        ]
    else:  # mixed
        found = random.sample([
            _mens_found_rect_area, _mens_found_triangle_area,
            _mens_found_circle_area, _mens_found_cuboid_volume,
        ], 4)
        inter = random.sample([
            _mens_inter_arc_length, _mens_inter_cylinder_volume,
            _mens_inter_sphere_volume, _mens_inter_sector_area,
            _mens_inter_cone_volume, _mens_inter_similar_area,
        ], 4)
        diff = random.sample([
            _mens_diff_cone_slant_from_height, _mens_diff_frustum_volume,
            _mens_diff_hemisphere_cone_surface_area, _mens_diff_similar_volume,
        ], 2)
        return found + inter + diff

    return select_tier_variants(pool)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN GENERATOR FUNCTION  (mirrors gcse_vectors exactly)
# ══════════════════════════════════════════════════════════════════════════════

def gcse_mensuration(difficulty, mode, variant_name=None):
    if mode == 'mcq':
        variants = gcse_mensuration_variants(difficulty, 'mcq')
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = run_mcq_variant(
            variants, variant_name
        )
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            'gcse', 'maths', 'mensuration',
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_mensuration_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        'gcse', 'maths', 'mensuration',
    )
