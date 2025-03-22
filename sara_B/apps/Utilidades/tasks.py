from celery import shared_task
from apps.Utilidades.Email.email_base import send_email_sara
from celery.exceptions import Retry
import time



@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def send_email_asincr(self, affair, template, destinatario=["tosaraweb@gmail.com"], solicitante=None, contexto=None, delay_second=5):
    try:
        time.sleep(delay_second)
        resultado = send_email_sara(affair, template, destinatario, solicitante, contexto)
        return {'status': resultado, 'message': 'Correo enviado'}	
    
    except Exception as e:
        print(f"Error en send_email_asincr: {e}")  # Registrar el error
        return Retry(exc=e)
