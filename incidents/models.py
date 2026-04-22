from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.choices import IncidentSeverity
from core.models import OrgScopedModel


class Incident(OrgScopedModel):
    class Status(models.TextChoices):
        DETECTED = 'detected', 'Detected'
        TRIAGED = 'triaged', 'Triaged'
        CONTAINED = 'contained', 'Contained'
        NOTIFIED = 'notified', 'Regulator notified'
        RESOLVED = 'resolved', 'Resolved'

    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=IncidentSeverity.choices, default=IncidentSeverity.MEDIUM)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DETECTED)
    detected_at = models.DateTimeField(default=timezone.now)
    regulator_deadline = models.DateTimeField(null=True, blank=True)
    regulator_notified_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    affected_subjects_estimate = models.PositiveIntegerField(default=0)
    affected_jurisdictions = models.JSONField(default=list)

    class Meta:
        ordering = ['-detected_at']

    def save(self, *args, **kwargs):
        if not self.regulator_deadline:
            self.regulator_deadline = self.detected_at + timedelta(hours=72)
        super().save(*args, **kwargs)

    @property
    def notification_overdue(self):
        return (
            self.status != self.Status.RESOLVED
            and self.regulator_notified_at is None
            and self.regulator_deadline
            and timezone.now() > self.regulator_deadline
        )
