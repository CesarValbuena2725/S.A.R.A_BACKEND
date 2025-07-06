from rest_framework.views import APIView
from rest_framework.response import Response
from apps.Utilidades.Permisos import getModelName
from rest_framework import status
from apps.Requests.models import Solicitud,Plan
from apps.Requests.api.serializers import SolicitudSerializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.Utilidades.Permisos import RolePermission


class GetStatisticSolicitud(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["AD"]
    """
    serializer_class = SolicitudSerializers

    def get(self, request, *args, **kwargs):
        try:

            year = self.kwargs.get('year', None)
            month = self.kwargs.get('month', None)
            if not month:
                print("no hay mes")
                data = Solicitud.objects.filter(fecha__year=year, is_active=True)
            else:
                print("hay mes")
                data = Solicitud.objects.filter(fecha__year=year, fecha__month=month, is_active=True)
            information = self.serializer_class(data, many=True).data
            data_count = {
                'total_solicitudes': len(information),
                'solicitudes_activo': len([sol for sol in information if sol['estado'] == 'AC']),
                'solicitudes_cancelado': len([sol for sol in information if sol['estado'] == 'CAL']),
                'solicitudes_progreso': len([sol for sol in information if sol['estado'] == 'PRO']),
                'solicitudes_finalizado': len([sol for sol in information if sol['estado'] == 'FIN']),
            }
            return Response({"data": data_count}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetStatisticPlan(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["AD"]
    """

    def get(self, request):
        try:
            Requets= Solicitud.objects.filter(is_active=True)
            plan = Plan.objects.filter(is_active=True)
            if not Requets:
                return Response({"error": "No hay solicitudes activas"}, status=status.HTTP_404_NOT_FOUND)
            data = {}

            for p in plan:
                data.update({p.nombre_plan: len(Requets.filter(id_plan=p.pk,is_active=True))})
            return Response({"data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReportAdmin(APIView):
   
    """ 
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["AD"]
    """

    def get(self, request, *args, **kwargs):
        try:

            name_model = self.kwargs.get('name_model', None)
            model = getModelName(name_model)
            if not model:
                return Response({"error": "Modelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        
            model_fields = model._meta.fields
            field_names = [field.name for field in model_fields]
            return Response({"fields": field_names}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)