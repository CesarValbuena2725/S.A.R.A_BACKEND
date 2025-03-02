from django.urls import path
from apps.Requests.api.views import PostRequests, FiltrarPlanes
from apps.Utilidades.CRUD import GetGeneral, PostGeneral,Delete_General, PUT_General
urlpatterns=[

    path('api/<str:namemodel>/get/',GetGeneral.as_view()),
    path('api/<str:namemodel>/post/',PostGeneral.as_view()),
    path('api/<str:namemodel>/put/<int:pk>/',PUT_General.as_view()),
    path('api/<str:namemodel>/delete/<int:pk>/',Delete_General.as_view()),
  

    path ('requestpost',PostRequests.as_view()),
    path ('filtrar-planes/<int:id_tipo_vehiculo>', FiltrarPlanes.as_view(), name="filtrar-planes")
]
