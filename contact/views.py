import requests
from django.conf import settings
from django.db import transaction
from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
#from rest_framework.throttling import ScopedRateThrottle
from .serializers import ContactMessageSerializer
from .models import ContactMessage


class ContactMessageView(views.APIView):
    permission_classes = [AllowAny]
    #TODO: quitar comentario para limitar el número de mensajes por IP
    #throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'contact'
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def post(self, request, *args, **kwargs):
        recaptcha_token = request.data.get("recaptcha_token")
        if not recaptcha_token:
            return Response(
                {"recaptcha_token": ["El token de reCAPTCHA es obligatorio."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        client_ip = self.get_client_ip(request)

        recaptcha_result = self.verify_recaptcha(recaptcha_token, client_ip)

        # Pasamos recaptcha_result al contexto del serializer
        serializer = ContactMessageSerializer(
            data=request.data,
            context={'recaptcha_result': recaptcha_result}
        )

        if serializer.is_valid():
            with transaction.atomic():
                # Guardar el mensaje y el score de reCAPTCHA
                contact_message = serializer.save(
                    ip_address=client_ip,
                    recaptcha_score=recaptcha_result.get("score", 0.0)
                )
            return Response(
                {"message": "Gracias por tu mensaje. Nos pondremos en contacto pronto."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def verify_recaptcha(self, token, remoteip=None):
        """Valida el token de reCAPTCHA con la API de Google."""
        url = "https://www.google.com/recaptcha/api/siteverify"
        data = {
            "secret": settings.RECAPTCHA_PRIVATE_KEY,
            "response": token,
        }
        if remoteip:
            data["remoteip"] = remoteip

        try:
            response = requests.post(url, data=data, timeout=5)
            response.raise_for_status()
            result = response.json()
            if not isinstance(result, dict):
                return {"success": False, "error-codes": ["invalid_response_format"]}

            return result
        except requests.exceptions.Timeout:
            return {"success": False, "error-codes": ["recaptcha_timeout"]}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error-codes": ["recaptcha_request_error", str(e)]}

    @staticmethod
    def get_client_ip(request):
        """Obtiene la dirección IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
