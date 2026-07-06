const API_AUTH = window.APP_CONFIG.authApi;
const API_PROP = window.APP_CONFIG.propiedadesApi;
const API_FAV = window.APP_CONFIG.favoritosApi;
const API_CONTACT = window.APP_CONFIG.apiBase;

function showToast(msg, type = '') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.getElementById('toastContainer').appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

async function getCsrfToken() {
  if (window.__csrfToken) return window.__csrfToken;
  const response = await fetch(`${API_AUTH}/csrf/`, { credentials: 'include' });
  const data = await response.json();
  window.__csrfToken = data.csrfToken;
  return window.__csrfToken;
}

async function postJson(url, body) {
  const csrf = await getCsrfToken();
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf,
    },
    credentials: 'include',
    body: JSON.stringify(body),
  });
}

function formatPrice(price) {
  if (!price) return 'Consultar precio';
  return '$ ' + Number(price).toLocaleString('es-CO');
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeMediaUrl(value) {
  if (!value) return 'assets/media/videos/dani.png';
  try {
    const url = new URL(value, window.location.origin);
    if (['http:', 'https:'].includes(url.protocol)) return url.href;
  } catch {
    return 'assets/media/videos/dani.png';
  }
  return 'assets/media/videos/dani.png';
}

function getBadgeClass(estado) {
  return { disponible: 'disponible', vendido: 'vendido', reservado: 'reservado' }[estado] || 'disponible';
}

function capitalize(value) {
  return value ? value.charAt(0).toUpperCase() + value.slice(1) : '';
}

let currentUser = null;
let favIds = new Set();

async function initAuth() {
  try {
    const res = await fetch(`${API_AUTH}/me/`, { credentials: 'include' });
    if (res.ok) {
      currentUser = await res.json();
      document.getElementById('navUserName').textContent =
        currentUser.first_name || currentUser.username;
      document.getElementById('navUser').classList.remove('oculto');
      document.getElementById('navLoginBtn').classList.add('oculto');

      try {
        const favRes = await fetch(`${API_FAV}/ids/`, { credentials: 'include' });
        if (favRes.ok) {
          const data = await favRes.json();
          favIds = new Set(data.ids.map(String));
        }
      } catch {
        favIds = new Set();
      }
    } else {
      document.getElementById('navUser').classList.add('oculto');
      document.getElementById('navLoginBtn').classList.remove('oculto');
    }
  } catch {
    document.getElementById('navUser').classList.add('oculto');
    document.getElementById('navLoginBtn').classList.remove('oculto');
  }
}

async function toggleFav(propId, btn) {
  if (!currentUser) {
    showToast('Inicia sesión para guardar favoritos');
    setTimeout(() => { window.location.href = 'login.html'; }, 1200);
    return;
  }

  btn.disabled = true;

  try {
    const csrf = await getCsrfToken();
    const res = await fetch(`${API_FAV}/toggle/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ propiedad_id: propId }),
    });

    if (res.ok || res.status === 201) {
      const data = await res.json();
      if (data.action === 'added') {
        favIds.add(String(propId));
        btn.textContent = '♥';
        btn.classList.add('active');
        showToast('❤ Guardado en favoritos', 'success');
      } else {
        favIds.delete(String(propId));
        btn.textContent = '♡';
        btn.classList.remove('active');
        showToast('Eliminado de favoritos');
      }
    } else {
      showToast('No se pudo actualizar favorito', 'error');
    }
  } catch {
    showToast('Error de conexión', 'error');
  } finally {
    btn.disabled = false;
  }
}

function buildCard(propiedad, delay = 0) {
  const img = safeMediaUrl(propiedad.imagen_display || 'assets/media/videos/dani.png');
  const isFav = favIds.has(String(propiedad.id));
  const safeTitle = escapeHtml(propiedad.titulo || 'Propiedad');
  const safeTipo = escapeHtml(propiedad.tipo ? capitalize(propiedad.tipo) : 'Inmueble');
  const safeCiudad = escapeHtml(propiedad.ciudad || 'Ibagué, Tolima');
  const safeEstado = escapeHtml(capitalize(propiedad.estado || 'disponible'));

  const features = [
    propiedad.habitaciones ? `${propiedad.habitaciones} 🛏` : null,
    propiedad.banos ? `${propiedad.banos} 🛁` : null,
    propiedad.area ? `${propiedad.area} m²` : null,
  ].filter(Boolean).map(escapeHtml);

  const card = document.createElement('div');
  card.className = 'propiedad-card reveal';
  card.style.transitionDelay = `${delay}s`;
  card.innerHTML = `
    <div class="card-img-wrap">
      <img src="${img}" alt="${safeTitle}" loading="lazy"
           onerror="this.src='assets/media/videos/dani.png'">
      <span class="card-badge ${getBadgeClass(propiedad.estado)}">
        ${safeEstado}
      </span>
      <button class="card-fav ${isFav ? 'active' : ''}" data-id="${propiedad.id}" title="Guardar en favoritos">
        ${isFav ? '♥' : '♡'}
      </button>
    </div>
    <div class="card-body">
      <div class="card-type">
        ${safeTipo}
      </div>
      <h3 class="card-title">${safeTitle}</h3>
      <div class="card-location">📍 ${safeCiudad}</div>
      <div class="card-price">${formatPrice(propiedad.precio)}</div>
      ${features.length
        ? `<div class="card-features">${features.map(feature => `<span>${feature}</span>`).join('')}</div>`
        : ''}
      <div class="card-actions">
        <a href="detalle.html?id=${propiedad.id}" class="btn btn-sm btn-primary">Ver detalle</a>
        <a href="#contacto" class="btn btn-sm btn-ghost-dark">Contacto</a>
      </div>
    </div>`;

  card.querySelector('.card-fav').addEventListener('click', (event) => {
    toggleFav(propiedad.id, event.currentTarget);
  });

  return card;
}

async function loadDestacadas() {
  try {
    const res = await fetch(`${API_PROP}/destacadas/`, { credentials: 'include' });
    if (!res.ok) throw new Error('API error');
    const data = await res.json();

    const skeleton = document.getElementById('propsSkeleton');
    const grid = document.getElementById('propsGrid');

    skeleton.style.display = 'none';

    if (!data.length) {
      document.getElementById('propsError').style.display = 'block';
      return;
    }

    data.slice(0, 4).forEach((propiedad, index) => grid.appendChild(buildCard(propiedad, index * 0.1)));
    grid.style.display = '';

    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.1 });
    document.querySelectorAll('#propsGrid .reveal').forEach(element => obs.observe(element));
  } catch {
    document.getElementById('propsSkeleton').style.display = 'none';
    document.getElementById('propsError').style.display = 'block';
  }
}

(async () => {
  await initAuth();
  await loadDestacadas();
})();

document.getElementById('navLogout')?.addEventListener('click', async (event) => {
  event.preventDefault();
  const csrf = await getCsrfToken();
  await fetch(`${API_AUTH}/logout/`, {
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
navbar.classList.add('scrolled');

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

const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add('visible');
  });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal:not(#propsGrid .reveal)').forEach(element => revealObs.observe(element));

document.getElementById('contactForm').addEventListener('submit', async (event) => {
  event.preventDefault();

  const form = event.target;
  const nombre = form.querySelector('input[type="text"]').value.trim();
  const email = form.querySelector('input[type="email"]').value.trim();
  const telefono = form.querySelector('input[type="tel"]').value.trim();
  const mensaje = form.querySelector('textarea').value.trim();

  try {
    const url = `${API_CONTACT}/contacto/`;
    console.log('Enviando contacto a:', url);
    const res = await postJson(url, { nombre, email, telefono, mensaje });
    if (!res.ok) {
      const responseText = await res.text();
      console.error('Error al enviar mensaje de contacto:', res.status, responseText);
      showToast('No se pudo enviar el mensaje. Revisa la consola.', 'error');
      return;
    }

    document.getElementById('formSuccess').classList.add('show');
    form.reset();
    showToast('Mensaje enviado correctamente.', 'success');
    setTimeout(() => document.getElementById('formSuccess').classList.remove('show'), 5000);
  } catch (error) {
    console.error('Error de conexión al enviar contacto:', error);
    showToast('Error de conexión. Intenta de nuevo.', 'error');
  }
});

function animateCount(element, target) {
  let current = 0;
  const step = Math.ceil(target / 60);
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    element.textContent = current + (element.dataset.suffix || '');
    if (current >= target) clearInterval(timer);
  }, 20);
}

async function loadPropiedadesCount() {
  try {
    const res = await fetch(`${API_PROP}/?limit=1`, { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      const total = data.count || 120;

      // Actualizar el texto en el hero
      const heroPropCount = document.getElementById('heroPropCount');
      if (heroPropCount) {
        heroPropCount.textContent = total;
      }

      // Animar el contador de estadísticas
      const statObs = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
          animateCount(document.getElementById('statProps'), total);
          statObs.disconnect();
        }
      });
      statObs.observe(document.getElementById('statProps'));
    }
  } catch (error) {
    console.error('Error loading propiedades count:', error);
  }
}

const statObs = new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) {
    loadPropiedadesCount();
    statObs.disconnect();
  }
});
statObs.observe(document.getElementById('statProps'));

document.querySelector('.hero-video-wrap video')?.addEventListener('error', () => {
  document.querySelector('.hero-video-wrap video').style.display = 'none';
});