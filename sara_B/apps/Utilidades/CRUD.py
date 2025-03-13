#Api General para la creaacion y visualizacion de los objetos segun el model Selcionado Dinamicamnete en la URL
from rest_framework import generics,status
from rest_framework.response import Response
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.Utilidades.Permisos import getModelName,getSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from apps.Requests.models import Solicitud
from rest_framework.exceptions import ValidationError

class FiltroGeneral(filters.FilterSet):
    estado = filters.ChoiceFilter(choices=Solicitud.Estados_solcitud.choices)

    class Meta:
        model = Solicitud
        fields = ['estado']


class BaseGeneral(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]


        allowed_roles = []  # Definir roles permitidos para cada clase hija

    def check_permissions(self, request):
        if not request.user.role in self.allowed_roles:
            raise PermissionDenied("No tienes permiso para esta acción.")

            Tentativa opcion Dos de permisos
    """
    """
    Base general para el manejor de peticiones HTTPP Baiscas  GET, PUT, DELETE, POST, diseñada.puntos claves: 
        *funciones get_model y get_serializers_class permite gestions lo datos enviados desde la URL 
        *uso de *args y *kgars para poder utilizar los elmemtos enviados en URL toda las clases hijas deben llamarlos 
        * Validacion desdes principlaes para evitar duplicidad 
    
    """

#Devuelve el serializer basado en el `namemodel` proporcionado en la solicitud.

    def get_serializer_class(self,*args, **kwargs):
        #self.kwargs = Es un dicionario con todos los datos pasados en el Path
        namemodel = self.kwargs.get('namemodel')
        serializer_class = getSerializer(namemodel)

        if not serializer_class:
            raise NotFound(detail=f"Model NotFound: {namemodel}")
        
        return serializer_class

#Devuelve el model basado en el `namemodel` proporcionado en la solicitud.

    def get_model(self,*args, **kwargs):
        namemodel = self.kwargs.get('namemodel')
        model= getModelName(namemodel)

        if not model:
            raise NotFound(detail=f"Model NotFound: {namemodel}")
        return model

#Clase base para manejar operaciones generales con modelos.

    def get_queryset(self):
        
        queryset = self.get_model().objects.all()
        
        #Filtros aplicados con filterset_class
        if self.filterset_class:
            filterset = self.filterset_class(self.request.GET, queryset=self.get_model().objects.all())
            if filterset.is_valid():
                queryset = filterset.qs
        
        return queryset  

    
    #realiza la validacion del objeto indicado segun el model que corresponda.
    def get_object(self, pk):
        queryset = self.get_queryset()
        try:
            return queryset.get(id=pk)
        except queryset.model.DoesNotExist:
            raise NotFound(detail=f"Objeto con id {pk} no encontrado en el modelo {queryset.model.__name__}.")
        
    #Llama los objetos dependiendo si pasan o no un PK

    def get(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            serializer_class = self.get_serializer_class()
            
            if not pk:
                queryset = self.get_queryset()
                serializer = serializer_class(queryset, many=True)
            else:
                instance = self.get_object(pk)
                serializer = serializer_class(instance)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


# Funcion para hacer el llamado de los objetos apartil del model  

class GetGeneral(BaseGeneral):
    """
    allowed_roles = ['AD', 'PR', 'RC', 'CA', 'CC'] 
    """

    def get(self, request,*args, **kwargs):  
        try:
            serializer_class = self.get_serializer_class()
            # Llama a get_queryset
            queryset = self.get_queryset()  # Ahora se llama sin argumentos
            model_serializers = serializer_class(queryset, many=True) 
            return Response(model_serializers.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    filter_backends = [DjangoFilterBackend]
    filterset_class = FiltroGeneral


#Api General para la creacion de registros en los model

class PostGeneral(BaseGeneral): # Heredan funcionalidades de las clase base 
    """
    allowed_roles = ['AD', 'CA']  # Roles Administrativos
    """
        
    def post(self, request,*args, **kwargs):
        # Obtiene el modelo basado en `namemodel`
        try:          
            # Obtiene el serializador basado en `namemodel` mediante `get_serializer_class`
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)        
        
        except ValidationError as e:
            return Response({"validation_error": e.detail},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Api General para la Actualizacion 

class PUTGeneral(BaseGeneral): # Herendan funcionaloidades de las clase base 
    """
    allowed_roles = ['AD','CA'] 
    """  

    # Realiza la revision de los  nuevos datos para el objeto y realiza la actualizacion
    def put(self,request,pk,*args, **kwargs):
        try:
            modelos=self.get_object(pk)
            serializer_class = self.get_serializer_class()
            model_serializars=serializer_class(modelos,data=request.data)
           
            if model_serializars.is_valid():
                model_serializars.save()

                return Response(model_serializars.data, status=status.HTTP_200_OK)
            return Response(model_serializars.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        except NotFound as e:
            return Response({'errors':str(e)},status=status.HTTP_404_NOT_FOUND)
        
#Api General para la eliminacion  de la Basse de datos, Esto no esta para auditorias pendiente por hablar 

class DeleteGeneral(BaseGeneral):

    """
    allowed_roles = ['AD','CA'] 
    """
    # Llama al objeto después de la validación

    def delete(self, request, pk,*args, **kwargs):
        try:
            #instancion del objeto pasando como segundo parametro el modelo para poder hacer la eliminacion
            instance = self.get_object(pk)
            instance.delete()
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
