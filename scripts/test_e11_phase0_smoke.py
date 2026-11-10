"""E11 Phase 0 smoke (docs/BADGES_AND_CELEBRATIONS_PLAN.md sections 1 and 6): the fixes found from David's 2026-11-10 report.
Run: python scripts/test_e11_phase0_smoke.py

Checks:
  1.1  page-delivered badges and moments reach a page that the service worker relays (the behaviour is tested with real browser
       headers in test_celebration_moments_smoke.py; here the wiring);
  1.2  browser storage that holds one pupil's state is keyed per account (lesson ticks, the guide's local copy, celebrated flags,
       the corner Zorp's quiet flag), the shared keys are removed unread, and a lesson save that the server has no row for is sent;
  1.3  one beat, not two: the first-correct dialog waits for a badge in the same moment; the lesson stage names the lesson badge
       its save earns, and that badge's own stage is not played; a spotlight steps aside while a stage is on screen.
The browser walks (service worker active, two pupils on one browser) are in the plan's section 8.
"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402

LESSON = ('gcse', 'maths', 'bidmas')   # six quick checks


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def new_pupil(prefix='e11'):
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'{prefix}_{s}@example.com', 'handle': f'{prefix}_{s}',
                                              'password': 'password123', 'age_confirm': True},
               headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def store_ns(html):
    m = re.search(r'<meta name="pb-store" content="([^"]*)">', html)
    assert m, 'the pb-store meta is missing'
    return m.group(1)


def csrf_of(html):
    return re.search(r'<meta name="csrf-token" content="([^"]+)">', html).group(1)


def test_storage_name_per_account():
    a, uid_a = new_pupil()
    b, uid_b = new_pupil()
    ns_a = store_ns(a.get('/topics').get_data(as_text=True))
    ns_b = store_ns(b.get('/topics').get_data(as_text=True))
    assert re.fullmatch(r'a[0-9a-f]{12}', ns_a) and re.fullmatch(r'a[0-9a-f]{12}', ns_b), (ns_a, ns_b)
    assert ns_a != ns_b, 'two accounts must never share a storage name'
    assert ns_a == store_ns(a.get('/profile').get_data(as_text=True)), 'stable for one account'
    assert ns_a not in (str(uid_a), 'a' + str(uid_a), 'u' + str(uid_a)), 'the account id itself is not the name'
    assert store_ns(app.test_client().get('/topics').get_data(as_text=True)) == '', 'signed out: no storage name'


def test_lesson_progress_keys_and_save():
    js = read('static/js/lesson-progress.js')
    assert "meta[name=\"pb-store\"]" in js and "(isLoggedIn ? storeNs : 'anon')" in js
    # the old browser-wide keys are removed and never read
    assert "removeItem('lesson-progress:' + lessonId)" in js and "removeItem('lesson-progress:' + lessonId + ':celebrated')" in js
    assert "getItem('lesson-progress:' + lessonId" not in js
    assert 'if (!useLocal) return [];' in js and 'if (!useLocal) return;' in js
    # a lesson the server has no row for still saves the pupil's own steps
    merge = js.split("if (!data || !data.ok) return;")[1][:1400]
    assert 'missing' in merge and 'if (!data.progress && !missing) return;' in merge and 'persistSnapshot(keys);' in merge
    # the server side of that: no row yet answers ok with progress null, and a save with all six steps earns both badges in
    # the JSON answer (the client names the lesson one on the lesson stage)
    c, _ = new_pupil()
    page = c.get('/topic/{}/{}/{}'.format(*LESSON)).get_data(as_text=True)
    body = c.get('/api/lesson-progress/{}/{}/{}'.format(*LESSON)).get_json()
    assert body['ok'] is True and body['progress'] is None, body
    keys = [f'step-{i}' for i in range(6)]
    r = c.post('/api/lesson-progress', json={'csrf_token': csrf_of(page), 'level': LESSON[0], 'subject': LESSON[1],
                                             'topic': LESSON[2], 'section_key': 'step-5', 'section_label': 'x',
                                             'completed_keys': keys, 'step_total': 6})
    got = [m['key'] for m in r.get_json().get('new_milestones') or []]
    assert 'first_lesson_step' in got and 'topic_completed:gcse:maths:bidmas' in got, got
    assert 'X-PB-Milestones' in r.headers


def test_other_per_pupil_keys():
    celebrate = read('static/js/celebrate.js')
    assert "'pb-u74-ms-'" not in celebrate and "'pb-u74-streak-'" not in celebrate
    assert "var LS_MILESTONE = 'pb-ms:' + STORE_NS + ':';" in celebrate and "var LS_STREAK = 'pb-streak:' + STORE_NS + ':';" in celebrate
    guide = read('static/js/guide.js')
    assert "var STORAGE_KEY = 'pb-guide-v1:' + STORE_NS;" in guide and "removeItem('pb-guide-v1')" in guide
    buddy = read('static/js/study-buddy.js')
    assert "var QUIET_KEY = 'pb-buddy-quiet:' +" in buddy and "removeItem('pb-buddy-quiet')" in buddy
    base = read('templates/base.html')
    assert '<meta name="pb-store" content="{{ pb_store_ns|default(\'\') }}">' in base
    assert base.index('name="pb-store"') < base.index("js/guide.js"), 'the meta comes before the scripts that read it'


def test_one_beat_not_two():
    guide = read('static/js/guide.js')
    rew = guide.split('  function reward(spec) {')[1].split('\n  }\n')[0]
    assert "if (spec.type === 'first_correct') return holdFirstCorrect(spec);" in rew
    assert "if (isBig(spec) || spec.type === 'lesson_complete') dropFirstCorrect();" in rew
    assert "if (spec.type === 'milestone' && absorbed[spec.key]) { markRewardSeen(id); return 'stage'; }" in rew
    assert rew.index('absorbLessonBadge(spec)') < rew.index('return moments([spec])')
    hold = guide.split('function holdFirstCorrect(spec) {')[1][:700]
    assert 'stageBusy() || badgeTimer || pendingMoments.length || pendingRewards.some(isBig)' in hold
    assert "markRewardSeen('first_correct')" in hold
    assert 'var FIRST_HOLD_MS = 1800;' in guide
    absorb = guide.split('function absorbLessonBadge(spec) {')[1][:600]
    assert "'topic_completed:' + [spec.level, spec.subject, spec.topic].join(':')" in absorb and 'absorbed[key] = true;' in absorb
    lp = read('static/js/lesson-progress.js')
    fin = lp.split('var finishing = !celebrated && steps.every(')[1][:1300]
    assert 'persistSnapshot(keys)' in fin and 'setTimeout(function () { finish(null); }, 2500);' in fin
    assert 'maybeCelebrateAllComplete(steps, true, lessonBadge(data));' in fin
    assert "var want = 'topic_completed:' + lessonId;" in lp and 'badge: badge || null,' in lp
    assert 'if (!live && finishingLive) return;' in lp
    moments = read('static/js/moments.js')
    assert "lessonBadge: 'New badge: {title}.'," in moments
    assert "g.markReward('milestone:' + String(m.badge.key)" in moments


def test_spotlight_steps_aside():
    tour = read('static/js/zorp-tour.js')
    guard = tour.split('function openSpot(id, target) {')[1].split('\n  }\n')[0]
    assert 'var away = blocked();' in guard and 'P.card.box.hidden = away;' in guard and 'mark(P.target, !away);' in guard
    assert 'if (!away) place(P.card, P.target);' in guard and '}, 300);' in guard


def test_delivery_rule_wiring():
    src = read('app.py').split('def _pending_may_emit')[1][:2200]
    assert "return mode == 'navigate' and dest not in _FRAME_DESTS" in src
    assert "if headers.get('Service-Worker'):" in src


def main():
    tests = [test_storage_name_per_account, test_lesson_progress_keys_and_save, test_other_per_pupil_keys, test_one_beat_not_two,
             test_spotlight_steps_aside, test_delivery_rule_wiring]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('E11 Phase 0 smoke passed.')


if __name__ == '__main__':
    main()
