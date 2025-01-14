from django.contrib import admin
from .models import Producto, Marca, Categoria, Pedido, Servicio, DetallePedido

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'precio_producto', 'stock_producto', 'marca', 'descontinuado')
    list_filter = ('marca', 'categorias', 'descontinuado')
    search_fields = ('nombre_producto', 'descripcion_producto')
    ordering = ('nombre_producto',)
    readonly_fields = ('codigo_producto',)

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca', 'descontinuado')
    search_fields = ('nombre_marca',)
    ordering = ('nombre_marca',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'descontinuado')
    search_fields = ('nombre_categoria',)
    ordering = ('nombre_categoria',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_servicio', 'precio_servicio', 'descontinuado')
    list_filter = ('descontinuado', 'categorias')
    search_fields = ('nombre_servicio', 'descripcion_servicio')
    ordering = ('nombre_servicio',)


# 1. Creas un Inline para DetallePedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    # Si quieres mostrar campos específicos, puedes usar `fields = [...]`
    # fields = ('item_type', 'producto', 'servicio', 'cantidad', 'precio')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion', 'completado')
    list_filter = ('completado',)
    search_fields = ('cliente__email', 'cliente_temporal_id')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

    # 2. Agregas el inline a tu PedidoAdmin para visualizar (y editar) los DetallePedido
    inlines = [DetallePedidoInline]


# (Opcional) Si quieres ver DetallePedido también como una sección aparte
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'item_type', 'producto', 'servicio', 'cantidad', 'precio')
    # Puedes filtrar o buscar si lo deseas
    # list_filter = ('item_type',)
    # search_fields = ('producto__nombre_producto', 'servicio__nombre_servicio', 'pedido__id')
