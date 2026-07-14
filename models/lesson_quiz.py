"""Lesson MCQ quiz session storage (10-question mixed-difficulty quizzes)."""
import uuid

from models.quicktest import load_quicktest_session, save_quicktest_session


def make_lesson_quiz_session_id(user_id=None):
    token = uuid.uuid4().hex
    if user_id:
        return f'lq_u{user_id}_{token}'
    return f'lq_a_{token}'


def save_lesson_quiz_session(conn, session_id, data):
    save_quicktest_session(conn, session_id, data)


def load_lesson_quiz_session(conn, session_id):
    return load_quicktest_session(conn, session_id)


def session_owner_user_id(session_id):
    if session_id.startswith('lq_u') and session_id.count('_') >= 2:
        middle = session_id[4:]
        user_part = middle.split('_', 1)[0]
        if user_part.isdigit():
            return int(user_part)
    return None


def can_access_lesson_quiz(data, session_id, viewer_user_id):
    owner = data.get('owner_user_id')
    if owner is None:
        owner = session_owner_user_id(session_id)
    if owner is not None:
        return viewer_user_id == owner
    return True
