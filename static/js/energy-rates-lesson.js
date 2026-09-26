document.addEventListener('DOMContentLoaded', function () {
  function updateCalc() {
    var mass = document.getElementById('mass-slider');
    var temp = document.getElementById('temp-slider');
    if (!mass || !temp) return;
    var m = mass.value;
    var dT = temp.value;
    var q = m * 4.18 * dT;
    var massVal = document.getElementById('mass-val');
    var tempVal = document.getElementById('temp-val');
    var result = document.getElementById('q-result');
    if (massVal) massVal.textContent = m;
    if (tempVal) tempVal.textContent = dT;
    if (result) result.textContent = Math.round(q);
  }
  ['mass-slider', 'temp-slider'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', updateCalc);
      el.addEventListener('change', updateCalc);
    }
  });
  updateCalc();
});
