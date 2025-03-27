from django.urls import path
from apps.Forms.api.views import PostCreateForms, DeleteForms
urlpatterns = [


    path("api/creacion/formularios/",PostCreateForms.as_view()),
    path("api/eliminar/formularios/<int:pk>/", DeleteForms.as_view())
]