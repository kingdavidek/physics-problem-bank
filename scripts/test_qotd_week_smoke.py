"""E5.3 QOTD week leaderboard smoke — run: python scripts/test_qotd_week_smoke.py"""
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.qotd import friend_qotd_week_leaderboard, qotd_window_day_keys  # noqa: E402
from models.social import follow_user  # noqa: E402
from models.user import User, utc_now_iso  # noqa: E402


def register(client, email, handle):
    r = client.get('/register')
    import re
    m = re.search(r'name="csrf_token" value="([^"]+)"', r.data.decode())
    token = m.group(1)
    r = client.post(
        '/register',
        data={
            'csrf_token': token,
            'email': email,
            'handle': handle,
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user
        return user.id


def seed_attempt(user_id, day_key, *, correct=True, answered_at=None):
    answered_at = answered_at or utc_now_iso()
    with get_db() as conn:
        conn.execute(
            '''
            INSERT OR REPLACE INTO qotd_attempts (user_id, day_key, correct, answer, answered_at)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (user_id, day_key, 1 if correct else 0, 'A', answered_at),
        )
        conn.commit()


def main():
    end_day = date.today().isoformat()
    window = qotd_window_day_keys(days=7, end_day=end_day)
    assert len(window) == 7
    assert window[-1] == end_day
    outside_day = (date.fromisoformat(end_day) - timedelta(days=7)).isoformat()
    assert outside_day not in window

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'qwka_{suffix}'
        handle_b = f'qwkb_{suffix}'
        register(client, f'{handle_a}@example.com', handle_a)
        uid_a = user_id_for(handle_a)

        logout = client.get('/profile')
        import re
        client.post(
            '/logout',
            data={'csrf_token': re.search(r'name="csrf_token" value="([^"]+)"', logout.data.decode()).group(1)},
            follow_redirects=True,
        )
        register(client, f'{handle_b}@example.com', handle_b)
        uid_b = user_id_for(handle_b)

        with get_db() as conn:
            follow_user(conn, uid_a, uid_b)
            follow_user(conn, uid_b, uid_a)

        for index, day_key in enumerate(window):
            seed_attempt(uid_a, day_key, correct=index % 2 == 0, answered_at=f'{day_key}T12:00:00')
        for day_key in window:
            seed_attempt(uid_b, day_key, correct=True, answered_at=f'{day_key}T10:00:00')
        seed_attempt(uid_a, outside_day, correct=True, answered_at=f'{outside_day}T12:00:00')
        seed_attempt(uid_b, outside_day, correct=True, answered_at=f'{outside_day}T10:00:00')

        with get_db() as conn:
            board = friend_qotd_week_leaderboard(conn, uid_a, days=7, end_day=end_day)
        assert len(board) == 2
        by_handle = {item['handle']: item for item in board}
        assert by_handle[handle_b]['rank'] == 1
        assert by_handle[handle_b]['correct_days'] == 7
        assert by_handle[handle_b]['answered_days'] == 7
        assert by_handle[handle_b]['days_in_window'] == 7
        assert by_handle[handle_a]['rank'] == 2
        assert by_handle[handle_a]['correct_days'] == 4
        assert by_handle[handle_a]['answered_days'] == 7

        client.patch(
            '/api/v1/me/settings',
            json={'show_accuracy_leaderboard': False},
        )
        logout = client.get('/profile')
        client.post(
            '/logout',
            data={'csrf_token': re.search(r'name="csrf_token" value="([^"]+)"', logout.data.decode()).group(1)},
            follow_redirects=True,
        )
        login = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': re.search(r'name="csrf_token" value="([^"]+)"', login.data.decode()).group(1),
                'email': f'{handle_a}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )

        r = client.get(f'/api/v1/qotd/week/leaderboard?end_day={end_day}&days=7')
        assert r.status_code == 200
        payload = r.get_json()
        assert payload['ok'] is True
        assert payload['day_keys'] == window
        handles = [item['handle'] for item in payload['leaderboard']]
        assert handle_a in handles
        assert handle_b not in handles

        logout = client.get('/profile')
        client.post(
            '/logout',
            data={'csrf_token': re.search(r'name="csrf_token" value="([^"]+)"', logout.data.decode()).group(1)},
            follow_redirects=True,
        )
        login = client.get('/login')
        client.post(
            '/login',
            data={
                'csrf_token': re.search(r'name="csrf_token" value="([^"]+)"', login.data.decode()).group(1),
                'email': f'{handle_b}@example.com',
                'password': 'password123',
            },
            follow_redirects=True,
        )

        r = client.get(f'/api/v1/qotd/week/leaderboard?end_day={end_day}&days=7')
        handles = [item['handle'] for item in r.get_json()['leaderboard']]
        assert handle_b in handles
        assert handle_a in handles

        r = client.get('/qotd?board=week')
        assert r.status_code == 200
        html = r.data.decode()
        assert 'This week' in html
        assert 'days answered' in html
        assert f'@{handle_b}' in html

        r = client.get('/api/v1/me/gamification')
        assert r.status_code == 200
        week_board = r.get_json()['qotd_week_leaderboard']
        assert week_board
        assert week_board[0]['handle'] == handle_b
        assert week_board[0]['correct_days'] == 7

    print('QOTD week leaderboard smoke tests passed.')


if __name__ == '__main__':
    main()
