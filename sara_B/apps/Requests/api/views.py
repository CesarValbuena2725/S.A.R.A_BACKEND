#Api General para la creaacion y visualizacion de los objetos segun el model Selcionado Dinamicamnete en la URL
from rest_framework import generics,status
from rest_framework.response import Response
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from  apps.Requests.models import Solicitud
from  apps.Requests.api.serializers import SolicitudSerializers
from apps.Utilidades.Email.email_base import send_email_sara


class PostRequests(generics.GenericAPIView):
    """
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated, RolePermission]
        allowed_roles = ['AD', 'RC', 'CA',] 
    """
    model = Solicitud
    serializer_class=SolicitudSerializers

    def get_queryset(self):
        return self.model.objects.all()  
    
    def get(self,request):
            try:
                usuario = self.model.objects.all()
                serializers = self.serializer_class(usuario, many=True)
                return Response(serializers.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


    def post(self, request):

        serializers=self.serializer_class(data=request.data)
        if not serializers.is_valid():
             return Response(serializers.errors ,status=status.HTTP_406_NOT_ACCEPTABLE)
        
        try:
            instancie= serializers.save()
            send_email_sara(
                contexto=f"Nueva solicitud {instancie.pk}",
                asunto= f"Nueva solicitud {instancie.pk}",
                plantilla="base_request.html",
                solicitante= instancie.placa,
                destinario= [""]
            )

            return Response(serializers.data ,status=status.HTTP_201_CREATED)

        except Exception as e:
             return Response(
                {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
#Crear un  en path para hacer el filtro de planes de solictudes  // el Frontend debe poder  enviar el tipo de Vehiculo y hacer la peticion al Servidor ; 