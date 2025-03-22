from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
"""
from apps.Access.api.utils import Map_Model_Accesss,Map_Serializer_Accesss
from apps.Requests.api.utils import MaMap_Model_Requests, Map_Serializer_Requests
"""


class RolePermission(BasePermission):
    message= "No tienes permisos para Esta Accion"

    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            self.message = "Debes estar Autenticado para Esta Accion"
            return False
        allowed_roles = getattr(view, 'allowed_roles', [])
        return request.user.rol in allowed_roles
    

MODEL_REGISTRY = {}
SERIALIZER_REGISTRY = {}


#Decorador para agregar model al diccionario 
def set_model(model):
    name = model.__name__.lower()  # Asegurar que siempre sea en minúsculas
    if name in MODEL_REGISTRY: #Valida que no se duplique las llaves 
        raise ValueError(f"El modelo '{name}' ya está registrado.")
    MODEL_REGISTRY[name] = model # agrega el model a diccionario 
    return model 

# Decorador para registrar serializers
def set_serializers(serializer):

    # ingresa al atributo model de la clase meta para que la llave quede con el mismo nombre del model
    #permitiendo que el namemodel del path lo reconosco pasando solo un atributp
    name = serializer.Meta.model.__name__.lower()  
    if name in SERIALIZER_REGISTRY:# agrega el model a diccionario 
        raise ValueError(f"El serializer '{name}' ya está registrado.")
    SERIALIZER_REGISTRY[name] = serializer
    return serializer

def getModelName(model):
    return MODEL_REGISTRY.get(model.lower())

def getSerializer(serializer):
    return SERIALIZER_REGISTRY.get(serializer.lower())