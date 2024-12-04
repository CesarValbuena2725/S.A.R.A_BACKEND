from rest_framework.views import APIView
from rest_framework import status,generics
from apps.Access.api.serializers import UsuarioSerializers,SolicitudRestablecerPassSerializers,RestablecerPasswordSerializers
from apps.Access.models import Usuario, Empleado
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.authentication import TokenAuthentication
from ...Utilidades.Permisos import RolePermission
from apps.Utilidades.Permisos import RolePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from apps.Utilidades.Email.email_base import send_email_sara




#Clase para realiza la Creacion del usuarios con la asignacion de toekn para verificaicon      
class CreateUser(APIView):
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, RolePermission]
    allowed_roles = ['AD','CA'] 
    """
    model = Usuario
    serializer_class = UsuarioSerializers

    def get(self, request):
        try:
            usuario = self.model.objects.all()
            serializers = self.serializer_class(usuario, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        serializers = self.serializer_class(data=request.data)
        if serializers.is_valid():
            objet = serializers.save()
            if isinstance(objet, Usuario):
                #token, created = Token.objects.get_or_create(user=objet)
                #return Response({'token': token.key, **serializers.data}, status=status.HTTP_201_CREATED)

                refresh=RefreshToken.for_user(user=objet)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'usuario':serializers.data
                    
                },status=status.HTTP_201_CREATED)
            else:
                return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

# clase que hace la verificacion de Credenciales y trae el token del usuario correspodiente 

class Login(APIView):

    def get(self, request):
        try:
            usuario = self.model.objects.all()
            serializers = self.serializer_class(usuario, many=True)
            return Response(serializers.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def post(self, request):
        usuario = request.data.get('usuario')
        password = request.data.get('password')

        if not usuario or not password:
            return Response({'error': 'Usuario y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Buscar al usuario
            user = get_object_or_404(Usuario, usuario=request.data['usuario'])

            # Verificar si el usuario está activo
            if user.estado == 'AC':
                # Verificar la contraseña
                if not user.Verificar_contraseña(request.data['password']):
                    return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

                # Generar los tokens (JWT)
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                # Serializar los datos del usuario
                serializers = UsuarioSerializers(instance=user)

                return Response({
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'usuario': serializers.data['usuario']
                }, status=status.HTTP_200_OK)

            else:
                return Response({'error': 'Usuario inactivo. Contacte al administrador de SARA'}, status=status.HTTP_403_FORBIDDEN)

        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
#Se realiza el envio de la dirrecion para restablecer contraseña
class SolicitudRestablecerPass(generics.GenericAPIView):
    serializer_class = SolicitudRestablecerPassSerializers

    def post(self,request):
        serializer = self.serializer_class(data= request.data)
        if serializer.is_valid():
            try:
                #Hace la instancia del Objetos segun el usuario que se indica en el formulario
                usuario = Usuario.objects.select_related('id_empleado').get(usuario=request.data['usuario'])

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
                reset_link = f"http://127.0.0.1:8000/access/restablecerpassword/{uid}/{token}/"

                #Realiza el envio del correo / pendiente por mejorar y cambiar esta aspecto
                try:
                    send_email_sara(reset_link,"Restablecer Contarseña SARA",[request.data['correo']],"base_email.html",usuario)
                    #send_mail('Restablecer Contarseña SARA',f'link de restablecimineto  {reset_link}',None,[request.data['correo']] )
                    return Response({'message':'Se realizo el envio correo para el restablecimiento de contarseña'}, status=status.HTTP_200_OK)
                except Exception as error_valid:
                    return Response({'detail': 'Error al enviar el correo: ' + str(error_valid)}, 
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Usuario.DoesNotExist as e:
                error = str(e)
                return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Serealiza el cambio de contarseña 
class ContraseñaRestablecida(APIView):
    serializer_class =RestablecerPasswordSerializers
    
    def post(self, request, uidb64, token):
        print("UIDB64:", uidb64)
        print("token: ",token)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(uid=uidb64, token=token)
                return Response({'msg': 'Contraseña restablecida correctamente'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)