from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status,generics
from apps.Forms.api.serializers import CreacionPlantillaSerializers, CategoriaItemsSerializers, ItemsSerializers, FormularioSerializers, FormularioPlanSerializers
from apps.Forms.models import CreacionPlantilla, CategoriaItems, Items, Formulario, FormularioPlan
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authentication import TokenAuthentication
from ...Utilidades.Permisos import RolePermission
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from apps.Utilidades.Email.email_base import send_email_sara
from django.http import Http404
from apps.Utilidades.CRUD import BaseGeneral
from .custom_renderer import RenderApiPersonalizado
from rest_framework.renderers import JSONRenderer

class CreacionFormularios(APIView):
    model = Formulario
    serializer_class = FormularioSerializers
    renderer_classes = [RenderApiPersonalizado, JSONRenderer]

    def get(self, request):
        return Response(
            {"message": "Usa POST para crear formularios"},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            nombre_formulario = request.data.get("nombre_formulario")
            items_ids = request.data.get("items", [])

            items = Items.objects.filter(id__in=items_ids)
            if len(items) != len(items_ids):
                return Response(
                    {"Error":"Alguno o más items no existen"}
                    , status=status.HTTP_404_NOT_FOUND
                )
            
            formulario = Formulario.objects.create(nombre_formulario=nombre_formulario)
          
            for item in items:
                CreacionPlantilla.objects.create(id_items=item, id_formulario=formulario)

            return Response(
                {"message": "Formulario creado exitosamente"},
                status=status.HTTP_201_CREATED
            )