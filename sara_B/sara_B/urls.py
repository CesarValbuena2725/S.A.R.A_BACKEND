"""
URL configuration for sara_B project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('access/', include('apps.Access.api.urls')),
    path('request/', include('apps.Requests.api.urls')),

    # Tres rutas generales para manejar el teme de tokes y refrecos del mismo,Son rutas predefinidad por la libreria Simple-JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Obtener Access y Refresh Token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refrescar Access Token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Verificar si el Access Token es válido
]

