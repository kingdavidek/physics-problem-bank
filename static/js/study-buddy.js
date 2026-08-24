(function () {
  'use strict';

  var root = document.querySelector('[data-buddy-root]');
  if (!root) return;

  var messageEl = root.querySelector('[data-buddy-message]');
  var detailEl = root.querySelector('[data-buddy-detail]');
  var actionsEl = root.querySelector('[data-buddy-actions]');
  var actionEl = root.querySelector('[data-buddy-action]');
  var dismissEl = root.querySelector('[data-buddy-dismiss]');
  var faceEl = root.querySelector('[data-buddy-face]');
  if (!messageEl || !actionEl || !dismissEl) return;

  var FACE_OK = {
    milestone: 1,
    celebrate: 1,
    qotd_nudge: 1,
    streak_risk: 1,
    weak_topic: 1,
    friend_challenge: 1,
    nudge: 1,
  };
  var FACE_FROM_EMOJI = {
    '🎉': 'milestone',
    '😄': 'celebrate',
    '❓': 'qotd_nudge',
    '🔥': 'streak_risk',
    '🤔': 'weak_topic',
    '🤝': 'friend_challenge',
    '👾': 'nudge',
  };

  function resolveFace(prompt) {
    var type = prompt && prompt.type;
    if (type && FACE_OK[type]) return type;
    var emoji = prompt && prompt.face;
    if (emoji && FACE_FROM_EMOJI[emoji]) return FACE_FROM_EMOJI[emoji];
    return 'nudge';
  }

  function applyFace(prompt) {
    if (!faceEl) return;
    faceEl.setAttribute('data-face', resolveFace(prompt));
  }

  function milestoneStorageKey(key) {
    return 'pb-buddy-milestone-' + (key || '');
  }

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

  function milestoneDismissed(key) {
    if (!key) return false;
    try {
      return window.localStorage.getItem(milestoneStorageKey(key)) === '1';
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
    applyFace(prompt);
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
    if (prompt.type === 'milestone' && prompt.milestone_key) {
      root.setAttribute('data-buddy-milestone-key', prompt.milestone_key);
    } else {
      root.removeAttribute('data-buddy-milestone-key');
    }
    root.hidden = false;
    if (window.pbCelebrate && window.pbCelebrate.fromBuddy) {
      window.pbCelebrate.fromBuddy(prompt);
    }
  }

  function maybeShow(prompt, source) {
    if (!prompt || !prompt.message) return false;
    if (prompt.topic) {
      root.setAttribute('data-buddy-topic', prompt.topic);
    }
    if (prompt.type === 'milestone' && prompt.milestone_key) {
      if (milestoneDismissed(prompt.milestone_key)) return true;
      show(prompt);
      return true;
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

  function acknowledgeMilestone(key) {
    if (!key) return;
    try {
      window.localStorage.setItem(milestoneStorageKey(key), '1');
    } catch (err) {}
  }

  function readEmbeddedMilestoneKey() {
    try {
      var jsonEl = document.getElementById('pb-buddy-prompt');
      if (!jsonEl) return '';
      var parsed = JSON.parse(jsonEl.textContent || 'null');
      if (parsed && parsed.type === 'milestone' && parsed.milestone_key) {
        return String(parsed.milestone_key);
      }
    } catch (err) {}
    return '';
  }

  actionEl.addEventListener('click', function () {
    var key = (root.getAttribute('data-buddy-milestone-key') || '').trim();
    if (!key) return;
    acknowledgeMilestone(key);
    root.hidden = true;
  });

  dismissEl.addEventListener('click', function () {
    root.hidden = true;
    var isStay = dismissEl.getAttribute('data-buddy-stay') === '1';
    try {
      if (isStay) {
        var topic = (root.getAttribute('data-buddy-topic') || '').trim();
        window.localStorage.setItem(stayStorageKey(topic), '1');
      } else {
        var milestoneKey = (root.getAttribute('data-buddy-milestone-key') || '').trim();
        if (!milestoneKey) {
          milestoneKey = readEmbeddedMilestoneKey();
        }
        if (milestoneKey) {
          acknowledgeMilestone(milestoneKey);
        } else {
          window.localStorage.setItem(storageKey(), '1');
        }
      }
    } catch (err) {}
  });

  function fetchBuddy() {
    var ctx = currentContext();
    var query = '';
    if (ctx.level && ctx.topic) {
      query =
        '?level=' + encodeURIComponent(ctx.level) +
        '&subject=' + encodeURIComponent(ctx.subject || '') +
        '&topic=' + encodeURIComponent(ctx.topic);
    }

    return fetch('/api/v1/me/buddy' + query, {
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
  }

  function refetchMatchesPage(detail) {
    if (!detail || !detail.topic) return true;
    var page = currentContext();
    if (!page.topic) return true;
    if (String(detail.topic).toLowerCase() !== String(page.topic).toLowerCase()) {
      return false;
    }
    if (detail.level && page.level && String(detail.level).toLowerCase() !== String(page.level).toLowerCase()) {
      return false;
    }
    return true;
  }

  document.addEventListener('pb-buddy-refetch', function (event) {
    var detail = (event && event.detail) || {};
    if (!refetchMatchesPage(detail)) return;
    fetchBuddy();
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

  fetchBuddy();
})();
