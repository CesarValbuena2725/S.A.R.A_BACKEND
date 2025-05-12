from django.urls import path
from apps.Requests.api.views import PostRequests, GetRequests,PatchRequest, DeleteRequestDB,FiltrarPlanes, CrearVehiculo, ActualizarTipoVehiculo, EliminarTipoVehiculo

urlpatterns=[


    path ('requestpost',PostRequests.as_view()),
    path ('filtrar-planes/<int:id_tipo_vehiculo>', FiltrarPlanes.as_view(), name="filtrar-planes"),
    path('requestget',GetRequests.as_view()),
    path('Requestput/<int:pk>/',PatchRequest.as_view()),
    path ('requestpost',PostRequests.as_view()),
    path ('crear_vehiculo', CrearVehiculo.as_view()),
    path('actualizar_vehiculo/<int:pk>/', ActualizarTipoVehiculo.as_view(), name="actualizar-vehiculo"),
    path('eliminar_vehiculo/<int:pk>/', EliminarTipoVehiculo.as_view())

]
