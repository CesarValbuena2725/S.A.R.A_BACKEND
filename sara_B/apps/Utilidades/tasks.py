from celery import shared_task
from apps.Utilidades.Email.email_base import send_email_sara
from weasyprint import HTML
from celery.exceptions import Retry
from django.template.loader import render_to_string
import time, os
from django.conf import settings



@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def send_email_asincr(self, pdf_path, affair, template, destinatario=["tosaraweb@gmail.com"], solicitante=None, contexto=None, delay_second=5, files=None):
    try:
        import time
        time.sleep(delay_second)

        # Agrega el PDF generado como archivo adjunto si no se pasó manualmente
        if files is None:
            files = [pdf_path]

        resultado = send_email_sara(affair, template, destinatario, solicitante, contexto, files)
        return {'status': resultado, 'message': 'Correo enviado'}

    except Exception as e:
        print(f"Error en send_email_asincr: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 3000})
def render_reporte_asyn(self, rendered_html, url):
    from weasyprint import HTML
    import time

    try:
        time.sleep(5)
        HTML(string=rendered_html).write_pdf(url)
        return url  
    except Exception as e:
        raise self.retry(exc=e)


    
    
