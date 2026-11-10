"""E9 Zorp voice: copy inventory and ENFORCING lint (docs/ZORP_CHARM.md section 3.3 and Appendix A).

Run:   python scripts/test_zorp_voice_smoke.py
Regenerate the appendix after changing any Zorp or system copy:
       python scripts/test_zorp_voice_smoke.py --write

Phase 3 switched this from report mode to enforcing. Every line Zorp says (and the system voice beside
him) is extracted by models/zorp_voice.py and checked against the section 3.3.4 rules:
  * banned phrases, US spellings, the "practise" verb, glossary terms and neutral dismissal labels
  * length limits per surface, reading level (per line from 8 words, mean over all lines, long words)
  * no emoji or dash in a Zorp line, at most one "!" per line and one line in four
  * the system voice never says "I" (and Zorp never speaks from a system source)
  * the Problem Bank bot speaks in the system voice and its "not a person" note is the same everywhere
  * the welcome line tells the truth about when Zorp cheers and dances
  * Appendix A in the plan is in sync with the copy
Add copy: edit the source, run `--write`, commit the regenerated Appendix A. A template line must carry
data-zorp-voice (see models/zorp_voice.py) or this smoke cannot see it.
"""
import os

os.environ.setdefault('PB_TESTING', '1')

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models import zorp_voice as voice  # noqa: E402

# Each source must yield at least this many items, so a silently broken regex cannot pass as "no errors".
MIN_ITEMS = {
    'static/js/guide-catalog.js': 31 + 20,   # 31 lines plus labels
    'static/js/stage-catalog.js': 8 + 17,    # 2026-11-08: E10 arrival film, 8 lines plus headings and button labels
    'static/js/zorp-coach.js': 7 + 2,         # 2026-11-08: E10 phase 3 coach, 7 lines plus two button labels
    'static/js/zorp-tour.js': 29 + 23,        # 2026-11-08: E10 phase 6 tour: 19 steps, the end scene and 9 spotlights (29 lines), plus 20 headings and 3 labels
    'static/js/guide.js': 6,
    'static/js/badge-stage.js': 11,           # 2026-11-08: E10 phase 4 badge stage copy; 9 -> 11 (the wardrobe line and the Try it on button, phase 6b)
    'static/js/wardrobe.js': 2,               # 2026-11-08: E10 phase 6b wardrobe status lines
    'models/zorp_wardrobe.py': 17,            # 2026-11-08: E10 phase 6b wardrobe item names (one per catalogue item)
    'templates/partials/wardrobe.html': 7,    # 2026-11-08: E10 phase 6b wardrobe panel (intro, two notes, locked reason twice, two buttons)
    'static/js/story-chapters.js': 55 + 14,   # 2026-11-08: E10 phase 8 story chapters: 18 scenes (about 36 lines, 18 headings, 18 buttons), the offer toast and its two buttons
    'models/story.py': 6 + 6 + 2 + 1,         # 2026-11-08: E10 phase 8 chapter titles, unlock sentences, the two second-way-in lines, the arrival title
    'templates/partials/story_shelf.html': 4,  # 2026-11-08: E10 phase 8 the shelf heading, its intro and the Watch / Watch again labels
    'static/js/moments.js': 23,               # 2026-11-08: E10 phase 5 moments copy (stages, toasts, micro)
    'models/gamification.py': 27,             # 2026-11-08: E10 phase 4 badge titles, blurbs and how-to lines
    'models/topic_status.py': 48,            # 2026-11-08: E10 phase 4 generated topic badge copy
    'static/js/study-buddy.js': 4,
    'static/js/notifications.js': 3,
    'static/js/feed.js': 1,
    'models/buddy.py': 10 + 4,
    'models/bot.py': 4,
    'generators/shared/misconceptions.py': 12,   # the hint messages (docs/GCSE_MATHS_HINTS.md section 6)
    'app.py': 7,
    'static/js/site.js': 2,
    'templates/welcome.html': 11,
    'templates/base.html': 12,
    'templates/partials/guide.html': 4,
    'templates/offline.html': 2,
    'templates/public_profile.html': 1,
    'templates/profile_settings.html': 8,
    'templates/saved_problems.html': 3,
    'templates/follow_list.html': 4,
    'templates/leaderboard_friends.html': 6,
    'templates/qotd.html': 6,                 # 2026-11-08: E10 phase 7, +1 for the Daily week heading
    'templates/errors/404.html': 5,           # 2026-11-08: E10 phase 7 friendly 404: heading, Zorp's line, the hint, two links
    'templates/errors/500.html': 4,           # 2026-11-08: E10 phase 7 friendly 500: heading, Zorp's line, two links
    'templates/partials/around.html': 3,      # 2026-11-08: E10 phase 7 results lines by score band (high, middle, low)
    'templates/profile.html': 3,              # 2026-11-08: E10 phase 7 the New ribbon and two empty-state lines (quiz history, revision plan)
}
MIN_LINES = {'static/js/story-chapters.js': 34, 'static/js/guide-catalog.js': 31, 'static/js/stage-catalog.js': 8, 'static/js/zorp-coach.js': 7, 'static/js/zorp-tour.js': 29, 'models/buddy.py': 10, 'app.py': 7}

# Sources that only ever speak in one voice (section 3.3.2: Zorp never speaks in notifications or in
# grading feedback, and the system voice has no character). Templates mix both, by attribute.
ZORP_ONLY = ('static/js/guide-catalog.js', 'static/js/stage-catalog.js', 'static/js/zorp-coach.js', 'static/js/zorp-tour.js', 'static/js/guide.js', 'static/js/study-buddy.js', 'models/buddy.py', 'static/js/badge-stage.js', 'static/js/moments.js', 'static/js/story-chapters.js', 'static/js/wardrobe.js', 'models/zorp_wardrobe.py')
SYSTEM_ONLY = ('app.py', 'static/js/site.js', 'static/js/notifications.js', 'static/js/feed.js', 'models/bot.py',
               'generators/shared/misconceptions.py')

BOT_NOTE = 'A Problem Bank bot, not a person.'


def _items():
    items, errors = voice.extract()
    assert not errors, 'extraction errors:\n  ' + '\n  '.join(errors)
    return items


def _violations(rule, items=None, levels=('error', 'warn')):
    items = _items() if items is None else items
    return [v for v in voice.lint(items) if v.rule == rule and v.level in levels]


def _fmt(found):
    return '\n  '.join(f'{v.item.ref} [{v.level}] {v.detail} | "{v.item.text[:80]}"' for v in found)


def _no(rule, hint=''):
    found = _violations(rule)
    assert not found, f'{rule}: {len(found)} violation(s). {hint}\n  ' + _fmt(found)


def test_inventory_extracts():
    items, errors = voice.extract()
    counts = Counter(i.path for i in items)
    lines = Counter(i.path for i in items if i.kind == 'line')
    for path, minimum in MIN_ITEMS.items():
        if counts[path] < minimum:
            errors.append(f'{path}: {counts[path]} items extracted, expected at least {minimum}')
    for path, minimum in MIN_LINES.items():
        if lines[path] < minimum:
            errors.append(f'{path}: {lines[path]} lines extracted, expected at least {minimum}')
    # every corner message was rendered with the 30-character sample topic somewhere
    assert len(voice.SAMPLE_TOPIC) == 30, len(voice.SAMPLE_TOPIC)
    if not any(voice.SAMPLE_TOPIC in i.text for i in items if i.surface == 'corner_message'):
        errors.append('no corner message was rendered with the sample topic label')
    zorp = [i for i in items if i.voice == 'zorp']
    system = [i for i in items if i.voice == 'system']
    print(f'  {len(items)} items ({len(zorp)} Zorp, {len(system)} system) from {len(counts)} source files')
    assert not errors, 'extraction errors:\n  ' + '\n  '.join(errors)


def test_every_marked_template_is_expected():
    """A template that gains a data-zorp-voice mark must be added to MIN_ITEMS, so its lines are counted."""
    marked = set(voice.marked_templates())
    expected = {p for p in MIN_ITEMS if p.startswith('templates/')}
    assert marked == expected, f'marked templates differ from MIN_ITEMS: only marked {sorted(marked - expected)}, only listed {sorted(expected - marked)}'


def test_limits_match_the_plan():
    """The limits are section 3.3.4's; changing one is a plan change, not a lint tweak."""
    assert voice.LIMITS == {'guide_line': 100, 'reward_line': 80, 'corner_message': 100,
                            'button_label': 22, 'detail_label': 20, 'welcome_line': 70}, voice.LIMITS
    assert voice.FK_MAX_LINE == 8 and voice.FK_MIN_WORDS_LINE == 8 and voice.FK_MAX_MEAN == 5, 'D11 thresholds'
    assert voice.EXCLAIM_MAX_SHARE == 0.25


def test_banned_phrases():
    _no('banned phrase', 'Loss, urgency, guilt and ability-judging phrases are banned in every voice (3.3.4).')
    found = _violations('warn phrase')
    assert not found, '"just" and "don\'t worry" need a voice-ok comment on the source line:\n  ' + _fmt(found)


def test_british_spelling():
    _no('US spelling', 'British spelling everywhere (3.3.1).')


def test_practise_verb():
    _no('practise verb', '"practise" is the verb, "practice" the noun.')


def test_lengths_per_surface():
    _no('length')
    # the longest corner message uses the 30-character topic, so the limit is checked at its worst case
    corner = [i for i in _items() if i.surface == 'corner_message']
    assert corner and max(len(i.text) for i in corner) <= voice.LIMITS['corner_message']


def test_reading_level():
    _no('reading level')
    levels = voice.reading_levels(_items())
    assert levels['n'] >= 40, levels['n']
    assert levels['mean'] <= voice.FK_MAX_MEAN, f"mean grade {levels['mean']:.2f}"
    # D11: the per-line limit only covers lines of 8 words or more, but every line counts toward the mean
    assert levels['max_limited'] <= voice.FK_MAX_LINE, levels['max_limited']
    print(f"  reading level: mean {levels['mean']:.1f} over {levels['n']} lines (limit {voice.FK_MAX_MEAN:g}), "
          f"highest of 8+ words {levels['max_limited']:.1f} (limit {voice.FK_MAX_LINE:g})")


def test_long_words():
    _no('long word', 'Words of four or more syllables need to be on LONG_WORD_ALLOW (physics terms, placeholders).')


def test_no_emoji_or_dashes_in_zorp_lines():
    _no('characters')
    # independent of the lint code: a plain scan of every Zorp item
    for it in _items():
        if it.voice == 'zorp':
            assert not re.search(r'[–—]|\s-\s', it.text), f'dash in Zorp copy {it.ref}: {it.text}'
            assert not voice.EMOJI_RE.search(it.text), f'emoji in Zorp copy {it.ref}: {it.text}'


def test_exclamation_budget():
    _no('exclamation')
    lines = voice.zorp_lines(_items())
    share = sum(1 for i in lines if '!' in i.text) / len(lines)
    assert share <= 0.25, f'{share:.0%} of Zorp lines carry a "!" (limit 25%)'


def test_system_voice_has_no_first_person():
    _no('system voice', 'The system voice has no "I" and no character (3.3.2).')


def test_voice_split_by_source():
    """Both directions of 3.3.2: Zorp-only sources hold no system item, system-only sources no Zorp item."""
    items = _items()
    for it in items:
        if it.path in ZORP_ONLY:
            assert it.voice == 'zorp', f'{it.ref} is a system item in a Zorp source'
        if it.path in SYSTEM_ONLY:
            assert it.voice == 'system', f'{it.ref} is a Zorp item in a system source (Zorp never speaks in notifications or grading feedback)'
    for it in items:
        if it.voice == 'system':
            assert not re.match(r'(?i)zorp\b[:,]', it.text), f'{it.ref} puts words in Zorp\'s mouth in the system voice'


def test_glossary_terms():
    _no('glossary', '"streak skip" (never "freeze"), no "DMs", no "habit" framing.')
    items = _items()
    text = ' '.join(i.text.lower() for i in items if i.voice == 'zorp')
    assert 'streak skip' in text, 'the Guide streak line should say "streak skip", as the profile page does'
    assert 'freeze' not in text
    profile = (ROOT / 'templates' / 'profile.html').read_text(encoding='utf-8')
    assert 'Skip used' in profile and 'Freeze used' not in profile, 'the calendar legend says "Skip used" (final audit B5)'
    assert 'skip available' in profile, 'the glossary term follows profile.html'
    assert any(i.text == 'Not now' for i in items if i.dismiss), '"Not now" is the neutral dismissal'


def test_dismiss_labels_neutral():
    found = _violations('dismiss label')
    assert not found, 'dismissal labels must be neutral and approved:\n  ' + _fmt(found)
    dismiss = [i for i in _items() if i.dismiss]
    assert len(dismiss) >= 25, len(dismiss)
    assert {i.text for i in dismiss} == set(voice.DISMISS_APPROVED), {i.text for i in dismiss} ^ set(voice.DISMISS_APPROVED)
    # D10: the corner bubble stay label is just "Keep learning" (the topic is in the message above)
    stay = [i for i in dismiss if i.path == 'models/buddy.py']
    assert [i.text for i in stay] == ['Keep learning'], [i.text for i in stay]


def test_bot_voice_and_note():
    """Decision (Phase 3): the Problem Bank bot is a system account, not Zorp, so it speaks in the system
    voice; its "not a person" note is the same words everywhere it appears."""
    items = _items()
    bot = [i for i in items if i.path == 'models/bot.py']
    assert bot and all(i.voice == 'system' for i in bot)
    notes = [i for i in items if i.surface == 'bot_note']
    assert len(notes) >= 4, [i.ref for i in notes]
    for it in notes:
        assert it.text == BOT_NOTE, f'{it.ref}: {it.text!r}'
    # the live strings, not just the extractor's view of them
    from models import bot as bot_mod
    assert bot_mod.BOT_PROMPT and '!' not in bot_mod.BOT_PROMPT and not re.search(voice.FIRST_PERSON, bot_mod.BOT_PROMPT.lower())
    assert 'Problem Bank bot' in bot_mod.BOT_PROMPT and 'Problem Bank bot' in bot_mod.BOT_PROMPT_DONE


def test_welcome_line_is_truthful():
    """Planner's flag: Zorp does not dance when a pupil answers correctly (cheer, hop and wave rotate); he
    dances on lesson_complete. The welcome line may promise a dance only for finishing a lesson."""
    ready = [i for i in _items() if i.path == 'templates/welcome.html' and 'dance' in i.text.lower()]
    assert len(ready) == 1, [i.text for i in ready]
    for sentence in re.split(r'(?<=[.!?])\s+', ready[0].text):
        if 'dance' in sentence.lower():
            assert 'lesson' in sentence.lower(), f'a dance is promised outside a finished lesson: {sentence!r}'
    poses = (ROOT / 'static' / 'js' / 'zorp-poses.js').read_text(encoding='utf-8')
    m = re.search(r'var REACT = (\{.*?\});', poses)
    assert m, 'REACT table not found in zorp-poses.js'
    import json
    clips = json.loads(m.group(1))['clips']
    assert clips['lesson_complete'] == ['dance'] and 'dance' not in clips['correct']


def test_guide_js_fallbacks_match_catalog():
    """guide.js falls back to its own reward lines when the catalog is missing; the two must not drift."""
    items = _items()
    catalog = {i.text for i in items if i.path == 'static/js/guide-catalog.js' and i.surface == 'reward_line'}
    for it in items:
        if it.path == 'static/js/guide.js' and it.surface == 'reward_line' and it.text != 'Well done.':
            sample = it.text.replace(voice.SAMPLES['days'] + '-day', '7-day')
            assert sample in catalog, f'{it.ref}: fallback {it.text!r} is not a catalog reward line'


def test_lint_catches_each_rule():
    """The rules actually bite: one synthetic bad line per rule, and a clean line passes."""
    def zorp(text, surface='guide_line', **kw):
        return voice.Item('(test)', 1, 'zorp', surface, voice.kind_of(surface), text, **kw)

    def system(text, surface='system_notification'):
        return voice.Item('(test)', 1, 'system', surface, voice.kind_of(surface), text)

    def rules(*its):
        return {(v.rule) for v in voice.lint(list(its)) if v.level in ('error', 'warn')}

    def clean(*its):   # a one-line inventory can trip the mean reading grade; the new rules are checked without it
        return rules(*its) - {'reading level'}

    assert not rules(zorp('Pick a topic, then start practising.'))
    assert 'banned phrase' in rules(zorp('Do not lose your streak.'))
    assert 'banned phrase' in rules(zorp('This one is easy.'))
    assert 'banned phrase' in rules(system('Hurry up'))
    assert 'US spelling' in rules(zorp('Pick a color.'))
    assert 'US spelling' in rules(system('Your favorite topic'))
    assert 'practise verb' in rules(zorp('Time to practice this topic.'))
    assert 'characters' in rules(zorp('Nice work — well done.'))
    assert 'characters' in rules(zorp('Well done \U0001F389'))
    assert 'exclamation' in rules(zorp('Yes! Great! Go!'))
    assert 'length' in rules(zorp('a' * 101))
    assert 'length' in rules(zorp('Close the panel now and then.', 'button_label'))
    assert 'length' in rules(zorp('x' * 71, 'welcome_line'))
    assert 'reading level' in rules(zorp('Photosynthesis demonstrates considerable evolutionary adaptations across environments.'))
    assert 'long word' in rules(zorp('Pick a topic and celebrate the information.'))
    assert 'system voice' in rules(system("I'll remind you tomorrow"))
    assert 'glossary' in rules(zorp('A freeze covers a missed day.'))
    assert 'glossary' in rules(zorp('Challenges have no DMs.'))
    assert 'dismiss label' in rules(zorp("No thanks, I don't want to learn", 'button_label', dismiss=True))
    assert 'dismiss label' in rules(zorp('Maybe later', 'button_label', dismiss=True))
    assert not rules(zorp('Not now', 'button_label', dismiss=True))
    assert 'warn phrase' in rules(zorp('Just pick one.'))
    assert not rules(zorp('Just pick one.', justified=True))
    # a dash in a system string is a note, not a failure (3.3.4: the Zorp rules cover Zorp lines)
    assert not rules(system('Offline — saved lessons still work'))
    # Final audit B2 (2026-10-12): loss, urgency and comparison wording from the spec's Do/Don't table
    assert 'banned phrase' in rules(zorp('Answer one before midnight.'))
    assert 'banned phrase' in rules(system('Practise before midnight'))
    assert 'banned phrase' in rules(zorp('Fancy a question tonight?'))
    assert 'banned phrase' in rules(system('A quick question tonight'))
    assert 'banned phrase' in rules(zorp('Your streak resets soon.'))
    assert 'banned phrase' in rules(zorp('Your streak ends tomorrow.'))
    assert 'banned phrase' in rules(system('The streak is gone.'))
    assert 'banned phrase' in rules(system('Gone are the days of your streak.'))
    assert not clean(zorp('Your streak is on 4 days.'))
    assert 'banned phrase' in rules(zorp('Sam is ahead of you.'))
    assert 'banned phrase' in rules(system('Sam is ahead of you on the board'))
    assert 'banned phrase' in rules(zorp('You are behind today.'))
    assert not clean(system('The ball is behind the wall'))   # "behind" is banned in Zorp's voice only
    assert 'warn phrase' in rules(zorp('Do not worry about it.'))
    assert 'warn phrase' in rules(zorp("Don't worry about it."))
    assert not clean(zorp('Do not worry about it.', justified=True))
    assert 'characters' in rules(zorp('Nice work - well done.'))   # a spaced hyphen is a dash
    assert not clean(zorp('A well-known result.'))                  # a hyphen inside a word is not
    # false positives fixed: "lose" in physics sentences; "we", "our" and "us" in the system voice
    assert 'banned phrase' in rules(zorp('Do not lose your points.'))
    assert 'banned phrase' in rules(system('Do not lose your badge'))
    assert 'banned phrase' in rules(zorp('Friction is fun. Do not lose your streak.'))   # the physics sentence must be the same one
    assert not clean(zorp('Friction makes the ball lose energy.'))
    assert not clean(zorp('A hot cup will lose heat.'))
    assert not clean(system('Charges lose momentum in a collision'))
    assert not clean(system('We keep our records safe for us'))
    assert 'system voice' in rules(system('I will keep my records'))
    assert 'system voice' in rules(system('Tell me later'))
    # the mean grade bites over the whole inventory
    hard = [zorp('Photosynthesis in organisms requires considerable atmospheric conditions.') for _ in range(5)]
    assert any(v.rule == 'reading level' and 'mean' in v.detail for v in voice.lint(hard))
    # the "!" share bites over the whole inventory
    loud = [zorp('Hooray!'), zorp('Yes!'), zorp('Calm line.')]
    assert any(v.rule == 'exclamation' and 'of Zorp lines' in v.detail for v in voice.lint(loud))


def test_hint_messages():
    """The hint catalogue (generators/shared/misconceptions.py MESSAGES, NUDGES and LADDER_COPY) is read by the lint, on the stricter
    system_hint surface: house style, length, reading level and kind wording are errors there."""
    from generators.shared import misconceptions

    items = [i for i in _items() if i.surface == 'system_hint']
    seen = {i.where: i.text for i in items}
    want = dict(misconceptions.MESSAGES)
    want.update({'nudge:' + k: v for k, v in misconceptions.NUDGES.items()})            # Phase 3: rung 1 lines
    want.update({'ladder:' + k: v for k, v in misconceptions.LADDER_COPY.items()})     # Phase 3: the words around the ladder
    from generators.shared import mcq_notes
    want.update({'note:' + k: v for k, v in mcq_notes.NOTES.items()})                  # Phase 4: multiple-choice distractor notes
    want.update({'note:' + k: v for k, v in mcq_notes.BANK_NOTES.items()})
    want['nudge:default'] = misconceptions.NUDGE_DEFAULT                               # whole-change review 2026-11-03 (F10)
    assert seen == want, 'the extractor must see every message, nudge, ladder line and distractor note, unchanged'
    assert all(i.voice == 'system' and i.path in ('generators/shared/misconceptions.py', 'generators/shared/mcq_notes.py', 'generators/shared/misconception_5b.py') for i in items)
    found = [v for v in voice.lint(items) if v.level in ('error', 'warn')]
    assert not found, 'hint copy violations:\n  ' + _fmt(found)
    assert voice.HINT_MAX_CHARS == 120 and voice.HINT_MAX_SENTENCES == 2
    # Whole-change review 2026-11-03 (F8, D5): a message names the slip, never the operation that turns the pupil's own
    # number into the answer. These four lines did ("Halve it.", "Turn it upside down to get the answer.", "Divide by
    # that number.", "Divide by the cost of one mile to find how many."); they have no digits, so the lint let them by.
    operations = ('halve it.', 'turn it upside down', 'divide by that number', 'divide by the cost of one')
    for key in ('pyth.diagonal_squared_not_halved', 'num.reciprocal_same', 'af.undefined_not_divided', 'lin.cost_not_divided'):
        text = misconceptions.MESSAGES[key].lower()
        assert not any(op in text for op in operations), f'{key} tells the pupil the operation to apply: {text!r}'
    # the rules bite on this surface (a dash in other system copy is only a note)
    def bad(text):
        it = voice.Item('(test)', 1, 'system', 'system_hint', 'line', text)
        return {v.rule for v in voice.lint([it]) if v.level in ('error', 'warn')}

    assert not bad('Check the sign. Look again at each step.')
    assert 'characters' in bad('Check the sign \u2014 look again.')
    assert 'characters' in bad('Check the sign \U0001F600')
    assert 'length' in bad('Check the sign. ' + 'x' * 110)
    assert 'hint copy' in bad('Check the sign. Look again. Then try once more.')
    assert 'hint copy' in bad('That is wrong. Check the sign.')
    assert 'hint copy' in bad('It is a careless slip. Check the sign.')
    assert 'hint copy' in bad('Just check the sign.')
    assert 'banned phrase' in bad('This one is easy. Check the sign.')
    assert 'US spelling' in bad('Check the color of the sign.')
    assert 'long word' in bad('Check the representation of the sign.')
    assert not bad('Take the square root of the hypotenuse squared.')
    assert 'reading level' in bad('Photosynthesis demonstrates considerable evolutionary adaptations across environments today.')
    assert 'system voice' in bad('I think the sign is out.')


_REF_LINE = re.compile(r'(`[^`\s]+?):\d+`')


def _without_line_numbers(text):
    return _REF_LINE.sub(r'\1`', text.replace('\r\n', '\n'))


def test_inventory_doc_in_sync():
    """Fails when any copy, voice, surface or count drifts. A shift of line numbers alone (an unrelated
    edit higher up in app.py or site.js) only prints a notice, so other work does not trip this smoke."""
    in_sync, new = voice.update_doc(write=False)
    if in_sync:
        return
    current = voice.DOC_PATH.read_text(encoding='utf-8')
    if _without_line_numbers(current) == _without_line_numbers(new):
        print('  notice: Appendix A line numbers have shifted (copy unchanged); '
              '`python scripts/test_zorp_voice_smoke.py --write` refreshes them')
        return
    raise AssertionError('docs/ZORP_CHARM.md Appendix A is out of date: run '
                         '`python scripts/test_zorp_voice_smoke.py --write` and commit the regenerated section')


TESTS = (
    test_inventory_extracts,
    test_every_marked_template_is_expected,
    test_limits_match_the_plan,
    test_banned_phrases,
    test_british_spelling,
    test_practise_verb,
    test_lengths_per_surface,
    test_reading_level,
    test_long_words,
    test_no_emoji_or_dashes_in_zorp_lines,
    test_exclamation_budget,
    test_system_voice_has_no_first_person,
    test_voice_split_by_source,
    test_glossary_terms,
    test_dismiss_labels_neutral,
    test_bot_voice_and_note,
    test_welcome_line_is_truthful,
    test_guide_js_fallbacks_match_catalog,
    test_lint_catches_each_rule,
    test_hint_messages,
    test_inventory_doc_in_sync,
)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if '--write' in argv:
        in_sync, _ = voice.update_doc(write=True)
        print('Appendix A already up to date.' if in_sync else 'Appendix A regenerated in docs/ZORP_CHARM.md.')
        return
    for fn in TESTS:
        fn()
    items = _items()
    notes = [v for v in voice.lint(items) if v.level == 'info']
    print(f'  {len(notes)} system-string notes (dash or symbol; listed in the plan, not failures)')
    print('Zorp voice smoke (E9 Phase 3, enforcing) passed.')


if __name__ == '__main__':
    main()
