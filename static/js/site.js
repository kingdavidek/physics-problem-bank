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
    var answerType = resolveFreeResponseAnswerType(block);
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
    if (answerType === 'coordinate_pairs') {
      return readCoordinatePairsAnswer(block);
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
    if (answerType === 'completed_square') {
      return readCompletedSquareAnswer(block);
    }
    if (answerType === 'vector_combo') {
      return readVectorComboAnswer(block);
    }
    if (answerType === 'vector_pair') {
      return readVectorPairAnswer(block);
    }
    if (answerType === 'linear_inequality') {
      return readLinearInequalityAnswer(block);
    }
    if (answerType === 'compound_inequality') {
      return readCompoundInequalityAnswer(block);
    }
    if (answerType === 'number_line') {
      return readNumberLineAnswer(block);
    }
    if (answerType === 'formula_fraction') {
      return readFormulaFractionAnswer(block);
    }
    if (answerType === 'algebraic') {
      return readAlgebraicAnswer(block);
    }
    if (answerType === 'algebraic_fraction') {
      var afNum = block.querySelector('.free-response-input-alg-frac-num');
      var afDen = block.querySelector('.free-response-input-alg-frac-den');
      if (!afNum) return '';
      var afN = (afNum.value || '').trim();
      if (!afN) return '';
      var afD = afDen ? (afDen.value || '').trim() : '';
      return afN + '|' + (afD || '1');
    }
    var single = block.querySelector('.free-response-input');
    return single ? (single.value || '').trim() : '';
  }

  function freeResponseCheckState(block) {
    if (!block || block.hidden) {
      return { checked: false, correct: null, userAnswer: '' };
    }
    var answerType = resolveFreeResponseAnswerType(block);
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
    if (answerType === 'completed_square') {
      var csqFields = block.querySelectorAll('.free-response-input-csq');
      if (!csqFields.length) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var csqChecked = Array.prototype.some.call(csqFields, function (input) {
        return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
      });
      var csqAllCorrect = csqChecked && Array.prototype.every.call(csqFields, function (input) {
        return input.classList.contains('is-correct');
      });
      return {
        checked: csqChecked,
        correct: csqChecked ? csqAllCorrect : null,
        userAnswer: readFreeResponseUserAnswer(block),
      };
    }
    if (answerType === 'vector_combo') {
      var vcomboFields = block.querySelectorAll('.free-response-input-vcombo');
      if (!vcomboFields.length) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var vcomboChecked = Array.prototype.some.call(vcomboFields, function (input) {
        return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
      });
      var vcomboAllCorrect = vcomboChecked && Array.prototype.every.call(vcomboFields, function (input) {
        return input.classList.contains('is-correct');
      });
      return {
        checked: vcomboChecked,
        correct: vcomboChecked ? vcomboAllCorrect : null,
        userAnswer: readFreeResponseUserAnswer(block),
      };
    }
    if (answerType === 'vector_pair') {
      var vpairFields = block.querySelectorAll('.free-response-input-vpair');
      if (!vpairFields.length) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var vpairChecked = Array.prototype.some.call(vpairFields, function (input) {
        return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
      });
      var vpairAllCorrect = vpairChecked && Array.prototype.every.call(vpairFields, function (input) {
        return input.classList.contains('is-correct');
      });
      return {
        checked: vpairChecked,
        correct: vpairChecked ? vpairAllCorrect : null,
        userAnswer: readFreeResponseUserAnswer(block),
      };
    }
    if (answerType === 'linear_inequality' || answerType === 'compound_inequality') {
      var ineqInputs = freeResponseInputs(block);
      if (!ineqInputs.length) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var ineqChecked = ineqInputs.some(function (input) {
        return input.classList.contains('is-correct') || input.classList.contains('is-wrong');
      });
      var ineqAllCorrect = ineqChecked && ineqInputs.every(function (input) {
        return input.classList.contains('is-correct');
      });
      return {
        checked: ineqChecked,
        correct: ineqChecked ? ineqAllCorrect : null,
        userAnswer: readFreeResponseUserAnswer(block),
      };
    }
    if (answerType === 'number_line') {
      var nlWidget = block.querySelector('.free-response-number-line');
      if (!nlWidget) {
        return { checked: false, correct: null, userAnswer: '' };
      }
      var nlChecked = nlWidget.classList.contains('is-correct')
        || nlWidget.classList.contains('is-wrong');
      return {
        checked: nlChecked,
        correct: nlChecked ? nlWidget.classList.contains('is-correct') : null,
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

  function normalizeFeedbackText(value) {
    return String(value || '').replace(/\s+/g, '').toLowerCase();
  }

  function freeResponseFieldPlaceholder(fieldType, formatHint) {
    if (formatHint) return formatHint;
    if (fieldType === 'keyword') return 'e.g. positive, negative, or none';
    if (fieldType === 'linear_equation') return 'e.g. y = 2x + 3';
    if (fieldType === 'two_var_equation') return 'e.g. 10c + 11t = 53';
    if (fieldType === 'linear_inequality') return 'e.g. m < 40';
    if (fieldType === 'number_estimate') return 'Your estimate from the graph';
    if (fieldType === 'fraction') return 'e.g. 3/4';
    if (fieldType === 'surd') return 'e.g. 4√3';
    if (fieldType === 'ratio' || fieldType === 'ratio_exact') return 'e.g. 3:5';
    if (fieldType === 'binary') return 'e.g. 1101';
    if (fieldType === 'hex') return 'e.g. FF';
    return 'Number or fraction';
  }

  function freeResponsePlaceholder(answerType, formatHint) {
    if (formatHint) return formatHint;
    if (answerType === 'fraction') return 'e.g. 3/4';
    if (answerType === 'linear') return 'e.g. x = 3';
    if (answerType === 'quadratic_roots') return 'e.g. 3, -2 or -3+√14, -3-√14';
    if (answerType === 'vector') return 'e.g. (3, 4)';
    if (answerType === 'surd') return 'e.g. √113';
    if (answerType === 'ratio' || answerType === 'ratio_exact') return 'e.g. 3:5';
    if (answerType === 'linear_equation') return 'e.g. y = 2x + 3';
    if (answerType === 'number_list') return 'Enter numbers separated by commas';
    if (answerType === 'number_estimate') return 'Your estimate from the graph';
    if (answerType === 'pi_multiple') return 'e.g. 4';
    if (answerType === 'algebraic') return 'e.g. a - b';
    if (answerType === 'binary') return 'e.g. 1101';
    if (answerType === 'hex') return 'e.g. FF';
    if (answerType === 'standard_form') return 'e.g. 3.2 × 10^5';
    return 'Enter a number';
  }

  function freeResponseCorrectFeedback(data, userAnswer) {
    var base = (data && data.feedback) || 'Correct!';
    if (!data || !data.correct) return base;
    var nu = data.normalized_user;
    var nc = data.normalized_correct;
    if (nu && nc && normalizeFeedbackText(nu) !== normalizeFeedbackText(nc)) {
      return base + ' Equivalent forms accepted.';
    }
    return base;
  }

  function freeResponseInputMode(answerType, formatHint) {
    var hint = String(formatHint || '').toLowerCase();
    if (answerType === 'fraction' || answerType === 'surd' || answerType === 'linear' ||
        answerType === 'quadratic_roots' || answerType === 'vector' || answerType === 'ratio' ||
        answerType === 'ratio_exact' || answerType === 'linear_equation' ||
        answerType === 'algebraic' || answerType === 'binary' || answerType === 'hex' ||
        answerType === 'pi_multiple') {
      return 'text';
    }
    if (hint.indexOf('fraction') !== -1 || hint.indexOf('surd') !== -1 ||
        hint.indexOf('√') !== -1 || hint.indexOf(':') !== -1) {
      return 'text';
    }
    return 'decimal';
  }

  function freeResponseInputs(block) {
    return Array.prototype.slice.call(block.querySelectorAll('.free-response-input'));
  }

  var COMPLETED_SQUARE_KINDS = ['plus', 'minus', 'scaled', 'expand'];

  function inferCompletedSquareKind(raw) {
    var kind = String(raw || '').trim().split('|')[0].toLowerCase();
    return COMPLETED_SQUARE_KINDS.indexOf(kind) >= 0 ? kind : '';
  }

  function resolveFreeResponseAnswerType(block) {
    if (!block) return 'number';
    var raw = (block.getAttribute('data-correct-raw') || block.dataset.correctRaw || '').trim();
    var inferredKind = inferCompletedSquareKind(raw);
    if (inferredKind) {
      if (!block.getAttribute('data-answer-template-kind')) {
        block.setAttribute('data-answer-template-kind', inferredKind);
      }
      block.setAttribute('data-answer-type', 'completed_square');
      return 'completed_square';
    }
    return (block.getAttribute('data-answer-type') || block.dataset.answerType || 'number').trim();
  }

  function applyFreeResponseProblemMetadata(block, problem) {
    if (!block || !problem) return;
    var raw = (problem.correct_answer_raw || '').trim();
    if (raw) {
      block.hidden = false;
      block.setAttribute('data-correct-raw', raw);
      block.dataset.correctRaw = raw;
    }
    var answerType = problem.answer_type || 'number';
    var inferredKind = inferCompletedSquareKind(raw);
    if (inferredKind) {
      answerType = 'completed_square';
      block.setAttribute('data-answer-template-kind', problem.answer_template_kind || inferredKind);
    } else if (problem.answer_template_kind) {
      block.setAttribute('data-answer-template-kind', problem.answer_template_kind);
    } else {
      block.removeAttribute('data-answer-template-kind');
    }
    block.setAttribute('data-answer-type', answerType);
    block.dataset.answerType = answerType;
    if (problem.answer_format_hint) {
      block.setAttribute('data-format-hint', problem.answer_format_hint);
    } else {
      block.removeAttribute('data-format-hint');
    }
    if (problem.answer_subject) {
      block.setAttribute('data-csq-subject', problem.answer_subject);
    } else {
      block.removeAttribute('data-csq-subject');
    }
    if (problem.answer_axis_min !== undefined && problem.answer_axis_min !== null
      && problem.answer_axis_min !== '') {
      block.setAttribute('data-axis-min', String(problem.answer_axis_min));
    } else {
      block.removeAttribute('data-axis-min');
    }
    if (problem.answer_axis_max !== undefined && problem.answer_axis_max !== null
      && problem.answer_axis_max !== '') {
      block.setAttribute('data-axis-max', String(problem.answer_axis_max));
    } else {
      block.removeAttribute('data-axis-max');
    }
    if (problem.answer_labels && problem.answer_labels.length) {
      block.setAttribute('data-label-a', problem.answer_labels[0] || '');
      block.setAttribute('data-label-b', problem.answer_labels[1] || '');
      block.setAttribute('data-answer-labels', JSON.stringify(problem.answer_labels));
    } else {
      block.removeAttribute('data-label-a');
      block.removeAttribute('data-label-b');
      block.setAttribute('data-answer-labels', '[]');
    }
    if (problem.answer_field_types && problem.answer_field_types.length) {
      block.setAttribute('data-field-types', JSON.stringify(problem.answer_field_types));
    } else {
      block.setAttribute('data-field-types', '[]');
    }
    if (problem.answer_pair_sep) {
      block.setAttribute('data-pair-sep', problem.answer_pair_sep);
    } else {
      block.setAttribute('data-pair-sep', 'and');
    }
    var hint = block.querySelector('.free-response-csq-hint');
    if (hint && problem.answer_format_hint) {
      hint.textContent = problem.answer_format_hint;
    }
    var vcomboHint = block.querySelector('.free-response-vcombo-hint');
    if (vcomboHint && problem.answer_format_hint) {
      vcomboHint.textContent = problem.answer_format_hint;
    }
    var vpairHint = block.querySelector('.free-response-vpair-hint');
    if (vpairHint && problem.answer_format_hint) {
      vpairHint.textContent = problem.answer_format_hint;
    }
    var ineqHint = block.querySelector('.free-response-ineq-hint');
    if (ineqHint && problem.answer_format_hint) {
      ineqHint.textContent = problem.answer_format_hint;
    }
    var formulaHint = block.querySelector('.free-response-formula-frac-hint');
    if (formulaHint && problem.answer_format_hint) {
      formulaHint.textContent = problem.answer_format_hint;
    }
  }

  function freeResponseRowKind(row) {
    if (!row) return 'number';
    if (row.classList.contains('free-response-row--standard-form')) return 'standard_form';
    if (row.classList.contains('free-response-row--number-pair')) return 'number_pair';
    if (row.classList.contains('free-response-row--coordinate-pairs')) return 'coordinate_pairs';
    if (row.classList.contains('free-response-row--number-list')) return 'number_list';
    if (row.classList.contains('free-response-row--power')) return 'power';
    if (row.classList.contains('free-response-row--linear-equation')) return 'linear_equation';
    if (row.classList.contains('free-response-row--ratio')) return 'ratio';
    if (row.classList.contains('free-response-row--fraction')) return 'fraction';
    if (row.classList.contains('free-response-row--linear')) return 'linear';
    if (row.classList.contains('free-response-row--quadratic-roots')) return 'quadratic_roots';
    if (row.classList.contains('free-response-row--vector')) return 'vector';
    if (row.classList.contains('free-response-row--number-fields')) return 'number_fields';
    if (row.classList.contains('free-response-row--completed-square')) return 'completed_square';
    if (row.classList.contains('free-response-row--vector-combo')) return 'vector_combo';
    if (row.classList.contains('free-response-row--vector-pair')) return 'vector_pair';
    if (row.classList.contains('free-response-row--linear-inequality')) return 'linear_inequality';
    if (row.classList.contains('free-response-row--compound-inequality')) return 'compound_inequality';
    if (row.classList.contains('free-response-row--number-line')) return 'number_line';
    if (row.classList.contains('free-response-row--formula-fraction')) return 'formula_fraction';
    if (row.classList.contains('free-response-row--pi-multiple')) return 'pi_multiple';
    if (row.classList.contains('free-response-row--surd')) return 'surd';
    if (row.classList.contains('free-response-row--algebraic')) return 'algebraic';
    if (row.classList.contains('free-response-row--algebraic-fraction')) return 'algebraic_fraction';
    return 'number';
  }

  function signButtonForInput(input) {
    var prev = input && input.previousElementSibling;
    if (!prev) return null;
    if (prev.classList.contains('free-response-csq-sign')
      || prev.classList.contains('free-response-vcombo-sign')) {
      return prev;
    }
    return null;
  }

  function csqSignButtonForInput(input) {
    return signButtonForInput(input);
  }

  function readSignedCoefficientValue(input) {
    var raw = (input.value || '').trim();
    if (!raw) return '';
    var normalized = raw.replace(/\u2212/g, '-').replace(/\s+/g, '');
    if (/^-/.test(normalized)) return normalized;

    var signBtn = signButtonForInput(input);
    if (!signBtn) return normalized;

    var sign = signBtn.getAttribute('data-sign') || '+';
    var signIsPlus = sign === '+' || sign === '\u002b';
    if (signIsPlus) return normalized;

    if (normalized.indexOf('/') >= 0) {
      var slash = normalized.indexOf('/');
      return '-' + normalized.slice(0, slash) + normalized.slice(slash);
    }
    var magnitude = parseFloat(normalized);
    if (isNaN(magnitude)) return raw;
    return String(-Math.abs(magnitude));
  }

  function readVectorComboAnswer(block) {
    var fields = block.querySelectorAll('.free-response-input-vcombo');
    return Array.prototype.map.call(fields, readSignedCoefficientValue).join('|');
  }

  function ineqSignSelectHtml(selected) {
    var sel = selected || '>=';
    function opt(value, label) {
      return '<option value="' + value + '"' + (sel === value ? ' selected' : '') + '>' + label + '</option>';
    }
    return (
      '<select class="free-response-ineq-sign" aria-label="Inequality sign">' +
      opt('=', '=') +
      opt('<', '&lt;') +
      opt('>', '&gt;') +
      opt('<=', '\u2264') +
      opt('>=', '\u2265') +
      '</select>'
    );
  }

  function compoundSignSelectHtml(selected) {
    var sel = selected || '<=';
    function opt(value, label) {
      return '<option value="' + value + '"' + (sel === value ? ' selected' : '') + '>' + label + '</option>';
    }
    return (
      '<select class="free-response-compound-sign" aria-label="Inequality sign">' +
      opt('<', '&lt;') +
      opt('<=', '\u2264') +
      opt('>', '&gt;') +
      opt('>=', '\u2265') +
      '</select>'
    );
  }

  function readLinearInequalityAnswer(block) {
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim();
    var sign = block.querySelector('.free-response-ineq-sign');
    var val = block.querySelector('.free-response-input-ineq-value');
    if (!sign || !val) return '';
    return varName + '|' + sign.value + '|' + (val.value || '').trim();
  }

  function readCompoundInequalityAnswer(block) {
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim();
    var bounds = block.querySelectorAll('.free-response-input-compound-bound');
    var signs = block.querySelectorAll('.free-response-compound-sign');
    if (bounds.length < 2 || signs.length < 2) return '';
    return [
      varName,
      signs[0].value,
      (bounds[0].value || '').trim(),
      signs[1].value,
      (bounds[1].value || '').trim(),
    ].join('|');
  }

  function readFormulaFractionAnswer(block) {
    var num = block.querySelector('.free-response-input-formula-frac-num');
    var den = block.querySelector('.free-response-input-formula-frac-den');
    if (!num || !den) return '';
    var n = (num.value || '').trim();
    var d = (den.value || '').trim();
    if (!n || !d) return '';
    return n + '|' + d;
  }

  function readCoordinatePairsAnswer(block) {
    var inputs = block.querySelectorAll('.free-response-input-coord-pair');
    if (!inputs.length) return '';
    return Array.prototype.map.call(inputs, function (input) {
      return (input.value || '').trim();
    }).join('|');
  }

  function readAlgebraicAnswer(block) {
    var input = block.querySelector('.free-response-input-algebraic');
    if (!input) return '';
    var expr = (input.value || '').trim();
    if (!expr) return '';
    var subject = (block.getAttribute('data-csq-subject') || '').trim();
    if (!subject) return expr;
    var lower = expr.toLowerCase();
    var subLower = subject.toLowerCase();
    if (lower.indexOf(subLower + '=') === 0) return expr;
    return subject + '=' + expr;
  }

  function formulaFractionRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim();
    return (
      '<div class="free-response-row free-response-row--formula-fraction">' +
      '<div class="free-response-formula-fraction-template" aria-label="Formula fraction answer">' +
      '<span class="free-response-formula-subject"><strong>' + esc(varName) + '</strong> =</span>' +
      '<div class="free-response-fraction-stack">' +
      '<input type="text" class="free-response-input free-response-input-formula-frac-num" placeholder="numerator" autocomplete="off" inputmode="text" aria-label="Numerator">' +
      '<span class="free-response-fraction-bar" aria-hidden="true"></span>' +
      '<input type="text" class="free-response-input free-response-input-formula-frac-den" placeholder="denominator" autocomplete="off" inputmode="text" aria-label="Denominator">' +
      '</div></div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function algebraicRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var formatHint = block.getAttribute('data-format-hint') || '';
    var algPh = freeResponsePlaceholder('algebraic', formatHint);
    var subject = (block.getAttribute('data-csq-subject') || '').trim();
    var prefix = subject
      ? '<span class="free-response-formula-subject"><strong>' + esc(subject) + '</strong> =</span>'
      : '';
    return (
      '<div class="free-response-row free-response-row--algebraic">' +
      prefix +
      '<input type="text" class="free-response-input free-response-input-algebraic" placeholder="' + esc(algPh) + '" autocomplete="off" inputmode="text" aria-label="Algebraic answer">' +
      '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function linearInequalityRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim();
    return (
      '<div class="free-response-row free-response-row--linear-inequality">' +
      '<div class="free-response-ineq-template" aria-label="Inequality answer">' +
      '<span class="free-response-ineq-part"><strong>' + esc(varName) + '</strong></span>' +
      ineqSignSelectHtml('>=') +
      '<input type="text" class="free-response-input free-response-input-ineq-value" placeholder="value" autocomplete="off" inputmode="text" aria-label="Inequality value">' +
      '</div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function compoundInequalityRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim();
    return (
      '<div class="free-response-row free-response-row--compound-inequality">' +
      '<div class="free-response-compound-ineq-template" aria-label="Compound inequality answer">' +
      '<input type="text" class="free-response-input free-response-input-compound-bound" placeholder="lo" autocomplete="off" inputmode="text" aria-label="Lower bound">' +
      compoundSignSelectHtml('<') +
      '<span class="free-response-ineq-part"><strong>' + esc(varName) + '</strong></span>' +
      compoundSignSelectHtml('<=') +
      '<input type="text" class="free-response-input free-response-input-compound-bound" placeholder="hi" autocomplete="off" inputmode="text" aria-label="Upper bound">' +
      '</div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function numberLineAxisBounds(block) {
    var minRaw = block.getAttribute('data-axis-min');
    var maxRaw = block.getAttribute('data-axis-max');
    var widget = block.querySelector('.free-response-number-line');
    if ((minRaw === null || minRaw === '') && widget) {
      minRaw = widget.getAttribute('data-axis-min');
    }
    if ((maxRaw === null || maxRaw === '') && widget) {
      maxRaw = widget.getAttribute('data-axis-max');
    }
    var amin = parseInt(minRaw, 10);
    var amax = parseInt(maxRaw, 10);
    if (isNaN(amin)) amin = -2;
    if (isNaN(amax)) amax = 6;
    if (amax <= amin) amax = amin + 4;
    return { min: amin, max: amax };
  }

  function numberLineDefaultState(axis) {
    var span = axis.max - axis.min;
    var left = axis.min + Math.floor(span / 3);
    var right = axis.min + Math.floor((2 * span) / 3);
    if (left >= right) {
      left = axis.min;
      right = axis.max;
    }
    return { left: left, right: right, leftClosed: false, rightClosed: false };
  }

  function readNumberLineAnswer(block) {
    var widget = block.querySelector('.free-response-number-line');
    if (!widget) return '';
    var varName = (block.getAttribute('data-csq-subject') || 'x').trim() || 'x';
    var left = widget.getAttribute('data-left');
    var right = widget.getAttribute('data-right');
    if (left === null || right === null || left === '' || right === '') return '';
    var leftSign = widget.getAttribute('data-left-closed') === '1' ? '<=' : '<';
    var rightSign = widget.getAttribute('data-right-closed') === '1' ? '<=' : '<';
    return [varName, leftSign, left, rightSign, right].join('|');
  }

  function numberLineRowHtml(block) {
    var bounds = numberLineAxisBounds(block);
    return (
      '<div class="free-response-row free-response-row--number-line">' +
      '<div class="free-response-number-line" data-axis-min="' + bounds.min +
      '" data-axis-max="' + bounds.max +
      '" role="group" aria-label="Number line inequality"></div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function numberLineXForValue(value, axis, pad, width) {
    var span = axis.max - axis.min;
    if (span <= 0) return pad;
    return pad + ((value - axis.min) / span) * (width - 2 * pad);
  }

  function numberLineValueFromClientX(clientX, svg, axis, pad, width) {
    var rect = svg.getBoundingClientRect();
    if (!rect.width) return axis.min;
    var x = ((clientX - rect.left) / rect.width) * width;
    var span = axis.max - axis.min;
    var t = (x - pad) / (width - 2 * pad);
    var value = axis.min + t * span;
    value = Math.round(value);
    if (value < axis.min) value = axis.min;
    if (value > axis.max) value = axis.max;
    return value;
  }

  function renderNumberLineWidget(widget, state) {
    if (!widget) return;
    var amin = parseInt(widget.getAttribute('data-axis-min'), 10);
    var amax = parseInt(widget.getAttribute('data-axis-max'), 10);
    if (isNaN(amin)) amin = -2;
    if (isNaN(amax) || amax <= amin) amax = amin + 4;
    var axis = { min: amin, max: amax };
    if (!state) {
      state = {
        left: parseInt(widget.getAttribute('data-left'), 10),
        right: parseInt(widget.getAttribute('data-right'), 10),
        leftClosed: widget.getAttribute('data-left-closed') === '1',
        rightClosed: widget.getAttribute('data-right-closed') === '1',
      };
      if (isNaN(state.left) || isNaN(state.right)) {
        state = numberLineDefaultState(axis);
      }
    }
    if (state.left > state.right) {
      var tmp = state.left;
      state.left = state.right;
      state.right = tmp;
      tmp = state.leftClosed;
      state.leftClosed = state.rightClosed;
      state.rightClosed = tmp;
    }

    widget.setAttribute('data-left', String(state.left));
    widget.setAttribute('data-right', String(state.right));
    widget.setAttribute('data-left-closed', state.leftClosed ? '1' : '0');
    widget.setAttribute('data-right-closed', state.rightClosed ? '1' : '0');

    var width = 480;
    var height = 96;
    var pad = 36;
    var y = 42;
    var leftX = numberLineXForValue(state.left, axis, pad, width);
    var rightX = numberLineXForValue(state.right, axis, pad, width);

    var ticks = '';
    var v;
    for (v = axis.min; v <= axis.max; v += 1) {
      var tx = numberLineXForValue(v, axis, pad, width);
      ticks +=
        '<line x1="' + tx + '" y1="' + (y - 7) + '" x2="' + tx + '" y2="' + (y + 7) +
        '" stroke="#475569" stroke-width="1.5"/>' +
        '<text x="' + tx + '" y="' + (y + 24) +
        '" text-anchor="middle" fill="#475569" font-size="13">' + v + '</text>';
    }

    var leftFill = state.leftClosed ? '#1a6fa8' : '#ffffff';
    var rightFill = state.rightClosed ? '#1a6fa8' : '#ffffff';
    var leftLabel = state.leftClosed ? 'closed' : 'open';
    var rightLabel = state.rightClosed ? 'closed' : 'open';

    widget.innerHTML =
      '<svg viewBox="0 0 ' + width + ' ' + height +
      '" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
      '<line x1="' + pad + '" y1="' + y + '" x2="' + (width - pad) + '" y2="' + y +
      '" stroke="#334155" stroke-width="2"/>' +
      '<polygon points="' + (width - pad) + ',' + (y - 5) + ' ' + (width - pad + 12) + ',' + y +
      ' ' + (width - pad) + ',' + (y + 5) + '" fill="#334155"/>' +
      ticks +
      '<line class="nl-segment" x1="' + leftX + '" y1="' + y + '" x2="' + rightX +
      '" y2="' + y + '" stroke="#1a6fa8" stroke-width="5" stroke-linecap="round"/>' +
      '<circle class="nl-endpoint nl-left' + (state.leftClosed ? ' nl-closed' : '') +
      '" data-end="left" cx="' + leftX + '" cy="' + y + '" r="9" fill="' + leftFill +
      '" stroke="#1a6fa8" stroke-width="2.5" tabindex="0" role="button" ' +
      'aria-label="Left endpoint at ' + state.left + ', ' + leftLabel +
      ' circle. Drag to move, click or press Enter to toggle."/>' +
      '<circle class="nl-endpoint nl-right' + (state.rightClosed ? ' nl-closed' : '') +
      '" data-end="right" cx="' + rightX + '" cy="' + y + '" r="9" fill="' + rightFill +
      '" stroke="#1a6fa8" stroke-width="2.5" tabindex="0" role="button" ' +
      'aria-label="Right endpoint at ' + state.right + ', ' + rightLabel +
      ' circle. Drag to move, click or press Enter to toggle."/>' +
      '</svg>' +
      '<div class="free-response-number-line-legend" aria-hidden="true">' +
      '<span><span class="nl-legend-dot open"></span> Open = not included</span>' +
      '<span><span class="nl-legend-dot closed"></span> Closed = included</span>' +
      '</div>';
  }

  function getNumberLineState(widget) {
    return {
      left: parseInt(widget.getAttribute('data-left'), 10),
      right: parseInt(widget.getAttribute('data-right'), 10),
      leftClosed: widget.getAttribute('data-left-closed') === '1',
      rightClosed: widget.getAttribute('data-right-closed') === '1',
    };
  }

  function wireNumberLineWidget(block) {
    var widget = block.querySelector('.free-response-number-line');
    if (!widget) return;

    var bounds = numberLineAxisBounds(block);
    widget.setAttribute('data-axis-min', String(bounds.min));
    widget.setAttribute('data-axis-max', String(bounds.max));

    if (!widget.getAttribute('data-left') || !widget.getAttribute('data-right')) {
      var defaults = numberLineDefaultState(bounds);
      widget.setAttribute('data-left', String(defaults.left));
      widget.setAttribute('data-right', String(defaults.right));
      widget.setAttribute('data-left-closed', defaults.leftClosed ? '1' : '0');
      widget.setAttribute('data-right-closed', defaults.rightClosed ? '1' : '0');
    }

    renderNumberLineWidget(widget);

    if (widget.dataset.nlWired === '1') return;
    widget.dataset.nlWired = '1';

    var drag = null;

    function currentAxis() {
      return {
        min: parseInt(widget.getAttribute('data-axis-min'), 10),
        max: parseInt(widget.getAttribute('data-axis-max'), 10),
      };
    }

    function applyState(state) {
      widget.classList.remove('is-correct', 'is-wrong');
      renderNumberLineWidget(widget, state);
    }

    function updateDragVisual(state) {
      widget.setAttribute('data-left', String(state.left));
      widget.setAttribute('data-right', String(state.right));
      widget.setAttribute('data-left-closed', state.leftClosed ? '1' : '0');
      widget.setAttribute('data-right-closed', state.rightClosed ? '1' : '0');
      widget.classList.remove('is-correct', 'is-wrong');

      var axis = currentAxis();
      var leftEl = widget.querySelector('.nl-left');
      var rightEl = widget.querySelector('.nl-right');
      var segment = widget.querySelector('.nl-segment');
      if (!leftEl || !rightEl || !segment) return;

      var leftX = numberLineXForValue(state.left, axis, 36, 480);
      var rightX = numberLineXForValue(state.right, axis, 36, 480);
      leftEl.setAttribute('cx', String(leftX));
      rightEl.setAttribute('cx', String(rightX));
      segment.setAttribute('x1', String(leftX));
      segment.setAttribute('x2', String(rightX));

      leftEl.setAttribute(
        'aria-label',
        'Left endpoint at ' + state.left + ', ' +
          (state.leftClosed ? 'closed' : 'open') +
          ' circle. Drag to move, click or press Enter to toggle.'
      );
      rightEl.setAttribute(
        'aria-label',
        'Right endpoint at ' + state.right + ', ' +
          (state.rightClosed ? 'closed' : 'open') +
          ' circle. Drag to move, click or press Enter to toggle.'
      );
    }

    function pointerPos(evt) {
      if (evt.touches && evt.touches.length) {
        return { x: evt.touches[0].clientX, y: evt.touches[0].clientY };
      }
      if (evt.changedTouches && evt.changedTouches.length) {
        return { x: evt.changedTouches[0].clientX, y: evt.changedTouches[0].clientY };
      }
      return { x: evt.clientX, y: evt.clientY };
    }

    function onPointerDown(evt) {
      if (widget.classList.contains('is-disabled')) return;
      var target = evt.target;
      if (!target || !target.classList || !target.classList.contains('nl-endpoint')) return;
      evt.preventDefault();
      var end = target.getAttribute('data-end');
      var pos = pointerPos(evt);
      drag = {
        end: end,
        startX: pos.x,
        startY: pos.y,
        moved: false,
        pointerId: evt.pointerId,
      };
      widget.classList.add('is-dragging');
      if (target.setPointerCapture && evt.pointerId !== undefined) {
        try { target.setPointerCapture(evt.pointerId); } catch (err) { /* ignore */ }
      }
    }

    function onPointerMove(evt) {
      if (!drag) return;
      var svg = widget.querySelector('svg');
      if (!svg) return;
      var pos = pointerPos(evt);
      var dx = Math.abs(pos.x - drag.startX);
      var dy = Math.abs(pos.y - drag.startY);
      if (dx > 4 || dy > 4) drag.moved = true;
      if (!drag.moved) return;
      evt.preventDefault();
      var axis = currentAxis();
      var value = numberLineValueFromClientX(pos.x, svg, axis, 36, 480);
      var state = getNumberLineState(widget);
      if (drag.end === 'left') {
        if (value > state.right) value = state.right;
        state.left = value;
      } else {
        if (value < state.left) value = state.left;
        state.right = value;
      }
      updateDragVisual(state);
    }

    function onPointerUp(evt) {
      if (!drag) return;
      var end = drag.end;
      var moved = drag.moved;
      drag = null;
      widget.classList.remove('is-dragging');
      if (moved || widget.classList.contains('is-disabled')) return;
      var state = getNumberLineState(widget);
      if (end === 'left') state.leftClosed = !state.leftClosed;
      else state.rightClosed = !state.rightClosed;
      applyState(state);
    }

    widget.addEventListener('pointerdown', onPointerDown);
    widget.addEventListener('pointermove', onPointerMove);
    widget.addEventListener('pointerup', onPointerUp);
    widget.addEventListener('pointercancel', onPointerUp);

    widget.addEventListener('keydown', function (evt) {
      if (widget.classList.contains('is-disabled')) return;
      var target = evt.target;
      if (!target || !target.classList || !target.classList.contains('nl-endpoint')) return;
      var end = target.getAttribute('data-end');
      var state = getNumberLineState(widget);
      var axis = currentAxis();
      if (evt.key === 'Enter' || evt.key === ' ') {
        evt.preventDefault();
        if (end === 'left') state.leftClosed = !state.leftClosed;
        else state.rightClosed = !state.rightClosed;
        applyState(state);
        var focusSel = end === 'left' ? '.nl-left' : '.nl-right';
        var focusEl = widget.querySelector(focusSel);
        if (focusEl) focusEl.focus();
        return;
      }
      if (evt.key === 'ArrowLeft' || evt.key === 'ArrowRight') {
        evt.preventDefault();
        var delta = evt.key === 'ArrowLeft' ? -1 : 1;
        if (end === 'left') {
          state.left = Math.max(axis.min, Math.min(state.right, state.left + delta));
        } else {
          state.right = Math.min(axis.max, Math.max(state.left, state.right + delta));
        }
        applyState(state);
        var focusSel2 = end === 'left' ? '.nl-left' : '.nl-right';
        var focusEl2 = widget.querySelector(focusSel2);
        if (focusEl2) focusEl2.focus();
      }
    });
  }

  function resetNumberLineWidget(block) {
    var widget = block.querySelector('.free-response-number-line');
    if (!widget) return;
    var bounds = numberLineAxisBounds(block);
    widget.setAttribute('data-axis-min', String(bounds.min));
    widget.setAttribute('data-axis-max', String(bounds.max));
    var defaults = numberLineDefaultState(bounds);
    widget.classList.remove('is-correct', 'is-wrong', 'is-disabled', 'is-dragging');
    renderNumberLineWidget(widget, defaults);
  }

  function setNumberLineVisualState(block, correct) {
    var widget = block.querySelector('.free-response-number-line');
    if (!widget) return;
    widget.classList.remove('is-correct', 'is-wrong', 'is-disabled');
    if (correct) {
      widget.classList.add('is-correct', 'is-disabled');
    } else {
      widget.classList.add('is-wrong');
    }
  }

  function readVectorPairAnswer(block) {
    var fields = block.querySelectorAll('.free-response-input-vpair');
    return Array.prototype.map.call(fields, function (input) {
      return (input.value || '').trim();
    }).join('|');
  }

  function vectorPairRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var labels = [];
    try {
      labels = JSON.parse(block.getAttribute('data-answer-labels') || '[]');
    } catch (err) {
      labels = [];
    }
    if (!labels.length) {
      labels = [
        (block.getAttribute('data-label-a') || 'x').trim(),
        (block.getAttribute('data-label-b') || 'y').trim(),
      ];
    }
    var inner = labels.map(function (label) {
      return (
        '<div class="free-response-vpair-group">' +
        '<span class="free-response-vpair-label"><strong>' + esc(label) + '</strong> =</span>' +
        '<span class="free-response-vpair-bracket" aria-hidden="true">(</span>' +
        '<span class="free-response-vpair-stack">' +
        '<input type="text" class="free-response-input free-response-input-vpair" placeholder="top" autocomplete="off" inputmode="text" aria-label="' + esc(label) + ' top component">' +
        '<input type="text" class="free-response-input free-response-input-vpair" placeholder="bottom" autocomplete="off" inputmode="text" aria-label="' + esc(label) + ' bottom component">' +
        '</span>' +
        '<span class="free-response-vpair-bracket" aria-hidden="true">)</span>' +
        '</div>'
      );
    }).join('');
    return (
      '<div class="free-response-row free-response-row--vector-pair">' +
      '<div class="free-response-vpair-template" aria-label="Vector pair answer">' +
      inner +
      '</div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function vectorComboRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var labels = [];
    try {
      labels = JSON.parse(block.getAttribute('data-answer-labels') || '[]');
    } catch (err) {
      labels = [];
    }
    if (!labels.length) {
      labels = [
        (block.getAttribute('data-label-a') || 'b').trim(),
        (block.getAttribute('data-label-b') || 'c').trim(),
      ];
    }
    var inner = labels.map(function (label) {
      return (
        vcomboSignButtonHtml('+') +
        '<input type="text" class="free-response-input free-response-input-vcombo" placeholder="e.g. 1/5" ' +
        'autocomplete="off" inputmode="text" aria-label="Coefficient of ' + esc(label) + '">' +
        '<span class="free-response-vcombo-part"><strong>' + esc(label) + '</strong></span>'
      );
    }).join('');
    return (
      '<div class="free-response-row free-response-row--vector-combo">' +
      '<div class="free-response-vcombo-template" aria-label="Vector expression answer">' +
      inner +
      '</div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
  }

  function wireVectorComboSignButtons(block) {
    block.querySelectorAll('.free-response-vcombo-sign').forEach(function (btn) {
      if (btn.dataset.vcomboSignInit === '1') return;
      btn.dataset.vcomboSignInit = '1';
      btn.addEventListener('click', function () {
        if (btn.disabled) return;
        var sign = btn.getAttribute('data-sign') || '+';
        if (sign === '+' || sign === '\u002b') {
          btn.setAttribute('data-sign', '-');
          btn.textContent = '\u2212';
        } else {
          btn.setAttribute('data-sign', '+');
          btn.textContent = '+';
        }
      });
    });
  }

  function resetVectorComboSignButtons(block) {
    block.querySelectorAll('.free-response-vcombo-sign').forEach(function (btn) {
      var defaultSign = btn.getAttribute('data-default-sign') || '+';
      btn.setAttribute('data-sign', defaultSign);
      btn.textContent = defaultSign === '-' ? '\u2212' : '+';
      btn.disabled = false;
      btn.classList.remove('is-correct', 'is-wrong');
    });
  }

  function readCsqFieldValue(input, kind) {
    var role = input.getAttribute('data-csq-role') || '';
    var raw = (input.value || '').trim();
    if (!raw) return '';
    var normalized = raw.replace(/\u2212/g, '-');
    var parsed = parseFloat(normalized);
    if (isNaN(parsed)) return raw;

    var signBtn = signButtonForInput(input);
    if (!signBtn) return String(parsed);

    var sign = signBtn.getAttribute('data-sign') || '+';
    var signIsPlus = sign === '+' || sign === '\u002b';
    var magnitude = Math.abs(parsed);
    var userTypedNegative = /^-/.test(normalized);

    if (role === 'p') {
      var innerPlus = userTypedNegative ? false : signIsPlus;
      if (kind === 'minus') {
        return innerPlus ? String(-magnitude) : String(magnitude);
      }
      return innerPlus ? String(magnitude) : String(-magnitude);
    }

    if (userTypedNegative) return String(parsed);
    return signIsPlus ? String(magnitude) : String(-magnitude);
  }

  function readCompletedSquareAnswer(block) {
    var kind = (block.getAttribute('data-answer-template-kind') || 'plus').trim();
    var csqFields = block.querySelectorAll('.free-response-input-csq');
    return Array.prototype.map.call(csqFields, function (input) {
      return readCsqFieldValue(input, kind);
    }).join('|');
  }

  function vcomboSignButtonHtml(defaultSign) {
    var sign = defaultSign === '-' ? '-' : '+';
    var label = sign === '-' ? '\u2212' : '+';
    return (
      '<button type="button" class="btn btn-secondary free-response-vcombo-sign" data-sign="' + sign +
      '" data-default-sign="' + sign + '" aria-label="Toggle sign between plus and minus">' +
      label + '</button>'
    );
  }

  function csqSignButtonHtml(defaultSign) {
    var sign = defaultSign === '-' ? '-' : '+';
    var label = sign === '-' ? '\u2212' : '+';
    return (
      '<button type="button" class="btn btn-secondary free-response-csq-sign" data-sign="' + sign +
      '" data-default-sign="' + sign + '" aria-label="Toggle sign between plus and minus">' +
      label + '</button>'
    );
  }

  function wireCompletedSquareSignButtons(block) {
    block.querySelectorAll('.free-response-csq-sign').forEach(function (btn) {
      if (btn.dataset.csqSignInit === '1') return;
      btn.dataset.csqSignInit = '1';
      btn.addEventListener('click', function () {
        if (btn.disabled) return;
        var sign = btn.getAttribute('data-sign') || '+';
        if (sign === '+' || sign === '\u002b') {
          btn.setAttribute('data-sign', '-');
          btn.textContent = '\u2212';
        } else {
          btn.setAttribute('data-sign', '+');
          btn.textContent = '+';
        }
      });
    });
  }

  function resetCompletedSquareSignButtons(block) {
    block.querySelectorAll('.free-response-csq-sign').forEach(function (btn) {
      var defaultSign = btn.getAttribute('data-default-sign') || '+';
      btn.setAttribute('data-sign', defaultSign);
      btn.textContent = defaultSign === '-' ? '\u2212' : '+';
      btn.disabled = false;
      btn.classList.remove('is-correct', 'is-wrong');
    });
  }

  function completedSquareRowHtml(block) {
    var esc = function (s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    };
    var kind = (block.getAttribute('data-answer-template-kind') || 'plus').trim();
    var subject = (block.getAttribute('data-csq-subject') || '').trim();
    var input = function (placeholder, label, role) {
      return (
        '<input type="text" class="free-response-input free-response-input-csq" data-csq-role="' +
        esc(role || '') + '" placeholder="' +
        esc(placeholder) + '" autocomplete="off" inputmode="numeric" aria-label="' + esc(label) + '">'
      );
    };
    var inner = '';
    if (kind === 'scaled') {
      if (subject) {
        inner += '<span class="free-response-csq-part">' + esc(subject) + ' =</span>';
      }
      inner += input('a', 'Factor outside the bracket', 'a') +
        '<span class="free-response-csq-part">((x</span>' +
        csqSignButtonHtml('+') +
        input('p', 'Value p in (x \u00b1 p)', 'p') +
        '<span class="free-response-csq-part">)\u00b2</span>' +
        csqSignButtonHtml('+') +
        input('k', 'Constant k', 'k') +
        '<span class="free-response-csq-part">)</span>';
    } else if (kind === 'minus') {
      inner += '<span class="free-response-csq-part">(x</span>' +
        csqSignButtonHtml('-') +
        input('p', 'Value p in (x \u00b1 p)', 'p') +
        '<span class="free-response-csq-part">)\u00b2</span>' +
        csqSignButtonHtml('+') +
        input('k', 'Constant k', 'k');
    } else if (kind === 'expand') {
      inner += '<span class="free-response-csq-part">x\u00b2</span>' +
        csqSignButtonHtml('+') +
        input('b', 'Coefficient of x', 'b') +
        '<span class="free-response-csq-part">x</span>' +
        csqSignButtonHtml('+') +
        input('c', 'Constant term', 'c');
    } else {
      inner += '<span class="free-response-csq-part">(x</span>' +
        csqSignButtonHtml('+') +
        input('p', 'Value p in (x \u00b1 p)', 'p') +
        '<span class="free-response-csq-part">)\u00b2</span>' +
        csqSignButtonHtml('+') +
        input('k', 'Constant k', 'k');
    }
    return (
      '<div class="free-response-row free-response-row--completed-square">' +
      '<div class="free-response-csq-template" aria-label="Completed square answer">' +
      inner +
      '</div>' +
      '<button type="button" class="btn free-response-check-btn">Check</button>' +
      '</div>'
    );
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
    if (answerType === 'coordinate_pairs') {
      var coordLabels = [];
      try {
        coordLabels = JSON.parse(block.getAttribute('data-answer-labels') || '[]');
      } catch (e) {
        coordLabels = [];
      }
      if (!coordLabels.length) {
        coordLabels = ['1st solution (x, y)', '2nd solution (x, y)'];
      }
      var coordRows = coordLabels.map(function (label) {
        return (
          '<label class="free-response-field">' +
          '<span class="free-response-field-label">' + esc(label) + '</span>' +
          '<input type="text" class="free-response-input free-response-input-coord-pair" placeholder="e.g. (-2, 4)" autocomplete="off" inputmode="text" aria-label="' + esc(label) + '">' +
          '</label>'
        );
      }).join('');
      return (
        '<div class="free-response-row free-response-row--coordinate-pairs">' +
        '<div class="free-response-coord-pairs-stack">' + coordRows + '</div>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'number_list') {
      var listPh = freeResponsePlaceholder('number_list', formatHint);
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
      var ratioPh = freeResponsePlaceholder(answerType, formatHint);
      return (
        '<div class="free-response-row free-response-row--ratio">' +
        '<input type="text" class="free-response-input free-response-input-ratio" placeholder="' + esc(ratioPh) + '" autocomplete="off" inputmode="text" aria-label="Your ratio">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'linear_equation') {
      var eqPh = freeResponsePlaceholder('linear_equation', formatHint);
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
        return freeResponseFieldPlaceholder(
          fieldType,
          fieldType === 'number' ? formatHint : ''
        );
      }
      var rows = labels.map(function (label, index) {
        var safeLabel = esc(label);
        var fieldType = fieldTypes[index] || 'number';
        var ph = esc(fieldPlaceholder(fieldType));
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
    if (answerType === 'completed_square') {
      return completedSquareRowHtml(block);
    }
    if (answerType === 'vector_combo') {
      return vectorComboRowHtml(block);
    }
    if (answerType === 'vector_pair') {
      return vectorPairRowHtml(block);
    }
    if (answerType === 'linear_inequality') {
      return linearInequalityRowHtml(block);
    }
    if (answerType === 'compound_inequality') {
      return compoundInequalityRowHtml(block);
    }
    if (answerType === 'number_line') {
      return numberLineRowHtml(block);
    }
    if (answerType === 'formula_fraction') {
      return formulaFractionRowHtml(block);
    }
    if (answerType === 'pi_multiple') {
      var piPh = freeResponsePlaceholder('pi_multiple', formatHint);
      return (
        '<div class="free-response-row free-response-row--pi-multiple">' +
        '<input type="text" class="free-response-input free-response-input-pi" placeholder="' + esc(piPh) + '" autocomplete="off" inputmode="text" aria-label="Coefficient of pi">' +
        '<span class="free-response-pi-sep" aria-hidden="true">π</span>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'surd') {
      var surdPh = freeResponsePlaceholder('surd', formatHint);
      return (
        '<div class="free-response-row free-response-row--surd">' +
        '<input type="text" class="free-response-input free-response-input-surd" placeholder="' + esc(surdPh) + '" autocomplete="off" inputmode="text" aria-label="Surd answer">' +
        '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'algebraic') {
      return algebraicRowHtml(block);
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
    if (answerType === 'fraction') {
      var fracPh = freeResponsePlaceholder('fraction', formatHint);
      return (
        '<div class="free-response-row free-response-row--fraction">' +
        '<input type="text" class="free-response-input" placeholder="' + esc(fracPh) + '" autocomplete="off" inputmode="text" aria-label="Your answer">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'linear') {
      var linearPh = freeResponsePlaceholder('linear', formatHint);
      return (
        '<div class="free-response-row free-response-row--linear">' +
        '<input type="text" class="free-response-input" placeholder="' + esc(linearPh) + '" autocomplete="off" inputmode="text" aria-label="Your answer">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'quadratic_roots') {
      var rootsPh = freeResponsePlaceholder('quadratic_roots', formatHint);
      return (
        '<div class="free-response-row free-response-row--quadratic-roots">' +
        '<input type="text" class="free-response-input free-response-input-quadratic-roots" placeholder="' + esc(rootsPh) + '" autocomplete="off" inputmode="text" aria-label="Quadratic roots">' +
        '<button type="button" class="btn btn-secondary free-response-roots-insert-btn" data-insert="±" aria-label="Insert plus-minus symbol">±</button>' +
        '<button type="button" class="btn btn-secondary free-response-roots-insert-btn" data-insert="√" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'vector') {
      var vectorPh = freeResponsePlaceholder('vector', formatHint);
      return (
        '<div class="free-response-row free-response-row--vector">' +
        '<input type="text" class="free-response-input free-response-input-vector" placeholder="' + esc(vectorPh) + '" autocomplete="off" inputmode="text" aria-label="Column vector">' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    var placeholder = freeResponsePlaceholder(answerType, formatHint);
    var numberInputMode = freeResponseInputMode(answerType, formatHint);
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

  function wireQuadraticRootsInsertButtons(block) {
    var input = block.querySelector('.free-response-input-quadratic-roots');
    if (!input) return;
    block.querySelectorAll('.free-response-roots-insert-btn').forEach(function (btn) {
      if (btn.dataset.rootsInsertInit === '1') return;
      btn.dataset.rootsInsertInit = '1';
      btn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, btn.getAttribute('data-insert') || '');
      });
    });
  }

  function ensureFreeResponseRow(block, answerType) {
    if (answerType === 'completed_square') {
      var currentCsq = block.querySelector('.free-response-row');
      if (!currentCsq || freeResponseRowKind(currentCsq) !== 'completed_square') {
        if (currentCsq) currentCsq.remove();
        var feedback = block.querySelector('.free-response-feedback');
        var wrap = document.createElement('div');
        wrap.innerHTML = freeResponseRowHtml(block, answerType);
        var row = wrap.firstChild;
        var hint = block.querySelector('.free-response-csq-hint');
        if (hint) {
          block.insertBefore(row, hint);
        } else if (feedback) {
          block.insertBefore(row, feedback);
        } else {
          block.appendChild(row);
        }
      }
      return;
    }
    if (answerType === 'vector_combo') {
      var currentVcombo = block.querySelector('.free-response-row');
      if (!currentVcombo || freeResponseRowKind(currentVcombo) !== 'vector_combo') {
        if (currentVcombo) currentVcombo.remove();
        var vFeedback = block.querySelector('.free-response-feedback');
        var vWrap = document.createElement('div');
        vWrap.innerHTML = freeResponseRowHtml(block, answerType);
        var vRow = vWrap.firstChild;
        var vHint = block.querySelector('.free-response-vcombo-hint');
        if (vHint) {
          block.insertBefore(vRow, vHint);
        } else if (vFeedback) {
          block.insertBefore(vRow, vFeedback);
        } else {
          block.appendChild(vRow);
        }
      }
      return;
    }
    if (answerType === 'vector_pair') {
      var currentVpair = block.querySelector('.free-response-row');
      if (!currentVpair || freeResponseRowKind(currentVpair) !== 'vector_pair') {
        if (currentVpair) currentVpair.remove();
        var pFeedback = block.querySelector('.free-response-feedback');
        var pWrap = document.createElement('div');
        pWrap.innerHTML = freeResponseRowHtml(block, answerType);
        var pRow = pWrap.firstChild;
        var pHint = block.querySelector('.free-response-vpair-hint');
        if (pHint) {
          block.insertBefore(pRow, pHint);
        } else if (pFeedback) {
          block.insertBefore(pRow, pFeedback);
        } else {
          block.appendChild(pRow);
        }
      }
      return;
    }
    if (answerType === 'linear_inequality' || answerType === 'compound_inequality') {
      var currentIneq = block.querySelector('.free-response-row');
      var expectedKind = answerType;
      if (!currentIneq || freeResponseRowKind(currentIneq) !== expectedKind) {
        if (currentIneq) currentIneq.remove();
        var iFeedback = block.querySelector('.free-response-feedback');
        var iWrap = document.createElement('div');
        iWrap.innerHTML = freeResponseRowHtml(block, answerType);
        var iRow = iWrap.firstChild;
        var iHint = block.querySelector('.free-response-ineq-hint');
        if (iHint) {
          block.insertBefore(iRow, iHint);
        } else if (iFeedback) {
          block.insertBefore(iRow, iFeedback);
        } else {
          block.appendChild(iRow);
        }
      }
      return;
    }
    if (answerType === 'number_line') {
      var currentNl = block.querySelector('.free-response-row');
      if (!currentNl || freeResponseRowKind(currentNl) !== 'number_line') {
        if (currentNl) currentNl.remove();
        var nlFeedback = block.querySelector('.free-response-feedback');
        var nlWrap = document.createElement('div');
        nlWrap.innerHTML = freeResponseRowHtml(block, answerType);
        var nlRow = nlWrap.firstChild;
        var nlHint = block.querySelector('.free-response-ineq-hint');
        if (nlHint) {
          block.insertBefore(nlRow, nlHint);
        } else if (nlFeedback) {
          block.insertBefore(nlRow, nlFeedback);
        } else {
          block.appendChild(nlRow);
        }
      }
      return;
    }
    if (answerType === 'formula_fraction') {
      var currentFf = block.querySelector('.free-response-row');
      if (!currentFf || freeResponseRowKind(currentFf) !== 'formula_fraction') {
        if (currentFf) currentFf.remove();
        var ffFeedback = block.querySelector('.free-response-feedback');
        var ffWrap = document.createElement('div');
        ffWrap.innerHTML = freeResponseRowHtml(block, answerType);
        var ffRow = ffWrap.firstChild;
        var ffHint = block.querySelector('.free-response-formula-frac-hint');
        if (ffHint) {
          block.insertBefore(ffRow, ffHint);
        } else if (ffFeedback) {
          block.insertBefore(ffRow, ffFeedback);
        } else {
          block.appendChild(ffRow);
        }
      }
      return;
    }
    var current = block.querySelector('.free-response-row');
    var rowKind = (answerType === 'ratio' || answerType === 'ratio_exact') ? 'ratio'
      : (answerType === 'linear_equation') ? 'linear_equation'
      : (answerType === 'fraction') ? 'fraction'
      : (answerType === 'linear') ? 'linear'
      : (answerType === 'quadratic_roots') ? 'quadratic_roots'
      : (answerType === 'vector') ? 'vector'
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
    if (answerType === 'completed_square') {
      wireCompletedSquareSignButtons(block);
    }
    if (answerType === 'vector_combo') {
      wireVectorComboSignButtons(block);
    }
    if (answerType === 'quadratic_roots') {
      wireQuadraticRootsInsertButtons(block);
    }
    if (answerType === 'number_line') {
      wireNumberLineWidget(block);
    }
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
    resetCompletedSquareSignButtons(block);
    resetVectorComboSignButtons(block);
    resetNumberLineWidget(block);
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
                fieldFeedback.textContent = '\u2713 ' + freeResponseCorrectFeedback(data, userValue);
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
    var answerType = resolveFreeResponseAnswerType(block);
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
      if (answerType === 'coordinate_pairs') {
        var coordInputs = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-coord-pair')
        );
        return { fields: coordInputs, all: coordInputs };
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
      if (answerType === 'formula_fraction') {
        var ffNum = block.querySelector('.free-response-input-formula-frac-num');
        var ffDen = block.querySelector('.free-response-input-formula-frac-den');
        return {
          num: ffNum,
          den: ffDen,
          all: [ffNum, ffDen].filter(Boolean),
        };
      }
      if (answerType === 'completed_square') {
        var csqFields = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-csq')
        );
        return { fields: csqFields, all: csqFields };
      }
      if (answerType === 'vector_combo') {
        var vcomboFields = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-vcombo')
        );
        return { fields: vcomboFields, all: vcomboFields };
      }
      if (answerType === 'vector_pair') {
        var vpairFields = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-vpair')
        );
        return { fields: vpairFields, all: vpairFields };
      }
      if (answerType === 'linear_inequality') {
        var ineqVal = block.querySelector('.free-response-input-ineq-value');
        var ineqSign = block.querySelector('.free-response-ineq-sign');
        return { value: ineqVal, sign: ineqSign, all: [ineqSign, ineqVal].filter(Boolean) };
      }
      if (answerType === 'compound_inequality') {
        var bounds = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-compound-bound')
        );
        var cSigns = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-compound-sign')
        );
        return { bounds: bounds, signs: cSigns, all: bounds.concat(cSigns) };
      }
      if (answerType === 'number_line') {
        var nlWidget = block.querySelector('.free-response-number-line');
        return { widget: nlWidget, all: nlWidget ? [nlWidget] : [] };
      }
      if (answerType === 'number_fields') {
        var fields = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-field')
        );
        return { fields: fields, all: fields };
      }
      var single = block.querySelector('.free-response-row--number .free-response-input')
        || block.querySelector('.free-response-row--fraction .free-response-input')
        || block.querySelector('.free-response-row--linear .free-response-input')
        || block.querySelector('.free-response-row--quadratic-roots .free-response-input')
        || block.querySelector('.free-response-row--vector .free-response-input');
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
      if (answerType === 'coordinate_pairs') {
        return readCoordinatePairsAnswer(block);
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
      if (answerType === 'completed_square') {
        return readCompletedSquareAnswer(block);
      }
      if (answerType === 'vector_combo') {
        return readVectorComboAnswer(block);
      }
      if (answerType === 'vector_pair') {
        return readVectorPairAnswer(block);
      }
      if (answerType === 'linear_inequality') {
        return readLinearInequalityAnswer(block);
      }
      if (answerType === 'compound_inequality') {
        return readCompoundInequalityAnswer(block);
      }
      if (answerType === 'number_line') {
        return readNumberLineAnswer(block);
      }
      if (answerType === 'formula_fraction') {
        return readFormulaFractionAnswer(block);
      }
      if (answerType === 'algebraic') {
        return readAlgebraicAnswer(block);
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
      if (answerType === 'coordinate_pairs') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'power') {
        return !(inputs.base && (inputs.base.value || '').trim()) || !(inputs.index && (inputs.index.value || '').trim());
      }
      if (answerType === 'number_fields') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'completed_square') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'vector_combo') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'vector_pair') {
        return !inputs.fields.length || inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'linear_inequality') {
        return !(inputs.value && (inputs.value.value || '').trim());
      }
      if (answerType === 'compound_inequality') {
        return !inputs.bounds.length || inputs.bounds.some(function (input) {
          return !(input.value || '').trim();
        });
      }
      if (answerType === 'number_line') {
        return !readNumberLineAnswer(block);
      }
      if (answerType === 'formula_fraction') {
        return !readFormulaFractionAnswer(block);
      }
      if (answerType === 'algebraic_fraction') {
        return !(inputs.num && (inputs.num.value || '').trim());
      }
      return !readUserAnswer();
    }

    function emptyMessage() {
      if (answerType === 'standard_form') return 'Enter the coefficient and power of 10.';
      if (answerType === 'number_pair') return 'Enter both values.';
      if (answerType === 'coordinate_pairs') return 'Enter both coordinate pairs.';
      if (answerType === 'power') return 'Enter the base and index.';
      if (answerType === 'number_fields') return 'Complete every answer field.';
      if (answerType === 'completed_square') return 'Use + or − for each term, then fill in every blank.';
      if (answerType === 'vector_combo') return 'Use + or − for each term, then enter each coefficient.';
      if (answerType === 'vector_pair') return 'Enter both components of each vector.';
      if (answerType === 'linear_inequality') return 'Choose the sign, then enter the value.';
      if (answerType === 'compound_inequality') return 'Enter both bounds and choose each sign.';
      if (answerType === 'number_line') return 'Set both endpoints on the number line.';
      if (answerType === 'formula_fraction') return 'Enter the numerator and denominator.';
      if (answerType === 'number_list') return 'Enter your answer.';
      if (answerType === 'pi_multiple') return 'Enter the coefficient of π.';
      if (answerType === 'surd') return 'Enter your answer in surd form.';
      if (answerType === 'algebraic') return 'Enter your simplified expression.';
      if (answerType === 'algebraic_fraction') return 'Enter the surd numerator (denominator optional if it is 1).';
      return 'Enter an answer first.';
    }

    function setInputState(correct) {
      var inputs = activeInputs();
      if (answerType === 'number_line') {
        setNumberLineVisualState(block, correct);
        block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
          btn.disabled = correct;
        });
        return;
      }
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
      block.querySelectorAll('.free-response-csq-sign, .free-response-vcombo-sign').forEach(function (btn) {
        btn.disabled = correct;
        btn.classList.remove('is-correct', 'is-wrong');
        if (correct) {
          btn.classList.add('is-correct');
        }
      });
    }

    function submitAnswer() {
      var inputs = activeInputs();
      if (answerType === 'number_line') {
        var nlLocked = block.querySelector('.free-response-number-line');
        if (nlLocked && nlLocked.classList.contains('is-disabled')
          && nlLocked.classList.contains('is-correct')) {
          return;
        }
      } else if (inputs.all.length && inputs.all[0] && inputs.all[0].disabled) {
        return;
      }

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
      if (answerType === 'number_line') {
        var nlBusy = block.querySelector('.free-response-number-line');
        if (nlBusy) nlBusy.classList.add('is-disabled');
      } else {
        inputs.all.forEach(function (input) {
          input.disabled = true;
        });
        block.querySelectorAll('.free-response-csq-sign, .free-response-vcombo-sign').forEach(function (btn) {
          btn.disabled = true;
        });
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
          if (data.correct) {
            setInputState(true);
            if (feedback) {
              feedback.textContent = '\u2713 ' + freeResponseCorrectFeedback(data, userAnswer);
              feedback.style.color = '#16a34a';
            }
          } else {
            setInputState(false);
            if (answerType === 'number_line') {
              var nlWrong = block.querySelector('.free-response-number-line');
              if (nlWrong) nlWrong.classList.remove('is-disabled');
            }
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
          if (answerType === 'number_line') {
            var nlErr = block.querySelector('.free-response-number-line');
            if (nlErr) nlErr.classList.remove('is-disabled');
          } else {
            inputs.all.forEach(function (input) {
              input.disabled = false;
            });
          }
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
    if (answerType !== 'number_line') {
      activeInputs().all.forEach(function (input) {
        input.addEventListener('keydown', function (event) {
          if (event.key === 'Enter') {
            event.preventDefault();
            submitAnswer();
          }
        });
      });
    }
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
        applyFreeResponseProblemMetadata(free, problem);
        var answerType = resolveFreeResponseAnswerType(free);
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
