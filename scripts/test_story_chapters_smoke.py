"""E10 phase 8: Zorp's story chapters (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md A6, section 11.13).
Run: python scripts/test_story_chapters_smoke.py

* Files and caps: the lazy story files have their own byte caps; no library, no markup strings; transform and opacity only; the story
  props are an inert template.
* The catalogue (static/js/story-chapters.js): six chapters of two to four scenes, titles equal to models/story.py, every beat names a
  real clip, view, prop and CSS state; the voice lint on every line; every face positive or neutral; the one wistful lore scene (Home)
  carries a positive resolve and the chapter ends positive; every chapter ends positive.
* Unlock rules, computed on the server: the counts 3, 5, 8, 10, 15 and 20, or a topic master badge (chapter 3) or a subject complete
  badge (chapter 6), whichever comes first.
* Delivery: a badge that crosses a threshold carries one offer toast (the first chapter it opened) in the JSON answer, the page island
  or the session; nothing else crosses nothing; the offer never plays by itself (Watch plays, Later and the dismiss do not).
* Existing pupils: one catch-up offer on a normal page, never all at once, never twice, never during the arrival or the tour.
* State: watched and offered flags live in the protected tours region of the guide state and survive a flood of other flags.
* The shelf on the profile: Chapter 0 first, unlocked chapters with Watch or Watch again, locked ones with "Unlocks at N badges".
* Lazy loading: ordinary pages carry only the asset island; the profile links the shelf's style and script only.
The browser walk (Playwright, light, dark, a phone, reduced motion) is in the plan's Progress section.
"""
import json
import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ['PB_TESTING'] = '1'

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

from flask import jsonify, request  # noqa: E402
from flask_login import current_user, login_required  # noqa: E402

import app as appmod  # noqa: E402
from app import app, get_db  # noqa: E402
from models import social, zorp_rig, zorp_voice as voice  # noqa: E402
from models import story  # noqa: E402
from test_zorp_stage_smoke import js_literal, runtime_clips  # noqa: E402

JS = ROOT / 'static' / 'js'
CSS = ROOT / 'static' / 'css'
CHAPTERS_JS = JS / 'story-chapters.js'
SHELF_JS = JS / 'story-shelf.js'
STORY_CSS = CSS / 'story.css'
PROPS_SVG = ROOT / 'static' / 'images' / 'story-props.svg'

# Own caps for the lazy files (bytes), set 2026-11-08 in E10 phase 8.
CAPS = {CHAPTERS_JS: 20_500, SHELF_JS: 1_800, STORY_CSS: 4_800, PROPS_SVG: 6_200}
PROPS = {'planet', 'ship', 'logbook', 'card', 'rock', 'door', 'toaster', 'postcard'}
NEW_PROPS = {'rock', 'door', 'toaster', 'postcard'}
LAYOUTS = {'centre', 'left'}
BEAT_KEYS = {'prop', 'zorp', 'play', 'turn', 'face', 'crew', 'burst', 'talk', 'wait'}
BEAT_EXTRA = {'set', 'async', 'target', 'facing'}
H = {'Accept': 'application/json'}


def _read(path):
    return Path(path).read_text(encoding='utf-8')


def chapters():
    """The CHAPTERS array of story-chapters.js as Python data."""
    src = _read(CHAPTERS_JS)
    start = src.index('var CHAPTERS = ') + len('var CHAPTERS = ')
    depth, k = 0, start
    while k < len(src):
        ch = src[k]
        if ch == "'":
            k += 1
            while src[k] != "'":
                k += 2 if src[k] == '\\' else 1
        elif src.startswith('//', k):
            k = src.index('\n', k)
            continue
        elif ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                return js_literal(src[start:k + 1])
        k += 1
    raise AssertionError('CHAPTERS literal not closed')


def scenes():
    return [(c, s) for c in chapters() for s in c['scenes']]


# ---- test-only route: earn badges the way the study-day path does, then note them for delivery ----
@app.post('/_t/earn')
@login_required
def _t_earn():
    keys = request.get_json()['keys']
    with get_db() as conn:
        for key in keys:
            conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, datetime('now'))",
                         (current_user.id, key))
        conn.commit()
    appmod._note_new_milestones(current_user.id, keys)
    return jsonify({'ok': True})


@app.post('/_t/earn-redirect')
@login_required
def _t_earn_redirect():
    from flask import redirect
    keys = request.get_json()['keys']
    with get_db() as conn:
        for key in keys:
            conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, datetime('now'))",
                         (current_user.id, key))
        conn.commit()
    appmod._note_new_milestones(current_user.id, keys)
    return redirect('/')


def make_client(prefix='sc'):
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'{prefix}_{s}@example.com', 'handle': f'{prefix}_{s}',
                                              'password': 'password123', 'age_confirm': True}, headers=H)
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def give(uid, n, prefix='b'):
    """n badges, quietly (rows only, nothing noted for delivery)."""
    with get_db() as conn:
        for i in range(n):
            conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, ?, datetime('now'))",
                         (uid, f'{prefix}_{i}'))
        conn.commit()


def patch_guide(c, guide):
    r = c.patch('/api/v1/me/settings', json={'guide': guide}, headers=H)
    assert r.status_code == 200, r.data[:200]
    return r


def stored(uid):
    with get_db() as conn:
        raw = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()['guide_json']
    return json.loads(raw)


def done_arrival(c):
    patch_guide(c, {'v': 1, 'origin': True, 'tours': {'app': True, 'coach': True}, 'rewards': {}})


def island(html, name):
    m = re.search(r'id="%s">(.*?)</script>' % name, html, re.S)
    return json.loads(m.group(1)) if m else []


def offers(moments):
    return [m for m in moments if m.get('kind') == 'story_offer']


# ---------------------------------------------------------------------------------------------
# Files, caps, hygiene
# ---------------------------------------------------------------------------------------------

def test_files_and_caps():
    for path, cap in CAPS.items():
        size = path.stat().st_size
        print(f'  {path.relative_to(ROOT)}: {size:,} of {cap:,} (headroom {cap - size:,})')
        assert size <= cap, f'{path.name} {size} B exceeds its cap {cap}'
    assert (JS / 'zorp-stage.js').stat().st_size <= 24_000, 'the engine keeps its cap (phase 8 adds only the four prop names and addProps)'
    for path in (CHAPTERS_JS, SHELF_JS):
        text = _read(path)
        for banned in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval(', 'new Function', 'setInterval',
                       'requestAnimationFrame', 'localStorage', 'http://', 'https://', 'onclick'):
            assert banned not in text, f'{path.name} uses {banned}'
    for path in (CHAPTERS_JS, SHELF_JS, STORY_CSS, PROPS_SVG):
        low = _read(path).lower()
        for lib in ('lottie', 'gsap', 'rive', 'anime.js', 'cdn', 'jsdelivr', 'unpkg'):
            assert not re.search(r'(?<![\w-])' + re.escape(lib) + r'(?![\w-])', low), f'{path.name} mentions {lib}'


def test_css_animates_transform_and_opacity_only():
    css = _read(STORY_CSS)
    for m in re.finditer(r'@keyframes\s+([\w-]+)\s*\{(.*?)\}\s*\}', css, re.S):
        props = set(re.findall(r'([a-z-]+)\s*:', m.group(2)))
        assert props <= {'transform', 'opacity'}, f'@keyframes {m.group(1)} animates {props}'
    for m in re.finditer(r'transition\s*:\s*([^;]+);', css):
        for part in re.split(r',(?![^()]*\))', m.group(1)):
            assert part.split()[0] in ('transform', 'opacity'), f'transition on {part.strip()!r}'
    assert 'transition-property' not in css


def test_props_template_is_inert():
    root = ET.parse(PROPS_SVG).getroot()
    ns = '{http://www.w3.org/2000/svg}'
    ids = {}
    for el in root.iter():
        tag = el.tag.replace(ns, '')
        assert tag not in ('script', 'foreignObject', 'a', 'image', 'use', 'iframe', 'style'), f'story props have <{tag}>'
        for attr, value in el.attrib.items():
            name = attr.split('}')[-1]
            assert not name.lower().startswith('on') and name != 'href' and 'javascript' not in value.lower(), (tag, attr)
        if 'id' in el.attrib:
            ids[el.attrib['id']] = el
    for need in NEW_PROPS:
        assert f'st-{need}' in ids and ids[f'st-{need}'].tag == ns + 'svg', need
    text = _read(PROPS_SVG)
    assert 'var(--' not in text, 'prop colours are literal: the stage is night sky in both themes'
    css = _read(STORY_CSS)
    for cls in set(re.findall(r'\.(sty-[\w-]+)', css)):
        if cls in ('sty-bump',):
            continue
        in_props = f'"{cls}"' in text or f' {cls}"' in text or f'"{cls} ' in text
        in_js = cls in _read(CHAPTERS_JS) or cls in _read(ROOT / 'templates' / 'partials' / 'story_shelf.html')
        assert in_props or in_js, f'story.css styles .{cls} that nothing has'
    stage_js = _read(JS / 'zorp-stage.js')
    for need in NEW_PROPS:
        assert f"{need}: ['st-{need}']" in stage_js, f'the engine does not know the {need} prop'
    assert 'addProps' in stage_js


# ---------------------------------------------------------------------------------------------
# The catalogue
# ---------------------------------------------------------------------------------------------

def test_catalogue_shape_and_beats():
    data = chapters()
    assert [c['n'] for c in data] == [1, 2, 3, 4, 5, 6]
    assert [c['title'] for c in data] == [c['title'] for c in story.CHAPTERS], 'titles equal models/story.py'
    clips = runtime_clips()
    states = set(re.findall(r'\[data-set~=(\w+)\]', _read(STORY_CSS))) | set(re.findall(r'\[data-set~=(\w+)\]', _read(CSS / 'stage.css')))
    ids = set()
    for ch in data:
        assert 2 <= len(ch['scenes']) <= 4, ch['n']
        for i, sc in enumerate(ch['scenes']):
            sid = sc['id']
            assert sid not in ids and sid.startswith('story.'), sid
            ids.add(sid)
            assert sc['heading'] == f"Chapter {ch['n']}: {ch['title']}", sid
            assert sc['layout'] in LAYOUTS and set(sc['props']) <= PROPS, sid
            lines = sc['lines']
            assert 1 <= len(lines) <= 2 and len(sc['beats']) == len(lines), f'{sid}: one beat list per line'
            assert all(len(t) <= 100 for t in lines), sid
            assert sc['skipLabel'] == 'Skip story' and sc['primary'] == 'Next', sid
            last = i == len(ch['scenes']) - 1
            assert (sc.get('story') == {'primary': 'Done'}) is last, f'{sid}: only the last scene says Done'
            for beats in sc['beats']:
                for b in beats:
                    acts = set(b) & BEAT_KEYS
                    assert len(acts) == 1 and set(b) <= BEAT_KEYS | BEAT_EXTRA, (sid, b)
                    if 'play' in b or 'crew' in b:
                        assert b.get('play', b.get('crew')) in clips, (sid, b)
                    if 'turn' in b:
                        assert b['turn'] in zorp_rig.VIEW_NAMES, (sid, b)
                    if 'prop' in b:
                        assert b['prop'] in PROPS, (sid, b)
                        if 'set' in b:
                            assert b['set'] in states, f'{sid}: no CSS for data-set state {b["set"]!r}'
                    if 'wait' in b:
                        assert 0 < b['wait'] <= 1200, (sid, b)
            # a prop a beat brings in is listed for the scene
            for beats in sc['beats']:
                for b in beats:
                    if 'prop' in b:
                        assert b['prop'] in sc['props'], f'{sid}: beat uses {b["prop"]} that the scene does not list'
    # each chapter is short: no more than about 40 s of reading (2 s plus 0.28 s a word at a calm pace) and about 20 s at the least
    for ch in data:
        secs = sum(2 + 0.28 * len(t.split()) for sc in ch['scenes'] for t in sc['lines'])
        assert 12 <= secs <= 45, (ch['n'], round(secs))
    # the chosen props: the maths belt, the crew on the ship, a door and the toaster, Home under Novara, the logbook, the postcard
    used = {c['n']: {p for sc in c['scenes'] for p in sc['props']} for c in data}
    assert {'planet', 'rock'} <= used[1] and 'ship' in used[2] and {'door', 'toaster'} <= used[3] and 'planet' in used[4]
    assert 'logbook' in used[5] and {'ship', 'postcard'} <= used[6]
    flat2 = [b for sc in data[1]['scenes'] for beats in sc['beats'] for b in beats]
    assert any(b.get('set') == 'bump' for b in flat2), 'chapter 2: the parking'
    flat1 = [b for sc in data[0]['scenes'] for beats in sc['beats'] for b in beats]
    assert any(b.get('set') == 'tumble' for b in flat1), 'chapter 1: a rock tumbles'
    flat3 = [b for sc in data[2]['scenes'] for beats in sc['beats'] for b in beats]
    assert any(b.get('set') == 'open' for b in flat3) and any(b.get('set') == 'pop' for b in flat3)
    # the content of the plan, in the words: the names and the postcard hint at more stories
    text = {c['n']: ' '.join(t for sc in c['scenes'] for t in sc['lines']) for c in data}
    for name in ('Pim', 'Juno', 'Tock'):
        assert name in text[2], name
    assert 'parks like' in text[2] and 'toaster' in text[3] and 'logbook' in text[5].lower()
    assert 'More stories may come' in text[6]
    # the engine has the sprites the chapters name and an opt-out for nothing: nothing advances by itself
    src = _read(CHAPTERS_JS)
    assert 'setTimeout(onNext' not in src and 'autoplay' not in src.lower()


def test_every_face_is_positive_or_neutral_and_chapters_end_positive():
    allowed = zorp_rig.CONTEXT_MAP['stage']
    assert all(zorp_rig.VALENCE[f] != 'negative' for f in allowed)
    data = chapters()
    for ch, sc in scenes():
        for key in ('face', 'end'):
            assert sc[key] in allowed and zorp_rig.VALENCE[sc[key]] in ('positive', 'neutral'), (sc['id'], key, sc[key])
        for beats in sc['beats']:
            for b in beats:
                if 'face' in b:
                    assert b['face'] in allowed, (sc['id'], b)
    # every chapter ends positive (not merely neutral)
    for ch in data:
        end = ch['scenes'][-1]['end']
        assert zorp_rig.VALENCE[end] == 'positive', (ch['n'], end)
    # no negative preset is named anywhere in the file
    negative = {n for n, v in zorp_rig.VALENCE.items() if v == 'negative'}
    src = _read(CHAPTERS_JS)
    for name in negative:
        assert f"'{name}'" not in src, f'story-chapters.js names negative preset {name}'
    # the lore: exactly one wistful scene (Home, first scene), with a positive resolve that the chapter really ends on
    lore = [(c['n'], s) for c, s in scenes() if s.get('lore')]
    assert [(n, s['id']) for n, s in lore] == [(4, 'story.home.look')], lore
    sc = lore[0][1]
    assert zorp_rig.VALENCE[sc['resolve']] == 'positive' and sc['resolve'] == data[3]['scenes'][-1]['end']
    assert data[3]['scenes'][0]['id'] == 'story.home.look' and len(data[3]['scenes']) >= 2, 'it resolves inside the chapter'
    assert sc['face'] == 'aww' and zorp_rig.VALENCE[sc['face']] == 'positive'
    # only the home chapter opens wistful: no other chapter starts below neutral or says anything sad
    assert all(not s.get('lore') for c, s in scenes() if c['n'] != 4)
    home = ' '.join(t for s in data[3]['scenes'] for t in s['lines']).lower()
    # Zorp's own feelings only: never tied to the pupil, no missing, no needing, no absence
    for word in (' you ', 'your', ' miss', 'need', 'lonely', 'alone', 'sad', 'cry', 'away from', 'come back', 'left me', 'waiting for'):
        assert word not in f' {home} ', f'Home must not say {word!r}'
    assert 'learn' in home and ('cheer' in data[3]['scenes'][-1]['beats'][-1][-1].get('play', ''))


def test_voice_rules_on_every_line():
    items, errors = voice.extract_story_copy()
    assert not errors, errors
    lines = [i for i in items if i.kind == 'line' and i.path == 'static/js/story-chapters.js' and i.surface == 'guide_line']
    expected = [t for c, s in scenes() for t in s['lines']]
    assert [i.text for i in lines] == expected, 'the extractor reads every scene line'
    assert 30 <= len(expected) <= 40
    found = [v for v in voice.lint(items) if v.level in ('error', 'warn') and v.item.path != '(inventory)']
    assert not found, '\n'.join(f'{v.item.ref} {v.rule}: {v.detail} | {v.item.text}' for v in found)
    for it in items:
        if it.voice == 'zorp' and it.surface == 'guide_line':
            assert len(it.text) <= 100 and it.text.count('!') <= 1, it.text
            assert not re.search(r'[–—]|\s-\s', it.text), it.text
        if it.surface == 'button_label':
            assert len(it.text) <= 22, it.text
        if it.dismiss:
            assert it.text in voice.DISMISS_APPROVED, it.text
    # at most one "!" in a whole chapter; British spelling and the bot rule are the lint's
    for ch in chapters():
        assert sum(t.count('!') for s in ch['scenes'] for t in s['lines']) <= 1, ch['n']
    low = ' '.join(expected).lower()
    for phrase in ('i missed you', 'i need you', 'miss you', 'come back', 'hurry', 'last chance', "don't miss", 'you forgot', 'streak',
                   'xp', 'level', 'badge', 'score', 'quiz'):
        assert phrase not in low, f'a chapter must not say {phrase!r}'
    copy = {i.where: i for i in items if i.path == 'static/js/story-chapters.js' and i.where in ('offer', 'watch', 'later')}
    assert copy['offer'].text == 'Zorp has a new story for you'
    assert copy['watch'].text == 'Watch' and copy['later'].text == 'Later' and copy['later'].dismiss
    # the shelf's own labels are linted through the template marks
    assert voice.marked_templates().count('templates/partials/story_shelf.html') == 1


# ---------------------------------------------------------------------------------------------
# The unlock rules (the server's)
# ---------------------------------------------------------------------------------------------

def test_unlock_rules_are_the_servers():
    def opened(n, extra=()):
        return story.unlocked_numbers([f'b_{i}' for i in range(n)] + list(extra))

    assert [c['badges'] for c in story.CHAPTERS] == [3, 6, 10, 15, 22, 30]   # 2026-11-10 E11 Phase 2 (was 3, 5, 8, 10, 15, 20)
    assert opened(0) == [] and opened(2) == [] and opened(3) == [1] and opened(5) == [1] and opened(6) == [1, 2]
    assert opened(9) == [1, 2] and opened(10) == [1, 2, 3] and opened(15) == [1, 2, 3, 4] and opened(21) == [1, 2, 3, 4]
    assert opened(22) == [1, 2, 3, 4, 5] and opened(29) == [1, 2, 3, 4, 5] and opened(30) == [1, 2, 3, 4, 5, 6]
    # a first topic master badge opens chapter 3 early; a subject complete badge opens chapter 6 early; other badges do not
    assert story.unlocked_numbers(['topic_master:gcse:maths:bidmas']) == [3]
    assert story.unlocked_numbers(['subject_completed:gcse:maths']) == [6]
    assert story.unlocked_numbers(['subject_ninja:gcse:maths', 'topics_master_5']) == []
    # crossing: the badges that open something, and only what they open
    base = ['a', 'b']
    assert story.newly_unlocked(base + ['c'], ['c']) == [1]
    assert story.newly_unlocked(base + ['c', 'd'], ['c', 'd']) == [1]
    assert story.newly_unlocked([f'b{i}' for i in range(5)], ['b4']) == [], 'no threshold crossed'
    assert story.newly_unlocked([f'b{i}' for i in range(6)], ['b5']) == [2]
    assert story.newly_unlocked([f'b{i}' for i in range(6)] + ['topic_master:gcse:maths:bidmas'], ['topic_master:gcse:maths:bidmas']) == [3]
    assert story.newly_unlocked([f'b{i}' for i in range(10)] + ['topic_master:x:y:z'], ['topic_master:x:y:z']) == [], 'chapter 3 was open by the count'
    assert story.newly_unlocked([f'b{i}' for i in range(4)] + ['topic_master:x:y:z'], ['topic_master:x:y:z']) == [3]
    assert story.newly_unlocked([f'b{i}' for i in range(1)] + ['subject_completed:gcse:maths'], ['subject_completed:gcse:maths']) == [6]
    # the shelf rows
    rows = story.shelf([f'b{i}' for i in range(6)], {'tours': {'story_w1': True}})
    assert [r['n'] for r in rows] == [0, 1, 2, 3, 4, 5, 6]
    assert rows[0]['title'] == 'Arrival' and rows[0]['unlocked']
    assert [r['unlocked'] for r in rows] == [True, True, True, False, False, False, False]
    assert rows[1]['watched'] and not rows[2]['watched']
    assert rows[3]['unlock'] == 'Unlocks at 10 badges' and rows[3]['alt'] == 'Or earn a topic master badge.'
    assert rows[6]['unlock'] == 'Unlocks at 30 badges' and rows[6]['alt'] == 'Or earn a subject complete badge.'
    assert rows[4]['alt'] == '' and rows[4]['unlock'] == 'Unlocks at 15 badges'
    # no database row, no table: the unlock is derived (nothing new stored)
    src = _read(ROOT / 'models' / 'story.py')
    assert 'INSERT' not in src.upper().replace('INSERT_', '') and 'CREATE TABLE' not in src.upper()


# ---------------------------------------------------------------------------------------------
# Delivery: the offer toast
# ---------------------------------------------------------------------------------------------

def test_a_badge_that_crosses_a_threshold_carries_one_offer():
    c, uid = make_client('dl')
    give(uid, 2)
    r = c.post('/_t/earn', json={'keys': ['x_3']}, headers=H).get_json()
    got = offers(r.get('new_moments') or [])
    assert len(got) == 1, r
    assert got[0] == {'type': 'toast', 'kind': 'story_offer', 'id': 'story:1', 'chapter': 1}, got[0]
    assert [m['key'] for m in r['new_milestones']] == ['x_3'], 'the badge itself still arrives with it (the badge stage plays first)'
    # a fourth and a fifth badge cross nothing (2026-11-10 E11 Phase 2: chapter 2 now opens at six)
    for k in ('x_4', 'x_5'):
        r = c.post('/_t/earn', json={'keys': [k]}, headers=H).get_json()
        assert offers(r.get('new_moments') or []) == [], k
    # the sixth opens chapter 2 only
    r = c.post('/_t/earn', json={'keys': ['x_6']}, headers=H).get_json()
    assert [m['chapter'] for m in offers(r.get('new_moments') or [])] == [2]
    # two chapters opened by one request: only the first of them is offered (never all at once)
    c2, uid2 = make_client('dl')
    give(uid2, 2)
    r = c2.post('/_t/earn', json={'keys': [f'y_{i}' for i in range(5)]}, headers=H).get_json()
    assert [m['chapter'] for m in offers(r.get('new_moments') or [])] == [1], r
    # a topic master badge opens chapter 3 on its own, with one other badge
    c3, uid3 = make_client('dl')
    give(uid3, 1)
    r = c3.post('/_t/earn', json={'keys': ['topic_master:gcse:maths:bidmas']}, headers=H).get_json()
    assert [m['chapter'] for m in offers(r.get('new_moments') or [])] == [3], r
    # a pupil who is not signed in as the earner is never given one
    assert story.offer_moment(3) == {'type': 'toast', 'kind': 'story_offer', 'id': 'story:3', 'chapter': 3}


def test_the_offer_rides_the_page_island_and_the_session():
    c, uid = make_client('pg')
    give(uid, 2)
    # a request that redirects keeps the moment for the next page; it is shown once
    r = c.post('/_t/earn-redirect', json={'keys': ['p_3']})
    assert r.status_code == 302
    with c.session_transaction() as sess:
        assert [m['chapter'] for m in offers(sess.get('pb_mm') or [])] == [1], dict(sess)
    html = c.get('/profile').get_data(as_text=True)
    first = island(html, 'pb-new-moments')
    assert [m['chapter'] for m in offers(first)] == [1], first
    assert offers(island(c.get('/profile').get_data(as_text=True), 'pb-new-moments')) == [], 'emitted once'


def test_the_offer_never_plays_by_itself():
    src = _read(CHAPTERS_JS)
    body = src[src.index('function offer(m)'):src.index('window.pbStory = ')]
    assert body.count('play(n)') == 1 and "watch.addEventListener('click', function () { dismiss(t); play(n); })" in body, 'only Watch plays'
    assert "later.addEventListener('click', function () { dismiss(t); })" in body and "x.addEventListener('click'" in body
    assert 'TOAST_MS' in body and "role', 'status'" in body, 'a polite status toast that goes away by itself'
    assert 'focus(' not in body, 'the toast never takes focus'
    guide = _read(JS / 'guide.js')
    run = guide[guide.index('function runMoments()'):guide.index('function moments(list)')]
    # offers wait where every moment waits: not while a dialog, a stage or the badge stage is up; shown after the other moments
    # 2026-11-10 E11 Phase 1: the moments and the badges of one beat now play together (r[0].play(batch, bigs)); offers still wait
    assert 'isOpen || stageBusy() || badgeTimer || momentTimer' in run and 'pendingRewards.some(isBig)' in run
    assert 'offers.length ? loadStory()' in run and 'st.offer(offers[0])' in run, 'one offer at a time'
    assert run.index('r[0].play(batch, bigs)') < run.index('st.offer(offers[0])'), 'after the other moments'
    assert "isStoryOffer(m) { return !!m && m.kind === 'story_offer'; }" in guide
    # it asks nothing of the pupil: the stage it opens is the stage's own dialog with a Skip story button and Esc
    assert "stage.play(ch.scenes, { story: true })" in src


# ---------------------------------------------------------------------------------------------
# Existing pupils: one catch-up offer
# ---------------------------------------------------------------------------------------------

def test_existing_pupils_are_offered_one_chapter_once():
    c, uid = make_client('cu')
    give(uid, 12)                       # chapters 1 to 3 are open (2026-11-10 E11 Phase 2 counts)
    done_arrival(c)
    html = c.get('/profile').get_data(as_text=True)
    got = offers(island(html, 'pb-new-moments'))
    assert [m['chapter'] for m in got] == [1], got   # the first one only, never all four
    # the client marks it offered (story_o1) when the toast is shown; after that, nothing, however many pages
    patch_guide(c, {'tours': {'story_o1': True}})
    for path in ('/profile', '/', '/topics'):
        assert offers(island(c.get(path).get_data(as_text=True), 'pb-new-moments')) == [], path
    # Later is final until a new badge opens a new chapter (the live offer, not a catch-up)
    r = c.post('/_t/earn', json={'keys': [f'z_{i}' for i in range(4)]}, headers=H).get_json()
    assert [m['chapter'] for m in offers(r.get('new_moments') or [])] == [4], r
    # the same pupil who has watched anything is never caught up
    c2, uid2 = make_client('cu')
    give(uid2, 12)
    done_arrival(c2)
    patch_guide(c2, {'tours': {'story_w2': True}})
    assert offers(island(c2.get('/profile').get_data(as_text=True), 'pb-new-moments')) == []
    # not before the arrival and the tour are done, and not for a pupil with fewer than three badges
    c3, uid3 = make_client('cu')
    give(uid3, 12)
    assert offers(island(c3.get('/profile').get_data(as_text=True), 'pb-new-moments')) == [], 'arrival and tour not done'
    patch_guide(c3, {'v': 1, 'origin': True, 'tours': {'coach': True}, 'rewards': {}})
    assert offers(island(c3.get('/profile').get_data(as_text=True), 'pb-new-moments')) == [], 'tour not done'
    patch_guide(c3, {'v': 1, 'tours': {'app': True}, 'run': {'id': 'app', 'step': 2}})
    assert offers(island(c3.get('/profile').get_data(as_text=True), 'pb-new-moments')) == [], 'never while a tour is running'
    patch_guide(c3, {'v': 1, 'run': None})
    assert [m['chapter'] for m in offers(island(c3.get('/profile').get_data(as_text=True), 'pb-new-moments'))] == [1]
    c4, uid4 = make_client('cu')
    give(uid4, 2)
    done_arrival(c4)
    assert offers(island(c4.get('/profile').get_data(as_text=True), 'pb-new-moments')) == []
    # a live offer on the page replaces the catch-up (two offers never meet)
    c5, uid5 = make_client('cu')
    give(uid5, 2)
    done_arrival(c5)
    c5.post('/_t/earn-redirect', json={'keys': ['q_3']})
    assert len(offers(island(c5.get('/profile').get_data(as_text=True), 'pb-new-moments'))) == 1
    # not on the arrival page or the settings page
    c6, uid6 = make_client('cu')
    give(uid6, 12)
    done_arrival(c6)
    assert offers(island(c6.get('/profile/settings').get_data(as_text=True), 'pb-new-moments')) == []
    # a guest has no guide state and no offer
    with app.test_client() as guest:
        assert b'story_offer' not in guest.get('/').data


# ---------------------------------------------------------------------------------------------
# State: the protected region
# ---------------------------------------------------------------------------------------------

def test_watched_flags_are_kept_in_the_protected_region():
    keys = [f'{p}{n}' for p in (story.FLAG_WATCHED, story.FLAG_OFFERED) for n in range(1, 7)]
    assert all(social._GUIDE_TOUR_KEY.match(k) for k in keys), 'every flag is a valid tours key'
    c, uid = make_client('st')
    patch_guide(c, {'tours': {'story_w1': True, 'story_o1': True, 'story_w4': True}})
    state = stored(uid)
    assert state['tours']['story_w1'] and state['tours']['story_o1'] and state['tours']['story_w4'], state
    assert not any(k.startswith('story_') for k in (state.get('rewards') or {})) and not any(k.startswith('story_') for k in state.get('recent', []))
    # a flood of level, lesson and badge flags (the ring) and the tour's own flags never push the story flags out
    flood = {'rewards': {f'level:{i}': True for i in range(60)} | {f'lesson:gcse:maths:t{i}': True for i in range(250)}
             | {f'milestone:b{i}': True for i in range(120)}}
    patch_guide(c, flood)
    patch_guide(c, {'tours': {'sp_hint': True, 'coach': True, 'app': True}})
    state = stored(uid)
    assert all(state['tours'].get(k) for k in ('story_w1', 'story_o1', 'story_w4')), state['tours']
    # all twelve flags fit the region with the tour flags beside them
    patch_guide(c, {'tours': {k: True for k in keys}})
    state = stored(uid)
    assert all(state['tours'].get(k) for k in keys)
    assert len(json.dumps(state['tours'], separators=(',', ':'))) <= social.GUIDE_TOURS_BYTES
    # the client sees them as tours flags (pbGuide.tour.seen)
    live = c.get('/api/v1/me/settings', headers=H).get_json()['settings']['guide']
    assert live['tours']['story_w3'] is True
    # watching is the only thing stored: no new table, column or personal data
    src = _read(CHAPTERS_JS)
    assert src.count("mark('story_w' + n)") == 1 and src.count("mark('story_o' + n)") == 1
    assert 'fetch(' in src and src.count('fetch(') == 1 and 'method' not in src, 'the only request is the props template (GET)'


# ---------------------------------------------------------------------------------------------
# The shelf
# ---------------------------------------------------------------------------------------------

def test_the_shelf_on_the_profile():
    c, uid = make_client('sh')
    give(uid, 4)
    patch_guide(c, {'tours': {'story_w1': True}})
    html = c.get('/profile').get_data(as_text=True)
    sect = html[html.index('id="milestones"'):]
    sect = sect[:sect.index('</section>')]
    assert 'data-story-shelf' in sect and 'Zorp’s story' in sect, 'inside the Milestones section'
    items = re.findall(r'<li class="sty-item[^"]*" data-story-item="(\d)">(.*?)</li>', sect, re.S)
    assert [n for n, _ in items] == list('0123456'), 'Chapter 0 first, then the chapters in order'
    by = {n: body for n, body in items}
    assert 'Chapter 0' in by['0'] and 'Arrival' in by['0'] and 'data-story-play="0"' in by['0'] and 'Watch again' in by['0']
    assert 'data-story-play="1"' in by['1'] and 'Watch again' in by['1'] and 'Watched.' in by['1'], 'chapter 1 is watched'
    for n in '23456':
        assert 'data-story-play' not in by[n] and 'is-locked' in sect, n
    assert 'Unlocks at 6 badges' in by['2'] and 'Unlocks at 10 badges' in by['3'] and 'Unlocks at 15 badges' in by['4']
    assert 'Unlocks at 22 badges' in by['5'] and 'Unlocks at 30 badges' in by['6']
    assert 'Or earn a topic master badge.' in by['3'] and 'Or earn a subject complete badge.' in by['6']
    assert 'The maths belt' in by['1'] and 'Meet the crew' in by['2'] and 'A postcard from Novara' in by['6']
    # an unwatched, unlocked chapter says Watch
    give(uid, 2, 'more')
    html = c.get('/profile').get_data(as_text=True)
    two = re.search(r'data-story-item="2">(.*?)</li>', html, re.S).group(1)
    assert 'data-story-play="2"' in two and '>Watch<' in two and 'New.' in two, two
    # a topic master badge opens chapter 3 on the shelf with two badges fewer than the count
    c2, uid2 = make_client('sh')
    give(uid2, 1)
    with get_db() as conn:
        conn.execute("INSERT INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'topic_master:gcse:maths:bidmas', datetime('now'))", (uid2,))
        conn.commit()
    html = c2.get('/profile').get_data(as_text=True)
    assert 'data-story-play="3"' in re.search(r'data-story-item="3">(.*?)</li>', html, re.S).group(1)
    # a new pupil: only Chapter 0 can be watched
    c3, uid3 = make_client('sh')
    html = c3.get('/profile').get_data(as_text=True)
    assert html.count('data-story-play=') == 1 and 'data-story-play="0"' in html
    # the shelf's script and style are linked on this page only; the chapter scenes are not
    assert 'js/story-shelf.js?v=1' in html and 'css/story.css?v=1' in html
    assert not re.search(r'<script[^>]+src="[^"]*story-chapters\.js', html)
    shelf_js = _read(SHELF_JS)
    assert 'pbGuide' in shelf_js and 'g.story(' in shelf_js and 'pb-story-watched' in shelf_js
    assert 'story-chapters' not in shelf_js, 'the shelf never loads the scenes itself'


# ---------------------------------------------------------------------------------------------
# Lazy loading, versions, the preview
# ---------------------------------------------------------------------------------------------

def test_lazy_loading_versions_and_preview():
    guide_html = _read(ROOT / 'templates' / 'partials' / 'guide.html')
    assert 'id="pb-story-assets"' in guide_html and "'?v=1'" in guide_html
    base = _read(ROOT / 'templates' / 'base.html')
    for name in ('story-chapters', 'story.css', 'story-props', 'story-shelf'):
        assert name not in base, f'base.html must not mention {name}'
    sw = _read(JS / 'sw.js')
    for name in ('story-chapters', 'story.css', 'story-props', 'story-shelf'):
        assert name not in sw, f'{name} is not precached'
    guide = _read(JS / 'guide.js')
    assert 'function loadStory()' in guide and "getElementById('pb-story-assets')" in guide
    assert 'story: function (n, opts)' in guide and 'offerStory' in guide and 'innerHTML' not in guide

    def assert_lazy(html, where):
        assert not re.search(r'<script[^>]+src="[^"]*story-chapters\.js', html), where
        assert not re.search(r'<link[^>]+href="[^"]*/story\.css', html) or where.startswith('/profile'), where
        assert 'story-props.svg' not in re.sub(r'<script type="application/json" id="pb-story-assets">.*?</script>', '', html, flags=re.S), where

    with app.test_client() as guest:
        html = guest.get('/').data.decode()
        assert_lazy(html, 'guest /')
        assert 'pb-story-assets' not in html, 'no story for guests'
    c, uid = make_client('lz')
    for path in ('/', '/topics', '/welcome', '/profile'):
        r = c.get(path)
        assert r.status_code == 200, path
        html = r.data.decode()
        assert_lazy(html, path)
        assets = island(html, 'pb-story-assets')
        assert set(assets) == {'js', 'css', 'props'} and all('?v=' in v for v in assets.values()), (path, assets)
    for url in ('/static/js/story-chapters.js', '/static/css/story.css', '/static/images/story-props.svg', '/static/js/story-shelf.js'):
        assert c.get(url).status_code == 200, url
    # the preview plays any chapter straight
    with app.test_client() as client:
        html = client.get('/guide-preview').data.decode()
    assert 'id="guide-preview-story"' in html and "guide-preview.js?v=10" in html
    for n in range(7):
        assert f'data-story-chapter="{n}"' in html, n
    assert 'data-story-offer="3"' in html
    js = _read(JS / 'guide-preview.js')
    assert ".get('story')" in js and 'g.offerStory(' in js and 'g.story(' in js


TESTS = (
    test_files_and_caps,
    test_css_animates_transform_and_opacity_only,
    test_props_template_is_inert,
    test_catalogue_shape_and_beats,
    test_every_face_is_positive_or_neutral_and_chapters_end_positive,
    test_voice_rules_on_every_line,
    test_unlock_rules_are_the_servers,
    test_a_badge_that_crosses_a_threshold_carries_one_offer,
    test_the_offer_rides_the_page_island_and_the_session,
    test_the_offer_never_plays_by_itself,
    test_existing_pupils_are_offered_one_chapter_once,
    test_watched_flags_are_kept_in_the_protected_region,
    test_the_shelf_on_the_profile,
    test_lazy_loading_versions_and_preview,
)


def main():
    for t in TESTS:
        t()
        print('ok', t.__name__)
    print('Story chapters smoke (E10 phase 8) passed.')


if __name__ == '__main__':
    main()
