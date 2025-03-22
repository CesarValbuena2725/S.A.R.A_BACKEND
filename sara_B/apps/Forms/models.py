from django.db import models
from apps.Access.models import Estado
from apps.Results.models import CategoriaOpciones
from apps.Requests.models import Plan

# Create your models here.
class CategoriaItems(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)


class Items(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones, on_delete=models.CASCADE)
    id_categoria_items = models.ForeignKey(CategoriaItems, on_delete=models.CASCADE)


class Formulario(models.Model):
    nombre_formulario = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)



class CreacionPlantilla(models.Model):
    id_items = models.ForeignKey(Items, on_delete=models.CASCADE)
    id_formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE)


class FormularioPlan(models.Model):
    id_plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    id_formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE)

