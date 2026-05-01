"""
propiedades/views.py
====================
ViewSets para la API REST de Remolina Inmobiliaria.

Migración de @api_view → ModelViewSet / ViewSet
-----------------------------------------------
  PropiedadViewSet   — CRUD completo de propiedades con filtros, búsqueda,
                       ordenamiento y paginación automática.
  AuthViewSet        — Registro, login, logout, perfil y cambio de contraseña.

Ventajas frente a @api_view:
  ✔ Router genera todas las URLs automáticamente
  ✔ CRUD completo con menos código (ModelViewSet)
  ✔ Acciones extra (@action) para endpoints especiales
  ✔ Permisos, parsers y filtros declarados por clase
  ✔ Paginación integrada en list()
  ✔ DRF Spectacular genera la documentación OpenAPI automáticamente
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from .filters import PropiedadFilter
from .models import Propiedad
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    CambioPasswordSerializer,
    PerfilSerializer,
    PropiedadListSerializer,
    PropiedadSerializer,
    RegistroSerializer,
)


# ══════════════════════════════════════════════════════════════════════════════
#  PROPIEDAD VIEWSET
# ══════════════════════════════════════════════════════════════════════════════

@extend_schema_view(
    list=extend_schema(
        summary='Listar propiedades',
        description='Devuelve la lista paginada de propiedades. Público.',
        parameters=[
            OpenApiParameter('tipo',        description='Filtrar por tipo', required=False),
            OpenApiParameter('estado',      description='Filtrar por estado', required=False),
            OpenApiParameter('ciudad',      description='Filtrar por ciudad (contiene)', required=False),
            OpenApiParameter('precio_min',  description='Precio mínimo', required=False),
            OpenApiParameter('precio_max',  description='Precio máximo', required=False),
            OpenApiParameter('search',      description='Búsqueda libre en título, descripción, ciudad', required=False),
            OpenApiParameter('ordering',    description='Ordenar por campo (ej: -precio, area)', required=False),
        ],
    ),
    retrieve=extend_schema(summary='Detalle de propiedad', description='Público.'),
    create=extend_schema(summary='Crear propiedad', description='Solo administradores (is_staff).'),
    update=extend_schema(summary='Actualizar propiedad (PUT)', description='Solo administradores.'),
    partial_update=extend_schema(summary='Actualizar propiedad (PATCH)', description='Solo administradores.'),
    destroy=extend_schema(summary='Eliminar propiedad', description='Solo administradores.'),
)
class PropiedadViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para el modelo Propiedad.

    list / retrieve  → AllowAny (público)
    create / update / destroy → IsAdminOrReadOnly (is_staff)

    Filtros disponibles (query params):
        tipo, estado, ciudad, precio_min, precio_max,
        area_min, area_max, habitaciones, banos, estrato, parqueadero
    Búsqueda libre:
        search=  (busca en título, descripción, ciudad, ubicación)
    Ordenamiento:
        ordering=precio | -precio | area | -fecha
    """

    queryset         = Propiedad.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    parser_classes   = [MultiPartParser, FormParser, JSONParser]
    filterset_class  = PropiedadFilter
    search_fields    = ['titulo', 'descripcion', 'ciudad', 'ubicacion']
    ordering_fields  = ['precio', 'area', 'fecha', 'id', 'estrato']
    ordering         = ['-id']                # orden por defecto

    def get_serializer_class(self):
        """
        Usa el serializer compacto para list() y el completo para el resto.
        Reduce payload en la lista y mantiene todos los campos en detalle/escritura.
        """
        if self.action == 'list':
            return PropiedadListSerializer
        return PropiedadSerializer

    @extend_schema(
        summary='Propiedades destacadas',
        description='Devuelve las 6 propiedades más recientes disponibles. Útil para el home.',
    )
    @action(detail=False, methods=['get'], url_path='destacadas', permission_classes=[AllowAny])
    def destacadas(self, request):
        """GET /api/propiedades/destacadas/ — sin paginación, para el carousel del home."""
        qs = Propiedad.objects.filter(estado='disponible').order_by('-id')[:6]
        serializer = PropiedadListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        summary='Estadísticas de propiedades',
        description='Conteos por tipo y estado. Solo administradores.',
    )
    @action(detail=False, methods=['get'], url_path='stats',
            permission_classes=[IsAuthenticated])
    def stats(self, request):
        """GET /api/propiedades/stats/ — solo para usuarios autenticados (is_staff en producción)."""
        from django.db.models import Count, Avg

        por_tipo   = Propiedad.objects.values('tipo').annotate(total=Count('id'))
        por_estado = Propiedad.objects.values('estado').annotate(total=Count('id'))
        precio_avg = Propiedad.objects.aggregate(promedio=Avg('precio'))

        return Response({
            'total':         Propiedad.objects.count(),
            'precio_promedio': precio_avg['promedio'],
            'por_tipo':      list(por_tipo),
            'por_estado':    list(por_estado),
        })


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH VIEWSET
# ══════════════════════════════════════════════════════════════════════════════

class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet de autenticación.

    Endpoints generados por el router:
        GET  /api/auth/csrf/         → csrf_token
        POST /api/auth/registro/     → registro
        POST /api/auth/login/        → iniciar_sesion
        POST /api/auth/logout/       → cerrar_sesion
        GET  /api/auth/me/           → mi_perfil
        PATCH/PUT /api/auth/me/      → editar_perfil   (action extra)
        POST /api/auth/cambiar-password/ → cambiar_password

    Todos son @action sobre el mismo ViewSet → un único prefijo /api/auth/
    """

    # Permiso por defecto; se sobreescribe por acción
    permission_classes = [AllowAny]

    # ── CSRF ─────────────────────────────────────────────────────────────────

    @extend_schema(summary='Obtener CSRF token', description='Devuelve el token CSRF necesario para requests POST desde el frontend.')
    @action(detail=False, methods=['get'], url_path='csrf')
    def csrf_token(self, request):
        """GET /api/auth/csrf/"""
        return Response({'csrfToken': get_token(request)})

    # ── Registro ──────────────────────────────────────────────────────────────

    @extend_schema(summary='Registro de usuario', request=RegistroSerializer)
    @action(detail=False, methods=['post'], url_path='registro')
    def registro(self, request):
        """POST /api/auth/registro/  body: { nombre, email, password }"""
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return Response(
            {
                'mensaje': 'Cuenta creada correctamente.',
                'usuario': PerfilSerializer(user, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED,
        )

    # ── Login ─────────────────────────────────────────────────────────────────

    @extend_schema(summary='Iniciar sesión')
    @action(detail=False, methods=['post'], url_path='login')
    def iniciar_sesion(self, request):
        """POST /api/auth/login/  body: { email, password }"""
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        if not email or not password:
            return Response(
                {'error': 'Correo y contraseña son requeridos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Credenciales incorrectas.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response({'error': 'Credenciales incorrectas.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Esta cuenta está desactivada.'},
                            status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response({
            'mensaje': 'Sesión iniciada correctamente.',
            'usuario': PerfilSerializer(user, context={'request': request}).data,
        })

    # ── Logout ────────────────────────────────────────────────────────────────

    @extend_schema(summary='Cerrar sesión')
    @action(detail=False, methods=['post'], url_path='logout',
            permission_classes=[IsAuthenticated])
    def cerrar_sesion(self, request):
        """POST /api/auth/logout/"""
        logout(request)
        return Response({'mensaje': 'Sesión cerrada correctamente.'})

    # ── Perfil propio ─────────────────────────────────────────────────────────

    @extend_schema(summary='Ver mi perfil')
    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[IsAuthenticated])
    def mi_perfil(self, request):
        """GET /api/auth/me/"""
        serializer = PerfilSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary='Editar mi perfil', request=PerfilSerializer)
    @action(detail=False, methods=['patch', 'put'], url_path='me/editar',
            permission_classes=[IsAuthenticated])
    def editar_perfil(self, request):
        """PATCH /api/auth/me/editar/  |  PUT /api/auth/me/editar/"""
        partial    = request.method == 'PATCH'
        serializer = PerfilSerializer(
            request.user,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # ── Cambio de contraseña ──────────────────────────────────────────────────

    @extend_schema(summary='Cambiar contraseña', request=CambioPasswordSerializer)
    @action(detail=False, methods=['post'], url_path='cambiar-password',
            permission_classes=[IsAuthenticated])
    def cambiar_password(self, request):
        """POST /api/auth/cambiar-password/  body: { password_actual, password_nuevo }"""
        serializer = CambioPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Cerrar sesión para forzar re-autenticación con la nueva contraseña
        logout(request)
        return Response({'mensaje': 'Contraseña actualizada. Por favor inicia sesión de nuevo.'})