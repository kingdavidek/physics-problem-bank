(function () {
  'use strict';

  try {
    if (window.localStorage.getItem('pb-buddy-storage') !== 'v3') {
      var buddyKeys = [];
      var deadPrefixes = [
        'pb-buddy-dismissed-',
        'pb-buddy-hide-',
        'pb-buddy-stay-',
        'pb-buddy-milestone-',
      ];
      for (var i = 0; i < window.localStorage.length; i += 1) {
        var key = window.localStorage.key(i);
        if (!key) continue;
        for (var p = 0; p < deadPrefixes.length; p += 1) {
          if (key.indexOf(deadPrefixes[p]) === 0) {
            buddyKeys.push(key);
            break;
          }
        }
      }
      buddyKeys.forEach(function (item) { window.localStorage.removeItem(item); });
      window.localStorage.setItem('pb-buddy-storage', 'v3');
    }
  } catch (e) {}

  var root = document.querySelector('[data-buddy-root]');
  if (!root) return;

  var cardEl = root.querySelector('[data-buddy-card]');
  var messageEl = root.querySelector('[data-buddy-message]');
  var detailEl = root.querySelector('[data-buddy-detail]');
  var actionsEl = root.querySelector('[data-buddy-actions]');
  var actionEl = root.querySelector('[data-buddy-action]');
  var dismissEl = root.querySelector('[data-buddy-dismiss]');
  var faceEl = root.querySelector('[data-buddy-face]');
  if (!cardEl || !messageEl || !actionEl || !dismissEl) return;

  var QUIET_KEY = 'pb-buddy-quiet';
  var QUIET_MS_ACTED = 10 * 60 * 1000;
  var QUIET_MS_DISMISSED = 30 * 60 * 1000;

  // No-runtime fallback table: name -> valence. A prompt face is never negative (E8 section 5),
  // so a negative entry here would still be refused by faceKnown().
  var FACE_OK = {
    milestone: 'positive',
    celebrate: 'positive',
    qotd_nudge: 'neutral',
    streak_risk: 'positive',
    weak_topic: 'neutral',
    friend_challenge: 'positive',
    nudge: 'neutral',
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

  // E8: pbZorp.hasExpression knows every preset; FACE_OK is only the no-runtime fallback.
  // Phase 2: presets whose valence is negative are never drawn for a prompt type.
  function faceKnown(name) {
    var z = window.pbZorp;
    if (z && typeof z.hasExpression === 'function') {
      if (!z.hasExpression(name)) return false;
      return typeof z.valenceOf !== 'function' || z.valenceOf(name) !== 'negative';
    }
    return Object.prototype.hasOwnProperty.call(FACE_OK, name) && FACE_OK[name] !== 'negative';
  }

  function resolveFace(prompt) {
    var type = prompt && prompt.type;
    if (type && faceKnown(type)) return type;
    var emoji = prompt && prompt.face;
    if (emoji && FACE_FROM_EMOJI[emoji]) return FACE_FROM_EMOJI[emoji];
    return 'nudge';
  }

  function applyFace(prompt) {
    if (!faceEl) return;
    var face = resolveFace(prompt);
    if (window.pbZorp && window.pbZorp.setFace(face, { el: faceEl })) return;
    faceEl.setAttribute('data-face', face);
  }

  var reactTimer = null;
  function reactBuddy() {
    if (!faceEl) return;
    if (window.pbZorp && typeof window.pbZorp.play === 'function') {
      window.pbZorp.play('nod', { el: faceEl, ifIdle: true });
      return;
    }
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    faceEl.classList.remove('is-reacting');
    void faceEl.offsetWidth;
    faceEl.classList.add('is-reacting');
    if (reactTimer) window.clearTimeout(reactTimer);
    reactTimer = window.setTimeout(function () {
      faceEl.classList.remove('is-reacting');
      reactTimer = null;
    }, 560);
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

  // --- Quiet-period gate ------------------------------------------------
  // One localStorage key tracks the last time the user acted on (or dismissed)
  // a bubble. `mark` is the server's opaque `task_mark`: while it is unchanged,
  // nothing new has happened, so a re-fetch during the quiet window still
  // shouldn't show anything even once the window itself has expired.

  function readQuiet() {
    try {
      var raw = window.localStorage.getItem(QUIET_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object' && typeof parsed.until === 'number') {
        return parsed;
      }
      return null;
    } catch (err) {
      return null;
    }
  }

  function writeQuiet(untilMs, mark) {
    try {
      window.localStorage.setItem(QUIET_KEY, JSON.stringify({ until: untilMs, mark: mark || '' }));
    } catch (err) {}
  }

  function shouldShow(prompt) {
    var state = readQuiet();
    if (!state) return true;
    var quietOver = Date.now() >= state.until;
    if (!prompt.task_mark) {
      // No task_mark to compare against: only showable once the quiet window
      // itself has lapsed.
      return quietOver;
    }
    return quietOver && prompt.task_mark !== state.mark;
  }

  function hasStayAction(prompt) {
    var actions = (prompt && prompt.actions) || [];
    for (var i = 0; i < actions.length; i += 1) {
      if (actions[i] && actions[i].kind === 'stay') return true;
    }
    return false;
  }

  function clearExtraActions() {
    if (!actionsEl) return;
    var extras = actionsEl.querySelectorAll('[data-buddy-extra]');
    extras.forEach(function (node) {
      node.parentNode.removeChild(node);
    });
  }

  var currentPrompt = null;

  function show(prompt) {
    if (!prompt || !prompt.message) return;
    currentPrompt = prompt;
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
    var stay = hasStayAction(prompt) ? actions.filter(function (item) {
      return item && item.kind === 'stay';
    })[0] : null;

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
    cardEl.hidden = false;
    root.setAttribute('data-buddy-state', 'card');
    if (window.pbCelebrate && window.pbCelebrate.fromBuddy) {
      window.pbCelebrate.fromBuddy(prompt);
    }
  }

  function maybeShow(prompt) {
    if (!prompt || !prompt.message) return false;
    if (prompt.topic) {
      root.setAttribute('data-buddy-topic', prompt.topic);
    }
    if (!shouldShow(prompt)) return false;
    show(prompt);
    return true;
  }

  // Primary action click, or any secondary [data-buddy-extra] link click: act
  // now, quiet for 10 minutes (a shorter window than an explicit dismiss,
  // since the user just engaged with the bubble rather than brushing it off).
  if (actionsEl) {
    actionsEl.addEventListener('click', function (event) {
      var target = event.target;
      if (!target) return;
      var isPrimary = target === actionEl;
      var isExtra = !!(target.hasAttribute && target.hasAttribute('data-buddy-extra'));
      if (!isPrimary && !isExtra) return;
      cardEl.hidden = true;
      root.setAttribute('data-buddy-state', 'face');
      writeQuiet(Date.now() + QUIET_MS_ACTED, currentPrompt && currentPrompt.task_mark);
    });
  }

  dismissEl.addEventListener('click', function () {
    cardEl.hidden = true;
    root.setAttribute('data-buddy-state', 'face');
    writeQuiet(Date.now() + QUIET_MS_DISMISSED, currentPrompt && currentPrompt.task_mark);
  });

  function fetchBuddy(fromRefetch) {
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
        var shown = maybeShow(data.buddy);
        if (fromRefetch && shown) reactBuddy();
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
    fetchBuddy(true);
  });

  if (faceEl && window.pbZorp) {
    window.pbZorp.bind(faceEl);
    window.pbZorp.idle(true, faceEl);   // runtime pauses on visibilitychange / reduced motion
  }

  // The island is always rendered when the aside renders (as `null` when there is
  // nothing to show), so its mere presence means the server already answered this
  // question for the initial load -- only fetch when there is no island at all
  // (e.g. a page that doesn't wire one up).
  var hasIsland = !!document.getElementById('pb-buddy-prompt');
  var embedded = readEmbeddedPrompt();
  if (embedded) maybeShow(embedded);
  if (!hasIsland) fetchBuddy();
})();
