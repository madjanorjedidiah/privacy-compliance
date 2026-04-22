"""Rate-limit helpers.

``client_ip`` is a django-ratelimit key function that returns the real
client IP, preferring ``X-Forwarded-For`` when present (i.e. when we're
behind nginx / an NPM proxy) and falling back to ``REMOTE_ADDR`` so tests
and local dev still work.
"""


def client_ip(group, request):
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '').strip()
    if fwd:
        # First entry is the originating client; the rest are hop IPs.
        return fwd.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
