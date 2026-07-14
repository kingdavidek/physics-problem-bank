"""Weekly study recap email — build, send, log, and unsubscribe."""
import hashlib
import hmac
import json
import os
import smtplib
import ssl
import urllib.error
import urllib.request
from datetime import date, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from models.gamification import get_study_streak, get_weekly_recap
from models.user import utc_now_iso

DIGEST_STATUS_SENT = 'sent'
DIGEST_STATUS_SKIPPED = 'skipped_no_activity'
DIGEST_STATUS_FAILED = 'failed'
DIGEST_STATUS_DRY_RUN = 'dry_run'


def mail_config():
    return {
        'enabled': os.environ.get('MAIL_ENABLED', '').strip() in ('1', 'true', 'yes'),
        'provider': (os.environ.get('MAIL_PROVIDER') or 'console').strip().lower(),
        'from_email': (os.environ.get('MAIL_FROM_EMAIL') or '').strip(),
        'from_name': (os.environ.get('MAIL_FROM_NAME') or 'Problem Bank').strip(),
        'site_url': (os.environ.get('SITE_URL') or '').strip().rstrip('/'),
        'resend_api_key': os.environ.get('RESEND_API_KEY', '').strip(),
        'sendgrid_api_key': os.environ.get('SENDGRID_API_KEY', '').strip(),
        'smtp_host': os.environ.get('SMTP_HOST', '').strip(),
        'smtp_port': int(os.environ.get('SMTP_PORT', '587') or '587'),
        'smtp_user': os.environ.get('SMTP_USER', '').strip(),
        'smtp_password': os.environ.get('SMTP_PASSWORD', '').strip(),
        'smtp_use_tls': os.environ.get('SMTP_USE_TLS', '1').strip() not in ('0', 'false', 'no'),
        'skip_inactive': os.environ.get('EMAIL_DIGEST_SKIP_INACTIVE', '1').strip() not in (
            '0',
            'false',
            'no',
        ),
    }


def current_week_key(today=None):
    """ISO date of the Monday starting the current calendar week."""
    day = today or date.today()
    monday = day - timedelta(days=day.weekday())
    return monday.isoformat()


def make_unsubscribe_token(user_id, secret):
    uid = str(int(user_id))
    sig = hmac.new(secret.encode('utf-8'), uid.encode('utf-8'), hashlib.sha256).hexdigest()[:32]
    return f'{uid}.{sig}'


def verify_unsubscribe_token(token, secret):
    if not token or not secret:
        return None
    parts = token.split('.', 1)
    if len(parts) != 2:
        return None
    uid, sig = parts
    if not uid.isdigit():
        return None
    expected = hmac.new(secret.encode('utf-8'), uid.encode('utf-8'), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        return None
    return int(uid)


def build_weekly_digest_payload(conn, user, *, site_url=None, topic_label_fn=None):
    """Assemble recap data for one user (no sending)."""
    cfg = mail_config()
    base = (site_url or cfg['site_url'] or '').rstrip('/')
    recap = get_weekly_recap(conn, user.id)
    streak = get_study_streak(conn, user.id)

    best_quiz = recap.get('best_quiz')
    if best_quiz and topic_label_fn:
        best_quiz = dict(best_quiz)
        best_quiz['topic_label'] = topic_label_fn(
            best_quiz.get('level'),
            best_quiz.get('subject'),
            best_quiz.get('topic'),
        )

    secret = os.environ.get('SECRET_KEY', '')
    unsubscribe_token = make_unsubscribe_token(user.id, secret) if secret else ''
    unsubscribe_url = f'{base}/email/unsubscribe?token={unsubscribe_token}' if base else ''

    return {
        'user_id': user.id,
        'handle': user.handle,
        'email': user.email,
        'week_key': current_week_key(),
        'site_url': base,
        'profile_url': f'{base}/profile' if base else '/profile',
        'settings_url': f'{base}/profile/settings' if base else '/profile/settings',
        'unsubscribe_url': unsubscribe_url,
        'recap': recap,
        'study_streak': streak,
        'best_quiz': best_quiz,
    }


def render_digest_subject(payload):
    active = payload['recap'].get('active_days', 0)
    if active:
        return f'Your week on Problem Bank — {active} active day{"s" if active != 1 else ""}'
    return 'Your weekly Problem Bank recap'


def render_digest_text(payload):
    recap = payload['recap']
    streak = payload.get('study_streak') or {}
    lines = [
        f"Hi @{payload['handle']},",
        '',
        'Here is your weekly study recap:',
        '',
        f"Active days: {recap.get('active_days', 0)} / {recap.get('days', 7)}",
        f"Topics practised: {recap.get('topics_practised', 0)}",
        f"Practice activities: {recap.get('activity_count', 0)}",
    ]
    current = streak.get('current_streak', 0)
    if current:
        lines.append(f"Study streak: {current} day{'s' if current != 1 else ''} (best: {streak.get('longest_streak', 0)})")

    best = payload.get('best_quiz')
    if best:
        label = best.get('topic_label') or best.get('topic', 'a topic')
        lines.append(f"Best quiz: {best['score']}/{best['total']} on {label}")

    lines.extend([
        '',
        f"Continue practising: {payload['profile_url']}",
        '',
        '— Problem Bank',
    ])
    if payload.get('unsubscribe_url'):
        lines.extend(['', f"Unsubscribe from weekly emails: {payload['unsubscribe_url']}"])
    return '\n'.join(lines)


def render_digest_html(payload):
    recap = payload['recap']
    streak = payload.get('study_streak') or {}
    best = payload.get('best_quiz')
    best_html = ''
    if best:
        label = best.get('topic_label') or best.get('topic', 'a topic')
        best_html = (
            f'<p><strong>Best quiz:</strong> {best["score"]}/{best["total"]} '
            f'on {label}</p>'
        )
    streak_html = ''
    current = streak.get('current_streak', 0)
    if current:
        streak_html = (
            f'<p><strong>Study streak:</strong> {current} day'
            f'{"s" if current != 1 else ""} '
            f'(personal best: {streak.get("longest_streak", 0)})</p>'
        )
    unsub = ''
    if payload.get('unsubscribe_url'):
        unsub = (
            f'<p style="font-size:12px;color:#666;margin-top:24px;">'
            f'<a href="{payload["unsubscribe_url"]}">Unsubscribe</a> from weekly recap emails '
            f'or change this in <a href="{payload["settings_url"]}">Settings</a>.</p>'
        )
    return f'''<!DOCTYPE html>
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#222;max-width:560px;">
  <h1 style="font-size:1.25rem;color:#1a6fa8;">Your week on Problem Bank</h1>
  <p>Hi @{payload['handle']},</p>
  <p>Summary for the last {recap.get('days', 7)} days:</p>
  <ul>
    <li><strong>Active days:</strong> {recap.get('active_days', 0)}</li>
    <li><strong>Topics practised:</strong> {recap.get('topics_practised', 0)}</li>
    <li><strong>Practice activities:</strong> {recap.get('activity_count', 0)}</li>
  </ul>
  {streak_html}
  {best_html}
  <p><a href="{payload['profile_url']}" style="color:#1a6fa8;">Open your profile →</a></p>
  {unsub}
</body></html>'''


def list_digest_subscribers(conn):
    rows = conn.execute(
        '''
        SELECT u.id, u.email, u.handle
        FROM users u
        JOIN user_profile_settings s ON s.user_id = u.id
        WHERE u.is_active = 1
          AND s.email_weekly_digest = 1
        ORDER BY u.id
        '''
    ).fetchall()
    return [dict(row) for row in rows]


def digest_already_sent(conn, user_id, week_key):
    row = conn.execute(
        '''
        SELECT id FROM email_digest_log
        WHERE user_id = ? AND week_key = ? AND status IN (?, ?)
        ''',
        (user_id, week_key, DIGEST_STATUS_SENT, DIGEST_STATUS_DRY_RUN),
    ).fetchone()
    return row is not None


def log_digest_send(conn, user_id, week_key, status, error_message=''):
    conn.execute(
        '''
        INSERT INTO email_digest_log (user_id, week_key, status, error_message, sent_at)
        VALUES (?, ?, ?, ?, ?)
        ''',
        (user_id, week_key, status, (error_message or '')[:500], utc_now_iso()),
    )
    conn.commit()


def _from_header(cfg):
    if cfg['from_name'] and cfg['from_email']:
        return f'{cfg["from_name"]} <{cfg["from_email"]}>'
    return cfg['from_email'] or 'noreply@example.com'


def send_email_message(to_email, subject, html_body, text_body):
    """Send one message. Returns (ok, error_message)."""
    cfg = mail_config()
    provider = cfg['provider']

    if provider == 'console':
        print('--- EMAIL (console provider) ---')
        print(f'To: {to_email}')
        print(f'Subject: {subject}')
        print(text_body)
        print('--- end ---')
        return True, ''

    if not cfg['enabled']:
        return False, 'MAIL_ENABLED is not set'

    if not cfg['from_email']:
        return False, 'MAIL_FROM_EMAIL is not set'

    if provider == 'resend':
        return _send_via_resend(cfg, to_email, subject, html_body, text_body)
    if provider == 'sendgrid':
        return _send_via_sendgrid(cfg, to_email, subject, html_body, text_body)
    if provider == 'smtp':
        return _send_via_smtp(cfg, to_email, subject, html_body, text_body)
    return False, f'Unknown MAIL_PROVIDER: {provider}'


def _send_via_resend(cfg, to_email, subject, html_body, text_body):
    if not cfg['resend_api_key']:
        return False, 'RESEND_API_KEY is not set'
    payload = {
        'from': _from_header(cfg),
        'to': [to_email],
        'subject': subject,
        'html': html_body,
        'text': text_body,
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.resend.com/emails',
        data=data,
        headers={
            'Authorization': f'Bearer {cfg["resend_api_key"]}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if 200 <= resp.status < 300:
                return True, ''
            return False, f'Resend HTTP {resp.status}'
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')[:300]
        return False, f'Resend HTTP {exc.code}: {body}'
    except urllib.error.URLError as exc:
        return False, str(exc.reason)


def _send_via_sendgrid(cfg, to_email, subject, html_body, text_body):
    if not cfg['sendgrid_api_key']:
        return False, 'SENDGRID_API_KEY is not set'
    payload = {
        'personalizations': [{'to': [{'email': to_email}]}],
        'from': {'email': cfg['from_email'], 'name': cfg['from_name']},
        'subject': subject,
        'content': [
            {'type': 'text/plain', 'value': text_body},
            {'type': 'text/html', 'value': html_body},
        ],
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.sendgrid.com/v3/mail/send',
        data=data,
        headers={
            'Authorization': f'Bearer {cfg["sendgrid_api_key"]}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if 200 <= resp.status < 300:
                return True, ''
            return False, f'SendGrid HTTP {resp.status}'
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')[:300]
        return False, f'SendGrid HTTP {exc.code}: {body}'
    except urllib.error.URLError as exc:
        return False, str(exc.reason)


def _send_via_smtp(cfg, to_email, subject, html_body, text_body):
    if not cfg['smtp_host']:
        return False, 'SMTP_HOST is not set'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = _from_header(cfg)
    msg['To'] = to_email
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    try:
        if cfg['smtp_use_tls']:
            context = ssl.create_default_context()
            with smtplib.SMTP(cfg['smtp_host'], cfg['smtp_port'], timeout=30) as smtp:
                smtp.starttls(context=context)
                if cfg['smtp_user']:
                    smtp.login(cfg['smtp_user'], cfg['smtp_password'])
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(cfg['smtp_host'], cfg['smtp_port'], timeout=30) as smtp:
                if cfg['smtp_user']:
                    smtp.login(cfg['smtp_user'], cfg['smtp_password'])
                smtp.send_message(msg)
        return True, ''
    except (OSError, smtplib.SMTPException) as exc:
        return False, str(exc)


def send_weekly_digest_to_user(conn, user, *, dry_run=False, topic_label_fn=None):
    """
    Build and send (or dry-run) one user's digest.
    Returns (status, error_message).
    """
    cfg = mail_config()
    payload = build_weekly_digest_payload(conn, user, topic_label_fn=topic_label_fn)
    week_key = payload['week_key']

    if digest_already_sent(conn, user.id, week_key):
        return 'already_sent', ''

    if cfg['skip_inactive'] and payload['recap'].get('active_days', 0) == 0:
        log_digest_send(conn, user.id, week_key, DIGEST_STATUS_SKIPPED)
        return DIGEST_STATUS_SKIPPED, ''

    subject = render_digest_subject(payload)
    html_body = render_digest_html(payload)
    text_body = render_digest_text(payload)

    if dry_run:
        send_email_message(user.email, subject, html_body, text_body)
        log_digest_send(conn, user.id, week_key, DIGEST_STATUS_DRY_RUN)
        return DIGEST_STATUS_DRY_RUN, ''

    ok, err = send_email_message(user.email, subject, html_body, text_body)
    if ok:
        log_digest_send(conn, user.id, week_key, DIGEST_STATUS_SENT)
        return DIGEST_STATUS_SENT, ''
    log_digest_send(conn, user.id, week_key, DIGEST_STATUS_FAILED, err)
    return DIGEST_STATUS_FAILED, err


def send_test_weekly_digest(conn, user, *, topic_label_fn=None):
    """Send one preview digest to the user (no dedup, no log). Returns (ok, error_message)."""
    payload = build_weekly_digest_payload(conn, user, topic_label_fn=topic_label_fn)
    subject = f'[Test] {render_digest_subject(payload)}'
    html_body = render_digest_html(payload)
    text_body = render_digest_text(payload)
    return send_email_message(user.email, subject, html_body, text_body)


def disable_weekly_digest(conn, user_id):
    from models.social import ensure_user_profile

    ensure_user_profile(conn, user_id)
    conn.execute(
        'UPDATE user_profile_settings SET email_weekly_digest = 0 WHERE user_id = ?',
        (user_id,),
    )
    conn.commit()
