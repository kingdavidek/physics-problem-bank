"""Friend quiz challenges — same fixed MCQ set, compare scores."""
import hashlib
import json

from models.user import utc_now_iso

CHALLENGE_PENDING = 'pending'
CHALLENGE_COMPLETE = 'complete'
CHALLENGE_DECLINED = 'declined'

MAX_OPEN_CHALLENGES_PER_USER = 20


def _letter(value):
    return (value or '').strip().upper()[:1]


def _normalize_answer_list(answers, total):
    out = []
    for i in range(total):
        raw = answers[i] if i < len(answers) else ''
        out.append(_letter(raw))
    return out


def _parse_answers_json(raw):
    try:
        parsed = json.loads(raw or '[]')
    except (TypeError, ValueError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [_letter(item) for item in parsed]


def _score_answers(problems, answers):
    score = 0
    for i, problem in enumerate(problems):
        letter = answers[i] if i < len(answers) else ''
        letter = _letter(letter)
        if letter and letter == _letter(problem.get('correct_answer')):
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
    data['creator_answers'] = _parse_answers_json(data.pop('creator_answers_json', None))
    data['opponent_answers'] = _parse_answers_json(data.pop('opponent_answers_json', None))
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


def count_actionable_challenges(conn, user_id):
    """Pending challenges where the user still needs to play."""
    rows = conn.execute(
        '''
        SELECT creator_id, opponent_id, creator_score, opponent_score
        FROM quiz_challenges
        WHERE status = ? AND (creator_id = ? OR opponent_id = ?)
        ''',
        (CHALLENGE_PENDING, user_id, user_id),
    ).fetchall()
    count = 0
    for row in rows:
        if row['creator_id'] == user_id:
            if row['creator_score'] is None:
                count += 1
        elif row['opponent_score'] is None:
            count += 1
    return count


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
    normalized = _normalize_answer_list(answers, len(problems))
    score = _score_answers(problems, normalized)
    answers_json = json.dumps(normalized)
    now = utc_now_iso()
    if role == 'creator':
        conn.execute(
            '''
            UPDATE quiz_challenges
            SET creator_score = ?, creator_completed_at = ?, creator_answers_json = ?
            WHERE id = ?
            ''',
            (score, now, answers_json, challenge_id),
        )
    else:
        conn.execute(
            '''
            UPDATE quiz_challenges
            SET opponent_score = ?, opponent_completed_at = ?, opponent_answers_json = ?
            WHERE id = ?
            ''',
            (score, now, answers_json, challenge_id),
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


def build_head_to_head(challenge):
    """Per-question comparison once both players have submitted."""
    problems = challenge.get('problems') or []
    creator_answers = challenge.get('creator_answers') or []
    opponent_answers = challenge.get('opponent_answers') or []
    questions = []
    for i, problem in enumerate(problems):
        correct = _letter(problem.get('correct_answer'))
        creator_answer = creator_answers[i] if i < len(creator_answers) else ''
        opponent_answer = opponent_answers[i] if i < len(opponent_answers) else ''
        questions.append({
            'index': i,
            'question': problem.get('question') or '',
            'options': problem.get('options') or [],
            'correct': correct,
            'creator_answer': creator_answer,
            'opponent_answer': opponent_answer,
            'creator_correct': bool(creator_answer and creator_answer == correct),
            'opponent_correct': bool(opponent_answer and opponent_answer == correct),
        })
    creator_score = challenge.get('creator_score')
    opponent_score = challenge.get('opponent_score')
    winner = None
    if creator_score is not None and opponent_score is not None:
        if creator_score > opponent_score:
            winner = 'creator'
        elif opponent_score > creator_score:
            winner = 'opponent'
        else:
            winner = 'draw'
    return {
        'questions': questions,
        'winner': winner,
        'has_answers': any(creator_answers) or any(opponent_answers),
    }
