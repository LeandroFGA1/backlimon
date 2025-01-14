from django.test import TestCase
from django.contrib.auth.models import User
from .models import Pedido
from rest_framework.test import APIClient

class PermisosClienteTests(TestCase):
    def setUp(self):
        self.cliente = User.objects.create_user('cliente', 'cliente@example.com', 'password')
        self.pedido = Pedido.objects.create(cliente=self.cliente, pagado=False)
        self.pedido_pagado = Pedido.objects.create(cliente=self.cliente, pagado=True)
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.cliente)

    def test_acceso_pedido_no_pagado(self):
        response = self.api_client.put(f'/api/pedidos/{self.pedido.id}/', {'nuevo': 'dato'})
        self.assertEqual(response.status_code, 200)

    def test_acceso_pedido_pagado(self):
        response = self.api_client.put(f'/api/pedidos/{self.pedido_pagado.id}/', {'nuevo': 'dato'})
        self.assertEqual(response.status_code, 403)