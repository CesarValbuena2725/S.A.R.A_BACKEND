import os
from celery import Celery

# Establecer la configuración predeterminada de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sara_B.settings')

app = Celery('sara_B')

# Cargar configuración desde Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks en todas las aplicaciones registradas en INSTALLED_APPS
app.autodiscover_tasks()
