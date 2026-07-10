"""Ensure all GCSE maths lessons have legible dark revision cards at the bottom."""
import re
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Insert before first matching anchor (file-specific order in tuple)
INSERT_MARKERS = (
    "\n  <!-- QUICK TEST",
    "\n  <!-- QUICK TEST BUTTONS",
    "\n</div>\n\n  <!-- Practice link -->",
)

CARD_STYLE = (
    'width="100%" viewBox="0 0 760 280" '
    'style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;"'
)

NEW_SECTIONS = {
    "gcse_maths_decimals_lesson.html": {
        "title": "Decimals — Quick Reference",
        "topic": "decimals",
        "num": "8",
        "year": "Year 9",
        "intro": "Use this card before a test. Line up decimal points for +/−, and count decimal places when you multiply.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Decimals revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Decimals — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Operations</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">Add/subtract: line up the decimal points</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Multiply: count total decimal places in answer</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Divide: make the divisor a whole number first</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Place value</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">Each column is ×10 — pad with zeros to compare</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">0.375 = 375 thousandths</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Fractions ↔ decimals</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Fraction → decimal: divide top ÷ bottom</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">¼ = 0.25, ⅜ = 0.375, ⅝ = 0.625</text>
          <text x="400" y="122" font-size="13" fill="#fbbf24" font-weight="bold">Higher (recurring)</text>
          <text x="400" y="142" font-size="13" fill="#e2e8f0">0.333… = ⅓ — dot or bar notation</text>
          <text x="400" y="162" font-size="13" fill="#e2e8f0">Multiply-and-subtract method for proofs</text>
        </svg>""",
        "mcq": ('A', "What is 2.4 × 0.5?", ["1.2", "12", "0.12", "2.9"],
                "2.4 × 0.5 = 1.2 (one decimal place in the answer)."),
    },
    "gcse_maths_number_lesson.html": {
        "title": "Number — Quick Reference",
        "topic": "number",
        "num": "9",
        "year": "Year 9",
        "intro": "Revise number types, powers and roots, and standard form before mixed exam questions.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Number revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Number — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Types of number</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">Natural, integer, rational, irrational</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Prime: only factors 1 and itself</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">HCF × LCM from factor trees / Venn</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Powers &amp; roots</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">aⁿ × aᵐ = aⁿ⁺ᵐ</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">√ and ∛ are inverse powers</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Standard form</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">a × 10ⁿ, 1 ≤ a &lt; 10</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Multiply: multiply a's, add powers</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">4500 = 4.5 × 10³</text>
        </svg>""",
        "mcq": ('C', "Write 3.2 × 10⁴ in ordinary form.", ["320", "3200", "32000", "0.00032"],
                "3.2 × 10⁴ = 32,000."),
    },
    "gcse_maths_ratio_proportion_lesson.html": {
        "title": "Ratio &amp; Proportion — Quick Reference",
        "topic": "ratio_proportion",
        "num": "9",
        "year": "Year 10",
        "intro": "Pick the right type of ratio question — sharing, scaling a recipe, or best buy.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Ratio revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Ratio &amp; Proportion — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Simplifying</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">Divide every part by the HCF</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">12 : 8 → 3 : 2</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Share £60 in ratio 3:2 → 3+2=5 parts</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Proportion</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">Direct: both ↑ together (y = kx)</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Inverse: one ↑, other ↓ (y = k/x)</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Recipes &amp; maps</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Scale every ingredient the same</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">1 : n on map → × n in real life</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Best buy: same unit price</text>
        </svg>""",
        "mcq": ('D', "Share £60 in ratio 2 : 3. How much for the 3 parts?", ["£24", "£30", "£36", "£40"],
                "5 parts total; one part = £12; 3 parts = £36."),
    },
    "gcse_maths_probability_lesson.html": {
        "title": "Probability — Quick Reference",
        "topic": "probability",
        "num": "8",
        "year": "Year 10",
        "intro": "Write probabilities as fractions/decimals from 0 to 1. Use tables or trees when there are two stages.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Probability revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Probability — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Basics</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">0 ≤ P ≤ 1</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">P(certain) = 1, P(impossible) = 0</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">P(not A) = 1 − P(A)</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Combined events</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">AND → multiply (if independent)</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">OR (mutually exclusive) → add</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Diagrams</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Sample space: list all outcomes</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Tree: multiply along branches</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Venn: overlap = both</text>
          <text x="400" y="138" font-size="13" fill="#e2e8f0">P(A|B): shrink sample space to B</text>
        </svg>""",
        "mcq": ('A', "A fair dice is rolled. P(getting a 6)?", ["1/6", "6", "1/3", "1/2"],
                "One favourable outcome out of six equally likely."),
    },
    "gcse_maths_statistics_lesson.html": {
        "title": "Statistics — Quick Reference",
        "topic": "statistics",
        "num": "8",
        "year": "Year 10",
        "intro": "Know when to use the mean, median or mode — and which chart fits the data.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Statistics revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Statistics — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Averages</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">Mean: total ÷ count</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Median: middle value (order first)</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Mode: most common</text>
          <text x="20" y="138" font-size="13" fill="#e2e8f0">Range = largest − smallest</text>
          <text x="20" y="162" font-size="13" fill="#fbbf24" font-weight="bold">Spread</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Grouped data: use midpoints</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Charts</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Bar / pie: categories</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Histogram: continuous (freq density)</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Cumulative freq → median/quartiles</text>
          <text x="400" y="138" font-size="13" fill="#e2e8f0">Box plot: Q1, median, Q3</text>
        </svg>""",
        "mcq": ('B', "Data: 3, 5, 5, 8. What is the median?", ["5", "5.5", "4", "8"],
                "Ordered: 3, 5, 5, 8 → average of middle two = 5."),
    },
    "gcse_maths_vectors_lesson.html": {
        "title": "Vectors — Quick Reference",
        "topic": "vectors",
        "num": "12",
        "year": "Year 10",
        "intro": "Column vectors show movement. Add for combined journeys; multiply by a number to scale.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Vectors revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Vectors — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Notation</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">→a or column (x, y)</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">AB = b − a (end − start)</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">BA = −AB</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Operations</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">Add: add x's and y's</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">k a: multiply both components by k</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Geometry</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Parallel vectors: one is multiple of other</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Midpoint: average of endpoints</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Magnitude |a| = √(x² + y²)</text>
        </svg>""",
        "mcq": ('C', "a = (2, 3), b = (−1, 4). What is a + b?", ["(1, 7)", "(3, 7)", "(1, 1)", "(3, −1)"],
                "Add components: (2+(−1), 3+4) = (1, 7)."),
    },
    "gcse_maths_trigonometry_lesson.html": {
        "title": "Trigonometry — Quick Reference",
        "topic": "trigonometry",
        "num": "14",
        "year": "Year 11",
        "intro": "Right-angled triangle? SOH CAH TOA. Otherwise use sine or cosine rule.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Trigonometry revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Trigonometry — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Right-angled (SOH CAH TOA)</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">sin = opp/hyp, cos = adj/hyp, tan = opp/adj</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Label sides relative to angle θ</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Pythagoras: a² + b² = c²</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Any triangle</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">Sine rule: a/sin A = b/sin B</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Cosine rule: a² = b² + c² − 2bc cos A</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Area &amp; exact values</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Area = ½ab sin C</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">sin 30° = ½, cos 60° = ½</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">tan 45° = 1</text>
        </svg>""",
        "mcq": ('A', "Right triangle: opp=3, hyp=5. Find sin θ.", ["3/5", "5/3", "4/5", "3/4"],
                "sin θ = opposite ÷ hypotenuse = 3/5."),
    },
    "gcse_maths_equations_inequalities_lesson.html": {
        "title": "Equations — Quick Reference",
        "topic": "equations_inequalities",
        "num": "10",
        "year": "Year 10",
        "intro": "Balance both sides. Factorise quadratics when possible; use the formula if not.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Equations revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Equations &amp; Inequalities — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Linear</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">Do the same to both sides</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">ax + b = c → x = (c − b)/a</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Unknowns on both sides: collect terms</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Quadratic</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">Factorise → each bracket = 0</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Formula: x = (−b ± √(b²−4ac))/2a</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Other</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Simultaneous: eliminate a variable</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Inequality: flip sign if ×/÷ by negative</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Show solution on number line</text>
        </svg>""",
        "mcq": ('A', "Solve 2x + 5 = 17.", ["x = 6", "x = 11", "x = 5", "x = 8"],
                "2x = 12 → x = 6."),
    },
    "gcse_maths_graphs_lesson.html": {
        "title": "Graphs — Quick Reference",
        "topic": "graphs",
        "num": "8",
        "year": "Year 10",
        "intro": "y = mx + c for straight lines. Quadratics give U-shaped curves; solve with graphs by finding intersections.",
        "svg": """<svg width="100%" viewBox="0 0 760 280" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Graphs revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Graphs — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Straight lines</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">y = mx + c (m = gradient)</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Gradient = rise ÷ run</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Parallel: same m; perpendicular: m₁m₂ = −1</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Quadratics</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">y = ax² + bx + c</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Turning point; roots where y = 0</text>
          <line x1="390" y1="48" x2="390" y2="260" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Solving</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Intersection of graphs = solutions</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">y = mx + c and ax² + bx + c</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Distance: √(Δx² + Δy²)</text>
        </svg>""",
        "mcq": ('A', "Line y = 2x + 1. What is the gradient?", ["2", "1", "½", "−2"],
                "In y = mx + c, m is the gradient."),
    },
}


def build_section(data: dict) -> str:
    correct, q, opts, hint = data["mcq"]
    letters = "ABCD"
    buttons = "\n".join(
        f'          <button class="btn mcq-btn" data-letter="{letters[i]}">{opts[i]}</button>'
        for i in range(4)
    )
    return f"""
  <!-- Revision card (auto-added) -->
  <details style="border:1px solid #d4e6f1;border-radius:8px;margin-bottom:12px;overflow:hidden;">
    <summary style="background:#eaf4fb;padding:13px 16px;cursor:pointer;font-size:1.05rem;font-weight:700;color:#1a6fa8;list-style:none;display:flex;align-items:center;gap:10px;">
      <span style="background:#1a6fa8;color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0;">{data["num"]}</span>
      {data["title"]}
      <span style="font-size:0.65rem;margin-left:8px;background:#e8f4fd;color:#1a6fa8;padding:2px 6px;border-radius:10px;">All Exam Boards</span>
      <span style="font-size:0.65rem;margin-left:6px;background:#fef4e8;color:#8a5300;padding:2px 6px;border-radius:10px;">{data["year"]}</span>
      <span style="font-size:0.65rem;margin-left:8px;background:#e8f4fd;color:#1a6fa8;padding:2px 6px;border-radius:10px;">Revision Card</span>
    </summary>
    <div style="padding:18px 20px;background:#fff;">

      <p>{data["intro"]}</p>

      <div style="text-align:center;margin:16px 0;">
        {data["svg"]}
      </div>

      <div style="background:var(--hint-bg); border-left:3px solid var(--primary); padding:14px 20px; margin:16px 0; border-radius:0 var(--radius) var(--radius) 0;">
        <p style="margin:0 0 8px; font-weight:600;">Quick Check</p>
        <div class="mcq-inline" data-correct="{correct}">
          <p style="margin:0 0 10px;">{q}</p>
{buttons}
          <p class="mcq-feedback" style="margin-top:8px; font-weight:600;"></p>
        </div>
        <p style="font-size:0.82rem; color:var(--text-muted); margin:8px 0 0;">{hint}</p>
      </div>

      <div style="margin-top:12px;">
        <a href="{{{{ url_for('topic_page', level='gcse', subject='maths', topic='{data["topic"]}') }}}}" style="display:inline-block;padding:8px 16px;background:var(--color-primary);color:#fff;border-radius:var(--radius);text-decoration:none;font-size:0.9rem;">Quick Test – Revision</a>
      </div>
    </div>
  </details>
"""


def legibility_pass(content: str) -> str:
    """Bump small fonts in dark revision SVGs and widen display."""
    if "#1e293b" not in content and "#1a2840" not in content:
        return content

    # Bump revision-card text sizes (dark-card palette only)
    for old, new in (
        ('font-size="10" fill="#e2e8f0"', 'font-size="12" fill="#e2e8f0"'),
        ('font-size="10" fill="#94a3b8"', 'font-size="12" fill="#94a3b8"'),
        ('font-size="11" fill="#e2e8f0"', 'font-size="13" fill="#e2e8f0"'),
        ('font-size="11" fill="#94a3b8"', 'font-size="13" fill="#94a3b8"'),
        ('font-size="10" fill="#fde68a"', 'font-size="12" fill="#fde68a"'),
        ('font-size="11" fill="#fde68a"', 'font-size="13" fill="#fde68a"'),
        ('font-size="11" fill="#bfdbfe"', 'font-size="13" fill="#bfdbfe"'),
        ('font-size="11" fill="#fecaca"', 'font-size="13" fill="#fecaca"'),
        ('font-size="11" fill="#fca5a5"', 'font-size="13" fill="#fca5a5"'),
        ('font-size="11" fill="#fbbf24"', 'font-size="13" fill="#fbbf24"'),
        ('font-size="10" fill="#fbbf24"', 'font-size="12" fill="#fbbf24"'),
        ('font-size="11" fill="#ffd080"', 'font-size="13" fill="#ffd080"'),
        ('font-size="11" fill="#e0e8ff"', 'font-size="13" fill="#e0e8ff"'),
    ):
        content = content.replace(old, new)

    # Standardise dark card SVG wrapper (fixed small widths → full width)
    content = re.sub(
        r'<svg width="\d+" height="\d+" viewBox="0 0 (\d+) (\d+)" '
        r'style="background:#1e293b[^"]*"',
        lambda m: f'<svg width="100%" viewBox="0 0 {m.group(1)} {m.group(2)}" '
                  f'style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;"',
        content,
    )
    content = re.sub(
        r'<svg width="\d+" height="\d+" viewBox="0 0 (\d+) (\d+)" '
        r'style="background:#1a2840[^"]*"',
        lambda m: f'<svg width="100%" viewBox="0 0 {m.group(1)} {m.group(2)}" '
                  f'style="max-width:760px;display:block;margin:0 auto;background:#1a2840;border-radius:10px;"',
        content,
    )
    # Already width=100% but missing max-width
    content = re.sub(
        r'(<svg width="100%" viewBox="0 0 \d+ \d+") '
        r'style="(max-width:\d+px; )?display:block; margin:auto[^"]*background:#1e293b',
        r'\1 style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;"',
        content,
    )
    return content


def sequences_dark_card() -> str:
    return """
      <div style="text-align:center;margin:16px 0;">
        <svg width="100%" viewBox="0 0 760 300" style="max-width:760px;display:block;margin:0 auto;background:#1e293b;border-radius:10px;" role="img" aria-label="Sequences revision card">
          <text x="380" y="28" font-size="16" fill="#93c5fd" text-anchor="middle" font-weight="bold">Sequences — Revision Card</text>
          <line x1="20" y1="38" x2="740" y2="38" stroke="#334155" stroke-width="1"/>
          <text x="20" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Arithmetic</text>
          <text x="20" y="78" font-size="13" fill="#e2e8f0">nth term: uₙ = a + (n−1)d</text>
          <text x="20" y="98" font-size="13" fill="#e2e8f0">Sum: Sₙ = n(a+l)/2</text>
          <text x="20" y="118" font-size="13" fill="#e2e8f0">Constant difference d</text>
          <text x="20" y="142" font-size="13" fill="#fbbf24" font-weight="bold">Geometric</text>
          <text x="20" y="162" font-size="13" fill="#e2e8f0">nth term: uₙ = arⁿ⁻¹</text>
          <text x="20" y="182" font-size="13" fill="#e2e8f0">Sum: Sₙ = a(rⁿ−1)/(r−1)</text>
          <text x="20" y="202" font-size="13" fill="#e2e8f0">S∞ = a/(1−r) if |r| &lt; 1</text>
          <line x1="390" y1="48" x2="390" y2="280" stroke="#334155" stroke-width="1"/>
          <text x="400" y="58" font-size="13" fill="#fbbf24" font-weight="bold">Other</text>
          <text x="400" y="78" font-size="13" fill="#e2e8f0">Quadratic nth: second diff constant</text>
          <text x="400" y="98" font-size="13" fill="#e2e8f0">Square numbers: n²</text>
          <text x="400" y="118" font-size="13" fill="#e2e8f0">Fibonacci: add previous two terms</text>
          <text x="400" y="138" font-size="13" fill="#e2e8f0">Is k in the sequence? Solve nth = k for n</text>
        </svg>
      </div>
"""


def main():
    for path in sorted(TEMPLATES.glob("gcse_maths_*_lesson.html")):
        content = path.read_text(encoding="utf-8")
        original = content
        changed = False

        if path.name in NEW_SECTIONS and "Revision card (auto-added)" not in content:
            section = build_section(NEW_SECTIONS[path.name])
            for marker in INSERT_MARKERS:
                if marker in content:
                    content = content.replace(marker, section + marker, 1)
                    changed = True
                    print(f"added card: {path.name}")
                    break

        if path.name == "gcse_maths_sequences_lesson.html" and 'background:#1e293b' not in content:
            # Replace light formula card block with dark legible card
            pattern = re.compile(
                r'      <!-- SVG formula card -->.*?</svg>\s*</div>',
                re.DOTALL,
            )
            if pattern.search(content):
                content = pattern.sub(sequences_dark_card().strip() + "\n", content, count=1)
                changed = True
                print(f"dark card: {path.name}")

        new_content = legibility_pass(content)
        if new_content != content:
            content = new_content
            changed = True
            print(f"legibility: {path.name}")

        if changed:
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
