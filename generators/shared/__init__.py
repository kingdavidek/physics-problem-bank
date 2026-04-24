# -----------------------------------------------
# HELPER
# -----------------------------------------------
def make_problem(question, solution, hint, difficulty, marks, level, subject, topic):
    """
    Central factory for all problem dicts.
    All fields are used by index.html — don't add/remove keys
    without updating the template too.

    question / solution / hint: HTML strings.
    Inline equations must use \\( ... \\) for MathJax.
    Display equations use \\[ ... \\].
    """
    return {
        "question":   question,
        "solution":   solution,
        "hint":       hint,
        "difficulty": difficulty,
        "marks":      marks,
        "topic_url":  f"/topic/{level}/{subject}/{topic}",
        "topic_name": topic.replace('_', ' ').title(),
        # Stored for future progress tracking — do not remove
        "level":      level,
        "subject":    subject,
        "topic":      topic,
    }