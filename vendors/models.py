from django.db import models

from core.models import OrgScopedModel


class Vendor(OrgScopedModel):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=40, choices=[
        ('processor', 'Processor'),
        ('sub_processor', 'Sub-processor'),
        ('controller', 'Controller (joint)'),
    ], default='processor')
    country = models.CharField(max_length=2, help_text='ISO-3166 alpha-2 code')
    data_categories = models.JSONField(default=list)
    purposes = models.JSONField(default=list)
    dpa_on_file = models.BooleanField(default=False)
    dpa_expires_on = models.DateField(null=True, blank=True)
    transfer_mechanism = models.CharField(max_length=40, blank=True)
    last_reviewed = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
