# Librerías estándar
import os

# Django
from django.conf import settings
from django.shortcuts import render
from django.template.loader import get_template, render_to_string
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.http import FileResponse



# REST Framework
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication



# Apps del proyecto
from apps.Requests.models import Solicitud
from apps.Result.api.serializers import (
    RespuestaSerializer,
    Respuestas,
    RespuestaModelSerializers,
    ImagenSerializer,
    Fotos,
)
from apps.Result.api.tools import Amount_Items, FunctionClose
from apps.Utilidades.Permisos import BASE_PERMISOSOS, RolePermission
from apps.Utilidades.Email.email_base import Send_Email_Sara
from apps.Utilidades.tasks import Send_Email_Asyn, Render_Reporte_Asyn


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
        
        serilizer = self.serializer_class(respuestas ,many = True)
        return Response(serilizer.data, status=status.HTTP_200_OK)


class FotosUploadView(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['PR','AD']
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
  
class PostRespuestas(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =["PR","AD"]
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

        return Response(resultado_actualizado, status=status.HTTP_200_OK)

class CloseRequest(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["PR", "AD"]
    """
    
    def get(self, request, *args ,**kwargs):

        id_request = self.kwargs.get('id_request')
        #funciona que valida que cada formulario Tenga respuesta Guardad 
        result = Amount_Items(id_request)
        
        if not result:
           return Response("there is not answer for the forms the request", status=status.HTTP_400_BAD_REQUEST)

        try:
            solicitud = Solicitud.objects.get(pk=id_request)
        except Solicitud.DoesNotExist:
            return Response("Solicitud no encontrada", status=status.HTTP_404_NOT_FOUND)
        
    
        
        try:
            # Clase que permite crear los contextos necesarios crear el informe, la logia esta separada 
            functiones = FunctionClose(id_request)
            # Se Guarda Cada uno de estos datos par pasarlo a la funcion que crea el informe
            context = {
                    'request': solicitud,
                    'cliente': functiones.Cliente(),
                    'vehiculo': functiones.Vehiculo(),
                    'fugas': functiones.Fugas(),
                    'carroceria': functiones.Carroceria(),
                    'novedades': functiones.Novedades(),
                    'pintura': functiones.Pintura(),
                    'PMC': functiones.Pmc(),
                    'PMV': functiones.Pmv(),
                    'porcentaje': functiones.Porcentaje(),
                    'foto':Fotos.objects.get(pk=2)

                }
            # Se Renderiza la informacion en un HTML con los datos necesarios 
            html_string = render_to_string("Reporte.html", context)
            # Se Crea una ruta donde Guardar e informe 
            output_path = os.path.join(settings.REPORTS_DIR, f"{solicitud.placa}.pdf")
            fotos = Fotos.objects.get(pk=2)
            # Se optine dirrecion de correo a donde se debe Enviar el informe PDF 
            dirrecion = Respuestas.objects.get(id_formulario =3, id_item =46, id_solicitud = id_request)
        except Exception as e:
            return Response(f"Error al renderizar el reporte: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Se actualizandos los datos de la solicitud
            solicitud.estado = Solicitud.Estados_solcitud.FINALIZADO
            solicitud.fecha_fin = localdate()
            solicitud.save()
        except Exception as e:
            return Response(f"Error al cerrar la solicitud: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            # funciones Asinconicas para crear el informa PDF apartir del HTML Creado se guarda en la ruta indica
            #!De manera automatica cuando termina la creacion del PDF Se hace en envio del correo adjuntado el informa creado 
            # Al ser asincronicas no retrasan la ejecucion del programa
            (Render_Reporte_Asyn.s(html_string, output_path) | 
            Send_Email_Asyn.s(
                affair="Solicitud Finalizada",
                template="email.html",
                destinatario=[solicitud.id_empleado.correo, dirrecion.respuesta_texto],
                solicitante=model_to_dict(solicitud,fields=['id', 'placa', 'estado', 'fecha', 'fecha_fin', 'observaciones']),
                contexto=fotos.imagen.url,
                delay_second=5
            )).delay()


            return Response("Se Envio el correo con el reporte Solicitado",status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error al enviar el correo: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Clase para Descargar el informe de manera manual en el caso de ser necesaria 
class DownloadReport(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["PR", "AD", "CC"]
    """
    def get(self,request, *args,**kwargs ):
        id_resquest = self.kwargs.get('id_request')
        try:
            solicitud = Solicitud.objects.get(id=id_resquest)

            if solicitud.estado != Solicitud.Estados_solcitud.FINALIZADO:
                return Response("La solicitud debe Estar finalizada para Descargar el reporte",status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error":e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            file_name = f"{solicitud.placa}.pdf"
            output_path = os.path.join(settings.REPORTS_DIR, file_name)

            if  not os.path.exists(output_path):
                return Response("Reporte No encontrado Validar con el Administrador", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return FileResponse(open(output_path, 'rb'), as_attachment=True, content_type='application/pdf')
        except Exception as e:
            return Response({"error":e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        