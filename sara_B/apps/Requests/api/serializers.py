from rest_framework import serializers
from apps.Requests.models import Solicitud, Plan, VehiculoPlan,TipoVehiculo



class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model =Solicitud
        exclude = ['fecha']
        read_only_fields = ['Placa', 'id_empleado']  # Campos que no se pueden modificar

<<<<<<< HEAD
  
=======
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'data' in kwargs: #Validos los datos De entrda 
            id_vehiculos= kwargs['data'].get('id_tipo_vehiculo') #invocamos los datos dados

            if id_vehiculos: #verificamos que los datos sean validos 
                planes_ids = VehiculoPlan.objects.filter(
                    id_vehiculo=id_vehiculos
                ).values_list('id_plan', flat=True) #filtamos los planes seguin el tipo de Vehiclo y los convertimos en listas 


                self.fields['id_plan'].queryset = Plan.objects.filter(id__in=planes_ids) #le asignaos las posibles opciones a id_plan

    def validate_id_tipo_vehiculo(self,value):
        if not TipoVehiculo.objects.filter(id=value).exists():
            raise serializers.ValidationError("El tipo de vehiculo no existe")
        return value

>>>>>>> cesar
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