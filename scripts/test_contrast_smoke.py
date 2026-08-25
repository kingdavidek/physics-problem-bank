"""U8.1 — WCAG 2.1 AA contrast smoke for semantic token pairs.

Run: python scripts/test_contrast_smoke.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / 'static' / 'css' / 'tokens.css'


def _srgb_channel(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    raw = hex_color.lstrip('#')
    r, g, b = (int(raw[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _srgb_channel(r) + 0.7152 * _srgb_channel(g) + 0.0722 * _srgb_channel(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    light, dark = sorted((relative_luminance(hex_a), relative_luminance(hex_b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def parse_hex_tokens(css: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for name, value in re.findall(r'--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;', css):
        found[name] = value.lower()
    return found


def resolve(name: str, hex_tokens: dict[str, str], aliases: dict[str, str]) -> str:
    if name in hex_tokens:
        return hex_tokens[name]
    target = aliases[name]
    if target.startswith('#'):
        return target.lower()
    if target.startswith('var(--') and target.endswith(')'):
        inner = target[6:-1]
        return resolve(inner, hex_tokens, aliases)
    raise KeyError(name)


def parse_aliases(css: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for name, value in re.findall(r'--([a-z0-9-]+):\s*([^;]+);', css):
        aliases[name] = value.strip()
    return aliases


# Body-sized text on surfaces must be >= 4.5:1. White-on-primary is the CTA pair.
PAIRS = (
    ('text', 'surface', 4.5),
    ('text-muted', 'surface', 4.5),
    ('text-subtle', 'surface', 4.5),
    ('text-muted', 'bg', 4.5),
    ('text-on-brand', 'brand-600', 4.5),
    ('correct-700', 'correct-50', 4.5),
    ('wrong-700', 'wrong-50', 4.5),
    ('streak-700', 'streak-100', 4.5),
    ('xp-700', 'xp-100', 4.5),
    ('brand-700', 'brand-50', 4.5),
)


def main() -> None:
    css = TOKENS.read_text(encoding='utf-8')
    hex_tokens = parse_hex_tokens(css)
    aliases = parse_aliases(css)
    failed = []
    for fg, bg, minimum in PAIRS:
        ratio = contrast_ratio(resolve(fg, hex_tokens, aliases), resolve(bg, hex_tokens, aliases))
        status = 'OK' if ratio + 1e-9 >= minimum else 'FAIL'
        print(f'{ratio:5.2f}  {status:4}  {fg} on {bg} (need {minimum})')
        if status == 'FAIL':
            failed.append(f'{fg} on {bg}: {ratio:.2f} < {minimum}')
    if failed:
        print('FAILED: ' + '; '.join(failed))
        sys.exit(1)
    print('Contrast smoke OK')


if __name__ == '__main__':
    main()
