"""Seed / reset the demo workspace (Kudu Fintech) at 0% compliance."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed demo user + org "Kudu Fintech" at 0% compliance.'

    def handle(self, *args, **options):
        from accounts.models import Membership, Organization, OrgProfile
        from assessments.models import Assessment
        from assessments.services import run_assessment
        from controls.models import Control
        from controls.services import sync_controls_from_assessment
        from dsar.models import DSARRequest
        from incidents.models import Incident
        from risks.models import Risk
        from templates_engine.models import GeneratedDocument

        User = get_user_model()

        user, user_created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@example.com',
                'display_name': 'Demo CEO',
                'is_staff': True,
                'is_superuser': True,
            },
        )
        if user_created:
            user.set_password('demodemo123!')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created user demo / demodemo123!'))
        else:
            self.stdout.write('User demo already present.')

        org, _ = Organization.objects.get_or_create(
            slug='kudu-fintech',
            defaults={
                'name': 'Kudu Fintech',
                'country': 'GH',
                'revenue_band': '10-25M',
                'employee_band': '51-250',
            },
        )

        # Wipe old demo state so the workspace starts at 0%
        Control.objects.filter(organization=org).delete()
        Assessment.objects.filter(organization=org).delete()
        Risk.objects.filter(organization=org).delete()
        DSARRequest.objects.filter(organization=org).delete()
        Incident.objects.filter(organization=org).delete()
        GeneratedDocument.objects.filter(organization=org).delete()

        profile, _ = OrgProfile.objects.get_or_create(organization=org)
        profile.sectors = ['fintech']
        profile.data_categories = ['contact', 'financial', 'government_id', 'behavioral']
        profile.processing_purposes = ['service_delivery', 'fraud', 'kyc', 'analytics']
        profile.data_subject_locations = ['GH', 'KE', 'NG', 'DE', 'FR', 'US-CA']
        profile.has_establishment_in = ['GH']
        profile.processes_eu_residents = True
        profile.offers_to_california_residents = True
        profile.cross_border_transfers = True
        profile.transfer_mechanisms = ['scc']
        profile.uses_automated_decision_making = True
        profile.processes_childrens_data = False
        profile.processes_health_data = False
        profile.processes_biometric_data = False
        profile.annual_data_subjects_estimate = 250_000
        profile.save()

        Membership.objects.get_or_create(
            user=user, organization=org,
            defaults={'role': Membership.Role.OWNER, 'is_primary': True},
        )

        org.onboarded_at = timezone.now()
        org.save()

        assessment = run_assessment(org, user=user, name='Initial assessment (demo)')
        created = sync_controls_from_assessment(org, assessment)
        self.stdout.write(self.style.SUCCESS(
            f'Assessment {assessment.pk} and {created} controls provisioned at 0% (all "not started").'
        ))

        Risk.objects.create(
            organization=org,
            title='Unencrypted customer KYC backups in cross-border CDN',
            description='Nightly KYC snapshots replicate to a non-EEA CDN edge without envelope encryption.',
            category='cross-border',
            likelihood=4, impact=5,
            data_sensitivity=5, data_volume_log10=5,
            regulator_activity=4, control_effectiveness=25,
            treatment=Risk.Treatment.MITIGATE,
        )
        Risk.objects.create(
            organization=org,
            title='Marketing consent not re-captured after UX redesign',
            description='Consent banner was replaced during a landing page refresh; historical consents may be stale.',
            category='consent',
            likelihood=3, impact=3,
            data_sensitivity=2, data_volume_log10=5,
            regulator_activity=3, control_effectiveness=40,
            treatment=Risk.Treatment.MITIGATE,
        )

        DSARRequest.objects.create(
            organization=org,
            subject_name='Oma Adeyemi',
            subject_email='oma@example.com',
            subject_country='NG',
            request_type='access',
            notes='Requested full export via support.',
        )

        Incident.objects.create(
            organization=org,
            title='Vendor misconfig exposed test dataset',
            description='Analytics sandbox bucket set to public for 2 hours; no production data involved per forensic review.',
            severity='high',
            status=Incident.Status.TRIAGED,
            affected_subjects_estimate=0,
            affected_jurisdictions=['GH', 'KE'],
        )

        self.stdout.write(self.style.SUCCESS(
            'Demo workspace ready: 2 risks, 1 DSAR, 1 incident; Compliance score = 0%.'
        ))
