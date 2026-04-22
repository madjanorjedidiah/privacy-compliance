from django.db import models

from core.models import TimeStampedModel


class Jurisdiction(TimeStampedModel):
    code = models.CharField(max_length=8, unique=True, help_text='ISO or region code, e.g. GH, KE, NG, US, EU')
    name = models.CharField(max_length=120)
    region = models.CharField(max_length=60, blank=True)
    authority = models.CharField(max_length=240, blank=True, help_text='Regulator name')
    authority_url = models.URLField(blank=True)
    flag_emoji = models.CharField(max_length=8, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Framework(TimeStampedModel):
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.CASCADE, related_name='frameworks')
    code = models.SlugField(max_length=40, unique=True, help_text='e.g. GDPR, GH-DPA-2012, NDPA-2023, CCPA')
    short_name = models.CharField(max_length=60)
    long_name = models.CharField(max_length=240)
    summary = models.TextField(blank=True)
    enacted_year = models.PositiveSmallIntegerField(null=True, blank=True)
    reference_url = models.URLField(blank=True)
    max_fine_description = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['jurisdiction__name', 'short_name']

    def __str__(self):
        return self.short_name


class RequirementCategory(models.TextChoices):
    GOVERNANCE = 'governance', 'Governance & Accountability'
    LAWFUL_BASIS = 'lawful_basis', 'Lawful basis & consent'
    TRANSPARENCY = 'transparency', 'Transparency & notices'
    RIGHTS = 'rights', 'Data subject rights'
    SECURITY = 'security', 'Security of processing'
    BREACH = 'breach', 'Breach notification'
    TRANSFERS = 'transfers', 'International transfers'
    DPIA = 'dpia', 'DPIA / Risk assessment'
    VENDORS = 'vendors', 'Processors & sub-processors'
    ROPA = 'ropa', 'Record of processing'
    RETENTION = 'retention', 'Retention & minimisation'
    SPECIAL = 'special', 'Special categories / children'
    REGISTRATION = 'registration', 'Regulator registration'
    AUTOMATED = 'automated', 'Automated decision-making'


class Requirement(TimeStampedModel):
    """An atomic obligation in a framework (e.g. 'Maintain Record of Processing Activities')."""
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, related_name='requirements')
    code = models.CharField(max_length=40, help_text='Citable reference, e.g. GDPR-Art-30')
    title = models.CharField(max_length=240)
    summary = models.TextField()
    category = models.CharField(max_length=20, choices=RequirementCategory.choices)
    citation = models.CharField(max_length=240, blank=True, help_text='Article / Section reference')
    severity_weight = models.PositiveSmallIntegerField(default=3, help_text='1 (low) – 5 (critical)')
    applicability_rule = models.CharField(
        max_length=80, blank=True,
        help_text='Name of rule function in jurisdictions.applicability (empty = always applies if framework applies)',
    )
    guidance = models.TextField(blank=True, help_text='Practical steps the org should take')
    typical_evidence = models.TextField(blank=True, help_text='Examples of evidence that satisfies this requirement')

    class Meta:
        ordering = ['framework', 'code']
        unique_together = ('framework', 'code')

    def __str__(self):
        return f'{self.framework.short_name} • {self.code} — {self.title}'


class RequirementMapping(TimeStampedModel):
    """Cross-jurisdictional equivalence between two requirements."""
    class Equivalence(models.TextChoices):
        EQUIVALENT = 'equivalent', 'Equivalent'
        STRICTER = 'stricter', 'Target is stricter'
        WEAKER = 'weaker', 'Target is weaker'
        PARTIAL = 'partial', 'Partial overlap'

    source = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='mappings_out')
    target = models.ForeignKey(Requirement, on_delete=models.CASCADE, related_name='mappings_in')
    equivalence = models.CharField(max_length=12, choices=Equivalence.choices)
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        unique_together = ('source', 'target')

    def __str__(self):
        return f'{self.source.code} ↔ {self.target.code} ({self.equivalence})'
