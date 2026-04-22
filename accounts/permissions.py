"""Role-based access helpers."""
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Membership


WRITE_ROLES = {Membership.Role.OWNER, Membership.Role.DPO, Membership.Role.COMPLIANCE}
READ_ROLES = WRITE_ROLES | {Membership.Role.AUDITOR, Membership.Role.VIEWER}


def _role(request):
    mem = getattr(request, 'active_membership', None)
    return mem.role if mem else None


def can_write(request):
    return _role(request) in WRITE_ROLES


def can_read(request):
    return _role(request) in READ_ROLES


def role_required(roles):
    """Decorator: only users whose active-org membership is in ``roles`` may enter."""
    allowed = {r.value if hasattr(r, 'value') else r for r in roles}

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            role = _role(request)
            if role is None:
                messages.error(request, 'No active workspace membership.')
                return redirect('accounts:login')
            if role not in allowed:
                raise PermissionDenied('Your role does not permit this action.')
            return view(request, *args, **kwargs)
        return wrapper
    return decorator


def write_required(view):
    return role_required(WRITE_ROLES)(view)
