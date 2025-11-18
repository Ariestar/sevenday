import os
import sys
import json
from pathlib import Path


def load_fixture(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    BASE = Path(__file__).resolve().parents[1]
    # 确保脚本静态分析与运行环境能解析顶级 apps 包
    apps_path = BASE / 'server' / 'apps'
    if str(BASE) not in sys.path:
        sys.path.insert(0, str(BASE))
    if str(apps_path) not in sys.path:
        sys.path.insert(0, str(apps_path))
    fixture = BASE / 'server' / 'fixtures' / 'academies_2025.json'
    if not fixture.exists():
        print('Fixture not found:', fixture)
        return

    data = load_fixture(fixture)

    # Use Django ORM
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
    django.setup()
    from academies.models import Academy  # type: ignore[reportMissingImports]

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

    print(f'Imported/updated {len(data)} academies, created {created}')


if __name__ == '__main__':
    main()
