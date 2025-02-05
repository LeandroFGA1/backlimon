# Generated by Django 5.1.4 on 2024-12-30 15:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_pedido_cliente_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='productos',
        ),
        migrations.RemoveField(
            model_name='servicioitem',
            name='pedido',
        ),
        migrations.RemoveField(
            model_name='servicioitem',
            name='servicio',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='servicios',
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('producto', 'Producto'), ('servicio', 'Servicio')], max_length=10)),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio', models.PositiveIntegerField(blank=True, null=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles_pedido', to='shop.pedido')),
                ('producto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.producto')),
                ('servicio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.servicio')),
            ],
        ),
        migrations.DeleteModel(
            name='ProductoItem',
        ),
        migrations.DeleteModel(
            name='ServicioItem',
        ),
    ]
