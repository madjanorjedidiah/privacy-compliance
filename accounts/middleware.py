from .models import Membership


class ActiveOrgMiddleware:
    """Attach the user's active organization to the request."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_org = None
        request.active_membership = None
        if request.user.is_authenticated:
            membership = (
                Membership.objects
                .filter(user=request.user, is_primary=True)
                .select_related('organization')
                .first()
            )
            if membership is None:
                membership = (
                    Membership.objects
                    .filter(user=request.user)
                    .select_related('organization')
                    .first()
                )
            if membership:
                request.active_org = membership.organization
                request.active_membership = membership
        return self.get_response(request)
