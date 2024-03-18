from django.conf import settings

from celery import Celery
import os
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('A')
celery_app.autodiscover_tasks()

celery_app.conf.broker_url = settings.RABBITMQ_CONNECTION

celery_app.conf.result_backend = 'rpc://'
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'pickle'
celery_app.conf.accept_content = ['json', 'pickle']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 8
