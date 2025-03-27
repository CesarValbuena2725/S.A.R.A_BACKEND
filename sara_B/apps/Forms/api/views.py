from rest_framework.views import APIView
from apps.Forms.api.serializers import CreateFormsSerializers
from rest_framework import status, generics
from rest_framework.response import Response
from apps.Forms.models import Formulario, CreacionFormulario,Items
from apps.Forms.api.serializers import CreacionFormularioSerializers, FormularioSerializers, ItemsSerializers
from django.db import transaction

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
