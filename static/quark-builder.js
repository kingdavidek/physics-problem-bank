const quarkData = {
  proton:   { quarks: ['u (⅔)', 'u (⅔)', 'd (-⅓)'], charge: '+1', colors: ['#d19900','#d19900','#5c79ff'] },
  neutron:  { quarks: ['u (⅔)', 'd (-⅓)', 'd (-⅓)'], charge: '0',  colors: ['#d19900','#5c79ff','#5c79ff'] },
  piplus:   { quarks: ['u (⅔)', 'anti-d (⅓)'],           charge: '+1', colors: ['#d19900','#5c79ff'] },
  piminus:  { quarks: ['d (-⅓)', 'anti-u (-⅔)'],         charge: '-1', colors: ['#5c79ff','#d19900'] },
  kplus:    { quarks: ['u (⅔)', 'anti-s (⅓)'],           charge: '+1', colors: ['#d19900','#8b4513'] },
  kminus:   { quarks: ['s (-⅓)', 'anti-u (-⅔)'],         charge: '-1', colors: ['#8b4513','#d19900'] }
};

function updateQuarkDisplay() {
  const sel = document.getElementById('particle-select').value;
  const data = quarkData[sel];
  const display = document.getElementById('quark-display');
  const chargeDisplay = document.getElementById('charge-display');
  display.innerHTML = data.quarks.map((q, i) =>
    `<div style="padding: 8px 14px; border-radius: 20px; background: ${data.colors[i]}; color: white;">${q}</div>`
  ).join('');
  chargeDisplay.textContent = 'Total charge: ' + data.charge;
}

document.addEventListener('DOMContentLoaded', function() {
  const sel = document.getElementById('particle-select');
  if (sel) {
    sel.addEventListener('change', updateQuarkDisplay);
    updateQuarkDisplay();   // show the first one
  }
});