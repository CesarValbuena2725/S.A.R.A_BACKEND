from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from apps.Utilidades.permisos import Set_Model
from django.utils import timezone
from apps.Utilidades.General.validations import MESSAGES_ERROR

class Estado(models.TextChoices):
    ACTIVO = 'AC', 'Activo'
    INACTIVO = 'IN', 'Inactivo'


Errores = {
    'unique': 'Este dato ya existe en el sistema. Verifique e intente con uno distinto.',
    'blank': 'El campo usuario no puede estar vacío.',
    'max_length': 'Valor fuera de los límites.',
    'invalid': 'Formato no válido',
}

@Set_Model
class Convenio(models.Model):
    nombre = models.CharField(max_length=40, unique=True, error_messages=MESSAGES_ERROR)
    nit = models.CharField(max_length=50, null=False, error_messages=MESSAGES_ERROR)
    telefono = models.CharField(max_length=10,error_messages=MESSAGES_ERROR)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    is_active = models.BooleanField(default=True) 
    
    #Restrcion para evitar remitir nit con datos Activos, pero permite si el dato esta inactivo
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nit'], condition=models.Q(is_active=True), name='unique_nit_activo')
        ]

    def save(self, *args, **kwargs):
        if not self.is_active:
            sucursales = Sucursal.objects.filter(id_convenio=self, is_active=True)
            for sucursal in sucursales:
                sucursal.is_active = False
                sucursal.save()  
        super().save(*args, **kwargs)


    def __str__(self):
        return self.nombre
    
@Set_Model
class Sucursal(models.Model):
    nombre = models.CharField(max_length=50,unique=True, error_messages=MESSAGES_ERROR)
    ciudad = models.CharField(max_length=50, error_messages=MESSAGES_ERROR)
    direccion = models.CharField(max_length=50, error_messages=MESSAGES_ERROR)
    telefono = models.CharField(max_length=10,error_messages=MESSAGES_ERROR)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE, null=False)
    is_active = models.BooleanField(default=True)  

    def save(self,*args,**kwargs):
        if not self.is_active:
            Empleado.objects.filter(id_sucursal=self, is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
    
@Set_Model
class Empleado(models.Model):
    nombres = models.CharField(max_length=60, error_messages=MESSAGES_ERROR)
    apellidos = models.CharField(max_length=60, error_messages=MESSAGES_ERROR)
    cedula = models.CharField(max_length=15,unique=True, null=False, error_messages=MESSAGES_ERROR)
    correo = models.EmailField(max_length=50, unique=True, error_messages=MESSAGES_ERROR)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=False)
    is_active = models.BooleanField(default=True)  
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cedula'], condition=models.Q(is_active=True), name='unique_cedula_activo')
        ]

    def save(self, *args,**kwargs):
        if not self.is_active:
            Usuario.objects.filter(id_empleado=self, is_active= True).update(is_active=False)
        super().save(*args, **kwargs)

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
    
@Set_Model
class Usuario(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        ADMINISTRADOR = 'AD', "Administrador"
        PERITO = 'PR', "Perito"
        RECEPCIONISTA = 'RC', "Recepcionista"
        ADMIN_CONVENIO = 'CA', "Administrador Convenio"
        CONSULTOR_CONVENIO = 'CC', "Consultor Convenio"

    usuario = models.CharField(max_length=20, unique=True ,error_messages=MESSAGES_ERROR)
    password = models.CharField(max_length=150)
    rol = models.CharField(max_length=2, choices=Roles.choices)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now, null=True, blank=True)


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


class UserSession(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    login_count = models.IntegerField(default=0)
    last_login = models.DateTimeField( default= timezone.now, null=True, blank=True)

    def registrar_login(self):
        self.login_count += 1
        self.last_login = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.id_usuario} - {self.login_count} inicios"
