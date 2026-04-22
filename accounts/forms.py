from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.choices import DataCategory, ProcessingPurpose, Sector, TransferMechanism
from core.constants import COUNTRY_CHOICES

from .models import Organization, OrgProfile, User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    display_name = forms.CharField(required=True, max_length=120, label='Full name')
    organization_name = forms.CharField(required=True, max_length=160)
    organization_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label='HQ country')

    class Meta:
        model = User
        fields = ['username', 'email', 'display_name', 'password1', 'password2']


class OrgBasicsForm(forms.ModelForm):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    class Meta:
        model = Organization
        fields = ['name', 'website', 'country', 'revenue_band', 'employee_band']


class OrgProfileForm(forms.ModelForm):
    sectors = forms.MultipleChoiceField(
        choices=Sector.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    data_categories = forms.MultipleChoiceField(
        choices=DataCategory.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    processing_purposes = forms.MultipleChoiceField(
        choices=ProcessingPurpose.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    data_subject_locations = forms.MultipleChoiceField(
        choices=COUNTRY_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Where do the people whose data you process live?',
    )
    has_establishment_in = forms.MultipleChoiceField(
        choices=COUNTRY_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Countries where you have an office, subsidiary, or legal presence',
    )
    transfer_mechanisms = forms.MultipleChoiceField(
        choices=TransferMechanism.choices, required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = OrgProfile
        fields = [
            'sectors', 'data_categories', 'processing_purposes',
            'data_subject_locations', 'has_establishment_in',
            'processes_eu_residents', 'offers_to_california_residents',
            'cross_border_transfers', 'transfer_mechanisms',
            'uses_automated_decision_making',
            'processes_childrens_data', 'processes_health_data', 'processes_biometric_data',
            'annual_data_subjects_estimate',
        ]

    def clean(self):
        cleaned = super().clean()
        for field in ('sectors', 'data_categories', 'processing_purposes',
                      'data_subject_locations', 'has_establishment_in',
                      'transfer_mechanisms'):
            value = cleaned.get(field)
            if value is None:
                cleaned[field] = []
        return cleaned
