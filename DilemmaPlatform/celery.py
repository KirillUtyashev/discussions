import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DilemmaPlatform.settings.dev')
app = Celery('DilemmaPlatform', broker_connection_retry=False,
             broker_connection_retry_on_startup=True, )
app.config_from_object('django.conf:settings')
broker_connection_retry = False

app.autodiscover_tasks()
app.conf.timezone = 'Europe/Moscow'
