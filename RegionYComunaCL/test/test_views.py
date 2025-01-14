"""from django.test import TestCase
from usuarios.models import Usuario
from rest_framework.test import APIClient

class RegionComunaViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff_user = Usuario.objects.create_user(
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        # Obtener el token de autenticación (ajusta la ruta según tu configuración)
        response = self.client.post('/api/auth/token/', {
            'email': 'staff@example.com',
            'password': 'password123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_list_regions(self):
        response = self.client.get('/api/RegionYComunaCL/region/')
        self.assertEqual(response.status_code, 200)

    def test_list_comunas(self):
        response = self.client.get('/api/RegionYComunaCL/comuna/')
        self.assertEqual(response.status_code, 200)
"""