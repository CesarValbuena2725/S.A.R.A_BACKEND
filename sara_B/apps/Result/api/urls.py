from django.urls import path
from apps.Result.api.views import PostRespuestas

urlpatterns=[

    path('api/resultado/post/',PostRespuestas.as_view())

]