from django.urls import path
from apps.Statistic.api.views import (GetStatisticSolicitud,ReportesExcel,GETPlanes,ReportLogins)

urlpatterns = [
    path('api/solicitud/<int:year>/', GetStatisticSolicitud.as_view(), name='solicitud-year'),  # Sin mes
    path('api/solicitud/<int:year>/<int:month>/', GetStatisticSolicitud.as_view(), name='solicitud-year-month'),  # Con mes
    path('api/planes/',GETPlanes.as_view()),
    path('api/reportesexcel/',
        ReportesExcel.as_view()),
    path('api/logins/',ReportLogins.as_view())

]
    