## Mapeo de model
from apps.Solicitudes.api.serializers import CategoriaServicioSerializers,SolicitudSerializers
from apps.Solicitudes.models import CategoriaServicio,Solicitud

# Mapeo de model del modulo de solicitudes 
 
Map_Model_Solicitud={
    'categoriaservicio':CategoriaServicio,
}

Map_Serializer_solicitud={
    'categoriaservicio':CategoriaServicioSerializers,
}