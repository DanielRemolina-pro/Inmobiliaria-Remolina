from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .serializers import RegistroSerializer, PerfilSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
    """
    Endpoint auxiliar: el frontend lo llama una vez al cargar la página
    para obtener el token CSRF sin necesidad de estar autenticado.
    """
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def registro(request):
    """
    POST /api/auth/registro/
    Body: { nombre, email, password }
    """
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Inicia sesión automáticamente tras el registro
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')
        return Response({
            'mensaje': 'Cuenta creada correctamente.',
            'usuario': PerfilSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_sesion(request):
    """
    POST /api/auth/login/
    Body: { email, password }
    """
    email    = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response(
            {'error': 'Correo y contraseña son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Buscar usuario por email (el username puede diferir)
    try:
        user_obj = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'error': 'Credenciales incorrectas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = authenticate(request, username=user_obj.username, password=password)
    if user is None:
        return Response(
            {'error': 'Credenciales incorrectas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

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
    """
    GET  /api/auth/me/   → devuelve datos del usuario autenticado
    PATCH /api/auth/me/  → actualiza nombre y/o teléfono
    """
    if request.method == 'GET':
        return Response(PerfilSerializer(request.user).data)

    serializer = PerfilSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)