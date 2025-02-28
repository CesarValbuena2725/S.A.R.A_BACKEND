from apps.Requests.models import VehiculoPlan,TipoVehiculo,Plan
from apps.Requests.api.serializers import  PlanSerializers,VehiculoplanSerializers, TipovehiculoSerializers


MaMap_Model_Requests={
    'plan':Plan,
    'tipo_vehiculo':TipoVehiculo,
    'vehiculo_plan':VehiculoPlan
}

Map_Serializer_Requests={
    'plan':PlanSerializers,
    'tipo_vehiculo':TipovehiculoSerializers,
    'vehiculo_plan':VehiculoplanSerializers
}