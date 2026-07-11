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
          if (feedback) {
            feedback.textContent = '\u2717 Not quite \u2014 try again.';
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

    typesetNodes([question, answer, hint, mcq]);
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
    var wraps = document.querySelectorAll('#mcq-options, #saved-mcq-options, .mcq-options[data-correct]');
    wraps.forEach(wireMcqBlock);
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
    initMcqInline();
    initMcqButtons();
    initSaveProblemForm();
    initRerollSavedForm();
    initScrollToProblem();
    initProbTreeInputs();
    initAnswerRevealMathJax();
  });
})();
