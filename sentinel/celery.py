"""Celery application for Sentinel.

Broker / backend are read from Django settings (CELERY_BROKER_URL and
CELERY_RESULT_BACKEND) so ops controls them via environment variables.
"""
import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentinel.settings')

app = Celery('sentinel')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
