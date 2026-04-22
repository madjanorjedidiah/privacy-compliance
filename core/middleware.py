"""Request middleware: attach a request ID usable in logs and tracing.

Uses ``contextvars`` instead of ``threading.local`` so it behaves correctly
under both WSGI (gunicorn) and ASGI (uvicorn/daphne) — async views can span
multiple tasks and ContextVar propagates through them.
"""
import uuid
from contextvars import ContextVar


_request_id_var: ContextVar[str] = ContextVar('request_id', default='-')


def get_request_id():
    return _request_id_var.get()


class RequestIDMiddleware:
    HEADER = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.META.get('HTTP_X_REQUEST_ID', '').strip()
        request_id = incoming[:64] or uuid.uuid4().hex
        token = _request_id_var.set(request_id)
        request.request_id = request_id
        try:
            response = self.get_response(request)
        finally:
            _request_id_var.reset(token)
        response.headers[self.HEADER] = request_id
        return response
