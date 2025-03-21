from django.urls import path
from apps.Forms.api.views import PostCreateForms
urlpatterns = [


    path("prueba",PostCreateForms.as_view())
]