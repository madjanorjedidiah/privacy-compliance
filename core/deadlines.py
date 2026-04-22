"""Per-jurisdiction DSAR and incident notification windows."""
from datetime import timedelta

from django.conf import settings


def _cfg(key, default):
    return settings.BRAND.get('DEADLINES', {}).get(key, default)


def _per_jur(code, key, default):
    overrides = settings.BRAND.get('DEADLINES_PER_JURISDICTION', {})
    return overrides.get(code, {}).get(key, default)


def dsar_due_at(received_at, jurisdiction_code=None):
    days = _per_jur(jurisdiction_code, 'dsar_days', _cfg('DSAR_DAYS_DEFAULT', 30))
    return received_at + timedelta(days=days)


def incident_deadline(detected_at, jurisdiction_codes=None):
    """Return the earliest regulator-notification deadline across affected jurisdictions."""
    default_hours = _cfg('INCIDENT_NOTIFY_HOURS_DEFAULT', 72)
    if not jurisdiction_codes:
        return detected_at + timedelta(hours=default_hours)
    windows = []
    for code in jurisdiction_codes:
        hours = _per_jur(code, 'incident_notify_hours', default_hours)
        windows.append(hours)
    earliest = min(windows) if windows else default_hours
    return detected_at + timedelta(hours=earliest)
