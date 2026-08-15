"""System bot account and daily QOTD challenge card (engagement E1.2)."""
import secrets

from models.qotd import current_day_key, get_daily_question, get_user_attempt
from models.user import User

BOT_HANDLE = 'problem_bot'
BOT_EMAIL = 'problem_bot@internal.problembank'
BOT_PROMPT = 'The Problem Bank bot challenges you!'
BOT_PROMPT_DONE = "You took today's Problem Bank bot challenge."


def is_bot_handle(handle):
    value = (handle or '').strip().lower()
    if value.startswith('@'):
        value = value[1:]
    return value == BOT_HANDLE


def is_bot_user(user):
    if user is None:
        return False
    return is_bot_handle(getattr(user, 'handle', '')) or (
        (getattr(user, 'email', '') or '').strip().lower() == BOT_EMAIL
    )


def ensure_system_bot(conn):
    """Idempotent seed of the non-human QOTD bot. Unguessable password; no extra PII."""
    existing = User.get_by_handle(conn, BOT_HANDLE)
    if existing:
        return existing
    existing_email = User.get_by_email(conn, BOT_EMAIL)
    if existing_email:
        return existing_email
    return User.create(conn, BOT_EMAIL, BOT_HANDLE, secrets.token_urlsafe(32))


def qotd_challenge_card(conn, viewer_id, *, day_key=None):
    """One synthetic feed card for today's QOTD. Not stored as an activity event."""
    day_key = day_key or current_day_key()
    try:
        daily = get_daily_question(day_key=day_key)
    except ValueError:
        return None
    ensure_system_bot(conn)
    attempt = get_user_attempt(conn, viewer_id, day_key) if viewer_id else None
    answered = bool(attempt)
    topic_name = daily.get('topic_name') or 'today’s question'
    return {
        'id': f'qotd-{day_key}',
        'type': 'qotd_challenge',
        'card_type': 'challenge',
        'card_label': 'Daily challenge',
        'actor_handle': BOT_HANDLE,
        'actor_url': f'/u/{BOT_HANDLE}',
        'message': BOT_PROMPT_DONE if answered else BOT_PROMPT,
        'detail': topic_name,
        'url': '/qotd',
        'created_at': f'{day_key}T00:00:00+00:00',
        'is_bot': True,
        'answered': answered,
        'day_key': day_key,
        'topic_label': topic_name,
        'bot_note': 'A Problem Bank bot — not a person.',
    }
