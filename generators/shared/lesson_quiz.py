"""
Build 10-question lesson MCQ quizzes (3 foundational, 4 intermediate, 3 difficult)
using each topic's existing generator MCQ mode.
"""
import random
import re

LESSON_QUIZ_MIX = (
    ("foundational", 3),
    ("intermediate", 4),
    ("difficult", 3),
)

_MAX_GENERATION_ATTEMPTS = 120


def _question_key(problem):
    """Normalized question text used to detect duplicate MCQs in one quiz."""
    q = problem.get("question") or ""
    return re.sub(r"\s+", " ", str(q).strip())


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
        else:
            if problem.get("options") and problem.get("correct_answer"):
                return True
    return False


def _generate_mcq_problem(generator, variants_func, difficulty, seen_keys, rng=None):
    """Return one unique MCQ problem dict, or None if none found."""
    rng = rng or random
    for _ in range(_MAX_GENERATION_ATTEMPTS):
        try:
            if variants_func:
                variants = variants_func(difficulty, "mcq")
                if variants:
                    variant = rng.choice(variants)
                    try:
                        problem = generator(
                            difficulty, "mcq", variant_name=variant.__name__
                        )
                    except TypeError:
                        problem = generator(difficulty, "mcq")
                else:
                    problem = generator(difficulty, "mcq")
            else:
                problem = generator(difficulty, "mcq")
        except TypeError:
            problem = generator(difficulty, "mcq")
        except Exception:
            continue

        if not (problem.get("options") and problem.get("correct_answer")):
            continue

        key = _question_key(problem)
        if key and key in seen_keys:
            continue

        out = dict(problem)
        out["difficulty"] = difficulty
        if key:
            seen_keys.add(key)
        return out
    return None


def _fill_quiz_slot(generator, variants_func, difficulty, count, problems, seen_keys, rng=None):
    """Append up to `count` unique problems for one difficulty band."""
    rng = rng or random
    added = 0
    while added < count:
        problem = _generate_mcq_problem(generator, variants_func, difficulty, seen_keys, rng)
        if not problem:
            break
        problems.append(problem)
        added += 1


def build_lesson_mcq_quiz(level, subject, topic, topic_config, *, seed=None):
    """
    Build 10 shuffled MCQs: 3 foundational, 4 intermediate, 3 difficult.
    Uses the topic's generator in MCQ mode (existing MCQ banks / variants).
    No two questions in the quiz share the same question text.
    Optional seed produces a reproducible quiz (for friend challenges).
    """
    rng = random.Random(seed) if seed is not None else random
    generator = topic_config["func"]
    variants_func = topic_config.get("variants_func")
    problems = []
    seen_keys = set()

    for difficulty, count in LESSON_QUIZ_MIX:
        _fill_quiz_slot(generator, variants_func, difficulty, count, problems, seen_keys, rng)

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
            )
            if len(problems) >= 10:
                break

    if not problems:
        raise ValueError(f"No MCQ problems available for {level}/{subject}/{topic}")

    rng.shuffle(problems)
    return problems[:10]
