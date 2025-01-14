from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .models import Producto, Marca, Categoria, Pedido, Servicio, DetallePedido
from .serializers import (ProductoSerializer, MarcaSerializer, CategoriaSerializer, PedidoSerializer,
                          ServicioSerializer, DetallePedidoSerializer)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductoItemPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Verificar si el pedido tiene un cliente autenticado
        if obj.pedido.cliente:
            cliente = obj.pedido.cliente
        else:
            # Si no hay cliente, usamos cliente_temporal_id
            cliente = obj.pedido.cliente_temporal_id

        # Compara el cliente (autenticado o temporal) con el usuario actual
        if cliente == request.user or cliente == request.user.username:
            return True
        return False

class IsStaffOrItemOwner(permissions.BasePermission):
    """
    Permite al personal modificar cualquier ítem y a los clientes solo ver los ítems de sus propios pedidos.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # Verifica si el usuario es el propietario del pedido asociado al ítem
        return obj.pedido.cliente == request.user or (
                obj.pedido.cliente_temporal_id and
                obj.pedido.cliente_temporal_id == request.session.get('cliente_temporal_id'))


class CanCreatePedido(permissions.BasePermission):
    """
    Permite a cualquier usuario crear pedidos, pero restringe la modificación y eliminación a solo personal,
    y permite a los usuarios ver solo sus propios pedidos.
    """

    def has_permission(self, request, view):
        # Permitir creación de pedidos solo para solicitudes POST.
        if request.method == 'POST':
            return True
        # Permitir acceso solo al personal o en métodos seguros para otros usuarios
        return request.user.is_staff or request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        # Permitir al personal acceso completo
        if request.user.is_staff:
            return True

        # obj es DetallePedido, así que el pedido asociado está en obj.pedido
        pedido = obj.pedido

        # Permitir acceso seguro (GET/HEAD/OPTIONS) solo al cliente del pedido
        # o al cliente temporal asociado
        if request.method in permissions.SAFE_METHODS:
            # Si no hay pedido, deniega
            if not pedido:
                return False

            es_cliente_registrado = (pedido.cliente == request.user)
            es_cliente_temporal = (
                    pedido.cliente_temporal_id
                    and pedido.cliente_temporal_id == request.session.get('cliente_temporal_id')
            )

            return es_cliente_registrado or es_cliente_temporal

        # Restringir modificaciones para todos excepto staff (arriba) o tu lógica
        return False


class ReadOnly(permissions.BasePermission):
    """
    Permite acceso de sólo lectura a cualquier usuario a productos, servicios, categorías y marcas.
    """

    def has_permission(self, request, view):
        # Permitir todos los métodos seguros (GET, HEAD, OPTIONS) que no modifiquen los datos.
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        # Aplicar la misma lógica a nivel de objeto.
        return request.method in permissions.SAFE_METHODS


class ProductoViewSet(viewsets.ModelViewSet):
    serializer_class = ProductoSerializer
    permission_classes = [ReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre_producto', 'descripcion_producto']
    ordering_fields = ['precio_producto', 'nombre_producto']
    queryset = Producto.objects.select_related('marca').prefetch_related('categorias').all()
    pagination_class = StandardResultsSetPagination

    @action(detail=True, methods=['get'])
    def related_products(self, request, pk=None):
        producto = self.get_object()
        related_products = Producto.objects.filter(categorias__in=producto.categorias.all().distinct())
        page = self.paginate_queryset(related_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(related_products, many=True, context={'request': request})
        return Response(serializer.data)


class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all().prefetch_related('productos')
    serializer_class = MarcaSerializer
    permission_classes = [ReadOnly]


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().prefetch_related('productos')
    serializer_class = CategoriaSerializer
    permission_classes = [ProductoItemPermission]


class DetallePedidoViewSet(viewsets.ModelViewSet):
    queryset = DetallePedido.objects.all()
    serializer_class = DetallePedidoSerializer
    permission_classes = [CanCreatePedido]  # O la que tu lógica indique

    def get_queryset(self):
        """
        Filtra los DetallesPedido asociados al usuario autenticado
        o al 'cliente_temporal_id' si no está autenticado.
        """
        if self.request.user.is_authenticated:
            return DetallePedido.objects.filter(pedido__cliente=self.request.user)
        else:
            # Aquí asumes que el 'username' del usuario anónimo
            # se está usando como cliente_temporal_id
            # (o la lógica que tengas para identificarlo).
            return DetallePedido.objects.filter(pedido__cliente_temporal_id=self.request.user.username)

    def perform_create(self, serializer):
        # Si el usuario está autenticado, no hay problema
        if self.request.user.is_authenticated:
            serializer.save()  # Esto supone que 'pedido' llega en la data o lo asignas de algún otro modo
        else:
            # Caso usuario no autenticado.
            # Revisamos si en la data viene un pedido asociado. Si no viene, creamos uno.
            pedido_existente = serializer.validated_data.get('pedido', None)

            if not pedido_existente:
                # Creamos un nuevo Pedido sin cliente
                # El ID temporal se generará en el save() de Pedido gracias a generar_cliente_temporal_id()
                nuevo_pedido = Pedido()
                nuevo_pedido.save()  # Aquí se genera 'cliente_temporal_id' si no hay cliente

                # Una vez creado, guardamos el DetallePedido con ese pedido
                serializer.save(pedido=nuevo_pedido)
            else:
                # Si sí hay un pedido en la data, se usa tal cual
                serializer.save()

    def perform_update(self, serializer):
        detalle = self.get_object()
        # Si tuvieras alguna lógica de restricción para actualización,
        # puedes colocarla aquí. Por ejemplo:
        if detalle.pedido.pagado:
            raise PermissionDenied("No se pueden modificar ítems de un pedido pagado.")
        serializer.save()

    def perform_destroy(self, instance):
        # Lógica de validación antes de borrar el detalle, si hace falta:
        if instance.pedido.pagado:
            raise PermissionDenied("No se pueden eliminar ítems de un pedido pagado.")
        instance.delete()


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    permission_classes = [CanCreatePedido]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_creacion', 'total']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Pedido.objects.all()
        elif self.request.user.is_authenticated:
            return Pedido.objects.filter(cliente=self.request.user)
        else:
            # En caso de usuario no autenticado
            return Pedido.objects.filter(cliente__isnull=False)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(cliente=self.request.user)
        else:
            # Generar un identificador temporal para el cliente no autenticado (o lo que tu lógica requiera)
            serializer.save(cliente_temporal_id=None)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.estado == 'enviado' and not self.request.user.is_staff:
            raise PermissionDenied("Solo el personal puede modificar pedidos ya enviados.")
        if instance.pagado:
            raise PermissionDenied("No se puede modificar un pedido que ya ha sido pagado.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.estado != 'pendiente' and not self.request.user.is_staff:
            raise PermissionDenied("No se pueden eliminar pedidos no pendientes a menos que sea personal.")
        if instance.pagado:
            raise PermissionDenied("No se puede eliminar un pedido que ya ha sido pagado.")
        instance.delete()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pagado or instance.estado == 'enviado':
            return Response({'error': 'No se puede modificar un pedido que ya ha sido pagado o enviado.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pagado or instance.estado == 'enviado':
            return Response({'error': 'No se puede eliminar un pedido que ya ha sido pagado o enviado.'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [ReadOnly]

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Solo el personal puede crear servicios.")
        serializer.save()

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Solo el personal puede actualizar servicios.")
        serializer.save()
