from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from contact.models import ContactMessage
from contact.views import ContactMessageView
from django.test import RequestFactory

class ContactMessageViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('contact-message')  # Cambia este nombre si usas otro en las rutas
        self.valid_data = {
            "nombre": "Juan",
            "apellidos": "Pérez",
            "email": "juan.perez@example.com",
            "telefono": "+123456789",
            "tipo_contacto": "producto",
            "mensaje": "Este es un mensaje válido.",
            "recaptcha_token": "test_token",
        }
        self.invalid_data = self.valid_data.copy()
        self.invalid_data["mensaje"] = "Corto"  # Mensaje muy corto para fallar la validación

    @patch('contact.views.ContactMessageView.verify_recaptcha')
    def test_post_successful_with_valid_data(self, mock_verify_recaptcha):
        # Simula una respuesta válida de reCAPTCHA
        mock_verify_recaptcha.return_value = {"success": True, "score": 0.9}
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(ContactMessage.objects.count(), 1)

    @patch('contact.views.ContactMessageView.verify_recaptcha')
    def test_post_fails_with_missing_recaptcha(self, mock_verify_recaptcha):
        data = self.valid_data.copy()
        data.pop("recaptcha_token")
        response = self.client.post(self.url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("recaptcha_token", response.data)

    @patch('contact.views.ContactMessageView.verify_recaptcha')
    def test_post_fails_with_invalid_message(self, mock_verify_recaptcha):
        mock_verify_recaptcha.return_value = {"success": True, "score": 0.9}
        response = self.client.post(self.url, data=self.invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mensaje", response.data)

    @patch('contact.views.ContactMessageView.verify_recaptcha')
    def test_post_fails_with_recaptcha_error(self, mock_verify_recaptcha):
        # Simula un error de reCAPTCHA
        mock_verify_recaptcha.return_value = {"success": False, "error-codes": ["invalid-input-response"]}
        response = self.client.post(self.url, data=self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_client_ip(self):
        factory = RequestFactory()

        # Caso 1: Sin cabecera HTTP_X_FORWARDED_FOR
        request = factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        ip = ContactMessageView.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

        # Caso 2: Con cabecera HTTP_X_FORWARDED_FOR
        request = factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 198.51.100.17'
        ip = ContactMessageView.get_client_ip(request)
        self.assertEqual(ip, '203.0.113.195')
