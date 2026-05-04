# 🏠 Inmobiliaria Remolina

> Plataforma web para la gestión y visualización de propiedades inmobiliarias.  
> Permite consultar propiedades, gestionar favoritos y administrar el catálogo desde una API construida con **Django REST Framework**.

---

## 📋 Índice

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Patrones de Diseño Aplicados](#patrones-de-diseño-aplicados)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Guía de Instalación](#guía-de-instalación)
7. [Endpoints de la API](#endpoints-de-la-api)
8. [Pruebas con Postman](#pruebas-con-postman)
9. [Variables de Entorno](#variables-de-entorno)
10. [Autores](#autores)

---

## 📖 Descripción del Proyecto

**Inmobiliaria Remolina** es un MVP funcional desarrollado como proyecto de curso bajo la metodología ágil **Scrum** en 5 Sprints. La plataforma permite:

- 📋 Listar, crear, editar y eliminar propiedades inmobiliarias
- 🔍 Filtrar por tipo, estado, modalidad, ciudad y rango de precio
- ❤️ Guardar propiedades en lista de favoritos (usuarios registrados)
- 🔐 Autenticación de usuarios con registro, login y gestión de perfil
- 📸 Subida de imágenes o URL externas para cada propiedad
- 📱 Interfaz web responsive con HTML, CSS y JavaScript vanilla

---

## 🛠️ Tecnologías Utilizadas

| Tecnología / Librería | Versión | Rol en el Proyecto |
|---|---|---|
| **Python** | 3.11+ | Lenguaje base del backend |
| **Django** | 6.0.4 | Framework web, ORM, Admin, Auth, Signals |
| **Django REST Framework** | 3.17.1 | API REST: ViewSets, Serializers, Permissions, Router |
| **django-cors-headers** | 4.9.0 | CORS para comunicación frontend ↔ backend |
| **django-filter** | 25.2 | Filtrado declarativo de querysets en la API |
| **drf-spectacular** | 0.29.0 | Documentación automática OpenAPI / Swagger UI |
| **Pillow** | 12.2.0 | Procesamiento de imágenes (ImageField) |
| **SQLite** | Built-in | Base de datos relacional para desarrollo/MVP |
| **HTML5 / CSS3** | Estándar W3C | Interfaz web del frontend |
| **JavaScript ES6+** | Nativo | Consumo de API REST, manejo de DOM |
| **Git & GitHub** | 2.x | Control de versiones y repositorio |
| **Postman** | Latest | Pruebas manuales y automatizadas de la API |

---

## 🏗️ Arquitectura del Sistema

El proyecto aplica **Arquitectura en Capas (Layered Architecture) con patrón MVC**:

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTACIÓN (Frontend)                                 │
│  HTML · CSS · JavaScript (Vanilla)                       │
│  index.html, propiedades.html, detalle.html, login.html  │
├─────────────────────────────────────────────────────────┤
│  CONTROLADOR / API REST                                  │
│  Django REST Framework ViewSets · Serializers            │
│  Permissions · DefaultRouter · django-filter             │
├─────────────────────────────────────────────────────────┤
│  LÓGICA DE NEGOCIO                                       │
│  Django Models · Signals (post_save) · Managers          │
│  Reglas de validación · Permisos por rol                 │
├─────────────────────────────────────────────────────────┤
│  PERSISTENCIA (Datos)                                    │
│  SQLite · Django ORM · Migrations                        │
│  Modelos: Propiedad · PerfilUsuario · Favorito           │
└─────────────────────────────────────────────────────────┘
```

### ¿Por qué MVC + Capas?

- Separa responsabilidades claramente entre capas
- Django usa el patrón **MVT** (variante de MVC) de forma nativa
- DRF agrega la capa de **Serialización** (Python ↔ JSON)
- Facilita pruebas unitarias por capa independiente
- Escalable a Microservicios en producción

---

## 🎨 Patrones de Diseño Aplicados

### 1. Factory Method (Creacional)
El **Django ORM Manager** actúa como Factory: `Propiedad.objects.create()` delega la construcción del objeto al Manager, sin exponer lógica de instanciación.

```python
# Aplicación en el proyecto
propiedad = Propiedad.objects.create(
    titulo="Casa Prado",
    tipo="casa",
    precio=250_000_000,
    ciudad="Ibagué"
)
```

### 2. Adapter / Serializer (Estructural)
`PropiedadSerializer` actúa como **Adapter** entre el modelo Django (objetos Python) y el formato JSON de la API REST. Convierte en ambas direcciones.

```python
# Modelo → JSON (serialización)
serializer = PropiedadSerializer(propiedad)
return Response(serializer.data)

# JSON → Modelo (deserialización + validación)
serializer = PropiedadSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
serializer.save()
```

### 3. Observer con Django Signals (Comportamiento)
El sistema de **Signals** de Django implementa el patrón Observer: cuando se crea un `User` (evento), el receptor `crear_perfil()` reacciona automáticamente.

```python
# backend/propiedades/models.py
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea el PerfilUsuario cuando se crea un nuevo User."""
    if created:
        PerfilUsuario.objects.create(user=instance)
```

---

## 📁 Estructura del Proyecto

```
Inmobiliaria-Remolina/
├── backend/                        # Backend Django
│   ├── config/                     # Configuración del proyecto
│   │   ├── settings.py             # Configuración principal
│   │   ├── urls.py                 # URLs raíz
│   │   └── wsgi.py / asgi.py      # Servidores de aplicación
│   ├── propiedades/                # App principal
│   │   ├── models.py               # Propiedad, PerfilUsuario, Favorito
│   │   ├── views.py                # PropiedadViewSet, AuthViewSet, FavoritoViewSet
│   │   ├── serializers.py          # Serializers para la API
│   │   ├── permissions.py          # IsAdminWithModelPerm, IsOwnerOrAdmin
│   │   ├── filters.py              # PropiedadFilter (django-filter)
│   │   ├── urls.py                 # Registro de routers y URLs
│   │   └── migrations/             # Migraciones de base de datos
│   ├── media/                      # Archivos de imagen subidos
│   ├── manage.py                   # CLI de Django
│   └── requirements.txt            # Dependencias Python
├── Documentos/                     # Documentación del proyecto
│   ├── Actas/                      # Actas de Daily Meetings
│   ├── Arquitectura/               # Diagramas de arquitectura
│   ├── Cronogramas/                # Cronograma de Sprints
│   ├── Diagramas HU Epicas/        # UML de historias épicas
│   ├── Diagramas Y Mockups HU Simples/ # Mockups HU001-HU021
│   ├── Requerimientos/             # RF y RNF del sistema
│   └── User Flows/                 # Flujos de usuario
├── index.html                      # Página principal (home)
├── propiedades.html                # Catálogo de propiedades
├── detalle.html                    # Detalle de propiedad
├── favoritos.html                  # Lista de favoritos
├── login.html                      # Login / Registro
├── nosotros.html                   # Página "Nosotros"
├── auth.js                         # Lógica de autenticación frontend
├── script.js                       # Scripts generales
├── styles.css                      # Estilos globales
└── README.md                       # Este archivo
```

---

## 🚀 Guía de Instalación

### Prerrequisitos

Antes de instalar, asegúrate de tener:

- **Python** 3.11 o superior → [descargar](https://python.org)
- **Git** → [descargar](https://git-scm.com)
- **Postman** (opcional, para pruebas) → [descargar](https://postman.com)

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/<usuario>/Inmobiliaria-Remolina.git
cd Inmobiliaria-Remolina
```

### Paso 2 — Crear entorno virtual

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Linux / Mac
source venv/bin/activate

# Activar en Windows (PowerShell)
venv\Scripts\Activate.ps1

# Activar en Windows (CMD)
venv\Scripts\activate.bat
```

### Paso 3 — Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

> Si hay errores con Pillow, instala primero las dependencias del sistema:  
> **Ubuntu/Debian:** `sudo apt install python3-dev libjpeg-dev zlib1g-dev`  
> **Mac:** `brew install libjpeg`

### Paso 4 — Aplicar migraciones de base de datos

```bash
python manage.py migrate
```

### Paso 5 — Crear superusuario (administrador)

```bash
python manage.py createsuperuser
# Ingresar: username, email, contraseña
```

### Paso 6 — (Opcional) Cargar datos de ejemplo

```bash
# Si existe un fixture de ejemplo
python manage.py loaddata propiedades_demo.json
```

### Paso 7 — Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El servidor estará disponible en:
- **API REST:** http://localhost:8000/api/
- **Admin Django:** http://localhost:8000/admin/
- **Documentación Swagger:** http://localhost:8000/api/schema/swagger-ui/

### Paso 8 — Abrir el Frontend

Abre el archivo `index.html` directamente en tu navegador, **o** usa la extensión **Live Server** de VS Code para un mejor desarrollo:

1. Instala la extensión "Live Server" en VS Code
2. Haz clic derecho sobre `index.html` → "Open with Live Server"
3. El frontend se abrirá en `http://127.0.0.1:5500`

> **Importante:** El frontend consume la API en `http://localhost:8000`. Ambos deben estar corriendo simultáneamente.

---

## 🔌 Endpoints de la API

Base URL: `http://localhost:8000/api/`

### Propiedades

| Método | Endpoint | Descripción | Auth requerida |
|---|---|---|---|
| GET | `/propiedades/` | Listar todas las propiedades | No |
| POST | `/propiedades/` | Crear propiedad | Admin |
| GET | `/propiedades/{id}/` | Ver detalle de propiedad | No |
| PUT/PATCH | `/propiedades/{id}/` | Editar propiedad | Admin |
| DELETE | `/propiedades/{id}/` | Eliminar propiedad | Admin |
| GET | `/propiedades/destacadas/` | Propiedades para el home | No |
| GET | `/propiedades/stats/` | Estadísticas del catálogo | Admin |

### Autenticación

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/auth/csrf/` | Obtener token CSRF |
| POST | `/auth/registro/` | Registrar nuevo usuario |
| POST | `/auth/login/` | Iniciar sesión |
| POST | `/auth/logout/` | Cerrar sesión |
| GET | `/auth/me/` | Ver perfil actual |
| PATCH | `/auth/me/editar/` | Editar perfil |
| POST | `/auth/cambiar-password/` | Cambiar contraseña |

### Favoritos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/favoritos/` | Ver mis favoritos |
| POST | `/favoritos/` | Agregar a favoritos |
| DELETE | `/favoritos/{id}/` | Quitar favorito por ID |
| DELETE | `/favoritos/propiedad/{id}/` | Quitar por ID de propiedad |
| GET | `/favoritos/ids/` | Solo IDs (para marcar en UI) |
| POST | `/favoritos/toggle/` | Toggle agregar/quitar |

---

## 🧪 Pruebas con Postman

### Importar colección

1. Abre Postman
2. Clic en **Import** → selecciona el archivo `Inmobiliaria_Remolina_API.postman_collection.json` (si existe en el repo)
3. Configura el entorno con `base_url = http://localhost:8000`

### Flujo de prueba recomendado

```
1. GET  /api/auth/csrf/           → guarda el token CSRF
2. POST /api/auth/registro/       → crear usuario de prueba
3. POST /api/auth/login/          → iniciar sesión
4. GET  /api/propiedades/         → listar propiedades
5. POST /api/favoritos/           → agregar propiedad a favoritos
6. GET  /api/favoritos/           → verificar mis favoritos
7. POST /api/auth/logout/         → cerrar sesión
```

### Script de prueba básico (Postman Tests tab)

```javascript
// Verificar status 200
pm.test("Status 200 OK", () => {
    pm.response.to.have.status(200);
});

// Verificar que la respuesta es un array
pm.test("Response is array", () => {
    const json = pm.response.json();
    pm.expect(json).to.be.an("array");
});

// Guardar ID de la primera propiedad
const id = pm.response.json()[0]?.id;
if (id) pm.environment.set("propiedad_id", id);
```

---

## 🔐 Variables de Entorno (Producción)

Para despliegue en producción, configura las siguientes variables en un archivo `.env`:

```env
DEBUG=False
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
DATABASE_URL=postgres://user:pass@host:5432/inmobiliaria
CORS_ALLOWED_ORIGINS=https://tudominio.com
```

> Para desarrollo local no es necesario, ya que `settings.py` usa valores por defecto seguros para entorno local.

---

## 👥 Autores

Proyecto desarrollado por el equipo de trabajo del curso **Ingeniería de Software I — Grupo 02**  
**Universidad de Ibagué** — Facultad de Ciencias, Ingeniería e Innovación  
**Semestre:** 2026-1 | **Metodología:** Scrum

| Integrante | Rol Scrum |
|---|---|
| *(Nombre 1)* | Scrum Master |
| *(Nombre 2)* | Product Owner |
| *(Nombre 3)* | Development Team |
| *(Nombre 4)* | Development Team |
| *(Nombre 5)* | Development Team |

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos en la Universidad de Ibagué.

---
