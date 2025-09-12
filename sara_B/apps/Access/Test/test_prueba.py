import pytest
from apps.Access.models import Convenio
from apps.Access.api.serializers import ConvenioSerializers

import pytest
from rest_framework import serializers

@pytest.mark.django_db
def test_convenio_sucursal(convenio_bases, sucursal_activa):
    assert sucursal_activa.id_convenio == convenio_bases
    assert convenio_bases.nombre == "Convenio Salud"


@pytest.mark.django_db
class TestConvenioSerializer:

    def test_serializer_valido(self):
        """Debe crear un convenio cuando los datos son correctos"""
        data = {
            "nombre": "Convenio Test",
            "nit": "123456789-0",
            "telefono": "3201234567",
            "estado": "AC",
            "is_active": True,
        }
        serializer = ConvenioSerializers(data=data)
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert isinstance(instance, Convenio)
        assert instance.nombre == "Convenio Test"

    def test_nombre_invalido(self):
        """Debe fallar cuando el nombre no cumple validación"""
        data = {
            "nombre": "78",   # inválido
            "nit": "123456789-0",
            "telefono": "3201234567",
            "estado": "AC",
            "is_active": True,
        }
        serializer = ConvenioSerializers(data=data)
        assert not serializer.is_valid()
        assert "nombre" in serializer.errors
        #assert str(serializer.errors["nombre"][0]) == "El valor ingresado no cumple con el formato permitido para STRING."
        #" Por favor verifique los datos e intente nuevamente."

    def test_nit_invalido(self):
        """Debe fallar si el NIT no tiene el formato esperado"""
        data = {
            "nombre": "Convenio Test",
            "nit": "ABC",  # inválido
            "telefono": "3201234567",
            "estado": "AC",
            "is_active": True,
        }
        serializer = ConvenioSerializers(data=data)
        assert not serializer.is_valid()
        assert "nit" in serializer.errors

    def test_telefono_invalido(self):
        """Debe fallar si el teléfono no es numérico o tiene longitud incorrecta"""
        data = {
            "nombre": "Convenio Test",
            "nit": "123456789-0",
            "telefono": "telefono",  # inválido
            "estado": "AC",
            "is_active": True,
        }
        serializer = ConvenioSerializers(data=data)
        assert not serializer.is_valid()
        assert "telefono" in serializer.errors
