"""Structured logging helpers."""
import json
import logging

from .middleware import get_request_id


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True


class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', '-'),
            'time': self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
        }
        if record.exc_info:
            payload['exc'] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(',', ':'))
