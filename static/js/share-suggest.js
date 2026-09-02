(function () {
  'use strict';

  var overlay = document.getElementById('share-suggest-overlay');
  var form = document.getElementById('share-suggest-form');
  if (!overlay || !form) return;

  var titleEl = document.getElementById('share-suggest-title');
  var submitBtn = document.getElementById('share-suggest-submit');
  var savedIdInput = document.getElementById('share-suggest-saved-id');
  var recipientWrap = document.querySelector('.share-suggest-recipient');
  var recipientInput = document.getElementById('share-suggest-recipient');
  var suggestionsEl = document.getElementById('share-suggest-recipient-list');
  var visibilityWrap = form.querySelector('[name="visibility"]').closest('.form-group');
  var currentAction = 'share';
  var suggestTimer = null;
  var activeIndex = -1;
  var latestUsers = [];

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function normalizeQuery(value) {
    return (value || '').trim().replace(/^@+/, '').toLowerCase();
  }

  function closeSuggestions() {
    if (!suggestionsEl) return;
    suggestionsEl.hidden = true;
    suggestionsEl.innerHTML = '';
    activeIndex = -1;
    latestUsers = [];
    if (recipientInput) recipientInput.setAttribute('aria-expanded', 'false');
  }

  function renderSuggestions(users, message) {
    if (!suggestionsEl) return;
    suggestionsEl.innerHTML = '';
    latestUsers = users || [];
    activeIndex = -1;

    if (!latestUsers.length) {
      var empty = document.createElement('li');
      empty.className = 'share-suggest-suggestion-empty';
      empty.textContent = message || 'No friends match that handle.';
      suggestionsEl.appendChild(empty);
      suggestionsEl.hidden = false;
      if (recipientInput) recipientInput.setAttribute('aria-expanded', 'true');
      return;
    }

    latestUsers.forEach(function (user, index) {
      var item = document.createElement('li');
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'share-suggest-suggestion';
      btn.setAttribute('role', 'option');
      btn.dataset.index = String(index);
      btn.innerHTML = '<span class="share-suggest-suggestion-handle">@' + escapeHtml(user.handle) + '</span>';
      btn.addEventListener('mousedown', function (event) {
        event.preventDefault();
        selectUser(user);
      });
      item.appendChild(btn);
      suggestionsEl.appendChild(item);
    });

    suggestionsEl.hidden = false;
    if (recipientInput) recipientInput.setAttribute('aria-expanded', 'true');
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function setActiveSuggestion(index) {
    if (!suggestionsEl) return;
    var buttons = suggestionsEl.querySelectorAll('.share-suggest-suggestion');
    buttons.forEach(function (btn, i) {
      btn.classList.toggle('is-active', i === index);
    });
    activeIndex = index;
    if (index >= 0 && buttons[index]) {
      buttons[index].scrollIntoView({ block: 'nearest' });
    }
  }

  function selectUser(user) {
    if (!recipientInput || !user) return;
    recipientInput.value = '@' + user.handle;
    closeSuggestions();
    recipientInput.focus();
  }

  function fetchFollowingSuggestions(query) {
    if (!query) {
      closeSuggestions();
      return;
    }

    fetch('/api/v1/me/following/search?q=' + encodeURIComponent(query) + '&limit=8', {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error(data.error || 'Search failed');
          return data;
        });
      })
      .then(function (data) {
        if (normalizeQuery(recipientInput.value) !== query) return;
        renderSuggestions(data.users || []);
      })
      .catch(function () {
        if (normalizeQuery(recipientInput.value) !== query) return;
        renderSuggestions([], 'Could not load friends. Try again.');
      });
  }

  function scheduleSuggestions() {
    if (!recipientInput || currentAction !== 'suggest') return;
    var query = normalizeQuery(recipientInput.value);
    window.clearTimeout(suggestTimer);
    if (!query) {
      closeSuggestions();
      return;
    }
    suggestTimer = window.setTimeout(function () {
      fetchFollowingSuggestions(query);
    }, 180);
  }

  function closeModal() {
    closeSuggestions();
    overlay.hidden = true;
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('site-search-open');
  }

  function openModal(action, savedId) {
    currentAction = action;
    savedIdInput.value = savedId || '';
    recipientInput.value = '';
    form.querySelector('[name="note"]').value = '';
    closeSuggestions();

    if (action === 'suggest') {
      titleEl.textContent = 'Send question to @user';
      submitBtn.textContent = 'Send';
      recipientWrap.hidden = false;
      recipientInput.required = true;
      visibilityWrap.hidden = true;
      form.action = '/suggestions';
    } else {
      titleEl.textContent = 'Share question';
      submitBtn.textContent = 'Share';
      recipientWrap.hidden = true;
      recipientInput.required = false;
      visibilityWrap.hidden = false;
      form.action = '/shared-questions/share';
    }

    overlay.hidden = false;
    overlay.setAttribute('aria-hidden', 'false');
    document.body.classList.add('site-search-open');
    (action === 'suggest' ? recipientInput : form.querySelector('[name="note"]')).focus();
  }

  if (recipientInput) {
    recipientInput.addEventListener('input', scheduleSuggestions);
    recipientInput.addEventListener('focus', scheduleSuggestions);
    recipientInput.addEventListener('blur', function () {
      window.setTimeout(closeSuggestions, 150);
    });
    recipientInput.addEventListener('keydown', function (event) {
      if (currentAction !== 'suggest' || suggestionsEl.hidden) return;

      var buttons = suggestionsEl.querySelectorAll('.share-suggest-suggestion');
      if (!buttons.length) return;

      if (event.key === 'ArrowDown') {
        event.preventDefault();
        var next = activeIndex + 1;
        if (next >= buttons.length) next = 0;
        setActiveSuggestion(next);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        var prev = activeIndex - 1;
        if (prev < 0) prev = buttons.length - 1;
        setActiveSuggestion(prev);
      } else if (event.key === 'Enter' && activeIndex >= 0) {
        event.preventDefault();
        selectUser(latestUsers[activeIndex]);
      } else if (event.key === 'Escape') {
        closeSuggestions();
      }
    });
  }

  document.addEventListener('click', function (event) {
    var btn = event.target.closest('.share-suggest-open');
    if (!btn) return;
    event.preventDefault();
    openModal(btn.getAttribute('data-action') || 'share', btn.getAttribute('data-saved-id') || '');
  });

  overlay.addEventListener('click', function (event) {
    if (event.target.closest('[data-close-share]')) closeModal();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !overlay.hidden) closeModal();
  });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    submitBtn.disabled = true;
    var body = new FormData(form);
    if (!body.get('csrf_token')) body.set('csrf_token', csrfToken());
    if (currentAction === 'suggest') {
      var handle = normalizeQuery(body.get('recipient_handle') || '');
      body.set('recipient_handle', handle);
    }

    fetch(form.action, {
      method: 'POST',
      body: body,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        Accept: 'application/json',
      },
      credentials: 'same-origin',
    })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error(data.error || 'Request failed');
          return data;
        });
      })
      .then(function (data) {
        closeModal();
        if (window.showAppToast) {
          window.showAppToast(data.message || 'Done.', 'success', data.share_url ? {
            linkUrl: data.share_url,
            linkLabel: 'View share',
          } : null);
        }
      })
      .catch(function (err) {
        if (window.showAppToast) {
          window.showAppToast(err.message || 'Something went wrong.', 'error');
        }
      })
      .finally(function () {
        submitBtn.disabled = false;
      });
  });

  document.querySelectorAll('.share-quiz-form').forEach(function (quizForm) {
    quizForm.addEventListener('submit', function (event) {
      event.preventDefault();
      var button = quizForm.querySelector('button[type="submit"]');
      if (button) button.disabled = true;
      fetch(quizForm.action, {
        method: 'POST',
        body: new FormData(quizForm),
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json',
        },
        credentials: 'same-origin',
      })
        .then(function (response) {
          return response.json().then(function (data) {
            if (!response.ok) throw new Error(data.error || 'Request failed');
            return data;
          });
        })
        .then(function (data) {
          if (window.showAppToast) window.showAppToast(data.message || 'Shared.', 'success');
        })
        .catch(function (err) {
          if (window.showAppToast) window.showAppToast(err.message || 'Could not share.', 'error');
        })
        .finally(function () {
          if (button) button.disabled = false;
        });
    });
  });
})();
