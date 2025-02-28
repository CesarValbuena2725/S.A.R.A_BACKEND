import uuid
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings

#

def send_email_sara(contexto, asunto, destinario, plantilla,solicitante):

    message_id = f"<{uuid.uuid4()}@gmail.com>"
    template = get_template(plantilla)

    context = {
            'asunto': asunto,
            'link': contexto,
            'datos':solicitante
    }

    body_html = template.render(context)

    email = EmailMessage(
        subject=asunto,
        body=body_html,
        from_email=settings.EMAIL_HOST_USER,
        to=destinario,
    )
    email.content_subtype = 'html'
    email.extra_headers = {'Message-ID': message_id}

    try:
        email.send()
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
