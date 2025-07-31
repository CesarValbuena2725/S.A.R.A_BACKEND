#BookShow 
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment,Border,Side,PatternFill
from openpyxl.utils import get_column_letter
from datetime import date, timedelta

#Django
from django.http import HttpResponse

#DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#Apps locals
from apps.Utilidades.Permisos import getModelName
from apps.Requests.models import Solicitud,Plan
from apps.Requests.api.serializers import SolicitudSerializers

#PErmisos 
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
        


class ReporteEmpleadosExcel(APIView):
    #Ejempli de URL Que e Debe utilizar 
    #http://localhost:8000/reporte/?year_start=2024&month_start=6&year_end=2025&month_end=7&state=inactivo

    def get(self, request, *args, **kwargs):
        # 1. Obtener y validar los datos
        try:
            year_start = int(request.GET.get("year_start", 2000)) 
            month_start = int(request.GET.get("month_start", 1)) 
            year_end = int(request.GET.get("year_end", 3000)) 
            month_end = int(request.GET.get("month_end", 12)) 

            state = request.GET.get("state", "Todos")  # valor por defecto
        except (ValueError, TypeError):
            return HttpResponse("Parámetros inválidos", status=400)
        
        # 2. Construir queryset con filtros
        queryset = Solicitud.objects.all()
        
        # Filtro por fechas
        if all([year_start, month_start, year_end, month_end]):
            try:
                date_start = date(year_start, month_start, 1)
                # Calcular último día del mes final
                if month_end == 12:
                    date_end = date(year_end, month_end, 31)
                else:
                    date_end = date(year_end, month_end + 1, 1) - timedelta(days=1)
                
                queryset = queryset.filter(fecha__range=(date_start, date_end))
            except (ValueError, TypeError):
                return HttpResponse("Rango de fechas inválido", status=400)

        # Filtro por estado
        if state != "Todos":
            queryset = queryset.filter(estado=state)

        # 3. Generar el Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Empleados"
        
        # creacion  de estilos
        borde_fino = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")
        
        # Titulo principal
        campos = [field.name for field in Solicitud._meta.fields if field.name not in ['id']]
        num_cols = len(campos)
        col_fin = get_column_letter(num_cols)
        
        ws.merge_cells(f"A1:{col_fin}1")
        celda_titulo = ws["A1"]
        celda_titulo.value = "REPORTE DE EMPLEADOS"
        celda_titulo.font = Font(bold=True, size=14)
        celda_titulo.alignment = Alignment(horizontal="center", vertical="center")

        # Encabezados de columnas
        for col_num, campo in enumerate(campos, 1):
            celda = ws.cell(row=2, column=col_num, value=campo.replace('_', ' ').title())
            celda.font = Font(bold=True)
            celda.alignment = Alignment(horizontal='center')
            celda.border = borde_fino
            celda.fill= fill

        # Datos
        for row_num, empleado in enumerate(queryset, 3):
            for col_num, campo in enumerate(campos, 1):
                valor = getattr(empleado, campo)
                if isinstance(valor, bool):
                    valor = "SI" if valor else "NO"
                elif isinstance(valor, date):
                    valor = valor.strftime('%d/%m/%Y')
                celda = ws.cell(row=row_num, column=col_num, value=str(valor))
                celda.border = borde_fino

        # Ajustar ancho de columnas
        for col_num, campo in enumerate(campos, 1):
            max_length = len(campo)
            for row in ws.iter_rows(min_row=3, min_col=col_num, max_col=col_num):
                for cell in row:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[get_column_letter(col_num)].width = max_length + 2

        # Preparar respuesta
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': 'attachment; filename="reporte_empleados.xlsx"'},
        )
        wb.save(response)
        return response