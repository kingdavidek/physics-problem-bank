(function () {
  'use strict';

  var overlay = document.getElementById('site-search-overlay');
  var openBtn = document.getElementById('site-search-open');
  var input = document.getElementById('site-search-input');
  var resultsEl = document.getElementById('site-search-results');
  if (!overlay || !openBtn || !input || !resultsEl) return;

  var debounceTimer = null;
  var activeController = null;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function openSearch() {
    overlay.hidden = false;
    overlay.setAttribute('aria-hidden', 'false');
    openBtn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('site-search-open');
    input.value = '';
    resultsEl.innerHTML = '';
    window.setTimeout(function () { input.focus(); }, 0);
  }

  function closeSearch() {
    overlay.hidden = true;
    overlay.setAttribute('aria-hidden', 'true');
    openBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('site-search-open');
    if (activeController) {
      activeController.abort();
      activeController = null;
    }
  }

  function renderEmpty(message) {
    resultsEl.innerHTML = '<p class="site-search-empty">' + escapeHtml(message) + '</p>';
  }

  function renderResults(data) {
    var topics = data.topics || [];
    var users = data.users || [];
    if (!topics.length && !users.length) {
      renderEmpty('No results for “' + data.query + '”.');
      return;
    }

    var html = '';
    if (topics.length) {
      html += '<section class="site-search-group"><h3>Topics &amp; lessons</h3><ul>';
      topics.forEach(function (item) {
        html += '<li><a href="' + escapeHtml(item.url) + '">';
        html += '<span class="site-search-title">' + escapeHtml(item.name) + '</span>';
        html += '<span class="site-search-meta">' + escapeHtml(item.group) + '</span>';
        html += '</a></li>';
      });
      html += '</ul></section>';
    }
    if (users.length) {
      html += '<section class="site-search-group"><h3>Users</h3><ul>';
      users.forEach(function (item) {
        var meta = item.profile_accessible
          ? (item.member_since ? 'Member since ' + item.member_since : 'Public profile')
          : 'Private profile';
        if (item.viewer_follows) meta += ' · Following';
        html += '<li><a href="' + escapeHtml(item.profile_url) + '">';
        html += '<span class="site-search-title">@' + escapeHtml(item.handle) + '</span>';
        html += '<span class="site-search-meta">' + escapeHtml(meta) + '</span>';
        html += '</a></li>';
      });
      html += '</ul></section>';
    }
    resultsEl.innerHTML = html;
  }

  function fetchResults(query) {
    if (activeController) activeController.abort();
    activeController = new AbortController();

    fetch('/api/v1/search?q=' + encodeURIComponent(query) + '&limit=6', {
      headers: { Accept: 'application/json' },
      signal: activeController.signal,
    })
      .then(function (response) {
        if (!response.ok) {
          return response.json().then(function (payload) {
            throw new Error((payload && payload.error) || 'Search failed');
          });
        }
        return response.json();
      })
      .then(renderResults)
      .catch(function (err) {
        if (err.name === 'AbortError') return;
        renderEmpty(err.message || 'Search failed.');
      });
  }

  function onInputChange() {
    var query = input.value.trim();
    window.clearTimeout(debounceTimer);
    if (query.length < 2) {
      resultsEl.innerHTML = '';
      return;
    }
    debounceTimer = window.setTimeout(function () {
      fetchResults(query);
    }, 220);
  }

  openBtn.addEventListener('click', openSearch);
  input.addEventListener('input', onInputChange);

  overlay.addEventListener('click', function (event) {
    if (event.target.closest('[data-close-search]')) closeSearch();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !overlay.hidden) {
      event.preventDefault();
      closeSearch();
      return;
    }
    if ((event.key === '/' || (event.key === 'k' && (event.metaKey || event.ctrlKey)))
        && overlay.hidden
        && !event.target.closest('input, textarea, select, [contenteditable="true"]')) {
      event.preventDefault();
      openSearch();
    }
  });
})();
