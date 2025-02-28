from django.db import models
from apps.Access.models import Estado
from django.utils import timezone
from apps.Access.models import Empleado

class Plan(models.Model):
    nombre_plan= models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre_plan
    
class TipoVehiculo(models.Model):
    nombre_vehiculo= models.CharField(max_length=50)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre_vehiculo
    
class VehiculoPlan(models.Model):
    id_plan =models.ForeignKey(Plan, on_delete=models.CASCADE)
    id_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE)


    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['id_plan','id_vehiculo'], name="Vehiculo_plan_pk")
        ]

class Solicitud(models.Model):

    class Estados_solcitud(models.TextChoices):
        ACTIVO = 'AC', 'Activo'
        CANCELADO = 'CAL', 'Cancelado'
        PROGRESO = 'PRO','En Progreso'

    placa= models.CharField(max_length=6)
    central_servicios=models.CharField(max_length=50, default="AutoSef")
    estado = models.CharField(max_length=3 , choices=Estados_solcitud.choices, default=Estados_solcitud.ACTIVO)
    turno = models.IntegerField()
    telefono = models.CharField(max_length=10)
    fecha =  models.DateTimeField (default=timezone.now)
    id_empleado =models.ForeignKey(Empleado, on_delete=models.CASCADE, null=True)
    observaciones= models.TextField()
    id_plan =models.ForeignKey(Plan, on_delete=models.CASCADE)
    id_tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.placa