"""Preview weekly digest for one user — run: python scripts/preview_weekly_digest.py --handle USER"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault('MAIL_PROVIDER', 'console')
os.environ.setdefault('SITE_URL', 'http://127.0.0.1:5000')

from app import app, get_db, _topic_label  # noqa: E402
from models.email_digest import build_weekly_digest_payload, render_digest_html, render_digest_text  # noqa: E402
from models.user import User  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Preview weekly digest email content')
    parser.add_argument('--handle', required=True, help='User handle (without @)')
    parser.add_argument('--format', choices=('text', 'html', 'both'), default='both')
    args = parser.parse_args()

    with app.app_context():
        with get_db() as conn:
            row = conn.execute(
                'SELECT * FROM users WHERE handle = ? COLLATE NOCASE',
                (args.handle.lstrip('@'),),
            ).fetchone()
            user = User.from_row(row)
            if not user:
                print(f'User not found: {args.handle}', file=sys.stderr)
                sys.exit(1)
            payload = build_weekly_digest_payload(conn, user, topic_label_fn=_topic_label)

    if args.format in ('text', 'both'):
        print('=== TEXT ===')
        print(render_digest_text(payload))
        print()
    if args.format in ('html', 'both'):
        print('=== HTML ===')
        print(render_digest_html(payload))


if __name__ == '__main__':
    main()
