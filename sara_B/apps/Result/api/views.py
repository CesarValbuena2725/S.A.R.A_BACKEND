# Librerías estándar
import os

# Django
from django.conf import settings
from django.shortcuts import render
from django.template.loader import get_template, render_to_string
from django.utils.timezone import localdate

# REST Framework
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

# Librerías externas
from weasyprint import HTML

# Apps del proyecto
from apps.Requests.models import Solicitud
from apps.Result.api.serializers import (
    RespuestaSerializer,
    Respuestas,
    RespuestaModelSerializers,
    ImagenSerializer,
    Fotos,
)
from apps.Result.api.tools import Amount_Items, FunctionClose, Render_Reporte
from apps.Utilidades.Permisos import BASE_PERMISOSOS, RolePermission
from apps.Utilidades.Email.email_base import send_email_sara



class FotosUploadView(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = BASE_PERMISOSOS
    """
    serializer_class = ImagenSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            serializer = ImagenSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                instancia = serializer.save()
                instancia.imagen = request.build_absolute_uri(instancia.imagen.url)
                instancia.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
        
class PDF(APIView):
    def get(self, request):
        
        html_string = render_to_string("report.html")


        output_path = os.path.join("C:/Users/tetro/OneDrive/Escritorio/S.A.R.A_BACKEND/sara_B/apps/Result/templates", "ptuen.pdf")

        try:
            HTML(string=html_string).write_pdf(output_path)
            return Response("Creación de PDF exitosa", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error al generar PDF: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Close_Request(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["PR", "AD"]
    """
    def get(self, request, *args ,**kwargs):

        id_request = self.kwargs.get('id_request')
        result = Amount_Items(id_request)

        if not result:
            return Response("there is not answer for the forms the request", status=status.HTTP_401_UNAUTHORIZED)

        try:
            solicitud = Solicitud.objects.get(pk=id_request)
        except Solicitud.DoesNotExist:
            return Response("Solicitud no encontrada", status=status.HTTP_404_NOT_FOUND)
        try:
            solicitud.estado = Solicitud.Estados_solcitud.FINALIZADO
            solicitud.fecha_fin = localdate()
            solicitud.save()
        except Exception as e:
            return Response(f"Error al cerrar la solicitud: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            functiones = FunctionClose(id_request)

            context = {
                    'request': solicitud,
                    'cliente': functiones.cliente(),
                    'vehiculo': functiones.vehiculo(),
                    'fugas': functiones.fugas(),
                    'carroceria': functiones.carroceria(),
                    'novedades': functiones.novedades(),
                    'pintura': functiones.pintura(),
                    'PMC': functiones.PMC(),
                    'PMV': functiones.PMV(),
                    'porcentaje': functiones.porcentaje(),
                    'foto':Fotos.objects.get(pk=2)

                }
            html_string = render_to_string("Reporte.html", context)
            output_path = os.path.join("C:/Users/tetro/OneDrive/Escritorio/S.A.R.A_BACKEND/sara_B/apps/Result/Reports", f"{solicitud.placa}.pdf")

        except Exception as e:
            return Response(f"Error al renderizar el reporte: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not Render_Reporte(html_string, output_path):
            return Response("Error al generar el reporte PDF", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if send_email_sara(
            affair="Solicitud Finalizada",
            template="email.html",
            destinario=[solicitud.id_empleado.correo],
            solicitante=solicitud,
            contexto=Fotos.objects.get(pk=2),
            files=[output_path]
        ):
            return Response("Reporte enviado por correo electrónico", status=status.HTTP_200_OK)

        return render(request, "Reporte.html", context)
        
class GetRespuestas(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["PR", "AD"]
    """
    model = Respuestas
    serializer_class = RespuestaModelSerializers

    def get_queryset(self):
        return self.model.objects.all()
    
    def get(self, request ,*args, **kwargs):
        solictud = self.kwargs.get("id_request")
        Form= self.kwargs.get("id_form")
        respuestas = Respuestas.objects.filter(id_solicitud=solictud,id_formulario= Form)

        if not respuestas:
            return Response("no hay registro para los datos enviados", status=status.HTTP_404_NOT_FOUND)
        
        serilizer = self.serializer_class(respuestas , many = True)
        return Response(serilizer.data, status=status.HTTP_200_OK)



class PostRespuestas(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =BASE_PERMISOSOS
    """
    serializer_class = RespuestaSerializer
    model_base= Respuestas
    
    def get_queryset(self):
        return self.model_base.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data) #Esto llama al Seralizer identicado con el Serializer_class
        if serializer.is_valid():
            resultado = serializer.save()
            # Convertir las respuestas a datos serializables
            respuestas_data = []
            for respuesta in resultado['respuestas_creadas']:
                respuestas_data.append({
                    'id': respuesta.id,
                    'id_Solicitud':respuesta.id_solicitud.id,
                    'id_formulario':respuesta.id_formulario.id,
                    'id_item': respuesta.id_item.id,
                    'id_opcion': respuesta.id_opcion.id if respuesta.id_opcion else None,
                    'respuesta_texto': respuesta.respuesta_texto
                })
            return Response({
                "Respuestas Registradas": respuestas_data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PutRespuesta(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["PR", "AD"]
    """

    def put(self, request):
        solicitud = request.data.get('solicitud')
        formulario = request.data.get('formulario')
        instancia = Respuestas.objects.filter(id_solicitud=solicitud, id_formulario=formulario).first()
        if not instancia:
            return Response("No existe respuesta para actualizar", status=status.HTTP_404_NOT_FOUND)

        serializer = RespuestaSerializer(
            instancia,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        resultado_actualizado = serializer.save()
        print("Esto devuelve el resultado actualizado", resultado_actualizado)

        return Response(resultado_actualizado, status=status.HTTP_200_OK)