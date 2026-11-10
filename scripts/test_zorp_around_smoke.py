"""E10 phase 7 smoke: Zorp around the site (empty states, 404 and 500, results faces and ring, waiting hook, lookAt, Daily week strip,
profile ribbon and ring), lazy loading and caps. Run: python scripts/test_zorp_around_smoke.py"""
import os
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ['PB_TESTING'] = '1'

from app import app, get_db  # noqa: E402
from models import qotd as qotd_model  # noqa: E402
from models import zorp_rig  # noqa: E402

# Own caps (bytes), 2026-11-08: E10 phase 7. Both files are on demand and not precached.
CAPS = {'static/js/zorp-around.js': 8600, 'static/css/around.css': 4000}


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def login():
    c = app.test_client()
    s = uuid.uuid4().hex[:8]
    r = c.post('/api/v1/auth/register', json={'email': f'ar_{s}@example.com', 'handle': f'ar_{s}', 'password': 'password123', 'age_confirm': True},
               headers={'Accept': 'application/json'})
    assert r.status_code == 201, r.data
    uid = r.get_json()['user']['id']
    with c.session_transaction() as sess:
        sess['_user_id'] = str(uid)
        sess['_fresh'] = True
    return c, uid, f'ar_{s}'


def test_caps_and_rules():
    for rel, cap in CAPS.items():
        n = len((ROOT / rel).read_bytes())
        print(f'  {rel}: {n} of {cap} B')
        assert n <= cap, (rel, n)
    js, css = read('static/js/zorp-around.js'), read('static/css/around.css')
    for bad in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'eval(', 'document.write', 'lottie', 'gsap', 'http://', 'https://'):
        assert bad not in js, bad
    # keyframes move transform and opacity only
    for body in re.findall(r'@keyframes [\w-]+ \{(.*?)\n?\}\s*(?=\n|$)', css, re.S):
        props = set(re.findall(r'([a-z-]+)\s*:', body))
        assert props <= {'transform', 'opacity'}, props
    assert 'scale' in css and 'rotate' in css
    # only positive or neutral faces can be drawn, and lookAt is gated on full motion
    assert "var FACES = { joy: 1, determined: 1, 'soft-smile': 1, nudge: 1 }" in js
    assert 'target && full()' in js and "aria-busy" in js and '}, 400)' in js


def test_faces_by_band():
    tpl = app.jinja_env.get_template('partials/around.html').module
    allowed = set(zorp_rig.CONTEXT_MAP['around.results'])
    got = {}
    with app.test_request_context('/'):
        for score, total, want in ((10, 10, 'joy'), (8, 10, 'joy'), (7, 10, 'determined'), (5, 10, 'determined'), (4, 10, 'soft-smile'), (0, 10, 'soft-smile')):
            html = str(tpl.results_zorp(score, total))
            face = re.search(r'data-around-face="([^"]+)"', html).group(1)
            assert face == want, (score, total, face)
            assert face in allowed and zorp_rig.VALENCE[face] != zorp_rig.NEGATIVE
            assert 'data-zorp-voice="zorp:guide_line"' in html
            got[face] = re.search(r'<p[^>]*>(.*?)</p>', html).group(1)
        assert str(tpl.results_zorp(0, 0)).strip() == ''
    assert 'again' in got['soft-smile'] and all(len(t) <= 100 for t in got.values())
    for name in allowed:
        assert zorp_rig.VALENCE[name] != zorp_rig.NEGATIVE, name


def test_empty_states_and_errors():
    c, uid, handle = login()
    pages = {'/saved-problems': 'peek', f'/u/{handle}/following': 'wave', '/leaderboard/friends?board=accuracy': 'wave',
             '/leaderboard/friends?board=effort': 'wave'}
    assert "data-zorp-autoplay=\"wave\"" in read('templates/qotd.html')   # the Daily board only shows it once friends exist
    for path, clip in pages.items():
        html = c.get(path).data.decode()
        m = re.search(r'<span class="study-buddy-face pb-zorp-small"[^>]*data-zorp-autoplay="([a-z-]+)"[^>]*>\s*<svg class="buddy-mascot"', html)
        assert m, path
        assert m.group(1) == clip and clip in zorp_rig.AUTOPLAY_CLIPS, (path, m.group(1))
        assert 'data-pose=' in html.split('class="empty-state')[1]
    saved = c.get('/saved-problems').data.decode()
    assert 'around-box-front' in saved and 'css/around.css' in saved
    assert 'press Follow' in c.get(f'/u/{handle}/following').data.decode()
    prof = c.get('/profile').data.decode()
    assert prof.count('around-empty') >= 1 and 'data-pose="sit"' in prof, 'quiz history sits'
    assert 'Your quiz scores will appear here' in prof
    assert 'zorp-around.js' in prof and 'css/around.css' in prof
    # the revision plan empty state is in the template with a think-chin pose
    tpl = read('templates/profile.html')
    assert "pose='think-chin'" in tpl and 'Nothing to schedule yet' in tpl
    # 404 and 500
    r = c.get('/no-such-page-here')
    html = r.data.decode()
    assert r.status_code == 404 and 'This page drifted off into the maths belt.' in html and 'data-pose="shrug"' in html and 'Go home' in html
    guest = app.test_client().get('/no-such-page-here')
    assert guest.status_code == 404 and 'data-pose="shrug"' in guest.data.decode()
    assert app.test_client().get('/api/v1/no-such').status_code == 404
    s500 = read('templates/errors/500.html')
    assert "pose='shrug'" in s500 and 'on our side' in s500
    for tpl_name in ('errors/404.html', 'errors/500.html', 'saved_problems.html', 'follow_list.html', 'leaderboard_friends.html', 'qotd.html', 'profile.html'):
        for pose_face in re.findall(r"buddy_mascot\(face='([a-z-]+)'", read('templates/' + tpl_name)):
            assert pose_face in zorp_rig.CONTEXT_MAP['around.empty'], (tpl_name, pose_face)


def test_results_pages_wiring():
    for rel in ('templates/lesson_mcq_results.html', 'templates/quicktest_results.html'):
        t = read(rel)
        assert 'data-around-ring' in t and 'results_zorp' in t and 'css/around.css' in t and 'zorp-around.js' in t, rel
    assert 'conic-gradient(var(--correct-300)' in read('static/css/pages.css'), 'ring colour token must exist'
    assert '@media (scripting: enabled)' in read('static/css/around.css')


def test_waiting_hooks_and_lazy_loading():
    for rel in ('static/js/lesson-assist.js', 'static/js/quiz-assist.js'):
        assert "window.pbAround[on ? 'wait' : 'done'](body)" in read(rel), rel
    base = read('templates/base.html')
    assert base.count("filename='js/zorp-around.js'") == 1 and 'lesson_assist_enabled and lesson_meta' in base
    c, uid, handle = login()
    assert 'zorp-around.js' not in c.get('/saved-problems').data.decode()
    assert 'zorp-around.js' not in app.test_client().get('/login').data.decode()
    assert 'zorp-around.js' not in read('static/js/sw.js') and 'around.css' not in read('static/js/sw.js'), 'not precached'


def test_daily_strip_and_ribbon():
    c, uid, handle = login()
    with get_db() as conn:
        dots = qotd_model.viewer_week_dots(conn, uid)
    assert len(dots) == 7 and dots[-1]['is_today'] and all(d['state'] == 'missed' for d in dots)
    html = c.get('/qotd').data.decode()
    assert 'qotd-week-dots' in html and 'is-pop' not in html
    with get_db() as conn:
        conn.execute("INSERT INTO qotd_attempts (user_id, day_key, correct, answer, answered_at) VALUES (?, ?, 1, 'A', datetime('now'))", (uid, qotd_model.current_day_key()))
        conn.commit()
    with c.session_transaction() as sess:
        sess['qotd_pop'] = qotd_model.current_day_key()
    html = c.get('/qotd').data.decode()
    assert re.search(r'streak-dot is-studied is-today is-pop', html), 'today pops once after an answer'
    assert 'is-pop' not in c.get('/qotd').data.decode(), 'only once'
    # ribbon: a badge earned now is new, one from 30 days ago is not
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'first_lesson_step', datetime('now'))", (uid,))
        conn.execute("INSERT OR IGNORE INTO user_milestones (user_id, milestone_key, earned_at) VALUES (?, 'questions_25', datetime('now', '-30 days'))", (uid,))
        conn.commit()
    prof = c.get('/profile').data.decode()
    assert prof.count('badge-new-ribbon') == 1


def test_autoplay_and_voice_wiring():
    for rel in ('saved_problems', 'follow_list', 'leaderboard_friends', 'qotd', 'errors/404'):
        for clip in re.findall(r'data-zorp-autoplay="([^"{]+)"', read(f'templates/{rel}.html')):
            assert clip in zorp_rig.AUTOPLAY_CLIPS, (rel, clip)
    assert 'around.results' in zorp_rig.CONTEXT_MAP


def main():
    for t in (test_caps_and_rules, test_faces_by_band, test_empty_states_and_errors, test_results_pages_wiring,
              test_waiting_hooks_and_lazy_loading, test_daily_strip_and_ribbon, test_autoplay_and_voice_wiring):
        t()
    print('Zorp around the site smoke (E10 phase 7) passed.')


if __name__ == '__main__':
    main()
