"""Improve GCSE maths Quick Reference cards: HTML for cramped layouts, CSS classes for SVG cards."""
from __future__ import annotations

import re
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

SVG_CLASS = 'class="revision-card-svg lesson-quick-ref"'
SVG_STYLE = (
    'style="max-width:760px;width:100%;height:auto;display:block;margin:0 auto;'
    'background:#f9f8f5;border:1px solid #d4e6f1;border-radius:10px;"'
)

QR_SECTION = re.compile(
    r"(<details[^>]*>\s*"
    r"<summary[^>]*>.*?Quick Reference.*?</summary>\s*"
    r'<div style="padding:[^"]*">)(.*?)(</div>\s*</details>)',
    re.DOTALL | re.IGNORECASE,
)


EMPTY_CENTER_WRAP = re.compile(
    r'<div style="text-align:center[^"]*">\s*(?:</div>\s*){1,4}',
    re.DOTALL,
)


def _wrap_html(card: str) -> str:
    return f'      <div class="revision-card-wrap">\n{card}\n      </div>'


def _card(title: str, aria: str, grid: str, footer: str = "") -> str:
    foot = (
        f'\n          <div class="lesson-quick-ref-advanced">{footer}\n          </div>'
        if footer
        else ""
    )
    return f"""        <div class="lesson-quick-ref-card" role="region" aria-label="{aria}">
          <h3>{title}</h3>
          <div class="lesson-quick-ref-grid lesson-quick-ref-grid--2col">
{grid}
          </div>{foot}
        </div>"""


def bidmas_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">BIDMAS order</h4>
              <ul>
                <li><strong>B</strong> — Brackets first</li>
                <li><strong>I</strong> — Indices (powers &amp; roots)</li>
                <li><strong>D / M</strong> — Divide &amp; multiply, left to right</li>
                <li><strong>A / S</strong> — Add &amp; subtract, left to right</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Negative numbers</h4>
              <ul>
                <li>\(a + (-b) = a - b\)</li>
                <li>\(a - (-b) = a + b\)</li>
                <li>Same signs × or ÷ → positive</li>
                <li>Different signs × or ÷ → negative</li>
                <li>\((-n)^2\) is positive; \(-(n^2)\) is negative</li>
              </ul>
            </div>"""
    footer = r"""
            <h4>Common exam traps</h4>
            <ul>
              <li>\(8 \div 4 \times 2 = 4\), not 1 — work D and M left to right</li>
              <li>\(10 - 3 + 2 = 9\), not 5 — work A and S left to right</li>
              <li>\((-3)^2 = +9\) but \(-(3^2) = -9\) — brackets change everything</li>
            </ul>"""
    return _wrap_html(
        _card(
            "BIDMAS &amp; Negative Numbers — Quick Reference",
            "BIDMAS and negative numbers quick reference",
            grid,
            footer,
        )
    )


def multiples_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Definitions</h4>
              <ul>
                <li>Multiple: \(n \times 1, 2, 3, \ldots\)</li>
                <li>Factor: divides exactly (no remainder)</li>
                <li>Prime: exactly two factors (1 and itself)</li>
                <li><strong>1 is not prime</strong></li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">HCF vs LCM</h4>
              <ul>
                <li><strong>HCF</strong> — biggest shared factor; use lowest prime powers</li>
                <li><strong>LCM</strong> — smallest shared multiple; use highest prime powers</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Prime factors</h4>
              <ul>
                <li>Factor tree → circle primes → index form</li>
                <li>e.g. \(36 = 2^2 \times 3^2\)</li>
              </ul>
            </div>"""
    footer = r"""
            <h4>Word problems</h4>
            <ul>
              <li><strong>HCF</strong> — sharing into equal groups, simplifying fractions</li>
              <li><strong>LCM</strong> — when events coincide, common denominators</li>
            </ul>"""
    return _wrap_html(
        _card(
            "Multiples &amp; Factors — Quick Reference",
            "Multiples and factors quick reference",
            grid,
            footer,
        )
    )


def algebra_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Simplifying</h4>
              <ul>
                <li>Like terms: same letter and power only</li>
                <li>Single bracket: \(a(b+c) = ab + ac\)</li>
                <li>Double bracket: multiply every term</li>
                <li>\((x+a)(x-a) = x^2 - a^2\)</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Equations</h4>
              <ul>
                <li>Linear: \(ax+b=c \Rightarrow x=(c-b)/a\)</li>
                <li>Quadratic: factorise → each bracket = 0</li>
                <li>Complete the square: half \(b\), adjust constant</li>
                <li>Formula: \(x = (-b \pm \sqrt{b^2-4ac})/(2a)\)</li>
              </ul>
            </div>"""
    footer = r"""
            <h4>Common exam traps</h4>
            <ul>
              <li>\(3x^2 + 2x \neq 5x^3\) — different powers stay separate</li>
              <li>\(-2(x-3) = -2x + 6\) — both signs change</li>
              <li>Quadratics usually have <strong>two</strong> solutions</li>
              <li>Factorise: take out the HCF fully first</li>
            </ul>"""
    return _wrap_html(
        _card("Algebra — Quick Reference", "Algebra quick reference", grid, footer)
    )


def fdp_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Decimal conversions</h4>
              <ul>
                <li>Decimal → %: multiply by 100</li>
                <li>% → decimal: divide by 100</li>
                <li>Decimal → fraction: use place value, simplify</li>
                <li>Fraction → decimal: top ÷ bottom</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Fraction &amp; percentage</h4>
              <ul>
                <li>% → fraction: write over 100, simplify</li>
                <li>Fraction → %: divide, then × 100</li>
                <li>Recurring decimal → fraction: algebra method</li>
                <li>Always simplify fractions fully</li>
              </ul>
            </div>"""
    footer = r"""
            <h4>Must-know equivalences</h4>
            <ul>
              <li>\(\frac12 = 0.5 = 50\%\) &nbsp;·&nbsp; \(\frac14 = 0.25 = 25\%\) &nbsp;·&nbsp; \(\frac34 = 0.75 = 75\%\)</li>
              <li>\(\frac15 = 0.2 = 20\%\) &nbsp;·&nbsp; \(\frac18 = 0.125 = 12.5\%\)</li>
            </ul>"""
    return _wrap_html(
        _card("FDP Conversions — Quick Reference", "FDP conversions quick reference", grid, footer)
    )


def geometry_angles_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Lines &amp; points</h4>
              <ul>
                <li>Straight line = 180°</li>
                <li>Around a point = 360°</li>
                <li>Vertically opposite angles are equal</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Parallel lines</h4>
              <ul>
                <li>Corresponding (F) = equal</li>
                <li>Alternate (Z) = equal</li>
                <li>Co-interior (C) = 180°</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Triangles</h4>
              <ul>
                <li>Angles sum to 180°</li>
                <li>Exterior = sum of two interior opposites</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Polygons</h4>
              <ul>
                <li>Interior sum = \((n-2) \times 180°\)</li>
                <li>Regular interior = \((n-2) \times 180 / n\)</li>
                <li>Exterior angle = \(360° / n\)</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Circle theorems</h4>
              <ul>
                <li>Centre angle = 2 × circumference angle</li>
                <li>Angle in semicircle = 90°</li>
                <li>Same segment → equal angles</li>
                <li>Cyclic quad: opposite angles = 180°</li>
                <li>Tangent ⊥ radius; tangents from a point are equal</li>
              </ul>
            </div>"""
    return _wrap_html(
        _card(
            "Geometry &amp; Angles — Quick Reference",
            "Geometry and angles quick reference",
            grid,
        )
    )


def transformations_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Reflections</h4>
              <ul>
                <li>\(x\)-axis: \((x,y) \to (x,-y)\)</li>
                <li>\(y\)-axis: \((x,y) \to (-x,y)\)</li>
                <li>\(y=x\): \((x,y) \to (y,x)\)</li>
                <li>\(y=-x\): \((x,y) \to (-y,-x)\)</li>
                <li>Line \(x=k\): \((x,y) \to (2k-x,y)\)</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Rotations (about origin)</h4>
              <ul>
                <li>90° CW: \((x,y) \to (y,-x)\)</li>
                <li>90° ACW: \((x,y) \to (-y,x)\)</li>
                <li>180°: \((x,y) \to (-x,-y)\)</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Translation &amp; enlargement</h4>
              <ul>
                <li>Vector \((a,b)\): \((x,y) \to (x+a,y+b)\)</li>
                <li>Enlargement SF \(k\) about origin: \((kx,ky)\)</li>
                <li>Area scale factor = \(k^2\)</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Combinations</h4>
              <ul>
                <li>Two parallel reflections → translation</li>
                <li>Two reflections in intersecting lines → rotation</li>
              </ul>
            </div>"""
    return _wrap_html(
        _card(
            "Transformations — Quick Reference",
            "Transformations quick reference",
            grid,
        )
    )


def mensuration_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">2D areas</h4>
              <ul>
                <li>Rectangle \(lw\) · Triangle \(\frac12 bh\)</li>
                <li>Parallelogram \(bh\) · Trapezium \(\frac12(a+b)h\)</li>
                <li>Circle \(\pi r^2\) · Sector \(\frac{\theta}{360}\pi r^2\)</li>
                <li>Circumference \(C = \pi d = 2\pi r\)</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Scale factors</h4>
              <ul>
                <li>Length × \(k\) · Area × \(k^2\) · Volume × \(k^3\)</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">3D volumes</h4>
              <ul>
                <li>Prism: area of cross-section × length</li>
                <li>Cylinder \(\pi r^2 h\) · Cone \(\frac13 \pi r^2 h\)</li>
                <li>Sphere \(\frac43 \pi r^3\) · Pyramid \(\frac13 \times base \times h\)</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Surface areas</h4>
              <ul>
                <li>Cylinder \(2\pi r(r+h)\) · Sphere \(4\pi r^2\)</li>
                <li>Cone slant height \(l = \sqrt{r^2+h^2}\)</li>
              </ul>
            </div>"""
    return _wrap_html(
        _card("Mensuration — Quick Reference", "Mensuration quick reference", grid)
    )


def pythagoras_card() -> str:
    grid = r"""
            <div>
              <h4 style="color:#1a6fa8;">Core rule</h4>
              <ul>
                <li>\(c^2 = a^2 + b^2\) (\(c\) = hypotenuse)</li>
                <li>Shorter side: \(a^2 = c^2 - b^2\)</li>
                <li>Converse: check \(a^2+b^2\) equals longest side squared</li>
              </ul>
              <h4 style="color:#1a6fa8;margin-top:14px;">Common triples</h4>
              <ul>
                <li>3-4-5 · 5-12-13 · 8-15-17</li>
              </ul>
            </div>
            <div>
              <h4 style="color:#1a6fa8;">Applications</h4>
              <ul>
                <li>Rectangle diagonal: \(\sqrt{w^2+h^2}\)</li>
                <li>3D: \(d^2 = l^2 + w^2 + h^2\)</li>
                <li>Coordinates: \(d = \sqrt{(\Delta x)^2 + (\Delta y)^2}\)</li>
              </ul>
              <p style="margin:12px 0 0;color:#555;font-size:0.95rem;">Never add lengths directly — square, add, then square root.</p>
            </div>"""
    return _wrap_html(
        _card("Pythagoras — Quick Reference", "Pythagoras quick reference", grid)
    )


HTML_REPLACEMENTS: dict[str, str] = {
    "gcse_maths_bidmas_lesson.html": bidmas_card(),
    "gcse_maths_multiples_factors_lesson.html": multiples_card(),
    "gcse_maths_algebra_lesson.html": algebra_card(),
    "gcse_maths_fdp_lesson.html": fdp_card(),
    "gcse_maths_geometry_angles_lesson.html": geometry_angles_card(),
    "gcse_maths_transformations_lesson.html": transformations_card(),
    "gcse_maths_mensuration_lesson.html": mensuration_card(),
    "gcse_maths_pythagoras_lesson.html": pythagoras_card(),
}

QR_SVG = re.compile(
    r'<svg(?![^>]*lesson-graph)(?![^>]*graphs-lesson-graph)[^>]*viewBox="[^"]+"[^>]*>.*?</svg>',
    re.DOTALL,
)

def _remove_div_block(content: str, marker: str) -> str:
    """Remove the first outermost <div ...marker...>…</div> block."""
    idx = content.find(marker)
    if idx == -1:
        return content
    start = content.rfind("<div", 0, idx)
    if start == -1:
        return content
    depth = 0
    i = start
    length = len(content)
    while i < length:
        if content.startswith("<div", i):
            depth += 1
            close = content.find(">", i)
            if close == -1:
                break
            i = close + 1
        elif content.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return content[:start] + content[i:]
        else:
            i += 1
    return content


def strip_html_cards(content: str) -> str:
    while 'class="revision-card-wrap"' in content:
        before = content
        content = _remove_div_block(content, 'class="revision-card-wrap"')
        if content == before:
            break
    while 'class="lesson-quick-ref-advanced"' in content:
        before = content
        content = _remove_div_block(content, 'class="lesson-quick-ref-advanced"')
        if content == before:
            break
    content = EMPTY_CENTER_WRAP.sub("", content)
    return content


def inject_html_card(content: str, card_html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        open_tag, body, close = match.groups()
        intro = ""
        for paragraph in re.finditer(r"<p[^>]*>.*?</p>", body, re.DOTALL):
            text = paragraph.group(0)
            lower = text.lower()
            if any(
                phrase in lower
                for phrase in ("use this", "revise", "revision card", "before a test")
            ):
                intro = text.strip() + "\n\n      "
                break
        return f"{open_tag}\n\n      {intro}{card_html}\n\n    {close}"

    new_content, count = QR_SECTION.subn(repl, content, count=1)
    if count == 0:
        raise ValueError("Quick Reference section not found")
    return new_content


def enhance_svg(svg: str) -> str:
    if 'class="revision-card-svg' not in svg:
        svg = re.sub(r"<svg", f"<svg {SVG_CLASS}", svg, count=1)
    svg = re.sub(r'style="[^"]*"', SVG_STYLE, svg, count=1)
    svg = svg.replace('font-size="15" fill="#28251d"', 'font-size="14" fill="#28251d"')
    svg = svg.replace('font-size="15" fill="#555555"', 'font-size="14" fill="#555555"')
    svg = re.sub(
        r'viewBox="0 0 520 (\d+)"',
        r'viewBox="0 0 760 \1"',
        svg,
    )
    return svg


def fix_qr_svg_in_section(content: str) -> str:
    def repl(match: re.Match[str]) -> str:
        open_tag, body, close = match.groups()
        svg_match = QR_SVG.search(body)
        if not svg_match:
            return match.group(0)
        enhanced = enhance_svg(svg_match.group(0))
        wrapped = enhanced
        if "revision-card-wrap" not in body[max(0, svg_match.start() - 80):svg_match.start()]:
            wrapped = f'      <div class="revision-card-wrap">\n        {enhanced}\n      </div>'
        body = body[: svg_match.start()] + wrapped + body[svg_match.end() :]
        return open_tag + body + close

    return QR_SECTION.sub(repl, content, count=1)


def remove_redundant_ul_after_card(content: str, filename: str) -> str:
    if filename not in HTML_REPLACEMENTS:
        return content
    pattern = re.compile(
        r"(</div>\s*</div>\s*)\n\s*<ul style=\"line-height:2[^\"]*\">.*?</ul>",
        re.DOTALL,
    )
    return pattern.sub(r"\1", content, count=1)


def process_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    original = content

    if path.name in HTML_REPLACEMENTS:
        content = strip_html_cards(content)
        content = inject_html_card(content, HTML_REPLACEMENTS[path.name])
        content = remove_redundant_ul_after_card(content, path.name)
    else:
        content = fix_qr_svg_in_section(content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = []
    for path in sorted(TEMPLATES.glob("gcse_maths_*_lesson.html")):
        if process_file(path):
            changed.append(path.name)
    if changed:
        print("Updated:", ", ".join(changed))
    else:
        print("No changes needed.")


if __name__ == "__main__":
    main()
