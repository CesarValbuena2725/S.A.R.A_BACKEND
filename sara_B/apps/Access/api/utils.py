from apps.Access.models import Convenio, Usuario,Sucursal,Empleado
from apps.Access.api.serializers import ConvenioSerializers,UsuarioSerializers,EmpleadoSerialzers,SucursalSeralizers


Map_Model_Accesss={
    'convenio':Convenio,
    'sucursal':Sucursal,
    'empleado':Empleado,
    'usuario':Usuario,
}

Map_Serializer_Accesss={
    'convenio':ConvenioSerializers,
    'sucursal':SucursalSeralizers,
    'empleado':EmpleadoSerialzers,
    'usuario':UsuarioSerializers,
}