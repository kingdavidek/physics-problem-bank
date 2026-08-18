(function () {
  'use strict';

  var root = document.querySelector('[data-buddy-root]');
  if (!root) return;

  var messageEl = root.querySelector('[data-buddy-message]');
  var detailEl = root.querySelector('[data-buddy-detail]');
  var actionsEl = root.querySelector('[data-buddy-actions]');
  var actionEl = root.querySelector('[data-buddy-action]');
  var dismissEl = root.querySelector('[data-buddy-dismiss]');
  if (!messageEl || !actionEl || !dismissEl) return;

  function utcDayKey() {
    return new Date().toISOString().slice(0, 10);
  }

  function storageKey() {
    return 'pb-buddy-hide-' + utcDayKey();
  }

  function stayStorageKey(topic) {
    return 'pb-buddy-stay-weak_topic-' + (topic || '') + '-' + utcDayKey();
  }

  function escapeText(value) {
    var node = document.createElement('span');
    node.textContent = value == null ? '' : String(value);
    return node.textContent;
  }

  function readEmbeddedPrompt() {
    var jsonEl = document.getElementById('pb-buddy-prompt');
    if (!jsonEl) return null;
    try {
      var parsed = JSON.parse(jsonEl.textContent || 'null');
      return parsed && parsed.message ? parsed : null;
    } catch (err) {
      return null;
    }
  }

  function currentContext() {
    var jsonEl = document.getElementById('pb-buddy-page');
    if (jsonEl) {
      try {
        var parsed = JSON.parse(jsonEl.textContent || 'null');
        if (parsed && parsed.level && parsed.topic) {
          return {
            level: String(parsed.level),
            subject: String(parsed.subject || ''),
            topic: String(parsed.topic),
          };
        }
      } catch (err) {}
    }
    var fromData = {
      level: (root.getAttribute('data-buddy-level') || '').trim(),
      subject: (root.getAttribute('data-buddy-subject') || '').trim(),
      topic: (root.getAttribute('data-buddy-topic') || '').trim(),
    };
    if (fromData.level && fromData.topic) {
      return fromData;
    }
    var path = window.location.pathname || '';
    var params = new URLSearchParams(window.location.search || '');
    var topicMatch = path.match(/^\/topic\/([^/]+)\/([^/]+)\/([^/]+)\/?$/);
    if (topicMatch) {
      return { level: topicMatch[1], subject: topicMatch[2], topic: topicMatch[3] };
    }
    var quizMatch = path.match(/^\/lesson-quiz\/([^/]+)\/([^/]+)\/([^/]+)/);
    if (quizMatch) {
      return { level: quizMatch[1], subject: quizMatch[2], topic: quizMatch[3] };
    }
    if ((path === '/' || path === '') && params.get('topic')) {
      return {
        level: params.get('level') || 'gcse',
        subject: params.get('subject') || '',
        topic: params.get('topic'),
      };
    }
    return {};
  }

  function hasStayAction(prompt) {
    var actions = (prompt && prompt.actions) || [];
    for (var i = 0; i < actions.length; i += 1) {
      if (actions[i] && actions[i].kind === 'stay') return true;
    }
    return false;
  }

  function globallyDismissed() {
    try {
      return window.localStorage.getItem(storageKey()) === '1';
    } catch (err) {
      return false;
    }
  }

  function stayDismissed(topic) {
    if (!topic) return false;
    try {
      return window.localStorage.getItem(stayStorageKey(topic)) === '1';
    } catch (err) {
      return false;
    }
  }

  function clearExtraActions() {
    if (!actionsEl) return;
    var extras = actionsEl.querySelectorAll('[data-buddy-extra]');
    extras.forEach(function (node) {
      node.parentNode.removeChild(node);
    });
  }

  function show(prompt) {
    if (!prompt || !prompt.message) return;
    messageEl.textContent = escapeText(prompt.message);
    if (detailEl) detailEl.textContent = escapeText(prompt.detail || 'Buddy');
    clearExtraActions();

    var actions = Array.isArray(prompt.actions) && prompt.actions.length
      ? prompt.actions
      : [{ kind: 'link', label: prompt.action_label || 'Open', url: prompt.action_url || '/topics' }];
    var links = actions.filter(function (item) {
      return item && item.kind !== 'stay' && item.url;
    });
    var stay = actions.filter(function (item) {
      return item && item.kind === 'stay';
    })[0];

    var primary = links[0] || {
      label: prompt.action_label || 'Open',
      url: prompt.action_url || '/topics',
    };
    actionEl.textContent = escapeText(primary.label);
    actionEl.setAttribute('href', primary.url || '/topics');
    actionEl.className = 'btn btn-primary btn-sm';

    if (actionsEl) {
      var insertBefore = dismissEl;
      links.slice(1).forEach(function (item) {
        var extra = document.createElement('a');
        extra.className = 'btn btn-outline btn-sm';
        extra.setAttribute('data-buddy-extra', '1');
        extra.setAttribute('href', item.url);
        extra.textContent = escapeText(item.label);
        actionsEl.insertBefore(extra, insertBefore);
      });
    }

    dismissEl.textContent = stay ? escapeText(stay.label) : 'Not now';
    dismissEl.setAttribute('data-buddy-stay', stay ? '1' : '0');
    root.hidden = false;
  }

  function maybeShow(prompt, source) {
    if (!prompt || !prompt.message) return false;
    if (prompt.topic) {
      root.setAttribute('data-buddy-topic', prompt.topic);
    }
    if (hasStayAction(prompt)) {
      if (stayDismissed(prompt.topic)) return true;
      show(prompt);
      return true;
    }
    if (globallyDismissed()) return true;
    show(prompt);
    return true;
  }

  dismissEl.addEventListener('click', function () {
    root.hidden = true;
    var isStay = dismissEl.getAttribute('data-buddy-stay') === '1';
    try {
      if (isStay) {
        var topic = (root.getAttribute('data-buddy-topic') || '').trim();
        window.localStorage.setItem(stayStorageKey(topic), '1');
      } else {
        window.localStorage.setItem(storageKey(), '1');
      }
    } catch (err) {}
  });

  if (root.getAttribute('data-buddy-server') === '1') {
    return;
  }
  if (dismissEl.getAttribute('data-buddy-stay') === '1' && messageEl.textContent) {
    root.removeAttribute('hidden');
    root.setAttribute('data-buddy-server', '1');
    return;
  }

  var embedded = readEmbeddedPrompt();
  if (embedded && maybeShow(embedded, 'embedded')) {
    root.setAttribute('data-buddy-server', '1');
    return;
  }

  var ctx = currentContext();
  if (!ctx.level || !ctx.topic) {
    return;
  }
  var query =
    '?level=' + encodeURIComponent(ctx.level) +
    '&subject=' + encodeURIComponent(ctx.subject || '') +
    '&topic=' + encodeURIComponent(ctx.topic);

  fetch('/api/v1/me/buddy' + query, {
    headers: {
      Accept: 'application/json',
      'X-PB-Buddy-Path': (window.location.pathname || '') + (window.location.search || ''),
    },
    credentials: 'same-origin',
    referrerPolicy: 'same-origin',
  })
    .then(function (response) {
      if (!response.ok) return null;
      return response.json();
    })
    .then(function (data) {
      if (!(data && data.ok && data.buddy)) return;
      maybeShow(data.buddy, 'fetch');
    })
    .catch(function () {});
})();
