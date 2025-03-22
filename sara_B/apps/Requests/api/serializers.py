from rest_framework import serializers
from apps.Requests.models import Solicitud, Plan, VehiculoPlan,TipoVehiculo
from apps.Utilidades.Permisos import set_serializers

class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model =Solicitud
        exclude = ['fecha']
        read_only_fields = ['Placa']  # Campos que no se pueden modificar

  
    def validate(self, data):

        id_plan = data.get("id_plan")
        id_tipo_vehiculo = data.get("id_tipo_vehiculo")

        if id_plan and id_tipo_vehiculo:
            exists = VehiculoPlan.objects.filter(id_plan=id_plan, id_vehiculo=id_tipo_vehiculo).exists()
            if not exists:
                raise serializers.ValidationError("La combinación de Plan y Tipo de Vehículo no es válida.")
        return data

@set_serializers
class PlanSerializers(serializers.ModelSerializer):

    class Meta:
        model= Plan
        fields= '__all__'
        
@set_serializers
class TipovehiculoSerializers(serializers.ModelSerializer):
    planes = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all(), many=True, write_only=True)

    class Meta:
        model= TipoVehiculo
        fields= '__all__'

    def create(self, validated_data):
        planes = validated_data.pop("planes", [])
        tipo_vehiculo = TipoVehiculo.objects.create(**validated_data)

        for plan_id in planes:
            VehiculoPlan.objects.create(id_vehiculo=tipo_vehiculo, id_plan=plan_id)

        return tipo_vehiculo
    
    def update(self, instance, validated_data):
        planes = validated_data.pop("plan", None)
        instance.nombre_vehiculo = validated_data.get("nombre_vehiculo", instance.nombre_vehiculo)
        instance.save()

        if planes is not None:
            VehiculoPlan.objects.filter(tipo_vehiculo=instance).delete()
            for plan_id in planes:
                VehiculoPlan.objects.create(tipo_vehiculo=instance, plan=plan_id)

        return instance
    
    
@set_serializers
class VehiculoplanSerializers(serializers.ModelSerializer):

    class Meta:
        model= VehiculoPlan
        fields='__all__'