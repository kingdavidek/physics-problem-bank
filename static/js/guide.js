/* Guide overlay runtime (E6). Origin, section tours, reward modal. */
(function () {
  'use strict';

  // E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.2): the browser copy of the guide's seen-state is one pupil's (the account's
  // storage name, meta pb-store; 'anon' signed out). The old shared key 'pb-guide-v1' could hand the last pupil's seen tours and
  // rewards to a new account before its first save, so it is removed unread. The server copy is the record once it exists.
  var STORE_NS = (function () {
    var m = document.querySelector('meta[name="pb-store"]');
    return (m && m.getAttribute('content')) || 'anon';
  })();
  var STORAGE_KEY = 'pb-guide-v1:' + STORE_NS;
  try { window.localStorage.removeItem('pb-guide-v1'); } catch (err) {}
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
    welcome: 1,
  };

  // E7 Phase 2: gestures. LEGACY_GESTURES are the four E6 CSS-keyframe names, used as the
  // fallback path when pbZorp is unavailable. ZORP_GESTURES is the superset now playable
  // through pbZorp.play (those four plus the new WAAPI clips).
  var LEGACY_GESTURES = { wink: 1, nod: 1, shake: 1, tap: 1 };
  // E8 Phase 5 adds the beat clips; play() ignores a name the runtime does not have (no zorp-poses.js).
  var ZORP_GESTURES = { wink: 1, nod: 1, shake: 1, tap: 1, cheer: 1, wave: 1, think: 1, hop: 1, 'side-point': 1, 'fist-pump': 1, victory: 1, flex: 1, shrug: 1, 'think-chin': 1, bow: 1, dance: 1, float: 1 };

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
  var emptyState = { v: 1, origin: false, tours: {}, rewards: {}, run: null };
  var seenState = { v: 1, origin: true, tours: {}, rewards: {}, run: null };
  var persistTimer = 0;
  var lastPersistBody = '';
  var memoryState = null;
  var flameTimer = 0;
  var flameNodes = [];
  var gestureTimer = 0;
  var gestureEl = null;

  function isPreview() {
    return !!(document.body && document.body.getAttribute('data-guide-preview') === '1');
  }

  function isQuizRunner() {
    return !!(document.body && document.body.getAttribute('data-guide-quiz') === '1');
  }

  // E10 phase 4: a quiz results page (lesson quiz results, a saved attempt, Quick Test results) is part of the quiz runner for
  // everything else, but a badge or streak moment may play there; question pages stay quiet.
  function isQuizResults() {
    return !!(document.body && document.body.getAttribute('data-guide-quiz-results') === '1');
  }

  function isBig(spec) {
    return !!spec && (spec.type === 'milestone' || spec.type === 'streak');
  }

  function prefersReducedMotion() {
    return !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  // E9 Phase 1 (docs/ZORP_CHARM.md 3.1.5): the line reveal follows the runtime's motion level, which honours data-motion
  // (the motion_preference setting) as well as the OS query. Without the runtime it is the media query, as before.
  function reducedLines() {
    var z = window.pbZorp;
    if (z && typeof z.motionLevel === 'function') return z.motionLevel() !== 'full';
    return prefersReducedMotion();
  }

  // The talk mouth caps in ms (3.0): story and reward lines 1,600; tours 1,200. A gesture that turns Zorp side-on
  // (side-point, bow) plays on the last line, and the talk mouth is placed for one view, so that line is not talked.
  var TALK_MAX = { story: 1600, reward: 1600, tour: 1200 };
  var VIEW_GESTURES = { 'side-point': 1, bow: 1 };

  // The text goes in first, synchronously (the live region reads it once); the mouth then follows.
  function showLine(text, step, last, reduced) {
    var z = window.pbZorp;
    if (z && typeof z.say === 'function' && faceEl) {
      z.say(bubbleEl, text, {
        el: faceEl,
        max: TALK_MAX[step.mode] || TALK_MAX.story,
        talk: !reduced && !(last && VIEW_GESTURES[step.gesture]),
      });
      return;
    }
    bubbleEl.textContent = text;
  }

  function hushFace() {
    var z = window.pbZorp;
    if (faceEl && z && typeof z.hush === 'function') z.hush(faceEl);
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
      // E10 phase 6: the tour in progress, {id, step}; null when none (the server keeps it in guide_json "run")
      run: base.run && typeof base.run.id === 'string' ? { id: base.run.id, step: parseInt(base.run.step, 10) || 0 } : null,
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
    if (!canPersist() || !window.fetch) return Promise.resolve();
    var payload = cloneState(state);
    var body = JSON.stringify({ guide: payload });
    if (body === lastPersistBody) return Promise.resolve();
    lastPersistBody = body;
    var headers = { Accept: 'application/json', 'Content-Type': 'application/json' };
    var token = csrfToken();
    if (token) headers['X-CSRF-Token'] = token;
    try {
      // keepalive: the tour saves its step just before it navigates to the next page
      return window.fetch('/api/v1/me/settings', {
        method: 'PATCH',
        headers: headers,
        body: body,
        credentials: 'same-origin',
        keepalive: true,
      }).catch(function () {});
    } catch (err) {}
    return Promise.resolve();
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

  // E8 Phase 2: a preset is accepted only inside the guide allowlist (models/zorp_rig.py
  // CONTEXT_MAP['guide'] via pbZorp.allowedIn). Lore steps (step.lore, allowlisted ids) may also
  // open on a negative preset, and the one big reward (step.big, the 100-day streak: happy tears,
  // 'guide.reward.big') on aww-teary; both show step.resolve (a positive one) on their last line.
  var GUIDE_FALLBACK = { nudge: 1, milestone: 1, celebrate: 1, qotd_nudge: 1, streak_risk: 1, weak_topic: 1, friend_challenge: 1 };
  function guideFace(step, lastLine) {
    var name = step.face;
    if ((step.lore || step.big) && lastLine && step.resolve) name = step.resolve;
    return name;
  }
  function setFace(name, context) {
    if (!faceEl) return;
    var z = window.pbZorp;
    var known = z && typeof z.allowedIn === 'function'
      ? z.allowedIn(context || 'guide', name)
      : GUIDE_FALLBACK[name] === 1;
    var face = known ? name : 'nudge';
    if (z && z.setFace(face, { el: faceEl })) return;
    faceEl.setAttribute('data-face', face);
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

  function clearGesture() {
    if (gestureTimer) {
      window.clearTimeout(gestureTimer);
      gestureTimer = 0;
    }
    if (gestureEl) {
      gestureEl.removeAttribute('data-gesture');
      gestureEl = null;
    }
  }

  function playGesture(name, target, cue) {
    var el = target || faceEl;
    if (!el) return false;
    if (window.pbZorp && ZORP_GESTURES[name]) {
      if (gestureTimer) {
        window.clearTimeout(gestureTimer);
        gestureTimer = 0;
      }
      if (gestureEl && gestureEl !== el) gestureEl.removeAttribute('data-gesture');
      gestureEl = null;
      window.pbZorp.bind(el);
      window.pbZorp.play(name, { el: el, cue: !!cue });   // E9 Phase 4: a reward's clip may sound its cues (pbSound gates them)
      return true;
    }
    if (prefersReducedMotion()) return false;
    if (!LEGACY_GESTURES[name]) return false;
    if (gestureTimer) {
      window.clearTimeout(gestureTimer);
      gestureTimer = 0;
    }
    if (gestureEl && gestureEl !== el) gestureEl.removeAttribute('data-gesture');
    gestureEl = el;
    el.removeAttribute('data-gesture');
    void el.getBoundingClientRect();
    el.setAttribute('data-gesture', name);
    gestureTimer = window.setTimeout(function () {
      gestureTimer = 0;
      if (gestureEl) gestureEl.removeAttribute('data-gesture');
      gestureEl = null;
    }, 1200);
    return true;
  }

  function gesture(name) {
    var demo = document.getElementById('guide-preview-zorp');
    return playGesture(name, demo || faceEl);
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
    // E10 phase 5: every lesson is its own moment (lesson:<level>:<subject>:<topic>); without a topic it is the old single reward
    if (spec.type === 'lesson_complete') return spec.topic ? ('lesson:' + [spec.level, spec.subject, spec.topic].join(':')).toLowerCase().replace(/[^a-z0-9_:]/g, '_').slice(0, 64) : 'lesson_complete';
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
        gesture: template.gesture || null,
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
        gesture: template.gesture || null,
        big: !!template.big,
        resolve: template.resolve || null,
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
        gesture: template.gesture || null,
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
    var reduced = reducedLines();
    if (reduced) lineIndex = lines.length;
    else if (lineIndex < 1) lineIndex = 1;
    if (lineIndex > lines.length) lineIndex = lines.length;

    // The last line of a lore step is checked against the plain guide list, so a negative
    // face can never stay on screen at the end of a step (missing or negative step.resolve).
    setFace(guideFace(step, lineIndex === lines.length),
      lineIndex < lines.length ? (step.big ? 'guide.reward.big' : (step.lore ? 'guide.lore' : 'guide')) : 'guide');
    setMedal(step.mode === 'reward' ? (step.medal || '') : '');
    var heading = step.heading || (step.mode === 'reward' ? 'Well done' : 'Zorp');
    if (step.mode === 'tour' && isNarrow() && step.spotLabel) heading = step.spotLabel;
    if (headingEl) headingEl.textContent = heading;
    if (bubbleEl) {
      showLine(reduced ? lines.join('\n') : lines[lineIndex - 1], step, lineIndex === lines.length, reduced);
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
    if (reduced || lineIndex === lines.length) playGesture(step.gesture, null, step.mode === 'reward');
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
    hushFace();
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
    clearGesture();
    if (lastFocus && typeof lastFocus.focus === 'function') {
      try { lastFocus.focus(); } catch (err) {}
    }
    lastFocus = null;
  }

  function afterClose() {
    playPendingRewards();
    runMoments();
    if (!isOpen) maybePlayTour();
  }

  function finishQueue() {
    var finishedId = queueId;
    var step = queue[stepIndex] || queue[0];
    if (finishedId === 'origin') markOriginSeen();
    else if (finishedId === 'reward' && step && step.id) {
      markRewardSeen(step.id);
    } else if (finishedId === 'appoffer') {
      // "Show me around" starts the tour; "Not now" (or Esc) means it is skipped, and it stays in Settings
      if (offerAccepted) beginAppTour(true);
      else endAppTour();
      offerAccepted = false;
    } else if (finishedId && finishedId !== 'reward') {
      markTourSeen(finishedId);
    }
    closeOverlay();
    window.setTimeout(afterClose, 0);
  }

  function advanceStep() {
    hushFace();
    stepIndex += 1;
    lineIndex = 0;
    if (stepIndex >= queue.length) {
      finishQueue();
      return;
    }
    renderStep();
  }

  var offerAccepted = false;

  function onPrimary() {
    var step = queue[stepIndex];
    var lines = stepLines(step);
    if (lineIndex < lines.length) {
      lineIndex += 1;
      renderStep();
      return;
    }
    if (queueId === 'appoffer') offerAccepted = true;
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

  // E10 (docs/ZORP_ARRIVAL_AND_CELEBRATIONS_PLAN.md 6.1): the full-screen stage lives in zorp-stage.js, stage-catalog.js and
  // stage.css, which only load when a stage is about to play (URLs from the #pb-stage-assets island in partials/guide.html).
  var stagePromise = null;
  var stagePending = false;

  function stageAssets() {
    var el = document.getElementById('pb-stage-assets');
    try {
      var a = el ? JSON.parse(el.textContent || '{}') : null;
      return a && a.js && a.css && a.catalog ? a : null;
    } catch (err) {
      return null;
    }
  }

  function addAsset(tag, attrs) {
    return new Promise(function (resolve, reject) {
      var node = document.createElement(tag);
      for (var key in attrs) {
        if (Object.prototype.hasOwnProperty.call(attrs, key)) node.setAttribute(key, attrs[key]);
      }
      node.onload = resolve;
      node.onerror = reject;
      document.head.appendChild(node);
    });
  }

  function loadStage() {
    if (window.pbStage && window.pbStage.play) return window.pbStage.ready();
    if (stagePromise) return stagePromise;
    var a = stageAssets();
    if (!a) return Promise.reject(new Error('no stage'));
    stagePromise = Promise.all([
      addAsset('link', { rel: 'stylesheet', href: a.css }),
      addAsset('script', { src: a.catalog }),
      addAsset('script', { src: a.js }),
    ]).then(function () {
      if (!window.pbStage) throw new Error('no stage');
      return window.pbStage.ready();
    });
    stagePromise.catch(function () { stagePromise = null; });
    return stagePromise;
  }

  // E10 phase 3: the first question after the arrival is coached (zorp-coach.js + coach.css, loaded only then). While the coach
  // loads or runs, no Practice tour opens; when it ends (finished, skipped or left) both are marked seen.
  var coachState = '';
  function coachAssets() {
    try { return JSON.parse((document.getElementById('pb-coach-assets') || {}).textContent || 'null'); } catch (err) { return null; }
  }

  function coachDue() {
    var body = document.body;
    return !!(body && body.getAttribute('data-guide-coach') === '1' && !coachState && !seen('coach') && coachAssets());
  }

  function startCoach() {
    var a = coachAssets();
    coachState = 'loading';
    // the corner Zorp rests on a phone from now on (chrome.css), not only once the coach files have loaded; zorp-coach.js clears the class when it ends
    document.body.classList.add('pb-coach-on');
    Promise.all([
      addAsset('link', { rel: 'stylesheet', href: a.css }),
      addAsset('script', { src: a.js }),
    ]).then(function () {
      if (!window.pbCoach || !window.pbCoach.start()) throw new Error('no coach');
      coachState = 'active';
    }).catch(function () {
      coachState = 'done';
      document.body.classList.remove('pb-coach-on');
      document.body.classList.add('pb-coach-done');
      skipTourThisLoad = false;
      maybePlayTour();
    });
  }

  document.addEventListener('pb-coach-ended', function (e) {
    coachState = 'done';
    document.body.classList.add('pb-coach-done');
    markTourSeen('coach');
    markTourSeen('practice');
    flushPersist();
    // E10 phase 6 (owner's answer 5): the app tour starts by itself when the coach is done or skipped (not when the pupil left the page)
    if (e && e.detail && e.detail.how !== 'leave' && !seen('app')) beginAppTour(true);
  });

  // E10 review fix 2: moments in flight (loading moments.js, or playing) count as a stage, so no dialog (the tour offer, a reward) opens beside them
  var momentsInFlight = 0;
  function stageBusy() {
    return stagePending || momentsInFlight > 0 || !!(window.pbStage && window.pbStage.isOpen());
  }

  // E10 phase 6: the app tour ("Show me around", across pages) and the just-in-time spotlights are zorp-tour.js and tour.css, loaded
  // only when one is due (URLs from the #pb-tour-assets island). The tour in progress is guide state "run" ({id, step}), so it
  // survives page loads. It starts by itself when the coached first question ends (done or skipped), is offered once to an account
  // that never had it (the Practice page), and replays from Settings. Once it has run or been skipped, the per-tab tours stay quiet.
  var tourPhase = '';   // '' | 'loading' | 'active' | 'done' (the app tour on this page view)
  var tourPromise = null;
  var spotChecked = false;
  var APP_PAGE = { index: 1, topics_index: 1, qotd_page: 1, friend_leaderboard_page: 1, profile: 1, student_classes: 1, profile_settings: 1 };
  // which spotlights an element-based page may show (the rest come from events: hint and bigger)
  var SPOT_PAGE = {
    topic_page: ['lessonquiz'], quicktest_results: ['quicktest'], lesson_mcq_results: ['aiexplain'], view_quiz_attempt: ['aiexplain'],
    student_classes: ['setwork'], student_class_work: ['setwork'], student_class_work_detail: ['setwork'],
    challenges_list: ['challenge'], friend_leaderboard_page: ['challenge'], profile: ['revision', 'saved'],
  };
  var SPOT_EVENT = { 'pb-hint-shown': 'hint', 'pb-hint-bigger': 'bigger' };

  function tourAssets() {
    try {
      var a = JSON.parse((document.getElementById('pb-tour-assets') || {}).textContent || 'null');
      return a && a.js && a.css ? a : null;
    } catch (err) {
      return null;
    }
  }

  function loadTour() {
    if (window.pbTour) return Promise.resolve(window.pbTour);
    if (tourPromise) return tourPromise;
    var a = tourAssets();
    if (!a) return Promise.reject(new Error('no tour'));
    tourPromise = Promise.all([addAsset('link', { rel: 'stylesheet', href: a.css }), addAsset('script', { src: a.js })]).then(function () {
      if (!window.pbTour) throw new Error('no tour');
      return window.pbTour;
    });
    tourPromise.catch(function () { tourPromise = null; });
    return tourPromise;
  }

  function appRun() {
    var run = loadState().run;
    return run && run.id === 'app' && !seen('app') ? run : null;
  }

  function tourOn() {
    return tourPhase === 'loading' || tourPhase === 'active';
  }

  // fresh: a new run from the first stop (after the coach, from Settings, or after "Show me around")
  function beginAppTour(fresh) {
    if (tourOn() || !tourAssets() || isPreview()) return;
    if (fresh) {
      var state = loadState();
      state.run = { id: 'app', step: 0 };
      if (!state.tours) state.tours = {};
      state.tours.app = false;
      saveState(state);
      flushPersist();
    }
    tourPhase = 'loading';
    document.body.classList.add('pb-tour-on');
    loadTour().then(function (tour) {
      if (!tour.start()) throw new Error('no stop on this page');
      tourPhase = 'active';
    }).catch(function () {
      tourPhase = '';
      document.body.classList.remove('pb-tour-on');
    });
  }

  // the tour ended (finished or skipped): the per-tab tours would only repeat it, so they count as seen
  function endAppTour() {
    tourPhase = 'done';
    document.body.classList.remove('pb-tour-on');
    var state = loadState();
    state.run = null;
    if (!state.tours) state.tours = {};
    ['app', 'practice', 'learn', 'daily', 'compete', 'profile'].forEach(function (id) { state.tours[id] = true; });
    saveState(state);
    flushPersist();
  }

  // a spotlight (one line, the first time a pupil meets a feature): never during a tour, the coach, a dialog or a stage
  function maybeSpot(ids) {
    if (!tourAssets() || isPreview() || tourOn() || coachState === 'loading' || coachState === 'active') return;
    var due = (ids || []).filter(function (id) { return !seen('sp_' + id); });
    if (!due.length) return;
    loadTour().then(function (tour) { tour.spot(due); }).catch(function () { /* the page works without it */ });
  }

  Object.keys(SPOT_EVENT).forEach(function (name) {
    document.addEventListener(name, function () {
      if (document.body.classList.contains('pb-coach-on') || document.body.getAttribute('data-guide-coach') === '1') return;   // the coached question has its own hints
      maybeSpot([SPOT_EVENT[name]]);
    });
  });

  // The origin story is the arrival film's scenes 1 to 5 on the stage (an account that never saw it); the dialogue-box
  // origin in guide-catalog.js stays as the fallback when the stage cannot load (offline, an old page).
  function playOrigin() {
    var steps = originSteps();
    var fallback = function () {
      stagePending = false;
      if (steps.length && !isOpen) startQueue(steps, 'origin');
    };
    if (!stageAssets()) {
      fallback();
      return;
    }
    stagePending = true;
    loadStage().then(function (stage) {
      stagePending = false;
      return stage.play('arrival', { story: true }).then(function () {
        markOriginSeen();
        flushPersist();
      });
    }).catch(fallback);
  }

  function play(id) {
    if (!overlay || !bubbleEl || !primaryBtn || !skipBtn) return;
    if (id === 'origin') {
      if (!stageBusy()) playOrigin();
      return;
    }
    if (id && (catalog().tours || {})[id]) playTour(id);
  }

  // E10 phase 4: badges and streak moments play on the badge stage (badge-stage.js and badge-stage.css, loaded only then; URLs from
  // the #pb-badge-assets island). Everything that arrives within a moment is one batch, so two badges (or a badge and its streak
  // reward) are one stage after another. If the files cannot load, the older reward dialog plays instead.
  var badgePromise = null;
  var badgeTimer = 0;

  function badgeAssets() {
    try {
      var a = JSON.parse((document.getElementById('pb-badge-assets') || {}).textContent || 'null');
      return a && a.js && a.css && a.props && stageAssets() ? a : null;
    } catch (err) {
      return null;
    }
  }

  function loadBadgeStage() {
    if (window.pbBadgeStage) return Promise.resolve(window.pbBadgeStage);
    if (badgePromise) return badgePromise;
    var a = badgeAssets();
    if (!a) return Promise.reject(new Error('no badge stage'));
    badgePromise = loadStage().then(function () {
      return Promise.all([addAsset('link', { rel: 'stylesheet', href: a.css }), addAsset('script', { src: a.js })]);
    }).then(function () {
      if (!window.pbBadgeStage) throw new Error('no badge stage');
      return window.pbBadgeStage;
    });
    badgePromise.catch(function () { badgePromise = null; });
    return badgePromise;
  }

  function playBadges() {
    var batch = [];
    var rest = [];
    pendingRewards.forEach(function (spec) {
      if (!isBig(spec)) rest.push(spec);
      else if (!rewardSeen(rewardId(spec))) batch.push(spec);
    });
    pendingRewards = rest;
    if (!batch.length) return false;
    stagePending = true;
    var legacy = function () {
      stagePending = false;
      for (var i = 0; i < batch.length; i += 1) {
        var step = buildRewardStep(batch[i]);
        if (step && !isOpen) { startQueue([step], 'reward'); return; }
      }
    };
    loadBadgeStage().then(function (bs) {
      stagePending = false;
      return bs.play(batch);
    }).catch(legacy);
    return true;
  }

  // E10 phase 5: moments (a level-up, a perfect quiz, a finished lesson, toasts, micro reactions) play from moments.js and
  // moments.css, loaded only when one is due (URLs from the #pb-moment-assets island). They wait for the badge stage and any
  // dialog, then play after it, so one stage is on screen at a time; never while quiz questions are on screen.
  var pendingMoments = [];
  var momentTimer = 0;
  var momentsPromise = null;

  function momentAssets() {
    try {
      var a = JSON.parse((document.getElementById('pb-moment-assets') || {}).textContent || 'null');
      return a && a.js && a.css && a.props && stageAssets() ? a : null;
    } catch (err) {
      return null;
    }
  }

  function loadMoments() {
    if (window.pbMoments) return Promise.resolve(window.pbMoments);
    if (momentsPromise) return momentsPromise;
    var a = momentAssets();
    if (!a) return Promise.reject(new Error('no moments'));
    momentsPromise = Promise.all([addAsset('link', { rel: 'stylesheet', href: a.css }), addAsset('script', { src: a.js })]).then(function () {
      if (!window.pbMoments) throw new Error('no moments');
      return window.pbMoments;
    });
    momentsPromise.catch(function () { momentsPromise = null; });
    return momentsPromise;
  }

  // E10 phase 8: Zorp's story chapters (story-chapters.js and story.css, loaded only when one plays or is offered; URLs from the
  // #pb-story-assets island). An offer ("Zorp has a new story for you", Watch or Later) rides the moments pipeline as a toast, so it
  // appears after any badge stage; it is shown last, one at a time, and never plays by itself.
  var storyPromise = null;

  function loadStory() {
    if (window.pbStory) return Promise.resolve(window.pbStory);
    if (storyPromise) return storyPromise;
    var a;
    try { a = JSON.parse((document.getElementById('pb-story-assets') || {}).textContent || 'null'); } catch (err) { a = null; }
    if (!a || !a.js || !a.css) return Promise.reject(new Error('no story'));
    storyPromise = loadStage().then(function () {
      var have = document.querySelector('link[href="' + a.css + '"]');   // the profile page links the style itself
      return Promise.all([have ? null : addAsset('link', { rel: 'stylesheet', href: a.css }), addAsset('script', { src: a.js })]);
    }).then(function () {
      if (!window.pbStory) throw new Error('no story');
      return window.pbStory;
    });
    storyPromise.catch(function () { storyPromise = null; });
    return storyPromise;
  }

  function isStoryOffer(m) { return !!m && m.kind === 'story_offer'; }

  function runMoments() {
    if (!pendingMoments.length || isOpen || stageBusy() || badgeTimer || pendingRewards.some(isBig)) return;
    var all = pendingMoments;
    var offers = all.filter(isStoryOffer);
    var batch = all.filter(function (m) { return !isStoryOffer(m); });
    pendingMoments = [];
    momentsInFlight += 1;
    var settled = function () { momentsInFlight -= 1; window.setTimeout(afterClose, 0); };   // also on failure: whatever waited may go now
    (batch.length ? loadMoments().then(function (m) { return m.play(batch); }) : Promise.resolve()).catch(function () { /* the page works without them */ }).then(function () {
      return offers.length ? loadStory().then(function (st) { st.offer(offers[0]); }) : null;
    }).then(function () { settled(); }, function () { settled(); });
  }

  function moments(list) {
    if (!overlay || !momentAssets() || (isQuizRunner() && !isQuizResults())) return false;
    (Array.isArray(list) ? list : []).forEach(function (m) { if (m && m.type && !(m.id && pendingMoments.some(function (x) { return x.id === m.id; }))) pendingMoments.push(m); });   // one fetch can be read twice (celebrate.js and site.js)
    if (pendingMoments.length && !momentTimer) momentTimer = window.setTimeout(function () { momentTimer = 0; runMoments(); }, 220);
    return pendingMoments.length > 0;
  }

  function playPendingRewards() {
    if (isOpen) return;
    if (stageBusy()) return;
    while (pendingRewards.length) {
      var head = pendingRewards[0];
      if (isQuizRunner() && !(isQuizResults() && isBig(head))) return;
      if (isBig(head) && badgeAssets()) {
        if (playBadges()) return;
        continue;
      }
      var spec = pendingRewards.shift();
      var id = rewardId(spec);
      if (!id || rewardSeen(id)) continue;
      var step = buildRewardStep(spec);
      if (!step) continue;
      startQueue([step], 'reward');
      return;
    }
  }

  // E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.3): one beat, not two.
  // * A pupil's first right answer often earns a badge at the same moment (Lesson learner on a quick check). The first-correct
  //   dialog waits FIRST_HOLD_MS (the confetti and Zorp's cheer do not); a badge or a stage in that time says it instead, and the
  //   dialog is then not shown at all.
  // * The lesson-complete stage carries the lesson's own badge (topic_completed:<level>:<subject>:<topic>, earned by the save of
  //   the last quick check): the badge is taken out of the queue, or kept out when it arrives later, and named on the lesson stage,
  //   which marks it seen when it plays (moments.js).
  var FIRST_HOLD_MS = 1800;
  var firstHold = 0;
  var absorbed = {};

  function dropFirstCorrect() {
    if (!firstHold) return;
    window.clearTimeout(firstHold);
    firstHold = 0;
    markRewardSeen('first_correct');
  }

  function holdFirstCorrect(spec) {
    if (firstHold) return false;
    firstHold = window.setTimeout(function () {
      firstHold = 0;
      if (rewardSeen('first_correct')) return;
      if (stageBusy() || badgeTimer || pendingMoments.length || pendingRewards.some(isBig)) { markRewardSeen('first_correct'); return; }
      pendingRewards.push(spec);
      if (!isOpen) playPendingRewards();
    }, FIRST_HOLD_MS);
    return true;
  }

  function absorbLessonBadge(spec) {
    var key = 'topic_completed:' + [spec.level, spec.subject, spec.topic].join(':');
    var found = null;
    pendingRewards = pendingRewards.filter(function (r) {
      if (r && r.type === 'milestone' && r.key === key) { found = r; return false; }
      return true;
    });
    if (found && !spec.badge) spec.badge = { key: key, title: (found.badge && found.badge.title) || '' };
    absorbed[key] = true;
  }

  function reward(spec) {
    if (!overlay || !bubbleEl || !primaryBtn || !skipBtn) return false;
    if (isQuizRunner() && !(isQuizResults() && isBig(spec))) return false;
    var id = rewardId(spec);
    if (!id) return false;
    if (rewardSeen(id)) return false;
    if (spec.type === 'milestone' && absorbed[spec.key]) { markRewardSeen(id); return 'stage'; }
    if (spec.type === 'first_correct') return holdFirstCorrect(spec);
    if (isBig(spec) || spec.type === 'lesson_complete') dropFirstCorrect();
    if (spec.type === 'lesson_complete' && spec.topic && momentAssets()) {
      absorbLessonBadge(spec);
      return moments([spec]) ? 'stage' : false;
    }
    pendingRewards.push(spec);
    if (isBig(spec) && badgeAssets()) {
      // wait a moment for the rest of the batch (a badge and its streak reward arrive together)
      if (!badgeTimer) badgeTimer = window.setTimeout(function () { badgeTimer = 0; playPendingRewards(); }, 120);
      return 'stage';
    }
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
    if (isPreview() || isQuizRunner()) return;
    if (coachState === 'loading' || coachState === 'active') return;
    if (coachDue()) {
      skipTourThisLoad = true;
      startCoach();
      return;
    }
    if (document.body.getAttribute('data-guide-coach') === '1') document.body.classList.add('pb-coach-done');   // no coach to wait for: the corner Zorp may show
    if (isOpen || stageBusy()) return;
    if (skipTourThisLoad) return;
    if (pendingRewards.length) {
      playPendingRewards();
      return;
    }
    var body = document.body;
    if (!body) return;
    var endpoint = body.getAttribute('data-guide-endpoint') || '';
    if (tourOn()) return;
    // the app tour in progress continues on its next page (it is not a per-tab tour, so NEVER_TOUR does not apply)
    if (APP_PAGE[endpoint] && appRun()) {
      beginAppTour(false);
      return;
    }
    if (NEVER_TOUR[endpoint]) return;
    // an account that never had the app tour is offered it once, on Practice (in place of that page's own first-visit tour)
    if (endpoint === 'index' && !seen('app') && !seen('appoffer') && seen('origin')) {
      markTourSeen('appoffer');
      play('appoffer');
      return;
    }
    // once the app tour has run (or been skipped) the per-tab tours would only repeat it
    var tour = seen('app') ? '' : tourFor(endpoint);
    if (!tour || seen(tour)) {
      spotPage(endpoint);
      return;
    }
    playTour(tour);
  }

  function spotPage(endpoint) {
    if (spotChecked || !SPOT_PAGE[endpoint]) return;
    spotChecked = true;
    maybeSpot(SPOT_PAGE[endpoint]);
  }

  function maybeAutoplay() {
    maybeMigrate();
    if (!overlay) return;
    var body = document.body;
    if (!body) return;
    if (isPreview()) return;
    var endpoint = body.getAttribute('data-guide-endpoint') || '';
    if (isQuizRunner()) {
      // a results page may show one spotlight (the first Quick Test, the first AI explain); question pages stay quiet
      if (isQuizResults() && seen('origin')) window.setTimeout(function () { spotPage(endpoint); }, 0);
      return;
    }
    if (NEVER_TOUR[endpoint] && !(APP_PAGE[endpoint] && appRun())) return;   // the app tour in progress also runs on Settings
    if (!seen('origin')) {
      skipTourThisLoad = true;
      play('origin');
      return;
    }
    window.setTimeout(maybePlayTour, 0);
  }

  function onKeydown(event) {
    if (!isOpen || (window.pbStage && window.pbStage.isOpen())) return;   // E10 review fix 2: Esc on a stage is the stage's, never the dialog's
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

  // E10: the arrival on /welcome marks the origin story seen when its story part ends (welcome.js).
  function markSeen(id) {
    if (id !== 'origin') return;
    markOriginSeen();
    flushPersist();
  }

  window.pbGuide = {
    play: play,
    reward: reward,
    seen: seen,
    resetOrigin: resetOrigin,
    gesture: gesture,
    markSeen: markSeen,
    markReward: function (id) { markRewardSeen(id); flushPersist(); },   // E10 phase 4: the badge stage marks each moment it plays
    moments: moments,   // E10 phase 5: hand over moments (a list of {type, id, ...}); they play after any badge stage
    rewardSeen: rewardSeen,
    rewardId: rewardId,
    loadStage: loadStage,
    // E10 phase 6: what zorp-tour.js needs from the guide (state, the stage, whether anything else is on screen)
    tour: {
      run: function () { var r = loadState().run; return r ? { id: r.id, step: r.step } : null; },
      setRun: function (run) { var s = loadState(); s.run = run || null; saveState(s); },
      seen: seen,
      markSeen: function (id) { markTourSeen(id); flushPersist(); },
      end: endAppTour,
      commit: function () {   // save the guide state now; resolves when the server has it
        if (persistTimer) { window.clearTimeout(persistTimer); persistTimer = 0; }
        return persistNow(loadState());
      },
      busy: function () { return isOpen || stageBusy() || !!badgeTimer || pendingRewards.length > 0 || pendingMoments.length > 0; },
      csrf: csrfToken,
    },
    badges: function (specs) {   // the badge stage straight, for the preview and tests (no seen-state check)
      return loadBadgeStage().then(function (bs) { return bs.play(specs); });
    },
    stage: function (spec, opts) {
      return loadStage().then(function (stage) { return stage.play(spec, opts); });
    },
    story: function (n, opts) {   // E10 phase 8: play chapter n (0 is the arrival) from the shelf or the preview
      return loadStory().then(function (st) { return st.play(n, opts); });
    },
    offerStory: function (n) {
      return loadStory().then(function (st) { var m = { id: 'story:' + n, chapter: n }; m.force = 1; return st.offer(m); });
    },
  };

  if (primaryBtn) primaryBtn.addEventListener('click', onPrimary);
  if (skipBtn) skipBtn.addEventListener('click', onSkip);
  document.addEventListener('keydown', onKeydown);
  window.addEventListener('resize', onViewport);
  window.addEventListener('orientationchange', onViewport);
  window.addEventListener('pagehide', flushPersist);
  // a stage just closed: anything that waited for it (a reward, a tour) may run now
  document.addEventListener('pb-stage-closed', function () { window.setTimeout(afterClose, 0); });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', maybeAutoplay);
  } else {
    maybeAutoplay();
  }
})();
