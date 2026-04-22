"""Settings package — picks ``dev`` or ``prod`` via the DJANGO_ENV env var.

Defaults to ``dev``. When ``DJANGO_DEBUG=0`` we force ``prod`` for safety.
"""
import os

_env = os.environ.get('DJANGO_ENV', '').strip().lower()
if not _env:
    _env = 'prod' if os.environ.get('DJANGO_DEBUG', '1') == '0' else 'dev'

if _env == 'prod':
    from .prod import *  # noqa: F401,F403
elif _env == 'test':
    from .test import *  # noqa: F401,F403
else:
    from .dev import *  # noqa: F401,F403
