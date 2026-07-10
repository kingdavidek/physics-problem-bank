from pathlib import Path
import re

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
issues = []
for f in sorted(TEMPLATES.glob("gcse_maths_*_lesson.html")):
    c = f.read_text(encoding="utf-8")
    idx = c.rfind("<!-- Practice link -->")
    if idx < 0:
        idx = c.rfind("QUICK TEST")
    tail = c[max(0, idx - 12000) : idx] if idx > 0 else c[-12000:]
    has_dark = "#1e293b" in tail or "#1a2840" in tail
    has_ref = bool(re.search(r"Quick Reference|Revision Card", tail, re.I))
    tiny = bool(re.search(r'font-size="10" fill="#e2e8f0"', tail))
    narrow = bool(re.search(r'viewBox="0 0 500 ', tail))
    status = "OK" if has_dark and has_ref else "MISSING"
    if not has_dark or not has_ref:
        issues.append(f.name)
    flags = []
    if tiny:
        flags.append("10px text")
    if narrow:
        flags.append("narrow viewBox")
    print(f"{f.name}: {status} {' '.join(flags)}")

print("---")
if issues:
    print("Needs attention:", ", ".join(issues))
else:
    print("All 22 lessons have dark revision cards at the bottom.")
