# Third-party imports
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local application imports
from apps.Requests.api.serializers import (
    PlanSerializers,
    SolicitudSerializers,
    TipovehiculoSerializers
)
from apps.Requests.models import Plan, Solicitud, TipoVehiculo, VehiculoPlan
from apps.Forms.models import Formulario, Items,CreacionFormulario
from apps.Forms.api.serializers import FormularioSerializers,ItemsSerializers,CreacionFormularioSerializers
from apps.Utilidades.CRUD import FiltroGeneral
from apps.Utilidades.permisos import BASE_PERMISOSOS, RolePermission
from apps.Utilidades.tasks import Send_Email_Asyn




class GetForms(generics.GenericAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =BASE_PERMISOSOS

    serializer_class= FormularioSerializers
    model_base  =  Formulario

    def get_queryset(self):
        return self.model_base.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        id_request = self.kwargs.get('id_request')

        try:
            instancie_request = Solicitud.objects.get(pk=id_request)
        except Solicitud.DoesNotExist:
            return Response({'detail': 'Solicitud no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            instancie_plan = Plan.objects.get(pk=instancie_request.id_plan.pk)
        except Plan.DoesNotExist:
            return Response({'detail': 'Plan no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Formularios por categoría principal
        forms = Formulario.objects.filter(id_categoria=instancie_plan.cuestionario, is_active=True)

        # Formularios adicionales
        data = list(forms)  

        for id_adicional in instancie_plan.lista_adicionales.all():
            adicionales = Formulario.objects.filter(pk=id_adicional.pk, is_active=True)
            data.extend(adicionales)  # Agrega los formularios adicionales a la lista

        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#!get para traer los items De los formularios:

class GetFormsItems(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =BASE_PERMISOSOS


    model = Items
    serializer_class = CreacionFormularioSerializers

    def get_queryset(self):
        query = self.model.objects.all()
        return query
    

    def get(self, request, *args, **kwargs):

        id_form = self.kwargs.get('id_form')
        
        data = CreacionFormulario.objects.filter(id_formulario=id_form)
        serializer = self.serializer_class(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GetRequests(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =BASE_PERMISOSOS

    serializer_class = SolicitudSerializers
    model_base = Solicitud
    def get_queryset(self):
        queryset = self.model_base.objects.filter(is_active=True)
        return queryset
    
    def get(self, request):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PostRequests(generics.GenericAPIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles =['AD', 'CA',] 
    
    model = Solicitud
    serializer_class=SolicitudSerializers

    def get_queryset(self):
        return self.model.objects.all()  


    def post(self, request):

        serializers=self.serializer_class(data=request.data)
        if not serializers.is_valid():
            return Response({"errors": serializers.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instance= serializers.save()
            contexto=f"Solicitud Cancelada {instance.pk}"
            affair= f"Nueva solicitud {instance.pk}"
            template="base_request.html"
            solicitante_data = self.serializer_class(instance).data

            # Realia el llamado a la tarea asincronica de enviao de correos 
            Send_Email_Asyn.delay(
                affair = affair,
                destinatario = ["tosaraweb@gmail.com",instance.id_empleado.correo],
                solicitante=self.serializer_class(instance).data,
                contexto=contexto,
                template =template
            )
            return Response(serializers.data ,status=status.HTTP_201_CREATED)

        except Exception as e:
             return Response(
                {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PatchRequest(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA']
    
    model = Solicitud
    serializer_class = SolicitudSerializers
    
    def get(self, request, pk):
        try:

            instance = self.model.objects.get(pk=pk)
            serializer = self.serializer_class(instance)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, pk):
        try:
            instancia = self.model.objects.get(pk=pk)
            #FIXME: Pendiente por Quiatar Cometarios, y Evitar modificaicon despues de que se Finalice 
            #!DEscomentariar despues de pruebas
            #if instancia.estado == 'FIN':
            #    return Response("Solicitud ya finalizada No se puede editar", status=status.HTTP_400_BAD_REQUEST)
        except self.model.DoesNotExist:
            return Response({"detail": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Serializar con la instancia existente y datos nuevos 
        model_serializers = self.serializer_class(instancia, data=request.data, partial=True)

        if not model_serializers.is_valid():
            return Response({"errors": model_serializers.errors}, status=status.HTTP_400_BAD_REQUEST)


        if model_serializers.validated_data.get('estado') == "CAL":
            try:
                #Crear Pantilla de modificacion
                Send_Email_Asyn.delay(
                #Es informacion infortante para el correo 
                contexto= instancia.pk,
                solicitante=self.serializer_class(instancia).data,
                #Asusnto de la Solcitud 
                affair= f"Solicitud Cancelada {instancia.pk}",
                #Base HTMl que se va a renderiar para el correo
                template="base_update_request.html",
                destinatario=["tosaraweb@gmail.com",instancia.id_empleado.correo],
                )

            except Exception as e:
                return Response(
                    {"detalles": f"Error al procesar la solicitud: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        model_serializers.save()
        return Response(model_serializers.data, status=status.HTTP_200_OK)

class DeleteRequestDB(APIView):
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD', 'RC', 'CA']
    
    def delete(self, request, pk):
        try:
            instancia = Solicitud.objects.get(pk=pk)
            instancia.is_active= False
            instancia.save()
            
            return Response({"detail": "Eliminado"}, status=status.HTTP_202_ACCEPTED)
        except Solicitud.DoesNotExist:
            return Response({"detail": "PK no válido"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



