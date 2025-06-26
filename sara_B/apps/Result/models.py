from django.db import models
from apps.Access.models import Estado
from apps.Utilidades.Permisos import set_model

from apps.Requests.models import Solicitud

# Create your models here.
#Modelo Temporal pruebas 
@set_model
class CategoriaFotos(models.TextChoices):
    PRINCIAPAL = 'PRI', 'Categoría 1'
    ACCESORIOS = 'ACC', 'Categoría 2'
    GENERALES = 'GEN', 'Categoría 3'

class CategoriaOpciones(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    is_active = models.BooleanField(default=True) 


    def __str__(self):
        return self.nombre
    
@set_model
class Opciones(models.Model):
    nombre_opcion= models.CharField(max_length=50, null=False)
    descripcion = models.CharField(max_length=250, null=True)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones,on_delete=models.CASCADE, null=False)
    is_active = models.BooleanField(default=True) 


    def __str__(self):
        return self.nombre_opcion
    
class Respuestas(models.Model):
    
    id_solicitud = models.ForeignKey(Solicitud,on_delete=models.CASCADE,null= False)
    id_formulario = models.ForeignKey('Forms.Formulario', on_delete=models.CASCADE, null=False)
    id_item = models.ForeignKey('Forms.Items', on_delete=models.CASCADE, null=False)
    id_opcion = models.ForeignKey(Opciones, on_delete=models.CASCADE, null= True)
    respuesta_texto =  models.CharField(max_length=60 , null= True)
    is_active = models.BooleanField(default=True) 


    def __str__(self):
        return self.id_solicitud.placa
    
class Fotos(models.Model):

    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, null=True)
    categoria_foto = models.CharField(max_length=3, choices=CategoriaFotos.choices, default=CategoriaFotos.GENERALES)
    imagen = models.ImageField(upload_to='imagenes/')
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.categoria_foto