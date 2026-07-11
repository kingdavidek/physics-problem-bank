(function () {
  'use strict';

  var openBtn = document.getElementById('nav-notif-open');
  var panel = document.getElementById('nav-notif-panel');
  var listEl = document.getElementById('nav-notif-list');
  var badge = document.getElementById('nav-notif-badge');
  var markAllBtn = document.getElementById('nav-notif-mark-all');
  if (!openBtn || !panel || !listEl || !badge) return;

  var isOpen = false;
  var pollTimer = null;

  function formatBadge(count) {
    if (!count || count <= 0) {
      badge.hidden = true;
      badge.textContent = '';
      return;
    }
    badge.hidden = false;
    badge.textContent = count > 9 ? '9+' : String(count);
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

  function renderList(notifications) {
    if (!notifications.length) {
      listEl.innerHTML = '<p class="nav-notif-empty">No notifications yet.</p>';
      return;
    }
    listEl.innerHTML = notifications.map(function (item) {
      var cls = 'nav-notif-item' + (item.read ? '' : ' is-unread');
      return (
        '<a href="' + item.url + '" class="' + cls + '" data-notif-id="' + item.id + '">' +
        '<span class="nav-notif-item-text">' + escapeHtml(item.message) + '</span>' +
        '<span class="nav-notif-item-time">' + escapeHtml(timeAgo(item.created_at)) + '</span>' +
        '</a>'
      );
    }).join('');
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fetchNotifications() {
    return fetch('/api/v1/me/notifications?limit=20', {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) throw new Error(data.error || 'Failed to load notifications');
        return data;
      });
    });
  }

  function refreshBadge() {
    return fetchNotifications()
      .then(function (data) {
        formatBadge(data.unread_count || 0);
        if (isOpen) renderList(data.notifications || []);
      })
      .catch(function () {});
  }

  function openPanel() {
    isOpen = true;
    panel.hidden = false;
    openBtn.setAttribute('aria-expanded', 'true');
    listEl.innerHTML = '<p class="nav-notif-empty">Loading…</p>';
    fetchNotifications()
      .then(function (data) {
        formatBadge(data.unread_count || 0);
        renderList(data.notifications || []);
      })
      .catch(function () {
        listEl.innerHTML = '<p class="nav-notif-empty">Could not load notifications.</p>';
      });
  }

  function closePanel() {
    isOpen = false;
    panel.hidden = true;
    openBtn.setAttribute('aria-expanded', 'false');
  }

  function markRead(id) {
    return fetch('/api/v1/me/notifications/read', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify({ id: id }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) throw new Error(data.error || 'Failed');
        formatBadge(data.unread_count || 0);
        return data;
      });
    });
  }

  function markAllRead() {
    return fetch('/api/v1/me/notifications/read', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      credentials: 'same-origin',
      body: JSON.stringify({ all: true }),
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) throw new Error(data.error || 'Failed');
        formatBadge(data.unread_count || 0);
        return fetchNotifications();
      });
    }).then(function (data) {
      if (data) renderList(data.notifications || []);
    });
  }

  openBtn.addEventListener('click', function (event) {
    event.stopPropagation();
    if (isOpen) closePanel();
    else openPanel();
  });

  if (markAllBtn) {
    markAllBtn.addEventListener('click', function (event) {
      event.preventDefault();
      event.stopPropagation();
      markAllRead().catch(function () {});
    });
  }

  listEl.addEventListener('click', function (event) {
    var link = event.target.closest('.nav-notif-item');
    if (!link) return;
    var id = link.getAttribute('data-notif-id');
    if (id && link.classList.contains('is-unread')) {
      markRead(parseInt(id, 10)).catch(function () {});
    }
  });

  document.addEventListener('click', function (event) {
    if (!isOpen) return;
    if (event.target.closest('.nav-notif-wrap')) return;
    closePanel();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && isOpen) closePanel();
  });

  pollTimer = window.setInterval(refreshBadge, 60000);
  window.addEventListener('beforeunload', function () {
    if (pollTimer) window.clearInterval(pollTimer);
  });
})();
