import pytest
from apps.Access.models import Convenio, Sucursal, Empleado, Usuario

@pytest.fixture
def convenio_bases(db):
    Objetive =  Convenio.objects.create(
        nombre="Convenio Salud",
        nit="123456789",
        telefono="3001234567",
        estado="AC",
        is_active=True
    )

    return Objetive

@pytest.fixture
def sucursal_activa(db, convenio_bases):
    return Sucursal.objects.create(
        nombre="Sucursal Centro",
        ciudad="Bogotá",
        direccion="Calle 123",
        telefono="3209876543",
        estado="AC",
        id_convenio=convenio_bases,
        is_active=True
    )