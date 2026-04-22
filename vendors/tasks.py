"""Scheduled tasks for vendor DPA lifecycle."""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

log = logging.getLogger(__name__)


@shared_task
def flag_expiring_dpas(days_ahead: int = 60):
    """Log a summary of DPAs expired or expiring within the window.

    Hook into email / notifications as those land; for now this gives ops a
    visible signal in the logs that a DPA is overdue for renewal.
    """
    from .models import Vendor

    today = timezone.now().date()
    horizon = today + timedelta(days=days_ahead)

    expired = Vendor.objects.filter(
        dpa_on_file=True, dpa_expires_on__lt=today,
    ).count()
    expiring = Vendor.objects.filter(
        dpa_on_file=True, dpa_expires_on__gte=today, dpa_expires_on__lte=horizon,
    ).count()
    missing = Vendor.objects.filter(dpa_on_file=False).count()

    log.info(
        'DPA lifecycle sweep: expired=%s expiring_%sd=%s missing=%s',
        expired, days_ahead, expiring, missing,
    )
    return {'expired': expired, 'expiring_soon': expiring, 'missing_dpa': missing}
