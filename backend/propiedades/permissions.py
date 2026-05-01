"""
propiedades/permissions.py
==========================
Clases de permisos personalizadas para la API de Remolina Inmobiliaria.

CAMBIOS respecto a la versión anterior
---------------------------------------
  IsAdminOrReadOnly     → igual que antes, se mantiene para compatibilidad.
  IsAdminWithModelPerm  → NUEVA. Requiere is_staff Y el permiso específico del
                          modelo de Django (add/change/delete). Esto cierra el
                          hueco donde un is_staff sin permisos de modelo podía
                          escribir en la API aunque el Django Admin se lo negara.

Por qué el admin no podía CREAR (bug original)
------------------------------------------------
La clase original solo verificaba `is_staff`. En el Django Admin, crear una
propiedad requiere el permiso `propiedades.add_propiedad`. Si ese permiso no
está asignado al usuario (pero sí change/delete), el admin le deja editar y
borrar, pero no crear. La API, al solo revisar `is_staff`, dejaba inconsistencia.

La nueva clase `IsAdminWithModelPerm` unifica ambos mundos: API y Django Admin
usan exactamente la misma lógica de permisos.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


# ── Mapa HTTP method → permiso de Django ──────────────────────────────────────
# Cada método de escritura se traduce al permiso mínimo requerido.
_PERM_MAP = {
    'POST':   'add',
    'PUT':    'change',
    'PATCH':  'change',
    'DELETE': 'delete',
}


class IsAdminOrReadOnly(BasePermission):
    """
    Permiso de lectura pública (GET, HEAD, OPTIONS).
    Escritura (POST, PUT, PATCH, DELETE) solo para usuarios is_staff.

    ATENCIÓN: solo verifica is_staff, no los permisos granulares del modelo.
    Úsala únicamente cuando quieras una barrera simple. Para mayor control
    usa IsAdminWithModelPerm.
    """
    message = 'Solo los administradores pueden crear, editar o eliminar propiedades.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsAdminWithModelPerm(BasePermission):
    """
    Permiso doble: is_staff + permiso de modelo de Django.

    Lógica:
      - GET / HEAD / OPTIONS → público, siempre permitido.
      - POST   → requiere is_staff + `<app>.add_<model>`
      - PUT / PATCH → requiere is_staff + `<app>.change_<model>`
      - DELETE → requiere is_staff + `<app>.delete_<model>`
      - Superusuarios omiten la verificación de permiso específico.

    Esto garantiza que la API y el Django Admin usen exactamente la misma
    lógica de autorización: no hay forma de crear/editar/eliminar por la API
    si el usuario no tiene el permiso Django correspondiente.

    Usado en: PropiedadViewSet (create, update, partial_update, destroy, stats)
    """
    message = (
        'No tienes permiso para realizar esta acción. '
        'Contacta al administrador del sistema.'
    )

    def has_permission(self, request, view):
        # Lectura: siempre pública
        if request.method in SAFE_METHODS:
            return True

        # Debe estar autenticado y ser staff
        if not (request.user and request.user.is_authenticated and request.user.is_staff):
            return False

        # Superusuarios tienen todo
        if request.user.is_superuser:
            return True

        # Obtener el verbo Django correspondiente al método HTTP
        accion = _PERM_MAP.get(request.method)
        if not accion:
            return False

        # Inferir el permiso desde el queryset del ViewSet
        queryset = getattr(view, 'queryset', None)
        if queryset is None:
            # Si el ViewSet no tiene queryset no podemos inferir: denegar
            return False

        modelo    = queryset.model
        app_label = modelo._meta.app_label
        nombre    = modelo._meta.model_name          # ej: "propiedad"
        permiso   = f'{app_label}.{accion}_{nombre}' # ej: "propiedades.add_propiedad"

        return request.user.has_perm(permiso)

    def has_object_permission(self, request, view, obj):
        """
        Verificación a nivel de objeto (detail views: PUT, PATCH, DELETE /{id}/).
        Reutiliza has_permission porque la lógica es la misma: cualquier admin
        con el permiso puede modificar cualquier propiedad.
        """
        return self.has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso a nivel de objeto.
    El propietario del recurso o un staff pueden modificarlo.

    Sin cambios respecto a la versión original.
    Usado en: edición de perfil propio.
    """
    message = 'Solo puedes modificar tu propio perfil.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user or request.user.is_staff
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        return obj == request.user or request.user.is_staff