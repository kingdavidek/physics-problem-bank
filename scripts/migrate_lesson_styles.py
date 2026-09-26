#!/usr/bin/env python3
"""U6.3 — map known lesson inline styles to the U6 class vocabulary.

Dry-run by default. Idempotent: a second pass is a no-op.

Does not rewrite teaching copy. Leaves unmatched `style=""` in place and
reports them.

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

SKIP_FILES: set[str] = set()

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

    # U6.5 — leftover inline styles (constructions/loci, A-level, one-offs)
    if tag == 'p' and c == compact_css('color:var(--text-muted)'):
        return ('lesson-muted',), True

    if tag == 'div' and css_has(c, 'border:1pxsolid#d4e6f1', 'border-radius:8px', 'padding:14px'):
        return ('lesson-tile',), True
    if tag == 'div' and css_has(c, 'font-weight:700', 'color:#1a6fa8', 'margin-bottom:8px'):
        return ('lesson-tile-title',), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:repeat(auto-fit,minmax(240px,1fr)'):
        return ('lesson-tile-grid',), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:repeat(auto-fit,minmax(200px,1fr)'):
        return ('lesson-tile-grid',), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:1fr1fr', 'gap:20px'):
        return ('lesson-tile-grid', 'lesson-tile-grid--2'), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:1fr1fr', 'gap:12px', 'margin:14px0'):
        return ('lesson-sign-grid', 'lesson-sign-grid--wide'), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:1fr1fr', 'gap:12px'):
        return ('lesson-sign-grid',), True

    if 'problem-card' in classes and css_has(c, 'border-left:4pxsolidvar(--color-primary)'):
        return ('problem-card--accent',), True

    if tag == 'a' and css_has(c, 'color:#1a6fa8', 'font-weight:600'):
        return ('lesson-link',), True
    if tag == 'a' and c == compact_css('color:#1a6fa8'):
        return ('lesson-link-plain',), True
    if tag == 'a' and css_has(c, 'display:inline-block', 'padding:8px16px', 'background:#059669'):
        return ('btn', 'btn-correct', 'btn-sm'), True
    if tag == 'a' and css_has(c, 'display:inline-block', 'margin:8px0'):
        return ('lesson-mt-md',), True

    if tag == 'div' and css_has(c, 'margin-top:12px', 'padding:12px') and 'background:var(--color-surface-offset)' in c:
        return ('lesson-solution',), True
    if tag == 'div' and css_has(c, 'margin-top:8px', 'padding:12px', 'background:var(--color-surface-offset)'):
        return ('lesson-solution',), True

    if tag == 'div' and css_has(c, 'background:var(--color-surface-2)', 'text-align:center'):
        return ('lesson-surface-chip',), True
    if tag == 'div' and css_has(c, 'background:#dbeafe', 'border-radius:7px', 'padding:10px14px', 'margin-top:12px'):
        return ('lesson-hint-box', 'lesson-hint-box--info'), True
    if tag == 'div' and css_has(c, 'background:#dcfce7', 'border-radius:7px', 'padding:10px14px', 'margin-top:8px'):
        return ('lesson-hint-box', 'lesson-hint-box--ok'), True
    if tag == 'div' and css_has(c, 'background:#fef9c3', 'border-left:4pxsolid#f59e0b'):
        return ('lesson-callout-strip',), True
    if tag == 'div' and css_has(c, 'background:#f1f5f9', 'font-family:monospace'):
        return ('lesson-code-box',), True

    if tag == 'div' and css_has(c, 'background:#dcfce7', 'border:1pxsolid#059669', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--pos'), True
    if tag == 'div' and css_has(c, 'background:#dcfce7', 'border:2pxsolid#059669', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--pos-strong'), True
    if tag == 'div' and css_has(c, 'background:#fce7f3', 'border:1pxsolid#a13544', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--neg'), True
    if tag == 'div' and css_has(c, 'background:#fce7f3', 'border:2pxsolid#a13544', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--neg-strong'), True
    if tag == 'div' and css_has(c, 'font-size:1.4rem', 'font-weight:700', 'color:#059669'):
        return ('lesson-sign-symbol', 'lesson-sign-symbol--pos'), True
    if tag == 'div' and css_has(c, 'font-size:1.4rem', 'font-weight:700', 'color:#a13544'):
        return ('lesson-sign-symbol', 'lesson-sign-symbol--neg'), True
    if tag == 'div' and css_has(c, 'font-size:1.2rem', 'font-weight:700', 'margin-bottom:6px'):
        return ('lesson-sign-heading',), True
    if tag == 'div' and css_has(c, 'font-weight:600', 'margin:4px0'):
        return ('lesson-sign-heading',), True
    if tag == 'div' and c == compact_css('font-size:.88rem;color:#444'):
        return ('lesson-sign-body',), True
    if tag == 'div' and css_has(c, 'font-size:.88rem', 'color:#444', 'margin-bottom:8px'):
        return ('lesson-sign-body', 'lesson-sign-body--spaced'), True
    if tag == 'div' and css_has(c, 'font-size:1rem', 'font-weight:600', 'color:#059669'):
        return ('lesson-sign-result', 'lesson-sign-result--pos'), True
    if tag == 'div' and css_has(c, 'font-size:1rem', 'font-weight:600', 'color:#a13544'):
        return ('lesson-sign-result', 'lesson-sign-result--neg'), True
    if tag == 'div' and css_has(c, 'font-size:.8rem', 'color:#555', 'margin-top:6px'):
        return ('lesson-sign-note',), True
    if tag == 'p' and css_has(c, 'background:#fce7f3', 'border-left:4pxsolid#a13544'):
        return ('lesson-warn-banner',), True

    if tag == 'img' and css_has(c, 'max-width:380px'):
        return ('lesson-img', 'lesson-img--sm'), True
    if tag == 'img' and css_has(c, 'max-width:420px'):
        return ('lesson-img', 'lesson-img--md'), True
    if tag == 'img' and css_has(c, 'max-width:280px'):
        return ('lesson-img', 'lesson-img--lg'), True
    if tag == 'img' and css_has(c, 'max-width:100%', 'margin:0auto'):
        return ('lesson-img',), True
    if tag == 'img' and css_has(c, 'max-width:100%', 'border-radius:8px'):
        return ('lesson-img',), True

    if tag == 'h3' and c == compact_css('margin-top:18px'):
        return ('lesson-h3-spaced',), True
    if tag == 'h3' and css_has(c, 'margin:0010px', 'color:#1a6fa8'):
        return ('lesson-h3-brand',), True

    if tag == 'svg' and c == compact_css('display:block;margin:auto'):
        return ('lesson-svg-center',), True
    if tag == 'svg' and css_has(c, 'max-width:100%', 'width:480px'):
        return ('lesson-svg-chart', 'lesson-svg-chart--480'), True
    if tag == 'svg' and css_has(c, 'max-width:100%', 'width:500px'):
        return ('lesson-svg-chart', 'lesson-svg-chart--500'), True
    if tag == 'svg' and css_has(c, 'max-width:100%', 'width:460px'):
        return ('lesson-svg-chart', 'lesson-svg-chart--460'), True
    if tag == 'svg' and c == compact_css('max-width:100%'):
        return ('lesson-svg-chart',), True

    if tag == 'div' and css_has(c, 'text-align:center', 'margin-top:24px', 'margin-bottom:48px'):
        return ('lesson-page-nav',), True
    if tag == 'div' and css_has(c, 'margin-top:12px', 'display:flex', 'gap:10px', 'flex-wrap:wrap'):
        return ('lesson-cta-row',), True
    if tag == 'div' and css_has(c, 'display:flex', 'align-items:center', 'gap:24px', 'flex-wrap:wrap', 'margin:20px0'):
        return ('lesson-flex-row',), True
    if tag == 'div' and css_has(c, 'display:flex', 'flex-wrap:wrap', 'gap:20px', 'justify-content:center', 'margin:20px0'):
        return ('lesson-flex-center',), True
    if tag == 'div' and css_has(c, 'display:flex', 'flex-wrap:wrap', 'gap:20px', 'align-items:flex-end'):
        return ('lesson-flex-end',), True
    if tag == 'div' and css_has(c, 'flex:1', 'min-width:200px', 'text-align:center'):
        return ('lesson-flex-item',), True
    if tag == 'div' and css_has(c, 'flex:1', 'min-width:250px', 'text-align:center'):
        return ('lesson-flex-item', 'lesson-flex-item--250'), True

    if tag == 'form' and c == compact_css('display:inline'):
        return ('lesson-form-inline',), True
    if tag == 'form' and c == compact_css('display:inline;margin-left:8px'):
        return ('lesson-form-inline', 'lesson-form-inline--gap'), True

    if tag == 'label' and css_has(c, 'display:block', 'font-size:0.9em', 'margin-bottom:4px'):
        return ('lesson-label',), True

    if tag == 'ol' and css_has(c, 'margin:0', 'padding-left:20px', 'line-height:1.9', 'color:#333'):
        return ('lesson-step-col',), True
    if tag == 'ul' and css_has(c, 'margin:0', 'padding-left:18px', 'line-height:1.75', 'font-size:0.95rem'):
        return ('lesson-list-tight',), True
    if tag == 'ul' and css_has(c, 'line-height:1.75', 'color:#333', 'padding-left:20px', 'margin:12px0'):
        return ('lesson-list-spaced',), True
    if tag == 'ul' and css_has(c, 'margin-top:8px', 'padding-left:20px'):
        return (), True
    if tag == 'ul' and c == compact_css('padding-left:20px'):
        return (), True
    if tag == 'ul' and css_has(c, 'margin:8px0020px', 'line-height:1.7'):
        return (), True

    if tag == 'p' and css_has(c, 'margin:8px00', 'font-size:1rem', 'color:#444'):
        return ('lesson-tile-caption',), True
    if tag == 'p' and css_has(c, 'font-size:1rem', 'margin:8px00', 'color:#444'):
        return ('lesson-body-text',), True
    if tag == 'p' and css_has(c, 'font-size:1rem', 'margin:8px00', 'color:#444', 'line-height:1.55'):
        return ('lesson-body-text',), True
    if tag == 'p' and css_has(c, 'font-size:1rem', 'color:#8a5300'):
        return ('lesson-warn-text',), True
    if tag == 'p' and css_has(c, 'color:#8a5300', 'background:#fef4e8', 'padding:8px12px'):
        return ('lesson-warn-pill',), True
    if tag == 'p' and css_has(c, 'font-weight:bold', 'color:var(--primary)'):
        return ('lesson-h3-brand',), True
    if tag == 'p' and c == compact_css('text-align:center;font-weight:bold'):
        return ('lesson-caption-center',), True
    if tag == 'p' and c == compact_css('font-size:0.9em;text-align:center'):
        return ('lesson-caption-center',), True
    if tag == 'p' and css_has(c, 'font-weight:600', 'margin-bottom:8px'):
        return (), True
    if tag == 'p' and css_has(c, 'font-size:1rem', 'margin-top:6px'):
        return ('lesson-caption-sm',), True
    if tag == 'p' and css_has(c, 'font-size:.88rem', 'color:#444', 'margin:008px', 'line-height:1.5'):
        return ('lesson-sign-body', 'lesson-sign-body--spaced'), True

    # Strip-only — spacing / inherited from section body
    STRIP_ONLY = {
        compact_css('margin-top:14px'),
        compact_css('margin-top:10px'),
        compact_css('margin-top:8px'),
        compact_css('margin:8px 0 0'),
        compact_css('margin:4px 0'),
        compact_css('margin:2px 0'),
        compact_css('margin:24px 0'),
        compact_css('margin-bottom:14px'),
        compact_css('margin-top:8px'),
        compact_css('margin-top:12px'),
        compact_css('text-align:center'),
        compact_css('text-align:center;font-size:1.05rem'),
        compact_css('line-height:1.8'),
        compact_css('font-weight:bold'),
        compact_css('margin:6px 0 0'),
        compact_css('margin-top:16px'),
    }
    if tag in ('p', 'div', 'hr') and c in STRIP_ONLY:
        return (), True
    if tag == 'hr' and c == compact_css('margin:10px 0'):
        return (), True
    if tag == 'line' and c == compact_css('cursor:pointer'):
        return (), True
    if tag == 'div' and c == compact_css('margin-top:8px'):
        return ('lesson-mt-sm',), True
    if tag == 'div' and c == compact_css('margin-top:12px'):
        return ('lesson-mt-md',), True
    if tag == 'div' and c == compact_css('margin-bottom:14px'):
        return ('lesson-mb-md',), True
    if tag == 'div' and c == compact_css('margin-bottom:16px'):
        return ('lesson-mb-lg',), True
    if tag == 'div' and c == compact_css('margin-bottom:12px'):
        return ('lesson-mb-md',), True
    if tag == 'div' and c == compact_css('max-width:100%'):
        return (), True
    if tag == 'div' and css_has(c, 'margin-top:16px', 'padding:16px', 'background:var(--color-surface-offset)'):
        return ('lesson-solution',), True
    if tag == 'div' and css_has(c, 'margin:20px0', 'background:#f9f8f5', 'border-radius:8px', 'padding:12px'):
        return ('lesson-tile',), True
    if tag == 'div' and css_has(c, 'background:#f0f9ff', 'border-radius:6px', 'padding:10px', 'font-size:.88rem'):
        return ('lesson-hint-box', 'lesson-hint-box--info'), True
    if tag == 'div' and css_has(c, 'background:#dcfce7', 'border-radius:6px', 'padding:10px', 'margin-top:8px'):
        return ('lesson-hint-box', 'lesson-hint-box--ok'), True
    if tag == 'div' and css_has(c, 'background:#f0f9ff', 'border-radius:7px', 'padding:12px', 'line-height:1.8'):
        return ('lesson-hint-box', 'lesson-hint-box--info'), True
    if tag == 'div' and css_has(c, 'font-size:.87rem', 'margin-top:8px', 'line-height:1.6', 'color:#333'):
        return ('lesson-caption-sm',), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:1fr1fr', 'gap:16px', 'margin-top:16px'):
        return ('lesson-tile-grid', 'lesson-tile-grid--2'), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:repeat(auto-fit,minmax(230px,1fr)'):
        return ('lesson-tile-grid',), True
    if tag == 'div' and css_has(c, 'display:grid', 'grid-template-columns:repeat(auto-fit,minmax(180px,1fr)'):
        return ('lesson-tile-grid',), True
    if tag == 'div' and css_has(c, 'background:#fce7f3', 'border-radius:8px', 'padding:12px', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--neg'), True
    if tag == 'div' and css_has(c, 'background:#e0fdf4', 'border-radius:8px', 'padding:12px', 'text-align:center'):
        return ('lesson-sign-tile', 'lesson-sign-tile--pos'), True
    if tag == 'div' and css_has(c, 'background:#fef9c3', 'border-radius:8px', 'padding:12px', 'text-align:center'):
        return ('lesson-callout-strip',), True
    if tag == 'div' and css_has(c, 'display:flex', 'gap:12px', 'font-size:1.2em', 'font-weight:bold'):
        return ('lesson-flex-row',), True
    if tag == 'div' and css_has(c, 'display:flex', 'gap:8px', 'align-items:center', 'margin-bottom:12px'):
        return ('lesson-cta-row',), True
    if tag == 'div' and css_has(c, 'display:none', 'gap:6px', 'align-items:center', 'flex:1'):
        return (), True
    if 'lesson-formula-panel' in classes:
        return (), True
    if tag == 'div' and css_has(c, 'color:#1a6fa8', 'margin-bottom:8px', 'font-weight:600'):
        return ('lesson-tile-title',), True

    if tag == 'p' and css_has(c, 'margin:6px00', 'font-size:.8rem', 'color:#555'):
        return ('lesson-caption-sm',), True
    if tag == 'p' and css_has(c, 'margin:4px0', 'font-weight:bold', 'color:#1a6fa8', 'font-size:1.1rem'):
        return ('lesson-sign-heading',), True
    if tag == 'p' and css_has(c, 'margin:4px0', 'font-weight:bold', 'color:#a13544', 'font-size:1.1rem'):
        return ('lesson-sign-heading',), True
    if tag == 'p' and css_has(c, 'margin:4px0', 'font-weight:bold', 'color:#059669', 'font-size:1.1rem'):
        return ('lesson-sign-heading',), True
    if tag == 'p' and css_has(c, 'margin:4px0', 'font-weight:bold', 'color:#b45309', 'font-size:1.1rem'):
        return ('lesson-sign-heading',), True
    if tag == 'p' and c == compact_css('margin:2px 0;font-size:1rem'):
        return (), True
    if tag == 'p' and css_has(c, 'font-size:.88rem', 'color:#444', 'margin:0010px', 'line-height:1.55'):
        return ('lesson-sign-body', 'lesson-sign-body--spaced'), True
    if tag == 'p' and css_has(c, 'margin-top:12px', 'color:#333'):
        return ('lesson-mt-md',), True
    if tag == 'p' and c == compact_css('color:#333'):
        return (), True
    if tag == 'p' and css_has(c, 'font-weight:bold', 'text-align:center'):
        return ('lesson-caption-center',), True
    if tag == 'p' and css_has(c, 'text-align:center', 'margin-top:8px', 'font-weight:500'):
        return ('lesson-caption-center',), True
    if tag == 'p' and css_has(c, 'margin-top:8px', 'font-weight:500'):
        return ('lesson-mt-sm',), True
    if tag == 'p' and css_has(c, 'font-weight:600', 'margin:16px08px', 'color:#1a6fa8'):
        return ('lesson-h3-brand',), True
    if tag == 'p' and css_has(c, 'font-weight:600', 'margin:20px08px', 'color:#1a6fa8'):
        return ('lesson-h3-brand',), True
    if tag == 'p' and css_has(c, 'font-size:1rem', 'color:#555', 'margin-top:8px'):
        return ('lesson-caption-sm',), True

    if tag == 'h3' and css_has(c, 'margin:0010px', 'color:#a13544'):
        return ('lesson-h3-brand',), True
    if tag == 'h3' and css_has(c, 'margin:0014px', 'text-align:center', 'font-size:1.1rem', 'color:#1a6fa8'):
        return ('lesson-h3-brand',), True

    if tag == 'ol' and css_has(c, 'line-height:1.8', 'padding-left:20px', 'color:#333'):
        return ('lesson-step-col',), True
    if tag == 'ol' and css_has(c, 'line-height:1.9', 'margin:8px012px20px'):
        return (), True
    if tag == 'ul' and css_has(c, 'margin:0', 'padding-left:16px', 'line-height:1.8', 'color:#333'):
        return ('lesson-list-tight',), True
    if tag == 'ul' and css_has(c, 'line-height:1.85', 'margin:12px012px20px'):
        return (), True
    if tag == 'ul' and css_has(c, 'line-height:1.75', 'margin:8px012px20px'):
        return (), True

    if tag == 'tr' and css_has(c, 'background:#1a6fa8', 'color:#fff'):
        return (), True
    if tag == 'img' and css_has(c, 'max-width:300px', 'border-radius:8px'):
        return ('lesson-img', 'lesson-img--lg'), True
    if tag == 'img' and css_has(c, 'max-width:350px', 'border-radius:8px'):
        return ('lesson-img', 'lesson-img--md'), True
    if tag == 'img' and css_has(c, 'max-width:400px', 'border-radius:8px'):
        return ('lesson-img', 'lesson-img--md'), True
    if tag == 'svg' and css_has(c, 'width:100%', 'max-width:400px', 'margin:0auto'):
        return ('lesson-svg-chart',), True

    if tag == 'blockquote' and css_has(c, 'background:var(--hint-bg)', 'border-left:3pxsolidvar(--primary)'):
        return ('lesson-callout',), True
    if tag == 'label' and css_has(c, 'display:block', 'font-weight:600', 'margin-bottom:4px', 'color:#1a6fa8'):
        return ('lesson-label',), True
    if tag == 'select' and c == compact_css('margin-bottom:12px'):
        return ('lesson-mb-md',), True
    if tag == 'span' and c == compact_css('letter-spacing:1px'):
        return (), True

    if tag in ('th', 'td', 'tr') and (
        'border-bottom' in c or 'padding:' in c or c == compact_css('text-align:center')
    ):
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
            print(f'  skip {path.name}')
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
