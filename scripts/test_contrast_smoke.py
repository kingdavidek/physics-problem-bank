"""U8.1 / D0 / D1 — WCAG 2.1 AA contrast smoke for semantic token pairs.

Run: python scripts/test_contrast_smoke.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKENS = ROOT / 'static' / 'css' / 'tokens.css'
DARK_MARKER = '@media (prefers-color-scheme: dark)'


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


def parse_aliases(css: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for name, value in re.findall(r'--([a-z0-9-]+):\s*([^;]+);', css):
        aliases[name] = value.strip()
    return aliases


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


def split_theme_css(css: str) -> tuple[str, str]:
    if DARK_MARKER not in css:
        return css, ''
    light, rest = css.split(DARK_MARKER, 1)
    return light, rest


# Body-sized text on surfaces must be >= 4.5:1. White-on-primary is the CTA pair.
PAIRS = (
    ('text', 'surface', 4.5),
    ('text-muted', 'surface', 4.5),
    ('text-subtle', 'surface', 4.5),
    ('text-muted', 'bg', 4.5),
    ('text-on-brand', 'brand-600', 4.5),
    ('on-correct', 'correct-50', 4.5),
    ('on-wrong', 'wrong-50', 4.5),
    ('on-streak', 'streak-100', 4.5),
    ('on-xp', 'xp-100', 4.5),
    ('on-brand', 'brand-50', 4.5),
    ('on-correct', 'correct-100', 4.5),
    ('on-wrong', 'wrong-100', 4.5),
    ('text', 'diagram-paper', 4.5),
)


def check_pairs(label: str, hex_tokens: dict[str, str], aliases: dict[str, str]) -> list[str]:
    failed = []
    print(f'--- {label} ---')
    for fg, bg, minimum in PAIRS:
        ratio = contrast_ratio(resolve(fg, hex_tokens, aliases), resolve(bg, hex_tokens, aliases))
        status = 'OK' if ratio + 1e-9 >= minimum else 'FAIL'
        print(f'{ratio:5.2f}  {status:4}  {fg} on {bg} (need {minimum})')
        if status == 'FAIL':
            failed.append(f'{label} {fg} on {bg}: {ratio:.2f} < {minimum}')
    return failed


def main() -> None:
    css = TOKENS.read_text(encoding='utf-8')
    assert DARK_MARKER in css, 'D0 dark override missing from tokens.css'
    light_css, dark_css = split_theme_css(css)
    light_hex = parse_hex_tokens(light_css)
    light_aliases = parse_aliases(light_css)
    failed = check_pairs('light', light_hex, light_aliases)

    dark_hex = dict(light_hex)
    dark_hex.update(parse_hex_tokens(dark_css))
    dark_aliases = dict(light_aliases)
    dark_block_aliases = parse_aliases(dark_css)
    dark_aliases.update(dark_block_aliases)
    # A dark `var(--…)` override must beat the light hex for the same name.
    for name, value in dark_block_aliases.items():
        if not value.startswith('#'):
            dark_hex.pop(name, None)
    failed.extend(check_pairs('dark', dark_hex, dark_aliases))

    if failed:
        print('FAILED: ' + '; '.join(failed))
        sys.exit(1)
    print('Contrast smoke OK')


if __name__ == '__main__':
    main()
