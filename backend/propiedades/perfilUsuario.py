# Migración 0004 — Agrega PerfilUsuario y campos extras a Propiedad
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propiedades', '0003_propiedad_imagen_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Crear PerfilUsuario ───────────────────────────────────────────
        migrations.CreateModel(
            name='PerfilUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telefono', models.CharField(blank=True, max_length=20)),
                ('ciudad',   models.CharField(blank=True, max_length=100)),
                ('creado',   models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='perfil',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Perfil de usuario',
                'verbose_name_plural': 'Perfiles de usuario',
            },
        ),
        # ── Nuevos campos en Propiedad ────────────────────────────────────
        migrations.AddField(
            model_name='propiedad',
            name='habitaciones',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propiedad',
            name='banos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propiedad',
            name='parqueadero',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='propiedad',
            name='estrato',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]