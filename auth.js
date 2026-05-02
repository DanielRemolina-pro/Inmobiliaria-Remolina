// ═══════════════════════════════════════════════════════════════
//  auth.js  —  Autenticación usando la API Django (session-based)
//  Endpoints:  /api/auth/csrf/  /api/auth/login/  /api/auth/registro/
//              /api/auth/logout/  /api/auth/me/
// ═══════════════════════════════════════════════════════════════

const API = 'http://127.0.0.1:8000/api/auth';

// ── Obtener CSRF token (desde cookie o endpoint auxiliar) ─────────────────
async function getCsrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  if (m) return m[1];
  const r = await fetch(`${API}/csrf/`, { credentials: 'include' });
  return (await r.json()).csrfToken;
}

async function postJson(url, body) {
  const csrf = await getCsrfToken();
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
    credentials: 'include',
    body: JSON.stringify(body),
  });
}

const authTabs        = document.querySelectorAll('.auth-tab');
const loginForm       = document.getElementById('login-form');
const registerForm    = document.getElementById('register-form');
const loginMessage    = document.getElementById('login-message');
const registerMessage = document.getElementById('register-message');
const userWelcome     = document.getElementById('user-welcome');
const userNameSpan    = document.getElementById('user-name');
const logoutButton    = document.getElementById('logout-button');



function showMessage(el, text, ok = false) {
  el.textContent = text;
  el.style.color = ok ? '#0b6623' : '#d8000c';
}

function switchTab(targetId) {
  authTabs.forEach(tab => {
    const target = tab.dataset.target;
    const form   = document.getElementById(target);
    if (target === targetId) {
      tab.classList.add('active'); form.classList.add('active'); form.classList.remove('oculto');
    } else {
      tab.classList.remove('active'); form.classList.remove('active'); form.classList.add('oculto');
    }
  });
}

function mostrarBienvenida(usuario) {
  userNameSpan.textContent = usuario.first_name || usuario.username || usuario.email;
  userWelcome.classList.remove('oculto');
  loginForm.classList.add('oculto');
  registerForm.classList.add('oculto');
  authTabs.forEach(tab => (tab.disabled = true));
}

authTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    switchTab(tab.dataset.target);
    loginMessage.textContent = ''; registerMessage.textContent = '';
  });
});




loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginMessage.textContent = '';
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  try {
    const res = await postJson(`${API}/login/`, { email, password });
    const data = await res.json();
    if (!res.ok) { showMessage(loginMessage, data.error || 'Error de acceso.'); return; }
    showMessage(loginMessage, data.mensaje || '¡Bienvenido!', true);
    mostrarBienvenida(data.usuario);
    setTimeout(() => { window.location.href = 'index.html'; }, 1200);
  } catch { showMessage(loginMessage, 'Error de conexión con el servidor.'); }
});

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  registerMessage.textContent = '';
  const nombre   = document.getElementById('register-name').value.trim();
  const email    = document.getElementById('register-email').value.trim();
  const password = document.getElementById('register-password').value;
  if (password.length < 6) { showMessage(registerMessage, 'La contraseña debe tener al menos 6 caracteres.'); return; }
  try {
    const res = await postJson(`${API}/registro/`, { nombre, email, password });
    const data = await res.json();
    if (!res.ok) {
      const errMsg = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Error al registrarse.';
      showMessage(registerMessage, errMsg); return;
    }
    showMessage(registerMessage, data.mensaje || 'Cuenta creada. Bienvenido.', true);
    mostrarBienvenida(data.usuario);
    registerForm.reset();
    setTimeout(() => { window.location.href = 'index.html'; }, 1200);
  } catch { showMessage(registerMessage, 'Error de conexión con el servidor.'); }
});

logoutButton?.addEventListener('click', async () => {
  try {
    await postJson(`${API}/logout/`, {});
    userWelcome.classList.add('oculto');
    loginForm.classList.remove('oculto');
    registerForm.classList.remove('oculto');
    authTabs.forEach(tab => (tab.disabled = false));
    switchTab('login-form');
  } catch { console.error('Error al cerrar sesión.'); }
});

(async () => {
  try {
    const res = await fetch(`${API}/me/`, { credentials: 'include' });
    if (res.ok) { mostrarBienvenida(await res.json()); }
    else { switchTab('login-form'); }
  } catch { switchTab('login-form'); }
})();