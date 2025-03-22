from django.db import models
from apps.Access.models import Estado

# Create your models here.
class CategoriaOpciones(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=Estado.choices, default=Estado.ACTIVO)
    