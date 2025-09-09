# Standard library imports
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone  import localdate
from django.http import HttpResponse


# Third-party imports
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

# Local application imports
from apps.Access.models import Usuario, Empleado,UserSession
from apps.Access.api.serializers import (
    UsuarioSerializer,
    SolicitudRestablecerPassSerializers,
    RestablecerPasswordSerializers,
    loginserializer,
    EmpleadoSerialzers
)
from apps.Utilidades.permisos import RolePermission
from apps.Utilidades.tasks import Send_Email_Asyn


class CreateUser(APIView):
    # clase para hace Validacion de Tokes 
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    # Funcion para la validacion de Roles Permitidos para el path
    allowed_roles = ['AD','CA'] 
    
    model = Usuario
    serializer_class = UsuarioSerializer

    def get(self, request):
        try:
            usuario = self.model.objects.all()
            serializers = self.serializer_class(usuario, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        # Se toma la Data y se pasa la Serilizer para ser procesa 
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            objet = serializers.save()
            if isinstance(objet, Usuario):
                refresh=RefreshToken.for_user(user=objet)
                # Se Reponde los tokes de Acceso y usuarios creados 
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'usuario':serializers.data
                    
                },status=status.HTTP_201_CREATED)
            else:
                return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


#######################################################################################3
# clase que hace la verificacion de Credenciales y trae el token del usuario correspodiente 


class Login(APIView):
    # instancion los modelos y serealizers necesarios 
    model = Usuario
    serializer_class= loginserializer

    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "https://sarafrontend-git-main-andres-felipes-projects-b859d2f8.vercel.app"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Max-Age"] = "86400"  # Opcional: cache de preflight por 1 día
        return response


    def post(self, request):
        # se toma la data y se pasa a la serilizer para ser procesada
        serializer= self.serializer_class(data=request.data)
        if  not serializer.is_valid():
            return Response({'error': 'Usuario y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)            
        # Se guarda cada uno de los datos validos 
        usuario = serializer.validated_data['usuario']
        password = serializer.validated_data['password']
      
        try:
            # Buscar al usuario
            user = get_object_or_404(Usuario, usuario=usuario)

            if user.id_empleado.estado =="IN":
                return Response({'error': 'Usuarioooo no encontrado.'}, status=status.HTTP_403_FORBIDDEN)

            

            # Verificar si el usuario está activo
            if user.estado == 'AC':
                
                # Verificar la contraseña
                if not user.verificar_contraseña(password):
                    return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

                # Generar los tokens (JWT)
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                count_session =UserSession.objects.filter(id_usuario =user.pk).exists()
                
                user.last_login= localdate()
                user.save()
                print(user.last_login)
                #  Se hace la validancion para registar la Sesiones 
                if not count_session:
                    data= UserSession.objects.create(
                        id_usuario=user,
                        login_count = 1
                    )
                    data.save()
                else:
                    login_count = UserSession.objects.get(id_usuario=user.pk).registrar_login()
                # Serializar los datos del usuario

                return Response({
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'usuario': user.id_empleado.nombres,
                    'rol':user.rol,
                    'id_usuario': user.pk,
                    'id_empleado': user.id_empleado.pk,
                }, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Usuario inactivo. Contacte al administrador de SARA'}, status=status.HTTP_403_FORBIDDEN)
        except Http404:
            return Response({'error':'Usuario no encontrado.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



######################################################################################################
#Se realiza el envio de la dirrecion para restablecer contraseña

class SolicitudRestablecerPass(generics.GenericAPIView):
    serializer_class = SolicitudRestablecerPassSerializers

    def post(self,request):

        serializer = self.serializer_class(data= request.data)

        if serializer.is_valid():
            try:

                #Hace la instancia del Usuario 
                usuario = Usuario.objects.select_related('id_empleado').get(usuario=request.data['usuario'])
                if usuario.id_empleado.estado =="IN":
                    return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_403_FORBIDDEN)
                #Valida que el usuario Exista y este Activo
                if not usuario or usuario.estado=='IN':
                    return Response({'detail': 'No puede realizar el restablecimiento'}, 
                                    status=status.HTTP_401_UNAUTHORIZED)
                
                #Realiza la verificacion que el correo corespoda al restrado en sistemas
                if not Empleado.objects.filter(correo=request.data['correo'], id=usuario.id_empleado.pk).exists():
                    return Response({'detail': 'Correo no está registrado o no corresponde al usuario'}, 
                                    status=status.HTTP_404_NOT_FOUND)
                
                #genera los token necesarios para el restablecimiento
                token_generator = PasswordResetTokenGenerator()
                token = token_generator.make_token(usuario)
                uid = urlsafe_base64_encode(force_bytes(usuario.pk))
                reset_link = "http://localhost:5173/reset"

                #Realiza el envio del correo / pendiente por mejorar y cambiar esta aspecto
                try:
                    
                    data_usuario = EmpleadoSerialzers(usuario.id_empleado).data

                    Send_Email_Asyn.delay(affair="Restablecer Password",
                                            template="base_email.html",
                                            destinatario=[request.data['correo']], 
                                            solicitante=data_usuario, contexto=reset_link)
                    
                    return Response({'data':{'token':token,'uid':uid}},status=status.HTTP_200_OK)
                
                except Exception as error_valid:
                    return Response({'detail': 'Error al enviar el correo: ' + str(error_valid)}, 
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Usuario.DoesNotExist as e:
                error = str(e)
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#############################################################################

#Clase el cambio de contarseña 
class ContraseñaRestablecida(APIView):
    serializer_class =RestablecerPasswordSerializers
    
    def post(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(uid=uidb64, token=token)
                return Response({'msg': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)