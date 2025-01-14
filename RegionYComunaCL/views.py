# views.py
from rest_framework import viewsets
from .models import Region, Comuna
from .serializers import RegionSerializer, ComunaSerializer
from .permissions import IsStaffOrAdmin
class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    #permission_classes = [IsStaffOrAdmin]

class ComunaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Comuna.objects.all()
    serializer_class = ComunaSerializer
    #permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        # Obtiene el parámetro `region_id` de la solicitud
        region_id = self.request.query_params.get('id_region')
        # Filtra las comunas si `region_id` está presente en la solicitud
        if region_id:
            return Comuna.objects.filter(region_id=region_id)
        # Si no hay `region_id`, devuelve todas las comunas
        return Comuna.objects.all()