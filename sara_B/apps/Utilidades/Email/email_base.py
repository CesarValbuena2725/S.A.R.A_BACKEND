import uuid
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template.loader import render_to_string

from django.conf import settings
import os


def Send_Email_Sara(affair, template, destinario=["tosaraweb@gmail.com"], solicitante=None, contexto=None, files=None):
    # Codigos Generados para que cada correo sea Unico
    unique_id = uuid.uuid4().hex[:6]
    subject = f"{affair} - Código de Solicitud {unique_id}"

    #template = get_template(template)
    context = {
        'asunto': affair,
        'informacion': contexto,
        'datos': solicitante
    }
    # Se renderiaza el template pasado 
    html_string = render_to_string(template, context)

    # Se Estrucutra el email
    email = EmailMessage(
        subject=subject,
        body=html_string,
        from_email=settings.EMAIL_HOST_USER,
        to=destinario
    )
    email.content_subtype = 'html'
    email.extra_headers = {'Message-ID': f"<{uuid.uuid4()}@gmail.com>"}
    
    # Validacion para archivos Adjuntos 
    if files:
        for f in files:
            try:
                if hasattr(f, 'read'):  # Archivos cargados desde request.FILES
                    email.attach(f.name, f.read(), f.content_type)
                    f.seek(0)  # Rebobinar el archivo por si hay que usarlo después
                elif isinstance(f, str):  # Ruta de archivo local
                    if os.path.isfile(f) and os.access(f, os.R_OK):
                        email.attach_file(f)
                    else:
                        print(f"Advertencia: No se pudo acceder al archivo {f}")
            except Exception as e:
                print(f"Error al adjuntar archivo {f}: {str(e)}")

    try:
        email.send()
        return "HTTP_200_OK"
    except Exception as e:
        return {"status": "error", "message": str(e)}
