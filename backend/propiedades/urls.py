"""
propiedades/urls.py
===================
Registro de ViewSets en el router.

El DefaultRouter genera automáticamente:

  PropiedadViewSet  →  /api/propiedades/
    GET    /api/propiedades/                    list
    POST   /api/propiedades/                    create
    GET    /api/propiedades/{id}/               retrieve
    PUT    /api/propiedades/{id}/               update
    PATCH  /api/propiedades/{id}/               partial_update
    DELETE /api/propiedades/{id}/               destroy
    GET    /api/propiedades/destacadas/         @action (home)
    GET    /api/propiedades/stats/              @action

  FavoritoViewSet  →  /api/favoritos/
    GET    /api/favoritos/                      list (mis favoritos con detalle)
    POST   /api/favoritos/                      create (agregar)
    DELETE /api/favoritos/{id}/                 destroy (quitar por ID favorito)
    DELETE /api/favoritos/propiedad/{prop_id}/  @action (quitar por ID propiedad)
    GET    /api/favoritos/ids/                  @action (solo IDs, para marcar ♥)
    POST   /api/favoritos/toggle/               @action (toggle add/remove)

  AuthViewSet  →  /api/auth/
    GET    /api/auth/csrf/
    POST   /api/auth/registro/
    POST   /api/auth/login/
    POST   /api/auth/logout/
    GET    /api/auth/me/
    PATCH  /api/auth/me/editar/
    POST   /api/auth/cambiar-password/
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, FavoritoViewSet, PropiedadViewSet

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet, basename='propiedad')
router.register(r'favoritos',   FavoritoViewSet,  basename='favorito')
router.register(r'auth',        AuthViewSet,       basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]