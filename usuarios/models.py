from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
from .managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class Cliente(models.Model):
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente_profile', null=True)
    primer_nombre = models.CharField(max_length=20)
    segundo_nombre = models.CharField(max_length=20, null=True, blank=True)
    primer_apellido = models.CharField(max_length=20)
    segundo_apellido = models.CharField(max_length=20)
    run = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{7,8}$', message='El RUN debe tener entre 7 y 8 dígitos')]
    )
    dv = models.CharField(
        max_length=1,
        validators=[RegexValidator(regex='^[0-9Kk]$', message='DV debe ser un número o K')]
    )
    region = models.CharField(max_length=100)
    comuna = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    es_cliente = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['primer_nombre']
        indexes = [
            models.Index(fields=['run']),
        ]


    def get_full_name(self):
        nombres = [self.primer_nombre, self.segundo_nombre, self.primer_apellido, self.segundo_apellido]
        return ' '.join(filter(None, nombres))

    def get_short_name(self):
        return self.primer_nombre



