## Mapeo de model
from apps.Solicitudes.api.serializers import CategoriaServicioSerializers,ClienteSerializers
from apps.Solicitudes.models import CategoriaServicio,Cliente

# Mapeo de model del modulo de solicitudes 
 
Map_Model_Solicitud={
    'cliente': Cliente,
    'categoriaservicio':CategoriaServicio,
}

Map_Serializer_solicitud={
    'cliente': ClienteSerializers,
    'categoriaservicio':CategoriaServicioSerializers,

}