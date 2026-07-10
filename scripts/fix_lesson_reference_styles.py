"""Normalize quick-reference / formula panels in lesson HTML for legibility."""
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Order matters: longer / larger font sizes first
FONT_REPLACEMENTS = [
    ('font-size="16"', 'font-size="18"'),
    ('font-size="15"', 'font-size="17"'),
    ('font-size="14"', 'font-size="16"'),
    ('font-size="13"', 'font-size="15"'),
    ('font-size="12"', 'font-size="14"'),
    ('font-size="11"', 'font-size="14"'),
    ('font-size="10"', 'font-size="14"'),
]

FILL_REPLACEMENTS = [
    ('fill="#60a5fa"', 'fill="#1a6fa8"'),
    ('fill="#a0c4ff"', 'fill="#1a6fa8"'),
    ('fill="#93c5fd"', 'fill="#1a6fa8"'),
    ('fill="#7dd3fc"', 'fill="#1a6fa8"'),
    ('fill="#38bdf8"', 'fill="#1a6fa8"'),
    ('fill="#fbbf24"', 'fill="#1a6fa8"'),
    ('fill="#ffd080"', 'fill="#1a6fa8"'),
    ('fill="#fcd34d"', 'fill="#8a5300"'),
    ('fill="#fde68a"', 'fill="#8a5300"'),
    ('fill="#e2e8f0"', 'fill="#28251d"'),
    ('fill="#e0e8ff"', 'fill="#28251d"'),
    ('fill="#f1f5f9"', 'fill="#28251d"'),
    ('fill="#cbd5e1"', 'fill="#444444"'),
    ('fill="#94a3b8"', 'fill="#555555"'),
    ('fill="#64748b"', 'fill="#555555"'),
    ('fill="#86efac"', 'fill="#059669"'),
    ('fill="#4ade80"', 'fill="#059669"'),
    ('fill="#6ee7b7"', 'fill="#059669"'),
    ('fill="#f9a8d4"', 'fill="#a13544"'),
    ('fill="#fda4af"', 'fill="#a13544"'),
    ('fill="#fca5a5"', 'fill="#a13544"'),
    ('fill="#c4b5fd"', 'fill="#1a6fa8"'),
    ('fill="#a78bfa"', 'fill="#1a6fa8"'),
    ('fill="#f472b6"', 'fill="#a13544"'),
]

STROKE_REPLACEMENTS = [
    ('stroke="#334155"', 'stroke="#d4e6f1"'),
    ('stroke="#475569"', 'stroke="#d4e6f1"'),
    ('stroke="#445"', 'stroke="#d4e6f1"'),
    ('stroke="#64748b"', 'stroke="#b8c9d4"'),
]

BG_REPLACEMENTS = [
    ("background:#1e293b", "background:#f9f8f5;border:1px solid #d4e6f1"),
    ("background:#1a2840", "background:#f9f8f5;border:1px solid #d4e6f1"),
    ("background:#0f172a", "background:#f9f8f5;border:1px solid #d4e6f1"),
    ("background:#172554", "background:#f9f8f5;border:1px solid #d4e6f1"),
]

HTML_REPLACEMENTS = [
    (
        '<div style="background:#1e293b;color:#fff;border-radius:8px;padding:16px;font-size:.95rem;">',
        '<div class="lesson-formula-panel" style="background:#eaf4fb;color:#28251d;border:1px solid #d4e6f1;border-radius:8px;padding:16px;font-size:1rem;line-height:1.65;">',
    ),
    (
        '<div style="background:#1e293b;color:#fff;border-radius:8px;padding:16px;font-size:0.95rem;">',
        '<div class="lesson-formula-panel" style="background:#eaf4fb;color:#28251d;border:1px solid #d4e6f1;border-radius:8px;padding:16px;font-size:1rem;line-height:1.65;">',
    ),
    (
        '<div style="background:#1a2840;color:#fff;border-radius:8px;padding:16px;font-size:.95rem;">',
        '<div class="lesson-formula-panel" style="background:#eaf4fb;color:#28251d;border:1px solid #d4e6f1;border-radius:8px;padding:16px;font-size:1rem;line-height:1.65;">',
    ),
    (
        '<div style="color:#60a5fa;margin-bottom:6px;font-weight:600;">',
        '<div style="color:#1a6fa8;margin-bottom:8px;font-weight:600;font-size:1rem;">',
    ),
    (
        '<div style="color:#60a5fa;margin-bottom:8px;font-weight:600;">',
        '<div style="color:#1a6fa8;margin-bottom:8px;font-weight:600;font-size:1rem;">',
    ),
    (
        '<div style="margin-top:8px;color:#86efac;">',
        '<div style="margin-top:8px;color:#059669;font-weight:600;font-size:1rem;">',
    ),
    (
        '<div style="margin-top:10px;color:#86efac;">',
        '<div style="margin-top:10px;color:#059669;font-weight:600;font-size:1rem;">',
    ),
    (
        'font-size:.85rem;',
        'font-size:1rem;',
    ),
    (
        'font-size:0.85rem;',
        'font-size:1rem;',
    ),
    (
        'font-size:.9rem;',
        'font-size:1rem;',
    ),
    (
        'font-size:0.9rem;',
        'font-size:1rem;',
    ),
    (
        'background:#f9f8f5;border:1px solid #d4e6f1;color:#fff;',
        'background:#eaf4fb;border:1px solid #d4e6f1;color:#28251d;',
    ),
]


def apply_replacements(text: str) -> str:
    for old, new in (
        BG_REPLACEMENTS
        + FILL_REPLACEMENTS
        + STROKE_REPLACEMENTS
        + FONT_REPLACEMENTS
        + HTML_REPLACEMENTS
    ):
        text = text.replace(old, new)
    return text


def main() -> None:
    changed = []
    for path in sorted(TEMPLATES.glob("*lesson*.html")):
        original = path.read_text(encoding="utf-8")
        updated = apply_replacements(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.name)
    print(f"Updated {len(changed)} files:")
    for name in changed:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
