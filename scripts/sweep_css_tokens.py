"""U0.8: replace hardcoded colours in static/css with semantic tokens.

Two passes:
  1. Collapse `var(--x, <fallback>)` where --x is now defined in tokens.css.
     The fallbacks were dead code and several disagreed with the token
     (--color-primary fell back to teal #01696f while --primary was blue).
  2. Map literal hex values that exactly duplicate a token onto that token.

Anything left over is reported. Diagram/lesson-specific colours are expected
to survive this pass; they are dealt with in U5/U6.

Run from the repo root:  python scripts/sweep_css_tokens.py [--apply]
"""

from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

CSS_DIR = Path(__file__).resolve().parent.parent / 'static' / 'css'

# `var(--name, fallback)` -> `var(--name)`, for names defined in tokens.css.
COLLAPSE_FALLBACKS = [
    '--font-mono', '--text-muted', '--muted', '--text', '--surface',
    '--border-soft', '--surface-alt', '--primary-light', '--panel-bg',
    '--color-primary', '--ease', '--kb-inset', '--safe-bottom', '--safe-left',
]

# Literal hex -> token. Only values whose intent is unambiguous.
HEX_MAP = {
    '#1a6fa8': 'var(--primary)',
    '#1d7eb8': 'var(--primary-hover)',
    '#1565a8': 'var(--primary-hover)',
    '#0e4e7a': 'var(--primary-dark)',
    '#dce6ef': 'var(--border)',
    '#e4e9f0': 'var(--border)',
    '#e8f4fd': 'var(--brand-100)',
    '#64748b': 'var(--text-muted)',
    '#eef2f7': 'var(--surface-sunken)',
    '#f8fafc': 'var(--ink-50)',
    '#e2e8f0': 'var(--ink-200)',
    '#0f172a': 'var(--ink-900)',
    '#1e293b': 'var(--ink-800)',
    # Status
    '#16a34a': 'var(--success)',
    '#dc2626': 'var(--danger)',
    '#f0fdf4': 'var(--success-bg)',
    '#fef2f2': 'var(--danger-bg)',
    '#bbf7d0': 'var(--success-border)',
    '#fecaca': 'var(--danger-border)',
    '#dcfce7': 'var(--correct-100)',
    '#fde8e8': 'var(--wrong-100)',
    '#fef4e8': 'var(--streak-100)',
    '#fffbeb': 'var(--warning-bg)',
    '#d97706': 'var(--warning)',
    '#b45309': 'var(--streak-700)',
    '#166534': 'var(--correct-700)',
    '#2e7d32': 'var(--correct-700)',
    '#9b1c1c': 'var(--wrong-700)',
    '#991b1b': 'var(--wrong-700)',
    '#b42318': 'var(--wrong-700)',
    '#a02020': 'var(--wrong-700)',
}


def collapse(text: str) -> tuple[str, int]:
    n = 0
    for name in COLLAPSE_FALLBACKS:
        pattern = re.compile(r'var\(\s*' + re.escape(name) + r'\s*,[^()]*\)')
        text, hits = pattern.subn(f'var({name})', text)
        n += hits
    return text, n


def map_hex(text: str) -> tuple[str, int]:
    n = 0
    for hex_value, token in HEX_MAP.items():
        pattern = re.compile(re.escape(hex_value) + r'\b', re.IGNORECASE)
        text, hits = pattern.subn(token, text)
        n += hits
    return text, n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    total_collapsed = total_mapped = 0
    remaining: collections.Counter[str] = collections.Counter()

    for path in sorted(CSS_DIR.glob('*.css')):
        if path.name == 'tokens.css':
            continue
        original = path.read_text(encoding='utf-8')
        text, collapsed = collapse(original)
        text, mapped = map_hex(text)
        total_collapsed += collapsed
        total_mapped += mapped
        for h in re.findall(r'#[0-9a-fA-F]{3,8}\b', text):
            remaining[h.lower()] += 1
        if text != original:
            print(f'  {path.name:<20} {collapsed:>3} fallbacks, {mapped:>3} hex')
            if args.apply:
                path.write_text(text, encoding='utf-8')

    print(f'\ncollapsed {total_collapsed} fallbacks, mapped {total_mapped} hex values')
    print(f'remaining: {sum(remaining.values())} literals, {len(remaining)} distinct')
    for h, n in remaining.most_common():
        print(f'  {h} x{n}')
    if not args.apply:
        print('\nDry run. Re-run with --apply to write.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
