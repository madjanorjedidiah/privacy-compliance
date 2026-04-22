"""Celery application for the Privacy Compliance platform.

Broker / backend are read from Django settings (CELERY_BROKER_URL and
CELERY_RESULT_BACKEND) so ops controls them via environment variables.
"""
import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privacy_compliance.settings')

app = Celery('privacy_compliance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
