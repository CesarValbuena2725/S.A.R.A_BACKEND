from rest_framework import serializers
from apps.Access.models import Empleado
from apps.Requests.models import Solicitud, Plan,TipoVehiculo
from apps.Utilidades.permisos import Set_Serializers
from apps.Forms.models import FormularioPlan,Formulario
from rest_framework.exceptions import APIException
from django.db import transaction
from apps.Utilidades.General.validations import ValidateFields

class SolicitudSerializers(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
        fields='__all__'
        read_only_fields = ['fecha']  # Bloquea escritura, pero permite lectura

    # Funciones para las validaciones 
    def validate_placa(self, value):
        return ValidateFields().validate(value,"PLACA")
    
    def validate_telefono(self, value):
        return ValidateFields().validate(value,"TEL")
    
    def validate_id_convenio(self, value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_sucursal(self, value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_empleado(self, value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_plan(self, value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_tipo_vehiculo(self, value):
        return ValidateFields().Validate_Relacion(value)

    # Validación general
    def validate(self, data):
        # Validar modificación de Placa
        if self.instance and 'Placa' in data:
            raise serializers.ValidationError({"Placa": "No modificable después de creación."})

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
    def validate_nombre_plan(self, value):
        return ValidateFields().validate(value,"STRING")
    def validate_id_tipo_vehiculo(self, value):
        return ValidateFields().Validate_Relacion(value)

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
    # Se reciben los IDs de planes
    planes = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.all(), 
        many=True, 
        write_only=True
    )

    class Meta:
        model = TipoVehiculo
        fields = '__all__'

    def validate_nombre_vehiculo(self, value):
        return ValidateFields().validate(value, "STRING")
    
    def create(self, validated_data):
        # Sacamos planes del diccionario para que no cause error en el modelo
        planes = validated_data.pop("planes", [])
        tipo_vehiculo = TipoVehiculo.objects.create(**validated_data)

        # Crear relaciones en la tabla intermedia

        return tipo_vehiculo
    
    def update(self, instance, validated_data):
        # Igual que en create, pero actualizando
        planes = validated_data.pop("planes", None)
        instance.nombre_vehiculo = validated_data.get("nombre_vehiculo", instance.nombre_vehiculo)
        instance.save()



        return instance

    
