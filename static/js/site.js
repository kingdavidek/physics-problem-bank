/**
 * Problem generator: cascade Level → Subject → Topic so only valid combinations show.
 * Also syncs Quick Test hidden fields and handles MCQ answer buttons on the index page.
 */
(function () {
  'use strict';

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function apiHeaders(extra) {
    var headers = Object.assign({ Accept: 'application/json' }, extra || {});
    var token = csrfToken();
    if (token) headers['X-CSRF-Token'] = token;
    return headers;
  }

  function celebrateResult(ok, target, revealTarget) {
    if (!window.pbCelebrate) return;
    if (ok) window.pbCelebrate.correct(target);
    else window.pbCelebrate.wrong(target, revealTarget || null);
  }

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
    var launchMode = !!document.querySelector('[data-launch-gcse-only="1"]');

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
      setOptionVisibility(subjectSel, function (opt) {
        if (launchMode && level === 'gcse' && opt.dataset.launchSubject !== '1') {
          return false;
        }
        return opt.dataset.level === level;
      });
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

  function initRevisionPlanForm() {
    var form = document.querySelector('.revision-plan-form');
    if (!form) return;
    var levelSel = form.querySelector('#revision-plan-level') || form.querySelector('select[name="level"]');
    var subjectSel = form.querySelector('#revision-plan-subject') || form.querySelector('select[name="subject"]');
    if (!levelSel || !subjectSel) return;

    function syncSubjectDropdown() {
      var level = levelSel.value;
      var prevSubject = subjectSel.value;
      setOptionVisibility(subjectSel, subjectPredicate(level));
      ensureValidSelection(subjectSel, prevSubject);
    }

    levelSel.addEventListener('change', syncSubjectDropdown);
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
    if (answerType === 'quadratic_roots') {
      return readQuadraticRootsUserAnswer(block);
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
    var partial = checked && !correct && inputs.some(function (input) {
      return input.classList.contains('is-partial');
    });
    var score = block.dataset.textScore;
    var scoreTotal = block.dataset.textScoreTotal;
    return {
      checked: checked,
      correct: checked ? correct : null,
      partial: partial,
      score: score !== undefined && score !== '' ? parseInt(score, 10) : null,
      scoreTotal: scoreTotal !== undefined && scoreTotal !== '' ? parseInt(scoreTotal, 10) : null,
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
      score: frState.score,
      scoreTotal: frState.scoreTotal,
    };
  }

  function syncQuickTestFormFields() {
    var state = collectQuickTestAnswerState();
    var userEl = document.getElementById('qt-user-answer');
    var checkedEl = document.getElementById('qt-checked');
    var correctEl = document.getElementById('qt-correct');
    var scoreEl = document.getElementById('qt-score');
    var scoreTotalEl = document.getElementById('qt-score-total');
    if (userEl) userEl.value = state.userAnswer || '';
    if (checkedEl) checkedEl.value = state.checked ? '1' : '0';
    if (correctEl) {
      correctEl.value = state.correct === true ? '1' : (state.correct === false ? '0' : '');
    }
    if (scoreEl) scoreEl.value = state.score != null ? String(state.score) : '';
    if (scoreTotalEl) scoreTotalEl.value = state.scoreTotal != null ? String(state.scoreTotal) : '';
    return state;
  }

  function dispatchQuicktestChecked(detail) {
    if (!document.getElementById('quicktest-quiz-runner')) return;
    document.dispatchEvent(new CustomEvent('pb-quicktest-checked', {
      bubbles: true,
      detail: detail || collectQuickTestAnswerState(),
    }));
  }

  function initQuickTestNextForm() {
    var form = document.getElementById('quicktest-next-form');
    if (!form) return;
    form.addEventListener('submit', function () {
      syncQuickTestFormFields();
    });
  }

  function resetMcqInline(block) {
    var feedback = block.querySelector('.mcq-feedback')
      || (block.parentElement && block.parentElement.querySelector('.mcq-feedback'));
    block.querySelectorAll('.mcq-btn').forEach(function (b) {
      b.disabled = false;
      b.classList.remove('is-correct', 'is-wrong', 'is-selected');
    });
    if (feedback) {
      feedback.textContent = '';
      feedback.style.color = '';
    }
    var retryWrap = block.querySelector('.mcq-retry-wrap');
    if (retryWrap) {
      retryWrap.hidden = true;
    }
    removeWrongAnswerReflection(block);
    delete block.dataset.reflectionOffered;
    removeCohortHint(block);
    block.dispatchEvent(new CustomEvent('mcq-reset', { bubbles: true }));
  }

  function findMcqFeedback(block) {
    return block.querySelector('.mcq-feedback')
      || (block.parentElement && block.parentElement.querySelector('.mcq-feedback'));
  }

  var REFLECTION_CHIP_OPTIONS = [
    { type: 'calculation_error', label: 'Calculation slip' },
    { type: 'misread_question', label: 'Misread the question' },
    { type: 'forgot_formula', label: 'Forgot a formula or rule' },
    { type: 'guessed', label: 'I guessed' },
    { type: 'other', label: 'Something else' },
  ];

  function isReflectionEligible() {
    var wrapper = document.querySelector('.site-wrapper');
    return Boolean(wrapper && wrapper.getAttribute('data-user-logged-in') === '1');
  }

  function trackableFromBlock(block) {
    if (!block || !block.dataset.level) return null;
    return {
      level: block.dataset.level,
      subject: block.dataset.subject,
      topic: block.dataset.topic,
      difficulty: block.dataset.difficulty || 'foundational',
    };
  }

  function removeWrongAnswerReflection(host) {
    if (!host) return;
    var panel = host.querySelector('.wrong-answer-reflection');
    if (panel) panel.remove();
  }

  function saveWrongAnswerReflection(context, source, payload) {
    var body = {
      level: context.level,
      subject: context.subject,
      topic: context.topic,
      difficulty: context.difficulty,
      source: source,
      reflection_text: payload.text || '',
    };
    if (payload.promptType) body.prompt_type = payload.promptType;
    if (payload.attemptId) body.attempt_id = payload.attemptId;
    return fetch('/api/v1/me/reflections', {
      method: 'POST',
      headers: apiHeaders({
        'Content-Type': 'application/json',
      }),
      credentials: 'same-origin',
      body: JSON.stringify(body),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var err = new Error((data && data.error) || 'Could not save reflection');
          err.data = data;
          throw err;
        }
        return data;
      });
    });
  }

  function showWrongAnswerReflection(host, context, source, attemptId) {
    if (!host || !context) return;
    removeWrongAnswerReflection(host);

    var panel = document.createElement('div');
    panel.className = 'wrong-answer-reflection';
    panel.setAttribute('role', 'region');
    panel.setAttribute('aria-label', 'Optional reflection');

    var title = document.createElement('p');
    title.className = 'wrong-answer-reflection-title';
    title.textContent = 'What tripped you up?';
    var optional = document.createElement('span');
    optional.className = 'wrong-answer-reflection-optional';
    optional.textContent = ' (optional)';
    title.appendChild(optional);
    panel.appendChild(title);

    var chips = document.createElement('div');
    chips.className = 'wrong-answer-reflection-chips';
    var selectedPrompt = null;

    var textarea = document.createElement('textarea');
    textarea.className = 'wrong-answer-reflection-input';
    textarea.rows = 2;
    textarea.maxLength = 500;
    textarea.placeholder = 'Anything else? (optional)';
    textarea.setAttribute('aria-label', 'Optional reflection note');

    var actions = document.createElement('div');
    actions.className = 'wrong-answer-reflection-actions';

    var saveBtn = document.createElement('button');
    saveBtn.type = 'button';
    saveBtn.className = 'btn btn-primary btn-sm wrong-answer-reflection-save';
    saveBtn.textContent = 'Save note';

    var skipBtn = document.createElement('button');
    skipBtn.type = 'button';
    skipBtn.className = 'btn-link wrong-answer-reflection-skip';
    skipBtn.textContent = 'Not now';

    var status = document.createElement('p');
    status.className = 'wrong-answer-reflection-status';
    status.hidden = true;

    function dismissPanel() {
      panel.remove();
    }

    function showSaved() {
      chips.hidden = true;
      textarea.hidden = true;
      actions.hidden = true;
      status.hidden = false;
      status.textContent = 'Thanks \u2014 noted.';
      status.style.color = '#16a34a';
      window.setTimeout(dismissPanel, 1400);
    }

    function persistReflection(promptType) {
      var text = (textarea.value || '').trim();
      if (!promptType && !text) return Promise.reject(new Error('empty'));
      saveBtn.disabled = true;
      skipBtn.disabled = true;
      chips.querySelectorAll('.wrong-answer-reflection-chip').forEach(function (btn) {
        btn.disabled = true;
      });
      return saveWrongAnswerReflection(context, source, {
        promptType: promptType,
        text: text,
        attemptId: attemptId,
      }).then(function () {
        showSaved();
      }).catch(function () {
        saveBtn.disabled = false;
        skipBtn.disabled = false;
        chips.querySelectorAll('.wrong-answer-reflection-chip').forEach(function (btn) {
          btn.disabled = false;
        });
        if (typeof showAppToast === 'function') {
          showAppToast('Could not save your note \u2014 try again.', 'error');
        }
      });
    }

    REFLECTION_CHIP_OPTIONS.forEach(function (option) {
      var chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'btn btn-outline btn-sm wrong-answer-reflection-chip';
      chip.textContent = option.label;
      chip.setAttribute('data-prompt-type', option.type);
      chip.addEventListener('click', function () {
        selectedPrompt = option.type;
        chips.querySelectorAll('.wrong-answer-reflection-chip').forEach(function (btn) {
          btn.classList.toggle('is-selected', btn === chip);
        });
        var text = (textarea.value || '').trim();
        if (!text) {
          persistReflection(option.type);
        }
      });
      chips.appendChild(chip);
    });
    panel.appendChild(chips);
    panel.appendChild(textarea);

    saveBtn.addEventListener('click', function () {
      persistReflection(selectedPrompt);
    });
    skipBtn.addEventListener('click', dismissPanel);
    actions.appendChild(saveBtn);
    actions.appendChild(skipBtn);
    panel.appendChild(actions);
    panel.appendChild(status);
    host.appendChild(panel);
  }

  function offerWrongAnswerReflection(block, source, data, recordThisAttempt) {
    if (!recordThisAttempt || !isReflectionEligible() || !block) return;
    if (data && (data.correct || isTextPartialScore(data))) return;
    if (block.dataset.reflectionOffered === '1') return;
    var context = trackableFromBlock(block);
    if (!context) return;
    block.dataset.reflectionOffered = '1';
    var attemptId = data && data.attempt_id != null ? data.attempt_id : null;
    showWrongAnswerReflection(block, context, source, attemptId);
  }

  function offerWrongAnswerReflectionMcq(block, attemptId, recordThisAttempt) {
    if (!recordThisAttempt || !isReflectionEligible() || !block) return;
    if (block.dataset.reflectionOffered === '1') return;
    var context = trackableFromBlock(block);
    if (!context) return;
    block.dataset.reflectionOffered = '1';
    showWrongAnswerReflection(block, context, 'mcq', attemptId);
  }

  function formatCohortHint(cohort) {
    if (!cohort || cohort.wrong_pct == null || !cohort.sample_size) return '';
    var pct = Math.round(Number(cohort.wrong_pct));
    if (!isFinite(pct)) return '';
    var attempts = Number(cohort.sample_size);
    var attemptLabel = attempts === 1 ? 'attempt' : 'attempts';
    return 'About ' + pct + '% of students got this wrong (' + attempts + ' ' + attemptLabel + ').';
  }

  function removeCohortHint(host) {
    if (!host) return;
    var el = host.querySelector('.cohort-hint');
    if (el) el.remove();
  }

  function showCohortHint(host, cohort) {
    if (!host) return;
    var text = formatCohortHint(cohort);
    removeCohortHint(host);
    if (!text) return;
    var el = document.createElement('p');
    el.className = 'cohort-hint';
    el.textContent = text;
    host.appendChild(el);
  }

  function persistMcqAnswer(block, userAnswer, correctAnswer, isCorrect) {
    if (!block.dataset.level) return Promise.resolve({ attempt_id: null, cohort: null, correct: isCorrect });
    return fetch('/api/v1/generator/mcq-answer', {
      method: 'POST',
      headers: apiHeaders({
        'Content-Type': 'application/json',
      }),
      credentials: 'same-origin',
      body: JSON.stringify({
        level: block.dataset.level,
        subject: block.dataset.subject,
        topic: block.dataset.topic,
        difficulty: block.dataset.difficulty || 'foundational',
        user_answer: userAnswer,
      }),
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            return { attempt_id: null, cohort: null, correct: isCorrect };
          }
          return {
            attempt_id: data.attempt_id != null ? data.attempt_id : null,
            cohort: data.cohort || null,
            correct: typeof data.correct === 'boolean' ? data.correct : isCorrect,
            correct_answer: data.correct_answer || correctAnswer,
          };
        });
      })
      .catch(function () { return { attempt_id: null, cohort: null, correct: isCorrect }; });
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
        block.querySelectorAll('.mcq-btn').forEach(function (b) {
          b.disabled = true;
          b.classList.toggle('is-selected', b === btn);
        });
        var letter = (btn.dataset.letter || '').trim().charAt(0);
        block.dataset.userChoice = letter;
        var isCorrect = letter === correctLetter;
        if (isCorrect) {
          btn.classList.add('is-correct');
          if (feedback) {
            feedback.textContent = '\u2713 Correct!';
            feedback.style.color = '#16a34a';
          }
          celebrateResult(true, btn);
          block.dispatchEvent(new CustomEvent('mcq-correct', { bubbles: true }));
        } else {
          btn.classList.add('is-wrong');
          var correctBtn = null;
          block.querySelectorAll('.mcq-btn').forEach(function (b) {
            var bLetter = (b.dataset.letter || '').trim().charAt(0);
            if (bLetter === correctLetter) {
              b.classList.add('is-correct');
              correctBtn = b;
            }
          });
          celebrateResult(false, btn, correctBtn);
          if (feedback) {
            feedback.textContent = '\u2717 Not quite \u2014 the correct answer is highlighted.';
            feedback.style.color = '#dc2626';
          }
          showMcqRetry(block);
        }
        if (trackable && block.dataset.mcqPersisted !== '1') {
          block.dataset.mcqPersisted = '1';
          var recordThisAttempt = true;
          var persistPromise = persistMcqAnswer(block, letter, correctRaw, isCorrect);
          persistPromise.then(function (result) {
            if (!isCorrect) {
              offerWrongAnswerReflectionMcq(block, result.attempt_id, recordThisAttempt);
            }
            showCohortHint(block, result.cohort);
            if (block.dataset.level && block.dataset.topic) {
              document.dispatchEvent(new CustomEvent('pb-buddy-refetch', {
                detail: {
                  level: block.dataset.level,
                  subject: block.dataset.subject || '',
                  topic: block.dataset.topic,
                },
              }));
            }
          });
        }
        dispatchQuicktestChecked({
          userAnswer: letter,
          checked: true,
          correct: isCorrect,
        });
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

  function isCoachingAnswerHint(hint) {
    var h = String(hint || '').toLowerCase();
    if (!h) return false;
    return (
      h.indexOf('mention') >= 0 ||
      h.indexOf('key ideas') >= 0 ||
      h.indexOf('your own words') >= 0 ||
      h.indexOf('below count') >= 0 ||
      h.indexOf('any of the') >= 0 ||
      h.indexOf('choose the correct description') >= 0
    );
  }

  function freeResponseFieldPlaceholder(fieldType, formatHint) {
    if (formatHint && !isCoachingAnswerHint(formatHint)) return formatHint;
    if (fieldType === 'keyword' || fieldType === 'text') return 'Enter your answer';
    if (fieldType === 'sql') return 'Write your SQL query';
    if (fieldType === 'linear_equation') return 'e.g. y = 2x + 3';
    if (fieldType === 'two_var_equation') return 'e.g. 10c + 11t = 53';
    if (fieldType === 'linear_inequality') return 'e.g. m < 40';
    if (fieldType === 'algebraic') return 'e.g. d/50 + d/100 or 3x + 6';
    if (fieldType === 'vector') return 'e.g. (3, 4)';
    if (fieldType === 'bearing') return 'e.g. 045';
    if (fieldType === 'number_estimate') return 'Your estimate from the graph';
    if (fieldType === 'fraction') return 'e.g. 3/4';
    if (fieldType === 'surd') return 'e.g. 4√3';
    if (fieldType === 'ratio' || fieldType === 'ratio_exact') return 'e.g. 3:5';
    if (fieldType === 'binary') return 'e.g. 1101';
    if (fieldType === 'hex') return 'e.g. FF';
    return 'Number or fraction';
  }

  function freeResponsePlaceholder(answerType, formatHint) {
    if (formatHint && !isCoachingAnswerHint(formatHint)) return formatHint;
    if (answerType === 'text' || answerType === 'keyword') return 'Enter your answer';
    if (answerType === 'sql') return 'Write your SQL query (one statement)';
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

  function splitQuadraticRootsRaw(raw) {
    var s = String(raw || '').trim();
    if (!s) return [];
    if (s.charAt(0) === '{' && s.charAt(s.length - 1) === '}') {
      s = s.slice(1, -1).trim();
    }
    s = s.replace(/\s+or\s+/gi, ',').replace(/\s+and\s+/gi, ',');
    var sep = (s.indexOf('|') >= 0 && s.indexOf(',') < 0) ? '|' : ',';
    return s.split(sep).map(function (part) {
      return part.trim();
    }).filter(Boolean);
  }

  function quadraticRootsFieldCount(block) {
    if (!block) return 0;
    var labels = [];
    try {
      labels = JSON.parse(block.getAttribute('data-answer-labels') || '[]');
    } catch (e) {
      labels = [];
    }
    if (labels && labels.length >= 2) return labels.length;
    return splitQuadraticRootsRaw(block.getAttribute('data-correct-raw') || '').length;
  }

  function readQuadraticRootsUserAnswer(block) {
    var multi = block.querySelectorAll('.free-response-input-quadratic-root');
    if (multi.length >= 2) {
      return Array.prototype.map.call(multi, function (input) {
        return (input.value || '').trim();
      }).join(', ');
    }
    var single = block.querySelector('.free-response-input-quadratic-roots')
      || block.querySelector('.free-response-input');
    return single ? (single.value || '').trim() : '';
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

  function freeResponseWrongFeedback(block, data) {
    var base = (data && data.feedback) || 'Not quite \u2014 try again.';
    if (data && data.score_total != null && data.score > 0 && data.score < data.score_total) {
      base = data.feedback || (data.score + '/' + data.score_total + ' key ideas found.');
    }
    var wrongHint = block.getAttribute('data-wrong-hint') || '';
    return wrongHint ? (base + ' ' + wrongHint) : base;
  }

  function isTextPartialScore(data) {
    return Boolean(
      data
      && data.score_total != null
      && data.score != null
      && data.score > 0
      && data.score < data.score_total
    );
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
    if (problem.answer_input_lines !== undefined && problem.answer_input_lines !== null
      && problem.answer_input_lines !== '') {
      block.setAttribute('data-answer-input-lines', String(problem.answer_input_lines));
    } else {
      block.removeAttribute('data-answer-input-lines');
    }
    if (problem.answer_wrong_hint) {
      block.setAttribute('data-wrong-hint', problem.answer_wrong_hint);
    } else {
      block.removeAttribute('data-wrong-hint');
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
    if (problem.answer_field_options && problem.answer_field_options.length) {
      block.setAttribute('data-field-options', JSON.stringify(problem.answer_field_options));
    } else {
      block.setAttribute('data-field-options', '[]');
    }
    if (problem.answer_field_pick_counts && problem.answer_field_pick_counts.length) {
      block.setAttribute('data-field-pick-counts', JSON.stringify(problem.answer_field_pick_counts));
    } else {
      block.removeAttribute('data-field-pick-counts');
    }
    if (problem.answer_field_row_sizes && problem.answer_field_row_sizes.length) {
      block.setAttribute('data-field-row-sizes', JSON.stringify(problem.answer_field_row_sizes));
    } else {
      block.setAttribute('data-field-row-sizes', '[]');
    }
    if (problem.answer_field_group_labels && problem.answer_field_group_labels.length) {
      block.setAttribute('data-field-group-labels', JSON.stringify(problem.answer_field_group_labels));
    } else {
      block.setAttribute('data-field-group-labels', '[]');
    }
    if (problem.answer_inline_sections) {
      block.setAttribute('data-inline-sections', '1');
    } else {
      block.removeAttribute('data-inline-sections');
    }
    if (problem.answer_step_bank && problem.answer_step_bank.length) {
      block.setAttribute('data-step-bank', JSON.stringify(problem.answer_step_bank));
    } else {
      block.setAttribute('data-step-bank', '[]');
    }
    if (problem.answer_order_matters) {
      block.setAttribute('data-order-matters', '1');
    } else {
      block.setAttribute('data-order-matters', '0');
    }
    if (problem.answer_pair_sep) {
      block.setAttribute('data-pair-sep', problem.answer_pair_sep);
    } else {
      block.setAttribute('data-pair-sep', 'and');
    }
    if (problem.answer_tests && problem.answer_tests.length) {
      block.setAttribute('data-answer-tests', JSON.stringify(problem.answer_tests));
    } else {
      block.setAttribute('data-answer-tests', '[]');
    }
    if (problem.answer_python_starter) {
      block.setAttribute('data-python-starter', problem.answer_python_starter);
    } else {
      block.removeAttribute('data-python-starter');
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
    if (row.classList.contains('free-response-row--proof-steps')) return 'proof_steps';
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
    if (row.classList.contains('free-response-row--python-run')) return 'python_run';
    if (row.classList.contains('free-response-row--sql')) return 'sql';
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
      '<button type="button" class="btn btn-secondary free-response-pi-btn" aria-label="Insert pi symbol">π</button>' +
      '<button type="button" class="btn btn-secondary free-response-square-btn" aria-label="Insert squared symbol">x²</button>' +
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

  function htmlEscape(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function numberFieldMcqRowHtml(label, options) {
    var letters = 'ABCD';
    var esc = htmlEscape;
    var buttons = (options || []).map(function (opt, i) {
      return (
        '<button type="button" class="btn mcq-btn" data-letter="' + letters.charAt(i) + '">' +
        esc(opt) +
        '</button>'
      );
    }).join('');
    return (
      '<div class="free-response-field-row">' +
      '<span class="free-response-field-label">' + esc(label) + '</span>' +
      '<div class="mcq-inline free-response-field-mcq">' + buttons + '</div>' +
      '<p class="free-response-field-feedback" aria-live="polite"></p>' +
      '</div>'
    );
  }

  function sqlInputLines(block, fallback) {
    var raw = block && block.getAttribute('data-answer-input-lines');
    if (raw !== null && raw !== '') {
      var parsed = parseInt(raw, 10);
      if (!isNaN(parsed) && parsed > 0) return parsed;
    }
    return fallback == null ? 3 : fallback;
  }

  function numberFieldRowHtml(label, fieldType, fieldOptions, formatHint) {
    var esc = htmlEscape;
    if (fieldType === 'mcq') {
      return numberFieldMcqRowHtml(label, fieldOptions || []);
    }
    var safeLabel = esc(label);
    var ph = esc(freeResponseFieldPlaceholder(
      fieldType,
      fieldType === 'number' ? formatHint : ''
    ));
    var insertBtns = '';
    if (fieldType === 'algebraic') {
      insertBtns = (
        '<button type="button" class="btn btn-secondary free-response-surd-btn" aria-label="Insert square root symbol">√</button>' +
        '<button type="button" class="btn btn-secondary free-response-pi-btn" aria-label="Insert pi symbol">π</button>' +
        '<button type="button" class="btn btn-secondary free-response-square-btn" aria-label="Insert squared symbol">x²</button>'
      );
    }
    var textWide = fieldType === 'text' || fieldType === 'keyword' || fieldType === 'sql';
    var rowClass = 'free-response-field-row' + (textWide ? ' free-response-field-row--text' : '') + (fieldType === 'sql' ? ' free-response-field-row--sql' : '');
    var fieldClass = 'free-response-field' + (textWide ? ' free-response-field--text' : '') + (fieldType === 'sql' ? ' free-response-field--sql' : '');
    var inputClass = 'free-response-input free-response-input-field' + (textWide ? ' free-response-input--text' : '') + (fieldType === 'sql' ? ' free-response-input--sql' : '');
    var inputHtml;
    if (fieldType === 'sql') {
      inputHtml = (
        '<textarea class="' + inputClass + '" rows="2" placeholder="' + ph + '" autocomplete="off" spellcheck="false" aria-label="' + safeLabel + '"></textarea>'
      );
    } else {
      inputHtml = (
        '<input type="text" class="' + inputClass + '" placeholder="' + ph + '" autocomplete="off" inputmode="text" aria-label="' + safeLabel + '">'
      );
    }
    return (
      '<div class="' + rowClass + '">' +
      '<label class="' + fieldClass + '">' +
      '<span class="free-response-field-label">' + safeLabel + '</span>' +
      inputHtml +
      '</label>' +
      insertBtns +
      '<button type="button" class="btn free-response-check-btn free-response-field-check-btn">Check</button>' +
      '<p class="free-response-field-feedback" aria-live="polite"></p>' +
      '</div>'
    );
  }

  function numberFieldsStackHtml(block, labels, fieldTypes, fieldOptions, formatHint) {
    var esc = htmlEscape;
    var rowSizes = [];
    var groupLabels = [];
    try {
      rowSizes = JSON.parse(block.getAttribute('data-field-row-sizes') || '[]');
    } catch (errRowSizes) {
      rowSizes = [];
    }
    try {
      groupLabels = JSON.parse(block.getAttribute('data-field-group-labels') || '[]');
    } catch (errGroupLabels) {
      groupLabels = [];
    }
    var stackClass = 'free-response-fields-stack';
    if (rowSizes.length) {
      stackClass += ' free-response-fields-stack--grouped';
    }
    var html = '';
    if (rowSizes.length) {
      var idx = 0;
      rowSizes.forEach(function (size, groupIndex) {
        html += '<div class="free-response-field-group">';
        if (groupLabels[groupIndex]) {
          html += '<span class="free-response-field-group-label">' + esc(groupLabels[groupIndex]) + '</span>';
        }
        html += '<div class="free-response-field-group-fields">';
        for (var j = 0; j < size; j += 1) {
          var label = labels[idx] || ('Field ' + (idx + 1));
          var fieldType = fieldTypes[idx] || 'number';
          html += numberFieldRowHtml(label, fieldType, fieldOptions[idx] || [], formatHint);
          idx += 1;
        }
        html += '</div></div>';
      });
    } else {
      html = labels.map(function (label, index) {
        var fieldType = fieldTypes[index] || 'number';
        return numberFieldRowHtml(label, fieldType, fieldOptions[index] || [], formatHint);
      }).join('');
    }
    return '<div class="' + stackClass + '">' + html + '</div>';
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
      var fieldOptions = [];
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
      try {
        fieldOptions = JSON.parse(block.getAttribute('data-field-options') || '[]');
      } catch (err3) {
        fieldOptions = [];
      }
      return (
        '<div class="free-response-row free-response-row--number-fields">' +
        numberFieldsStackHtml(block, labels, fieldTypes, fieldOptions, formatHint) +
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
        '<button type="button" class="btn btn-secondary free-response-pi-btn" aria-label="Insert pi symbol">π</button>' +
        '<button type="button" class="btn btn-secondary free-response-square-btn" aria-label="Insert squared symbol">x²</button>' +
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
      var rootCount = quadraticRootsFieldCount(block);
      if (rootCount >= 2) {
        var pairClass = rootCount === 2
          ? ' free-response-row--quadratic-roots-pair'
          : ' free-response-row--quadratic-roots-multi';
        var insertBtns = (
          '<button type="button" class="btn btn-secondary free-response-roots-insert-btn" data-insert="±" aria-label="Insert plus-minus symbol">±</button>' +
          '<button type="button" class="btn btn-secondary free-response-roots-insert-btn" data-insert="√" aria-label="Insert square root symbol">√</button>' +
          '<button type="button" class="btn free-response-check-btn">Check</button>'
        );
        if (rootCount === 2) {
          return (
            '<div class="free-response-row free-response-row--quadratic-roots' + pairClass + '">' +
            '<span class="free-response-root-prefix" aria-hidden="true"><strong>x</strong> =</span>' +
            '<input type="text" class="free-response-input free-response-input-quadratic-root" placeholder="e.g. -0.67" autocomplete="off" inputmode="text" aria-label="First root">' +
            '<span class="free-response-pair-sep" aria-hidden="true">or</span>' +
            '<span class="free-response-root-prefix" aria-hidden="true"><strong>x</strong> =</span>' +
            '<input type="text" class="free-response-input free-response-input-quadratic-root" placeholder="e.g. -2" autocomplete="off" inputmode="text" aria-label="Second root">' +
            insertBtns +
            '</div>'
          );
        }
        var rootRows = '';
        for (var ri = 0; ri < rootCount; ri += 1) {
          rootRows += (
            '<label class="free-response-field">' +
            '<span class="free-response-field-label"><strong>x</strong> =</span>' +
            '<input type="text" class="free-response-input free-response-input-quadratic-root" placeholder="root ' + (ri + 1) + '" autocomplete="off" inputmode="text" aria-label="Root ' + (ri + 1) + '">' +
            '</label>'
          );
        }
        return (
          '<div class="free-response-row free-response-row--quadratic-roots' + pairClass + '">' +
          '<div class="free-response-roots-stack">' + rootRows + '</div>' +
          insertBtns +
          '</div>'
        );
      }
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
    if (answerType === 'sql') {
      var sqlPh = esc(freeResponsePlaceholder('sql', formatHint));
      var sqlLines = sqlInputLines(block, 2);
      var sqlRows = sqlLines <= 1 ? 1 : 2;
      return (
        '<div class="free-response-row free-response-row--number free-response-row--text free-response-row--sql">' +
        '<textarea class="free-response-input free-response-input--sql" rows="' + sqlRows + '" placeholder="' + sqlPh + '" autocomplete="off" spellcheck="false" aria-label="Your SQL query"></textarea>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'python_run') {
      var pyPh = esc(formatHint || 'Write your Python code');
      var pyLines = sqlInputLines(block, 4);
      var pyRows = pyLines <= 1 ? 2 : Math.min(pyLines, 8);
      var pyStarter = esc(block.getAttribute('data-python-starter') || '');
      return (
        '<div class="free-response-row free-response-row--number free-response-row--text free-response-row--python-run">' +
        '<p class="python-desktop-hint" role="note">Works best on a computer — the code editor is cramped on a phone.</p>' +
        '<textarea class="free-response-input free-response-input--python free-response-input--sql" rows="' + pyRows + '" placeholder="' + pyPh + '" autocomplete="off" spellcheck="false" aria-label="Your Python code">' + pyStarter + '</textarea>' +
        '<button type="button" class="btn free-response-check-btn">Check</button>' +
        '</div>'
      );
    }
    if (answerType === 'proof_steps') {
      var stepBank = [];
      try {
        stepBank = JSON.parse(block.getAttribute('data-step-bank') || '[]');
      } catch (errBank) {
        stepBank = [];
      }
      var orderMatters = (block.getAttribute('data-order-matters') || '1') === '1';
      var pickCount = proofStepsPickCount(block.getAttribute('data-correct-raw') || '', block, null);
      if (pickCount) orderMatters = false;
      var proofHint = esc(formatHint || (
        orderMatters
          ? 'Select the correct proof steps in order'
          : (pickCount
            ? ('Select ' + pickCount + ' correct options')
            : 'Select all correct statements')
      ));
      var bankHtml = stepBank.map(function (step) {
        return (
          '<button type="button" class="btn btn-secondary free-response-proof-step" data-step-id="' +
          esc(step.id || '') +
          '">' +
          String(step.text || '') +
          '</button>'
        );
      }).join('');
      return (
        '<div class="free-response-row free-response-row--proof-steps" data-order-matters="' +
        (orderMatters ? '1' : '0') +
        '"' +
        (pickCount ? (' data-pick-count="' + pickCount + '"') : '') +
        '>' +
        '<p class="free-response-proof-hint">' + proofHint + '</p>' +
        '<div class="free-response-proof-bank" aria-label="Proof step bank">' + bankHtml + '</div>' +
        '<div class="free-response-proof-selected-wrap">' +
        '<p class="free-response-proof-selected-label">Your proof</p>' +
        '<ol class="free-response-proof-selected" aria-live="polite"></ol>' +
        '<button type="button" class="btn btn-secondary free-response-proof-clear">Clear</button>' +
        '</div>' +
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
    var input = block.querySelector('.free-response-input-surd')
      || block.querySelector('.free-response-input-algebraic')
      || block.querySelector('.free-response-input-alg-frac-num');
    if (!input) return;

    var surdBtn = block.querySelector('.free-response-surd-btn');
    if (surdBtn && surdBtn.dataset.surdInit !== '1') {
      surdBtn.dataset.surdInit = '1';
      surdBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, '√');
      });
    }

    var piBtn = block.querySelector('.free-response-pi-btn');
    if (piBtn && piBtn.dataset.piInit !== '1') {
      piBtn.dataset.piInit = '1';
      piBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, 'π');
      });
    }

    var squareBtn = block.querySelector('.free-response-square-btn');
    if (squareBtn && squareBtn.dataset.squareInit !== '1') {
      squareBtn.dataset.squareInit = '1';
      squareBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, '^2');
      });
    }
  }

  function wireQuadraticRootsInsertButtons(block) {
    var inputs = Array.prototype.slice.call(
      block.querySelectorAll('.free-response-input-quadratic-root, .free-response-input-quadratic-roots')
    );
    if (!inputs.length) return;
    var lastFocused = inputs[0];
    inputs.forEach(function (input) {
      input.addEventListener('focus', function () {
        lastFocused = input;
      });
    });
    block.querySelectorAll('.free-response-roots-insert-btn').forEach(function (btn) {
      if (btn.dataset.rootsInsertInit === '1') return;
      btn.dataset.rootsInsertInit = '1';
      btn.addEventListener('click', function () {
        var target = lastFocused;
        if (!target || target.disabled) {
          target = inputs.find(function (input) { return !input.disabled; }) || null;
        }
        if (!target || target.disabled) return;
        insertAtCursor(target, btn.getAttribute('data-insert') || '');
      });
    });
  }

  function ensureFreeResponseRow(block, answerType) {
    if (answerType === 'number_fields' && block.getAttribute('data-inline-sections') === '1') {
      return;
    }
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
      : (answerType === 'sql') ? 'sql'
      : (answerType === 'python_run') ? 'python_run'
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
    if (answerType === 'python_run') {
      var starter = block.getAttribute('data-python-starter') || '';
      var pyInput = block.querySelector('.free-response-input--python');
      if (pyInput && starter && !pyInput.value) {
        pyInput.value = starter;
      }
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
    block.querySelectorAll('.free-response-field-mcq .mcq-btn').forEach(function (btn) {
      btn.disabled = false;
      btn.classList.remove('is-correct', 'is-wrong', 'is-selected');
    });
    block.querySelectorAll('.free-response-field-row').forEach(function (row) {
      delete row.dataset.fieldCorrect;
    });
    var feedback = block.querySelector('.free-response-feedback');
    if (feedback) {
      feedback.textContent = '';
      feedback.style.color = '';
    }
    removeWrongAnswerReflection(block);
    delete block.dataset.reflectionOffered;
    removeCohortHint(block);
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

  function wireFieldInsertButtons(row, input) {
    if (!row || !input) return;
    var surdBtn = row.querySelector('.free-response-surd-btn');
    if (surdBtn && surdBtn.dataset.surdInit !== '1') {
      surdBtn.dataset.surdInit = '1';
      surdBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, '√');
      });
    }
    var piBtn = row.querySelector('.free-response-pi-btn');
    if (piBtn && piBtn.dataset.piInit !== '1') {
      piBtn.dataset.piInit = '1';
      piBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, 'π');
      });
    }
    var squareBtn = row.querySelector('.free-response-square-btn');
    if (squareBtn && squareBtn.dataset.squareInit !== '1') {
      squareBtn.dataset.squareInit = '1';
      squareBtn.addEventListener('click', function () {
        if (input.disabled) return;
        insertAtCursor(input, '^2');
      });
    }
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
      if (!fieldRows.length) return false;
      return Array.prototype.every.call(fieldRows, function (row) {
        if (row.dataset.fieldCorrect === '1') return true;
        var input = row.querySelector('.free-response-input-field');
        return input && input.disabled && input.classList.contains('is-correct');
      });
    }

    function maybePersistAllFields() {
      if (!allFieldsCorrect()) return;
      if (blockFeedback) {
        blockFeedback.textContent = '\u2713 All parts correct!';
        blockFeedback.style.color = '#16a34a';
      }
    }

    function submitNumberFieldAnswer(index, row, fieldType, userValue, onDone) {
      var fieldCorrect = correctParts[index] || '';
      var fieldFeedback = row.querySelector('.free-response-field-feedback');
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

      return fetch('/api/v1/problems/check', {
        method: 'POST',
        headers: apiHeaders({
          'Content-Type': 'application/json',
        }),
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
          if (typeof onDone === 'function') {
            onDone(data, userValue, fieldFeedback);
          }
          showCohortHint(block, data.cohort);
          return data;
        });
    }

    fieldRows.forEach(function (row, index) {
      var fieldType = fieldTypes[index] || 'number';
      var fieldFeedback = row.querySelector('.free-response-field-feedback');

      if (fieldType === 'order') {
        var stepCount = proofStepsOrderCount(correctParts[index] || '');
        var selected = [];
        var bank = row.querySelector('.free-response-proof-bank');
        var list = row.querySelector('.free-response-proof-selected');
        var clearBtn = row.querySelector('.free-response-proof-clear');
        var checkBtn = row.querySelector('.free-response-field-check-btn');

        function orderStepButton(id) {
          if (!bank) return null;
          return bank.querySelector('.free-response-proof-step[data-step-id="' + id + '"]');
        }

        function renderOrderSelected() {
          if (!list) return;
          list.innerHTML = '';
          selected.forEach(function (id, selIndex) {
            var btn = orderStepButton(id);
            var text = btn ? btn.innerHTML : id;
            var li = document.createElement('li');
            li.innerHTML = text + ' ';
            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'btn btn-secondary free-response-proof-remove';
            remove.textContent = 'Remove';
            remove.addEventListener('click', function () {
              selected.splice(selIndex, 1);
              clearProofStepFeedback(row);
              if (fieldFeedback) {
                fieldFeedback.textContent = '';
                fieldFeedback.style.color = '';
              }
              syncOrderBankState();
              renderOrderSelected();
            });
            li.appendChild(remove);
            list.appendChild(li);
          });
        }

        function syncOrderBankState() {
          if (!bank) return;
          bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
            var id = btn.getAttribute('data-step-id') || '';
            var used = selected.indexOf(id) >= 0;
            btn.classList.toggle('is-used', used);
            btn.disabled = used;
            btn.classList.remove('is-selected-toggle');
          });
        }

        if (bank) {
          bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
            btn.addEventListener('click', function () {
              if (row.dataset.fieldCorrect === '1') return;
              var id = btn.getAttribute('data-step-id') || '';
              if (!id || selected.indexOf(id) >= 0) return;
              if (stepCount && selected.length >= stepCount) return;
              clearProofStepFeedback(row);
              if (fieldFeedback) {
                fieldFeedback.textContent = '';
                fieldFeedback.style.color = '';
              }
              selected.push(id);
              syncOrderBankState();
              renderOrderSelected();
            });
          });
        }

        if (clearBtn) {
          clearBtn.addEventListener('click', function () {
            if (row.dataset.fieldCorrect === '1') return;
            selected = [];
            clearProofStepFeedback(row);
            syncOrderBankState();
            renderOrderSelected();
            if (fieldFeedback) {
              fieldFeedback.textContent = '';
              fieldFeedback.style.color = '';
            }
          });
        }

        if (!checkBtn) return;
        checkBtn.addEventListener('click', function () {
          if (row.dataset.fieldCorrect === '1') return;
          if (!selected.length) {
            if (fieldFeedback) {
              fieldFeedback.textContent = 'Put the steps in the correct order.';
              fieldFeedback.style.color = '#dc2626';
            }
            return;
          }
          checkBtn.disabled = true;
          submitNumberFieldAnswer(index, row, 'proof_steps', selected.join('|'), function (data) {
            if (data.correct) {
              row.dataset.fieldCorrect = '1';
              handleProofStepsCheckResult(data, {
                feedbackEl: fieldFeedback,
                listEl: list,
                rowEl: row,
                checkBtn: checkBtn,
                bankEl: bank,
                clearBtn: clearBtn,
              });
              maybePersistAllFields();
            } else {
              handleProofStepsCheckResult(data, {
                feedbackEl: fieldFeedback,
                listEl: list,
                rowEl: row,
                checkBtn: checkBtn,
                bankEl: bank,
                clearBtn: clearBtn,
              });
            }
          }).catch(function (err) {
            checkBtn.disabled = false;
            if (fieldFeedback) {
              fieldFeedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
              fieldFeedback.style.color = '#dc2626';
            }
          });
        });
        return;
      }

      if (fieldType === 'pick') {
        var pickCount = parseInt(row.getAttribute('data-pick-count') || '0', 10);
        if (!pickCount) {
          pickCount = proofStepsPickCount(correctParts[index] || '', block, row);
        }
        var selected = [];
        var bank = row.querySelector('.free-response-proof-bank');
        var list = row.querySelector('.free-response-proof-selected');
        var clearBtn = row.querySelector('.free-response-proof-clear');
        var checkBtn = row.querySelector('.free-response-field-check-btn');

        function pickStepButton(id) {
          if (!bank) return null;
          return bank.querySelector('.free-response-proof-step[data-step-id="' + id + '"]');
        }

        function renderPickSelected() {
          if (!list) return;
          list.innerHTML = '';
          selected.forEach(function (id, selIndex) {
            var btn = pickStepButton(id);
            var text = btn ? btn.innerHTML : id;
            var li = document.createElement('li');
            li.innerHTML = text + ' ';
            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'btn btn-secondary free-response-proof-remove';
            remove.textContent = 'Remove';
            remove.addEventListener('click', function () {
              selected.splice(selIndex, 1);
              clearProofStepFeedback(row);
              if (fieldFeedback) {
                fieldFeedback.textContent = '';
                fieldFeedback.style.color = '';
              }
              syncPickBankState();
              renderPickSelected();
            });
            li.appendChild(remove);
            list.appendChild(li);
          });
        }

        function syncPickBankState() {
          if (!bank) return;
          bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
            var id = btn.getAttribute('data-step-id') || '';
            var used = selected.indexOf(id) >= 0;
            btn.classList.toggle('is-selected-toggle', used);
          });
        }

        if (bank) {
          bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
            btn.addEventListener('click', function () {
              if (row.dataset.fieldCorrect === '1') return;
              var id = btn.getAttribute('data-step-id') || '';
              if (!id) return;
              clearProofStepFeedback(row);
              if (fieldFeedback) {
                fieldFeedback.textContent = '';
                fieldFeedback.style.color = '';
              }
              var idx = selected.indexOf(id);
              if (idx >= 0) {
                selected.splice(idx, 1);
              } else if (!pickCount || selected.length < pickCount) {
                selected.push(id);
              }
              syncPickBankState();
              renderPickSelected();
            });
          });
        }

        if (clearBtn) {
          clearBtn.addEventListener('click', function () {
            if (row.dataset.fieldCorrect === '1') return;
            selected = [];
            clearProofStepFeedback(row);
            syncPickBankState();
            renderPickSelected();
            if (fieldFeedback) {
              fieldFeedback.textContent = '';
              fieldFeedback.style.color = '';
            }
          });
        }

        if (!checkBtn) return;
        checkBtn.addEventListener('click', function () {
          if (row.dataset.fieldCorrect === '1') return;
          if (!selected.length) {
            if (fieldFeedback) {
              fieldFeedback.textContent = pickCount
                ? ('Select ' + pickCount + ' correct options.')
                : 'Select your answer.';
              fieldFeedback.style.color = '#dc2626';
            }
            return;
          }
          checkBtn.disabled = true;
          submitNumberFieldAnswer(index, row, 'proof_steps', selected.join('|'), function (data) {
            if (data.correct) {
              row.dataset.fieldCorrect = '1';
              handleProofStepsCheckResult(data, {
                feedbackEl: fieldFeedback,
                listEl: list,
                rowEl: row,
                checkBtn: checkBtn,
                bankEl: bank,
                clearBtn: clearBtn,
              });
              maybePersistAllFields();
            } else {
              handleProofStepsCheckResult(data, {
                feedbackEl: fieldFeedback,
                listEl: list,
                rowEl: row,
                checkBtn: checkBtn,
                bankEl: bank,
                clearBtn: clearBtn,
              });
            }
          }).catch(function (err) {
            checkBtn.disabled = false;
            if (fieldFeedback) {
              fieldFeedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
              fieldFeedback.style.color = '#dc2626';
            }
          });
        });
        return;
      }

      if (fieldType === 'mcq') {
        var mcqWrap = row.querySelector('.free-response-field-mcq');
        if (!mcqWrap) return;
        var correctLetter = (correctParts[index] || '').trim().charAt(0).toUpperCase();
        mcqWrap.querySelectorAll('.mcq-btn').forEach(function (btn) {
          btn.addEventListener('click', function () {
            if (row.dataset.fieldCorrect === '1') return;
            var letter = (btn.dataset.letter || '').trim().charAt(0).toUpperCase();
            mcqWrap.querySelectorAll('.mcq-btn').forEach(function (b) {
              b.disabled = true;
              b.classList.toggle('is-selected', b === btn);
            });
            submitNumberFieldAnswer(index, row, 'mcq', letter, function (data) {
              btn.classList.remove('is-correct', 'is-wrong');
              mcqWrap.querySelectorAll('.mcq-btn').forEach(function (b) {
                b.classList.remove('is-correct', 'is-wrong');
              });
              if (data.correct) {
                btn.classList.add('is-correct');
                row.dataset.fieldCorrect = '1';
                if (fieldFeedback) {
                  fieldFeedback.textContent = '\u2713 Correct!';
                  fieldFeedback.style.color = '#16a34a';
                }
                celebrateResult(true, btn);
                maybePersistAllFields();
              } else {
                btn.classList.add('is-wrong');
                var fieldCorrectBtn = null;
                mcqWrap.querySelectorAll('.mcq-btn').forEach(function (b) {
                  var bLetter = (b.dataset.letter || '').trim().charAt(0).toUpperCase();
                  if (bLetter === correctLetter) {
                    b.classList.add('is-correct');
                    fieldCorrectBtn = b;
                  }
                });
                celebrateResult(false, btn, fieldCorrectBtn);
                mcqWrap.querySelectorAll('.mcq-btn').forEach(function (b) { b.disabled = false; });
                if (fieldFeedback) {
                  fieldFeedback.textContent = '\u2717 Not quite \u2014 the correct answer is highlighted.';
                  fieldFeedback.style.color = '#dc2626';
                }
              }
            }).catch(function (err) {
              mcqWrap.querySelectorAll('.mcq-btn').forEach(function (b) { b.disabled = false; });
              if (fieldFeedback) {
                fieldFeedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
                fieldFeedback.style.color = '#dc2626';
              }
            });
          });
        });
        return;
      }

      var input = row.querySelector('.free-response-input-field');
      var checkBtn = row.querySelector('.free-response-field-check-btn');
      if (!input || !checkBtn) return;

      wireFieldInsertButtons(row, input);

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

        checkBtn.disabled = true;
        input.disabled = true;

        submitNumberFieldAnswer(index, row, fieldType, userValue, function (data, userValue) {
          input.classList.remove('is-correct', 'is-wrong', 'is-partial');
          if (data.correct) {
            input.classList.add('is-correct');
            input.disabled = true;
            checkBtn.disabled = true;
            if (fieldFeedback) {
              fieldFeedback.textContent = '\u2713 ' + freeResponseCorrectFeedback(data, userValue);
              fieldFeedback.style.color = '#16a34a';
            }
            celebrateResult(true, checkBtn || row);
            maybePersistAllFields();
          } else if (isTextPartialScore(data)) {
            input.classList.add('is-partial');
            input.disabled = false;
            checkBtn.disabled = false;
            if (fieldFeedback) {
              fieldFeedback.textContent = '\u25D0 ' + freeResponseWrongFeedback(block, data);
              fieldFeedback.style.color = '#d97706';
            }
          } else {
            input.classList.add('is-wrong');
            input.disabled = false;
            checkBtn.disabled = false;
            if (fieldFeedback) {
              fieldFeedback.textContent = '\u2717 ' + freeResponseWrongFeedback(block, data);
              fieldFeedback.style.color = '#dc2626';
            }
          }
        }).catch(function (err) {
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
        if (event.key === 'Enter' && input.tagName !== 'TEXTAREA') {
          event.preventDefault();
          submitField();
        }
      });
    });
  }

  function proofStepsOrderCount(correctRaw) {
    var raw = String(correctRaw || '').trim();
    if (raw.indexOf('1|') === 0) {
      return Math.max(0, raw.split('|').length - 1);
    }
    return 0;
  }

  function proofStepStatusLabel(status) {
    if (status === 'correct') return '\u2713 Correct';
    if (status === 'wrong_order') return '\u21C4 Wrong order';
    if (status === 'wrong') return '\u2717 Not a proof step';
    return '';
  }

  function clearProofStepFeedback(container) {
    if (!container) return;
    container.querySelectorAll('.free-response-proof-selected li').forEach(function (li) {
      li.classList.remove('proof-step-status--correct', 'proof-step-status--wrong', 'proof-step-status--wrong-order');
      var badge = li.querySelector('.free-response-proof-status');
      if (badge) badge.remove();
    });
  }

  function applyProofStepFeedback(list, stepFeedback) {
    if (!list || !stepFeedback || !stepFeedback.length) return;
    var items = list.querySelectorAll('li');
    stepFeedback.forEach(function (item, index) {
      var li = items[index];
      if (!li) return;
      li.classList.remove('proof-step-status--correct', 'proof-step-status--wrong', 'proof-step-status--wrong-order');
      var status = item.status || 'wrong';
      if (status === 'correct') {
        li.classList.add('proof-step-status--correct');
      } else if (status === 'wrong_order') {
        li.classList.add('proof-step-status--wrong-order');
      } else {
        li.classList.add('proof-step-status--wrong');
      }
      var badge = li.querySelector('.free-response-proof-status');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'free-response-proof-status';
        var removeBtn = li.querySelector('.free-response-proof-remove');
        if (removeBtn) {
          li.insertBefore(badge, removeBtn);
        } else {
          li.appendChild(badge);
        }
      }
      badge.textContent = proofStepStatusLabel(status);
      badge.title = item.hint || '';
    });
  }

  function handleProofStepsCheckResult(data, context) {
    var feedback = context.feedbackEl;
    var list = context.listEl;
    var row = context.rowEl;
    var checkBtn = context.checkBtn;
    var bank = context.bankEl;
    var clearBtn = context.clearBtn;
    var block = context.blockEl;

    if (data.score_total != null && data.score != null && block) {
      block.dataset.textScore = String(data.score);
      block.dataset.textScoreTotal = String(data.score_total);
    }

    if (data.correct) {
      if (feedback) {
        feedback.textContent = '\u2713 Correct!';
        feedback.style.color = '#16a34a';
      }
      if (row) row.classList.add('is-correct');
      celebrateResult(true, checkBtn || row);
      if (bank) {
        bank.querySelectorAll('.free-response-proof-step').forEach(function (b) {
          b.disabled = true;
        });
      }
      if (clearBtn) clearBtn.disabled = true;
    } else {
      if (feedback) {
        if (isTextPartialScore(data) && !data.step_feedback) {
          feedback.textContent = '\u25D0 ' + (context.partialFeedback || freeResponseWrongFeedback(block, data));
          feedback.style.color = '#d97706';
        } else {
          feedback.textContent = '\u2717 ' + (data.feedback || 'Not quite.');
          feedback.style.color = '#dc2626';
        }
      }
      applyProofStepFeedback(list, data.step_feedback);
      if (checkBtn) checkBtn.disabled = false;
    }
  }

  function proofStepsPickCount(correctRaw, block, row) {
    var pickAttr = '';
    if (row && row.getAttribute('data-pick-count')) {
      pickAttr = row.getAttribute('data-pick-count');
    } else if (block && block.getAttribute('data-pick-count')) {
      pickAttr = block.getAttribute('data-pick-count');
    }
    if (pickAttr) {
      var parsedAttr = parseInt(pickAttr, 10);
      if (!isNaN(parsedAttr) && parsedAttr > 0) return parsedAttr;
    }
    var raw = String(correctRaw || '').trim();
    if (raw.indexOf('pick|') === 0) {
      var parts = raw.split('|');
      var parsedRaw = parseInt(parts[1], 10);
      if (!isNaN(parsedRaw) && parsedRaw > 0) return parsedRaw;
    }
    return 0;
  }

  function wirePythonRunFreeResponse(block, correctRaw, trackable) {
    var textarea = block.querySelector('.free-response-input--python');
    var checkBtn = block.querySelector('.free-response-check-btn');
    var feedback = block.querySelector('.free-response-feedback');
    if (!textarea || !checkBtn) return;

    checkBtn.addEventListener('click', function () {
      if (textarea.disabled) return;
      var code = (textarea.value || '').trim();
      if (!code) {
        if (feedback) {
          feedback.textContent = 'Write your Python code first.';
          feedback.style.color = '#dc2626';
        }
        textarea.classList.remove('is-correct', 'is-wrong');
        return;
      }
      if (typeof globalThis.runPythonRunTests !== 'function') {
        if (feedback) {
          feedback.textContent = 'Python runner is still loading — try again in a moment.';
          feedback.style.color = '#dc2626';
        }
        return;
      }
      var tests = [];
      try {
        tests = JSON.parse(block.getAttribute('data-answer-tests') || '[]');
      } catch (parseErr) {
        tests = [];
      }
      if (!tests.length) {
        if (feedback) {
          feedback.textContent = 'This question has no test fixtures configured.';
          feedback.style.color = '#dc2626';
        }
        return;
      }

      checkBtn.disabled = true;
      textarea.disabled = true;
      if (feedback) {
        feedback.textContent = 'Running your code…';
        feedback.style.color = '';
      }

      globalThis.runPythonRunTests(code, tests).then(function (results) {
        var recordThisAttempt = trackable && block.dataset.freeResponsePersisted !== '1';
        var body = {
          user_answer: JSON.stringify(results),
          correct_answer_raw: correctRaw,
          answer_type: 'python_run',
        };
        if (trackable) {
          body.level = block.dataset.level;
          body.subject = block.dataset.subject;
          body.topic = block.dataset.topic;
          body.difficulty = block.dataset.difficulty || 'foundational';
          if (block.dataset.freeResponsePersisted === '1') {
            body.record_attempt = false;
          }
        }
        return fetch('/api/v1/problems/check', {
          method: 'POST',
          headers: apiHeaders({
            'Content-Type': 'application/json',
          }),
          credentials: 'same-origin',
          body: JSON.stringify(body),
        }).then(function (response) {
          var contentType = response.headers.get('content-type') || '';
          if (contentType.indexOf('application/json') === -1) {
            throw new Error('Server returned an unexpected response — try refreshing the page.');
          }
          return response.json().then(function (data) {
            if (!response.ok) {
              var err = new Error(data.error || 'Check failed');
              err.data = data;
              throw err;
            }
            return data;
          });
        }).then(function (data) {
          var ok = Boolean(data.correct);
          textarea.classList.remove('is-correct', 'is-wrong');
          if (ok) {
            textarea.classList.add('is-correct');
            textarea.disabled = true;
            checkBtn.disabled = true;
          } else {
            textarea.classList.add('is-wrong');
            textarea.disabled = false;
            checkBtn.disabled = false;
          }
          celebrateResult(ok, checkBtn || textarea);
          if (feedback) {
            feedback.textContent = data.feedback || (ok ? 'Correct!' : 'Not quite.');
            feedback.style.color = ok ? '#16a34a' : '#dc2626';
          }
          if (ok && trackable) {
            block.dataset.freeResponsePersisted = '1';
          } else if (!ok) {
            offerWrongAnswerReflection(block, 'check', data, recordThisAttempt);
            if (trackable && block.dataset.freeResponsePersisted !== '1') {
              block.dataset.freeResponsePersisted = '1';
            }
          }
          showCohortHint(block, data.cohort);
        });
      }).catch(function (err) {
        textarea.disabled = false;
        checkBtn.disabled = false;
        textarea.classList.remove('is-correct');
        textarea.classList.add('is-wrong');
        if (feedback) {
          feedback.textContent = (err && err.message) || 'Could not run your code — try again.';
          feedback.style.color = '#dc2626';
        }
      });
    });
  }

  function wireProofStepsFreeResponse(block, correctRaw, trackable) {
    var row = block.querySelector('.free-response-row--proof-steps');
    if (!row) return;
    var orderMatters = (row.getAttribute('data-order-matters')
      || block.getAttribute('data-order-matters')
      || '1') === '1';
    var pickCount = proofStepsPickCount(correctRaw, block, row);
    if (pickCount) orderMatters = false;
    var selected = [];
    var bank = row.querySelector('.free-response-proof-bank');
    var list = row.querySelector('.free-response-proof-selected');
    var clearBtn = row.querySelector('.free-response-proof-clear');
    var checkBtn = row.querySelector('.free-response-check-btn');
    var feedback = block.querySelector('.free-response-feedback');

    function stepButton(id) {
      if (!bank) return null;
      return bank.querySelector('.free-response-proof-step[data-step-id="' + id + '"]');
    }

    function renderSelected() {
      if (!list) return;
      list.innerHTML = '';
      selected.forEach(function (id, index) {
        var btn = stepButton(id);
        var text = btn ? btn.innerHTML : id;
        var li = document.createElement('li');
        li.innerHTML = text + ' ';
        var remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'btn btn-secondary free-response-proof-remove';
        remove.textContent = 'Remove';
        remove.addEventListener('click', function () {
          selected.splice(index, 1);
          clearProofStepFeedback(row);
          if (feedback) {
            feedback.textContent = '';
            feedback.style.color = '';
          }
          syncBankState();
          renderSelected();
        });
        li.appendChild(remove);
        list.appendChild(li);
      });
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([list]).catch(function () {});
      }
    }

    function syncBankState() {
      if (!bank) return;
      bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
        var id = btn.getAttribute('data-step-id') || '';
        var used = selected.indexOf(id) >= 0;
        if (orderMatters) {
          btn.classList.toggle('is-used', used);
          btn.disabled = used;
          btn.classList.remove('is-selected-toggle');
        } else {
          btn.classList.toggle('is-selected-toggle', used);
          btn.disabled = false;
          btn.classList.remove('is-used');
        }
      });
    }

    if (bank) {
      bank.querySelectorAll('.free-response-proof-step').forEach(function (btn) {
        btn.addEventListener('click', function () {
          if (checkBtn && checkBtn.disabled) return;
          var id = btn.getAttribute('data-step-id') || '';
          if (!id) return;
          clearProofStepFeedback(row);
          if (feedback) {
            feedback.textContent = '';
            feedback.style.color = '';
          }
          var idx = selected.indexOf(id);
          if (orderMatters) {
            if (idx >= 0) return;
            selected.push(id);
          } else if (idx >= 0) {
            selected.splice(idx, 1);
          } else {
            if (pickCount && selected.length >= pickCount) return;
            selected.push(id);
          }
          syncBankState();
          renderSelected();
        });
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (checkBtn && checkBtn.disabled) return;
        selected = [];
        clearProofStepFeedback(row);
        syncBankState();
        renderSelected();
        if (feedback) {
          feedback.textContent = '';
          feedback.style.color = '';
        }
      });
    }

    if (!checkBtn) return;
    checkBtn.addEventListener('click', function () {
      if (!selected.length) {
        if (feedback) {
          feedback.textContent = orderMatters
            ? 'Select the correct proof steps in order.'
            : (pickCount
              ? ('Select ' + pickCount + ' correct options.')
              : 'Select all correct statements.');
          feedback.style.color = '#dc2626';
        }
        return;
      }
      var recordThisAttempt = trackable && block.dataset.freeResponsePersisted !== '1';
      var body = {
        user_answer: selected.join('|'),
        correct_answer_raw: correctRaw,
        answer_type: 'proof_steps',
      };
      if (trackable) {
        body.level = block.dataset.level;
        body.subject = block.dataset.subject;
        body.topic = block.dataset.topic;
        body.difficulty = block.dataset.difficulty || 'foundational';
        if (block.dataset.freeResponsePersisted === '1') {
          body.record_attempt = false;
        }
      }
      checkBtn.disabled = true;
      fetch('/api/v1/problems/check', {
        method: 'POST',
        headers: apiHeaders({
          'Content-Type': 'application/json',
        }),
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
          handleProofStepsCheckResult(data, {
            feedbackEl: feedback,
            listEl: list,
            rowEl: row,
            checkBtn: checkBtn,
            bankEl: bank,
            clearBtn: clearBtn,
            blockEl: block,
          });
          offerWrongAnswerReflection(block, 'check', data, recordThisAttempt);
          if (trackable && block.dataset.freeResponsePersisted !== '1') {
            block.dataset.freeResponsePersisted = '1';
          }
          showCohortHint(block, data.cohort);
        })
        .catch(function (err) {
          checkBtn.disabled = false;
          if (feedback) {
            feedback.textContent = (err.data && err.data.error) || err.message || 'Could not check answer.';
            feedback.style.color = '#dc2626';
          }
        });
    });

    syncBankState();
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
    if (answerType === 'proof_steps') {
      wireProofStepsFreeResponse(block, correctRaw, trackable);
      return;
    }
    if (answerType === 'python_run') {
      wirePythonRunFreeResponse(block, correctRaw, trackable);
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
      if (answerType === 'quadratic_roots') {
        var rootInputs = Array.prototype.slice.call(
          block.querySelectorAll('.free-response-input-quadratic-root')
        );
        if (rootInputs.length >= 2) {
          return { fields: rootInputs, all: rootInputs };
        }
        var singleRoot = block.querySelector('.free-response-input-quadratic-roots')
          || block.querySelector('.free-response-row--quadratic-roots .free-response-input');
        return { single: singleRoot, all: singleRoot ? [singleRoot] : [] };
      }
      var single = block.querySelector('.free-response-row--number .free-response-input')
        || block.querySelector('.free-response-row--fraction .free-response-input')
        || block.querySelector('.free-response-row--linear .free-response-input')
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
      if (answerType === 'quadratic_roots') {
        return readQuadraticRootsUserAnswer(block);
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
      if (answerType === 'quadratic_roots' && inputs.fields && inputs.fields.length >= 2) {
        return inputs.fields.some(function (input) {
          return !(input.value || '').trim();
        });
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
      if (answerType === 'quadratic_roots') return 'Enter a value in every root field.';
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
        input.classList.remove('is-correct', 'is-wrong', 'is-partial');
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
        btn.classList.remove('is-correct', 'is-wrong', 'is-partial');
        if (correct) {
          btn.classList.add('is-correct');
        }
      });
    }

    function setInputStatePartial() {
      var inputs = activeInputs();
      inputs.all.forEach(function (input) {
        input.classList.remove('is-correct', 'is-wrong');
        input.classList.add('is-partial');
        input.disabled = false;
      });
      block.querySelectorAll('.free-response-check-btn').forEach(function (btn) {
        btn.disabled = false;
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

      var recordThisAttempt = trackable && block.dataset.freeResponsePersisted !== '1';

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
        if (block.dataset.freeResponsePersisted === '1') {
          body.record_attempt = false;
        }
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
        headers: apiHeaders({
          'Content-Type': 'application/json',
        }),
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
          if (data.score_total != null && data.score != null) {
            block.dataset.textScore = String(data.score);
            block.dataset.textScoreTotal = String(data.score_total);
          }
          if (data.correct) {
            setInputState(true);
            if (feedback) {
              feedback.textContent = '\u2713 ' + freeResponseCorrectFeedback(data, userAnswer);
              feedback.style.color = '#16a34a';
            }
            celebrateResult(true, checkBtn || block);
          } else if (isTextPartialScore(data)) {
            setInputStatePartial();
            if (feedback) {
              feedback.textContent = '\u25D0 ' + freeResponseWrongFeedback(block, data);
              feedback.style.color = '#d97706';
            }
          } else {
            setInputState(false);
            if (answerType === 'number_line') {
              var nlWrong = block.querySelector('.free-response-number-line');
              if (nlWrong) nlWrong.classList.remove('is-disabled');
            }
            if (feedback) {
              feedback.textContent = '\u2717 ' + freeResponseWrongFeedback(block, data);
              feedback.style.color = '#dc2626';
            }
            celebrateResult(false, checkBtn || block);
            offerWrongAnswerReflection(block, 'check', data, recordThisAttempt);
          }
          showCohortHint(block, data.cohort);
          if (trackable && block.dataset.freeResponsePersisted !== '1') {
            block.dataset.freeResponsePersisted = '1';
          }
          dispatchQuicktestChecked(freeResponseCheckState(block));
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
          if (document.getElementById('quicktest-quiz-runner')) {
            document.dispatchEvent(new CustomEvent('pb-quicktest-check-failed', { bubbles: true }));
          }
        });
    }

    checkBtn.addEventListener('click', submitAnswer);
    if (answerType !== 'number_line') {
      activeInputs().all.forEach(function (input) {
        input.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' && input.tagName !== 'TEXTAREA') {
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

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderAnswerGradingHintHtml(problem) {
    var keywords = problem.answer_text_keywords;
    var fieldHints = problem.answer_field_hints;
    if ((!keywords || !keywords.length) && (!fieldHints || !fieldHints.length)) {
      return '';
    }
    var required = problem.answer_text_required;
    var title = 'To get this marked correct, mention:';
    if (keywords && keywords.length && required && keywords.length > required) {
      title = 'To get full marks, mention any ' + required + ' of:';
    } else if (keywords && keywords.length) {
      title = 'To get this marked correct, mention:';
    } else {
      title = 'Key ideas we look for:';
    }
    var chips = (keywords && keywords.length ? keywords : fieldHints).map(function (item) {
      return '<span class="answer-keyword-chip">' + escapeHtml(String(item)) + '</span>';
    }).join(keywords && keywords.length ? ', ' : '; ');
    return (
      '<p class="answer-grading-hint"><strong>' + title + '</strong> ' + chips + '</p>'
    );
  }

  function applySavedProblemPayload(problem) {
    var question = document.getElementById('saved-question-content');
    if (question) question.innerHTML = problem.question_html || '';

    var answer = document.getElementById('saved-answer-content');
    if (answer) answer.innerHTML = problem.solution_html || '';

    var gradingHint = document.getElementById('saved-answer-grading-hint');
    if (gradingHint) {
      gradingHint.innerHTML = renderAnswerGradingHintHtml(problem);
    }

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

    var first = document.querySelector('.prob-tree-input');
    if (first) {
      var host = first.closest('svg') || first;
      var wrap = host.parentElement;
      if (wrap && !wrap.querySelector('.prob-tree-mobile-hint')) {
        var hint = document.createElement('p');
        hint.className = 'prob-tree-mobile-hint';
        hint.setAttribute('role', 'note');
        hint.textContent = 'On a phone, scroll the tree sideways to fill each box.';
        wrap.appendChild(hint);
      }
    }

    // Diagram foreignObjects are ~22px tall; enlarge on phones so 16px text fits.
    if (window.matchMedia && window.matchMedia('(max-width: 640px)').matches) {
      document.querySelectorAll('svg foreignObject').forEach(function (fo) {
        var input = fo.querySelector('.prob-tree-input');
        if (!input) return;
        var w = parseFloat(fo.getAttribute('width')) || 0;
        var h = parseFloat(fo.getAttribute('height')) || 0;
        var x = parseFloat(fo.getAttribute('x')) || 0;
        var y = parseFloat(fo.getAttribute('y')) || 0;
        var nextW = Math.max(w, 56);
        var nextH = Math.max(h, 36);
        if (nextW === w && nextH === h) return;
        fo.setAttribute('width', String(nextW));
        fo.setAttribute('height', String(nextH));
        fo.setAttribute('y', String(y - (nextH - h) / 2));
        if (input.getAttribute('aria-label') !== 'outcome probability') {
          fo.setAttribute('x', String(x - (nextW - w) / 2));
        }
      });
    }
  }

  function initRevisionQueue() {
    var panel = document.querySelector('[data-revision-queue]');
    if (!panel) return;

    panel.addEventListener('click', function (e) {
      var btn = e.target.closest('.revision-queue-action');
      if (!btn || !panel.contains(btn)) return;
      e.preventDefault();
      if (btn.disabled) return;
      var item = btn.closest('.revision-queue-item');
      if (!item) return;
      var action = btn.getAttribute('data-action');
      var endpoint = action === 'complete'
        ? '/api/v1/me/revision-queue/complete'
        : '/api/v1/me/revision-queue/dismiss';

      btn.disabled = true;
      fetch(endpoint, {
        method: 'POST',
        headers: apiHeaders({ 'Content-Type': 'application/json' }),
        credentials: 'same-origin',
        body: JSON.stringify({
          level: item.dataset.level,
          subject: item.dataset.subject,
          topic: item.dataset.topic,
        }),
      })
        .then(function (r) { return r.json().catch(function () { return {}; }); })
        .then(function (data) {
          if (data && data.ok) {
            item.remove();
            showAppToast(
              action === 'complete' ? 'Nice work — see you next time.' : 'Snoozed for a few days.',
              'success'
            );
            if (!panel.querySelector('.revision-queue-item')) {
              panel.remove();
            }
          } else {
            btn.disabled = false;
            showAppToast('Something went wrong — try again.', 'error');
          }
        })
        .catch(function () {
          btn.disabled = false;
          showAppToast('Something went wrong — try again.', 'error');
        });
    });
  }

  function initAnswerRevealMathJax() {
    document.querySelectorAll('details.answer-reveal, details.practice-hint-drawer').forEach(function (details) {
      details.addEventListener('toggle', function () {
        if (!details.open || !window.MathJax || !MathJax.typesetPromise) return;
        var targets = [details.querySelector('.answer'), details.querySelector('.hint')];
        MathJax.typesetPromise(targets.filter(Boolean)).catch(function () {});
      });
    });
  }

  function initKeyboardInset() {
    var root = document.documentElement;

    function keyboardInset() {
      var vv = window.visualViewport;
      if (!vv) return 0;
      var layoutH = Math.max(window.innerHeight, document.documentElement.clientHeight);
      return Math.max(0, Math.round(layoutH - vv.height - vv.offsetTop));
    }

    function revealPrimaryAction() {
      var active = document.activeElement;
      if (!active || !active.closest) return;
      var row = active.closest(
        '.free-response-row, .free-response-field-row, .free-response-field-group, .lesson-assist-followup'
      );
      if (!row) return;
      var target = row.querySelector(
        '.free-response-check-btn, .free-response-field-check-btn, .lesson-assist-send'
      ) || row;
      var vv = window.visualViewport;
      var rect = target.getBoundingClientRect();
      var viewBottom = vv ? vv.offsetTop + vv.height : window.innerHeight;
      var viewTop = vv ? vv.offsetTop : 0;
      if (rect.bottom > viewBottom - 12) {
        window.scrollBy(0, rect.bottom - viewBottom + 16);
      } else if (rect.top < viewTop + 12) {
        window.scrollBy(0, rect.top - viewTop - 16);
      }
    }

    function update(opts) {
      var inset = keyboardInset();
      root.style.setProperty('--kb-inset', inset + 'px');
      document.body.classList.toggle('kb-open', inset > 40);
      if (inset > 40 && opts && opts.reveal) {
        window.setTimeout(revealPrimaryAction, 50);
      }
    }

    update();
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', function () { update({ reveal: true }); });
    } else {
      window.addEventListener('resize', function () { update({ reveal: true }); });
    }
    document.addEventListener('focusin', function () {
      window.setTimeout(function () { update({ reveal: true }); }, 80);
    });
    document.addEventListener('focusout', function () {
      window.setTimeout(function () { update(); }, 80);
    });
  }

  window.showAppToast = showAppToast;
  window.pbQuicktest = {
    collectState: collectQuickTestAnswerState,
    syncFormFields: syncQuickTestFormFields,
  };

  var _EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var _HANDLE_RE = /^[a-z0-9_]{3,20}$/;

  function passwordStrengthScore(value) {
    var score = 0;
    if (!value) return 0;
    if (value.length >= 8) score += 1;
    if (value.length >= 12) score += 1;
    if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
    if (/\d/.test(value)) score += 1;
    if (/[^A-Za-z0-9]/.test(value)) score += 1;
    if (score <= 1) return 1;
    if (score === 2) return 2;
    if (score === 3) return 3;
    return 4;
  }

  function passwordStrengthLabel(level) {
    if (level === 1) return 'Weak — try a longer mix of letters and numbers';
    if (level === 2) return 'Fair — add uppercase, numbers, or symbols';
    if (level === 3) return 'Good password';
    if (level === 4) return 'Strong password';
    return '';
  }

  function setFieldFeedback(group, message, ok) {
    if (!group) return false;
    var feedback = group.querySelector('.field-feedback');
    var serverError = group.querySelector('[data-server-error]');
    if (serverError) {
      serverError.hidden = true;
    }
    if (feedback) {
      if (message) {
        feedback.textContent = message;
        feedback.hidden = false;
        feedback.classList.toggle('is-error', !ok);
        feedback.classList.toggle('is-ok', !!ok);
      } else {
        feedback.textContent = '';
        feedback.hidden = true;
        feedback.classList.remove('is-error', 'is-ok');
      }
    }
    group.classList.toggle('is-invalid', !!message && !ok);
    group.classList.toggle('is-valid', ok === true);
    return !message || ok;
  }

  function validateRegisterEmail(value) {
    var email = (value || '').trim().toLowerCase();
    if (!email) return 'Email is required.';
    if (email.length > 254) return 'Email is too long.';
    if (!_EMAIL_RE.test(email)) return 'Enter a valid email address.';
    return null;
  }

  function validateRegisterHandle(value) {
    var handle = (value || '').trim().toLowerCase().replace(/^@/, '');
    if (!handle) return 'Handle is required.';
    if (!_HANDLE_RE.test(handle)) {
      return 'Handle must be 3–20 characters: lowercase letters, numbers, and underscores only.';
    }
    return null;
  }

  function validateRegisterPassword(value) {
    if (!value) return 'Password is required.';
    if (value.length < 8) return 'Password must be at least 8 characters.';
    if (value.length > 128) return 'Password is too long.';
    return null;
  }

  function initRegisterForm() {
    var form = document.getElementById('register-form');
    if (!form) return;

    var emailInput = form.querySelector('#email');
    var handleInput = form.querySelector('#handle');
    var passwordInput = form.querySelector('#password');
    var confirmInput = form.querySelector('#confirm_password');
    var ageInput = form.querySelector('#age_confirm');
    var ageRow = document.getElementById('age-confirm-row');
    var submitBtn = document.getElementById('register-submit');
    var strengthWrap = document.getElementById('password-strength');
    var strengthFill = strengthWrap ? strengthWrap.querySelector('.password-strength-fill') : null;
    var strengthLabel = document.getElementById('password-strength-label');
    var touched = {
      email: false,
      handle: false,
      password: false,
      confirm_password: false,
      age_confirm: false,
    };

    function groupFor(name) {
      return form.querySelector('[data-validate="' + name + '"]');
    }

    function updatePasswordStrength() {
      if (!strengthWrap || !strengthFill || !strengthLabel) return;
      var value = passwordInput.value;
      if (!value) {
        strengthWrap.hidden = true;
        strengthFill.setAttribute('data-level', '0');
        strengthLabel.textContent = '';
        return;
      }
      var level = passwordStrengthScore(value);
      strengthWrap.hidden = false;
      strengthFill.setAttribute('data-level', String(level));
      strengthLabel.textContent = passwordStrengthLabel(level);
    }

    function validateField(name, showFeedback) {
      var group = groupFor(name);
      if (!group) return true;
      var message = null;
      var ok = false;
      if (name === 'email') {
        message = validateRegisterEmail(emailInput.value);
        ok = !message;
      } else if (name === 'handle') {
        message = validateRegisterHandle(handleInput.value);
        ok = !message;
      } else if (name === 'password') {
        message = validateRegisterPassword(passwordInput.value);
        ok = !message;
        updatePasswordStrength();
      } else if (name === 'confirm_password') {
        if (!confirmInput.value) {
          message = 'Please confirm your password.';
        } else if (confirmInput.value !== passwordInput.value) {
          message = 'Passwords do not match.';
        }
        ok = !message;
      } else if (name === 'age_confirm') {
        if (!ageInput.checked) {
          message = 'You must confirm you are 13 or older to create an account.';
        }
        ok = !message;
        if (ageRow) ageRow.classList.toggle('is-invalid', !!message);
      }
      if (showFeedback || touched[name]) {
        setFieldFeedback(group, message, ok);
      }
      return ok;
    }

    function formIsValid() {
      return (
        validateRegisterEmail(emailInput.value) === null &&
        validateRegisterHandle(handleInput.value) === null &&
        validateRegisterPassword(passwordInput.value) === null &&
        confirmInput.value === passwordInput.value &&
        !!ageInput.checked
      );
    }

    function refreshSubmit() {
      if (submitBtn) submitBtn.disabled = !formIsValid();
    }

    function bindField(input, name) {
      if (!input) return;
      input.addEventListener('input', function () {
        touched[name] = true;
        validateField(name, true);
        if (name === 'password' && (touched.confirm_password || confirmInput.value)) {
          validateField('confirm_password', true);
        }
        refreshSubmit();
      });
      input.addEventListener('blur', function () {
        touched[name] = true;
        validateField(name, true);
        refreshSubmit();
      });
    }

    bindField(emailInput, 'email');
    bindField(handleInput, 'handle');
    bindField(passwordInput, 'password');
    bindField(confirmInput, 'confirm_password');

    if (handleInput) {
      handleInput.addEventListener('input', function () {
        var start = handleInput.selectionStart;
        var end = handleInput.selectionEnd;
        var next = handleInput.value.toLowerCase();
        if (next !== handleInput.value) {
          handleInput.value = next;
          if (start != null && end != null) {
            handleInput.setSelectionRange(start, end);
          }
        }
      });
    }

    if (ageInput) {
      ageInput.addEventListener('change', function () {
        touched.age_confirm = true;
        validateField('age_confirm', true);
        refreshSubmit();
      });
    }

    form.addEventListener('submit', function (event) {
      touched.email = true;
      touched.handle = true;
      touched.password = true;
      touched.confirm_password = true;
      touched.age_confirm = true;
      var valid = ['email', 'handle', 'password', 'confirm_password', 'age_confirm']
        .every(function (name) { return validateField(name, true); });
      if (!valid) {
        event.preventDefault();
        refreshSubmit();
      }
    });

    ['email', 'handle', 'password', 'confirm_password'].forEach(function (name) {
      var group = groupFor(name);
      if (group && group.querySelector('[data-server-error]')) {
        group.classList.add('is-invalid');
      }
    });
    if (groupFor('age_confirm') && groupFor('age_confirm').querySelector('[data-server-error]')) {
      if (ageRow) ageRow.classList.add('is-invalid');
    }

    refreshSubmit();
  }

  document.addEventListener('DOMContentLoaded', function () {
    initGeneratorForm();
    initRevisionPlanForm();
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
    initRevisionQueue();
    initKeyboardInset();
    initRegisterForm();
  });
})();
