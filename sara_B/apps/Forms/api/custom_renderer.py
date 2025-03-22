from django.utils.safestring import mark_safe
from rest_framework.renderers import BrowsableAPIRenderer

class RenderApiPersonalizado(BrowsableAPIRenderer):
    def get_rendered_html_form(self, data, view, method, request):
        formulario_renderizado = super().get_rendered_html_form(data, view, method, request)

        if not formulario_renderizado or isinstance(formulario_renderizado, bool):
            return mark_safe("<p>No hay formulario disponible para esta vista.</p>")

        formulario_modificado = formulario_renderizado.replace(
            "Lists are not currently supported in HTML input.",
            "<input type='text' name='items' placeholder='Ej: 1,2,3'>"
        )

        return mark_safe(formulario_modificado)  # 🔹 Esto indica que es HTML seguro
