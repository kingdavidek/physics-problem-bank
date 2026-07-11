(function () {
  'use strict';

  var listEl = document.getElementById('feed-list');
  if (!listEl) return;

  var pollTimer = null;
  var currentFilter = listEl.getAttribute('data-feed-filter') || 'all';

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function timeAgo(iso) {
    if (!iso) return '';
    var then = new Date(iso);
    if (Number.isNaN(then.getTime())) return iso.slice(0, 10);
    var diffMs = Date.now() - then.getTime();
    var mins = Math.floor(diffMs / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return mins + 'm ago';
    var hours = Math.floor(mins / 60);
    if (hours < 24) return hours + 'h ago';
    var days = Math.floor(hours / 24);
    if (days < 7) return days + 'd ago';
    return iso.slice(0, 10);
  }

  function renderItems(items) {
    if (!items.length) {
      listEl.innerHTML =
        '<p class="profile-empty feed-empty">' +
        'Follow people to see their activity. ' +
        '<a href="/search">Search users</a> ' +
        'or browse <a href="/topics">topics</a>.' +
        '</p>';
      return;
    }

    var html = '<ul class="profile-list feed-list">';
    items.forEach(function (item) {
      html +=
        '<li class="profile-list-item feed-card" data-feed-id="' + item.id + '">' +
        '<div class="profile-list-main">' +
        '<span class="feed-card-badge feed-card-badge--' + escapeHtml(item.card_type) + '">' +
        escapeHtml(item.card_label) +
        '</span>' +
        '<a href="' + escapeHtml(item.url) + '">' + escapeHtml(item.message) + '</a>' +
        '<span class="profile-list-meta feed-card-time">' +
        escapeHtml(timeAgo(item.created_at)) +
        '</span>' +
        '</div></li>';
    });
    html += '</ul>';
    listEl.innerHTML = html;
  }

  function fetchFeed() {
    var url = '/api/v1/feed?filter=' + encodeURIComponent(currentFilter) + '&limit=50';
    return fetch(url, {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) throw new Error(data.error || 'Failed to load feed');
        return data;
      });
    });
  }

  function refreshFeed() {
    return fetchFeed()
      .then(function (data) {
        if (data.filter) currentFilter = data.filter;
        renderItems(data.items || []);
      })
      .catch(function () {});
  }

  document.querySelectorAll('.feed-filter-pill').forEach(function (pill) {
    pill.addEventListener('click', function () {
      currentFilter = pill.getAttribute('data-feed-filter') || 'all';
      listEl.setAttribute('data-feed-filter', currentFilter);
    });
  });

  document.querySelectorAll('.feed-card-time[data-created-at]').forEach(function (el) {
    var iso = el.getAttribute('data-created-at');
    if (iso) el.textContent = timeAgo(iso);
  });

  pollTimer = window.setInterval(refreshFeed, 60000);
  window.addEventListener('beforeunload', function () {
    if (pollTimer) window.clearInterval(pollTimer);
  });
})();
