from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Propiedad, Visita


class VisitaApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='cliente1',
			email='cliente1@example.com',
			password='Password123!',
		)
		self.propiedad = Propiedad.objects.create(
			titulo='Casa campestre',
			tipo='casa',
			modalidad='venta',
			ciudad='Ibague',
			precio=350000000,
			imagen_url='https://example.com/casa.jpg',
		)
		self.fecha_valida = timezone.localdate() + timedelta(days=1)

	def test_usuario_autenticado_puede_agendar_visita(self):
		self.client.force_login(self.user)

		response = self.client.post(
			'/api/visitas/',
			{
				'propiedad': self.propiedad.id,
				'fecha': self.fecha_valida.isoformat(),
				'hora': '10:00',
				'nota': 'Prefiero visita en la manana.',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Visita.objects.count(), 1)
		visita = Visita.objects.get()
		self.assertEqual(visita.usuario, self.user)
		self.assertEqual(visita.propiedad, self.propiedad)
		self.assertEqual(visita.hora, '10:00')

	def test_no_permite_reservar_horario_ya_ocupado(self):
		User.objects.create_user(
			username='cliente2',
			email='cliente2@example.com',
			password='Password123!',
		)
		Visita.objects.create(
			usuario=self.user,
			propiedad=self.propiedad,
			fecha=self.fecha_valida,
			hora='09:00',
		)
		self.client.force_login(self.user)

		response = self.client.post(
			'/api/visitas/',
			{
				'propiedad': self.propiedad.id,
				'fecha': self.fecha_valida.isoformat(),
				'hora': '09:00',
				'nota': '',
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('hora', response.data)

	def test_horas_ocupadas_retorna_horarios_de_la_propiedad_y_fecha(self):
		Visita.objects.create(
			usuario=self.user,
			propiedad=self.propiedad,
			fecha=self.fecha_valida,
			hora='09:00',
		)
		Visita.objects.create(
			usuario=self.user,
			propiedad=self.propiedad,
			fecha=self.fecha_valida,
			hora='15:00',
		)
		self.client.force_login(self.user)

		response = self.client.get(
			'/api/visitas/horas_ocupadas/',
			{
				'propiedad': self.propiedad.id,
				'fecha': self.fecha_valida.isoformat(),
			},
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['horas_ocupadas'], ['09:00', '15:00'])
