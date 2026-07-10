/**
 * Lesson page assistant: highlight text → Explain button → panel
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-lesson-content]');
  if (!root) return;

  var MIN_LEN = 8;
  var MAX_LEN = 800;
  var PRESETS = [
    { label: 'Simpler', question: "Explain this as if I'm in Year 7." },
    { label: 'Example', question: 'Give one short worked example related to this.' },
    { label: 'Why it matters', question: 'Why is this important for GCSE exams?' },
  ];

  var toolbar = null;
  var panel = null;
  var state = {
    selection: null,
    loading: false,
  };

  function lessonContext() {
    return {
      level: root.dataset.lessonLevel || '',
      subject: root.dataset.lessonSubject || '',
      topic: root.dataset.lessonTopic || '',
      topicTitle: root.dataset.lessonTitle || '',
      pageUrl: window.location.pathname,
    };
  }

  function stripBadgeText(text) {
    return (text || '')
      .replace(/\s+/g, ' ')
      .replace(/\b(All Exam Boards|Revision Card|Year \d+|Higher|Foundation)\b/gi, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function isBlockedNode(node) {
    if (!node) return true;
    var el = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
    while (el && el !== root) {
      if (el.matches('button, summary, svg, header, nav, .mcq-btn')) return true;
      if (el.closest('header, nav')) return true;
      el = el.parentElement;
    }
    return false;
  }

  function nearestSectionTitle(node) {
    var el = node && (node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement);
    while (el && el !== root) {
      if (el.tagName === 'DETAILS') {
        var summary = el.querySelector('summary');
        if (summary) return stripBadgeText(summary.textContent);
      }
      el = el.parentElement;
    }
    return '';
  }

  function surroundingText(node) {
    var el = node && (node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement);
    while (el && el !== root) {
      if (el.matches('p, li, td, blockquote, h2, h3, h4')) {
        return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 1200);
      }
      el = el.parentElement;
    }
    return '';
  }

  function nearMcq(node) {
    var el = node && (node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement);
    return !!(el && el.closest && el.closest('.mcq-inline'));
  }

  function readSelection() {
    var sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;

    var text = sel.toString().replace(/\s+/g, ' ').trim();
    if (text.length < MIN_LEN || text.length > MAX_LEN) return null;

    var anchor = sel.anchorNode;
    if (!anchor || !root.contains(anchor)) return null;
    if (isBlockedNode(anchor)) return null;

    var range = sel.getRangeAt(0);
    var rect = range.getBoundingClientRect();
    if (!rect.width && !rect.height) return null;

    return {
      text: text,
      surrounding: surroundingText(anchor),
      sectionTitle: nearestSectionTitle(anchor),
      nearMcq: nearMcq(anchor),
      rect: rect,
    };
  }

  function ensureToolbar() {
    if (toolbar) return toolbar;
    toolbar = document.createElement('div');
    toolbar.className = 'lesson-assist-toolbar';
    toolbar.hidden = true;
    toolbar.innerHTML =
      '<button type="button" class="lesson-assist-toolbar-btn">Explain this</button>';
    document.body.appendChild(toolbar);
    toolbar.querySelector('button').addEventListener('mousedown', function (e) {
      e.preventDefault();
      e.stopPropagation();
    });
    toolbar.querySelector('button').addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (state.selection) openPanel(state.selection);
    });
    return toolbar;
  }

  function positionToolbar(rect) {
    var bar = ensureToolbar();
    var top = rect.top - 48;
    var left = rect.left + rect.width / 2;
    top = Math.max(12, top);
    left = Math.max(72, Math.min(left, window.innerWidth - 72));
    bar.style.top = top + 'px';
    bar.style.left = left + 'px';
    bar.hidden = false;
  }

  function hideToolbar() {
    if (toolbar) toolbar.hidden = true;
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

  function ensurePanel() {
    if (panel) return panel;
    panel = document.createElement('aside');
    panel.className = 'lesson-assist-panel';
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-labelledby', 'lesson-assist-title');
    panel.hidden = true;
    panel.innerHTML =
      '<div class="lesson-assist-panel-inner">' +
      '<header class="lesson-assist-panel-header">' +
      '<h2 id="lesson-assist-title">Explain this passage</h2>' +
      '<button type="button" class="lesson-assist-close" aria-label="Close">&times;</button>' +
      '</header>' +
      '<div class="lesson-assist-quote-wrap">' +
      '<blockquote class="lesson-assist-quote"></blockquote>' +
      '<p class="lesson-assist-section"></p>' +
      '</div>' +
      '<div class="lesson-assist-mcq-note" hidden>I\'ll explain the idea, not pick A/B/C/D for you.</div>' +
      '<div class="lesson-assist-body" aria-live="polite"></div>' +
      '<div class="lesson-assist-presets"></div>' +
      '<form class="lesson-assist-followup">' +
      '<input type="text" maxlength="200" placeholder="Ask a follow-up…" aria-label="Follow-up question">' +
      '<button type="submit" class="lesson-assist-send">Ask</button>' +
      '</form>' +
      '<p class="lesson-assist-footnote">AI explanation — check with your teacher if unsure.</p>' +
      '<p class="lesson-assist-remaining"></p>' +
      '</div>';
    document.body.appendChild(panel);

    panel.querySelector('.lesson-assist-close').addEventListener('click', closePanel);
    panel.querySelector('.lesson-assist-followup').addEventListener('submit', function (e) {
      e.preventDefault();
      var input = panel.querySelector('.lesson-assist-followup input');
      var q = (input.value || '').trim();
      if (!q || state.loading || !state.selection) return;
      fetchExplanation(state.selection, q);
    });

    var presetsEl = panel.querySelector('.lesson-assist-presets');
    PRESETS.forEach(function (preset) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'lesson-assist-preset';
      btn.textContent = preset.label;
      btn.addEventListener('click', function () {
        if (state.loading || !state.selection) return;
        panel.querySelectorAll('.lesson-assist-preset').forEach(function (b) {
          b.classList.remove('is-active');
        });
        btn.classList.add('is-active');
        fetchExplanation(state.selection, preset.question);
      });
      presetsEl.appendChild(btn);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel && !panel.hidden) closePanel();
    });

    return panel;
  }

  function openPanel(selection) {
    hideToolbar();
    var p = ensurePanel();
    state.selection = selection;
    p.hidden = false;
    p.querySelector('.lesson-assist-quote').textContent = selection.text;
    var sectionEl = p.querySelector('.lesson-assist-section');
    if (selection.sectionTitle) {
      sectionEl.textContent = selection.sectionTitle;
      sectionEl.hidden = false;
    } else {
      sectionEl.hidden = true;
    }
    p.querySelector('.lesson-assist-mcq-note').hidden = !selection.nearMcq;
    p.querySelector('.lesson-assist-followup input').value = '';
    fetchExplanation(selection, 'Explain this passage in simple terms.');
  }

  function closePanel() {
    if (panel) panel.hidden = true;
    state.loading = false;
  }

  function setLoading(on) {
    state.loading = on;
    if (!panel) return;
    var body = panel.querySelector('.lesson-assist-body');
    if (on) {
      body.innerHTML = '<p class="lesson-assist-loading">Thinking…</p>';
    }
    panel.querySelectorAll('.lesson-assist-preset, .lesson-assist-send').forEach(function (btn) {
      btn.disabled = on;
    });
  }

  function setRemaining(n) {
    if (!panel || n == null) return;
    var el = panel.querySelector('.lesson-assist-remaining');
    if (n <= 3) {
      el.textContent = n + ' explanation' + (n === 1 ? '' : 's') + ' left today.';
      el.hidden = false;
    } else {
      el.hidden = true;
    }
  }

  function fetchExplanation(selection, question) {
    setLoading(true);
    var ctx = lessonContext();
    ctx.sectionTitle = selection.sectionTitle;
    ctx.nearMcq = selection.nearMcq;

    fetch('/api/lesson/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify({
        selection: {
          text: selection.text,
          surrounding: selection.surrounding,
          charCount: selection.text.length,
        },
        context: ctx,
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
        setLoading(false);
        var body = panel.querySelector('.lesson-assist-body');
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
          setRemaining(result.data.meta.remainingToday);
        }
      })
      .catch(function () {
        setLoading(false);
        panel.querySelector('.lesson-assist-body').innerHTML =
          '<p class="lesson-assist-error">Could not reach the assistant. Check your connection and try again.</p>';
      });
  }

  function showToolbarForSelection() {
    if (panel && !panel.hidden) return;

    var selection = readSelection();
    if (!selection) {
      hideToolbar();
      return;
    }

    state.selection = selection;
    positionToolbar(selection.rect);
  }

  document.addEventListener('mouseup', function (e) {
    if (panel && !panel.hidden && panel.contains(e.target)) return;
    if (toolbar && toolbar.contains(e.target)) return;
    setTimeout(showToolbarForSelection, 20);
  });

  document.addEventListener('mousedown', function (e) {
    if (toolbar && toolbar.contains(e.target)) return;
    if (panel && !panel.hidden && panel.contains(e.target)) return;
    setTimeout(function () {
      if (!readSelection()) hideToolbar();
    }, 0);
  });
})();
