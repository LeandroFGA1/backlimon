from rest_framework import serializers
from .models import Producto, Marca, Categoria, Pedido, Servicio, DetallePedido
from utils.validators import validate_nombre_objeto, validate_precio, validate_cantidad, validate_longitud_minima

from usuarios.models import Usuario  # Asegúrate de importar el modelo correcto


class MarcaSerializer(serializers.ModelSerializer):
    nombre_marca = serializers.CharField(
        validators=[lambda value: validate_nombre_objeto(value, min_length=2)]
    )

    class Meta:
        model = Marca
        fields = '__all__'


    def get_is_active(self, obj):

        return not obj.descontinuado

class CategoriaSerializer(serializers.ModelSerializer):
    nombre_categoria = serializers.CharField(
        validators=[lambda value: validate_nombre_objeto(value, min_length=2)]
    ) 


    class Meta:
        model = Categoria
        fields = '__all__'

    def get_is_active(self, obj):

        return not obj.descontinuado

class ProductoSerializer(serializers.ModelSerializer):
    nombre_producto = serializers.CharField(
        validators=[lambda value: validate_nombre_objeto(value)]
    )
    precio_producto = serializers.FloatField(validators=[validate_precio])
    marca = MarcaSerializer(read_only=True)
    categorias = CategoriaSerializer(many=True, read_only=True)
    class Meta:
        model = Producto
        fields = ['codigo_producto','nombre_producto','descripcion_producto', 'precio_producto',
                  'stock_producto', 'categorias', 'marca']


    def validate_stock_producto(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value


class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = '__all__'
    def validate(self, data):
        item_type = data.get('item_type')
        producto = data.get('producto')
        cantidad = data.get('cantidad', 1)

        if item_type == 'producto' and producto:
            if cantidad > producto.stock_producto:
                raise serializers.ValidationError({
                    "cantidad": f"No hay suficiente stock para {producto.nombre_producto}, ña."
                })
        return data

    def has_object_permission(self, request, view, obj):
        # obj es un DetallePedido
        # Así que el pedido es obj.pedido

        # Caso 1: usuario autenticado
        if request.user.is_authenticated:
            return obj.pedido.cliente == request.user

        # Caso 2: usuario no autenticado
        # Suponiendo que guardaste en request.user.username el cliente_temporal_id
        return obj.pedido.cliente_temporal_id == request.user.username


class PedidoSerializer(serializers.ModelSerializer):
    # Este campo manejará todos los detalles
    detalles_pedido = DetallePedidoSerializer(many=True, required=False)

    total_computado = serializers.SerializerMethodField()
    cliente = serializers.PrimaryKeyRelatedField(required=False, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'cliente_temporal_id', 'pagado', 'fecha_creacion', 'fecha_despacho',
            'fecha_entrega', 'estado', 'completado', 'direccion_envio', 'tracking_number',
            'total', 'detalles_pedido', 'total_computado'
        ]

    def create(self, validated_data):
        # Sacamos la data de detalles (si viene)
        detalles_data = validated_data.pop('detalles_pedido', [])

        # Creamos el Pedido
        pedido = Pedido.objects.create(**validated_data)

        # Creamos cada DetallePedido
        for detalle in detalles_data:
            DetallePedido.objects.create(pedido=pedido, **detalle)

        # Ajustamos el total al final
        pedido.actualizar_total()
        return pedido

    def update(self, instance, validated_data):
        detalles_data = validated_data.pop('detalles_pedido', None)

        instance = super().update(instance, validated_data)

        if detalles_data is not None:

            instance.detalles_pedido.all().delete()
            for detalle in detalles_data:
                DetallePedido.objects.create(pedido=instance, **detalle)

            instance.actualizar_total()

        return instance

    def get_total_computado(self, obj):
        return obj.total

    def validate(self, data):
        if data.get('estado') == 'cancelado' and data.get('pagado', False):
            raise serializers.ValidationError("No se puede cancelar un pedido que ya ha sido pagado.")
        return data


class ServicioSerializer(serializers.ModelSerializer):
    categorias = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), many=True, required=False
    )
    nombre_servicio = serializers.CharField(
        validators=[lambda value: validate_nombre_objeto(value, min_length=3)]
    )
    descripcion_servicio = serializers.CharField(validators=[lambda value: validate_longitud_minima(value, min_length=3)])
    class Meta:
        model = Servicio
        fields = [
            'id', 'nombre_servicio', 'descripcion_servicio', 'categorias', 'descontinuado'
        ]


    def create(self, validated_data):
        categorias_data = validated_data.pop('categorias', None)
        servicio = Servicio.objects.create(**validated_data)
        if categorias_data:
            servicio.categorias.set(categorias_data)
        return servicio

    def update(self, instance, validated_data):
        categorias_data = validated_data.pop('categorias', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if categorias_data:
            instance.categorias.set(categorias_data)
        instance.save()
        return instance