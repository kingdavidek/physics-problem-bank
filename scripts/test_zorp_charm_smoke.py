"""E9 Zorp charm: budget ledger, library bans and static wiring (docs/ZORP_CHARM.md).

Run: python scripts/test_zorp_charm_smoke.py

Phase 0 (2026-10-04) records the section 2.1 ledger at its measured baseline and adds the bans that
hold for the whole epic (no animation or audio library, no audio file). The rule: CAPS are enforced
(fail); BASELINE is the recorded P0 column of the doc ledger and is never edited again; drift from it
is printed, not failed, because unrelated work (any CSS file, the page) moves these numbers too. Each
E9 phase records its own measured column in the doc ledger. CAPS only rise by a dated ledger entry
(measured need plus about 10 percent, the rule David authorised on 2026-10-02).

Phase 5 (2026-10-06) adds test_showreel_section, test_evaluation_kit and test_phase5_docs.

Phase 1 (built 2026-10-04) adds test_talk_js_budget and the talk wiring checks, Phase 2 the soft-body checks, Phase 4
(2026-10-06) test_sound_js_budget, test_cues_only_from_beat_start and the sound preview and pin checks (see section 6).
"""
import os

os.environ['PB_TESTING'] = '1'
os.environ.setdefault('PB_STYLEGUIDE', '1')

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

JS_DIR = ROOT / 'static' / 'js'
CSS_DIR = ROOT / 'static' / 'css'
STATIC = ROOT / 'static'
DOC = ROOT / 'docs' / 'ZORP_CHARM.md'
LESSON_ONLY_CSS = {'lesson-pages.css', 'lesson-assist.css'}  # same split as test_u8_a11y_smoke.py

# Measured 2026-10-04 on main 43e387e (nothing in static/ changed in Phase 0). Bytes unless noted.
BASELINE = {
    'zorp_motion_js': 53_406,
    'zorp_poses_js': 30_185,
    'parts_library': 16_562,        # <template> only
    'rig_island': 5_362,            # with its <script> tags
    'default_instance': 3_036,
    'default_instance_elements': 50,
    'page_mascot': 31_137,          # 3 mascots + library + island on a logged-in /
    'page_mascot_gzip': 5_096,
    'motion_css': 9_170,
    'css_total': 236_921,
    'css_core': 211_929,
    'sound_js': 3_557,
    'guide_js': 24_347,
    'study_buddy_js': 13_398,
    'guide_catalog_js': 8_805,
}
# Not in BASELINE (the file is new in Phase 1); its own cap, measured per phase from P1.

# Caps in force today (the E8 constants this ledger mirrors) and the E9 caps from section 2.1.
# Where E9 raises a cap, the raise lands in the phase named here, never earlier.
RUNTIME_JS_MAX_BYTES = 56_000        # unchanged by E9 (about 150 B for the talking gate)
POSES_JS_MAX_BYTES = 36_500          # RAISED 33_200 -> 36_500 on 2026-10-04 (Phase 2, the plan's own raise): measured 35_531 B (soft body layer, jelly, cheek, antenna whip, cheer and hop beat clips), 35_909 B after the review, headroom 591 B for the Phase 4 cue hooks; ledger in docs/ZORP_CHARM.md 2.1
TALK_JS_MAX_BYTES = 10_500           # new file; plan estimate 5.5 KB and cap 7_000. Raised 2026-10-04 (Phase 1): measured 8_298 B, need plus about 9 percent (8_662 B after the review fix). RAISED 9_000 -> 10_500 on 2026-10-12 (final audit A3): the motion-drop hush measured 9_550 B, need plus about 10 percent
SOUND_JS_MAX_BYTES = 9_900           # RAISED 7_000 -> 9_900 on 2026-10-06 (Phase 4): the plan's 5.6 KB estimate did not allow for the gate, the arbiter, the cue bus, stopAll, the blips and the unlock hooks; measured 8_971 B, need plus about 10 percent; ledger in docs/ZORP_CHARM.md 2.1
PARTS_LIBRARY_MAX_BYTES = 18_200     # talk mouths add about 600 B; raise only with a ledger entry
RIG_JSON_MAX_BYTES = 6_000
INSTANCE_DEFAULT_MAX_BYTES = 4_500
INSTANCE_MAX_ELEMENTS = 70
PAGE_MASCOT_MAX_BYTES = 36_000
PAGE_MASCOT_MAX_GZIP = 6_000
MOTION_CSS_BUDGET_BYTES = 12_000     # E9 adds about 450 B (talk and ride pivots, .zorp-sr, belly origin)
CSS_BUDGET_BYTES = 246_000           # unchanged: core headroom 4_071 B covers the about 600 B E9 needs
CSS_CORE_BUDGET_BYTES = 216_000

CAPS = {
    'zorp_motion_js': RUNTIME_JS_MAX_BYTES,
    'zorp_poses_js': POSES_JS_MAX_BYTES,
    'parts_library': PARTS_LIBRARY_MAX_BYTES,
    'rig_island': RIG_JSON_MAX_BYTES,
    'default_instance': INSTANCE_DEFAULT_MAX_BYTES,
    'default_instance_elements': INSTANCE_MAX_ELEMENTS,
    'page_mascot': PAGE_MASCOT_MAX_BYTES,
    'page_mascot_gzip': PAGE_MASCOT_MAX_GZIP,
    'motion_css': MOTION_CSS_BUDGET_BYTES,
    'css_total': CSS_BUDGET_BYTES,
    'css_core': CSS_CORE_BUDGET_BYTES,
    'sound_js': SOUND_JS_MAX_BYTES,
    'zorp_talk_js': TALK_JS_MAX_BYTES,
}

# Case-insensitive text scan of the whole static/ tree. Word-bounded so "milestone.js" is not "tone.js".
LIBRARY_BANS = re.compile(r'(?<![\w.-])(?:lottie|howler|tone(?:\.js|js)(?!\w))')
AUDIO_EXTENSIONS = ('.mp3', '.ogg', '.oga', '.wav', '.m4a', '.aac', '.flac', '.opus', '.weba', '.mid', '.midi')
# First-party sources only (vendor code mentions them). Word-bounded so ".wave(" or a ".wave" class is not ".wav".
AUDIO_REFERENCES = re.compile(r'<audio\b|new audio\(|\.(?:mp3|ogg|oga|wav|m4a|flac|opus)\b')


def _size(path):
    return Path(path).stat().st_size


def measure():
    """Every ledger value, measured now. Needs the app (renders templates in memory, one page request)."""
    import test_zorp_expression_smoke as e8  # noqa: E402 - its helpers render the same way the E8 ledger does

    from app import app  # noqa: E402

    default_svg = e8._render(lambda m: str(m.buddy_mascot()))
    tpl, island = e8._split_library(e8._library_html())
    with app.test_client() as client:
        e8._register(client)
        html = client.get('/').data.decode()
    mascots = re.findall(r'<svg class="buddy-mascot".*?</svg>', html, re.S)
    p_tpl, p_island = e8._split_library(html)
    joined = ''.join(mascots) + p_tpl + p_island
    css_files = sorted(CSS_DIR.glob('*.css'))
    return {
        'zorp_motion_js': _size(JS_DIR / 'zorp-motion.js'),
        'zorp_poses_js': _size(JS_DIR / 'zorp-poses.js'),
        'parts_library': len(tpl.encode('utf-8')),
        'rig_island': len(island.encode('utf-8')),
        'default_instance': len(default_svg.encode('utf-8')),
        'default_instance_elements': e8._elements(default_svg),
        'page_mascot': len(joined.encode('utf-8')),
        'page_mascot_gzip': e8._gz(joined),
        'motion_css': _size(CSS_DIR / 'motion.css'),
        'css_total': sum(_size(p) for p in css_files),
        'css_core': sum(_size(p) for p in css_files if p.name not in LESSON_ONLY_CSS),
        'sound_js': _size(JS_DIR / 'sound.js'),
        'zorp_talk_js': _size(JS_DIR / 'zorp-talk.js'),
        'guide_js': _size(JS_DIR / 'guide.js'),
        'study_buddy_js': _size(JS_DIR / 'study-buddy.js'),
        'guide_catalog_js': _size(JS_DIR / 'guide-catalog.js'),
    }


_MEASURED = None


def measured():
    global _MEASURED
    if _MEASURED is None:
        _MEASURED = measure()
    return _MEASURED


def test_ledger_within_caps():
    got = measured()
    for name, cap in CAPS.items():
        print(f'  {name}: {got[name]:,} of {cap:,} (headroom {cap - got[name]:,})')
        assert got[name] <= cap, f'{name} {got[name]} exceeds its cap {cap}'


def test_ledger_baseline_recorded():
    """Report only: drift of every measured value from the recorded P0 baseline (the caps are what fail).
    A phase copies these numbers into its own column of the docs/ZORP_CHARM.md section 2.1 ledger."""
    got = measured()
    assert set(BASELINE) <= set(got), sorted(set(BASELINE) - set(got))
    for name, base in BASELINE.items():
        delta = got[name] - base
        print(f'  {name}: {got[name]:,} (P0 {base:,}, {"+" if delta >= 0 else ""}{delta:,})')


def test_ledger_doc_matches_constants():
    """Section 2.1 'P0' column carries the measured numbers (comma formatted) and the doc names the constants."""
    text = DOC.read_text(encoding='utf-8')
    start = text.index('### 2.1 Budget ledger')
    end = text.index('## 3. Detailed design')
    ledger = text[start:end]
    for key in ('zorp_motion_js', 'zorp_poses_js', 'parts_library', 'rig_island', 'default_instance', 'page_mascot',
                'motion_css', 'css_total', 'css_core', 'sound_js'):
        assert f'{BASELINE[key]:,}' in ledger, f'{key} baseline {BASELINE[key]:,} missing from the doc ledger'
    for name in ('TALK_JS_MAX_BYTES', 'SOUND_JS_MAX_BYTES', 'RUNTIME_JS_MAX_BYTES', 'POSES_JS_MAX_BYTES'):
        assert name in ledger, name
    assert POSES_JS_MAX_BYTES == 36_500 and '36,500' in ledger and '2026-10-04' in ledger
    assert f'{TALK_JS_MAX_BYTES:,}' in ledger and f'{SOUND_JS_MAX_BYTES:,}' in ledger
    assert 'Measured (Phase 1' in text, 'the Phase 1 measured column is recorded in section 2.1'
    assert 'Measured (Phase 2' in text, 'the Phase 2 measured column is recorded in section 2.1'
    assert 'Measured (Phase 4' in text, 'the Phase 4 measured column is recorded in section 2.1'
    assert 'Measured (Phase 5' in text, 'the Phase 5 measured column is recorded in section 2.1'


def test_no_animation_or_audio_libraries():
    """E9 stays hand-built SVG + WAAPI + WebAudio oscillators (E7 section 2 #9 and #12): no library, no audio file."""
    files = [p for p in sorted(STATIC.rglob('*')) if p.is_file()]
    assert files, 'static/ is empty'
    audio_files = [str(p.relative_to(ROOT)) for p in files if p.suffix.lower() in AUDIO_EXTENSIONS]
    assert not audio_files, f'audio files under static/ (oscillators only, no files): {audio_files}'
    for path in files:
        if path.suffix.lower() not in ('.js', '.css', '.html', '.json', '.svg', '.md', '.webmanifest', '.txt', '.mjs'):
            continue
        text = path.read_text(encoding='utf-8', errors='ignore').lower()
        rel = path.relative_to(ROOT)
        hit = LIBRARY_BANS.search(text)
        assert not hit, f'{rel} mentions {hit.group(0)!r} (no animation or audio library)'
        if 'vendor' not in rel.parts:
            hit = AUDIO_REFERENCES.search(text)
            assert not hit, f'{rel} references audio ({hit.group(0)!r}); cues are synthesised, never loaded'
    # first-party templates never load audio either
    for path in sorted((ROOT / 'templates').rglob('*.html')):
        text = path.read_text(encoding='utf-8', errors='ignore').lower()
        assert '<audio' not in text and 'new audio(' not in text, f'{path.relative_to(ROOT)} embeds audio'


def test_sound_js_is_oscillator_only():
    """Today's sound.js synthesises everything: no fetch, no decodeAudioData, no media element."""
    text = (JS_DIR / 'sound.js').read_text(encoding='utf-8')
    assert 'createOscillator' in text
    for banned in ('fetch(', 'decodeAudioData', 'XMLHttpRequest', 'new Audio', 'createMediaElementSource'):
        assert banned not in text, banned


# ---------------------------------------------------------------------------------------------
# Phase 1: the talking mouth
# ---------------------------------------------------------------------------------------------

TEMPLATES = ROOT / 'templates'


def _read(path):
    return Path(path).read_text(encoding='utf-8')


def test_talk_js_budget():
    size = _size(JS_DIR / 'zorp-talk.js')
    print(f'  zorp-talk.js: {size:,} of {TALK_JS_MAX_BYTES:,}')
    assert size <= TALK_JS_MAX_BYTES, f'zorp-talk.js {size} B exceeds {TALK_JS_MAX_BYTES}'
    text = _read(JS_DIR / 'zorp-talk.js')
    assert 'innerHTML' not in text and 'insertAdjacentHTML' not in text, 'nodes only (CSP discipline)'
    assert 'createElementNS' in text and 'pb.register' in text
    assert 'requestAnimationFrame' not in text and 'setInterval' not in text, 'no frame loop, no polling'


def test_talk_loaded_under_runtime_guard_after_poses():
    base = _read(TEMPLATES / 'base.html')
    guard = base.index('{% if current_user.is_authenticated or guide_preview_mode or zorp_motion_demo %}')
    block = base[guard:base.index('{% endif %}', guard)]
    assert block.index('zorp-motion.js') < block.index('zorp-poses.js') < block.index('zorp-talk.js') < block.index('zorp-triggers.js')
    assert "zorp-talk.js') }}?v=2\" defer" in block, 'new file, version 2, deferred like its neighbours'
    assert 'zorp-talk.js' not in base[:guard] and 'zorp-talk.js' not in base[base.index('{% endif %}', guard):], 'only under the guard'


def test_talk_precached():
    sw = _read(JS_DIR / 'sw.js')
    assert "'/static/js/zorp-talk.js'" in sw, 'unversioned, like the other runtime files (the offline fallback ignores ?v=)'
    assert "CACHE_VERSION = 'pb-v105'" in sw


def test_talk_mouths_not_in_presets():
    from models import zorp_rig

    assert zorp_rig.TALK_MOUTHS == ('talk-1', 'talk-2', 'side-talk-1', 'side-talk-2')
    for name, ch in zorp_rig.PRESETS.items():
        assert ch['mouth'] not in zorp_rig.TALK_MOUTHS, f'preset {name} uses a talk mouth'
    for ids in zorp_rig.CONTEXT_MAP.values():
        assert not set(ids) & set(zorp_rig.TALK_MOUTHS)
    assert set(zorp_rig.TALK_MOUTHS) <= set(zorp_rig.CHANNELS['mouth'])
    # neutral shapes: ink and rouge only, no downturn colour, no valence colours
    parts = _read(ROOT / 'templates' / 'partials' / 'zorp_parts.html')
    for vid in zorp_rig.TALK_MOUTHS:
        start = parts.index(f"n == '{vid}'")
        art = parts[start:parts.index('{%- elif', start)]
        assert '--wrong' not in art and '--correct' not in art, vid
        assert 'ink-800' in art and 'class="zf"' in art, vid


def test_talk_mouths_have_side_art():
    from models import zorp_rig

    assert zorp_rig.map_variant('side', 'mouth', 'talk-1') == 'side-talk-1'
    assert zorp_rig.map_variant('side', 'mouth', 'talk-2') == 'side-talk-2'
    assert zorp_rig.map_variant('back-glance', 'mouth', 'talk-2') == 'side-talk-2'
    assert zorp_rig.validate() is True


def test_talk_mouth_geometry():
    """3.1.1: talk-1 is 7.2 x 3.0, talk-2 is 9.0 x 4.6 (1.6 taller: at least 1.3 so 56 px reads), top edge y 43.4, centred x 32.
    The profile twins are 4.5 and 5.5 wide with the same two heights."""
    parts = _read(ROOT / 'templates' / 'partials' / 'zorp_parts.html')

    def art(vid):
        start = parts.index(f"n == '{vid}'")
        d = re.search(r'd="(M[^"]+)"', parts[start:parts.index('{%- elif', start)]).group(1)
        m = re.match(r'M([\d.]+) ([\d.]+)h([\d.]+)q0 ([\d.]+)', d)
        x, y, w, h = (float(v) for v in m.groups())
        return x, y, w, h

    t1, t2 = art('talk-1'), art('talk-2')
    assert t1[2] == 7.2 and t1[3] == 3.0 and t2[2] == 9.0 and t2[3] == 4.6
    assert t2[3] - t1[3] >= 1.3
    assert t1[1] == 43.4 and t2[1] == 43.4 and abs(t1[0] + t1[2] / 2 - 32) < 0.01 and abs(t2[0] + t2[2] / 2 - 32) < 0.01
    s1, s2 = art('side-talk-1'), art('side-talk-2')
    assert s1[2] == 4.5 and s2[2] == 5.5 and s2[3] - s1[3] >= 1.3
    assert 'zorp-rouge' in parts[parts.index("n == 'talk-2'"):parts.index("n == 'side-talk-1'")], 'the open frame has a small rouge tongue'


def test_guide_say_with_textcontent_fallback():
    guide = _read(JS_DIR / 'guide.js')
    assert 'z.say(bubbleEl, text' in guide and "typeof z.say === 'function'" in guide
    assert 'bubbleEl.textContent = text' in guide, 'without zorp-talk.js the line is plain textContent'
    assert 'innerHTML' not in guide
    assert 'TALK_MAX = { story: 1600, reward: 1600, tour: 1200 }' in guide
    assert 'hushFace' in guide and guide.count('hushFace();') >= 2, 'closeOverlay and advanceStep hush'
    # the text is the argument; talk is off at reduced and off motion
    assert 'talk: !reduced' in guide


def test_guide_reveal_uses_motion_level():
    guide = _read(JS_DIR / 'guide.js')
    assert "z.motionLevel() !== 'full'" in guide
    assert 'return prefersReducedMotion();' in guide, 'media-query fallback without the runtime'
    assert "prefers-reduced-motion" in guide
    render = guide[guide.index('function renderStep'):guide.index('function openOverlay')]
    assert 'prefersReducedMotion' not in render and 'reducedLines()' in render, 'renderStep follows the runtime motion level'


def test_consumer_wiring_and_caps():
    buddy = _read(JS_DIR / 'study-buddy.js')
    assert "z.talk({ el: faceEl, text: messageEl.textContent, max: 1200 })" in buddy
    assert buddy.count('hushFace();') == 2, 'dismiss and action both hush'
    assert buddy.index('talkMessage();') > buddy.index("root.setAttribute('data-buddy-state', 'card');"), 'after the card is unhidden'
    welcome = _read(JS_DIR / 'welcome.js')
    assert 'max: 1400' in welcome and 'setTimeout(talkCopy, 400)' in welcome and '.then(settle, settle).then(talkCopy)' in welcome
    for text in (buddy, welcome, _read(JS_DIR / 'guide.js')):
        assert 'innerHTML' not in text


def test_runtime_hooks_for_talk():
    core = _read(JS_DIR / 'zorp-motion.js')
    lively = core[core.index('function lively(inst)'):core.index('function blink(inst)')]
    assert '!inst.talking' in lively, 'no glance or look-around starts mid-sentence'
    assert core.count('inst.talk.stop()') == 3, 'setView, turnRun and stop() (a restored view) end the talk (the mouth is placed for one view)'
    stop = core[core.index('  function stop(inst)'):core.index('  function clearThought')]
    # a clip's stop() leaves a talk alone, except where it puts a cut-short excursion's view back (final audit A1)
    assert stop.count('inst.talk') == 2 and stop.count('inst.talk.stop()') == 1, 'stop() touches inst.talk only to end it before restoring inst.home'
    assert stop.index('inst.talk.stop()') < stop.index('inst.view = inst.home.view'), 'the talk ends before the view is put back'
    assert stop.index('if (inst.dirty)') < stop.index('inst.talk.stop()') < stop.index('if (inst.home)')
    css = _read(CSS_DIR / 'motion.css')
    assert '.zorp-slot--talk' in css


def test_talk_pins():
    base = _read(TEMPLATES / 'base.html')
    for needle in ("zorp-motion.js') }}?v=14", "css/motion.css') }}?v=9", "study-buddy.js') }}?v=29", "guide.js') }}?v=19", "zorp-poses.js') }}?v=6",
                   "sound.js') }}?v=4", "celebrate.js') }}?v=11"):
        assert needle.replace("css/", "") in base or needle in base, needle
    assert "welcome.js') }}?v=5" in _read(TEMPLATES / 'welcome.html')
    assert "styleguide.js') }}?v=13" in _read(TEMPLATES / 'styleguide.html')


def test_soft_switch_only_in_styleguide():
    """data-zorp-soft is a dev A/B switch: only styleguide.js sets it; zorp-poses.js reads it as `!== 'off'`."""
    setters = []
    for p in sorted(list(JS_DIR.glob('*.js')) + list((ROOT / 'templates').rglob('*.html'))):
        text = p.read_text(encoding='utf-8')
        if 'data-zorp-soft' in text and p.name not in ('zorp-poses.js',):
            setters.append(p.name)
    assert sorted(setters) == ['styleguide.html', 'styleguide.js'], setters
    poses = (JS_DIR / 'zorp-poses.js').read_text(encoding='utf-8')
    assert 'data-zorp-soft' in poses and re.search(r"data-zorp-soft'\)\s*!==\s*'off'", poses)
    assert 'setAttribute' not in poses.split('data-zorp-soft')[1][:40]


def test_belly_not_shipped():
    """D4 (pear belly) was dropped after the Phase 2 A/B sheet: no belly layer in markup, parts or scripts."""
    for p in list((ROOT / 'templates').rglob('*.html')) + list(STATIC.rglob('*.js')) + list(STATIC.rglob('*.css')):
        assert 'zorp-belly' not in p.read_text(encoding='utf-8'), p


def test_ride_wrappers_markup():
    """Antennae always ride in g.zorp-ride; the hat rides in g.zorp-hatride only when a hat is worn; findParts finds them."""
    from app import app  # noqa: E402

    html = app.test_client().get('/styleguide').data.decode()
    assert 'class="zorp-ride"' in html
    buddy = (ROOT / 'templates' / 'partials' / 'buddy.html').read_text(encoding='utf-8')
    assert '{% if look.hat %}<g class="zorp-hatride">' in buddy
    motion = (JS_DIR / 'zorp-motion.js').read_text(encoding='utf-8')
    for sel in ('.zorp-face', '.zorp-ride', '.zorp-hatride', '.zorp-slot--cheeks'):
        assert sel in motion, sel


def test_body_squash_anchored_at_feet():
    """The soft body scales .buddy-body about its own bottom (fill-box 50% 100%, y 57.5, the riders' and harness's anchor), so the
    feet stay planted (review 2026-10-04: moving the origin passed every other test)."""
    css = _read(CSS_DIR / 'motion.css')
    sel = re.compile(r'(^|[\s,])\.buddy-body[\s,{]')
    box = [r for r in re.findall(r'([^{}]+)\{([^{}]*)\}', css) if sel.search(r[0])]
    assert any('transform-box: fill-box' in decl for _, decl in box), 'fill-box on .buddy-body'
    assert [decl.strip() for s, decl in box if s.strip() == '.buddy-body'] == ['transform-origin: 50% 100%;']
    buddy = (ROOT / 'templates' / 'partials' / 'buddy.html').read_text(encoding='utf-8')
    body = buddy[buddy.index('<g class="buddy-body">'):buddy.index('</g>', buddy.index('zorp-highlight') + 40)]
    m = re.search(r'buddy-body-shape" cx="32" cy="([\d.]+)" rx="21" ry="([\d.]+)"', body)
    assert m and float(m.group(1)) + float(m.group(2)) == 57.5, 'the body bottom (the fill-box bottom) is y 57.5'
    h = re.search(r'<ellipse cx="22" cy="([\d.]+)" rx="6" ry="([\d.]+)"', body)
    assert h and float(h.group(1)) + float(h.group(2)) < 57.5, 'the highlight never extends the fill-box'


def test_styleguide_charm_section():
    from app import app  # noqa: E402

    html = app.test_client().get('/styleguide').data.decode()
    start = html.index('id="zorp-charm"')
    body = html[start:html.index('</section>', start)]
    assert 'href="#zorp-charm"' in html and 'data-charm-phase="5"' in body
    assert 'data-zorp-motion-banner' in body and 'data-zorp-preview-full' in body, 'full-motion preview switch present'
    assert body.index('data-zorp-motion-banner') < body.index('data-zorp-talk>')
    for size in (56, 72, 128):
        for view in ('front', 'side'):
            assert f'data-talk-size="{size}"' in body and f'data-talk-view="{view}"' in body
    assert body.count('data-zorp-demo') == 6
    for needle in ('data-zorp-talk-text', 'data-zorp-talk-cap', 'data-zorp-talk-plan', 'data-zorp-talk-chips', 'data-zorp-hush'):
        assert needle in body, needle
    assert 'guide-catalog.js' in html, 'the Guide lines are available for the chips'
    sg = _read(JS_DIR / 'styleguide.js')
    assert 'talkPlan' in sg and 'pbGuideCatalog' in sg and 'innerHTML' not in sg


# ---------------------------------------------------------------------------------------------
# Phase 4: sound, off by default (2026-10-06)
# ---------------------------------------------------------------------------------------------

def test_sound_js_budget():
    size = _size(JS_DIR / 'sound.js')
    print(f'  sound.js: {size:,} of {SOUND_JS_MAX_BYTES:,}')
    assert size <= SOUND_JS_MAX_BYTES, f'sound.js {size} B exceeds {SOUND_JS_MAX_BYTES}'
    text = _read(JS_DIR / 'sound.js')
    assert 'innerHTML' not in text and 'requestAnimationFrame' not in text and 'setInterval' not in text
    for banned in ('fetch(', 'decodeAudioData', 'XMLHttpRequest', 'new Audio', 'createMediaElementSource'):
        assert banned not in text, banned
    # no sound file is referenced and no context is built at the top level: the module only binds listeners on load
    assert 'ensureCtx' not in text[text.index('  bindUnlock();'):]


def test_cues_only_from_beat_start():
    """3.4.3 rule 5 by construction: pbSound.zorp( is called from the beat engine's start() (full motion only) and from the
    styleguide preview, nowhere else; every cue beat names jump, land or tada, and the sound is scheduled with rt.after
    (so stop() cancels it), only when the caller passed cue."""
    callers = []
    for path in sorted(JS_DIR.glob('*.js')):
        if path.name == 'sound.js':
            continue
        if re.search(r'pbSound\.zorp\(|\bs\.zorp\(', _read(path)):
            callers.append(path.name)
    assert callers == ['styleguide.js', 'zorp-poses.js'], callers
    poses = _read(JS_DIR / 'zorp-poses.js')
    assert poses.count('pbSound.zorp(') == 1
    start = poses[poses.index('    function start(inst, spd, opts, c)'):poses.index('    function beatClip(o)')]
    assert 'opts && opts.cue && b.cue' in start and 'rt.after(inst, at +' in start and 'window.pbSound.zorp(b.cue)' in start
    assert "b.cue === 'land' ? (b.ms || 0) / spd : 0" in start, 'a land sounds at the end of its beat'
    cues = re.findall(r"cue: '([a-z]+)'", poses)
    assert sorted(set(cues)) == ['jump', 'land', 'tada'] and cues.count('jump') == cues.count('land') == 4 and cues.count('tada') == 3, cues
    compiled = poses[poses.index('function compileBeats'):poses.index('    // A beat clip starts from the standing pose')]
    assert 'cue' not in compiled, 'compileBeats never plays or schedules a sound'
    core = _read(JS_DIR / 'zorp-motion.js')
    assert 'pbSound' not in core, 'the runtime core knows nothing of sound'


def test_styleguide_sound_preview():
    from app import app  # noqa: E402

    html = app.test_client().get('/styleguide').data.decode()
    start = html.index('id="zorp-charm"')
    body = html[start:html.index('</section>', start)]
    for cue in ('jump', 'land', 'tada', 'sequence'):
        assert f'data-zorp-cue="{cue}"' in body, cue
    assert 'data-zorp-blips' in body and 'data-zorp-sound-stop' in body and 'data-zorp-sound-out' in body
    assert 'sound.js' in html, 'loaded on every page'
    sg = _read(JS_DIR / 'styleguide.js')
    assert 'function wireSound' in sg and "wireSound(document.getElementById('zorp-charm'))" in sg
    assert '{ force: true }' in sg and 'blips: true, force: true' in sg and 's.arm()' in sg
    assert 'innerHTML' not in sg


def test_settings_page_loads_no_new_script():
    """The Zorp radio needs no script: it saves with the form like motion_preference (the sound switch keeps settings-sound.js)."""
    page = _read(TEMPLATES / 'profile_settings.html')
    assert page.count('<script') == 1 and "settings-sound.js') }}?v=1" in page
    assert 'name="zorp_sound"' in page and 'value="chatter"' not in page


# ---------------------------------------------------------------------------------------------
# Phase 5: the evaluation kit, the showreel and the docs (2026-10-06)
# ---------------------------------------------------------------------------------------------

DOCS = ROOT / 'docs'
EVAL_DOC = DOCS / 'ZORP_EVALUATION.md'
PRINT_HTML = DOCS / 'zorp_evaluation_print.html'
SHOWREEL_ORDER = ('origin', 'reward', 'reward-flat', 'bubble', 'sound-on', 'sound-off')


def test_showreel_section():
    """The six showreel buttons are in the #zorp-charm section, in the class-session order, and wired in styleguide.js."""
    from app import app  # noqa: E402

    html = app.test_client().get('/styleguide').data.decode()
    start = html.index('id="zorp-charm"')
    body = html[start:html.index('</section>', start)]
    assert 'data-charm-phase="5"' in body
    assert 'data-zorp-showreel' in body
    got = re.findall(r'data-showreel="([a-z-]+)"', body)
    assert tuple(got) == SHOWREEL_ORDER, got
    labels = re.findall(r'data-showreel="[a-z-]+">([^<]+)<', body)
    assert labels[0].startswith('1.') and labels[5].startswith('6.') and 'soft' in labels[1].lower() and 'A/B' in labels[2]
    assert 'data-showreel-line' in body and 'data-showreel-bubble' in body and 'data-showreel-status' in body
    assert body.count('data-zorp-demo') == 6, 'the six talk demos are unchanged'
    assert 'data-showreel-stage="big"' in body and 'data-showreel-stage="small"' in body, 'the reel has its own two Zorps, next to the buttons (a Zorp scrolled off screen would not talk)'
    assert body.index('data-showreel="origin"') < body.index('data-showreel-stage="big"') < body.index('data-showreel-status')
    assert body.index('data-zorp-showreel') < body.index('data-zorp-soft-toggle'), 'the reel sits before the Phase 2 controls'
    assert body.index('data-zorp-motion-banner') < body.index('data-zorp-showreel'), 'the full-motion switch comes first'
    sg = _read(JS_DIR / 'styleguide.js')
    assert 'function wireShowreel' in sg and "wireShowreel(document.getElementById('zorp-charm'))" in sg
    reel = sg[sg.index('function wireShowreel'):sg.index('// E9 Phase 4 (docs/ZORP_CHARM.md 3.4.7)')]
    assert 'innerHTML' not in reel and 'fetch(' not in reel and 'localStorage' not in reel, 'nothing stored or sent'
    assert "z.play('fist-pump'" in reel and 'max: 1600' in reel and 'max: 1200' in reel, 'real clips and caps'
    assert reel.count('force: true') == 2, 'only the two preview cues are forced'
    assert "z.motionLevel() === 'full'" in reel, 'cues only at full motion (D8)'
    assert 'data-zorp-soft-toggle' in reel and 'data-zorp-soft' in reel, 'the A/B goes through the existing toggle'
    assert reel.count('setSoft(true)') >= 2, 'the A/B restores the soft body, after step 3 and at every press'
    # the reel never sets the soft switch itself: only the toggle button does
    assert 'setAttribute' not in reel and 'removeAttribute' not in reel


EVAL_PROMPTS_RE = re.compile(r'^\d\. \*\*(.+?)\*\*\s*$', re.M)
TEST_STYLE = re.compile(r'\b(true or false|true/false|match|matching|which of these|tick the|circle|rate|rating|score|out of \d+|1 to 5|1 to 10|stars?)\b', re.I)


def test_evaluation_kit():
    text = _read(EVAL_DOC)
    for heading in ('## 1. Purpose', '## 5. The session plan', '## 6. What to show', '## 7. Pupil prompts', '## 8. Sorting the sticky notes',
                    '## 9. Results table', '## 10. Decision rules', '## 11. Privacy', '## 12. Safeguarding'):
        assert heading in text, heading
    # house style for docs prose: British spelling, no emoji, no em or en dashes
    for doc in (text, re.sub(r'<style>.*?</style>', '', _read(PRINT_HTML), flags=re.S)):
        assert '\u2014' not in doc and '\u2013' not in doc, 'no em or en dashes'
        assert not re.search('[\U0001F300-\U0001FAFF\u2600-\u27BF]', doc), 'no emoji'
        for us in ('color', 'favorite', 'behavior', 'organize', 'analyze', 'center'):
            assert not re.search(rf'\b{us}\b', doc, re.I), us
    # 4 to 6 open prompts, none test-style
    prompts = EVAL_PROMPTS_RE.findall(text[text.index('## 7. Pupil prompts'):text.index('## 8. Sorting')])
    assert 4 <= len(prompts) <= 6, prompts
    for prompt in prompts:
        assert prompt.endswith(('?', '.')) and '?' in prompt and len(prompt.split()) >= 6, prompt
        assert not TEST_STYLE.search(prompt), prompt
    sheet = _read(PRINT_HTML)
    for prompt in prompts:
        assert prompt.replace('\u2019', "'") in sheet.replace('\u2019', "'"), f'the printable sheet lacks: {prompt}'
    # the plan facts
    for needle in ('S1 and S2', 'under 13', 'projector', 'no names', 'No photos of faces', 'destroyed', 'Nothing is typed into the app',
                   'standard 13', 'D7', 'chatter'):
        assert needle.lower() in text.lower(), needle
    for knob in ('TALK_MAX', 'T_OPEN', 'SOFT', 'JELLY', 'CUE_GAIN', 'BLIP_GAIN', 'SEQ_MS', 'REACT.gap'):
        assert knob in text, knob
    # the knobs named in the doc exist in the code with the values it quotes
    assert 'var SOFT = 0.4;' in _read(JS_DIR / 'zorp-poses.js')
    assert 'var CUE_GAIN = 0.06;' in _read(JS_DIR / 'sound.js') and 'var BLIP_GAIN = 0.03;' in _read(JS_DIR / 'sound.js')
    assert 'var T_OPEN = 75, T_SHUT = 60, T_GAP = 40;' in _read(JS_DIR / 'zorp-talk.js')
    assert 'TALK_MAX = { story: 1600, reward: 1600, tour: 1200 }' in _read(JS_DIR / 'guide.js')
    # the results table is a BLANK template: no digits in any data row, and it says so
    table = text[text.index('## 9. Results table'):text.index('## 10. Decision rules')]
    assert 'BLANK' in table and 'no session has been run' in table
    rows = [r for r in table.splitlines() if r.startswith('|')]
    data = rows[2:]
    assert data, 'a few empty rows to copy'
    for row in data:
        cells = [c.strip() for c in row.strip('|').split('|')]
        assert cells[0] == '(blank)' and not any(cells[1:]), f'the template must stay blank: {row}'
    # the printable kit is one self-contained file: two A4 pages, no script, no external asset
    assert '@page { size: A4' in sheet and sheet.count('class="page') == 2
    assert '<script' not in sheet and '<link' not in sheet and '<img' not in sheet
    assert not re.search(r'(?:src|href)\s*=\s*["\']?(?:https?:)?//', sheet) and 'url(' not in sheet and '@import' not in sheet
    assert 'data-' not in sheet and 'http' not in sheet


def test_phase5_docs():
    charm = _read(DOC)
    assert 'E9 built; evaluation pending' in charm
    assert 'Phase 5 build notes (2026-10-06)' in charm and 'Phase 5 not built' not in charm
    assert 'no tuning was applied' in charm.lower() and 'results are blank' in charm
    expr = _read(DOCS / 'ZORP_EXPRESSIVENESS.md')
    sec10 = expr[expr.index('## 10. How to use Zorp'):]
    for name in ('say(', 'talk(', 'hush(', 'talkPlan', 'cue: true', 'pbSound.zorp', 'Soft body'):
        assert name in sec10, name
    handoff = _read(DOCS / 'AI_HANDOFF.md')
    rule17 = [line for line in handoff.splitlines() if line.startswith('17. ')][0]
    assert 'Talk and cues only at E9 moments' in rule17 and 'text first' in rule17 and 'sound off by default and tap-gated' in rule17
    assert 'E9 Phase 5 built 2026-10-06' in handoff and 'E9 built; evaluation pending' in handoff
    dpia = _read(DOCS / 'DPIA.md')
    row = [line for line in dpia.splitlines() if line.startswith('| 2026-10-06 | E9 Phase 5')]
    assert len(row) == 1 and 'offline and anonymous' in row[0] and 'standard 13' in row[0] and 'sound' in row[0]
    # the docs smokes: no licensed-character words in the handoff or the styleguide (test_zorp_kit_smoke.py)
    blob = (handoff + _read(TEMPLATES / 'styleguide.html')).lower()
    for word in ('mickey', 'elvis', 'disney', 'steamboat'):
        assert word not in blob, word


def main():
    test_no_animation_or_audio_libraries()
    test_sound_js_is_oscillator_only()
    test_ledger_within_caps()
    test_ledger_baseline_recorded()
    test_ledger_doc_matches_constants()
    test_talk_js_budget()
    test_talk_loaded_under_runtime_guard_after_poses()
    test_talk_precached()
    test_talk_mouths_not_in_presets()
    test_talk_mouths_have_side_art()
    test_talk_mouth_geometry()
    test_guide_say_with_textcontent_fallback()
    test_guide_reveal_uses_motion_level()
    test_consumer_wiring_and_caps()
    test_runtime_hooks_for_talk()
    test_talk_pins()
    test_styleguide_charm_section()
    test_soft_switch_only_in_styleguide()
    test_belly_not_shipped()
    test_ride_wrappers_markup()
    test_body_squash_anchored_at_feet()
    test_sound_js_budget()
    test_cues_only_from_beat_start()
    test_styleguide_sound_preview()
    test_settings_page_loads_no_new_script()
    test_showreel_section()
    test_evaluation_kit()
    test_phase5_docs()
    print('Zorp charm smoke (E9 Phases 1, 2, 4 and 5) passed.')


if __name__ == '__main__':
    main()
