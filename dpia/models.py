from django.conf import settings
from django.db import models

from core.models import OrgScopedModel


class DPIA(OrgScopedModel):
    """Data Protection Impact Assessment — formal register entry."""
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        IN_REVIEW = 'in_review', 'In review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected — do not proceed'
        REFERRED = 'referred', 'Referred to regulator'

    class Outcome(models.TextChoices):
        PROCEED = 'proceed', 'Proceed'
        PROCEED_CONDITIONS = 'conditions', 'Proceed with conditions'
        CONSULT_REGULATOR = 'consult', 'Consult regulator (Art. 36)'
        DO_NOT_PROCEED = 'halt', 'Do not proceed'

    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    outcome = models.CharField(max_length=16, choices=Outcome.choices, blank=True)

    # 9-question EDPB trigger screen; any True answer suggests DPIA is mandatory.
    trigger_automated_decisions = models.BooleanField(default=False)
    trigger_large_scale_special = models.BooleanField(default=False)
    trigger_systematic_monitoring = models.BooleanField(default=False)
    trigger_sensitive_combined = models.BooleanField(default=False)
    trigger_new_technology = models.BooleanField(default=False)
    trigger_children = models.BooleanField(default=False)
    trigger_vulnerable_subjects = models.BooleanField(default=False)
    trigger_data_matching = models.BooleanField(default=False)
    trigger_denies_service = models.BooleanField(default=False)

    inherent_likelihood = models.PositiveSmallIntegerField(default=3, help_text='1-5')
    inherent_impact = models.PositiveSmallIntegerField(default=3, help_text='1-5')
    residual_likelihood = models.PositiveSmallIntegerField(default=2, help_text='1-5')
    residual_impact = models.PositiveSmallIntegerField(default=2, help_text='1-5')

    consultation_summary = models.TextField(blank=True)
    mitigations = models.TextField(blank=True)
    decision_note = models.TextField(blank=True)

    dpo = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='dpo_of_dpias',
    )
    business_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='business_owner_of_dpias',
    )
    approved_at = models.DateField(null=True, blank=True)
    next_review = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'DPIA'
        verbose_name_plural = 'DPIAs'

    def __str__(self):
        return self.title

    @property
    def triggers_fired(self):
        return sum(1 for f in [
            self.trigger_automated_decisions, self.trigger_large_scale_special,
            self.trigger_systematic_monitoring, self.trigger_sensitive_combined,
            self.trigger_new_technology, self.trigger_children,
            self.trigger_vulnerable_subjects, self.trigger_data_matching,
            self.trigger_denies_service,
        ] if f)

    @property
    def is_dpia_required(self):
        """EDPB WP248 guidance — two or more triggers generally indicate DPIA required."""
        return self.triggers_fired >= 2

    @property
    def inherent_score(self):
        return self.inherent_likelihood * self.inherent_impact

    @property
    def residual_score(self):
        return self.residual_likelihood * self.residual_impact
