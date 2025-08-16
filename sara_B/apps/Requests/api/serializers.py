from rest_framework import serializers
from apps.Access.models import Empleado
from apps.Requests.models import Solicitud, Plan, VehiculoPlan,TipoVehiculo
from apps.Utilidades.Permisos import Set_Serializers
from apps.Forms.models import FormularioPlan,Formulario
from rest_framework.exceptions import APIException
from django.db import transaction

class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields='__all__'
        read_only_fields = ['fecha']  # Bloquea escritura, pero permite lectura

    # Validación de empleado
    def validate_id_empleado(self, value):
        if value.estado == "IN":
            raise serializers.ValidationError("Empleado inactivo.")
        return value

    # Validación general
    def validate(self, data):
        # Validar modificación de Placa
        #if self.instance and 'Placa' in data:
         #   raise serializers.ValidationError({"Placa": "No modificable después de creación."})

        # Validar convenio
        if data.get("id_convenio") and data["id_convenio"].estado == 'IN':
            raise serializers.ValidationError({"id_convenio": "Convenio inactivo."})

        # Validar sucursal
        if data.get("id_sucursal") and data["id_sucursal"].estado == 'IN':
            raise serializers.ValidationError({"id_sucursal": "Sucursal inactiva."})

        plan = data["id_plan"]
        tipo_vehiculo = data["id_tipo_vehiculo"]

        if plan.id_tipo_vehiculo != tipo_vehiculo:
            raise serializers.ValidationError({
                "id_plan": "Combinación inválida con el tipo de vehículo."
            })

        return data
    
@Set_Serializers
class PlanSerializers(serializers.ModelSerializer):
    # Campos Espcial que permite un  agregar un campo que  cumple las caractetircas indicadas 
    lista_adicionales = serializers.PrimaryKeyRelatedField(
        queryset=Formulario.objects.filter(id_categoria=3),
        many=True
    )

    class Meta:
        model = Plan
        fields = '__all__'


    def create(self, data):
        list_adic = data.get('lista_adicionales', [])
        data.pop('lista_adicionales', None)  
        # NOTE: Obliga a que toda  se ejecute bien o devuelos los cambios hechos hasta el error 
        with transaction.atomic():
            instance = Plan.objects.create(**data)
            instance.lista_adicionales.set(list_adic)

            try:
                # Registra a reacion de los planes y los formularios en la table intermedia 
                for formulario in list_adic:
                    FormularioPlan.objects.create(id_plan=instance, id_formulario=formulario)

                questions = Formulario.objects.filter(id_categoria=instance.cuestionario)

                for formulario in questions:
                    FormularioPlan.objects.create(id_plan=instance, id_formulario=formulario)

            except Exception as e:
                raise APIException({"detail": f"Error al Proceesar la Creacion : {str(e)}"})

        return instance
    
    def update(self, instance, validated_data):
        lista_adic = validated_data.pop('lista_adicionales', None)
        cuestionario_nuevo = validated_data.get('cuestionario', instance.cuestionario)

        with transaction.atomic():
            # Actualizar campos simples
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # Actualizar M2M lista_adicionales
            if lista_adic is not None:
                instance.lista_adicionales.set(lista_adic)

            try:
                # Eliminar relaciones previas del plan
                FormularioPlan.objects.filter(id_plan=instance).delete()

                # Relacionar adicionales nuevos si fueron enviados
                if lista_adic:
                    FormularioPlan.objects.bulk_create([
                        FormularioPlan(id_plan=instance, id_formulario=formulario)
                        for formulario in lista_adic
                    ])

                # Agregar los formularios del cuestionario (si cambió o si es inicial)
                questions = Formulario.objects.filter(id_categoria=cuestionario_nuevo)

                FormularioPlan.objects.bulk_create([
                    FormularioPlan(id_plan=instance, id_formulario=formulario)
                    for formulario in questions
                ])

            except Exception as e:
                raise APIException({"detail": f"Error al procesar la actualización: {str(e)}"})

        return instance



@Set_Serializers
class TipovehiculoSerializers(serializers.ModelSerializer):
    planes = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all(), many=True, write_only=True)

    class Meta:
        model= TipoVehiculo
        fields= '__all__'

    def create(self, validated_data):
        
        tipo_vehiculo = TipoVehiculo.objects.create(**validated_data)
        planes = validated_data.get("planes", [])

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
    
    
@Set_Serializers
class VehiculoplanSerializers(serializers.ModelSerializer):

    class Meta:
        model= VehiculoPlan
        fields='__all__'