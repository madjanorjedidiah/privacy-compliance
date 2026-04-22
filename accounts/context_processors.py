def active_org(request):
    return {
        'active_org': getattr(request, 'active_org', None),
        'active_membership': getattr(request, 'active_membership', None),
    }
