from rest_framework.views import APIView
from apps.Forms.api.serializers import CreateFormsSerializers
from rest_framework import status
from rest_framework.response import Response
from apps.Forms.models import Formulario, CreacionFormulario,Items
from apps.Forms.api.serializers import CreacionFormularioSerializers
from django.db import transaction

class PostCreateForms(APIView):
    serializer_class = CreateFormsSerializers

    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            formulario = serializer.save()

            return Response(formulario, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
