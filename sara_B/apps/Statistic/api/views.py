# NOTE:BookShow 
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment,Border,Side,PatternFill
from openpyxl.utils import get_column_letter
from datetime import date, timedelta,datetime

#Django
from django.http import HttpResponse

#DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Apps locals
from apps.Utilidades.Permisos import getModelName
from apps.Access.models import UserSession
from apps.Requests.models import Solicitud,Plan
from apps.Access.api.serializers import SerializersUserSession
from apps.Requests.api.serializers import SolicitudSerializers,PlanSerializers

#PErmisos 
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.Utilidades.Permisos import RolePermission

#NOTE:Clase para consultar la cantidad de soliciutdes  Activas en cada estado
#!Pendiente a Rivison y refacturizacion 
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