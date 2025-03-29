from django.db import models
from apps.Access.models import Estado
from apps.Utilidades.Permisos import set_model
from apps.Requests.models import Plan
from apps.Result.models import CategoriaOpciones


@set_model  
class Items(models.Model):
    nombre_items= models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=250, null=True)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones,on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre_items

@set_model
class Formulario(models.Model):
    nombre_formulario= models.CharField(max_length=50, null=False)
    estado= models.CharField(max_length=2,choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return  self.nombre_formulario
    
@set_model
class FormularioPlan(models.Model):
    id_formulario= models.ForeignKey(Formulario, on_delete=models.CASCADE, null=False)
    id_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False)

    class Meta:

        constraints=[

            models.UniqueConstraint(fields=['id_formulario','id_plan'], name="Formulario_plan_pk")
        ]
    
@set_model
class CreacionFormulario(models.Model):
    id_formulario= models.ForeignKey(Formulario, on_delete=models.CASCADE, null=False)
    id_items = models.ForeignKey(Items, on_delete=models.CASCADE, null=False)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['id_formulario','id_items'], name='Creacion_formulario_pk')
        ]
    def __str__(self):
        return self.id_formulario.nombre_formulario
