from django.core.management.base import BaseCommand

from jurisdictions.models import Requirement
from templates_engine.models import TemplateDefinition
from templates_engine.seed_templates import TEMPLATES


class Command(BaseCommand):
    help = 'Seed the TemplateDefinition rows for MVP.'

    def handle(self, *args, **options):
        loaded = 0
        links = 0
        for t in TEMPLATES:
            obj, _ = TemplateDefinition.objects.update_or_create(
                kind=t['kind'],
                jurisdiction_code=t.get('jurisdiction_code', ''),
                version=t.get('version', 1),
                defaults={
                    'name': t['name'],
                    'description': t.get('description', ''),
                    'body': t['body'],
                },
            )
            req_codes = t.get('requirements', [])
            if req_codes:
                reqs = Requirement.objects.filter(code__in=req_codes)
                obj.requirements.set(reqs)
                links += reqs.count()
            loaded += 1
        self.stdout.write(self.style.SUCCESS(f'{loaded} templates seeded with {links} requirement links.'))
