"""Moderation CLI + GDPR action log smoke — run: python scripts/test_s2_ops_smoke.py"""
import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ['PB_TESTING'] = '1'
os.environ['MAIL_PROVIDER'] = 'console'
os.environ['SITE_URL'] = 'http://127.0.0.1:5000'
os.environ.setdefault('SECRET_KEY', 'pb-testing')

from app import app, get_db  # noqa: E402
from models.gdpr_action_log import append_gdpr_action, log_path  # noqa: E402
from models.moderation import create_report, list_open_reports, resolve_report  # noqa: E402
from models.sharing import (  # noqa: E402
    create_shared_question,
    create_suggestion,
    operator_delete_shared_question,
    operator_dismiss_suggestion,
)
from models.user import User  # noqa: E402


def main():
    with tempfile.TemporaryDirectory() as raw:
        os.environ['PB_GDPR_ACTION_LOG'] = str(Path(raw) / 'gdpr_actions.log')
        append_gdpr_action('export', 'demo_handle', row_counts={'keys': 3})
        append_gdpr_action('erase', 'demo_handle', row_counts={'users': 1})
        lines = log_path().read_text(encoding='utf-8').strip().splitlines()
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert first['action'] == 'export'
        assert first['handle'] == 'demo_handle'
        assert '@' not in json.dumps(first)

    with app.app_context():
        suffix = uuid.uuid4().hex[:8]
        with get_db() as conn:
            a = User.create(conn, f's2a_{suffix}@example.com', f's2a_{suffix}', 'password123')
            b = User.create(conn, f's2b_{suffix}@example.com', f's2b_{suffix}', 'password123')
            report_id = create_report(
                conn, a.id, reported_user_id=b.id, report_type='spam', note='s2',
                context={'shared_question_id': 1},
            )
            open_rows = list_open_reports(conn)
            assert any(row['id'] == report_id for row in open_rows)
            assert resolve_report(conn, report_id) is True
            assert resolve_report(conn, report_id) is False
            assert all(row['id'] != report_id for row in list_open_reports(conn))

            share_id = create_shared_question(
                conn, a.id, 'gcse', 'maths', 'bidmas', 'standard', 'foundational',
                {'question': 'q', 'answer': '1'},
                visibility='private',
            )
            assert operator_delete_shared_question(conn, share_id) is True
            assert operator_delete_shared_question(conn, share_id) is False

            sug_id = create_suggestion(
                conn, a.id, b.id, 'gcse', 'maths', 'bidmas', 'standard', 'foundational',
                {'question': 'q', 'answer': '1'},
            )
            assert operator_dismiss_suggestion(conn, sug_id) is True

    print('S2 ops smoke tests passed.')


if __name__ == '__main__':
    main()
