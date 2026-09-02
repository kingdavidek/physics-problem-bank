"""Operator CLI: erase a user by handle. Usage:
  python scripts/gdpr_erase_user.py --handle NAME [--confirm]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import get_db  # noqa: E402
from models.account_deletion import delete_user_account  # noqa: E402
from models.gdpr_action_log import append_gdpr_action  # noqa: E402
from models.user import User, normalize_handle  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Erase a Problem Bank account (GDPR Art 17).')
    parser.add_argument('--handle', required=True)
    parser.add_argument('--confirm', action='store_true', help='Required to actually delete')
    args = parser.parse_args()
    handle = normalize_handle(args.handle)
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        if not user:
            print(f'No user @{handle}', file=sys.stderr)
            return 1
        if not args.confirm:
            print(f'Would delete @{handle} (id={user.id}). Re-run with --confirm.')
            return 0
        counts = delete_user_account(conn, user.id)
    append_gdpr_action('erase', handle, row_counts=counts)
    print(counts)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
