from django.urls import path
from apps.Statistic.api.views import (ReportAdmin,GetStatisticSolicitud,ReporteEmpleadosExcel,GETPlanes)

urlpatterns = [
    path('solicitud/<int:year>/', GetStatisticSolicitud.as_view(), name='solicitud-year'),  # Sin mes
    path('solicitud/<int:year>/<int:month>/', GetStatisticSolicitud.as_view(), name='solicitud-year-month'),  # Con mes
    path('plan',GETPlanes.as_view()),
    path('reporte/',
        ReporteEmpleadosExcel.as_view()),

]
    