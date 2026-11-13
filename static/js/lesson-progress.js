/**
 * Lesson progress rail — a subsection counts as complete only after its Quick Check
 * MCQ is answered correctly (mcq-correct event).
 * U4.3 chrome: mobile progress bar, inline quiz CTA, completion celebration.
 */
(function () {
  'use strict';

  var wrapper = document.querySelector('.site-wrapper[data-lesson-content]');
  if (!wrapper) return;

  var level = wrapper.dataset.lessonLevel;
  var subject = wrapper.dataset.lessonSubject;
  var topic = wrapper.dataset.lessonTopic;
  var isLoggedIn = wrapper.dataset.userLoggedIn === '1';
  var csrfMeta = document.querySelector('meta[name="csrf-token"]');
  var csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';
  // E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.2): the browser copy of a pupil's ticks is that pupil's own. The keys carry
  // the account's storage name (meta pb-store), so pupils who share a computer never see each other's ticks (a ticked step ignores a
  // right answer, so a borrowed tick used to block the pupil's own progress). Signed out uses its own 'anon' keys, which a signed-in
  // pupil never reads (David's answer 9). The old keys, shared by everyone on the browser, are removed unread.
  var storeMeta = document.querySelector('meta[name="pb-store"]');
  var storeNs = (storeMeta && storeMeta.getAttribute('content')) || '';
  var lessonId = level + ':' + subject + ':' + topic;
  var useLocal = !isLoggedIn || !!storeNs;   // signed in without a storage name: keep nothing in the browser, the server holds it all
  var storageKey = 'lesson-progress:' + (isLoggedIn ? storeNs : 'anon') + ':' + lessonId;
  var celebrateKey = storageKey + ':celebrated';
  try {
    window.localStorage.removeItem('lesson-progress:' + lessonId);
    window.localStorage.removeItem('lesson-progress:' + lessonId + ':celebrated');
  } catch (err) {}

  var contentRoot;
  var topbarEl;
  var topbarFillEl;
  var topbarLabelEl;
  var topbarToastEl;
  var topbarToastFillEl;
  var topbarToastLabelEl;
  var topbarHideTimer;
  var quizCtaBar;
  var celebrated = false;
  var finishingLive = false;
  var TOPBAR_SHOW_MS = 2800;
  var TOPBAR_FADE_MS = 420;

  function isMobileLesson() {
    return window.matchMedia('(max-width: 960px)').matches;
  }

  function hideMobileTopbarToast() {
    if (!topbarToastEl) return;
    clearTimeout(topbarHideTimer);
    topbarToastEl.classList.remove('is-showing');
    topbarHideTimer = setTimeout(function () {
      topbarToastEl.classList.remove('is-visible');
    }, TOPBAR_FADE_MS);
  }

  function showMobileTopbarPulse() {
    if (!topbarToastEl || !topbarLabelEl || !topbarFillEl || !isMobileLesson()) return;
    topbarToastLabelEl.textContent = topbarLabelEl.textContent;
    topbarToastFillEl.style.width = topbarFillEl.style.width;
    topbarToastEl.setAttribute('aria-valuenow', topbarEl.getAttribute('aria-valuenow') || '0');
    topbarToastEl.setAttribute('aria-valuemax', topbarEl.getAttribute('aria-valuemax') || '0');
    clearTimeout(topbarHideTimer);
    topbarToastEl.classList.add('is-visible');
    window.requestAnimationFrame(function () {
      topbarToastEl.classList.add('is-showing');
    });
    topbarHideTimer = setTimeout(hideMobileTopbarToast, TOPBAR_SHOW_MS);
  }

  function findLessonContentRoot(root) {
    var shell = root.querySelector('.lesson-shell');
    if (shell) return shell;
    var candidates = root.querySelectorAll('.page-shell');
    if (candidates.length) return candidates[0];
    return root.firstElementChild || root;
  }

  function removeInlineQuizCtas(root) {
    root.querySelectorAll('a[href*="/lesson-quiz/"]').forEach(function (link) {
      var host = link.parentElement;
      if (host && host !== root && host.tagName === 'DIV' && host.children.length === 1) {
        host.remove();
      } else {
        link.remove();
      }
    });
  }

  function removeLegacyLessonEndCtas(scope) {
    scope.querySelectorAll('form[action="/quicktest/start"]').forEach(function (form) {
      var host = form.closest('div');
      if (host && host !== scope) host.remove();
      else form.remove();
    });

    scope.querySelectorAll('a[href*="/lesson-quiz/"]').forEach(function (link) {
      var label = (link.textContent || '').replace(/\s+/g, ' ').trim();
      if (label === 'Start Practice Quiz') {
        var block = link.closest('div');
        if (block) block.remove();
      }
    });

    scope.querySelectorAll('p').forEach(function (paragraph) {
      if ((paragraph.textContent || '').replace(/\s+/g, ' ').trim() !== 'Ready to practise?') return;
      var block = paragraph.closest('div');
      if (block) block.remove();
      else paragraph.remove();
    });
  }

  function initGeneratorCta(scope) {
    var practiceUrl = wrapper.dataset.lessonPracticeUrl;
    if (!practiceUrl) return;

    removeLegacyLessonEndCtas(scope);

    var footer = document.createElement('div');
    footer.className = 'lesson-generator-cta';
    footer.innerHTML =
      '<p>Want more practice questions?</p>' +
      '<a href="' + practiceUrl + '" class="btn btn-outline btn-lg">' +
      'Practice this topic with the generator' +
      '</a>';
    scope.appendChild(footer);
  }

  function initQuizCta(root) {
    if (document.querySelector('[data-quiz-runner]') || document.body.classList.contains('quiz-runner-active')) {
      return;
    }
    var quizUrl = wrapper.dataset.lessonQuizUrl;
    var quizCount = parseInt(wrapper.dataset.lessonQuizCount || '10', 10);
    if (!quizUrl) return;

    removeInlineQuizCtas(root);

    quizCtaBar = document.createElement('div');
    quizCtaBar.className = 'lesson-quiz-cta-bar';
    quizCtaBar.innerHTML =
      '<a href="' + quizUrl + '" class="btn btn-primary lesson-quiz-cta-btn">' +
      'Take the quiz · ' + quizCount + ' questions' +
      '</a>';
    root.appendChild(quizCtaBar);
  }

  function initMobileTopbar(shell) {
    var topbarMarkup =
      '<span class="lesson-progress-topbar-label"></span>' +
      '<div class="lesson-progress-topbar-track">' +
      '<div class="lesson-progress-topbar-fill"></div>' +
      '</div>';

    topbarEl = document.createElement('div');
    topbarEl.className = 'lesson-progress-topbar is-pinned';
    topbarEl.setAttribute('role', 'progressbar');
    topbarEl.setAttribute('aria-label', 'Lesson progress');   // E10 Phase 9 review: a progress bar needs a name
    topbarEl.setAttribute('aria-valuemin', '0');
    topbarEl.innerHTML = topbarMarkup;
    shell.insertBefore(topbarEl, contentRoot);
    topbarLabelEl = topbarEl.querySelector('.lesson-progress-topbar-label');
    topbarFillEl = topbarEl.querySelector('.lesson-progress-topbar-fill');

    topbarToastEl = document.createElement('div');
    topbarToastEl.className = 'lesson-progress-topbar lesson-progress-topbar-toast';
    topbarToastEl.setAttribute('role', 'status');
    topbarToastEl.setAttribute('aria-live', 'polite');
    topbarToastEl.innerHTML = topbarMarkup;
    document.body.appendChild(topbarToastEl);
    topbarToastLabelEl = topbarToastEl.querySelector('.lesson-progress-topbar-label');
    topbarToastFillEl = topbarToastEl.querySelector('.lesson-progress-topbar-fill');
  }

  function enhanceSectionCards(steps) {
    steps.forEach(function (step) {
      var subsection = step.subsection;
      var sectionNum = step.index + 1;
      subsection.classList.add('lesson-section', 'lesson-section-card');
      subsection.setAttribute('data-lesson-section', String(sectionNum));

      var summary = subsection.querySelector(':scope > summary');
      if (!summary) return;
      summary.classList.add('lesson-section-summary');

      var chip = summary.querySelector('.lesson-section-chip');
      if (!chip) {
        var spans = summary.querySelectorAll(':scope > span');
        var i;
        for (i = 0; i < spans.length; i += 1) {
          if (/^\d+$/.test((spans[i].textContent || '').trim())) {
            chip = spans[i];
            break;
          }
        }
        if (chip) {
          chip.classList.add('lesson-section-chip');
        } else {
          chip = document.createElement('span');
          chip.className = 'lesson-section-chip';
          chip.textContent = String(sectionNum);
          summary.insertBefore(chip, summary.firstChild);
        }
      }

      if (!summary.querySelector('.lesson-section-status')) {
        var status = document.createElement('span');
        status.className = 'lesson-section-status';
        summary.appendChild(status);
      }
    });
  }

  function updateSectionStatus(step) {
    var summary = step.subsection.querySelector(':scope > summary');
    if (!summary) return;
    var status = summary.querySelector('.lesson-section-status');
    if (!status) return;
    status.classList.toggle('is-complete', step.completed);
    status.setAttribute(
      'aria-label',
      step.completed ? 'Section complete' : 'Section incomplete'
    );
  }

  function updateMobileTopbar(steps, pulse) {
    if (!topbarFillEl || !topbarLabelEl || !steps.length) return;
    var completed = steps.filter(function (step) { return step.completed; }).length;
    var total = steps.length;
    var pct = total ? Math.round((completed / total) * 100) : 0;
    topbarFillEl.style.width = pct + '%';
    topbarLabelEl.textContent =
      completed + ' of ' + total + ' sections · ' + pct + '%';
    topbarEl.setAttribute('aria-valuenow', String(completed));
    topbarEl.setAttribute('aria-valuemax', String(total));
    topbarEl.setAttribute('aria-valuetext', completed + ' of ' + total + ' sections complete');
    if (pulse) showMobileTopbarPulse();
  }

  // E10 phase 5: finishing a lesson is a stage moment, once per lesson (pbGuide's seen-state lesson:<level>:<subject>:<topic> and the
  // local flag). It plays only when the last quick check is answered on this page (live), never because a lesson that was
  // already finished loads, so older lessons and other devices are not celebrated again.
  function maybeCelebrateAllComplete(steps, live, badge) {
    if (!steps.length || celebrated) return;
    if (!live && finishingLive) return;   // the last quick check's own celebration is waiting for its save
    var allDone = steps.every(function (step) { return step.completed; });
    if (!allDone) return;
    celebrated = true;
    try {
      if (useLocal) window.localStorage.setItem(celebrateKey, '1');
    } catch (err) {}
    if (quizCtaBar) quizCtaBar.classList.add('is-complete');
    pathLessonDone();
    if (live && window.pbCelebrate && window.pbCelebrate.lessonComplete) {
      var heading = document.querySelector('h1');
      window.pbCelebrate.lessonComplete({
        level: level,
        subject: subject,
        topic: topic,
        name: heading ? (heading.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60) : '',
        quiz: wrapper.dataset.lessonQuizUrl || '',
        badge: badge || null,
      });
    }
  }

  // E11 Phase 4 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 4.3): the topic's mastery path (from the server, signed-in pupils only) as chips
  // under the lesson's heading, and the quiz bar's line once every quick check is done ("Lesson done. A 10/10 on the quiz makes you
  // a ninja on this topic."). The words come from models/progress_bits.py; textContent only.
  var path = null;
  try { path = JSON.parse(wrapper.dataset.lessonPath || 'null'); } catch (err) { path = null; }
  var pathChips = null;
  function markDone(li) {
    li.classList.add('is-done');
    var s = document.createElement('span');
    s.className = 'vh';
    s.textContent = ' ' + (path.done || '');
    li.appendChild(s);
  }
  function initPath(root) {
    if (!path || !path.steps) return;
    pathChips = document.createElement('ol');
    pathChips.className = 'mastery-chips lesson-path';
    pathChips.setAttribute('aria-label', path.label || '');
    path.steps.forEach(function (step) {
      var li = document.createElement('li');
      li.className = 'mastery-chip';
      li.setAttribute('data-step', step.id);
      li.textContent = step.label;
      if (step.done) markDone(li);
      pathChips.appendChild(li);
    });
    var h1 = root.querySelector('h1');
    if (h1 && h1.parentNode) h1.parentNode.insertBefore(pathChips, h1.nextSibling);
    else root.insertBefore(pathChips, root.firstChild);
    if (path.steps[0] && path.steps[0].done) pathLessonDone();
  }
  function pathLessonDone() {
    if (!path) return;
    var li = pathChips && pathChips.querySelector('[data-step="lesson"]');
    if (li && !li.classList.contains('is-done')) markDone(li);
    if (quizCtaBar && path.bar && !quizCtaBar.querySelector('.lesson-quiz-cta-note')) {
      var note = document.createElement('p');
      note.className = 'lesson-quiz-cta-note';
      note.textContent = path.bar;
      quizCtaBar.insertBefore(note, quizCtaBar.firstChild);
    }
  }

  function readCelebratedFlag() {
    try {
      return useLocal && window.localStorage.getItem(celebrateKey) === '1';
    } catch (err) {
      return false;
    }
  }

  function subsectionForMcq(mcq) {
    return mcq.closest('details');
  }

  function sectionLabel(detailsEl) {
    var summary = detailsEl && detailsEl.querySelector(':scope > summary');
    if (!summary) return '';
    return (summary.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200);
  }

  function summaryTop(subsection) {
    var summary = subsection && subsection.querySelector(':scope > summary');
    var rootRect = contentRoot.getBoundingClientRect();
    var targetRect = summary
      ? summary.getBoundingClientRect()
      : subsection.getBoundingClientRect();
    return targetRect.top + targetRect.height / 2 - rootRect.top + contentRoot.scrollTop;
  }

  function mcqTop(step) {
    var subsection = step.subsection;
    var mcq = step.mcq;
    var rootRect = contentRoot.getBoundingClientRect();
    var targetRect;

    if (subsection.open && mcq) {
      targetRect = mcq.getBoundingClientRect();
    } else {
      var summary = subsection.querySelector(':scope > summary');
      targetRect = summary
        ? summary.getBoundingClientRect()
        : subsection.getBoundingClientRect();
    }

    return targetRect.top + targetRect.height / 2 - rootRect.top + contentRoot.scrollTop;
  }

  function openSubsection(detailsEl) {
    var chain = [];
    var el = detailsEl;
    while (el && el !== contentRoot) {
      if (el.tagName === 'DETAILS') chain.push(el);
      el = el.parentElement;
    }
    chain.reverse().forEach(function (d) {
      d.open = true;
    });
  }

  function normalizeStepKey(key) {
    if (!key) return '';
    if (key.indexOf('section-') === 0) {
      return 'step-' + key.slice('section-'.length);
    }
    return key;
  }

  function buildSteps(root) {
    var mcqs = root.querySelectorAll('.mcq-inline');
    var steps = [];
    mcqs.forEach(function (mcq, index) {
      var subsection = subsectionForMcq(mcq);
      if (!subsection) return;
      var key = 'step-' + index;
      subsection.dataset.lessonStepKey = key;
      steps.push({
        key: key,
        index: index,
        mcq: mcq,
        subsection: subsection,
        completed: false,
      });
    });
    return steps;
  }

  function completedKeys(steps) {
    return steps.filter(function (step) {
      return step.completed;
    }).map(function (step) {
      return step.key;
    });
  }

  function readLocalProgress() {
    if (!useLocal) return [];
    try {
      var raw = window.localStorage.getItem(storageKey);
      if (!raw) return [];
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.completed_keys)) return [];
      return data.completed_keys.map(normalizeStepKey).filter(Boolean);
    } catch (err) {
      return [];
    }
  }

  function writeLocalProgress(keys) {
    if (!useLocal) return;
    try {
      window.localStorage.setItem(
        storageKey,
        JSON.stringify({ completed_keys: keys })
      );
    } catch (err) {}
  }

  contentRoot = findLessonContentRoot(wrapper);
  initGeneratorCta(wrapper);
  initQuizCta(contentRoot);
  initPath(contentRoot);
  celebrated = readCelebratedFlag();
  if (celebrated && quizCtaBar) { quizCtaBar.classList.add('is-complete'); pathLessonDone(); }

  var steps = buildSteps(contentRoot);
  if (!steps.length) return;

  enhanceSectionCards(steps);
  contentRoot.classList.add('lesson-progress-content');

  var shell = document.createElement('div');
  shell.className = 'lesson-progress-shell';
  contentRoot.parentNode.insertBefore(shell, contentRoot);
  shell.appendChild(contentRoot);

  initMobileTopbar(shell);

  var rail = document.createElement('div');
  rail.className = 'lesson-progress-rail';
  rail.setAttribute('aria-label', 'Lesson progress');
  rail.innerHTML =
    '<div class="lesson-progress-rail-inner">' +
    '<div class="lesson-progress-rail-track">' +
    '<div class="lesson-progress-rail-fill"></div>' +
    '</div>' +
    '</div>';
  shell.insertBefore(rail, contentRoot);

  var railInner = rail.querySelector('.lesson-progress-rail-inner');
  var fillEl = rail.querySelector('.lesson-progress-rail-fill');
  var layoutTimer = null;
  var saveTimer = null;
  var startTop = 0;

  var startNode = document.createElement('div');
  startNode.className = 'lesson-progress-rail-node is-start';
  startNode.setAttribute('aria-hidden', 'true');
  railInner.appendChild(startNode);

  function applyCompletedKeys(keys) {
    var keySet = {};
    (keys || []).forEach(function (key) {
      keySet[normalizeStepKey(key)] = true;
    });

    steps.forEach(function (step) {
      var done = !!keySet[step.key];
      step.completed = done;
      step.subsection.classList.toggle('lesson-subsection-complete', done);
      step.subsection.dataset.mcqCompleted = done ? '1' : '0';
      updateSectionStatus(step);
    });
    updateRail();
    updateMobileTopbar(steps);
    maybeCelebrateAllComplete(steps, false);
  }

  function markStepComplete(step) {
    if (step.completed) return;
    step.completed = true;
    step.subsection.classList.add('lesson-subsection-complete');
    step.subsection.dataset.mcqCompleted = '1';
    updateSectionStatus(step);
    updateRail();
    updateMobileTopbar(steps, true);
    var finishing = !celebrated && steps.every(function (s) { return s.completed; });
    if (!finishing) {
      persistProgress(step);
      return;
    }
    // E11 Phase 0 (docs/BADGES_AND_CELEBRATIONS_PLAN.md 1.3.2): the last quick check saves at once, and the lesson stage waits for
    // the answer (at most 2.5 s), so it can name the lesson badge that save earns: one stage, not a lesson stage then a badge stage.
    var keys = completedKeys(steps);
    writeLocalProgress(keys);
    clearTimeout(saveTimer);
    finishingLive = true;
    var done = false;
    var finish = function (data) {
      if (done) return;
      done = true;
      maybeCelebrateAllComplete(steps, true, lessonBadge(data));
    };
    var saving = persistSnapshot(keys);
    if (!saving) { finish(null); return; }
    saving.then(finish, function () { finish(null); });
    setTimeout(function () { finish(null); }, 2500);
  }

  function wireMcqCompletion(step) {
    step.mcq.addEventListener('mcq-correct', function () {
      markStepComplete(step);
    });
  }

  steps.forEach(function (step) {
    wireMcqCompletion(step);

    var node = document.createElement('button');
    node.type = 'button';
    node.className = 'lesson-progress-rail-node';
    node.setAttribute('aria-label', 'Quick check ' + (step.index + 1));
    node.title = 'Jump to quick check ' + (step.index + 1);
    node.dataset.stepKey = step.key;
    node.addEventListener('click', function () {
      openSubsection(step.subsection);
      window.requestAnimationFrame(function () {
        var target = step.mcq;
        if (target && target.scrollIntoView) {
          var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          target.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
        }
        scheduleLayout();
      });
    });
    railInner.appendChild(node);
    step.nodeEl = node;
  });

  function highestCompletedIndex() {
    var highest = -1;
    steps.forEach(function (step, index) {
      if (step.completed) highest = index;
    });
    return highest;
  }

  function updateRail() {
    var contentHeight = contentRoot.offsetHeight;
    railInner.style.height = contentHeight + 'px';

    startTop = summaryTop(steps[0].subsection);
    startNode.style.top = startTop + 'px';

    var mcqPositions = steps.map(function (step) {
      return mcqTop(step);
    });

    var trackTop = startTop;
    var trackBottom = mcqPositions.length
      ? mcqPositions[mcqPositions.length - 1]
      : startTop;
    var trackHeight = Math.max(24, trackBottom - trackTop);
    var track = rail.querySelector('.lesson-progress-rail-track');
    track.style.top = trackTop + 'px';
    track.style.height = trackHeight + 'px';

    var highest = highestCompletedIndex();
    var fillEnd = startTop;
    if (highest >= 0) {
      fillEnd = Math.max(startTop, mcqPositions[highest]);
    }
    fillEl.style.height = Math.max(0, fillEnd - trackTop) + 'px';

    steps.forEach(function (step, index) {
      var node = step.nodeEl;
      node.style.top = mcqPositions[index] + 'px';
      node.classList.toggle('is-reached', step.completed);
      node.classList.toggle('is-current', index === highest && step.completed);
    });

    updateMobileTopbar(steps);
  }

  function scheduleLayout() {
    clearTimeout(layoutTimer);
    layoutTimer = setTimeout(updateRail, 50);
  }

  // resolves with the server's answer (its JSON, which carries any badges the save earned), or null; null straight away when
  // nothing is sent
  function persistSnapshot(keys) {
    if (!isLoggedIn || !csrfToken || !steps.length || !keys.length) return null;
    var lastKey = keys[keys.length - 1];
    var step = steps.filter(function (item) { return item.key === lastKey; })[0] || steps[0];
    return fetch('/api/lesson-progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        csrf_token: csrfToken,
        level: level,
        subject: subject,
        topic: topic,
        section_key: step.key,
        section_label: sectionLabel(step.subsection),
        completed_keys: keys,
        step_total: steps.length,
      }),
      credentials: 'same-origin',
    }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  }

  // the lesson's own badge in a save's answer (topic_completed:<level>:<subject>:<topic>), for the lesson stage to name
  function lessonBadge(data) {
    var want = 'topic_completed:' + lessonId;
    var list = (data && data.new_milestones) || [];
    for (var i = 0; i < list.length; i += 1) {
      var b = list[i];
      if (b && b.key === want) return { key: b.key, title: b.title || '' };
    }
    return null;
  }

  function persistProgress(step) {
    var keys = completedKeys(steps);
    writeLocalProgress(keys);

    if (!isLoggedIn || !csrfToken || !step) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
      persistSnapshot(keys);
    }, 400);
  }

  steps.forEach(function (step) {
    step.subsection.addEventListener('toggle', scheduleLayout);
  });

  window.addEventListener('resize', scheduleLayout);
  window.addEventListener('scroll', scheduleLayout, { passive: true });

  if (window.MathJax && MathJax.startup) {
    MathJax.startup.promise.then(scheduleLayout).catch(function () {});
  }

  applyCompletedKeys(readLocalProgress());

  if (isLoggedIn && level && subject && topic) {
    fetch(
      '/api/lesson-progress/' +
        encodeURIComponent(level) + '/' +
        encodeURIComponent(subject) + '/' +
        encodeURIComponent(topic),
      { credentials: 'same-origin' }
    )
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.ok) return;
        // E11 Phase 0: the local copy is this pupil's own now, so steps it has and the server lacks (answered offline, or a save
        // that failed) are saved even when the server holds nothing yet for this lesson; before, a lesson with no server row never
        // saved from here.
        var serverKeys = ((data.progress && data.progress.completed_keys) || []).map(normalizeStepKey);
        var localKeys = readLocalProgress();
        var merged = {};
        localKeys.concat(serverKeys).forEach(function (key) {
          if (key) merged[key] = true;
        });
        var keys = Object.keys(merged);
        writeLocalProgress(keys);
        applyCompletedKeys(keys);
        var missing = keys.some(function (key) { return serverKeys.indexOf(key) < 0; });
        if (!data.progress && !missing) return;
        persistSnapshot(keys);
      })
      .catch(function () {});
  }
})();
