import re
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


def validate_email(email):
    """Valida si un correo tiene un formato correcto."""
    if email:
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise ValueError("Ingrese un correo electrónico válido.")
    return email


def validate_telefono(telefono):
    """Valida que el número de teléfono tenga entre 8 y 15 dígitos."""
    if telefono:
        if not re.match(r'^\+?\d{8,15}$', telefono):
            raise ValueError("Ingrese un número de teléfono válido.")
    return telefono


def validate_nombre(nombre):
    """Valida que el nombre contenga solo letras y no esté vacío."""
    if not nombre or not nombre.replace(' ', '').isalpha():
        raise ValueError("El nombre debe contener solo letras.")
    return nombre.strip().title()

def validate_apellidos(apellidos):
    """Valida que los apellidos contengan solo letras."""
    if not apellidos or not apellidos.replace(' ', '').isalpha():
        raise ValueError("Los apellidos deben contener solo letras.")
    return apellidos.strip().title()


def validate_nombre_objeto(nombre, min_length=2):
    """
    Valida que un nombre de objeto (como marca, categoría, producto o servicio) sea alfabético
    y tenga una longitud mínima.
    """
    if len(nombre) < min_length:
        raise ValueError(f"El nombre debe tener al menos {min_length} caracteres.")
    if not nombre.isalnum():
        raise ValueError("El nombre debe contener solo caracteres alfabéticos.")
    return nombre.strip()

def validate_precio(precio):
    """Valida que un precio sea mayor o igual a cero."""
    if precio is not None and precio < 0:
        raise ValueError("El precio debe ser mayor o igual a cero.")
    return precio

def validate_cantidad(cantidad, min_value=1):
    """Valida que una cantidad sea al menos igual a un valor mínimo."""
    if cantidad < min_value:
        raise ValueError(f"La cantidad debe ser al menos {min_value}.")
    return cantidad

def validate_longitud_minima(texto, min_length=3):
    """Valida que un texto tenga una longitud mínima."""
    if len(texto.strip()) < min_length:
        raise ValueError(f"El texto debe tener al menos {min_length} caracteres.")
    return texto.strip()

