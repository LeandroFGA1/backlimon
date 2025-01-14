"""
URL configuration for ecosustentable project.

The `urlpatterns` list routes URLs to views.py. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views.py
    1. Add an import:  from my_app import views.py
    2. Add a URL to urlpatterns:  path('', views.py.home, name='home')
Class-based views.py
    1. Add an import:  from other_app.views.py import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import index

urlpatterns = [
    # Ruta del panel de administración
    path('admin/', admin.site.urls),

    # Rutas de la API
    path('api/', include('shop.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/', include('contact.urls')),
    path('api/RegionYComunaCL/', include('RegionYComunaCL.urls')),
    # Rutas de autenticación JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Ruta para la página de inicio
    path('', index, name='index'),
]
