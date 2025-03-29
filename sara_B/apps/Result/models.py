from django.db import models
from apps.Access.models import Estado
from apps.Utilidades.Permisos import set_model

# Create your models here.
#Modelo Temporal pruebas 
@set_model
class CategoriaOpciones(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)

    def __str__(self):
        return self.nombre
    
@set_model
class Opciones(models.Model):
    nombre_opcione= models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=250, null=True)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones,on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre_opcione