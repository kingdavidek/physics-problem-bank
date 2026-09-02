"""Daily retention prune. Usage: python scripts/prune_expired_data.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import get_db  # noqa: E402
from models.retention import prune_expired_data  # noqa: E402


def main():
    with get_db() as conn:
        counts = prune_expired_data(conn)
    print(json.dumps(counts, indent=2, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
