from django.urls import path
from apps.Statistic.api.views import (GetStatisticSolicitud,ReportesExcel,GETPlanes,ReportLogins,GetTiempoSolucion)

urlpatterns = [
    path('api/solicitud/<int:year>/', GetStatisticSolicitud.as_view()),  # Sin mes
    path('api/planes/',GETPlanes.as_view()),
    path('api/reportesexcel/',
        ReportesExcel.as_view()),
    path('api/logins/',ReportLogins.as_view()),
    path('prueba/',GetTiempoSolucion.as_view())

]
    