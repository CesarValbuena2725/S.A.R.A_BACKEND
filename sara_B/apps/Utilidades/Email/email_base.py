import uuid
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings

def send_email_sara(affair, template, destinario=["tosaraweb@gmail.com"], solicitante=None, contexto=None):

    unique_id = uuid.uuid4().hex[:6]  # Tomar los primeros 6 caracteres del UUID
    subject = f"{affair}  codigo de Solicitud {unique_id}"  # Agregar el identificador único al asunto

   

    # Renderizar la plantilla HTML
    template = get_template(template)
    context = {
        'asunto': affair,
        'informacion': contexto,
        'datos': solicitante
    }
    body_html = template.render(context)

    # Crear el correo electrónico
    email = EmailMessage(
        subject=subject,  # Usar el asunto con el identificador único
        body=body_html,
        from_email=settings.EMAIL_HOST_USER,
        to=destinario
    )
    email.content_subtype = 'html'
    message_id = f"<{uuid.uuid4()}@gmail.com>"
    email.extra_headers = {'Message-ID': message_id}


    try:
        email.send()
    except Exception as e:
        print(f"Error al enviar el correo: {e}")