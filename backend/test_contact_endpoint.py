import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from propiedades.models import Contacto

client = Client()
data = {
    'nombre': 'Prueba Remolina',
    'email': 'contacto@remolina.com',
    'telefono': '3001234567',
    'mensaje': 'Mensaje de prueba del endpoint de contacto.'
}
response = client.post('/api/contacto/', json.dumps(data), content_type='application/json')
print(response.status_code)
print(response.content.decode('utf-8'))
contacto = Contacto.objects.filter(email='contacto@remolina.com').order_by('-creado').first()
if contacto:
    print('saved', contacto.id, contacto.nombre, contacto.email, contacto.telefono)
else:
    print('saved', False)
