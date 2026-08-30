"""
Build 10-question lesson quizzes (3 foundational, 4 intermediate, 3 difficult)
from a topic's lesson bank (mixed formats) or MCQ mode.
"""
import random
import re

from generators.shared.answer_checkers import MAX_USER_ANSWER_LEN, check_answer

LESSON_QUIZ_MIX = (
    ("foundational", 3),
    ("intermediate", 4),
    ("difficult", 3),
)

_MAX_GENERATION_ATTEMPTS = 120


def _question_key(problem):
    """Normalized question text used to detect duplicate problems in one quiz."""
    q = problem.get("question") or ""
    return re.sub(r"\s+", " ", str(q).strip())


def is_lesson_quiz_problem(problem):
    """True if the problem can be graded as MCQ or as a typed session answer."""
    if not isinstance(problem, dict):
        return False
    if not str(problem.get("question") or "").strip():
        return False
    if problem.get("options") and problem.get("correct_answer"):
        return True
    if problem.get("correct_answer_raw") is not None and problem.get("answer_type"):
        return True
    return False


def _quiz_generation_mode(topic_config):
    """Prefer an explicit lesson bank; otherwise keep existing MCQ quizzes."""
    if topic_config.get("lesson_bank"):
        return "lesson"
    return "mcq"


def _call_generator(generator, difficulty, mode, variant_name=None):
    kwargs_list = []
    if variant_name:
        kwargs_list.append({"variant_name": variant_name})
    kwargs_list.extend(({}, {"variant_name": None}))
    last_error = None
    for extra in kwargs_list:
        try:
            return generator(difficulty, mode, **extra)
        except TypeError:
            try:
                return generator(difficulty, mode)
            except Exception as exc:
                last_error = exc
                continue
        except Exception as exc:
            last_error = exc
            continue
    if last_error:
        return None
    return None


def topic_supports_lesson_mcq(topic_config):
    """Return True if the topic generator can produce MCQ problems."""
    generator = topic_config["func"]
    for kwargs in ({}, {"variant_name": None}):
        try:
            problem = generator("foundational", "mcq", **kwargs)
        except TypeError:
            try:
                problem = generator("foundational", "mcq")
            except Exception:
                return False
        except Exception:
            return False
        else:
            if problem.get("options") and problem.get("correct_answer"):
                return True
    return False


def topic_supports_lesson_quiz(topic_config):
    """Capability detection: MCQ and/or typed lesson-bank problems."""
    mode = _quiz_generation_mode(topic_config)
    generator = topic_config["func"]
    problem = _call_generator(generator, "foundational", mode)
    if is_lesson_quiz_problem(problem):
        return True
    if mode != "mcq" and topic_supports_lesson_mcq(topic_config):
        return True
    return False


def _generate_quiz_problem(generator, variants_func, difficulty, seen_keys, rng=None, mode="mcq"):
    """Return one unique gradable quiz problem, or None if none found."""
    rng = rng or random
    for _ in range(_MAX_GENERATION_ATTEMPTS):
        variant_name = None
        try:
            if variants_func:
                variants = variants_func(difficulty, mode)
                if variants:
                    variant = rng.choice(variants)
                    variant_name = getattr(variant, "__name__", None)
                    problem = _call_generator(generator, difficulty, mode, variant_name)
                else:
                    problem = _call_generator(generator, difficulty, mode)
            else:
                problem = _call_generator(generator, difficulty, mode)
        except Exception:
            continue

        if not is_lesson_quiz_problem(problem):
            continue

        key = _question_key(problem)
        if key and key in seen_keys:
            continue

        out = dict(problem)
        out["difficulty"] = difficulty
        if variant_name and not out.get("variant_name"):
            out["variant_name"] = variant_name
        if key:
            seen_keys.add(key)
        return out
    return None


def _generate_mcq_problem(generator, variants_func, difficulty, seen_keys, rng=None):
    """Return one unique MCQ problem dict, or None if none found."""
    problem = _generate_quiz_problem(
        generator, variants_func, difficulty, seen_keys, rng, mode="mcq"
    )
    if problem and problem.get("options") and problem.get("correct_answer"):
        return problem
    return None


def _fill_quiz_slot(
    generator, variants_func, difficulty, count, problems, seen_keys, rng=None, mode="mcq"
):
    """Append up to `count` unique problems for one difficulty band."""
    rng = rng or random
    added = 0
    # Mixed lesson banks: take one MCQ first when the band has one, so a random
    # 10-question draw cannot be typed-only (ES0 fixture has 1 MCQ in 5 items).
    if mode == "lesson":
        mcq = _generate_mcq_problem(
            generator, variants_func, difficulty, seen_keys, rng
        )
        if mcq:
            problems.append(mcq)
            added += 1
    while added < count:
        problem = _generate_quiz_problem(
            generator, variants_func, difficulty, seen_keys, rng, mode=mode
        )
        if not problem:
            break
        problems.append(problem)
        added += 1


def build_single_mcq(level, subject, topic, topic_config, *, difficulty='difficult', rng=None):
    """One MCQ at ``difficulty``, or None if the topic cannot produce one."""
    rng = rng or random
    problem = _generate_mcq_problem(
        topic_config['func'],
        topic_config.get('variants_func'),
        difficulty,
        set(),
        rng,
    )
    if problem:
        problem['difficulty'] = difficulty
    return problem


def build_lesson_quiz(level, subject, topic, topic_config, *, seed=None):
    """
    Build 10 shuffled quiz problems: 3 foundational, 4 intermediate, 3 difficult.

    Topics with ``lesson_bank`` draw from mixed lesson-mode generators
    ({options, correct_answer} or {correct_answer_raw, answer_type, ...}).
    Other topics keep the existing MCQ-only bank.
    No two questions in the quiz share the same question text.
    Optional seed produces a reproducible quiz (for friend challenges).
    """
    rng = random.Random(seed) if seed is not None else random
    generator = topic_config["func"]
    variants_func = topic_config.get("variants_func")
    mode = _quiz_generation_mode(topic_config)
    problems = []
    seen_keys = set()

    for difficulty, count in LESSON_QUIZ_MIX:
        _fill_quiz_slot(
            generator, variants_func, difficulty, count, problems, seen_keys, rng, mode=mode
        )

    if len(problems) < 10:
        for difficulty in ("foundational", "intermediate", "difficult"):
            _fill_quiz_slot(
                generator,
                variants_func,
                difficulty,
                10 - len(problems),
                problems,
                seen_keys,
                rng,
                mode=mode,
            )
            if len(problems) >= 10:
                break

    if len(problems) < 10 and mode != "mcq":
        for difficulty in ("foundational", "intermediate", "difficult"):
            _fill_quiz_slot(
                generator,
                variants_func,
                difficulty,
                10 - len(problems),
                problems,
                seen_keys,
                rng,
                mode="mcq",
            )
            if len(problems) >= 10:
                break

    if not problems:
        raise ValueError(f"No lesson-quiz problems available for {level}/{subject}/{topic}")

    rng.shuffle(problems)
    return problems[:10]


def build_lesson_mcq_quiz(level, subject, topic, topic_config, *, seed=None):
    """MCQ-only quiz (friend challenges). Mixed lesson banks use :func:`build_lesson_quiz`."""
    forced = dict(topic_config)
    forced['lesson_bank'] = False
    return build_lesson_quiz(level, subject, topic, forced, seed=seed)


def _user_answer_text(user_answer):
    if isinstance(user_answer, dict):
        user_answer = user_answer.get("user_answer")
    if user_answer is None:
        return ""
    text = str(user_answer).strip()
    if len(text) > MAX_USER_ANSWER_LEN:
        return text[:MAX_USER_ANSWER_LEN]
    return text


def grade_lesson_quiz_problem(problem, user_answer):
    """
    Grade one lesson-quiz answer against the saved session problem.

    Never uses a client-supplied answer key. Overall quiz scoring stays
    one point per fully correct question.
    """
    user = _user_answer_text(user_answer)
    if problem.get("options") and problem.get("correct_answer"):
        letter = user.upper()[:1]
        correct_letter = (problem.get("correct_answer") or "").strip().upper()[:1]
        ok = bool(letter and correct_letter and letter == correct_letter)
        return {
            "user_answer": letter,
            "correct": ok,
            "score": 1 if ok else 0,
            "score_total": 1,
        }

    raw = problem.get("correct_answer_raw")
    answer_type = problem.get("answer_type") or "number"
    if raw is None:
        return {
            "user_answer": user,
            "correct": False,
            "score": 0,
            "score_total": 1,
        }

    try:
        result = check_answer(answer_type, raw, user)
    except ValueError:
        return {
            "user_answer": user,
            "correct": False,
            "score": 0,
            "score_total": 1,
        }

    score_total = int(result.get("score_total") or 1)
    if result.get("score") is not None:
        score = int(result["score"])
    else:
        score = score_total if result.get("correct") else 0
    ok = bool(result.get("correct"))
    return {
        "user_answer": user,
        "correct": ok,
        "score": score,
        "score_total": score_total,
        "feedback": result.get("feedback"),
    }


def lesson_quiz_problems_are_mixed(problems):
    """True when at least one question is typed rather than MCQ."""
    for problem in problems or []:
        if not (problem.get("options") and problem.get("correct_answer")):
            return True
    return False
