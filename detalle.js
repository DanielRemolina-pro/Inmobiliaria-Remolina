// ── Auth state + nav (Django session API) ──────────────────────────────
const AUTH_API  = window.APP_CONFIG.authApi;
const PROPS_API = window.APP_CONFIG.propiedadesApi;
const VISITAS_API = window.APP_CONFIG.visitasApi;
let currentUser = null;

async function getCsrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  if (m) return m[1];
  const r = await fetch(`${AUTH_API}/csrf/`, { credentials: 'include' });
  return (await r.json()).csrfToken;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function safeMediaUrl(value, fallback = 'videos/dani.png') {
  if (!value) return fallback;
  try {
    const url = new URL(value, window.location.origin);
    if (['http:', 'https:'].includes(url.protocol)) return url.href;
  } catch {
    return fallback;
  }
  return fallback;
}

async function initAuth() {
  const navUser     = document.getElementById('navUser');
  const navLoginBtn = document.getElementById('navLoginBtn');
  try {
    const res = await fetch(`${AUTH_API}/me/`, { credentials: 'include' });
    if (res.ok) {
      currentUser = await res.json();
      document.getElementById('navUserName').textContent =
        currentUser.first_name || currentUser.username || currentUser.email;
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
}

document.getElementById('navLogout')?.addEventListener('click', async (e) => {
  e.preventDefault();
  const csrf = await getCsrfToken();
  await fetch(`${AUTH_API}/logout/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  window.location.reload();
});

document.getElementById('navHamburger')?.addEventListener('click', () => {
  document.getElementById('navMenu').classList.toggle('open');
});

const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 30);
  });
}

let allImgs = [];
let lbIdx  = 0;

function abrirLightbox(i) {
  lbIdx = i;
  actualizarLb();
  document.getElementById('lightbox').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function cerrarLightbox() {
  document.getElementById('lightbox').classList.remove('open');
  document.body.style.overflow = '';
}

function lbNav(dir) {
  lbIdx = (lbIdx + dir + allImgs.length) % allImgs.length;
  actualizarLb();
}

function actualizarLb() {
  document.getElementById('lbImg').src = allImgs[lbIdx] || '';
  document.getElementById('lbCounter').textContent = `${lbIdx + 1} / ${allImgs.length}`;
}

document.addEventListener('keydown', e => {
  if (!document.getElementById('lightbox').classList.contains('open')) return;
  if (e.key === 'ArrowLeft')  lbNav(-1);
  if (e.key === 'ArrowRight') lbNav(1);
  if (e.key === 'Escape')     cerrarLightbox();
});

async function cargarDetalle() {
  const id = new URLSearchParams(window.location.search).get('id');
  if (!id) return;

  try {
    const res = await fetch(`${PROPS_API}/${id}/`);
    const p   = await res.json();

    document.title = `${p.titulo || 'Propiedad'} — Remolina`;
    document.getElementById('breadTitle').textContent  = p.titulo;
    document.getElementById('detTitulo').textContent   = p.titulo;
    document.getElementById('metaId').textContent      = '#' + id;

    if (p.tipo) {
      document.getElementById('detTipo').textContent  = p.tipo;
      document.getElementById('metaTipo').textContent = p.tipo;
    }

    document.getElementById('detPrecio').textContent =
      p.precio ? '$' + p.precio.toLocaleString('es-CO') : 'Consultar precio';
    document.getElementById('detPrecioNota').textContent =
      p.precio ? 'Negociable • Financiación disponible' : '';

    const ubText = [p.ubicacion, p.ciudad, 'Tolima'].filter(Boolean).join(' — ');
    document.getElementById('ubicacionText').textContent = ubText;

    document.getElementById('metaEstado').textContent = p.estado || '—';
    document.getElementById('metaCiudad').textContent = p.ciudad ? p.ciudad + ', Tolima' : '—';

    let areaStr = '—';
    if (p.area) {
      areaStr = p.area >= 10000
        ? (p.area / 10000).toFixed(2) + ' ha'
        : p.area.toLocaleString('es-CO') + ' m²';
    }
    document.getElementById('metaArea').textContent = areaStr;

    const statsData = [
      { icon: '📐', label: 'Área',   value: areaStr },
      { icon: '🏷️', label: 'Tipo',   value: p.tipo  || '—' },
      { icon: '✅', label: 'Estado', value: p.estado || '—' },
    ];
    document.getElementById('detStats').innerHTML = statsData.map(s => `
      <div class="det-stat">
        <div class="det-stat-icon">${s.icon}</div>
        <div class="det-stat-label">${escapeHtml(s.label)}</div>
        <div class="det-stat-value">${escapeHtml(s.value)}</div>
      </div>
    `).join('');

    const frases = (p.descripcion || '').split('.')
      .map(d => d.trim()).filter(Boolean);
    document.getElementById('detDesc').innerHTML = frases.map(f => `
      <div class="det-desc-item">${escapeHtml(f)}.</div>
    `).join('');

    const extras = [];
    if (p.habitaciones) extras.push({ label: 'Habitaciones', val: p.habitaciones });
    if (p.banos)        extras.push({ label: 'Baños',        val: p.banos        });
    if (p.parqueadero)  extras.push({ label: 'Parqueadero',  val: p.parqueadero  });
    if (p.estrato)      extras.push({ label: 'Estrato',      val: p.estrato      });

    if (extras.length) {
      const grid = document.getElementById('detExtras');
      grid.style.display = 'grid';
      grid.innerHTML = extras.map(e => `
        <div class="det-extra-item">
          <div class="det-extra-label">${escapeHtml(e.label)}</div>
          <div class="det-extra-val">${escapeHtml(e.val)}</div>
        </div>
      `).join('');
    }

    allImgs = [];
    if (p.imagen_display) allImgs.push(safeMediaUrl(p.imagen_display));
    else if (p.imagen_url) allImgs.push(safeMediaUrl(p.imagen_url));
    if (Array.isArray(p.imagenes)) {
      p.imagenes.forEach(img => {
        const src = img.imagen
          ? safeMediaUrl(`${window.APP_CONFIG.apiOrigin}${img.imagen}`)
          : safeMediaUrl(img.url);
        if (src && !allImgs.includes(src)) allImgs.push(src);
      });
    }
    if (allImgs.length === 0) allImgs.push('videos/dani.png');

    document.getElementById('mainHeroImg').src = allImgs[0] || '';
    document.getElementById('side1Img').src    = allImgs[1] || allImgs[0] || '';
    document.getElementById('side2Img').src    = allImgs[2] || allImgs[0] || '';

    if (allImgs.length < 2) document.getElementById('heroSide1').style.display = 'none';
    if (allImgs.length < 3) document.getElementById('heroSide2').style.display = 'none';

    const strip = document.getElementById('thumbStrip');
    const thumbsHTML = allImgs.map((src, i) => `
      <div class="thumb-item ${i === 0 ? 'active' : ''}"
           onclick="seleccionarThumb(${i})">
        <img src="${safeMediaUrl(src)}" alt="Vista ${i + 1}">
      </div>
    `).join('');

    let phHTML = '';
    if (currentUser?.is_staff) {
      phHTML = `
        <div class="thumb-placeholder admin-upload-btn" title="Agregar imagen" onclick="abrirModalMedia('imagen')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="3"/>
            <path d="M12 8v8M8 12h8"/>
          </svg>
          <span>+ Foto</span>
        </div>
        <div class="thumb-placeholder admin-upload-btn" title="Agregar video URL" onclick="abrirModalMedia('video')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="9"/>
            <polygon points="10,8 16,12 10,16" fill="currentColor" stroke="none"/>
          </svg>
          <span>+ Video</span>
        </div>
      `;
    }

    strip.innerHTML = thumbsHTML + phHTML;

    if (currentUser?.is_staff) {
      let adminPanel = document.getElementById('adminPanel');
      if (!adminPanel) {
        adminPanel = document.createElement('div');
        adminPanel.id = 'adminPanel';
        adminPanel.style.cssText =
          'display:flex;gap:0.75rem;margin:1.5rem 0;padding:1rem;' +
          'background:rgba(220,38,38,0.08);border:1px solid rgba(220,38,38,0.25);border-radius:0.5rem;';
        adminPanel.innerHTML = `
          <span style="flex:1;color:var(--ivory-dim,#aaa);font-size:0.85rem;align-self:center;">
            ⚙ Panel de administrador
          </span>
          <a href="propiedades.html?editar=${id}"
             style="padding:0.5rem 1.25rem;background:#d97706;color:#fff;border-radius:0.4rem;font-size:0.9rem;text-decoration:none;">
            ✏ Editar propiedad
          </a>
          <button id="btnEliminarProp"
            style="padding:0.5rem 1.25rem;background:#dc2626;color:#fff;border:none;border-radius:0.4rem;font-size:0.9rem;cursor:pointer;">
            🗑 Eliminar
          </button>
        `;
        const breadcrumb = document.querySelector('.breadcrumb');
        breadcrumb ? breadcrumb.after(adminPanel) : document.querySelector('main .container').prepend(adminPanel);
      }

      document.getElementById('btnEliminarProp')?.addEventListener('click', async () => {
        if (!confirm('¿Eliminar esta propiedad? Esta acción no se puede deshacer.')) return;
        try {
          const csrf = await getCsrfToken();
          const r = await fetch(`${PROPS_API}/${id}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': csrf },
            credentials: 'include',
          });
          if (r.status === 204) {
            alert('Propiedad eliminada.');
            window.location.href = 'propiedades.html';
          } else {
            const err = await r.json();
            alert(err.error || 'Error al eliminar.');
          }
        } catch {
          alert('Error de conexión.');
        }
      });
    }

    const wspBtn = document.getElementById('btnWhatsapp');
    const wspMsg = encodeURIComponent(`¡Hola! Estoy interesado/a en la propiedad: *${p.titulo}* (Ref. #${id}). ¿Podría darme más información?`);
    wspBtn.href = `https://wa.me/573054152644?text=${wspMsg}`;

    if (p.video_url) {
      const videoSection   = document.getElementById('videoSection');
      const videoContainer = document.getElementById('videoContainer');
      videoSection.style.display = 'block';

      const isYoutube = /youtube\.com|youtu\.be/.test(p.video_url);
      if (isYoutube) {
        const videoId = p.video_url.match(/(?:v=|youtu\.be\/)([^&\s?]+)/)?.[1];
        if (videoId) {
          videoContainer.innerHTML = `<iframe width="100%" height="100%"
            src="https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1"
            frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen style="border:none; display:block;"></iframe>`;
        }
      } else {
        const safeVideoUrl = safeMediaUrl(p.video_url, '');
        if (safeVideoUrl) {
          videoContainer.innerHTML = `<video controls style="width:100%; height:100%; display:block;">
            <source src="${safeVideoUrl}">
            Tu navegador no soporta video HTML5.
          </video>`;
        }
      }
    }

    if (currentUser) {
      document.getElementById('agendarCard').style.display = 'block';
      if (p.precio) document.getElementById('calcPrecio').value = p.precio;

      const hoy     = new Date();
      const manana  = new Date(hoy); manana.setDate(hoy.getDate() + 1);
      const maxDia  = new Date(hoy); maxDia.setDate(hoy.getDate() + 7);

      const toISO = d => d.toISOString().split('T')[0];
      const fechaInput = document.getElementById('visitaFecha');
      fechaInput.min   = toISO(manana);
      fechaInput.max   = toISO(maxDia);
      fechaInput.value = toISO(manana);

      fechaInput.addEventListener('change', () => cargarHorasDisponibles(id, fechaInput.value));
      cargarHorasDisponibles(id, toISO(manana));
    } else {
      document.getElementById('loginInvite').style.display = 'block';
      if (p.precio) document.getElementById('calcPrecio').value = p.precio;
    }

    const precioLabel = document.querySelector('.precio-label');
    if (precioLabel) {
      precioLabel.textContent = p.modalidad === 'arriendo' ? 'Precio de arriendo / mes' : 'Precio de venta';
    }
  } catch (err) {
    console.error('Error cargando detalle:', err);
  }
}

function seleccionarThumb(i) {
  document.getElementById('mainHeroImg').src = allImgs[i];
  document.querySelectorAll('.thumb-item').forEach((el, idx) => {
    el.classList.toggle('active', idx === i);
  });
}

function calcularCredito() {
  const precio = parseFloat(document.getElementById('calcPrecio').value);
  const cuotaPct = parseFloat(document.getElementById('calcCuota').value) / 100;
  const plazoAnios = parseFloat(document.getElementById('calcPlazo').value);
  const tasaAnual = parseFloat(document.getElementById('calcTasa').value) / 100;

  if (!precio || !cuotaPct || !plazoAnios || !tasaAnual) {
    alert('Por favor completa todos los campos de la calculadora.');
    return;
  }

  const montoFinanciar = precio * (1 - cuotaPct);
  const tasaMensual    = tasaAnual / 12;
  const nMeses         = plazoAnios * 12;

  const cuota = montoFinanciar * (tasaMensual * Math.pow(1 + tasaMensual, nMeses))
                / (Math.pow(1 + tasaMensual, nMeses) - 1);

  const totalPagar = cuota * nMeses;
  const totalInteres = totalPagar - montoFinanciar;

  const fmt = n => '$ ' + Math.round(n).toLocaleString('es-CO');

  document.getElementById('calcCuotaMensual').textContent = fmt(cuota);
  document.getElementById('calcDetalle').textContent =
    `Monto a financiar: ${fmt(montoFinanciar)} · Total intereses: ${fmt(totalInteres)} · Total a pagar: ${fmt(totalPagar)}`;
  document.getElementById('calcResultado').style.display = 'block';
}

const TODAS_HORAS = [
  { valor: '09:00', label: '9:00 AM' },
  { valor: '10:00', label: '10:00 AM' },
  { valor: '11:00', label: '11:00 AM' },
  { valor: '14:00', label: '2:00 PM' },
  { valor: '15:00', label: '3:00 PM' },
  { valor: '16:00', label: '4:00 PM' },
];

async function cargarHorasDisponibles(propiedadId, fecha) {
  const select = document.getElementById('visitaHora');
  select.innerHTML = '<option value="">Cargando disponibilidad…</option>';
  select.disabled  = true;

  try {
    const res  = await fetch(
      `${VISITAS_API}/horas_ocupadas/?propiedad=${propiedadId}&fecha=${fecha}`,
      { credentials: 'include' }
    );
    const data = await res.json();
    const ocupadas = data.horas_ocupadas || [];

    select.innerHTML = '';
    let hayDisponibles = false;

    TODAS_HORAS.forEach(h => {
      const opt = document.createElement('option');
      opt.value = h.valor;
      if (ocupadas.includes(h.valor)) {
        opt.textContent = `${h.label} — Ocupada`;
        opt.disabled    = true;
        opt.style.color = '#6b7280';
      } else {
        opt.textContent = h.label;
        hayDisponibles  = true;
      }
      select.appendChild(opt);
    });

    const primera = select.querySelector('option:not([disabled])');
    if (primera) primera.selected = true;

    if (!hayDisponibles) {
      select.innerHTML = '<option value="">No hay horas disponibles este día</option>';
    }
  } catch {
    select.innerHTML = '<option value="">Error al cargar horas</option>';
  } finally {
    select.disabled = false;
  }
}

async function agendarVisita() {
  const propiedadId = new URLSearchParams(window.location.search).get('id');
  const fecha = document.getElementById('visitaFecha').value;
  const hora  = document.getElementById('visitaHora').value;
  const nota  = document.getElementById('visitaNota').value;
  const msg   = document.getElementById('agendarMsg');
  const btn   = document.getElementById('btnAgendarVisita');

  if (!fecha || !hora) {
    msg.style.color = '#f87171';
    msg.textContent = 'Por favor selecciona fecha y hora.';
    return;
  }

  btn.disabled     = true;
  btn.textContent  = 'Guardando…';
  msg.textContent  = '';

  try {
    const csrfRes = await fetch(`${AUTH_API}/csrf/`, { credentials: 'include' });
    const { csrfToken } = await csrfRes.json();

    const res = await fetch(`${VISITAS_API}/`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({
        propiedad: parseInt(propiedadId),
        fecha,
        hora,
        nota,
      }),
    });

    if (res.ok) {
      msg.style.color = '#4ade80';
      msg.textContent = '✅ ¡Visita agendada! Te abrimos WhatsApp para confirmación.';
      btn.textContent = '✅ Agendada';

      cargarHorasDisponibles(propiedadId, fecha);

      const propTitulo = document.getElementById('detTitulo')?.textContent || 'propiedad';
      const horaLabel  = TODAS_HORAS.find(h => h.valor === hora)?.label || hora;
      const wspMsg     = encodeURIComponent(
        `¡Hola! Acabo de agendar una visita:\n🏠 *${propTitulo}* (Ref. #${propiedadId})\n📅 Fecha: ${fecha}\n🕐 Hora: ${horaLabel}${nota ? '\n💬 Nota: ' + nota : ''}`
      );
      setTimeout(() => window.open(`https://wa.me/573054152644?text=${wspMsg}`, '_blank'), 1200);
    } else {
      const err = await res.json().catch(() => ({}));
      const errMsg = err?.hora?.[0] || err?.fecha?.[0] || err?.detail || 'No se pudo agendar la visita.';
      msg.style.color = '#f87171';
      msg.textContent = `❌ ${errMsg}`;
      btn.disabled    = false;
      btn.textContent = 'Solicitar visita';
      cargarHorasDisponibles(propiedadId, fecha);
    }
  } catch {
    msg.style.color = '#f87171';
    msg.textContent = '❌ Error de conexión. ¿Está el servidor activo?';
    btn.disabled    = false;
    btn.textContent = 'Solicitar visita';
  }
}

function abrirModalMedia(tipo) {
  document.getElementById('modalMediaOverlay').style.display = 'flex';
  document.getElementById('modalMediaTipo').value = tipo;
  document.getElementById('modalMediaTitulo').textContent =
    tipo === 'imagen' ? '📷 Agregar imagen' : '🎬 Agregar video';
  document.getElementById('mediaImagenGroup').style.display = tipo === 'imagen' ? 'block' : 'none';
  document.getElementById('mediaVideoGroup').style.display  = tipo === 'video'  ? 'block' : 'none';
  document.getElementById('mediaMsg').textContent = '';
}

function cerrarModalMedia() {
  document.getElementById('modalMediaOverlay').style.display = 'none';
  document.getElementById('mediaFileInput').value  = '';
  document.getElementById('mediaUrlInput').value   = '';
  document.getElementById('mediaVideoUrl').value   = '';
  document.getElementById('mediaMsg').textContent  = '';
}

async function guardarMedia() {
  const tipo     = document.getElementById('modalMediaTipo').value;
  const propId   = new URLSearchParams(window.location.search).get('id');
  const msg      = document.getElementById('mediaMsg');
  const btn      = document.getElementById('btnGuardarMedia');

  btn.disabled    = true;
  btn.textContent = 'Guardando…';
  msg.textContent = '';

  try {
    const csrfRes   = await fetch(`${AUTH_API}/csrf/`, { credentials: 'include' });
    const { csrfToken } = await csrfRes.json();

    if (tipo === 'video') {
      const videoUrl = document.getElementById('mediaVideoUrl').value.trim();
      if (!videoUrl) {
        msg.style.color = '#f87171';
        msg.textContent = 'Pega la URL del video.';
        return;
      }

      const res = await fetch(`${PROPS_API}/${propId}/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
        body: JSON.stringify({ video_url: videoUrl }),
      });
      if (res.ok) {
        msg.style.color = '#4ade80';
        msg.textContent = '✅ Video guardado. Recargando…';
        setTimeout(() => location.reload(), 1200);
      } else {
        throw new Error('Error al guardar video');
      }
    } else {
      const file    = document.getElementById('mediaFileInput').files[0];
      const urlVal  = document.getElementById('mediaUrlInput').value.trim();

      if (!file && !urlVal) {
        msg.style.color = '#f87171';
        msg.textContent = 'Selecciona un archivo o pega una URL.';
        return;
      }

      const fd = new FormData();
      if (file)   fd.append('imagen',     file);
      if (urlVal) fd.append('imagen_url', urlVal);

      const res = await fetch(`${PROPS_API}/${propId}/`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'X-CSRFToken': csrfToken },
        body: fd,
      });
      if (res.ok) {
        msg.style.color = '#4ade80';
        msg.textContent = '✅ Imagen guardada. Recargando…';
        setTimeout(() => location.reload(), 1200);
      } else {
        throw new Error('Error al guardar imagen');
      }
    }
  } catch (e) {
    msg.style.color = '#f87171';
    msg.textContent = `❌ ${e.message}`;
  } finally {
    btn.disabled    = false;
    btn.textContent = 'Guardar';
  }
}

(async () => {
  await initAuth();
  await cargarDetalle();
})();