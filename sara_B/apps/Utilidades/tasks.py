from celery import shared_task
from apps.Utilidades.Email.email_base import send_email_sara
from weasyprint import HTML
from celery.exceptions import Retry
from django.template.loader import render_to_string
import time, os
from django.conf import settings



@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def send_email_asincr(self, affair, template, destinatario=["tosaraweb@gmail.com"], solicitante=None, contexto=None, delay_second=5):
    try:
        time.sleep(delay_second)
        resultado = send_email_sara(affair, template, destinatario, solicitante, contexto)
        return {'status': resultado, 'message': 'Correo enviado'}	
    
    except Exception as e:
        print(f"Error en send_email_asincr: {e}")  # Registrar el error
        return Retry(exc=e)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 3000})
def create_pdf_from_html(self, rendered_html, output_filename):
    try:
        time.sleep(5)  

        full_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        HTML(string=rendered_html).write_pdf(full_path)

        if os.path.exists(full_path):
            return {
                'status': 'success',
                'message': f"PDF generado correctamente en {full_path}"
            }
        else:
            return {
                'status': 'error',
                'message': "El archivo no se generó"
            }

    except Exception as e:
        raise self.retry(exc=e)