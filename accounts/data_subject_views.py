"""Self-service endpoints for the app user's OWN data (GDPR Art. 15 / 17).

* ``/accounts/me/export/``  — returns a JSON bundle of everything we hold
                              about the logged-in user.
* ``/accounts/me/delete/``  — irrevocable self-service account deletion.
"""
import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import AuthEvent


def _collect_user_data(user):
    """Shape the user's personal data as a plain dict for export."""
    memberships = [
        {
            'organization': m.organization.name,
            'role': m.role,
            'is_primary': m.is_primary,
            'joined_at': m.created_at.isoformat() if m.created_at else None,
        }
        for m in user.memberships.select_related('organization').all()
    ]
    auth_events = list(
        user.auth_events.order_by('-created_at')[:500].values(
            'kind', 'ip_address', 'user_agent', 'created_at',
        )
    )
    for e in auth_events:
        if e.get('created_at'):
            e['created_at'] = e['created_at'].isoformat()

    return {
        'exported_at': None,
        'user': {
            'username': user.username,
            'email': user.email,
            'display_name': user.display_name,
            'job_title': user.job_title,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'memberships': memberships,
        'auth_events': auth_events,
    }


@login_required
@require_POST
def export_my_data(request):
    """GDPR Art. 15 — machine-readable copy of everything we hold on the user."""
    from django.utils import timezone as _tz

    bundle = _collect_user_data(request.user)
    bundle['exported_at'] = _tz.now().isoformat()

    AuthEvent.objects.create(
        user=request.user, kind=AuthEvent.Kind.DATA_EXPORT,
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    payload = json.dumps(bundle, indent=2, default=str)
    resp = HttpResponse(payload, content_type='application/json; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{request.user.username}-data-export.json"'
    return resp


@login_required
def delete_my_account(request):
    """GDPR Art. 17 — erasure of the user's own account.

    Does NOT delete organisation data (which may be legally retained by the
    controller under other obligations). Owners cannot self-delete while
    they are the sole owner of an organisation — that path must go through
    ownership transfer first.
    """
    owns_solo_org = any(
        m.role == 'owner' and m.organization.memberships.filter(role='owner').count() == 1
        for m in request.user.memberships.all()
    )

    if request.method == 'POST':
        if owns_solo_org:
            messages.error(
                request,
                'You are the sole owner of a workspace. Transfer ownership before deleting your account.',
            )
            return redirect('accounts:delete_me')
        confirm = request.POST.get('confirm', '').strip().lower()
        if confirm != request.user.username.lower():
            messages.error(request, 'Please type your username exactly to confirm deletion.')
            return redirect('accounts:delete_me')
        AuthEvent.objects.create(
            user=request.user, kind=AuthEvent.Kind.ACCOUNT_DELETE,
            ip_address=request.META.get('REMOTE_ADDR'),
            username_attempted=request.user.username,
        )
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('accounts:login')

    return render(request, 'accounts/delete_me.html', {'owns_solo_org': owns_solo_org})
