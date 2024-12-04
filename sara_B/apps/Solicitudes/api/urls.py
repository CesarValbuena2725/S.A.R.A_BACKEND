from django.urls import path
from apps.Utilidades.CRUD import GetGeneral,PUT_General,PostGeneral,Delete_General
from apps.Solicitudes.api.views import PostSolicitud

urlpatterns=[
    path('<str:namemodel>/get',GetGeneral.as_view()),
    path('<str:namemodel>/post',PostGeneral.as_view()),
    path('<str:namemodel>/put/<int:pk>',PUT_General.as_view()),
    path('<str:namemodel>/delete/<int:pk>',Delete_General.as_view()),
    path('postsolicitud/',PostSolicitud.as_view())
]


