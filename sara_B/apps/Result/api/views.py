from apps.Result.api.serializers import CategoriaOpcionesSerializer, Opciones,RespuestaSerializer,Respuestas,RespuestaModelSerializers,ImagenSerializer,Fotos
from rest_framework import generics,status
from rest_framework.response import Response
from apps.Utilidades.Permisos import BASE_PERMISOSOS, RolePermission
from rest_framework.views import APIView
from django.shortcuts import render
from apps.Requests.models import Solicitud
from apps.Result.api.tools import Amount_Items,FunctionClose
from apps.Forms.models import Items
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from weasyprint import HTML
from django.template.loader import get_template
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from weasyprint import HTML
import os
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings


class Prueba(APIView):
    def get(self, request):
        imagenes = Fotos.objects.all()
        for img in imagenes:
            #Remplazar la URL relativa por la absoluta

            img.url_absoluta = request.build_absolute_uri(img.imagen.url)
            print(img.url_absoluta)
            print(img.imagen.url)

        html_string = render_to_string('galeria.html', {
            'imagenes': imagenes})

        output_path = os.path.join("C:/Users/tetro/OneDrive/Escritorio/S.A.R.A_BACKEND/sara_B/apps/Result/templates", "ptuen.pdf")

        try:
            HTML(string=html_string, base_url=settings.MEDIA_ROOT).write_pdf(output_path)
            return Response("Creación de PDF exitosa", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error al generar PDF: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


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
    def get(self, request, *args ,**kwargs):

        id_request = self.kwargs.get('id_request')
        result = Amount_Items(id_request)

        if not result:
            return Response("there is not answer for the forms the request", status=status.HTTP_401_UNAUTHORIZED)
        data = Respuestas.objects.filter(id_solicitud = id_request, id_formulario=3).order_by('id_formulario') 

        functiones = FunctionClose(id_request)

        solicitud=Solicitud.objects.get(pk=id_request)

        img = Fotos.objects.get(pk=1)
        print("Prueba de envio Vacion",functiones.PMV())
        context = {
                'request': solicitud,
                'cliente': data,
                'vehiculo': functiones.vehiculo(),
                'img': img,
                'fugas': functiones.fugas(),
                'carroceria': functiones.carroceria(),
                'novedades': functiones.novedades(),
                'pintura': functiones.pintura(),
                'PMC': functiones.PMC(),
                'PMV': functiones.PMV(),

            }
        html_string = render_to_string("Reporte.html", context)

        """        Generación del PDF
                output_path = os.path.join("C:/Users/tetro/OneDrive/Escritorio/S.A.R.A_BACKEND/sara_B/apps/Result/templates", "ptuen.pdf")
        try:
            HTML(string=html_string).write_pdf(output_path)
            return Response("Creación de PDF exitosa", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(f"Error al generar PDF: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        """
        return render(request, "Reporte.html", context)
        



class GetRespuestas(generics.GenericAPIView):
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