from rest_framework.exceptions import ValidationError as DRFValidationError
from django.test import TestCase
from contact.serializers import ContactMessageSerializer
from contact.models import ContactMessage


class ContactMessageSerializerTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "nombre": "Juan",
            "apellidos": "Pérez",
            "email": "juan.perez@example.com",
            "telefono": "+123456789",
            "tipo_contacto": "producto",
            "mensaje": "Este es un mensaje válido.",
            "recaptcha_token": "test_token"
        }
        self.context = {
            "recaptcha_result": {
                "success": True,
                "score": 0.9
            }
        }

    def test_serializer_valid_data(self):
        serializer = ContactMessageSerializer(data=self.valid_data, context=self.context)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_invalid_without_email_and_phone(self):
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = None
        invalid_data["telefono"] = None
        serializer = ContactMessageSerializer(data=invalid_data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Debe proporcionar al menos un correo electrónico o un número telefónico.", str(serializer.errors))

    def test_serializer_invalid_message_with_links(self):
        invalid_data = self.valid_data.copy()
        invalid_data["mensaje"] = "Visita http://example.com para más información."
        serializer = ContactMessageSerializer(data=invalid_data, context=self.context)
        self.assertFalse(serializer.is_valid())
        self.assertIn("El mensaje no debe contener enlaces.", str(serializer.errors))

    def test_serializer_invalid_recaptcha_failure(self):
        context_with_failure = {
            "recaptcha_result": {
                "success": False
            }
        }
        serializer = ContactMessageSerializer(data=self.valid_data, context=context_with_failure)
        self.assertFalse(serializer.is_valid())
        self.assertIn("La verificación de reCAPTCHA falló.", str(serializer.errors))

    def test_serializer_invalid_recaptcha_low_score(self):
        context_with_low_score = {
            "recaptcha_result": {
                "success": True,
                "score": 0.4
            }
        }
        serializer = ContactMessageSerializer(data=self.valid_data, context=context_with_low_score)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Actividad sospechosa detectada.", str(serializer.errors))

    def test_create_removes_recaptcha_token(self):
        serializer = ContactMessageSerializer(data=self.valid_data, context=self.context)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertIsInstance(instance, ContactMessage)
        self.assertNotIn("recaptcha_token", vars(instance))
