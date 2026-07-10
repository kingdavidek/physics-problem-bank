/**
 * Quiz results AI helper — per-question "AI explain" buttons (no text selection).
 */
(function () {
  'use strict';

  var root = document.querySelector('.site-wrapper[data-quiz-review="1"]');
  if (!root) return;

  var PRESETS = [
    { label: 'Simpler', question: "Explain this as if I'm in Year 7." },
    { label: 'Why I was wrong', question: 'Explain why my answer was wrong and how to get the right one.' },
    { label: 'Step by step', question: 'Walk me through this step by step.' },
  ];

  function lessonContext() {
    return {
      level: root.dataset.lessonLevel || '',
      subject: root.dataset.lessonSubject || '',
      topic: root.dataset.lessonTopic || '',
      topicTitle: root.dataset.lessonTitle || '',
      pageUrl: window.location.pathname,
      quizReview: true,
    };
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function formatExplanation(text) {
    var safe = escapeHtml(text || '');
    safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/\n/g, '<br>');
    return safe;
  }

  function parseQuizItem(button) {
    var raw = button.getAttribute('data-quiz-item');
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch (err) {
      return null;
    }
  }

  function closeOtherPanels(activeWrap) {
    document.querySelectorAll('.quiz-assist-wrap.is-open').forEach(function (wrap) {
      if (wrap !== activeWrap) {
        wrap.classList.remove('is-open');
        var panel = wrap.querySelector('.quiz-assist-panel');
        if (panel) panel.hidden = true;
      }
    });
  }

  function setLoading(wrap, on) {
    var panel = wrap.querySelector('.quiz-assist-panel');
    if (!panel) return;
    var body = panel.querySelector('.quiz-assist-body');
    if (on) {
      body.innerHTML = '<p class="lesson-assist-loading">Thinking…</p>';
    }
    panel.querySelectorAll('.quiz-assist-preset, .quiz-assist-send').forEach(function (btn) {
      btn.disabled = on;
    });
  }

  function setRemaining(wrap, n) {
    var el = wrap.querySelector('.quiz-assist-remaining');
    if (!el || n == null) return;
    if (n <= 3) {
      el.textContent = n + ' explanation' + (n === 1 ? '' : 's') + ' left today.';
      el.hidden = false;
    } else {
      el.hidden = true;
    }
  }

  function fetchExplanation(wrap, quizItem, question) {
    setLoading(wrap, true);
    fetch('/api/lesson/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        mode: 'quiz_review',
        context: lessonContext(),
        quiz: quizItem,
        question: question,
        locale: 'en-GB',
      }),
    })
      .then(function (resp) {
        return resp.json().then(function (data) {
          return { status: resp.status, data: data };
        });
      })
      .then(function (result) {
        setLoading(wrap, false);
        var body = wrap.querySelector('.quiz-assist-body');
        if (!result.data.ok) {
          var msg =
            (result.data.error && result.data.error.message) ||
            'Something went wrong. Please try again.';
          body.innerHTML = '<p class="lesson-assist-error">' + escapeHtml(msg) + '</p>';
          return;
        }
        body.innerHTML =
          '<div class="lesson-assist-answer">' +
          formatExplanation(result.data.explanation) +
          '</div>';
        if (result.data.meta && result.data.meta.remainingToday != null) {
          setRemaining(wrap, result.data.meta.remainingToday);
        }
      })
      .catch(function () {
        setLoading(wrap, false);
        wrap.querySelector('.quiz-assist-body').innerHTML =
          '<p class="lesson-assist-error">Could not reach the assistant. Check your connection and try again.</p>';
      });
  }

  function ensurePanel(wrap) {
    if (wrap.querySelector('.quiz-assist-panel')) return;

    var panel = document.createElement('div');
    panel.className = 'quiz-assist-panel';
    panel.hidden = true;
    panel.innerHTML =
      '<div class="quiz-assist-presets"></div>' +
      '<div class="quiz-assist-body" aria-live="polite"></div>' +
      '<form class="quiz-assist-followup">' +
      '<input type="text" maxlength="200" placeholder="Ask a follow-up…" aria-label="Follow-up question">' +
      '<button type="submit" class="quiz-assist-send lesson-assist-send">Ask</button>' +
      '</form>' +
      '<p class="quiz-assist-footnote">AI explanation — check with your teacher if unsure.</p>' +
      '<p class="quiz-assist-remaining lesson-assist-remaining" hidden></p>';

    wrap.appendChild(panel);

    PRESETS.forEach(function (preset) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'quiz-assist-preset lesson-assist-preset';
      btn.textContent = preset.label;
      btn.addEventListener('click', function () {
        var quizItem = parseQuizItem(wrap.querySelector('.quiz-assist-btn'));
        if (!quizItem) return;
        panel.querySelectorAll('.quiz-assist-preset').forEach(function (b) {
          b.classList.remove('is-active');
        });
        btn.classList.add('is-active');
        fetchExplanation(wrap, quizItem, preset.question);
      });
      panel.querySelector('.quiz-assist-presets').appendChild(btn);
    });

    panel.querySelector('.quiz-assist-followup').addEventListener('submit', function (e) {
      e.preventDefault();
      var input = panel.querySelector('.quiz-assist-followup input');
      var q = (input.value || '').trim();
      var quizItem = parseQuizItem(wrap.querySelector('.quiz-assist-btn'));
      if (!q || !quizItem) return;
      fetchExplanation(wrap, quizItem, q);
    });
  }

  document.querySelectorAll('.quiz-assist-wrap').forEach(function (wrap) {
    ensurePanel(wrap);
    var btn = wrap.querySelector('.quiz-assist-btn');
    if (!btn) return;

    btn.addEventListener('click', function () {
      var quizItem = parseQuizItem(btn);
      if (!quizItem) return;

      var panel = wrap.querySelector('.quiz-assist-panel');
      var opening = panel.hidden;
      closeOtherPanels(wrap);

      if (opening) {
        wrap.classList.add('is-open');
        panel.hidden = false;
        panel.querySelector('.quiz-assist-followup input').value = '';
        panel.querySelectorAll('.quiz-assist-preset').forEach(function (b) {
          b.classList.remove('is-active');
        });
        fetchExplanation(
          wrap,
          quizItem,
          'Explain this quiz question and help me understand the correct method.'
        );
      } else {
        wrap.classList.remove('is-open');
        panel.hidden = true;
      }
    });
  });
})();
