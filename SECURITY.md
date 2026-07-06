# 🔐 Guía de Seguridad - Inmobiliaria Remolina

## Configuración de Seguridad

### 1. Variables de Entorno Requeridas

Crea un archivo `backend/.env` con las siguientes variables:

```env
# Base de datos (Supabase)
DATABASE_URL=postgresql://postgres:PASSWORD@aws-1-us-east-2.pooler.supabase.com:5432/postgres

# Django
DEBUG=False  # Siempre False en producción
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui

# CORS y hosts
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

**IMPORTANTE:**
- 🔴 Nunca commit el `.env` a Git
- 🔴 Nunca hardcodees claves secretas en el código
- 🔴 `SECRET_KEY` debe ser una cadena aleatoria de al menos 50 caracteres

### 2. Cómo generar una SECRET_KEY segura

En Python:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

O usando openssl:

```bash
openssl rand -base64 50
```

### 3. Medidas de Seguridad Implementadas ✅

#### Frontend (JavaScript)
- ✅ HTML sanitization: `escapeHtml()` protege contra XSS
- ✅ No hay credenciales hardcodeadas
- ✅ API calls configurables por entorno
- ✅ CSRF token automático en formularios

#### Backend (Django)
- ✅ `DEBUG = False` obligatorio en producción
- ✅ `CSRF_COOKIE_SECURE = True` (HTTPS only)
- ✅ `CSRF_COOKIE_HTTPONLY = True` (imposible acceder desde JS)
- ✅ `SESSION_COOKIE_HTTPONLY = True` (protege cookies de sesión)
- ✅ `X_FRAME_OPTIONS = 'DENY'` (protege contra clickjacking)
- ✅ `SECURE_CONTENT_TYPE_NOSNIFF = True`
- ✅ `SECURE_BROWSER_XSS_FILTER = True`
- ✅ CORS restringido a dominios autorizados
- ✅ Rate limiting activo (throttling por usuario)

#### Base de Datos
- ✅ Conexión via Supabase (PostgreSQL)
- ✅ SSL/TLS requerido (`pooler.supabase.com`)
- ✅ Credenciales en variable de entorno

### 4. Autenticación

#### Admin Django
- URL: `/admin`
- Requiere credenciales de superuser
- Acceso solo para administradores

#### API REST
- Endpoints de lectura (`GET`): Públicos
- Endpoints de escritura (`POST`, `PUT`, `PATCH`, `DELETE`): Requieren autenticación

### 5. Despliegue en Producción

#### Antes de lanzar:

```bash
# 1. Verificar que DEBUG = False
grep "DEBUG" backend/.env

# 2. Generar SECRET_KEY segura
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Actualizar ALLOWED_HOSTS
# 4. Verificar CORS_ORIGINS
# 5. Certificado SSL/TLS configurado
```

#### Comando de inicio seguro:

```bash
# Aplicar migraciones
python manage.py migrate --noinput

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar con Gunicorn (no el servidor de desarrollo)
gunicorn config.wsgi --workers 4 --bind 0.0.0.0:8000
```

### 6. Verificación de Seguridad

```bash
# Django security check
python manage.py check --deploy

# Debería mostrar 0 errores críticos
```

### 7. Auditoría Reciente

**Última revisión:** 2026-06-10

✅ Sin referencias a Firebase
✅ Credenciales no expuestas
✅ HTML sanitizado contra XSS
✅ CSRF protection activa
✅ SQL injection protegido (ORM Django)
✅ localStorage solo con datos no-sensibles

### 8. Política de Cambios

Cuando actualices el código:
- 🔒 Nunca adicionar hardcoded credentials
- 🔒 Usar `escapeHtml()` para todos los datos dinámicos en HTML
- 🔒 Verificar permisos en endpoints nuevos
- 🔒 Validar entrada del usuario
- 🔒 Testear seguridad antes de producción

---

**Contacto:** Para reportar vulnerabilidades, contacta a: admin@remolina.local
