from django.db import models
from apps.Access.models import Estado,Empleado
from django.utils import timezone



class EstadosSolicitud(models.TextChoices):
    ACTIVO = 'ACT', 'Activo'
    PROGRESO = 'PRO','En Progreso'
    CANCELADO= 'CAN', 'Cancelado'


class Cliente(models.Model):

    class TiposDocumentos(models.TextChoices):
        CEDULA= 'CC','Cedula'
        NIT = 'NI', 'NIT'
        CEDULAEXT = 'CT', 'Cedula Extrangerida'
        
    primer_nombre= models.CharField(max_length=100)
    segundo_nombre=models.CharField(max_length=100)
    primer_apellido= models.CharField(max_length=100)
    segundo_apellido= models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=2, choices=TiposDocumentos.choices, default=TiposDocumentos.CEDULA)
    documento = models.CharField(max_length=20)
    telefono = models.BigIntegerField()
    direccion = models.CharField (max_length=50)
    correo = models.EmailField(max_length=100)

    def __str__(self):
        return (f"{self.primer_nombre}  {self.primer_apellido}")

class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    estado= models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre

class Solicitud(models.Model):

    placa = models.CharField(max_length=6)
    centro_servicio= models.CharField(max_length=100, default= "AutoSef")
    turno = models.IntegerField()
    estado = models.CharField(max_length=3, choices=EstadosSolicitud.choices, default= EstadosSolicitud.ACTIVO)
    fecha =  models.DateField (default=timezone.now)
    observaciones= models.CharField(max_length=250)
    empleado = models.ForeignKey(Empleado,on_delete= models.CASCADE, null=False)
    cliente= models.ForeignKey(Cliente, on_delete=models.CASCADE, null=False)
    categoria_servicio= models.ForeignKey(CategoriaServicio, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.placa
