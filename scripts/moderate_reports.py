"""Operator CLI: list and resolve user reports (S2.6).

Usage:
  python scripts/moderate_reports.py list
  python scripts/moderate_reports.py resolve --id N
  python scripts/moderate_reports.py hide-share --id N
  python scripts/moderate_reports.py dismiss-suggestion --id N
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import get_db  # noqa: E402
from models.moderation import list_open_reports, resolve_report  # noqa: E402
from models.sharing import operator_delete_shared_question, operator_dismiss_suggestion  # noqa: E402


def cmd_list(args):
    with get_db() as conn:
        rows = list_open_reports(conn, limit=args.limit)
    if not rows:
        print('No open reports.')
        return 0
    for row in rows:
        print(
            f"#{row['id']} {row['created_at']} {row['report_type']} "
            f"@{row['reporter_handle']} -> @{row['reported_handle'] or '—'} "
            f"note={row['note']!r} context={json.dumps(row['context'])}"
        )
    return 0


def cmd_resolve(args):
    with get_db() as conn:
        ok = resolve_report(conn, args.id)
    if not ok:
        print(f'No open report #{args.id}', file=sys.stderr)
        return 1
    print(f'Resolved report #{args.id}')
    return 0


def cmd_hide_share(args):
    with get_db() as conn:
        ok = operator_delete_shared_question(conn, args.id)
    if not ok:
        print(f'No shared question #{args.id}', file=sys.stderr)
        return 1
    print(f'Deleted shared question #{args.id}')
    return 0


def cmd_dismiss_suggestion(args):
    with get_db() as conn:
        ok = operator_dismiss_suggestion(conn, args.id)
    if not ok:
        print(f'No suggestion #{args.id}', file=sys.stderr)
        return 1
    print(f'Dismissed suggestion #{args.id}')
    return 0


def main():
    parser = argparse.ArgumentParser(description='Triage Problem Bank user reports.')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_list = sub.add_parser('list', help='Open reports, oldest first')
    p_list.add_argument('--limit', type=int, default=100)
    p_list.set_defaults(func=cmd_list)

    p_res = sub.add_parser('resolve', help='Mark a report resolved')
    p_res.add_argument('--id', type=int, required=True)
    p_res.set_defaults(func=cmd_resolve)

    p_share = sub.add_parser('hide-share', help='Delete a shared question by id')
    p_share.add_argument('--id', type=int, required=True)
    p_share.set_defaults(func=cmd_hide_share)

    p_sug = sub.add_parser('dismiss-suggestion', help='Dismiss a suggested question by id')
    p_sug.add_argument('--id', type=int, required=True)
    p_sug.set_defaults(func=cmd_dismiss_suggestion)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
