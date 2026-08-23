"""Shared SVG diagram primitives (Phase U5, docs/UI_REDESIGN.md §8.2–8.3).

Importable from generators and exposed as a Jinja global. U5.2 draws the
mensuration solids; U5.3 adds charts, formula triangles, fitted geometry, and v–t graphs;
U5.4 wraps remaining GCSE geometry generators (angles, bearings, circle theorems,
trig/vectors, graphical simultaneous equations) through the same root; U5.5 adds
pie charts, Venn diagrams, and probability trees plus constructions/loci wrappers.
"""
from __future__ import annotations

import html
import math
from itertools import count

from markupsafe import Markup

# Hex values copied from static/css/tokens.css so generator fragments stay
# aligned with the semantic palette even when CSS variables are unavailable.
PALETTE = {
    'ink': '#1c2430',          # --ink-800 / --text
    'ink_muted': '#64748b',    # --ink-500
    'brand': '#1a86d4',        # --brand-500
    'brand_soft': '#dbeefd',   # --brand-100
    'brand_mid': '#b9dffb',    # --brand-200
    'brand_pale': '#eff8ff',   # --brand-50
    'brand_edge': '#86c9f6',   # --brand-300
    'measure': '#ef4444',      # --wrong-500 (dimension labels + measure lines)
    'success': '#16a34a',      # --correct-500 (secondary leg / positive quantity)
    'hidden': '#94a3b8',       # --ink-400 (dashed hidden edges)
    'surface': '#ffffff',      # --surface
    'fill': '#dbeefd',         # --brand-100 (shape fill)
    'cyl_left': '#b9dffb',     # --brand-200 (body gradient, §8.3)
    'cyl_mid': '#eff8ff',      # --brand-50
    'cyl_right': '#86c9f6',    # --brand-300
}

STROKE_OUTLINE = 2
STROKE_MEASURE = 1.5
STROKE_HIDDEN = 1
FONT_SIZE = 14
FONT_WEIGHT = 600
FONT_FAMILY = 'Work Sans, system-ui, sans-serif'

_UID = count(1)


def _esc(text) -> str:
    return html.escape(str(text), quote=True)


def _num(value) -> str:
    if isinstance(value, float):
        value = round(value, 2)
        if value.is_integer():
            return str(int(value))
        return f'{value:g}'
    return str(value)


def _text(x, y, text, *, fill, anchor='middle'):
    """Label with §8.2 typography. ``text-anchor`` is always explicit."""
    if anchor not in ('start', 'middle', 'end'):
        raise ValueError(f'invalid text-anchor: {anchor!r}')
    return (
        f'<text x="{_num(x)}" y="{_num(y)}" fill="{fill}" font-size="{FONT_SIZE}" '
        f'font-weight="{FONT_WEIGHT}" font-family="{FONT_FAMILY}" '
        f'text-anchor="{anchor}">{_esc(text)}</text>'
    )


def shape_label(x, y, text, *, anchor='middle'):
    """Ink label for a shape name or vertex."""
    return _text(x, y, text, fill=PALETTE['ink'], anchor=anchor)


def measure_label(x, y, text, *, anchor='middle'):
    """Red-accent label for a length, radius, or angle."""
    return _text(x, y, text, fill=PALETTE['measure'], anchor=anchor)


def _shared_defs(ids: dict) -> str:
    p = PALETTE
    return (
        f'<defs>'
        f'<linearGradient id="{ids["body"]}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{p["cyl_left"]}"/>'
        f'<stop offset="50%" stop-color="{p["cyl_mid"]}"/>'
        f'<stop offset="100%" stop-color="{p["cyl_right"]}"/>'
        f'</linearGradient>'
        f'<linearGradient id="{ids["top"]}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{p["brand_pale"]}"/>'
        f'<stop offset="100%" stop-color="{p["brand_soft"]}"/>'
        f'</linearGradient>'
        f'<radialGradient id="{ids["shade"]}" cx="34%" cy="30%" r="68%">'
        f'<stop offset="0%" stop-color="{p["brand_pale"]}"/>'
        f'<stop offset="55%" stop-color="{p["brand_mid"]}"/>'
        f'<stop offset="100%" stop-color="{p["brand_edge"]}"/>'
        f'</radialGradient>'
        f'<marker id="{ids["arrow"]}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{p["measure"]}"/>'
        f'</marker>'
        f'</defs>'
    )


def viewbox_svg(min_x, min_y, width, height, *, title, desc=None, body, max_width=360, variant=''):
    """Accessible SVG root with an explicit viewBox origin.

    Sizing is CSS; never a fixed pixel width attribute. ``body`` may be an SVG
    markup string, or a callable ``body(ids) -> str`` that receives unique
    gradient/marker ids from the shared ``<defs>``. Decorative geometry is
    wrapped in ``aria-hidden`` so ``<title>``/``<desc>`` are the accessible name.
    """
    title = str(title or '').strip()
    if not title:
        raise ValueError('viewbox_svg() requires a non-empty title')
    desc_text = str(desc).strip() if desc else title
    uid = next(_UID)
    ids = {
        'body': f'sk-body-{uid}',
        'top': f'sk-top-{uid}',
        'shade': f'sk-shade-{uid}',
        'arrow': f'sk-arrow-{uid}',
        'title': f'sk-title-{uid}',
        'desc': f'sk-desc-{uid}',
    }
    if callable(body):
        inner = body(ids)
    else:
        inner = '' if body is None else str(body)
    max_w = f'{int(max_width)}px' if isinstance(max_width, (int, float)) else str(max_width)
    classes = 'svg-kit'
    if variant:
        classes += f' svg-kit--{variant}'
    root = (
        f'<svg role="img" class="{classes}" xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{_num(min_x)} {_num(min_y)} {_num(width)} {_num(height)}" '
        f'preserveAspectRatio="xMidYMid meet" '
        f'style="width:100%;max-width:{max_w};height:auto;display:block" '
        f'aria-labelledby="{ids["title"]}" aria-describedby="{ids["desc"]}">'
        f'<title id="{ids["title"]}">{_esc(title)}</title>'
        f'<desc id="{ids["desc"]}">{_esc(desc_text)}</desc>'
        f'{_shared_defs(ids)}'
        f'<g aria-hidden="true">{inner}</g>'
        f'</svg>'
    )
    return Markup(root)


def svg(width, height, *, title, desc=None, body, max_width=360, variant=''):
    """Accessible SVG root with viewBox origin at (0, 0)."""
    return viewbox_svg(
        0, 0, width, height,
        title=title, desc=desc, body=body, max_width=max_width, variant=variant,
    )


def fitted_svg(bounds_x, bounds_y, *, title, desc=None, body, pad=12, max_width=260, variant=''):
    """Accessible SVG with a content-tight viewBox (not anchored at 0,0)."""
    xs = list(bounds_x)
    ys = list(bounds_y)
    min_x = min(xs) - pad
    max_x = max(xs) + pad
    min_y = min(ys) - pad
    max_y = max(ys) + pad
    vw = max(max_x - min_x, 48)
    vh = max(max_y - min_y, 48)
    return viewbox_svg(
        min_x, min_y, vw, vh,
        title=title, desc=desc, body=body, max_width=max_width, variant=variant,
    )


def _arc(x1, y1, rx, ry, x2, y2, *, sweep, stroke, width, dashed=False, fill='none'):
    dash = ' stroke-dasharray="5 4"' if dashed else ''
    return (
        f'<path d="M{_num(x1)} {_num(y1)} A{_num(rx)} {_num(ry)} 0 0 {int(sweep)} '
        f'{_num(x2)} {_num(y2)}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{width}" stroke-linecap="round"{dash}/>'
    )


def _measure_v(x, y1, y2, label, ids, *, label_dx=10, label_anchor='start'):
    p = PALETTE
    tick = 5
    mid_y = (float(y1) + float(y2)) / 2 + 5
    return (
        f'<line x1="{_num(x - tick)}" y1="{_num(y1)}" x2="{_num(x + tick)}" y2="{_num(y1)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}"/>'
        f'<line x1="{_num(x - tick)}" y1="{_num(y2)}" x2="{_num(x + tick)}" y2="{_num(y2)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}"/>'
        f'<line x1="{_num(x)}" y1="{_num(y1)}" x2="{_num(x)}" y2="{_num(y2)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}" '
        f'marker-start="url(#{ids["arrow"]})" marker-end="url(#{ids["arrow"]})"/>'
        f'{measure_label(x + label_dx, mid_y, label, anchor=label_anchor)}'
    )


def _measure_h(x1, x2, y, label, ids, *, label_dy=-8):
    p = PALETTE
    tick = 5
    mid_x = (float(x1) + float(x2)) / 2
    label_y = float(y) + label_dy
    return (
        f'<line x1="{_num(x1)}" y1="{_num(y - tick)}" x2="{_num(x1)}" y2="{_num(y + tick)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}"/>'
        f'<line x1="{_num(x2)}" y1="{_num(y - tick)}" x2="{_num(x2)}" y2="{_num(y + tick)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}"/>'
        f'<line x1="{_num(x1)}" y1="{_num(y)}" x2="{_num(x2)}" y2="{_num(y)}" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}" '
        f'marker-start="url(#{ids["arrow"]})" marker-end="url(#{ids["arrow"]})"/>'
        f'{measure_label(mid_x, label_y, label)}'
    )


def _caption(cx, y, text):
    if not text:
        return ''
    return shape_label(cx, y, text)


# ---------------------------------------------------------------------------
# Styleguide samples
# ---------------------------------------------------------------------------

def demo_strokes(*, title='Stroke and label sample'):
    """Styleguide sample: 2px outline, 1.5px measure, 1px dashed hidden, labels."""
    p = PALETTE

    def body(_ids):
        return (
            f'<rect x="40" y="28" width="120" height="64" fill="{p["fill"]}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'<line x1="40" y1="104" x2="160" y2="104" stroke="{p["measure"]}" '
            f'stroke-width="{STROKE_MEASURE}"/>'
            f'<line x1="40" y1="28" x2="160" y2="28" stroke="{p["hidden"]}" '
            f'stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
            f'{shape_label(100, 64, "shape")}'
            f'{measure_label(100, 122, "12 cm")}'
        )

    return svg(
        200,
        140,
        title=title,
        desc='A rectangle with a 2px outline, a 1.5px measurement line, a 1px dashed hidden edge, an ink shape label, and a red measurement label.',
        body=body,
        max_width=280,
    )


def demo_gradient(*, title='Shared body gradient'):
    """Styleguide sample: the reusable left-to-right solid-body gradient."""

    def body(ids):
        return (
            f'<rect x="28" y="24" width="144" height="80" rx="8" '
            f'fill="url(#{ids["body"]})" stroke="{PALETTE["brand"]}" '
            f'stroke-width="{STROKE_OUTLINE}"/>'
            f'{shape_label(100, 70, "defs")}'
        )

    return svg(
        200,
        128,
        title=title,
        desc='Rectangle filled with the shared svg_kit body gradient used by solid primitives.',
        body=body,
        max_width=280,
    )


def _stub(name, title, desc=None):
    """Placeholder primitive. Still uses the svg() wrapper."""
    p = PALETTE

    def body(_ids):
        return (
            f'<rect x="28" y="32" width="144" height="72" rx="8" fill="{p["fill"]}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'<line x1="28" y1="116" x2="172" y2="116" stroke="{p["measure"]}" '
            f'stroke-width="{STROKE_MEASURE}"/>'
            f'{shape_label(100, 74, name)}'
        )

    return svg(
        200,
        140,
        title=title,
        desc=desc or f'Placeholder for the {name} primitive.',
        body=body,
        max_width=200,
    )


# ---------------------------------------------------------------------------
# U5.2 mensuration solids
# ---------------------------------------------------------------------------

def cylinder(
    r_label='r',
    h_label='h',
    *,
    shaded=True,
    caption=None,
    scale=1,
    max_width=200,
    title=None,
    desc=None,
):
    """Textbook cylinder: body gradient, dashed hidden base, top highlight, r/h."""
    p = PALETTE
    s = float(scale)
    rx, ry, body_h = 50 * s, 14 * s, 86 * s
    pad_l, pad_r, pad_t, pad_b = 20, 92, 44, 28 if caption else 20
    cx = pad_l + rx
    top_cy = pad_t + ry
    bot_cy = top_cy + body_h
    left, right = cx - rx, cx + rx
    width = pad_l + 2 * rx + pad_r
    height = bot_cy + ry + pad_b

    def body(ids):
        fill_body = f'url(#{ids["body"]})' if shaded else p['fill']
        fill_top = f'url(#{ids["top"]})' if shaded else p['brand_pale']
        return (
            f'<path d="M{_num(left)} {_num(top_cy)} L{_num(left)} {_num(bot_cy)} '
            f'A{_num(rx)} {_num(ry)} 0 0 1 {_num(right)} {_num(bot_cy)} '
            f'L{_num(right)} {_num(top_cy)} Z" fill="{fill_body}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_arc(left, bot_cy, rx, ry, right, bot_cy, sweep=0, stroke=p["hidden"], width=STROKE_HIDDEN, dashed=True)}'
            f'<ellipse cx="{_num(cx)}" cy="{_num(top_cy)}" rx="{_num(rx)}" ry="{_num(ry)}" '
            f'fill="{fill_top}" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_arc(cx - rx * 0.72, top_cy - ry * 0.35, rx * 0.42, ry * 0.55, cx - rx * 0.12, top_cy - ry * 0.92, sweep=1, stroke=p["surface"], width=1.5)}'
            f'{_measure_h(cx, right, top_cy, r_label, ids, label_dy=-10)}'
            f'{_measure_v(right + 18, top_cy, bot_cy, h_label, ids)}'
            f'{_caption(cx, height - 10, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Cylinder with radius {r_label} and height {h_label}',
        desc=desc or (
            f'A 3D cylinder. The curved body is shaded, the back of the base is dashed, '
            f'and the radius {r_label} and height {h_label} are labelled.'
        ),
        body=body,
        max_width=max_width,
    )


def cone(
    r_label='r',
    h_label='h',
    *,
    slant_label=None,
    shaded=True,
    caption=None,
    scale=1,
    max_width=200,
    title=None,
    desc=None,
):
    """Cone: gradient body, dashed hidden base, outside h, optional slant l."""
    p = PALETTE
    s = float(scale)
    rx, ry, body_h = 50 * s, 14 * s, 96 * s
    pad_l, pad_r, pad_t, pad_b = 20, 92, 36, 28 if caption else 20
    cx = pad_l + rx
    apex_y = pad_t
    base_cy = apex_y + body_h
    left, right = cx - rx, cx + rx
    width = pad_l + 2 * rx + pad_r
    height = base_cy + ry + pad_b

    def body(ids):
        fill_body = f'url(#{ids["body"]})' if shaded else p['fill']
        fill_base = p['brand_mid'] if shaded else p['fill']
        parts = [
            f'<path d="M{_num(cx)} {_num(apex_y)} L{_num(left)} {_num(base_cy)} '
            f'A{_num(rx)} {_num(ry)} 0 0 1 {_num(right)} {_num(base_cy)} Z" '
            f'fill="{fill_body}" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}" '
            f'stroke-linejoin="round"/>',
            _arc(left, base_cy, rx, ry, right, base_cy, sweep=0, stroke=p['hidden'], width=STROKE_HIDDEN, dashed=True),
            f'<path d="M{_num(left)} {_num(base_cy)} A{_num(rx)} {_num(ry)} 0 0 1 {_num(right)} {_num(base_cy)}" '
            f'fill="{fill_base}" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>',
            _measure_h(cx, right, base_cy + ry + 2, r_label, ids, label_dy=16),
            _measure_v(right + 18, apex_y, base_cy, h_label, ids),
        ]
        if slant_label:
            mx = (cx + right) / 2 + 8
            my = (apex_y + base_cy) / 2
            parts.append(measure_label(mx, my, slant_label, anchor='start'))
        parts.append(_caption(cx, height - 10, caption))
        return ''.join(parts)

    return svg(
        width,
        height,
        title=title or f'Cone with radius {r_label} and height {h_label}',
        desc=desc or (
            f'A 3D cone. The back of the base is dashed, and the radius {r_label} '
            f'and perpendicular height {h_label} are labelled.'
        ),
        body=body,
        max_width=max_width,
    )


def sphere(r_label='r', *, caption=None, max_width=180, title=None, desc=None):
    """Sphere with equatorial ellipse (front solid, back dashed) and radius."""
    p = PALETTE
    r = 48
    pad_l, pad_t, pad_b = 24, 36, 24 if caption else 16
    cx = pad_l + r
    cy = pad_t + r
    width = cx + r + 28
    height = cy + r + (28 if caption else 16)
    ry = r * 0.28

    def body(ids):
        return (
            f'<circle cx="{_num(cx)}" cy="{_num(cy)}" r="{_num(r)}" '
            f'fill="url(#{ids["shade"]})" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_arc(cx - r, cy, r, ry, cx + r, cy, sweep=0, stroke=p["hidden"], width=STROKE_HIDDEN, dashed=True)}'
            f'{_arc(cx - r, cy, r, ry, cx + r, cy, sweep=1, stroke=p["brand"], width=STROKE_OUTLINE)}'
            f'{_arc(cx - r * 0.55, cy - r * 0.55, r * 0.35, r * 0.22, cx - r * 0.08, cy - r * 0.78, sweep=1, stroke=p["surface"], width=1.5)}'
            f'{_measure_h(cx, cx + r, cy, r_label, ids, label_dy=-10)}'
            f'{_caption(cx, height - 8, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Sphere with radius {r_label}',
        desc=desc or f'A sphere. The equator is shown with a dashed hidden back edge, and the radius {r_label} is labelled.',
        body=body,
        max_width=max_width,
    )


def cuboid(
    l_label='l',
    w_label='w',
    h_label='h',
    *,
    caption=None,
    max_width=200,
    title=None,
    desc=None,
):
    """Isometric cuboid with dashed hidden edges and l/w/h measure labels."""
    p = PALETTE
    length, tall = 100, 72
    ox, oy = 38, 22
    x0, y_top = 40, 48
    ftl, ftr = (x0, y_top), (x0 + length, y_top)
    fbl, fbr = (x0, y_top + tall), (x0 + length, y_top + tall)
    btl, btr = (x0 + ox, y_top - oy), (x0 + length + ox, y_top - oy)
    bbl, bbr = (x0 + ox, y_top + tall - oy), (x0 + length + ox, y_top + tall - oy)
    width = btr[0] + 28
    height = fbl[1] + (36 if caption else 24)

    def poly(pts, fill):
        points = ' '.join(f'{_num(x)},{_num(y)}' for x, y in pts)
        return (
            f'<polygon points="{points}" fill="{fill}" stroke="{p["brand"]}" '
            f'stroke-width="{STROKE_OUTLINE}" stroke-linejoin="round"/>'
        )

    def body(_ids):
        hidden = (
            f'<line x1="{_num(btl[0])}" y1="{_num(btl[1])}" x2="{_num(bbl[0])}" y2="{_num(bbl[1])}" '
            f'stroke="{p["hidden"]}" stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
            f'<line x1="{_num(fbl[0])}" y1="{_num(fbl[1])}" x2="{_num(bbl[0])}" y2="{_num(bbl[1])}" '
            f'stroke="{p["hidden"]}" stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
            f'<line x1="{_num(bbl[0])}" y1="{_num(bbl[1])}" x2="{_num(bbr[0])}" y2="{_num(bbr[1])}" '
            f'stroke="{p["hidden"]}" stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
        )
        return (
            poly((ftl, ftr, btr, btl), p['brand_pale'])
            + poly((ftl, ftr, fbr, fbl), p['fill'])
            + poly((ftr, btr, bbr, fbr), p['brand_mid'])
            + hidden
            + measure_label((ftl[0] + ftr[0]) / 2, fbl[1] + 18, l_label)
            + measure_label((ftr[0] + btr[0]) / 2 + 10, (ftr[1] + btr[1]) / 2, w_label, anchor='start')
            + measure_label(ftl[0] - 12, (ftl[1] + fbl[1]) / 2 + 5, h_label, anchor='end')
            + _caption(width / 2, height - 8, caption)
        )

    return svg(
        width,
        height,
        title=title or f'Cuboid {l_label} by {w_label} by {h_label}',
        desc=desc or (
            f'An isometric cuboid. Hidden edges are dashed. Length {l_label}, '
            f'width {w_label}, and height {h_label} are labelled.'
        ),
        body=body,
        max_width=max_width,
    )


def cylinder_hemisphere(
    r_label='r',
    h_label='h',
    *,
    caption=None,
    max_width=220,
    title=None,
    desc=None,
):
    """Composite silo: cylinder with a hemisphere cap. Join ellipse is dashed."""
    p = PALETTE
    rx, ry, body_h = 50, 14, 78
    pad_l, pad_r, pad_t, pad_b = 20, 92, 28, 28 if caption else 20
    cx = pad_l + rx
    dome_top = pad_t
    top_cy = dome_top + rx
    bot_cy = top_cy + body_h
    left, right = cx - rx, cx + rx
    width = pad_l + 2 * rx + pad_r
    height = bot_cy + ry + pad_b

    def body(ids):
        return (
            f'<path d="M{_num(left)} {_num(top_cy)} A{_num(rx)} {_num(rx)} 0 0 0 {_num(right)} {_num(top_cy)}" '
            f'fill="url(#{ids["top"]})" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'<path d="M{_num(left)} {_num(top_cy)} L{_num(left)} {_num(bot_cy)} '
            f'A{_num(rx)} {_num(ry)} 0 0 1 {_num(right)} {_num(bot_cy)} '
            f'L{_num(right)} {_num(top_cy)} Z" fill="url(#{ids["body"]})" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_arc(left, bot_cy, rx, ry, right, bot_cy, sweep=0, stroke=p["hidden"], width=STROKE_HIDDEN, dashed=True)}'
            f'<ellipse cx="{_num(cx)}" cy="{_num(top_cy)}" rx="{_num(rx)}" ry="{_num(ry)}" '
            f'fill="none" stroke="{p["hidden"]}" stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
            f'{_measure_h(cx, right, top_cy, r_label, ids, label_dy=-10)}'
            f'{_measure_v(right + 18, top_cy, bot_cy, h_label, ids)}'
            f'{_caption(cx, height - 10, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Silo: cylinder with hemisphere cap, radius {r_label}, height {h_label}',
        desc=desc or (
            f'A composite solid: a cylinder of height {h_label} with a hemisphere of radius '
            f'{r_label} on top. The join is drawn dashed because it is inside the solid.'
        ),
        body=body,
        max_width=max_width,
    )


# ---------------------------------------------------------------------------
# 2D helpers used by the mensuration generator (U5.2 call-site migration)
# ---------------------------------------------------------------------------

def rectangle(w_label, h_label, *, caption=None, max_width=240, title=None, desc=None):
    p = PALETTE
    box_w, box_h = 140, 78
    x0, y0 = 48, 32
    width, height = 220, 140 if caption else 128

    def body(ids):
        return (
            f'<rect x="{x0}" y="{y0}" width="{box_w}" height="{box_h}" fill="{p["fill"]}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_measure_h(x0, x0 + box_w, y0 - 4, w_label, ids, label_dy=-8)}'
            f'{_measure_v(x0 - 16, y0, y0 + box_h, h_label, ids, label_dx=-8, label_anchor="end")}'
            f'{_caption(x0 + box_w / 2, height - 10, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Rectangle {w_label} by {h_label}',
        desc=desc or f'A rectangle labelled {w_label} along the length and {h_label} along the width.',
        body=body,
        max_width=max_width,
    )


def right_triangle(base_label, height_label, *, caption=None, max_width=240, title=None, desc=None):
    p = PALETTE
    x0, y_base, x1, y_apex = 36, 108, 168, 28
    width, height = 200, 148 if caption else 132

    def body(ids):
        return (
            f'<polygon points="{x0},{y_base} {x1},{y_base} {x0},{y_apex}" fill="{p["fill"]}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}" stroke-linejoin="round"/>'
            f'<line x1="{x0}" y1="{y_apex}" x2="{x0}" y2="{y_base}" stroke="{p["hidden"]}" '
            f'stroke-width="{STROKE_HIDDEN}" stroke-dasharray="5 4"/>'
            f'{_measure_h(x0, x1, y_base + 4, base_label, ids, label_dy=18)}'
            f'{measure_label(x0 - 12, (y_apex + y_base) / 2 + 5, height_label, anchor="end")}'
            f'{_caption((x0 + x1) / 2, height - 10, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Right triangle base {base_label}, height {height_label}',
        desc=desc or f'A right-angled triangle with base {base_label} and perpendicular height {height_label}.',
        body=body,
        max_width=max_width,
    )


def circle_with_radius(r_label='r', *, caption=None, max_width=200, title=None, desc=None):
    p = PALETTE
    r, cx, cy = 56, 88, 80
    width, height = 176, 176 if caption else 164

    def body(ids):
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{p["fill"]}" '
            f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{_measure_h(cx, cx + r, cy, r_label, ids, label_dy=-10)}'
            f'{_caption(cx, height - 10, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Circle with radius {r_label}',
        desc=desc or f'A circle with a labelled radius {r_label}.',
        body=body,
        max_width=max_width,
    )


def sector(angle, r_label='r', *, caption=None, max_width=200, title=None, desc=None):
    p = PALETTE
    angle = float(angle)
    cx, cy, r = 88, 118, 70
    theta = math.radians(angle)
    ex = cx + r * math.cos(-theta)
    ey = cy + r * math.sin(-theta)
    large = 1 if angle > 180 else 0
    pad_l, pad_r, pad_t, pad_b = 16, 24, 20, 24 if caption else 14
    width = cx + r + pad_r
    height = cy + pad_b
    lx = cx + (r * 0.45) * math.cos(-theta / 2)
    ly = cy + (r * 0.45) * math.sin(-theta / 2)

    def body(_ids):
        return (
            f'<path d="M{_num(cx)} {_num(cy)} L{_num(cx + r)} {_num(cy)} '
            f'A{_num(r)} {_num(r)} 0 {large} 0 {_num(ex)} {_num(ey)} Z" '
            f'fill="{p["fill"]}" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'{measure_label((cx + cx + r) / 2, cy - 6, r_label)}'
            f'{measure_label(lx, ly, f"{int(angle) if angle == int(angle) else angle}°")}'
            f'{_caption(cx, height - 8, caption)}'
        )

    return svg(
        width,
        height,
        title=title or f'Sector of {angle}° with radius {r_label}',
        desc=desc or f'A circular sector of angle {angle}° and radius {r_label}.',
        body=body,
        max_width=max_width,
    )


def sector_with_arc(angle=70, r_label='r', theta_label='θ', *, max_width=200):
    """Lesson sector with highlighted arc and arc-length label."""
    p = PALETTE
    angle = float(angle)
    cx, cy, r = 82, 118, 68
    theta = math.radians(angle)
    ex = cx + r * math.cos(-theta)
    ey = cy + r * math.sin(-theta)
    large = 1 if angle > 180 else 0
    inner = r - 8
    iex = cx + inner * math.cos(-theta)
    iey = cy + inner * math.sin(-theta)
    width = cx + r + 36
    height = 150

    def body(_ids):
        return (
            f'<path d="M{_num(cx)} {_num(cy)} L{_num(cx + r)} {_num(cy)} '
            f'A{_num(r)} {_num(r)} 0 {large} 0 {_num(ex)} {_num(ey)} Z" '
            f'fill="{p["fill"]}" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
            f'<path d="M{_num(cx + inner)} {_num(cy)} A{_num(inner)} {_num(inner)} 0 {large} 0 '
            f'{_num(iex)} {_num(iey)}" fill="none" stroke="{p["measure"]}" stroke-width="{STROKE_MEASURE}"/>'
            f'{measure_label(128, 78, "arc length")}'
            f'{shape_label(118, 112, r_label)}'
            f'{shape_label(92, 96, theta_label)}'
            f'<path d="M{_num(cx + 18)} {_num(cy)} A18 18 0 0 0 {_num(cx + 14)} {_num(cy - 14)}" '
            f'fill="none" stroke="{p["brand"]}" stroke-width="{STROKE_MEASURE}"/>'
        )

    return svg(
        width,
        height,
        title=f'Sector of {angle}° showing arc length',
        desc=f'A sector with radius {r_label}, angle {theta_label}, and the curved arc highlighted.',
        body=body,
        max_width=max_width,
    )


def circular_segment(angle=60, *, max_width=200, caption='Segment area'):
    """Lesson segment: region between chord and arc."""
    p = PALETTE
    segment_fill = '#dcfce7'
    segment_stroke = '#16a34a'
    angle = float(angle)
    cx, cy, r = 88, 118, 64
    theta = math.radians(angle)
    ex = cx + r * math.cos(-theta)
    ey = cy + r * math.sin(-theta)
    large = 1 if angle > 180 else 0
    width = cx + r + 32
    height = 158

    def body(_ids):
        return (
            f'<path d="M{_num(cx)} {_num(cy)} L{_num(cx + r)} {_num(cy)} '
            f'A{_num(r)} {_num(r)} 0 {large} 0 {_num(ex)} {_num(ey)} Z" '
            f'fill="none" stroke="{segment_stroke}" stroke-width="{STROKE_MEASURE}" '
            f'stroke-dasharray="5 4"/>'
            f'<path d="M{_num(cx + r)} {_num(cy)} A{_num(r)} {_num(r)} 0 {large} 0 {_num(ex)} {_num(ey)}" '
            f'fill="{segment_fill}" stroke="{segment_stroke}" stroke-width="{STROKE_OUTLINE}"/>'
            f'<line x1="{_num(cx + r)}" y1="{_num(cy)}" x2="{_num(ex)}" y2="{_num(ey)}" '
            f'stroke="{segment_stroke}" stroke-width="{STROKE_MEASURE}"/>'
            f'{shape_label(112, 100, "segment", anchor="middle")}'
            f'{shape_label(88, 132, "= sector − triangle", anchor="middle")}'
            f'{_caption(cx, height - 6, caption)}'
        )

    return svg(
        width,
        height,
        title='Circular segment',
        desc='The segment between a chord and an arc, equal to sector area minus triangle area.',
        body=body,
        max_width=max_width,
    )


def prism(*_args, **_kwargs):
    return _stub('prism', 'Prism')


def annulus(*_args, **_kwargs):
    return _stub('annulus', 'Annulus')


def number_line(*_args, **_kwargs):
    return _stub('number line', 'Number line')


def pie_chart(
    sizes,
    labels=None,
    *,
    highlight_index=None,
    title='Pie chart',
    desc=None,
    max_width=220,
):
    """Part-of-whole pie chart. ``sizes`` are relative frequencies or counts."""
    p = PALETTE
    values = [float(v) for v in sizes]
    total = sum(values)
    if total <= 0:
        raise ValueError('pie_chart sizes must sum to a positive total')
    if labels is None:
        labels = [str(i + 1) for i in range(len(values))]
    if len(labels) != len(values):
        raise ValueError('labels length must match sizes')

    fills = [p['brand'], p['measure'], p['success'], p['brand_mid'], p['brand_soft'], p['hidden']]
    cx, cy, r = 100, 108, 72
    angle = 0.0
    slices = []
    desc_parts = []
    for i, (val, label) in enumerate(zip(values, labels)):
        sweep = 360.0 * val / total
        if sweep <= 0:
            continue
        fill = fills[i % len(fills)]
        if highlight_index is not None and i == highlight_index:
            fill = p['brand_mid']
            stroke = p['brand']
            sw = STROKE_OUTLINE
        else:
            stroke = p['ink']
            sw = 1
        start = angle
        end = angle + sweep
        angle = end
        start_rad = math.radians(start - 90)
        end_rad = math.radians(end - 90)
        x1 = cx + r * math.cos(start_rad)
        y1 = cy + r * math.sin(start_rad)
        x2 = cx + r * math.cos(end_rad)
        y2 = cy + r * math.sin(end_rad)
        large = 1 if sweep > 180 else 0
        slices.append(
            f'<path d="M {cx:.1f} {cy:.1f} L {x1:.1f} {y1:.1f} '
            f'A {r} {r} 0 {large} 1 {x2:.1f} {y2:.1f} Z" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )
        sector_angle = round(sweep, 1)
        desc_parts.append(f'{label}: {val} ({sector_angle}°)')

    mid_angle = 0.0  # reserved for future sector labels
    legend_y = 196
    legend = []
    for i, (val, label) in enumerate(zip(values, labels)):
        sweep = 360.0 * val / total
        if sweep <= 0:
            continue
        fill = fills[i % len(fills)]
        lx, ly = 24, legend_y + i * 18
        legend.append(
            f'<rect x="{lx}" y="{ly - 10}" width="12" height="12" rx="2" fill="{fill}" '
            f'stroke="{p["ink"]}" stroke-width="1"/>'
            f'{shape_label(lx + 20, ly, f"{label} ({val})", anchor="start")}'
        )

    desc_text = desc or '; '.join(desc_parts)
    body = (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["ink"]}" '
        f'stroke-width="{STROKE_OUTLINE}" aria-hidden="true"/>'
        + ''.join(slices)
        + ''.join(legend)
    )
    return svg(200, 220, title=title, desc=desc_text, body=lambda ids: body, max_width=max_width, variant='chart')


def _venn_cell(x, y, value, font_size=13):
    if value is None:
        w, h = 34, 18
        return (
            f'<rect x="{x - w // 2}" y="{y - h + 4}" width="{w}" height="{h}" rx="3" '
            f'fill="{PALETTE["surface"]}" stroke="{PALETTE["hidden"]}" stroke-width="1.2" '
            f'stroke-dasharray="3,2"/>'
            f'{_text(x, y, "?", fill=PALETTE["hidden"], anchor="middle")}'
        )
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{font_size}" '
        f'font-weight="{FONT_WEIGHT}" fill="{PALETTE["ink"]}">{_esc(value)}</text>'
    )


def venn2(
    a_only,
    b_only,
    both,
    neither,
    *,
    label_a='A',
    label_b='B',
    title='Two-set Venn diagram',
    desc=None,
    max_width=480,
):
    """Two-set Venn with region counts."""
    p = PALETTE
    total = a_only + b_only + both + neither
    desc_text = desc or (
        f'{label_a} only {a_only}, {label_b} only {b_only}, both {both}, neither {neither}, total {total}'
    )
    body = (
        f'<rect x="10" y="20" width="460" height="225" fill="none" stroke="{p["hidden"]}" '
        f'stroke-width="{STROKE_OUTLINE}" rx="6"/>'
        f'{shape_label(456, 38, "ξ", anchor="end")}'
        f'<circle cx="185" cy="122" r="85" fill="{p["brand"]}" fill-opacity="0.18" '
        f'stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
        f'<circle cx="295" cy="122" r="85" fill="{p["measure"]}" fill-opacity="0.18" '
        f'stroke="{p["measure"]}" stroke-width="{STROKE_OUTLINE}"/>'
        f'{shape_label(147, 72, label_a)}'
        f'{shape_label(333, 72, label_b)}'
        f'{shape_label(138, 112, str(a_only))}'
        f'{_text(138, 128, "A only", fill=p["ink_muted"], anchor="middle")}'
        f'{shape_label(240, 112, str(both))}'
        f'{_text(240, 128, "A ∩ B", fill=p["ink_muted"], anchor="middle")}'
        f'{shape_label(342, 112, str(b_only))}'
        f'{_text(342, 128, "B only", fill=p["measure"], anchor="middle")}'
        f'{_text(45, 228, f"Neither: {neither}", fill=p["ink_muted"], anchor="start")}'
        f'{_text(435, 228, f"Total = {total}", fill=p["ink_muted"], anchor="end")}'
    )
    return svg(480, 260, title=title, desc=desc_text, body=lambda ids: body, max_width=max_width, variant='chart')


_VENN3_R = 78
_VENN3_AX, _VENN3_AY = 214, 132
_VENN3_BX, _VENN3_BY = 306, 132
_VENN3_CX, _VENN3_CY = 260, 188
_VENN3_POS = {
    'a_only': (172, 124),
    'b_only': (348, 124),
    'c_only': (260, 232),
    'ab_only': (260, 104),
    'ac_only': (208, 162),
    'bc_only': (312, 162),
    'abc': (260, 140),
    'neither': (52, 248),
}


def venn3(
    a_only=None,
    b_only=None,
    c_only=None,
    ab_only=None,
    ac_only=None,
    bc_only=None,
    abc=None,
    neither=None,
    *,
    label_a='A',
    label_b='B',
    label_c='C',
    blank=False,
    title='Three-set Venn diagram',
    desc=None,
    max_width=520,
):
    """Three-set Venn. Pass ``blank=True`` for fill-in cells (values may be None)."""
    p = PALETTE
    regions = {
        'a_only': a_only,
        'b_only': b_only,
        'c_only': c_only,
        'ab_only': ab_only,
        'ac_only': ac_only,
        'bc_only': bc_only,
        'abc': abc,
        'neither': neither,
    }
    numeric = [v for v in regions.values() if v is not None]
    total = sum(numeric) if numeric and not blank else None
    cells = ''.join(
        _venn_cell(x, y, regions[key])
        for key, (x, y) in _VENN3_POS.items()
    )
    footer = (
        f'<text x="28" y="264" font-size="10" fill="{p["ink_muted"]}">'
        'Write counts in each region and for neither.</text>'
        if blank
        else (f'<text x="492" y="248" text-anchor="end" font-size="11" fill="{p["ink_muted"]}">'
              f'Total = {total}</text>' if total is not None else '')
    )
    desc_text = desc or (
        'Three-set Venn diagram with counts in each region.'
        if not blank
        else 'Blank three-set Venn diagram for students to complete.'
    )
    body = (
        f'<rect x="10" y="16" width="500" height="268" fill="none" stroke="{p["hidden"]}" '
        f'stroke-width="{STROKE_OUTLINE}" rx="6"/>'
        f'{shape_label(498, 34, "ξ", anchor="end")}'
        f'<circle cx="{_VENN3_AX}" cy="{_VENN3_AY}" r="{_VENN3_R}" fill="{p["brand"]}" '
        f'fill-opacity="0.16" stroke="{p["brand"]}" stroke-width="{STROKE_OUTLINE}"/>'
        f'<circle cx="{_VENN3_BX}" cy="{_VENN3_BY}" r="{_VENN3_R}" fill="{p["measure"]}" '
        f'fill-opacity="0.16" stroke="{p["measure"]}" stroke-width="{STROKE_OUTLINE}"/>'
        f'<circle cx="{_VENN3_CX}" cy="{_VENN3_CY}" r="{_VENN3_R}" fill="{p["success"]}" '
        f'fill-opacity="0.16" stroke="{p["success"]}" stroke-width="{STROKE_OUTLINE}"/>'
        f'{shape_label(168, 56, label_a)}'
        f'{shape_label(352, 56, label_b)}'
        f'{shape_label(260, 272, label_c)}'
        f'{cells}{footer}'
    )
    return svg(520, 300, title=title, desc=desc_text, body=lambda ids: body, max_width=max_width, variant='chart')


_PROB_TREE_COLOURS = {
    'red': '#c0392b',
    'green': '#2e7d32',
    'blue': '#1a6fa8',
    'black': '#333333',
    'white': '#8a8f96',
    'yellow': '#b8860b',
    'purple': '#7b3fa0',
    'orange': '#d35400',
    'pink': '#c2389a',
    'brown': '#8a5a2b',
}
_PROB_TREE_FALLBACK = (PALETTE['brand'], PALETTE['measure'])


def _prob_tree_colour(name, index):
    return _PROB_TREE_COLOURS.get(str(name).strip().lower(), _PROB_TREE_FALLBACK[index % 2])


def prob_tree(
    c1,
    c2,
    p1n,
    p1d,
    p2n,
    p2d,
    p11n,
    p11d,
    p12n,
    p12d,
    p21n,
    p21d,
    p22n,
    p22d,
    *,
    title='Two-stage probability tree',
    show_probs=True,
    fill_in=False,
    desc=None,
    max_width=None,
):
    """Two-draw probability tree with optional branch probabilities and fill-in inputs."""

    def _fr(n, d):
        g = math.gcd(abs(int(n)), abs(int(d)))
        return f'{n // g}/{d // g}'

    o11 = _fr(p1n * p11n, p1d * p11d)
    o12 = _fr(p1n * p12n, p1d * p12d)
    o21 = _fr(p2n * p21n, p2d * p21d)
    o22 = _fr(p2n * p22n, p2d * p22d)
    b1 = _fr(p1n, p1d)
    b2 = _fr(p2n, p2d)
    b11 = _fr(p11n, p11d)
    b12 = _fr(p12n, p12d)
    b21 = _fr(p21n, p21d)
    b22 = _fr(p22n, p22d)

    col1 = _prob_tree_colour(c1, 0)
    col2 = _prob_tree_colour(c2, 1)
    p = PALETTE
    w = 640 if fill_in else 600
    if max_width is None:
        max_width = w

    def _branch_label(x, y, val, color):
        if show_probs:
            return _text(x, y, val, fill=color, anchor='middle')
        if not fill_in:
            return ''
        rx, ry = x - 22, y - 11
        return (
            f'<foreignObject x="{rx}" y="{ry}" width="54" height="22">'
            f'<input xmlns="http://www.w3.org/1999/xhtml" type="text" '
            f'class="prob-tree-input" data-ans="{_esc(val)}" '
            f'autocomplete="off" spellcheck="false" aria-label="branch probability"/>'
            f'</foreignObject>'
        )

    def _outcome_row(x, y, lbl, prob):
        if show_probs:
            return _text(x, y, f'→ {lbl} = {prob}', fill=p['ink_muted'], anchor='start')
        if not fill_in:
            return _text(x, y, f'→ {lbl}', fill=p['ink_muted'], anchor='start')
        bx = x + 118
        return (
            f'{_text(x, y, f"→ {lbl} = ", fill=p["ink_muted"], anchor="start")}'
            f'<foreignObject x="{bx}" y="{y - 11}" width="48" height="22">'
            f'<input xmlns="http://www.w3.org/1999/xhtml" type="text" '
            f'class="prob-tree-input" data-ans="{_esc(prob)}" '
            f'autocomplete="off" spellcheck="false" aria-label="outcome probability"/>'
            f'</foreignObject>'
        )

    body = (
        f'{shape_label(w // 2, 18, title)}'
        f'<circle cx="55" cy="148" r="4" fill="{p["ink"]}" aria-hidden="true"/>'
        f'<line x1="55" y1="148" x2="228" y2="76" stroke="{col1}" stroke-width="{STROKE_MEASURE}"/>'
        f'<line x1="55" y1="148" x2="228" y2="220" stroke="{col2}" stroke-width="{STROKE_MEASURE}"/>'
        + _branch_label(132, 99, b1, col1)
        + _branch_label(132, 202, b2, col2)
        + f'<circle cx="228" cy="76" r="3" fill="{col1}"/>'
        + shape_label(236, 70, str(c1), anchor='start')
        + f'<circle cx="228" cy="220" r="3" fill="{col2}"/>'
        + shape_label(236, 230, str(c2), anchor='start')
        + f'<line x1="228" y1="76" x2="390" y2="38" stroke="{col1}" stroke-width="{STROKE_MEASURE}"/>'
        + f'<line x1="228" y1="76" x2="390" y2="114" stroke="{col2}" stroke-width="{STROKE_MEASURE}"/>'
        + f'<line x1="228" y1="220" x2="390" y2="182" stroke="{col1}" stroke-width="{STROKE_MEASURE}"/>'
        + f'<line x1="228" y1="220" x2="390" y2="258" stroke="{col2}" stroke-width="{STROKE_MEASURE}"/>'
        + _branch_label(309, 49, b11, col1)
        + _branch_label(309, 103, b12, col2)
        + _branch_label(309, 194, b21, col1)
        + _branch_label(309, 255, b22, col2)
        + shape_label(398, 34, str(c1), anchor='start')
        + shape_label(398, 110, str(c2), anchor='start')
        + shape_label(398, 178, str(c1), anchor='start')
        + shape_label(398, 254, str(c2), anchor='start')
        + _outcome_row(440, 34, f'({c1},{c1})', o11)
        + _outcome_row(440, 110, f'({c1},{c2})', o12)
        + _outcome_row(440, 178, f'({c2},{c1})', o21)
        + _outcome_row(440, 254, f'({c2},{c2})', o22)
        + _text(228, 278, '1st draw', fill=p['ink_muted'], anchor='middle')
        + _text(390, 278, '2nd draw', fill=p['ink_muted'], anchor='middle')
        + _text(
            w - 90,
            278,
            'outcome' if not show_probs and not fill_in else 'outcome · P(outcome)',
            fill=p['ink_muted'],
            anchor='middle',
        )
    )
    desc_text = desc or (
        f'Two-stage tree: first draw {c1} or {c2}, then second draw with branch probabilities.'
    )
    return viewbox_svg(
        0,
        0,
        w,
        290,
        title=title,
        desc=desc_text,
        body=lambda ids: body,
        max_width=max_width,
        variant='tree',
    )


_FORMULA_COVER = '#fcd34d'


def formula_triangle(top, bl, br, cover=None, title='Formula triangle', desc=None, max_width=170):
    """SDT / DMV / PFA style formula triangle. ``cover`` is ``top``, ``bl``, or ``br``."""
    p = PALETTE
    fills = {
        'top': _FORMULA_COVER if cover == 'top' else p['brand_pale'],
        'bl': _FORMULA_COVER if cover == 'bl' else p['brand_soft'],
        'br': _FORMULA_COVER if cover == 'br' else p['brand_mid'],
    }
    stroke = p['brand']
    desc_text = desc or f'Formula triangle: {top} on top, {bl} and {br} on the bottom row.'

    def body(_ids):
        return (
            f'<polygon points="100,12 58,78 142,78" fill="{fills["top"]}" '
            f'stroke="{stroke}" stroke-width="1.5"/>'
            f'<polygon points="58,78 12,150 100,150 100,78" fill="{fills["bl"]}" '
            f'stroke="{stroke}" stroke-width="1.5"/>'
            f'<polygon points="100,78 142,78 188,150 100,150" fill="{fills["br"]}" '
            f'stroke="{stroke}" stroke-width="1.5"/>'
            f'<polygon points="100,12 12,150 188,150" fill="none" stroke="{stroke}" stroke-width="2.5"/>'
            f'<line x1="58" y1="78" x2="142" y2="78" stroke="{stroke}" stroke-width="1.5"/>'
            f'<line x1="100" y1="78" x2="100" y2="150" stroke="{stroke}" stroke-width="1.5"/>'
            f'{shape_label(100, 52, top)}'
            f'{shape_label(56, 128, bl)}'
            f'{shape_label(144, 128, br)}'
            f'{_text(100, 128, "×", fill=p["ink_muted"], anchor="middle")}'
        )

    return svg(
        200,
        160,
        title=title,
        desc=desc_text,
        body=body,
        max_width=max_width,
        variant='inline',
    )


def bar_chart(categories, values, title='Bar chart', desc=None, max_width=400):
    W, H = 400, 280
    PL, PR, PT, PB = 55, 20, 30, 52
    pw, ph = W - PL - PR, H - PT - PB
    max_val = max(values)
    n = len(categories)
    bar_w = min(55, pw // n - 12)
    bar_gap = (pw - bar_w * n) // (n + 1)
    p = PALETTE
    desc_text = desc or f'Bar chart with {n} categories.'

    def body(_ids):
        parts = [
            f'<line x1="{PL}" y1="{PT + ph}" x2="{W - PR}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
        ]
        for i in range(6):
            val = round(max_val * i / 5)
            yp = PT + ph - (val / max_val) * ph
            parts.append(
                f'<line x1="{PL - 4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" stroke="{p["ink_muted"]}"/>'
            )
            parts.append(_text(PL - 7, yp + 4, val, fill=p['ink_muted'], anchor='end'))
        for i, (cat, val) in enumerate(zip(categories, values)):
            x = PL + bar_gap + i * (bar_w + bar_gap)
            bh = (val / max_val) * ph
            y = PT + ph - bh
            parts.append(
                f'<rect x="{x:.0f}" y="{y:.0f}" width="{bar_w}" height="{bh:.0f}" '
                f'fill="{p["brand"]}" rx="2"/>'
            )
            parts.append(shape_label(x + bar_w / 2, y - 5, val))
            parts.append(shape_label(x + bar_w / 2, PT + ph + 20, cat))
        return ''.join(parts)

    return svg(W, H, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')


def freq_table(values, freqs, title='Frequency table', desc=None, max_width=300):
    w = 300
    h = 30 + 25 * len(values)
    total_f = sum(freqs)
    total_fx = sum(v * f for v, f in zip(values, freqs))
    desc_text = desc or f'Frequency table with {len(values)} rows.'

    def body(_ids):
        parts = [
            shape_label(70, 28, 'x'),
            shape_label(170, 28, 'f'),
            shape_label(240, 28, 'fx'),
        ]
        for i, (v, f) in enumerate(zip(values, freqs)):
            y = 45 + i * 25
            parts.append(shape_label(70, y, v))
            parts.append(shape_label(170, y, f))
            parts.append(shape_label(240, y, v * f))
        y_last = 45 + len(values) * 25
        parts.append(
            f'<line x1="40" y1="{y_last - 15}" x2="260" y2="{y_last - 15}" stroke="{PALETTE["ink_muted"]}"/>'
        )
        parts.append(shape_label(70, y_last, 'Σ'))
        parts.append(shape_label(170, y_last, total_f))
        parts.append(shape_label(240, y_last, total_fx))
        return ''.join(parts)

    return svg(w, h, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')


def histogram(intervals, freqs, title='Histogram', desc=None, max_width=460):
    W, H = 460, 310
    PL, PR, PT, PB = 65, 22, 32, 52
    pw, ph = W - PL - PR, H - PT - PB
    densities = [f / (high - low) for (low, high), f in zip(intervals, freqs)]
    max_d = max(densities)
    x_span = intervals[-1][1] - intervals[0][0]
    p = PALETTE
    desc_text = desc or 'Histogram with frequency density on the vertical axis.'

    def sx(low):
        return PL + (low - intervals[0][0]) / x_span * pw

    def body(_ids):
        parts = [
            f'<line x1="{PL}" y1="{PT + ph}" x2="{W - PR}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
        ]
        for (low, high), f, d in zip(intervals, freqs, densities):
            x = sx(low)
            bw = sx(high) - x
            bh = (d / max_d) * ph
            y = PT + ph - bh
            parts.append(
                f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{bh:.0f}" '
                f'fill="{p["brand"]}" opacity="0.85" stroke="{p["brand"]}" stroke-width="0.5"/>'
            )
            parts.append(shape_label(x, PT + ph + 18, low))
        parts.append(shape_label(sx(intervals[-1][1]), PT + ph + 18, intervals[-1][1]))
        y_step = max(1, int(max_d / 5) + 1)
        for val in range(0, int(max_d) + y_step, y_step):
            yp = PT + ph - (val / max_d) * ph
            if PT - 5 <= yp <= PT + ph:
                parts.append(
                    f'<line x1="{PL - 4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" '
                    f'stroke="{p["ink_muted"]}"/>'
                )
                parts.append(_text(PL - 7, yp + 4, val, fill=p['ink_muted'], anchor='end'))
        cy_lbl = PT + ph // 2
        parts.append(shape_label(W // 2, H - 8, 'Class intervals'))
        parts.append(
            f'<text x="14" y="{cy_lbl}" fill="{p["ink_muted"]}" font-size="{FONT_SIZE}" '
            f'font-weight="{FONT_WEIGHT}" font-family="{FONT_FAMILY}" '
            f'transform="rotate(-90,14,{cy_lbl})" text-anchor="middle">Frequency density</text>'
        )
        return ''.join(parts)

    return svg(W, H, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')


def box_plot(min_val, q1, q2, q3, max_val, title='Box plot', desc=None, max_width=460):
    W, H = 460, 175
    PL, PR = 50, 30
    pw = W - PL - PR
    by1, by2, wcy = 45, 115, 80
    scale = pw / max(1, max_val - min_val)
    p = PALETTE
    desc_text = desc or (
        f'Box plot from {min_val} to {max_val}, median {q2}.'
    )

    def x(val):
        return PL + (val - min_val) * scale

    lmap = {min_val: 'Min', q1: 'Q\u2081', q2: 'Median', q3: 'Q\u2083', max_val: 'Max'}

    def body(_ids):
        parts = [
            f'<line x1="{PL}" y1="{by2}" x2="{W - PR}" y2="{by2}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
            f'<line x1="{x(min_val):.0f}" y1="{wcy}" x2="{x(q1):.0f}" y2="{wcy}" '
            f'stroke="{p["brand"]}" stroke-width="2.5"/>',
            f'<line x1="{x(min_val):.0f}" y1="{by1 + 6}" x2="{x(min_val):.0f}" y2="{by2 - 6}" '
            f'stroke="{p["brand"]}" stroke-width="2"/>',
            f'<rect x="{x(q1):.0f}" y="{by1}" width="{x(q3) - x(q1):.0f}" height="{by2 - by1}" '
            f'fill="{p["brand_soft"]}" stroke="{p["brand"]}" stroke-width="2"/>',
            f'<line x1="{x(q2):.0f}" y1="{by1}" x2="{x(q2):.0f}" y2="{by2}" '
            f'stroke="{p["measure"]}" stroke-width="2.5"/>',
            f'<line x1="{x(q3):.0f}" y1="{wcy}" x2="{x(max_val):.0f}" y2="{wcy}" '
            f'stroke="{p["brand"]}" stroke-width="2.5"/>',
            f'<line x1="{x(max_val):.0f}" y1="{by1 + 6}" x2="{x(max_val):.0f}" y2="{by2 - 6}" '
            f'stroke="{p["brand"]}" stroke-width="2"/>',
        ]
        for val in [min_val, q1, q2, q3, max_val]:
            xp = x(val)
            parts.append(
                f'<line x1="{xp:.0f}" y1="{by2}" x2="{xp:.0f}" y2="{by2 + 5}" stroke="{p["ink_muted"]}"/>'
            )
            parts.append(shape_label(xp, by2 + 20, val))
            parts.append(
                f'<text x="{xp:.0f}" y="{by1 - 10}" fill="{p["ink_muted"]}" '
                f'font-size="10" font-weight="{FONT_WEIGHT}" font-family="{FONT_FAMILY}" '
                f'text-anchor="middle">{lmap[val]}</text>'
            )
        return ''.join(parts)

    return svg(W, H, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')


def cumulative_frequency_curve(upper_bounds, cum_freqs, title='Cumulative frequency curve', desc=None, max_width=520):
    W, H = 520, 340
    PL, PR, PT, PB = 62, 22, 35, 52
    pw, ph = W - PL - PR, H - PT - PB
    max_cf = cum_freqs[-1]
    x_max_d = upper_bounds[-1]
    class_w = upper_bounds[1] - upper_bounds[0] if len(upper_bounds) > 1 else x_max_d - upper_bounds[0]
    lb0 = upper_bounds[0] - class_w
    all_x = [lb0] + list(upper_bounds)
    all_cf = [0] + list(cum_freqs)
    x_lo = lb0
    p = PALETTE
    desc_text = desc or 'Cumulative frequency curve (ogive).'

    def sx(v):
        return PL + (v - x_lo) / (x_max_d - x_lo) * pw

    def sy(v):
        return PT + ph - (v / max_cf) * ph

    path = 'M' + ' L'.join(f'{sx(v):.0f},{sy(c):.0f}' for v, c in zip(all_x, all_cf))

    def body(_ids):
        parts = [
            f'<line x1="{PL}" y1="{PT + ph}" x2="{W - PR}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
            f'<line x1="{PL}" y1="{PT}" x2="{PL}" y2="{PT + ph}" '
            f'stroke="{p["ink_muted"]}" stroke-width="1.5"/>',
        ]
        for ub in all_x:
            xp = sx(ub)
            parts.append(
                f'<line x1="{xp:.0f}" y1="{PT + ph}" x2="{xp:.0f}" y2="{PT + ph + 5}" '
                f'stroke="{p["ink_muted"]}"/>'
            )
            parts.append(shape_label(xp, PT + ph + 20, ub))
        y_step = max(1, max_cf // 5)
        for val in range(0, max_cf + 1, y_step):
            yp = sy(val)
            if PT - 5 <= yp <= PT + ph:
                parts.append(
                    f'<line x1="{PL - 4}" y1="{yp:.0f}" x2="{PL}" y2="{yp:.0f}" '
                    f'stroke="{p["ink_muted"]}"/>'
                )
                parts.append(_text(PL - 7, yp + 4, val, fill=p['ink_muted'], anchor='end'))
        parts.append(
            f'<path d="{path}" fill="none" stroke="{p["brand"]}" stroke-width="2.5"/>'
        )
        for v, c in zip(all_x[1:], all_cf[1:]):
            parts.append(
                f'<circle cx="{sx(v):.0f}" cy="{sy(c):.0f}" r="4" fill="{p["measure"]}"/>'
            )
        cy_lbl = PT + ph // 2
        parts.append(shape_label(W // 2, H - 8, 'Upper class boundary'))
        parts.append(
            f'<text x="14" y="{cy_lbl}" fill="{p["ink_muted"]}" font-size="{FONT_SIZE}" '
            f'font-weight="{FONT_WEIGHT}" font-family="{FONT_FAMILY}" '
            f'transform="rotate(-90,14,{cy_lbl})" text-anchor="middle">Cumulative frequency</text>'
        )
        return ''.join(parts)

    return svg(W, H, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')


def velocity_time_graph(
    u,
    v,
    t,
    *,
    shaded=False,
    v_max=40,
    t_max=15,
    title='Velocity-time graph',
    desc=None,
    max_width=280,
):
    """Straight-line v–t segment from initial speed ``u`` to ``v`` over time ``t``."""
    W, H = 260, 180
    p = PALETTE
    desc_text = desc or f'Velocity increases from {u} m/s to {v} m/s over {t} s.'

    def vy(vel):
        return int(130 - (vel / v_max) * 110)

    def tx(time):
        return int(40 + (time / t_max) * 180)

    def body(_ids):
        parts = [
            f'<line x1="40" y1="20" x2="40" y2="150" stroke="{p["ink"]}" stroke-width="2"/>',
            f'<line x1="40" y1="150" x2="240" y2="150" stroke="{p["ink"]}" stroke-width="2"/>',
            shape_label(140, 172, 'Time (s)'),
            f'<text x="12" y="88" fill="{p["ink_muted"]}" font-size="11" '
            f'font-weight="{FONT_WEIGHT}" font-family="{FONT_FAMILY}" '
            f'transform="rotate(-90,12,88)" text-anchor="middle">v (m/s)</text>',
        ]
        if shaded:
            parts.append(
                f'<polygon points="{tx(0)},{vy(u)} {tx(t)},{vy(v)} {tx(t)},{vy(0)} {tx(0)},{vy(0)}" '
                f'fill="{p["brand"]}" fill-opacity="0.12" stroke="none"/>'
            )
        parts.append(
            f'<line x1="{tx(0)}" y1="{vy(u)}" x2="{tx(t)}" y2="{vy(v)}" '
            f'stroke="{p["brand"]}" stroke-width="2.5"/>'
        )
        parts.append(shape_label(35, vy(u) + 4, u, anchor='end'))
        parts.append(shape_label(35, vy(v) + 4, v, anchor='end'))
        parts.append(shape_label(tx(t), 163, t))
        parts.append(shape_label(40, 163, '0'))
        return ''.join(parts)

    return svg(W, H, title=title, desc=desc_text, body=body, max_width=max_width, variant='chart')
