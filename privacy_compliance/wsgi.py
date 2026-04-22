"""WSGI config for the privacy_compliance Django project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privacy_compliance.settings')

application = get_wsgi_application()
