from django.db import models
from apps.Solicitudes.models import Solicitud
from apps.Creacion_Formularios.models import CategoriaOpciones
from apps.Creacion_Formularios.models import CreacionFormulario, CampoItem, RespuestaCampo


class Opciones(models.Model):
    nombres = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=50)
    id_categoria_opciones = models.ForeignKey(CategoriaOpciones, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nombres


class Resultados(models.Model):
    respuesta_texto = models.CharField(max_length=100)
    respuesta_num = models.IntegerField()
    id_opciones = models.ForeignKey(Opciones, on_delete=models.CASCADE, null=False)
    id_solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, null=False)
    id_creacion_formulario = models.ForeignKey(CreacionFormulario, on_delete=models.CASCADE, null=False)
    id_campo_item = models.ForeignKey(CampoItem, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.id_creacion_formulario


class RespuestaResultados(models.Model):
    id_respuesta_campo = models.ForeignKey(RespuestaCampo, on_delete=models.CASCADE, null=False)
    id_resultados = models.ForeignKey(Resultados, on_delete=models.CASCADE, null=False)
