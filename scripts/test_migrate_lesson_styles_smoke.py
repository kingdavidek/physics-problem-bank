"""U6.3 — lesson style migrator is dry-run, idempotent, and skips radioactivity.

Run: python scripts/test_migrate_lesson_styles_smoke.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import migrate_lesson_styles as mig  # noqa: E402

SAMPLE = '''{% extends "base.html" %}
{% block content %}
<div style="max-width:860px;margin:0 auto;padding:12px;">
  <div style="background:linear-gradient(135deg,#1a6fa8,#0e4e7a);color:#fff;border-radius:10px;padding:22px 28px;margin-bottom:20px;">
    <h1 style="margin:0 0 6px;font-size:1.7rem;">Number</h1>
    <p style="margin:0;opacity:.9;font-size:.97rem;">GCSE Mathematics</p>
    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;">
      <span style="background:rgba(255,255,255,.18);border-radius:20px;padding:3px 12px;font-size:.8rem;">AQA</span>
    </div>
  </div>
  <details open style="border:1px solid #d4e6f1;border-radius:8px;margin-bottom:12px;overflow:hidden;">
    <summary style="background:#eaf4fb;padding:13px 16px;cursor:pointer;font-size:1.05rem;font-weight:700;color:#1a6fa8;list-style:none;display:flex;align-items:center;gap:10px;">
      <span style="background:#1a6fa8;color:#fff;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">1</span>
      Place Value
      <span style="font-size:0.65rem; margin-left:8px; background:#e8f4fd; color:#1a6fa8; padding:2px 6px; border-radius:10px;">All Exam Boards</span>
      <span style="font-size:0.65rem; margin-left:6px; background:#fef4e8; color:#8a5300; padding:2px 6px; border-radius:10px;">Year 9</span>
    </summary>
    <div style="padding:18px 20px;background:#fff;">
      <ul style="line-height:1.9;">
        <li>Keep this teaching copy</li>
      </ul>
      <div style="margin-top:18px; padding:14px 16px; background:var(--color-surface-2); border-radius:var(--radius); border-left:4px solid #1a6fa8;">
        <p style="margin:0 0 10px; font-weight:600;">Quick Check</p>
        <div class="mcq-inline" data-correct="A">
          <p style="margin:0 0 10px;">A question?</p>
          <p class="mcq-feedback" style="margin-top:8px; font-weight:600;"></p>
        </div>
      </div>
    </div>
  </details>
  <div style="text-align:center;margin-top:20px;padding:16px;background:#f0f9ff;border-radius:8px;">
    <p style="margin:0 0 10px;font-weight:600;color:#1a6fa8;">Ready to practise?</p>
  </div>
</div>
<style>
  .keep-me { color: #1a6fa8; }
</style>
{% endblock %}
'''


def test_sample_maps_known_styles_and_keeps_copy():
    updated, mapped, unmapped = mig.migrate_text(SAMPLE)
    assert mapped >= 15
    assert unmapped == []
    assert 'Keep this teaching copy' in updated
    assert 'class="lesson-shell"' in updated
    assert 'class="lesson-hero"' in updated
    assert 'class="hero-sub"' in updated
    assert 'class="hero-pills"' in updated
    assert 'class="hero-pill"' in updated
    assert 'class="lesson-section"' in updated
    assert 'class="lesson-section-summary"' in updated
    assert 'class="lesson-section-chip"' in updated
    assert 'lesson-tag--warn' in updated
    assert 'class="lesson-section-body"' in updated
    assert 'class="lesson-quickcheck"' in updated
    assert 'class="lesson-quickcheck-title"' in updated
    assert 'class="mcq-inline"' in updated
    assert 'class="lesson-practice-cta"' in updated
    assert 'style="' not in updated.split('<style>')[0]
    assert '.keep-me { color: #1a6fa8; }' in updated
    again, mapped2, unmapped2 = mig.migrate_text(updated)
    assert again == updated
    assert mapped2 == 0
    assert unmapped2 == []


def test_mensuration_is_already_migrated_noop():
    src = (ROOT / 'templates' / 'gcse_maths_mensuration_lesson.html').read_text(encoding='utf-8')
    updated, mapped, unmapped = mig.migrate_text(src)
    assert updated == src
    assert mapped == 0
    assert unmapped == []


def test_radioactivity_is_skipped_by_default_list():
    assert 'gcse_physics_radioactivity_lesson.html' in mig.SKIP_FILES
    listed = [p.name for p in mig.lesson_files(None)]
    assert 'gcse_maths_number_lesson.html' in listed
    assert 'gcse_physics_radioactivity_lesson.html' in listed


def test_applied_lessons_are_idempotent():
    path = ROOT / 'templates' / 'gcse_maths_number_lesson.html'
    before = path.read_text(encoding='utf-8')
    assert 'class="lesson-shell"' in before
    updated, mapped, unmapped = mig.migrate_text(before)
    assert updated == before
    assert mapped == 0
    assert unmapped == []


if __name__ == '__main__':
    test_sample_maps_known_styles_and_keeps_copy()
    test_mensuration_is_already_migrated_noop()
    test_radioactivity_is_skipped_by_default_list()
    test_applied_lessons_are_idempotent()
    print('U6.3 migrator smoke OK')
