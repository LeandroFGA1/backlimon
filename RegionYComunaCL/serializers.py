# serializers.py
from rest_framework import serializers
from .models import Region, Comuna

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'nombre']

class ComunaSerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    class Meta:
        model = Comuna
        fields = ['id', 'nombre', 'region']
