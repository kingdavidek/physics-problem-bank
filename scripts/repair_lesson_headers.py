"""Repair corrupted lesson headers after batch formatting."""
import re
from pathlib import Path

EXAM_PILLS = """    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">AQA</span>
      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">Edexcel</span>
      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">OCR</span>
    </div>
  </div>"""

GCSE_P = (
    '    <p style="margin:0;opacity:.9;font-size:.97rem;">'
    "GCSE Mathematics – Foundation and Higher Tier · All Exam Boards</p>"
)


def repair(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    original = content

    content = content.replace("<<div", "<div")
    content = content.replace("background:#fff;\">>", "background:#fff;\">")

    # Fix broken or incomplete exam-board pills before Quick Test
    content = re.sub(
        r"    <div style=\"margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;\">[\s\S]*?  <!-- Quick Test",
        EXAM_PILLS + "\n  <!-- Quick Test",
        content,
        count=1,
    )

    # Remove stray comment fragments (partial <p> lines)
    content = re.sub(r"\n  <!--[^═\n<][^\n]*</p>\n", "\n", content)

    # Move orphan intro (line-height paragraph) into header subtitle
    orphan = re.search(
        r"(  </div>\n  <!-- Quick Test button -->.*?</div>\n)\n"
        r"(  <p style=\"line-height:[^\"]*;\">[\s\S]*?</p>\n)\n"
        r"(  <!--)",
        content,
        re.DOTALL,
    )
    if orphan:
        intro_html = re.search(
            r"<p style=\"line-height:[^\"]*;\">([\s\S]*?)</p>",
            orphan.group(2),
        ).group(1).strip()
        new_sub = f'    <p style="margin:0;opacity:.9;font-size:.97rem;">{intro_html}</p>'
        if GCSE_P in content:
            content = content.replace(GCSE_P, new_sub, 1)
        content = content[: orphan.start()] + orphan.group(1) + "\n" + orphan.group(3) + content[orphan.end() :]

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"repaired: {path.name}")


for p in sorted(Path("templates").glob("gcse_maths_*_lesson.html")):
    repair(p)
