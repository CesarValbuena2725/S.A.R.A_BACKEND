from apps.Forms.models import CreacionFormulario
from apps.Requests.api.tools import listForm
from apps.Result.models import Respuestas
from apps.Requests.models import Solicitud
from django.template.loader import render_to_string
from weasyprint import HTML
import os


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



def Render_Reporte(template,Url,):
    try:
        HTML(string=template).write_pdf(Url)
        return True
    except Exception as e:
            return False 


import logging

logger = logging.getLogger(__name__)

class FunctionClose:
    """Clase para cerrar la solicitud y generar secciones del reporte PDF."""

    def __init__(self, solicitud):
        self.solicitud = solicitud
        self.respuestas = Respuestas.objects.filter(id_solicitud=solicitud)
        
    def vehiculo(self):
        list_vehiculo = {}
        for respuesta in self.respuestas:
            list_vehiculo.update({respuesta.id_item.pk:  respuesta.id_opcion if respuesta.id_opcion else respuesta.respuesta_texto})
        return list_vehiculo
    def cliente(self):
        data = Respuestas.objects.filter(id_solicitud = self.solicitud, id_formulario=3).order_by('id_formulario') 

        return data


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
            ids_items=[170, 171, 172, 173, 174, 175,76,82,86,85],
            ids_opciones=[68,29]
        )

    def carroceria(self):
        """Obtiene las respuestas relacionadas con el estado de la carrocería."""
        return self._filtrar_respuestas(
            ids_items=[104, 107, 110, 122, 123, 129, 134, 139, 141, 144, 145, 150, 155, 160, 165, 166, 169,162],
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
    def PMV(self):
        """Obtiene las respuestas relacionadas con el estado de la PMV."""
        return self._filtrar_respuestas(
            ids_items=[100,101,102,103],
            usar_respuesta_texto=True
        )
    def PMC(self):
        """Obtiene las respuestas relacionadas con el estado de la PMC."""
        return self._filtrar_respuestas(
            ids_items=[55,56,57,59,60,61,62,63],
            usar_respuesta_texto=True
        )
    def Vidrios(self):
        """Obtiene las respuestas relacionadas con el estado de los vidrios."""
        return self._filtrar_respuestas(
            ids_items=[105,118,54],
            ids_opciones=[41, 42,16,18]
        )
    def latoneria(self):
        """Obtiene las respuestas relacionadas con el estado de la latonería."""
        return self._filtrar_respuestas(
            ids_items=[160,139,161,140,162,141,163,142,164,143,165,144,166,145,167,146,169,168,110,108],
            ids_opciones=[5,6,10,7,1],
        )
    
    def luces(self):
        """Obtiene las respuestas relacionadas con el estado de las luces."""
        return self._filtrar_respuestas(
            ids_items=[115,120,117,128,149,131,152,133,154,135,156,136,157,230,231,234,235,237,239,238],
            ids_opciones=[29]
        )
    def tapiceria(self):
        """Obtiene las respuestas relacionadas con el estado de la tapicería."""
        return self._filtrar_respuestas(
            ids_items=[53,130,138,151,159,206,209,219,218],
            ids_opciones=[16,29]
        )

    def porcentaje(self):
        request = Solicitud.objects.get(pk=self.solicitud)

        # Selección correcta de la BASE
        if request.id_plan.cuestionario.pk == 1:
            BASE = [15, 20, 20, 9, 3]
        else:
            BASE = [ 11, 20, 13, 9, 3]

        # Resultados obtenidos
        list_result = [
            self.fugas(),
            self.latoneria(),
            self.luces(),
            self.tapiceria(),
            self.Vidrios()
        ]

        # Calcular porcentaje basado en los resultados
        Percentage = {}
        for key, result, base in zip(['fugas', 'Latoneria', 'Luces', 'Tapiceria', 'Vidrios'],list_result,BASE
        ):
            cantidad = len(result)
            porcentaje = (cantidad / base * 100)
            Percentage[key] = round(100-porcentaje,1)

        return(Percentage)
