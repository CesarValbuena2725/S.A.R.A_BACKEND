from rest_framework import serializers
from apps.Forms.models import FormularioPlan, CategoriaItems, CreacionPlantilla, Items, Formulario
from apps.Utilidades.Permisos import set_serializers


@set_serializers
class CategoriaItemsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CategoriaItems
        fields = '__all__'


@set_serializers
class FormularioPlanSerializers(serializers.ModelSerializer):
    class Meta:
        model = FormularioPlan
        fields = '__all__'


@set_serializers
class CreacionPlantillaSerializers(serializers.ModelSerializer):
    class Meta:
        model = CreacionPlantilla
        fields = '__all__'


@set_serializers
class ItemsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = '__all__'



class FormularioSerializers(serializers.ModelSerializer):

    items = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    class Meta:
        model = Formulario
        fields = '__all__'