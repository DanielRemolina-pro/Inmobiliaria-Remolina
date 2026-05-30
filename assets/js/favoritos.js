const API_AUTH = window.APP_CONFIG.authApi;
const API_FAV = window.APP_CONFIG.favoritosApi;

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

function formatPrecio(precio) {
  if (precio === null || precio === undefined) return 'Consultar precio';
  return '$ ' + Number(precio).toLocaleString('es-CO');
}

function formatArea(area) {
  if (!area) return '—';
  return area >= 10000 ? (area / 10000).toFixed(1) + ' ha' : area + ' m²';
}

function hideLoading() {
  document.getElementById('favsLoading').style.display = 'none';
}

function showSection(id) {
  document.getElementById(id).style.display = '';
}

async function quitarFavorito(propId, cardEl) {
  const btn = cardEl.querySelector('.btn-remove-fav');
  if (btn) btn.disabled = true;

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
      if (data.action === 'removed') {
        cardEl.style.transition = 'opacity 0.3s, transform 0.3s';
        cardEl.style.opacity = '0';
        cardEl.style.transform = 'scale(0.95)';
        setTimeout(() => {
          cardEl.remove();
          const grid = document.getElementById('favsGrid');
          const total = grid.querySelectorAll('.propiedad-card').length;
          document.getElementById('favCount').textContent = total;
          if (total === 0) {
            showSection('favsEmpty');
            document.getElementById('headerActions').style.display = 'none';
          }
        }, 300);
        showToast('Eliminado de favoritos');
      } else {
        showToast('Actualizado', 'success');
        if (btn) btn.disabled = false;
      }
    } else {
      showToast('No se pudo quitar el favorito', 'error');
      if (btn) btn.disabled = false;
    }
  } catch {
    showToast('Error de conexión', 'error');
    if (btn) btn.disabled = false;
  }
}

function buildFavCard(fav, delay = 0) {
  const propiedad = fav.propiedad || fav;
  const img = propiedad.imagen_display || propiedad.imagen_url || 'assets/media/videos/dani.png';

  const features = [
    propiedad.habitaciones ? `${propiedad.habitaciones} 🛏` : null,
    propiedad.banos ? `${propiedad.banos} 🛁` : null,
    propiedad.area ? formatArea(propiedad.area) : null,
  ].filter(Boolean);

  const card = document.createElement('div');
  card.className = 'propiedad-card reveal';
  card.style.transitionDelay = `${delay}s`;

  card.innerHTML = `
    <div class="card-img-wrap">
      <img src="${img}" alt="${propiedad.titulo}" loading="lazy"
           onerror="this.src='assets/media/videos/dani.png'">
      <span class="card-badge ${propiedad.estado || 'disponible'}">
        ${propiedad.estado ? propiedad.estado.charAt(0).toUpperCase() + propiedad.estado.slice(1) : 'Disponible'}
      </span>
      <button class="card-fav active" title="Guardado en favoritos" aria-label="En favoritos">♥</button>
    </div>
    <div class="card-body">
      <div class="card-type">
        ${propiedad.tipo ? propiedad.tipo.charAt(0).toUpperCase() + propiedad.tipo.slice(1) : 'Inmueble'}
        ${propiedad.ciudad ? '• ' + propiedad.ciudad : ''}
      </div>
      <h3 class="card-title">${propiedad.titulo}</h3>
      <div class="card-location">📍 ${propiedad.ciudad || 'Ibagué'}, Tolima</div>
      <div class="card-price">${formatPrecio(propiedad.precio)}</div>
      ${features.length
        ? `<div class="card-features">${features.map(feature => `<span>${feature}</span>`).join('')}</div>`
        : ''}
      <div class="card-actions">
        <a href="detalle.html?id=${propiedad.id}" class="btn btn-sm btn-primary">Ver detalle</a>
        <button class="btn-remove-fav" data-id="${propiedad.id}">🗑 Quitar</button>
      </div>
    </div>`;

  card.querySelector('.btn-remove-fav').addEventListener('click', () => {
    quitarFavorito(propiedad.id, card);
  });

  return card;
}

async function cargarFavoritos() {
  try {
    const res = await fetch(`${API_FAV}/`, { credentials: 'include' });

    hideLoading();

    if (res.status === 401 || res.status === 403) {
      showSection('favsAuthWall');
      return;
    }

    if (!res.ok) throw new Error('API error');

    const data = await res.json();
    const lista = Array.isArray(data) ? data : (data.results || []);

    document.getElementById('favCount').textContent = lista.length;

    if (lista.length === 0) {
      showSection('favsEmpty');
      return;
    }

    document.getElementById('headerActions').style.display = '';

    const grid = document.getElementById('favsGrid');
    lista.forEach((fav, index) => {
      const card = buildFavCard(fav, index * 0.08);
      grid.appendChild(card);
    });

    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { threshold: 0.08 });
    grid.querySelectorAll('.reveal').forEach(element => obs.observe(element));
  } catch {
    hideLoading();
    showSection('favsError');
  }
}

async function initAuth() {
  const navUser = document.getElementById('navUser');
  const navLoginBtn = document.getElementById('navLoginBtn');
  try {
    const res = await fetch(`${API_AUTH}/me/`, { credentials: 'include' });
    if (res.ok) {
      const user = await res.json();
      document.getElementById('navUserName').textContent =
        user.first_name || user.username || user.email;
      navUser.classList.remove('oculto');
      navLoginBtn.classList.add('oculto');
      return true;
    }

    navUser.classList.add('oculto');
    navLoginBtn.classList.remove('oculto');
    return false;
  } catch {
    navUser.classList.add('oculto');
    navLoginBtn.classList.remove('oculto');
    return false;
  }
}

document.getElementById('navLogout')?.addEventListener('click', async (event) => {
  event.preventDefault();
  const csrf = await getCsrfToken();
  await fetch(`${API_AUTH}/logout/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  window.location.href = 'index.html';
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

document.getElementById('navHamburger').addEventListener('click', () => {
  document.getElementById('navMenu').classList.toggle('open');
});

(async () => {
  const autenticado = await initAuth();
  if (!autenticado) {
    hideLoading();
    showSection('favsAuthWall');
    document.getElementById('favCount').textContent = '0';
    return;
  }

  await cargarFavoritos();
})();