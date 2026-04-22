from django.conf import settings
from django.db import models
from django.utils import timezone

from core.choices import DataCategory, ProcessingPurpose, TransferMechanism
from core.models import OrgScopedModel
from core.validators import list_of_choices, list_of_strings


class Vendor(OrgScopedModel):
    class Role(models.TextChoices):
        PROCESSOR = 'processor', 'Processor'
        SUB_PROCESSOR = 'sub_processor', 'Sub-processor'
        JOINT_CONTROLLER = 'joint', 'Joint controller'

    class RiskTier(models.TextChoices):
        LOW = 'low', 'Low (non-personal or pseudonymised)'
        MEDIUM = 'medium', 'Medium (business PII)'
        HIGH = 'high', 'High (sensitive / financial / health)'
        CRITICAL = 'critical', 'Critical (special category at scale)'

    name = models.CharField(max_length=160)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.PROCESSOR)
    country = models.CharField(max_length=2, help_text='ISO-3166 alpha-2 code')
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)

    data_categories = models.JSONField(
        default=list, validators=[list_of_choices(DataCategory.choices)],
    )
    purposes = models.JSONField(
        default=list, validators=[list_of_choices(ProcessingPurpose.choices)],
    )
    sub_processor_countries = models.JSONField(
        default=list, validators=[list_of_strings],
        help_text='Countries where the vendor stores or processes data.',
    )

    # DPA lifecycle
    dpa_on_file = models.BooleanField(default=False)
    dpa_signed_on = models.DateField(null=True, blank=True)
    dpa_expires_on = models.DateField(null=True, blank=True)
    dpa_document_url = models.URLField(blank=True)

    # Transfer
    transfer_mechanism = models.CharField(
        max_length=16, choices=TransferMechanism.choices, blank=True,
    )
    tia_completed = models.BooleanField(
        default=False,
        help_text='Transfer Impact Assessment completed (post-Schrems II).',
    )

    # Risk + audit
    risk_tier = models.CharField(max_length=10, choices=RiskTier.choices, default=RiskTier.MEDIUM)
    last_security_audit = models.DateField(null=True, blank=True)
    next_security_audit = models.DateField(null=True, blank=True)
    certifications = models.JSONField(
        default=list, validators=[list_of_strings],
        help_text='Certifications held, e.g. ["ISO 27001", "SOC 2 Type II", "ISO 27701"].',
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='owned_vendors',
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def dpa_expiring_soon(self):
        if not self.dpa_expires_on:
            return False
        from datetime import timedelta
        return self.dpa_expires_on <= (timezone.now().date() + timedelta(days=60))

    @property
    def dpa_expired(self):
        if not self.dpa_expires_on:
            return False
        return self.dpa_expires_on < timezone.now().date()
