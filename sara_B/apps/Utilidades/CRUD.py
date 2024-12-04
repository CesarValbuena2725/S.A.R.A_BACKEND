#Api General para la creaacion y visualizacion de los objetos segun el model Selcionado Dinamicamnete en la URL
from rest_framework import generics,status
from rest_framework.response import Response
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.Utilidades.Permisos import getModelName,GetSerializer

class BaseGeneral(generics.GenericAPIView):
    #Clase base para manejar operaciones generales con modelos.
    def get_queryset(self):
        return self.model.objects.all()  
    
    #Devuelve el serializer basado en el `namemodel` proporcionado en la solicitud.
    def get_serializer_class(self):
        #self.kwargs = Es un dicionario con todos los datos pasados en el Path
        namemodel = self.kwargs.get('namemodel')
        serializer_class = GetSerializer(namemodel)
        #En el Caso que el serialixers no exista devolvera un error
        if  None== serializer_class:
            raise NotFound(detail="Serialiazers no existe")
        return serializer_class
    
    #realiza la validacion del objeto indicado segun el model que corresponda.
    def get_object(self, pk, namemodel):
        model = getModelName(namemodel)
        if not model:
            raise NotFound(detail="Modelo no encontrado.", code=404)
        try:
            return model.objects.get(id=pk)
        except model.DoesNotExist:
            raise NotFound(detail=f"Objeto con id {pk} no encontrado en el modelo {namemodel}.", code=404)
    
     # Llama al Objetos despues de la Validacion
    def get(self, request, pk, namemodel):
        try:
            serializer_class = GetSerializer(namemodel)
            instance = self.get_object(pk, namemodel)
            serializer = serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

class GetGeneral(generics.GenericAPIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'PR', 'RC', 'CA', 'CC'] 
    """
    def get_queryset(self):
        return self.model.objects.all()  

    def get(self, request, namemodel):
        self.model = getModelName(namemodel)    
        try:
            if not self.model:
                return Response({"detail": "Modelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            serializer_class = GetSerializer(namemodel)
            # Llama a get_queryset
            queryset = self.get_queryset()  # Ahora se llama sin argumentos
            model_serializers = serializer_class(queryset, many=True) 
            return Response(model_serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

#ApiGenerla para la creacion de registros en los model
class PostGeneral(BaseGeneral): # Herendan funcionaloidades de las clase base 
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'CA']  # Roles Administrativos
    """
    def get(self, request, namemodel):
        self.model = getModelName(namemodel)    
        try:
            if not self.model:
                return Response({"detail": "Modelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            serializer_class = GetSerializer(namemodel)
            # Llama a get_queryset
            queryset = self.get_queryset()  # Ahora se llama sin argumentos
            model_serializers = serializer_class(queryset, many=True) 
            return Response(model_serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    def post(self, request, namemodel):
        # Obtiene el modelo basado en `namemodel`
        try:    
            model = getModelName(namemodel)
            if not model:
                return Response({"detail": "Modelo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

            # Obtiene el serializador basado en `namemodel` mediante `get_serializer_class`
            serializer_class = self.get_serializer_class()

            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


#Api General para la Actualizacion 
class PUT_General(BaseGeneral): # Herendan funcionaloidades de las clase base 
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD','CA'] 
    """  

    # Realiza la revision de los  nuevos datos para el objeto y realiza la actualizacion
    def put(self,request,pk,namemodel):
        try:
            modelos=self.get_object(pk)
            serializer_class = GetSerializer(namemodel)
            model_serializars=serializer_class(modelos,data=request.data)
            if model_serializars.is_valid():
                model_serializars.save()
                return Response(model_serializars.data, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response(model_serializars.errors,status=status.HTTP_400_BAD_REQUEST)
#Api General para la eliminacion  

class Delete_General(BaseGeneral):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD','CA'] 
    """
    # Llama al objeto después de la validación

    def delete(self, request, pk, namemodel):
        try:
            #instancion del objeto pasando como segundo parametro el modelo para poder hacer la eliminacion
            instance = self.get_object(pk, namemodel)
            instance.delete()
            return Response({"detail": "Eliminado"}, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


