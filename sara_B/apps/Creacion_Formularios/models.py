from django.db import models


class ObligatorioEnum(models.TextChoices):
    SI = 'SI', 'si'
    NO = 'NO', 'no'


class CategoriaOpciones(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class CategoriaItems(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Items(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones, on_delete=models.CASCADE, null=False)
    id_categoria_items = models.ForeignKey(CategoriaItems, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre
    
class CreacionFormulario(models.Model):
    nombre_formulario = models.CharField(max_length=50)
    id_items = models.ForeignKey(Items, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombre_formulario


class TiposPlanes(models.Model):
    nombre = models.CharField(max_length=50)
    creacion_formulario = models.ForeignKey(CreacionFormulario, on_delete=models.CASCADE,null=False)

    def __str__(self):
        return self.nombre


class CampoItem(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_dato = models.CharField(max_length=100)
    obligatorio = models.CharField(max_length=2, choices=ObligatorioEnum.choices, default=ObligatorioEnum.NO)

    def __str__(self):
        return self.nombre


class RespuestaCampo(models.Model):
    valor = models.CharField(max_length=50)
    id_campo_item = models.ForeignKey(CampoItem, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.valor

