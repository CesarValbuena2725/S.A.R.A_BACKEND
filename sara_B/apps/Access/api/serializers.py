from rest_framework import serializers
from apps.Access.models import Convenio,Sucursal,Empleado,Usuario
from .Validaciones import logitud_minima,validate_positive,validate_number,validate_text
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from rest_framework.exceptions import ValidationError
from apps.Utilidades.Permisos import set_serializers




@set_serializers
class ConvenioSerializers(serializers.ModelSerializer):
    class Meta:
        model=Convenio
        fields= '__all__'


    # Funciones que hacen validacion de Cada campo 

@set_serializers
class SucursalSeralizers(serializers.ModelSerializer):
    class Meta:
        model=Sucursal
        fields= '__all__'
        
@set_serializers
class EmpleadoSerialzers(serializers.ModelSerializer):
    class Meta:
        model=Empleado
        fields='__all__'

@set_serializers
class UsuarioSerializers(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)  # Hacer opcional

    class Meta:
        model = Usuario
        exclude = ['is_active', 'is_staff', 'is_superuser', 'last_login']

    def validate_usuario(self, value):
        if logitud_minima(value):
            return validate_text(value)
        
    def validate_id_empleado(self, value):
            try:
                if value.estado != "IN":
                    return value
                raise serializers.ValidationError("Empleado inactivo.")
            except Empleado.DoesNotExist:
                raise serializers.ValidationError("Empleado no encontrado.")


    def update(self, instance, validated_data):
        """ Evitar sobreescribir la contraseña si no se envía en la solicitud """
        validated_data.pop('password', None)  # Si password no está en validated_data, no lo cambia
        return super().update(instance, validated_data)


class SolicitudRestablecerPassSerializers(serializers.Serializer):
    usuario = serializers.CharField(max_length=100)
    correo = serializers.EmailField(max_length=100)

    class Meta:
        fields = ['correo', 'usuario']
      
class RestablecerPasswordSerializers(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=10)
    password_conf = serializers.CharField(write_only=True, min_length=10)

    def validate(self, data):
        if data['password'] != data['password_conf']:
            raise ValidationError("Las contraseñas no coinciden.")
        return data

    def save(self, uid, token):
        try:
            user_id = urlsafe_base64_decode (uid).decode()  
            user = Usuario.objects.get(pk=user_id)
        except (ValueError, TypeError, OverflowError, Usuario.DoesNotExist):
            raise ValidationError("El enlace no es válido.")
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            raise ValidationError("El token no es válido o ha expirado.")
    
        user.set_password(self.validated_data['password'])
        user.save()

class loginserializers(serializers.Serializer):
    usuario = serializers.CharField(max_length=100)
    password= serializers.CharField(max_length=250)