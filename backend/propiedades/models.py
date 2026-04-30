from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """Extiende User con datos adicionales. Se crea automáticamente."""
    user     = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    ciudad   = models.CharField(max_length=100, blank=True)
    creado   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.user.username}'


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


# ── Modelo Propiedad ──────────────────────────────────────────────────────

class Propiedad(models.Model):
    TIPO_CHOICES = [
        ('casa',        'Casa'),
        ('apartamento', 'Apartamento'),
        ('lote',        'Lote'),
        ('finca',       'Finca'),
        ('local',       'Local'),
        ('bodega',      'Bodega'),
    ]
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('vendido',    'Vendido'),
        ('reservado',  'Reservado'),
    ]

    # ── Campos originales (ya en DB) ─────────────────────────────────────
    titulo      = models.CharField(max_length=200)
    precio      = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField(blank=True)
    tipo        = models.CharField(max_length=50, choices=TIPO_CHOICES, null=True, blank=True)
    ciudad      = models.CharField(max_length=100, null=True, blank=True)
    ubicacion   = models.CharField(max_length=200, null=True, blank=True)
    area        = models.FloatField(null=True, blank=True)
    estado      = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    imagen      = models.ImageField(upload_to='propiedades/', null=True, blank=True)
    imagen_url  = models.URLField(null=True, blank=True)
    fecha       = models.DateField(auto_now_add=False, null=True, blank=True)

    # ── Nuevos campos (migración 0004) ───────────────────────────────────
    habitaciones = models.IntegerField(null=True, blank=True)
    banos        = models.IntegerField(null=True, blank=True)
    parqueadero  = models.BooleanField(null=True, blank=True)
    estrato      = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering            = ['-id']

    def __str__(self):
        return self.titulo