from django.db import models
from apps.Access.models import Estado
from django.utils.timezone  import localdate
from apps.Access.models import Empleado
from apps.Utilidades.permisos import Set_Model
from apps.Access.models import Convenio,Sucursal


@Set_Model  
class TipoVehiculo(models.Model):
    nombre_vehiculo = models.CharField(max_length=50)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.nombre_vehiculo
@Set_Model
class Plan(models.Model):
    nombre_plan = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    cuestionario = models.ForeignKey('Forms.CategoriaFormularios', on_delete=models.CASCADE, null=True)
    id_tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE, null=True)
    lista_adicionales = models.ManyToManyField('Forms.Formulario')
    is_active = models.BooleanField(default=True)

    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre_plan'], condition=models.Q(is_active=True), name='unique_nombre_plan_activo')
        ]
    
    def save(self, *args,**kwargs):
        if not self.is_active:
            from apps.Forms.models import FormularioPlan
            FormularioPlan.objects.filter(id_plan=self).delete()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.nombre_plan



@Set_Model 
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