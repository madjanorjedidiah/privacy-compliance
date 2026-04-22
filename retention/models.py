from django.conf import settings
from django.db import models

from core.choices import DataCategory
from core.models import OrgScopedModel


class RetentionPolicy(OrgScopedModel):
    """Data retention schedule entry — one row per data category × context."""
    class Trigger(models.TextChoices):
        COLLECTION = 'collection', 'From date of collection'
        LAST_INTERACTION = 'last_interaction', 'From last interaction'
        CONTRACT_END = 'contract_end', 'From contract termination'
        LEGAL_HOLD_END = 'legal_hold_end', 'From end of legal hold'
        TRANSACTION_DATE = 'transaction_date', 'From transaction date'

    class DestructionMethod(models.TextChoices):
        DELETE = 'delete', 'Secure deletion'
        ANONYMISE = 'anonymise', 'Anonymisation'
        PSEUDONYMISE = 'pseudonymise', 'Pseudonymisation'
        ARCHIVE = 'archive', 'Cold archive'

    name = models.CharField(max_length=200)
    data_category = models.CharField(max_length=32, choices=DataCategory.choices)
    description = models.TextField(blank=True)

    retention_months = models.PositiveSmallIntegerField(
        help_text='Number of months data is retained after the trigger event.',
    )
    trigger = models.CharField(max_length=24, choices=Trigger.choices, default=Trigger.COLLECTION)

    legal_basis = models.CharField(
        max_length=240,
        help_text='Citation that justifies this retention period (e.g. "Tax Act §12 — 6 years").',
        blank=True,
    )
    destruction_method = models.CharField(
        max_length=16, choices=DestructionMethod.choices, default=DestructionMethod.DELETE,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='owned_retention_policies',
    )
    last_reviewed = models.DateField(null=True, blank=True)
    next_review = models.DateField(null=True, blank=True)
    legal_hold = models.BooleanField(
        default=False,
        help_text='If true, suspend automatic destruction (litigation / investigation).',
    )

    class Meta:
        ordering = ['data_category', 'name']
        verbose_name_plural = 'retention policies'

    def __str__(self):
        return f'{self.name} ({self.get_data_category_display()})'
