from pathlib import Path
import json

from django.db import migrations


def load_fixture(apps, schema_editor):
    # Locate the fixture file relative to project root
    BASE = Path(__file__).resolve().parents[4]
    fixture = BASE / 'server' / 'fixtures' / 'academies_2025.json'
    if not fixture.exists():
        # nothing to do
        return

    data = json.loads(fixture.read_text(encoding='utf-8'))
    Academy = apps.get_model('academies', 'Academy')

    # Update or create each record by pk; this is idempotent and safe on existing DBs
    for item in data:
        pk = item.get('pk')
        fields = item.get('fields', {})
        name = fields.get('name')
        level = fields.get('level', 0)
        logo = fields.get('logo', '')
        pid = fields.get('pid')

        defaults = {
            'name': name,
            'level': level,
            'logo': logo,
        }
        # set parent if provided
        if pid is None:
            # set parent to None
            Academy.objects.update_or_create(id=pk, defaults={**defaults, 'parent_id': None})
        else:
            Academy.objects.update_or_create(id=pk, defaults={**defaults, 'parent_id': pid})


class Migration(migrations.Migration):
    dependencies = [
        ('academies', '0002_data_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
