from apps.Forms.models import CreacionFormulario
from apps.Requests.api.tools import listForm
from apps.Result.models import Respuestas
from apps.Requests.models import Solicitud
from django.template.loader import render_to_string


def Amount_Items(request):
    list_form = listForm(request)

    for i in list_form:
        solicitud = Solicitud.objects.get(pk=request) 
        amount_items = CreacionFormulario.objects.filter(id_formulario=i).count()
        amount_answer = Respuestas.objects.filter(id_solicitud=solicitud.pk, id_formulario=i).count()

        if amount_items != amount_answer:
            return False  

    return True  


def Render_Reporte(name_tempalte,data):
    html = render_to_string(name_tempalte, data)
    return html


