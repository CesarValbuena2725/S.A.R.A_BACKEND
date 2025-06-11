from rest_framework import serializers
from apps.Result.models import CategoriaOpciones,Opciones, Respuestas
from apps.Utilidades.Permisos import set_serializers
from apps.Requests.models import Solicitud
from apps.Forms.models import Formulario,Items
from apps.Requests.api.tools import listForm
from apps.Forms.models import CreacionFormulario
from django.db import transaction
@set_serializers
class CategoriaOpcionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaOpciones
        fields = '__all__'

@set_serializers
class OpcionesSeralizers(serializers.ModelSerializer):
    class Meta:
        model = Opciones
        fields='__all__'

class RespuestaModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Respuestas
        fields = '__all__'
    
class RespuestaSerializer(serializers.Serializer):
    solicitud = serializers.PrimaryKeyRelatedField(queryset=Solicitud.objects.filter(is_active=True))
    formulario = serializers.PrimaryKeyRelatedField(queryset=Formulario.objects.filter(is_active=True))
    resultados = serializers.JSONField()

    def validate(self, data):
        result = data.get('resultados')
        request = data.get('solicitud')
        form= data.get('formulario')
        
        list_forms= listForm(request)
        if  form.pk not in list_forms:
            raise serializers.ValidationError("Formulario no corresponde")

        if request.estado != "PRO":
            raise serializers.ValidationError("No se pueden registrar respuestas en ese estado")

        if not result or len(result) == 0:
            raise serializers.ValidationError("No se enviaron respuestas")
        if not isinstance(result, list):
            raise serializers.ValidationError("'resultados' debe ser una lista de respuestas")

        for item in result:
            if not len(item)==2:  
                raise serializers.ValidationError("Respuestas incompletas o fuera de rango")

        return data

    def create(self, validated_data):
        solicitud = validated_data['solicitud']
        formulario = validated_data['formulario']
        resultados = validated_data['resultados']
        respuestas = []

        try:
            with transaction.atomic():
                for item_data in resultados:
                    if not isinstance(item_data, list) or len(item_data) != 2:
                        raise serializers.ValidationError(
                            f"Estructura inválida en respuesta: {item_data}. Se esperaba [id_item, id_opcion]"
                        )

                    id_item, id_opcion = item_data

                    data_value= Respuestas.objects.filter(id_solicitud=solicitud, id_formulario=formulario,id_item=id_item)
                    if data_value.exists():
                        raise serializers.ValidationError(f"La solicitud: {solicitud},con el formulario: {formulario} del item:{id_item} ya tiene una respuesta Guardad")

                    if not CreacionFormulario.objects.filter(id_formulario=formulario, id_items=id_item).exists():
                        raise serializers.ValidationError(
                            f"El ítem con ID {id_item} no pertenece al formulario {formulario.id}"
                        )

                    try:
                        item = Items.objects.get(pk=id_item)
                        print(item.id_categoria_opciones)
                    except Items.DoesNotExist:
                        raise serializers.ValidationError(
                            f"El ítem con ID {id_item} no existe en el sistema"
                        )

                    if item.id_categoria_opciones.pk != 16:
                        if not Opciones.objects.filter(id_categoria_opciones=item.id_categoria_opciones, pk=id_opcion).exists():
                            raise serializers.ValidationError(
                                f"La opción con ID {id_opcion} no es válida para el ítem {id_item}"
                            )
                        option = Opciones.objects.get(pk=id_opcion)
                        option2= None
                    else:
                        option = None
                        option2=str(id_opcion)

                    respuesta = Respuestas.objects.create(
                        id_solicitud=solicitud,
                        id_formulario=formulario,
                        id_item=item,
                        id_opcion=option if option else None,
                        respuesta_texto=option2
                    )
                    respuestas.append(respuesta)

        except serializers.ValidationError as ve:
            raise ve
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Error inesperado: {str(e)}"})

        return {'respuestas_creadas': respuestas}
    
    def update(self, instance, validated_data):
        solicitud = validated_data['solicitud']
        formulario = validated_data['formulario']
        resultados = validated_data['resultados']
        respuestas = []
        
        for item_data in resultados:
            id_item, id_opcion = item_data
            
            respuesta = Respuestas.objects.get(
                id_solicitud=solicitud,
                id_formulario=formulario,
                id_item=id_item,
    
            )
            try:
                item = Items.objects.get(pk=id_item)
            except Items.DoesNotExist:
                        raise serializers.ValidationError(
                            f"El ítem con ID {id_item} no existe en el sistema"
                        )

            if item.id_categoria_opciones.pk != 16:

                if not Opciones.objects.filter(id_categoria_opciones=item.id_categoria_opciones, pk=id_opcion).exists():
                    raise serializers.ValidationError(
                                f"La opción con ID {id_opcion} no es válida para el ítem {id_item}"
                            )
                option = Opciones.objects.get(pk=id_opcion)
            else:
                option = None
            
            if respuesta:
                respuesta.id_opcion = option if option else None
                respuesta.respuesta_texto = str(id_opcion) if item.id_categoria_opciones == 16 else None
                respuesta.save()
            
            respuestas.append(respuesta.id)
        
        return {'respuestas_actualizadas': respuestas}



