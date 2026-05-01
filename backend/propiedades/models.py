"""
propiedades/models.py
=====================
Modelos de dominio para Remolina Inmobiliaria.

  PerfilUsuario  → extiende User con campos de contacto (OneToOne)
  Propiedad      → inmueble publicado en la plataforma
  Favorito       → relación usuario ↔ propiedad (lista de deseos)

Los signals post_save crean/guardan el PerfilUsuario automáticamente
al crear un User, evitando lógica duplicada en las vistas.
"""

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# ── PerfilUsuario ─────────────────────────────────────────────────────────────

class PerfilUsuario(models.Model):
    """
    Extiende el modelo User de Django con campos adicionales de contacto.
    Se crea automáticamente al registrar un usuario (ver signal post_save).
    """
    user     = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    telefono = models.CharField(max_length=20, blank=True)
    ciudad   = models.CharField(max_length=100, blank=True)
    creado   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.user.get_full_name() or self.user.username}'


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea el PerfilUsuario cuando se crea un nuevo User."""
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    """Sincroniza el save del User con su PerfilUsuario."""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


# ── Propiedad ─────────────────────────────────────────────────────────────────

class Propiedad(models.Model):
    """
    Inmueble publicado en la plataforma Remolina Inmobiliaria.

    Campos de imagen:
      - imagen     → archivo subido directamente (ImageField)
      - imagen_url → URL externa (Firebase Storage, Cloudinary, etc.)
    Al menos uno debe estar presente.
    """

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

    # Información básica
    titulo      = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    tipo        = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        null=True, blank=True,
        verbose_name='Tipo',
    )
    estado      = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name='Estado',
    )

    # Ubicación
    ciudad    = models.CharField(max_length=100, null=True, blank=True, verbose_name='Ciudad')
    ubicacion = models.CharField(max_length=200, null=True, blank=True, verbose_name='Dirección / sector')

    # Precio y área
    precio = models.IntegerField(null=True, blank=True, verbose_name='Precio (COP)')
    area   = models.FloatField(null=True, blank=True, verbose_name='Área (m²)')

    # Características
    habitaciones = models.IntegerField(null=True, blank=True, verbose_name='Habitaciones')
    banos        = models.IntegerField(null=True, blank=True, verbose_name='Baños')
    parqueadero  = models.BooleanField(null=True, blank=True, verbose_name='Parqueadero')
    estrato      = models.IntegerField(null=True, blank=True, verbose_name='Estrato')

    # Imagen
    imagen     = models.ImageField(
        upload_to='propiedades/',
        null=True, blank=True,
        verbose_name='Imagen (archivo)',
    )
    imagen_url = models.URLField(null=True, blank=True, verbose_name='Imagen (URL externa)')

    # Fecha de publicación
    fecha = models.DateField(null=True, blank=True, verbose_name='Fecha de publicación')

    class Meta:
        verbose_name        = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering            = ['-id']

    def __str__(self):
        return f'[{self.get_tipo_display()}] {self.titulo} — {self.ciudad or "sin ciudad"}'

    @property
    def imagen_principal(self):
        """Devuelve la URL de imagen preferida: archivo > URL externa."""
        if self.imagen:
            return self.imagen.url
        return self.imagen_url or ''


# ── Favorito ──────────────────────────────────────────────────────────────────

class Favorito(models.Model):
    """
    Relación muchos-a-muchos entre usuario y propiedad.
    Representa la lista de favoritos/deseos de cada usuario.

    unique_together garantiza que un usuario no pueda guardar
    la misma propiedad dos veces.
    """
    usuario    = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoritos',
        verbose_name='Usuario',
    )
    propiedad  = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name='guardado_por',
        verbose_name='Propiedad',
    )
    creado     = models.DateTimeField(auto_now_add=True, verbose_name='Guardado el')

    class Meta:
        verbose_name        = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together     = ('usuario', 'propiedad')
        ordering            = ['-creado']

    def __str__(self):
        return f'{self.usuario.username} ❤ {self.propiedad.titulo}'