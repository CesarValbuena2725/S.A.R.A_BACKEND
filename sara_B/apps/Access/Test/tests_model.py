# tests/unit/test_convenio_model.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from apps.Access.models import Convenio, Estado, Sucursal
from apps.Utilidades.General.base_pruebas import InformetionBAse


class ConvenioModelUnitTest(TestCase):
    """Tests unitarios puros para el modelo Convenio - Sin base de datos"""
    
    def test_creacion_convenio_valido(self):
        """Validar asignación de campos en creación de Convenio"""
        convenio = Convenio(
            nombre="Convenio Test",
            nit="123456789-1",
            telefono=1234567890,
            estado=Estado.ACTIVO
        )
        self.assertEqual(convenio.nombre, "Convenio Test")
        self.assertEqual(convenio.nit, "123456789-1")
        self.assertEqual(convenio.telefono, 1234567890)
        self.assertEqual(convenio.estado, Estado.ACTIVO)
        self.assertTrue(convenio.is_active)

    def test_estado_por_defecto_activo(self):
        """El estado por defecto debe ser ACTIVO"""
        convenio = Convenio(nombre="Test", nit="123", telefono=123)
        self.assertEqual(convenio.estado, Estado.ACTIVO)
        self.assertTrue(convenio.is_active)

    def test_str_representation(self):
        """La representación string debe ser el nombre"""
        convenio = Convenio(nombre="Mi Convenio", nit="123", telefono=123)
        self.assertEqual(str(convenio), "Mi Convenio")

    @patch('apps.Access.models.Sucursal.objects')
    def test_save_desactiva_sucursales_si_inactivo(self, mock_sucursal_manager):
        """Si se desactiva el convenio, también se desactivan sus sucursales"""
        mock_sucursal1 = MagicMock()
        mock_sucursal2 = MagicMock()
        mock_sucursal_manager.filter.return_value = [mock_sucursal1, mock_sucursal2]
        
        convenio = Convenio(nombre="Test", nit="123", telefono=123, is_active=False)
        convenio.save()
        
        mock_sucursal_manager.filter.assert_called_once_with(
            id_convenio=convenio,
            is_active=True
        )
        self.assertFalse(mock_sucursal1.is_active)
        self.assertFalse(mock_sucursal2.is_active)
        mock_sucursal1.save.assert_called_once()
        mock_sucursal2.save.assert_called_once()

    @patch('apps.Access.models.Sucursal.objects')
    def test_save_no_desactiva_sucursales_si_activo(self, mock_sucursal_manager):
        """Si el convenio está activo, no se modifican las sucursales"""
        convenio = Convenio(nombre="Test", nit="123", telefono=123, is_active=True)
        convenio.save()
        mock_sucursal_manager.filter.assert_not_called()


class SucursalModelUnitTest(InformetionBAse):
    """Tests unitarios puros para el modelo Sucursal"""
    

    def test_creacion_sucursal_valido(self):
        """Validar asignación de campos en creación de Sucursal"""
        sucursal = Sucursal(
            nombre="Sucursal Test",
            ciudad="Bogota",
            direccion="kr test #00",
            telefono=1234567890,
            estado=Estado.ACTIVO,
            id_convenio=self.CONVENIO
        )
        self.assertEqual(sucursal.nombre, "Sucursal Test")
        self.assertEqual(sucursal.ciudad, "Bogota")
        self.assertEqual(sucursal.direccion, "kr test #00")
        self.assertEqual(sucursal.telefono, 1234567890)
        self.assertEqual(sucursal.estado, Estado.ACTIVO)
        self.assertEqual(sucursal.id_convenio, self.CONVENIO)
        self.assertTrue(sucursal.is_active)

    def test_estado_por_defecto_activo(self):
        """El estado por defecto debe ser ACTIVO"""
        sucursal = Sucursal(
            nombre="Test",
            ciudad="Test Ciudad",
            direccion="Test Direccion",
            telefono=123,
            id_convenio=self.CONVENIO
        )
        self.assertEqual(sucursal.estado, Estado.ACTIVO)
        self.assertTrue(sucursal.is_active)
    
    def test_str_representation(self):
        """La representación string debe ser el nombre"""
        sucursal = Sucursal(nombre="Mi convenio",ciudad="test_cuidad", direccion ="test_dirrecion", telefono=1135, id_convenio=self.CONVENIO)
        self.assertEqual(str(sucursal),"Mi convenio")