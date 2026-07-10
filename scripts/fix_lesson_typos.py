from pathlib import Path

for p in Path("templates").glob("gcse_maths_*_lesson.html"):
    t = p.read_text(encoding="utf-8")
    t2 = t.replace("<<div", "<div").replace("background:#fff;\">>", "background:#fff;\">")
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print("fixed", p.name)
