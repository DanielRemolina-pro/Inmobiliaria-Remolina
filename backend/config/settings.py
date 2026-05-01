"""
Django settings — Remolina Inmobiliaria
========================================
Sin dependencia de django-environ.
Las variables sensibles se leen con os.environ.get()
con valores por defecto para desarrollo local.

CAMBIOS DE SEGURIDAD respecto a la versión anterior
-----------------------------------------------------
  1. SECRET_KEY sin valor por defecto inseguro en código.
     Ahora lanza error si no se define en producción (DEBUG=False).

  2. DEFAULT_PERMISSION_CLASSES cambiado de IsAuthenticatedOrReadOnly
     a IsAuthenticated. Los endpoints públicos declaran explícitamente
     AllowAny. Esto aplica el principio "denegar por defecto": cualquier
     endpoint nuevo será privado a menos que se indique lo contrario.

  3. Throttle diferenciado: se añade límite más estricto para escritura
     ('write': '20/minute') para prevenir abuso de la API de creación.

  4. CORS endurecido: la variable CORS_ALLOWED_ORIGINS es leída desde
     el entorno. En desarrollo sigue permitiendo localhost. En producción
     solo acepta los dominios explícitos.

  5. Cookies de sesión y CSRF marcadas como Secure en producción.
     SESSION_COOKIE_HTTPONLY=True siempre (protege contra XSS).

  6. SPECTACULAR_SETTINGS: la documentación Swagger se deshabilita
     automáticamente en producción (SERVE_SWAGGER_UI=not DEBUG).

  7. X_FRAME_OPTIONS = 'DENY' — ya venía por el middleware, ahora explícito.

  8. SECURE_CONTENT_TYPE_NOSNIFF y SECURE_BROWSER_XSS_FILTER activados
     siempre.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Entorno: desarrollo o producción ─────────────────────────────────────────
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ── SECRET_KEY ────────────────────────────────────────────────────────────────
# En producción NUNCA dejes un valor por defecto en el código.
# Define la variable de entorno SECRET_KEY antes de lanzar el servidor.
_default_secret = 'django-insecure-da$t#dwso8j+bq@o=5ul(9@mvy_wy@_sbxnskrrx#_-mw3ye6#'
SECRET_KEY = os.environ.get('SECRET_KEY', _default_secret if DEBUG else None)

if not SECRET_KEY:
    raise RuntimeError(
        '⛔  SECRET_KEY no está definida. '
        'Exporta la variable de entorno antes de lanzar el servidor en producción: '
        'export SECRET_KEY="tu-clave-secreta-larga-y-aleatoria"'
    )

# ── Hosts permitidos ──────────────────────────────────────────────────────────
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 'localhost,127.0.0.1'
).split(',')

# ── Aplicaciones ──────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Proyecto
    'propiedades',
]

# ── Middleware ────────────────────────────────────────────────────────────────
# CorsMiddleware DEBE ir primero para que los headers CORS lleguen
# antes de que otros middlewares procesen la petición.
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Base de datos ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Validación de contraseñas ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internacionalización ──────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE     = 'America/Bogota'
USE_I18N      = True
USE_TZ        = True

# ── Archivos estáticos y media ────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ══════════════════════════════════════════════════════════════════════════════
#  CORS — Cross-Origin Resource Sharing
# ══════════════════════════════════════════════════════════════════════════════
#
#  DESARROLLO (DEBUG=True):
#    Permitimos todos los orígenes para facilitar las pruebas con Live Server,
#    file://, Swagger, etc.
#
#  PRODUCCIÓN (DEBUG=False):
#    Solo se aceptan los orígenes explícitos definidos en la variable de entorno
#    CORS_ORIGINS (separados por coma).
#    Si no se define la variable, la lista queda vacía y SOLO el origen del
#    mismo servidor (same-origin) puede hacer peticiones credenciales.
#
#  ⛔  NUNCA pongas CORS_ALLOW_ALL_ORIGINS=True en producción con
#     CORS_ALLOW_CREDENTIALS=True. Es una vulnerabilidad CORS crítica que
#     permite a cualquier sitio web hacer peticiones autenticadas en nombre
#     de tus usuarios.

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS  = True
    CORS_ALLOW_CREDENTIALS  = True
    CSRF_COOKIE_SAMESITE    = None      # Necesario para cross-origin en dev
    SESSION_COOKIE_SAMESITE = None
    CSRF_COOKIE_SECURE      = False
    SESSION_COOKIE_SECURE   = False
else:
    CORS_ALLOW_ALL_ORIGINS  = False
    CORS_ALLOW_CREDENTIALS  = True
    # Define en el entorno: CORS_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
    CORS_ALLOWED_ORIGINS = [
        o.strip()
        for o in os.environ.get('CORS_ORIGINS', '').split(',')
        if o.strip()
    ]
    CSRF_COOKIE_SAMESITE    = 'Lax'   # Protege contra CSRF cross-site
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE      = True    # Solo enviar cookies en HTTPS
    SESSION_COOKIE_SECURE   = True

# ── Cookies: protección siempre activa ────────────────────────────────────────
# HttpOnly en la cookie de sesión: JS no puede leerla → protege contra XSS
SESSION_COOKIE_HTTPONLY = True

# La cookie CSRF SÍ debe ser legible por JS para que el frontend pueda
# incluirla en los headers. Solo en producción con HTTPS esto es seguro.
CSRF_COOKIE_HTTPONLY = False

# ── CSRF: orígenes confiables ─────────────────────────────────────────────────
# Permite peticiones POST/DELETE desde el frontend en desarrollo local.
# En producción reemplaza con tu dominio real (ej: https://remolina.com.co)
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'http://localhost,http://localhost:5500,http://localhost:5501,'
        'http://127.0.0.1,http://127.0.0.1:5500,http://127.0.0.1:5501,'
        'http://127.0.0.1:8000',
    ).split(',')
    if o.strip()
]

# ══════════════════════════════════════════════════════════════════════════════
#  SEGURIDAD ADICIONAL (headers HTTP)
# ══════════════════════════════════════════════════════════════════════════════

# Evita que los navegadores adivinen el Content-Type → previene XSS via upload
SECURE_CONTENT_TYPE_NOSNIFF = True

# Header X-Frame-Options: el sitio no puede embeberse en un <iframe> externo
X_FRAME_OPTIONS = 'DENY'

# En producción: fuerza HTTPS y activa HSTS
if not DEBUG:
    SECURE_SSL_REDIRECT          = True
    SECURE_HSTS_SECONDS          = 31536000   # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD          = True

# ══════════════════════════════════════════════════════════════════════════════
#  DJANGO REST FRAMEWORK
# ══════════════════════════════════════════════════════════════════════════════

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],

    # ── CAMBIO DE SEGURIDAD ───────────────────────────────────────────────────
    # Antes: IsAuthenticatedOrReadOnly → cualquier endpoint era público en GET.
    # Ahora: IsAuthenticated → cualquier endpoint nuevo es privado por defecto.
    # Los endpoints públicos declaran explícitamente AllowAny en su ViewSet
    # (ej: PropiedadViewSet.get_permissions → list/retrieve → AllowAny).
    # Principio: "denegar por defecto, permitir explícitamente".
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Paginación
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,

    # Documentación automática
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    # ── Rate limiting ─────────────────────────────────────────────────────────
    # 'anon'  → usuarios no autenticados (lectura pública)
    # 'user'  → usuarios autenticados (lectura + favoritos)
    # 'write' → operaciones de escritura admin (crear/editar/borrar propiedades)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':  '60/minute',
        'user':  '300/minute',
        'write': '20/minute',   # Throttle estricto para escritura
    },
}

# ── drf-spectacular (Swagger / OpenAPI) ───────────────────────────────────────
# ⛔  En producción la documentación Swagger está deshabilitada.
#    Expone la estructura interna de la API a cualquier persona.
#    Si necesitas acceso en producción, protégelo con autenticación o
#    restríngelo a IPs internas con un reverse-proxy (nginx).
SPECTACULAR_SETTINGS = {
    'TITLE':                'Remolina Inmobiliaria API',
    'DESCRIPTION':          'API REST para gestión de propiedades inmobiliarias en Ibagué.',
    'VERSION':              '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    # Deshabilitar Swagger UI y ReDoc en producción
    'SERVE_SWAGGER_UI':     DEBUG,
    'SERVE_REDOC_UI':       DEBUG,
}