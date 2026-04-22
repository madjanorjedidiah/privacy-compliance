"""Settings for the privacy_compliance Django project.

One file, driven by environment variables so the same module works in
dev, test, and prod. Copy ``.env.example`` to ``.env`` to populate values.
"""
import sys
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parent.parent


# ----- Environment ---------------------------------------------------------

env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    DATABASE_URL=(str, ''),
    DB_ENGINE=(str, 'django.db.backends.postgresql'),
    DB_NAME=(str, ''),
    DB_USER=(str, 'postgres'),
    DB_PASSWORD=(str, ''),
    DB_HOST=(str, 'pgbouncer'),
    DB_PORT=(str, '6432'),
    REDIS_URL=(str, ''),
    CELERY_BROKER_URL=(str, ''),
    CELERY_RESULT_BACKEND=(str, ''),
    APP_SECRET_KEY=(str, ''),
    APP_ENABLE_HTTPS=(bool, False),
    APP_HSTS_SECONDS=(int, 0),
    APP_LOG_LEVEL=(str, 'INFO'),
    APP_LOG_FORMAT=(str, 'text'),
    APP_RATE_LIMIT_LOGIN=(str, '5/m'),
    APP_RATE_LIMIT_SIGNUP=(str, '10/h'),
    DJANGO_SUPERUSER_USERNAME=(str, ''),
    DJANGO_SUPERUSER_EMAIL=(str, ''),
    DJANGO_SUPERUSER_PASSWORD=(str, ''),
)

_env_file = BASE_DIR / '.env'
if _env_file.exists():
    env.read_env(str(_env_file))

DEBUG = env('DJANGO_DEBUG')
TESTING = 'test' in sys.argv or any(a.startswith('test') for a in sys.argv)


# ----- Secret key ----------------------------------------------------------

_DEV_SECRET_KEY = 'django-insecure-dev-only-change-in-prod-wpfz7-4gc4pgimbcp'

if TESTING:
    SECRET_KEY = 'test-secret-key'
elif DEBUG:
    SECRET_KEY = env('APP_SECRET_KEY') or _DEV_SECRET_KEY
else:
    SECRET_KEY = env('APP_SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure-'):
        raise RuntimeError(
            'APP_SECRET_KEY must be set to a strong value when DJANGO_DEBUG=0.'
        )


# ----- Hosts / CSRF --------------------------------------------------------

if DEBUG or TESTING:
    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = [
        'http://127.0.0.1:8000', 'http://localhost:8000', 'http://0.0.0.0:8000',
    ]
else:
    ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS') or ['mydataprotection.cocoatool.org']
    CSRF_TRUSTED_ORIGINS = env('DJANGO_CSRF_TRUSTED_ORIGINS') or [
        'https://mydataprotection.cocoatool.org',
    ]


# ----- Applications --------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'django_htmx',
    'rest_framework',
    'django_celery_beat',

    'core',
    'accounts',
    'jurisdictions',
    'assessments',
    'controls',
    'risks',
    'templates_engine',
    'dsar',
    'incidents',
    'vendors',
    'ropa',
    'retention',
    'training',
    'dpia',
    'dashboard',
    'ops',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'core.middleware.RequestIDMiddleware',
    'accounts.middleware.ActiveOrgMiddleware',
]

ROOT_URLCONF = 'privacy_compliance.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.branding',
                'accounts.context_processors.active_org',
            ],
        },
    },
]

WSGI_APPLICATION = 'privacy_compliance.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'accounts:login'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Fast hashing in tests only
if TESTING:
    PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ----- Static & media ------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.StaticFilesStorage' if (DEBUG or TESTING)
    else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# ----- Database ------------------------------------------------------------

_DATABASE_URL = env('DATABASE_URL')
_DB_NAME = env('DB_NAME')

if TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
elif _DATABASE_URL:
    DATABASES = {'default': env.db_url('DATABASE_URL')}
elif _DB_NAME:
    DATABASES = {
        'default': {
            'ENGINE': env('DB_ENGINE'),
            'NAME': _DB_NAME,
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST'),
            'PORT': env('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

if not DEBUG and not TESTING and DATABASES['default']['ENGINE'].endswith('postgresql'):
    DATABASES['default'].setdefault('CONN_MAX_AGE', 60)
    DATABASES['default'].setdefault('CONN_HEALTH_CHECKS', True)
    _db_options = DATABASES['default'].setdefault('OPTIONS', {})
    _db_options.setdefault('sslmode', env.str('POSTGRES_SSLMODE', default='prefer'))


# ----- Cache ---------------------------------------------------------------

_REDIS_URL = env('REDIS_URL')
if TESTING or not _REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'privacy-compliance-local',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _REDIS_URL,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    SESSION_CACHE_ALIAS = 'default'


# ----- Sessions & cookies --------------------------------------------------

SESSION_COOKIE_NAME = 'privacy_sessionid'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'


# ----- Security headers (prod only) ---------------------------------------

if not DEBUG and not TESTING:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = env('APP_ENABLE_HTTPS')
    SECURE_HSTS_SECONDS = env('APP_HSTS_SECONDS') or (60 * 60 * 24 * 365)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False  # HTMX reads the CSRF cookie
    X_FRAME_OPTIONS = 'DENY'


# ----- Logging -------------------------------------------------------------

LOG_LEVEL = (env('APP_LOG_LEVEL') or 'INFO').upper()
LOG_FORMAT = (env('APP_LOG_FORMAT') or 'text').lower()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'text': {'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'},
        'json': {'()': 'core.logging.JSONFormatter'},
    },
    'filters': {'request_id': {'()': 'core.logging.RequestIDFilter'}},
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json' if LOG_FORMAT == 'json' else 'text',
            'filters': ['request_id'],
        },
    },
    'root': {'handlers': ['console'], 'level': LOG_LEVEL},
    'loggers': {
        'django.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'django.db.backends': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
        'privacy_compliance': {'handlers': ['console'], 'level': LOG_LEVEL, 'propagate': False},
    },
}


# ----- Rate limiting -------------------------------------------------------

RATE_LIMIT_LOGIN = env('APP_RATE_LIMIT_LOGIN')
RATE_LIMIT_SIGNUP = env('APP_RATE_LIMIT_SIGNUP')


# ----- Email ---------------------------------------------------------------

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
elif TESTING:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
else:
    EMAIL_BACKEND = env.str('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
    EMAIL_HOST = env.str('EMAIL_HOST', default='')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
    DEFAULT_FROM_EMAIL = env.str(
        'DJANGO_DEFAULT_FROM_EMAIL',
        default='Privacy Compliance <no-reply@mydataprotection.cocoatool.org>',
    )
    ADMINS = [tuple(a.split(':', 1)) for a in env.list('DJANGO_ADMINS', default=[]) if ':' in a]
    SERVER_EMAIL = env.str('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)


# ----- Branding & domain-specific settings --------------------------------

BRAND = {
    'BRAND_NAME': 'Privacy Compliance',
    'BRAND_TAGLINE': 'Continuous Data Protection Compliance',
    'PRIMARY_DOMAIN': 'mydataprotection.cocoatool.org',
    'SUPPORT_EMAIL': 'privacy@cocoatool.org',
    'LEGAL_DISCLAIMER': (
        'This platform provides compliance management tooling. Content is '
        'informational and not legal advice; consult qualified counsel for '
        'regulatory decisions.'
    ),
    'RISK_SCORING': {
        'SENSITIVITY_BONUS_PER_STEP': 0.15,
        'VOLUME_BONUS_PER_STEP': 0.10,
        'REGULATOR_BONUS_PER_STEP': 0.10,
        'CONTROL_EFFECTIVENESS_MAX_REDUCTION': 0.80,
        'SEVERITY_THRESHOLDS': {'CRITICAL': 20, 'HIGH': 14, 'MEDIUM': 8, 'LOW': 4},
    },
    'DEADLINES': {
        'DSAR_DAYS_DEFAULT': 30,
        'INCIDENT_NOTIFY_HOURS_DEFAULT': 72,
    },
    'DEADLINES_PER_JURISDICTION': {
        'US-CA': {'dsar_days': 45},
        'CCPA':  {'dsar_days': 45},
        'KE':    {'dsar_days': 30},
        'GH':    {'dsar_days': 30},
        'NG':    {'dsar_days': 30},
        'EU':    {'dsar_days': 30},
    },
    'POLICY_REVIEW_DEFAULT_MONTHS': 12,
    'TRAINING_REFRESH_DEFAULT_MONTHS': 12,
}

MESSAGE_TAGS = {
    10: 'debug', 20: 'info', 25: 'success', 30: 'warning', 40: 'error',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'auth': '10/minute',
        'dsar-intake': '30/hour',
    },
}


# ----- Celery --------------------------------------------------------------

CELERY_BROKER_URL = env('CELERY_BROKER_URL') or env('REDIS_URL') or 'memory://'
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND') or env('REDIS_URL') or 'cache+memory://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_TIME_LIMIT = 300
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
