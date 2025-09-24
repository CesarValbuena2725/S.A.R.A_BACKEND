import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DataError
from apps.Access.models import Convenio, Sucursal, Empleado
from apps.Forms.models import CategoriaFormularios
from apps.Requests.models import Plan, TipoVehiculo, Solicitud


# -------------------------------------------------------------------
# Tests TipoVehiculo
# -------------------------------------------------------------------
@pytest.mark.django_db
class TestsTipoVehiculoModel:
    def Base_create_tipo_vehiculo(self, data):
        return TipoVehiculo.objects.create(**data)

    def test_create_correct(self):
        data = {
            "nombre_vehiculo": "Carro",
            "estado": "AC",
            "is_active": True,
        }
        instance = self.Base_create_tipo_vehiculo(data)

        assert instance.nombre_vehiculo == "Carro"
        assert instance.estado == "AC"
        assert instance.is_active is True

    def test_status_default(self):
        data = {
            "nombre_vehiculo": "Carro",
        }
        instance = self.Base_create_tipo_vehiculo(data)

        assert instance.estado == "AC"
        assert instance.is_active is True

    def test_create_incorrect(self):
        data = {
            "nombre_vehiculo": "Carro" * 70,  # excede el max_length
            "estado": "AC",
            "is_active": True,
        }
        with pytest.raises(DataError):
            self.Base_create_tipo_vehiculo(data)


# -------------------------------------------------------------------
# Tests Plan
# -------------------------------------------------------------------
@pytest.mark.django_db
class TestsPlanModel:
    def Base_create_plan(self, data):
        return Plan.objects.create(**data)

    def test_create_correct(self, tipo_vehiculo_base, Categoria_formulario_base):
        data = {
            "nombre_plan": "Plan Básico",
            "estado": "AC",
            "cuestionario": Categoria_formulario_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "is_active": True,
        }
        instance = self.Base_create_plan(data)

        assert instance.nombre_plan == "Plan Básico"
        assert instance.estado == "AC"
        assert isinstance(instance.cuestionario, CategoriaFormularios)
        assert isinstance(instance.id_tipo_vehiculo, TipoVehiculo)

    def test_status_default(self, tipo_vehiculo_base, Categoria_formulario_base):
        data = {
            "nombre_plan": "Plan Básico",
            "cuestionario": Categoria_formulario_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
        }
        instance = self.Base_create_plan(data)

        assert instance.is_active is True
        assert instance.estado == "AC"

    def test_create_incorrect(self, tipo_vehiculo_base, Categoria_formulario_base):
        data = {
            "nombre_plan": "Plan Básico" * 60,  # excede max_length
            "cuestionario": Categoria_formulario_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
        }
        with pytest.raises(DataError):
            self.Base_create_plan(data)

    def test_tipovehiculo_incorrect(self, Categoria_formulario_base):
        data = {
            "nombre_plan": "Plan Básico",
            "estado": "AC",
            "cuestionario": Categoria_formulario_base,
            "id_tipo_vehiculo": None,
            "is_active": True,
        }
        with pytest.raises((IntegrityError, ValidationError)):
            self.Base_create_plan(data)


# -------------------------------------------------------------------
# Tests Solicitud
# -------------------------------------------------------------------
@pytest.mark.django_db
class TestSolicitudModel:
    def Base_create_solicitud(self, data):
        return Solicitud.objects.create(**data)

    def test_create_correct(
        self, plan_base, convenio_bases, sucursal_base, empleado_base, tipo_vehiculo_base
    ):
        data = {
            "placa": "ABC123",
            "estado": "AC",
            "telefono": "3001234567",
            "fecha": date(2025, 9, 16),
            "fecha_fin": None,
            "id_convenio": convenio_bases,
            "id_sucursal": sucursal_base,
            "id_empleado": empleado_base,
            "id_plan": plan_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "observaciones": "Solicitud de prueba para validación.",
            "is_active": True,
        }
        instance = self.Base_create_solicitud(data)

        assert instance.placa == "ABC123"
        assert instance.estado == "AC"
        assert instance.telefono == "3001234567"
        assert instance.fecha == date(2025, 9, 16)
        assert isinstance(instance.id_convenio, Convenio)
        assert isinstance(instance.id_sucursal, Sucursal)
        assert isinstance(instance.id_empleado, Empleado)
        assert isinstance(instance.id_plan, Plan)
        assert isinstance(instance.id_tipo_vehiculo, TipoVehiculo)

    def test_status_default(
        self, plan_base, convenio_bases, sucursal_base, empleado_base, tipo_vehiculo_base
    ):
        data = {
            "placa": "ABC123",
            "telefono": "3001234567",
            "id_convenio": convenio_bases,
            "id_sucursal": sucursal_base,
            "id_empleado": empleado_base,
            "id_plan": plan_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "observaciones": "Solicitud de prueba para validación.",
        }
        instance = self.Base_create_solicitud(data)

        assert instance.is_active is True
        assert isinstance(instance.fecha, date)
        assert instance.estado == "AC"

    def test_convenio_incorrecto(
        self, plan_base, sucursal_base, empleado_base, tipo_vehiculo_base
    ):
        data = {
            "placa": "ABC123",
            "telefono": "3001234567",
            "id_convenio": None,  # inválido
            "id_sucursal": sucursal_base,
            "id_empleado": empleado_base,
            "id_plan": plan_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "observaciones": "Solicitud de prueba para validación.",
        }
        with pytest.raises((IntegrityError, ValidationError)):
            self.Base_create_solicitud(data)

    def test_empleado_incorrecto(
        self, plan_base, convenio_bases, sucursal_base, tipo_vehiculo_base
    ):
        data = {
            "placa": "ABC123",
            "telefono": "3001234567",
            "id_convenio": convenio_bases,
            "id_sucursal": sucursal_base,
            "id_empleado": None,  # inválido
            "id_plan": plan_base,
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "observaciones": "Solicitud de prueba para validación.",
        }
        with pytest.raises((IntegrityError, ValidationError)):
            self.Base_create_solicitud(data)

    def test_plan_incorrecto(
        self, convenio_bases, sucursal_base, empleado_base, tipo_vehiculo_base
    ):
        data = {
            "placa": "ABC123",
            "telefono": "3001234567",
            "id_convenio": convenio_bases,
            "id_sucursal": sucursal_base,
            "id_empleado": empleado_base,
            "id_plan": None,  # inválido
            "id_tipo_vehiculo": tipo_vehiculo_base,
            "observaciones": "Solicitud de prueba para validación.",
        }
        with pytest.raises((IntegrityError, ValidationError)):
            self.Base_create_solicitud(data)
