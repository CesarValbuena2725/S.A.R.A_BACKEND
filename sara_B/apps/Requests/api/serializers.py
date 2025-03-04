from rest_framework import serializers
from apps.Requests.models import Solicitud, Plan, VehiculoPlan,TipoVehiculo



class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model =Solicitud
        exclude = ['fecha']
        read_only_fields = ['Placa', 'id_empleado']  # Campos que no se pueden modificar

  
    def validate(self, data):

        id_plan = data.get("id_plan")
        id_tipo_vehiculo = data.get("id_tipo_vehiculo")

        if id_plan and id_tipo_vehiculo:
            exists = VehiculoPlan.objects.filter(id_plan=id_plan, id_vehiculo=id_tipo_vehiculo).exists()
            if not exists:
                raise serializers.ValidationError("La combinación de Plan y Tipo de Vehículo no es válida.")

        return data

class PlanSerializers(serializers.ModelSerializer):

    class Meta:
        model= Plan
        fields= '__all__'

class TipovehiculoSerializers(serializers.ModelSerializer):
    class Meta:
        model= TipoVehiculo
        fields= '__all__'

class VehiculoplanSerializers(serializers.ModelSerializer):
    class Meta:
        model= VehiculoPlan
        fields='__all__'