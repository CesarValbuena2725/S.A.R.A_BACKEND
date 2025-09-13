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
def sucursal_base(db, convenio_bases):
    return Sucursal.objects.create(
        nombre="Sucursal Centro",
        ciudad="Bogotá",
        direccion="Calle 123",
        telefono="3209876543",
        estado="AC",
        id_convenio=convenio_bases,
        is_active=True
    )
@pytest.fixture
def empleado_base(db, sucursal_base):
    return Empleado.objects.create(
        nombres ="names test",
        apellidos="surnames tests",
        cedula ="1000555444",
        correo = "emailtests@gmail.com",
        estado = "AC",
        id_sucursal =sucursal_base,
        is_active = True
    )
@pytest.fixture
def usuario_base(db, empleado_base):
    return Usuario.objects.create(
        usuario= "user bases",
        password ="123456789",
        rol ="AD",
        estado ="AC",
        id_empleado= empleado_base
    )