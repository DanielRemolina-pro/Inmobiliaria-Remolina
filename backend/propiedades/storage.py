"""
propiedades/storage.py
=======================
Utilidad para subir imágenes a Supabase Storage.
"""

import uuid
from django.conf import settings
from supabase import create_client


def subir_imagen_a_supabase(archivo):
    """
    Sube un archivo de imagen (InMemoryUploadedFile de Django) a Supabase Storage
    y devuelve la URL pública resultante.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            'Supabase Storage no está configurado (faltan SUPABASE_URL o SUPABASE_SERVICE_KEY).'
        )

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    extension = archivo.name.split('.')[-1] if '.' in archivo.name else 'jpg'
    nombre_archivo = f'{uuid.uuid4().hex}.{extension}'

    contenido = archivo.read()

    supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
        path=nombre_archivo,
        file=contenido,
        file_options={'content-type': archivo.content_type or 'image/jpeg'},
    )

    return supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).get_public_url(nombre_archivo)