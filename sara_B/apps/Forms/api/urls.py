from django.urls import path
from apps.Forms.api.views import PostCreateForms, DeleteForms, UpdateForms,ShowForms
urlpatterns = [


    path("api/creacion/formularios/",PostCreateForms.as_view()),
    path("api/eliminar/formularios/<int:pk>/", DeleteForms.as_view()),
    path('api/actualizar/formularios/<int:pk>/', UpdateForms.as_view()),
    path('api/mostrarformulario/<int:pk>/',ShowForms.as_view()),

]