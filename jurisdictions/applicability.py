"""
Applicability engine.

Each Requirement optionally references a rule name here via `applicability_rule`.
A rule takes an OrgProfile and returns (applicable: bool, rationale: str).

Framework-level applicability is dispatched through FRAMEWORK_RULES — a
registry keyed by framework code, so adding a new jurisdiction is a matter
of registering a callable rather than editing a large if/elif tree.
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


def _rule_gdpr(profile):
    locations = profile.data_subject_locations or []
    establishments = profile.has_establishment_in or []
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


def _rule_by_country(country_code, display_name, act_name):
    """Factory for simple "process data of residents OR established in country" rules."""
    def _rule(profile):
        locations = profile.data_subject_locations or []
        establishments = profile.has_establishment_in or []
        if country_code in locations or country_code in establishments:
            return ApplicabilityResult(
                True,
                f'The {act_name} applies because you process data of {display_name} residents or are established in {display_name}.',
            )
        return ApplicabilityResult(False, f'No {display_name} subjects or establishment indicated.')
    return _rule


def _rule_ccpa(profile):
    locations = profile.data_subject_locations or []
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
        'You target California residents but do not meet the revenue/volume thresholds for CCPA/CPRA. Requirements may still apply via contract.',
    )


FRAMEWORK_RULES = {
    'GDPR': _rule_gdpr,
    'GH-DPA-2012': _rule_by_country('GH', 'Ghanaian', 'Ghana Data Protection Act'),
    'KE-DPA-2019': _rule_by_country('KE', 'Kenyan', 'Kenya Data Protection Act'),
    'NG-NDPA-2023': _rule_by_country('NG', 'Nigerian', 'Nigeria Data Protection Act 2023'),
    'US-CCPA': _rule_ccpa,
}


def framework_applies(profile, framework_code: str) -> ApplicabilityResult:
    rule = FRAMEWORK_RULES.get(framework_code)
    if rule is None:
        return ApplicabilityResult(True, 'No framework rule — defaulting to applicable.')
    return rule(profile)


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
