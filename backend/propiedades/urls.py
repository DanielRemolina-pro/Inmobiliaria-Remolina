from django.urls import path
from . import views
 
urlpatterns = [
    path('csrf/',     views.csrf_token,      name='auth-csrf'),
    path('registro/', views.registro,         name='auth-registro'),
    path('login/',    views.iniciar_sesion,   name='auth-login'),
    path('logout/',   views.cerrar_sesion,    name='auth-logout'),
    path('me/',       views.mi_perfil,        name='auth-me'),
]
 