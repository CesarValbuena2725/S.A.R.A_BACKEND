from django.urls import path
from apps.Requests.api.views import (PostRequests, GetRequests,PatchRequest, 
                                     DeleteRequestDB,
                                     GetForms,GetFormsItems)

urlpatterns=[

    path('api/solicitud/get/',GetRequests.as_view()),
    path ('api/solicitud/post/',PostRequests.as_view()),
    path('api/solicitud/patch/<int:pk>/',PatchRequest.as_view()),
    path('api/solicitud/delete/<int:pk>/',DeleteRequestDB.as_view()),

    path('api/formslist/get/<int:id_request>/', GetForms.as_view()),
    path('api/itemslist/get/<int:id_form>/',GetFormsItems.as_view()),


]
