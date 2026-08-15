(function () {
  'use strict';

  var root = document.querySelector('[data-buddy-root]');
  if (!root) return;

  var messageEl = root.querySelector('[data-buddy-message]');
  var detailEl = root.querySelector('[data-buddy-detail]');
  var actionEl = root.querySelector('[data-buddy-action]');
  var dismissEl = root.querySelector('[data-buddy-dismiss]');
  if (!messageEl || !actionEl || !dismissEl) return;

  function utcDayKey() {
    return new Date().toISOString().slice(0, 10);
  }

  function storageKey() {
    return 'pb-buddy-dismissed-' + utcDayKey();
  }

  function escapeText(value) {
    var node = document.createElement('span');
    node.textContent = value == null ? '' : String(value);
    return node.textContent;
  }

  function show(prompt) {
    if (!prompt || !prompt.message) return;
    messageEl.textContent = escapeText(prompt.message);
    if (detailEl) detailEl.textContent = escapeText(prompt.detail || 'Buddy');
    actionEl.textContent = escapeText(prompt.action_label || 'Open');
    actionEl.setAttribute('href', prompt.action_url || '/topics');
    root.hidden = false;
  }

  dismissEl.addEventListener('click', function () {
    root.hidden = true;
    try {
      window.localStorage.setItem(storageKey(), '1');
    } catch (err) {}
  });

  try {
    if (window.localStorage.getItem(storageKey()) === '1') return;
  } catch (err) {}

  fetch('/api/v1/me/buddy', {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
  })
    .then(function (response) {
      if (!response.ok) return null;
      return response.json();
    })
    .then(function (data) {
      if (data && data.ok && data.buddy) show(data.buddy);
    })
    .catch(function () {});
})();
