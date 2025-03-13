#Api General para la creaacion y visualizacion de los objetos segun el model Selcionado Dinamicamnete en la URL
from rest_framework import generics,status
from rest_framework.response import Response
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from  apps.Requests.models import Solicitud, Plan, VehiculoPlan
from  apps.Requests.api.serializers import SolicitudSerializers, PlanSerializers
from apps.Utilidades.Email.email_base import send_email_sara
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters

"""
class CustomPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
"""
class SolicitudFilter(filters.FilterSet):
    estado = filters.ChoiceFilter(choices=Solicitud.Estados_solcitud.choices)  # Solo acepta valores válidos

    class Meta:
        model = Solicitud
        fields = ['estado']


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


    def post(self, request):

        serializers=self.serializer_class(data=request.data)
        if not serializers.is_valid():
             return Response(serializers.errors ,status=status.HTTP_406_NOT_ACCEPTABLE)
        
        try:
            instancie= serializers.save()
            send_email_sara(
                contexto=f"Solicitud Cancelada {instancie.pk}",
                affair= f"Nueva solicitud {instancie.pk}",
                template="base_request.html",
                solicitante= instancie,
            )

            return Response(serializers.data ,status=status.HTTP_201_CREATED)

        except Exception as e:
             return Response(
                {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#Crear un  en path para hacer el filtro de planes de solictudes  // el Frontend debe poder  enviar el tipo de Vehiculo y hacer la peticion al Servidor ; 
class FiltrarPlanes(APIView):
    def get(self, request, id_tipo_vehiculo):
        """
        Filtra los planes según el tipo de vehículo dado.
        """
        # Verificamos si el id_tipo_vehiculo existe en VehiculoPlan, filtrando los planes asociados al tipo_vehiculo
        planes_ids = VehiculoPlan.objects.filter(id_vehiculo=id_tipo_vehiculo).values_list('id_plan', flat=True)
        

        #Si no se encuentran planes asociados a ese id, retorna un error 404
        if not planes_ids:
            return Response(
                {"error": "No hay planes disponibles para este tipo de vehículo."},
                status=status.HTTP_404_NOT_FOUND
            )
        #Filtra los objetos de plan que tengan un id dentro del tipo_vehiculo
        planes = Plan.objects.filter(id__in=planes_ids)
        serializer = PlanSerializers(planes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CrearSolicitudAPIView(generics.CreateAPIView):
    """
    Vista para crear solicitudes validando que el plan y el tipo de vehículo coincidan.
    """
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializers
#Crear un  en path para hacer el filtro de planes de solictudes  // el Frontend debe poder  enviar el tipo de Vehiculo y hacer la peticion al Servidor ;

# Get Solicitudes

class GetRequests(generics.ListAPIView):
    """
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated, RolePermission]
        allowed_roles = ['AD', 'RC', 'CA',] 
    """
    
    serializer_class=SolicitudSerializers

    queryset = Solicitud.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = SolicitudFilter      
         
#Crear  genera notificacion  put para estado !=

class PutRequest(APIView):
    """
        authentication_classes = [JWTAuthentication]
        permission_classes = [IsAuthenticated, RolePermission]
        allowed_roles = ['AD', 'CA',] 
    """
    model = Solicitud
    serializer_class = SolicitudSerializers
    
    def get(self, request, pk):
        try:
            instance = self.model.objects.get(pk=pk)
            serializer = self.serializer_class(instance)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, pk):
        try:
            instancia = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return Response({"detail": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Serializar con la instancia existente y datos nuevos 
        model_serializers = self.serializer_class(instancia, data=request.data, partial=True)

        if not model_serializers.is_valid():
            return Response(model_serializers.errors, status=status.HTTP_400_BAD_REQUEST)



        if model_serializers.validated_data.get('estado') == "CAL":
            try:
                #Crear Pantilla de modificacion
                send_email_sara(
                #Es informacion infortante para el correo 
                contexto= instancia.pk,
                #Asusnto de la Solcitud 
                affair= f"Solicitud Cancelada {instancia.pk}",
                #Base HTMl que se va a renderiar para el correo
                template="base_update_request.html",
                #sin Solicitante// default None
                #sin Destinatario// Default correo SARA
                )

            except Exception as e:
                return Response(
                    {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        model_serializers.save()
        return Response(model_serializers.data, status=status.HTTP_200_OK)


#eliminar  genera notificiaon  notificicaion 

class DeleteRequestDB(APIView):
    """
    Vista para eliminar una solicitud por su PK.
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA']
    """
    def delete(self, request, pk):
        try:
            instancia = Solicitud.objects.get(pk=pk)
            instancia.delete()
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except Solicitud.DoesNotExist:
            return Response({"detail": "PK no válido"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Crear un  en path para hacer el filtro de planes de solictudes  // el Frontend debe poder  enviar el tipo de Vehiculo y hacer la peticion al Servidor ; 
class FiltrarPlanes(APIView):
    def get(self, request, id_tipo_vehiculo):
        """
        Filtra los planes según el tipo de vehículo dado.
        """
        # Verificamos si el id_tipo_vehiculo existe en VehiculoPlan, filtrando los planes asociados al tipo_vehiculo
        planes_ids = VehiculoPlan.objects.filter(id_vehiculo=id_tipo_vehiculo).values_list('id_plan', flat=True)
        

        #Si no se encuentran planes asociados a ese id, retorna un error 404
        if not planes_ids:
            return Response(
                {"error": "No hay planes disponibles para este tipo de vehículo."},
                status=status.HTTP_404_NOT_FOUND
            )
        #Filtra los objetos de plan que tengan un id dentro del tipo_vehiculo
        planes = Plan.objects.filter(id__in=planes_ids)
        serializer = PlanSerializers(planes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



