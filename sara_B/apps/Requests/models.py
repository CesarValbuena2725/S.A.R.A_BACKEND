from django.db import models
from apps.Access.models import Estado
from django.utils.timezone  import localdate
from apps.Access.models import Empleado
from apps.Utilidades.Permisos import set_model
from apps.Access.models import Convenio,Sucursal


@set_model  
class TipoVehiculo(models.Model):
    nombre_vehiculo = models.CharField(max_length=50)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.nombre_vehiculo
@set_model
class Plan(models.Model):
    nombre_plan = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    cuestionario = models.ForeignKey('Forms.CategoriaFormularios', on_delete=models.CASCADE, null=True)
    id_tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE, null=True)
    lista_adicionales = models.ManyToManyField('Forms.Formulario')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_plan


@set_model 
class VehiculoPlan(models.Model):
    id_plan =models.ForeignKey(Plan, on_delete=models.CASCADE)
    id_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)  


    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['id_plan','id_vehiculo'], name="Vehiculo_plan_pk")
        ]

@set_model 
class Solicitud(models.Model):


    class Estados_solcitud(models.TextChoices):
        ACTIVO = 'AC', 'Activo'
        CANCELADO = 'CAL', 'Cancelado'
        PROGRESO = 'PRO','En Progreso'
        FINALIZADO ='FIN', 'Finalizado'

    placa= models.CharField(max_length=6)
    estado = models.CharField(max_length=3 , choices=Estados_solcitud.choices, default=Estados_solcitud.ACTIVO)
    telefono = models.CharField(max_length=10)
    fecha = models.DateField(default=localdate)
    fecha_fin = models.DateField(null=True, blank=True )
    id_convenio = models.ForeignKey(Convenio, on_delete=models.CASCADE)
    id_sucursal= models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    id_empleado =models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_plan =models.ForeignKey(Plan, on_delete=models.CASCADE)
    id_tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE)
    observaciones= models.TextField(null=True )
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.placa