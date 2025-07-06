from django.urls import path
from apps.Requests.api.views import (PostRequests, GetRequests,PatchRequest, 
                                     DeleteRequestDB,FiltrarPlanes, CrearVehiculo, 
                                     ActualizarTipoVehiculo, EliminarTipoVehiculo,
                                     GetForms,GetFormsItems)

urlpatterns=[

    path('api/solicitud/get/',GetRequests.as_view()),
    path ('api/solicitud/post/',PostRequests.as_view()),
    path('api/solicitud/patch/<int:pk>/',PatchRequest.as_view()),
    path('api/solicitud/delete/<int:pk>/',DeleteRequestDB.as_view()),

    path('api/formslist/get/<int:id_request>/', GetForms.as_view()),
    path('api/itemslist/get/<int:id_form>/',GetFormsItems.as_view()),


    path ('crear_vehiculo', CrearVehiculo.as_view()),
    path('actualizar_vehiculo/<int:pk>/', ActualizarTipoVehiculo.as_view(), name="actualizar-vehiculo"),
    path ('filtrar_planes/<int:id_tipo_vehiculo>', FiltrarPlanes.as_view(), name="filtrar-planes"),
    path('eliminar_vehiculo/<int:pk>/', EliminarTipoVehiculo.as_view())

]
