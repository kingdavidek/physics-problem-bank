"""E5.4 streak freeze smoke — run: python scripts/test_streak_freeze_smoke.py"""
import os
import re
import sys
import tempfile
import uuid
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
_smoke_dir = tempfile.mkdtemp(prefix='pb_streak_freeze_')
os.environ['PB_DB_PATH'] = str(Path(_smoke_dir) / 'smoke.db')

from app import app, get_db  # noqa: E402
from models.gamification import get_study_streak, record_study_day  # noqa: E402
from models.user import User  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle):
    r = client.get('/register')
    token = csrf_from(r.data.decode())
    client.post(
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


def study_days(conn, user_id):
    rows = conn.execute(
        'SELECT study_date FROM user_study_days WHERE user_id = ? ORDER BY study_date',
        (user_id,),
    ).fetchall()
    return [row['study_date'] for row in rows]


def freeze_dates(conn, user_id):
    rows = conn.execute(
        'SELECT freeze_date FROM user_streak_freezes WHERE user_id = ? ORDER BY freeze_date',
        (user_id,),
    ).fetchall()
    return [row['freeze_date'] for row in rows]


def main():
    d1 = date.fromisoformat('2026-08-18')  # Tuesday
    d3 = date.fromisoformat('2026-08-20')  # Thursday (one missed day: 2026-08-19)
    d5 = date.fromisoformat('2026-08-22')  # Saturday (second gap same week)
    d6 = date.fromisoformat('2026-08-23')  # Sunday (consecutive after reset)
    d8 = date.fromisoformat('2026-08-25')  # Monday next ISO week (one skip: 2026-08-24)

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle = f'sfz_{suffix}'
        register(client, f'{handle}@example.com', handle)
        r = client.get('/profile')
        assert r.status_code == 200
        assert 'skip available' in r.data.decode()
        with get_db() as conn:
            user = User.get_by_handle(conn, handle)
            assert user
            uid = user.id

            streak = record_study_day(conn, uid, on_date=d1)
            assert streak['current'] == 1
            assert streak['freeze_available'] == 1

            pending = get_study_streak(conn, uid, as_of=d3)
            assert pending['current'] == 1, 'display keeps streak while freeze can cover gap'
            assert pending['freeze_available'] == 1

            streak = record_study_day(conn, uid, on_date=d3)
            assert streak['current'] == 2
            assert streak['freeze_available'] == 0
            assert freeze_dates(conn, uid) == ['2026-08-19']
            assert study_days(conn, uid) == ['2026-08-18', '2026-08-20']
            assert '2026-08-19' not in study_days(conn, uid)

            streak = record_study_day(conn, uid, on_date=d5)
            assert streak['current'] == 1, 'second one-day gap in same week resets streak'
            assert streak['freeze_available'] == 0
            assert freeze_dates(conn, uid) == ['2026-08-19']

            streak = record_study_day(conn, uid, on_date=d6)
            assert streak['current'] == 2
            assert streak['freeze_available'] == 0

            streak = record_study_day(conn, uid, on_date=d8)
            assert streak['current'] == 3
            assert streak['freeze_available'] == 0, 'freeze regranted in new ISO week then consumed'
            assert freeze_dates(conn, uid) == ['2026-08-19', '2026-08-24']
            assert study_days(conn, uid) == [
                '2026-08-18',
                '2026-08-20',
                '2026-08-22',
                '2026-08-23',
                '2026-08-25',
            ]

            display = get_study_streak(conn, uid, as_of=d8)
            assert display['current'] == 3
            assert display['freeze_used_dates'] == ['2026-08-19', '2026-08-24']

        r = client.get('/api/v1/me/gamification')
        assert r.status_code == 200
        payload = r.get_json()
        assert 'freeze_available' in payload['study_streak']
        assert 'freeze_used_dates' in payload['study_streak']

    print('Streak freeze smoke tests passed.')


if __name__ == '__main__':
    main()
