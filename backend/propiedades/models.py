from django.db import models
from django.utils.timezone import now

class Propiedad(models.Model):
    titulo = models.CharField(max_length=200)
    precio = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField()

    tipo = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    ubicacion = models.CharField(max_length=200, null=True, blank=True)

    area = models.FloatField(null=True, blank=True)
    estado = models.CharField(max_length=20, default="disponible")

    fecha = models.DateField(default=now)

    imagen = models.ImageField(upload_to='propiedades/', null=True, blank=True)
    imagen_url = models.URLField(null=True, blank=True)