"""Operator CLI: export a user by handle. Usage:
  python scripts/gdpr_export_user.py --handle NAME [--out FILE]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import get_db  # noqa: E402
from models.data_export import build_user_export  # noqa: E402
from models.gdpr_action_log import append_gdpr_action  # noqa: E402
from models.user import User, normalize_handle  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='Export a Problem Bank account (GDPR Art 15/20).')
    parser.add_argument('--handle', required=True)
    parser.add_argument('--out', help='Write JSON to this path (default: stdout)')
    args = parser.parse_args()
    handle = normalize_handle(args.handle)
    with get_db() as conn:
        user = User.get_by_handle(conn, handle)
        if not user:
            print(f'No user @{handle}', file=sys.stderr)
            return 1
        payload = build_user_export(conn, user.id)
    append_gdpr_action('export', handle, row_counts={'keys': len(payload)})
    text = json.dumps(payload, indent=2, default=str)
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print(f'Wrote {args.out}')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
