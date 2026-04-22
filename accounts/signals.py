"""Auth event audit signals.

Listens to Django's built-in auth signals and persists an ``AuthEvent``
row for each. Keeps the audit trail regulator-ready without scattering
logging across views.
"""
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed,
)
from django.dispatch import receiver

from .models import AuthEvent


def _client_ip(request):
    if not request:
        return None
    fwd = request.META.get('HTTP_X_FORWARDED_FOR', '').strip()
    if fwd:
        return fwd.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _user_agent(request):
    if not request:
        return ''
    return request.META.get('HTTP_USER_AGENT', '')[:400]


@receiver(user_logged_in)
def _on_login(sender, request, user, **kwargs):
    AuthEvent.objects.create(
        user=user,
        kind=AuthEvent.Kind.LOGIN_OK,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )


@receiver(user_login_failed)
def _on_login_failed(sender, credentials, request=None, **kwargs):
    AuthEvent.objects.create(
        user=None,
        username_attempted=(credentials or {}).get('username', '')[:150],
        kind=AuthEvent.Kind.LOGIN_FAIL,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )


@receiver(user_logged_out)
def _on_logout(sender, request, user, **kwargs):
    AuthEvent.objects.create(
        user=user,
        kind=AuthEvent.Kind.LOGOUT,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
    )
