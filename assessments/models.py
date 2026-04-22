from django.db import models

from core.models import OrgScopedModel, TimeStampedModel


class Assessment(OrgScopedModel):
    """A scoping assessment run for an org — persists applicability results."""
    name = models.CharField(max_length=140, default='Initial applicability assessment')
    run_at = models.DateTimeField(auto_now_add=True)
    run_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    profile_snapshot = models.JSONField(default=dict, help_text='Snapshot of OrgProfile at run time')

    class Meta:
        ordering = ['-run_at']

    def __str__(self):
        return f'{self.name} ({self.organization})'


class FrameworkApplicability(TimeStampedModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='frameworks')
    framework = models.ForeignKey('jurisdictions.Framework', on_delete=models.CASCADE)
    applicable = models.BooleanField()
    rationale = models.TextField(blank=True)

    class Meta:
        unique_together = ('assessment', 'framework')
        ordering = ['framework__jurisdiction__name']


class RequirementApplicability(TimeStampedModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='requirements')
    requirement = models.ForeignKey('jurisdictions.Requirement', on_delete=models.CASCADE)
    applicable = models.BooleanField()
    rationale = models.TextField(blank=True)

    class Meta:
        unique_together = ('assessment', 'requirement')
