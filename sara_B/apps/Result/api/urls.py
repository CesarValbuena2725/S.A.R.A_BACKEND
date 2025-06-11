from django.urls import path
from apps.Result.api.views import PostRespuestas,GetRespuestas,PutRespuesta,PDF,prueba,Close_Request

urlpatterns=[

    path('api/resultado/post/',PostRespuestas.as_view()),
    path('api/resultado/get/<int:id_request>/<int:id_form>/',GetRespuestas.as_view()),
    path('api/resultado/put/',PutRespuesta.as_view()),
    path('api/result/pdf/',PDF.as_view()),
    path('api/finalizar/get/<int:id_request>',Close_Request.as_view()),
    path('prueba/',prueba)

]