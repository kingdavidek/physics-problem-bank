"""Check lesson assist loads on quiz review page."""
import re
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import app, get_db  # noqa: E402
from models.user import User  # noqa: E402
from models.user_data import record_quiz_attempt  # noqa: E402


def csrf_from(html):
    m = re.search(r'name="csrf_token" value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf-token" content="([^"]+)"', html)
    return m.group(1)


def main():
    suffix = uuid.uuid4().hex[:8]
    with app.test_client() as client:
        r = client.get('/register')
        client.post(
            '/register',
            data={
                'csrf_token': csrf_from(r.data.decode()),
                'email': f'assist_{suffix}@example.com',
                'handle': f'assist_{suffix}',
                'password': 'password123',
                'confirm_password': 'password123',
                'age_confirm': '1',
            },
            follow_redirects=True,
        )
        with get_db() as conn:
            user = User.get_by_email(conn, f'assist_{suffix}@example.com')
            attempt_id = record_quiz_attempt(
                conn,
                user.id,
                'gcse',
                'maths',
                'bidmas',
                1,
                1,
                ['B'],
                [{
                    'question': 'Test question',
                    'options': ['A) 1', 'B) 2'],
                    'correct_answer': 'B',
                    'solution': 'Because 2 is correct.',
                }],
            )
        r = client.get(f'/quiz-attempts/{attempt_id}')
        html = r.data.decode()
        assert 'data-quiz-review="1"' in html
        assert 'quiz-assist.js' in html
        assert 'lesson-assist.js' not in html
        assert 'AI explain this question' in html
        assert 'lesson-progress.js' not in html

        r = client.post(
            '/api/lesson/explain',
            json={
                'mode': 'quiz_review',
                'context': {
                    'level': 'gcse',
                    'subject': 'maths',
                    'topic': 'bidmas',
                    'topicTitle': 'BIDMAS',
                    'pageUrl': f'/quiz-attempts/{attempt_id}',
                    'quizReview': True,
                },
                'quiz': {
                    'question': 'What is 3 + 4?',
                    'options': ['A) 6', 'B) 7', 'C) 8'],
                    'userAnswer': 'A',
                    'correctAnswer': 'B',
                    'modelExplanation': 'Add the numbers.',
                    'questionNumber': 1,
                    'wasCorrect': False,
                },
                'question': 'Explain why I was wrong.',
            },
        )
        data = r.get_json()
        assert data['ok'] is True, data
        assert data['explanation']
    print('Quiz review lesson assist check passed.')


if __name__ == '__main__':
    main()
