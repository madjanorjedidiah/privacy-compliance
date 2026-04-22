"""Public pages for the platform itself (privacy notice, terms, cookies)."""
from django.shortcuts import render


def privacy_notice(request):
    """Platform's own privacy notice (GDPR Arts. 12-14 / Ghana DPA s.24)."""
    return render(request, 'public/privacy_notice.html')


def terms(request):
    return render(request, 'public/terms.html')


def cookies(request):
    return render(request, 'public/cookies.html')
