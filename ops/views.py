"""Operational endpoints: liveness + readiness probes."""
import logging

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse


log = logging.getLogger('privacy_compliance.ops')


def health(request):
    """Lightweight liveness check — returns 200 if the process is running."""
    return JsonResponse({'status': 'alive', 'brand': settings.SENTINEL['BRAND_NAME']})


def readyz(request):
    """Readiness check — fails if DB or cache is unreachable."""
    checks = {}
    ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        checks['database'] = 'ok'
    except Exception as exc:  # pragma: no cover
        checks['database'] = f'failed: {exc.__class__.__name__}'
        ok = False
    try:
        cache.set('readyz:probe', 1, timeout=5)
        if cache.get('readyz:probe') != 1:
            raise RuntimeError('cache miss')
        checks['cache'] = 'ok'
    except Exception as exc:
        checks['cache'] = f'failed: {exc.__class__.__name__}'
        ok = False

    status = 200 if ok else 503
    return JsonResponse(
        {'status': 'ready' if ok else 'unready', 'checks': checks},
        status=status,
    )
