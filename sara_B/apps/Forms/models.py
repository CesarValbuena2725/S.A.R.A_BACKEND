from django.db import models
from apps.Access.models import Estado
from apps.Utilidades.Permisos import Set_Model
from apps.Result.models import CategoriaOpciones

class Tipo(models.TextChoices):
    STRING = 'STR', 'texto'
    ENTERO = 'INT', 'numero entero'
    OPCIONES = 'OPC', 'booleano'
    FECHA = 'FEC', 'fecha'

@Set_Model  
class Items(models.Model):
    nombre_items= models.CharField(max_length=50, null=False)
    tipo = models.CharField(max_length=250, choices=Tipo.choices, default=Tipo.OPCIONES)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones,on_delete=models.CASCADE )
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return self.nombre_items

@Set_Model
class CategoriaFormularios(models.Model):
    nombre = models.CharField(max_length=50)
    is_active= models.BooleanField(default=True)

    def __str__(self):
        return self.nombre



@Set_Model
class Formulario(models.Model):
    nombre_formulario= models.CharField(max_length=50, null=False)
    estado= models.CharField(max_length=2,choices=Estado.choices, default=Estado.ACTIVO)
    id_categoria = models.ManyToManyField(CategoriaFormularios)
    is_active = models.BooleanField(default=True)  

    def __str__(self):
        return  self.nombre_formulario
    
@Set_Model
class FormularioPlan(models.Model):
    id_formulario= models.ForeignKey(Formulario, on_delete=models.CASCADE, null=False)
    id_plan = models.ForeignKey('Requests.Plan', on_delete=models.CASCADE, null=False)
    is_active = models.BooleanField(default=True)  

    class Meta:

        constraints=[

            models.UniqueConstraint(fields=['id_formulario','id_plan'], name="Formulario_plan_pk")
        ]
    
@Set_Model
class CreacionFormulario(models.Model):
    id_formulario= models.ForeignKey(Formulario, on_delete=models.CASCADE, null=False)
    id_items = models.ForeignKey(Items, on_delete=models.CASCADE, null=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['id_formulario','id_items'], name='Creacion_formulario_pk')
        ]
    def __str__(self):
        return self.id_formulario.nombre_formulario
