from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import OrgScopedModel, TimeStampedModel


class TrainingModule(OrgScopedModel):
    """A training module employees must complete (e.g. 'Data Protection 101')."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    required_months = models.PositiveSmallIntegerField(
        default=12,
        help_text='Completion must be refreshed every N months.',
    )
    audience_note = models.CharField(
        max_length=240, blank=True,
        help_text='Who must complete this module (e.g. "All staff handling customer data").',
    )
    resource_url = models.URLField(blank=True)
    mandatory = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TrainingRecord(TimeStampedModel):
    """Proof of a user having completed a training module on a given date."""
    module = models.ForeignKey(TrainingModule, on_delete=models.CASCADE, related_name='records')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='training_records',
    )
    completed_on = models.DateField(default=timezone.now)
    expires_on = models.DateField(null=True, blank=True)
    evidence_link = models.URLField(blank=True)
    evidence_file = models.FileField(upload_to='training/%Y/%m/', null=True, blank=True)
    notes = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-completed_on']
        indexes = [models.Index(fields=['module', 'user', '-completed_on'])]

    def save(self, *args, **kwargs):
        if not self.expires_on and self.module_id:
            # 30-day approximation is sufficient for refresh reminders;
            # avoids a python-dateutil dependency.
            from datetime import timedelta
            self.expires_on = self.completed_on + timedelta(days=self.module.required_months * 30)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.expires_on and self.expires_on < timezone.now().date())

    def __str__(self):
        return f'{self.user} — {self.module}'
