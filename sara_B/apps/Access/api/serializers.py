from rest_framework import serializers
from apps.Access.models import Convenio,Sucursal,Empleado,Usuario,UserSession
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from rest_framework.exceptions import ValidationError
from apps.Utilidades.permisos import Set_Serializers
from apps.Utilidades.General.validations import ValidateFields


@Set_Serializers
class ConvenioSerializers(serializers.ModelSerializer):
    class Meta:
        model = Convenio
        fields = '__all__'
    
    # Funciones que hacen validacion de Cada campo 
    def validate_nombre(self, value):
        return ValidateFields().validate(value, type_validate="STRING")
    def validate_nit(self,value):
        return ValidateFields().validate(value,"NIT")
    def validate_telefono(self,value):
        return ValidateFields().validate(value,"TEL")

@Set_Serializers
class SucursalSerializers(serializers.ModelSerializer):
    class Meta:
        model=Sucursal
        fields= '__all__'
    def validate_nombre(self,value):
        return ValidateFields().validate(value,"STRING")
    def validate_ciudad(self,value):
        return ValidateFields().validate(value,"STRING")
    def validate_telefono(self,value):
        return ValidateFields().validate(value,"TEL")
    
    def validate_id_convenio(self,value):
        return ValidateFields().Validate_Relacion(value)
        
@Set_Serializers
class EmpleadoSerialzers(serializers.ModelSerializer):
    class Meta:
        model=Empleado
        fields='__all__'

    #funciones para validaciones de Datos    
    def validate_nombres(self, value):
        return ValidateFields().validate(value,"STRING")
    def validate_apellidos(self, value):
        return ValidateFields().validate(value,"STRING")
    def validate_cedula(self, value):
        return ValidateFields().validate(value,"CEDULA")
    def validate_correo(self, value):
        return ValidateFields().validate(value,"EMAIL")
    def validate_id_sucursal(self,value):
        return ValidateFields().Validate_Relacion(value)
    
@Set_Serializers
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)  # Hacer opcional

    class Meta:
        model = Usuario
        exclude = ['is_active', 'is_staff', 'is_superuser', ]

    def validate_usuario(self, value):
        data =ValidateFields().Length_min(value, 6)
        if not data:
            return data
        return ValidateFields().validate(data,"STRING").lower()
        
    def validate_password(self,value):
        return ValidateFields().validate(value,"PASSWORD")
    
    def validate_id_empleado(self, value):
        return ValidateFields().Validate_Relacion(value)

    def update(self, instance, validated_data):
        """ Evitar sobreescribir la contraseña si no se envía en la solicitud """
        validated_data.pop('password', None)  # Si password no está en validated_data, no lo cambia
        return super().update(instance, validated_data)

class SerializersUserSession(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = '__all__'


class loginserializer(serializers.Serializer):
    usuario = serializers.CharField(max_length=100)
    password= serializers.CharField(max_length=250)

    def validate_usuario(self, value):
        data = ValidateFields().validate(value,"STRING")
        return data.lower()

class SolicitudRestablecerPassSerializers(serializers.Serializer):
    usuario = serializers.CharField(max_length=100)
    correo = serializers.EmailField(max_length=100)

    class Meta:
        fields = ['correo', 'usuario']

    def validate_usuario(self, value):
        data = ValidateFields().validate(value,"STRING")
        return data.lower()
    
    def validate_correo(self, value):
        return ValidateFields().validate(value,"EMAIL")
      

class RestablecerPasswordSerializers(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=10)
    password_conf = serializers.CharField(write_only=True, min_length=10)

    def validate(self, data):
        if data['password'] != data['password_conf']:
            raise ValidationError("Las contraseñas no coinciden.")
        return data

    def save(self, uid, token):
        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = Usuario.objects.get(pk=user_id)
        except (ValueError, TypeError, OverflowError, UnicodeDecodeError):
            raise ValidationError("ID de usuario inválido.")
        except Usuario.DoesNotExist:
            raise ValidationError("Usuario no encontrado.")
        
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            raise ValidationError("El token no es válido o ha expirado.")
        
        user.set_password(self.validated_data['password'])
        user.save()