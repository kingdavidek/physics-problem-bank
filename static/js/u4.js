/**
 * Phase U4 — page chrome: profile tabs, topics level filter, practice picker labels.
 */
(function () {
  'use strict';

  var TAB_HASH = {
    overview: 'overview',
    progress: 'progress',
    social: 'social',
    history: 'history',
    milestones: 'progress',
    'revision-plan': 'progress',
    reflections: 'progress',
    'study-buddy': 'overview',
  };

  function initProfileTabs() {
    var nav = document.querySelector('.profile-tabs');
    if (!nav) return;

    var buttons = nav.querySelectorAll('[role="tab"]');
    var panels = document.querySelectorAll('[data-profile-tab]');
    if (!buttons.length || !panels.length) return;

    function setTab(name, pushHash) {
      var tab = TAB_HASH[name] || name;
      if (!['overview', 'progress', 'social', 'history'].includes(tab)) {
        tab = 'overview';
      }

      buttons.forEach(function (btn) {
        var active = btn.dataset.tab === tab;
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
        btn.classList.toggle('is-active', active);
      });

      panels.forEach(function (panel) {
        var show = panel.dataset.profileTab === tab;
        panel.hidden = !show;
        panel.classList.toggle('is-active', show);
      });

      if (pushHash !== false) {
        var hash = tab === 'overview' ? '#overview' : '#' + tab;
        if (window.location.hash !== hash) {
          history.replaceState(null, '', hash);
        }
      }
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

  function initTopicsFilter() {
    var bar = document.querySelector('.topics-level-bar');
    if (!bar) return;

    var groups = document.querySelectorAll('.topic-group[data-level]');
    var buttons = bar.querySelectorAll('[data-level-filter]');

    function apply(level) {
      buttons.forEach(function (btn) {
        var active = btn.dataset.levelFilter === level;
        btn.classList.toggle('is-active', active);
        btn.setAttribute('aria-selected', active ? 'true' : 'false');
      });
      groups.forEach(function (group) {
        var show = level === 'all' || group.dataset.level === level;
        group.hidden = !show;
      });
    }

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        apply(btn.dataset.levelFilter);
      });
    });

    apply('all');
  }

  function labelForSelect(selectEl) {
    if (!selectEl) return '';
    var opt = selectEl.selectedOptions[0];
    return opt ? opt.textContent.trim() : '';
  }

  function initPracticePicker() {
    var card = document.querySelector('.practice-picker-card');
    if (!card) return;

    var levelSel = document.getElementById('level-select');
    var subjectSel = document.getElementById('subject-select');
    var topicSel = document.getElementById('topic-select');
    var modeSel = document.getElementById('mode-select');
    var diffSel = document.getElementById('difficulty');
    var drawer = card.querySelector('.practice-picker-drawer');
    var toggleBtn = card.querySelector('.practice-picker-edit');
    var pills = {
      level: card.querySelector('[data-picker="level"]'),
      subject: card.querySelector('[data-picker="subject"]'),
      topic: card.querySelector('[data-picker="topic"]'),
      mode: card.querySelector('[data-picker="mode"]'),
      difficulty: card.querySelector('[data-picker="difficulty"]'),
    };

    function openDrawer() {
      if (!drawer || !toggleBtn) return;
      drawer.hidden = false;
      toggleBtn.setAttribute('aria-expanded', 'true');
      toggleBtn.textContent = 'Hide options';
    }

    function syncPills() {
      Object.keys(pills).forEach(function (key) {
        var el = pills[key];
        var select = key === 'level' ? levelSel
          : key === 'subject' ? subjectSel
          : key === 'topic' ? topicSel
          : key === 'mode' ? modeSel
          : diffSel;
        if (el && select) {
          var label = labelForSelect(select);
          if (key === 'mode') label = label.replace(/^[^\w]+/, '').trim();
          el.textContent = label;
        }
      });
    }

    [levelSel, subjectSel, topicSel, modeSel, diffSel].forEach(function (sel) {
      if (sel) sel.addEventListener('change', syncPills);
    });

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        var drawer = card.querySelector('.practice-picker-drawer');
        if (!drawer) return;
        var open = drawer.hidden;
        if (open) {
          openDrawer();
        } else {
          drawer.hidden = true;
          toggleBtn.setAttribute('aria-expanded', 'false');
          toggleBtn.textContent = 'Change selection';
        }
      });
    }

    card.querySelectorAll('[data-open-picker]').forEach(function (pill) {
      pill.addEventListener('click', function () {
        openDrawer();
      });
    });

    syncPills();
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
    initPracticePicker();
    initCollapsibleLists();
    initSegmentedLinks();
  });
})();
