from rest_framework import serializers
import re 


import re


class ValidateFields:
    def __init__(self):
        self.base = {
            'INT': r'^\d+$',  # solo enteros positivos
            'DECIMAL': r'^\d+(\.\d{1,2})?$',  # números decimales hasta 2 dígitos
            'STRING': r'^[A-Za-zÁÉÍÓÚáéíóúñÑ0-9]+(?:\s+[A-Za-zÁÉÍÓÚáéíóúñÑ0-9]+)*$',  # solo letras y espacios intermedios
            'PASSWORD': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',  # contraseña segura
            'TEL': r'^(3\d{9}|\d{7}|\d{10})$',
            'EMAIL': r'^[\w\.-]+@[\w\.-]+\.\w{2,}$',  # email
            'PLACA': r'^(?:[A-Z]{3}\d{3}|[A-Z]{3}\d{2}[A-Z])$',  # placas Colombia
            'DATE': r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$',  # fecha YYYY-MM-DD
            'NIT': r'^\d{9,10}(-\d{1})?$',
        }

    def validate(self, value, type_validate):
        """
        Valida un campo según el tipo definido en self.base
        y aplica limpieza básica según corresponda.
        """
        if not isinstance(value, str):
            value = str(value)

        # Limpieza general Espacion al final y principio 
        data = value.strip()

        # Normalización según tipo

        if type_validate in ["STRING"]:
            # quita dobles espacios y pone mayúscula inicial
            data = re.sub(r"\s+", " ", data).title()

        # ponen en minisculas 
        elif type_validate in ["EMAIL"]:
            data = data.lower()

        #La pone en mayusculas
        elif type_validate in ["PLACA"]:
            data = data.upper()

        elif type_validate in ["PASSWORD"]:
            # aquí no transformamos nada, solo validamos
            pass

        elif type_validate in ["INT", "DECIMAL", "TEL", "ZIPCODE"]:
            data = data  # sin cambios

        # Validaciones con Expreciones  regulares
        pattern = self.base.get(type_validate)
        if not pattern:
            raise ValueError(f"Tipo de validación '{type_validate}' no soportado")

        if not re.fullmatch(pattern, data):
            raise serializers.ValidationError(f"El valor ingresado no cumple con el formato permitido para {type_validate}. "
                                                "Por favor verifique los datos e intente nuevamente.")
        return data
    #Funciona para tamaño minimo 
    def Length_min(self, value,tamaño):
        if len(value)< int(tamaño):
            raise ValueError("Caractereres insuficionetes para realizar el registro")

    def Validate_Relacion(self, value):
        if value.estado == "IN":
            raise ValueError(f"{value._meta.model_name } inactivo.")
        if value.is_active == 0:
            raise ValueError(f"{value._meta.model_name } Eliminado")
        return value
    
