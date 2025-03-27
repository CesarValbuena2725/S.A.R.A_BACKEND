from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from apps.Utilidades.Permisos import set_model

class Estado(models.TextChoices):
    ACTIVO = 'AC', 'Activo'
    INACTIVO = 'IN', 'Inactivo'

Errores = {
    'unique': 'Este nombre de usuario está en uso.',
    'blank': 'El campo usuario no puede estar vacío.',
    'max_length': 'Valor fuera de los límites.',
    'invalid': 'Formato no válido',
}

@set_model
class Convenio(models.Model):
    nombre = models.CharField(max_length=100, unique=True, error_messages=Errores)
    nit = models.CharField(max_length=100, unique=True, null=False, error_messages=Errores)
    telefono = models.BigIntegerField(error_messages=Errores)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre
    
@set_model
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100, error_messages=Errores)
    ciudad = models.CharField(max_length=100, error_messages=Errores)
    direccion = models.CharField(max_length=100, error_messages=Errores)
    telefono = models.BigIntegerField(error_messages=Errores)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
    
    
@set_model
class Empleado(models.Model):
    nombres = models.CharField(max_length=100, error_messages=Errores)
    apellidos = models.CharField(max_length=100, error_messages=Errores)
    cedula = models.BigIntegerField(unique=True, null=False, error_messages=Errores)
    correo = models.EmailField(max_length=50, unique=True, error_messages=Errores)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombres

class UsuarioManager(BaseUserManager):
    def create_user(self, usuario, password=None, **extra_fields):
        if not usuario:
            raise ValueError("El nombre de usuario es obligatorio")
        user = self.model(usuario=usuario, **extra_fields)
        user.password = make_password(password)  # Corrección aquí
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(usuario, password, **extra_fields)
    
@set_model
class Usuario(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMINISTRADOR = 'AD', "Administrador"
        PERITO = 'PR', "Perito"
        RECEPCIONISTA = 'RC', "Recepcionista"
        ADMIN_CONVENIO = 'CA', "Administrador Convenio"
        CONSULTOR_CONVENIO = 'CC', "Consultor Convenio"

    usuario = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=150)
    rol = models.CharField(max_length=2, choices=Roles.choices)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, default=1)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def verificar_contraseña(self, contraseña_plana):
        return check_password(contraseña_plana, self.password)

    def __str__(self):
        return self.usuario
