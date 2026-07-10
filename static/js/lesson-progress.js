/**
 * Lesson progress rail — a subsection counts as complete only after its Quick Check
 * MCQ is answered correctly (mcq-correct event).
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

  var contentRoot;

  function findLessonContentRoot(root) {
    var candidates = root.querySelectorAll(
      '.page-shell, [style*="max-width:860px"], [style*="max-width: 860px"]'
    );
    if (candidates.length) return candidates[0];
    return root.firstElementChild || root;
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
    });
    updateRail();
  }

  contentRoot = findLessonContentRoot(wrapper);
  contentRoot.classList.add('lesson-progress-content');

  var steps = buildSteps(contentRoot);
  if (!steps.length) return;

  var shell = document.createElement('div');
  shell.className = 'lesson-progress-shell';
  contentRoot.parentNode.insertBefore(shell, contentRoot);
  shell.appendChild(contentRoot);

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

  function markStepComplete(step) {
    if (step.completed) return;
    step.completed = true;
    step.subsection.classList.add('lesson-subsection-complete');
    step.subsection.dataset.mcqCompleted = '1';
    updateRail();
    persistProgress(step);
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
  }

  function scheduleLayout() {
    clearTimeout(layoutTimer);
    layoutTimer = setTimeout(updateRail, 50);
  }

  function persistProgress(step) {
    var keys = completedKeys(steps);
    writeLocalProgress(keys);

    if (!isLoggedIn || !csrfToken || !step) return;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(function () {
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
        }),
        credentials: 'same-origin',
      }).catch(function () {});
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
  updateRail();

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
      })
      .catch(function () {});
  }
})();
