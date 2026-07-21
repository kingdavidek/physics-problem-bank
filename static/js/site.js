/**
 * Problem generator: cascade Level → Subject → Topic so only valid combinations show.
 * Also syncs Quick Test hidden fields and handles MCQ answer buttons on the index page.
 */
(function () {
  'use strict';

  function setOptionVisibility(selectEl, predicate) {
    let firstVisible = null;
    for (const opt of selectEl.options) {
      const ok = predicate(opt);
      opt.hidden = !ok;
      opt.disabled = !ok;
      if (ok && !firstVisible) firstVisible = opt;
    }
    return firstVisible;
  }

  function subjectPredicate(level) {
    return function (opt) {
      return opt.dataset.level === level;
    };
  }

  function topicPredicate(level, subject) {
    return function (opt) {
      return opt.dataset.level === level && opt.dataset.subject === subject;
    };
  }

  function ensureValidSelection(selectEl, preferValue) {
    const cur = selectEl.selectedOptions[0];
    if (cur && !cur.disabled) return;

    if (preferValue != null && preferValue !== '') {
      const match = [...selectEl.options].find(
        function (o) { return !o.disabled && o.value === preferValue; }
      );
      if (match) {
        match.selected = true;
        return;
      }
    }
    const first = [...selectEl.options].find(function (o) { return !o.disabled; });
    if (first) first.selected = true;
  }

  function initGeneratorForm() {
    var levelSel = document.getElementById('level-select');
    var subjectSel = document.getElementById('subject-select');
    var topicSel = document.getElementById('topic-select');
    if (!levelSel || !subjectSel || !topicSel) return;

    function syncTopicDropdown() {
      var level = levelSel.value;
      var subject = subjectSel.value;
      setOptionVisibility(topicSel, topicPredicate(level, subject));
      ensureValidSelection(topicSel, topicSel.dataset.pendingTopic || topicSel.value);
      delete topicSel.dataset.pendingTopic;
    }

    function syncSubjectDropdown() {
      var level = levelSel.value;
      var prevSubject = subjectSel.value;
      setOptionVisibility(subjectSel, subjectPredicate(level));
      ensureValidSelection(subjectSel, prevSubject);
      if (subjectSel.value !== prevSubject) {
        topicSel.dataset.pendingTopic = '';
      }
      syncTopicDropdown();
    }

    function onLevelChange() {
      var prevTopic = topicSel.value;
      topicSel.dataset.pendingTopic = prevTopic;
      syncSubjectDropdown();
    }

    function onSubjectChange() {
      var prevTopic = topicSel.value;
      topicSel.dataset.pendingTopic = prevTopic;
      syncTopicDropdown();
    }

    levelSel.addEventListener('change', onLevelChange);
    subjectSel.addEventListener('change', onSubjectChange);

    syncSubjectDropdown();
  }

  function syncProblemActionHiddenFields() {
    var levelSel = document.getElementById('level-select');
    var subjectSel = document.getElementById('subject-select');
    var topicSel = document.getElementById('topic-select');
    var modeSel = document.getElementById('mode-select');
    var diffSel = document.getElementById('difficulty');
    if (!levelSel || !subjectSel || !topicSel || !modeSel || !diffSel) return;

    var fields = [
      ['qt-level', 'qt-subject', 'qt-topic', 'qt-mode', 'qt-difficulty'],
      ['rr-level', 'rr-subject', 'rr-topic', 'rr-mode', 'rr-difficulty'],
    ];
    var values = [
      levelSel.value,
      subjectSel.value,
      topicSel.value,
      modeSel.value,
      diffSel.value,
    ];
    fields.forEach(function (ids) {
      ids.forEach(function (id, i) {
        var el = document.getElementById(id);
        if (el) el.value = values[i];
      });
    });
  }

  function syncQuickTestHiddenFields() {
    syncProblemActionHiddenFields();
  }

  function initQuickTestForm() {
    var qtf = document.getElementById('quicktest-form');
    if (qtf) {
      qtf.addEventListener('submit', function () {
        syncProblemActionHiddenFields();
      });
    }
    var rrf = document.getElementById('reroll-form');
    if (rrf) {
      rrf.addEventListener('submit', function () {
        syncProblemActionHiddenFields();
      });
    }
    var main = document.getElementById('main-form');
    if (main) {
      main.addEventListener('change', syncProblemActionHiddenFields);
    }
    syncProblemActionHiddenFields();
  }

  function readFreeResponseUserAnswer(block) {
    if (!block) return '';
    var answerType = (block.getAttribute('data-answer-type') || 'number').trim();
    if (answerType === 'standard_form') {
      var coeff = block.querySelector('.free-response-input-coeff');
      var exp = block.querySelector('.free-response-input-exp');
      if (!coeff || !exp) return '';
      return (coeff.value || '').trim() + '|' + (exp.value || '').trim();
    }
    if (answerType === 'number_pair') {
      var a = block.querySelector('.free-response-input-a');
      var b = block.querySelector('.free-response-input-b');
      if (!a || !b) return '';
      return (a.value || '').trim() + '|' + (b.value || '').trim();
    }
    if (answerType === 'power') {
      var base = block.querySelector('.free-response-input-base');
      var index = block.querySelector('.free-response-input-index');
      if (!base || !index) return '';
      return (base.value || '').trim() + '|' + (index.value || '').trim();
    }
    if (answerType === 'number_fields') {
      var fields = block.querySelectorAll('.free-response-input-field');
      var correctRaw = (block.getAttribute('data-correct-raw') || '').trim();
      var sep = correctRaw.indexOf('\x1e') >= 0 ? '\x1e' : '|';
      return Array.prototype.map.call(fields, function (input) {
        return (input.value || '').trim();
      }).join(sep);
    }
    var single = block.querySelector('.free-response-input');
    return single ? (single.value || '').trim() : '';
  }

  function freeResponseCheckState(block) {
    if (!block || block.hidden) {
      return { checked: false, correct: null, userAnswer: '' };
    }
    var answerType = (block.getAttribute('data-answer-type') || 'number').trim();
    if (answerType === 'number_fields') {
      var fields = block.querySelectorAll('.free-response-input-field');
      if (!fields.length) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var checked = Array.prototype.some.call(fields, function (input) {
        return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
      });
      var allCorrect = checked && Array.prototype.every.call(fields, function (input) {
        return input.classList.contains('is-correct');
      });
      return {
        checked: checked,
        correct: checked ? allCorrect : null,
        userAnswer: readFreeResponseUserAnswer(block),
      };
    }
    var inputs = freeResponseInputs(block);
    var checked = inputs.some(function (input) {
      return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
    });
    var correct = checked && inputs.length > 0 && inputs.every(function (input) {
      return input.classList.contains('is-correct');
    });
    return {
      checked: checked,
      correct: checked ? correct : null,
      userAnswer: readFreeResponseUserAnswer(block),
    };
  }

  function collectQuickTestAnswerState() {
    var mcq = document.getElementById('mcq-options');
    if (mcq) {
      var choice = (mcq.dataset.userChoice || '').trim();
      if (!choice) {
        return { userAnswer: '', checked: false, correct: null };
      }
      var correctLetter = ((mcq.getAttribute('data-correct') || '').trim()).charAt(0);
      return {
        userAnswer: choice,
        checked: true,
        correct: choice === correctLetter,
      };
    }
    var fr = document.querySelector('.free-response-inline');
    var frState = freeResponseCheckState(fr);
    return {
      userAnswer: frState.userAnswer,
      checked: frState.checked,
      correct: frState.correct,
    };
  }

  function initQuickTestNextForm() {
    var form = document.getElementById('quicktest-next-form');
    if (!form) return;
    form.addEventListener('submit', function () {
      var state = collectQuickTestAnswerState();
      var userEl = document.getElementById('qt-user-answer');
      var checkedEl = document.getElementById('qt-checked');
      var correctEl = document.getElementById('qt-correct');
      if (userEl) userEl.value = state.userAnswer || '';
      if (checkedEl) checkedEl.value = state.checked ? '1' : '0';
      if (correctEl) {
        correctEl.value = state.correct === true ? '1' : (state.correct === false ? '0' : '');
      }
    });
  }

  function resetMcqInline(block) {
    var feedback = block.querySelector('.mcq-feedback')
      || (block.parentElement && block.parentElement.querySelector('.mcq-feedback'));
    block.querySelectorAll('.mcq-btn').forEach(function (b) {
      b.disabled = false;
      b.classList.remove('is-correct', 'is-wrong');
    });
    if (feedback) {
      feedback.textContent = '';
      feedback.style.color = '';
    }
    var retryWrap = block.querySelector('.mcq-retry-wrap');
    if (retryWrap) {
      retryWrap.hidden = true;
    }
    block.dispatchEvent(new CustomEvent('mcq-reset', { bubbles: true }));
  }

  function findMcqFeedback(block) {
    return block.querySelector('.mcq-feedback')
      || (block.parentElement && block.parentElement.querySelector('.mcq-feedback'));
  }

  function persistMcqAnswer(block, userAnswer, correctAnswer, isCorrect) {
    if (!block.dataset.level) return;
    fetch('/api/v1/generator/mcq-answer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify({
        level: block.dataset.level,
        subject: block.dataset.subject,
        topic: block.dataset.topic,
        difficulty: block.dataset.difficulty || 'foundational',
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        correct: isCorrect,
      }),
    }).catch(function () {});
  }

  function wireMcqBlock(block) {
    if (!block || block.dataset.mcqInit === '1') return;

    var correctRaw = (block.getAttribute('data-correct') || block.dataset.correct || '').trim();
    if (!correctRaw) return;

    block.dataset.mcqInit = '1';
    var correctLetter = correctRaw.charAt(0);
    var feedback = findMcqFeedback(block);
    var trackable = Boolean(block.dataset.level);

    block.querySelectorAll('.mcq-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (btn.disabled) {
          return;
        }
        block.querySelectorAll('.mcq-btn').forEach(function (b) { b.disabled = true; });
        var letter = (btn.dataset.letter || '').trim().charAt(0);
        block.dataset.userChoice = letter;
        var isCorrect = letter === correctLetter;
        if (isCorrect) {
          btn.classList.add('is-correct');
          if (feedback) {
            feedback.textContent = '\u2713 Correct!';
            feedback.style.color = '#16a34a';
          }
          block.dispatchEvent(new CustomEvent('mcq-correct', { bubbles: true }));
        } else {
          btn.classList.add('is-wrong');
          block.querySelectorAll('.mcq-btn').forEach(function (b) {
            var bLetter = (b.dataset.letter || '').trim().charAt(0);
            if (bLetter === correctLetter) {
              b.classList.add('is-correct');
            }
          });
          if (feedback) {
            feedback.textContent = '\u2717 Not quite \u2014 the correct answer is highlighted.';
            feedback.style.color = '#dc2626';
          }
          showMcqRetry(block);
        }
        if (trackable && block.dataset.mcqPersisted !== '1') {
          block.dataset.mcqPersisted = '1';
          persistMcqAnswer(block, letter, correctRaw, isCorrect);
        }
      });
    });
  }

  function showMcqRetry(block) {
    var wrap = block.querySelector('.mcq-retry-wrap');
    if (!wrap) {
      wrap = document.createElement('div');
      wrap.className = 'mcq-retry-wrap';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn btn-outline mcq-retry-btn';
      btn.textContent = 'Try again';
      btn.addEventListener('click', function () {
        resetMcqInline(block);
      });
      wrap.appendChild(btn);
      block.appendChild(wrap);
    }
    wrap.hidden = false;
  }

  function initMcqInline() {
    document.querySelectorAll('.mcq-inline').forEach(wireMcqBlock);
  }

  function freeResponseInputs(block) {
    return Array.prototype.slice.call(block.querySelectorAll('.free-response-input'));
  }

  function freeResponseRowKind(row) {
    if (!row) return 'number';
    if (row.classList.contains('free-response-row--standard-form')) return 'standard_form';
    if (row.classList.contains('free-response-row--number-pair')) return 'number_pair';
    if (row.classList.contains('free-response-row--number-list')) return 'number_list';
    if (row.classList.contains('free-response-row--power')) return 'power';
    if (row.classList.contains('free-response-row--linear-equation')) return 'linear_equation';
    if (row.classList.contains('free-response-row--ratio')) return 'ratio';
    if (row.classList.contains('free-response-row--number-fields')) return 'number_fields';
    if (row.classList.contains('free-response-row--pi-multiple')) return 'pi_multiple';
    if (row.classList.contains('free-response-row--surd')) return 'surd';
    if (row.classList.contains('free-response-row--algebraic')) return 'algebraic';
    if (row.classList.contains('free-response-row--algebraic-fraction')) return 'algebraic_fraction';
    return 'number';
  }

  function freeResponseRowHtml(block, answerType) {
    var formatHint = block.getAttribute('data-format-hint') || '';
    var labelA = block.getAttribute('data-label-a') || 'First value';
    var labelB = block.getAttribute('data-label-b') || 'Second value';
    var pairSep = block.getAttribute('data-pair-sep') || 'and';
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };

    if (answerType === 'standard_form') {
      return (
        '<div class="free-response-row free-response-row--standard-form">' +
        '<input type="text" class="free-response-input free-response-input-coeff" placeholder="e.g. 3.2" autocomplete="off" inputmode="decimal" aria-label="Standard form coefficient">' +
        '<span class="free-response-sf-sep" aria-hidden="true">× 10^</span>' +
        '<input type="text" class="free-response-input free-response-input-exp" placeholder="e.g. 5" autocomplete="off" inputmode="numeric" aria-label="Standard form power">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'number_pair') {
      return (
        '<div class="free-response-row free-response-row--number-pair">' +
        '<input type="text" class="free-response-input free-response-input-a" placeholder="' + esc(labelA) + '" autocomplete="off" inputmode="decimal" aria-label="' + esc(labelA) + '">' +
        '<span class="free-response-pair-sep" aria-hidden="true">' + esc(pairSep) + '</span>' +
        '<input type="text" class="free-response-input free-response-input-b" placeholder="' + esc(labelB) + '" autocomplete="off" inputmode="decimal" aria-label="' + esc(labelB) + '">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'number_list') {
      var listPh = formatHint || 'Enter numbers separated by commas';
      return (
        '<div class="free-response-row free-response-row--number-list">' +
        '<input type="text" class="free-response-input free-response-input-list" placeholder="' + esc(listPh) + '" autocomplete="off" inputmode="decimal" aria-label="Your answer">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'power') {
      return (
        '<div class="free-response-row free-response-row--power">' +
        '<input type="text" class="free-response-input free-response-input-base" placeholder="e.g. 2" autocomplete="off" inputmode="numeric" aria-label="Base">' +
        '<span class="free-response-power-sep" aria-hidden="true">^</span>' +
        '<input type="text" class="free-response-input free-response-input-index" placeholder="e.g. 12" autocomplete="off" inputmode="numeric" aria-label="Index">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'ratio' || answerType === 'ratio_exact') {
      var ratioPh = formatHint || 'e.g. 3:5';
      return (
        '<div class="free-response-row free-response-row--ratio">' +
        '<input type="text" class="free-response-input free-response-input-ratio" placeholder="' + esc(ratioPh) + '" autocomplete="off" inputmode="text" aria-label="Your ratio">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'linear_equation') {
      var eqPh = formatHint || 'e.g. y = 2x + 3';
      return (
        '<div class="free-response-row free-response-row--linear-equation">' +
        '<input type="text" class="free-response-input free-response-input-linear-equation" placeholder="' + esc(eqPh) + '" autocomplete="off" inputmode="text" aria-label="Linear equation">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'number_fields') {
      var labels = [];
      var fieldTypes = [];
      try {
        labels = JSON.parse(block.getAttribute('data-answer-labels') || '[]');
      } catch (err) {
        labels = [];
      }
      try {
        fieldTypes = JSON.parse(block.getAttribute('data-field-types') || '[]');
      } catch (err2) {
        fieldTypes = [];
      }
      function fieldPlaceholder(fieldType) {
        if (fieldType === 'keyword') return 'e.g. positive, negative, or none';
        if (fieldType === 'linear_equation') return 'e.g. y = 2x + 3';
        if (fieldType === 'number_estimate') return 'Your estimate from the graph';
        if (fieldType === 'ratio' || fieldType === 'ratio_exact') return 'e.g. 3:5';
        if (fieldType === 'binary') return 'e.g. 1101';
        if (fieldType === 'hex') return 'e.g. FF';
        return 'Number or fraction';
      }
      var rows = labels.map(function (label, index) {
        var safeLabel = esc(label);
        var ph = esc(fieldPlaceholder(fieldTypes[index] || 'number'));
        return (
          '<div class="free-response-field-row">' +
          '<label class="free-response-field">' +
          '<span class="free-response-field-label">' + safeLabel + '</span>' +
          '<input type="text" class="free-response-input free-response-input-field" placeholder="' + ph + '" autocomplete="off" inputmode="text" aria-label="' + safeLabel + '">' +
          '</label>' +
          '<button type="button" class="btn free-response-check-btn free-response-field-check-btn">Check</button>' +
          '<p class="free-response-field-feedback" aria-live="polite"></p>' +
          '</div>'
        );
      }).join('');
      return (
        '<div class="free-response-row free-response-row--number-fields">' +
        '<div class="free-response-fields-stack">' + rows + '</div>' +
        '</div>'
      );
    }
    if (answerType === 'pi_multiple') {
      var piPh = formatHint || 'e.g. 4';
      return (
        '<div class="free-response-row free-response-row--pi-multiple">' +
        '<input type="text" class="free-response-input free-response-input-pi" placeholder="' + esc(piPh) + '" autocomplete="off" inputmode="text" aria-label="Coefficient of pi">' +
        '<span class="free-response-pi-sep" aria-hidden="true">π</span>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'surd') {
      var surdPh = formatHint || 'e.g. √113';
      return (
        '<div class="free-response-row free-response-row--surd">' +
        '<input type="text" class="free-response-input free-response-input-surd" placeholder="' + esc(surdPh) + '" autocomplete="off" inputmode="text" aria-label="Surd answer">' +
        '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'algebraic') {
      var algPh = formatHint || 'e.g. a - b';
      return (
        '<div class="free-response-row free-response-row--algebraic">' +
        '<input type="text" class="free-response-input free-response-input-algebraic" placeholder="' + esc(algPh) + '" autocomplete="off" inputmode="text" aria-label="Algebraic answer">' +
        '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'algebraic_fraction') {
      var fracNumPh = 'e.g. 6 − 3√3';
      var hintLower = formatHint.toLowerCase();
      if (hintLower.indexOf('+ √') !== -1 || hintLower.indexOf('+√') !== -1) {
        var sumMatch = formatHint.match(/√\d+\s*\+\s*√\d+/);
        if (sumMatch) {
          fracNumPh = 'e.g. ' + sumMatch[0].replace(/\s+/g, ' ');
        } else {
          fracNumPh = 'e.g. √18 + √10';
        }
      }
      return (
        '<div class="free-response-row free-response-row--algebraic-fraction">' +
        '<div class="free-response-fraction-stack" aria-label="Fraction answer">' +
        '<input type="text" class="free-response-input free-response-input-alg-frac-num" placeholder="' + esc(fracNumPh) + '" autocomplete="off" inputmode="text" aria-label="Numerator">' +
        '<span class="free-response-fraction-bar" aria-hidden="true"></span>' +
        '<input type="text" class="free-response-input free-response-input-alg-frac-den" placeholder="1 if none" autocomplete="off" inputmode="numeric" aria-label="Denominator">' +
        '</div>' +
        '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    var placeholder = formatHint || 'Enter a number';
    var numberInputMode = formatHint.toLowerCase().indexOf('fraction') !== -1
      ? 'text'
      : 'decimal';
    return (
      '<div class="free-response-row free-response-row--number">' +
      '<input type="text" class="free-response-input" placeholder="' + esc(placeholder) + '" autocomplete="off" inputmode="' + numberInputMode + '" aria-label="Your answer">' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function insertAtCursor(input, text) {
    if (!input) return;
    var start = input.selectionStart;
    var end = input.selectionEnd;
    var value = input.value || '';
    if (typeof start === 'number' && typeof end === 'number') {
      input.value = value.slice(0, start) + text + value.slice(end);
      var pos = start + text.length;
      input.setSelectionRange(pos, pos);
    } else {
      input.value = value + text;
    }
    input.focus();
  }

  function wireSurdInsertButton(block) {
    var btn = block.querySelector('.free-response-surd-btn');
    var input = block.querySelector('.free-response-input-surd')
      || block.querySelector('.free-response-input-algebraic')
      || block.querySelector('.free-response-input-alg-frac-num');
    if (!btn || !input || btn.dataset.surdInit === '1') return;
    btn.dataset.surdInit = '1';
    btn.addEventListener('click', function () {
      if (input.disabled) return;
      insertAtCursor(input, '√');
    });
  }

  function ensureFreeResponseRow(block, answerType) {
    var current = block.querySelector('.free-response-row');
    var rowKind = (answerType === 'ratio' || answerType === 'ratio_exact') ? 'ratio'
      : (answerType === 'linear_equation') ? 'linear_equation'
      : answerType;
    if (!current || freeResponseRowKind(current) !== rowKind) {
      if (current) current.remove();
      var feedback = block.querySelector('.free-response-feedback');
      var wrap = document.createElement('div');
      wrap.innerHTML = freeResponseRowHtml(block, answerType);
      var row = wrap.firstChild;
      if (feedback) {
        block.insertBefore(row, feedback);
      } else {
        block.appendChild(row);
      }
    }
  }

  function setFreeResponseInputMode(block, answerType) {
    ensureFreeResponseRow(block, answerType);
    if (answerType === 'surd' || answerType === 'algebraic' || answerType === 'algebraic_fraction') {
      wireSurdInsertButton(block);
    }
  }

  function resetFreeResponseBlock(block) {
    freeResponseInputs(block).forEach(function (input) {
      input.value = '';
      input.disabled = false;
      input.classList.remove('is-correct', 'is-wrong');
    });
    block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
      btn.disabled = false;
    });
    block.querySelectorAll('.free-response-field-feedback').forEach(function (el) {
      el.textContent = '';
      el.style.color = '';
    });
    var feedback = block.querySelector('.free-response-feedback');
    if (feedback) {
      feedback.textContent = '';
      feedback.style.color = '';
    }
    delete block.dataset.freeResponsePersisted;
  }

  function newAttemptGroupId() {
    return 'g_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 9);
  }

  function splitNumberFieldCorrectParts(correctRaw) {
    if (!correctRaw) return [];
    if (correctRaw.indexOf('\x1e') >= 0) {
      return correctRaw.split('\x1e');
    }
    return correctRaw.split('|');
  }

  function wireNumberFieldsFreeResponse(block, correctRaw, trackable) {
    var correctParts = splitNumberFieldCorrectParts(correctRaw);
    var fieldRows = block.querySelectorAll('.free-response-field-row');
    var blockFeedback = block.querySelector('.free-response-feedback');
    var partTotal = correctParts.length;
    if (trackable && !block.dataset.attemptGroupId) {
      block.dataset.attemptGroupId = newAttemptGroupId();
    }
    var fieldTypes = [];
    try {
      fieldTypes = JSON.parse(block.getAttribute('data-field-types') || '[]');
    } catch (err) {
      fieldTypes = [];
    }

    function allFieldsCorrect() {
      var inputs = block.querySelectorAll('.free-response-input-field');
      if (!inputs.length) return false;
      return Array.prototype.every.call(inputs, function (input) {
        return input.disabled && input.classList.contains('is-correct');
      });
    }

    function maybePersistAllFields() {
      if (!allFieldsCorrect()) return;
      if (blockFeedback) {
        blockFeedback.textContent = '\u2713 All parts correct!';
        blockFeedback.style.color = '#16a34a';
      }
    }

    fieldRows.forEach(function (row, index) {
      var input = row.querySelector('.free-response-input-field');
      var checkBtn = row.querySelector('.free-response-field-check-btn');
      var fieldFeedback = row.querySelector('.free-response-field-feedback');
      if (!input || !checkBtn) return;

      function submitField() {
        if (input.disabled && input.classList.contains('is-correct')) return;

        var userValue = (input.value || '').trim();
        if (!userValue) {
          if (fieldFeedback) {
            fieldFeedback.textContent = 'Enter an answer.';
            fieldFeedback.style.color = '#dc2626';
          }
          return;
        }

        var fieldCorrect = correctParts[index] || '';
        var fieldType = fieldTypes[index] || 'number';
        checkBtn.disabled = true;
        input.disabled = true;

        var body = {
          user_answer: userValue,
          correct_answer_raw: fieldCorrect,
          answer_type: fieldType,
        };
        if (trackable) {
          body.level = block.dataset.level;
          body.subject = block.dataset.subject;
          body.topic = block.dataset.topic;
          body.difficulty = block.dataset.difficulty || 'foundational';
          if (block.dataset.attemptGroupId) {
            body.attempt_group_id = block.dataset.attemptGroupId;
            body.part_index = index;
            body.part_total = partTotal;
          }
        }

        fetch('/api/v1/problems/check', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },
          credentials: 'same-origin',
          body: JSON.stringify(body),
        })
          .then(function (response) {
            return response.json().then(function (data) {
              if (!response.ok) {
                var err = new Error(data.error || 'Check failed');
                err.data = data;
                throw err;
              }
              return data;
            });
          })
          .then(function (data) {
            input.classList.remove('is-correct', 'is-wrong');
            if (data.correct) {
              input.classList.add('is-correct');
              input.disabled = true;
              checkBtn.disabled = true;
              if (fieldFeedback) {
                fieldFeedback.textContent = '\u2713 ' + (data.feedback || 'Correct!');
                fieldFeedback.style.color = '#16a34a';
              }
              maybePersistAllFields();
            } else {
              input.classList.add('is-wrong');
              input.disabled = false;
              checkBtn.disabled = false;
              if (fieldFeedback) {
                fieldFeedback.textContent = '\u2717 ' + (data.feedback || 'Not quite \u2014 try again.');
                fieldFeedback.style.color = '#dc2626';
              }
            }
          })
          .catch(function (err) {
            input.disabled = false;
            checkBtn.disabled = false;
            if (fieldFeedback) {
              fieldFeedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
              fieldFeedback.style.color = '#dc2626';
            }
          });
      }

      checkBtn.addEventListener('click', submitField);
      input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          submitField();
        }
      });
    });
  }

  function wireFreeResponseBlock(block) {
    if (!block || block.dataset.freeResponseInit === '1') return;

    var correctRaw = (block.getAttribute('data-correct-raw') || block.dataset.correctRaw || '').trim();
    if (!correctRaw) return;

    block.dataset.freeResponseInit = '1';
    var answerType = (block.getAttribute('data-answer-type') || block.dataset.answerType || 'number').trim();
    setFreeResponseInputMode(block, answerType);

    var trackable = Boolean(block.dataset.level);

    if (answerType === 'number_fields') {
      wireNumberFieldsFreeResponse(block, correctRaw, trackable);
      return;
    }

    var checkBtn = block.querySelector('.free-response-check-btn');
    var feedback = block.querySelector('.free-response-feedback');
    if (!checkBtn) return;

    function activeInputs() {
      if (answerType === 'standard_form') {
        return {
          coeff: block.querySelector('.free-response-input-coeff'),
          exp: block.querySelector('.free-response-input-exp'),
          all: freeResponseInputs(block),
        };
      }
      if (answerType === 'number_pair') {
        return {
          a: block.querySelector('.free-response-input-a'),
          b: block.querySelector('.free-response-input-b'),
          all: freeResponseInputs(block),
        };
      }
      if (answerType === 'number_list') {
        var listInput = block.querySelector('.free-response-input-list');
        return { single: listInput, all: listInput ? [listInput] : [] };
      }
      if (answerType === 'power') {
        return {
          base: block.querySelector('.free-response-input-base'),
          index: block.querySelector('.free-response-input-index'),
          all: freeResponseInputs(block),
        };
      }
      if (answerType === 'ratio' || answerType === 'ratio_exact') {
        var ratioInput = block.querySelector('.free-response-input-ratio');
        return { single: ratioInput, all: ratioInput ? [ratioInput] : [] };
      }
      if (answerType === 'linear_equation') {
        var eqInput = block.querySelector('.free-response-input-linear-equation');
        return { single: eqInput, all: eqInput ? [eqInput] : [] };
      }
      if (answerType === 'pi_multiple') {
        var piInput = block.querySelector('.free-response-input-pi');
        return { single: piInput, all: piInput ? [piInput] : [] };
      }
      if (answerType === 'surd') {
        var surdInput = block.querySelector('.free-response-input-surd');
        return { single: surdInput, all: surdInput ? [surdInput] : [] };
      }
      if (answerType === 'algebraic') {
        var algInput = block.querySelector('.free-response-input-algebraic');
        return { single: algInput, all: algInput ? [algInput] : [] };
      }
      if (answerType === 'algebraic_fraction') {
        var fracNum = block.querySelector('.free-response-input-alg-frac-num');
        var fracDen = block.querySelector('.free-response-input-alg-frac-den');
        return {
          num: fracNum,
          den: fracDen,
          all: [fracNum, fracDen].filter(Boolean),
        };
      }
      if (answerType === 'number_fields') {
        var fields = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-field')
        );
        return { fields: fields, all: fields };
      }
      var single = block.querySelector('.free-response-row--number .free-response-input');
      return { single: single, all: single ? [single] : [] };
    }

    function readUserAnswer() {
      var inputs = activeInputs();
      if (answerType === 'standard_form') {
        if (!inputs.coeff || !inputs.exp) return '';
        return (inputs.coeff.value || '').trim() + '|' + (inputs.exp.value || '').trim();
      }
      if (answerType === 'number_pair') {
        if (!inputs.a || !inputs.b) return '';
        return (inputs.a.value || '').trim() + '|' + (inputs.b.value || '').trim();
      }
      if (answerType === 'power') {
        if (!inputs.base || !inputs.index) return '';
        return (inputs.base.value || '').trim() + '|' + (inputs.index.value || '').trim();
      }
      if (answerType === 'number_fields') {
        return inputs.fields.map(function (input) {
          return (input.value || '').trim();
        }).join('|');
      }
      if (answerType === 'algebraic_fraction') {
        if (!inputs.num) return '';
        var num = (inputs.num.value || '').trim();
        if (!num) return '';
        var den = inputs.den ? (inputs.den.value || '').trim() : '';
        return num + '|' + (den || '1');
      }
      return inputs.single ? (inputs.single.value || '').trim() : '';
    }

    function isEmptyAnswer() {
      var inputs = activeInputs();
      if (answerType === 'standard_form') {
        return !(inputs.coeff && (inputs.coeff.value || '').trim()) || !(inputs.exp && (inputs.exp.value || '').trim());
      }
      if (answerType === 'number_pair') {
        return !(inputs.a && (inputs.a.value || '').trim()) || !(inputs.b && (inputs.b.value || '').trim());
      }
      if (answerType === 'power') {
        return !(inputs.base && (inputs.base.value || '').trim()) || !(inputs.index && (inputs.index.value || '').trim());
      }
      if (answerType === 'number_fields') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'algebraic_fraction') {
        return !(inputs.num && (inputs.num.value || '').trim());
      }
      return !readUserAnswer();
    }

    function emptyMessage() {
      if (answerType === 'standard_form') return 'Enter the coefficient and power of 10.';
      if (answerType === 'number_pair') return 'Enter both values.';
      if (answerType === 'power') return 'Enter the base and index.';
      if (answerType === 'number_fields') return 'Complete every answer field.';
      if (answerType === 'number_list') return 'Enter your answer.';
      if (answerType === 'pi_multiple') return 'Enter the coefficient of π.';
      if (answerType === 'surd') return 'Enter your answer in surd form.';
      if (answerType === 'algebraic') return 'Enter your simplified expression.';
      if (answerType === 'algebraic_fraction') return 'Enter the surd numerator (denominator optional if it is 1).';
      return 'Enter an answer first.';
    }

    function setInputState(correct) {
      var inputs = activeInputs();
      inputs.all.forEach(function (input) {
        input.classList.remove('is-correct', 'is-wrong');
        if (correct) {
          input.classList.add('is-correct');
          input.disabled = true;
        } else {
          input.classList.add('is-wrong');
          input.disabled = false;
        }
      });
      block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
        btn.disabled = correct;
      });
    }

    function submitAnswer() {
      var inputs = activeInputs();
      if (inputs.all.length && inputs.all[0] && inputs.all[0].disabled) return;

      if (isEmptyAnswer()) {
        if (feedback) {
          feedback.textContent = emptyMessage();
          feedback.style.color = '#dc2626';
        }
        return;
      }

      var userAnswer = readUserAnswer();

      var body = {
        user_answer: userAnswer,
        correct_answer_raw: correctRaw,
        answer_type: answerType,
      };
      if (trackable) {
        body.level = block.dataset.level;
        body.subject = block.dataset.subject;
        body.topic = block.dataset.topic;
        body.difficulty = block.dataset.difficulty || 'foundational';
      }

      block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
        btn.disabled = true;
      });
      inputs.all.forEach(function (input) {
        input.disabled = true;
      });

      fetch('/api/v1/problems/check', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify(body),
      })
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) {
              var err = new Error(data.error || 'Check failed');
              err.data = data;
              throw err;
            }
            return data;
          });
        })
        .then(function (data) {
          if (data.correct) {
            setInputState(true);
            if (feedback) {
              feedback.textContent = '\u2713 ' + (data.feedback || 'Correct!');
              feedback.style.color = '#16a34a';
            }
          } else {
            setInputState(false);
            if (feedback) {
              feedback.textContent = '\u2717 ' + (data.feedback || 'Not quite \u2014 try again.');
              feedback.style.color = '#dc2626';
            }
          }
          if (trackable && block.dataset.freeResponsePersisted !== '1') {
            block.dataset.freeResponsePersisted = '1';
            persistMcqAnswer(
              block,
              data.normalized_user || userAnswer,
              data.normalized_correct || correctRaw,
              Boolean(data.correct)
            );
          }
        })
        .catch(function (err) {
          inputs.all.forEach(function (input) {
            input.disabled = false;
          });
          block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
            btn.disabled = false;
          });
          if (feedback) {
            feedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
            feedback.style.color = '#dc2626';
          }
        });
    }

    checkBtn.addEventListener('click', submitAnswer);
    activeInputs().all.forEach(function (input) {
      input.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
          event.preventDefault();
          submitAnswer();
        }
      });
    });
  }

  function initFreeResponseInline() {
    document.querySelectorAll('.free-response-inline').forEach(wireFreeResponseBlock);
  }

  function showAppToast(message, type, options) {
    var host = document.getElementById('app-toast-host');
    if (!host) return;

    var toast = document.createElement('div');
    toast.className = 'app-toast is-' + (type === 'error' ? 'error' : 'success');

    if (options && options.linkUrl && options.linkLabel) {
      toast.appendChild(document.createTextNode(message + ' '));
      var link = document.createElement('a');
      link.href = options.linkUrl;
      link.textContent = options.linkLabel;
      toast.appendChild(link);
    } else {
      toast.textContent = message;
    }

    host.appendChild(toast);
    window.setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.2s ease';
      window.setTimeout(function () {
        toast.remove();
      }, 220);
    }, 4200);
  }

  function postJsonForm(form) {
    return fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
      },
      credentials: 'same-origin',
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var err = new Error(data.error || 'Request failed');
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  function typesetNodes(nodes) {
    if (!window.MathJax || !MathJax.typesetPromise) return;
    var list = nodes.filter(Boolean);
    if (!list.length) return;
    MathJax.typesetPromise(list).catch(function () {});
  }

  function wireMcqWrap(wrap) {
    wireMcqBlock(wrap);
  }

  function initSaveProblemForm() {
    var form = document.getElementById('save-problem-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var button = form.querySelector('button[type="submit"]');
      if (button) button.disabled = true;

      postJsonForm(form)
        .then(function (data) {
          showAppToast(data.message || 'Question saved to your profile.', 'success', {
            linkUrl: data.saved_url,
            linkLabel: 'View saved',
          });
        })
        .catch(function (err) {
          showAppToast(
            (err.data && err.data.error) || err.message || 'Could not save that question.',
            'error'
          );
        })
        .finally(function () {
          if (button) button.disabled = false;
        });
    });
  }

  function applySavedProblemPayload(problem) {
    var question = document.getElementById('saved-question-content');
    if (question) question.innerHTML = problem.question_html || '';

    var answer = document.getElementById('saved-answer-content');
    if (answer) answer.innerHTML = problem.solution_html || '';

    var hint = document.getElementById('saved-hint-content');
    var hintWrap = document.getElementById('saved-hint-wrap');
    if (hint) {
      if (problem.hint_html) {
        hint.innerHTML = problem.hint_html;
        if (hintWrap) hintWrap.hidden = false;
      } else if (hintWrap) {
        hintWrap.hidden = true;
      }
    }

    var mcq = document.getElementById('saved-mcq-options');
    if (mcq && problem.options && problem.options.length) {
      mcq.dataset.correct = problem.correct_answer || '';
      delete mcq.dataset.mcqInit;
      delete mcq.dataset.mcqPersisted;
      mcq.innerHTML = '';
      problem.options.forEach(function (opt) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn mcq-btn';
        btn.dataset.letter = (opt.charAt(0) || '').trim();
        btn.innerHTML = opt;
        mcq.appendChild(btn);
      });
      var feedback = document.getElementById('saved-mcq-feedback');
      if (feedback) {
        feedback.textContent = '';
        feedback.style.color = '';
      }
      wireMcqWrap(mcq);
    }

    var free = document.getElementById('saved-free-response');
    if (free) {
      var raw = (problem.correct_answer_raw || '').trim();
      if (raw) {
        free.hidden = false;
        free.setAttribute('data-correct-raw', raw);
        free.dataset.correctRaw = raw;
        var answerType = problem.answer_type || 'number';
        free.setAttribute('data-answer-type', answerType);
        free.dataset.answerType = answerType;
        if (problem.answer_format_hint) {
          free.setAttribute('data-format-hint', problem.answer_format_hint);
        } else {
          free.removeAttribute('data-format-hint');
        }
        if (problem.answer_labels && problem.answer_labels.length) {
          free.setAttribute('data-label-a', problem.answer_labels[0] || '');
          free.setAttribute('data-label-b', problem.answer_labels[1] || '');
          free.setAttribute('data-answer-labels', JSON.stringify(problem.answer_labels));
        } else {
          free.removeAttribute('data-label-a');
          free.removeAttribute('data-label-b');
          free.setAttribute('data-answer-labels', '[]');
        }
        if (problem.answer_field_types && problem.answer_field_types.length) {
          free.setAttribute('data-field-types', JSON.stringify(problem.answer_field_types));
        } else {
          free.setAttribute('data-field-types', '[]');
        }
        if (problem.answer_pair_sep) {
          free.setAttribute('data-pair-sep', problem.answer_pair_sep);
        } else {
          free.setAttribute('data-pair-sep', 'and');
        }
        setFreeResponseInputMode(free, answerType);
        delete free.dataset.freeResponseInit;
        delete free.dataset.freeResponsePersisted;
        resetFreeResponseBlock(free);
        wireFreeResponseBlock(free);
      } else {
        free.hidden = true;
        free.setAttribute('data-correct-raw', '');
        free.dataset.correctRaw = '';
        resetFreeResponseBlock(free);
      }
    }

    typesetNodes([question, answer, hint, mcq, free]);
  }

  function initRerollSavedForm() {
    var form = document.getElementById('reroll-saved-form');
    if (!form) return;

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var button = form.querySelector('button[type="submit"]');
      if (button) button.disabled = true;

      postJsonForm(form)
        .then(function (data) {
          if (data.problem) applySavedProblemPayload(data.problem);
          showAppToast(data.message || 'New numbers generated for this saved question.', 'success');
        })
        .catch(function (err) {
          showAppToast(
            (err.data && err.data.error) || err.message || 'Could not refresh this question.',
            'error'
          );
        })
        .finally(function () {
          if (button) button.disabled = false;
        });
    });
  }

  function initMcqButtons() {
    var wraps = document.querySelectorAll(
      '#mcq-options, #saved-mcq-options, #shared-mcq-options, #suggestion-mcq-options, .mcq-options[data-correct]'
    );
    wraps.forEach(wireMcqBlock);
    typesetNodes(Array.prototype.slice.call(wraps));
  }

  function scrollToProblemCard() {
    var card = document.querySelector('.problem-card');
    if (!card) return;

    var headerOffset = 72; // leave room below the sticky/site header
    var cancelled = false;

    function doScroll() {
      if (cancelled) return;
      var top = card.getBoundingClientRect().top + window.pageYOffset - headerOffset;
      window.scrollTo({ top: Math.max(top, 0), behavior: 'auto' });
    }

    // Once the user takes over, stop issuing corrective scrolls.
    function stop() { cancelled = true; }
    ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (ev) {
      window.addEventListener(ev, stop, { passive: true, once: true });
    });

    doScroll();
    // Re-align after asynchronous MathJax / SVG layout shifts.
    window.addEventListener('load', doScroll);
    setTimeout(doScroll, 250);
    setTimeout(doScroll, 700);
    setTimeout(function () {
      doScroll();
      window.removeEventListener('load', doScroll);
    }, 1400);
  }

  function initScrollToProblem() {
    // Mark generate / reroll submissions so the reloaded page lands on the question.
    ['main-form', 'reroll-form'].forEach(function (id) {
      var f = document.getElementById(id);
      if (!f) return;
      f.addEventListener('submit', function () {
        try { sessionStorage.setItem('scrollToProblem', '1'); } catch (e) {}
      });
    });

    var flag = null;
    try { flag = sessionStorage.getItem('scrollToProblem'); } catch (e) {}
    if (flag === '1') {
      try { sessionStorage.removeItem('scrollToProblem'); } catch (e) {}
      scrollToProblemCard();
    }
  }

  function initProbTreeInputs() {
    // Self-checking inputs on blank probability-tree diagrams.
    function toValue(str) {
      if (str == null) return null;
      var s = String(str).trim();
      if (s === '') return null;
      if (s.indexOf('/') >= 0) {
        var parts = s.split('/');
        if (parts.length !== 2) return null;
        var n = parseFloat(parts[0]);
        var d = parseFloat(parts[1]);
        if (!isFinite(n) || !isFinite(d) || d === 0) return null;
        return n / d;
      }
      var v = parseFloat(s);
      return isFinite(v) ? v : null;
    }

    function matches(typed, answer) {
      var a = toValue(typed);
      var b = toValue(answer);
      if (a === null || b === null) return false;
      return Math.abs(a - b) < 0.005; // accept equivalent fractions and rounded decimals
    }

    document.addEventListener('input', function (e) {
      var el = e.target;
      if (!el || !el.classList || !el.classList.contains('prob-tree-input')) return;
      el.classList.remove('correct', 'incorrect');
      if (el.value.trim() === '') return;
      el.classList.add(matches(el.value, el.getAttribute('data-ans')) ? 'correct' : 'incorrect');
    });
  }

  function initAnswerRevealMathJax() {
    document.querySelectorAll('details.answer-reveal').forEach(function (details) {
      details.addEventListener('toggle', function () {
        if (!details.open || !window.MathJax || !MathJax.typesetPromise) return;
        var targets = [details.querySelector('.answer'), details.querySelector('.hint')];
        MathJax.typesetPromise(targets.filter(Boolean)).catch(function () {});
      });
    });
  }

  window.showAppToast = showAppToast;

  document.addEventListener('DOMContentLoaded', function () {
    initGeneratorForm();
    initQuickTestForm();
    initQuickTestNextForm();
    initMcqInline();
    initFreeResponseInline();
    initMcqButtons();
    initSaveProblemForm();
    initRerollSavedForm();
    initScrollToProblem();
    initProbTreeInputs();
    initAnswerRevealMathJax();
  });
})();
