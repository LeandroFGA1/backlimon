import requests
from django.conf import settings
from rest_framework import serializers

class RecaptchaValidator:
    """
    Clase para validar el token de Recaptcha vía API de Google.
    """
    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    @staticmethod
    def validate(token, remote_ip=None):
        if not token:
            raise serializers.ValidationError("El token de reCAPTCHA es obligatorio.")

        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': token,
        }
        if remote_ip:
            data['remoteip'] = remote_ip

        try:
            response = requests.post(RecaptchaValidator.VERIFY_URL, data=data)
            response.raise_for_status()
            result = response.json()
            if not result.get("success", False) or result.get("score", 0) < 0.5:
                raise serializers.ValidationError("La verificación de reCAPTCHA falló.")
        except requests.RequestException as e:
            raise serializers.ValidationError(f"Fallo al verificar reCAPTCHA: {str(e)}")

        return result

