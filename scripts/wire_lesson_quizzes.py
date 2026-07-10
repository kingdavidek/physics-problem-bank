"""Wire Practice Quiz links on GCSE maths/cs lesson pages that support MCQ mode."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from topic_registry import TOPICS
from generators.shared.lesson_quiz import topic_supports_lesson_mcq

TEMPLATES = ROOT / "templates"


def lesson_path(subject, topic):
    return TEMPLATES / f"gcse_{subject}_{topic}_lesson.html"


def wire_content(text, subject, topic):
    quiz = (
        f"{{{{ url_for('lesson_mcq_quiz', level='gcse', subject='{subject}', "
        f"topic='{topic}') }}}}"
    )
    topic_page = (
        f"{{{{ url_for('topic_page', level='gcse', subject='{subject}', "
        f"topic='{topic}') }}}}"
    )
    # Replace topic_page links that are NOT practice-mode query strings
    text = text.replace(topic_page + "?", topic_page + "?")
    text = re.sub(re.escape(topic_page) + r"(?!\?)", quiz, text)
    text = text.replace("▶ Quick Practice Test", "▶ Practice Quiz (10 MCQs)")
    text = text.replace("Start Practice Questions", "Start Practice Quiz")
    return text


def main():
    updated = []
    skipped = []
    for subject in ("maths", "cs"):
        for topic, config in TOPICS["gcse"][subject].items():
            path = lesson_path(subject, topic)
            if not path.exists():
                skipped.append(f"{subject}/{topic} (no lesson file)")
                continue
            if not topic_supports_lesson_mcq(config):
                skipped.append(f"{subject}/{topic} (no MCQ mode)")
                continue
            original = path.read_text(encoding="utf-8")
            new = wire_content(original, subject, topic)
            if new != original:
                path.write_text(new, encoding="utf-8")
                updated.append(str(path.name))
    print("Updated:", len(updated))
    for name in sorted(updated):
        print(" ", name)
    print("Skipped:", len(skipped))


if __name__ == "__main__":
    main()
