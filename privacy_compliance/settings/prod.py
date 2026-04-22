"""Production settings for mydataprotection.cocoatool.org."""
from .base import *  # noqa: F401,F403
from .base import env


DEBUG = False

# Secret key MUST be provided via env; refuse to start otherwise.
SECRET_KEY = env('SENTINEL_SECRET_KEY')
if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
    raise RuntimeError(
        'SENTINEL_SECRET_KEY must be set to a strong value in production.'
    )

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS') or [
    'mydataprotection.cocoatool.org',
]

CSRF_TRUSTED_ORIGINS = env('DJANGO_CSRF_TRUSTED_ORIGINS') or [
    'https://mydataprotection.cocoatool.org',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ----- Security headers -----------------------------------------------------

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SENTINEL_ENABLE_HTTPS', default=True)
SECURE_HSTS_SECONDS = env.int('SENTINEL_HSTS_SECONDS', default=60 * 60 * 24 * 365)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # CSRF cookie must be readable by JS for HTMX

X_FRAME_OPTIONS = 'DENY'

# ----- Database connection resilience --------------------------------------

DATABASES['default'].setdefault('CONN_MAX_AGE', 60)
DATABASES['default'].setdefault('CONN_HEALTH_CHECKS', True)
DATABASES['default'].setdefault('OPTIONS', {})
DATABASES['default']['OPTIONS'].setdefault('sslmode', env.str('POSTGRES_SSLMODE', default='prefer'))

# ----- Email ---------------------------------------------------------------

EMAIL_BACKEND = env.str('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env.str(
    'DJANGO_DEFAULT_FROM_EMAIL',
    default=f'Sentinel <no-reply@{SENTINEL["PRIMARY_DOMAIN"]}>',
)

ADMINS = [tuple(a.split(':', 1)) for a in env.list('DJANGO_ADMINS', default=[]) if ':' in a]
SERVER_EMAIL = env.str('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
