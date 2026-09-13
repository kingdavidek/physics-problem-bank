"""S3 cadence checks — weekly backups, monthly reports, quarterly restore drill.

Usage:
  python scripts/ops_cadence.py weekly
  python scripts/ops_cadence.py monthly
  python scripts/ops_cadence.py restore-drill
  python scripts/ops_cadence.py feature-gate

Never restores onto the live database. Scratch default: data/restore-scratch.db
(gitignored). Full calendar: docs/CADENCE.md
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

from backup_sqlite import MAGIC, passphrase, restore_backup_file  # noqa: E402

FEATURE_QUESTIONS = (
    'Does it collect a new category of personal data? If yes, update the ROPA, privacy notice, and retention schedule in the same PR.',
    'Does it make anything about a child more visible to anyone else? If yes, it defaults to off.',
    'Does it send data to a new third party? If yes, subprocessor entry and transfer basis before it ships.',
    'Does it profile, rank, or nudge? If yes, revisit the DPIA section on Children\'s Code standard 13.',
)

STALE_HOURS_DEFAULT = 192  # 8 days — weekly backup with a little slack


def _backup_dir() -> Path:
    return Path(os.environ.get('PB_BACKUP_DIR') or (ROOT / 'data' / 'backups'))


def _live_db_paths() -> set[Path]:
    override = (os.environ.get('PB_DB_PATH') or '').strip()
    paths = {ROOT / 'data' / 'quicktest.db'}
    if override:
        paths.add(Path(override))
    return {p.resolve() for p in paths}


def _list_backups(backup_dir: Path) -> list[Path]:
    files = list(backup_dir.glob('quicktest-*.db')) + list(backup_dir.glob('quicktest-*.db.enc'))
    return sorted(files, key=lambda p: p.name, reverse=True)


def _file_age_hours(path: Path, *, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return (now - mtime).total_seconds() / 3600.0


def _emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, default=str))
        return
    kind = payload.get('kind', 'cadence')
    print(f'cadence: {kind}')
    for key, value in payload.items():
        if key == 'kind':
            continue
        if key == 'questions' and isinstance(value, (list, tuple)):
            for i, q in enumerate(value, 1):
                print(f'  {i}. {q}')
            continue
        print(f'  {key}: {value}')


def _log(kind: str, summary: dict) -> None:
    from models.cadence_log import append_cadence

    append_cadence(kind, summary=summary)


def cmd_weekly(args) -> int:
    backup_dir = Path(args.backup_dir) if args.backup_dir else _backup_dir()
    backups = _list_backups(backup_dir) if backup_dir.is_dir() else []
    newest = backups[0] if backups else None
    age = _file_age_hours(newest) if newest else None
    stale_hours = args.stale_hours
    ok = newest is not None and age is not None and age <= stale_hours
    payload = {
        'kind': 'weekly',
        'backup_dir': str(backup_dir),
        'backup_count': len(backups),
        'newest_backup': str(newest) if newest else None,
        'age_hours': round(age, 1) if age is not None else None,
        'stale_hours': stale_hours,
        'backup_ok': ok,
        'dependabot': 'Review open Dependabot PRs (weekly pip + github-actions).',
        'pip_audit': 'GitHub Actions: smoke.yml on PR; cadence.yml Monday 09:00 UTC.',
        'prune': 'On the host: python scripts/prune_expired_data.py (daily cron after launch).',
    }
    _log('weekly', {
        'backup_ok': ok,
        'backup_count': len(backups),
        'age_hours': payload['age_hours'],
    })
    _emit(payload, args.json)
    if args.strict and not ok:
        return 1
    return 0


def cmd_monthly(args) -> int:
    os.environ.setdefault('PB_TESTING', os.environ.get('PB_TESTING', '0'))
    from app import get_db
    from models.moderation import list_open_reports

    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        open_reports = list_open_reports(conn, limit=500)
        try:
            locked = conn.execute(
                '''
                SELECT COUNT(*) AS n FROM login_lockouts
                WHERE locked_until IS NOT NULL AND locked_until > ?
                ''',
                (now,),
            ).fetchone()
            spraying = conn.execute(
                'SELECT COUNT(*) AS n FROM login_lockouts WHERE fail_count >= 5'
            ).fetchone()
            locked_n = int(locked['n'] if locked else 0)
            spray_n = int(spraying['n'] if spraying else 0)
        except sqlite3.OperationalError:
            locked_n = 0
            spray_n = 0

    payload = {
        'kind': 'monthly',
        'open_reports': len(open_reports),
        'lockouts_active': locked_n,
        'lockouts_fail_count_ge_5': spray_n,
        'next': 'python scripts/moderate_reports.py list  (docs/MODERATION.md)',
    }
    _log('monthly', {
        'open_reports': len(open_reports),
        'lockouts_active': locked_n,
        'lockouts_fail_count_ge_5': spray_n,
    })
    _emit(payload, args.json)
    return 0


def _scratch_summary(db_path: Path) -> dict:
    conn = sqlite3.connect(str(db_path))
    try:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        users = None
        if 'users' in tables:
            users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        return {'table_count': len(tables), 'users': users, 'readable': True}
    finally:
        conn.close()


def cmd_restore_drill(args) -> int:
    backup_dir = Path(args.backup_dir) if args.backup_dir else _backup_dir()
    src = Path(args.src) if args.src else None
    if src is None:
        backups = _list_backups(backup_dir)
        if not backups:
            print(f'No backups in {backup_dir}', file=sys.stderr)
            return 1
        src = backups[0]
    if not src.is_file():
        print(f'Backup not found: {src}', file=sys.stderr)
        return 1

    dest = Path(args.dest) if args.dest else (ROOT / 'data' / 'restore-scratch.db')
    dest_resolved = dest.resolve()
    if dest_resolved in _live_db_paths():
        print('Refusing to restore onto the live database. Pick a scratch --to path.', file=sys.stderr)
        return 1
    if dest_resolved.parent.resolve() == _backup_dir().resolve() and args.dest:
        print('Refusing to write a restore into the backup directory.', file=sys.stderr)
        return 1

    pass_text = (args.passphrase or passphrase()).strip()
    blob_head = src.read_bytes()[:6]
    if blob_head == MAGIC and not pass_text:
        print('Encrypted backup requires PB_BACKUP_PASSPHRASE or --passphrase.', file=sys.stderr)
        return 1

    dest.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ('', '-wal', '-shm'):
        leftover = Path(str(dest) + suffix) if suffix else dest
        leftover.unlink(missing_ok=True)

    restore_backup_file(src, dest, pass_text)
    summary = _scratch_summary(dest)
    payload = {
        'kind': 'restore_drill',
        'from': str(src),
        'to': str(dest),
        'encrypted': blob_head == MAGIC,
        **summary,
        'next': 'Re-read templates/legal_privacy.html against the code; review docs/SUBPROCESSORS.md; set Last reviewed in docs/DPIA.md.',
    }
    _log('restore_drill', {
        'from': src.name,
        'table_count': summary['table_count'],
        'users': summary['users'],
    })
    _emit(payload, args.json)
    return 0


def cmd_feature_gate(args) -> int:
    payload = {
        'kind': 'feature_gate',
        'source': 'docs/SECURITY_AND_GDPR.md §6.1',
        'questions': list(FEATURE_QUESTIONS),
    }
    _emit(payload, args.json)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Problem Bank S3 cadence checks.')
    parser.add_argument('--json', action='store_true', help='Machine-readable output')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_w = sub.add_parser('weekly', help='Backup freshness + Dependabot / pip-audit reminders')
    p_w.add_argument('--backup-dir', default='')
    p_w.add_argument('--stale-hours', type=float, default=STALE_HOURS_DEFAULT)
    p_w.add_argument('--strict', action='store_true', help='Exit 1 if no fresh backup')
    p_w.set_defaults(func=cmd_weekly)

    p_m = sub.add_parser('monthly', help='Open reports + login lockout counts')
    p_m.set_defaults(func=cmd_monthly)

    p_r = sub.add_parser('restore-drill', help='Restore newest backup to a scratch DB')
    p_r.add_argument('--from', dest='src', default='', help='Backup file (default: newest)')
    p_r.add_argument('--to', dest='dest', default='', help='Scratch DB (default: data/restore-scratch.db)')
    p_r.add_argument('--backup-dir', default='')
    p_r.add_argument('--passphrase', default='')
    p_r.set_defaults(func=cmd_restore_drill)

    p_f = sub.add_parser('feature-gate', help='Print the four questions before a new feature')
    p_f.set_defaults(func=cmd_feature_gate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())
