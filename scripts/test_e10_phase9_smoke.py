"""E10 Phase 9 smoke: the whole-change review of the celebrations (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md 11.16).
Run: python scripts/test_e10_phase9_smoke.py

Checks what the review fixed: a hidden element stays hidden whatever its display rule; brand-blue text uses a token that keeps
4.5:1 on both themes (the ratios are computed from tokens.css); one main landmark; named progress bar; real h2 headings over the
profile's h3s; the stage's layout for a phone on its side; the wording fixes.
"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

HDR = {'Accept': 'application/json'}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def _lum(hex_):
    h = hex_.lstrip('#')
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def token(css, name, block=0):
    """The value of --name in the n-th block that defines it (0: light :root, then the two dark blocks)."""
    vals = re.findall(rf'--{name}:\s*([^;]+);', css)
    return vals[block].strip()


def resolve(css, value, block):
    m = re.fullmatch(r'var\(--([\w-]+)\)', value)
    if not m:
        return value
    name = m.group(1)
    vals = re.findall(rf'--{name}:\s*([^;]+);', css)
    return resolve(css, vals[min(block, len(vals) - 1)].strip(), block)


def test_hidden_always_hides():
    base = read('static/css/base.css')
    assert '[hidden] { display: none !important; }' in base
    # the three buttons the review found showing although hidden: their own rules lost to a display rule
    assert 'S.got.hidden = id === ' in read('static/js/zorp-coach.js')
    assert 'c.skip.hidden = true;' in read('static/js/zorp-tour.js')
    assert 'replay.hidden = !(b.earned && canReplay());' in read('static/js/badge-sheet.js')


def test_brand_text_contrast():
    css = read('static/css/tokens.css')
    assert css.count('--brand-text:') == 3, 'light, dark (system) and dark (chosen)'
    light_text = resolve(css, token(css, 'brand-text', 0), 0)
    light_surface = resolve(css, token(css, 'surface', 0), 0)
    dark_text = resolve(css, token(css, 'brand-text', 1), 1)
    dark_surface = token(css, 'surface', 1)
    assert ratio(light_text, light_surface) >= 4.5, (light_text, light_surface, ratio(light_text, light_surface))
    assert ratio(dark_text, dark_surface) >= 4.5, (dark_text, dark_surface, ratio(dark_text, dark_surface))
    assert token(css, 'brand-text', 2) == token(css, 'brand-text', 1)
    uses = {
        'static/css/badge-stage.css': ('.bd-kicker {', '.badge-next-link {'),
        'static/css/chrome.css': ('.app-toast-action {',),
        'static/css/shelf.css': ('.shelf-next-kicker {', '.shelf-more > summary {'),
        'static/css/wardrobe.css': ('button.wd-why {',),
        'static/css/pages.css': ('.mastery-pct {',),
        'static/css/components.css': ('.btn-link {', '.profile-section-link {'),
    }
    for rel, rules in uses.items():
        src = read(rel)
        for rule in rules:
            body = src[src.index(rule):src.index('}', src.index(rule))]
            assert 'color: var(--brand-text)' in body, f'{rel} {rule}'
    pages = read('static/css/pages.css')
    active = pages[pages.index('.pill--filter.is-active,'):]
    active = active[:active.index('}')]
    assert 'background: var(--brand-600);' in active and ratio('#ffffff', resolve(css, token(css, 'brand-600', 0), 0)) >= 4.5
    chip = pages[pages.index('.recent-practised-chip.is-current {'):]
    assert 'color: var(--on-brand);' in chip[:chip.index('}')]
    assert '.profile-stat-card--xp strong { color: var(--on-xp); }' in read('static/css/components.css')


def test_one_main_landmark_and_headings():
    base = read('templates/base.html')
    assert base.count('<main id="main" class="site-wrapper') == 1 and base.count('</main>') == 1
    assert '<div class="site-wrapper' not in base
    from app import app
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    uid = c.post('/api/v1/auth/register', json={'email': f'p9_{s}@example.com', 'handle': f'p9_{s}', 'password': 'password123',
                                                'age_confirm': True}, headers=HDR).get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
        sess['pb_own'] = uid
    for path in ('/topics', '/profile', '/profile/settings', '/practice'):
        html = c.get(path).get_data(as_text=True)
        assert html.count('<main ') == 1 and html.count('</main>') == 1, path
    prof = read('templates/profile.html')
    assert '<div class="section-panel-header"><h2>Progress charts</h2></div>' in prof and '<h2>Milestones</h2>' in prof
    assert '.section-panel-header h2 { margin: 0; font: inherit; color: inherit; letter-spacing: inherit; }' in read('static/css/components.css')
    assert "topbarEl.setAttribute('aria-label', 'Lesson progress');" in read('static/js/lesson-progress.js')


def test_phone_on_its_side():
    css = read('static/css/stage.css')
    block = css[css.index('@media (orientation: landscape) and (max-height: 500px) {'):]
    for needle in ('.pb-stage:not([data-layout=choose]) .pb-st-set { right: 48%; }', 'width: 46%;',
                   '.pb-stage:not([data-layout=choose]) .bd-box, .pb-stage:not([data-layout=choose]) .mo-box', '.pb-st-mute { right: auto;'):
        assert needle in block, needle


def test_wording():
    moments = read('static/js/moments.js')
    for needle in ("lessonFirst: 'You finished every quick check in this lesson. Well done.'",
                   "week: 'You answered the question of the day on all seven days this week.'",
                   "backfillMany: 'You already earned {count} badges. They are on your profile now.'"):
        assert needle in moments, needle
    assert 'Daily question' not in read('models/badge_shelf.py').split('LINES', 1)[1][:4000]
    from models import gamification as gam
    for key, n in (('perfect_1', 'a lesson quiz'), ('perfect_5', '5 lesson quizzes'), ('perfect_20', '20 lesson quizzes')):
        assert gam.MILESTONE_CATALOG[key]['blurb'] == f'You got every answer right on {n}.', key
    assert "'Show full marks on a lesson quiz as a small card'" in read('templates/profile_settings.html')
    assert "'Choose light or dark, how much I move, and how I cheer, with or without sound.'" in read('static/js/zorp-tour.js')


def test_docs():
    plan = read('docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md')
    assert '### 11.16 Phase 9' in plan


def main():
    for t in (test_hidden_always_hides, test_brand_text_contrast, test_one_main_landmark_and_headings, test_phone_on_its_side, test_wording,
              test_docs):
        t()
        print('ok', t.__name__)
    print('E10 Phase 9 smoke passed.')


if __name__ == '__main__':
    main()
