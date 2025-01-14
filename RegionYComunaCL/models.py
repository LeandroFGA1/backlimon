from django.db import models


class Region(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'region'  # Reemplaza con el nombre real de la tabla
        managed = False  # Django no intentará crear ni modificar esta tabla


class Comuna(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, db_column='id_region')  # Llave foránea

    class Meta:
        db_table = 'comuna'
        managed = False



