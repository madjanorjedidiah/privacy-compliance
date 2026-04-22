from django.conf import settings
from django.db import models

from core.choices import DataCategory, ProcessingPurpose, TransferMechanism
from core.models import OrgScopedModel
from core.validators import list_of_choices, list_of_strings


class LawfulBasis(models.TextChoices):
    CONSENT = 'consent', 'Consent (Art. 6(1)(a))'
    CONTRACT = 'contract', 'Contract (Art. 6(1)(b))'
    LEGAL_OBLIGATION = 'legal_obligation', 'Legal obligation (Art. 6(1)(c))'
    VITAL_INTERESTS = 'vital_interests', 'Vital interests (Art. 6(1)(d))'
    PUBLIC_TASK = 'public_task', 'Public task (Art. 6(1)(e))'
    LEGITIMATE_INTERESTS = 'legitimate_interests', 'Legitimate interests (Art. 6(1)(f))'


class SpecialCategoryBasis(models.TextChoices):
    NONE = 'none', 'Not processing special categories'
    EXPLICIT_CONSENT = 'explicit_consent', 'Explicit consent (Art. 9(2)(a))'
    EMPLOYMENT = 'employment', 'Employment / social security (Art. 9(2)(b))'
    VITAL = 'vital', 'Vital interests (Art. 9(2)(c))'
    NON_PROFIT = 'non_profit', 'Not-for-profit activity (Art. 9(2)(d))'
    PUBLIC = 'public', 'Data made public by subject (Art. 9(2)(e))'
    LEGAL_CLAIMS = 'legal_claims', 'Legal claims (Art. 9(2)(f))'
    SUBSTANTIAL_PUBLIC = 'substantial_public', 'Substantial public interest (Art. 9(2)(g))'
    HEALTH = 'health', 'Preventive / occupational / public health (Art. 9(2)(h)-(i))'
    ARCHIVING = 'archiving', 'Archiving / research / statistics (Art. 9(2)(j))'


class DataSubjectCategory(models.TextChoices):
    CUSTOMERS = 'customers', 'Customers / end users'
    PROSPECTS = 'prospects', 'Prospects / leads'
    EMPLOYEES = 'employees', 'Employees'
    CONTRACTORS = 'contractors', 'Contractors / vendors'
    VISITORS = 'visitors', 'Website visitors'
    CHILDREN = 'children', 'Children (<16 or local equivalent)'
    PATIENTS = 'patients', 'Patients'
    STUDENTS = 'students', 'Students'
    JOB_APPLICANTS = 'job_applicants', 'Job applicants'
    THIRD_PARTIES = 'third_parties', 'Third parties'


class ProcessingActivity(OrgScopedModel):
    """Structured Art. 30 GDPR / NDPA §29 / Kenya DPA §25 record."""
    class Role(models.TextChoices):
        CONTROLLER = 'controller', 'Controller'
        JOINT_CONTROLLER = 'joint', 'Joint controller'
        PROCESSOR = 'processor', 'Processor'

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.CONTROLLER)

    purposes = models.JSONField(
        default=list,
        validators=[list_of_choices(ProcessingPurpose.choices)],
        help_text='Processing purposes from the canonical list.',
    )
    lawful_basis = models.CharField(max_length=24, choices=LawfulBasis.choices, default=LawfulBasis.CONTRACT)
    special_category_basis = models.CharField(
        max_length=24, choices=SpecialCategoryBasis.choices, default=SpecialCategoryBasis.NONE,
    )
    lawful_basis_note = models.TextField(
        blank=True,
        help_text='For legitimate interests, include the LIA outcome summary.',
    )

    data_categories = models.JSONField(
        default=list,
        validators=[list_of_choices(DataCategory.choices)],
    )
    data_subject_categories = models.JSONField(
        default=list,
        validators=[list_of_choices(DataSubjectCategory.choices)],
    )

    recipients = models.JSONField(
        default=list,
        validators=[list_of_strings],
        help_text='Free-text list of internal recipients + processor / sub-processor names.',
    )
    internal_systems = models.JSONField(
        default=list,
        validators=[list_of_strings],
        help_text='Internal systems / data stores processing this activity.',
    )

    cross_border_transfers = models.BooleanField(default=False)
    transfer_countries = models.JSONField(
        default=list,
        validators=[list_of_strings],
        help_text='ISO country codes of destination jurisdictions.',
    )
    transfer_mechanism = models.CharField(
        max_length=24, choices=TransferMechanism.choices, blank=True,
    )

    retention_schedule = models.ForeignKey(
        'retention.RetentionPolicy',
        on_delete=models.SET_NULL, null=True, blank=True, related_name='activities',
    )
    retention_note = models.CharField(max_length=240, blank=True)

    security_measures = models.TextField(
        blank=True,
        help_text='Technical and organisational measures (TOMs) applied.',
    )
    dpia_required = models.BooleanField(default=False)
    dpia = models.ForeignKey(
        'dpia.DPIA', on_delete=models.SET_NULL, null=True, blank=True, related_name='activities',
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='owned_processing_activities',
    )
    last_reviewed = models.DateField(null=True, blank=True)
    next_review = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'processing activity'
        verbose_name_plural = 'processing activities (ROPA)'

    def __str__(self):
        return self.name
