"""Send weekly digest batch — run: python scripts/send_weekly_digest.py [--dry-run] [--handle USER]"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db, _topic_label  # noqa: E402
from models.email_digest import (  # noqa: E402
    DIGEST_STATUS_DRY_RUN,
    DIGEST_STATUS_FAILED,
    DIGEST_STATUS_SENT,
    DIGEST_STATUS_SKIPPED,
    list_digest_subscribers,
    mail_config,
    send_weekly_digest_to_user,
)
from models.user import User  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Send weekly recap emails to opted-in users')
    parser.add_argument('--dry-run', action='store_true', help='Print/send via console provider without real delivery')
    parser.add_argument('--handle', help='Send to one user only (must be opted in unless --force-handle)')
    parser.add_argument(
        '--force-handle',
        action='store_true',
        help='With --handle, send even if not subscribed (for admin testing)',
    )
    args = parser.parse_args()

    cfg = mail_config()
    dry_run = args.dry_run or cfg['provider'] == 'console'

    if not dry_run and not cfg['enabled']:
        print('MAIL_ENABLED is not set. Use --dry-run or configure mail (see docs/EMAIL_SETUP.md).', file=sys.stderr)
        sys.exit(1)

    if not cfg['site_url']:
        print('Warning: SITE_URL is not set — unsubscribe links may be incomplete.', file=sys.stderr)

    counts = {DIGEST_STATUS_SENT: 0, DIGEST_STATUS_DRY_RUN: 0, DIGEST_STATUS_SKIPPED: 0, DIGEST_STATUS_FAILED: 0, 'already_sent': 0}

    with app.app_context():
        with get_db() as conn:
            if args.handle:
                row = conn.execute(
                    'SELECT * FROM users WHERE handle = ? COLLATE NOCASE',
                    (args.handle.lstrip('@'),),
                ).fetchone()
                user = User.from_row(row)
                if not user:
                    print(f'User not found: {args.handle}', file=sys.stderr)
                    sys.exit(1)
                if not args.force_handle:
                    subs = {s['id'] for s in list_digest_subscribers(conn)}
                    if user.id not in subs:
                        print('User has not opted in to weekly digest.', file=sys.stderr)
                        sys.exit(1)
                targets = [user]
            else:
                rows = list_digest_subscribers(conn)
                targets = []
                for row in rows:
                    targets.append(User.from_row(conn.execute('SELECT * FROM users WHERE id = ?', (row['id'],)).fetchone()))

            for user in targets:
                status, err = send_weekly_digest_to_user(
                    conn,
                    user,
                    dry_run=dry_run,
                    topic_label_fn=_topic_label,
                )
                counts[status] = counts.get(status, 0) + 1
                label = f'@{user.handle} <{user.email}>'
                if status == DIGEST_STATUS_FAILED:
                    print(f'FAIL {label}: {err}')
                elif status == 'already_sent':
                    print(f'SKIP {label}: already sent this week')
                else:
                    print(f'{status.upper()} {label}')

    print(
        f"Done — sent: {counts.get(DIGEST_STATUS_SENT, 0) + counts.get(DIGEST_STATUS_DRY_RUN, 0)}, "
        f"skipped (no activity): {counts.get(DIGEST_STATUS_SKIPPED, 0)}, "
        f"failed: {counts.get(DIGEST_STATUS_FAILED, 0)}, "
        f"already_sent: {counts.get('already_sent', 0)}"
    )
    if counts.get(DIGEST_STATUS_FAILED, 0):
        sys.exit(1)


if __name__ == '__main__':
    main()
