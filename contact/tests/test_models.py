from django.test import TestCase
from contact.models import ContactMessage
from django.core.exceptions import ValidationError


class ContactMessageModelTest(TestCase):

    def setUp(self):
        self.valid_data = {
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan.perez@example.com',
            'telefono': '+123456789',
            'tipo_contacto': ContactMessage.TipoContactoChoices.PRODUCTO,
            'mensaje': 'Este es un mensaje de prueba con suficiente longitud.',
            'ip_address': '127.0.0.1',
            'recaptcha_score': 0.9
        }

    def test_model_can_be_created_with_valid_data(self):
        contact_message = ContactMessage.objects.create(**self.valid_data)
        self.assertEqual(contact_message.nombre, 'Juan')
        self.assertEqual(contact_message.tipo_contacto, ContactMessage.TipoContactoChoices.PRODUCTO)

    def test_clean_raises_error_if_no_email_or_phone(self):
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = None
        invalid_data['telefono'] = None
        contact_message = ContactMessage(**invalid_data)
        with self.assertRaises(ValidationError) as e:
            contact_message.clean()
        self.assertIn('Debe proporcionar al menos un correo electrónico o un número de teléfono', str(e.exception))

    def test_clean_raises_error_if_message_is_too_short(self):
        invalid_data = self.valid_data.copy()
        invalid_data['mensaje'] = 'Corto'
        contact_message = ContactMessage(**invalid_data)
        with self.assertRaises(ValidationError) as e:
            contact_message.clean()
        self.assertIn('El mensaje es demasiado corto', str(e.exception))

    def test_meta_options(self):
        self.assertEqual(ContactMessage._meta.verbose_name, 'Mensaje de contacto')
        self.assertEqual(ContactMessage._meta.verbose_name_plural, 'Mensajes de contacto')
        self.assertEqual(ContactMessage._meta.ordering, ['-fecha_envio'])

    def test_str_representation(self):
        contact_message = ContactMessage.objects.create(**self.valid_data)
        expected_str = f"Juan Pérez - producto ({contact_message.fecha_envio.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(contact_message), expected_str)
