from django.urls import path
from apps.Statistic.api.views import (GetStatisticSolicitud,ReportesExcel,GETPlanes,ReportLogins)

urlpatterns = [
    path('solicitud/<int:year>/', GetStatisticSolicitud.as_view(), name='solicitud-year'),  # Sin mes
    path('solicitud/<int:year>/<int:month>/', GetStatisticSolicitud.as_view(), name='solicitud-year-month'),  # Con mes
    path('plan',GETPlanes.as_view()),
    path('reporte/',
        ReportesExcel.as_view()),
    path('prueba/',ReportLogins.as_view())

]
    