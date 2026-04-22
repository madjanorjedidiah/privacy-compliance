"""Privacy Compliance Django project.

Import the Celery app at package import time so `app.autodiscover_tasks()`
sees every installed Django app.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
