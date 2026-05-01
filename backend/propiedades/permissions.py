"""
propiedades/permissions.py
==========================
Clases de permisos personalizadas para la API de Remolina Inmobiliaria.

Separar los permisos en su propio módulo (SRP) permite reutilizarlos
en cualquier ViewSet sin duplicar lógica de autorización.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Permiso de lectura pública (GET, HEAD, OPTIONS).
    Escritura (POST, PUT, PATCH, DELETE) restringida a usuarios is_staff.

    Usado en: PropiedadViewSet
    """
    message = 'Solo los administradores pueden crear, editar o eliminar propiedades.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """
    Permiso a nivel de objeto.
    El propietario del recurso o un staff pueden modificarlo.

    Usado en: PerfilViewSet (edición de perfil propio)
    """
    message = 'Solo puedes modificar tu propio perfil.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # obj es un User — solo el mismo usuario o un admin puede editarlo
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        return obj == request.user or request.user.is_staff