from django.urls import path
from apps.Access.api.views import CreateUser,Login,SolicitudRestablecerPass,ContraseñaRestablecida,GetEmploye

urlpatterns=[

    path('api/createuser/post',CreateUser.as_view()),
    path('api/login/',Login.as_view()),
    path('api/solicitarpassword/', SolicitudRestablecerPass.as_view()),
    path('api/restablecerpassword/<str:uidb64>/<str:token>/',ContraseñaRestablecida.as_view()),
    path("api/empleado/get/",GetEmploye.as_view())
]
    