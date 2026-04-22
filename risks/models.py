from django.conf import settings
from django.db import models

from core.choices import RiskLevel, Severity
from core.models import OrgScopedModel


class Risk(OrgScopedModel):
    class Treatment(models.TextChoices):
        ACCEPT = 'accept', 'Accept'
        MITIGATE = 'mitigate', 'Mitigate'
        TRANSFER = 'transfer', 'Transfer'
        AVOID = 'avoid', 'Avoid'

    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=40, blank=True, help_text='e.g. breach, cross-border, vendor')

    likelihood = models.PositiveSmallIntegerField(choices=RiskLevel.choices, default=RiskLevel.MODERATE)
    impact = models.PositiveSmallIntegerField(choices=RiskLevel.choices, default=RiskLevel.MODERATE)

    data_sensitivity = models.PositiveSmallIntegerField(
        default=2,
        help_text='1 (low) to 5 (special category / children / biometric)',
    )
    data_volume_log10 = models.PositiveSmallIntegerField(
        default=3,
        help_text='log10 of estimated subjects affected (3 = 1k, 4 = 10k, 5 = 100k, 6 = 1M)',
    )
    regulator_activity = models.PositiveSmallIntegerField(
        default=2,
        help_text='1 (quiet) to 5 (very active) — weight for regulator activity in affected jurisdictions',
    )
    control_effectiveness = models.PositiveSmallIntegerField(
        default=50,
        help_text='0–100 percent — estimated effectiveness of controls in place',
    )

    treatment = models.CharField(max_length=12, choices=Treatment.choices, default=Treatment.MITIGATE)
    treatment_notes = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_risks')
    review_date = models.DateField(null=True, blank=True)

    inherent_score = models.PositiveIntegerField(default=0)
    residual_score = models.PositiveIntegerField(default=0)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)

    linked_requirements = models.ManyToManyField('jurisdictions.Requirement', blank=True, related_name='linked_risks')

    class Meta:
        ordering = ['-residual_score', 'title']

    def __str__(self):
        return self.title

    def compute_scores(self):
        """Compute inherent and residual risk scores and severity label."""
        inherent = (self.likelihood or 1) * (self.impact or 1)  # 1..25

        sensitivity_bonus = max(0, (self.data_sensitivity or 1) - 2)  # 0..3
        volume_bonus = max(0, (self.data_volume_log10 or 0) - 3) / 2  # 0..1.5
        regulator_bonus = max(0, (self.regulator_activity or 1) - 2) / 2  # 0..1.5

        modified = inherent * (1 + sensitivity_bonus * 0.15 + volume_bonus * 0.1 + regulator_bonus * 0.1)

        effectiveness = max(0, min(100, self.control_effectiveness or 0))
        residual = modified * (1 - effectiveness / 100 * 0.8)

        self.inherent_score = round(modified)
        self.residual_score = round(residual)

        if residual >= 20:
            self.severity = Severity.CRITICAL
        elif residual >= 14:
            self.severity = Severity.HIGH
        elif residual >= 8:
            self.severity = Severity.MEDIUM
        elif residual >= 4:
            self.severity = Severity.LOW
        else:
            self.severity = Severity.INFO
        return self

    def save(self, *args, **kwargs):
        self.compute_scores()
        super().save(*args, **kwargs)
