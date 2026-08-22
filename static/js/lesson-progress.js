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
  var storageKey = 'lesson-progress:' + level + ':' + subject + ':' + topic;
  var celebrateKey = storageKey + ':celebrated';

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
    var candidates = root.querySelectorAll(
      '.page-shell, [style*="max-width:860px"], [style*="max-width: 860px"]'
    );
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

  function maybeCelebrateAllComplete(steps) {
    if (!steps.length || celebrated) return;
    var allDone = steps.every(function (step) { return step.completed; });
    if (!allDone) return;
    celebrated = true;
    try {
      window.localStorage.setItem(celebrateKey, '1');
    } catch (err) {}
    if (quizCtaBar) quizCtaBar.classList.add('is-complete');
    if (window.pbCelebrate && window.pbCelebrate.lessonComplete) {
      window.pbCelebrate.lessonComplete();
    }
  }

  function readCelebratedFlag() {
    try {
      return window.localStorage.getItem(celebrateKey) === '1';
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
  celebrated = readCelebratedFlag();
  if (celebrated && quizCtaBar) quizCtaBar.classList.add('is-complete');

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
    maybeCelebrateAllComplete(steps);
  }

  function markStepComplete(step) {
    if (step.completed) return;
    step.completed = true;
    step.subsection.classList.add('lesson-subsection-complete');
    step.subsection.dataset.mcqCompleted = '1';
    updateSectionStatus(step);
    updateRail();
    updateMobileTopbar(steps, true);
    persistProgress(step);
    maybeCelebrateAllComplete(steps);
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
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
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

  function persistSnapshot(keys) {
    if (!isLoggedIn || !csrfToken || !steps.length || !keys.length) return;
    var lastKey = keys[keys.length - 1];
    var step = steps.filter(function (item) { return item.key === lastKey; })[0] || steps[0];
    fetch('/api/lesson-progress', {
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
    }).catch(function () {});
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
        if (!data || !data.progress) return;
        var serverKeys = (data.progress.completed_keys || []).map(normalizeStepKey);
        var localKeys = readLocalProgress();
        var merged = {};
        localKeys.concat(serverKeys).forEach(function (key) {
          if (key) merged[key] = true;
        });
        var keys = Object.keys(merged);
        writeLocalProgress(keys);
        applyCompletedKeys(keys);
        persistSnapshot(keys);
      })
      .catch(function () {});
  }
})();
