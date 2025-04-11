from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission

class RolePermission(BasePermission):
    message = "No tienes permisos para esta acción."

    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            self.message = "Debes estar autenticado para esta acción."
            return False

        # Obtener roles permitidos en la vista
        allowed_roles = set(getattr(view, 'allowed_roles', []))

        # Verificar que el usuario tenga un rol asignado
        user_role = getattr(request.user, 'rol', None)
        if user_role is None:
            self.message = "El usuario no tiene un rol asignado."
            return False
        
        # Verificar si el usuario tiene un rol permitido
        if allowed_roles and user_role not in allowed_roles:
            self.message = "No tienes permisos para esta acción."
            return False
        
        return True
    

BASE_PERMISOSOS = ['AD', 'PR', 'RC', 'CA', 'CC']


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
