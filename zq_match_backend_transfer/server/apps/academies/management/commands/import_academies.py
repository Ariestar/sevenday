from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
import json


class Command(BaseCommand):
    help = "Import academies from a fixture JSON into Academy model (update_or_create by pk)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            dest="fixture",
            help="Path to fixture JSON file (defaults to server/fixtures/academies_2025.json)",
            default=None,
        )

    def handle(self, *args, **options):
        fixture_path = options.get("fixture")
        base = Path(settings.BASE_DIR) if hasattr(settings, 'BASE_DIR') else Path.cwd()
        if fixture_path:
            path = Path(fixture_path)
        else:
            path = base / 'server' / 'fixtures' / 'academies_2025.json'

        if not path.exists():
            raise CommandError(f"Fixture not found: {path}")

        self.stdout.write(f"Loading fixture from {path}")
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)

        from academies.models import Academy

        created = 0
        for item in data:
            pk = item.get('pk')
            fields = item.get('fields', {})
            name = fields.get('name')
            level = fields.get('level', 0)
            logo = fields.get('logo', '')
            pid = fields.get('pid')

            obj, is_new = Academy.objects.update_or_create(
                id=pk,
                defaults={
                    'name': name,
                    'level': level,
                    'logo': logo,
                    'pid_id': pid,
                },
            )
            if is_new:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Imported/updated {len(data)} academies, created {created}'))
