(function () {
  'use strict';

  var openBtn = document.getElementById('nav-notif-open');
  var panel = document.getElementById('nav-notif-panel');
  var listEl = document.getElementById('nav-notif-list');
  var badge = document.getElementById('nav-notif-badge');
  var markAllBtn = document.getElementById('nav-notif-mark-all');
  var backdrop = document.getElementById('nav-notif-backdrop');
  var closeBtn = document.getElementById('nav-notif-close');
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

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function renderNotificationItem(item) {
    var cls = 'nav-notif-item' + (item.read ? '' : ' is-unread');
    var text = '<span class="nav-notif-item-text">' + escapeHtml(item.message) + '</span>';
    var time = '<span class="nav-notif-item-time">' + escapeHtml(timeAgo(item.created_at)) + '</span>';
    var actions = item.actions || [];
    if (
      item.type === 'study_pair_invite'
      && item.pair_id
      && actions.indexOf('accept') !== -1
      && actions.indexOf('ignore') !== -1
    ) {
      return (
        '<div class="' + cls + ' nav-notif-item-actionable" data-notif-id="' + item.id + '" data-pair-id="' + item.pair_id + '">' +
        text + time +
        '<div class="nav-notif-item-actions">' +
        '<button type="button" class="btn btn-primary btn-sm nav-notif-accept" data-action="accept">Accept</button>' +
        '<button type="button" class="btn btn-outline btn-sm nav-notif-ignore" data-action="ignore">Ignore</button>' +
        '</div></div>'
      );
    }
    var href = item.url || '#';
    return (
      '<a href="' + escapeHtml(href) + '" class="' + cls + '" data-notif-id="' + item.id + '">' +
      text + time +
      '</a>'
    );
  }

  function skeletonHtml() {
    if (window.pbSkeletonMarkup) return window.pbSkeletonMarkup('notif', 4);
    return '<p class="nav-notif-empty">Loading</p>';
  }

  function renderList(notifications) {
    if (!notifications.length) {
      listEl.innerHTML = '<p class="nav-notif-empty">No notifications yet.</p>';
      return;
    }
    listEl.innerHTML = notifications.map(renderNotificationItem).join('');
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
    if (window.matchMedia('(max-width: 640px)').matches) {
      document.body.classList.add('nav-notif-open');
      if (backdrop) backdrop.hidden = false;
    }
    listEl.innerHTML = skeletonHtml();
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
    document.body.classList.remove('nav-notif-open');
    if (backdrop) backdrop.hidden = true;
  }

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function markRead(id) {
    return fetch('/api/v1/me/notifications/read', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        'X-CSRF-Token': csrfToken(),
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
        'X-CSRF-Token': csrfToken(),
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

  function respondStudyPair(pairId, action) {
    var path = action === 'accept'
      ? '/api/v1/study-pairs/' + pairId + '/accept'
      : '/api/v1/study-pairs/' + pairId + '/decline';
    return fetch(path, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'X-CSRF-Token': csrfToken(),
      },
      credentials: 'same-origin',
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var err = new Error(data.error || 'Request failed');
          err.code = data.code;
          throw err;
        }
        return data;
      });
    });
  }

  function showToast(message, type, options) {
    if (typeof window.showAppToast === 'function') {
      window.showAppToast(message, type || 'success', options);
    }
  }

  function handleStudyPairAction(itemEl, action) {
    var pairId = parseInt(itemEl.getAttribute('data-pair-id'), 10);
    var notifId = parseInt(itemEl.getAttribute('data-notif-id'), 10);
    if (!pairId) return;

    var buttons = itemEl.querySelectorAll('button');
    buttons.forEach(function (btn) { btn.disabled = true; });

    respondStudyPair(pairId, action)
      .then(function () {
        if (notifId) return markRead(notifId);
      })
      .then(function () {
        if (action === 'accept') {
          showToast('Study buddy connected!', 'success', {
            linkUrl: '/profile#study-buddy',
            linkLabel: 'View buddy',
          });
        } else {
          showToast('Invite ignored.', 'success');
        }
        return fetchNotifications();
      })
      .then(function (data) {
        if (data) {
          formatBadge(data.unread_count || 0);
          renderList(data.notifications || []);
        }
      })
      .catch(function (err) {
        buttons.forEach(function (btn) { btn.disabled = false; });
        showToast(err.message || 'Could not update study buddy invite.', 'error');
        if (err.code === 'invite_not_pending' || err.code === 'pair_not_found') {
          fetchNotifications()
            .then(function (data) {
              formatBadge(data.unread_count || 0);
              renderList(data.notifications || []);
            })
            .catch(function () {});
        }
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

  if (closeBtn) {
    closeBtn.addEventListener('click', function (event) {
      event.stopPropagation();
      closePanel();
    });
  }

  if (backdrop) {
    backdrop.addEventListener('click', closePanel);
  }

  listEl.addEventListener('click', function (event) {
    var actionBtn = event.target.closest('[data-action]');
    if (actionBtn) {
      event.preventDefault();
      event.stopPropagation();
      var itemEl = actionBtn.closest('.nav-notif-item-actionable');
      if (!itemEl || actionBtn.disabled) return;
      handleStudyPairAction(itemEl, actionBtn.getAttribute('data-action'));
      return;
    }

    var link = event.target.closest('a.nav-notif-item');
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

  if (window.matchMedia) {
    window.matchMedia('(max-width: 640px)').addEventListener('change', function (event) {
      if (!isOpen) return;
      if (event.matches) {
        document.body.classList.add('nav-notif-open');
        if (backdrop) backdrop.hidden = false;
      } else {
        document.body.classList.remove('nav-notif-open');
        if (backdrop) backdrop.hidden = true;
      }
    });
  }

  pollTimer = window.setInterval(refreshBadge, 60000);
  window.addEventListener('beforeunload', function () {
    if (pollTimer) window.clearInterval(pollTimer);
  });
})();
