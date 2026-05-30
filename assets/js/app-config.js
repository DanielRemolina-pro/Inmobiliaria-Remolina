(() => {
  const explicitOrigin = window.REMOLINA_API_ORIGIN || '';
  const isLocalFrontend = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  const apiOrigin = explicitOrigin || (isLocalFrontend ? 'http://127.0.0.1:8000' : window.location.origin);
  const normalizedOrigin = apiOrigin.replace(/\/$/, '');
  const apiBase = `${normalizedOrigin}/api`;

  window.APP_CONFIG = {
    apiOrigin: normalizedOrigin,
    apiBase,
    authApi: `${apiBase}/auth`,
    propiedadesApi: `${apiBase}/propiedades`,
    favoritosApi: `${apiBase}/favoritos`,
    visitasApi: `${apiBase}/visitas`,
  };
})();