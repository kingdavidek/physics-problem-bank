"""Apply constructions_loci lesson shell formatting to all other GCSE maths lessons."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
SKIP = "gcse_maths_constructions_loci_lesson.html"

WRAPPER_OLD = re.compile(
    r'<div style="max-width:860px;\s*margin:0 auto;\s*padding:0 16px;">'
)
WRAPPER_NEW = '<div style="max-width:860px;margin:0 auto;padding:12px;">'

DETAILS_OPEN = (
    '<details class="lesson-section" open>',
    '<details open style="border:1px solid #d4e6f1;border-radius:8px;margin-bottom:12px;overflow:hidden;">',
)
DETAILS = (
    '<details class="lesson-section">',
    '<details style="border:1px solid #d4e6f1;border-radius:8px;margin-bottom:12px;overflow:hidden;">',
)

SUMMARY_STYLES = [
    'summary style="cursor:pointer;padding:14px 18px;background:var(--color-surface-2);border-radius:var(--radius);font-weight:600;font-size:1.05rem;margin-bottom:4px;"',
    'summary style="cursor:pointer; padding:14px 18px; background:var(--color-surface-2); border-radius:var(--radius); font-weight:600; font-size:1.05rem; margin-bottom:4px;"',
]
SUMMARY_NEW = (
    'summary style="background:#eaf4fb;padding:13px 16px;cursor:pointer;'
    'font-size:1.05rem;font-weight:700;color:#1a6fa8;list-style:none;'
    'display:flex;align-items:center;gap:10px;"'
)

INNER_DIV_STYLES = [
    '<div style="padding:16px;background:var(--color-surface);border-radius:0 0 var(--radius) var(--radius);margin-bottom:12px;">',
    '<div style="padding:16px; background:var(--color-surface); border-radius:0 0 var(--radius) var(--radius); margin-bottom:12px;">',
]
INNER_DIV_NEW = '<div style="padding:18px 20px;background:#fff;">'

EXAM_PILLS = '    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">'

NUM_CIRCLE = (
    '<span style="background:#1a6fa8;color:#fff;border-radius:50%;width:26px;'
    'height:26px;display:flex;align-items:center;justify-content:center;'
    'font-size:.85rem;flex-shrink:0;">{n}</span>'
)

def quick_test_top(topic: str) -> str:
    return f"""  <!-- Quick Test button -->
  <div style="text-align:right;margin-bottom:14px;">
    <a href="{{{{ url_for('topic_page', level='gcse', subject='maths', topic='{topic}') }}}}"
       style="background:#1a6fa8;color:#fff;padding:9px 20px;border-radius:7px;text-decoration:none;font-weight:600;font-size:.93rem;">
      ▶ Quick Practice Test
    </a>
  </div>

"""


def footer_block(topic: str) -> str:
    return f"""  <!-- Practice link -->
  <div style="text-align:center;margin-top:20px;padding:16px;background:#f0f9ff;border-radius:8px;">
    <p style="margin:0 0 10px;font-weight:600;color:#1a6fa8;">Ready to practise?</p>
    <a href="{{{{ url_for('topic_page', level='gcse', subject='maths', topic='{topic}') }}}}"
       style="background:#1a6fa8;color:#fff;padding:10px 28px;border-radius:8px;text-decoration:none;font-weight:700;">
      Start Practice Questions
    </a>
  </div>

"""


def extract_topic(content: str, path: Path) -> str:
    m = re.search(r"topic='([^']+)'", content)
    if m:
        return m.group(1)
    stem = path.stem  # gcse_maths_algebra_lesson
    if stem.startswith("gcse_maths_") and stem.endswith("_lesson"):
        return stem[len("gcse_maths_") : -len("_lesson")]
    raise ValueError("No topic slug found")


def build_header(h1: str, subtitle: str | None, intro: str | None) -> str:
    parts = [
        '  <!-- Header -->',
        '  <div style="background:linear-gradient(135deg,#1a6fa8,#0e4e7a);color:#fff;border-radius:10px;padding:22px 28px;margin-bottom:20px;">',
        f'    <h1 style="margin:0 0 6px;font-size:1.7rem;">{h1}</h1>',
    ]
    if intro:
        parts.append(f'    <p style="margin:0;opacity:.9;font-size:.97rem;">{intro}</p>')
    elif subtitle:
        parts.append(f'    <p style="margin:0;opacity:.9;font-size:.97rem;">{subtitle}</p>')
    parts.extend([
        '    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">',
        '      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">AQA</span>',
        '      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">Edexcel</span>',
        '      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">OCR</span>',
        '    </div>',
        '  </div>',
        '',
    ])
    return "\n".join(parts)


def replace_header(content: str, topic: str) -> str:
    """Replace h1 + optional muted + optional intro with gradient header + top quick test."""
    if "linear-gradient(135deg,#1a6fa8,#0e4e7a)" in content:
        return content
    pattern = re.compile(
        r"(<div style=\"max-width:860px;margin:0 auto;padding:12px;\">\s*\n)"
        r"\s*<h1>([^<]+)</h1>\s*\n"
        r"(?:\s*<p style=\"color:var\(--text-muted\);\">([\s\S]*?)</p>\s*\n)?"
        r"(?:\s*<p>([\s\S]*?)</p>\s*\n)?",
        re.DOTALL,
    )
    m = pattern.search(content)
    if not m:
        raise ValueError("Could not find header block")
    h1 = m.group(2).strip()
    muted = m.group(3).strip() if m.group(3) else None
    intro = m.group(4).strip() if m.group(4) else None
    header = build_header(h1, muted, intro)
    quick = quick_test_top(topic)
    return content[: m.start()] + m.group(1) + header + quick + content[m.end() :]


def fix_double_div(content: str) -> str:
    content = content.replace("<<div", "<div")
    return content.replace('background:#fff;">>', 'background:#fff;">')


GCSE_SUBTITLE = "GCSE Mathematics – Foundation and Higher Tier · All Exam Boards"


def move_orphan_intro_into_header(content: str) -> str:
    """Move intro paragraph after Quick Test into the gradient header subtitle."""
    pattern = re.compile(
        r"(  </div>\n  <!-- Quick Test button -->.*?</div>\n)\n"
        r"(  <p>[\s\S]*?</p>\n)\n"
        r"(  <!--)",
        re.DOTALL,
    )
    m = pattern.search(content)
    if not m:
        return content
    intro_inner = re.search(r"<p>([\s\S]*?)</p>", m.group(2))
    if not intro_inner:
        return content
    intro_html = intro_inner.group(1).strip()
    new_sub = f'    <p style="margin:0;opacity:.9;font-size:.97rem;">{intro_html}</p>'
    gcse_p = f'    <p style="margin:0;opacity:.9;font-size:.97rem;">{GCSE_SUBTITLE}</p>'
    if gcse_p in content:
        content = content.replace(gcse_p, new_sub, 1)
    else:
        content = content.replace(EXAM_PILLS, new_sub + "\n" + EXAM_PILLS, 1)
    return content[: m.start()] + m.group(1) + "\n" + m.group(3) + content[m.end() :]


def ensure_quick_test_top(content: str, topic: str) -> str:
    if "Quick Practice Test" in content:
        return content
    if "linear-gradient(135deg,#1a6fa8,#0e4e7a)" not in content:
        return content
    return re.sub(
        r"(<!-- Header -->\s*<div style=\"background:linear-gradient\(135deg,#1a6fa8,#0e4e7a\)[^>]*>[\s\S]*?</div>\n)",
        r"\1" + quick_test_top(topic),
        content,
        count=1,
    )


def add_section_numbers(content: str) -> str:
    def repl(m: re.Match) -> str:
        open_tag, body, close = m.group(1), m.group(2), m.group(3)
        if "border-radius:50%" in body and "flex-shrink:0" in body:
            return m.group(0)
        line = re.search(r"^\s*(\d+)\.\s*(.+?)\s*$", body, re.M)
        if not line:
            return m.group(0)
        n, title = line.group(1), line.group(2).strip()
        rest = body[line.end() :]
        return (
            f"{open_tag}\n"
            f"      {NUM_CIRCLE.format(n=n)}\n"
            f"      {title}{rest}{close}"
        )

    return re.sub(
        r"(<summary[^>]*>)(.*?)(</summary>)",
        repl,
        content,
        flags=re.DOTALL,
    )


def add_footer(content: str, topic: str) -> str:
    if "Ready to practise?" in content:
        return content
    footer = footer_block(topic)
    if "<script>" in content:
        return content.replace("\n<script>", "\n" + footer + "<script>", 1)
    return content.replace("\n{% endblock %}", "\n" + footer + "{% endblock %}", 1)


def format_file(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    topic = extract_topic(content, path)

    content = fix_double_div(content)
    content = WRAPPER_OLD.sub(WRAPPER_NEW, content)
    content = content.replace(DETAILS_OPEN[0], DETAILS_OPEN[1])
    content = content.replace(DETAILS[0], DETAILS[1])
    for old in SUMMARY_STYLES:
        content = content.replace(old, SUMMARY_NEW)
    for old in INNER_DIV_STYLES:
        content = content.replace(old, INNER_DIV_NEW)

    content = replace_header(content, topic)
    if "linear-gradient(135deg,#1a6fa8,#0e4e7a)" in content and "Quick Practice Test" not in content:
        content = ensure_quick_test_top(content, topic)
    content = move_orphan_intro_into_header(content)
    content = add_section_numbers(content)
    content = add_footer(content, topic)
    content = fix_double_div(content)

    path.write_text(content, encoding="utf-8")
    print(f"OK: {path.name}")


def main() -> None:
    for path in sorted(TEMPLATES.glob("gcse_maths_*_lesson.html")):
        if path.name == SKIP:
            continue
        try:
            format_file(path)
        except Exception as e:
            print(f"FAIL: {path.name}: {e}")


if __name__ == "__main__":
    main()
