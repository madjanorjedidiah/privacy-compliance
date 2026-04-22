from django.conf import settings
from django.db import models

from core.choices import ControlStatus
from core.models import OrgScopedModel, TimeStampedModel


class Control(OrgScopedModel):
    """An org-level control tracking fulfilment of one Requirement."""
    requirement = models.ForeignKey('jurisdictions.Requirement', on_delete=models.CASCADE, related_name='controls')
    status = models.CharField(max_length=20, choices=ControlStatus.choices, default=ControlStatus.NOT_STARTED)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_controls')
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('organization', 'requirement')
        ordering = ['requirement__framework__short_name', 'requirement__code']

    def __str__(self):
        return f'{self.requirement.code} — {self.organization}'

    @property
    def is_done(self):
        return self.status in (ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED, ControlStatus.NOT_APPLICABLE)

    @property
    def progress_weight(self):
        return {
            ControlStatus.NOT_STARTED: 0,
            ControlStatus.IN_PROGRESS: 40,
            ControlStatus.IMPLEMENTED: 80,
            ControlStatus.VERIFIED: 100,
            ControlStatus.NOT_APPLICABLE: 100,
        }.get(self.status, 0)


class Evidence(TimeStampedModel):
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='evidence/%Y/%m/', null=True, blank=True)
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
