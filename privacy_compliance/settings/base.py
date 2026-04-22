"""Base settings — environment-agnostic defaults.

All site-wide configuration lives here. Environment-specific files (dev.py,
prod.py, test.py) override what they need and leave the rest alone.

All knobs that could differ between environments are read from environment
variables via ``django-environ``. Copy ``.env.example`` to ``.env`` to start.
"""
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    DATABASE_URL=(str, ''),
    # Shared-infra DB_* fallback (pgbouncer defaults on the host).
    DB_ENGINE=(str, 'django.db.backends.postgresql'),
    DB_NAME=(str, ''),
    DB_USER=(str, 'postgres'),
    DB_PASSWORD=(str, ''),
    DB_HOST=(str, 'pgbouncer'),
    DB_PORT=(str, '6432'),
    REDIS_URL=(str, ''),
    CELERY_BROKER_URL=(str, ''),
    CELERY_RESULT_BACKEND=(str, ''),
    SENTINEL_SECRET_KEY=(str, ''),
    SENTINEL_ENABLE_HTTPS=(bool, False),
    SENTINEL_HSTS_SECONDS=(int, 0),
    SENTINEL_LOG_LEVEL=(str, 'INFO'),
    SENTINEL_LOG_FORMAT=(str, 'text'),
    SENTINEL_RATE_LIMIT_LOGIN=(str, '5/m'),
    SENTINEL_RATE_LIMIT_SIGNUP=(str, '10/h'),
    DJANGO_SUPERUSER_USERNAME=(str, ''),
    DJANGO_SUPERUSER_EMAIL=(str, ''),
    DJANGO_SUPERUSER_PASSWORD=(str, ''),
)

# Load .env if present (noop in environments where it isn't).
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    env.read_env(str(_env_file))


# ----- Applications ---------------------------------------------------------

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ----- Static & media -------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ----- Database -------------------------------------------------------------

_DATABASE_URL = env('DATABASE_URL')
_DB_NAME = env.str('DB_NAME', default='')
if _DATABASE_URL:
    DATABASES = {'default': env.db_url('DATABASE_URL')}
elif _DB_NAME:
    # Shared-infra style (mirrors docker-compose on the server).
    DATABASES = {
        'default': {
            'ENGINE': env.str('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': _DB_NAME,
            'USER': env.str('DB_USER', default='postgres'),
            'PASSWORD': env.str('DB_PASSWORD', default=''),
            'HOST': env.str('DB_HOST', default='pgbouncer'),
            'PORT': env.str('DB_PORT', default='6432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ----- Cache ----------------------------------------------------------------

_REDIS_URL = env('REDIS_URL')
if _REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': _REDIS_URL,
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
    SESSION_CACHE_ALIAS = 'default'
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'privacy-compliance-local',
        }
    }


# ----- Sessions & cookies ---------------------------------------------------

SESSION_COOKIE_NAME = 'sentinel_sessionid'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'


# ----- Logging --------------------------------------------------------------

LOG_LEVEL = env('SENTINEL_LOG_LEVEL').upper() or 'INFO'
LOG_FORMAT = env('SENTINEL_LOG_FORMAT').lower()  # 'text' or 'json'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'text': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s',
        },
        'json': {
            '()': 'core.logging.JSONFormatter',
        },
    },
    'filters': {
        'request_id': {'()': 'core.logging.RequestIDFilter'},
    },
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


# ----- Rate limiting --------------------------------------------------------

SENTINEL_RATE_LIMIT_LOGIN = env('SENTINEL_RATE_LIMIT_LOGIN')
SENTINEL_RATE_LIMIT_SIGNUP = env('SENTINEL_RATE_LIMIT_SIGNUP')


# ----- Branding & domain-specific settings ---------------------------------

SENTINEL = {
    'BRAND_NAME': 'Sentinel',
    'BRAND_TAGLINE': 'Continuous Data Protection Compliance',
    'PRIMARY_DOMAIN': 'mydataprotection.cocoatool.org',
    'SUPPORT_EMAIL': 'privacy@cocoatool.org',
    'LEGAL_DISCLAIMER': (
        'Sentinel provides compliance management tooling. Content is '
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

# ----- Celery ---------------------------------------------------------------

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
