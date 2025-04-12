# Third-party imports
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
# Local application imports
from apps.Utilidades.Permisos import (
    RolePermission,
    getModelName,
    getSerializer
)


class FiltroGeneral(filters.FilterSet):
    estado = filters.ChoiceFilter(choices=[('AC', 'Activo'), ('CAL', 'Cancelado'), ('PRO', 'En progreso')])

    class Meta:
        model = None  # Será asignado dinámicamente


class BaseGeneral(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated,RolePermission]
    allowed_roles = []  # Definir roles permitidos para cada clase hija
    """
    
    def get_serializer_class(self):
        namemodel = self.kwargs.get('namemodel')
        serializer_class = getSerializer(namemodel)
        if not serializer_class:
            raise NotFound(detail=f"Modelo no encontrado: {namemodel}")
        return serializer_class

    def get_model(self):
        namemodel = self.kwargs.get('namemodel')
        model = getModelName(namemodel)
        if not model:
            raise NotFound(detail=f"Modelo no encontrado: {namemodel}")
        return model

    def get_queryset(self):
        model = self.get_model()
        queryset = model.objects.all()
        
        # Aplicar filtros si existen
        if hasattr(self, "filterset_class") and self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=queryset)
            queryset = filterset.qs

        return queryset

    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(id=pk)
        except queryset.model.DoesNotExist:
            raise NotFound(detail=f"Objeto con ID {pk} no encontrado en {queryset.model.__name__}.")

class GetGeneral(BaseGeneral):
    
    allowed_roles = ['AD', 'PR', 'RC', 'CA', 'CC']
    filter_backends = [DjangoFilterBackend]
    filterset_class = FiltroGeneral
    
    def get(self, request, *args, **kwargs):
        try:
            serializer_class = self.get_serializer_class()
            queryset = self.get_queryset()
            model_serializers = serializer_class(queryset, many=True) 
            return Response(model_serializers.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostGeneral(BaseGeneral):
    allowed_roles = ['AD', 'CA']

    def post(self, request, *args, **kwargs):
        try:
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"validation_error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class PatchGeneral(BaseGeneral):
    allowed_roles = ['AD', 'CA']

    def patch(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object(pk)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        except NotFound as e:
            return Response({'errors': str(e)}, status=status.HTTP_404_NOT_FOUND)

class PutGeneral(BaseGeneral):
    allowed_roles = ['AD', 'CA']

    def put(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object(pk)
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(instance, data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        except NotFound as e:
            return Response({'errors': str(e)}, status=status.HTTP_404_NOT_FOUND)

class DeleteGeneral(BaseGeneral):
    allowed_roles = ['AD', 'CA']

    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object(pk)
            instance.delete()
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
