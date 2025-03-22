from django.urls import path
from .views import CreacionFormularios

urlpatterns = [
    path('crear-formulario/', CreacionFormularios.as_view(), name='crear-formulario'),
]