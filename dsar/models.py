from django.conf import settings
from django.db import models
from django.utils import timezone

from core.choices import DSARType
from core.deadlines import dsar_due_at
from core.models import OrgScopedModel


class DSARRequest(OrgScopedModel):
    class Status(models.TextChoices):
        RECEIVED = 'received', 'Received'
        VERIFYING = 'verifying', 'Verifying identity'
        IN_PROGRESS = 'in_progress', 'In progress'
        CLOSED = 'closed', 'Closed'
        REJECTED = 'rejected', 'Rejected'

    subject_name = models.CharField(max_length=160)
    subject_email = models.EmailField()
    subject_country = models.CharField(max_length=2, blank=True)
    request_type = models.CharField(max_length=24, choices=DSARType.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RECEIVED)
    received_at = models.DateTimeField(default=timezone.now)
    due_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-received_at']

    def save(self, *args, **kwargs):
        if not self.due_at:
            self.due_at = dsar_due_at(self.received_at, self.subject_country or None)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.status != self.Status.CLOSED and self.due_at and timezone.now() > self.due_at
