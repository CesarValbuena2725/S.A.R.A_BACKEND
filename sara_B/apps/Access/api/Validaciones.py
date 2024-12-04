from rest_framework import serializers
import re



"""
Ejemplo una exprexion regular de usos de los Verificiaion de terminos para las validacions Estudialar
pattern = r'^\+?\d{1,3}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
if not re.fullmatch(pattern, data):
raise ValidationError("El número de teléfono no es válido")
    return data


r'^\+?\d{1,9}?[-.\s]?\(?\d{1,4}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
"""

def validate_positive(value):
    if value <= 0:
        raise serializers.ValidationError("Los campos no pueden pueden Ser negativos")
    return value

def validate_number(value):
    pattern = r'^[\d-]+$' # Solo numeros y guio para el NIT
    if not re.fullmatch(pattern, value):
        raise serializers.ValidationError("Formato no valido")
    return value


def logitud_minima(value):
    if len(value) < 5:
        raise serializers.ValidationError("debe tener mas caracteres")
    return value

def validate_text(value):
    minusculas=value.lower()
    return minusculas