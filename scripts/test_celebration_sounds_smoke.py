"""Celebration sounds smoke (docs/CELEBRATION_SOUNDS_PLAN.md).
Run: python scripts/test_celebration_sounds_smoke.py

Checks: the library and pbSound.play in Node (scripts/celebration_sound_harness.js: every sound, gains and lengths, the gates, the
400 ms gap and chained layers, force, stopAll, the tap carried across a page, the late guard, a failed load); the library is made in
code and loaded only by sound.js; every sound a celebration asks for exists, timed by tier and family; reduced motion asks for one
soft sound; the stage's speaker button and quiet on close; the setting saves both ways and new accounts start on; the gallery
auditions every sound.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

JS = ROOT / 'static' / 'js'
LIB = JS / 'sound-library.js'
LIB_MAX_BYTES = 7_500   # 2026-11-13 (new): 15 sounds and the noise, filter and chord helpers (6,924 B); loads only when a sound may play
HARNESS = ROOT / 'scripts' / 'celebration_sound_harness.js'
HDR = {'Accept': 'application/json'}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def library_names():
    src = LIB.read_text(encoding='utf-8')
    block = src[src.index('var SOUNDS = {'):src.index('\n  };', src.index('var SOUNDS = {'))]
    return set(re.findall(r"^    '?([a-z][a-z-]*)'?: \{", block, re.M))


def test_harness():
    node = shutil.which('node')
    if not node:
        print('node not found on PATH -- skipping the celebration sound harness.')
        return
    r = subprocess.run([node, str(HARNESS), str(JS / 'sound.js'), str(LIB)], cwd=str(ROOT), capture_output=True, text=True, check=False)
    print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)
    assert r.returncode == 0, 'celebration sound harness FAILED'


def test_made_in_code_and_loaded_on_demand():
    src = LIB.read_text(encoding='utf-8')
    assert LIB.stat().st_size <= LIB_MAX_BYTES, f'sound-library.js {LIB.stat().st_size:,} B > {LIB_MAX_BYTES:,}'
    assert 'createOscillator' in src and 'createBufferSource' in src and 'createBiquadFilter' in src
    for banned in ('fetch(', 'decodeAudioData', 'XMLHttpRequest', 'new Audio', 'createMediaElementSource', '.mp3', '.ogg', '.wav'):
        assert banned not in src, banned
    assert len(library_names()) == 15, sorted(library_names())
    base = read('templates/base.html')
    assert "data-pb-sound-lib=\"{{ url_for('static', filename='js/sound-library.js') }}?v=1\"" in base
    for path in sorted((ROOT / 'templates').rglob('*.html')):
        n = path.read_text(encoding='utf-8').count('js/sound-library.js')
        assert n == (1 if path.name == 'base.html' else 0), f'{path.name}: the library loads only through sound.js'
    sound = read('static/js/sound.js')
    assert "getAttribute('data-pb-sound-lib')" in sound and 'play: play' in sound and 'prepare:' in sound
    assert "if (zorpMode() === 'celebrations') library();" in sound, 'prepare loads nothing while the setting is off'
    csp = re.findall(r"media-src[^;\"']*", read('app.py'))
    assert not csp, f'no media-src change: {csp}'


def calls(text):
    return set(re.findall(r"\bsnd\('([a-z-]+)'", text)) | set(re.findall(r"(?:pbSound|snd)\.play\('([a-z-]+)'", text))


def test_every_sound_asked_for_exists():
    names = library_names()
    stage = read('static/js/badge-stage.js')
    moments = read('static/js/moments.js')
    story = read('static/js/story-chapters.js')
    zstage = read('static/js/zorp-stage.js')
    asked = calls(stage) | calls(moments) | calls(story) | calls(zstage)
    asked |= set(re.findall(r"'([a-z]+)'", stage[stage.index('var TOUCH = {'):stage.index('};', stage.index('var TOUCH = {'))]))
    m = moments[moments.index('function chime(m)'):moments.index('function enter(m, set)')]
    asked |= set(re.findall(r"(?:level|perfect|week): '([a-z]+)'", m)) | {'book'}
    asked -= {'perfect', 'growth'}   # TOUCH keys
    assert asked and asked <= names, sorted(asked - names)
    from models import gamification as gam
    tiers = {v.get('tier') for v in gam.MILESTONE_CATALOG.values()} | {'violet'}
    assert {'stamp-' + t for t in tiers} <= names, tiers
    # the badge stage: whoosh (a streak's swell), the stamp as the medal lands (chained), the family touch; reduced motion one soft stamp
    snd = stage[stage.index('function sound(item)'):stage.index('function enter(item, fam, set)')]
    for needle in ("if (!full()) { snd(stamp, { soft: true }); return; }", "snd(f === 'streak' || f === 'streak100' ? 'fire' : 'whoosh');",
                   "later(function () { snd(stamp, { chain: true }); }, STAMP);", "f === 'streak100' ? 'violet'",
                   "later(function () { snd(TOUCH[f], { chain: true }); }, STAMP + 600);"):
        assert needle in snd, needle
    assert "var TOUCH = { perfect: 'sparkle', growth: 'sprout' };" in stage
    assert 'sound(item);\n    if (!full())' in stage, 'asked before the reduced-motion return'
    # the moments: timed with the picture; reduced motion the main sound, soft
    for needle in ("if (!full()) { o.soft = true; snd(main, o); return; }", "later(function () { snd('confetti', { chain: true }); }, 1060);",
                   "{ perfect: 780, level: 900, week: 300 }[m.type] || (m.more ? 715 : 1300)", "step: { days: 0, right: 1, best: 2 }[m.part] || 0"):
        assert needle in m, needle
    assert '    chime(m);\n  }' in moments
    toast = moments[moments.index('  function toast(m) {'):]
    assert "snd('pop', null, 1);" in toast[:toast.index('\n  }\n')], 'the corner card pop'
    # a stage that starts to close (finish() drops body.pb-stage-open before its fade) never sounds a timer still due
    assert "if (s && s.play && D.body.classList.contains('pb-stage-open')) s.play(name, o);" in stage
    assert "if (s && s.play && (card || D.body.classList.contains('pb-stage-open'))) s.play(name, o);" in moments
    fin = read('static/js/zorp-stage.js')
    fin = fin[fin.index('  function finish(how) {'):]
    assert fin.index("D.body.classList.remove('pb-stage-open')") < fin.index('var done = function')
    assert "window.pbSound.play('story', { soft: !full() })" in story and 'if (!i &&' in story, 'the chapter opens with its phrase'
    # the timers die with the scene (later), so a skipped card never sounds afterwards
    assert 'setTimeout' not in snd and 'setTimeout' not in m


def test_stage_button_and_quiet_on_close():
    js = read('static/js/zorp-stage.js')
    css = read('static/css/stage.css')
    fin = js[js.index('  function finish(how) {'):js.index('  function next() {')]
    assert 'window.pbSound.stopAll()' in fin, 'Continue at the end, Skip, Skip all and Esc all end in finish()'
    btn = js[js.index('  function muteBtn(st, ns) {'):js.index('  function build() {')]
    for needle in ("if (!(sndOn() || muted) || !snd || !snd.play || !ns) return;", "b.setAttribute('aria-label', 'Celebration sounds');",
                   "b.setAttribute('aria-pressed', yes ? 'true' : 'false');", "if (muted) snd.stopAll(); else snd.play('pop', { chain: true });",
                   "D.documentElement.setAttribute('data-zorp-sound', mode);", "getAttribute('data-guide-preview') === '1'",
                   "fetch('/api/v1/me/settings', { method: 'PATCH'", "JSON.stringify({ zorp_sound: mode })", "'X-CSRF-Token'"):
        assert needle in btn, needle
    assert 'innerHTML' not in btn and "createElementNS(ns, 'svg')" in btn and 'http' not in btn
    assert '    muteBtn(st, (r.zorp && r.zorp.namespaceURI) || (props && props.documentElement && props.documentElement.namespaceURI));\n    return r;' in js
    assert "if (window.pbSound && window.pbSound.prepare) window.pbSound.prepare();" in js
    rule = css[css.index('.pb-st-mute {'):]
    assert 'width: 44px; height: 44px;' in rule[:400] and '.pb-st-mute:focus-visible' in css


def _register(c, tag):
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'cs{tag}_{s}@example.com', 'handle': f'cs{tag}_{s}', 'password': 'password123',
                                              'age_confirm': True}, headers=HDR)
    assert r.status_code in (200, 201), r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:   # signed in, as the gallery smoke does
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
        sess['pb_own'] = uid
    return uid


def test_setting_saves_both_ways_and_new_accounts_start_on():
    from app import app
    c = app.test_client()
    _register(c, 'a')
    html = c.get('/topics').get_data(as_text=True)
    assert 'data-zorp-sound="celebrations"' in html, 'new accounts start on (E10, decision 6)'
    assert 'data-pb-sound-lib="' in html
    for mode in ('off', 'celebrations', 'off'):
        r = c.patch('/api/v1/me/settings', data=json.dumps({'zorp_sound': mode}), content_type='application/json', headers=HDR)
        assert r.status_code == 200, r.data
        assert f'data-zorp-sound="{mode}"' in c.get('/topics').get_data(as_text=True)
    r = c.patch('/api/v1/me/settings', data=json.dumps({'zorp_sound': 'loud'}), content_type='application/json', headers=HDR)
    assert r.status_code == 400


def test_gallery_auditions_every_sound():
    js = read('static/js/celebrations-gallery.js')
    tpl = read('templates/celebrations_gallery.html')
    listed = set(re.findall(r"\['([a-z-]+)', '", js[js.index('var SOUNDS = ['):js.index('];', js.index('var SOUNDS = ['))]))
    assert listed == library_names(), sorted(listed ^ library_names())
    for needle in ('data-gal-with-sound', 'data-gal-soft', 'id="gallery-sounds-list"', "celebrations-gallery.js') }}?v=2"):
        assert needle in tpl, needle
    for needle in ("s.play(name, Object.assign({ force: true }, o))", "window.pbSound.arm()", "html.setAttribute('data-zorp-sound', withSound.checked ? 'celebrations' : 'off');"):
        assert needle in js, needle


def test_docs():
    plan = read('docs/CELEBRATION_SOUNDS_PLAN.md')
    assert '## 7. Built' in plan and '6.1' in plan
    assert 'Off by default' not in plan, 'new accounts start on (decision 6)'
    assert 'celebration sounds' in read('docs/ZORP_CHARM.md').lower()


def main():
    for t in (test_harness, test_made_in_code_and_loaded_on_demand, test_every_sound_asked_for_exists, test_stage_button_and_quiet_on_close,
              test_setting_saves_both_ways_and_new_accounts_start_on, test_gallery_auditions_every_sound, test_docs):
        t()
        print('ok', t.__name__)
    print('Celebration sounds smoke passed.')


if __name__ == '__main__':
    main()
