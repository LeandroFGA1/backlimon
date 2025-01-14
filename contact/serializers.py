from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from utils.validators import validate_email, validate_telefono, validate_nombre, validate_apellidos
from .models import ContactMessage
import re


class ContactMessageSerializer(serializers.ModelSerializer):
    recaptcha_token = serializers.CharField(write_only=True, required=True)

    nombre = serializers.CharField(
        validators=[validate_nombre],
        required=True,
        allow_blank=False
    )
    apellidos = serializers.CharField(
        validators=[validate_apellidos],
        required=True,
        allow_blank=False
    )
    email = serializers.EmailField(
        validators=[validate_email],
        required=False,
        allow_null=True,
    )
    telefono = serializers.CharField(
        validators=[validate_telefono],
        required=False,
        allow_null=True,
    )
    mensaje = serializers.CharField(
        min_length=10,
        required=True,
        allow_blank=False
    )

    class Meta:
        model = ContactMessage
        fields = ['nombre', 'apellidos', 'email', 'telefono', 'tipo_contacto', 'mensaje', 'recaptcha_token']
        extra_kwargs = {
            'nombre': {'required': True, 'allow_blank': False},
            'apellidos': {'required': True, 'allow_blank': False},
            'tipo_contacto': {'required': True},
            'mensaje': {'required': True, 'allow_blank': False, 'min_length': 10},
        }

    def validate(self, data):
        # Asegurar que al menos email o teléfono estén presentes
        if not data.get("email") and not data.get("telefono"):
            raise serializers.ValidationError(
                "Debe proporcionar al menos un correo electrónico o un número telefónico.")

        # Prevenir enlaces en el mensaje para reducir spam
        mensaje = data.get("mensaje", "").lower()
        if 'http' in mensaje or 'www' in mensaje:
            raise serializers.ValidationError({"mensaje": "El mensaje no debe contener enlaces."})

        # Validación de reCAPTCHA usando el contexto
        recaptcha_result = self.context.get('recaptcha_result')
        if not recaptcha_result:
            raise serializers.ValidationError({"recaptcha_token": "No se pudo verificar el token de reCAPTCHA."})

        if not recaptcha_result.get("success", False):
            raise serializers.ValidationError({"recaptcha_token": "La verificación de reCAPTCHA falló."})

        score = recaptcha_result.get("score", 0.0)
        if score < 0.5:
            raise serializers.ValidationError(
                {"recaptcha_token": "Actividad sospechosa detectada. Por favor, inténtalo de nuevo."})

        return data

    def create(self, validated_data):
        validated_data.pop('recaptcha_token', None)
        return super().create(validated_data)
