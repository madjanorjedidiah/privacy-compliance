from django.core.management.base import BaseCommand
from django.db import transaction

from jurisdictions.models import (
    Framework, Jurisdiction, Requirement, RequirementMapping,
)
from jurisdictions.seed_data import (
    JURISDICTIONS, FRAMEWORKS, REQUIREMENTS, CROSSWALK,
)


class Command(BaseCommand):
    help = 'Seed jurisdictions, frameworks, requirements and crosswalk.'

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true', help='Wipe and reseed.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['refresh']:
            self.stdout.write(self.style.WARNING('Refreshing jurisdiction data...'))
            RequirementMapping.objects.all().delete()
            Requirement.objects.all().delete()
            Framework.objects.all().delete()
            Jurisdiction.objects.all().delete()

        # Jurisdictions
        j_map = {}
        for j in JURISDICTIONS:
            obj, _ = Jurisdiction.objects.update_or_create(
                code=j['code'],
                defaults={k: v for k, v in j.items() if k != 'code'},
            )
            j_map[j['code']] = obj
        self.stdout.write(self.style.SUCCESS(f'  • {len(j_map)} jurisdictions loaded.'))

        # Frameworks
        f_map = {}
        for f in FRAMEWORKS:
            jur = j_map[f['jurisdiction_code']]
            obj, _ = Framework.objects.update_or_create(
                code=f['code'],
                defaults={
                    'jurisdiction': jur,
                    'short_name': f['short_name'],
                    'long_name': f['long_name'],
                    'summary': f['summary'],
                    'enacted_year': f['enacted_year'],
                    'reference_url': f['reference_url'],
                    'max_fine_description': f['max_fine_description'],
                },
            )
            f_map[f['code']] = obj
        self.stdout.write(self.style.SUCCESS(f'  • {len(f_map)} frameworks loaded.'))

        # Requirements
        r_map = {}
        total = 0
        for framework_code, reqs in REQUIREMENTS.items():
            framework = f_map[framework_code]
            for r in reqs:
                obj, _ = Requirement.objects.update_or_create(
                    framework=framework,
                    code=r['code'],
                    defaults={
                        'title': r['title'],
                        'summary': r['summary'],
                        'category': r['category'],
                        'citation': r.get('citation', ''),
                        'severity_weight': r.get('severity_weight', 3),
                        'applicability_rule': r.get('applicability_rule', ''),
                        'guidance': r.get('guidance', ''),
                        'typical_evidence': r.get('typical_evidence', ''),
                    },
                )
                r_map[r['code']] = obj
                total += 1
        self.stdout.write(self.style.SUCCESS(f'  • {total} requirements loaded.'))

        # Crosswalk
        mapped = 0
        for source_code, target_code, equivalence, note in CROSSWALK:
            source = r_map.get(source_code)
            target = r_map.get(target_code)
            if not source or not target:
                self.stdout.write(self.style.WARNING(f'  ! Crosswalk skipped: {source_code} → {target_code}'))
                continue
            RequirementMapping.objects.update_or_create(
                source=source, target=target,
                defaults={'equivalence': equivalence, 'note': note},
            )
            mapped += 1
        self.stdout.write(self.style.SUCCESS(f'  • {mapped} crosswalk mappings loaded.'))
        self.stdout.write(self.style.SUCCESS('Seed complete.'))
