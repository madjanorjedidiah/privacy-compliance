"""Shared constants across apps — single source of truth."""
from .choices import ControlStatus


COUNTRY_CHOICES = [
    ('GH', '🇬🇭 Ghana'),
    ('KE', '🇰🇪 Kenya'),
    ('NG', '🇳🇬 Nigeria'),
    ('US', '🇺🇸 United States'),
    ('US-CA', '🇺🇸 California (USA)'),
    ('GB', '🇬🇧 United Kingdom'),
    ('DE', '🇩🇪 Germany'),
    ('FR', '🇫🇷 France'),
    ('IE', '🇮🇪 Ireland'),
    ('NL', '🇳🇱 Netherlands'),
    ('ES', '🇪🇸 Spain'),
    ('IT', '🇮🇹 Italy'),
    ('ZA', '🇿🇦 South Africa'),
    ('CA', '🇨🇦 Canada'),
]


COMPLIANCE_STATUS_ORDER = [
    ControlStatus.NOT_STARTED,
    ControlStatus.IN_PROGRESS,
    ControlStatus.IMPLEMENTED,
]


DONE_CONTROL_STATUSES = [
    ControlStatus.IMPLEMENTED,
    ControlStatus.VERIFIED,
    ControlStatus.NOT_APPLICABLE,
]
