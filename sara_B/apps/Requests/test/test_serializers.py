import pytest

from apps.Access.models import Convenio, Sucursal, Empleado
from apps.Forms.models import CategoriaFormularios
from apps.Requests.models import Plan, TipoVehiculo, Solicitud


import pytest
from rest_framework.exceptions import ValidationError, APIException
from apps.Requests.models import Plan
from apps.Forms.models import Formulario
from apps.Forms.api.serializers import FormularioSerializers,FormularioPlan
from apps.Requests.api.serializers  import PlanSerializers 


@pytest.mark.django_db
class TestPlanSerializers:

    def test_validate_nombre_plan_ok(self, tipo_vehiculo_base):
        serializer = PlanSerializers()
        result = serializer.validate_nombre_plan("Plan Básico")
        assert result == "Plan Básico"

    def test_validate_id_tipo_vehiculo_ok(self, tipo_vehiculo_base):
        serializer = PlanSerializers()
        result = serializer.validate_id_tipo_vehiculo(tipo_vehiculo_base)
        assert result == tipo_vehiculo_base

    def test_create_plan_invalid_nombre(self, tipo_vehiculo_base):
        data = {
            "nombre_plan": "",  # inválido
            "descripcion": "Test error",
            "precio": 20000,
            "id_tipo_vehiculo": tipo_vehiculo_base.id,
            "cuestionario": 1,
            "lista_adicionales": []
        }

        serializer = PlanSerializers(data=data)
        assert not serializer.is_valid()
        assert "nombre_plan" in serializer.errors

