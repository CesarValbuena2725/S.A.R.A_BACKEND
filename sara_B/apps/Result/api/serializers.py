from rest_framework import serializers
from apps.Result.models import CategoriaOpciones,Opciones
from apps.Utilidades.Permisos import set_serializers

@set_serializers
class CategoriaOpcionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaOpciones
        fields = '__all__'

@set_serializers
class OpcionesSeralizers(serializers.ModelSerializer):
    class Meta:
        model = Opciones
        fields='__all__'