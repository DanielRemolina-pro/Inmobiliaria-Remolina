from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('propiedades', '0005_favorito'),
    ]

    operations = [
        migrations.AddField(
            model_name='propiedad',
            name='modalidad',
            field=models.CharField(
                choices=[('venta', 'Venta'), ('arriendo', 'Arriendo')],
                default='venta',
                max_length=20,
                verbose_name='Modalidad',
            ),
        ),
        migrations.AddField(
            model_name='propiedad',
            name='video_url',
            field=models.URLField(
                blank=True,
                null=True,
                verbose_name='Video URL (YouTube o enlace directo)',
            ),
        ),
    ]