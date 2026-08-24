#!/usr/bin/env python3
"""U6.3 — map known lesson inline styles to the U6 class vocabulary.

Dry-run by default. Idempotent: a second pass is a no-op.

Does not rewrite teaching copy. Leaves unmatched `style=""` in place and
reports them. Skips `gcse_physics_radioactivity_lesson.html` (U6.6).

Usage (from repo root):
  python scripts/migrate_lesson_styles.py
  python scripts/migrate_lesson_styles.py --file templates/gcse_maths_number_lesson.html
  python scripts/migrate_lesson_styles.py --apply --file templates/gcse_maths_number_lesson.html
"""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'templates'

SKIP_FILES = {
    # Standalone page with its own :root / palette — U6.6, not this codemod.
    'gcse_physics_radioactivity_lesson.html',
}

STYLE_ATTR_RE = re.compile(r'\s+style="[^"]*"', re.I)
CLASS_ATTR_RE = re.compile(r'\bclass="([^"]*)"')
TAG_OPEN_RE = re.compile(r'<([a-zA-Z][a-zA-Z0-9]*)((?:\s[^>]*)?)(/?)>', re.S)
STYLE_BLOCK_RE = re.compile(r'(<style\b[^>]*>.*?</style>)', re.I | re.S)


def compact_css(value: str) -> str:
    return re.sub(r'\s+', '', value).lower().rstrip(';')


def css_has(compacted: str, *parts: str) -> bool:
    return all(compact_css(part) in compacted for part in parts)


def class_list(open_tag: str) -> list[str]:
    match = CLASS_ATTR_RE.search(open_tag)
    if not match:
        return []
    return [item for item in match.group(1).split() if item]


def add_classes(open_tag: str, *names: str) -> str:
    have = class_list(open_tag)
    for name in names:
        if name and name not in have:
            have.append(name)
    packed = ' '.join(have)
    if CLASS_ATTR_RE.search(open_tag):
        return CLASS_ATTR_RE.sub(f'class="{packed}"', open_tag, count=1)
    return re.sub(r'^<([a-zA-Z][a-zA-Z0-9]*)', rf'<\1 class="{packed}"', open_tag, count=1)


def strip_style(open_tag: str) -> str:
    return STYLE_ATTR_RE.sub('', open_tag)


def style_value(open_tag: str) -> str | None:
    match = re.search(r'\sstyle="([^"]*)"', open_tag, re.I)
    return match.group(1) if match else None


def classify(tag: str, css: str, classes: list[str]) -> tuple[tuple[str, ...], bool]:
    """Return (classes to add, drop_style).

    drop_style False means leave the attribute (unmapped).
    """
    c = compact_css(css)
    tag = tag.lower()

    # Shell
    if tag == 'div' and css_has(c, 'max-width:860px', 'margin:0auto'):
        return ('lesson-shell',), True
    if tag == 'div' and css_has(c, 'max-width:820px', 'margin:0auto'):
        return ('lesson-shell',), True

    # Hero
    if tag == 'div' and 'linear-gradient(135deg,#1a6fa8' in c:
        return ('lesson-hero',), True
    if tag == 'h1' and css_has(c, 'margin:006px', 'font-size:1.7rem'):
        return (), True
    if tag == 'p' and css_has(c, 'opacity:.9', 'font-size:.97rem'):
        return ('hero-sub',), True
    if tag == 'div' and css_has(c, 'margin-top:10px', 'display:flex', 'gap:8px', 'flex-wrap:wrap'):
        return ('hero-pills',), True
    if tag == 'span' and css_has(c, 'rgba(255,255,255,.18)', 'border-radius:20px', 'font-size:.8rem'):
        return ('hero-pill',), True

    # Quiz / generator CTAs
    if tag == 'div' and css_has(c, 'text-align:right', 'margin-bottom:14px'):
        return ('lesson-quiz-cta',), True
    if tag == 'a' and css_has(c, 'background:#1a6fa8', 'padding:9px20px', 'font-weight:600'):
        return ('btn', 'btn-primary'), True
    if tag == 'a' and css_has(c, 'background:#1a6fa8', 'padding:10px28px', 'font-weight:700'):
        return ('btn', 'btn-primary'), True
    if tag == 'a' and css_has(c, 'display:inline-block', 'padding:8px16px', 'background:var(--color-primary)'):
        return ('btn', 'btn-primary', 'btn-sm'), True
    if tag == 'button' and css_has(c, 'background:#1a6fa8', 'color:#fff', 'cursor:pointer'):
        return ('btn', 'btn-primary'), True

    # Accordion (top-level GCSE pattern)
    if tag == 'details' and css_has(c, 'border:1pxsolid#d4e6f1', 'overflow:hidden'):
        return ('lesson-section',), True
    if tag == 'details' and css_has(c, 'border:1pxsolid#e2e8f0', 'border-radius:6px'):
        return ('lesson-subsection',), True
    if tag == 'summary' and css_has(c, 'background:#eaf4fb', 'font-weight:700', 'color:#1a6fa8'):
        return ('lesson-section-summary',), True
    if tag == 'summary' and css_has(c, 'background:#f8fafc', 'color:#334155'):
        return (), True
    if tag == 'summary' and css_has(c, 'cursor:pointer', 'padding:14px18px', 'background:var(--color-surface-2)'):
        return ('lesson-section-summary',), True
    if tag == 'span' and css_has(c, 'border-radius:50%', 'width:26px', 'height:26px', 'background:#1a6fa8'):
        return ('lesson-section-chip',), True
    if tag == 'span' and css_has(c, 'font-size:0.65rem', 'border-radius:10px', 'background:#fef4e8', 'color:#8a5300'):
        return ('lesson-tag', 'lesson-tag--warn'), True
    if tag == 'span' and css_has(c, 'font-size:0.65rem', 'border-radius:10px', 'background:#e8f4fd', 'color:#1a6fa8'):
        return ('lesson-tag',), True
    if tag == 'span' and css_has(c, 'font-size:0.65rem', 'border-radius:10px'):
        # Other exam-board / skill chips (purple, green, …)
        return ('lesson-tag',), True

    if tag == 'div' and css_has(c, 'padding:18px20px', 'background:#fff'):
        return ('lesson-section-body',), True
    if tag == 'div' and css_has(c, 'padding:14px16px8px', 'background:#fff'):
        return ('lesson-section-body',), True
    if tag == 'div' and c == compact_css('padding:14px 16px'):
        return ('lesson-section-body',), True
    if tag == 'div' and css_has(c, 'padding:16px', 'background:var(--color-surface)', 'margin-bottom:12px'):
        return ('lesson-section-body',), True

    # Lists — spacing lives on .lesson-section-body ol/ul
    if tag in ('ol', 'ul') and c in {
        compact_css('line-height:1.9'),
        compact_css('line-height:1.8'),
        compact_css('line-height:2'),
    }:
        return (), True

    # Quick check + callouts
    if tag == 'div' and css_has(c, 'border-left:4pxsolid#1a6fa8') and 'padding:14px16px' in c:
        return ('lesson-quickcheck',), True
    if tag == 'div' and css_has(c, 'border-left:3pxsolidvar(--primary)', 'padding:14px20px'):
        return ('lesson-quickcheck',), True
    if tag == 'p' and css_has(c, 'font-weight:600') and c in {
        compact_css('margin:0 0 8px;font-weight:600'),
        compact_css('margin:0 0 10px;font-weight:600'),
    }:
        return ('lesson-quickcheck-title',), True
    if tag == 'p' and c == compact_css('margin:0 0 10px'):
        return (), True
    if tag == 'p' and 'mcq-feedback' in classes and css_has(c, 'margin-top:8px', 'font-weight:600'):
        return (), True
    if tag == 'p' and c == compact_css('margin-top:8px;font-weight:600'):
        return (), True

    if tag == 'div' and css_has(c, 'background:#fff3cd', 'border-left:4pxsolid#f59e0b'):
        return ('lesson-callout', 'lesson-callout--warning'), True
    if tag == 'div' and css_has(c, 'border-left:4pxsolid#1a6fa8') and 'background:#dbeafe' in c:
        return ('lesson-callout', 'lesson-callout--note'), True
    if tag == 'div' and css_has(c, 'background:#eaf4fb', 'border-left:3pxsolid#1a6fa8'):
        return ('lesson-callout', 'lesson-callout--note'), True
    if tag == 'div' and css_has(c, 'border-left:4pxsolid#059669'):
        return ('lesson-callout', 'lesson-callout--exam'), True
    if tag in ('p', 'div') and css_has(c, 'background:#e8f4fd', 'text-align:center'):
        return ('lesson-callout', 'lesson-callout--formula'), True
    if tag == 'p' and css_has(c, 'background:#fffbeb', 'border-left:4pxsolid#f59e0b'):
        return ('lesson-callout', 'lesson-callout--warning'), True
    if tag == 'p' and css_has(c, 'border-left:4pxsolid#059669'):
        return ('lesson-callout', 'lesson-callout--exam'), True
    if tag == 'p' and css_has(c, 'text-align:center') and ('font-size:1.1rem' in c or 'font-size:1.1em' in c):
        return ('lesson-callout', 'lesson-callout--formula'), True
    if tag == 'p' and c in {
        compact_css('text-align:center'),
        compact_css('text-align:center;font-style:italic'),
    }:
        return (), True
    if tag == 'div' and 'problem-card' in classes and 'background:var(--color-surface-2)' in c:
        return (), True
    if tag == 'div' and c == compact_css('margin-top:12px'):
        return (), True
    if tag == 'tr' and c in {
        compact_css('background:var(--color-surface-2)'),
        compact_css('background:#eaf4fb'),
        compact_css('background:#f0f9ff'),
        compact_css('background:var(--color-surface-offset)'),
        compact_css('border-bottom:1px solid var(--color-border)'),
        compact_css('border-bottom:2px solid var(--color-border)'),
    }:
        return (), True
    if tag == 'th' and c in {
        compact_css('padding:10px;text-align:left'),
        compact_css('padding:8px 12px;text-align:left'),
    }:
        return (), True
    if tag == 'td' and c == compact_css('padding:7px 12px'):
        return (), True
    if tag == 'summary' and css_has(c, 'cursor:pointer', 'font-weight:bold', 'color:var(--color-primary)'):
        return (), True

    # Figures / diagrams
    if tag == 'div' and css_has(c, 'text-align:center') and 'margin:' in c and 'padding:' not in c:
        return ('lesson-figure',), True
    if tag == 'svg' and 'background:#f9f8f5' in c:
        return ('lesson-diagram',), True

    # Tables
    if tag == 'table' and ('border-collapse:collapse' in c or css_has(c, 'width:100%')):
        return ('lesson-table',), True
    if tag in ('th', 'td') and 'padding:' in c and 'border' in c:
        return (), True
    if tag in ('th', 'td') and c in {
        compact_css('padding:8px'),
        compact_css('padding:8px 12px'),
        compact_css('text-align:left;padding:8px'),
        compact_css('text-align:center'),
        compact_css('padding:9px;border-top:1px solid var(--color-divider)'),
        compact_css('padding:8px;border-top:1px solid var(--color-divider)'),
        compact_css('border-bottom:1px solid var(--color-border)'),
        compact_css('border-bottom:1px solid #ddd;text-align:left;padding:8px'),
        compact_css('border-bottom:1px solid var(--border)'),
        compact_css('border-bottom:1px solid var(--border);background:var(--color-surface-2)'),
    }:
        return (), True

    # Quick-ref headings / practice footer
    if tag == 'h4' and 'color:#1a6fa8' in c:
        return (), True
    if tag == 'div' and css_has(c, 'text-align:center', 'background:#f0f9ff', 'padding:16px'):
        return ('lesson-practice-cta',), True
    if tag == 'p' and css_has(c, 'color:#1a6fa8', 'font-weight:600') and 'margin:0010px' in c:
        return (), True

    # Captions under diagrams
    if tag == 'p' and css_has(c, 'color:var(--text-muted)') and 'font-size:' in c:
        return (), True

    return (), False


def transform_markup(html: str) -> tuple[str, int, list[tuple[str, str]]]:
    mapped = 0
    unmapped: list[tuple[str, str]] = []

    def repl(match: re.Match[str]) -> str:
        nonlocal mapped
        tag, attrs, slash = match.group(1), match.group(2) or '', match.group(3)
        open_tag = match.group(0)
        css = style_value(open_tag)
        if css is None:
            return open_tag
        classes = class_list(open_tag)
        extra, drop = classify(tag, css, classes)
        if not drop:
            unmapped.append((tag.lower(), css))
            return open_tag
        mapped += 1
        rewritten = strip_style(open_tag)
        if extra:
            rewritten = add_classes(rewritten, *extra)
        return rewritten

    return TAG_OPEN_RE.sub(repl, html), mapped, unmapped


def migrate_text(text: str) -> tuple[str, int, list[tuple[str, str]]]:
    chunks = STYLE_BLOCK_RE.split(text)
    out: list[str] = []
    mapped = 0
    unmapped: list[tuple[str, str]] = []
    for chunk in chunks:
        if STYLE_BLOCK_RE.fullmatch(chunk):
            out.append(chunk)
            continue
        new, n_mapped, leftover = transform_markup(chunk)
        out.append(new)
        mapped += n_mapped
        unmapped.extend(leftover)
    return ''.join(out), mapped, unmapped


def lesson_files(only: Path | None) -> list[Path]:
    if only:
        path = only if only.is_absolute() else ROOT / only
        return [path]
    return sorted(TEMPLATES.glob('*_lesson.html'))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Write files (default is dry-run)')
    parser.add_argument('--file', type=Path, help='Single template (relative to repo root or absolute)')
    args = parser.parse_args()

    total_mapped = 0
    leftover = collections.Counter()
    leftover_sample: dict[str, str] = {}
    files_changed = 0
    skipped = 0

    for path in lesson_files(args.file):
        if not path.exists():
            print(f'  missing: {path}')
            return 1
        if path.name in SKIP_FILES:
            skipped += 1
            print(f'  skip {path.name} (U6.6 radioactivity — not this migrator)')
            continue
        original = path.read_text(encoding='utf-8')
        updated, mapped, unmapped = migrate_text(original)
        total_mapped += mapped
        changed = updated != original
        if changed:
            files_changed += 1
            if args.apply:
                path.write_text(updated, encoding='utf-8')
        status = 'wrote' if (changed and args.apply) else ('would write' if changed else 'unchanged')
        print(f'  {status:<11} {path.name:<48} mapped {mapped:>4}  unmapped {len(unmapped):>3}')
        for tag, css in unmapped:
            key = f'{tag} | {compact_css(css)}'
            leftover[key] += 1
            leftover_sample.setdefault(key, path.name)

    print()
    print(f'mapped {total_mapped} attributes across {files_changed} file(s); skipped {skipped}')
    print(f'unmapped leftover: {sum(leftover.values())}  ({len(leftover)} distinct)')
    for key, count in leftover.most_common(80):
        style = key.split(' | ', 1)[1]
        print(f'  {count:4}  {key.split(" | ", 1)[0]:<8} {style[:110]}  [{leftover_sample[key]}]')
    if len(leftover) > 80:
        print(f'  … {len(leftover) - 80} more distinct signatures')
    if not args.apply:
        print('\nDry run. Re-run with --apply to write (U6.4: one file or small batches, then review).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
