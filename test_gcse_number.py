import random
import math


def make_problem(question, solution, hint, difficulty, marks, level, subject, topic, **extra):
    data = {
        "question": question,
        "solution": solution,
        "hint": hint,
        "difficulty": difficulty,
        "marks": marks,
        "level": level,
        "subject": subject,
        "topic": topic,
    }
    data.update(extra)
    return data

namespace = {
    "random": random,
    "math": math,
    "make_problem": make_problem,
}

with open("/home/ubuntu/gcse_number_generator_additions.py", "r", encoding="utf-8") as f:
    code = f.read()

exec(compile(code, "/home/ubuntu/gcse_number_generator_additions.py", "exec"), namespace)

for difficulty in ["foundational", "intermediate", "difficult", "mixed"]:
    variants = namespace["gcse_number_variants"] (difficulty, "revision")
    assert len(variants) == 10, (difficulty, len(variants))
    for v in variants:
        q, s, hint, marks = v()
        assert isinstance(q, str) and q
        assert isinstance(s, str) and s
        assert isinstance(hint, str) and hint
        assert isinstance(marks, int)
    problem = namespace["gcse_number"] (difficulty, "revision")
    assert problem["topic"] == "number"

for _ in range(100):
    problem = namespace["gcse_number"] ("foundational", "mcq")
    assert "options" in problem and len(problem["options"]) == 4
    assert problem["correct_answer"] in ["A", "B", "C", "D"]

print("GCSE Number generator additions passed runtime checks.")
