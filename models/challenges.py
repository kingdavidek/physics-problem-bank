"""Friend quiz challenges — same fixed MCQ set, compare scores."""
import hashlib
import json

from models.user import utc_now_iso

CHALLENGE_PENDING = 'pending'
CHALLENGE_COMPLETE = 'complete'
CHALLENGE_DECLINED = 'declined'

MAX_OPEN_CHALLENGES_PER_USER = 20


def _score_answers(problems, answers):
    score = 0
    for i, problem in enumerate(problems):
        letter = answers[i] if i < len(answers) else ''
        letter = (letter or '').strip().upper()[:1]
        if letter and letter == (problem.get('correct_answer') or '').strip().upper()[:1]:
            score += 1
    return score


def _challenge_row(row):
    if not row:
        return None
    data = dict(row)
    try:
        data['problems'] = json.loads(data.pop('problems_json') or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        data['problems'] = []
    return data


def create_challenge(conn, creator_id, opponent_id, level, subject, topic, problems, *, seed):
    open_count = conn.execute(
        '''
        SELECT COUNT(*) AS n FROM quiz_challenges
        WHERE status = ?
          AND (creator_id = ? OR opponent_id = ?)
        ''',
        (CHALLENGE_PENDING, creator_id, creator_id),
    ).fetchone()['n']
    if open_count >= MAX_OPEN_CHALLENGES_PER_USER:
        raise ValueError('challenge_limit')

    now = utc_now_iso()
    cursor = conn.execute(
        '''
        INSERT INTO quiz_challenges (
            creator_id, opponent_id, level, subject, topic, seed,
            problems_json, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            creator_id,
            opponent_id,
            level,
            subject,
            topic,
            int(seed),
            json.dumps(problems),
            CHALLENGE_PENDING,
            now,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_challenge(conn, challenge_id):
    row = conn.execute(
        '''
        SELECT c.*,
               cu.handle AS creator_handle,
               ou.handle AS opponent_handle
        FROM quiz_challenges c
        JOIN users cu ON cu.id = c.creator_id
        JOIN users ou ON ou.id = c.opponent_id
        WHERE c.id = ?
        ''',
        (challenge_id,),
    ).fetchone()
    return _challenge_row(row)


def list_challenges_for_user(conn, user_id, *, limit=50):
    rows = conn.execute(
        '''
        SELECT c.*,
               cu.handle AS creator_handle,
               ou.handle AS opponent_handle
        FROM quiz_challenges c
        JOIN users cu ON cu.id = c.creator_id
        JOIN users ou ON ou.id = c.opponent_id
        WHERE c.creator_id = ? OR c.opponent_id = ?
        ORDER BY c.created_at DESC
        LIMIT ?
        ''',
        (user_id, user_id, limit),
    ).fetchall()
    return [_challenge_row(row) for row in rows]


def user_role_in_challenge(challenge, user_id):
    if challenge['creator_id'] == user_id:
        return 'creator'
    if challenge['opponent_id'] == user_id:
        return 'opponent'
    return None


def user_has_submitted(challenge, user_id):
    role = user_role_in_challenge(challenge, user_id)
    if role == 'creator':
        return challenge.get('creator_score') is not None
    if role == 'opponent':
        return challenge.get('opponent_score') is not None
    return False


def submit_challenge_attempt(conn, challenge_id, user_id, answers):
    challenge = get_challenge(conn, challenge_id)
    if not challenge:
        raise ValueError('not_found')
    if challenge['status'] == CHALLENGE_DECLINED:
        raise ValueError('declined')
    role = user_role_in_challenge(challenge, user_id)
    if not role:
        raise ValueError('forbidden')
    if user_has_submitted(challenge, user_id):
        raise ValueError('already_submitted')

    problems = challenge['problems']
    score = _score_answers(problems, answers)
    now = utc_now_iso()
    if role == 'creator':
        conn.execute(
            '''
            UPDATE quiz_challenges
            SET creator_score = ?, creator_completed_at = ?
            WHERE id = ?
            ''',
            (score, now, challenge_id),
        )
    else:
        conn.execute(
            '''
            UPDATE quiz_challenges
            SET opponent_score = ?, opponent_completed_at = ?
            WHERE id = ?
            ''',
            (score, now, challenge_id),
        )

    updated = get_challenge(conn, challenge_id)
    if (
        updated['creator_score'] is not None
        and updated['opponent_score'] is not None
    ):
        conn.execute(
            'UPDATE quiz_challenges SET status = ? WHERE id = ?',
            (CHALLENGE_COMPLETE, challenge_id),
        )
        updated['status'] = CHALLENGE_COMPLETE
    conn.commit()
    return updated, score


def decline_challenge(conn, challenge_id, user_id):
    challenge = get_challenge(conn, challenge_id)
    if not challenge or challenge['opponent_id'] != user_id:
        return False
    if challenge['status'] != CHALLENGE_PENDING:
        return False
    conn.execute(
        'UPDATE quiz_challenges SET status = ? WHERE id = ?',
        (CHALLENGE_DECLINED, challenge_id),
    )
    conn.commit()
    return True


def make_challenge_seed(creator_id, opponent_id, level, subject, topic):
    raw = f'{creator_id}:{opponent_id}:{level}:{subject}:{topic}:{utc_now_iso()}'
    return int(hashlib.sha256(raw.encode('utf-8')).hexdigest()[:8], 16)


def serialize_challenge(challenge, viewer_id):
    role = user_role_in_challenge(challenge, viewer_id)
    total = len(challenge.get('problems') or [])
    return {
        'id': challenge['id'],
        'status': challenge['status'],
        'level': challenge['level'],
        'subject': challenge['subject'],
        'topic': challenge['topic'],
        'seed': challenge['seed'],
        'total': total,
        'creator_handle': challenge.get('creator_handle'),
        'opponent_handle': challenge.get('opponent_handle'),
        'creator_score': challenge.get('creator_score'),
        'opponent_score': challenge.get('opponent_score'),
        'viewer_role': role,
        'viewer_submitted': user_has_submitted(challenge, viewer_id) if role else False,
        'created_at': challenge.get('created_at'),
        'creator_completed_at': challenge.get('creator_completed_at'),
        'opponent_completed_at': challenge.get('opponent_completed_at'),
    }
