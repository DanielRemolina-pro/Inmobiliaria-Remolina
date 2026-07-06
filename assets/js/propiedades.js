const API_AUTH = window.APP_CONFIG.authApi;
const API_PROP = window.APP_CONFIG.propiedadesApi;
const API_FAV  = window.APP_CONFIG.favoritosApi;

let currentUser = null;
let favIds      = new Set();
let propiedades = [];
let currentPage = 1;
let modalidadActiva = '';
let totalPropiedades = 0;
let totalPages = 1;
const PAGE_SIZE = 12;
let filtrosTimer = null;

function showToast(msg, type = '') {
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = msg;
  document.getElementById('toastContainer').appendChild(t);
  setTimeout(() => t.remove(), 3200);
}

async function getCsrfToken() {
  if (window.__csrfToken) return window.__csrfToken;
  const r = await fetch(`${API_AUTH}/csrf/`, { credentials: 'include' });
  const d = await r.json();
  window.__csrfToken = d.csrfToken;
  return window.__csrfToken;
}

function formatPrecio(p) {
  if (p === null || p === undefined) return 'Consultar precio';
  return '$ ' + Number(p).toLocaleString('es-CO');
}

function formatArea(a) {
  if (!a) return '—';
  return a >= 10000 ? (a / 10000).toFixed(1) + ' ha' : a + ' m²';
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

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
}

async function initAuth() {
  const navUser     = document.getElementById('navUser');
  const navLoginBtn = document.getElementById('navLoginBtn');

  try {
    const res = await fetch(`${API_AUTH}/me/`, { credentials: 'include' });
    if (res.ok) {
      currentUser = await res.json();
      document.getElementById('navUserName').textContent =
        currentUser.first_name || currentUser.username || currentUser.email;
      navUser.classList.remove('oculto');
      navLoginBtn.classList.add('oculto');

      if (currentUser.is_staff) {
        document.getElementById('btnNuevaPropiedad').classList.remove('oculto');
      }

      try {
        const favRes = await fetch(`${API_FAV}/ids/`, { credentials: 'include' });
        if (favRes.ok) {
          const d = await favRes.json();
          favIds = new Set(d.ids.map(String));
        }
      } catch {
        favIds = new Set();
      }
    } else {
      navUser.classList.add('oculto');
      navLoginBtn.classList.remove('oculto');
    }
  } catch {
    navUser.classList.add('oculto');
    navLoginBtn.classList.remove('oculto');
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
    const res  = await fetch(`${API_FAV}/toggle/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ propiedad_id: propId }),
    });
    if (res.ok || res.status === 201) {
      const d = await res.json();
      if (d.action === 'added') {
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

async function cargarPropiedades() {
  try {
    const params = buildQueryParams();
    const res = await fetch(`${API_PROP}/?${params.toString()}`, { credentials: 'include' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    totalPropiedades = data.count || 0;
    totalPages = Math.max(1, Math.ceil(totalPropiedades / PAGE_SIZE));
    propiedades = (data.results || []).map(p => ({
      id:          p.id,
      titulo:      p.titulo,
      precio:      p.precio,
      descripcion: p.descripcion,
      tipo:        p.tipo,
      ciudad:      p.ciudad,
      ubicacion:   p.ubicacion || '',
      area:        p.area,
      estado:      p.estado || 'disponible',
      modalidad:   p.modalidad || 'venta',
      fecha:       p.fecha,
      img:         p.imagen_display || p.imagen_url || 'assets/media/videos/dani.png',
    }));

    render();
  } catch (err) {
    console.error('Error cargando propiedades:', err);
    propiedades = [];
    totalPropiedades = 0;
    totalPages = 1;
    render();
    showToast('Error al cargar propiedades', 'error');
  }
}

function buildQueryParams() {
  const params = new URLSearchParams();
  const search = document.getElementById('searchInput').value.trim();
  const tipo   = document.getElementById('tipoFilter').value;
  const ciudad = document.getElementById('ciudadFilter').value;
  const orden  = document.getElementById('ordenFilter').value;
  const min    = document.getElementById('precioMin').value.trim();
  const max    = document.getElementById('precioMax').value.trim();

  params.set('page', String(currentPage));
  if (search) params.set('search', search);
  if (tipo) params.set('tipo', tipo);
  if (ciudad) params.set('ciudad', ciudad);
  if (min) params.set('precio_min', min);
  if (max) params.set('precio_max', max);
  if (modalidadActiva) params.set('modalidad', modalidadActiva);

  const orderingMap = {
    'precio-asc': 'precio',
    'precio-desc': '-precio',
    'area-desc': '-area',
    'reciente': '-fecha',
  };
  if (orderingMap[orden]) params.set('ordering', orderingMap[orden]);

  return params;
}

function applyFilters() {
  currentPage = 1;
  cargarPropiedades();
}

function applyFiltersDebounced() {
  clearTimeout(filtrosTimer);
  filtrosTimer = setTimeout(() => {
    applyFilters();
  }, 250);
}

function render() {
  const grid  = document.getElementById('propiedadesGrid');
  const empty = document.getElementById('emptyState');
  document.getElementById('totalCount').textContent = totalPropiedades;

  if (totalPropiedades === 0) {
    grid.innerHTML = '';
    empty.classList.remove('oculto');
    document.getElementById('pagination').innerHTML = '';
    return;
  }
  empty.classList.add('oculto');

  grid.innerHTML = '';
  propiedades.forEach(p => {
    const isFav = favIds.has(String(p.id));
    const card  = document.createElement('div');
    card.className = 'propiedad-card reveal visible';
    const safeTitle = escapeHtml(p.titulo || 'Propiedad');
    const safeType = escapeHtml(capitalize(p.tipo || 'Inmueble'));
    const safeCity = escapeHtml(p.ciudad || 'Ibagué');
    const safeUbicacion = escapeHtml(p.ubicacion || '');
    const safeImg = safeMediaUrl(p.img);

    card.innerHTML = `
      <div class="card-img-wrap">
        <img src="${safeImg}" alt="${safeTitle}" loading="lazy"
             onerror="this.src='assets/media/videos/dani.png'">
        <span class="card-badge ${getBadgeClass(p.estado)}">
          ${escapeHtml(capitalize(p.estado))}
        </span>
        <span class="card-modalidad-badge ${p.modalidad === 'arriendo' ? 'arriendo' : 'venta'}">
          ${p.modalidad === 'arriendo' ? '🔑 Arriendo' : '🏷 Venta'}
        </span>
        <button class="card-fav ${isFav ? 'active' : ''}" data-id="${p.id}" title="Guardar en favoritos">
          ${isFav ? '♥' : '♡'}
        </button>
      </div>
      <div class="card-body">
        <div class="card-type">
          ${safeType}${p.ciudad ? ' · ' + safeCity : ''}
        </div>
        <h3 class="card-title">${safeTitle}</h3>
        <div class="card-location">📍 ${safeCity}, Tolima</div>
        <div class="card-price">${formatPrecio(p.precio)}</div>
        <div class="card-features">
          <span>Área: ${escapeHtml(formatArea(p.area))}${p.ubicacion ? ' · ' + safeUbicacion : ''}</span>
        </div>
        <div class="card-actions">
          <a href="detalle.html?id=${p.id}" class="btn btn-sm btn-primary">Ver detalle</a>
          <a href="index.html#contacto" class="btn btn-sm btn-ghost-dark">Contacto</a>
        </div>
        ${currentUser?.is_staff ? `
          <div class="admin-card-actions">
            <button class="admin-card-btn admin-edit" data-edit="${p.id}">✏ Editar</button>
            <button class="admin-card-btn admin-delete" data-delete="${p.id}">🗑 Eliminar</button>
          </div>
        ` : ''}
      </div>`;

    card.querySelector('.card-fav')
      .addEventListener('click', e => toggleFav(p.id, e.currentTarget));

    card.querySelector('[data-edit]')
      ?.addEventListener('click', () => abrirModalEditar(p.id));

    card.querySelector('[data-delete]')
      ?.addEventListener('click', e => eliminarPropiedad(p.id, e.currentTarget));

    grid.appendChild(card);
  });

  const pg = document.getElementById('pagination');
  if (totalPages <= 1) { pg.innerHTML = ''; return; }
  pg.innerHTML = Array.from({ length: totalPages }, (_, i) => i + 1).map(n =>
    `<button class="page-btn ${n === currentPage ? 'active' : ''}" data-page="${n}">${n}</button>`
  ).join('');
  pg.querySelectorAll('.page-btn').forEach(btn =>
    btn.addEventListener('click', async () => {
      currentPage = parseInt(btn.dataset.page);
      await cargarPropiedades();
      window.scrollTo({ top: 300, behavior: 'smooth' });
    })
  );
}

async function eliminarPropiedad(id, btn) {
  if (!currentUser?.is_staff) {
    showToast('Solo el administrador puede modificar propiedades.', 'error');
    return;
  }
  if (!confirm('¿Seguro que deseas eliminar esta propiedad?\nEsta acción no se puede deshacer.')) return;
  btn.disabled = true;
  try {
    const csrf = await getCsrfToken();
    const res  = await fetch(`${API_PROP}/${id}/`, {
      method: 'DELETE',
      headers: { 'X-CSRFToken': csrf },
      credentials: 'include',
    });
    if (res.status === 204) {
      if (propiedades.length === 1 && currentPage > 1) {
        currentPage -= 1;
      }
      await cargarPropiedades();
      showToast('Propiedad eliminada correctamente.', 'success');
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.detail || err.error || 'Error al eliminar.', 'error');
    }
  } catch {
    showToast('Error de conexión.', 'error');
  } finally {
    btn.disabled = false;
  }
}

const overlay  = document.getElementById('adminModal');
const form     = document.getElementById('adminForm');
const loader   = document.getElementById('modalLoader');
let editId   = null;

function abrirModal() {
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function cerrarModal() {
  overlay.classList.remove('open');
  document.body.style.overflow = '';
  editId = null;
  form.reset();
  document.getElementById('imgPreviewWrap').classList.add('oculto');
  document.getElementById('imgNote').classList.add('oculto');
  document.getElementById('modalError').classList.add('oculto');
  document.getElementById('modalError').textContent = '';
  loader.classList.add('oculto');
  form.classList.remove('oculto');
  document.getElementById('modalSubmitBtn').disabled = false;
  document.getElementById('modalSubmitLabel').textContent = 'Guardar propiedad';
}

document.getElementById('modalClose').addEventListener('click', cerrarModal);
document.getElementById('modalCancelBtn').addEventListener('click', cerrarModal);
overlay.addEventListener('click', e => { if (e.target === overlay) cerrarModal(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarModal(); });

window.abrirModalCrear = function () {
  if (!currentUser?.is_staff) {
    showToast('Solo el administrador puede crear propiedades.', 'error');
    return;
  }
  cerrarModal();
  editId = null;
  document.getElementById('modalTitle').textContent = 'Nueva propiedad';
  document.getElementById('modalSubmitLabel').textContent = 'Crear propiedad';
  document.getElementById('imgNote').classList.remove('oculto');
  document.getElementById('f_fecha').value = new Date().toISOString().slice(0, 10);
  abrirModal();
};

async function abrirModalEditar(id) {
  if (!currentUser?.is_staff) {
    showToast('Solo el administrador puede editar propiedades.', 'error');
    return;
  }
  cerrarModal();
  editId = id;
  document.getElementById('modalTitle').textContent = 'Editar propiedad';
  document.getElementById('modalSubmitLabel').textContent = 'Guardar cambios';
  document.getElementById('imgNote').classList.add('oculto');

  loader.classList.remove('oculto');
  form.classList.add('oculto');
  abrirModal();

  try {
    const res = await fetch(`${API_PROP}/${id}/`, { credentials: 'include' });
    if (!res.ok) throw new Error('No se pudo cargar la propiedad.');
    const p = await res.json();

    document.getElementById('f_titulo').value       = p.titulo        || '';
    document.getElementById('f_tipo').value         = p.tipo          || '';
    document.getElementById('f_estado').value       = p.estado        || 'disponible';
    document.getElementById('f_modalidad').value    = p.modalidad     || 'venta';
    document.getElementById('f_ciudad').value       = p.ciudad        || '';
    document.getElementById('f_ubicacion').value    = p.ubicacion     || '';
    document.getElementById('f_precio').value       = p.precio        ?? '';
    document.getElementById('f_area').value         = p.area          ?? '';
    document.getElementById('f_habitaciones').value = p.habitaciones  ?? '';
    document.getElementById('f_banos').value        = p.banos         ?? '';
    document.getElementById('f_estrato').value      = p.estrato       ?? '';
    document.getElementById('f_parqueadero').checked = !!p.parqueadero;
    document.getElementById('f_imagen_url').value   = p.imagen_url    || '';
    document.getElementById('f_video_url').value    = p.video_url     || '';
    document.getElementById('f_descripcion').value  = p.descripcion   || '';
    document.getElementById('f_fecha').value        = p.fecha         || '';

    const imgSrc = p.imagen_display || p.imagen_url;
    if (imgSrc) {
      document.getElementById('imgPreview').src = imgSrc;
      document.getElementById('imgPreviewWrap').classList.remove('oculto');
    }
  } catch (err) {
    cerrarModal();
    showToast(err.message || 'Error al cargar propiedad.', 'error');
    return;
  }

  loader.classList.add('oculto');
  form.classList.remove('oculto');
}

document.getElementById('f_imagen').addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    document.getElementById('imgPreview').src = ev.target.result;
    document.getElementById('imgPreviewWrap').classList.remove('oculto');
  };
  reader.readAsDataURL(file);
});

form.addEventListener('submit', async e => {
  e.preventDefault();

  if (!currentUser?.is_staff) {
    mostrarErrorModal('Solo el administrador puede crear o editar propiedades.');
    return;
  }

  const submitBtn   = document.getElementById('modalSubmitBtn');
  const submitLabel = document.getElementById('modalSubmitLabel');
  const errorBox    = document.getElementById('modalError');
  errorBox.classList.add('oculto');
  errorBox.textContent = '';

  const titulo = document.getElementById('f_titulo').value.trim();
  const tipo   = document.getElementById('f_tipo').value;
  if (!titulo) { mostrarErrorModal('El título es obligatorio.'); return; }
  if (!tipo)   { mostrarErrorModal('Selecciona un tipo de propiedad.'); return; }

  const imagenUrl  = document.getElementById('f_imagen_url').value.trim();
  const imagenFile = document.getElementById('f_imagen').files[0];
  if (!editId && !imagenUrl && !imagenFile) {
    mostrarErrorModal('Para crear una propiedad debes agregar una URL de imagen o subir un archivo.');
    return;
  }

  const fd = new FormData();
  const campos = [
    ['titulo',       document.getElementById('f_titulo').value.trim()],
    ['tipo',         document.getElementById('f_tipo').value],
    ['estado',       document.getElementById('f_estado').value],
    ['modalidad',    document.getElementById('f_modalidad').value],
    ['ciudad',       document.getElementById('f_ciudad').value.trim()],
    ['ubicacion',    document.getElementById('f_ubicacion').value.trim()],
    ['precio',       document.getElementById('f_precio').value],
    ['area',         document.getElementById('f_area').value],
    ['habitaciones', document.getElementById('f_habitaciones').value],
    ['banos',        document.getElementById('f_banos').value],
    ['estrato',      document.getElementById('f_estrato').value],
    ['imagen_url',   imagenUrl],
    ['video_url',    document.getElementById('f_video_url').value.trim()],
    ['descripcion',  document.getElementById('f_descripcion').value.trim()],
    ['fecha',        document.getElementById('f_fecha').value],
  ];
  campos.forEach(([key, val]) => { if (val !== '' && val !== null) fd.append(key, val); });

  fd.append('parqueadero', document.getElementById('f_parqueadero').checked ? 'true' : 'false');

  if (imagenFile) fd.append('imagen', imagenFile);

  submitBtn.disabled = true;
  submitLabel.textContent = editId ? 'Guardando…' : 'Creando…';

  try {
    const csrf   = await getCsrfToken();
    const url    = editId ? `${API_PROP}/${editId}/` : `${API_PROP}/`;
    const method = editId ? 'PATCH' : 'POST';

    const res = await fetch(url, {
      method,
      headers: { 'X-CSRFToken': csrf },
      credentials: 'include',
      body: fd,
    });

    if (res.ok || res.status === 201) {
      showToast(
        editId ? '✅ Propiedad actualizada correctamente.' : '✅ Propiedad creada correctamente.',
        'success'
      );
      cerrarModal();
      await cargarPropiedades();
    } else {
      const errData = await res.json().catch(() => ({ detail: `Error HTTP ${res.status}` }));
      console.error('Error al guardar:', res.status, errData);
      mostrarErrorModal(parsearErrores(errData));
    }
  } catch (err) {
    console.error('Error de red:', err);
    mostrarErrorModal(`Error de conexión: ${err.message}. ¿Está el servidor Django corriendo?`);
  } finally {
    submitBtn.disabled = false;
    submitLabel.textContent = editId ? 'Guardar cambios' : 'Crear propiedad';
  }
});

function mostrarErrorModal(msg) {
  const errorBox = document.getElementById('modalError');
  errorBox.textContent = msg;
  errorBox.classList.remove('oculto');
  errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function parsearErrores(data) {
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  const msgs = Object.entries(data).map(([campo, errs]) => {
    const e = Array.isArray(errs) ? errs.join(' ') : errs;
    return `${campo}: ${e}`;
  });
  return msgs.join('\n') || 'Error al guardar la propiedad.';
}

document.querySelectorAll('.modalidad-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.modalidad-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    modalidadActiva = tab.dataset.modalidad;
    applyFilters();
  });
});

['searchInput','tipoFilter','ciudadFilter','ordenFilter','precioMin','precioMax'].forEach(id => {
  const el = document.getElementById(id);
  el?.addEventListener('input',  applyFiltersDebounced);
  el?.addEventListener('change', applyFilters);
});

document.getElementById('clearFilters').addEventListener('click', () => {
  ['searchInput','tipoFilter','ciudadFilter','ordenFilter','precioMin','precioMax']
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  applyFilters();
});

document.getElementById('navLogout')?.addEventListener('click', async e => {
  e.preventDefault();
  const csrf = await getCsrfToken();
  await fetch(`${API_AUTH}/logout/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  window.location.reload();
});

const fabMain  = document.getElementById('fab-main');
const fabItems = document.getElementById('fab-items');
fabMain.addEventListener('click', () => {
  fabItems.classList.toggle('oculto');
  fabMain.classList.toggle('open');
});
document.addEventListener('click', e => {
  if (!fabMain.contains(e.target) && !fabItems.contains(e.target)) {
    fabItems.classList.add('oculto');
    fabMain.classList.remove('open');
  }
});

document.getElementById('navHamburger').addEventListener('click', () => {
  document.getElementById('navMenu').classList.toggle('open');
});

const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('tipo')) document.getElementById('tipoFilter').value = urlParams.get('tipo');

(async () => {
  await initAuth();
  await cargarPropiedades();

  const editarId = new URLSearchParams(window.location.search).get('editar');
  if (editarId && currentUser?.is_staff) {
    await abrirModalEditar(parseInt(editarId));
  }
})();