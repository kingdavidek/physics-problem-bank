"""E10 phase 5 moments smoke: level-up, perfect quiz, finished lesson, toasts, micro, honest XP.
Run: python scripts/test_celebration_moments_smoke.py

Checks: caps and rules of the lazy files; copy, faces and choreography; level-up detection and once-only delivery (JSON, page
island, session); a real lesson quiz through its results page (perfect moment, toast, retry cleared, honest XP line); the other
toasts (personal best, Quick Test, Daily week, set work, challenge, streak skip); the queue order rule when a badge and a moment
coincide; honest XP everywhere a number is shown; lazy loading; the voice lint of the moments copy.
"""
import json
import os
import re
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from flask import jsonify, redirect  # noqa: E402
from flask_login import current_user, login_required  # noqa: E402

import app as appmod  # noqa: E402
from app import app, get_db  # noqa: E402
from models import gamification as gam  # noqa: E402
from models import zorp_voice as voice  # noqa: E402
from models.zorp_rig import CONTEXT_MAP  # noqa: E402

# Own caps (bytes). 2026-11-08: E10 phase 5, lazy files that load only when a moment is due.
CAPS = {
    'static/js/moments.js': 36500,   # 2026-11-10 E11 Phase 0: +600, the lesson stage names the lesson badge (measured 24,085 B); 2026-11-10 E11 Phase 1 RAISED 24_600 -> 36_500: the one-sequence player, the setting, the day's budget, the carry to the next page and eleven new corner cards (measured 35,988 B). Lazy: loads only when a moment is due
    'static/css/moments.css': 5000,
}
TOPIC = ('gcse', 'maths', 'bidmas')   # ten multiple choice questions


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


# ---- test-only routes (registered before the first request) ----
@app.post('/_t/effort/<event_type>')
@login_required
def _t_effort(event_type):
    with get_db() as conn:
        appmod.record_activity_event(conn, current_user.id, event_type, {}, 'private')
    return jsonify({'ok': True})


@app.post('/_t/effort-redirect/<event_type>')
@login_required
def _t_effort_redirect(event_type):
    with get_db() as conn:
        appmod.record_activity_event(conn, current_user.id, event_type, {}, 'private')
    return redirect('/')


@app.post('/_t/finished')
@login_required
def _t_finished():
    from flask import request
    q = request.get_json()
    appmod.g.pb_new_ms = q.get('badges') or []
    appmod._note_quiz_finished(current_user.id, *TOPIC, q['score'], q['total'], q['attempt'], wrong=q['total'] - q['score'],
                               retry_mode=q.get('retry', False), kind=q.get('kind', 'lesson'))
    appmod.g.pb_new_ms = []
    return jsonify({'ok': True})


@app.post('/_t/setwork/<status>')
@login_required
def _t_setwork(status):
    appmod._record_set_work_answer(7, {'status': status})
    return jsonify({'ok': True})


@app.post('/_t/daily/<day>')
@login_required
def _t_daily(day):
    appmod._note_daily_answered(current_user.id, day, True)
    return jsonify({'ok': True})


@app.post('/_t/study')
@login_required
def _t_study():
    appmod._record_study_activity(current_user.id)
    return jsonify({'ok': True})


def make_client():
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'mo_{s}@example.com', 'handle': f'mo_{s}',
                                              'password': 'password123', 'age_confirm': True},
               headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid


def holds_full_marks(uid):
    """E11 Phase 1: an account that already holds Full marks, so its next 10/10 is the perfect moment (a first 10/10 ever earns the
    badge instead, whose stage is that 10/10's celebration)."""
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at, quiet) "
                     "VALUES (?, 'perfect_1', datetime('now'), 2)", (uid,))
        conn.commit()


def lifetime(uid):
    with get_db() as conn:
        return gam.lifetime_effort_xp(conn, uid)


def seed_xp(uid, points):
    """Give the pupil `points` effort points the quick way (topic opened events weigh 1 each)."""
    with get_db() as conn:
        for _ in range(points):
            conn.execute("INSERT INTO user_activity_events (user_id, event_type, payload_json, visibility, created_at) "
                         "VALUES (?, 'topic_opened', '{}', 'private', datetime('now', '-1 hour'))", (uid,))
        conn.commit()


def moments_of(html):
    m = re.search(r'<script type="application/json" id="pb-new-moments">(.*?)</script>', html, re.S)
    return json.loads(m.group(1)) if m else []


def csrf_of(html):
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


# ---- files, rules, copy ----
def test_caps_and_rules():
    for rel, cap in CAPS.items():
        n = (ROOT / rel).stat().st_size
        assert n <= cap, f'{rel} is {n} bytes, cap {cap}'
    js, css = read('static/js/moments.js'), read('static/css/moments.css')
    assert 'innerHTML' not in js and 'insertAdjacentHTML' not in js and 'eval(' not in js
    assert not re.search(r'https?://', js.replace(SVG_NS, '')) and 'cdn' not in js.lower()
    assert '@keyframes' not in css and 'transition' not in css and 'animation' not in css   # WAAPI only, in the script
    for banned in ('width', 'height', 'top', 'left', 'margin', 'background', 'color'):
        for m in re.finditer(r'\.animate\(\[(.*?)\],', js, re.S):
            assert not re.search(r'\b%s\s*:' % banned, m.group(1)), (banned, m.group(1)[:80])
    assert 'onclick' not in js and 'onerror' not in js


SVG_NS = 'http://www.w3.org/2000/svg'


def test_copy_faces_scenes():
    js = read('static/js/moments.js')
    faces_block = js.split('// BEGIN FACES')[1].split('// END FACES')[0]
    scenes_block = js.split('// BEGIN SCENES')[1].split('// END SCENES')[0]
    faces = set(re.findall(r":\s*'([a-z-]+)'", faces_block)) | set(re.findall(r"(?:face|end):\s*'([a-z-]+)'", scenes_block))
    assert faces and faces <= set(CONTEXT_MAP['stage.moment']), faces - set(CONTEXT_MAP['stage.moment'])
    assert set(CONTEXT_MAP['stage.moment']) <= set(CONTEXT_MAP['guide'])
    poses = read('static/js/zorp-poses.js')
    for clip in set(re.findall(r"play:\s*'([a-z-]+)'", scenes_block)):
        assert re.search(r"add\('%s'" % clip, poses), clip
    items, errors = voice.extract_moment_copy()
    assert not errors and len(items) >= 23, errors
    bad = [v for v in voice.lint(items) if v.level == 'error']
    assert not bad, bad
    lines = {i.where: i.text for i in items}
    assert lines['levelLine'] == 'Level 4. Your effort points keep adding up.'
    assert lines['hint'] == 'Got there with a hint.' and lines['fixed'] == 'All fixed.'
    assert lines['skip'] == 'Your weekly skip kept your streak going.'
    assert lines['quizMore'] == '7 out of 10. Retry the 3 you missed?'
    for k in ('week', 'setwork', 'challenge', 'best', 'quicktest'):
        for word in ('won', 'win ', 'lost', 'lose', 'beat', 'rank', 'better than'):
            assert word not in lines[k].lower() + ' ', (k, word)
    assert 'XP' not in ' '.join(lines.values())   # numbers come from the server, never from copy


# ---- level-up ----
def test_level_up_detection_and_delivery():
    c, uid = make_client()
    h = {'Accept': 'application/json'}
    seed_xp(uid, 197)                                    # level 1 (below 200)
    assert gam.xp_level_from_points(197) == 1
    r = c.post('/_t/effort/lesson_step_completed', headers=h)   # +2: 199, still level 1
    assert 'new_moments' not in r.get_json()
    r = c.post('/_t/effort/quiz_completed', headers=h)           # +3: 202, level 2
    body = r.get_json()
    assert r.headers.get('X-PB-Milestones'), r.headers
    lv = [m for m in body['new_moments'] if m['type'] == 'level']
    assert len(lv) == 1 and lv[0]['level'] == 2 and lv[0]['id'] == 'level:2' and 0 <= lv[0]['pct'] <= 1, body
    assert lifetime(uid) == 202
    r = c.post('/_t/effort/quiz_completed', headers=h)           # 205: nothing new
    assert 'new_moments' not in r.get_json()
    # a non-effort event never counts; a topic page view shows the island once
    # redirect path: the next page carries it once, then nothing
    uid2 = make_client()
    c2, u2 = uid2
    seed_xp(u2, 198)
    r = c2.post('/_t/effort-redirect/quiz_completed')            # 201: level 2, redirect
    assert r.status_code == 302
    first = c2.get('/profile').get_data(as_text=True)
    assert [m['id'] for m in moments_of(first)] == ['level:2']
    second = c2.get('/profile').get_data(as_text=True)
    assert moments_of(second) == []
    # level maths
    up = gam.level_up_between(199, 202)
    assert up and up['level'] == 2 and gam.level_up_between(202, 205) is None
    assert gam.level_up_between(449, 451)['level'] == 3 and gam.level_up_between(0, 1) is None
    # a level jump of two levels in one step reports the highest
    assert gam.level_up_between(100, 460)['level'] == 3


# ---- a real lesson quiz ----
def quiz_problems(uid):
    with get_db() as conn:
        row = conn.execute("SELECT data FROM quicktest_sessions WHERE session_id LIKE 'lq_%' ORDER BY rowid DESC LIMIT 1").fetchone()
    return json.loads(row['data'])['problems']


def take_quiz(c, uid, wrong):
    """Start the BIDMAS lesson quiz, answer it (the first `wrong` questions wrongly) and submit. Returns the response."""
    level, subject, topic = TOPIC
    r = c.get(f'/lesson-quiz/{level}/{subject}/{topic}')
    assert r.status_code == 200
    problems = quiz_problems(uid)
    form = {}
    for i, p in enumerate(problems):
        right = p['correct_answer']
        letter = next(ch for ch in 'ABCD' if ch != right[:1].upper()) if i < wrong else right[:1].upper()
        form[f'answer_{i}'] = letter
    return c.post(f'/lesson-quiz/{level}/{subject}/{topic}/submit', data=form)


def test_perfect_quiz_real_flow_and_honest_xp():
    c, uid = make_client()
    xp0 = lifetime(uid)
    r = take_quiz(c, uid, wrong=0)
    assert r.status_code == 302 and '/quiz-attempts/' in r.headers['Location']
    xp1 = lifetime(uid)
    page = c.get(r.headers['Location']).get_data(as_text=True)
    ms = moments_of(page)
    # 2026-11-10 E11 Phase 1: the first 10/10 ever earns the Full marks badge, and its badge stage is that 10/10's celebration (no
    # perfect moment beside it); every later 10/10 is the full-screen perfect moment (David's answer 1)
    badges = re.search(r'id="pb-new-milestones">(.*?)</script>', page, re.S)
    assert badges and 'perfect_1' in [b['key'] for b in json.loads(badges.group(1))], 'the first 10/10 earns Full marks'
    assert not [m for m in ms if m['type'] == 'perfect'], ms
    assert not [m for m in ms if m['type'] == 'toast' and m['kind'] in ('quiz_done', 'personal_best')], ms
    # honest XP: the line equals what was recorded (3 for the quiz, plus nothing else on the submit)
    shown = re.search(r'quiz-results-xp">\+(\d+) XP earned', page)
    assert shown, 'the XP line is missing after a fresh submit'
    quiz_points = gam.EFFORT_WEIGHTS['quiz_completed']
    assert int(shown.group(1)) == quiz_points == xp1 - xp0, (shown.group(1), xp0, xp1)
    # once: a reload shows no moment and no XP line
    again = c.get(r.headers['Location']).get_data(as_text=True)
    assert moments_of(again) == [] and 'quiz-results-xp' not in again
    assert 'score * 5' not in read('templates/lesson_mcq_results.html')
    # the second 10/10 is the perfect moment, its own (the badge is not earned twice)
    r2 = take_quiz(c, uid, wrong=0)
    page2 = c.get(r2.headers['Location']).get_data(as_text=True)
    perfect = [m for m in moments_of(page2) if m['type'] == 'perfect']
    assert len(perfect) == 1 and perfect[0]['score'] == 10 and perfect[0]['total'] == 10, perfect
    assert 'perfect_1' not in page2.split('id="pb-new-milestones">')[-1][:400] or 'id="pb-new-milestones"' not in page2
    r3 = take_quiz(c, uid, wrong=0)
    ms3 = moments_of(c.get(r3.headers['Location']).get_data(as_text=True))
    assert [m['id'] for m in ms3 if m['type'] == 'perfect'] != [perfect[0]['id']], 'each 10/10 is its own moment'


def test_imperfect_quiz_toast_retry_and_cleared():
    c, uid = make_client()
    r = take_quiz(c, uid, wrong=3)
    page = c.get(r.headers['Location']).get_data(as_text=True)
    ms = moments_of(page)
    assert not [m for m in ms if m['type'] == 'perfect']
    t = [m for m in ms if m['type'] == 'toast' and m['kind'] in ('quiz_done', 'personal_best')]
    assert len(t) == 1 and t[0]['score'] == 7 and t[0]['total'] == 10 and t[0]['wrong'] == 3, ms
    assert 'id="retry-wrong"' in page   # the toast link points at the real control
    # retry the three: all right clears them
    level, subject, topic = TOPIC
    r = c.post(f'/lesson-quiz/{level}/{subject}/{topic}/retry-wrong', data={'csrf_token': csrf_of(page)})
    assert r.status_code == 302, r.status_code
    r = c.get(f'/lesson-quiz/{level}/{subject}/{topic}')
    assert r.status_code == 200
    problems = quiz_problems(uid)
    assert len(problems) == 3
    form = {f'answer_{i}': p['correct_answer'][:1].upper() for i, p in enumerate(problems)}
    r = c.post(f'/lesson-quiz/{level}/{subject}/{topic}/submit', data=form)
    ms = moments_of(c.get(r.headers['Location']).get_data(as_text=True))
    kinds = [m.get('kind') for m in ms if m['type'] == 'toast']
    assert kinds == ['retry_cleared'] and not [m for m in ms if m['type'] == 'perfect'], ms   # a retry run is not a perfect quiz


def test_other_toasts_and_rules():
    c, uid = make_client()
    h = {'Accept': 'application/json'}

    def post(path, data=None):
        return c.post(path, json=data, headers=h).get_json()

    # perfect + a ninja or master badge in the same request: the badge stage plays alone (no perfect moment, no toast)
    b = post('/_t/finished', {'score': 10, 'total': 10, 'attempt': 901, 'badges': ['topic_ninja:gcse:maths:bidmas']})
    assert 'new_moments' not in b
    b = post('/_t/finished', {'score': 10, 'total': 10, 'attempt': 900, 'badges': ['perfect_1']})
    assert 'new_moments' not in b                                         # E11 Phase 1: Full marks is that 10/10's stage
    b = post('/_t/finished', {'score': 10, 'total': 10, 'attempt': 902, 'badges': ['streak_7']})
    assert [m['type'] for m in b['new_moments']] == ['perfect']           # an unrelated badge: both play, badge first
    b = post('/_t/finished', {'score': 4, 'total': 4, 'attempt': 903})
    assert [m['type'] for m in b['new_moments']] == ['perfect']
    b = post('/_t/finished', {'score': 2, 'total': 2, 'attempt': 904})
    assert b['new_moments'][0]['kind'] == 'quiz_done'                     # under three questions: a toast, not a stage
    b = post('/_t/finished', {'score': 9, 'total': 10, 'attempt': 905, 'kind': 'quicktest'})
    assert b['new_moments'][0]['kind'] == 'quicktest_done' and b['new_moments'][0]['wrong'] == 1
    b = post('/_t/finished', {'score': 3, 'total': 3, 'attempt': 906, 'retry': True})
    assert b['new_moments'][0]['kind'] == 'retry_cleared'
    # personal best: against the pupil's own earlier attempts on the topic only
    with get_db() as conn:
        for score in (5, 6):
            conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at) "
                         "VALUES (?, ?, ?, ?, ?, 10, '[]', datetime('now'))", (uid, *TOPIC, score))
        conn.commit()
        conn.execute("INSERT INTO quiz_attempts (user_id, level, subject, topic, score, total, answers_json, created_at) "
                     "VALUES (?, ?, ?, ?, 7, 10, '[]', datetime('now'))", (uid, *TOPIC))
        conn.commit()
        assert gam.personal_best_quiz(conn, uid, *TOPIC, 7, 10) is True
        assert gam.personal_best_quiz(conn, uid, *TOPIC, 6, 10) is False
        assert gam.personal_best_quiz(conn, uid, *TOPIC, 10, 10) is False  # a perfect score has its own moment
    b = post('/_t/finished', {'score': 7, 'total': 10, 'attempt': 907})
    assert b['new_moments'][0]['kind'] == 'personal_best'
    b = post('/_t/finished', {'score': 6, 'total': 10, 'attempt': 908})
    assert b['new_moments'][0]['kind'] == 'quiz_done'
    # a signed-out visitor gets nothing noted
    anon = app.test_client()
    with app.test_request_context('/'):
        appmod._note_moment(1, {'type': 'toast', 'id': 'toast:x', 'kind': 'quiz_done'})
        assert not getattr(appmod.g, 'pb_new_moments', None)
    # set work: the real +1 and, on the last answer, the toast; one effort point really recorded
    xp0 = lifetime(uid)
    b = post('/_t/setwork/assigned')
    kinds = [(m['type'], m.get('kind')) for m in b['new_moments']]
    assert ('micro', 'xp') in kinds and ('toast', 'set_work_done') not in kinds, kinds
    pts = [m['points'] for m in b['new_moments'] if m.get('kind') == 'xp']
    assert pts == [gam.EFFORT_WEIGHTS['set_work_answered']] and lifetime(uid) - xp0 == pts[0]
    b = post('/_t/setwork/complete')
    assert ('toast', 'set_work_done') in [(m['type'], m.get('kind')) for m in b['new_moments']]
    # the Daily: a micro each time; seven answered days in a calendar week make a toast, once
    sunday = date(2026, 11, 1)
    week = [(sunday - timedelta(days=i)).isoformat() for i in range(7)]
    with get_db() as conn:
        for d in week[1:]:
            conn.execute("INSERT OR IGNORE INTO qotd_attempts (user_id, day_key, correct, answer, answered_at) VALUES (?, ?, 1, 'A', datetime('now'))", (uid, d))
        conn.commit()
    b = post('/_t/daily/' + week[0])
    assert [(m['type'], m.get('kind')) for m in b['new_moments']] == [('micro', 'daily')]   # six days recorded: no week yet
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO qotd_attempts (user_id, day_key, correct, answer, answered_at) VALUES (?, ?, 1, 'A', datetime('now'))", (uid, week[0]))
        conn.commit()
    b = post('/_t/daily/' + week[0])
    assert ('toast', 'daily_week') in [(m['type'], m.get('kind')) for m in b['new_moments']]
    # the challenge toast has its two call sites
    src = read('app.py')
    assert src.count("'kind': 'challenge_done'") == 2
    assert 'no win' not in read('static/js/moments.js')
    del anon


def test_streak_skip_toast():
    c, uid = make_client()
    h = {'Accept': 'application/json'}
    today = date.today()
    with get_db() as conn:
        gam.record_study_day(conn, uid, on_date=today - timedelta(days=3))     # a streak with a gap of one missed day below
        gam.record_study_day(conn, uid, on_date=today - timedelta(days=2))
        week = gam._iso_week_key(today)
        conn.execute('UPDATE user_streaks SET freeze_available = 1, freeze_week_key = ? WHERE user_id = ?', (week, uid))
        conn.commit()
    # now study today: yesterday was missed, the weekly skip covers it
    b = c.post('/_t/study', headers=h).get_json()
    kinds = [m.get('kind') for m in (b.get('new_moments') or [])]
    assert kinds == ['streak_skip'], (b, kinds)
    # studying again the same day uses nothing further
    b = c.post('/_t/study', headers=h).get_json()
    assert 'new_moments' not in b


# ---- queue order, wiring, honest XP, lazy loading ----
def test_queue_and_wiring():
    guide = read('static/js/guide.js')
    moments = read('static/js/moments.js')
    celebrate = read('static/js/celebrate.js')
    progress = read('static/js/lesson-progress.js')
    # 2026-11-10 E11 Phase 1: one beat, one sequence. Moments and badges wait for the beat timers and any open stage or dialog, then
    # go to moments.js together (the scene, the badges by tier, the level-up; three cards at most)
    assert 'isOpen || stageBusy() || badgeTimer || momentTimer' in guide and 'pendingRewards.some(isBig)' in guide
    assert 'r[0].play(batch, bigs)' in guide and "if (isBig(head) && momentAssets()) { runMoments(); return; }" in guide
    assert 'runMoments();' in guide.split('function afterClose()')[1][:200]
    # never while quiz questions are on screen
    assert '(isQuizRunner() && !isQuizResults())' in guide
    # stages in one batch: perfect, lesson, level; one sequence through the stage
    assert "m.type === 'perfect' ? 0 : (m.type === 'lesson_complete' ? 1 : 2)" in moments
    assert 'window.pbStage.play(items.map(function (it) { return it.scene; })' in moments
    # seen-state
    assert "'level:' + m.level" in moments and "g.rewardId(m)" in moments
    assert "'lesson:' + [spec.level, spec.subject, spec.topic].join(':')" in guide.replace('(\'lesson:\'', '\'lesson:\'') or "('lesson:' + [spec.level, spec.subject, spec.topic].join(':'))" in guide
    # lesson complete: every lesson, only on the live finish, no points float
    assert 'showXpFloat(null, 25)' not in celebrate and '25' not in celebrate.split('lessonComplete')[1][:400]
    # 2026-11-10 E11 Phase 0: the live call now also hands over the lesson badge that the last save earned
    assert 'live' in progress and 'maybeCelebrateAllComplete(steps, true, lessonBadge(data))' in progress and 'maybeCelebrateAllComplete(steps, false)' in progress
    assert "reward(Object.assign({ type: 'lesson_complete' }, info || {}))" in celebrate
    # delivery on every path
    assert 'handOver(data.new_moments)' in celebrate and "getElementById('pb-new-moments')" in celebrate
    assert 'pb-hint-shown' in celebrate and 'pb-answer-checked' in celebrate
    base = read('templates/base.html')
    assert 'id="pb-new-moments"' in base


def test_honest_xp():
    celebrate = read('static/js/celebrate.js')
    assert "typeof points === 'number' ? points : 10" not in celebrate and ': 0;' in celebrate
    assert "points > 0 ? '+' + points + ' XP' : ''" in celebrate
    # every XP number a pupil can see comes from a recorded value: the template line, the celebrate float (only when given a
    # number), the profile's totals (computed from events). No literal amounts are left in the scripts.
    for rel in ('static/js/celebrate.js', 'static/js/lesson-progress.js', 'static/js/site.js', 'static/js/moments.js'):
        text = read(rel)
        assert not re.search(r"[+]\s*\d+\s*XP", text), rel
        assert '+25' not in text
    for rel in ('templates/lesson_mcq_results.html', 'templates/quicktest_results.html', 'templates/qotd.html', 'templates/student_class_work_detail.html'):
        assert not re.search(r"[+]\s*\{\{[^}]*\*\s*\d+", read(rel)), rel
    # a plain check records no effort points, so the check responses carry no XP number either
    assert "'xp'" not in read('static/js/site.js')
    # the weights the copy relies on
    assert gam.EFFORT_WEIGHTS['question_generated'] == 1 and gam.EFFORT_WEIGHTS['quiz_completed'] == 3
    assert gam.EFFORT_WEIGHTS['lesson_step_completed'] == 2 and gam.EFFORT_WEIGHTS['set_work_answered'] == 1
    # a guest sees no XP line
    guest = app.test_client()
    assert 'quiz-results-xp' not in guest.get('/').get_data(as_text=True)


def test_lazy_loading():
    c, uid = make_client()
    guest = app.test_client()
    for client in (guest, c):
        for path in ('/', '/topics'):
            html = client.get(path).get_data(as_text=True)
            assert not re.search(r'<(script|link)[^>]+moments\.(js|css)', html), path
    html = c.get('/').get_data(as_text=True)
    island = re.search(r'id="pb-moment-assets">(.*?)</script>', html, re.S)
    assert island, 'the moment asset island is missing on a signed-in page'
    urls = json.loads(island.group(1))
    # 2026-11-10 E11 Phase 1: + settings (the link on the 'Full marks will show as a small card' card)
    assert set(urls) == {'js', 'css', 'props', 'profile', 'settings'} and 'moments.js' in urls['js'] and 'moments.css' in urls['css']
    assert c.get(urls['js']).status_code == 200 and c.get(urls['css']).status_code == 200
    sw = read('static/js/sw.js')
    assert 'moments.js' not in sw and 'moments.css' not in sw
    assert "pb-v125" in sw   # 2026-11-10: E11 Phase 2 bump (was pb-v124, Phase 1); 2026-11-10: E11 Phase 1 bump (was pb-v123, Phase 0); 2026-11-10: E11 Phase 0 bump (was pb-v122, lesson-quiz spotlight); 2026-11-08: E10 phase 8 bump (was pb-v119, review fixes); 2026-11-08: E10 phase 6b bump (was pb-v116, phase 6); 2026-11-08: E10 phase 6 bump (was pb-v115); 2026-11-08: E10 review fixes bump (was pb-v118)


# ---- E10 review fixes (2026-11-08) ----
def register_user(prefix='rv'):
    """A new pupil: (client signed in by session, user id, email, handle). The password is password123."""
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    email, handle = f'{prefix}_{s}@example.com', f'{prefix}_{s}'
    r = c.post('/api/v1/auth/register', json={'email': email, 'handle': handle, 'password': 'password123', 'age_confirm': True},
               headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid, email, handle


PENDING_KEYS = ('pb_ms', 'pb_mm', 'pb_qxp', 'pb_own')


def hold(c, uid, ms=('streak_7',), moment_id='toast:quiz:77'):
    """Put pending badges, a moment and the XP line in the browser's session as a finished quiz leaves them."""
    with c.session_transaction() as sess:
        sess['pb_ms'] = list(ms)
        sess['pb_mm'] = [{'type': 'toast', 'id': moment_id, 'kind': 'quiz_done', 'score': 3, 'total': 10, 'wrong': 7}]
        sess['pb_qxp'] = [77, 3]
        sess['pb_own'] = uid


def held(c):
    with c.session_transaction() as sess:
        return {k: sess[k] for k in PENDING_KEYS if k in sess}


def islands(html):
    m = re.search(r'id="pb-new-milestones">(.*?)</script>', html, re.S)
    return (json.loads(m.group(1)) if m else []), moments_of(html)


def web_login(c, email):
    html = c.get('/login').get_data(as_text=True)
    return c.post('/login', data={'csrf_token': csrf_of(html), 'email': email, 'password': 'password123'})


def web_logout(c):
    html = c.get('/profile').get_data(as_text=True)
    return c.post('/logout', data={'csrf_token': csrf_of(html)})


def test_review_pending_lists_belong_to_the_pupil():
    # fix 1: a shared browser must never show the next pupil the previous pupil's moments
    browser, a_id, a_email, _ = register_user()
    _, b_id, b_email, _ = register_user()
    seed_xp(a_id, 198)
    assert browser.post('/_t/effort-redirect/quiz_completed').status_code == 302      # a level-up waits in the session
    assert held(browser)['pb_own'] == a_id and 'pb_mm' in held(browser)
    hold(browser, a_id)
    # logout (web) clears everything
    assert web_logout(browser).status_code == 302
    assert held(browser) == {}, held(browser)
    # ... and so does a login, even when something was left behind
    hold(browser, a_id)
    with browser.session_transaction() as sess:
        sess.pop('_user_id', None)
    assert web_login(browser, b_email).status_code == 302
    assert held(browser) == {}
    ms, mm = islands(browser.get('/').get_data(as_text=True))
    assert ms == [] and mm == [], 'B must not see A\'s badge or score'
    # lists left under another pupil's name are dropped when read (an old cookie, a swapped session)
    hold(browser, a_id)
    page = browser.get('/profile').get_data(as_text=True)
    assert islands(page) == ([], []) and held(browser) == {}
    # lists with no owner mark at all are not trusted either
    with browser.session_transaction() as sess:
        sess['pb_ms'] = ['streak_7']
        sess['pb_mm'] = [{'type': 'toast', 'id': 'toast:quiz:5', 'kind': 'quiz_done', 'score': 1, 'total': 2, 'wrong': 1}]
    assert islands(browser.get('/profile').get_data(as_text=True)) == ([], [])
    # the owner still gets their own lists, once
    hold(browser, b_id, ms=('streak_3',), moment_id='toast:quiz:78')
    ms, mm = islands(browser.get('/profile').get_data(as_text=True))
    assert [m['key'] for m in ms] == ['streak_3'] and [m['id'] for m in mm] == ['toast:quiz:78']
    assert islands(browser.get('/profile').get_data(as_text=True)) == ([], [])
    # a new quiz score is written under its owner, and the XP line is read only by that owner
    hold(browser, a_id)
    web_logout(browser)
    web_login(browser, b_email)
    assert 'pb_qxp' not in held(browser)
    # the API paths clear too: register, login and logout
    for path, body, headers in (
        ('/api/v1/auth/login', {'email': a_email, 'password': 'password123'}, {}),
        ('/api/v1/auth/register', {'email': 'x_%s@example.com' % uuid.uuid4().hex[:6], 'handle': 'x_%s' % uuid.uuid4().hex[:6],
                                   'password': 'password123', 'age_confirm': True}, {}),
        ('/api/v1/auth/logout', {}, {}),
    ):
        hold(browser, b_id)
        browser.post(path, json=body, headers=dict(headers, Accept='application/json'))
        assert held(browser) == {}, path
    # a web registration on the same browser starts clean too
    anon = app.test_client()
    with anon.session_transaction() as sess:
        sess['pb_ms'] = ['streak_7']
        sess['pb_mm'] = [{'type': 'toast', 'id': 'toast:quiz:9', 'kind': 'quiz_done', 'score': 1, 'total': 2, 'wrong': 1}]
        sess['pb_qxp'] = [9, 3]
        sess['pb_own'] = a_id
    tag = uuid.uuid4().hex[:8]
    r = anon.post('/register', data={'csrf_token': csrf_of(anon.get('/register').get_data(as_text=True)), 'email': f'wr_{tag}@example.com',
                                     'handle': f'wr_{tag}', 'password': 'password123', 'confirm_password': 'password123', 'age_confirm': '1'})
    assert r.status_code == 302, r.get_data(as_text=True)[:300]
    assert held(anon) == {}
    # the lists carry their owner when written by the after_request hook
    c, uid = make_client()
    seed_xp(uid, 198)
    c.post('/_t/effort-redirect/quiz_completed')
    assert held(c)['pb_own'] == uid


def mixed_quiz_url():
    return '/lesson-quiz/eursc/science/measurement'


def right_free_answer(problem):
    """A typed answer the lesson quiz marks right for a free-response question (found by trying what the key suggests)."""
    from generators.shared.answer_checkers import check_answer
    from generators.shared.lesson_quiz import grade_lesson_quiz_problem
    raw = str(problem.get('correct_answer_raw'))
    candidates = [raw.split('~')[0], raw]
    try:
        candidates.append(str(check_answer(problem.get('answer_type') or 'number', raw, '').get('normalized_correct') or ''))
    except Exception:  # noqa: BLE001 - a candidate that cannot be built is simply not tried
        pass
    for guess in candidates:
        if guess and grade_lesson_quiz_problem(problem, guess)['correct']:
            return guess
    raise AssertionError(('no right answer found for', problem.get('answer_type'), raw))


def finish_mixed_quiz(c, uid, wrong):
    """Walk the one-question-at-a-time lesson quiz through /next. Returns the redirect target after the last question."""
    base = mixed_quiz_url()
    html = c.get(base, follow_redirects=True).get_data(as_text=True)
    assert 'data-quiz-runner' in html or 'lesson-quiz-question' in html or '/next' in html
    problems = quiz_problems(uid)
    loc = None
    for i, p in enumerate(problems):
        tok = csrf_of(c.get(base + '/question').get_data(as_text=True))
        if p.get('options'):
            right = p['correct_answer'].strip().upper()[:1]
            answer = next(ch for ch in 'ABCD' if ch != right) if i < wrong else right
        else:
            answer = 'definitely wrong' if i < wrong else right_free_answer(p)
        r = c.post(base + '/next', data={'csrf_token': tok, 'qt_user_answer': answer, 'qt_checked': '1'})
        assert r.status_code == 302
        loc = r.headers['Location']
    return loc, problems


def test_review_mixed_lesson_quiz_next_path_finishes_like_submit():
    # fix 4: the one-question-at-a-time path (47 of 91 lesson quizzes) used to finish with no moment, personal best or XP line
    c, uid = make_client()
    holds_full_marks(uid)
    xp0 = lifetime(uid)
    loc, problems = finish_mixed_quiz(c, uid, wrong=0)
    assert '/quiz-attempts/' in loc, loc
    from generators.shared.lesson_quiz import lesson_quiz_problems_are_mixed
    assert len(problems) >= 3 and lesson_quiz_problems_are_mixed(problems), 'this is a one-question-at-a-time quiz'
    assert held(c).get('pb_qxp') and held(c)['pb_own'] == uid, held(c)
    page = c.get(loc).get_data(as_text=True)
    ms = moments_of(page)
    assert [m['type'] for m in ms if m['type'] == 'perfect'] == ['perfect'], ms
    shown = re.search(r'quiz-results-xp">\+(\d+) XP earned', page)
    assert shown and int(shown.group(1)) == gam.EFFORT_WEIGHTS['quiz_completed'] == lifetime(uid) - xp0, (shown, xp0, lifetime(uid))
    again = c.get(loc).get_data(as_text=True)
    assert moments_of(again) == [] and 'quiz-results-xp' not in again, 'once'
    # not perfect: the toast with the Retry link, a personal best on the first run
    c2, uid2 = make_client()
    loc2, problems2 = finish_mixed_quiz(c2, uid2, wrong=2)
    page2 = c2.get(loc2).get_data(as_text=True)
    toasts = [m for m in moments_of(page2) if m['type'] == 'toast']
    assert toasts and toasts[0]['kind'] in ('quiz_done', 'personal_best') and toasts[0]['wrong'] == 2, toasts
    assert 'id="retry-wrong"' in page2 and 'quiz-results-xp' in page2


def test_review_quiz_question_fetches_keep_badges_for_results():
    # fix 3: a badge earned by a call made from a quiz question page is kept for the results page (the question page is quiet,
    # and the answer to the call used to carry it to nowhere)
    c, uid, _, _ = register_user('qq')
    today = gam._utc_today()
    with get_db() as conn:
        for i in range(6, 0, -1):
            gam.record_study_day(conn, uid, on_date=today - timedelta(days=i))   # six days: the next study day makes seven
    index = c.get('/').get_data(as_text=True)
    r = c.post('/quicktest/start', data={'csrf_token': csrf_of(index), 'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas',
                                         'mode': 'practice', 'difficulty': 'foundational'}, follow_redirects=True)
    question = r.get_data(as_text=True)
    assert 'data-guide-quiz="1"' in question and 'data-guide-quiz-results' not in question
    assert islands(question) == ([], []), 'the question page is quiet'
    # the first answer: a JSON call from the question page, flagged as such
    body = c.post('/_t/study', headers={'Accept': 'application/json', 'X-PB-Quiz': '1'}).get_json()
    assert 'new_milestones' not in body and 'new_moments' not in body, body
    assert 'streak_7' in held(c)['pb_ms']
    # an ordinary call (not from a question page) still carries them in the body
    c3, uid3, _, _ = register_user('qq')
    with get_db() as conn:
        for i in range(6, 0, -1):
            gam.record_study_day(conn, uid3, on_date=today - timedelta(days=i))
    plain = c3.post('/_t/study', headers={'Accept': 'application/json'}).get_json()
    assert 'streak_7' in [m['key'] for m in plain['new_milestones']]
    # the rest of the test: finish the Quick Test; the results page plays the badge
    for _ in range(40):
        tok = csrf_of(c.get('/quicktest').get_data(as_text=True)) if c.get('/quicktest').status_code == 200 else None
        if not tok:
            break
        nxt = c.post('/quicktest/next', data={'csrf_token': tok})
        if nxt.headers['Location'].endswith('/quicktest/results'):
            break
    results = c.get('/quicktest/results').get_data(as_text=True)
    assert 'data-guide-quiz-results="1"' in results
    ms, mm = islands(results)
    assert 'streak_7' in [m['key'] for m in ms], (ms, mm)
    assert [m for m in mm if m.get('kind') == 'quicktest_done'], mm
    assert islands(c.get('/profile').get_data(as_text=True)) == ([], []), 'once'
    celebrate = read('static/js/celebrate.js')
    assert "'X-PB-Quiz'" in celebrate and "data-guide-quiz-results" in celebrate and 'fromQuestionPage' in celebrate


def test_review_challenge_page_is_a_results_page_once_submitted():
    # fix 6: after submitting, the challenge toast plays on the challenge page, not on the next unrelated page
    h = {'Accept': 'application/json'}
    a, a_id, _, a_handle = register_user('ch')
    b, b_id, _, b_handle = register_user('ch')
    a.post(f'/api/v1/users/{b_handle}/follow', headers=h)
    b.post(f'/api/v1/users/{a_handle}/follow', headers=h)
    r = a.post('/api/v1/challenges', json={'opponent_handle': b_handle, 'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'}, headers=h)
    assert r.status_code == 201, r.data
    cid = r.get_json()['challenge']['id']
    before = a.get(f'/challenges/{cid}').get_data(as_text=True)
    assert 'data-guide-quiz="1"' in before and 'data-guide-quiz-results' not in before
    r = a.post(f'/challenges/{cid}', data={'csrf_token': csrf_of(before), 'action': 'submit', **{f'answer_{i}': 'A' for i in range(10)}})
    assert r.status_code == 302
    assert held(a)['pb_mm'][0]['id'] == f'toast:challenge:{cid}'
    page = a.get(f'/challenges/{cid}').get_data(as_text=True)
    assert 'data-guide-quiz-results="1"' in page, 'submitted: no questions left, so the page may celebrate'
    assert [m['id'] for m in moments_of(page)] == [f'toast:challenge:{cid}']
    assert moments_of(a.get('/topics').get_data(as_text=True)) == [], 'not on the next, unrelated page'
    # the other pupil has not submitted: their challenge page still holds back
    other = b.get(f'/challenges/{cid}').get_data(as_text=True)
    assert 'data-guide-quiz-results' not in other
    # the JSON route, called from a question page, keeps the toast for the challenge page
    a2, a2_id, _, a2_handle = register_user('ch')
    b2, b2_id, _, b2_handle = register_user('ch')
    a2.post(f'/api/v1/users/{b2_handle}/follow', headers=h)
    b2.post(f'/api/v1/users/{a2_handle}/follow', headers=h)
    cid2 = a2.post('/api/v1/challenges', json={'opponent_handle': b2_handle, 'level': 'gcse', 'subject': 'maths', 'topic': 'bidmas'},
                   headers=h).get_json()['challenge']['id']
    body = a2.post(f'/api/v1/challenges/{cid2}/submit', json={'answers': ['A'] * 10}, headers=dict(h, **{'X-PB-Quiz': '1'})).get_json()
    assert body['ok'] and 'new_moments' not in body
    page2 = a2.get(f'/challenges/{cid2}').get_data(as_text=True)
    assert [m['id'] for m in moments_of(page2)] == [f'toast:challenge:{cid2}']


def test_review_background_renders_leave_pending_lists_alone():
    # fix 7: only a page the pupil is looking at reads the pending lists (not /offline, an error page or a background fetch)
    c, uid, _, _ = register_user('bg')
    hold(c, uid)
    assert islands(c.get('/offline').get_data(as_text=True)) == ([], []) and 'pb_mm' in held(c), '/offline'
    r = c.get('/static/js/does-not-exist.js.map')
    assert r.status_code == 404 and b'pb-new-milestones' not in r.data and 'pb_mm' in held(c), 'static 404'
    r = c.get('/no-such-page-at-all')
    assert r.status_code == 404 and b'pb-new-moments' not in r.data and 'pb_mm' in held(c), 'page 404'
    for hdrs in ({'Service-Worker': 'script'}, {'Sec-Fetch-Dest': 'empty'}, {'Sec-Fetch-Mode': 'cors'}, {'Sec-Fetch-Dest': 'image'}):
        assert islands(c.get('/topics', headers=hdrs).get_data(as_text=True)) == ([], []) and 'pb_mm' in held(c), hdrs
    # a real navigation (browser headers, or none at all as the Flask test client sends) reads them, once
    ms, mm = islands(c.get('/topics', headers={'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate'}).get_data(as_text=True))
    assert [m['key'] for m in ms] == ['streak_7'] and [m['id'] for m in mm] == ['toast:quiz:77']
    assert 'pb_mm' not in held(c) and 'pb_ms' not in held(c)
    assert 'Sec-Fetch-Dest' in read('app.py').split('def _pending_may_emit')[1][:1500]


def test_e11_service_worker_navigation_reads_pending_lists():
    # E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.1): Chrome sends these exact headers for a page that sw.js relays
    # (every page after a pupil's first visit). They must count as a page view, or quiz results and redirects never celebrate.
    relayed = {'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'empty'}
    direct = {'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-User': '?1', 'Sec-Fetch-Dest': 'document'}
    for hdrs in (relayed, direct):
        c, uid, _, _ = register_user('sw')
        hold(c, uid)
        ms, mm = islands(c.get('/topics', headers=hdrs).get_data(as_text=True))
        assert [m['key'] for m in ms] == ['streak_7'] and [m['id'] for m in mm] == ['toast:quiz:77'], hdrs
        assert 'pb_ms' not in held(c) and 'pb_mm' not in held(c), hdrs
    # still background: a fetch (cors or no-cors, any Dest), a frame, the service worker's own script fetch
    c, uid, _, _ = register_user('sw')
    hold(c, uid)
    for hdrs in ({'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty'}, {'Sec-Fetch-Mode': 'no-cors', 'Sec-Fetch-Dest': 'empty'},
                 {'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'iframe'}, {'Sec-Fetch-Mode': 'same-origin', 'Sec-Fetch-Dest': 'document'},
                 {'Service-Worker': 'script', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Dest': 'empty'}):
        assert islands(c.get('/topics', headers=hdrs).get_data(as_text=True)) == ([], []) and 'pb_mm' in held(c), hdrs
    # the real quiz path under the service worker: submit, then the relayed results page plays the badge and Full marks
    c, uid = make_client()
    r = take_quiz(c, uid, wrong=0)
    page = c.get(r.headers['Location'], headers=relayed).get_data(as_text=True)
    ms, mm = islands(page)
    assert {'first_quiz', 'perfect_1'} <= {m['key'] for m in ms}, ms   # E11 Phase 1: a first 10/10 earns Full marks
    holds_full_marks(uid)
    r = take_quiz(c, uid, wrong=0)
    ms, mm = islands(c.get(r.headers['Location'], headers=relayed).get_data(as_text=True))
    assert [m['type'] for m in mm if m['type'] == 'perfect'] == ['perfect'], mm


def test_review_guide_js_stage_and_tour_offer():
    # fix 2 (the browser walk is in the review notes; here the wiring): moments in flight count as a stage until play settles,
    # and Esc on a stage is never the dialog's
    guide = read('static/js/guide.js')
    assert 'var momentsInFlight = 0;' in guide
    assert 'stagePending || momentsInFlight > 0 ||' in guide
    run = guide.split('function runMoments()')[1].split('function moments(list)')[0]
    assert 'momentsInFlight += 1;' in run and 'momentsInFlight -= 1;' in run and 'settled()' in run
    assert run.count('settled') >= 3, 'cleared on success and on failure'
    key = guide.split('function onKeydown(event)')[1][:260]
    assert 'window.pbStage.isOpen()' in key and key.index('pbStage.isOpen()') < key.index("'Escape'")


def main():
    tests = [
        test_caps_and_rules, test_copy_faces_scenes, test_level_up_detection_and_delivery, test_perfect_quiz_real_flow_and_honest_xp,
        test_imperfect_quiz_toast_retry_and_cleared, test_other_toasts_and_rules, test_streak_skip_toast, test_queue_and_wiring,
        test_honest_xp, test_lazy_loading,
        # 2026-11-08: E10 review fixes
        test_review_pending_lists_belong_to_the_pupil, test_review_mixed_lesson_quiz_next_path_finishes_like_submit,
        test_review_quiz_question_fetches_keep_badges_for_results, test_review_challenge_page_is_a_results_page_once_submitted,
        test_review_background_renders_leave_pending_lists_alone, test_review_guide_js_stage_and_tour_offer,
        # 2026-11-10: E11 Phase 0
        test_e11_service_worker_navigation_reads_pending_lists,
    ]
    for t in tests:
        t()
        print('ok', t.__name__)
    print('Celebration moments smoke (E10 phase 5) passed.')


if __name__ == '__main__':
    main()
