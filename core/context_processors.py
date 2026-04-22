from django.conf import settings


def branding(request):
    return {
        'BRAND': settings.SENTINEL,
    }
