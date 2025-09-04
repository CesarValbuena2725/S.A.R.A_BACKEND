from django.test import TestCase
from apps.Access.models import Convenio, Estado
from apps.Access.api.serializers import ConvenioSerializers
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError

class ConvenioFieldValidationsTest(TestCase):
    """Tests específicos para validaciones de campos del modelo"""
    
    def test_nombre_max_length_validation(self):
        """El nombre no debe exceder 100 caracteres"""
        with self.assertRaises(ValidationError):
            convenio = Convenio(
                nombre='A' * 101,  # 101 caracteres
                nit="123456789-1",
                telefono=1234567890
            )
            convenio.full_clean()  # Esto debería fallar

    def test_nombre_unique_validation(self):
        """El nombre debe ser único (esto testea la constraint a nivel de modelo)"""
        # Nota: Para test unitario puro, mockearíamos la BD
        # Este test sería más adecuado como integration test
        
        # Mock de la verificación de unicidad
        with patch('apps.Access.models.Convenio.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = True  # Simular que ya existe
            
            convenio = Convenio(
                nombre="Nombre Duplicado",
                nit="123456789-1", 
                telefono=1234567890
            )
            
            with self.assertRaises(ValidationError):
                convenio.full_clean()

    def test_estado_choices_validation(self):
        """El estado debe ser una opción válida"""
        with self.assertRaises(ValidationError):
            convenio = Convenio(
                nombre="Test",
                nit="123456789-1",
                telefono=1234567890,
                estado="INVALIDO"  # Estado no válido
            )
        self.assertEqual(convenio.full_clean())