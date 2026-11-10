"""E10 phase 6, part 1 fix 1: the guide seen-state can never be filled by celebration flags.
Run: python scripts/test_guide_state_budget_smoke.py

Phases 4 and 5 put one flag per badge, level and lesson into guide_json (4,096 bytes, 40 flags per update). A busy pupil could fill it, an
over-large merge was refused, and the tour, coach and spotlight flags then stopped saving. The state is now split into regions with
their own byte budgets (models/social.py): tours (and spotlights) and durable rewards are never evicted by the level, lesson and badge
flags, which live in a ring that drops its oldest entries. This test fills a pupil with many lessons, levels and badges and proves tour
flags, the tour step and the coach flag still save, that nothing is refused, and that the stored blob stays under the limit.
"""
import json
import os
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models import social  # noqa: E402

H = {'Accept': 'application/json'}


def make_client():
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'gb_{s}@example.com', 'handle': f'gb_{s}',
                                              'password': 'password123', 'age_confirm': True}, headers=H)
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def stored(uid):
    with get_db() as conn:
        raw = conn.execute('SELECT guide_json FROM user_profile_settings WHERE user_id = ?', (uid,)).fetchone()['guide_json']
    return raw, json.loads(raw)


def patch(c, guide):
    return c.patch('/api/v1/me/settings', json={'guide': guide}, headers=H)


def live(c):
    return c.get('/api/v1/me/settings', headers=H).get_json()['settings']['guide']


def test_merge_function_budgets():
    # 300 lesson flags, 60 levels and 285 badges in one merge: nothing is refused, the result fits, the flags that matter survive
    incoming = {
        'tours': {'coach': True, 'app': True, 'sp_hint': True},
        'rewards': {'streak:7': True, 'first_correct': True, 'lesson_complete': True},
        'run': {'id': 'app', 'step': 7},
    }
    for i in range(300):
        incoming['rewards'][f'lesson:gcse:maths:topic_number_{i}'] = True
    for i in range(60):
        incoming['rewards'][f'level:{i + 2}'] = True
    for i in range(285):
        incoming['rewards'][f'milestone:topic_completed:gcse:maths:topic_{i}'] = True
    dumped = social.merge_guide_json('', incoming)
    assert len(dumped) <= social.GUIDE_JSON_MAX, len(dumped)
    data = json.loads(dumped)
    assert data['tours'] == {'coach': True, 'app': True, 'sp_hint': True}
    assert data['rewards'] == {'streak:7': True, 'first_correct': True, 'lesson_complete': True}
    assert data['run'] == {'id': 'app', 'step': 7}
    assert 0 < len(data['recent']) <= social.GUIDE_RECENT_MAX
    # the newest flags are the ones kept (the ring drops its oldest)
    assert data['recent'][-1] == 'milestone:topic_completed:gcse:maths:topic_284'
    assert 'lesson:gcse:maths:topic_number_0' not in data['recent']
    # the worst case for every region at once still fits under the limit
    worst = {
        'tours': {f't_{chr(97 + i % 26)}{i:02d}_' + 'x' * 20: True for i in range(200)},
        'rewards': {f'streak:{i}_' + 'y' * 50: True for i in range(300)},
    }
    for i in range(200):
        worst['rewards'][f'lesson:' + 'z' * 56 + f'{i:03d}'] = True
    worst_dumped = social.merge_guide_json('', worst)
    assert len(worst_dumped) <= social.GUIDE_JSON_MAX, len(worst_dumped)
    # an old blob with every flag in `rewards` (as phases 4 and 5 wrote it) is moved into the ring on the next merge
    old = json.dumps({'v': 1, 'origin': True, 'tours': {'learn': True},
                      'rewards': {**{f'lesson:a:b:t{i}': True for i in range(30)}, 'streak:7': True}})
    merged = json.loads(social.merge_guide_json(old, {'tours': {'app': True}}))
    assert merged['tours'] == {'learn': True, 'app': True} and merged['rewards'] == {'streak:7': True}
    assert len(merged['recent']) == 30 or len(merged['recent']) <= social.GUIDE_RECENT_MAX
    # run: shape-checked, cleared by null
    assert social.validate_guide_patch({'run': {'id': 'app', 'step': 999}})[1]
    assert social.validate_guide_patch({'run': {'id': 'App!', 'step': 1}})[1]
    assert social.validate_guide_patch({'run': 'x'})[1]
    assert social.validate_guide_patch({'run': None})[1] is None
    cleared = json.loads(social.merge_guide_json(dumped, {'run': None}))
    assert 'run' not in cleared


def test_a_busy_pupil_still_saves_tour_flags():
    c, uid = make_client()
    # the client sends its whole state each time; do what an active pupil's client does for many lessons, levels and badges
    # (the client hydrates from the server's state, so what it sends back is what the server kept, plus the new flag)
    for i in range(150):
        flags = {f'lesson:gcse:maths:topic_{i}': True}
        if i < 40:
            flags[f'level:{i + 2}'] = True
        r = patch(c, {'rewards': {**live(c)['rewards'], **flags}})
        assert r.status_code == 200, (i, r.status_code, r.data[:200])
    for i in range(285):
        r = patch(c, {'rewards': {**live(c)['rewards'], f'milestone:topic_completed:gcse:maths:topic_{i}': True}})
        assert r.status_code == 200, (i, r.data[:200])
    raw, data = stored(uid)
    assert len(raw) <= social.GUIDE_JSON_MAX, len(raw)
    # now the flags that must never be crowded out
    r = patch(c, {'tours': {'coach': True, 'practice': True, 'sp_hint': True, 'sp_saved': True}, 'run': {'id': 'app', 'step': 3}})
    assert r.status_code == 200, r.data[:200]
    g = live(c)
    assert all(g['tours'].get(k) is True for k in ('coach', 'practice', 'sp_hint', 'sp_saved')), g['tours']
    assert g['run'] == {'id': 'app', 'step': 3}
    # and again after the pupil goes on to finish the tour and a badge arrives
    r = patch(c, {'tours': {'app': True, 'learn': True}, 'run': None, 'rewards': {'milestone:app_tour': True, 'streak:7': True}})
    assert r.status_code == 200
    g = live(c)
    assert g['tours'].get('app') is True and g['run'] is None
    assert g['rewards'].get('streak:7') is True and g['rewards'].get('milestone:app_tour') is True
    raw, data = stored(uid)
    assert len(raw) <= social.GUIDE_JSON_MAX and data['tours']['coach'] is True
    # the page hydrates the client with one rewards dict (durable flags, then the ring) and the run
    html = c.get('/').get_data(as_text=True)
    start = html.index('id="pb-guide-state"')
    island = json.loads(html[html.index('>', start) + 1:html.index('</script>', start)])
    assert island['tours']['app'] is True and island['rewards']['streak:7'] is True and island['run'] is None
    # a single huge update (many flags at once) is accepted, not refused
    huge = {'rewards': {f'lesson:x:y:z{i}': True for i in range(380)}, 'tours': {'sp_quicktest': True}}
    assert patch(c, huge).status_code == 200
    assert live(c)['tours'].get('sp_quicktest') is True
    # a real fault is still refused: a transport body far beyond any pupil's state, and a bad run
    assert patch(c, {'rewards': {f'lesson:x:{"y" * 40}:{i}': True for i in range(700)}}).status_code == 400
    assert patch(c, {'run': {'id': 'app', 'step': -1}}).status_code == 400


def test_phase_5_flags_use_the_ring():
    # the two kinds of flag guide.js writes for celebrations: level:<n>, lesson:<level>:<subject>:<topic>, milestone:<key>
    c, uid = make_client()
    assert patch(c, {'rewards': {'level:2': True, 'lesson:gcse:maths:algebra': True, 'milestone:streak_7': True, 'first_correct': True,
                                 'lesson_complete': True, 'streak:7': True}}).status_code == 200
    raw, data = stored(uid)
    # (the test client sorts JSON keys, so only the set is compared; a browser sends them in the order the client added them)
    assert sorted(data['recent']) == ['lesson:gcse:maths:algebra', 'level:2', 'milestone:streak_7'], data
    assert data['rewards'] == {'first_correct': True, 'lesson_complete': True, 'streak:7': True}
    g = live(c)
    assert set(g['rewards']) == {'level:2', 'lesson:gcse:maths:algebra', 'milestone:streak_7', 'first_correct', 'lesson_complete', 'streak:7'}
    # the wiring: guide.js marks them the same way (rewardSeen / markReward), and the doc says where they live
    guide = (ROOT / 'static/js/guide.js').read_text(encoding='utf-8')
    assert 'function markRewardSeen' in guide and "run: base.run && typeof base.run.id === 'string'" in guide
    plan = (ROOT / 'docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md').read_text(encoding='utf-8')
    assert '11.9 Phase 6' in plan and 'seen-state regions' in plan


def main():
    for t in (test_merge_function_budgets, test_a_busy_pupil_still_saves_tour_flags, test_phase_5_flags_use_the_ring):
        t()
        print('ok', t.__name__)
    print('Guide state budget smoke (E10 phase 6) passed.')


if __name__ == '__main__':
    main()
