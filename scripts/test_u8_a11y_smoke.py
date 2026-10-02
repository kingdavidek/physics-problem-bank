"""U8.3 / U8.6 — chrome a11y and CSS budget.

Run: python scripts/test_u8_a11y_smoke.py
"""
import os
import sys
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app  # noqa: E402

CSS_DIR = ROOT / 'static' / 'css'
LESSON_ONLY = {'lesson-pages.css', 'lesson-assist.css'}
# Uncompressed tree; D2 lesson SVG remaps live in lesson-pages.css.
# E6 Guide overlay + A3 spotlight + A6 streak fire + B gestures live in chrome.css.
# ES0 science subject tokens + year/unit topic-path headings.
# Stage 1 science hero + figure/table/print/gloss (lesson-pages) + MCQ feedback states.
# E7 §2 #11 (2026-09-20): raised by +14,000 in one deliberate bump to make room for
# motion.css (rig/idle/reaction clips, capped at 8KB per E7 §2 #8) plus a first slice
# of automatic Zorp cosmetics (§2 #12/#13) — colour/scale/mouth variants and, later,
# hat/hair/shoe overlays. Record actual bytes used per phase here, not the estimate.
# E7 Phase 1 (2026-09-22): motion.css = 2,288 bytes; tree now 218,686 (core 193,694).
# E7 Phase 1.5 (2026-09-23): motion.css = 4,028 bytes; tree now 220,426 (core 195,434).
# Budget NOT raised for this phase — headroom was already reserved by the §2 #11 bump.
# E7 Phase 1.6 (2026-09-24): motion.css unchanged at 4,028 bytes; tree now 220,510 (core 195,518).
# Budget NOT raised — only pages.css grew (~84 bytes) for the dev-only styleguide hero demo.
# E7 Phase 2 (2026-09-24): motion.css untouched (still 4,028 bytes, no react() code lives there —
# thought bubble is JS-created); practice.css grew ~659 bytes (quiz-runner-option animation
# selectors + checkmark position/colour fix). Tree now 221,169 (core 196,177). Budget NOT raised.
# E7 Phase 3 (2026-09-26): motion.css untouched (still 4,028 bytes) — welcome layout/dots/cards/
# transition CSS lives in pages.css instead (~2,126 bytes added, per §2 #8's "not motion.css" note
# for anything that isn't a shared rig/idle/reaction keyframe). Post-review fix added a small
# `.sr-only-submit` rule to chrome.css (~150 bytes, the Enter-key-submits-the-wrong-button fix).
# Tree now 223,496 (core 198,504). Budget NOT raised — plenty of headroom remained from the §2 #11 bump.
# E7 Phase 4 (2026-09-26): page-transition/View Transitions CSS in base.css, the combined
# btn-press keyframes + reduced-motion flash in practice.css, confetti shape/sparkle CSS in
# chrome.css, the shared `.pb-zorp-small` mascot class + streak-ring-peek positioning in
# pages.css, and one `flex-shrink` line in components.css together add ~4,123 bytes (no new
# file — motion.css untouched, still 4,028 bytes; figure includes post-review fixes: the
# reduced-motion @view-transition disable block and comment expansions in base.css/zorp-motion.js
# don't add CSS bytes beyond what's counted here). Tree now 227,619 bytes (core 202,627).
# Budget NOT raised — plenty of headroom remained from the §2 #11 bump.
# E7 Phase 5 (2026-09-26): motion_preference mirror rules — the universal data-motion
# catch-all plus small mirrors of the existing prefers-reduced-motion blocks in motion.css
# (idle-breathe/sway + zorp-pulse), chrome.css (.confetti-burst/.sparkle-bit), base.css
# (view-transition pseudo-elements), and practice.css (button colour-only flash) — add
# ~3,151 bytes across base.css/motion.css/chrome.css/practice.css, no lesson-only sheet
# touched. Tree now 230,770 bytes (core 205,778). Budget NOT raised — plenty of headroom
# remained from the §2 #11 bump.
# Buddy quiet fix (2026-09-27): chrome.css gained the face-only-Zorp rules (a defensive
# `.study-buddy-card[hidden]` rule, hiding the corner buddy while the PWA install banner
# is showing so the two mascots never stack, and lifting the corner buddy above the
# practice "new question" sticky bar, safe-area aware; click-through face) — ~1,731
# bytes after review fixes, no lesson-only sheet touched. Tree now 232,501 bytes (core
# 207,509). Budget NOT raised, but core headroom is now only ~2.5 KB — the next CSS
# addition should look for savings or raise the budget deliberately.
# E8 Phase 5 (2026-09-30): pages.css +about 200 bytes (welcome hero margin). Tree 236,037 (core 211,045); caps unchanged.
# E8 Phase 7 (2026-10-01): motion.css +about 400 bytes (dark-mode glow colour, side-view sweat rule). Tree 236,439 (core 211,447); caps unchanged.
# E8 Phase 1 (2026-09-29): raised 240,000 -> 246,000 (docs/ZORP_EXPRESSIVENESS.md 2.1). motion.css
# 4,844 -> 6,445 bytes (face colour props, .zk/.zf ink classes, .zorp-face pivots, twinkle and zzz
# keyframes with reduced/data-motion mirrors, minus the old data-mouth rules); chrome.css lost the
# eight face show-rules (about 600 bytes). Tree now 233,523 (core 208,531).
CSS_BUDGET_BYTES = 246_000
# Core sheets loaded on every page after the U8.6 lesson split.
# S0 added fonts.css (~1KB) plus legal-footer / email-verify chrome.
# E6 A1–A6 overlay/spotlight/streak-fire and B wink/nod/shake/tap live in chrome.css.
# ES0 science subject + /topics year-unit grouping.
# Stage 1 science hero accent (components) + MCQ live-feedback classes (practice).
# E7 §2 #11 (2026-09-20): raised by +11,000 alongside CSS_BUDGET_BYTES, same reason.
# E7 Phase 1 (2026-09-22): motion.css = 2,288 bytes; tree now 218,686 (core 193,694).
# E7 Phase 1.5 (2026-09-23): motion.css = 4,028 bytes; tree now 220,426 (core 195,434).
# Budget NOT raised for this phase — headroom was already reserved by the §2 #11 bump.
# E7 Phase 1.6 (2026-09-24): motion.css unchanged at 4,028 bytes; tree now 220,510 (core 195,518).
# Budget NOT raised — only pages.css grew (~84 bytes) for the dev-only styleguide hero demo.
# E7 Phase 2 (2026-09-24): practice.css grew ~659 bytes (see CSS_BUDGET_BYTES note above).
# Tree now 221,169 (core 196,177). Budget NOT raised.
# E7 Phase 3 (2026-09-26): pages.css grew ~2,126 bytes for the /welcome layout, chrome.css grew
# ~150 bytes in post-review fixes (see CSS_BUDGET_BYTES note above). Tree now 223,496 (core
# 198,504). Budget NOT raised.
# E7 Phase 4 (2026-09-26): see CSS_BUDGET_BYTES note above — ~4,123 bytes added across
# base.css/practice.css/chrome.css/pages.css/components.css, no lesson-only sheet touched
# (total and core grew by the same amount). Tree now 227,619 (core 202,627). Budget NOT raised.
# E7 Phase 5 (2026-09-26): see CSS_BUDGET_BYTES note above — ~3,151 bytes added, no
# lesson-only sheet touched (total and core grew by the same amount). Tree now 230,770
# (core 205,778). Budget NOT raised.
# Buddy quiet fix (2026-09-27): see CSS_BUDGET_BYTES note above — ~1,731 bytes added to
# chrome.css only, no lesson-only sheet touched (total and core grew by the same
# amount). Tree now 232,501 (core 207,509). Budget NOT raised.
# E8 Phase 1 (2026-09-29): raised 210,000 -> 216,000 alongside CSS_BUDGET_BYTES (see the note
# above; motion.css +1,601 bytes, chrome.css about -600 bytes). Tree now 233,523 (core 208,531).
# E8 Phase 2 (2026-09-29): motion.css 6,445 -> 7,466 bytes (fx keyframes drop/pop/orbit, fx slot
# pivots, wildcard reduced/data-motion mirrors). Budgets NOT raised. Tree now 234,544 (core 209,552).
# E8 Phase 3 (2026-09-29): motion.css 7,466 -> 7,895 bytes (arm pivot switch to view-box, flip wrapper,
# front-layer arm rule, plate pivot). Budgets NOT raised. Tree now 234,973 (core 209,981).
CSS_CORE_BUDGET_BYTES = 216_000


def test_tab_bar_aria_current():
    client = app.test_client()
    html = client.get('/').data.decode()
    assert 'id="app-tab-bar"' in html
    assert 'aria-label="Main navigation"' in html
    assert 'aria-current="page"' in html


def test_profile_tablist_markup():
    src = (ROOT / 'templates' / 'profile.html').read_text(encoding='utf-8')
    assert 'role="tablist"' in src
    assert 'aria-orientation="horizontal"' in src
    assert 'role="tab"' in src


def test_css_budget():
    files = sorted(CSS_DIR.glob('*.css'))
    total = sum(path.stat().st_size for path in files)
    core = sum(path.stat().st_size for path in files if path.name not in LESSON_ONLY)
    print(f'CSS uncompressed {total} bytes across {len(files)} files (core {core})')
    assert files, 'missing static/css'
    assert (CSS_DIR / 'lesson-pages.css').is_file()
    assert total <= CSS_BUDGET_BYTES, f'{total} exceeds {CSS_BUDGET_BYTES}'
    assert core <= CSS_CORE_BUDGET_BYTES, f'core {core} exceeds {CSS_CORE_BUDGET_BYTES}'


def test_lesson_pages_css_is_route_only():
    client = app.test_client()
    home = client.get('/').data.decode()
    assert 'lesson-pages.css' not in home
    lesson = client.get('/topic/gcse/maths/mensuration')
    assert lesson.status_code == 200
    html = lesson.data.decode()
    assert 'lesson-pages.css' in html
    assert html.index('pages.css') < html.index('lesson-pages.css')


def test_card_vocabulary_and_mcq_letter_markup():
    components = (ROOT / 'static' / 'css' / 'components.css').read_text(encoding='utf-8')
    assert '.card-raised' in components
    assert '.card-tinted' in components
    practice = (ROOT / 'static' / 'css' / 'practice.css').read_text(encoding='utf-8')
    assert '.mcq-letter' in practice
    assert '.mcq-btn[data-letter]::before' not in practice
    js = (ROOT / 'static' / 'js' / 'site.js').read_text(encoding='utf-8')
    assert 'decorateMcqButton' in js
    assert 'mcq-letter' in js
    assert '#16a34a' not in js
    assert '#dc2626' not in js
    tokens = (ROOT / 'static' / 'css' / 'tokens.css').read_text(encoding='utf-8')
    assert '--on-correct' in tokens
    assert '--on-wrong' in tokens
    assert '--diagram-paper' in tokens
    assert ':root[data-theme="dark"]' in tokens
    assert ':root:not([data-theme="light"])' in tokens
    theme_js = (ROOT / 'static' / 'js' / 'theme.js').read_text(encoding='utf-8')
    assert 'pb-theme' in theme_js
    pages = (ROOT / 'static' / 'css' / 'pages.css').read_text(encoding='utf-8')
    switch_knob = pages.split('.switch::after')[1].split('}')[0]
    assert 'background: #fff' not in switch_knob
    lesson_pages = (ROOT / 'static' / 'css' / 'lesson-pages.css').read_text(encoding='utf-8')
    assert '[fill="#1a6fa8"]' in lesson_pages
    assert 'lesson-table-wrap' in lesson_pages
    assert '@media print' in lesson_pages
    diagrams = (ROOT / 'static' / 'css' / 'diagrams.css').read_text(encoding='utf-8')
    assert '#f9f8f5' not in diagrams
    assert 'var(--diagram-paper)' in diagrams
    sg = (ROOT / 'templates' / 'styleguide.html').read_text(encoding='utf-8')
    assert 'class="card card-raised"' in sg
    assert 'class="mcq-letter"' in sg


def main():
    test_tab_bar_aria_current()
    test_profile_tablist_markup()
    test_css_budget()
    test_lesson_pages_css_is_route_only()
    test_card_vocabulary_and_mcq_letter_markup()
    print('U8 a11y / CSS budget smoke OK')


if __name__ == '__main__':
    main()
