# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, ComunaViewSet

router = DefaultRouter()
router.register(r'region', RegionViewSet)
router.register(r'comuna', ComunaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
