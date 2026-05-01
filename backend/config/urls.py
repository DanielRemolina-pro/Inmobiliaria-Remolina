"""
config/urls.py
==============
URLs raíz del proyecto Remolina Inmobiliaria.

Incluye:
  /admin/          → Panel de administración Django
  /api/            → API REST (propiedades + auth)
  /api/schema/     → Esquema OpenAPI (JSON)
  /api/docs/       → Swagger UI  (documentación interactiva)
  /api/redoc/      → ReDoc       (documentación alternativa)
  /media/          → Archivos subidos por el usuario (solo en DEBUG)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# Personalización del admin
admin.site.site_header = 'Remolina Inmobiliaria — Admin'
admin.site.site_title  = 'Remolina Admin'
admin.site.index_title = 'Panel de administración'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API REST
    path('api/', include('propiedades.urls')),

    # Documentación OpenAPI
    path('api/schema/',        SpectacularAPIView.as_view(),        name='schema'),
    path('api/docs/',          SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',         SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),
]

# Media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)