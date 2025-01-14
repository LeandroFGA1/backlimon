from django.contrib.auth.models import BaseUserManager
from decouple import config
class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password is None or password.strip() == "":
            raise ValueError('La contraseña es obligatoria para crear un usuario.')
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, auth_password=None, **extra_fields):

        required_password = config('SUPERUSER_AUTH_PASSWORD', default=None)

        if required_password is None:
            raise ValueError('La contraseña de autenticación para superusuarios no está configurada.')
        if not auth_password or auth_password != required_password:
            raise ValueError('No tienes permiso para crear un superusuario. Contraseña inválida.')
        if not password:
            raise ValueError('La contraseña del superusuario no puede estar vacía.')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
