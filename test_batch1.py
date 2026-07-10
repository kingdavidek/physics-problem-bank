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

namespace = {"random": random, "math": math, "make_problem": make_problem}
with open("/home/ubuntu/gcse_batch1_generator_additions.py", "r", encoding="utf-8") as f:
    code = f.read()
exec(compile(code, "/home/ubuntu/gcse_batch1_generator_additions.py", "exec"), namespace)

topics = [
    ("geometry_angles", "gcse_geometry_angles", "gcse_geometry_angles_variants"),
    ("mensuration", "gcse_mensuration", "gcse_mensuration_variants"),
    ("graphs", "gcse_graphs", "gcse_graphs_variants"),
]

for topic, gen_name, variants_name in topics:
    gen = namespace[gen_name]
    variants_func = namespace[variants_name]
    for difficulty in ["foundational", "intermediate", "difficult", "mixed"]:
        variants = variants_func(difficulty, "revision")
        assert len(variants) == 10, (topic, difficulty, len(variants))
        for v in variants:
            q, s, hint, marks = v()
            assert isinstance(q, str) and q, (topic, v.__name__, "question")
            assert isinstance(s, str) and s, (topic, v.__name__, "solution")
            assert isinstance(hint, str) and hint, (topic, v.__name__, "hint")
            assert isinstance(marks, int) and marks >= 1, (topic, v.__name__, "marks")
            problem_named = gen(difficulty, "revision", variant_name=v.__name__)
            assert problem_named["topic"] == topic, (topic, problem_named["topic"])
        problem = gen(difficulty, "revision")
        assert problem["topic"] == topic, (topic, problem["topic"])
    for _ in range(50):
        mcq = gen("foundational", "mcq")
        assert mcq["topic"] == topic
        assert "options" in mcq and len(mcq["options"]) == 4, topic
        assert mcq["correct_answer"] in ["A", "B", "C", "D"], topic

print("Batch 1 GCSE Maths generators passed runtime checks.")
