from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
"""
from apps.Access.api.utils import Map_Model_Accesss,Map_Serializer_Accesss
from apps.Requests.api.utils import MaMap_Model_Requests, Map_Serializer_Requests
"""


from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    message = "No tienes permisos para esta acción."

    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            self.message = "Debes estar autenticado para esta acción."
            return False

        allowed_roles = getattr(view, 'allowed_roles', [])
        
        # Verificar que el usuario tenga el atributo 'rol' antes de acceder
        user_role = getattr(request.user, 'rol', None)
        if user_role is None:
            self.message = "El usuario no tiene un rol asignado."
            return False

        return user_role in allowed_roles


# Diccionarios de registro
MODEL_REGISTRY = {}
SERIALIZER_REGISTRY = {}

# Decorador para registrar modelos en el diccionario
def set_model(model):
    name = model.__name__.lower()  # Asegurar que siempre sea en minúsculas
    if name in MODEL_REGISTRY:
        raise ValueError(f"El modelo '{name}' ya está registrado. No se pueden duplicar modelos.")
    
    MODEL_REGISTRY[name] = model
    return model 

# Decorador para registrar serializers
def set_serializers(serializer):
    try:
        name = serializer.Meta.model.__name__.lower()
    except AttributeError:
        raise ValueError(f"El serializador {serializer.__name__} no tiene un modelo definido en Meta.")

    if name in SERIALIZER_REGISTRY:
        raise ValueError(f"El serializador '{name}' ya está registrado. No se pueden duplicar serializadores.")
    
    SERIALIZER_REGISTRY[name] = serializer
    return serializer


# Función para obtener un modelo registrado
def getModelName(model):
    if not model:
        raise ValueError("El nombre del modelo no puede ser None o vacío.")
    
    model = model.lower()
    if model not in MODEL_REGISTRY:
        raise ValueError(f"El modelo '{model}' no está registrado.")
    
    return MODEL_REGISTRY[model]

# Función para obtener un serializador registrado
def getSerializer(serializer):
    if not serializer:
        raise ValueError("El nombre del serializador no puede ser None o vacío.")

    serializer = serializer.lower()
    if serializer not in SERIALIZER_REGISTRY:
        raise ValueError(f"El serializador '{serializer}' no está registrado.")
    
    return SERIALIZER_REGISTRY[serializer]
