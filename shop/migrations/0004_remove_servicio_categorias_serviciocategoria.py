# Generated by Django 5.1.3 on 2024-12-01 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_producto_categorias'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='categorias',
        ),
        migrations.CreateModel(
            name='ServicioCategoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categoria_servicios', to='shop.categoria')),
                ('servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicio_categorias', to='shop.servicio')),
            ],
            options={
                'unique_together': {('servicio', 'categoria')},
            },
        ),
    ]
