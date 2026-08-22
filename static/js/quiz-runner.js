(function () {
  'use strict';

  function initLessonQuizRunner() {
    var root = document.querySelector('[data-quiz-runner]') || document.getElementById('lesson-quiz-runner');
    var form = root ? (root.querySelector('form.quiz-runner-form') || document.getElementById('lesson-quiz-form')) : null;
    if (!root || !form) return;

    var steps = Array.prototype.slice.call(form.querySelectorAll('.quiz-runner-step'));
    var checkBtn = document.getElementById('quiz-runner-check');
    var counterEl = document.getElementById('quiz-runner-counter');
    var segments = document.querySelectorAll('.quiz-runner-segment');
    var total = steps.length;
    var current = 0;
    var submitLabel = root.getAttribute('data-submit-label') || 'Submit quiz';

    function afterCheckLabel() {
      return current === total - 1 ? submitLabel : 'Next question';
    }

    function updateChrome() {
      if (counterEl) counterEl.textContent = (current + 1) + ' / ' + total;
      segments.forEach(function (seg, index) {
        seg.classList.toggle('is-current', index === current);
      });
    }

    function showStep(index) {
      steps.forEach(function (step, i) {
        step.hidden = i !== index;
      });
      current = index;
      updateChrome();
      var active = steps[index];
      if (!active) return;
      var selected = active.querySelector('.quiz-runner-option.is-selected');
      if (checkBtn) {
        checkBtn.disabled = !selected;
        checkBtn.textContent = active.dataset.checked === '1' ? afterCheckLabel() : 'Check';
      }
    }

    function markSegment(index, state) {
      var seg = segments[index];
      if (!seg) return;
      seg.classList.remove('is-done', 'is-correct', 'is-wrong', 'is-current');
      if (state === 'correct') seg.classList.add('is-correct');
      else if (state === 'wrong') seg.classList.add('is-wrong');
      else seg.classList.add('is-done');
    }

    function revealStep(step, letter) {
      var correct = (step.dataset.correct || '').trim().charAt(0).toUpperCase();
      var isCorrect = letter === correct;
      step.querySelectorAll('.quiz-runner-option').forEach(function (btn) {
        var opt = (btn.dataset.letter || '').trim().charAt(0).toUpperCase();
        btn.disabled = true;
        btn.classList.remove('is-selected');
        if (opt === correct) btn.classList.add('is-correct');
        else if (opt === letter) btn.classList.add('is-wrong');
      });
      markSegment(current, isCorrect ? 'correct' : 'wrong');
      step.dataset.checked = '1';
      if (checkBtn) {
        checkBtn.disabled = false;
        checkBtn.textContent = afterCheckLabel();
      }
      return isCorrect;
    }

    form.querySelectorAll('.quiz-runner-option').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var step = btn.closest('.quiz-runner-step');
        if (!step || step.dataset.checked === '1') return;
        var letter = (btn.dataset.letter || '').trim().charAt(0).toUpperCase();
        step.querySelectorAll('.quiz-runner-option').forEach(function (b) {
          b.classList.remove('is-selected');
        });
        btn.classList.add('is-selected');
        var hidden = step.querySelector('input[type="hidden"][name^="answer_"]');
        if (hidden) hidden.value = letter;
        if (checkBtn) checkBtn.disabled = false;
      });
    });

    if (checkBtn) {
      checkBtn.addEventListener('click', function () {
        var step = steps[current];
        if (!step) return;
        if (step.dataset.checked !== '1') {
          var selected = step.querySelector('.quiz-runner-option.is-selected');
          if (!selected) return;
          var letter = (selected.dataset.letter || '').trim().charAt(0).toUpperCase();
          revealStep(step, letter);
          return;
        }
        if (current < total - 1) {
          showStep(current + 1);
          return;
        }
        var missing = [];
        steps.forEach(function (s, idx) {
          var input = s.querySelector('input[type="hidden"][name^="answer_"]');
          if (!input || !input.value) missing.push(idx + 1);
        });
        if (missing.length) {
          window.alert('Please answer all ' + total + ' questions before submitting.');
          showStep(missing[0] - 1);
          return;
        }
        form.submit();
      });
    }

    showStep(0);
  }

  function initQuicktestRunner() {
    var root = document.getElementById('quicktest-quiz-runner');
    var form = document.getElementById('quicktest-next-form');
    var checkBtn = document.getElementById('quiz-runner-check');
    if (!root || !form || !checkBtn) return;

    var mcq = document.getElementById('mcq-options');
    var fr = root.querySelector('.free-response-inline');
    var segments = root.querySelectorAll('.quiz-runner-segment');
    var current = parseInt(root.getAttribute('data-current') || '1', 10);
    var total = parseInt(root.getAttribute('data-total') || '1', 10);
    var answered = false;
    var checking = false;

    function isLastQuestion() {
      return current >= total;
    }

    function nextLabel() {
      return isLastQuestion() ? 'Finish test' : 'Next question';
    }

    function markSegment(correct) {
      var seg = segments[current - 1];
      if (!seg) return;
      seg.classList.remove('is-current', 'is-done');
      seg.classList.add(correct ? 'is-correct' : 'is-wrong');
    }

    function collectState() {
      if (window.pbQuicktest && window.pbQuicktest.collectState) {
        return window.pbQuicktest.collectState();
      }
      return { userAnswer: '', checked: false, correct: null };
    }

    function hasDraftAnswer() {
      var state = collectState();
      return Boolean((state.userAnswer || '').trim());
    }

    function refreshDraftButton() {
      if (answered || checking) return;
      checkBtn.disabled = !hasDraftAnswer();
      checkBtn.textContent = 'Check';
    }

    function setAnswered(detail) {
      answered = true;
      checking = false;
      markSegment(Boolean(detail && detail.correct === true));
      checkBtn.disabled = false;
      checkBtn.textContent = nextLabel();
    }

    function triggerFreeResponseCheck() {
      if (!fr || checking) return;
      var hiddenCheck = fr.querySelector('.free-response-check-btn, .free-response-field-check-btn');
      if (!hiddenCheck) return;
      checking = true;
      checkBtn.disabled = true;
      hiddenCheck.click();
    }

    function advanceQuicktest() {
      if (window.pbQuicktest && window.pbQuicktest.syncFormFields) {
        window.pbQuicktest.syncFormFields();
      }
      if (form.requestSubmit) {
        form.requestSubmit();
      } else {
        form.submit();
      }
    }

    checkBtn.addEventListener('click', function () {
      if (answered) {
        advanceQuicktest();
        return;
      }
      if (mcq) {
        if (!hasDraftAnswer()) return;
        var state = collectState();
        if (state.checked) {
          setAnswered(state);
        }
        return;
      }
      if (fr) {
        var stateFr = collectState();
        if (stateFr.checked) {
          setAnswered(stateFr);
          return;
        }
        triggerFreeResponseCheck();
      }
    });

    document.addEventListener('pb-quicktest-checked', function (event) {
      var detail = event.detail || {};
      if (!detail.checked) {
        checking = false;
        refreshDraftButton();
        return;
      }
      setAnswered(detail);
    });

    document.addEventListener('pb-quicktest-check-failed', function () {
      checking = false;
      refreshDraftButton();
    });

    if (fr) {
      fr.querySelectorAll('input, textarea, select').forEach(function (input) {
        input.addEventListener('input', refreshDraftButton);
        input.addEventListener('change', refreshDraftButton);
      });
    }

    if (mcq) {
      mcq.querySelectorAll('.mcq-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
          window.setTimeout(refreshDraftButton, 0);
        });
      });
    }

    var initial = collectState();
    if (initial.checked) {
      setAnswered(initial);
    } else {
      refreshDraftButton();
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initLessonQuizRunner();
    initQuicktestRunner();
  });
})();
