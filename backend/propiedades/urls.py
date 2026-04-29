from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropiedadViewSet, check_admin

router = DefaultRouter()
router.register(r'propiedades', PropiedadViewSet)

urlpatterns = [
    path('check-admin/', check_admin),
    path('api/', include(router.urls)),
]
