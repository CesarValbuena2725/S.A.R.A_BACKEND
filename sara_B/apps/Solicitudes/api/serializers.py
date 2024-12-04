from rest_framework import serializers
from apps.Solicitudes.models import Solicitud, Cliente, CategoriaServicio


class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields = '__all__'

class ClienteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class CategoriaServicioSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = '__all__'
