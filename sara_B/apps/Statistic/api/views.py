from rest_framework.views import APIView
from rest_framework.response import Response
from apps.Utilidades.Permisos import getModelName
from rest_framework import status


class ReportAdmin(APIView):
   
    """ 
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ["AD"]
    """

    def get(self, request, *args, **kwargs):
        try:

            name_model = self.kwargs.get('name_model', None)
            model = getModelName(name_model)
            if not model:
                return Response({"error": "Modelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        
            model_fields = model._meta.fields
            field_names = [field.name for field in model_fields]
            return Response({"fields": field_names}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)