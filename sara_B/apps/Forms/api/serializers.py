from rest_framework import serializers
from apps.Forms.models import Formulario,Items,FormularioPlan,CreacionFormulario
from apps.Requests.models import Plan
from apps.Utilidades.Permisos import set_serializers
from rest_framework.exceptions import APIException
from django.db import transaction
from apps.Result.models import CategoriaOpciones



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
                        try:
                            categoria = CategoriaOpciones.objects.get(pk=item_data.get('id_categoria_opciones').pk)
                        except CategoriaOpciones.DoesNotExist:
                            raise serializers.ValidationError(
                                {"items": f"Invalid CategoriaOpciones {item_data['id_categoria_opciones']} NOT Exist."})
                        
                        item = Items.objects.create(
                            nombre_items=item_data["nombre_items"],
                            descripcion=item_data["descripcion"],
                            id_categoria_opciones=categoria)
                                
                        CreacionFormulario.objects.create(id_formulario=formulario, id_items=item)
                        created_items.append(item)

            except Exception as e:
                    
                raise APIException({"detail": f"Error al procesar la solicitud: {str(e)}"})

            return {
            "formulario": FormularioSerializers(formulario).data,
            "items": ItemsSerializers(created_items, many=True).data,
        }

        
        
        def update(self, instance, validated_data):
            try:
                with transaction.atomic():
                    
                    formulario_data = validated_data.get("formulario", {})
                    instance.nombre_formulario = formulario_data.get("nombre_formulario", instance.nombre_formulario)
                    instance.save()

                    
                    creacion_formulario_data = formulario_data.get("creacion_formulario", [])

                    
                    items_actuales = set(instance.creacionformulario_set.values_list('id_items_id', flat=True))
                    items_nuevos = set()

                    for item_data in creacion_formulario_data:
                        item_id = item_data.get("id")
                        nuevo_nombre = item_data.get("nombre_item")

                        try:
                           
                            creacion_instance = CreacionFormulario.objects.get(id_formulario=instance, id_items_id=item_id)
                            item_instance = creacion_instance.id_items

                            
                            if nuevo_nombre:
                                item_instance.nombre_items = nuevo_nombre
                                item_instance.save()

                            # Guardamos el ID en los nuevos ítems enviados
                            items_nuevos.add(item_id)

                        except CreacionFormulario.DoesNotExist:
                            raise serializers.ValidationError({
                                "creacion_formulario": f"El ítem con id {item_id} no está relacionado con este formulario."
                            })

                    
                    items_a_eliminar = items_actuales - items_nuevos
                    CreacionFormulario.objects.filter(id_formulario=instance, id_items_id__in=items_a_eliminar).delete()

            except Exception as e:
                raise APIException({"detail": f"Error al actualizar: {str(e)}"})

            
            return {
                "formulario": FormularioSerializers(instance).data,
                "creacion_formulario": [
                    {
                        "id": cf.id,
                        "nombre_item": cf.id_items.nombre_items
                    } for cf in instance.creacionformulario_set.all()
                ]
            }



            
