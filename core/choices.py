from django.db import models


class Severity(models.TextChoices):
    CRITICAL = 'critical', 'Critical'
    HIGH = 'high', 'High'
    MEDIUM = 'medium', 'Medium'
    LOW = 'low', 'Low'
    INFO = 'info', 'Info'


class ControlStatus(models.TextChoices):
    NOT_STARTED = 'not_started', 'Not started'
    IN_PROGRESS = 'in_progress', 'In progress'
    IMPLEMENTED = 'implemented', 'Implemented'
    VERIFIED = 'verified', 'Verified'
    NOT_APPLICABLE = 'not_applicable', 'Not applicable'


class RiskLevel(models.IntegerChoices):
    LOW = 1, 'Low'
    MODERATE = 2, 'Moderate'
    ELEVATED = 3, 'Elevated'
    HIGH = 4, 'High'
    SEVERE = 5, 'Severe'


class DataCategory(models.TextChoices):
    GENERAL_PII = 'general_pii', 'General personal data'
    CONTACT = 'contact', 'Contact details'
    FINANCIAL = 'financial', 'Financial'
    HEALTH = 'health', 'Health / Medical'
    BIOMETRIC = 'biometric', 'Biometric'
    LOCATION = 'location', 'Location / Geolocation'
    CHILDREN = 'children', 'Data of minors (children)'
    BEHAVIORAL = 'behavioral', 'Behavioral / Profiling'
    SPECIAL_CATEGORY = 'special_category', 'Special category (race, religion, union, sexual orientation, political)'
    CRIMINAL = 'criminal', 'Criminal convictions'
    CREDENTIALS = 'credentials', 'Authentication credentials'
    GOVERNMENT_ID = 'government_id', 'Government-issued ID'


class ProcessingPurpose(models.TextChoices):
    SERVICE_DELIVERY = 'service_delivery', 'Service delivery'
    MARKETING = 'marketing', 'Marketing / Advertising'
    ANALYTICS = 'analytics', 'Analytics / Product improvement'
    FRAUD = 'fraud', 'Fraud prevention / Security'
    HR = 'hr', 'HR / Employment'
    LEGAL = 'legal', 'Legal obligation / Tax / Accounting'
    RESEARCH = 'research', 'Research'
    PERSONALIZATION = 'personalization', 'Personalization'
    KYC = 'kyc', 'KYC / Regulatory verification'


class Sector(models.TextChoices):
    FINTECH = 'fintech', 'Fintech / Financial services'
    HEALTH = 'health', 'Healthcare'
    ECOMMERCE = 'ecommerce', 'E-commerce / Retail'
    SAAS = 'saas', 'SaaS / Software'
    EDUCATION = 'education', 'Education'
    TELECOM = 'telecom', 'Telecom'
    NGO = 'ngo', 'NGO / Non-profit'
    PUBLIC = 'public', 'Public sector'
    MEDIA = 'media', 'Media / Advertising'
    OTHER = 'other', 'Other'


class TransferMechanism(models.TextChoices):
    SCC = 'scc', 'Standard Contractual Clauses'
    BCR = 'bcr', 'Binding Corporate Rules'
    ADEQUACY = 'adequacy', 'Adequacy decision'
    DEROGATION = 'derogation', 'Derogation (Art. 49 GDPR / equivalent)'
    CONSENT = 'consent', 'Explicit consent'
    NONE = 'none', 'No mechanism in place'


class DSARType(models.TextChoices):
    ACCESS = 'access', 'Access'
    RECTIFICATION = 'rectification', 'Rectification'
    ERASURE = 'erasure', 'Erasure / Deletion'
    RESTRICTION = 'restriction', 'Restriction of processing'
    PORTABILITY = 'portability', 'Portability'
    OBJECTION = 'objection', 'Objection'
    AUTOMATED_DECISION = 'automated_decision', 'Opt-out of automated decisions'
    OPT_OUT_SALE = 'opt_out_sale', 'Opt-out of sale/share (CCPA)'


class IncidentSeverity(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'
