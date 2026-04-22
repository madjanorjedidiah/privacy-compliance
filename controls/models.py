from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from core.choices import ControlStatus
from core.models import OrgScopedModel, TimeStampedModel


ALLOWED_EVIDENCE_EXTENSIONS = [
    'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp',
    'doc', 'docx', 'xls', 'xlsx', 'csv',
    'txt', 'md', 'json', 'log',
]
MAX_EVIDENCE_FILE_BYTES = 10 * 1024 * 1024  # 10 MiB


def _validate_file_size(f):
    if f.size and f.size > MAX_EVIDENCE_FILE_BYTES:
        raise ValidationError(
            f'Evidence files must be smaller than {MAX_EVIDENCE_FILE_BYTES // (1024 * 1024)} MB.'
        )


class Control(OrgScopedModel):
    """An org-level control tracking fulfilment of one Requirement."""
    requirement = models.ForeignKey('jurisdictions.Requirement', on_delete=models.CASCADE, related_name='controls')
    status = models.CharField(max_length=20, choices=ControlStatus.choices, default=ControlStatus.NOT_STARTED)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_controls')
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('organization', 'requirement')
        ordering = ['requirement__framework__short_name', 'requirement__code']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'due_date']),
        ]

    def __str__(self):
        return f'{self.requirement.code} — {self.organization}'

    @property
    def is_done(self):
        return self.status in (ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED, ControlStatus.NOT_APPLICABLE)

    @property
    def progress_weight(self):
        return {
            ControlStatus.NOT_STARTED: 0,
            ControlStatus.IN_PROGRESS: 40,
            ControlStatus.IMPLEMENTED: 80,
            ControlStatus.VERIFIED: 100,
            ControlStatus.NOT_APPLICABLE: 100,
        }.get(self.status, 0)


class ControlStatusChange(TimeStampedModel):
    """Append-only log of every control status transition, for audit trails."""
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=20, choices=ControlStatus.choices)
    to_status = models.CharField(max_length=20, choices=ControlStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+',
    )
    note = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['control', '-created_at'])]

    def __str__(self):
        return f'{self.control.requirement.code}: {self.from_status} → {self.to_status}'


class Evidence(TimeStampedModel):
    control = models.ForeignKey(Control, on_delete=models.CASCADE, related_name='evidence')
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='evidence/%Y/%m/', null=True, blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EVIDENCE_EXTENSIONS),
            _validate_file_size,
        ],
    )
    external_link = models.URLField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
