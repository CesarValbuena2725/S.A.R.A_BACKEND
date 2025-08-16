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
    Get_Model_Name,
    Get_Serializer_Name
)


class FiltroGeneral(filters.FilterSet):
    estado = filters.ChoiceFilter(choices=[('AC', 'Activo'), ('CAL', 'Cancelado'), ('PRO', 'En progreso')])

    class Meta:
        model = None  # Será asignado dinámicamente

# BAse General para el CRUD
class BaseGeneral(generics.GenericAPIView):

    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    """
    allowed_roles = [] 
 
    # Funcion que Valida el serializers Pasado dinamicamente por la URL
    def get_serializer_class(self):
        namemodel = self.kwargs.get('namemodel')
        serializer_class = Get_Serializer_Name(namemodel)
        if not serializer_class:
            raise NotFound(detail=f"Modelo no encontrado: {namemodel}")
        return serializer_class
    
    # Funcion que Valida el model Pasado dinamicamente por la URL
    def get_model(self):
        namemodel = self.kwargs.get('namemodel')
        model = Get_Model_Name(namemodel)
        if not model:
            raise NotFound(detail=f"Modelo no encontrado: {namemodel}")
        return model
    # Funcion General para el renderizados de diversas objetos
    def get_queryset(self):
        model = self.get_model()
        queryset = model.objects.all()
        
        # Aplicar filtros si existen
        if hasattr(self, "filterset_class") and self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=queryset)
            queryset = filterset.qs

        return queryset
    #Funcion que permite el renderizado unico de objeto
    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(id=pk)
        except queryset.model.DoesNotExist:
            raise NotFound(detail=f"Objeto con ID {pk} no encontrado en {queryset.model.__name__}.")

class GetAdmin(BaseGeneral):
    #!solo Admin 
    allowed_roles=['AD']
    
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

class GetFilter(BaseGeneral):
    allowed_roles = ['AD', 'PR', 'RC', 'CA', 'CC']
   
    
    def get(self, request, *args, **kwargs):
        try:

            #/Se llaman los campos pasados por URL
            atribut = self.kwargs.get('atribut')
            value = self.kwargs.get('value')

            #Se intancial el model para poder hacer una validacion de Atributos existentes 
            model = self.get_model()
            valid_fields = [f.name for f in model._meta.get_fields()]

            if atribut not in valid_fields:
                return Response(
                    {'error': f"Campo '{atribut}' no válido para este modelo."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer_class = self.get_serializer_class()
            queryset = self.get_queryset().filter(**{atribut:value}, is_active=True)
            model_serializers = serializer_class(queryset, many=True) 

            return Response(model_serializers.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetGeneral(BaseGeneral):
    allowed_roles = ['AD', 'PR', 'RC', 'CA', 'CC']

    filter_backends = [DjangoFilterBackend]
    filterset_class = FiltroGeneral
    
    def get(self, request, *args, **kwargs):
        try:
            serializer_class = self.get_serializer_class()
            queryset = self.get_queryset().exclude(is_active=False)
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
            return Response({"validation_error": e.detail}, status=status.HTTP_306_RESERVED)
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

            if not instance.is_active:
                return Response({"detail": "El objeto ya está inactivo."}, status=status.HTTP_400_BAD_REQUEST)
            
            instance.is_active=False
            instance.save()
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class DeleteAdmin(BaseGeneral):
    
    allowed_roles = ['AD', 'CA']

    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object(pk)

            instance.delete()
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

