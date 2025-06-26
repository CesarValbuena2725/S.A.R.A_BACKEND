from apps.Forms.models import CreacionFormulario
from apps.Requests.api.tools import listForm
from apps.Result.models import Respuestas
from apps.Requests.models import Solicitud
from django.template.loader import render_to_string
from apps.Result.models import Opciones

def Amount_Items(request):
    solicitud = Solicitud.objects.get(pk=request) 
    list_form = listForm(solicitud)
    try:
        for i in list_form:
            amount_items = CreacionFormulario.objects.filter(id_formulario=i).count()
            amount_answer = Respuestas.objects.filter(id_solicitud=request, id_formulario=i).count()
            if amount_items != amount_answer:
                return False  
        return True  
    except Exception as e:
        print(f"Error al contar los items: {e}")
        return False


def Render_Reporte(name_tempalte,data):
    html = render_to_string(name_tempalte, data)
    return html


import logging

logger = logging.getLogger(__name__)

class FunctionClose:
    """Clase para cerrar la solicitud y generar secciones del reporte PDF."""

    def __init__(self, solicitud):
        self.solicitud = solicitud
        self.respuestas = Respuestas.objects.filter(id_solicitud=solicitud)

    def _filtrar_respuestas(self, ids_items, ids_opciones=None, usar_respuesta_texto=False):
        """
        Filtra respuestas según items y opcionalmente por opciones.
        
        Args:
            ids_items (list): Lista de IDs de ítems a filtrar.
            ids_opciones (list, optional): Lista de IDs de opciones válidas. Si es None, se aceptan todas.
            usar_respuesta_texto (bool): Si True, usa `respuesta_texto` en lugar de `id_opcion`.

        Returns:
            dict: Diccionario con la estructura {id_item: [nombre_item, valor]}
        """
        resultado_dict = {}
        try:
            for respuesta in self.respuestas:
                if respuesta.id_item.pk in ids_items:
                    if ids_opciones is None or respuesta.id_opcion.pk in ids_opciones:
                        valor = respuesta.respuesta_texto if usar_respuesta_texto else respuesta.id_opcion
                        resultado_dict[respuesta.id_item.pk] = [respuesta.id_item.nombre_items, valor]
            return resultado_dict
        except Exception as e:
            logger.error(f"Error al filtrar respuestas: {e}")
            return {}

    def fugas(self):
        """Obtiene las fugas del reporte (opción 68 seleccionada)."""
        return self._filtrar_respuestas(
            ids_items=[170, 171, 172, 173, 174, 175],
            ids_opciones=[68]
        )

    def carroceria(self):
        """Obtiene las respuestas relacionadas con el estado de la carrocería."""
        return self._filtrar_respuestas(
            ids_items=[104, 107, 110, 122, 123, 129, 134, 139, 141, 144, 145, 150, 155, 160, 165, 166, 169],
            ids_opciones=[1, 3, 5, 7, 10, 11]
        )

    def novedades(self):
        """Obtiene novedades reportadas en texto libre."""
        return self._filtrar_respuestas(
            ids_items=[243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253],
            usar_respuesta_texto=True
        )
    def pintura(self):
        """Obtiene las respuestas relacionadas con el estado de la pintura."""
        return self._filtrar_respuestas(
            ids_items=[19,52]
        )