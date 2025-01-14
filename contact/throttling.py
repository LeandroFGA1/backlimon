from rest_framework.throttling import BaseThrottle
import time
from django.core.cache import cache


class ContactMessageRateThrottle(BaseThrottle):
    RATE = 5  # Número de solicitudes permitidas
    DURATION = 60 * 60  # Duración en segundos (1 hora)

    cache_format = 'throttle_contact_message_%(ip)s'

    def __init__(self):
        # Inicializa los atributos de instancia
        self.ip_addr = None
        self.key = None
        self.history = []

    def allow_request(self, request, view):
        self.ip_addr = self.get_ident(request)
        self.key = self.cache_format % {'ip': self.ip_addr}
        self.history = cache.get(self.key, [])

        now = time.time()

        # Elimina solicitudes antiguas fuera del período de tiempo
        self.history = [timestamp for timestamp in self.history if timestamp > now - self.DURATION]

        if len(self.history) >= self.RATE:
            return False

        self.history.append(now)
        cache.set(self.key, self.history, self.DURATION)
        return True

    def wait(self):
        """
        Calcula el tiempo de espera hasta que se permita la siguiente solicitud.
        """
        earliest = self.history[0]
        now = time.time()
        remaining_duration = self.DURATION - (now - earliest)
        return remaining_duration

    def get_ident(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
