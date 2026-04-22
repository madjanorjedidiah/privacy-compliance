import secrets

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError, models, transaction
from django.db.models import Q, UniqueConstraint
from django.utils.text import slugify

from core.choices import DataCategory, ProcessingPurpose, Sector, TransferMechanism
from core.models import TimeStampedModel
from core.validators import list_of_choices, list_of_strings


class User(AbstractUser):
    display_name = models.CharField(max_length=120, blank=True)
    job_title = models.CharField(max_length=120, blank=True)

    @property
    def friendly_name(self):
        return self.display_name or self.get_full_name() or self.username


class Organization(TimeStampedModel):
    REVENUE_BANDS = [
        ('<1M', 'Under $1M'),
        ('1-10M', '$1M – $10M'),
        ('10-25M', '$10M – $25M'),
        ('25-100M', '$25M – $100M'),
        ('100M+', 'Over $100M'),
    ]
    EMPLOYEE_BANDS = [
        ('1-10', '1 – 10'),
        ('11-50', '11 – 50'),
        ('51-250', '51 – 250'),
        ('251-1000', '251 – 1,000'),
        ('1000+', '1,000+'),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=2, help_text='ISO-3166 alpha-2 code of HQ')
    revenue_band = models.CharField(max_length=12, choices=REVENUE_BANDS, blank=True)
    employee_band = models.CharField(max_length=12, choices=EMPLOYEE_BANDS, blank=True)
    onboarded_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:140] or 'org'
            # Race-safe: retry with a random suffix on IntegrityError rather
            # than pre-checking for uniqueness (TOCTOU).
            for attempt in range(6):
                candidate = base if attempt == 0 else f'{base}-{secrets.token_hex(3)}'
                self.slug = candidate
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    continue
            raise IntegrityError(f'Could not generate a unique slug for {self.name}')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class OrgProfile(TimeStampedModel):
    """Data-processing profile. Drives the applicability engine."""
    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name='profile'
    )

    sectors = models.JSONField(
        default=list,
        validators=[list_of_choices(Sector.choices)],
        help_text=f'Choices: {[c[0] for c in Sector.choices]}',
    )
    data_categories = models.JSONField(
        default=list,
        validators=[list_of_choices(DataCategory.choices)],
        help_text=f'Choices: {[c[0] for c in DataCategory.choices]}',
    )
    processing_purposes = models.JSONField(
        default=list,
        validators=[list_of_choices(ProcessingPurpose.choices)],
        help_text=f'Choices: {[c[0] for c in ProcessingPurpose.choices]}',
    )

    data_subject_locations = models.JSONField(
        default=list,
        validators=[list_of_strings],
        help_text='ISO alpha-2 country codes where data subjects reside (e.g. ["GH","NG","KE","DE","US-CA"])',
    )

    has_establishment_in = models.JSONField(
        default=list,
        validators=[list_of_strings],
        help_text='Countries where the organization has an establishment',
    )

    processes_eu_residents = models.BooleanField(default=False)
    offers_to_california_residents = models.BooleanField(default=False)
    cross_border_transfers = models.BooleanField(default=False)
    transfer_mechanisms = models.JSONField(
        default=list,
        validators=[list_of_choices(TransferMechanism.choices)],
    )

    uses_automated_decision_making = models.BooleanField(default=False)
    processes_childrens_data = models.BooleanField(default=False)
    processes_health_data = models.BooleanField(default=False)
    processes_biometric_data = models.BooleanField(default=False)

    annual_data_subjects_estimate = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Profile of {self.organization}'


class Membership(TimeStampedModel):
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        DPO = 'dpo', 'Data Protection Officer'
        COMPLIANCE = 'compliance', 'Compliance Officer'
        AUDITOR = 'auditor', 'Auditor (read-only)'
        VIEWER = 'viewer', 'Viewer'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OWNER)
    is_primary = models.BooleanField(default=False, help_text='User\'s active workspace')

    class Meta:
        unique_together = ('organization', 'user')
        constraints = [
            UniqueConstraint(
                fields=['user'],
                condition=Q(is_primary=True),
                name='membership_one_primary_per_user',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Clear the primary flag on any other membership this user has,
            # inside a transaction, to respect the partial-unique constraint.
            with transaction.atomic():
                Membership.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} @ {self.organization} ({self.role})'
