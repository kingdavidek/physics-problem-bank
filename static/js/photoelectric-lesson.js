document.addEventListener('DOMContentLoaded', function () {
  function updateCalc() {
    var metalSelect = document.getElementById('metal-select');
    var freqSlider = document.getElementById('freq-slider');
    var freqDisplay = document.getElementById('freq-display');
    var keResult = document.getElementById('ke-result');
    if (!metalSelect || !freqSlider || !freqDisplay || !keResult) return;

    var phiEv = parseFloat(metalSelect.value);
    var f = parseFloat(freqSlider.value) * 1e14;
    var h = 6.63e-34;
    var e = 1.60e-19;
    var photonEnergyJ = h * f;
    var photonEnergyEv = photonEnergyJ / e;
    var keEv = photonEnergyEv - phiEv;

    freqDisplay.textContent = freqSlider.value;
    if (keEv < 0) {
      keResult.textContent = 'no emission (below threshold)';
      keResult.style.color = 'var(--color-text-muted)';
    } else {
      keResult.textContent = keEv.toFixed(2) + ' eV';
      keResult.style.color = 'var(--color-text)';
    }
  }

  function showTransition(label, deltaEv, element) {
    var h = 6.63e-34;
    var c = 3.00e8;
    var e = 1.60e-19;
    var deltaJ = deltaEv * e;
    var wavelength = (h * c) / deltaJ;
    var info = document.getElementById('transition-info');
    if (!info) return;
    info.textContent = label + ': ΔE = ' + deltaEv.toFixed(2) + ' eV, λ ≈ ' + (wavelength * 1e9).toFixed(0) + ' nm';
    if (deltaEv >= 1.6 && deltaEv <= 3.2) {
      info.style.color = '#35a16b';
      info.textContent += ' (visible)';
    } else {
      info.style.color = '#a13544';
    }
    element.style.stroke = '#ff4500';
    window.setTimeout(function () {
      element.style.stroke = deltaEv <= 3.2 ? '#35a16b' : '#d19900';
    }, 300);
  }

  var metalSelect = document.getElementById('metal-select');
  var freqSlider = document.getElementById('freq-slider');
  if (metalSelect) metalSelect.addEventListener('input', updateCalc);
  if (metalSelect) metalSelect.addEventListener('change', updateCalc);
  if (freqSlider) freqSlider.addEventListener('input', updateCalc);
  document.querySelectorAll('[data-transition-label]').forEach(function (el) {
    el.style.cursor = 'pointer';
    el.addEventListener('click', function () {
      showTransition(
        el.getAttribute('data-transition-label'),
        parseFloat(el.getAttribute('data-transition-delta')),
        el,
      );
    });
  });
  updateCalc();
});
