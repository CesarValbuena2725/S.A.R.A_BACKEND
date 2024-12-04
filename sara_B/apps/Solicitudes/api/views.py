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



class PostSolicitud(APIView):
    serializer_class = SolicitudSerializers
    model = Solicitud

    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD','CA'] 
    """

    def get_queryset(self, request):
        return self.model.objects.all()

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            objeto = serializers.save()
            if isinstance(objeto, Solicitud):
                try:
                    asunto = f"Creación de Solicitud {objeto.pk}"
                    mesage = (f"Se crea la solicitud para la placa {objeto.placa}")
                    destinatario = objeto.cliente.correo 
                    send_mail(asunto, mesage, None, [destinatario])
                    return Response(serializers.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    eror = str(e)
                    return Response({'error': eror}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
                    
