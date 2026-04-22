"""Request middleware: attach a request ID usable in logs and tracing."""
import logging
import uuid
from threading import local


_request_local = local()


def get_request_id():
    return getattr(_request_local, 'request_id', '-')


class RequestIDMiddleware:
    HEADER = 'X-Request-ID'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        incoming = request.META.get('HTTP_X_REQUEST_ID', '').strip()
        request_id = incoming[:64] or uuid.uuid4().hex
        _request_local.request_id = request_id
        request.request_id = request_id
        try:
            response = self.get_response(request)
        finally:
            _request_local.request_id = None
        response.headers[self.HEADER] = request_id
        return response
