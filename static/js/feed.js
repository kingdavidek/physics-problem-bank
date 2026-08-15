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

  function renderAvatar(avatar, size) {
    var av = avatar || {};
    var face = escapeHtml(av.face || '🙂');
    var bg = escapeHtml(av.bg || '#eef6fc');
    var extra = av.extra ? escapeHtml(av.extra) : '';
    var sizeClass = size ? ' user-avatar--' + size : '';
    var html =
      '<span class="user-avatar' + sizeClass + '" style="background: ' + bg + ';" aria-hidden="true">' +
      '<span class="user-avatar-face">' + face + '</span>';
    if (extra) html += '<span class="user-avatar-extra">' + extra + '</span>';
    return html + '</span>';
  }

  function renderChallenge(challenge) {
    if (!challenge) return '';
    return (
      '<ul class="profile-list feed-list feed-challenge-list">' +
      '<li class="profile-list-item feed-card feed-card--bot" data-feed-id="' +
      escapeHtml(String(challenge.id)) +
      '">' +
      renderAvatar(challenge.avatar, 'sm') +
      '<div class="profile-list-main">' +
      '<span class="feed-card-badge feed-card-badge--' +
      escapeHtml(challenge.card_type || 'challenge') +
      '">' +
      escapeHtml(challenge.card_label || 'Daily challenge') +
      '</span>' +
      '<a href="' +
      escapeHtml(challenge.url || '/qotd') +
      '">' +
      escapeHtml(challenge.message || '') +
      '</a>' +
      '<span class="profile-list-meta">' +
      escapeHtml((challenge.detail || '') + ' · @' + (challenge.actor_handle || 'problem_bot')) +
      '</span>' +
      '<span class="feed-card-bot-note">' +
      escapeHtml(challenge.bot_note || 'A Problem Bank bot — not a person.') +
      '</span>' +
      '</div></li></ul>'
    );
  }

  function renderItems(items, challenge) {
    var html = renderChallenge(challenge);
    if (!items.length) {
      html +=
        '<p class="profile-empty feed-empty">' +
        'Follow people to see their activity. ' +
        '<a href="/search">Search users</a> ' +
        'or browse <a href="/topics">topics</a>.' +
        '</p>';
      listEl.innerHTML = html;
      return;
    }

    html += '<ul class="profile-list feed-list">';
    items.forEach(function (item) {
      html +=
        '<li class="profile-list-item feed-card" data-feed-id="' + item.id + '">' +
        renderAvatar(item.actor_avatar, 'sm') +
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
        renderItems(data.items || [], data.qotd_challenge || null);
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
