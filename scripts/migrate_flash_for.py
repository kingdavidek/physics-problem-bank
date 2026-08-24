"""One-off: migrate flash() calls to flash_for(page, ...) from nearby redirect."""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / 'app.py'
text = APP.read_text(encoding='utf-8')
lines = text.splitlines()

SKIP_QOTD_FLASH = (
    'Not quite — answer was',
    'Correct!',
    'You already answered today.',
)


def page_from_redirect(line: str):
    if "url_for('profile_settings')" in line:
        return 'profile_settings'
    if "url_for('saved_problems_index')" in line:
        return 'saved_problems_index'
    if "url_for('suggestions_inbox')" in line:
        return 'suggestions_inbox'
    if "url_for('challenges_list')" in line:
        return 'challenges_list'
    if "url_for('challenge_new')" in line:
        return 'challenge_new'
    if "url_for('challenge_detail'" in line:
        return 'challenge_detail'
    if "url_for('view_saved_problem'" in line:
        return 'view_saved_problem'
    if "url_for('view_shared_question'" in line:
        return 'view_shared_question'
    if "url_for('quicktest_results')" in line:
        return 'quicktest_results'
    if "url_for('lesson_mcq_results')" in line:
        return 'lesson_mcq_results'
    if "url_for('qotd_page')" in line:
        return 'qotd_page'
    if "url_for('index')" in line:
        return 'index'
    if "url_for('profile')" in line:
        return 'profile'
    if '_public_profile_url' in line:
        return 'public_profile'
    if 'redirect(share_url)' in line or 'redirect(share_url' in line:
        return 'view_shared_question'
    if 'redirect(next_url)' in line:
        return 'profile'
    if 'request.referrer' in line:
        return 'index'
    m = re.search(r"redirect\(url_for\('([^']+)'", line)
    if m:
        return m.group(1)
    return None


def is_flash_line(line: str) -> bool:
    stripped = line.lstrip()
    return stripped.startswith('flash(') and 'flash_for' not in stripped


out = []
i = 0
while i < len(lines):
    line = lines[i]
    if not is_flash_line(line):
        out.append(line)
        i += 1
        continue

    block = [line]
    j = i + 1
    joined = line
    while joined.count('(') > joined.count(')'):
        if j >= len(lines):
            break
        block.append(lines[j])
        joined = '\n'.join(block)
        j += 1

    page = None
    for k in range(j, min(j + 10, len(lines))):
        page = page_from_redirect(lines[k])
        if page:
            break

    block_text = '\n'.join(block)
    if page == 'qotd_page' and any(token in block_text for token in SKIP_QOTD_FLASH):
        i = j
        continue

    if page is None:
        print(f'WARNING: no redirect page for flash at line {i + 1}')
        out.extend(block)
        i = j
        continue

    transformed = re.sub(r'\bflash\(', f"flash_for('{page}', ", block_text, count=1)
    out.extend(transformed.splitlines())
    i = j

APP.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('done')
