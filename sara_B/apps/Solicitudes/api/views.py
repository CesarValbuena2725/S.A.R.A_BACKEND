from rest_framework import status
from apps.Solicitudes.models import Solicitud
from apps.Solicitudes.api.serializers import SolicitudSerializers
from rest_framework.views import APIView
from django.core.mail import send_mail
from rest_framework.response import Response
from ...Utilidades.Permisos import RolePermission
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions
from apps.Utilidades.Email.email_base import send_email_sara



class PostSolicitud(APIView):
    serializer_class = SolicitudSerializers
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'CA']

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        
        if not serializers.is_valid():
            return Response(serializers.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            objeto = serializers.save()
            
            # Enviar correo electrónico de la base ya creadad / solo cambia la pantialla HTML
            send_email_sara(
                subject=f"Nuevo solicitud Creada {objeto.pk}",
                recipient_list=["tosaraweb@gmail.com"],
                template="Base_Solicitud.html",
                context={"placa": objeto.placa}
            )

            return Response(serializers.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class PUTSolicitud(APIView):
    serializer_class = SolicitudSerializers
    model = Solicitud

    def get(self, request, pk):
        try:
            instance = self.model.objects.get(id=pk)
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response({"detail": "Objeto no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            instancia = self.model.objects.get(id=pk)
            
            serializer = self.serializer_class(instancia, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except self.model.DoesNotExist:
            return Response({"detail": "Objeto no existe"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)