from rest_framework.views import APIView
from apps.Forms.api.serializers import CreateFormsSerializers
from rest_framework import status, generics
from rest_framework.response import Response
from apps.Forms.models import Formulario, CreacionFormulario,Items,FormularioPlan
from apps.Forms.api.serializers import CreacionFormularioSerializers, FormularioSerializers, ItemsSerializers
from apps.Requests.models import Plan
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from apps.Utilidades.CRUD import BaseGeneral
from apps.Result.models import Opciones
from apps.Result.api.serializers import OpcionesSeralizers


class PostCreateForms(APIView):
    serializer_class = CreateFormsSerializers

    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            formulario = serializer.save()

            return Response(formulario, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateForms(APIView):
    
    def get(self, request, pk):
        try:
            # Obtener el formulario
            nombre_formulario = Formulario.objects.get(pk=pk)
        except Formulario.DoesNotExist:
            return Response({'Error': f"Este formulario no existe: {pk}"}, status=status.HTTP_404_NOT_FOUND)

        # Serializar el formulario
        formulario_serializer = FormularioSerializers(nombre_formulario)

        # Obtener los ítems relacionados desde CreacionFormulario
        items_relacionados = CreacionFormulario.objects.filter(id_formulario=nombre_formulario)
        print(items_relacionados)
        items_serializer = CreacionFormularioSerializers(items_relacionados, many=True)

        return Response({
            "nombre_formulario": formulario_serializer.data,
            "items": items_serializer.data
        }, status=status.HTTP_200_OK)


    def patch(self, request, pk): # Funcion para Actualiacion parcial de los Datos.
        try:
            # Obtener la instancia del formulario
            instance = Formulario.objects.get(pk=pk)
        except Formulario.DoesNotExist:
            return Response({'Error': f"Este formulario no existe: {pk}"}, status=status.HTTP_404_NOT_FOUND)

        # Validar datos parciales con el serializer del Formulario
        formulario_serializer = FormularioSerializers(instance, data=request.data, partial=True)

        if formulario_serializer.is_valid():
            try:
                with transaction.atomic():
                    formulario_serializer.save()  # Guardamos los cambios en Formulario
                    
                    if 'items' in request.data:
                        for item_data in request.data['items']:
                            try:
                                # Buscar la relación en la tabla intermedia
                                creacion_instance = CreacionFormulario.objects.get(
                                    id_formulario=instance, id_items=item_data['id']
                                )

                                # Obtener la instancia del ítem real
                                item_instance = creacion_instance.id_items  

                                # Serializar y actualizar el ítem
                                item_serializer = ItemsSerializers(item_instance, data=item_data, partial=True)

                                if item_serializer.is_valid():
                                    item_serializer.save()
                                else:
                                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                            except CreacionFormulario.DoesNotExist:
                                return Response({'Error': f"El item con id {item_data['id']} no está asociado al formulario."}, 
                                                status=status.HTTP_404_NOT_FOUND)

                    return Response({"Mensaje": "Formulario e ítems actualizados con éxito"}, status=status.HTTP_200_OK)
                    
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(formulario_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                            

class DeleteForms(APIView):

    def delete(self,request,pk):
        try:

            instanacia= Formulario.objects.get(pk=pk)
            creacionformulario =  CreacionFormulario.objects.filter(id_formulario=instanacia.pk)

        except Formulario.DoesNotExist:
            return Response({'Errors':f"Form key not exist: {pk}"},status=status.HTTP_404_NOT_FOUND)
        
        #serralizers  = CreacionFormularioSerializers(creacionformulario,many=True)
        try:
            with transaction.atomic():

                for items  in  creacionformulario: #Elimina Cada items de cada formulario
                    delete_items= Items.objects.filter(pk=items.id_items.pk)
                    delete_items.delete()
                creacionformulario.delete()
                instanacia.delete()
                return Response({"Exito":"El formulario Fue eliminado"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'Errors':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class ShowForms(APIView):
    
    def get(self, request, pk):
        try:
            plan = Plan.objects.get(pk=pk)

            formularios_ids = FormularioPlan.objects.filter(id_plan=pk).values_list("id_formulario", flat=True)
            if not formularios_ids:
                return Response("No se encontraron formularios relacionados", status=status.HTTP_204_NO_CONTENT)

            formularios = Formulario.objects.filter(pk__in=formularios_ids)
            response_data = []

            for formulario in formularios:
                # Obtener los ítems del formulario
                items_ids = Items.objects.filter(
                    pk__in=CreacionFormulario.objects.filter(id_formulario=formulario.pk).values_list("id_items", flat=True)
                )

                # Serializar los ítems para poder relacion las opciones
                serialized_items = []
                for item in items_ids:
                    opciones_ids = Opciones.objects.filter(id_categoria_opciones=item.id_categoria_opciones)

                    serialized_item = ItemsSerializers(item).data
                    #Dentro de Cada item, Creamos el campo opciones 
                    serialized_item["opciones"] = OpcionesSeralizers(opciones_ids, many=True).data 
                    #Agremos todo al principal
                    serialized_items.append(serialized_item)
                    
                #Agregamos  todo a las respueta 
                response_data.append({
                    "formulario": FormularioSerializers(formulario).data,
                    "items": serialized_items,
                })

            return Response(response_data, status=status.HTTP_200_OK)

        except Plan.DoesNotExist:
            return Response("Plan no existe, validar PK enviado", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
