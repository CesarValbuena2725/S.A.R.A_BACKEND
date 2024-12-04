from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.hashers import make_password,check_password

class Estado(models.TextChoices):
    ACTIVO = 'AC', 'Activo'
    INACTIVO = 'IN', 'Inactivo'

Errores={'unique': 'Este nombre de usuario  en uso.',
        'blank': 'El campo usuario no puede estar vacío.',
        'max_length': 'Valor no fuera de los limites',
        'invalid':'Formato no valido',

        }

class Convenio(models.Model):
    nombre = models.CharField(max_length=100, unique=True,error_messages=Errores)
    nit = models.CharField(max_length=100, unique=True, null=False,error_messages=Errores)
    telefono = models.BigIntegerField(error_messages=Errores)
    ciudad = models.CharField(max_length=100,error_messages=Errores)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre

class Sucursal(models.Model):
    nombre=models.CharField(max_length=100,error_messages=Errores)
    ciudad=models.CharField(max_length=100,error_messages=Errores)
    direccion= models.CharField(max_length=100,error_messages=Errores)
    telefono = models.BigIntegerField(error_messages=Errores)
    estado= models.CharField(max_length=2,choices=Estado.choices, default=Estado.ACTIVO)
    convenio= models.ForeignKey(Convenio, on_delete=models.CASCADE,null=False)

    class Meta:
        ordering= ['nombre']

    def __str__(self):
        return self.nombre

class Empleado(models.Model):
    nombres= models.CharField(max_length=100, error_messages=Errores  )
    apellidos=models.CharField(max_length=100)
    cedula= models.BigIntegerField(unique=True,error_messages=Errores,null=False)
    correo= models.EmailField(max_length=50,unique=True,error_messages=Errores)
    estado= models.CharField(max_length=2,choices=Estado.choices, default=Estado.ACTIVO)
    id_sucursal= models.ForeignKey(Sucursal, on_delete= models.CASCADE, null=False)

    def __str__ (self):
        return self.nombres

"""
linea de Comando Que relaixa el remplazo de una model por Defecto de Django "User" por 
model personalida "Usuario", mediante la BaseUserManager modifica el model User  nuestro gusto

"""

class UsuarioManager(BaseUserManager):
    def create_user(self, usuario, password=None, **extra_fields):
        if not usuario:
            raise ValueError("El nombre de usuario es obligatorio")
        user = self.model(usuario=usuario, **extra_fields)
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


"""
Con las heredan las clases para poder hacer el cambio de manera precisa, Se necesitas los mismos campos por defecto del moel user 
y se agregan los campos Personalizados 
"""

class Usuario(AbstractBaseUser, PermissionsMixin):
    
    class Roles(models.TextChoices):
        administrador= 'AD',"Administrador"
        perito='PR', 'Perito'
        recepcionista='RC','Recepcionista'
        adconvenio='CA','Administardor Convenio'
        convenioc='CC','Consultor Convenio'

    usuario = models.CharField(max_length=100, unique=True)
    password= models.CharField(max_length=150)
    rol = models.CharField(max_length=2, choices=Roles.choices)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    id_empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)  # Último in
    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.password = make_password(self.password)
        super(Usuario, self).save(*args, **kwargs)

    def Verificar_contraseña(self, contarseña_plana):
        return check_password(contarseña_plana, self.password)

    def __str__(self):
        return self.usuario

