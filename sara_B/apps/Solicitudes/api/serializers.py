from rest_framework import serializers
from apps.Solicitudes.models import Solicitud,  CategoriaServicio


class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        exclude = ['fecha']  # Aquí defines los campos a excluir, si es necesario.

    def update(self, instance, validated_data):
        allowed_field = 'estado'

        if allowed_field in validated_data:
            setattr(instance, allowed_field, validated_data[allowed_field])

        instance.save()
        return instance
    
class CategoriaServicioSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = '__all__'
