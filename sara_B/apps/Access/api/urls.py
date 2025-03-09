from django.urls import path
from apps.Access.models import Convenio,Sucursal,Empleado,Usuario
from apps.Access.api.serializers import ConvenioSerializers, SucursalSeralizers,EmpleadoSerialzers,UsuarioSerializers
from apps.Access.api.views import CreateUser,Login,SolicitudRestablecerPass,ContraseñaRestablecida
from apps.Utilidades.CRUD import GetGeneral,PUTGeneral,PostGeneral,DeleteGeneral

urlpatterns=[
    
    path('api/<str:namemodel>/get/',GetGeneral.as_view()),
    path('api/<str:namemodel>/post/',PostGeneral.as_view()),
    path('api/<str:namemodel>/put/<int:pk>/',PUTGeneral.as_view()),
    path('api/<str:namemodel>/delete/<int:pk>/',DeleteGeneral.as_view()),
    path('creacionuser/',CreateUser.as_view()),

    path('login/',Login.as_view()),
    path('solicitarpassword/', SolicitudRestablecerPass.as_view()),
    path('restablecerpassword/<uidb64>/<token>/',ContraseñaRestablecida.as_view())
]
    