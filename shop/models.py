from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import hashlib
import os
from django.utils import timezone
import hmac
from django.db.models import Sum

class Marca(models.Model):
    nombre_marca = models.CharField(max_length=150, unique=True)
    descontinuado = models.BooleanField(default=False)

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre_marca

    def set_nombre(self, nombre):
        self.nombre_marca = nombre
        self.save()

    def get_descontinuado(self):
        return self.descontinuado

    def set_descontinuado(self, valor):
        self.descontinuado = valor
        self.save()

    def __str__(self):
        return self.nombre_marca


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=150, unique=True)
    descontinuado = models.BooleanField(default=False)

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre_categoria

    def set_nombre(self, nombre):
        self.nombre_categoria = nombre
        self.save()

    def get_descontinuado(self):
        return self.descontinuado

    def set_descontinuado(self, valor):
        self.descontinuado = valor
        self.save()

    def __str__(self):
        return self.nombre_categoria


class Servicio(models.Model):
    codigo_servicio = models.CharField(max_length=100, unique=True)
    nombre_servicio = models.CharField(max_length=100, unique=True)
    descripcion_servicio = models.TextField()
    categorias = models.ManyToManyField(Categoria, through='ServicioCategoria', related_name='servicios')
    descontinuado = models.BooleanField(default=False)
    precio_servicio = models.PositiveIntegerField()

    def clean(self):
        # Validación de nombre_servicio
        if not self.nombre_servicio or len(self.nombre_servicio) < 3:
            raise ValidationError("El nombre del servicio debe tener al menos 3 caracteres.")

        # Validación de descripcion_servicio
        if not self.descripcion_servicio or len(self.descripcion_servicio) < 3:
            raise ValidationError("La descripción del servicio debe tener al menos 3 caracteres.")

    @property
    def get_categoria(self):
        return self.categorias.all()

    def add_categoria(self, categoria):
        if not self.categorias.filter(id=categoria.id).exists():
            ServicioCategoria.objects.create(servicio=self, categoria=categoria)

    @transaction.atomic
    def change_categoria(self, categoria_antigua, categoria_nueva):
        relacion = ServicioCategoria.objects.filter(servicio=self, categoria=categoria_antigua).first()
        if relacion:
            relacion.categoria = categoria_nueva
            relacion.save()

    def remove_categoria(self, categoria):
        ServicioCategoria.objects.filter(servicio=self, categoria=categoria).delete()

    def __str__(self):
        return self.nombre_servicio

    def get_id(self):
        return self.id

    def get_nombre(self):
        return self.nombre_servicio

    def set_nombre(self, nombre):

        if not nombre:
            raise ValueError("El nombre del servicio no puede estar vacío.")

        if len(nombre) < 3:
            raise ValueError("El nombre del servicio debe tener al menos 3 caracteres.")

        nombre = nombre.lower()

        if self.nombre_servicio != nombre:
            self.nombre_servicio = nombre
        self.save(update_fields=['nombre_servicio'])

    def get_descripcion(self):
        return self.descripcion_servicio

    def set_descripcion(self, descripcion):

        if not descripcion:
            raise ValueError("La descripción del servicio no puede estar vacía.")

        if len(descripcion) < 3:
            raise ValueError("La descripción del servicio debe tener al menos 3 caracteres.")
        self.descripcion_servicio = descripcion
        self.save(update_fields=['descripcion_servicio'])

    def get_descontinuado(self):
        return self.descontinuado

    def set_descontinuado(self, valor):
        self.descontinuado = valor
        self.save()

class Producto(models.Model):
    codigo_producto = models.CharField(max_length=100, unique=True)
    nombre_producto = models.CharField(max_length=150)
    descripcion_producto = models.TextField()
    precio_producto = models.PositiveIntegerField()
    stock_producto = models.PositiveIntegerField()
    descontinuado = models.BooleanField(default=False)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name='productos')
    categorias = models.ManyToManyField(Categoria, through='ProductoCategoria')

    # Métodos relacionados con stock
    def ajustar_stock(self, cantidad):
        """Ajusta el stock del producto a la cantidad especificada."""
        if cantidad < 0:
            raise ValueError("El stock no puede ser negativo.")
        self.stock_producto = cantidad
        self.save(update_fields=['stock_producto'])

    # Métodos relacionados con precio
    def ajustar_precio(self, precio):
        """Ajusta el precio del producto."""
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.precio_producto = precio
        self.save(update_fields=['precio_producto'])


    def ajustar_nombre(self, nombre):
        if not nombre:
            raise ValueError("El nombre del producto no puede estar vacío.")
        if len(nombre) < 3:
            raise ValueError("El nombre del producto debe tener al menos 3 caracteres.")
        nombre = nombre.lower()
        if self.nombre_producto != nombre:
            self.nombre_producto = nombre
            self.save(update_fields=['nombre_producto'])

    # Métodos relacionados con categorías
    def agregar_categoria(self, categoria):
            """
            Agrega una categoría al producto a través del modelo intermedio.
            Si ya está asociada, no hace nada.
            """
            ProductoCategoria.objects.get_or_create(producto=self, categoria=categoria)


    @transaction.atomic
    def cambiar_categoria(self, categoria_antigua, categoria_nueva):
            """
            Reemplaza una categoría antigua con una nueva para este producto.
            """
            ProductoCategoria.objects.filter(producto=self, categoria=categoria_antigua).delete()
            self.agregar_categoria(categoria_nueva)

    def eliminar_categoria(self, categoria):
            """
            Elimina una categoría asociada al producto.
            """
            ProductoCategoria.objects.filter(producto=self, categoria=categoria).delete()

    @property
    def listado_categorias(self):
            """
            Devuelve una lista de nombres de categorías asociadas al producto.
            """
            return [relacion.categoria.nombre_categoria for relacion in ProductoCategoria.objects.filter(producto=self)]

            # Métodos relacionados con marca

    def actualizar_marca(self, nueva_marca):
        """Actualiza la marca del producto."""
        self.marca = nueva_marca
        self.save(update_fields=['marca'])

        # Métodos relacionados con descontinuación

    def marcar_descontinuado(self, valor):
        """Marca el producto como descontinuado o activo."""
        self.descontinuado = valor
        self.save(update_fields=['descontinuado'])

    @property
    def estado_descontinuado(self):
        """Devuelve si el producto está descontinuado o no."""
        return "Descontinuado" if self.descontinuado else "Activo"



    def clean(self):
        super().clean()
        if self.precio_producto < 0:
            raise ValidationError("El precio del producto no puede ser negativo.")
        if self.stock_producto < 0:
            raise ValidationError("El stock del producto no puede ser negativo.")
        if not self.codigo_producto.strip():
            raise ValidationError("El código del producto no puede estar vacío.")
        if len(self.nombre_producto) < 3:
            raise ValidationError("El nombre del producto debe tener al menos 3 caracteres.")

    def __str__(self):
        """Representación en texto del producto."""
        categorias = ', '.join(self.listado_categorias) if self.categorias.exists() else "Sin categorías"
        return (
            f"{self.nombre_producto} (Código: {self.codigo_producto}) - "
            f"Precio: ${self.precio_producto}, Stock: {self.stock_producto}, "
            f"Marca: {self.marca}, Categorías: {categorias}, Estado: {self.estado_descontinuado}"
        )

class ProductoCategoria(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='producto_categorias')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'categoria')

    def save(self, *args, **kwargs):
        if not self.pk and ProductoCategoria.objects.filter(producto=self.producto, categoria=self.categoria).exists():
            raise ValidationError('Este producto ya está asociado a esta categoría.')
        super().save(*args, **kwargs)

class ServicioCategoria(models.Model):
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, related_name='servicio_categorias')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='categoria_servicios')

    class Meta:
        unique_together = ('servicio', 'categoria')

    def __str__(self):
        return f"{self.servicio.nombre_servicio} - {self.categoria.nombre_categoria}"

class Pedido(models.Model):


    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En Preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET,
        null=True,
        blank=True,
        related_name='pedidos'
    )
    cliente_temporal_id = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        blank=True,

        help_text="ID único para clientes no registrados"
    )
    pagado = models.BooleanField(default=False, help_text="Indica si el pedido ha sido pagado completamente.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_despacho = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        default='pendiente',
        choices=ESTADO_CHOICES
    )
    completado = models.BooleanField(default=False)
    direccion_envio = models.TextField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=False, null=True)
    total = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"Pedido {self.id} de {self.cliente if self.cliente else 'Cliente Temporal'}"

    def actualizar_total(self):
        nuevo_total = 0
        for detalle in self.detalles_pedido.all():
            nuevo_total += detalle.subtotal()
        if self.total != nuevo_total:
            self.total = nuevo_total
            self.save(update_fields=['total'])

    def cliente_email(self):
        """Devuelve el email del cliente registrado o indica si es un cliente temporal"""
        return self.cliente.email if self.cliente and hasattr(self.cliente, 'email') else "Cliente Temporal"

    cliente_email.short_description = "Email del Cliente"

    def save(self, *args, **kwargs):
        # Si no hay cliente registrado, asignamos un cliente temporal y generamos su ID.
        if not self.cliente:
            if not self.cliente_temporal_id:
                self.cliente_temporal_id = self.generar_cliente_temporal_id()
        # Si el cliente está registrado, asignamos su dirección de envío por defecto.
        elif not self.direccion_envio and hasattr(self.cliente, 'direccion'):
            self.direccion_envio = self.cliente.direccion

        super().save(*args, **kwargs)

    def generar_cliente_temporal_id(self):
        """Genera un identificador único alfanumérico utilizando HMAC con SHA-256 para mayor seguridad."""
        # Clave secreta que deberías guardar de manera segura y no hardcodear en el código
        secret_key = b'my_secret_key'  # Asegúrate de manejar esta clave de forma segura

        # Datos que combinamos para hacer el hash
        datos = (f"{self.direccion_envio or ''}{timezone.now().isoformat()}"
                 f"{self.tracking_number or ''}{os.urandom(16).hex()}")

        # Crear un nuevo HMAC utilizando la clave secreta y los datos, usando SHA-256 como el algoritmo de hash
        hmac_hash = hmac.new(secret_key, datos.encode(), hashlib.sha256).hexdigest()
        # Tomar los primeros 20 caracteres del hash
        identificador_unico = hmac_hash[:20]

        return identificador_unico

    def actualizar_estado(self, nuevo_estado):
        if nuevo_estado == 'entregado' and not self.fecha_despacho:
            raise ValidationError("No se puede marcar como entregado sin una fecha de despacho.")
        self.estado = nuevo_estado
        self.save()

    def get_info(self):
        return f"Pedido {self.id} creado el {self.fecha_creacion}"

    def get_fecha_despacho(self):
        return self.fecha_despacho

    def get_fecha_entrega(self):
        return self.fecha_entrega

    def get_productos(self):
        return self.productos.all()

    def get_completado(self):
        return self.completado

    def set_fecha_despacho(self, fecha):
        self.fecha_despacho = fecha
        self.save()

    def set_fecha_entrega(self, fecha):
        self.fecha_entrega = fecha
        self.save()

    def set_completado(self, valor):
        self.completado = valor
        self.save()

    def cancelar_pedido(self):
        if self.pagado:
            raise ValidationError("No se puede cancelar un pedido que ya ha sido pagado.")
        if self.estado in ['entregado', 'cancelado']:
            raise ValidationError(f"No se puede cancelar un pedido que ya está {self.estado}.")

        # Cancelar productos (los que tengan item_type='producto')
        detalles_producto = self.detalles_pedido.filter(item_type='producto')
        for detalle in detalles_producto:
            if detalle.producto:
                detalle.producto.stock_producto += detalle.cantidad
                detalle.producto.save()

        self.estado = 'cancelado'
        self.completado = True
        self.save()

    def clean(self):
        super().clean()
        if self.estado == 'entregado' and not self.fecha_despacho:
            raise ValidationError(
                {'fecha_despacho': "No se puede marcar un pedido como entregado sin una fecha de despacho."})
        if self.pagado and self.estado == 'cancelado':
            raise ValidationError({'estado': "No se puede cancelar un pedido que ya ha sido pagado."})



class DetallePedido(models.Model):
    PEDIDO_ITEM_CHOICES = [
        ('producto', 'Producto'),
        ('servicio', 'Servicio')
    ]

    pedido = models.ForeignKey('Pedido', related_name='detalles_pedido', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10, choices=PEDIDO_ITEM_CHOICES)
    producto = models.ForeignKey('Producto', on_delete=models.SET_NULL, null=True, blank=True)
    servicio = models.ForeignKey('Servicio', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.PositiveIntegerField(null=True, blank=True)

    def subtotal(self):
        return self.cantidad * (self.precio or 0)

    def clean(self):
        """
        Asegúrate de que haya stock suficiente antes de confirmar el guardado
        (aplica sólo para productos).
        """
        super().clean()

        if self.item_type == 'producto' and self.producto:
            if self.cantidad > self.producto.stock_producto:
                raise ValidationError("No hay suficiente stock para este producto")

    def save(self, *args, **kwargs):
        """
        Actualiza el stock del producto si es la primera vez que se está guardando este detalle.
        """
        # Llama a las validaciones
        self.full_clean()

        # Si no tiene 'pk', significa que se está creando un registro nuevo
        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        # Si es un nuevo detalle y es de tipo producto, descuenta el stock
        if es_nuevo and self.item_type == 'producto' and self.producto:
            self.producto.stock_producto -= self.cantidad
            self.producto.save()

    def __str__(self):
        if self.item_type == 'producto' and self.producto:
            return f"{self.cantidad} x {self.producto.nombre_producto} (Pedido {self.pedido.id})"
        elif self.item_type == 'servicio' and self.servicio:
            return f"{self.cantidad} x {self.servicio.nombre_servicio} (Pedido {self.pedido.id})"
        else:
            return f"Detalle de pedido {self.id}"
