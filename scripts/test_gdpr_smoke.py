"""GDPR / S0 smoke test — run: python scripts/test_gdpr_smoke.py"""
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-gdpr-smoke')

from app import app, get_db  # noqa: E402
from models.account_deletion import (  # noqa: E402
    DELETED_HANDLE_LABEL,
    delete_user_account,
    handle_is_reserved,
    remaining_user_rows,
)
from models.auth_tokens import (  # noqa: E402
    consume_password_reset_token,
    create_password_reset_token,
    peek_password_reset_token,
)
from models.data_export import build_user_export  # noqa: E402
from models.notifications import create_notification  # noqa: E402
from models.privacy import hashed_ip  # noqa: E402
from models.reflections import save_reflection  # noqa: E402
from models.retention import prune_expired_data  # noqa: E402
from models.social import follow_user, record_activity_event  # noqa: E402
from models.user import User, mark_email_verified, validate_handle  # noqa: E402
from models.user_data import record_quiz_attempt, save_problem  # noqa: E402


def csrf_from(html: str) -> str:
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    assert m, 'csrf token not found'
    return m.group(1)


def register(client, email, handle, password='password123'):
    r = client.get('/register')
    assert r.status_code == 200
    token = csrf_from(r.data.decode())
    r = client.post(
        '/register',
        data={
            'csrf_token': token,
            'email': email,
            'handle': handle,
            'password': password,
            'confirm_password': password,
            'age_confirm': '1',
        },
        follow_redirects=True,
    )
    assert r.status_code == 200, r.data[:500]
    return r


def logout(client):
    html = client.get('/').data.decode()
    client.post('/logout', data={'csrf_token': csrf_from(html)}, follow_redirects=True)


def login(client, email, password='password123'):
    r = client.get('/login')
    client.post(
        '/login',
        data={
            'csrf_token': csrf_from(r.data.decode()),
            'email': email,
            'password': password,
        },
        follow_redirects=True,
    )


def user_id_for(handle):
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        assert user, handle
        return user.id


def main():
    digest = hashed_ip('secret', '203.0.113.9')
    assert len(digest) == 16
    assert digest != hashed_ip('secret', '203.0.113.10')
    assert '.' not in digest

    with app.test_client() as client:
        suffix = uuid.uuid4().hex[:8]
        handle_a = f'gda_{suffix}'
        handle_b = f'gdb_{suffix}'
        email_a = f'gda_{suffix}@example.com'
        email_b = f'gdb_{suffix}@example.com'

        for path in ('/privacy', '/privacy/simple', '/terms'):
            r = client.get(path)
            assert r.status_code == 200, path
            html = r.data.decode().lower()
            assert 'privacy' in html or 'terms' in html

        r = client.get('/register')
        html = r.data.decode()
        assert '/privacy' in html
        assert '/terms' in html
        assert 'By creating an account you agree' in html

        register(client, email_a, handle_a)
        uid_a = user_id_for(handle_a)

        r = client.post(
            '/',
            data={
                'level': 'gcse',
                'subject': 'maths',
                'topic': 'bidmas',
                'mode': 'standard',
                'difficulty': 'foundational',
                'action': 'start',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200

        logout(client)
        r = client.get(f'/u/{handle_a}')
        assert r.status_code == 200
        page = r.data.decode()
        assert 'profile is private' in page.lower()
        assert handle_a in page
        assert 'Last topic opened' not in page
        assert email_a not in page

        register(client, email_b, handle_b)
        uid_b = user_id_for(handle_b)
        logout(client)

        with get_db() as conn:
            mark_email_verified(conn, uid_a)
            mark_email_verified(conn, uid_b)
            save_problem(
                conn, uid_a, 'gcse', 'maths', 'bidmas', 'standard', 'foundational',
                {'question': 'What is 2+2?', 'answer': '4'},
            )
            record_quiz_attempt(
                conn, uid_a, 'gcse', 'maths', 'bidmas', 3, 5,
                [{'correct': True}], [{'question': 'q'}],
            )
            save_reflection(
                conn, uid_a, 'gcse', 'maths', 'bidmas',
                source='check', prompt_type='guessed',
                reflection_text='I guessed the order of operations.',
            )
            follow_user(conn, uid_b, uid_a)
            create_notification(
                conn, uid_b, 'new_follower',
                {'handle': handle_a, 'from_handle': handle_a},
            )
            record_activity_event(
                conn, uid_b, 'suggestion_sent',
                {'handle': handle_a, 'topic': 'bidmas'},
            )
            conn.execute(
                '''
                INSERT INTO user_reports (
                    reporter_id, reported_user_id, report_type, note, created_at
                ) VALUES (?, ?, 'other', 'smoke', ?)
                ''',
                (uid_b, uid_a, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

            payload = build_user_export(conn, uid_a)
            dump = json.dumps(payload, default=str)
            assert payload['account']['handle'] == handle_a
            assert payload['account']['email'] == email_a
            assert 'password_hash' not in dump
            assert email_b not in dump
            practice = payload['practice']
            assert practice['saved_problems']
            assert practice['quiz_attempts']
            assert any(
                'guessed the order' in (row.get('reflection_text') or '')
                for row in practice['user_wrong_answer_reflections']
            )
            assert all('email' not in row for row in payload['social']['followers'])

        login(client, email_a)
        r = client.get('/me/export')
        assert r.status_code == 200, r.data[:400]
        exported = json.loads(r.data.decode())
        assert exported['account']['handle'] == handle_a
        assert 'password_hash' not in json.dumps(exported)

        r = client.get('/api/v1/me/export', headers={'Accept': 'application/json'})
        assert r.status_code == 200
        assert r.get_json()['ok'] is True

        logout(client)
        with get_db() as conn:
            counts = delete_user_account(conn, uid_a)
            assert counts.get('ok') is True
            leftover = remaining_user_rows(conn, uid_a)
            nonzero = {table: n for table, n in leftover.items() if n}
            assert not nonzero, nonzero
            assert handle_is_reserved(conn, handle_a)
            assert validate_handle(handle_a, conn)
            note = conn.execute(
                'SELECT payload_json FROM user_notifications WHERE user_id = ?',
                (uid_b,),
            ).fetchone()['payload_json']
            assert DELETED_HANDLE_LABEL in note
            assert handle_a.lower() not in note.lower()
            event = conn.execute(
                'SELECT payload_json FROM user_activity_events WHERE user_id = ?',
                (uid_b,),
            ).fetchone()['payload_json']
            assert DELETED_HANDLE_LABEL in event
            assert handle_a.lower() not in event.lower()
            report = conn.execute(
                'SELECT reported_user_id FROM user_reports WHERE reporter_id = ?',
                (uid_b,),
            ).fetchone()
            assert report['reported_user_id'] is None

        r = client.get('/register')
        token = csrf_from(r.data.decode())
        r = client.post(
            '/register',
            data={
                'csrf_token': token,
                'email': f'gda_new_{suffix}@example.com',
                'handle': handle_a,
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
        )
        assert r.status_code == 200
        assert b'reserved' in r.data.lower() or b'choose another' in r.data.lower()

        with get_db() as conn:
            user_b = User.get_by_id(conn, uid_b)
            raw_ok = create_password_reset_token(conn, uid_b)
            assert peek_password_reset_token(conn, raw_ok)
            consumed = consume_password_reset_token(conn, raw_ok)
            assert consumed == uid_b
            assert consume_password_reset_token(conn, raw_ok) is None

            raw_expired = create_password_reset_token(conn, uid_b)
            past = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            conn.execute(
                'UPDATE password_reset_tokens SET expires_at = ? WHERE token_hash = ?',
                (past, hashlib.sha256(raw_expired.encode()).hexdigest()),
            )
            conn.commit()
            assert peek_password_reset_token(conn, raw_expired) is False
            assert consume_password_reset_token(conn, raw_expired) is None

            raw_invalidated = create_password_reset_token(conn, uid_b)
            user_b.set_password(conn, 'password123')
            assert peek_password_reset_token(conn, raw_invalidated) is False
            assert consume_password_reset_token(conn, raw_invalidated) is None

            raw_happy = create_password_reset_token(conn, uid_b)

        r = client.get(f'/reset-password/{raw_happy}')
        assert r.status_code == 200
        r = client.post(
            f'/reset-password/{raw_happy}',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'password': 'newpass123',
                'confirm_password': 'newpass123',
            },
            follow_redirects=True,
        )
        assert r.status_code == 200
        login(client, email_b, 'newpass123')
        r = client.get('/profile')
        assert r.status_code == 200
        assert handle_b.encode() in r.data
        logout(client)

        r = client.get('/forgot-password')
        assert r.status_code == 200
        r = client.post(
            '/forgot-password',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': 'nobody-not-an-account@example.com',
            },
        )
        assert b'If that email is on an account' in r.data

        now = datetime.now(timezone.utc)
        old_day = (now - timedelta(days=40)).date().isoformat()
        today = now.date().isoformat()
        old_iso = (now - timedelta(days=400)).isoformat()
        with get_db() as conn:
            conn.execute(
                '''
                INSERT OR REPLACE INTO rate_limit_buckets
                    (bucket_key, window_start, count, updated_at)
                VALUES (?, ?, 1, ?), (?, ?, 1, ?)
                ''',
                ('export:ip:deadbeef', old_day, old_iso, 'export:ip:alivebeef', today, now.isoformat()),
            )
            conn.execute(
                '''
                INSERT OR REPLACE INTO lesson_assist_usage (day, client_key, count)
                VALUES (?, 'ip:old', 1), (?, 'ip:new', 1)
                ''',
                (old_day, today),
            )
            conn.execute(
                '''
                INSERT INTO email_digest_log (user_id, week_key, status, sent_at)
                VALUES (?, 'old-week', 'sent', ?), (?, 'new-week', 'sent', ?)
                ''',
                (uid_b, old_iso, uid_b, now.isoformat()),
            )
            conn.execute(
                '''
                INSERT OR REPLACE INTO deleted_handles (handle, deleted_at)
                VALUES (?, ?), (?, ?)
                ''',
                ('oldgone_handle', old_iso, f'keep_{suffix}', now.isoformat()),
            )
            conn.commit()
            prune_expired_data(conn, now=now, delete_inactive=False)
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM rate_limit_buckets WHERE bucket_key = 'export:ip:deadbeef'"
            ).fetchone()['n'] == 0
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM rate_limit_buckets WHERE bucket_key = 'export:ip:alivebeef'"
            ).fetchone()['n'] == 1
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM lesson_assist_usage WHERE client_key = 'ip:old'"
            ).fetchone()['n'] == 0
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM lesson_assist_usage WHERE client_key = 'ip:new'"
            ).fetchone()['n'] == 1
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM email_digest_log WHERE week_key = 'old-week'"
            ).fetchone()['n'] == 0
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM email_digest_log WHERE week_key = 'new-week'"
            ).fetchone()['n'] == 1
            assert conn.execute(
                "SELECT COUNT(*) AS n FROM deleted_handles WHERE handle = 'oldgone_handle'"
            ).fetchone()['n'] == 0
            assert conn.execute(
                'SELECT COUNT(*) AS n FROM deleted_handles WHERE handle = ?',
                (f'keep_{suffix}',),
            ).fetchone()['n'] == 1

    print('GDPR / S0 smoke tests passed.')


if __name__ == '__main__':
    main()
