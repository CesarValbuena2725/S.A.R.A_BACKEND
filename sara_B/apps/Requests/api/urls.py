from django.urls import path
from apps.Requests.api.views import PostRequests, GetRequests, PutRequest, DeleteRequestDB,FiltrarPlanes

urlpatterns=[


    path ('requestpost',PostRequests.as_view()),
    path ('filtrar-planes/<int:id_tipo_vehiculo>', FiltrarPlanes.as_view(), name="filtrar-planes"),
    path('requestget',GetRequests.as_view()),
    path('Requestput/<int:pk>/',PutRequest.as_view()),
    path ('requestpost',PostRequests.as_view() ) 
]
