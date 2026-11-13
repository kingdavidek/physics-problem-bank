document.addEventListener('DOMContentLoaded', function () {
  if (!window.pbSound) return;
  var input = document.querySelector('input[name="sound_enabled"]');
  if (input) {
    window.pbSound.setEnabled(input.checked);
    input.addEventListener('change', function () {
      window.pbSound.setEnabled(input.checked);
      if (input.checked) window.pbSound.preview();
    });
  }
  // docs/CELEBRATION_SOUNDS_PLAN.md 8: choosing On for Celebration sounds plays one sample, as the switch above does. The pupil's
  // own tap on the option is the only trigger; force is needed because the setting is saved only with the form.
  var group = document.getElementById('zorp-sound-group');
  if (group && window.pbSound.play) {
    group.addEventListener('change', function (e) {
      var t = e.target;
      if (t && t.name === 'zorp_sound' && t.value === 'celebrations' && t.checked) window.pbSound.play('stamp-gold', { force: true });
      else window.pbSound.stopAll();
    });
  }
});
