"""Celebrations gallery smoke (/celebrations-gallery, dev only; docs/BADGES_AND_CELEBRATIONS_PLAN.md section 13).
Run: python scripts/test_celebrations_gallery_smoke.py

Checks: the dev gate (404 on a production HTTPS site); every catalogue badge outside the subject lines is on the page with its
display data, plus a subject and a topic sample; the wardrobe line each badge would carry; preview mode; the page never takes a
signed-in pupil's waiting celebrations; every corner card kind the gallery shows exists in moments.js; the client wiring.
"""
import json
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app  # noqa: E402
from models import gamification as gam  # noqa: E402

HDR = {'Accept': 'application/json'}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def rows_of(html):
    return json.loads(re.search(r'id="gallery-badges">(.*?)</script>', html, re.S).group(1))


def test_gate():
    old = {k: os.environ.get(k) for k in ('PB_TESTING', 'PB_STYLEGUIDE', 'SITE_URL')}
    try:
        os.environ.pop('PB_TESTING', None)
        os.environ.pop('PB_STYLEGUIDE', None)
        os.environ['SITE_URL'] = 'https://pb.example.com'
        assert app.test_client().get('/celebrations-gallery', base_url='https://pb.example.com').status_code == 404
        assert app.test_client().get('/celebrations-gallery', base_url='http://127.0.0.1:5000').status_code == 200, 'localhost always'
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_every_badge_is_there():
    html = app.test_client().get('/celebrations-gallery').get_data(as_text=True)
    assert 'data-guide-preview="1"' in html, 'preview mode: nothing is saved'
    rows = rows_of(html)
    keys = [b['key'] for r in rows for b in r['badges']]
    want = [k for k in gam.MILESTONE_CATALOG if not k.startswith('subject_')]
    assert set(want) <= set(keys) and len(keys) == len(set(keys)), sorted(set(want) - set(keys))
    assert {'subject_completed:gcse:maths', 'topic_master:gcse:maths:bidmas'} <= set(keys)
    for b in (b for r in rows for b in r['badges']):
        assert {'key', 'title', 'blurb', 'family', 'emoji', 'tier', 'how'} <= set(b) and b['title'] and b['how'], b
    by_key = {b['key']: b for r in rows for b in r['badges']}
    assert by_key['perfect_1']['wardrobe']['id'] == 'hat.crown' and by_key['bounce_1']['wardrobe']['id'] == 'hat.sprout'
    assert 'wardrobe' not in by_key['perfect_5'], 'the first badge of a family opens its item'
    assert html.count('data-gal-badge="') == len(keys) and html.count('data-gal-line="') == len(rows)


def test_never_takes_waiting_celebrations():
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    uid = c.post('/api/v1/auth/register', json={'email': f'g_{s}@example.com', 'handle': f'g_{s}', 'password': 'password123',
                                                'age_confirm': True}, headers=HDR).get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
        sess['pb_own'] = uid
        sess['pb_ms'] = ['first_quiz']
    html = c.get('/celebrations-gallery').get_data(as_text=True)
    assert 'id="pb-new-milestones"' not in html and 'id="pb-new-moments"' not in html
    later = c.get('/topics').get_data(as_text=True)
    assert 'first_quiz' in (re.search(r'id="pb-new-milestones">(.*?)</script>', later, re.S) or [None, ''])[1], 'still waiting for a real page'


def test_client():
    js = read('static/js/celebrations-gallery.js')
    moments = read('static/js/moments.js')
    block = js[js.index('var CARDS = ['):js.index('];', js.index('var CARDS = ['))]   # 2026-11-13: the SOUNDS list has the same shape
    kinds = set(re.findall(r"^\s*\['(\w+)', '", block, re.M))
    assert len(kinds) >= 20
    faces = moments[moments.index('// BEGIN FACES'):moments.index('// END FACES')]
    for kind in kinds:
        assert re.search(rf'\b{kind}: \'', faces), f'{kind} has no card in moments.js'
    for needle in ("g.badges([spec(b)])", "window.pbMoments.sequence(front, badges, back)", "window.pbMoments.toast(",
                   "badges = [spec(badgeAt('1:1'))];", "g.story(parseInt(a, 10))", "window.pbCelebrate.xp(parseInt(a, 10))",
                   "island('pb-moment-assets')", "island('pb-badge-assets')"):
        assert needle in js, needle
    assert 'celebrations-gallery.js' not in read('static/js/sw.js'), 'dev only, never precached'
    assert "url_for('celebrations_gallery')" in read('templates/guide_preview.html')


def main():
    for t in (test_gate, test_every_badge_is_there, test_never_takes_waiting_celebrations, test_client):
        t()
        print('ok', t.__name__)
    print('Celebrations gallery smoke passed.')


if __name__ == '__main__':
    main()
