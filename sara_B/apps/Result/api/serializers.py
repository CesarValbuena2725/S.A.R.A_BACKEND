from rest_framework import serializers
from apps.Result.models import CategoriaOpciones,Opciones, Respuestas,Fotos
from apps.Utilidades.permisos import Set_Serializers
from apps.Utilidades.General.validations import ValidateFields
from apps.Requests.models import Solicitud
from apps.Forms.models import Formulario,Items
from apps.Requests.api.tools import List_Form
from apps.Forms.models import CreacionFormulario
from django.db import transaction


@Set_Serializers
class CategoriaOpcionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaOpciones
        fields = '__all__'

    def validate_nombre(self, value):
        return ValidateFields().Validate_Relacion(value)

@Set_Serializers
class OpcionesSeralizers(serializers.ModelSerializer):
    class Meta:
        model = Opciones
        fields='__all__'

    def validate_nombre_opcion(self, value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_categoria_opciones(self, value):
        return ValidateFields().Validate_Relacion(value)

class RespuestaModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Respuestas
        fields = '__all__'

    def validate_id_solicitud(self,value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_formulario(self,value):
        return ValidateFields().Validate_Relacion(value)
    
    def validate_id_item(self,value):
        return ValidateFields().Validate_Relacion(value)




    
class RespuestaSerializer(serializers.Serializer):
    #Se relacion los Serializer del los modelos necesarios, con sus respectivas restriciones 
    solicitud = serializers.PrimaryKeyRelatedField(queryset=Solicitud.objects.filter(is_active=True))
    formulario = serializers.PrimaryKeyRelatedField(queryset=Formulario.objects.filter(is_active=True))
    resultados = serializers.JSONField()

    def validate_solicitud(self, value):
        return ValidateFields().Validate_Relacion(value)
    def validate_formulario(self, value):
        return ValidateFields().Validate_Relacion(value)

    def validate(self, data):
        result = data.get('resultados')
        request = data.get('solicitud')
        form= data.get('formulario')
        #Se llama la funcion que lista los formularios correspodientes al plan de la solicitud
        list_forms= List_Form(request)
        if  form.pk not in list_forms:
            raise serializers.ValidationError("Formulario no corresponde")
        # Se validan estado de la solicitud
        if request.estado != "PRO":
            raise serializers.ValidationError("No se pueden registrar respuestas en ese estado")
        # Se Valida que si el fornato de [Repuesta, items], todos Vengas con respuestas agregdas 
        if not result or len(result) == 0:
            raise serializers.ValidationError("No se enviaron respuestas")
        # Se validan que vengas en el formatos Esperado
        if not isinstance(result, list):
            raise serializers.ValidationError("'resultados' debe ser una lista de respuestas")
        # Se validan que no vengas Datos que no correspoenden 
        for item in result:
            if not len(item)==2:  
                raise serializers.ValidationError("Respuestas incompletas o fuera de rango")

        return data

    def create(self, validated_data):
        #DEspues de Validar la informacion se separa segun los modelos o necesidad para Facilidad de procesar 
        solicitud = validated_data['solicitud']
        formulario = validated_data['formulario']
        resultados = validated_data['resultados']
        respuestas = []

        try:
            #Se uitliza que todo el proceso se cumplime y el caso que no se desangan los cambios hechos 
            with transaction.atomic(): 
                # Se Vuelve a validar la estructura de la respuesta
                for item_data in resultados:
                    if not isinstance(item_data, list) or len(item_data) != 2:
                        raise serializers.ValidationError(
                            f"Estructura inválida en respuesta: {item_data}. Se esperaba [id_item, id_opcion]"
                        )

                    id_item, id_opcion = item_data

                    data_value= Respuestas.objects.filter(id_solicitud=solicitud, id_formulario=formulario,id_item=id_item)
                    
                    # Se validan que el item enviado si corresponda con el formulario y la solicitud

                    if not CreacionFormulario.objects.filter(id_formulario=formulario, id_items=id_item).exists():
                        raise serializers.ValidationError(
                            f"El ítem con ID {id_item} no pertenece al formulario {formulario.id}"
                        )

                    try:
                        # Se valida que el item enviado si exista en la base de datos
                        item = Items.objects.get(pk=id_item)
                    
                    except Items.DoesNotExist:
                        raise serializers.ValidationError(
                            f"El ítem con ID {id_item} no existe en el sistema"
                        )
                    # Se la categoria del items en en blanco no debe tener Opcion enviada 
                    if item.id_categoria_opciones.pk != 16:
                        if not Opciones.objects.filter(id_categoria_opciones=item.id_categoria_opciones, pk=id_opcion).exists():
                            raise serializers.ValidationError(
                                f"La opción con ID {id_opcion} no es válida para el ítem {id_item}"
                            )
                        # El caso  que el categoria lo permita se instancia y se deja la respuesta dos en blaco
                        option = Opciones.objects.get(pk=id_opcion)
                        option2= None
                    else:
                        # Del caso contrario se toma la repuesta libre y se guarda 
                        option = None
                        option2=str(id_opcion)
                    # Se registran las repuestas Segun corresponda, si corresponde a categoria de opciones se registra la respuesta 1 o  2
                    respuesta = Respuestas.objects.create(
                        id_solicitud=solicitud,
                        id_formulario=formulario,
                        id_item=item,
                        id_opcion=option if option else None,
                        respuesta_texto=option2
                    )
                    # Se agrega todo a ala varible que contrendra la repuesta 
                    respuestas.append(respuesta)

        except serializers.ValidationError as ve:
            raise ve
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Error inesperado: {str(e)}"})
        # en le data se responde 
        return {'respuestas_creadas': respuestas}
    
    def update(self, instance, validated_data):
        # Se obtiene la informacion Validad 
        solicitud = validated_data['solicitud']
        formulario = validated_data['formulario']
        resultados = validated_data['resultados']
        respuestas = []
        # Se recoren las repuestas y se validan
        for item_data in resultados:
            id_item, id_opcion = item_data
            
            respuesta = Respuestas.objects.get(
                id_solicitud=solicitud,
                id_formulario=formulario,
                id_item=id_item,
    
            )
            # Se hacen las mismas Validaciones que en al funcion Create 
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
            # Se hacen las correspondientes Actualizaciones 
            if respuesta:
                respuesta.id_opcion = option if option else None
                respuesta.respuesta_texto = str(id_opcion) if item.id_categoria_opciones.pk == 16 else None
                respuesta.save()
            
            respuestas.append(respuesta.id)
        
        return {'respuestas_actualizadas': respuestas}
    

class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fotos
        fields =  '__all__'
        
    def validate(self, data):
        solicitud = data.get("id_solicitud")
        if (Fotos.objects.filter(id_solicitud= solicitud)):
            raise serializers.ValidationError("Ya existe una foto guardad para esta solicitud")
        return data


