from rest_framework.views import APIView
from apps.Forms.api.serializers import CreateFormsSerializers
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateFormsSerializers

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PostCreateForms(APIView):
    serializer_class = CreateFormsSerializers

    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            formulario = serializer.save()

            return Response(formulario, status=status.HTTP_201_CREATED)

        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)