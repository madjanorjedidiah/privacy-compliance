"""Scheduled tasks for training expiry reminders."""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

log = logging.getLogger(__name__)


@shared_task
def flag_expiring_training(days_ahead: int = 30):
    from .models import TrainingRecord

    today = timezone.now().date()
    horizon = today + timedelta(days=days_ahead)

    expired = TrainingRecord.objects.filter(expires_on__lt=today).count()
    expiring = TrainingRecord.objects.filter(
        expires_on__gte=today, expires_on__lte=horizon,
    ).count()
    log.info(
        'Training sweep: expired=%s expiring_%sd=%s',
        expired, days_ahead, expiring,
    )
    return {'expired': expired, 'expiring_soon': expiring}
