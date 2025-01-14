from django.core.exceptions import ValidationError
from itertools import cycle
from django.core.validators import validate_email as django_validate_email
from .models import Cliente
import regex as re


def validate_run_dv(run, dv):
    try:
        reversed_digits = map(int, reversed(str(run)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        expected_dv = (-s) % 11
        if expected_dv == 10:
            expected_dv = 'K'
        else:
            expected_dv = str(expected_dv)

        if dv.upper() != expected_dv:
            raise ValidationError(f"El dígito verificador no es válido para el RUN proporcionado. Esperado: {expected_dv}, Obtenido: {dv}")

    except ValueError:
        raise ValidationError("El RUN debe contener sólo dígitos.")

def validate_email(value):
    value = value.lower().strip()

    try:
        django_validate_email(value)
    except ValidationError as e:
        raise ValidationError(f"Email inválido: {str(e)}")

    if Cliente.objects.filter(email=value).exists():
        raise ValidationError("Este email ya está registrado.")

    domain = value.split('@')[-1]
    blacklisted_domains = ["example.com", "invalid.com"]
    if domain in blacklisted_domains:
        raise ValidationError("Registros desde este dominio no están permitidos.")

    return value

def validate_name(value):
    if not re.match(r'^\p{L}+\s*\p{L}*$', value):
        raise ValidationError("Este campo debe contener solo letras y espacios.")
    return value.strip().title()