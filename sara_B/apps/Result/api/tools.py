from apps.Forms.models import CreacionFormulario
from apps.Requests.api.tools import listForm
from apps.Result.models import Respuestas
from apps.Requests.models import Solicitud
from django.template.loader import render_to_string


def Amount_Items(request):
    solicitud = Solicitud.objects.get(pk=request) 
    list_form = listForm(solicitud)
    try:
        for i in list_form:
            amount_items = CreacionFormulario.objects.filter(id_formulario=i).count()
            amount_answer = Respuestas.objects.filter(id_solicitud=request, id_formulario=i).count()
            print(f"Formulario ID: {i}, Items: {amount_items}, Respuestas: {amount_answer}")
            if amount_items != amount_answer:
                return False  
        return True  
    except Exception as e:
        print(f"Error al contar los items: {e}")
        return False


def Render_Reporte(name_tempalte,data):
    html = render_to_string(name_tempalte, data)
    return html


