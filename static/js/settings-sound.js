document.addEventListener('DOMContentLoaded', function () {
  var input = document.querySelector('input[name="sound_enabled"]');
  if (!input || !window.pbSound) return;
  window.pbSound.setEnabled(input.checked);
  input.addEventListener('change', function () {
    window.pbSound.setEnabled(input.checked);
    if (input.checked) window.pbSound.preview();
  });
});
