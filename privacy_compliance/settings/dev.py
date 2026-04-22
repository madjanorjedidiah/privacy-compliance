"""Development settings — permissive, for local work only."""
from .base import *  # noqa: F401,F403
from .base import BASE_DIR, env  # noqa: F401


DEBUG = True
SECRET_KEY = env('SENTINEL_SECRET_KEY') or 'django-insecure-dev-only-change-in-prod-wpfz7-4gc4pgimbcp'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000', 'http://localhost:8000', 'http://0.0.0.0:8000',
]

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
