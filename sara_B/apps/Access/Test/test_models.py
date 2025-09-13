import pytest
from apps.Access.models import Convenio,Sucursal,Empleado, Usuario
from django.core.exceptions import ValidationError
from django.db import IntegrityError,DataError
from django.contrib.auth.hashers import make_password, check_password
@pytest.mark.django_db
class TestAgreementModel:

    def Bases_Create_agremmet(self, data):
        return Convenio.objects.create(**data)
        
    def test_create_agreement_correct(self):
        
        data={"nombre": "Convenio Salud Total",
            "nit": "900123456",
            "telefono": "3104567890",
            "estado": "AC"}
        
        instancia = self.Bases_Create_agremmet(data)
        assert instancia.nombre == "Convenio Salud Total"
        assert instancia.nit == "900123456"
        assert instancia.telefono == "3104567890"
        assert instancia.estado =="AC"

    def test_status_defauld(self):
        data = {
            'nombre':"Agremment test",
            'nit':"1122334455",
            'telefono':"3212055488"
        }
        instancie = self.Bases_Create_agremmet(data)

        assert instancie.estado =="AC"

    def test_data_incorrect(self):
        data = {
            'nombre': "a" * 61,
            'nit': "123456789",  # Valor válido
            'telefono': "3212015488",
        }
        with pytest.raises(DataError):
            self.Bases_Create_agremmet(data)

@pytest.mark.django_db
class TestBranchModel:

    def base_create_branch(self,data):
        return Sucursal.objects.create(**data)
    
    def test_create_correct(self,convenio_bases):
        data={
            'nombre':"test branch",
            'ciudad':"Bogotá",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'estado':"AC",
            'id_convenio':convenio_bases,
            'is_active':True
            }
        instance= self.base_create_branch(data)
        assert instance.nombre =="test branch"
        assert instance.ciudad =="Bogotá"
        assert instance.direccion =="Calle 123"
        assert instance.telefono == "3209876543"
        assert instance.estado == "AC"
        assert isinstance(instance.id_convenio,Convenio)

    def test_status_defauld(self,convenio_bases):
        data ={
            'nombre':"test branch",
            'ciudad':"Bogotá",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':convenio_bases,
            }
        instance = self.base_create_branch(data)
        assert instance.estado =="AC"
        assert instance.is_active == True

    def test_convenio_incorrect(self):
        data ={
            'nombre':"test branch",
            'ciudad':"Bogotá",
            'direccion':"Calle 123",
            'telefono':"3209876543",
            'id_convenio':None,
            }
        with pytest.raises((IntegrityError,ValidationError)):
            self.base_create_branch(data)

@pytest.mark.django_db
class TestEmployeModel:
    def base_create_employe(self,data):
        return Empleado.objects.create(**data)
    
    def test_create_correct(self, sucursal_base):
        data = {
            'nombres':"names tests",
            'apellidos':"surnames test",
            'cedula':"1000445566",
            'correo':"tetsemail@tester.com",
            'estado':"AC",
            'id_sucursal':sucursal_base,
            'is_active':True
        }

        instance= self.base_create_employe(data)
        assert instance.nombres =="names tests"
        assert instance.apellidos == "surnames test"
        assert instance.cedula == "1000445566"
        assert instance.correo == "tetsemail@tester.com"
        assert instance.estado == "AC"
        assert isinstance(instance.id_sucursal,Sucursal)
        assert instance.is_active == True

    def test_status_defauld(self,sucursal_base):
        data = {
            'nombres':"names tests",
            'apellidos':"surnames test",
            'cedula':"1000445566",
            'correo':"tetsemail@tester.com",
            'id_sucursal':sucursal_base,
        }

        instance = self.base_create_employe(data)
        assert instance.estado == "AC"
        assert instance.is_active == True
    def test_sucursal_incorrect(self):
        data = {
            'nombres':"names tests",
            'apellidos':"surnames test",
            'cedula':"1000445566",
            'correo':"tetsemail@tester.com",
            'id_sucursal':None,
        }
        with pytest.raises((IntegrityError, ValidationError)):
            self.base_create_employe(data)

@pytest.mark.django_db
class TestUserModel:
    def base_create_user(self,data):
        return Usuario.objects.create(**data)
    
    def test_create_correct(self, empleado_base):
        data ={
            'usuario':"user test",
            'password':"123456789",
            'rol':'AD',
            'estado':"AC",
            'id_empleado':empleado_base,
            'is_active':True
        }
        instance = self.base_create_user(data)
        assert instance.usuario == "user test"
        assert instance.rol == "AD"
        assert instance.estado =="AC"
        assert isinstance(instance.id_empleado , Empleado)
        assert instance.is_active == True
    
    def test_password_hashed(self,empleado_base):
        data ={
            'usuario':"user test",
            'password':"123456789",
            'rol':'AD',
            'estado':"AC",
            'id_empleado':empleado_base,
            'is_active':True
        }
        instance = self.base_create_user(data)
        assert  instance.password != "123456789"
        assert instance.password.startswith('pbkdf2_sha256$')
        assert instance.verificar_contraseña("123456789")
        assert not instance.verificar_contraseña("488754745")
    def test_status_defauld(self,empleado_base):
        data ={
            'usuario':"user test",
            'password':"123456789",
            'rol':'AD',
            'id_empleado':empleado_base,
        }
        instance = self.base_create_user(data)

        assert instance.estado =="AC"
        assert instance.is_active== True