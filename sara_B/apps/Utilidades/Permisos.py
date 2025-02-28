from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.Access.api.utils import Map_Model_Accesss,Map_Serializer_Accesss
from apps.Requests.api.utils import MaMap_Model_Requests, Map_Serializer_Requests

class RolePermission(BasePermission):
    message= "No tienes permisos para Esta Accion"

    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            self.message = "Debes estar Autenticado para Esta Accion"
            return False
        allowed_roles = getattr(view, 'allowed_roles', [])
        return request.user.rol in allowed_roles
    

Map_Model={

}
Map_Model.update(Map_Model_Accesss)
Map_Model.update(MaMap_Model_Requests)

Map_Serializer={

}
Map_Serializer.update(Map_Serializer_Accesss)
Map_Serializer.update(Map_Serializer_Requests)

def getModelName(model):
    return Map_Model.get(model.lower())

def GetSerializer(serializer):
    return Map_Serializer.get(serializer.lower())