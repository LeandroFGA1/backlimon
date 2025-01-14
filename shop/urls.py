from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet,
    CategoriaViewSet,
    MarcaViewSet,
    PedidoViewSet,
    ServicioViewSet,
    DetallePedidoViewSet,  # Asegúrate de haberlo importado
)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='productos')
router.register(r'categorias', CategoriaViewSet, basename='categorias')
router.register(r'marcas', MarcaViewSet, basename='marcas')
router.register(r'pedidos', PedidoViewSet, basename='pedidos')
router.register(r'servicios', ServicioViewSet, basename='servicios')

# Ahora en vez de producto-items y servicio-items, usas un solo 'detalles-pedido'
router.register(r'detalles-pedido', DetallePedidoViewSet, basename='detalles-pedido')

urlpatterns = [
    path('', include(router.urls)),
]
