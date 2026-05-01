"""
propiedades/views.py
====================
ViewSets para la API REST de Remolina Inmobiliaria.

  PropiedadViewSet  — CRUD completo de propiedades con filtros,
                      búsqueda, ordenamiento y paginación automática.
  AuthViewSet       — Registro, login, logout, perfil y cambio de contraseña.
  FavoritoViewSet   — Gestión de favoritos del usuario autenticado.
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
from .models import Favorito, Propiedad
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    CambioPasswordSerializer,
    FavoritoSerializer,
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
    """
    queryset           = Propiedad.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]
    filterset_class    = PropiedadFilter
    search_fields      = ['titulo', 'descripcion', 'ciudad', 'ubicacion']
    ordering_fields    = ['precio', 'area', 'fecha', 'id', 'estrato']
    ordering           = ['-id']

    def get_serializer_class(self):
        if self.action == 'list':
            return PropiedadListSerializer
        return PropiedadSerializer

    @extend_schema(
        summary='Propiedades destacadas',
        description='Devuelve las 6 propiedades más recientes disponibles. Útil para el home.',
    )
    @action(detail=False, methods=['get'], url_path='destacadas', permission_classes=[AllowAny])
    def destacadas(self, request):
        """GET /api/propiedades/destacadas/ — sin paginación, para el home."""
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
        """GET /api/propiedades/stats/"""
        from django.db.models import Count, Avg

        por_tipo   = Propiedad.objects.values('tipo').annotate(total=Count('id'))
        por_estado = Propiedad.objects.values('estado').annotate(total=Count('id'))
        precio_avg = Propiedad.objects.aggregate(promedio=Avg('precio'))

        return Response({
            'total':           Propiedad.objects.count(),
            'precio_promedio': precio_avg['promedio'],
            'por_tipo':        list(por_tipo),
            'por_estado':      list(por_estado),
        })


# ══════════════════════════════════════════════════════════════════════════════
#  FAVORITO VIEWSET
# ══════════════════════════════════════════════════════════════════════════════

class FavoritoViewSet(viewsets.ViewSet):
    """
    Gestión de favoritos del usuario autenticado.

    Endpoints:
        GET    /api/favoritos/              → listar mis favoritos
        POST   /api/favoritos/              → agregar propiedad a favoritos
        DELETE /api/favoritos/{id}/         → quitar favorito por ID de favorito
        DELETE /api/favoritos/propiedad/{prop_id}/ → quitar por ID de propiedad
        GET    /api/favoritos/ids/          → solo los IDs de propiedades favoritas
                                              (útil para marcar ♥ en cards del index)

    Todos requieren autenticación.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Listar mis favoritos')
    def list(self, request):
        """GET /api/favoritos/ — devuelve favoritos con detalle de propiedad."""
        favoritos  = Favorito.objects.filter(usuario=request.user).select_related('propiedad')
        serializer = FavoritoSerializer(favoritos, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary='Agregar a favoritos', request=FavoritoSerializer)
    def create(self, request):
        """POST /api/favoritos/  body: { propiedad_id: <int> }"""
        serializer = FavoritoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        favorito = serializer.save()
        return Response(
            FavoritoSerializer(favorito, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary='Quitar favorito por ID de favorito')
    def destroy(self, request, pk=None):
        """DELETE /api/favoritos/{id}/"""
        try:
            favorito = Favorito.objects.get(pk=pk, usuario=request.user)
        except Favorito.DoesNotExist:
            return Response(
                {'error': 'Favorito no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        favorito.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Quitar favorito por ID de propiedad')
    @action(detail=False, methods=['delete'], url_path=r'propiedad/(?P<prop_id>\d+)')
    def quitar_por_propiedad(self, request, prop_id=None):
        """DELETE /api/favoritos/propiedad/{prop_id}/ — más cómodo para el frontend."""
        eliminados, _ = Favorito.objects.filter(
            usuario=request.user,
            propiedad_id=prop_id,
        ).delete()
        if eliminados == 0:
            return Response(
                {'error': 'Esta propiedad no estaba en tus favoritos.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary='IDs de propiedades favoritas',
        description='Devuelve solo la lista de IDs. Útil para marcar ♥ en cards sin cargar todo el detalle.',
    )
    @action(detail=False, methods=['get'], url_path='ids')
    def ids(self, request):
        """GET /api/favoritos/ids/ → { ids: [1, 5, 12, ...] }"""
        ids = Favorito.objects.filter(
            usuario=request.user
        ).values_list('propiedad_id', flat=True)
        return Response({'ids': list(ids)})

    @extend_schema(summary='Toggle favorito (agregar/quitar en un solo endpoint)')
    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle(self, request):
        """
        POST /api/favoritos/toggle/  body: { propiedad_id: <int> }
        Si la propiedad ya es favorita la quita; si no, la agrega.
        Responde con { action: 'added'|'removed', favorito_id: <int>|null }
        """
        prop_id = request.data.get('propiedad_id')
        if not prop_id:
            return Response(
                {'error': 'propiedad_id es requerido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            propiedad = Propiedad.objects.get(pk=prop_id)
        except Propiedad.DoesNotExist:
            return Response(
                {'error': 'Propiedad no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        favorito = Favorito.objects.filter(usuario=request.user, propiedad=propiedad).first()
        if favorito:
            favorito.delete()
            return Response({'action': 'removed', 'favorito_id': None})
        else:
            nuevo = Favorito.objects.create(usuario=request.user, propiedad=propiedad)
            return Response(
                {'action': 'added', 'favorito_id': nuevo.pk},
                status=status.HTTP_201_CREATED,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH VIEWSET
# ══════════════════════════════════════════════════════════════════════════════

class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet de autenticación.

    Endpoints:
        GET  /api/auth/csrf/
        POST /api/auth/registro/
        POST /api/auth/login/
        POST /api/auth/logout/
        GET  /api/auth/me/
        PATCH/PUT /api/auth/me/editar/
        POST /api/auth/cambiar-password/
    """
    permission_classes = [AllowAny]

    @extend_schema(summary='Obtener CSRF token')
    @action(detail=False, methods=['get'], url_path='csrf')
    def csrf_token(self, request):
        return Response({'csrfToken': get_token(request)})

    @extend_schema(summary='Registro de usuario', request=RegistroSerializer)
    @action(detail=False, methods=['post'], url_path='registro')
    def registro(self, request):
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

    @extend_schema(summary='Iniciar sesión')
    @action(detail=False, methods=['post'], url_path='login')
    def iniciar_sesion(self, request):
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
            return Response({'error': 'Credenciales incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user_obj.username, password=password)
        if user is None:
            return Response({'error': 'Credenciales incorrectas.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Esta cuenta está desactivada.'}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)
        return Response({
            'mensaje': 'Sesión iniciada correctamente.',
            'usuario': PerfilSerializer(user, context={'request': request}).data,
        })

    @extend_schema(summary='Cerrar sesión')
    @action(detail=False, methods=['post'], url_path='logout',
            permission_classes=[IsAuthenticated])
    def cerrar_sesion(self, request):
        logout(request)
        return Response({'mensaje': 'Sesión cerrada correctamente.'})

    @extend_schema(summary='Ver mi perfil')
    @action(detail=False, methods=['get'], url_path='me',
            permission_classes=[IsAuthenticated])
    def mi_perfil(self, request):
        serializer = PerfilSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @extend_schema(summary='Editar mi perfil', request=PerfilSerializer)
    @action(detail=False, methods=['patch', 'put'], url_path='me/editar',
            permission_classes=[IsAuthenticated])
    def editar_perfil(self, request):
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

    @extend_schema(summary='Cambiar contraseña', request=CambioPasswordSerializer)
    @action(detail=False, methods=['post'], url_path='cambiar-password',
            permission_classes=[IsAuthenticated])
    def cambiar_password(self, request):
        serializer = CambioPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logout(request)
        return Response({'mensaje': 'Contraseña actualizada. Por favor inicia sesión de nuevo.'})