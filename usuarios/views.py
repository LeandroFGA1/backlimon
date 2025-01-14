#from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
#import requests
from .models import Cliente
from .serializers import ClienteSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite el acceso solo al propietario del objeto o a administradores.
    """
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes_by_action = {
        'create': [permissions.AllowAny],
        'list': [permissions.IsAdminUser],
        'retrieve': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'update': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'partial_update': [permissions.IsAuthenticated, IsOwnerOrAdmin],
        'destroy': [permissions.IsAdminUser],
    }

    def get_permissions(self):
        """
        Asigna permisos basados en la acción que se está ejecutando.
        """
        permission_classes = self.permission_classes_by_action.get(self.action, self.permission_classes)
        return [permission() for permission in permission_classes]



    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user != instance and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Token de actualización no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Token no válido."}, status=status.HTTP_400_BAD_REQUEST)