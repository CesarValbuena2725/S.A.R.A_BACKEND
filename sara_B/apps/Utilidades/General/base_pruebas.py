# tests/base_api_test.py
from django.test import TestCase
from apps.Access.models import Convenio,Sucursal,Estado

class InformetionBAse(TestCase):
    CONVENIO = Convenio(
            nombre="Convenio Test",
            nit="123456789-1", 
            telefono=1234567890,
            estado=Estado.ACTIVO
        )

    SUCURSAL =Sucursal(
            nombre="convenio test",
            ciudad="Bogota",
            direccion="kr test # 00",
            telefono=1234567890,
            estado=Estado.ACTIVO,
            id_convenio=CONVENIO
        )


