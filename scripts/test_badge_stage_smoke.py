"""E10 phase 4 badges smoke: copy, delivery, caps, lazy loading. Run: python scripts/test_badge_stage_smoke.py"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from flask import jsonify, redirect  # noqa: E402
from flask_login import current_user, login_required  # noqa: E402

import app as appmod  # noqa: E402
from app import app, get_db  # noqa: E402
from models import gamification as gam  # noqa: E402
from models.zorp_rig import CONTEXT_MAP  # noqa: E402

# Own caps (bytes). 2026-11-08: E10 phase 4, lazy files that load only when a badge is shown.
CAPS = {
    'static/js/badge-stage.js': 22500,   # 2026-11-10 E11 Phase 2 RAISED 20_000 -> 22_500: the perfect and growth families, the drawn sprouts (21,886 B); 2026-11-08: E10 phase 6b RAISED 18_000 -> 18_500 (+500) for the wardrobe line and the Try it on button (18,373 B); 2026-11-10 E11 Phase 1 RAISED 18_500 -> 20_000: part() lets moments.js play the badge cards inside one sequence (19,399 B)
    'static/css/badge-stage.css': 5500,
    'static/images/badge-props.svg': 8000,
    'static/js/badge-sheet.js': 3300,   # 2026-11-11: E11 Phase 3 RAISED 2_500 -> 3_300: the sheet reads the #pb-badge-data island and has Watch again (3,202 B)
}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


# Test-only routes (registered before the first request).
@app.get('/_t/badge-json')
@login_required
def _t_badge_json():
    appmod._note_new_milestones(current_user.id, [gam.MILESTONE_FIRST_QUIZ])
    return jsonify({'ok': True})


@app.get('/_t/badge-redirect')
@login_required
def _t_badge_redirect():
    appmod._note_new_milestones(current_user.id, [gam.MILESTONE_FIRST_QUIZ])
    return redirect('/')


def register(client):
    s = uuid.uuid4().hex[:8]
    r = client.post('/api/v1/auth/register', json={'email': f'bs_{s}@example.com', 'handle': f'bs_{s}',
                                                   'password': 'password123', 'age_confirm': True},
                    headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    b = r.get_json()
    return b['token'], b['user']['id']


def test_catalog_copy():
    for key, m in gam.MILESTONE_CATALOG.items():
        for f in ('title', 'blurb', 'how', 'family'):
            assert m.get(f), (key, f)
        assert m['family'] in gam.BADGE_FAMILIES, key
        assert len(m['blurb']) <= 80 and len(m['how']) <= 80, key
    assert gam.MILESTONE_CATALOG[gam.MILESTONE_ACCURACY_TOP_FRIEND]['title'] == 'Sharp week'
    assert 'Top of the class' not in read('app.py') + read('templates/profile.html')


def test_families_and_faces():
    js = read('static/js/badge-stage.js')
    block = js.split('// BEGIN FAMILIES')[1].split('// END FAMILIES')[0]
    faces = set(re.findall(r"(?:face|end):\s*'([a-z-]+)'", block)) | set(re.findall(r"\{ face: '([a-z-]+)' \}", block))
    assert faces <= set(CONTEXT_MAP['stage.badge']), faces - set(CONTEXT_MAP['stage.badge'])
    poses = read('static/js/zorp-poses.js') + read('static/js/guide-catalog.js')
    for clip in set(re.findall(r"play:\s*'([a-z-]+)'", block)):
        assert re.search(r"add\('%s'|\"%s\"|'%s'" % (clip, clip, clip), poses), clip
    for fam in gam.BADGE_FAMILIES:
        assert (fam in block) or fam in ('topic_completed',), fam


def test_delivery():
    with app.test_client() as c:
        tok, uid = register(c)
        h = {'Authorization': f'Bearer {tok}', 'Accept': 'application/json'}
        r = c.get('/_t/badge-json', headers=h)
        body = r.get_json()
        assert body['new_milestones'][0]['key'] == gam.MILESTONE_FIRST_QUIZ and body['new_milestones'][0]['blurb'], body
        assert r.headers.get('X-PB-Milestones') == '1'
        r = c.get('/_t/badge-redirect', headers=h)
        assert r.status_code == 302


def test_session_pending_once():
    with app.test_client() as c:
        s = uuid.uuid4().hex[:8]
        r = c.post('/api/v1/auth/register', json={'email': f'bp_{s}@example.com', 'handle': f'bp_{s}',
                                                  'password': 'password123', 'age_confirm': True})
        assert r.status_code == 201, r.data
        tok = r.get_json()['token']
        with c.session_transaction() as sess:
            sess['_user_id'] = str(r.get_json()['user']['id'])
            sess['_fresh'] = True
        c.get('/_t/badge-redirect')
        first = c.get('/profile').get_data(as_text=True)
        second = c.get('/profile').get_data(as_text=True)
        assert 'first_quiz' in first.split('pb-new-milestones')[1][:600]
        assert 'pb-new-milestones' not in second or 'first_quiz' not in second.split('pb-new-milestones')[1][:600]


def test_static_wiring():
    base = read('templates/base.html')
    guide_html = read('templates/partials/guide.html')
    for rel in CAPS:
        name = Path(rel).name
        assert name not in base, f'{name} must load lazily, not from base.html'
        assert name in guide_html or name in read('templates/profile.html') or name in read('templates/guide_preview.html'), name
        sw = read('static/sw.js') if (ROOT / 'static/sw.js').exists() else ''
        assert name not in sw, f'{name} must not be precached'
    assert 'effort' in read('app.py')
    assert gam.EFFORT_EVENT_TYPES.get('set_work_answered') == 1 if isinstance(gam.EFFORT_EVENT_TYPES, dict) else 'set_work_answered' in gam.EFFORT_EVENT_TYPES
    assert read('app.py').count('_record_set_work_answer(') >= 3   # def + two routes


def test_caps():
    for rel, cap in CAPS.items():
        n = (ROOT / rel).stat().st_size
        assert n <= cap, f'{rel} is {n} bytes, cap {cap}'
    assert 'innerHTML' not in read('static/js/badge-stage.js')
    assert 'innerHTML' not in read('static/js/badge-sheet.js')


def main():
    tests = [test_catalog_copy, test_families_and_faces, test_delivery, test_session_pending_once, test_static_wiring, test_caps]
    for t in tests:
        t()
    print('Badge stage smoke (E10 phase 4) passed.')


if __name__ == '__main__':
    main()
