function syncAceptarButtonState(isChecked) {
  const button = document.getElementById('btnAceptar');
  button.disabled = !isChecked;
  button.style.opacity = isChecked ? '1' : '0.4';
  button.style.cursor = isChecked ? 'pointer' : 'not-allowed';
}

function aceptarTerminos() {
  localStorage.setItem('terminosAceptados', 'si');
  document.getElementById('terminosOverlay').style.display = 'none';
  document.body.style.overflow = '';
}

function rechazarTerminos() {
  document.getElementById('terminosOverlay').style.display = 'none';
  document.getElementById('bloqueado').style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function volverATerminos() {
  document.getElementById('bloqueado').style.display = 'none';
  document.getElementById('terminosOverlay').style.display = 'flex';
  document.getElementById('checkTerminos').checked = false;
  syncAceptarButtonState(false);
}

window.aceptarTerminos = aceptarTerminos;
window.rechazarTerminos = rechazarTerminos;
window.volverATerminos = volverATerminos;

if (localStorage.getItem('terminosAceptados') === 'si') {
  document.getElementById('terminosOverlay').style.display = 'none';
} else {
  document.body.style.overflow = 'hidden';
}

document.getElementById('checkTerminos').addEventListener('change', function () {
  syncAceptarButtonState(this.checked);
});