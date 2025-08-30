# tests/unit/test_convenio_serializer.py
from django.test import TestCase
from apps.Access.models import Convenio, Estado
from rest_framework import serializers
from apps.Access.api.serializers import ConvenioSerializers
from unittest.mock import patch, MagicMock


# permite Crear objetos Falsos         self.mock_empresa = MagicMock(spec=Empresa)


class ConvenioSerializerUnitTest(TestCase):
    """Tests unitarios para el serializer - Mockeando ValidateFields"""
    
    def setUp(self):
        # ✅ Patch la ruta CORRECTA donde se USA ValidateFields en el serializer
        self.validate_fields_patcher = patch(
            'apps.Access.api.serializers.ValidateFields'  # Ruta exacta
        )
        self.mock_validate_fields_class = self.validate_fields_patcher.start()
        
        # ✅ Crear instancia mock para el validador
        self.mock_validator_instance = MagicMock()
        self.mock_validate_fields_class.return_value = self.mock_validator_instance
        
    def tearDown(self):
        self.validate_fields_patcher.stop()
    
    def test_serializer_valida_campos_correctamente(self):
        """El serializer debe llamar a las validaciones específicas de cada campo"""
        # Configurar el mock para que devuelva valores validados
        self.mock_validator_instance.validate.side_effect = [
            "NOMBRE_VALIDADO",  # Para nombre
            "NIT_VALIDADO",     # Para nit  
            "TEL_VALIDADO"      # Para telefono
        ]
        
        data = {
            'nombre': 'test nombre',
            'nit': '123456789-1',
            'telefono': 1234567890,
            'estado': Estado.ACTIVO
        }
        
        serializer = ConvenioSerializers(data=data)
        is_valid = serializer.is_valid()
        
        # Verificar que se llamaron las validaciones correctas
        self.mock_validator_instance.validate.assert_any_call('test nombre', type_validate='STRING')
        self.mock_validator_instance.validate.assert_any_call('123456789-1', 'NIT')
        self.mock_validator_instance.validate.assert_any_call(1234567890, 'TEL')
        
        # Verificar que los datos fueron validados
        self.assertTrue(is_valid)
        self.assertEqual(serializer.validated_data['nombre'], 'NOMBRE_VALIDADO')
        self.assertEqual(serializer.validated_data['nit'], 'NIT_VALIDADO')
        self.assertEqual(serializer.validated_data['telefono'], 'TEL_VALIDADO')
    
    
    def test_serializer_invalido_si_validacion_falla(self):
        #El serializer debe ser inválido si ValidateFields falla
        # Simular que la validación falla para NIT
        self.mock_validator_instance.validate.side_effect = [
            "NOMBRE_VALIDADO",  # Nombre ok
            serializers.ValidationError("NIT inválido"),  # NIT falla
            "TEL_VALIDADO"  # Teléfono ok (pero no se llegará aquí)
        ]
        
        data = {
            'nombre': 'test nombre',
            'nit': 'nit-invalido',
            'telefono': 123456789088
        }
        
        serializer = ConvenioSerializers(data=data)
        is_valid = serializer.is_valid()
        
        # Debe ser inválido por el NIT
        self.assertFalse(is_valid)
        self.assertIn('nit', serializer.errors)
    
    def test_serializer_crea_instancia_correctamente(self):
        #Test de creación de instancia desde datos validados
        validated_data = {
            'nombre': 'Convenio Test',
            'nit': '123456789-1',
            'telefono': 1234567890,
            'estado': Estado.ACTIVO
        }
        
        serializer = ConvenioSerializers()
        instance = serializer.create(validated_data)
        
        # Verificar que se crea la instancia correctamente
        self.assertIsInstance(instance, Convenio)
        self.assertEqual(instance.nombre, 'Convenio Test')
        self.assertEqual(instance.nit, '123456789-1')
        self.assertEqual(instance.telefono, 1234567890)
        self.assertEqual(instance.estado, Estado.ACTIVO)

    def test_serializer_actualiza_instancia_correctamente(self):
        """Test de actualización de instancia existente"""
        # Crear instancia real pero no persistida
        instance = Convenio()
        instance.nombre = "Viejo Nombre"
        instance.nit = "000000000-0"
        instance.telefono = 1111111111
        instance.estado = Estado.ACTIVO
        
        validated_data = {
            'nombre': 'Nuevo Nombre',
            'nit': '987654321-9',
            'telefono': 9876543210,
            'estado': Estado.INACTIVO
        }
        
        serializer = ConvenioSerializers()
        updated_instance = serializer.update(instance, validated_data)
        
        # Verificar actualización
        self.assertEqual(instance.nombre, 'Nuevo Nombre')
        self.assertEqual(instance.nit, '987654321-9')
        self.assertEqual(instance.telefono, 9876543210)
        self.assertEqual(instance.estado, Estado.INACTIVO)
        self.assertIs(updated_instance, instance)