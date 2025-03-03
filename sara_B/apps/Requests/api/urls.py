from django.urls import path
from apps.Requests.api.views import PostRequests, GetRequests, PutRequest, DeleteRequestDB
from apps.Utilidades.CRUD import GetGeneral, PostGeneral,Delete_General, PUT_General
urlpatterns=[

    path('api/<str:namemodel>/get/',GetGeneral.as_view()),
    path('api/<str:namemodel>/post/',PostGeneral.as_view()),
    path('api/<str:namemodel>/put/<int:pk>/',PUT_General.as_view()),
    path('api/<str:namemodel>/delete/<int:pk>/',Delete_General.as_view()),
  

    path ('resquestpost',PostRequests.as_view() ),
    path('requestget',GetRequests.as_view()),
    path('Requestput/<int:pk>/',PutRequest.as_view())

]
    