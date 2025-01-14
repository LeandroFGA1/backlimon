from django.core.management.base import BaseCommand, CommandError
from usuarios.models  import (Usuario)
from decouple import config


class Command(BaseCommand):
    help = 'Crea un superusuario después de verificar la contraseña de autorización'

    def handle(self, *args, **kwargs):
        email = input("Email: ")

        # Solicitar y confirmar la contraseña del superusuario
        while True:
            password = input("Password del superusuario: ")
            password_confirm = input("Confirma el password del superusuario: ")
            if password == password_confirm:
                break
            else:
                self.stderr.write("Las contraseñas no coinciden. Inténtalo nuevamente.")

        # Solicitar la contraseña de autorización
        auth_password = input("Password de autorización: ")

        # Verificar la contraseña de autorización desde el .env
        required_password = config('SUPERUSER_AUTH_PASSWORD', default=None)

        if not required_password:
            raise CommandError("La contraseña de autorización no está configurada en el entorno.")

        if auth_password != required_password:
            raise CommandError("La contraseña de autorización es incorrecta.")

        # Crear el superusuario
        try:
            Usuario.objects.create_superuser(email=email, password=password, auth_password=auth_password)
            self.stdout.write(self.style.SUCCESS(f'Superusuario {email} creado exitosamente'))
        except Exception as e:
            raise CommandError(str(e))
