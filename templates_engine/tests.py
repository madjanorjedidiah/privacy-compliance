from django.core.management import call_command
from django.test import TestCase

from accounts.models import Organization, OrgProfile
from templates_engine.engine import generate_document, render_template
from templates_engine.models import TemplateDefinition


class TemplateEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')
        call_command('seed_templates')

    def _org(self):
        org = Organization.objects.create(name='Acme Ltd', country='GH', website='https://acme.example')
        OrgProfile.objects.create(
            organization=org,
            data_categories=['contact', 'financial'],
            processing_purposes=['service_delivery'],
            cross_border_transfers=True,
        )
        return org

    def test_privacy_notice_gdpr_renders_with_org_name(self):
        org = self._org()
        tmpl = TemplateDefinition.objects.get(kind='privacy_notice', jurisdiction_code='EU')
        body = render_template(tmpl, org, 'EU')
        self.assertIn('Acme Ltd', body)
        self.assertIn('GDPR', body)

    def test_ropa_template_renders(self):
        org = self._org()
        tmpl = TemplateDefinition.objects.get(kind='ropa', jurisdiction_code='')
        body = render_template(tmpl, org, None)
        self.assertIn('Record of Processing', body)
        self.assertIn('Acme Ltd', body)

    def test_generate_document_creates_record(self):
        org = self._org()
        tmpl = TemplateDefinition.objects.get(kind='dsar_response', jurisdiction_code='')
        doc = generate_document(tmpl, org, jurisdiction_code='NG')
        self.assertEqual(doc.organization, org)
        self.assertIn('Acme Ltd', doc.rendered_content)

    def test_templates_are_linked_to_requirements(self):
        tmpl = TemplateDefinition.objects.get(kind='privacy_notice', jurisdiction_code='EU')
        codes = list(tmpl.requirements.values_list('code', flat=True))
        self.assertIn('GDPR-Art-12', codes)

    def test_universal_template_links_across_jurisdictions(self):
        ropa = TemplateDefinition.objects.get(kind='ropa', jurisdiction_code='')
        codes = set(ropa.requirements.values_list('code', flat=True))
        self.assertTrue({'GDPR-Art-30', 'NG-ROPA'} <= codes)
