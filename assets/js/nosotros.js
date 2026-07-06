const API = window.APP_CONFIG.authApi;
const API_PROP = window.APP_CONFIG.propiedadesApi;

async function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  if (match) return match[1];
  const response = await fetch(`${API}/csrf/`, { credentials: 'include' });
  return (await response.json()).csrfToken;
}

async function loadPropiedadesCount() {
  try {
    const response = await fetch(`${API_PROP}/?limit=1`, { credentials: 'include' });
    if (response.ok) {
      const data = await response.json();
      const total = data.count || 0;

      // Actualizar el contador en las cifras
      const propiedadesCount = document.getElementById('propiedadesCount');
      if (propiedadesCount) {
        propiedadesCount.textContent = `+${total}`;
      }

      // Actualizar el texto en el hero
      const heroPropCount = document.getElementById('nosotrosHeroPropCount');
      if (heroPropCount) {
        heroPropCount.textContent = total;
      }
    }
  } catch (error) {
    console.error('Error loading propiedades count:', error);
  }
}

(async () => {
  const navUser = document.getElementById('navUser');
  const navLoginBtn = document.getElementById('navLoginBtn');
  try {
    const res = await fetch(`${API}/me/`, { credentials: 'include' });
    if (res.ok) {
      const user = await res.json();
      document.getElementById('navUserName').textContent = user.first_name || user.username || user.email;
      navUser.classList.remove('oculto');
      navLoginBtn.classList.add('oculto');
    } else {
      navUser.classList.add('oculto');
      navLoginBtn.classList.remove('oculto');
    }
  } catch {
    navUser.classList.add('oculto');
    navLoginBtn.classList.remove('oculto');
  }

  loadPropiedadesCount();
})();

document.getElementById('navLogout')?.addEventListener('click', async (event) => {
  event.preventDefault();
  const csrf = await getCsrfToken();
  await fetch(`${API}/logout/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  window.location.reload();
});

const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 30);
});

document.getElementById('navHamburger').addEventListener('click', () => {
  document.getElementById('navMenu').classList.toggle('open');
});

const fabMain = document.getElementById('fab-main');
const fabItems = document.getElementById('fab-items');
fabMain.addEventListener('click', () => {
  fabItems.classList.toggle('oculto');
  fabMain.classList.toggle('open');
});
document.addEventListener('click', (event) => {
  if (!fabMain.contains(event.target) && !fabItems.contains(event.target)) {
    fabItems.classList.add('oculto');
    fabMain.classList.remove('open');
  }
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(element => observer.observe(element));