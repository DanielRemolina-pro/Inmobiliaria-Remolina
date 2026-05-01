"""
propiedades/urls.py
===================
Registro de ViewSets en el router.

El DefaultRouter genera automáticamente:

  PropiedadViewSet  →  /api/propiedades/
    GET    /api/propiedades/              list
    POST   /api/propiedades/              create
    GET    /api/propiedades/{id}/         retrieve
    PUT    /api/propiedades/{id}/         update
    PATCH  /api/propiedades/{id}/         partial_update
    DELETE /api/propiedades/{id}/         destroy
    GET    /api/propiedades/destacadas/   @action
    GET    /api/propiedades/stats/        @action

  AuthViewSet  →  /api/auth/
    GET    /api/auth/csrf/                @action
    POST   /api/auth/registro/            @action
    POST   /api/auth/login/               @action
    POST   /api/auth/logout/              @action
    GET    /api/auth/me/                  @action
    PATCH  /api/auth/me/editar/           @action
    POST   /api/auth/cambiar-password/    @action

  Raíz del API  →  /api/
    GET    /api/                          lista de endpoints (DefaultRouter)
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, PropiedadViewSet

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet, basename='propiedad')
router.register(r'auth',        AuthViewSet,      basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]