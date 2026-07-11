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
  var visibilityWrap = form.querySelector('[name="visibility"]').closest('.form-group');
  var currentAction = 'share';

  function csrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function closeModal() {
    overlay.hidden = true;
    overlay.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('site-search-open');
  }

  function openModal(action, savedId) {
    currentAction = action;
    savedIdInput.value = savedId || '';
    recipientInput.value = '';
    form.querySelector('[name="note"]').value = '';

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
