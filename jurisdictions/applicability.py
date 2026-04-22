"""
Applicability engine.

Each Requirement optionally references a rule name here via `applicability_rule`.
A rule takes an OrgProfile and returns (applicable: bool, rationale: str).

Design notes:
- Rules are pure functions of OrgProfile fields.
- We return a rationale string that we can surface in the UI ("Why is this in scope?").
- Framework-level applicability is determined by presence of subject-country or
  establishment in the jurisdiction's country list (see FRAMEWORK_APPLICABILITY).
"""
from dataclasses import dataclass


@dataclass
class ApplicabilityResult:
    applicable: bool
    rationale: str


# ---------------------------------------------------------------------------
# Framework-level rules
# ---------------------------------------------------------------------------

EU_COUNTRIES = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE',
    'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT',
    'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO',
}


def _any(seq_a, seq_b):
    return any(x in seq_b for x in (seq_a or []))


def framework_applies(profile, framework_code: str) -> ApplicabilityResult:
    locations = profile.data_subject_locations or []
    establishments = profile.has_establishment_in or []

    if framework_code == 'GDPR':
        eu_subject = _any(locations, EU_COUNTRIES) or profile.processes_eu_residents
        eu_estab = _any(establishments, EU_COUNTRIES)
        if eu_subject or eu_estab:
            reason = []
            if eu_estab:
                reason.append('your organization has an establishment in the EU/EEA')
            if eu_subject:
                reason.append('you process data of EU/EEA residents')
            return ApplicabilityResult(True, 'GDPR applies because ' + ' and '.join(reason) + '.')
        return ApplicabilityResult(False, 'No EU/EEA subjects or establishment indicated.')

    if framework_code == 'GH-DPA-2012':
        if 'GH' in locations or 'GH' in establishments:
            return ApplicabilityResult(True, 'The Ghana Data Protection Act applies because you process data of Ghanaian residents or are established in Ghana.')
        return ApplicabilityResult(False, 'No Ghanaian subjects or establishment indicated.')

    if framework_code == 'KE-DPA-2019':
        if 'KE' in locations or 'KE' in establishments:
            return ApplicabilityResult(True, 'The Kenya Data Protection Act applies because you process data of Kenyan residents or are established in Kenya.')
        return ApplicabilityResult(False, 'No Kenyan subjects or establishment indicated.')

    if framework_code == 'NG-NDPA-2023':
        if 'NG' in locations or 'NG' in establishments:
            return ApplicabilityResult(True, 'The Nigeria Data Protection Act 2023 applies because you process data of Nigerian residents or are established in Nigeria.')
        return ApplicabilityResult(False, 'No Nigerian subjects or establishment indicated.')

    if framework_code == 'US-CCPA':
        # CCPA/CPRA thresholds (simplified): targets California residents AND
        # (>$25M revenue OR >100k consumers OR >50% revenue from selling/sharing data).
        if not profile.offers_to_california_residents and 'US-CA' not in locations:
            return ApplicabilityResult(False, 'You do not indicate targeting California residents.')
        revenue = profile.organization.revenue_band
        meets_revenue = revenue in {'25-100M', '100M+'}
        meets_volume = profile.annual_data_subjects_estimate >= 100_000
        if meets_revenue or meets_volume:
            reason = []
            if meets_revenue:
                reason.append('your revenue exceeds the $25M threshold')
            if meets_volume:
                reason.append(f'you process data of {profile.annual_data_subjects_estimate:,} subjects')
            return ApplicabilityResult(True, 'CCPA/CPRA applies because you target California residents and ' + ' and '.join(reason) + '.')
        return ApplicabilityResult(
            False,
            'You target California residents but do not meet the revenue/volume thresholds for CCPA/CPRA. Requirements may still apply via contract.'
        )

    return ApplicabilityResult(True, 'No framework rule — defaulting to applicable.')


# ---------------------------------------------------------------------------
# Per-requirement rules (optional)
# ---------------------------------------------------------------------------

def requires_dpia(profile) -> ApplicabilityResult:
    if profile.uses_automated_decision_making or profile.processes_health_data or profile.processes_biometric_data or profile.processes_childrens_data:
        return ApplicabilityResult(True, 'High-risk processing detected (automated decisions, health, biometric, or children\'s data).')
    return ApplicabilityResult(False, 'No high-risk processing indicators — DPIA recommended but not mandatory.')


def requires_dpo(profile) -> ApplicabilityResult:
    if profile.processes_health_data or profile.processes_biometric_data:
        return ApplicabilityResult(True, 'Large-scale processing of special category data triggers a mandatory DPO appointment.')
    if profile.annual_data_subjects_estimate >= 10_000:
        return ApplicabilityResult(True, f'Processing {profile.annual_data_subjects_estimate:,} subjects — appointment of a DPO is recommended.')
    return ApplicabilityResult(True, 'A DPO/privacy lead remains best practice even when not mandatory.')


def requires_transfer_mechanism(profile) -> ApplicabilityResult:
    if profile.cross_border_transfers:
        return ApplicabilityResult(True, 'You indicate cross-border transfers — a lawful transfer mechanism is required.')
    return ApplicabilityResult(False, 'No cross-border transfers declared.')


def requires_children_safeguards(profile) -> ApplicabilityResult:
    if profile.processes_childrens_data:
        return ApplicabilityResult(True, 'Processing children\'s data triggers enhanced consent and safeguards.')
    return ApplicabilityResult(False, 'No processing of children\'s data declared.')


def requires_opt_out_sale(profile) -> ApplicabilityResult:
    if profile.offers_to_california_residents:
        return ApplicabilityResult(True, 'Do-Not-Sell/Share link is a CCPA/CPRA requirement for California consumers.')
    return ApplicabilityResult(False, 'You do not target California residents.')


RULE_REGISTRY = {
    'requires_dpia': requires_dpia,
    'requires_dpo': requires_dpo,
    'requires_transfer_mechanism': requires_transfer_mechanism,
    'requires_children_safeguards': requires_children_safeguards,
    'requires_opt_out_sale': requires_opt_out_sale,
}


def requirement_applies(requirement, profile) -> ApplicabilityResult:
    rule = (requirement.applicability_rule or '').strip()
    if not rule:
        return ApplicabilityResult(True, 'Baseline obligation — applies to all processors under this framework.')
    fn = RULE_REGISTRY.get(rule)
    if fn is None:
        return ApplicabilityResult(True, f'Rule `{rule}` not found — defaulting to applicable.')
    return fn(profile)
