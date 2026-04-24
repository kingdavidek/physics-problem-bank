def make_problem(question, solution, hint, difficulty, marks, level, subject, topic, **extra):
    data = {
        "question": question,
        "solution": solution,
        "hint": hint,
        "difficulty": difficulty,
        "marks": marks,
        "topic_url": f"/topic/{level}/{subject}/{topic}",
        "topic_name": topic.replace("-", " ").title(),
        "level": level,
        "subject": subject,
        "topic": topic,
    }
    data.update(extra)
    return data