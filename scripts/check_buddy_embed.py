"""Check buddy embed on functions lesson."""
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

db = ROOT / 'data' / 'quicktest.db'
if db.exists():
    os.environ['PB_DB_PATH'] = str(db)

from app import app, get_db  # noqa: E402
from models.user import User  # noqa: E402


def csrf(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert m
    return m.group(1)


with app.test_client() as c:
    r = c.get('/register')
    tok = csrf(r.data.decode())
    c.post(
        '/register',
        data={
            'csrf_token': tok,
            'email': 'chk@test.com',
            'handle': 'chk_buddy',
            'password': 'password123',
            'confirm_password': 'password123',
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    with get_db() as conn:
        uid = User.get_by_handle(conn, 'chk_buddy').id
        old = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        conn.execute('DELETE FROM quiz_attempts WHERE user_id = ?', (uid,))
        conn.execute(
            '''
            INSERT INTO quiz_attempts (
                user_id, level, subject, topic, score, total,
                answers_json, problems_json, created_at
            ) VALUES (?, 'gcse', 'maths', 'functions', 1, 10, '[]', '[]', ?)
            ''',
            (uid, old),
        )
        conn.commit()

    with c.session_transaction() as sess:
        print('session user?', sess.get('_user_id'))

    r = c.get('/topic/gcse/maths/functions')
    h = r.data.decode()
    print('status', r.status_code)
    print('view_args test via embed marker', 'pb-buddy-embed-v2' in h)
    print('study-buddy.js?v=2', 'study-buddy.js?v=2' in h)
    print('old buddy.js tag', '/js/buddy.js' in h)
    print('Practise MCQ', 'Practise MCQ' in h)
    print('Practise this', 'Practise this' in h)
    m = re.search(r'data-buddy-message[^>]*>([^<]*)', h)
    print('server message', m.group(1) if m else None)
