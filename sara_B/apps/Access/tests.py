from apps.Utilidades.General.base_pruebas import AbstractBaseAPI
from apps.Access.models import Convenio,Sucursal


"""

    def setUp(self):
        super().setUp()
        # 🔹 Crear usuario temporal
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # 🔹 Crear empleado falso asociado
        self.empleado = Empleado.objects.create(
            user=self.user,
            nombre="Empleado Falso",
            cargo="Tester QA",
            telefono="3001234567"
        )

        # 🔹 Generar token para autenticación
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # 🔹 Configurar token en el cliente
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # 🔹 Crear una instancia inicial (si quieres probar PATCH/PUT)
        self.instance = self.model.objects.create(
            **self.validate_instancie,
            empleado=self.empleado  # Asociamos el empleado a la instancia
        )

        # 🔹 Actualizamos el valid_data para incluir relación
        self.valid_data["empleado"] = self.empleado.id
"""

class SucursalAPITest(AbstractBaseAPI):
    __test__ = True
    model = Convenio
    namemodel = "convenio"
    validate_instancie = {
        "nombre": "Sucursal Central",
        "nit": "10021054-9",
        "telefono": 123456789,
        
    }
    valid_data = {
        "nombre": "Sucursal Central",
        "nit": "155021054-9",
        "telefono": 3212015488,
        "estado":"AC"
    }
    invalid_data = {
        "nombre": "",  # ❌ vacío, debería fallar
        "direccion": "Calle sin nombre",
        "telefono": "000",
        "convenio": 9999  # ❌ id inexistente
    }
    def test_create_valid(self):   self._create_valid
    def test_create_invalid(self): self._create_invalid()
    def test_update_put(self):     self._update_put()
    def test_patch(self):          self._patch()
    def test_delete(self):         self._delete()

