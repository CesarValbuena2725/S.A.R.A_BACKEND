from celery import shared_task

@shared_task
def suma(x, y):
    return x + y