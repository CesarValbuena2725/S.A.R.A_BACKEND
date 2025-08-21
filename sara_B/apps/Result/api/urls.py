from django.urls import path
from apps.Result.api.views import PostRespuestas,GetRespuestas,PutRespuesta,CloseRequest,FotosUploadView,DownloadReport

urlpatterns=[

    path('api/resultado/post/',PostRespuestas.as_view()),
    path('api/resultado/get/<int:id_request>/<int:id_form>/',GetRespuestas.as_view()),
    path('api/resultado/put/',PutRespuesta.as_view()),
    path('api/finalizar/get/<int:id_request>/',CloseRequest.as_view()),
    path('api/subirimagen/post/', FotosUploadView.as_view(), name='subir-imagen'),
    path("api/descarga/reporte/<int:id_request>/",DownloadReport.as_view()),


]

