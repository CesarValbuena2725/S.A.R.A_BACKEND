from apps.Forms.models import Formulario
from apps.Requests.models import Plan, Solicitud

def listForm(id):
    try:
        solicitud = Solicitud.objects.get(pk=id.pk)
        plan = solicitud.id_plan

        # Formularios por cuestionario del plan
        forms_base = Formulario.objects.filter(id_categoria=plan.cuestionario)

        # Formularios adicionales del plan (ManyToMany)
        adicionales = plan.lista_adicionales.all()

        # Unir ambos QuerySets
        data = forms_base | adicionales

        return list(data.values_list('id', flat=True))

    except Solicitud.DoesNotExist:
        return ["noenconatadp"]
    except Exception as e:
        return [str(e)]



