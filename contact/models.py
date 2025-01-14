from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class ContactMessage(models.Model):
    nombre = models.CharField(_('Nombre'), max_length=50)
    apellidos = models.CharField(_('Apellidos'), max_length=50)
    email = models.EmailField(_('Correo electrónico'), blank=True, null=True)
    telefono = models.CharField(
        _('Teléfono'),
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message=_('Ingrese un número de teléfono válido.')
            )
        ]
    )

    class TipoContactoChoices(models.TextChoices):
        PRODUCTO = 'producto', _('Producto')
        SERVICIO = 'servicio', _('Servicio')
        OTRO = 'otros', _('Otros')

    tipo_contacto = models.CharField(
        _('Tipo de contacto'),
        max_length=10,
        choices=TipoContactoChoices.choices
    )
    mensaje = models.TextField(_('Mensaje'))
    fecha_envio = models.DateTimeField(_('Fecha de envío'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('Dirección IP'), blank=True, null=True)
    recaptcha_score = models.DecimalField(_('Score reCAPTCHA'), max_digits=4, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = _('Mensaje de contacto')
        verbose_name_plural = _('Mensajes de contacto')

    def __str__(self):
        return f"{self.nombre} {self.apellidos} - {self.tipo_contacto} ({self.fecha_envio.strftime('%Y-%m-%d %H:%M')})"

    def clean(self):
        super().clean()
        if not self.email and not self.telefono:
            raise ValidationError(_('Debe proporcionar al menos un correo electrónico o un número de teléfono para poder contactarlo.'))

        # Validar que el mensaje no sea demasiado corto
        if len(self.mensaje.strip()) < 10:
            raise ValidationError({'mensaje': _('El mensaje es demasiado corto.')})
