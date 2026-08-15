"""E1.1 lesson-assist smoke — run: python scripts/test_lesson_assist_smoke.py

CI / default: LESSON_ASSIST_MOCK=1 (no paid API). Optional live path:
set LESSON_ASSIST_LIVE_SMOKE=1 with a real LESSON_ASSIST_API_KEY locally.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

if os.environ.get('LESSON_ASSIST_LIVE_SMOKE', '').strip() not in ('1', 'true', 'yes', 'on'):
    os.environ['LESSON_ASSIST_MOCK'] = '1'

from app import app  # noqa: E402


VALID_PAYLOAD = {
    'selection': {
        'text': 'BIDMAS means Brackets, Indices, Division, Multiplication, Addition, Subtraction.',
        'surrounding': 'Use BIDMAS to decide the order of operations.',
        'charCount': 80,
    },
    'context': {
        'level': 'gcse',
        'subject': 'maths',
        'topic': 'bidmas',
        'topicTitle': 'BIDMAS',
        'sectionTitle': 'Order of operations',
        'pageUrl': '/topics/gcse/maths/bidmas',
        'nearMcq': False,
    },
    'question': 'Explain this as if I am in Year 7.',
    'locale': 'en-GB',
}


def main():
    with app.test_client() as client:
        r = client.post('/api/lesson/explain', json=VALID_PAYLOAD)
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True, data
        assert data.get('explanation'), data
        meta = data.get('meta') or {}
        assert 'remainingToday' in meta

        r = client.post(
            '/api/lesson/explain',
            json={
                'selection': {'text': 'short'},
                'context': {
                    'level': 'gcse',
                    'subject': 'maths',
                    'topic': 'bidmas',
                    'topicTitle': 'BIDMAS',
                },
            },
        )
        assert r.status_code == 400, r.data
        err = r.get_json()
        assert err['ok'] is False
        assert err['error']['code'] == 'invalid_selection'

        r = client.post(
            '/api/lesson/explain',
            json={
                'selection': {
                    'text': 'This selection is long enough to pass the minimum.',
                },
                'context': {
                    'level': 'gcse',
                    'subject': 'maths',
                    'topic': 'not_a_real_topic',
                    'topicTitle': 'Missing',
                },
            },
        )
        assert r.status_code == 400, r.data
        assert r.get_json()['error']['code'] == 'invalid_context'

    print('Lesson assist smoke tests passed.')


if __name__ == '__main__':
    main()
