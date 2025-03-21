from rest_framework import serializers
from apps.Forms.models import Formulario,CategoriaOpciones,Items,FormularioPlan,CreacionFormulario
from apps.Requests.models import Plan
from apps.Utilidades.Permisos import set_serializers
from rest_framework.exceptions import APIException
from django.db import transaction

@set_serializers
class CategoriaOpcionesSerializers(serializers.ModelSerializer):
    class Meta:
        model= CategoriaOpciones
        fields= '__all__'


@set_serializers
class ItemsSerializers(serializers.ModelSerializer):
    id_categoria_opciones = serializers.PrimaryKeyRelatedField(queryset=CategoriaOpciones.objects.all())

    class Meta:
        model = Items
        fields= '__all__'


@set_serializers
class FormularioSerializers(serializers.ModelSerializer):
    class Meta:
        model = Formulario
        fields= '__all__'
@set_serializers
class FormularioPlanSerializers(serializers.ModelSerializer):
    class Meta:
        model=FormularioPlan
        fields='__all__'

@set_serializers
class CreacionFormularioSerializers(serializers.ModelSerializer):
    class Meta:
        model = CreacionFormulario
        fields = '__all__'



class CreateFormsSerializers(serializers.Serializer):

        formulario = FormularioSerializers() 
        items = ItemsSerializers(many=True)
        plan = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all())

        def validate(self, data):

            # Validar los datos del formulario usando FormularioSerializers

            formulario_data = data.get('formulario')
            formulario_serializer = FormularioSerializers(data=formulario_data)
            if not formulario_serializer.is_valid():
                raise serializers.ValidationError({"formulario": formulario_serializer.errors})

            # Validar los ítems
            items_data = data.get('items', [])

            for item_data in items_data:
                if not isinstance(item_data, dict):
                    raise serializers.ValidationError({"items": "Each item must be a JSON object."})

            return data

        def create(self, validated_data):
            form_data = validated_data.get('formulario')
            items_data = validated_data.get('items', [])
            plan_data = validated_data.get('plan')

            if not plan_data:
                raise serializers.ValidationError({"plan": f"invalidad Plan {plan_data} NOT Exist"})

            if not form_data:
                raise serializers.ValidationError({"formulario": "Invalid data, Verify data "})
            
            try:

                with transaction.atomic(): #obliga  que todo se complete con exito, de lo contrario no guarda nada 

                # Crear Formulario
                    formulario = Formulario.objects.create(**form_data)
                    if formulario:
                    # Relacionar Formulario con Plan
                        formulario_plan = FormularioPlan.objects.create(id_formulario=formulario, id_plan=plan_data)

                    # Crear Items y asociarlos al Formulario
                    created_items = []

                    for item_data in items_data:

                        item = Items.objects.create(
                            nombre_items=item_data["nombre_items"],
                            descripcion=item_data["descripcion"],
                            id_categoria_opciones=item_data.get('id_categoria_opciones'))
                                
                        CreacionFormulario.objects.create(id_formulario=formulario, id_items=item)
                        created_items.append(item)

            except Exception as e:
                    
                raise APIException({"detail": f"Error al procesar la solicitud: {str(e)}"})

            return {
            "formulario": FormularioSerializers(formulario).data,
            "items": ItemsSerializers(created_items, many=True).data,
        }
