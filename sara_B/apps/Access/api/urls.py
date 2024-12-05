from django.urls import path
from apps.Access.models import Convenio,Sucursal,Empleado,Usuario
from apps.Access.api.serializers import ConvenioSerializers, SucursalSeralizers,EmpleadoSerialzers,UsuarioSerializers
from apps.Access.api.views import CreateUser,Login,SolicitudRestablecerPass,ContraseñaRestablecida
from apps.Utilidades.CRUD import GetGeneral,PUT_General,PostGeneral,Delete_General

urlpatterns=[
    
    path('api/<str:namemodel>/get',GetGeneral.as_view()),
    path('api/<str:namemodel>/post',PostGeneral.as_view()),
    path('api/<str:namemodel>/put/<int:pk>',PUT_General.as_view()),
    path('api/<str:namemodel>/delete/<int:pk>',Delete_General.as_view()),

    path('login77/',Login.as_view()),

    path('solicitarpassword/', SolicitudRestablecerPass.as_view()),
    path('restablecerpassword/<uidb64>/<token>/',ContraseñaRestablecida.as_view())
]
    