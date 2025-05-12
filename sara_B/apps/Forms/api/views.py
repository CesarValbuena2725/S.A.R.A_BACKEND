# Standard library imports
from django.db import transaction

# Third-party imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local application imports
from apps.Forms.api.serializers import (
    CreateFormsSerializers,
    CreacionFormularioSerializers,
    FormularioSerializers,
    ItemsSerializers
)
from apps.Forms.models import CreacionFormulario, Formulario, FormularioPlan, Items
from apps.Requests.models import Plan
from apps.Result.api.serializers import OpcionesSeralizers
<<<<<<< HEAD
from apps.Result.models import Opciones
from apps.Utilidades.CRUD import FiltroGeneral
from apps.Utilidades.Permisos import BASE_PERMISOSOS, RolePermission
=======
from apps.Utilidades.CRUD import FiltroGeneral
>>>>>>> 6f4fada2946dbe24874cd592161ebf6e6d534496


class PostCreateForms(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA',] 
    serializer_class = CreateFormsSerializers

    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            formulario = serializer.save()

            return Response(formulario, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateForms(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA',] 
    
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

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA',] 

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





class ShowForms(generics.ListAPIView):
<<<<<<< HEAD

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = BASE_PERMISOSOS


=======
>>>>>>> 6f4fada2946dbe24874cd592161ebf6e6d534496
    serializer_class = FormularioSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_class = FiltroGeneral

    def get_queryset(self):
        # Obtiene el pk desde la URL
        pk = self.kwargs.get("pk")
        try:
            # Validar que el plan exista
            Plan.objects.get(pk=pk)
        except Plan.DoesNotExist:
            return Formulario.objects.none()  # Retorna un queryset vacío si el Plan no existe

        # Obtener los formularios relacionados con el Plan
        formularios_ids = FormularioPlan.objects.filter(id_plan=pk).values_list("id_formulario", flat=True)
        return Formulario.objects.filter(pk__in=formularios_ids)

    def list(self, request, *args, **kwargs):
        # Sobrescribir list para aplicar tu lógica personalizada
        response_data = []
        for formulario in self.get_queryset():
            # Obtener ítems relacionados al formulario
            items_ids = Items.objects.filter(
                pk__in=CreacionFormulario.objects.filter(id_formulario=formulario.pk).values_list("id_items", flat=True)
            )

            serialized_items = []
            for item in items_ids:
                opciones_ids = Opciones.objects.filter(id_categoria_opciones=item.id_categoria_opciones)
                serialized_item = ItemsSerializers(item).data
                serialized_item["opciones"] = OpcionesSeralizers(opciones_ids, many=True).data
                serialized_items.append(serialized_item)

            response_data.append({
                "formulario": FormularioSerializers(formulario).data,
                "items": serialized_items,
            })

        # Aplicar filtros y paginación a la respuesta final
        page = self.paginate_queryset(response_data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(response_data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        # Aquí se aplican tus filtros usando DjangoFilterBackend y FiltroGeneral
        return super().filter_queryset(queryset)

    def paginate_queryset(self, queryset):
        # Pagina los resultados automáticamente usando los métodos de ListAPIView
<<<<<<< HEAD
        return super().paginate_queryset(queryset)
=======
        return super().paginate_queryset(queryset)

>>>>>>> 6f4fada2946dbe24874cd592161ebf6e6d534496
