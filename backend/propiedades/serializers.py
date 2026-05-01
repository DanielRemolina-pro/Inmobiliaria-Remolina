"""
propiedades/serializers.py
==========================
Serializers para la API de Remolina Inmobiliaria.

Estructura:
  - RegistroSerializer       → creación de usuario
  - CambioPasswordSerializer → cambio de contraseña autenticado
  - PerfilSerializer         → lectura/escritura del perfil propio
  - PropiedadListSerializer  → lista compacta (menos campos, más rápida)
  - PropiedadSerializer      → detalle completo (lectura + escritura)
  - FavoritoSerializer       → favoritos del usuario autenticado
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Favorito, PerfilUsuario, Propiedad


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH SERIALIZERS
# ══════════════════════════════════════════════════════════════════════════════

class RegistroSerializer(serializers.Serializer):
    """Valida y crea un nuevo usuario desde el formulario de registro."""

    nombre   = serializers.CharField(max_length=150)
    email    = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        nombre   = validated_data['nombre'].strip()
        email    = validated_data['email']
        password = validated_data['password']

        base = email.split('@')[0]
        username, counter = base, 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{counter}'
            counter += 1

        partes     = nombre.split(' ', 1)
        first_name = partes[0]
        last_name  = partes[1] if len(partes) > 1 else ''

        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )


class CambioPasswordSerializer(serializers.Serializer):
    """Permite que el usuario cambie su contraseña estando autenticado."""

    password_actual = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_nuevo  = serializers.CharField(
        min_length=8,
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate_password_actual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value

    def validate_password_nuevo(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['password_nuevo'])
        user.save()
        return user


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer anidado para el modelo PerfilUsuario."""

    class Meta:
        model  = PerfilUsuario
        fields = ('telefono', 'ciudad', 'creado')
        read_only_fields = ('creado',)


class PerfilSerializer(serializers.ModelSerializer):
    """
    Lectura y escritura del perfil completo del usuario autenticado.
    Anida PerfilUsuario para exponer teléfono, ciudad y fecha de creación.
    """
    perfil = PerfilUsuarioSerializer(required=False)

    class Meta:
        model  = User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
            'is_staff', 'date_joined',
            'perfil',
        )
        read_only_fields = ('id', 'username', 'email', 'is_staff', 'date_joined')

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name  = validated_data.get('last_name',  instance.last_name)
        instance.save()

        perfil = instance.perfil
        perfil.telefono = perfil_data.get('telefono', perfil.telefono)
        perfil.ciudad   = perfil_data.get('ciudad',   perfil.ciudad)
        perfil.save()

        return instance


# ══════════════════════════════════════════════════════════════════════════════
#  PROPIEDAD SERIALIZERS
# ══════════════════════════════════════════════════════════════════════════════

class PropiedadListSerializer(serializers.ModelSerializer):
    imagen_display = serializers.SerializerMethodField()

    class Meta:
        model = Propiedad
        fields = (
            'id', 'titulo', 'precio', 'tipo', 'estado',
            'ciudad', 'area', 'habitaciones', 'banos',
            'imagen_display',
        )

    def get_imagen_display(self, obj):
        request = self.context.get('request')
        if obj.imagen:
            return request.build_absolute_uri(obj.imagen.url) if request else obj.imagen.url
        if obj.imagen_url:
            return obj.imagen_url
        return None


class PropiedadSerializer(serializers.ModelSerializer):
    """
    Serializer completo para creación, edición y detalle de propiedad.
    """
    imagen_display = serializers.SerializerMethodField(read_only=True)
    imagen = serializers.ImageField(required=False, allow_null=True, write_only=False)

    class Meta:
        model  = Propiedad
        fields = (
            'id', 'titulo', 'descripcion', 'precio', 'tipo',
            'ciudad', 'ubicacion', 'area', 'estado',
            'imagen', 'imagen_display', 'imagen_url',
            'habitaciones', 'banos', 'parqueadero', 'estrato',
            'fecha',
        )

    def get_imagen_display(self, obj):
        request = self.context.get('request')
        if obj.imagen:
            return request.build_absolute_uri(obj.imagen.url) if request else obj.imagen.url
        if obj.imagen_url:
            return obj.imagen_url
        return None

    def validate_precio(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('El precio no puede ser negativo.')
        return value

    def validate_area(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('El área debe ser mayor a 0 m².')
        return value

    def validate_estrato(self, value):
        if value is not None and value not in range(1, 7):
            raise serializers.ValidationError('El estrato debe estar entre 1 y 6.')
        return value

    def validate(self, attrs):
        imagen     = attrs.get('imagen')
        imagen_url = attrs.get('imagen_url')
        if self.instance is None and not imagen and not imagen_url:
            raise serializers.ValidationError(
                {'imagen': 'Debes proporcionar una imagen de archivo o una URL de imagen.'}
            )
        return attrs


# ══════════════════════════════════════════════════════════════════════════════
#  FAVORITO SERIALIZER
# ══════════════════════════════════════════════════════════════════════════════

class FavoritoSerializer(serializers.ModelSerializer):
    """
    Serializer para la lista de favoritos del usuario.
    Incluye el detalle completo de la propiedad anidada (solo lectura).
    """
    propiedad = PropiedadListSerializer(read_only=True)
    propiedad_id = serializers.PrimaryKeyRelatedField(
        queryset=Propiedad.objects.all(),
        source='propiedad',
        write_only=True,
    )

    class Meta:
        model  = Favorito
        fields = ('id', 'propiedad', 'propiedad_id', 'creado')
        read_only_fields = ('id', 'creado')

    def validate(self, attrs):
        """Previene duplicados a nivel de serializer (la BD también lo garantiza)."""
        usuario   = self.context['request'].user
        propiedad = attrs['propiedad']
        if Favorito.objects.filter(usuario=usuario, propiedad=propiedad).exists():
            raise serializers.ValidationError('Esta propiedad ya está en tus favoritos.')
        return attrs

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)