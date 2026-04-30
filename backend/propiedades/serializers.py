from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PerfilUsuario, Propiedad


# ── Auth serializers ─────────────────────────────────────────────────────

class RegistroSerializer(serializers.Serializer):
    """Valida y crea un nuevo usuario."""
    nombre   = serializers.CharField(max_length=150)
    email    = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value.lower()

    def create(self, validated_data):
        nombre   = validated_data['nombre']
        email    = validated_data['email']
        password = validated_data['password']

        base_username = email.split('@')[0]
        username = base_username
        counter  = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        partes     = nombre.strip().split(' ', 1)
        first_name = partes[0]
        last_name  = partes[1] if len(partes) > 1 else ''

        return User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )


class PerfilSerializer(serializers.ModelSerializer):
    telefono = serializers.CharField(source='perfil.telefono', required=False, allow_blank=True)
    ciudad   = serializers.CharField(source='perfil.ciudad',   required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'telefono', 'ciudad', 'date_joined')
        read_only_fields = ('id', 'username', 'email', 'is_staff', 'date_joined')

    def update(self, instance, validated_data):
        perfil_data      = validated_data.pop('perfil', {})
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name  = validated_data.get('last_name',  instance.last_name)
        instance.save()
        perfil = instance.perfil
        perfil.telefono = perfil_data.get('telefono', perfil.telefono)
        perfil.ciudad   = perfil_data.get('ciudad',   perfil.ciudad)
        perfil.save()
        return instance


# ── Propiedad serializer ─────────────────────────────────────────────────

class PropiedadSerializer(serializers.ModelSerializer):
    # Devuelve la URL absoluta de la imagen cuando existe
    imagen = serializers.SerializerMethodField()

    class Meta:
        model  = Propiedad
        fields = (
            'id', 'titulo', 'descripcion', 'precio', 'tipo',
            'ciudad', 'ubicacion', 'area', 'estado',
            'imagen', 'imagen_url',
            'habitaciones', 'banos', 'parqueadero', 'estrato',
            'fecha',
        )

    def get_imagen(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.imagen.url) if request else obj.imagen.url

    # Para escritura se acepta el campo imagen como upload
    def to_internal_value(self, data):
        # Permitir campo imagen como archivo en escritura
        mutable = super().to_internal_value(data)
        return mutable