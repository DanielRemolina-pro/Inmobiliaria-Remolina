from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Propiedad
from .serializers import RegistroSerializer, PerfilSerializer, PropiedadSerializer


# ══════════════════════════════════════════════════════════════════════════
#  AUTH VIEWS
# ══════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
    """GET /api/auth/csrf/ — devuelve el CSRF token para el frontend."""
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    """POST /api/auth/registro/  body: { nombre, email, password }"""
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return Response({
            'mensaje': 'Cuenta creada correctamente.',
            'usuario': PerfilSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_sesion(request):
    """POST /api/auth/login/  body: { email, password }"""
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Correo y contraseña son requeridos.'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Credenciales incorrectas.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return Response({'error': 'Credenciales incorrectas.'},
                        status=status.HTTP_401_UNAUTHORIZED)

    login(request, user)
    return Response({
        'mensaje': 'Sesión iniciada correctamente.',
        'usuario': PerfilSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cerrar_sesion(request):
    """POST /api/auth/logout/"""
    logout(request)
    return Response({'mensaje': 'Sesión cerrada.'})


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    """GET /api/auth/me/  |  PATCH /api/auth/me/"""
    if request.method == 'GET':
        return Response(PerfilSerializer(request.user).data)

    serializer = PerfilSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ══════════════════════════════════════════════════════════════════════════
#  PROPIEDADES VIEWS
#
#  Permisos:
#    GET  (listar / ver detalle) → AllowAny   (público)
#    POST (crear)                → is_staff   (solo administradores)
#    PUT / PATCH (editar)        → is_staff   (solo administradores)
#    DELETE (eliminar)           → is_staff   (solo administradores)
# ══════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def propiedades_list(request):
    """
    GET  /api/propiedades/  — lista todas las propiedades (público)
    POST /api/propiedades/  — crea una propiedad (solo administradores)
    """
    if request.method == 'GET':
        props = Propiedad.objects.all()
        serializer = PropiedadSerializer(props, many=True, context={'request': request})
        return Response(serializer.data)

    # ── POST: solo administradores (is_staff) ──────────────────────────
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {'error': 'Solo los administradores pueden crear propiedades.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PropiedadSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def propiedad_detail(request, pk):
    """
    GET    /api/propiedades/<pk>/  — ver detalle (público)
    PUT    /api/propiedades/<pk>/  — editar completo (solo administradores)
    PATCH  /api/propiedades/<pk>/  — editar parcial  (solo administradores)
    DELETE /api/propiedades/<pk>/  — eliminar         (solo administradores)
    """
    try:
        propiedad = Propiedad.objects.get(pk=pk)
    except Propiedad.DoesNotExist:
        return Response({'error': 'Propiedad no encontrada.'},
                        status=status.HTTP_404_NOT_FOUND)

    # ── Lectura pública ──────────────────────────────────────────────────
    if request.method == 'GET':
        serializer = PropiedadSerializer(propiedad, context={'request': request})
        return Response(serializer.data)

    # ── Escritura / eliminación: solo administradores ───────────────────
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {'error': 'Solo los administradores pueden modificar o eliminar propiedades.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == 'DELETE':
        propiedad.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    partial    = (request.method == 'PATCH')
    serializer = PropiedadSerializer(
        propiedad, data=request.data, partial=partial, context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)