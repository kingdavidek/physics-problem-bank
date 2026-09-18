"""Canonical lesson step counts derived from lesson templates."""
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'templates'
FILENAME_RE = re.compile(r'^(gcse|alevel|myp|eursc)_([a-z]+)_([a-z0-9_]+)_lesson\.html$')
_MCQ_MARKER = 'class="mcq-inline"'


@lru_cache(maxsize=256)
def lesson_step_total(level, subject, topic):
    """Return the number of Quick Check MCQs for a topic lesson (0 if unknown)."""
    level = (level or '').strip()
    subject = (subject or '').strip()
    topic = (topic or '').strip()
    if not level or not subject or not topic:
        return 0

    custom = f'{level}_{subject}_{topic}_lesson.html'
    path = TEMPLATES / custom
    if path.is_file():
        return path.read_text(encoding='utf-8').count(_MCQ_MARKER)

    return 0


def lesson_step_totals_for_topics(topics_tree):
    """Build {(level, subject, slug): step_total} from the topic registry tree."""
    totals = {}
    for level, subjects in (topics_tree or {}).items():
        if not isinstance(subjects, dict):
            continue
        for subject, topics in subjects.items():
            if not isinstance(topics, dict):
                continue
            for slug in topics:
                total = lesson_step_total(level, subject, slug)
                if total > 0:
                    totals[(level, subject, slug)] = total
    return totals
