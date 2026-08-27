/* Guide overlay runtime (E6). Origin, section tours, reward modal. */
(function () {
  'use strict';

  var STORAGE_KEY = 'pb-guide-v1';
  var NARROW_PX = 640;
  var ENDPOINT_TOUR = {
    index: 'practice',
    profile: 'profile',
    qotd_page: 'daily',
    topics_index: 'learn',
    friend_leaderboard_page: 'compete',
  };
  var NEVER_TOUR = {
    profile_settings: 1,
    legal_privacy: 1,
    legal_privacy_simple: 1,
    legal_terms: 1,
    login: 1,
    register: 1,
    forgot_password: 1,
    offline: 1,
    lesson_mcq_quiz: 1,
    lesson_mcq_results: 1,
    quicktest_question: 1,
    quicktest_results: 1,
    view_quiz_attempt: 1,
    challenge_detail: 1,
  };

  var storageBroken = false;
  var skipTourThisLoad = false;
  var overlay = document.querySelector('[data-guide-root]');
  var panel = overlay && overlay.querySelector('.guide-panel');
  var bubbleEl = overlay && overlay.querySelector('[data-guide-bubble]');
  var primaryBtn = overlay && overlay.querySelector('[data-guide-primary]');
  var skipBtn = overlay && overlay.querySelector('[data-guide-skip]');
  var faceEl = overlay && overlay.querySelector('[data-guide-face]');
  var medalEl = overlay && overlay.querySelector('[data-guide-medal]');
  var headingEl = overlay && overlay.querySelector('#guide-heading');
  var spotEl = overlay && overlay.querySelector('[data-guide-spot]');

  var queue = [];
  var queueId = '';
  var stepIndex = 0;
  var lineIndex = 0;
  var isOpen = false;
  var lastFocus = null;
  var pendingRewards = [];
  var emptyState = { v: 1, origin: false, tours: {}, rewards: {} };
  var seenState = { v: 1, origin: true, tours: {}, rewards: {} };
  var persistTimer = 0;
  var lastPersistBody = '';
  var memoryState = null;
  var flameTimer = 0;
  var flameNodes = [];

  function isPreview() {
    return !!(document.body && document.body.getAttribute('data-guide-preview') === '1');
  }

  function isQuizRunner() {
    return !!(document.body && document.body.getAttribute('data-guide-quiz') === '1');
  }

  function prefersReducedMotion() {
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function isNarrow() {
    return window.innerWidth <= NARROW_PX;
  }

  function copyFlags(src) {
    var out = {};
    if (!src || typeof src !== 'object') return out;
    for (var key in src) {
      if (Object.prototype.hasOwnProperty.call(src, key)) out[key] = !!src[key];
    }
    return out;
  }

  function cloneState(base) {
    return {
      v: 1,
      origin: !!base.origin,
      tours: copyFlags(base.tours),
      rewards: copyFlags(base.rewards),
    };
  }

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function canPersist() {
    return !isPreview() && !storageBroken && !!document.getElementById('pb-guide-state');
  }

  function readServerHydrate() {
    var el = document.getElementById('pb-guide-state');
    if (!el) return { persisted: false, state: null };
    var persisted = el.getAttribute('data-guide-persisted') === '1';
    try {
      var parsed = JSON.parse(el.textContent || '{}');
      if (!parsed || typeof parsed !== 'object') return { persisted: persisted, state: null };
      return { persisted: persisted, state: cloneState(parsed) };
    } catch (err) {
      return { persisted: false, state: null };
    }
  }

  function readLocal() {
    try {
      var raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return cloneState(emptyState);
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') return cloneState(seenState);
      return cloneState(parsed);
    } catch (err) {
      storageBroken = true;
      return cloneState(seenState);
    }
  }

  function persistNow(state) {
    if (!canPersist() || !window.fetch) return;
    var payload = cloneState(state);
    var body = JSON.stringify({ guide: payload });
    if (body === lastPersistBody) return;
    lastPersistBody = body;
    var headers = { Accept: 'application/json', 'Content-Type': 'application/json' };
    var token = csrfToken();
    if (token) headers['X-CSRF-Token'] = token;
    try {
      window.fetch('/api/v1/me/settings', {
        method: 'PATCH',
        headers: headers,
        body: body,
        credentials: 'same-origin',
      }).catch(function () {});
    } catch (err) {}
  }

  function schedulePersist(state) {
    if (!canPersist()) return;
    if (persistTimer) window.clearTimeout(persistTimer);
    persistTimer = window.setTimeout(function () {
      persistTimer = 0;
      persistNow(state);
    }, 400);
  }

  function flushPersist() {
    if (!persistTimer) return;
    window.clearTimeout(persistTimer);
    persistTimer = 0;
    persistNow(loadState());
  }

  function loadState() {
    if (isPreview()) return cloneState(emptyState);
    if (memoryState) return cloneState(memoryState);
    if (storageBroken) {
      memoryState = cloneState(seenState);
      return cloneState(memoryState);
    }
    var server = readServerHydrate();
    if (server.persisted && server.state) {
      memoryState = server.state;
      return cloneState(memoryState);
    }
    memoryState = readLocal();
    return cloneState(memoryState);
  }

  function saveState(state) {
    if (isPreview() || storageBroken) return;
    memoryState = cloneState(state);
    var cloned = cloneState(state);
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cloned));
    } catch (err) {
      storageBroken = true;
      return;
    }
    schedulePersist(cloned);
  }

  function maybeMigrate() {
    if (!canPersist()) return;
    var server = readServerHydrate();
    if (server.persisted) {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(server.state || cloneState(emptyState)));
      } catch (err) {}
      return;
    }
    var local = readLocal();
    if (storageBroken) return;
    if (local.origin || Object.keys(local.tours).length || Object.keys(local.rewards).length) {
      persistNow(local);
    }
  }

  function catalog() {
    return window.pbGuideCatalog || { origin: [], tours: {}, rewards: {} };
  }

  function originSteps() {
    var steps = catalog().origin;
    return Array.isArray(steps) ? steps : [];
  }

  function tourFor(endpoint) {
    return ENDPOINT_TOUR[endpoint] || '';
  }

  function markOriginSeen() {
    var state = loadState();
    state.origin = true;
    saveState(state);
  }

  function markTourSeen(id) {
    if (!id) return;
    var state = loadState();
    if (!state.tours) state.tours = {};
    state.tours[id] = true;
    saveState(state);
  }

  function rewardSeen(id) {
    if (!id) return true;
    var state = loadState();
    return !!(state.rewards && state.rewards[id]);
  }

  function markRewardSeen(id) {
    if (!id) return;
    var state = loadState();
    if (!state.rewards) state.rewards = {};
    state.rewards[id] = true;
    saveState(state);
  }

  function hideBuddyMilestone(key) {
    if (!key || isPreview()) return;
    try {
      window.localStorage.setItem('pb-buddy-milestone-' + key, '1');
    } catch (err) {}
  }

  function stepLines(step) {
    if (!step || !Array.isArray(step.lines)) return [];
    var out = [];
    for (var i = 0; i < step.lines.length; i += 1) {
      var line = step.lines[i];
      if (typeof line === 'string' && line) out.push(line);
    }
    return out;
  }

  function isShown(el) {
    if (!el || el.hidden) return false;
    if (el.closest && el.closest('[hidden]')) return false;
    var style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    return true;
  }

  function firstMatch(spec) {
    if (!spec) return null;
    var parts = String(spec).split(',');
    for (var i = 0; i < parts.length; i += 1) {
      var sel = parts[i].trim();
      if (!sel) continue;
      var el = null;
      try { el = document.querySelector(sel); } catch (err) { el = null; }
      if (el && isShown(el)) return el;
    }
    return null;
  }

  function tourSteps(id) {
    var raw = (catalog().tours || {})[id];
    if (!Array.isArray(raw)) return [];
    var out = [];
    for (var i = 0; i < raw.length; i += 1) {
      var step = raw[i];
      if (!step) continue;
      if (step.highlight && !firstMatch(step.highlight)) continue;
      out.push(step);
    }
    return out;
  }

  function focusables() {
    if (!panel) return [];
    var nodes = panel.querySelectorAll('button:not([hidden]):not([disabled])');
    var list = [];
    for (var i = 0; i < nodes.length; i += 1) list.push(nodes[i]);
    return list;
  }

  function setFace(name) {
    if (!faceEl) return;
    var ok = {
      nudge: 1,
      milestone: 1,
      celebrate: 1,
      qotd_nudge: 1,
      streak_risk: 1,
      weak_topic: 1,
      friend_challenge: 1,
    };
    faceEl.setAttribute('data-face', ok[name] ? name : 'nudge');
  }

  function setMedal(glyph) {
    if (!medalEl) return;
    medalEl.textContent = glyph || '';
  }

  function playStreakFlame() {
    if (prefersReducedMotion()) return;
    var nodes = document.querySelectorAll('.nav-streak, .streak-ring-wrap, #app-tab-bar a.app-tab[href="/profile"]');
    var i;
    for (i = 0; i < flameNodes.length; i += 1) flameNodes[i].classList.remove('is-flame');
    flameNodes = [];
    for (i = 0; i < nodes.length; i += 1) {
      nodes[i].classList.add('is-flame');
      flameNodes.push(nodes[i]);
    }
    if (medalEl) {
      medalEl.classList.add('is-flame');
      flameNodes.push(medalEl);
    }
    if (flameTimer) window.clearTimeout(flameTimer);
    flameTimer = window.setTimeout(function () {
      flameTimer = 0;
      for (i = 0; i < flameNodes.length; i += 1) flameNodes[i].classList.remove('is-flame');
      flameNodes = [];
    }, 3200);
  }

  function clearSpot() {
    if (!spotEl) return;
    spotEl.hidden = true;
    spotEl.style.top = '';
    spotEl.style.left = '';
    spotEl.style.width = '';
    spotEl.style.height = '';
  }

  function layoutSpot(el) {
    if (!spotEl || !el) return;
    var pad = 6;
    var rect = el.getBoundingClientRect();
    spotEl.hidden = false;
    spotEl.style.top = Math.max(0, rect.top - pad) + 'px';
    spotEl.style.left = Math.max(0, rect.left - pad) + 'px';
    spotEl.style.width = Math.max(0, rect.width + pad * 2) + 'px';
    spotEl.style.height = Math.max(0, rect.height + pad * 2) + 'px';
  }

  function highlightTarget(step) {
    clearSpot();
    if (!step || step.mode !== 'tour' || !step.highlight) return;
    if (isNarrow()) return;
    var el = firstMatch(step.highlight);
    if (!el) return;
    var behavior = prefersReducedMotion() ? 'auto' : 'smooth';
    try {
      el.scrollIntoView({ block: 'center', inline: 'nearest', behavior: behavior });
    } catch (err) {
      try { el.scrollIntoView(true); } catch (err2) {}
    }
    layoutSpot(el);
  }

  function lookupMilestone(key) {
    var emoji = '';
    var title = '';
    try {
      var el = document.getElementById('pb-milestone-catalog');
      if (el) {
        var map = JSON.parse(el.textContent || '{}');
        if (map && map[key]) {
          emoji = map[key].emoji || '';
          title = map[key].title || '';
        }
      }
    } catch (err) {}
    var cat = catalog().milestones || {};
    if (cat[key]) {
      if (!emoji) emoji = cat[key].emoji || '';
      if (!title) title = cat[key].title || '';
    }
    return { emoji: emoji || '★', title: title || 'New badge' };
  }

  function rewardId(spec) {
    if (!spec || !spec.type) return '';
    if (spec.type === 'milestone') {
      return 'milestone:' + String(spec.key || 'badge').replace(/\s+/g, '_');
    }
    if (spec.type === 'streak') {
      var days = parseInt(spec.days, 10);
      if (!days) return '';
      return 'streak:' + days;
    }
    if (spec.type === 'first_correct') return 'first_correct';
    if (spec.type === 'lesson_complete') return 'lesson_complete';
    return '';
  }

  function buildRewardStep(spec) {
    var id = rewardId(spec);
    if (!id) return null;
    var rewards = catalog().rewards || {};
    var template = rewards[id] || rewards[spec.type] || {};
    if (spec.type === 'milestone') {
      var meta = lookupMilestone(spec.key);
      return {
        id: id,
        mode: 'reward',
        face: template.face || 'milestone',
        medal: spec.emoji || meta.emoji,
        heading: spec.title || meta.title,
        lines: template.lines || ['You earned this.'],
        primary: template.primary || 'Close',
        skipLabel: null,
        rewardType: 'milestone',
        rewardKey: spec.key,
      };
    }
    if (spec.type === 'streak') {
      var n = parseInt(spec.days, 10);
      return {
        id: id,
        mode: 'reward',
        face: template.face || 'celebrate',
        medal: '🔥',
        heading: n + '-day streak',
        lines: template.lines || [n + '-day streak. Nice work keeping it going.'],
        primary: template.primary || 'Close',
        skipLabel: null,
        rewardType: 'streak',
        rewardKey: String(n),
      };
    }
    if (spec.type === 'first_correct' || spec.type === 'lesson_complete') {
      return {
        id: id,
        mode: 'reward',
        face: template.face || 'celebrate',
        medal: template.medal || (spec.type === 'first_correct' ? '✓' : '★'),
        heading: template.heading || (spec.type === 'first_correct' ? 'First correct' : 'Lesson complete'),
        lines: template.lines || ['Well done.'],
        primary: template.primary || 'Close',
        skipLabel: null,
        rewardType: spec.type,
        rewardKey: spec.type,
      };
    }
    return null;
  }

  function renderStep() {
    var step = queue[stepIndex];
    if (!step) {
      finishQueue();
      return;
    }
    var lines = stepLines(step);
    if (!lines.length) {
      advanceStep();
      return;
    }
    if (prefersReducedMotion()) lineIndex = lines.length;
    else if (lineIndex < 1) lineIndex = 1;
    if (lineIndex > lines.length) lineIndex = lines.length;

    setFace(step.face);
    setMedal(step.mode === 'reward' ? (step.medal || '') : '');
    var heading = step.heading || (step.mode === 'reward' ? 'Well done' : 'Zorp');
    if (step.mode === 'tour' && isNarrow() && step.spotLabel) heading = step.spotLabel;
    if (headingEl) headingEl.textContent = heading;
    if (bubbleEl) {
      bubbleEl.textContent = prefersReducedMotion()
        ? lines.join('\n')
        : lines[lineIndex - 1];
    }
    if (primaryBtn) primaryBtn.textContent = step.primary || 'Continue';
    if (skipBtn) {
      if (step.skipLabel) {
        skipBtn.hidden = false;
        skipBtn.textContent = step.skipLabel;
      } else {
        skipBtn.hidden = true;
      }
    }
    overlay.setAttribute('data-guide-mode', step.mode || 'story');
    if (step.mode === 'tour') document.body.classList.add('guide-tour-open');
    else document.body.classList.remove('guide-tour-open');
    highlightTarget(step);
    if (step.rewardType === 'streak') playStreakFlame();
  }

  function openOverlay() {
    if (!overlay || isOpen) return;
    lastFocus = document.activeElement;
    overlay.hidden = false;
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('guide-open');
    isOpen = true;
    window.setTimeout(function () {
      if (primaryBtn) primaryBtn.focus();
    }, 0);
  }

  function closeOverlay() {
    if (!overlay || !isOpen) return;
    overlay.hidden = true;
    overlay.setAttribute('aria-hidden', 'true');
    overlay.removeAttribute('data-guide-mode');
    document.body.classList.remove('guide-open');
    document.body.classList.remove('guide-tour-open');
    isOpen = false;
    queue = [];
    queueId = '';
    stepIndex = 0;
    lineIndex = 0;
    setMedal('');
    clearSpot();
    if (lastFocus && typeof lastFocus.focus === 'function') {
      try { lastFocus.focus(); } catch (err) {}
    }
    lastFocus = null;
  }

  function afterClose() {
    playPendingRewards();
    if (!isOpen) maybePlayTour();
  }

  function finishQueue() {
    var finishedId = queueId;
    var step = queue[stepIndex] || queue[0];
    if (finishedId === 'origin') markOriginSeen();
    else if (finishedId === 'reward' && step && step.id) {
      markRewardSeen(step.id);
      if (step.rewardType === 'milestone') hideBuddyMilestone(step.rewardKey);
    } else if (finishedId && finishedId !== 'reward') {
      markTourSeen(finishedId);
    }
    closeOverlay();
    window.setTimeout(afterClose, 0);
  }

  function advanceStep() {
    stepIndex += 1;
    lineIndex = 0;
    if (stepIndex >= queue.length) {
      finishQueue();
      return;
    }
    renderStep();
  }

  function onPrimary() {
    var step = queue[stepIndex];
    var lines = stepLines(step);
    if (lineIndex < lines.length) {
      lineIndex += 1;
      renderStep();
      return;
    }
    advanceStep();
  }

  function onSkip() {
    finishQueue();
  }

  function startQueue(steps, id) {
    if (isOpen) closeOverlay();
    queue = steps;
    queueId = id;
    stepIndex = 0;
    lineIndex = 0;
    if (steps[0] && steps[0].mode === 'tour') document.body.classList.add('guide-tour-open');
    openOverlay();
    renderStep();
  }

  function playTour(id) {
    var steps = tourSteps(id);
    if (steps.length < 1) {
      markTourSeen(id);
      return;
    }
    startQueue(steps, id);
  }

  function play(id) {
    if (!overlay || !bubbleEl || !primaryBtn || !skipBtn) return;
    if (id === 'origin') {
      var steps = originSteps();
      if (steps.length < 1) return;
      startQueue(steps, 'origin');
      return;
    }
    if (id && (catalog().tours || {})[id]) playTour(id);
  }

  function playPendingRewards() {
    if (isOpen) return;
    if (isQuizRunner()) return;
    while (pendingRewards.length) {
      var spec = pendingRewards.shift();
      var id = rewardId(spec);
      if (!id || rewardSeen(id)) continue;
      var step = buildRewardStep(spec);
      if (!step) continue;
      if (spec.type === 'milestone') hideBuddyMilestone(spec.key);
      startQueue([step], 'reward');
      return;
    }
  }

  function reward(spec) {
    if (!overlay || !bubbleEl || !primaryBtn || !skipBtn) return false;
    if (isQuizRunner()) return false;
    var id = rewardId(spec);
    if (!id) return false;
    if (rewardSeen(id)) return false;
    pendingRewards.push(spec);
    if (isOpen) return true;
    playPendingRewards();
    return isOpen && queueId === 'reward';
  }

  function seen(id) {
    var state = loadState();
    if (id === 'origin') return !!state.origin;
    if (state.rewards && state.rewards[id]) return true;
    return !!(state.tours && state.tours[id]);
  }

  function resetOrigin() {
    var state = loadState();
    state.origin = false;
    saveState(state);
    flushPersist();
  }

  function maybePlayTour() {
    if (!overlay) return;
    if (isPreview() || isQuizRunner() || isOpen) return;
    if (skipTourThisLoad) return;
    if (pendingRewards.length) {
      playPendingRewards();
      return;
    }
    var body = document.body;
    if (!body) return;
    var endpoint = body.getAttribute('data-guide-endpoint') || '';
    if (NEVER_TOUR[endpoint]) return;
    var tour = tourFor(endpoint);
    if (!tour || seen(tour)) return;
    playTour(tour);
  }

  function maybeAutoplay() {
    maybeMigrate();
    if (!overlay) return;
    var body = document.body;
    if (!body) return;
    if (isPreview()) return;
    if (isQuizRunner()) return;
    var endpoint = body.getAttribute('data-guide-endpoint') || '';
    if (NEVER_TOUR[endpoint]) return;
    if (!seen('origin')) {
      skipTourThisLoad = true;
      play('origin');
      return;
    }
    window.setTimeout(maybePlayTour, 0);
  }

  function onKeydown(event) {
    if (!isOpen) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      onSkip();
      return;
    }
    if (event.key !== 'Tab') return;
    var items = focusables();
    if (!items.length) return;
    var first = items[0];
    var last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function onViewport() {
    if (!isOpen) return;
    var step = queue[stepIndex];
    if (step && step.mode === 'tour')     highlightTarget(step);
  }

  window.pbGuide = {
    play: play,
    reward: reward,
    seen: seen,
    resetOrigin: resetOrigin,
  };

  if (primaryBtn) primaryBtn.addEventListener('click', onPrimary);
  if (skipBtn) skipBtn.addEventListener('click', onSkip);
  document.addEventListener('keydown', onKeydown);
  window.addEventListener('resize', onViewport);
  window.addEventListener('orientationchange', onViewport);
  window.addEventListener('pagehide', flushPersist);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', maybeAutoplay);
  } else {
    maybeAutoplay();
  }
})();
