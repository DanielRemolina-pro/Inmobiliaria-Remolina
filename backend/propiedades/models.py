from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """
    Extiende el modelo User de Django con datos adicionales.
    Se crea automáticamente al registrar un usuario.
    """
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono  = models.CharField(max_length=20, blank=True)
    ciudad    = models.CharField(max_length=100, blank=True)
    creado    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.user.username}'


# ── Signal: crea el perfil automáticamente al crear un User ──────────────────
@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()