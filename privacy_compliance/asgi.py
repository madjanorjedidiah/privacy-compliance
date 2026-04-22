"""ASGI config for the privacy_compliance Django project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privacy_compliance.settings')

application = get_asgi_application()
