from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, LogoutView, CustomTokenObtainPairView

# Configura el DefaultRouter para gestionar los ViewSets
router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='clientes')  # Registra un ViewSet para 'clientes'

urlpatterns = [
    # Incluir las rutas gestionadas por el router
    path('', include(router.urls)),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    # Endpoint para cerrar sesión
    path('logout/', LogoutView.as_view(), name='logout'),
]
