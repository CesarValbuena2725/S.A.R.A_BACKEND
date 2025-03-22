from django.urls import path
from apps.Forms.api.views import PostCreateForms, DeleteForms, UpdateForms
urlpatterns = [


    path("prueba",PostCreateForms.as_view()),
    path("api/eliminar/formularios/<int:pk>/", DeleteForms.as_view()),
    path('api/actualizar/formularios/<int:pk>/', UpdateForms.as_view()),

]