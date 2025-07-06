from django.urls import path
from apps.Statistic.api.views import (ReportAdmin,GetStatisticSolicitud,GetStatisticPlan)

urlpatterns = [
    path('solicitud/<int:year>/', GetStatisticSolicitud.as_view(), name='solicitud-year'),  # Sin mes
    path('solicitud/<int:year>/<int:month>/', GetStatisticSolicitud.as_view(), name='solicitud-year-month'),  # Con mes
    path('plan/',GetStatisticPlan.as_view()),
]
    