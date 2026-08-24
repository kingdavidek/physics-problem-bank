/**
 * Phase U4 — page chrome: profile tabs, topics level filter, collapsible lists.
 */
(function () {
  'use strict';

  function prefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function scrollBehavior() {
    return prefersReducedMotion() ? 'auto' : 'smooth';
  }

  var TAB_HASH = {
    overview: 'overview',
    progress: 'progress',
    social: 'social',
    history: 'history',
    milestones: 'progress',
    'revision-plan': 'progress',
    reflections: 'progress',
    'study-buddy': 'overview',
    'study-buddy-invite': 'overview',
  };

  var TAB_IDS = ['overview', 'progress', 'social', 'history'];

  function initProfileTabs() {
    var nav = document.querySelector('.profile-tabs');
    if (!nav) return;

    var buttons = nav.querySelectorAll('[role="tab"]');
    var stacks = document.querySelectorAll('.profile-tab-stack');
    if (!buttons.length || !stacks.length) return;

    function scrollToHashTarget() {
      var raw = (window.location.hash || '').replace(/^#/, '');
      if (!raw || TAB_IDS.indexOf(raw) !== -1) return;
      var el = document.getElementById(raw);
      if (el) {
        window.requestAnimationFrame(function () {
          el.scrollIntoView({ behavior: scrollBehavior(), block: 'start' });
        });
      }
    }

    function setTab(name, pushHash) {
      var tab = TAB_HASH[name] || name;
      if (TAB_IDS.indexOf(tab) === -1) {
        tab = 'overview';
      }

      buttons.forEach(function (btn) {
        var active = btn.dataset.tab === tab;
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
        btn.classList.toggle('is-active', active);
      });

      stacks.forEach(function (stack) {
        var show = stack.dataset.profileTab === tab;
        stack.hidden = !show;
        stack.classList.toggle('is-active', show);
      });

      if (pushHash !== false) {
        var hash = tab === 'overview' ? '#overview' : '#' + tab;
        if (window.location.hash !== hash) {
          history.replaceState(null, '', hash);
        }
      }

      scrollToHashTarget();
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        setTab(btn.dataset.tab, true);
      });
    });

    window.addEventListener('hashchange', function () {
      var raw = (window.location.hash || '#overview').replace(/^#/, '');
      setTab(raw, false);
    });

    var initial = (window.location.hash || '#overview').replace(/^#/, '');
    setTab(initial, false);
  }

  function levelFromHash(hash) {
    var level = 'all';
    if (hash === 'gcse' || hash === 'alevel' || hash === 'myp') {
      level = hash;
    } else if (hash.indexOf('topics-') === 0) {
      level = hash.split('-')[1] || 'all';
    }
    if (level === 'gcse' || level === 'alevel' || level === 'myp') return level;
    return 'all';
  }

  function initTopicsFilter() {
    var bar = document.querySelector('.topics-level-bar');
    if (!bar) return;

    var groups = document.querySelectorAll('.topic-group[data-level]');
    var buttons = bar.querySelectorAll('[data-level-filter]');

    function apply(level, persist) {
      buttons.forEach(function (btn) {
        var active = btn.dataset.levelFilter === level;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      groups.forEach(function (group) {
        var show = level === 'all' || group.dataset.level === level;
        group.hidden = !show;
      });
      if (persist === false) return;
      if (window.history && window.history.replaceState) {
        var next = window.location.pathname + window.location.search;
        if (level !== 'all') next += '#' + level;
        window.history.replaceState(null, '', next);
      }
    }

    function scrollToGroup(hash) {
      if (hash.indexOf('topics-') !== 0) return;
      var target = document.getElementById(hash);
      if (target && !target.hidden && target.scrollIntoView) {
        window.setTimeout(function () {
          target.scrollIntoView({ behavior: scrollBehavior(), block: 'start' });
        }, 0);
      }
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        apply(btn.dataset.levelFilter);
      });
    });

    window.addEventListener('hashchange', function () {
      var nextHash = (window.location.hash || '').replace(/^#/, '');
      apply(levelFromHash(nextHash), false);
      scrollToGroup(nextHash);
    });

    var hash = (window.location.hash || '').replace(/^#/, '');
    apply(levelFromHash(hash), false);
    scrollToGroup(hash);
  }

  function initCollapsibleLists() {
    document.querySelectorAll('[data-collapsible-list]').forEach(function (root) {
      var limit = parseInt(root.dataset.collapsibleList, 10) || 5;
      var items = root.querySelectorAll('[data-collapsible-item]');
      var btn = root.querySelector('[data-collapsible-toggle]');
      if (items.length <= limit || !btn) return;

      function setCollapsed(collapsed) {
        items.forEach(function (item, index) {
          if (index >= limit) item.hidden = collapsed;
        });
        btn.hidden = false;
        btn.textContent = collapsed
          ? 'Show ' + (items.length - limit) + ' more'
          : 'Show less';
        btn.dataset.collapsed = collapsed ? '1' : '0';
      }

      btn.addEventListener('click', function () {
        setCollapsed(btn.dataset.collapsed !== '0');
      });

      setCollapsed(true);
    });
  }

  function skeletonMarkup(kind, count) {
    var n = count || (kind === 'notif' ? 4 : 5);
    var html = '<div class="pb-skeleton pb-skeleton--' + (kind || 'list') +
      '" role="status" aria-busy="true" aria-live="polite">';
    html += '<span class="pb-skeleton-label">Loading</span>';
    var i;
    for (i = 0; i < n; i += 1) {
      html +=
        '<div class="pb-skeleton-row">' +
        '<span class="pb-skeleton-block pb-skeleton-block--avatar"></span>' +
        '<span class="pb-skeleton-lines">' +
        '<span class="pb-skeleton-block pb-skeleton-block--title"></span>' +
        '<span class="pb-skeleton-block pb-skeleton-block--meta"></span>' +
        '</span>';
      if (kind === 'leaderboard') {
        html += '<span class="pb-skeleton-block pb-skeleton-block--score"></span>';
      }
      html += '</div>';
    }
    html += '</div>';
    return html;
  }
  window.pbSkeletonMarkup = skeletonMarkup;

  function modifiedClick(event) {
    return event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button > 0;
  }

  function initSkeletonNav() {
    document.querySelectorAll('[data-skeleton-nav]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (modifiedClick(event)) return;
        var target = document.querySelector(link.getAttribute('data-skeleton-nav'));
        if (!target) return;
        var kind = link.getAttribute('data-skeleton-kind') || 'list';
        target.innerHTML = skeletonMarkup(kind);
      });
    });
  }

  function initSegmentedLinks() {
    document.querySelectorAll('.segmented-control--links').forEach(function (bar) {
      var path = window.location.pathname + window.location.search;
      bar.querySelectorAll('a').forEach(function (link) {
        var href = link.getAttribute('href') || '';
        if (path.indexOf(href.split('?')[0]) === 0 && link.search === window.location.search) {
          link.classList.add('is-active');
          link.setAttribute('aria-current', 'page');
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initProfileTabs();
    initTopicsFilter();
    initCollapsibleLists();
    initSegmentedLinks();
    initSkeletonNav();
  });
})();
