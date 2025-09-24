import pytest
from apps.Access.api.serializers import ConvenioSerializers,SucursalSerializers,EmpleadoSerialzers,UsuarioSerializer


@pytest.mark.django_db
class TestConvenioSerializer:

    def test_serializer_valido(self):
       # Debe crear un convenio cuando los datos son correctos
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

    def test_nombre_invalido(self):
       # Debe fallar cuando el nombre no cumple validación
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
        assert str(serializer.errors["nombre"][0]) == "El valor ingresado no cumple con el formato permitido para STRING. Por favor verifique los datos e intente nuevamente."
        #" Por favor verifique los datos e intente nuevamente."

    def test_nit_invalido(self):
       # Debe fallar si el NIT no tiene el formato esperado
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
        #Debe fallar si el teléfono no es numérico o tiene longitud incorrecta
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

@pytest.mark.django_db
class TestBranchSerializer:
    def Base_serializer(self,data):
        return SucursalSerializers(data=data)
    
    def test_serializer_correcte(self, convenio_bases):
        data={
            'nombre':"test branch",
            'ciudad':"Bogota",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'estado':"AC",
            'id_convenio':convenio_bases.pk,
            'is_active':True
        }

        instance = self.Base_serializer(data)
        assert instance.is_valid(), instance.errors
        instance = instance.save()
    
    def test_name_serializer(self,convenio_bases):
        data ={
            'nombre':"test815 branch",
            'ciudad':"Bogota",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':convenio_bases.pk,
        }
        instance = self.Base_serializer(data)
        assert not instance.is_valid()
        assert 'nombre' in instance.errors
    
    def test_cuidad_serializer(self, convenio_bases):
        data ={
            'nombre':"test branch",
            'ciudad':"kr 27 l 72 a 23 sur",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':convenio_bases.pk,
        }
        instance = self.Base_serializer(data)
        assert not  instance.is_valid()
        assert 'ciudad' in instance.errors

    def test_relation_inactive(self,convenio_bases):
        convenio_bases.is_active =False
        convenio_bases.save()
        data={
            'nombre':"test branch",
            'ciudad':"Bogota",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':convenio_bases.pk,
        }
        instance = self.Base_serializer(data=data)
        assert not instance.is_valid() 
        assert 'id_convenio' in instance.errors
    def test_relation_status_incorrect(self, convenio_bases):
        convenio_bases.estado ="IN"
        convenio_bases.save()
        data={
            'nombre':"test branch",
            'ciudad':"Bogota",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':convenio_bases.pk,
        }
        instance = self.Base_serializer(data=data)
        assert not instance.is_valid() 
        assert 'id_convenio' in instance.errors

@pytest.mark.django_db  
class TestEmployeSerializer:
    def base_serializer(self,data):
        return EmpleadoSerialzers(data=data)
    
    def test_correct_serializer(self,sucursal_base):
        data ={
            'nombres':"name test",
            'apellidos':"surname test",
            'cedula':"1000455391",
            'correo':"testemial@gmail.com",
            'id_sucursal':sucursal_base.pk
        }
        instance = self.base_serializer(data)

        assert instance.is_valid(), instance.errors  

        obj = instance.save()  

        assert obj.nombres == "Name Test"
        assert obj.apellidos =="Surname Test"
        
    def test_cedula_serializer(self,sucursal_base):
        data ={
            'nombres':"name test",
            'apellidos':"surname test",
            'cedula':"yasysy",
            'correo':"testemial@gmail.com",
            'id_sucursal':sucursal_base.pk
        }
        instance = self.base_serializer(data)
        assert not instance.is_valid()
        assert 'cedula' in instance.errors
    def test_correo_serializers(self, sucursal_base):
        data ={
            'nombres':"name test",
            'apellidos':"surname test",
            'cedula':"1000455391",
            'correo':"testemial",
            'id_sucursal':sucursal_base.pk
        }

        instance = self.base_serializer(data)
        assert not instance.is_valid()
        assert 'correo' in instance.errors
    
    def test_relation_inactive(self, sucursal_base):
        sucursal_base.is_active = False
        sucursal_base.save()
        data ={
            'nombres':"name test",
            'apellidos':"surname test",
            'cedula':"1000455391",
            'correo':"testemial@gmail.com",
            'id_sucursal':sucursal_base.pk
        }
        instance= self.base_serializer(data)
        assert not instance.is_valid()
        assert 'id_sucursal' in instance.errors

    def test_relation_status_incorrect(self, sucursal_base):


        sucursal_base.estado = "IN"
        sucursal_base.save()
        data ={
            'nombres':"name test",
            'apellidos':"surname test",
            'cedula':"1000455391",
            'correo':"testemial@gmail.com",
            'id_sucursal':sucursal_base.pk
        }
        instance = self.base_serializer(data)

        assert not instance.is_valid()
        assert 'id_sucursal' in instance.errors
@pytest.mark.django_db
class TestUserSerializer:
    def base_serializer(self, data):
        return UsuarioSerializer(data=data)
    
    def test_correct_serializr(self, empleado_base):
        data ={
            'usuario':"TESTUSER",
            'password':"PasswordSeguro782+",
            'rol':"AD",
            'id_empleado':empleado_base.pk
        }
        instance = self.base_serializer(data)
        assert instance.is_valid()
        obj= instance.save()
        assert obj.usuario =="testuser"

    def test_passwor_serializer(self, empleado_base):
        data ={
            'usuario':"TESTUSER",
            'password':"passoas",
            'rol':"AD",
            'id_empleado':empleado_base.pk
        }

        instance = self.base_serializer(data)
        assert not instance.is_valid()
        assert 'password' in instance.errors
    def test_relaction_inactive(self, empleado_base):
        empleado_base.is_active = False
        empleado_base.save()
        data ={
            'usuario':"TESTUSER",
            'password':"PasswordSeguro782+",
            'rol':"AD",
            'id_empleado':empleado_base.pk
        }
        instance = self.base_serializer(data)
        assert not instance.is_valid()
        assert 'id_empleado'  in instance.errors
    def test_relation_status_incorrect(self, empleado_base):
        empleado_base.estado = "IN"
        empleado_base.save()
        data ={
            'usuario':"TESTUSER",
            'password':"PasswordSeguro782+",
            'rol':"AD",
            'id_empleado':empleado_base.pk
        }
        instance = self.base_serializer(data)
        assert not instance.is_valid()
        assert 'id_empleado' in instance.errors