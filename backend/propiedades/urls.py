from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ─────────────────────────────────────────────────────────────
    path('auth/csrf/',     views.csrf_token,    name='auth-csrf'),
    path('auth/registro/', views.registro,       name='auth-registro'),
    path('auth/login/',    views.iniciar_sesion, name='auth-login'),
    path('auth/logout/',   views.cerrar_sesion,  name='auth-logout'),
    path('auth/me/',       views.mi_perfil,      name='auth-me'),

    # ── Propiedades ──────────────────────────────────────────────────────
    # GET  → público   |  POST → is_staff
    path('propiedades/',      views.propiedades_list,  name='propiedades-list'),
    # GET  → público   |  PUT/PATCH/DELETE → is_staff
    path('propiedades/<int:pk>/', views.propiedad_detail, name='propiedad-detail'),
]