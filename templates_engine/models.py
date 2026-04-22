from django.conf import settings
from django.db import models

from core.models import OrgScopedModel, TimeStampedModel


class TemplateKind(models.TextChoices):
    PRIVACY_NOTICE = 'privacy_notice', 'Privacy Notice / Policy'
    ROPA = 'ropa', 'Record of Processing Activities (ROPA)'
    DSAR_RESPONSE = 'dsar_response', 'DSAR Response'
    DPIA = 'dpia', 'Data Protection Impact Assessment'
    BREACH_NOTIFICATION = 'breach_notification', 'Regulator Breach Notification'
    DPA_CLAUSES = 'dpa_clauses', 'Data Processing Agreement clauses'
    COOKIE_POLICY = 'cookie_policy', 'Cookie Policy'


class TemplateDefinition(TimeStampedModel):
    """A jurisdiction-aware template. Body is a Django template string rendered by the engine."""
    kind = models.CharField(max_length=32, choices=TemplateKind.choices)
    jurisdiction_code = models.CharField(max_length=16, blank=True, help_text='Empty = universal')
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    body = models.TextField(help_text='Django-template string. Context = {org, profile, jurisdiction, frameworks, today}.')
    version = models.PositiveSmallIntegerField(default=1)
    requirements = models.ManyToManyField(
        'jurisdictions.Requirement', blank=True, related_name='templates',
        help_text='Requirements this template helps satisfy.',
    )

    class Meta:
        ordering = ['kind', 'jurisdiction_code']
        unique_together = ('kind', 'jurisdiction_code', 'version')

    def __str__(self):
        return f'{self.get_kind_display()} ({self.jurisdiction_code or "universal"})'


class GeneratedDocument(OrgScopedModel):
    template = models.ForeignKey(TemplateDefinition, on_delete=models.PROTECT, related_name='documents')
    title = models.CharField(max_length=240)
    rendered_content = models.TextField()
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
