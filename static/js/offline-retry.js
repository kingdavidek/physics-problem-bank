document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('offline-retry');
  if (!btn) return;
  btn.addEventListener('click', function (event) {
    if (!navigator.onLine) {
      event.preventDefault();
      window.location.reload();
    }
  });
});
